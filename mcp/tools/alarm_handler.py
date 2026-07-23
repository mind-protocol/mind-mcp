"""
[ACT] Alarm — Citizens set their own alarms for autonomous wake.

No cron. Citizens have agency over when they wake. Each alarm is a Moment node in
the citizen's L1 graph (l1_{handle}_graph) — see runtime/orchestrator/graph_alarms.py.

Usage via MCP:
    alarm(action="set", time="2026-03-14T08:00:00Z", reason="Check CI pipeline")
    alarm(action="set", time="08:00", repeat="daily", reason="Morning standup")
    alarm(action="list")
    alarm(action="cancel", alarm_id="wake-abc123def456")
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from runtime.orchestrator import graph_alarms

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
    """Store one wake in the citizen's L1 graph and return its structured record.

    The wake is a Moment node — the citizen's state is its graph, not a file.
    """
    if not time_str:
        raise ValueError("'time' is required")
    if not prompt or not prompt.strip():
        raise ValueError("'prompt' is required")
    if repeat not in {"once", "hourly", "daily", "weekly"}:
        raise ValueError("repeat must be once, hourly, daily, or weekly")

    trigger_at = _parse_time(time_str)
    wake = graph_alarms.create_wake(
        handle=handle,
        scheduled_for=trigger_at,
        prompt=prompt.strip(),
        place=place.strip() if isinstance(place, str) and place.strip() else None,
        repeat=repeat,
    )

    # The alarm/schedule_wake tools report on these keys; keep their contract stable.
    return {
        **wake,
        "citizen": handle,
        "trigger_at": trigger_at,
        "repeat": repeat if repeat != "once" else None,
        "reason": wake["prompt"],
        "place": wake["place"] or None,
        "set_by": handle,
        "set_at": wake["createdAt"],
        "active": True,
    }


def _list_alarms(handle: str) -> Dict:
    """List dormant wakes for a citizen, read from their L1 graph."""
    wakes = graph_alarms.list_wakes(handle)
    if not wakes:
        return {"content": [{"type": "text", "text": "No active alarms."}]}

    lines = [f"Active alarms ({len(wakes)}):"]
    for w in sorted(wakes, key=lambda x: x.get("scheduledFor", "")):
        repeat = f" (repeats {w['repeat']})" if w.get("repeat") and w["repeat"] != "once" else ""
        place = f" @ {w['place']}" if w.get("place") else ""
        lines.append(f"  [{w['id']}] {w.get('scheduledFor', '?')}{repeat}{place} — {w.get('prompt', '')}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


def _cancel_alarm(handle: str, args: Dict) -> Dict:
    """Cancel a wake by ID."""
    alarm_id = args.get("alarm_id")
    if not alarm_id:
        return {"content": [{"type": "text", "text": "Error: 'alarm_id' is required for cancel"}]}

    if not graph_alarms.cancel_wake(handle, alarm_id):
        return {"content": [{"type": "text", "text": f"Alarm {alarm_id} not found"}]}

    logger.info(f"Alarm cancelled for @{handle}: {alarm_id}")
    return {"content": [{"type": "text", "text": f"Alarm {alarm_id} cancelled."}]}
