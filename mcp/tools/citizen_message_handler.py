"""Citizen-to-citizen messaging, including deliberate self-stimulation.

``talk`` and ``think`` are two intention-revealing views over the same
delivery mechanism:

* talk(target, message) sends a thought to any citizen;
* think(message) sends it back to the current citizen.

Both invoke the target citizen through ``quick_call``. Keeping one delivery
path makes self-talk obey the same identity, persistence, and wake behaviour
as every other citizen-to-citizen message.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("mind.citizen_message")


TALK_SCHEMA = {
    "name": "talk",
    "description": (
        "[SPEAK] Send a message to any citizen and receive their response. "
        "Use this for citizen-to-citizen dialogue. The target may also be your "
        "own citizen handle; use think when the intention is explicitly self-directed."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Citizen handle to address, with or without @.",
            },
            "message": {
                "type": "string",
                "description": "Message or thought to send to the citizen.",
            },
        },
        "required": ["target", "message"],
    },
}


THINK_SCHEMA = {
    "name": "think",
    "description": (
        "[THINK] Send a message to yourself using the same citizen messaging "
        "mechanism as talk. This deliberately self-stimulates your cognition: "
        "use it to bring a subject back under attention, think more about it, "
        "or continue an internal line of inquiry."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": (
                    "Thought to send back to yourself so it receives another "
                    "cognitive pass."
                ),
            },
        },
        "required": ["message"],
    },
}


def handle_talk(args: Dict[str, Any]) -> Dict[str, Any]:
    """Address any citizen through the shared citizen messaging path."""
    target = _normalize_handle(args.get("target"))
    if not target:
        return _err("'target' is required and cannot be empty.")
    return _deliver(target, args.get("message"), intent="talk")


def handle_self_think(args: Dict[str, Any]) -> Dict[str, Any]:
    """Address the current citizen to create a deliberate self-stimulus."""
    return _deliver(_detect_citizen(), args.get("message"), intent="think")


def _deliver(target: str, raw_message: Any, *, intent: str) -> Dict[str, Any]:
    """Shared implementation for outward talk and inward thought."""
    message = str(raw_message or "").strip()
    if not message:
        return _err("'message' is required and cannot be empty.")

    caller = _detect_citizen()
    logger.info("%s @%s -> @%s: %s", intent, caller, target, message[:60])

    try:
        from runtime.orchestrator.claude_invoker import quick_call

        response = quick_call(target, message, caller_handle=caller)
        if intent == "think":
            return _ok(f"Self-stimulus sent to @{target}.\n\n@{target} reflects:\n\n{response}")
        return _ok(f"@{target} responds:\n\n{response}")
    except Exception as exc:
        logger.exception("%s delivery to @%s failed", intent, target)
        return _err(f"{intent.capitalize()} with @{target} failed: {exc}")


def _detect_citizen() -> str:
    """Resolve the current citizen from explicit runtime identity signals."""
    handle = _normalize_handle(os.getenv("CITIZEN_HANDLE"))
    if handle:
        return handle

    parts = Path.cwd().parts
    for index, part in enumerate(parts):
        if part.lower() == "citizens" and index + 1 < len(parts):
            return _normalize_handle(parts[index + 1])

    actor_id = _normalize_handle(os.getenv("ACTOR_ID"))
    for prefix in ("citizen_", "agent_", "actor_"):
        if actor_id.lower().startswith(prefix):
            return actor_id[len(prefix):]
    return actor_id or "mind"


def _normalize_handle(value: Any) -> str:
    return str(value or "").strip().lstrip("@").lower()


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(message: str) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "isError": True,
    }
