"""Simple MCP tool for scheduling a citizen wake-up."""

from __future__ import annotations

from typing import Any, Dict

from mcp.tools.alarm_handler import schedule_wake_record


TOOL_SCHEMA = {
    "name": "schedule_wake",
    "description": (
        "[ACT] Schedule a future wake-up with a time, a prompt to run when waking, "
        "and an optional place providing context."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "time": {
                "type": "string",
                "description": "ISO 8601 datetime or local HH:MM. A past HH:MM means tomorrow.",
            },
            "prompt": {
                "type": "string",
                "description": "The instruction or context delivered when the citizen wakes.",
            },
            "place": {
                "type": "string",
                "description": "Optional place or Space ID associated with the wake-up.",
            },
            "repeat": {
                "type": "string",
                "enum": ["once", "hourly", "daily", "weekly"],
                "default": "once",
            },
            "handle": {
                "type": "string",
                "description": "Citizen to wake. Defaults to system.",
            },
        },
        "required": ["time", "prompt"],
    },
}


def handle_schedule_wake(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        alarm = schedule_wake_record(
            handle=str(args.get("handle") or args.get("_citizen_handle") or "system"),
            time_str=str(args.get("time") or ""),
            prompt=str(args.get("prompt") or ""),
            place=args.get("place"),
            repeat=str(args.get("repeat") or "once"),
        )
    except ValueError as exc:
        return {"content": [{"type": "text", "text": f"Error: {exc}"}], "isError": True}

    place = f"\nPlace: {alarm['place']}" if alarm.get("place") else ""
    repeat = f"\nRepeat: {alarm['repeat']}" if alarm.get("repeat") else ""

    # A scheduled wake is only real if a live alarm watcher will consume it. Warn the caller
    # when the orchestrator is down so the "Wake scheduled" line is never misleading.
    from mcp.tools.orchestrator_heartbeat import liveness_warning
    warning = liveness_warning() or ""

    return {
        "content": [{
            "type": "text",
            "text": (
                f"Wake scheduled: {alarm['id']}\n"
                f"Time: {alarm['trigger_at']}\n"
                f"Prompt: {alarm['prompt']}{place}{repeat}{warning}"
            ),
        }]
    }
