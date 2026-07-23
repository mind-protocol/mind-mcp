"""Orchestrator liveness heartbeat — shared by the alarm watcher and the wake tools.

Problem this solves:
    ``schedule_wake`` / ``alarm`` only *write* a line to ``citizens/{handle}/alarms.jsonl``.
    The line is turned into a real wake by the ``AlarmWatcher`` background thread, which
    lives in a *separate process* (the orchestrator daemon, ``home_server.py``). The MCP
    server that Claude talks to and the orchestrator do not share memory — only the
    filesystem. If the daemon is not running, alarms pile up silently and the tool still
    reports ``Wake scheduled`` as if it worked.

Fix:
    The watcher writes a heartbeat file on every scan. The wake tools read it and can warn
    the caller when no live watcher will ever deliver the alarm they just scheduled.

The heartbeat is a single JSON file (epoch timestamps, no timezone ambiguity). Both the
watcher and the tools resolve its path the same way so they always agree.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("mind.orchestrator_heartbeat")

# The watcher scans every 30s (alarm_watcher.SCAN_INTERVAL). We treat the orchestrator as
# alive if we have seen a heartbeat within a few scan intervals — enough slack to tolerate a
# slow scan or a GC pause without flapping.
DEFAULT_SCAN_INTERVAL = 30
STALE_AFTER_SECONDS = 100  # ~3 scan intervals + margin


def heartbeat_path() -> Path:
    """Resolve the heartbeat file path. Both processes must agree on this."""
    override = os.environ.get("MIND_ORCHESTRATOR_HEARTBEAT")
    if override:
        return Path(override)
    # mcp/tools/<this file> -> project root is three parents up.
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "data" / "orchestrator_heartbeat.json"


def touch_heartbeat(scan_interval: int = DEFAULT_SCAN_INTERVAL) -> None:
    """Record that the alarm watcher is alive and scanning. Called from its run loop.

    Best-effort: a heartbeat write must never crash the watcher.
    """
    path = heartbeat_path()
    payload = {
        "beat_at": time.time(),
        "pid": os.getpid(),
        "scan_interval": int(scan_interval),
        "component": "alarm_watcher",
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload))
        os.replace(tmp, path)  # atomic swap so readers never see a half-written file
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug(f"Could not write orchestrator heartbeat: {exc}")


def read_heartbeat() -> Optional[Dict[str, Any]]:
    """Return the last heartbeat payload, or None if missing/unreadable."""
    path = heartbeat_path()
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug(f"Could not read orchestrator heartbeat: {exc}")
        return None


def orchestrator_liveness(now: Optional[float] = None) -> Tuple[bool, Optional[float], str]:
    """Report whether a live alarm watcher will deliver newly scheduled wakes.

    Returns ``(alive, age_seconds, detail)``:
      - ``alive``       True if a fresh heartbeat exists.
      - ``age_seconds`` Seconds since the last heartbeat, or None if never seen.
      - ``detail``      Human-readable status for surfacing to the caller.
    """
    now = time.time() if now is None else now
    beat = read_heartbeat()
    if not beat:
        return False, None, "no orchestrator heartbeat found — the daemon has never run or was cleared"

    beat_at = beat.get("beat_at")
    if not isinstance(beat_at, (int, float)):
        return False, None, "orchestrator heartbeat is malformed"

    age = max(0.0, now - float(beat_at))
    stale_after = max(STALE_AFTER_SECONDS, int(beat.get("scan_interval", DEFAULT_SCAN_INTERVAL)) * 3 + 10)
    if age <= stale_after:
        return True, age, f"orchestrator alive (last heartbeat {age:.0f}s ago)"
    return False, age, f"orchestrator heartbeat is stale ({age:.0f}s old) — the daemon looks stopped"


def liveness_warning() -> Optional[str]:
    """Return a warning string to append to a wake-scheduling response, or None if healthy."""
    alive, _age, detail = orchestrator_liveness()
    if alive:
        return None
    return (
        "\n\n⚠️  WARNING: this wake was written to disk but WILL NOT FIRE right now — "
        f"{detail}. Start the orchestrator (`python home_server.py` in mind-mcp-v2) so the "
        "alarm watcher can scan and deliver it."
    )
