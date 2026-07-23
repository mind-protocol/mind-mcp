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
import uuid
from datetime import datetime
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
    # Look for citizens dir in project root
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "citizens" / handle / "alarms.jsonl"


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
        today = datetime.now().strftime("%Y-%m-%d")
        dt = datetime.fromisoformat(f"{today}T{time_str}:00")
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
    reason = args.get("reason", "")
    repeat = args.get("repeat", "once")

    if not time_str:
        return {"content": [{"type": "text", "text": "Error: 'time' is required for set action"}]}
    if not reason:
        return {"content": [{"type": "text", "text": "Error: 'reason' is required for set action"}]}

    try:
        trigger_at = _parse_time(time_str)
    except ValueError as e:
        return {"content": [{"type": "text", "text": f"Error parsing time: {e}"}]}

    alarm = {
        "id": f"alarm_{uuid.uuid4().hex[:8]}",
        "citizen": handle,
        "trigger_at": trigger_at,
        "repeat": repeat if repeat != "once" else None,
        "reason": reason,
        "set_by": handle,
        "set_at": datetime.now().isoformat(),
        "active": True,
    }

    alarms_file = _get_alarms_file(handle)
    alarms_file.parent.mkdir(parents=True, exist_ok=True)
    with open(alarms_file, "a") as f:
        f.write(json.dumps(alarm) + "\n")

    logger.info(f"Alarm set for @{handle}: {alarm['id']} at {trigger_at} ({repeat})")

    repeat_str = f", repeats {repeat}" if alarm["repeat"] else ""
    return {
        "content": [{
            "type": "text",
            "text": f"Alarm set: {alarm['id']}\nTime: {trigger_at}{repeat_str}\nReason: {reason}",
        }]
    }


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
        lines.append(f"  [{a['id']}] {a['trigger_at']}{repeat} — {a.get('reason', '')}")

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
    existing = []
    for line in alarms_file.read_text().strip().split("\n"):
        if line.strip():
            try:
                alarm = json.loads(line)
                if alarm.get("id") == alarm_id:
                    alarm["active"] = False
                    found = True
                elif alarm.get("active", True) and alarm.get("id"):
                    existing.append({"id": alarm.get("id"), "name": alarm.get("reason")})
                updated.append(json.dumps(alarm))
            except json.JSONDecodeError:
                updated.append(line)

    if not found:
        from mcp.tools.suggest import suggestion_block
        hint = suggestion_block(alarm_id, "alarm", existing)
        return {"content": [{"type": "text", "text": f"Alarm {alarm_id} not found{hint}"}]}

    alarms_file.write_text("\n".join(updated) + "\n")
    logger.info(f"Alarm cancelled for @{handle}: {alarm_id}")
    return {"content": [{"type": "text", "text": f"Alarm {alarm_id} cancelled."}]}
