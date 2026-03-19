"""
[ACT] Call — File-based communication between citizens.

Usage:
    call(path="citizens/forge/calls/topic.md", message="Hey, need help")

Flow:
1. Append message to file (with timestamp + citizen handle)
2. Block — poll file for changes (1s interval, 5min timeout)
3. When file changes: return the diff (new lines)
4. Claude sees the diff, can call() again to continue

Each call() is one turn. The file is the transcript.
Multiple citizens can call the same file = shared room.

TG/WH integration: separate scripts do TTS on diffs and send to external platforms.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("mind.call")

POLL_INTERVAL = 1.0   # seconds between checks
POLL_TIMEOUT = 300.0  # 5 minutes max wait

TOOL_SCHEMA = {
    "name": "call",
    "description": (
        "[ACT] Call a citizen or location. "
        "Direct call: call(target='@forge', message='How does the bridge work?') → invokes @forge directly, returns their answer. "
        "File call: call(path='citizens/forge/calls/topic.md', message='Hey') → writes to shared file, waits for response. "
        "Use direct call for quick questions. Use file call for ongoing conversations."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Direct call: citizen handle (e.g. '@forge' or 'forge'). Invokes them with your question and returns their answer.",
            },
            "path": {
                "type": "string",
                "description": "File call: path to the call file. Created if it doesn't exist.",
            },
            "message": {
                "type": "string",
                "description": "The question or message.",
            },
        },
        "required": ["message"],
    },
}


def handle_call_file_watcher(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Call a citizen directly or write to a shared call file."""
    target = args.get("target", "").strip().lstrip("@")
    message = args.get("message", "").strip()
    path_str = args.get("path", "").strip()

    # ── Direct call: invoke the target citizen with the question ──
    if target and message:
        caller = _detect_citizen()
        logger.info(f"direct call @{caller} → @{target}: {message[:60]}")
        try:
            from runtime.orchestrator.claude_invoker import quick_call
            response = quick_call(target, message, caller_handle=caller)
            return _ok(f"@{target} says:\n\n{response}")
        except Exception as e:
            logger.error(f"direct call failed: {e}")
            return _err(f"Direct call to @{target} failed: {e}")

    # Default: business/SYNC_Project.md in the repo root
    if not path_str:
        cwd = Path.cwd()
        # Walk up to find business/SYNC_Project.md
        search = cwd
        for _ in range(10):
            candidate = search / "business" / "SYNC_Project.md"
            if candidate.exists():
                path_str = str(candidate)
                break
            if search.parent == search:
                break
            search = search.parent
        if not path_str:
            return _err("No path given and business/SYNC_Project.md not found.")

    path = Path(path_str)
    if not path.is_absolute():
        # Resolve relative to citizen's working directory
        cwd = Path.cwd()
        path = (cwd / path).resolve()
    else:
        path = path.resolve()

    # Detect who's calling
    citizen = _detect_citizen()

    # Create parent dirs
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Write message
    if message:
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] @{citizen}: {message}\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
        logger.info(f"call @{citizen} → {path.name}: {message[:60]}")

        # Sync to graph
        try:
            from runtime.sync.filesystem_to_graph import sync_file
            sync_file(str(path), actor_handle=citizen)
        except Exception:
            pass

    # Snapshot current state
    current_lines = _read_lines(path)
    current_count = len(current_lines)
    current_mtime = _get_mtime(path)

    # Step 2: Poll for changes
    start_time = time.time()
    while time.time() - start_time < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)

        new_mtime = _get_mtime(path)
        if new_mtime <= current_mtime:
            continue

        # File changed — compute diff
        new_lines = _read_lines(path)
        diff = new_lines[current_count:]

        if not diff:
            # mtime changed but no new lines (e.g., whitespace)
            current_mtime = new_mtime
            continue

        # Filter out our own writes (don't echo back)
        other_lines = [l for l in diff if f"@{citizen}:" not in l]

        if not other_lines:
            # Only our own echo — keep waiting
            current_count = len(new_lines)
            current_mtime = new_mtime
            continue

        # Got a response
        diff_text = "".join(other_lines)
        return _ok(diff_text.strip())

    # Timeout
    return _ok("(no response after 5 minutes)")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_citizen() -> str:
    """Detect current citizen from working directory."""
    cwd = Path.cwd()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == "citizens" and i + 1 < len(parts):
            return parts[i + 1]
    return "unknown"


def _read_lines(path: Path) -> list[str]:
    """Read all lines from a file."""
    if not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError:
        return []


def _get_mtime(path: Path) -> float:
    """Get file modification time."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}], "isError": True}
