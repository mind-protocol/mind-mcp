"""
Core work logic shared between CLI and TUI.

This module contains:
- Data structures (WorkResult, EscalationDecision)
- Constants (issue symbols, priorities, depth filters)
- Pure functions for building prompts and parsing output
- Async agent running for TUI integration

DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
"""

import asyncio
import concurrent.futures
import json
import logging
import random
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .agent_cli import build_agent_command, normalize_agent
from .agent_graph import AgentGraph, ISSUE_TO_POSTURE, DEFAULT_POSTURE
from .agents.prompts import get_agent_system_prompt, get_learnings_content
from .doctor_types import DoctorConfig
from .doctor_files import save_doctor_config
from .work_verification import (
    verify_completion,
    format_verification_feedback,
    all_passed,
    get_failed_membrane_protocols,
    VerificationResult,
)

logger = logging.getLogger(__name__)


# Symbols and emojis per issue type
ISSUE_SYMBOLS = {
    "MONOLITH": ("🏔️", "▓"),
    "UNDOCUMENTED": ("📝", "□"),
    "STALE_SYNC": ("⏰", "◷"),
    "PLACEHOLDER": ("🔲", "▢"),
    "INCOMPLETE_CHAIN": ("🔗", "⛓"),
    "NO_DOCS_REF": ("📎", "⌘"),
    "BROKEN_IMPL_LINK": ("💔", "⚡"),
    "STUB_IMPL": ("🚧", "▲"),
    "INCOMPLETE_IMPL": ("🔧", "◐"),
    "UNDOC_IMPL": ("📋", "◎"),
    "LARGE_DOC_MODULE": ("📚", "▤"),
    "YAML_DRIFT": ("🗺️", "≋"),
    "MISSING_TESTS": ("🧪", "⚗"),
    "ORPHAN_DOCS": ("👻", "◌"),
    "STALE_IMPL": ("📉", "⇅"),
    "DOC_GAPS": ("🕳️", "○"),
    "ESCALATION": ("⚖️", "⚡"),
    "PROPOSITION": ("💡", "✨"), # New: Agent proposals for improvement/refactor/features
    "SUGGESTION": ("💡", "?"),
    "NEW_UNDOC_CODE": ("🆕", "+"),
    "COMPONENT_NO_STORIES": ("📖", "◇"),
    "HOOK_UNDOC": ("🪝", "⌒"),
    "DOC_DUPLICATION": ("📋", "≡"),
    "MAGIC_VALUES": ("🔢", "#"),
    "HARDCODED_CONFIG": ("⚙️", "∞"),
    "HARDCODED_SECRET": ("🔐", "!"),
    "LONG_PROMPT": ("📜", "¶"),
    "LONG_SQL": ("🗃️", "§"),
    "LOG_ERROR": ("🧯", "×"),
}

# Human-readable descriptions for issue types
ISSUE_DESCRIPTIONS = {
    "MONOLITH": ("split", "into smaller modules"),
    "UNDOCUMENTED": ("add module mapping + docs for", ""),
    "STALE_SYNC": ("update outdated SYNC for", ""),
    "PLACEHOLDER": ("fill in placeholders in", ""),
    "INCOMPLETE_CHAIN": ("add missing docs to", ""),
    "NO_DOCS_REF": ("add DOCS: comment to", ""),
    "BROKEN_IMPL_LINK": ("fix broken links in", ""),
    "STUB_IMPL": ("implement stubs in", ""),
    "INCOMPLETE_IMPL": ("complete functions in", ""),
    "UNDOC_IMPL": ("add to IMPLEMENTATION docs:", ""),
    "LARGE_DOC_MODULE": ("reduce size of", "docs"),
    "YAML_DRIFT": ("fix modules.yaml entry for", ""),
    "MISSING_TESTS": ("add tests for", ""),
    "ORPHAN_DOCS": ("link or remove orphan docs in", ""),
    "STALE_IMPL": ("update IMPLEMENTATION doc for", ""),
    "DOC_GAPS": ("complete gaps left in", ""),
    "ESCALATION": ("resolve conflict in", ""),
    "PROPOSITION": ("review agent proposition in", ""), # New: Agent proposals for improvement/refactor/features
    "SUGGESTION": ("implement suggestion from", ""),
    "NEW_UNDOC_CODE": ("update docs for", ""),
    "COMPONENT_NO_STORIES": ("add stories for", ""),
    "HOOK_UNDOC": ("document hook", ""),
    "DOC_DUPLICATION": ("consolidate duplicate docs in", ""),
    "MAGIC_VALUES": ("extract magic numbers from", "to constants"),
    "HARDCODED_CONFIG": ("externalize config in", ""),
    "HARDCODED_SECRET": ("remove secret from", ""),
    "LONG_PROMPT": ("externalize prompts in", "to prompts/"),
    "LONG_SQL": ("externalize SQL in", "to .sql files"),
    "LOG_ERROR": ("review log errors in", ""),
}

# Agent symbols for parallel execution (20 symbols for variety)
AGENT_SYMBOLS = [
    "🥷", "🧚", "🤖", "🦊", "🐙", "🦄", "🧙", "🐲", "🦅", "🐺",
    "🦝", "🦉", "🐢", "🦎", "🐝", "🦋", "🐬", "🦈", "🦁", "🐯",
]

# Symbol to folder name mapping
AGENT_SYMBOL_NAMES = {
    "🥷": "ninja",
    "🧚": "fairy",
    "🤖": "robot",
    "🦊": "fox",
    "🐙": "octopus",
    "🦄": "unicorn",
    "🧙": "wizard",
    "🐲": "dragon",
    "🦅": "eagle",
    "🐺": "wolf",
    "🦝": "raccoon",
    "🦉": "owl",
    "🐢": "turtle",
    "🦎": "lizard",
    "🐝": "bee",
    "🦋": "butterfly",
    "🐬": "dolphin",
    "🦈": "shark",
    "🦁": "lion",
    "🐯": "tiger",
}


def get_symbol_name(symbol: str, index: int = 0) -> str:
    """Get folder-safe name for an agent symbol with optional index for duplicates.

    Args:
        symbol: The emoji symbol
        index: The agent index (0-based), used for numbering when > 10 agents

    Returns:
        Folder name like "ninja" for first 10, "ninja-2" for 11th ninja, etc.
    """
    base_name = AGENT_SYMBOL_NAMES.get(symbol, f"agent-{ord(symbol) if len(symbol) == 1 else hash(symbol) % 10000}")
    cycle = index // len(AGENT_SYMBOLS)
    if cycle > 0:
        return f"{base_name}-{cycle + 1}"
    return base_name


def get_issue_folder_name(issue_type: str, path: str, index: int = 0) -> str:
    """Get folder-safe name from issue type and path.

    Args:
        issue_type: e.g., "MONOLITH", "STALE_SYNC"
        path: e.g., "docs/physics/SYNC_Physics.md"
        index: Agent index for uniqueness

    Returns:
        Folder name like "STALE_SYNC-physics-SYNC_Physics" (sanitized)
    """
    import re
    # Extract meaningful parts from path
    path_parts = path.replace("\\", "/").split("/")
    # Take last 2 meaningful parts (skip extension)
    meaningful = []
    for part in reversed(path_parts):
        if part and part not in (".", ".."):
            # Remove extension
            name = re.sub(r'\.[^.]+$', '', part)
            if name:
                meaningful.insert(0, name)
            if len(meaningful) >= 2:
                break

    # Build folder name: TYPE-path_part1-path_part2
    path_str = "-".join(meaningful) if meaningful else "unknown"
    # Sanitize: only alphanumeric, dash, underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{issue_type}-{path_str}")
    # Add index if needed for uniqueness
    if index > 0:
        sanitized = f"{index:02d}-{sanitized}"
    else:
        sanitized = f"{index:02d}-{sanitized}"
    return sanitized[:60]  # Limit length

# Issue priority (lower = fix first)
# Order: MONOLITH (blocks all) → INCOMPLETE_IMPL (code first) → DOC_DUPLICATION →
#        INCOMPLETE_CHAIN (structural) → LARGE_DOC_MODULE (info) → HARDCODED_CONFIG (often false positive)
ISSUE_PRIORITY = {
    "HARDCODED_SECRET": 0,   # Security first
    "ESCALATION": 1,          # Conflicts block progress
    "MONOLITH": 2,           # Blocks everything
    "INCOMPLETE_IMPL": 3,    # Code before docs
    "STUB_IMPL": 4,          # Also code
    "INCOMPLETE_CHAIN": 6,   # Structural docs
    "YAML_DRIFT": 7,         # Config alignment
    "UNDOCUMENTED": 8,       # New docs needed
    "PLACEHOLDER": 9,        # Fill in gaps
    "BROKEN_IMPL_LINK": 10,  # Fix links
    "NO_DOCS_REF": 11,       # Add refs
    "STALE_SYNC": 12,        # Update state
    "UNDOC_IMPL": 13,        # Doc existing code
    "STALE_IMPL": 14,        # Update impl docs
    "DOC_GAPS": 15,          # Fill gaps
    "NEW_UNDOC_CODE": 16,    # New code docs
    "PROPOSITION": 16,        # New: Agent proposals, high priority for human review
    "SUGGESTION": 17,        # Nice to have
    "ORPHAN_DOCS": 18,       # Cleanup
    "MISSING_TESTS": 19,     # Tests last
    "LARGE_DOC_MODULE": 20,  # Info only
    "DOC_DUPLICATION": 30,    # Lower priority
    "COMPONENT_NO_STORIES": 31,
    "HOOK_UNDOC": 22,
    "MAGIC_VALUES": 23,
    "LONG_PROMPT": 24,
    "LONG_SQL": 25,
    "LEGACY_MARKER": 26,     # Convert old formats
    "UNRESOLVED_QUESTION": 27,  # Investigate questions
    "LOG_ERROR": 90,
    "HARDCODED_CONFIG": 99,  # Often false positive, last
}

# Issue types categorized by work depth
DEPTH_LINKS = {
    "NO_DOCS_REF",
    "BROKEN_IMPL_LINK",
    "YAML_DRIFT",
    "UNDOC_IMPL",
    "ORPHAN_DOCS",
}

DEPTH_DOCS = DEPTH_LINKS | {
    "UNDOCUMENTED",
    "STALE_SYNC",
    "PLACEHOLDER",
    "INCOMPLETE_CHAIN",
    "LARGE_DOC_MODULE",
    "STALE_IMPL",
    "DOC_GAPS",
    "ESCALATION",
    "DOC_DUPLICATION",
}

DEPTH_FULL = DEPTH_DOCS | {
    "MONOLITH",
    "STUB_IMPL",
    "INCOMPLETE_IMPL",
    "MISSING_TESTS",
    "HARDCODED_SECRET",
    "HARDCODED_CONFIG",
    "MAGIC_VALUES",
    "LONG_PROMPT",
    "LONG_SQL",
}


@dataclass
class WorkResult:
    """Result from a single work agent."""
    issue_type: str
    target_path: str
    success: bool
    agent_output: str
    duration_seconds: float
    error: Optional[str] = None
    decisions_made: Optional[List[Dict[str, str]]] = None
    provider_used: Optional[str] = None  # Actual provider used (resolved from "all")
    # Verification results (when using run_work_agent_with_verification_async)
    verification_results: Optional[List['VerificationResult']] = None
    verification_passed: bool = False
    retry_count: int = 0
    membrane_protocols_needed: Optional[List[str]] = None
    # Graph agent tracking
    selected_agent_id: Optional[str] = None
    selected_posture: Optional[str] = None


@dataclass
class EscalationDecision:
    """User's decision for an ESCALATION conflict."""
    conflict_title: str
    decision: str
    passed: bool = False


# Agent system prompt loaded from .mind/actors/ (see agents.prompts.get_agent_system_prompt)


def _get_git_head(target_dir: Path) -> Optional[str]:
    """Return current git HEAD hash, or None if unavailable."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None
    except Exception:
        return None


# NOTE: These lookup functions are intentionally simple one-line implementations.
# They provide semantic meaning for dictionary lookups with sensible defaults.
# Short body does not mean incomplete - these are complete implementations.

def get_issue_symbol(issue_type: str) -> tuple:
    """Get emoji and symbol for an issue type."""
    default = ("🔹", "•")
    if not issue_type:
        return default
    symbol = ISSUE_SYMBOLS.get(issue_type)
    if symbol:
        return symbol
    return ISSUE_SYMBOLS.get(issue_type.upper(), default)


def get_issue_action_parts(issue_type: str) -> tuple:
    """Get action parts (prefix, suffix) for an issue type."""
    default = ("fix", "")
    if not issue_type:
        return default
    parts = ISSUE_DESCRIPTIONS.get(issue_type)
    if parts:
        return parts
    return ISSUE_DESCRIPTIONS.get(issue_type.upper(), default)


def get_issue_action(issue_type: str, path: str) -> str:
    """Get human-readable action for an issue."""
    prefix, suffix = get_issue_action_parts(issue_type)
    if suffix:
        return f"{prefix} {path} {suffix}"
    return f"{prefix} {path}"


def get_depth_types(depth: str) -> set:
    """Get the set of issue types for a given depth level."""
    if depth == "links":
        return DEPTH_LINKS
    elif depth == "docs":
        return DEPTH_DOCS
    else:
        return DEPTH_FULL


def split_docs_to_read(docs_to_read: List[str], target_dir: Path) -> tuple[List[str], List[str]]:
    """Split docs into existing and missing paths relative to target_dir."""
    existing = []
    missing = []
    for doc in docs_to_read:
        if not doc:
            continue
        doc_path = Path(doc)
        candidate = doc_path if doc_path.is_absolute() else (target_dir / doc_path)
        if candidate.exists():
            existing.append(doc)
        else:
            missing.append(doc)
    return existing, missing


def _detect_recent_issue_number(target_dir: Path, max_commits: int = 5) -> Optional[int]:
    """Detect a recent issue number from the last few commit messages."""
    import subprocess
    import re

    try:
        result = subprocess.run(
            ["git", "log", f"-{max_commits}", "--pretty=%s"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            match = re.search(r"#(\d+)", line)
            if match:
                return int(match.group(1))
    except Exception:
        return None
    return None


def build_agent_prompt(
    issue: Any,  # DoctorIssue
    instructions: Dict[str, Any],
    target_dir: Path,
    github_issue_number: Optional[int] = None,
) -> str:
    """Build the full prompt for the work agent."""
    existing_docs, missing_docs = split_docs_to_read(instructions["docs_to_read"], target_dir)
    docs_list = "\n".join(f"- {d}" for d in existing_docs) or "- (no docs found)"
    missing_section = ""
    if missing_docs:
        missing_list = "\n".join(f"- {d}" for d in missing_docs)
        missing_section = f"""
## Missing Docs at Prompt Time
{missing_list}

If any missing docs should exist, locate the correct paths before proceeding.
"""

    if github_issue_number is None:
        github_issue_number = _detect_recent_issue_number(target_dir)

    github_section = ""
    if github_issue_number:
        github_section = f"""
## GitHub Issue
This fix is tracked by GitHub issue #{github_issue_number}.
When committing, include "Closes #{github_issue_number}" in your commit message.
"""

    return f"""# mind Work Task

## Issue Type: {issue.issue_type}
## Severity: {issue.severity}
{github_section}
## VIEW to Follow
Load and follow: `.mind/views/{instructions['view']}`

## Docs to Read FIRST (before any changes)
{docs_list}
{missing_section}

{instructions['prompt']}

## After Completion
1. Commit your changes with a descriptive message using a type prefix (e.g., "fix:", "docs:", "refactor:"){f' and include "Closes #{github_issue_number}"' if github_issue_number else ''}
2. Update `.mind/state/SYNC_Project_State.md` with:
   - What you fixed
   - Files created/modified
   - Any issues encountered
"""


def parse_decisions_from_output(output: str) -> List[Dict[str, str]]:
    """Parse DECISION items from agent output."""
    decisions = []
    lines = output.split('\n')
    current_decision = None

    for line in lines:
        stripped = line.strip()

        if '### DECISION:' in stripped or '### Decision:' in stripped:
            if current_decision and current_decision.get('name'):
                decisions.append(current_decision)
            name = stripped.split(':', 1)[1].strip() if ':' in stripped else ''
            current_decision = {'name': name, 'conflict': '', 'resolution': '', 'reasoning': ''}
        elif current_decision:
            lower = stripped.lower()
            if lower.startswith('- conflict:') or lower.startswith('conflict:'):
                current_decision['conflict'] = stripped.split(':', 1)[1].strip()
            elif lower.startswith('- resolution:') or lower.startswith('resolution:'):
                current_decision['resolution'] = stripped.split(':', 1)[1].strip()
            elif lower.startswith('- reasoning:') or lower.startswith('reasoning:'):
                current_decision['reasoning'] = stripped.split(':', 1)[1].strip()
            elif lower.startswith('- updated:') or lower.startswith('updated:'):
                current_decision['updated'] = stripped.split(':', 1)[1].strip()
            elif stripped.startswith('###') or stripped.startswith('## '):
                if current_decision.get('name'):
                    decisions.append(current_decision)
                current_decision = None

    if current_decision and current_decision.get('name'):
        decisions.append(current_decision)

    return decisions


def parse_stream_json_line(line: str) -> Optional[str]:
    """Parse a single JSON line from agent stream output, return readable text."""
    try:
        data = json.loads(line)
        msg_type = data.get("type", "")

        # Handle streaming content deltas (main streaming output)
        if msg_type == "content_block_delta":
            delta = data.get("delta", {})
            if delta.get("type") == "text_delta":
                return delta.get("text", "")

        # Handle tool use start
        elif msg_type == "content_block_start" or msg_type == "tool_code":
            if msg_type == "content_block_start":
                content = data.get("content_block", {})
                tool_name = content.get("name", "")
                tool_input = content.get("input", {})
            else:
                tool_name = data.get("name", "")
                tool_input = data.get("args", {})

            if tool_input:
                # Show key params briefly
                params = []
                for k, v in list(tool_input.items())[:2]:
                    val = str(v)[:40] + "..." if len(str(v)) > 40 else str(v)
                    params.append(f"{k}={val}")
                param_str = ", ".join(params)
                return f"\n**🔧 {tool_name}**(`{param_str}`)\n"
            return f"\n**🔧 {tool_name}**\n"

        # Handle final assistant message (fallback)
        elif msg_type == "assistant":
            message = data.get("message", {})
            content_list = message.get("content", [])
            if content_list and isinstance(content_list, list):
                for content in content_list:
                    if content.get("type") == "text":
                        return content.get("text", "")
            return None

        # Handle tool results
        elif msg_type == "result" or msg_type == "tool_result":
            res_val = data.get("result", "")
            if res_val:
                res_str = str(res_val)
                return f"[Result: {res_str[:100]}...]" if len(res_str) > 100 else f"[Result: {res_str}]"
            return None

        # Handle errors
        elif msg_type == "error":
            code = data.get("code", "UNKNOWN")
            message = data.get("message", "Unknown error")
            return f"\n**❌ ERROR ({code})**: {message}\n"

    except json.JSONDecodeError:
        pass
    except Exception:
        pass
    return None


async def run_work_agent_async(
    issue: Any,  # DoctorIssue
    target_dir: Path,
    on_output: Callable[[str], Awaitable[None]],
    instructions: Dict[str, Any],
    config: DoctorConfig,
    github_issue_number: Optional[int] = None,
    escalation_decisions: Optional[List[EscalationDecision]] = None,
    agent_id: Optional[str] = None,
    session_dir: Optional[Path] = None,
    agent_symbol: Optional[str] = None,
    agent_provider: str = "codex",
) -> WorkResult:
    """
    Async version of run_work_agent for TUI integration.
    """
    # Handle ESCALATION decisions
    if issue.issue_type == "ESCALATION" and escalation_decisions:
        decisions_text = "\n".join(
            f"- **{d.conflict_title}**: {d.decision}"
            for d in escalation_decisions if not d.passed
        )
        instructions["prompt"] = instructions["prompt"].replace(
            "{escalation_decisions}",
            decisions_text or "(No decisions provided)"
        )
    elif issue.issue_type == "ESCALATION":
        instructions["prompt"] = instructions["prompt"].replace(
            "{escalation_decisions}",
            "(No decisions provided - skip this issue)"
        )

    agent_provider = normalize_agent(agent_provider)
    # Resolve "all" to actual provider BEFORE building command so we can track it
    if agent_provider == "all":
        agent_provider = random.choice(["gemini", "claude", "codex"])

    prompt = build_agent_prompt(issue, instructions, target_dir, github_issue_number)

    # Load posture-based system prompt from .mind/actors/
    posture = agent_id.replace("agent_", "") if agent_id and agent_id.startswith("agent_") else DEFAULT_POSTURE
    system_prompt = get_agent_system_prompt(posture, target_dir) + get_learnings_content(target_dir)

    GEMINI_PRIMARY_MODEL = "gemini-3-flash-preview"
    GEMINI_FALLBACK_MODEL = "gemini-2.5-flash"

    # Determine Gemini model, with fallback logic
    fallback_key = agent_id or "default_work"
    current_gemini_model = config.gemini_model_fallback_status.get(fallback_key, GEMINI_PRIMARY_MODEL)
    
    current_attempt = 0
    max_attempts = 2 if agent_provider == "gemini" else 1
    text_output = []
    start_time = time.time()

    # Outer loop for model fallback retry
    try:
        while current_attempt < max_attempts:
            current_attempt += 1
            rate_limit_detected = [False] # Use list for closure modification

            try:
                agent_cmd = build_agent_command(
                    agent_provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    stream_json=(agent_provider in ("claude", "gemini")),
                    continue_session=False,
                    model_name=current_gemini_model if agent_provider == "gemini" else None,
                    add_dir=target_dir,
                )

                start_time = time.time()
                text_output = []  # Reset text_output for each attempt

            except Exception as e:
                logger.error(f"Error during agent command build: {e}")
                if current_attempt >= max_attempts:
                    raise
                continue

            # Create agent directory within session folder
            if session_dir and agent_symbol:
                agent_dir = session_dir / agent_symbol
            elif session_dir and agent_id:
                agent_dir = session_dir / agent_id
            elif agent_id:
                agent_dir = target_dir / ".mind" / "work" / agent_id
            else:
                agent_dir = target_dir / ".mind" / "work" / f"agent-{uuid.uuid4().hex[:8]}"

            agent_dir.mkdir(parents=True, exist_ok=True)

            # Copy CLAUDE.md so agent has context
            claude_md_src = target_dir / ".mind" / "CLAUDE.md"
            claude_md_dst = agent_dir / "CLAUDE.md"
            agents_md_src = target_dir / "AGENTS.md"
            agents_md_dst = agent_dir / "AGENTS.md"
            if claude_md_src.exists() and not claude_md_dst.exists():
                shutil.copy(claude_md_src, claude_md_dst)
            if agents_md_src.exists():
                agents_md_dst.write_text(agents_md_src.read_text())
            elif claude_md_src.exists():
                agents_md_dst.write_text(claude_md_src.read_text())

            # Write issue info to agent folder
            issue_info = agent_dir / "ISSUE.md"
            issue_info.write_text(f"""# Work Task

**Issue Type:** {issue.issue_type}
**Severity:** {issue.severity}
**Target:** {issue.path}

## Instructions
{instructions.get('prompt', 'No instructions provided')}

## Docs to Read
{chr(10).join('- ' + d for d in instructions.get('docs_to_read', []))}
""")

            head_before = _get_git_head(target_dir)

            def run_agent_sync():
                """Run agent synchronously in thread, return output lines."""
                output_lines = []
                try:
                    proc = subprocess.Popen(
                        agent_cmd.cmd,
                        cwd=agent_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE if agent_cmd.stdin else None,
                        text=False,
                    )
                    if agent_cmd.stdin:
                        proc.stdin.write((agent_cmd.stdin + "\n").encode())
                        proc.stdin.close()

                    for line in proc.stdout:
                        line_str = line.decode(errors='replace').strip()
                        if not line_str:
                            continue
                        
                        # Detect rate limit error in Gemini JSON output
                        if '"code": "RATE_LIMIT_EXCEEDED"' in line_str:
                            rate_limit_detected[0] = True

                        parsed = parse_stream_json_line(line_str)
                        if parsed:
                            output_lines.append(parsed)
                        elif not line_str.startswith("{"):
                            output_lines.append(line_str)

                    proc.wait()
                    return output_lines, proc.returncode
                except Exception as e:
                    output_lines.append(f"ERROR: {e}")
                    return output_lines, -1

            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = loop.run_in_executor(pool, run_agent_sync)
                last_callback = time.time()
                while not future.done():
                    await asyncio.sleep(0.5)
                    now = time.time()
                    if (now - last_callback) > 5.0:
                        await on_output("")
                        last_callback = now

                text_output, returncode = await asyncio.wrap_future(future)
            
            # Check for rate limit fallback
            if rate_limit_detected[0] and agent_provider == "gemini" and current_gemini_model == GEMINI_PRIMARY_MODEL:
                logger.warning(f"Rate limit hit for Gemini. Falling back to {GEMINI_FALLBACK_MODEL} and retrying.")
                current_gemini_model = GEMINI_FALLBACK_MODEL
                config.gemini_model_fallback_status[fallback_key] = current_gemini_model
                save_doctor_config(target_dir, config)
                continue

            duration = time.time() - start_time
            head_after = _get_git_head(target_dir)
            readable_output = "\n".join(text_output)
            success = bool(head_before and head_after and head_before != head_after)
            decisions = parse_decisions_from_output(readable_output)

            # Workaround: Delete GEMINI.md created by gemini CLI in agent's directory
            if agent_provider == "gemini":
                gemini_md_path = agent_dir / "GEMINI.md"
                if gemini_md_path.exists():
                    gemini_md_path.unlink()

            error = None
            if returncode != 0:
                error = f"Exit code: {returncode}"
            elif not success:
                error = "No git commit detected"

            return WorkResult(
                issue_type=issue.issue_type,
                target_path=issue.path,
                success=success,
                agent_output=readable_output,
                duration_seconds=duration,
                error=error,
                decisions_made=decisions if decisions else None,
                provider_used=agent_provider,
            )

    except asyncio.TimeoutError:
        return WorkResult(
            issue_type=issue.issue_type,
            target_path=issue.path,
            success=False,
            agent_output="\n".join(text_output),
            duration_seconds=600,
            error="Agent timed out after 10 minutes",
            provider_used=agent_provider,
        )
    except Exception as e:
        logger.error(f"Work agent failed: {e}")
        return WorkResult(
            issue_type=issue.issue_type,
            target_path=issue.path,
            success=False,
            agent_output="\n".join(text_output),
            duration_seconds=time.time() - start_time,
            error=str(e),
            provider_used=agent_provider,
        )


def _select_work_agent(issue_type: str) -> tuple[str, str]:
    """
    Select a work agent based on issue type posture mapping.

    Returns:
        Tuple of (agent_id, posture)
    """
    posture = ISSUE_TO_POSTURE.get(issue_type, DEFAULT_POSTURE)
    agent_id = f"agent_{posture}"
    return agent_id, posture


async def run_work_agent_with_verification_async(
    issue: Any,  # DoctorIssue
    target_dir: Path,
    on_output: Callable[[str], Awaitable[None]],
    instructions: Dict[str, Any],
    config: DoctorConfig,
    github_issue_number: Optional[int] = None,
    escalation_decisions: Optional[List[EscalationDecision]] = None,
    agent_id: Optional[str] = None,
    session_dir: Optional[Path] = None,
    agent_symbol: Optional[str] = None,
    agent_provider: str = "codex",
    max_verification_retries: int = 3,
    membrane_query: Optional[Callable] = None,
    use_graph_agents: bool = True,
) -> WorkResult:
    """
    Run work agent with mandatory verification and retry on failure.

    This function:
    1. Selects agent based on posture matching to issue type (if use_graph_agents)
    2. Sets agent status to 'running' in graph
    3. Runs agent, then runs verification checks
    4. If verification fails, restarts with --continue and feedback
    5. Sets agent status back to 'ready' on completion

    Args:
        issue: The doctor issue to work
        target_dir: Project root
        on_output: Callback for streaming output
        instructions: Work instructions
        config: Doctor config
        github_issue_number: Optional GitHub issue link
        escalation_decisions: Decisions for ESCALATION issues
        agent_id: Agent identifier
        session_dir: Session directory
        agent_symbol: Agent emoji symbol
        agent_provider: Agent CLI provider
        max_verification_retries: Max retries on verification failure
        membrane_query: Optional membrane query function
        use_graph_agents: Whether to use graph-based agent selection/status

    Returns:
        WorkResult with verification info
    """
    # Initialize graph agent management
    selected_agent_id = None
    posture = None
    agent_graph = None

    if use_graph_agents:
        try:
            agent_graph = AgentGraph(graph_name="mind")
            selected_agent_id, posture = _select_work_agent(issue.issue_type)

            # Set agent to running
            agent_graph.set_agent_running(selected_agent_id)
            logger.info(f"[work] Selected agent {selected_agent_id} (posture: {posture}) for {issue.issue_type}")
        except Exception as e:
            logger.warning(f"[work] Graph agent management failed, continuing without: {e}")
            agent_graph = None

    total_output = []
    total_duration = 0.0
    retry_count = 0
    last_result = None
    continue_feedback = ""

    try:
        while retry_count <= max_verification_retries:
            # Build prompt with feedback if this is a retry
            current_instructions = instructions.copy()
            if continue_feedback:
                current_instructions["prompt"] = (
                    continue_feedback + "\n\n" + current_instructions["prompt"]
                )

            # Capture git HEAD before
            head_before = _get_git_head(target_dir)

            # Run agent
            result = await run_work_agent_async(
                issue=issue,
                target_dir=target_dir,
                on_output=on_output,
                instructions=current_instructions,
                config=config,
                github_issue_number=github_issue_number,
                escalation_decisions=escalation_decisions,
                agent_id=agent_id,
                session_dir=session_dir,
                agent_symbol=agent_symbol,
                agent_provider=agent_provider,
            )

            # Capture git HEAD after
            head_after = _get_git_head(target_dir)

            # Collect output and duration
            total_output.append(result.agent_output)
            total_duration += result.duration_seconds
            last_result = result

            # If agent didn't even run successfully, don't verify
            if result.error and "Exit code" in result.error:
                logger.warning(f"Agent failed with error: {result.error}")
                break

            # Run verification
            verification_results = verify_completion(
                issue=issue,
                target_dir=target_dir,
                head_before=head_before,
                head_after=head_after,
                membrane_query=membrane_query,
            )

            if all_passed(verification_results):
                # All checks passed!
                logger.info(f"Verification PASSED for {issue.issue_type} in {issue.path}")
                return WorkResult(
                    issue_type=result.issue_type,
                    target_path=result.target_path,
                    success=True,
                    agent_output="\n---\n".join(total_output),
                    duration_seconds=total_duration,
                    error=None,
                    decisions_made=result.decisions_made,
                    provider_used=result.provider_used,
                    verification_results=verification_results,
                    verification_passed=True,
                    retry_count=retry_count,
                    membrane_protocols_needed=None,
                    selected_agent_id=selected_agent_id,
                    selected_posture=posture,
                )

            # Verification failed
            retry_count += 1
            failed_protocols = get_failed_membrane_protocols(verification_results)

            if retry_count > max_verification_retries:
                # Max retries exceeded
                logger.warning(
                    f"Verification failed after {max_verification_retries} retries "
                    f"for {issue.issue_type} in {issue.path}"
                )
                return WorkResult(
                    issue_type=result.issue_type,
                    target_path=result.target_path,
                    success=False,
                    agent_output="\n---\n".join(total_output),
                    duration_seconds=total_duration,
                    error=f"Verification failed after {max_verification_retries} retries",
                    decisions_made=result.decisions_made,
                    provider_used=result.provider_used,
                    verification_results=verification_results,
                    verification_passed=False,
                    retry_count=retry_count - 1,
                    membrane_protocols_needed=failed_protocols,
                    selected_agent_id=selected_agent_id,
                    selected_posture=posture,
                )

            # Format feedback for next attempt
            continue_feedback = format_verification_feedback(
                results=verification_results,
                issue=issue,
                attempt=retry_count,
                max_attempts=max_verification_retries,
            )

            logger.info(
                f"Verification failed (attempt {retry_count}/{max_verification_retries}), "
                f"restarting with feedback. Failed protocols: {failed_protocols}"
            )

            # Notify via output callback
            await on_output(f"\n[Verification failed, retry {retry_count}/{max_verification_retries}]\n")

        # Loop exited without success
        return WorkResult(
            issue_type=issue.issue_type,
            target_path=issue.path,
            success=False,
            agent_output="\n---\n".join(total_output) if total_output else "",
            duration_seconds=total_duration,
            error="Verification loop exited unexpectedly",
            verification_passed=False,
            retry_count=retry_count,
            selected_agent_id=selected_agent_id,
            selected_posture=posture,
        )

    finally:
        # Always set agent back to ready
        if agent_graph and selected_agent_id:
            agent_graph.set_agent_ready(selected_agent_id)
            logger.info(f"[work] Agent {selected_agent_id} set back to ready")
