"""
[ACT] Place — Living Places: join, speak, listen, leave, list, create.

AI citizens interact with shared spaces via this tool. Each action modifies the
knowledge graph (authoritative) and sends a best-effort notification to the
Place Server for real-time distribution.

Usage via MCP:
    place(action="create", name="The Agora", type="forum", description="Public discussion space")
    place(action="join", place_id="place_abc123", actor_id="dragon_slayer")
    place(action="speak", place_id="place_abc123", text="Hello everyone")
    place(action="listen", place_id="place_abc123")
    place(action="leave", place_id="place_abc123")
    place(action="list")
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.place")

PLACE_SERVER_URL = os.environ.get("PLACE_SERVER_URL", "http://localhost:8800")

TOOL_SCHEMA = {
    "name": "place",
    "description": (
        "[ACT] Living Places — join, speak, listen, leave, list, or create shared spaces. "
        "Use action='create' to make a new place, 'join' to enter, 'speak' to send a moment, "
        "'listen' to read recent moments, 'leave' to exit, 'list' to see active places."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["join", "speak", "listen", "leave", "list", "create"],
                "description": "What to do: join/speak/listen/leave a place, list places, or create a new one.",
            },
            "place_id": {
                "type": "string",
                "description": "Place (Space node) ID. Required for join/speak/listen/leave.",
            },
            "actor_id": {
                "type": "string",
                "description": "Actor performing the action. Auto-detected from cwd if omitted.",
            },
            "text": {
                "type": "string",
                "description": "Message content (required for action='speak').",
            },
            "name": {
                "type": "string",
                "description": "Display name for a new place (required for action='create').",
            },
            "type": {
                "type": "string",
                "description": "Place subtype (for action='create'). Default: 'room'.",
            },
            "description": {
                "type": "string",
                "description": "Place description (for action='create').",
            },
            "limit": {
                "type": "integer",
                "description": "Max moments to return (for action='listen', default: 20).",
            },
        },
        "required": ["action"],
    },
}


# ---------------------------------------------------------------------------
# Place Server notification (fire-and-forget)
# ---------------------------------------------------------------------------

def _notify_place_server(place_id: str, event_data: Dict[str, Any]) -> None:
    """Fire-and-forget notification to Place Server."""
    try:
        import urllib.request
        url = f"{PLACE_SERVER_URL}/api/places/{place_id}/notify"
        data = json.dumps(event_data).encode()
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass  # Non-blocking, best-effort


# ---------------------------------------------------------------------------
# Actor resolution
# ---------------------------------------------------------------------------

def _resolve_actor(args: Dict[str, Any], ctx: ServerContext) -> str:
    """Resolve actor ID from args or normalize via runtime helper."""
    actor_id = args.get("actor_id")
    try:
        from runtime.agents import normalize_agent_id
        return normalize_agent_id(actor_id, graph_ops=ctx.graph_ops)
    except Exception:
        return actor_id or "unknown"


# ---------------------------------------------------------------------------
# Timestamps
# ---------------------------------------------------------------------------

def _timestamps() -> tuple:
    """Return (ISO string, unix seconds) for the current moment."""
    now = datetime.now(timezone.utc)
    return now.isoformat(), int(now.timestamp())


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def handle_place(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Dispatch place actions."""
    action = args.get("action")

    if action == "create":
        return _place_create(args, ctx)
    elif action == "join":
        return _place_join(args, ctx)
    elif action == "speak":
        return _place_speak(args, ctx)
    elif action == "listen":
        return _place_listen(args, ctx)
    elif action == "leave":
        return _place_leave(args, ctx)
    elif action == "list":
        return _place_list(args, ctx)
    else:
        return _err(f"Unknown action '{action}'. Use: create, join, speak, listen, leave, list.")


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def _place_create(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Create a new place (Space node in the graph)."""
    name = args.get("name")
    if not name:
        return _err("'name' is required for action='create'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    place_id = f"place_{uuid.uuid4().hex[:12]}"
    place_type = args.get("type", "room")
    description = args.get("description", "")
    created_at, created_at_s = _timestamps()

    try:
        ctx.graph_ops.add_place(
            id=place_id,
            name=name,
            type=place_type,
        )
        # Set additional properties not covered by add_place
        ctx.graph_ops._query(
            "MATCH (n:Space {id: $id}) "
            "SET n.description = $desc, n.created_at = $ts, n.created_at_s = $ts_s",
            {"id": place_id, "desc": description, "ts": created_at, "ts_s": created_at_s},
        )

        _notify_place_server(place_id, {
            "event": "place_created",
            "place_id": place_id,
            "name": name,
            "type": place_type,
            "created_at": created_at,
        })

        return _ok(
            f"Place created:\n"
            f"  ID: {place_id}\n"
            f"  Name: {name}\n"
            f"  Type: {place_type}"
        )
    except Exception as e:
        logger.exception("Place create failed")
        return _err(f"Creating place: {e}")


def _place_join(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Join a place — create AT link from actor to space."""
    place_id = args.get("place_id")
    if not place_id:
        return _err("'place_id' is required for action='join'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    actor_id = _resolve_actor(args, ctx)
    created_at, created_at_s = _timestamps()

    try:
        # Verify place exists
        result = ctx.graph_ops._query(
            "MATCH (p:Space {id: $id}) RETURN p.id, p.name",
            {"id": place_id},
        )
        if not result:
            return _err(f"Place '{place_id}' not found.")

        place_name = result[0][1] if len(result[0]) > 1 else place_id

        # Create AT link (presence)
        ctx.graph_ops.add_presence(actor_id, place_id, present=1.0, visible=1.0)

        _notify_place_server(place_id, {
            "event": "actor_joined",
            "place_id": place_id,
            "actor_id": actor_id,
            "timestamp": created_at,
        })

        return _ok(f"{actor_id} joined '{place_name}' ({place_id})")
    except Exception as e:
        logger.exception("Place join failed")
        return _err(f"Joining place: {e}")


def _place_speak(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Send a moment to a place — create Moment node + IN link + CREATED link."""
    place_id = args.get("place_id")
    text = args.get("text")
    if not place_id:
        return _err("'place_id' is required for action='speak'.")
    if not text:
        return _err("'text' is required for action='speak'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    actor_id = _resolve_actor(args, ctx)
    moment_id = f"moment_{uuid.uuid4().hex[:12]}"
    created_at, created_at_s = _timestamps()

    try:
        # Create Moment node with place and speaker links
        ctx.graph_ops.add_moment(
            id=moment_id,
            text=text,
            type="dialogue",
            status="completed",
            speaker=actor_id,
            place_id=place_id,
        )
        # Set timestamp seconds
        ctx.graph_ops._query(
            "MATCH (m:Moment {id: $id}) SET m.created_at_s = $ts_s",
            {"id": moment_id, "ts_s": created_at_s},
        )

        _notify_place_server(place_id, {
            "event": "moment_created",
            "place_id": place_id,
            "moment_id": moment_id,
            "actor_id": actor_id,
            "text": text,
            "timestamp": created_at,
        })

        return _ok(
            f"Moment sent to {place_id}:\n"
            f"  Moment ID: {moment_id}\n"
            f"  From: {actor_id}\n"
            f"  Text: {text[:120]}{'...' if len(text) > 120 else ''}"
        )
    except Exception as e:
        logger.exception("Place speak failed")
        return _err(f"Speaking in place: {e}")


def _place_listen(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Read recent moments from a place."""
    place_id = args.get("place_id")
    if not place_id:
        return _err("'place_id' is required for action='listen'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    limit = args.get("limit", 20)

    try:
        # Query moments linked to this space, with their speakers
        cypher = """
        MATCH (m:Moment)-[:AT]->(p:Space {id: $place_id})
        OPTIONAL MATCH (a:Actor)-[:SAID]->(m)
        RETURN m.id, m.content, m.type, m.created_at, a.id, a.name
        ORDER BY m.created_at DESC
        LIMIT $limit
        """
        result = ctx.graph_ops._query(cypher, {"place_id": place_id, "limit": limit})

        if not result:
            return _ok(f"No moments in '{place_id}' yet.")

        lines = [f"Recent moments in {place_id} ({len(result)}):\n"]
        # Reverse so oldest first for reading order
        for row in reversed(result):
            m_id, content, m_type, m_ts, a_id, a_name = (
                row[0] if len(row) > 0 else None,
                row[1] if len(row) > 1 else "",
                row[2] if len(row) > 2 else "",
                row[3] if len(row) > 3 else "",
                row[4] if len(row) > 4 else None,
                row[5] if len(row) > 5 else None,
            )
            speaker = a_name or a_id or "unknown"
            content_preview = (content or "")[:200]
            lines.append(f"[{speaker}] {content_preview}")
            lines.append(f"  id={m_id}  type={m_type}  at={m_ts}")
            lines.append("")

        return _ok("\n".join(lines))
    except Exception as e:
        logger.exception("Place listen failed")
        return _err(f"Listening in place: {e}")


def _place_leave(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Leave a place — delete AT link from actor to space."""
    place_id = args.get("place_id")
    if not place_id:
        return _err("'place_id' is required for action='leave'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    actor_id = _resolve_actor(args, ctx)
    created_at, _ = _timestamps()

    try:
        # Delete the specific AT link between this actor and this place
        result = ctx.graph_ops._query(
            "MATCH (a:Actor {id: $actor_id})-[r:AT]->(p:Space {id: $place_id}) "
            "DELETE r RETURN a.id",
            {"actor_id": actor_id, "place_id": place_id},
        )
        if not result:
            return _err(f"{actor_id} is not in '{place_id}'.")

        _notify_place_server(place_id, {
            "event": "actor_left",
            "place_id": place_id,
            "actor_id": actor_id,
            "timestamp": created_at,
        })

        return _ok(f"{actor_id} left '{place_id}'")
    except Exception as e:
        logger.exception("Place leave failed")
        return _err(f"Leaving place: {e}")


def _place_list(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """List active places with participant counts."""
    if not ctx.graph_ops:
        return _err("No graph connection.")

    try:
        cypher = """
        MATCH (p:Space)
        OPTIONAL MATCH (a:Actor)-[:AT]->(p)
        WHERE a IS NULL OR a.type <> 'background'
        RETURN p.id, p.name, p.type, p.description, count(a) AS participants
        ORDER BY participants DESC, p.name
        """
        result = ctx.graph_ops._query(cypher)

        if not result:
            return _ok("No places found. Use action='create' to make one.")

        lines = ["Active Places:\n"]
        for row in result:
            p_id = row[0] if len(row) > 0 else ""
            p_name = row[1] if len(row) > 1 else ""
            p_type = row[2] if len(row) > 2 else ""
            p_desc = row[3] if len(row) > 3 else ""
            count = row[4] if len(row) > 4 else 0

            lines.append(f"{p_name} ({p_type})")
            lines.append(f"  ID: {p_id}")
            lines.append(f"  Participants: {count}")
            if p_desc:
                lines.append(f"  Description: {p_desc[:100]}")
            lines.append("")

        return _ok("\n".join(lines))
    except Exception as e:
        logger.exception("Place list failed")
        return _err(f"Listing places: {e}")


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
