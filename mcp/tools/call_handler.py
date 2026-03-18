"""
[ACT] Call — Instant citizen-to-citizen communication via temporary room.

Creates a temporary Space, joins both caller and target, sends the opening
message as a Moment, then wakes the target citizen (injects into their
active session or spawns a new one via the orchestrator queue).

Usage via MCP:
    call(target="@forge", message="Hey, I need your help with the orchestrator")
    call(target="sentinel", message="Security check needed")
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.call")

# State directory for session routing
PROJECT_ROOT = Path(os.environ.get(
    "MIND_PROJECT_ROOT",
    Path(__file__).parent.parent.parent,
))
MIND_STATE = Path(os.environ.get(
    "MIND_STATE_DIR",
    PROJECT_ROOT / "shrine" / "state",
))
MIND_QUEUE = MIND_STATE / "message_queue.jsonl"
MIND_NEURONS = MIND_STATE / "neurons"
MIND_CITIZENS = Path(os.environ.get(
    "MIND_CITIZENS_DIR",
    PROJECT_ROOT / "citizens",
))

TOOL_SCHEMA = {
    "name": "call",
    "description": (
        "[ACT] Call a citizen — creates a temporary room and sends your message. "
        "Like a phone call: instant, synchronous, direct. "
        "Use target='@handle' and message='what you want to say'. "
        "After calling, use place(action='listen') to hear their response "
        "and place(action='speak') to continue the conversation."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "The citizen to call (@handle or handle). Required.",
            },
            "message": {
                "type": "string",
                "description": "Your opening message. Required.",
            },
            "actor_id": {
                "type": "string",
                "description": "Your actor ID. Auto-detected if omitted.",
            },
        },
        "required": ["target", "message"],
    },
}


def _resolve_actor(args: Dict[str, Any], ctx: ServerContext) -> str:
    """Resolve actor ID from args or detect citizen/agent from context."""
    actor_id = args.get("actor_id")
    try:
        from runtime.identity import resolve_actor_id
        return resolve_actor_id(
            actor_id,
            target_dir=ctx.target_dir,
            graph_ops=ctx.graph_ops,
        )
    except Exception:
        return actor_id or "unknown"


def _normalize_handle(target: str) -> str:
    """Strip @ prefix and lowercase."""
    return target.lstrip("@").strip().lower()


# ── Target citizen wake-up ────────────────────────────────────────────────

def _find_active_session(target_handle: str) -> Optional[str]:
    """Find an active neuron session for the target citizen.

    Scans shrine/state/neurons/*.yaml for a session whose
    citizen_handle matches and status is active/busy.

    Returns session_id if found, None otherwise.
    """
    if not MIND_NEURONS.is_dir():
        return None

    try:
        import yaml
    except ImportError:
        # Fallback: parse YAML manually for simple key: value format
        yaml = None

    for neuron_file in MIND_NEURONS.glob("*.yaml"):
        try:
            text = neuron_file.read_text(encoding="utf-8")
            if yaml:
                data = yaml.safe_load(text)
            else:
                # Simple key: value parser
                data = {}
                for line in text.split("\n"):
                    if ": " in line:
                        k, v = line.split(": ", 1)
                        data[k.strip()] = v.strip()

            # Check if this neuron belongs to the target citizen
            meta = data.get("metadata", data)
            citizen = (
                meta.get("citizen_handle")
                or meta.get("handle")
                or data.get("citizen_handle")
                or ""
            )
            status = data.get("status", "")

            if citizen.lower() == target_handle and status in ("active", "busy"):
                session_id = data.get("session_id") or neuron_file.stem
                return session_id
        except Exception:
            continue

    return None


def _inject_into_session(session_id: str, caller_id: str, message: str,
                         room_id: str) -> bool:
    """Write a pending message into a running session's queue.

    The message_inject_hook.py (PostToolUse hook) will pick this up
    and inject it as additionalContext into the running Claude session.
    """
    pending_file = MIND_STATE / f"pending_messages_{session_id}.txt"
    try:
        caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")
        content = (
            f"[CALL from @{caller_name}]\n"
            f"Room: {room_id}\n"
            f"Message: {message}\n"
            f"\n"
            f"Reply using: place(action='speak', place_id='{room_id}', text='...')\n"
        )
        # Append (don't overwrite — there may be other pending messages)
        with open(pending_file, "a", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Injected call message into session {session_id}")
        return True
    except OSError as e:
        logger.warning(f"Failed to inject into session {session_id}: {e}")
        return False


def _wake_citizen(target_handle: str, caller_id: str, message: str,
                  room_id: str) -> bool:
    """Wake a sleeping citizen by queueing a session via the orchestrator.

    Writes to message_queue.jsonl which the orchestrator daemon picks up.
    """
    if not MIND_QUEUE.parent.is_dir():
        logger.warning(f"State dir not found: {MIND_QUEUE.parent}")
        return False

    caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")
    task = (
        f"You have a call from @{caller_name}.\n"
        f"Room: {room_id}\n"
        f"Their message: {message}\n"
        f"\n"
        f"Join the call and respond:\n"
        f"  place(action='speak', place_id='{room_id}', text='your response')"
    )

    request = {
        "voice_text": task,
        "mode": "social",
        "source": "citizen",
        "hotkey": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "citizen_handle": target_handle,
            "citizen_mode": "social",
            "call_room_id": room_id,
            "call_from": caller_name,
        },
    }

    try:
        with open(MIND_QUEUE, "a", encoding="utf-8") as f:
            f.write(json.dumps(request) + "\n")
        logger.info(f"Queued wake for @{target_handle} (call from @{caller_name})")
        return True
    except OSError as e:
        logger.warning(f"Failed to queue wake for @{target_handle}: {e}")
        return False


def _is_human(target_handle: str, graph_ops) -> bool:
    """Check if the target is a human (not an AI citizen)."""
    if not graph_ops:
        return False
    for actor_id in [target_handle, f"CITIZEN_{target_handle}",
                     f"actor_human_{target_handle}_ai"]:
        try:
            result = graph_ops._query(
                "MATCH (a:Actor {id: $id}) RETURN a.type",
                {"id": actor_id},
            )
            if result and result[0] and result[0][0]:
                return str(result[0][0]).lower() == "human"
        except Exception:
            continue
    return False


def _notify_telegram(caller_id: str, message: str, room_id: str) -> bool:
    """Send a call notification to Telegram (for human targets)."""
    try:
        from mcp.tools.send_handler import handle_send
        caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")
        tg_message = (
            f"Call from @{caller_name}\n\n"
            f"{message}\n\n"
            f"Room: {room_id}"
        )
        result = handle_send({
            "platform": "telegram",
            "message": tg_message,
            "handle": caller_name,
        })
        return "Error" not in str(result.get("content", [{}])[0].get("text", ""))
    except Exception as e:
        logger.warning(f"Telegram notification failed: {e}")
        return False


def _notify_target(target_handle: str, caller_id: str, message: str,
                   room_id: str, graph_ops=None) -> str:
    """Notify the target about the call.

    For humans: send Telegram notification.
    For AI citizens: inject into active session or queue wake-up.
    """
    # Check if target is human
    if _is_human(target_handle, graph_ops):
        if _notify_telegram(caller_id, message, room_id):
            return "Sent Telegram notification (human)"
        return "Human target, Telegram failed"

    # AI citizen flow
    # 1. Check for active session
    session_id = _find_active_session(target_handle)
    if session_id:
        if _inject_into_session(session_id, caller_id, message, room_id):
            return f"Injected into active session {session_id[:8]}..."

    # 2. Wake the citizen
    if _wake_citizen(target_handle, caller_id, message, room_id):
        return "Queued wake-up for citizen"

    return "Graph only (no active session, citizen not found locally)"


# ── Main handler ──────────────────────────────────────────────────────────

def handle_call(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Create a call room between caller and target."""
    target = args.get("target")
    message = args.get("message")

    if not target:
        return _err("'target' is required. Who do you want to call?")
    if not message:
        return _err("'message' is required. What do you want to say?")
    if not ctx.graph_ops:
        return _err("No graph connection.")

    caller_id = _resolve_actor(args, ctx)
    target_handle = _normalize_handle(target)
    now = datetime.now(timezone.utc)
    ts_iso = now.isoformat()
    ts_s = int(now.timestamp())

    # Generate room ID and moment ID
    room_id = f"call_{uuid.uuid4().hex[:12]}"
    moment_id = f"moment_{uuid.uuid4().hex[:12]}"

    try:
        # 1. Create temporary room (Space node)
        caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")
        room_name = f"Call: @{caller_name} ↔ @{target_handle}"
        ctx.graph_ops.add_place(
            id=room_id,
            name=room_name,
            type="call",
        )
        ctx.graph_ops._query(
            "MATCH (n:Space {id: $id}) "
            "SET n.temporary = true, n.created_at = $ts, n.created_at_s = $ts_s",
            {"id": room_id, "ts": ts_iso, "ts_s": ts_s},
        )

        # 2. Ensure caller Actor node exists, then join
        ctx.graph_ops._query(
            "MERGE (a:Actor {id: $id}) ON CREATE SET a.type = 'citizen', a.name = $name",
            {"id": caller_id, "name": caller_name},
        )
        ctx.graph_ops.add_presence(caller_id, room_id, present=1.0, visible=1.0)

        # 3. Join target to room (resolve target actor ID)
        target_actor_id = None
        for prefix in [f"CITIZEN_{target_handle}", target_handle]:
            result = ctx.graph_ops._query(
                "MATCH (a:Actor {id: $id}) RETURN a.id",
                {"id": prefix},
            )
            if result:
                target_actor_id = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get("a.id", prefix)
                break

        if not target_actor_id:
            target_actor_id = f"CITIZEN_{target_handle}"
            ctx.graph_ops._query(
                "MERGE (a:Actor {id: $id}) SET a.type = 'citizen', a.name = $name",
                {"id": target_actor_id, "name": target_handle},
            )

        ctx.graph_ops.add_presence(target_actor_id, room_id, present=1.0, visible=1.0)

        # 4. Send opening message as Moment
        ctx.graph_ops.add_moment(
            id=moment_id,
            text=message,
            type="dialogue",
            status="completed",
            speaker=caller_id,
            place_id=room_id,
        )
        ctx.graph_ops._query(
            "MATCH (m:Moment {id: $id}) SET m.created_at_s = $ts_s",
            {"id": moment_id, "ts_s": ts_s},
        )

        # 5. Notify place server (fire-and-forget)
        try:
            from mcp.tools.place_handler import _notify_place_server
            _notify_place_server(room_id, {
                "event": "call_started",
                "room_id": room_id,
                "caller": caller_id,
                "target": target_actor_id,
                "message": message[:200],
                "timestamp": ts_iso,
            })
        except Exception as e:
            logger.debug(f"Place server notification failed for call {room_id}: {e}")

        # 6. Wake target citizen (inject, spawn, or Telegram)
        wake_status = _notify_target(
            target_handle, caller_id, message, room_id,
            graph_ops=ctx.graph_ops,
        )

        # 7. Get immediate response from target via subconscious
        #    Don't wait for LLM — get a graph physics response now.
        #    If the target has an active LLM session, the full response
        #    will appear in the room later (via place listen).
        target_response = _get_subconscious_response(target_handle, message)

        # 8. If we got a response, write it as a Moment in the room
        if target_response:
            response_moment_id = f"moment_{uuid.uuid4().hex[:12]}"
            try:
                ctx.graph_ops.add_moment(
                    id=response_moment_id,
                    text=target_response,
                    type="dialogue",
                    status="completed",
                    speaker=target_actor_id,
                    place_id=room_id,
                )
                ctx.graph_ops._query(
                    "MATCH (m:Moment {id: $id}) SET m.created_at_s = $ts_s, m.subconscious = true",
                    {"id": response_moment_id, "ts_s": int(datetime.now(timezone.utc).timestamp())},
                )
            except Exception as e:
                logger.debug(f"Could not write target response moment: {e}")

        # Build response
        lines = [
            f"Call started with @{target_handle}",
            f"",
            f"  Room: {room_id}",
            f"  You said: {message[:120]}{'...' if len(message) > 120 else ''}",
            f"  Status: {wake_status}",
        ]

        if target_response:
            lines += [
                f"",
                f"@{target_handle} responds:",
                f"",
                target_response,
            ]
        else:
            lines += [
                f"",
                f"@{target_handle} has no brain loaded — waiting for LLM session.",
            ]

        lines += [
            f"",
            f"To continue:",
            f"  place(action='listen', place_id='{room_id}')  — hear more",
            f"  place(action='speak', place_id='{room_id}', text='...')  — reply",
            f"  place(action='leave', place_id='{room_id}')  — hang up",
        ]

        return _ok("\n".join(lines))
    except Exception as e:
        logger.exception("Call failed")
        return _err(f"Starting call: {e}")


def _get_subconscious_response(target_handle: str, stimulus_text: str) -> str:
    """Get an immediate subconscious response from the target citizen.

    Injects the caller's message as a stimulus into the target's L1 graph,
    runs a few ticks, and returns what surfaces in working memory.

    Returns empty string if the target has no brain or if it fails.
    """
    try:
        from runtime.orchestrator.claude_invoker import invoke_subconscious

        result = invoke_subconscious(
            request={
                "voice_text": stimulus_text,
                "metadata": {"citizen_handle": target_handle},
            },
            session_id=f"call_{target_handle}",
            citizen_handle=target_handle,
        )
        return result
    except Exception as e:
        logger.debug(f"Subconscious response failed for {target_handle}: {e}")
        return ""


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
