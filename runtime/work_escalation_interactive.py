"""
Interactive work functions for CLI.

Extracted from work.py to reduce monolith size.
Contains:
- Manager agent functionality (input listener, spawn, check)
- Interactive conflict resolution (ESCALATION)
- CLI progress display utilities

DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
"""

import subprocess
import sys
import time
from pathlib import Path
from threading import Lock
from typing import List, Optional

from .agent_cli import build_agent_command, normalize_agent
from .work_core import EscalationDecision, get_issue_symbol


# ANSI color codes (CLI-specific)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    GRAY = "\033[38;5;245m"

    # Agent colors (cycle through for parallel agents)
    AGENT_COLORS = [
        "\033[38;5;39m",   # Blue
        "\033[38;5;208m",  # Orange
        "\033[38;5;42m",   # Green
        "\033[38;5;201m",  # Pink
        "\033[38;5;226m",  # Yellow
        "\033[38;5;51m",   # Cyan
        "\033[38;5;196m",  # Red
        "\033[38;5;141m",  # Purple
    ]

    # Status colors
    SUCCESS = "\033[38;5;42m"   # Green
    FAILURE = "\033[38;5;196m"  # Red
    WARNING = "\033[38;5;208m"  # Orange
    INFO = "\033[38;5;39m"      # Blue

    # Special colors
    VIOLET = "\033[38;5;183m"   # Light violet for user messages
    HEALTH = "\033[38;5;87m"    # Cyan for health score
    CRITICAL = "\033[38;5;196m" # Red for critical count
    WARN_COUNT = "\033[38;5;214m"  # Orange-yellow for warning count


def color(text: str, color_code: str) -> str:
    """Wrap text in ANSI color codes with automatic reset."""
    return f"{color_code}{text}{Colors.RESET}"


def print_progress_bar(current: int, total: int, width: int = 40, status: str = "") -> None:
    """Print a progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(f"\r  [{bar}] {current}/{total} {status}")
    sys.stdout.flush()


# Global state for manager input
manager_input_queue: List[str] = []
manager_input_lock = Lock()
stop_input_listener = False


def input_listener_thread():
    """Background thread that listens for user input during works."""
    global stop_input_listener
    import select

    while not stop_input_listener:
        try:
            # Check if input is available (non-blocking on Unix)
            if sys.platform != 'win32':
                readable, _, _ = select.select([sys.stdin], [], [], 0.5)
                if readable:
                    line = sys.stdin.readline().strip()
                    if line:
                        with manager_input_lock:
                            manager_input_queue.append(line)
            else:
                # Windows fallback - just sleep
                time.sleep(0.5)
        except Exception:
            break


def spawn_manager_agent(
    user_input: str,
    recent_logs: List[str],
    target_dir: Path,
    agent_provider: str = "codex",
) -> Optional[str]:
    """Spawn the mind manager with user input and recent logs."""
    agent_provider = normalize_agent(agent_provider)

    manager_dir = target_dir / ".mind" / "agents" / "manager"
    if not manager_dir.exists():
        print(f"  {Colors.DIM}(mind manager not found at {manager_dir}){Colors.RESET}")
        return None

    claude_md_src = target_dir / ".mind" / "CLAUDE.md"
    claude_md_dst = manager_dir / "CLAUDE.md"
    manager_agents_src = manager_dir / "AGENTS.md"
    agents_md_src = target_dir / "AGENTS.md"
    agents_md_dst = manager_dir / "AGENTS.md"
    if claude_md_src.exists() and not claude_md_dst.exists():
        claude_md_dst.write_text(claude_md_src.read_text())
    if manager_agents_src.exists():
        agents_md_dst.write_text(manager_agents_src.read_text())
    elif agents_md_src.exists():
        agents_md_dst.write_text(agents_md_src.read_text())
    elif claude_md_src.exists():
        agents_md_dst.write_text(claude_md_src.read_text())

    # Build context with recent logs
    logs_context = "\n".join(recent_logs[-50:]) if recent_logs else "(No recent logs)"

    prompt = f"""## Human Input During Work

The human has provided input during an active work session:

**Human says:** {user_input}

## Recent Work Logs

```
{logs_context}
```

## Your Task

Respond to the human's input. If they're:
- Asking a question → Answer it
- Providing context → Acknowledge and explain how it helps
- Making a decision → Record it as a DECISION
- Redirecting → Acknowledge the new direction

Keep your response concise - works are in progress.
"""

    try:
        agent_cmd = build_agent_command(
            agent_provider,
            prompt=prompt,
            stream_json=False,
            continue_session=True,
        )

        print()
        print(f"{Colors.BOLD}🎛️  mind Manager{Colors.RESET}")
        print(f"{'─'*40}")

        # Stream output instead of capturing (faster feedback)
        process = subprocess.Popen(
            agent_cmd.cmd,
            cwd=manager_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            stdin=subprocess.PIPE if agent_cmd.stdin else None,
        )
        if agent_cmd.stdin and process.stdin:
            process.stdin.write(agent_cmd.stdin + "\n")
            process.stdin.flush()
            process.stdin.close()

        response_lines = []
        try:
            # Read output line by line with timeout
            import select
            while True:
                # Check if process finished
                if process.poll() is not None:
                    break

                # Check for output with short timeout
                readable, _, _ = select.select([process.stdout], [], [], 0.1)
                if readable:
                    line = process.stdout.readline()
                    if line:
                        print(line, end='', flush=True)
                        response_lines.append(line)

            # Get any remaining output
            remaining = process.stdout.read()
            if remaining:
                print(remaining, end='', flush=True)
                response_lines.append(remaining)

            process.wait(timeout=30)  # Wait for process to finish

        except subprocess.TimeoutExpired:
            process.kill()
            print(f"  {Colors.DIM}(Manager timed out){Colors.RESET}")

        print(f"{'─'*40}")
        return ''.join(response_lines).strip() if response_lines else None

    except Exception as e:
        print(f"  {Colors.DIM}(Manager error: {e}){Colors.RESET}")

    return None


def check_for_manager_input(
    recent_logs: List[str],
    target_dir: Path,
    agent_provider: str = "codex",
) -> Optional[str]:
    """Check if user has provided input, spawn manager if so."""
    global manager_input_queue

    with manager_input_lock:
        if manager_input_queue:
            user_input = manager_input_queue.pop(0)
            # Echo user input in violet
            print(f"\n{Colors.VIOLET}💬 You: {user_input}{Colors.RESET}")
            return spawn_manager_agent(user_input, recent_logs, target_dir, agent_provider)

    return None


def resolve_escalation_interactive(issue) -> List[EscalationDecision]:
    """Interactively resolve ESCALATION conflicts with user input.

    Args:
        issue: DoctorIssue with issue_type == "ESCALATION"

    Returns:
        List of EscalationDecision with user's choices
    """
    decisions = []
    items = issue.details.get("items", [])

    print()
    print(f"{Colors.BOLD}⚖️  ESCALATION: Conflicts need your decision{Colors.RESET}")
    print(f"   File: {issue.path}")
    print(f"{'─'*60}")

    for i, item in enumerate(items, 1):
        title = item.get("title", "Unknown conflict")
        details = item.get("details", [])

        print()
        print(f"{Colors.BOLD}Conflict {i}/{len(items)}: {title}{Colors.RESET}")
        print()

        # Parse details into context, options, pros/cons, recommendation, and context-needed fields
        options = []
        recommendation = None
        context_lines = []
        trying_to = None
        need_to_know = None
        context_needed = None
        would_help = None

        for detail in details:
            stripped = detail.strip()
            if stripped.startswith("(") and ")" in stripped[:4]:
                # Option: (A) text or (1) text
                options.append(stripped)
            elif stripped.lower().startswith("pro:"):
                # Pro for previous option
                if options:
                    options[-1] += f"\n      {Colors.SUCCESS}✓ {stripped[4:].strip()}{Colors.RESET}"
            elif stripped.lower().startswith("con:"):
                # Con for previous option
                if options:
                    options[-1] += f"\n      {Colors.FAILURE}✗ {stripped[4:].strip()}{Colors.RESET}"
            elif "**recommendation" in stripped.lower() or stripped.lower().startswith("recommendation:"):
                # Agent's recommendation
                recommendation = stripped.replace("**Recommendation:**", "").replace("**recommendation:**", "").strip()
            elif stripped.lower().startswith("trying to:"):
                trying_to = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("need to know:"):
                need_to_know = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("context needed:"):
                context_needed = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("this would help"):
                would_help = stripped.split(":", 1)[1].strip() if ":" in stripped else stripped
            else:
                context_lines.append(stripped)

        # Determine if this is a "context needed" type ESCALATION
        is_context_type = trying_to or need_to_know or context_needed

        if is_context_type:
            # Show context-needed format
            if trying_to:
                print(f"  {Colors.BOLD}🎯 Trying to:{Colors.RESET} {trying_to}")
            if need_to_know:
                print(f"  {Colors.BOLD}❓ Need to know:{Colors.RESET} {need_to_know}")
            if context_needed:
                print(f"  {Colors.DIM}   {context_needed}{Colors.RESET}")
            if would_help:
                print(f"  {Colors.BOLD}💡 This would help:{Colors.RESET} {would_help}")
            # Show any additional context
            for line in context_lines:
                print(f"  {Colors.DIM}{line}{Colors.RESET}")
        else:
            # Show choice-type format - context first
            for line in context_lines:
                print(f"  {Colors.DIM}{line}{Colors.RESET}")

        # Show options with pros/cons
        if options:
            print()
            print(f"  {Colors.BOLD}Options:{Colors.RESET}")
            for opt in options:
                for line in opt.split('\n'):
                    print(f"    {line}")

        # Show recommendation
        if recommendation:
            print()
            print(f"  {Colors.BOLD}💡 Agent recommends:{Colors.RESET} {recommendation}")

        print()
        print(f"  Enter your decision (or 'pass' to skip):")
        print(f"  > ", end="")

        try:
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            user_input = "pass"

        if user_input.lower() == "pass" or not user_input:
            decisions.append(EscalationDecision(
                conflict_title=title,
                decision="",
                passed=True
            ))
            print(f"  {Colors.DIM}Skipped{Colors.RESET}")
        else:
            decisions.append(EscalationDecision(
                conflict_title=title,
                decision=user_input,
                passed=False
            ))
            print(f"  {Colors.SUCCESS}Decision recorded{Colors.RESET}")

    print(f"{'─'*60}")
    resolved = len([d for d in decisions if not d.passed])
    print(f"  {resolved}/{len(decisions)} conflicts decided")
    print()

    return decisions


def reset_manager_state():
    """Reset the global manager state. Call before starting a work session."""
    global stop_input_listener, manager_input_queue
    stop_input_listener = False
    manager_input_queue = []


def stop_manager_listener():
    """Signal the input listener to stop."""
    global stop_input_listener
    stop_input_listener = True
