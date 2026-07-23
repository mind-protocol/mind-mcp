"""Citizen-to-citizen messaging, including deliberate self-stimulation.

``talk`` and ``think`` are two intention-revealing views over the same
cognitive ingress and delivery mechanism:

* talk(target, message) sends a thought to any citizen;
* think(message) sends it back to the current citizen.

Both first persist a stimulus Moment and run the target's awareness and
thought ticks through the Home Server, then invoke the target through
``quick_call``. The Home Server remains the only tick owner.
"""

import logging
from typing import Any, Dict

from mcp.tools.cognitive_stimulus import (
    CognitiveStimulusError,
    detect_citizen,
    trigger_cognitive_ticks,
)

logger = logging.getLogger("mind.citizen_message")


TALK_SCHEMA = {
    "name": "talk",
    "description": (
        "[SPEAK] Send a message to any citizen and receive their response. "
        "The message is first persisted as a stimulus and triggers the target's "
        "awareness and thought ticks. "
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
        "it persists a Moment and triggers awareness then thought ticks. "
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
    return _deliver(detect_citizen(), args.get("message"), intent="think")


def _deliver(target: str, raw_message: Any, *, intent: str) -> Dict[str, Any]:
    """Shared implementation for outward talk and inward thought."""
    message = str(raw_message or "").strip()
    if not message:
        return _err("'message' is required and cannot be empty.")

    caller = detect_citizen()
    logger.info("%s @%s -> @%s: %s", intent, caller, target, message[:60])

    try:
        tick_report = trigger_cognitive_ticks(
            target=target,
            content=message,
            source=f"mcp:{intent}",
            caller=caller,
            metadata={"intent": intent},
        )
        from runtime.orchestrator.claude_invoker import quick_call

        response = quick_call(target, message, caller_handle=caller)
        tick_text = (
            f"Stimulus {tick_report['moment_id']} processed by "
            "awareness + thought ticks."
        )
        if intent == "think":
            return _ok(
                f"Self-stimulus sent to @{target}. {tick_text}"
                f"\n\n@{target} reflects:\n\n{response}"
            )
        return _ok(f"{tick_text}\n\n@{target} responds:\n\n{response}")
    except CognitiveStimulusError as exc:
        logger.error("%s stimulus for @%s failed: %s", intent, target, exc)
        return _err(
            f"{intent.capitalize()} with @{target} was not delivered because "
            f"its cognitive ticks did not run: {exc}"
        )
    except Exception as exc:
        logger.exception("%s delivery to @%s failed", intent, target)
        return _err(f"{intent.capitalize()} with @{target} failed: {exc}")


def _normalize_handle(value: Any) -> str:
    return str(value or "").strip().lstrip("@").lower()


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(message: str) -> Dict[str, Any]:
    return {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "isError": True,
    }
