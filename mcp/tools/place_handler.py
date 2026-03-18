"""
[ACT] Place — Living Places: join, speak, listen, leave, list, create, call, grant_access, revoke_access.

AI citizens interact with shared spaces via this tool. Each action modifies the
knowledge graph (authoritative) and sends a best-effort notification to the
Place Server for real-time distribution.

Private spaces use AES-256-GCM encryption. Content is encrypted/decrypted
transparently — callers see plaintext; the graph stores ciphertext. Access is
managed via sealed-box key exchange (X25519).

Usage via MCP:
    place(action="create", name="The Agora", type="forum", description="Public discussion space")
    place(action="create", name="War Room", type="council", visibility="private")
    place(action="join", place_id="place_abc123", actor_id="dragon_slayer")
    place(action="speak", place_id="place_abc123", text="Hello everyone")
    place(action="listen", place_id="place_abc123")
    place(action="leave", place_id="place_abc123")
    place(action="list")
    place(action="call", target_actor_id="voce")
    place(action="call", participants=["voce", "anima", "piazza"])
    place(action="grant_access", place_id="place_abc123", target_actor_id="new_member", role="member")
    place(action="revoke_access", place_id="place_abc123", target_actor_id="ex_member")

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.place")

PLACE_SERVER_URL = os.environ.get("PLACE_SERVER_URL", "http://localhost:8800")

# Path to mind-protocol Python crypto library
MIND_PROTOCOL_PYTHON = os.environ.get(
    "MIND_PROTOCOL_PYTHON",
    str(Path("/home/mind-protocol/mind-protocol/python")),
)

# Directory containing actor .keys/ subdirectories
MIND_KEYS_DIR = os.environ.get(
    "MIND_KEYS_DIR",
    str(Path("/home/mind-protocol/cities-of-light/citizens")),
)

TOOL_SCHEMA = {
    "name": "place",
    "description": (
        "[ACT] Living Places — join, speak, listen, leave, list, create, call, grant_access, or revoke_access. "
        "Use action='create' to make a new place (with optional visibility='private'), "
        "'join' to enter, 'speak' to send a moment, "
        "'listen' to read recent moments, 'leave' to exit, 'list' to see active places, "
        "'call' to start a private 1:1 or group call with another actor, "
        "'grant_access' to give another actor access to a private place, "
        "'revoke_access' to remove an actor's access and rotate the space key."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["join", "speak", "listen", "leave", "list", "create", "call", "grant_access", "revoke_access"],
                "description": "What to do: join/speak/listen/leave a place, list places, create a new one, call another actor (creates private space + joins both), grant_access to a private place, or revoke_access (removes access + rotates key).",
            },
            "place_id": {
                "type": "string",
                "description": "Place (Space node) ID. Required for join/speak/listen/leave/grant_access.",
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
            "visibility": {
                "type": "string",
                "enum": ["public", "private"],
                "description": "Space visibility (for action='create'). Default: 'public'.",
            },
            "target_actor_id": {
                "type": "string",
                "description": "Target actor for action='call' (who to call), action='grant_access' (who to grant access to), or action='revoke_access' (who to revoke).",
            },
            "participants": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of actor IDs to include in a group call (for action='call'). Overrides target_actor_id.",
            },
            "role": {
                "type": "string",
                "enum": ["owner", "admin", "member"],
                "description": "Access role to grant (for action='grant_access'). Default: 'member'.",
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
# Crypto library loader (lazy)
# ---------------------------------------------------------------------------

def _ensure_crypto_path() -> None:
    """Add mind-protocol/python to sys.path so 'from crypto import ...' works."""
    if MIND_PROTOCOL_PYTHON not in sys.path:
        sys.path.insert(0, MIND_PROTOCOL_PYTHON)


def _import_crypto():
    """Lazy-import the crypto facade. Returns the module or None."""
    try:
        _ensure_crypto_path()
        import crypto
        return crypto
    except ImportError as e:
        logger.warning(f"Crypto library not available: {e}")
        return None


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
    except Exception as e:
        logger.debug(f"Place server notification failed for {place_id}: {e}")


# ---------------------------------------------------------------------------
# Actor resolution
# ---------------------------------------------------------------------------

def _resolve_actor(args: Dict[str, Any], ctx: ServerContext) -> str:
    """Resolve actor ID from args or detect citizen/agent from context."""
    actor_id = args.get("actor_id")
    try:
        from runtime.identity import resolve_actor_id as normalize_agent_id
        return normalize_agent_id(
            actor_id,
            target_dir=ctx.target_dir,
            graph_ops=ctx.graph_ops,
        )
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
# Encryption helpers
# ---------------------------------------------------------------------------

def _resolve_space_visibility(place_id: str, graph_ops) -> bool:
    """Check whether a Space is private.

    Returns True if visibility == 'private', False otherwise.
    Missing visibility property defaults to 'public' (False).
    """
    try:
        result = graph_ops._query(
            "MATCH (s:Space {id: $id}) RETURN s.visibility",
            {"id": place_id},
        )
        if result and result[0] and result[0][0]:
            return str(result[0][0]).lower() == "private"
    except Exception as e:
        logger.warning(f"Could not resolve space visibility for {place_id}: {e}")
    return False


def _get_space_key(actor_id: str, place_id: str, graph_ops) -> Optional[bytes]:
    """Retrieve and decrypt the space key for an actor.

    Looks up the HAS_ACCESS link between the actor and the space (or parent
    spaces up to 5 levels) to find the sealed-box-encrypted space key, then
    decrypts it using the actor's private key from disk.

    Returns the raw 32-byte space key, or None if access is unavailable.
    """
    crypto = _import_crypto()
    if not crypto:
        logger.warning("Crypto library not available — cannot retrieve space key")
        return None

    # 1. Find encrypted_key from HAS_ACCESS link (direct, then parent hierarchy)
    encrypted_key = None
    access_role = None

    # Direct access
    try:
        result = graph_ops._query(
            "MATCH (a:Actor {id: $actor_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "RETURN r.encrypted_key, r.role",
            {"actor_id": actor_id, "place_id": place_id},
        )
        if result and result[0] and result[0][0]:
            encrypted_key = result[0][0]
            access_role = result[0][1] if len(result[0]) > 1 else None
    except Exception as e:
        logger.debug(f"Direct HAS_ACCESS lookup failed: {e}")

    # Parent hierarchy (up to 5 levels) if no direct access
    if not encrypted_key:
        try:
            result = graph_ops._query(
                "MATCH (a:Actor {id: $actor_id})-[r:HAS_ACCESS]->(parent:Space) "
                "MATCH (s:Space {id: $place_id})-[:IN*1..5]->(parent) "
                "RETURN r.encrypted_key, r.role "
                "LIMIT 1",
                {"actor_id": actor_id, "place_id": place_id},
            )
            if result and result[0] and result[0][0]:
                encrypted_key = result[0][0]
                access_role = result[0][1] if len(result[0]) > 1 else None
        except Exception as e:
            logger.debug(f"Parent hierarchy HAS_ACCESS lookup failed: {e}")

    if not encrypted_key:
        logger.debug(f"No HAS_ACCESS link found for {actor_id} -> {place_id}")
        return None

    # 2. Load actor's private key from disk
    try:
        keys_dir = os.path.join(MIND_KEYS_DIR, actor_id, ".keys")
        actor_keys = crypto.load_actor_keys(keys_dir)
    except FileNotFoundError:
        logger.warning(f"No key files found for actor '{actor_id}' at {keys_dir}")
        return None
    except Exception as e:
        logger.warning(f"Failed to load keys for actor '{actor_id}': {e}")
        return None

    # 3. Decrypt space key using sealed box
    try:
        space_key = crypto.decrypt_space_key_for_actor(
            encrypted_key=encrypted_key,
            actor_public_key=actor_keys["public_key"],
            actor_private_key=actor_keys["private_key"],
        )
        return space_key
    except Exception as e:
        logger.warning(f"Failed to decrypt space key for {actor_id} -> {place_id}: {e}")
        return None


def _get_actor_public_key(actor_id: str, graph_ops) -> Optional[bytes]:
    """Get an actor's public key from the graph.

    Returns raw 32-byte public key, or None if not found.
    """
    import base64
    try:
        result = graph_ops._query(
            "MATCH (a:Actor {id: $id}) RETURN a.public_key",
            {"id": actor_id},
        )
        if result and result[0] and result[0][0]:
            return base64.b64decode(result[0][0])
    except Exception as e:
        logger.debug(f"Could not get public key for {actor_id}: {e}")
    return None


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
    elif action == "call":
        return _place_call(args, ctx)
    elif action == "grant_access":
        return _place_grant_access(args, ctx)
    elif action == "revoke_access":
        return _place_revoke_access(args, ctx)
    else:
        return _err(
            f"Unknown action '{action}'. "
            "Use: create, join, speak, listen, leave, list, call, grant_access, revoke_access."
        )


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def _place_create(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Create a new place (Space node in the graph).

    If visibility='private', generates a space key, wraps it for the creator
    via sealed box, and stores the HAS_ACCESS link with role='owner'.
    """
    name = args.get("name")
    if not name:
        return _err("'name' is required for action='create'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    place_id = f"place_{uuid.uuid4().hex[:12]}"
    place_type = args.get("type", "room")
    description = args.get("description", "")
    visibility = args.get("visibility", "public")
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
            "SET n.description = $desc, n.created_at = $ts, "
            "n.created_at_s = $ts_s, n.visibility = $vis",
            {
                "id": place_id,
                "desc": description,
                "ts": created_at,
                "ts_s": created_at_s,
                "vis": visibility,
            },
        )

        result_lines = [
            f"Place created:",
            f"  ID: {place_id}",
            f"  Name: {name}",
            f"  Type: {place_type}",
            f"  Visibility: {visibility}",
        ]

        # If private, set up encryption
        if visibility == "private":
            crypto = _import_crypto()
            if not crypto:
                return _err(
                    "Crypto library not available — cannot create private space. "
                    "Ensure mind-protocol/python/crypto is installed."
                )

            actor_id = _resolve_actor(args, ctx)

            # Get creator's public key from graph
            creator_pub_key = _get_actor_public_key(actor_id, ctx.graph_ops)
            if not creator_pub_key:
                return _err(
                    f"Actor '{actor_id}' has no public_key registered in the graph. "
                    "Register it first (set a.public_key on the Actor node)."
                )

            # Generate space key
            space_key = crypto.generate_space_key()

            # Wrap space key for creator
            encrypted_key = crypto.encrypt_space_key_for_actor(space_key, creator_pub_key)

            # Create HAS_ACCESS link with role='owner' and encrypted_key
            ctx.graph_ops._query(
                "MATCH (a:Actor {id: $actor_id}), (s:Space {id: $place_id}) "
                "MERGE (a)-[r:HAS_ACCESS]->(s) "
                "SET r.role = 'owner', r.encrypted_key = $ekey, "
                "r.granted_at = $ts, r.granted_by = $actor_id",
                {
                    "actor_id": actor_id,
                    "place_id": place_id,
                    "ekey": encrypted_key,
                    "ts": created_at,
                },
            )

            result_lines.append(f"  Owner: {actor_id}")
            result_lines.append(f"  Encryption: space key generated and wrapped for owner")

        _notify_place_server(place_id, {
            "event": "place_created",
            "place_id": place_id,
            "name": name,
            "type": place_type,
            "visibility": visibility,
            "created_at": created_at,
        })

        return _ok("\n".join(result_lines))
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
    """Send a moment to a place — create Moment node + IN link + CREATED link.

    If the space is private, the text is encrypted with AES-256-GCM before
    being stored in the graph. The Moment node gets an 'encrypted' flag.
    """
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
    is_private = _resolve_space_visibility(place_id, ctx.graph_ops)
    encrypted = False
    store_text = text

    # Encrypt content for private spaces
    if is_private:
        crypto = _import_crypto()
        if not crypto:
            return _err("Crypto library not available — cannot speak in private space.")

        space_key = _get_space_key(actor_id, place_id, ctx.graph_ops)
        if not space_key:
            return _err(
                f"No access to private space '{place_id}'. "
                "Use grant_access to obtain a space key."
            )

        try:
            store_text = crypto.encrypt_content(text, space_key)
            encrypted = True
        except Exception as e:
            logger.exception("Content encryption failed")
            return _err(f"Encrypting content: {e}")

    try:
        # Create Moment node with place and speaker links
        ctx.graph_ops.add_moment(
            id=moment_id,
            text=store_text,
            type="dialogue",
            status="completed",
            speaker=actor_id,
            place_id=place_id,
        )
        # Set timestamp seconds and encrypted flag
        ctx.graph_ops._query(
            "MATCH (m:Moment {id: $id}) "
            "SET m.created_at_s = $ts_s, m.encrypted = $encrypted",
            {"id": moment_id, "ts_s": created_at_s, "encrypted": encrypted},
        )

        # Notify with plaintext for real-time delivery (server-side only,
        # not persisted — the graph has ciphertext)
        _notify_place_server(place_id, {
            "event": "moment_created",
            "place_id": place_id,
            "moment_id": moment_id,
            "actor_id": actor_id,
            "text": text if not encrypted else "[encrypted]",
            "encrypted": encrypted,
            "timestamp": created_at,
        })

        return _ok(
            f"Moment sent to {place_id}:\n"
            f"  Moment ID: {moment_id}\n"
            f"  From: {actor_id}\n"
            f"  Encrypted: {encrypted}\n"
            f"  Text: {text[:120]}{'...' if len(text) > 120 else ''}"
        )
    except Exception as e:
        logger.exception("Place speak failed")
        return _err(f"Speaking in place: {e}")


def _place_listen(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Read recent moments from a place.

    If the space is private, moments are decrypted transparently using the
    caller's space key. Moments that cannot be decrypted show '[encrypted]'.
    """
    place_id = args.get("place_id")
    if not place_id:
        return _err("'place_id' is required for action='listen'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    limit = args.get("limit", 20)
    is_private = _resolve_space_visibility(place_id, ctx.graph_ops)
    space_key = None

    # Pre-fetch space key for private spaces
    if is_private:
        actor_id = _resolve_actor(args, ctx)
        crypto = _import_crypto()
        if not crypto:
            return _err("Crypto library not available — cannot listen in private space.")

        space_key = _get_space_key(actor_id, place_id, ctx.graph_ops)
        if not space_key:
            return _err(
                f"No access to private space '{place_id}'. "
                "Use grant_access to obtain a space key."
            )

    try:
        # Query moments linked to this space, with their speakers
        cypher = """
        MATCH (m:Moment)-[:AT]->(p:Space {id: $place_id})
        OPTIONAL MATCH (a:Actor)-[:SAID]->(m)
        RETURN m.id, m.content, m.type, m.created_at, a.id, a.name, m.encrypted
        ORDER BY m.created_at DESC
        LIMIT $limit
        """
        result = ctx.graph_ops._query(cypher, {"place_id": place_id, "limit": limit})

        if not result:
            return _ok(f"No moments in '{place_id}' yet.")

        lines = [f"Recent moments in {place_id} ({len(result)}):\n"]
        # Reverse so oldest first for reading order
        for row in reversed(result):
            m_id = row[0] if len(row) > 0 else None
            content = row[1] if len(row) > 1 else ""
            m_type = row[2] if len(row) > 2 else ""
            m_ts = row[3] if len(row) > 3 else ""
            a_id = row[4] if len(row) > 4 else None
            a_name = row[5] if len(row) > 5 else None
            m_encrypted = row[6] if len(row) > 6 else False

            speaker = a_name or a_id or "unknown"

            # Decrypt if needed
            display_content = content or ""
            if m_encrypted and space_key and content:
                try:
                    crypto = _import_crypto()
                    if crypto:
                        display_content = crypto.decrypt_content(content, space_key)
                except Exception as e:
                    logger.debug(f"Could not decrypt moment {m_id}: {e}")
                    display_content = "[encrypted]"

            content_preview = display_content[:200]
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
        RETURN p.id, p.name, p.type, p.description, count(a) AS participants,
               p.visibility
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
            p_vis = row[5] if len(row) > 5 else "public"

            vis_tag = " [private]" if str(p_vis).lower() == "private" else ""
            lines.append(f"{p_name} ({p_type}){vis_tag}")
            lines.append(f"  ID: {p_id}")
            lines.append(f"  Participants: {count}")
            if p_desc:
                lines.append(f"  Description: {p_desc[:100]}")
            lines.append("")

        return _ok("\n".join(lines))
    except Exception as e:
        logger.exception("Place list failed")
        return _err(f"Listing places: {e}")


def _place_call(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Start a call — create a private ephemeral Space, join caller, invite participants.

    A call is a shortcut for: create private Space → join caller → join/invite each
    participant → return the place_id so participants can speak/listen.

    Usage:
        place(action="call", target_actor_id="voce")           # 1:1 call
        place(action="call", participants=["voce", "anima"])    # group call
    """
    if not ctx.graph_ops:
        return _err("No graph connection.")

    actor_id = _resolve_actor(args, ctx)

    # Resolve participants
    participants = args.get("participants") or []
    target = args.get("target_actor_id")
    if target and target not in participants:
        participants.append(target)
    if not participants:
        return _err("'target_actor_id' or 'participants' required for action='call'.")

    all_members = [actor_id] + participants
    created_at, created_at_s = _timestamps()

    # Generate call Space ID and name
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    member_names = " + ".join(all_members[:4])
    if len(all_members) > 4:
        member_names += f" +{len(all_members) - 4}"
    call_name = f"Call: {member_names}"

    try:
        # Create private Space for the call
        ctx.graph_ops._query(
            """MERGE (s:Space {id: $id})
               SET s.type = 'call',
                   s.name = $name,
                   s.capacity = $capacity,
                   s.status = 'active',
                   s.visibility = 'private',
                   s.ephemeral = true,
                   s.synthesis = $synthesis,
                   s.created_at = $ts,
                   s.created_at_s = $ts_s""",
            {
                "id": call_id,
                "name": call_name,
                "capacity": len(all_members) + 5,  # small buffer
                "synthesis": f"Private call between {member_names}",
                "ts": created_at,
                "ts_s": created_at_s,
            },
        )

        # Join all members (create AT links)
        joined = []
        for member_id in all_members:
            try:
                ctx.graph_ops.add_presence(member_id, call_id, present=1.0, visible=1.0)
                joined.append(member_id)
            except Exception as e:
                logger.warning(f"Could not join {member_id} to call: {e}")

        # Grant HAS_ACCESS with encrypted space keys to all members
        crypto = _import_crypto()
        space_key = None
        use_encryption = False

        if crypto:
            try:
                space_key = crypto.generate_space_key()
                use_encryption = True
            except Exception as e:
                logger.warning(f"Could not generate space key: {e}")

        for member_id in all_members:
            try:
                role = "owner" if member_id == actor_id else "member"
                encrypted_key = None

                if use_encryption and space_key:
                    member_pub_key = _get_actor_public_key(member_id, ctx.graph_ops)
                    if member_pub_key:
                        try:
                            encrypted_key = crypto.encrypt_space_key_for_actor(
                                space_key, member_pub_key,
                            )
                        except Exception as e:
                            logger.warning(
                                f"Could not wrap space key for {member_id}: {e}"
                            )

                if encrypted_key:
                    ctx.graph_ops._query(
                        """MATCH (a {id: $actor}), (s:Space {id: $space})
                           MERGE (a)-[r:link {type: 'HAS_ACCESS'}]->(s)
                           SET r.role = $role, r.granted_at = $ts,
                               r.encrypted_key = $ekey, r.granted_by = $grantor""",
                        {
                            "actor": member_id,
                            "space": call_id,
                            "role": role,
                            "ts": created_at,
                            "ekey": encrypted_key,
                            "grantor": actor_id,
                        },
                    )
                else:
                    # Fallback: grant access without encryption
                    ctx.graph_ops._query(
                        """MATCH (a {id: $actor}), (s:Space {id: $space})
                           MERGE (a)-[r:link {type: 'HAS_ACCESS'}]->(s)
                           SET r.role = $role, r.granted_at = $ts""",
                        {
                            "actor": member_id,
                            "space": call_id,
                            "role": role,
                            "ts": created_at,
                        },
                    )
            except Exception as e:
                logger.debug(f"Access grant failed for member {member_id}: {e}")

        # If any member lacks a public key, downgrade space to public so
        # everyone can still speak/listen without encrypted keys.
        if not use_encryption or any(
            not _get_actor_public_key(m, ctx.graph_ops) for m in all_members
        ):
            try:
                ctx.graph_ops._query(
                    "MATCH (s:Space {id: $id}) SET s.visibility = 'public'",
                    {"id": call_id},
                )
            except Exception as e:
                logger.debug(f"Visibility downgrade failed for space {call_id}: {e}")

        # Create a Moment announcing the call
        moment_id = f"moment_{uuid.uuid4().hex[:12]}"
        ctx.graph_ops._query(
            """CREATE (m:Moment {
                   id: $mid, type: 'system', content: $content,
                   synthesis: $content, energy: 0.5,
                   created_at: $ts, created_at_s: $ts_s
               })
               WITH m
               MATCH (s:Space {id: $sid})
               CREATE (m)-[:link {type: 'IN'}]->(s)""",
            {
                "mid": moment_id,
                "content": f"📞 Call started by {actor_id} with {', '.join(participants)}",
                "sid": call_id,
                "ts": created_at,
                "ts_s": created_at_s,
            },
        )

        # Notify Place Server
        _notify_place_server(call_id, {
            "event": "call_started",
            "place_id": call_id,
            "caller": actor_id,
            "participants": participants,
            "timestamp": created_at,
        })

        # Send invitation notification to each participant via their preferred channel
        for participant in participants:
            try:
                _notify_participant(participant, actor_id, call_id, call_name, ctx)
            except Exception as e:
                logger.debug(f"Participant notification failed for {participant}: {e}")

        lines = [
            f"Call started: {call_name}",
            f"Place ID: {call_id}",
            f"Joined: {', '.join(joined)}",
            "",
            "Use place(action='speak', place_id='{}', text='...') to talk.".format(call_id),
            "Use place(action='listen', place_id='{}') to hear.".format(call_id),
            "Use place(action='leave', place_id='{}') to hang up.".format(call_id),
        ]
        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Place call failed")
        return _err(f"Starting call: {e}")


def _notify_participant(
    participant_id: str,
    caller_id: str,
    call_id: str,
    call_name: str,
    ctx: ServerContext,
) -> None:
    """Send a call invitation to a participant via Telegram or other channel."""
    try:
        # Try to find participant's Telegram chat_id from graph
        result = ctx.graph_ops._query(
            "MATCH (a {id: $id}) RETURN a.telegram_chat_id",
            {"id": participant_id},
        )
        if result and result[0][0]:
            chat_id = str(result[0][0])
            import urllib.request
            msg = (
                f"📞 Incoming call from @{caller_id}\n"
                f"Join: place(action='join', place_id='{call_id}')\n"
                f"Or speak directly: place(action='speak', place_id='{call_id}', text='...')"
            )
            # Use the send handler if available, otherwise direct Telegram API
            url = f"{PLACE_SERVER_URL}/api/notify"
            data = json.dumps({
                "type": "call_invitation",
                "target": participant_id,
                "caller": caller_id,
                "place_id": call_id,
                "message": msg,
            }).encode()
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=2)
    except Exception as e:
        logger.debug(f"Call invitation notification failed for {participant_id}: {e}")


def _place_grant_access(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Grant another actor access to a private space.

    The caller must have 'owner' or 'admin' role on the space. Their space
    key is decrypted, then re-wrapped (sealed box) for the target actor's
    public key and stored as a new HAS_ACCESS link.
    """
    place_id = args.get("place_id")
    target_actor_id = args.get("target_actor_id")
    role = args.get("role", "member")

    if not place_id:
        return _err("'place_id' is required for action='grant_access'.")
    if not target_actor_id:
        return _err("'target_actor_id' is required for action='grant_access'.")
    if role not in ("owner", "admin", "member"):
        return _err(f"Invalid role '{role}'. Use: owner, admin, member.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    # Verify space is private
    if not _resolve_space_visibility(place_id, ctx.graph_ops):
        return _err(f"Space '{place_id}' is not private. grant_access is only for private spaces.")

    crypto = _import_crypto()
    if not crypto:
        return _err("Crypto library not available — cannot grant access.")

    actor_id = _resolve_actor(args, ctx)
    created_at, _ = _timestamps()

    # Verify caller has owner or admin role
    try:
        result = ctx.graph_ops._query(
            "MATCH (a:Actor {id: $actor_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "RETURN r.role",
            {"actor_id": actor_id, "place_id": place_id},
        )
        if not result or not result[0]:
            return _err(f"Actor '{actor_id}' has no access to space '{place_id}'.")

        caller_role = result[0][0]
        if caller_role not in ("owner", "admin"):
            return _err(
                f"Actor '{actor_id}' has role '{caller_role}' — "
                "only 'owner' or 'admin' can grant access."
            )
    except Exception as e:
        logger.exception("Role verification failed")
        return _err(f"Verifying caller role: {e}")

    # Get caller's space key
    space_key = _get_space_key(actor_id, place_id, ctx.graph_ops)
    if not space_key:
        return _err(f"Could not decrypt space key for '{actor_id}'.")

    # Get target actor's public key from graph
    target_pub_key = _get_actor_public_key(target_actor_id, ctx.graph_ops)
    if not target_pub_key:
        return _err(
            f"Target actor '{target_actor_id}' has no public_key registered in the graph."
        )

    # Wrap space key for target actor
    try:
        encrypted_key = crypto.encrypt_space_key_for_actor(space_key, target_pub_key)
    except Exception as e:
        logger.exception("Key wrapping failed")
        return _err(f"Wrapping space key for target: {e}")

    # Create HAS_ACCESS link
    try:
        ctx.graph_ops._query(
            "MATCH (a:Actor {id: $target_id}), (s:Space {id: $place_id}) "
            "MERGE (a)-[r:HAS_ACCESS]->(s) "
            "SET r.role = $role, r.encrypted_key = $ekey, "
            "r.granted_at = $ts, r.granted_by = $grantor",
            {
                "target_id": target_actor_id,
                "place_id": place_id,
                "role": role,
                "ekey": encrypted_key,
                "ts": created_at,
                "grantor": actor_id,
            },
        )

        _notify_place_server(place_id, {
            "event": "access_granted",
            "place_id": place_id,
            "target_actor_id": target_actor_id,
            "role": role,
            "granted_by": actor_id,
            "timestamp": created_at,
        })

        return _ok(
            f"Access granted:\n"
            f"  Space: {place_id}\n"
            f"  Target: {target_actor_id}\n"
            f"  Role: {role}\n"
            f"  Granted by: {actor_id}"
        )
    except Exception as e:
        logger.exception("Grant access failed")
        return _err(f"Granting access: {e}")


def _place_revoke_access(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Revoke an actor's access to a private space and rotate the space key.

    Implements the ALGORITHM from Space_Encryption.md lines 323-386:
      1. Authorize revoker (must be owner/admin; only owners revoke owners)
      2. Delete the HAS_ACCESS link for the revokee
      3. Generate a new space key
      4. Re-encrypt all Moments in the space with the new key
      5. Re-wrap the new key for all remaining members

    Forward secrecy: if the revokee's HAS_ACCESS link has a granted_at
    timestamp, only Moments created after that time are re-encrypted.
    Otherwise all Moments are re-encrypted.
    """
    place_id = args.get("place_id")
    target_actor_id = args.get("target_actor_id")

    if not place_id:
        return _err("'place_id' is required for action='revoke_access'.")
    if not target_actor_id:
        return _err("'target_actor_id' is required for action='revoke_access'.")

    if not ctx.graph_ops:
        return _err("No graph connection.")

    # Verify space is private
    if not _resolve_space_visibility(place_id, ctx.graph_ops):
        return _err(f"Space '{place_id}' is not private. revoke_access is only for private spaces.")

    crypto = _import_crypto()
    if not crypto:
        return _err("Crypto library not available — cannot revoke access.")

    actor_id = _resolve_actor(args, ctx)

    # ------------------------------------------------------------------
    # Step 1: Authorize revoker
    # ------------------------------------------------------------------
    try:
        result = ctx.graph_ops._query(
            "MATCH (a:Actor {id: $actor_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "RETURN r.role",
            {"actor_id": actor_id, "place_id": place_id},
        )
        if not result or not result[0]:
            return _err(f"Actor '{actor_id}' has no access to space '{place_id}'.")

        revoker_role = result[0][0]
        if revoker_role not in ("owner", "admin"):
            return _err(
                f"Actor '{actor_id}' has role '{revoker_role}' — "
                "only 'owner' or 'admin' can revoke access."
            )
    except Exception as e:
        logger.exception("Revoker authorization failed")
        return _err(f"Verifying revoker role: {e}")

    # Check the revokee's role and granted_at timestamp
    try:
        result = ctx.graph_ops._query(
            "MATCH (a:Actor {id: $target_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "RETURN r.role, r.granted_at",
            {"target_id": target_actor_id, "place_id": place_id},
        )
        if not result or not result[0]:
            return _err(f"Actor '{target_actor_id}' has no access to space '{place_id}'.")

        revokee_role = result[0][0]
        revokee_granted_at = result[0][1] if len(result[0]) > 1 else None

        # Only owners can revoke owners
        if revokee_role == "owner" and revoker_role != "owner":
            return _err("Only owners can revoke other owners.")

        # Cannot revoke yourself
        if target_actor_id == actor_id:
            return _err("Cannot revoke your own access. Use 'leave' instead.")

    except Exception as e:
        logger.exception("Revokee lookup failed")
        return _err(f"Looking up revokee access: {e}")

    # ------------------------------------------------------------------
    # Step 2: Get the old space key (before deleting anything)
    # ------------------------------------------------------------------
    old_space_key = _get_space_key(actor_id, place_id, ctx.graph_ops)
    if not old_space_key:
        return _err(f"Could not decrypt space key for revoker '{actor_id}'.")

    # ------------------------------------------------------------------
    # Step 3: Delete HAS_ACCESS link for revokee
    # ------------------------------------------------------------------
    try:
        ctx.graph_ops._query(
            "MATCH (a:Actor {id: $target_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "DELETE r",
            {"target_id": target_actor_id, "place_id": place_id},
        )
    except Exception as e:
        logger.exception("Failed to delete HAS_ACCESS link")
        return _err(f"Deleting access link: {e}")

    # Also remove presence (AT link) if present
    try:
        ctx.graph_ops._query(
            "MATCH (a:Actor {id: $target_id})-[r:AT]->(s:Space {id: $place_id}) "
            "DELETE r",
            {"target_id": target_actor_id, "place_id": place_id},
        )
    except Exception as e:
        logger.debug(f"AT link removal failed for {target_actor_id} in {place_id}: {e}")

    # ------------------------------------------------------------------
    # Step 4: Generate new space key
    # ------------------------------------------------------------------
    new_space_key = crypto.generate_space_key()

    # ------------------------------------------------------------------
    # Step 5: Re-encrypt Moments with new key (forward secrecy)
    # ------------------------------------------------------------------
    # If we know when the revokee joined, only re-encrypt Moments created
    # after that point (forward secrecy). Otherwise re-encrypt all.
    try:
        if revokee_granted_at:
            # Re-encrypt only Moments created after the revokee was granted access
            moment_query = (
                "MATCH (m:Moment)-[:AT]->(s:Space {id: $place_id}) "
                "WHERE m.encrypted = true AND m.created_at >= $since "
                "RETURN m.id, m.content"
            )
            moment_params = {"place_id": place_id, "since": revokee_granted_at}
        else:
            # No join timestamp — re-encrypt all encrypted Moments
            moment_query = (
                "MATCH (m:Moment)-[:AT]->(s:Space {id: $place_id}) "
                "WHERE m.encrypted = true "
                "RETURN m.id, m.content"
            )
            moment_params = {"place_id": place_id}

        moments = ctx.graph_ops._query(moment_query, moment_params)
    except Exception as e:
        logger.exception("Failed to query Moments for re-encryption")
        # Rollback: restore revokee access with old key? No — key is already
        # compromised. Log and continue with key rotation for remaining members.
        moments = []
        logger.error(
            f"Could not re-encrypt Moments in {place_id}: {e}. "
            "Continuing with key rotation for remaining members."
        )

    re_encrypted_count = 0
    re_encrypt_errors = 0

    if moments:
        for row in moments:
            m_id = row[0] if len(row) > 0 else None
            m_content = row[1] if len(row) > 1 else None

            if not m_id or not m_content:
                continue

            try:
                # Decrypt with old key
                plaintext = crypto.decrypt_content(m_content, old_space_key)

                # Re-encrypt with new key
                new_ciphertext = crypto.encrypt_content(plaintext, new_space_key)

                # Update the Moment in the graph
                ctx.graph_ops._query(
                    "MATCH (m:Moment {id: $mid}) "
                    "SET m.content = $content",
                    {"mid": m_id, "content": new_ciphertext},
                )
                re_encrypted_count += 1

            except Exception as e:
                logger.warning(f"Failed to re-encrypt Moment {m_id}: {e}")
                re_encrypt_errors += 1

    # Also re-encrypt synthesis fields on Moments that have them
    try:
        if revokee_granted_at:
            synth_query = (
                "MATCH (m:Moment)-[:AT]->(s:Space {id: $place_id}) "
                "WHERE m.encrypted = true AND m.synthesis IS NOT NULL "
                "AND m.created_at >= $since "
                "RETURN m.id, m.synthesis"
            )
            synth_params = {"place_id": place_id, "since": revokee_granted_at}
        else:
            synth_query = (
                "MATCH (m:Moment)-[:AT]->(s:Space {id: $place_id}) "
                "WHERE m.encrypted = true AND m.synthesis IS NOT NULL "
                "RETURN m.id, m.synthesis"
            )
            synth_params = {"place_id": place_id}

        synth_moments = ctx.graph_ops._query(synth_query, synth_params)

        if synth_moments:
            for row in synth_moments:
                m_id = row[0] if len(row) > 0 else None
                m_synth = row[1] if len(row) > 1 else None

                if not m_id or not m_synth:
                    continue

                # Only re-encrypt if the synthesis looks encrypted
                if not crypto.is_encrypted(str(m_synth)):
                    continue

                try:
                    plaintext_synth = crypto.decrypt_content(m_synth, old_space_key)
                    new_synth_ciphertext = crypto.encrypt_content(plaintext_synth, new_space_key)
                    ctx.graph_ops._query(
                        "MATCH (m:Moment {id: $mid}) "
                        "SET m.synthesis = $synthesis",
                        {"mid": m_id, "synthesis": new_synth_ciphertext},
                    )
                except Exception as e:
                    logger.warning(f"Failed to re-encrypt synthesis for Moment {m_id}: {e}")
    except Exception as e:
        logger.warning(f"Synthesis re-encryption query failed: {e}")

    # ------------------------------------------------------------------
    # Step 6: Re-wrap new key for all remaining members
    # ------------------------------------------------------------------
    created_at, _ = _timestamps()
    rewrapped_count = 0
    rewrap_errors = 0

    try:
        remaining = ctx.graph_ops._query(
            "MATCH (a:Actor)-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
            "RETURN a.id, r.role",
            {"place_id": place_id},
        )
    except Exception as e:
        logger.exception("Failed to query remaining members")
        return _err(
            f"Access revoked and {re_encrypted_count} Moments re-encrypted, "
            f"but failed to query remaining members for key re-wrap: {e}"
        )

    if remaining:
        for row in remaining:
            member_id = row[0] if len(row) > 0 else None
            if not member_id:
                continue

            # Get member's public key
            member_pub_key = _get_actor_public_key(member_id, ctx.graph_ops)
            if not member_pub_key:
                logger.warning(
                    f"Cannot re-wrap key for '{member_id}' — no public key in graph"
                )
                rewrap_errors += 1
                continue

            try:
                # Wrap new space key for this member
                new_encrypted_key = crypto.encrypt_space_key_for_actor(
                    new_space_key, member_pub_key
                )

                # Update the HAS_ACCESS link with the new encrypted key
                ctx.graph_ops._query(
                    "MATCH (a:Actor {id: $member_id})-[r:HAS_ACCESS]->(s:Space {id: $place_id}) "
                    "SET r.encrypted_key = $ekey",
                    {
                        "member_id": member_id,
                        "place_id": place_id,
                        "ekey": new_encrypted_key,
                    },
                )
                rewrapped_count += 1
            except Exception as e:
                logger.warning(f"Failed to re-wrap key for '{member_id}': {e}")
                rewrap_errors += 1

    # Notify Place Server
    _notify_place_server(place_id, {
        "event": "access_revoked",
        "place_id": place_id,
        "target_actor_id": target_actor_id,
        "revoked_by": actor_id,
        "key_rotated": True,
        "moments_re_encrypted": re_encrypted_count,
        "members_re_wrapped": rewrapped_count,
        "timestamp": created_at,
    })

    # Build result summary
    lines = [
        f"Access revoked and space key rotated:",
        f"  Space: {place_id}",
        f"  Revoked: {target_actor_id} (was {revokee_role})",
        f"  Revoked by: {actor_id} ({revoker_role})",
        f"  Moments re-encrypted: {re_encrypted_count}",
        f"  Members re-wrapped: {rewrapped_count}",
    ]

    if re_encrypt_errors:
        lines.append(f"  Re-encryption errors: {re_encrypt_errors}")
    if rewrap_errors:
        lines.append(f"  Re-wrap errors: {rewrap_errors}")

    forward_secrecy = "yes (from {})".format(revokee_granted_at) if revokee_granted_at else "no (all Moments re-encrypted)"
    lines.append(f"  Forward secrecy: {forward_secrecy}")

    return _ok("\n".join(lines))


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
