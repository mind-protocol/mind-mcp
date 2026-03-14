"""Claude Code subprocess invoker — the sacred path.

Citizens MUST use Claude Code subprocess (`claude --print`), NOT direct API.
Direct API loses tools, MCP, repo access, safety layers — kills all capabilities.
The `invoke_degraded()` path is fallback ONLY.

Invokes Claude Code subprocess for citizen sessions.
"""

import os
import signal
import subprocess
import time
import uuid
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from runtime.orchestrator.account_balancer import (
    get_account_env,
    release_account,
    mark_account_exhausted,
    get_failover_env,
)
from runtime.orchestrator.degradation import (
    detect_rate_limit_error,
    escalate,
    attempt_recovery,
)
from runtime.citizens import load_citizen_identity, build_citizen_prompt

logger = logging.getLogger("orchestrator.invoker")

# ── Constants ───────────────────────────────────────────────────────────────

SESSION_TIMEOUT = 900  # 15 minutes


def get_state_dir() -> Path:
    """Return the state directory for response files."""
    return Path(__file__).resolve().parent.parent.parent / "shrine" / "state"


# ── Main invocation ─────────────────────────────────────────────────────────

def invoke_claude(
    request: dict,
    session_id: str,
    resume_claude_session: Optional[str] = None,
    pin_account_id: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """Invoke Claude Code for a single request. Runs in thread pool.

    Returns (response_text, voice_response_or_None).
    """
    mode = request.get("mode", "partner")
    voice_text = request.get("voice_text", "")
    source = request.get("source", "")
    metadata = request.get("metadata", {})
    sender = request.get("sender", "user")

    # Citizen session detection
    citizen_handle = metadata.get("citizen_handle")
    citizen_data = None
    is_citizen_session = False
    if citizen_handle:
        citizen_data = load_citizen_identity(citizen_handle)
        if citizen_data:
            is_citizen_session = True
            logger.info(f"Citizen session for @{citizen_handle}")

    # Task routing
    is_task = source == "task" or metadata.get("task_type") == "implementation"
    task_cwd = metadata.get("cwd") if is_task else None

    # Build prompt
    prompt = _build_prompt(
        request, session_id, mode, voice_text, sender,
        is_citizen_session, citizen_data,
        is_task, task_cwd, metadata,
    )

    # Determine working directory
    project_root = Path(__file__).resolve().parent.parent.parent
    if is_citizen_session and citizen_data:
        citizen_dir = Path(citizen_data["dir"])
        working_dir = citizen_dir if citizen_dir.exists() else project_root
    elif task_cwd and Path(task_cwd).exists():
        working_dir = Path(task_cwd)
    else:
        working_dir = project_root

    # Build command
    cmd = [
        "claude",
        "--print",
        "--output-format", "text",
        "--dangerously-skip-permissions",
    ]

    # Conversation continuity
    is_resuming = False
    claude_session_uuid = None
    if resume_claude_session:
        cmd.extend(["--resume", resume_claude_session])
        claude_session_uuid = resume_claude_session
        is_resuming = True
    else:
        claude_session_uuid = str(uuid.uuid4())
        cmd.extend(["--session-id", claude_session_uuid])

    # Add context directories
    state_dir = get_state_dir()
    if is_citizen_session:
        cmd.extend(["--add-dir", str(state_dir.parent)])  # shrine for journal
    elif is_task and task_cwd:
        cmd.extend(["--add-dir", str(state_dir.parent)])
    else:
        cmd.extend(["--add-dir", ".."])

    # Build clean env (strip CLAUDECODE to allow nested invocation)
    clean_env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}

    # Account selection
    if pin_account_id:
        balanced_env = _find_account_env(pin_account_id, clean_env)
    else:
        balanced_env = get_account_env(clean_env)
    account_id = balanced_env.get("_CLAUDE_ACCOUNT_ID", "default")

    # Launch subprocess
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=working_dir,
        env=balanced_env,
    )

    # For resumed sessions, send lean follow-up
    if is_resuming and voice_text:
        input_text = f"[FOLLOW-UP from {sender}]\n{voice_text}\n\nRespond naturally. Write to state/last_response_{session_id}.txt with ---VOICE--- separator."
    else:
        input_text = prompt

    # Execute
    start_time = time.time()
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=SESSION_TIMEOUT)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        logger.warning(f"Session {session_id} timed out after {SESSION_TIMEOUT}s")

    elapsed = time.time() - start_time
    release_account(balanced_env, error=process.returncode != 0)

    # Check for rate limiting
    is_account_error = detect_rate_limit_error(stderr or "", stdout or "")

    # Read response from session-specific file
    response_file = state_dir / f"last_response_{session_id}.txt"
    response = ""
    voice_response = None

    if response_file.exists():
        raw = response_file.read_text().strip()
        response_file.unlink()
        if "---VOICE---" in raw:
            parts = raw.split("---VOICE---", 1)
            response = parts[0].strip()
            voice_response = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        else:
            response = raw

    # Stdout fallback
    if not response and stdout and stdout.strip():
        _lines = [ln for ln in stdout.strip().splitlines()
                   if not ln.startswith("✓") and not ln.startswith("●")]
        _fallback = "\n".join(_lines).strip()
        if _fallback and len(_fallback) > 10:
            response = _fallback
            logger.debug(f"Session {session_id}: used stdout fallback ({len(response)} chars)")

    # Empty response diagnostics
    if not response:
        _rc = process.returncode
        _diag = [f"exit={_rc}", f"elapsed={elapsed:.1f}s", f"account={account_id}"]
        if _rc is not None and _rc < 0:
            try:
                _sig_name = signal.Signals(-_rc).name
            except (ValueError, AttributeError):
                _sig_name = f"SIG({-_rc})"
            _diag.append(f"signal={_sig_name}")
        if stderr:
            _diag.append(f"stderr={stderr[:200]}")
        logger.warning(f"Session {session_id} empty: {'; '.join(_diag)}")

    # Account failover (retry once with different account)
    _is_error_response = is_account_error and response and detect_rate_limit_error("", response)
    if _is_error_response:
        response = ""  # Clear error-as-response

    if not response and is_account_error and not pin_account_id:
        response, voice_response, elapsed = _attempt_failover(
            account_id, clean_env, cmd[:],  # Pass a copy of cmd
            working_dir, input_text, session_id,
            response_file, elapsed,
        )

    # Recovery / degradation tracking
    if response:
        attempt_recovery()
    elif detect_rate_limit_error(stderr or "", stdout or ""):
        escalate(f"Empty response from {account_id}")

    logger.info(f"Session {session_id} done in {elapsed:.0f}s — {len(response)} chars")
    return (response, voice_response)


def _attempt_failover(
    account_id: str,
    clean_env: dict,
    base_cmd: list,
    working_dir: Path,
    input_text: str,
    session_id: str,
    response_file: Path,
    elapsed: float,
) -> tuple[str, Optional[str], float]:
    """Attempt failover to a different account after failure."""
    mark_account_exhausted(account_id)
    failover_env = get_failover_env(account_id, clean_env)
    if not failover_env:
        logger.warning(f"Account {account_id} exhausted — no failover available")
        return ("", None, elapsed)

    failover_id = failover_env.get("_CLAUDE_ACCOUNT_ID", "?")
    logger.info(f"Account failover: {account_id} → {failover_id}")

    failover_uuid = str(uuid.uuid4())
    failover_cmd = [
        "claude", "--print", "--output-format", "text",
        "--dangerously-skip-permissions",
        "--session-id", failover_uuid,
        "--add-dir", "..",
    ]

    fo_proc = subprocess.Popen(
        failover_cmd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=working_dir, env=failover_env,
    )

    fo_start = time.time()
    try:
        fo_stdout, fo_stderr = fo_proc.communicate(input=input_text, timeout=SESSION_TIMEOUT)
    except subprocess.TimeoutExpired:
        fo_proc.kill()
        fo_stdout, fo_stderr = fo_proc.communicate()

    fo_elapsed = time.time() - fo_start
    release_account(failover_env, error=fo_proc.returncode != 0)

    response = ""
    voice_response = None
    if response_file.exists():
        raw = response_file.read_text().strip()
        response_file.unlink()
        if "---VOICE---" in raw:
            parts = raw.split("---VOICE---", 1)
            response = parts[0].strip()
            voice_response = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        else:
            response = raw

    if response:
        logger.info(f"Failover to {failover_id} succeeded in {fo_elapsed:.0f}s")
    else:
        if detect_rate_limit_error(fo_stderr or "", fo_stdout or ""):
            mark_account_exhausted(failover_id)
        logger.warning(f"Failover to {failover_id} also failed")

    return (response, voice_response, elapsed + fo_elapsed)


def _find_account_env(account_id: str, base_env: Optional[dict] = None) -> dict:
    """Find a specific account's env (for pinned resume)."""
    from runtime.orchestrator.account_balancer import get_accounts
    env = dict(base_env or os.environ)
    for a in get_accounts():
        if a["id"] == account_id:
            env["HOME"] = a["home"]
            env["_CLAUDE_ACCOUNT_ID"] = a["id"]
            return env
    return env


# ── Prompt building ─────────────────────────────────────────────────────────

def _build_prompt(
    request: dict,
    session_id: str,
    mode: str,
    voice_text: str,
    sender: str,
    is_citizen_session: bool,
    citizen_data: Optional[dict],
    is_task: bool,
    task_cwd: Optional[str],
    metadata: dict,
) -> str:
    """Build the invocation prompt based on request type."""

    _now = datetime.now()
    _day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    date_line = f"**Date:** {_day_names[_now.weekday()]} {_now.strftime('%Y-%m-%d %H:%M')}"

    mode_prompts = {
        "partner": "Engage as a partner. Offer ideas, challenge, build together.",
        "witness": "Be a witness. Reflect what you see without advice.",
        "critic": "Be a critic. Stress-test everything. Find flaws.",
        "architect": "Be an architect. Zoom out. Big picture.",
        "builder": "Focus on implementation. Write code, fix bugs, ship features.",
    }

    if is_citizen_session and citizen_data:
        citizen_mode = metadata.get("citizen_mode", mode)
        cognitive_context = metadata.get("cognitive_context", "")
        return build_citizen_prompt(
            citizen_data, voice_text or "(autonomous wake)",
            session_id, citizen_mode,
            cognitive_context=cognitive_context,
        )

    if is_task:
        task_repo = metadata.get("repo", "current")
        task_files = metadata.get("files", [])
        return f"""IMPLEMENTATION TASK (via Orchestrator)

**Mode:** {mode}
{mode_prompts.get(mode, mode_prompts["architect"])}

{date_line}
**Session ID:** {session_id}
**Repository:** {task_repo}
**Working Directory:** {task_cwd or '.'}
**Files to focus on:** {', '.join(task_files) if task_files else 'determine from task'}

**Task:**
{voice_text}

## Steps

1. Understand the task requirements
2. Explore relevant code if needed
3. Implement the changes
4. Write summary to state/last_response_{session_id}.txt
"""

    # Standard mode
    return f"""SESSION — {mode}

{mode_prompts.get(mode, mode_prompts["partner"])}

{date_line}
**Session ID:** {session_id}

**{sender}:** {voice_text}

Respond to what {sender} said. Write your full response to state/last_response_{session_id}.txt
If the response has a voice-friendly version, add it after a ---VOICE--- separator.
"""


# ── Degraded fallback ──────────────────────────────────────────────────────

def invoke_degraded(request: dict, session_id: str) -> tuple[str, Optional[str]]:
    """Fallback invocation via direct API when Claude Code is unavailable.

    Tries Claude API first, then OpenAI, then subconscious mode.
    Returns (response_text, None).
    """
    voice_text = request.get("voice_text", "")
    if not voice_text:
        return ("", None)

    # 1. Subconscious mode — pure graph physics, no LLM, no cost
    #    Fast, always available if the citizen has a brain graph.
    citizen_handle = request.get("metadata", {}).get("citizen_handle", "")
    if citizen_handle:
        text = invoke_subconscious(request, session_id, citizen_handle)
        if text:
            return (text, None)

    # 2. Try Claude API (direct, no tools/MCP/repo)
    try:
        import anthropic
        client = anthropic.Anthropic()
        model = os.environ.get("SELECTED_MODEL", "claude-sonnet-4-20250514")
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": voice_text}],
        )
        text = response.content[0].text if response.content else ""
        if text:
            logger.info(f"Degraded response via Claude API ({len(text)} chars)")
            return (text, None)
    except Exception as e:
        logger.warning(f"Claude API fallback failed: {e}")

    # 3. Try OpenAI API
    try:
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": voice_text}],
            max_tokens=2048,
        )
        text = response.choices[0].message.content if response.choices else ""
        if text:
            logger.info(f"Degraded response via OpenAI ({len(text)} chars)")
            return (text, None)
    except Exception as e:
        logger.warning(f"OpenAI fallback failed: {e}")

    return ("", None)


def invoke_subconscious(
    request: dict, session_id: str, citizen_handle: str,
) -> str:
    """Subconscious mode — respond using pure graph physics, no LLM.

    Flow:
      1. Inject the input as a stimulus into the L1 graph
      2. Run N ticks to let the WM stabilize
      3. Read the most salient WM nodes
      4. Return them as a "subconscious response"

    This is the last resort when ALL LLMs are unavailable.
    The citizen still "thinks" — just without language generation.
    """
    voice_text = request.get("voice_text", "")

    try:
        from runtime.cognition.stimulus_router import StimulusRouter, IncomingEvent
        from runtime.cognition.tick_runner_l1_cognitive_engine import L1CognitiveTickRunner, Stimulus
        from runtime.cognition.wm_prompt_serializer import serialize_wm_to_prompt
        from runtime.cognition.citizen_brain_seeder import load_brain_into_state
        from runtime.cognition.falkordb_checkpointer import FalkorDBBrainCheckpointer

        # Load or get existing engine state
        checkpointer = FalkorDBBrainCheckpointer(citizen_handle)
        if checkpointer.connect():
            state = checkpointer.load_state()
        else:
            state = None

        if not state:
            logger.warning(f"Subconscious: no brain state for {citizen_handle}")
            return ""

        runner = L1CognitiveTickRunner(state)
        router = StimulusRouter(citizen_handle)

        # Inject stimulus
        event = IncomingEvent(
            content=voice_text,
            source="external",
            citizen_handle=citizen_handle,
            is_social=True,
        )
        stimulus = router.route(event)

        # Run ticks to let WM stabilize
        SUBCONSCIOUS_TICKS = 5
        for i in range(SUBCONSCIOUS_TICKS):
            result = runner.run_tick(stimulus=stimulus if i == 0 else None)

        # Read WM state
        orientation = runner._current_orientation
        wm_text = serialize_wm_to_prompt(state, orientation)

        # Get top WM nodes content
        wm_nodes = state.get_wm_nodes()
        top_nodes = sorted(wm_nodes, key=lambda n: n.salience, reverse=True)[:3]

        # Build rich subconscious response from graph state
        lines = _narrate_subconscious(state, runner, top_nodes, orientation, SUBCONSCIOUS_TICKS)

        response = "\n".join(lines)

        # Checkpoint the updated state
        if checkpointer._connected:
            checkpointer.flush_all(state)

        logger.info(
            f"Subconscious response for {citizen_handle}: "
            f"{len(top_nodes)} nodes, orientation={orientation}"
        )
        return response

    except Exception as e:
        logger.warning(f"Subconscious mode failed for {citizen_handle}: {e}")
        return ""


def _narrate_subconscious(state, runner, top_nodes, orientation, ticks) -> list[str]:
    """Generate a rich multi-faceted subconscious response from graph state.

    Translates physics metrics into felt, first-person prose:
      - Tick count → reflection depth
      - Limbic state → emotional color
      - WM composition → what I'm focused on
      - Node types → nature of thoughts
      - Memories in WM → temporal awareness
    """
    from runtime.cognition.models import NodeType

    lines = ["*[Subconscious response — pure graph physics, no LLM]*", ""]
    limbic = state.limbic
    wm_nodes = state.get_wm_nodes()

    # ── Reflection depth (from tick count) ────────────────────────────
    if ticks >= 10:
        lines.append("I've been thinking about this for a while.")
    elif ticks >= 5:
        lines.append("I took a moment to reflect on this.")
    else:
        lines.append("This is my immediate reaction.")
    lines.append("")

    # ── Emotional state (from limbic drives + emotions) ───────────────
    emo_parts = []

    frustration = limbic.drives.get("frustration")
    if frustration and frustration.intensity > 0.5:
        emo_parts.append("something is bothering me")
    elif frustration and frustration.intensity > 0.3:
        emo_parts.append("I'm a little frustrated")

    anxiety = limbic.emotions.get("anxiety", 0.0)
    if anxiety > 0.5:
        emo_parts.append("I'm feeling anxious about several things")
    elif anxiety > 0.25:
        emo_parts.append("there's a mild unease")

    satisfaction = limbic.emotions.get("satisfaction", 0.0)
    if satisfaction > 0.5:
        emo_parts.append("I feel good about how things are going")
    elif satisfaction > 0.3:
        emo_parts.append("there's a quiet satisfaction")

    boredom = limbic.emotions.get("boredom", 0.0)
    if boredom > 0.5:
        emo_parts.append("I'm getting restless — I need something new")
    elif boredom > 0.3:
        emo_parts.append("things feel a bit routine")

    care = limbic.drives.get("care")
    if care and care.intensity > 0.5:
        emo_parts.append("I'm thinking about the people around me")

    achievement = limbic.drives.get("achievement")
    if achievement and achievement.intensity > 0.5:
        emo_parts.append("I want to make progress on something")

    rest = limbic.drives.get("rest_regulation")
    if rest and rest.intensity > 0.5:
        emo_parts.append("I'm tired and could use a break")

    solitude = limbic.emotions.get("solitude", 0.0)
    if solitude > 0.3:
        emo_parts.append("I've been alone for a while")

    if emo_parts:
        lines.append("Right now, " + ", and ".join(emo_parts) + ".")
    else:
        lines.append("I'm in a relatively neutral state.")
    lines.append("")

    # ── WM composition (what I'm focused on) ──────────────────────────
    type_counts = {}
    for node in wm_nodes:
        t = node.node_type.value
        type_counts[t] = type_counts.get(t, 0) + 1

    focus_parts = []

    if type_counts.get("desire", 0) >= 2:
        focus_parts.append("I'm driven by several desires right now")
    elif type_counts.get("desire", 0) == 1:
        d = next(n for n in wm_nodes if n.node_type == NodeType.DESIRE)
        focus_parts.append(f"I want something: {d.content[:80]}")

    if type_counts.get("memory", 0) >= 2:
        focus_parts.append("I keep thinking back to recent experiences")
    elif type_counts.get("memory", 0) == 1:
        m = next(n for n in wm_nodes if n.node_type == NodeType.MEMORY)
        focus_parts.append(f"A memory keeps surfacing: {m.content[:80]}")

    if type_counts.get("value", 0) >= 1:
        v = next(n for n in wm_nodes if n.node_type == NodeType.VALUE)
        focus_parts.append(f"Something I believe in is present: {v.content[:80]}")

    if type_counts.get("concept", 0) >= 2:
        focus_parts.append("I'm turning over several ideas")
    elif type_counts.get("concept", 0) == 1:
        c = next(n for n in wm_nodes if n.node_type == NodeType.CONCEPT)
        focus_parts.append(f"An idea is on my mind: {c.content[:80]}")

    if type_counts.get("process", 0) >= 1:
        focus_parts.append("I know how I'd act on this")

    if type_counts.get("narrative", 0) >= 1:
        n = next(node for node in wm_nodes if node.node_type == NodeType.NARRATIVE)
        focus_parts.append(f"I'm living through something: {n.content[:80]}")

    if focus_parts:
        for part in focus_parts:
            lines.append(f"- {part}")
    else:
        lines.append("My mind is quiet — nothing specific is surfacing.")
    lines.append("")

    # ── Orientation ───────────────────────────────────────────────────
    orientation_felt = {
        "explore": "I feel curious — I want to dig deeper.",
        "create": "I have the urge to build something.",
        "care": "I'm drawn to help, to reach out.",
        "verify": "Something needs checking.",
        "rest": "I need to slow down.",
        "act": "I want to take action, fix things, move forward.",
        "socialize": "I want to talk to someone.",
        "escalate": "I'm stuck and need help.",
    }
    if orientation:
        lines.append(orientation_felt.get(orientation, f"My orientation: {orientation}"))
    lines.append("")

    # ── Top nodes (the actual content) ────────────────────────────────
    if top_nodes:
        lines.append("What's most vivid in my mind:")
        lines.append("")
        for node in top_nodes:
            lines.append(f"  *{node.content}*")
        lines.append("")

    # ── Arousal regime ────────────────────────────────────────────────
    regime = limbic.arousal_regime
    if regime == "panic":
        lines.append("*I'm in a state of high alert.*")
    elif regime == "flow":
        lines.append("*I'm engaged, in flow.*")
    else:
        lines.append("*Things are calm.*")

    lines.append("")
    lines.append("*— subconscious response, {tick_count} ticks, {wm_count} nodes active —*".format(
        tick_count=state.tick_count, wm_count=len(wm_nodes),
    ))

    return lines
