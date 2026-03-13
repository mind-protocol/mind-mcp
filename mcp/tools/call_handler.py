"""
[ACT] Call — Instant citizen-to-citizen communication via temporary room.

Creates a temporary Space, joins both caller and target, sends the opening
message as a Moment. Participants continue via place(speak/listen).

Usage via MCP:
    call(target="@forge", message="Hey, I need your help with the orchestrator")
    call(target="sentinel", message="Security check needed")
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.call")

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
    """Resolve actor ID from args or normalize via runtime helper."""
    actor_id = args.get("actor_id")
    try:
        from runtime.agents import normalize_agent_id
        return normalize_agent_id(actor_id, graph_ops=ctx.graph_ops)
    except Exception:
        return actor_id or "unknown"


def _normalize_handle(target: str) -> str:
    """Strip @ prefix and lowercase."""
    return target.lstrip("@").strip().lower()


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
        room_name = f"Call: @{caller_id.replace('CITIZEN_', '')} ↔ @{target_handle}"
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
            {"id": caller_id, "name": caller_id.replace("CITIZEN_", "")},
        )
        ctx.graph_ops.add_presence(caller_id, room_id, present=1.0, visible=1.0)

        # 3. Join target to room (resolve target actor ID)
        target_actor_id = None
        # Try CITIZEN_ prefix first
        for prefix in [f"CITIZEN_{target_handle}", target_handle]:
            result = ctx.graph_ops._query(
                "MATCH (a:Actor {id: $id}) RETURN a.id",
                {"id": prefix},
            )
            if result:
                target_actor_id = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get("a.id", prefix)
                break

        if not target_actor_id:
            # Actor node doesn't exist yet — create a minimal one so AT link works
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
        except Exception:
            pass

        return _ok(
            f"Call started with @{target_handle}\n"
            f"\n"
            f"  Room: {room_id}\n"
            f"  Name: {room_name}\n"
            f"  Message sent: {message[:120]}{'...' if len(message) > 120 else ''}\n"
            f"\n"
            f"To continue the conversation:\n"
            f"  place(action='listen', place_id='{room_id}')  — hear their response\n"
            f"  place(action='speak', place_id='{room_id}', text='...')  — reply\n"
            f"  place(action='leave', place_id='{room_id}')  — hang up"
        )
    except Exception as e:
        logger.exception("Call failed")
        return _err(f"Starting call: {e}")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
