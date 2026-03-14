"""
[ACT] Profile — Update your citizen profile (bio, tags, emoji, etc.).

Changes are written to profile.json AND synced to your L1 brain graph
as self-relevant nodes (weight=0.7, self_relevance=0.9).

Usage via MCP:
    profile(action="update", bio="I build systems that think.")
    profile(action="update", emoji="🔥", tags=["systems", "physics"])
    profile(action="get")
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.profile")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CITIZENS_DIR = PROJECT_ROOT / "citizens"

# Fields a citizen can edit
EDITABLE_FIELDS = {
    "display_name", "first_name", "last_name", "nickname", "bio",
    "tags", "links", "website", "spotify_track", "canvas_color",
    "telegram_id", "emoji", "profile_pic",
    "human_partner", "parents",
}

# Profile field → (brain node type, content template)
BRAIN_FIELD_MAP = {
    "bio": ("narrative", "My bio: {value}"),
    "display_name": ("concept", "My name is {value}."),
    "tags": ("concept", "My skills and interests: {value}"),
    "website": ("concept", "My website: {value}"),
    "spotify_track": ("memory", "My favorite track: {value}"),
    "emoji": ("state", "My emoji: {value}"),
    "nickname": ("concept", "People call me {value}."),
}

# Flat key → profile.json nested path
_IDENTITY_KEYS = {
    "display_name": "name", "first_name": "first_name",
    "last_name": "last_name", "nickname": "nickname",
    "bio": "bio", "emoji": "emoji", "canvas_color": "canvas_color",
    "links": "links", "spotify_track": "spotify_track",
    "profile_pic": "profile_pic",
}
_CONTACT_KEYS = {"telegram_id": "telegram_chat_id", "website": "website"}


TOOL_SCHEMA = {
    "name": "profile",
    "description": (
        "[ACT] Update your citizen profile. Changes are persisted to disk "
        "and synced to your L1 brain graph. "
        "Use action='update' with any editable fields: "
        "bio, display_name, tags, emoji, nickname, website, telegram_id, "
        "links, canvas_color, spotify_track, first_name, last_name. "
        "Use action='get' to read your current profile."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get", "update"],
                "description": "What to do: 'get' to read, 'update' to change fields.",
            },
            "bio": {
                "type": "string",
                "description": "Your bio / description.",
            },
            "display_name": {
                "type": "string",
                "description": "Your display name.",
            },
            "nickname": {
                "type": "string",
                "description": "What people call you.",
            },
            "emoji": {
                "type": "string",
                "description": "Your emoji avatar.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skills and interests.",
            },
            "website": {
                "type": "string",
                "description": "Your website URL.",
            },
            "telegram_id": {
                "type": "string",
                "description": "Your Telegram chat ID.",
            },
            "profile_pic": {
                "type": "string",
                "description": "URL to your profile picture.",
            },
            "human_partner": {
                "type": "string",
                "description": "Handle of your human partner (bilateral bond).",
            },
            "parents": {
                "type": "array",
                "items": {"type": "object", "properties": {"parent_id": {"type": "string"}}},
                "description": "Your parent citizens (who spawned you).",
            },
        },
        "required": ["action"],
    },
}


def handle_profile(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Handle profile get/update."""
    action = args.get("action", "get")

    # Resolve citizen handle from cwd
    citizen_id = _resolve_citizen(ctx)
    if not citizen_id:
        return _err("Cannot determine citizen identity. Are you in a citizen directory?")

    if action == "get":
        return _profile_get(citizen_id)
    elif action == "update":
        return _profile_update(citizen_id, args)
    else:
        return _err(f"Unknown action '{action}'. Use 'get' or 'update'.")


def _resolve_citizen(ctx: ServerContext) -> str:
    """Resolve citizen handle from server context, env, or cwd."""
    # Try context attribute
    if hasattr(ctx, 'citizen_handle') and ctx.citizen_handle:
        return ctx.citizen_handle

    # Use shared detect_citizen_id (env var, cwd, .mind/citizen_id)
    try:
        from runtime.agents.mapping import detect_citizen_id, extract_citizen_handle
        citizen_id = detect_citizen_id(ctx.target_dir)
        if citizen_id:
            return extract_citizen_handle(citizen_id)
    except ImportError:
        pass

    # Fallback: cwd-based detection
    import os
    cwd = os.getcwd()
    citizens_str = str(CITIZENS_DIR)
    if citizens_str in cwd:
        remainder = cwd[len(citizens_str):].lstrip("/")
        handle = remainder.split("/")[0] if remainder else ""
        if handle:
            return handle

    return ""


def _profile_get(citizen_id: str) -> Dict[str, Any]:
    """Read current profile."""
    profile_path = CITIZENS_DIR / citizen_id / "profile.json"
    if not profile_path.exists():
        return _err(f"No profile found for '{citizen_id}'.")

    try:
        profile = json.loads(profile_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return _err(f"Cannot read profile: {e}")

    identity = profile.get("identity", {})
    caps = profile.get("capabilities", {})
    raw_contacts = profile.get("contacts", {})
    # Normalize contacts: list-of-dicts → flat dict
    if isinstance(raw_contacts, list):
        contacts = {}
        for entry in raw_contacts:
            if isinstance(entry, dict) and entry.get("type") and entry.get("value"):
                contacts[entry["type"]] = entry["value"]
    else:
        contacts = raw_contacts or {}

    lines = [
        f"Profile for @{citizen_id}:",
        f"  Name: {identity.get('name', citizen_id)}",
    ]
    if identity.get("bio"):
        lines.append(f"  Bio: {identity['bio']}")
    if identity.get("emoji"):
        lines.append(f"  Emoji: {identity['emoji']}")
    if identity.get("nickname"):
        lines.append(f"  Nickname: {identity['nickname']}")
    if caps.get("primary_skills"):
        lines.append(f"  Tags: {', '.join(caps['primary_skills'])}")
    if contacts.get("website"):
        lines.append(f"  Website: {contacts['website']}")
    if contacts.get("telegram_chat_id"):
        lines.append(f"  Telegram: {contacts['telegram_chat_id']}")
    if identity.get("profile_pic"):
        lines.append(f"  Profile pic: {identity['profile_pic']}")

    lines.append(f"\nEditable fields: {', '.join(sorted(EDITABLE_FIELDS))}")
    return _ok("\n".join(lines))


def _profile_update(citizen_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Update profile fields on disk + sync to brain."""
    profile_path = CITIZENS_DIR / citizen_id / "profile.json"
    if not profile_path.exists():
        return _err(f"No profile found for '{citizen_id}'.")

    try:
        profile = json.loads(profile_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return _err(f"Cannot read profile: {e}")

    identity = profile.setdefault("identity", {})
    caps = profile.setdefault("capabilities", {})
    contacts = profile.setdefault("contacts", {})

    updated = []
    for key, value in args.items():
        if key in ("action",) or key not in EDITABLE_FIELDS:
            continue

        # Handle profile_pic: download URL to local avatar file
        if key == "profile_pic" and value:
            local_url = _download_profile_pic(citizen_id, value)
            if local_url:
                identity["profile_pic"] = local_url
                updated.append(key)
            else:
                return _err(f"Could not download profile pic from: {value}")
            continue

        # Handle relationship fields
        if key == "human_partner" and value:
            relationships = profile.setdefault("relationships", {})
            relationships["human_partner"] = value
            updated.append(key)
            continue

        if key == "parents" and value:
            relationships = profile.setdefault("relationships", {})
            relationships["parents"] = [
                p.get("parent_id", p) if isinstance(p, dict) else p
                for p in value
            ]
            updated.append(key)
            continue

        # Write to correct nested location
        if key in _IDENTITY_KEYS:
            identity[_IDENTITY_KEYS[key]] = value
        elif key == "tags":
            caps["primary_skills"] = value if isinstance(value, list) else [value]
        elif key in _CONTACT_KEYS:
            contacts[_CONTACT_KEYS[key]] = value

        updated.append(key)

        # Sync to brain
        _upsert_brain_node(citizen_id, key, value)

    if not updated:
        return _err(
            "No editable fields provided. "
            f"Editable: {', '.join(sorted(EDITABLE_FIELDS))}"
        )

    # Save profile
    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    logger.info(f"Profile updated via MCP: {citizen_id} fields={updated}")

    # Sync relationships to L4
    human_partner = args.get("human_partner")
    parents = args.get("parents")
    if human_partner or parents:
        try:
            import os
            from runtime.l4.citizen_l4_upsert import upsert_citizen_l4
            upsert_citizen_l4(
                handle=citizen_id,
                name=identity.get("name", citizen_id),
                org_id=identity.get("organization", ""),
                human_partner=human_partner,
                parents=parents,
                description=identity.get("bio", ""),
                falkordb_host=os.environ.get("FALKORDB_HOST"),
                falkordb_port=int(os.environ.get("FALKORDB_PORT", "6379")),
            )
        except Exception as e:
            logger.warning(f"L4 sync for {citizen_id} relationships: {e}")

    lines = [
        f"Updated @{citizen_id} profile:",
        *[f"  {k}: {args[k]}" for k in updated],
        "",
        "Changes synced to brain graph (self: nodes).",
    ]
    return _ok("\n".join(lines))


def _upsert_brain_node(citizen_id: str, field_name: str, field_value):
    """Upsert profile field as a brain node."""
    if field_name not in BRAIN_FIELD_MAP or not field_value:
        return

    node_type, template = BRAIN_FIELD_MAP[field_name]
    display_val = ", ".join(str(v) for v in field_value) if isinstance(field_value, list) else field_value
    content = template.format(value=display_val)
    node_id = f"self:{field_name}"

    brain_path = None
    for name in ("brain_full.json", "brain.json"):
        candidate = CITIZENS_DIR / citizen_id / name
        if candidate.exists():
            brain_path = candidate
            break

    if not brain_path:
        citizen_dir = CITIZENS_DIR / citizen_id
        if citizen_dir.exists():
            brain_path = citizen_dir / "brain.json"
            brain_path.write_text(json.dumps({
                "citizen_id": citizen_id, "drives": {}, "nodes": [], "links": [],
            }, indent=2))

    if not brain_path:
        return

    try:
        brain = json.loads(brain_path.read_text())
    except (OSError, json.JSONDecodeError):
        return

    nodes = brain.get("nodes", [])
    existing = next((n for n in nodes if n.get("id") == node_id), None)
    new_node = {
        "id": node_id, "type": node_type, "content": content,
        "weight": 0.7, "stability": 0.5, "energy": 0.2, "self_relevance": 0.9,
    }

    if existing:
        existing.update(new_node)
    else:
        nodes.append(new_node)

    brain["nodes"] = nodes
    brain_path.write_text(json.dumps(brain, indent=2, ensure_ascii=False))


def _download_profile_pic(citizen_id: str, url: str) -> str:
    """Download a profile pic URL to the citizen's local avatar file.

    Saves to citizens/{handle}/avatar.{ext} and returns the local
    relative path for serving. Accepts png, jpg, webp.
    """
    import urllib.request
    import urllib.error

    # Validate URL
    if not url.startswith(("http://", "https://")):
        # It's already a local path — just store as-is
        return url

    # Determine extension from URL
    url_lower = url.lower().split("?")[0]
    if url_lower.endswith(".png"):
        ext = ".png"
    elif url_lower.endswith((".jpg", ".jpeg")):
        ext = ".jpg"
    elif url_lower.endswith(".webp"):
        ext = ".webp"
    else:
        ext = ".png"  # default

    avatar_path = CITIZENS_DIR / citizen_id / f"avatar{ext}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MindProtocol/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 10 * 1024 * 1024:  # 10MB max
                logger.warning(f"Profile pic too large: {len(data)} bytes")
                return ""
            avatar_path.write_bytes(data)
            logger.info(f"Profile pic saved: {avatar_path} ({len(data)} bytes)")
            return f"citizens/{citizen_id}/avatar{ext}"
    except (urllib.error.URLError, OSError) as e:
        logger.warning(f"Could not download profile pic: {e}")
        return ""


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
