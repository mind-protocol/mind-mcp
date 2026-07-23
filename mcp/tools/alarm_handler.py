"""
[ACT] Alarm — Citizens set their own alarms for autonomous wake.

No cron. Citizens have agency over when they wake. Alarms are per-citizen,
stored in citizens/{handle}/alarms.jsonl.

Usage via MCP:
    alarm(action="set", time="2026-03-14T08:00:00Z", reason="Check CI pipeline")
    alarm(action="set", time="08:00", repeat="daily", reason="Morning standup")
    alarm(action="list")
    alarm(action="cancel", alarm_id="alarm_abc123")
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("mind.alarm")

TOOL_SCHEMA = {
    "name": "alarm",
    "description": "Set, list, or cancel alarms. Citizens decide when they wake — no cron. Alarms fire at the specified time and enqueue a wake message.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["set", "list", "cancel"],
                "description": "Action to perform",
            },
            "time": {
                "type": "string",
                "description": "When to fire (ISO 8601 datetime or HH:MM for today). Required for 'set'.",
            },
            "reason": {
                "type": "string",
                "description": "Why this alarm exists — shown when citizen wakes. Required for 'set'.",
            },
            "repeat": {
                "type": "string",
                "enum": ["once", "hourly", "daily", "weekly"],
                "description": "Repeat schedule. Default: 'once'.",
            },
            "alarm_id": {
                "type": "string",
                "description": "Alarm ID to cancel. Required for 'cancel'.",
            },
        },
        "required": ["action"],
    },
}


def _get_alarms_file(handle: str) -> Path:
    """Return the alarms file path for a citizen."""
    project_root = Path(__file__).resolve().parent.parent.parent
    citizens_dir = Path(os.environ.get("MIND_CITIZENS_DIR", project_root / "citizens"))
    return citizens_dir / handle / "alarms.jsonl"


def _parse_time(time_str: str) -> str:
    """Parse a time string into ISO 8601 format."""
    # Already ISO format
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.isoformat()
    except ValueError:
        pass

    # HH:MM format — assume today
    try:
        now = datetime.now()
        dt = datetime.fromisoformat(f"{now:%Y-%m-%d}T{time_str}:00")
        if dt <= now:
            dt += timedelta(days=1)
        return dt.isoformat()
    except ValueError:
        pass

    raise ValueError(f"Cannot parse time: {time_str}")


def handle_alarm(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle alarm tool calls."""
    action = arguments.get("action", "list")

    # Determine calling citizen (from context or default)
    handle = arguments.get("_citizen_handle", "system")

    if action == "set":
        return _set_alarm(handle, arguments)
    elif action == "list":
        return _list_alarms(handle)
    elif action == "cancel":
        return _cancel_alarm(handle, arguments)
    else:
        return {"content": [{"type": "text", "text": f"Unknown action: {action}"}]}


def _set_alarm(handle: str, args: Dict) -> Dict:
    """Set a new alarm for a citizen."""
    time_str = args.get("time")
    prompt = args.get("prompt") or args.get("reason", "")
    repeat = args.get("repeat", "once")

    if not time_str:
        return {"content": [{"type": "text", "text": "Error: 'time' is required for set action"}]}
    if not prompt:
        return {"content": [{"type": "text", "text": "Error: 'reason' is required for set action"}]}

    try:
        alarm = schedule_wake_record(
            handle=handle,
            time_str=time_str,
            prompt=prompt,
            place=args.get("place") or args.get("place_id"),
            repeat=repeat,
        )
    except ValueError as e:
        return {"content": [{"type": "text", "text": f"Error parsing time: {e}"}]}

    repeat_str = f", repeats {repeat}" if alarm["repeat"] else ""
    place_str = f"\nPlace: {alarm['place']}" if alarm.get("place") else ""

    # An alarm is only real if a live watcher will consume it. Warn when the orchestrator is
    # down so the "Alarm set" line is never misleading.
    from mcp.tools.orchestrator_heartbeat import liveness_warning
    warning = liveness_warning() or ""

    return {
        "content": [{
            "type": "text",
            "text": (
                f"Alarm set: {alarm['id']}\nTime: {alarm['trigger_at']}{repeat_str}"
                f"\nPrompt: {alarm['prompt']}{place_str}{warning}"
            ),
        }]
    }


def schedule_wake_record(
    *,
    handle: str,
    time_str: str,
    prompt: str,
    place: str | None = None,
    repeat: str = "once",
) -> Dict[str, Any]:
    """Persist one wake schedule and return its structured record."""
    if not time_str:
        raise ValueError("'time' is required")
    if not prompt or not prompt.strip():
        raise ValueError("'prompt' is required")
    if repeat not in {"once", "hourly", "daily", "weekly"}:
        raise ValueError("repeat must be once, hourly, daily, or weekly")

    trigger_at = _parse_time(time_str)
    alarm = {
        "id": f"alarm_{uuid.uuid4().hex[:8]}",
        "citizen": handle,
        "trigger_at": trigger_at,
        "repeat": repeat if repeat != "once" else None,
        "reason": prompt.strip(),
        "prompt": prompt.strip(),
        "place": place.strip() if isinstance(place, str) and place.strip() else None,
        "set_by": handle,
        "set_at": datetime.now().isoformat(),
        "active": True,
    }

    alarms_file = _get_alarms_file(handle)
    alarms_file.parent.mkdir(parents=True, exist_ok=True)
    with open(alarms_file, "a") as f:
        f.write(json.dumps(alarm) + "\n")

    logger.info(f"Wake scheduled for @{handle}: {alarm['id']} at {trigger_at} ({repeat})")
    return alarm


def _list_alarms(handle: str) -> Dict:
    """List active alarms for a citizen."""
    alarms_file = _get_alarms_file(handle)
    if not alarms_file.exists():
        return {"content": [{"type": "text", "text": "No alarms set."}]}

    alarms = []
    for line in alarms_file.read_text().strip().split("\n"):
        if line.strip():
            try:
                alarm = json.loads(line)
                if alarm.get("active", True):
                    alarms.append(alarm)
            except json.JSONDecodeError:
                pass

    if not alarms:
        return {"content": [{"type": "text", "text": "No active alarms."}]}

    lines = [f"Active alarms ({len(alarms)}):"]
    for a in sorted(alarms, key=lambda x: x.get("trigger_at", "")):
        repeat = f" (repeats {a['repeat']})" if a.get("repeat") else ""
        place = f" @ {a['place']}" if a.get("place") else ""
        lines.append(
            f"  [{a['id']}] {a['trigger_at']}{repeat}{place} — "
            f"{a.get('prompt') or a.get('reason', '')}"
        )

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


def _cancel_alarm(handle: str, args: Dict) -> Dict:
    """Cancel an alarm by ID."""
    alarm_id = args.get("alarm_id")
    if not alarm_id:
        return {"content": [{"type": "text", "text": "Error: 'alarm_id' is required for cancel"}]}

    alarms_file = _get_alarms_file(handle)
    if not alarms_file.exists():
        return {"content": [{"type": "text", "text": f"Alarm {alarm_id} not found"}]}

    # Rewrite file with alarm deactivated
    updated = []
    found = False
    for line in alarms_file.read_text().strip().split("\n"):
        if line.strip():
            try:
                alarm = json.loads(line)
                if alarm.get("id") == alarm_id:
                    alarm["active"] = False
                    found = True
                updated.append(json.dumps(alarm))
            except json.JSONDecodeError:
                updated.append(line)

    if not found:
        return {"content": [{"type": "text", "text": f"Alarm {alarm_id} not found"}]}

    alarms_file.write_text("\n".join(updated) + "\n")
    logger.info(f"Alarm cancelled for @{handle}: {alarm_id}")
    return {"content": [{"type": "text", "text": f"Alarm {alarm_id} cancelled."}]}
