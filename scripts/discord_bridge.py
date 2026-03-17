#!/usr/bin/env python3
"""Discord Bridge — citizens speak with their own identity via webhooks.

Each citizen gets a Discord webhook identity (name + avatar).
One bot listens for inbound messages, routes them via message_router.
Citizens respond through channel webhooks — each message shows the citizen's
name, emoji, and profile picture.

Usage:
  discord_bridge.py listen                                      # Start listener
  discord_bridge.py channels                                    # List all channels in guild
  discord_bridge.py guild                                       # Show server info
  discord_bridge.py read <channel> [limit]                      # Read channel (name or ID)
  discord_bridge.py send <channel> <message>                    # Send as bot
  discord_bridge.py speak [@handle] <channel> <message>         # Send as citizen
  discord_bridge.py image [@handle] <channel> <file_or_url>     # Send image/video as citizen
  discord_bridge.py imagine [@handle] <channel> <prompt>        # Generate image (Ideogram) + send as citizen
  discord_bridge.py react <channel> <message_id> <emoji>        # Add emoji reaction
  discord_bridge.py unread [@handle] [channel]                  # Show unread messages / summary
  discord_bridge.py mentions [@handle] <channel>                # Show messages that mention citizen
  discord_bridge.py markread [@handle] <channel>                # Mark channel as read
  discord_bridge.py list                                        # List citizens for Discord
  discord_bridge.py whoami                                      # Show detected handle
  discord_bridge.py thread <file.json>                          # Cross-post tweet thread

Handle auto-detection: MIND_HANDLE env → MIND_ACTOR env → CWD in citizens/ → git user.name
Channel: by ID (number) or name (string, e.g. "general").
"""

import os
import sys
import json
import time
import asyncio
import re
import threading
import requests as http_requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord import Webhook
import aiohttp

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).parent.parent / ".env")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ROOT = Path(__file__).parent.parent
SHRINE = ROOT / "shrine" / "state"
CITIZENS_DIR = ROOT / "citizens"
DISCORD_API = "https://discord.com/api/v10"
STATIC_BASE = os.getenv("MANEMUS_STATIC_URL", "https://manemus.onrender.com/static")
DISCORD_LOG = SHRINE / "discord_messages.jsonl"
WEBHOOK_CACHE_FILE = SHRINE / "discord_webhook_cache.json"

# Channel IDs (override via env or config)
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("DISCORD_ANNOUNCEMENTS_CHANNEL", "1284619860101562450"))
TOWN_SQUARE_CHANNEL_ID = int(os.getenv("DISCORD_TOWN_SQUARE_CHANNEL", "0"))

# Rate limiting
_last_webhook_send: dict[str, float] = {}
WEBHOOK_COOLDOWN_S = 1.0  # min seconds between sends per webhook

# Discord client (for listen mode)
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

# ---------------------------------------------------------------------------
# Citizen registry helpers
# ---------------------------------------------------------------------------

def detect_handle() -> str | None:
    """Auto-detect the calling citizen's handle.

    Resolution order:
      1. MIND_HANDLE env var (explicit override)
      2. MIND_ACTOR env var (e.g. "actor_caterina" → "caterina")
      3. CWD inside citizens/ (e.g. /citizens/caterina/... → "caterina")
      4. Git user name matching a citizen handle
    """
    # 1. Explicit env
    h = os.getenv("MIND_HANDLE")
    if h:
        return h.lower().strip().lstrip("@")

    # 2. Actor ID env (strip "actor_" prefix)
    actor = os.getenv("MIND_ACTOR")
    if actor:
        h = actor.lower().removeprefix("actor_").strip()
        if (CITIZENS_DIR / h / "profile.json").exists():
            return h

    # 3. CWD — walk up from cwd looking for citizens/{handle} pattern
    try:
        cwd = Path.cwd().resolve()
        citizens_resolved = CITIZENS_DIR.resolve()
        if str(cwd).startswith(str(citizens_resolved)):
            rel = cwd.relative_to(citizens_resolved)
            handle = rel.parts[0] if rel.parts else None
            if handle and (CITIZENS_DIR / handle / "profile.json").exists():
                return handle
    except (ValueError, OSError):
        pass

    # 4. Git user.name as fallback
    try:
        import subprocess
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            git_name = result.stdout.strip().lower().replace(" ", "_")
            if (CITIZENS_DIR / git_name / "profile.json").exists():
                return git_name
    except (OSError, subprocess.TimeoutExpired):
        pass

    return None


def _load_citizen_profile(handle: str) -> dict | None:
    """Load a citizen's profile.json."""
    profile_path = CITIZENS_DIR / handle / "profile.json"
    if not profile_path.exists():
        return None
    try:
        return json.loads(profile_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _get_all_citizen_handles() -> list[str]:
    """List all citizen directory handles."""
    if not CITIZENS_DIR.exists():
        return []
    return sorted(
        d.name for d in CITIZENS_DIR.iterdir()
        if d.is_dir() and (d / "profile.json").exists()
    )


# Cache for mention enrichment (handle → "emoji **@handle**")
_mention_cache: dict[str, str] = {}
_mention_cache_ttl: float = 0


def _enrich_mentions(text: str) -> str:
    """Replace @handle mentions with emoji **@handle** format.

    Looks up citizen emoji from L4 graph (mind_protocol).
    Format: emoji **@handle** (e.g. 🎓 **@mentor**)
    Falls back to local profile if L4 unavailable.
    Caches for performance.
    """
    import re as _re

    global _mention_cache, _mention_cache_ttl
    now = time.time()

    # Refresh cache every 5 minutes
    if now - _mention_cache_ttl > 300:
        _mention_cache.clear()
        _mention_cache_ttl = now

    # Pre-load from L4 if cache is empty
    if not _mention_cache:
        try:
            from falkordb import FalkorDB as _FB
            _host = os.environ.get("FALKORDB_HOST", "localhost")
            _port = int(os.environ.get("FALKORDB_PORT", "6379"))
            _g4 = _FB(host=_host, port=_port).select_graph(
                os.environ.get("L4_GRAPH", "mind_protocol")
            )
            _r = _g4.query(
                "MATCH (a:Actor) WHERE a.emoji IS NOT NULL "
                "RETURN a.id, a.emoji"
            )
            for row in _r.result_set:
                if row[0] and row[1]:
                    _mention_cache[row[0].lower()] = f"{row[1]} **@{row[0]}**"
        except Exception:
            pass

    def _replace_mention(match):
        handle = match.group(1).lower()

        if handle in _mention_cache:
            return _mention_cache[handle]

        # Fallback: check local profile for emoji
        profile = _load_citizen_profile(handle)
        if not profile:
            return match.group(0)  # Keep original @handle if not found

        identity = profile.get("identity", {})
        emoji = identity.get("emoji", "")
        if emoji:
            enriched = f"{emoji} **@{handle}**"
        else:
            enriched = f"**@{handle}**"
        _mention_cache[handle] = enriched
        return enriched

    # Match @handle but not @@, @mentions inside URLs, or email addresses
    return _re.sub(r'(?<![@\w])@(\w+)', _replace_mention, text)


def _citizen_display_name(profile: dict) -> str:
    """Build display name from profile: 'Emoji FirstName LastName' or fallback."""
    identity = profile.get("identity", {})
    emoji = identity.get("emoji", "")
    first = identity.get("first_name", "")
    last = identity.get("last_name", "")
    name = identity.get("name", identity.get("handle", ""))

    if first and last:
        display = f"{first} {last}"
    elif first:
        display = first
    else:
        display = name

    if emoji:
        display = f"{emoji} {display}"

    return display


def _citizen_avatar_url(handle: str, profile: dict = None) -> str | None:
    """Return avatar URL for a citizen — checks profile_pic, then static paths."""
    if profile:
        identity = profile.get("identity", {})
        # Check explicit profile pic
        pic = identity.get("profile_pic") or identity.get("photo")
        if pic and pic.startswith("http"):
            return pic

    # Try static paths
    for path in [f"citizens/{handle}.png", f"team/{handle}.png"]:
        url = f"{STATIC_BASE}/{path}"
        return url  # Assume it exists; Discord handles 404 gracefully

    return None


# ---------------------------------------------------------------------------
# Webhook management — one webhook per channel, reused for all citizens
# ---------------------------------------------------------------------------

_webhook_cache: dict[int, str] = {}  # channel_id → webhook_url


def _load_webhook_cache():
    """Load webhook URL cache from disk."""
    global _webhook_cache
    if WEBHOOK_CACHE_FILE.exists():
        try:
            _webhook_cache = {int(k): v for k, v in json.loads(WEBHOOK_CACHE_FILE.read_text()).items()}
        except (json.JSONDecodeError, OSError):
            _webhook_cache = {}


def _save_webhook_cache():
    """Persist webhook cache."""
    SHRINE.mkdir(parents=True, exist_ok=True)
    WEBHOOK_CACHE_FILE.write_text(json.dumps({str(k): v for k, v in _webhook_cache.items()}, indent=2))


def _get_or_create_webhook_sync(channel_id: int) -> str | None:
    """Get or create a webhook for a channel (sync REST)."""
    if channel_id in _webhook_cache:
        return _webhook_cache[channel_id]

    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

    # List existing webhooks on channel
    try:
        resp = http_requests.get(f"{DISCORD_API}/channels/{channel_id}/webhooks", headers=headers, timeout=10)
        if resp.ok:
            webhooks = resp.json()
            # Reuse existing Mind Protocol webhook
            for wh in webhooks:
                if wh.get("name") == "Mind Citizen":
                    _webhook_cache[channel_id] = wh["url"] if "url" in wh else f"https://discord.com/api/webhooks/{wh['id']}/{wh['token']}"
                    _save_webhook_cache()
                    return _webhook_cache[channel_id]
    except http_requests.exceptions.RequestException:
        pass

    # Create new webhook
    try:
        resp = http_requests.post(
            f"{DISCORD_API}/channels/{channel_id}/webhooks",
            headers=headers,
            json={"name": "Mind Citizen"},
            timeout=10,
        )
        if resp.ok:
            wh = resp.json()
            url = f"https://discord.com/api/webhooks/{wh['id']}/{wh['token']}"
            _webhook_cache[channel_id] = url
            _save_webhook_cache()
            print(f"  Created webhook for channel {channel_id}")
            return url
        else:
            print(f"  Failed to create webhook: {resp.status_code} {resp.text}")
    except http_requests.exceptions.RequestException as e:
        print(f"  Webhook creation error: {e}")

    return None


# ---------------------------------------------------------------------------
# Send as citizen (sync — usable from anywhere)
# ---------------------------------------------------------------------------

def send_as_citizen(handle: str | None, channel_id: int, text: str, embed: dict = None) -> dict | None:
    """Send a message to a Discord channel as a specific citizen via webhook.

    If handle is None, auto-detects from env/CWD.
    The message appears with the citizen's name and avatar.
    """
    if not handle:
        handle = detect_handle()
        if not handle:
            raise ValueError("Cannot auto-detect citizen handle. Set MIND_HANDLE env or pass handle explicitly.")

    webhook_url = _get_or_create_webhook_sync(channel_id)
    if not webhook_url:
        print(f"  No webhook available for channel {channel_id}")
        return None

    # Rate limit
    cache_key = f"{handle}:{channel_id}"
    now = time.time()
    last = _last_webhook_send.get(cache_key, 0)
    if now - last < WEBHOOK_COOLDOWN_S:
        time.sleep(WEBHOOK_COOLDOWN_S - (now - last))

    profile = _load_citizen_profile(handle)
    display_name = _citizen_display_name(profile) if profile else handle.replace("_", " ").title()
    avatar_url = _citizen_avatar_url(handle, profile)

    # Impact visibility: incomplete profile → inform the citizen
    if profile:
        identity = profile.get("identity", {})
        missing = []
        if not identity.get("name"):
            missing.append("name")
        if not identity.get("bio"):
            missing.append("bio")
        if not identity.get("emoji"):
            missing.append("emoji")
        if missing:
            try:
                from citizen_wake import _inject_l1_stimulus
                _inject_l1_stimulus(
                    handle,
                    f"Les autres citoyens te voient comme '{display_name}' sans {', '.join(missing)}. "
                    f"Tes contributions dans le graph sont plus difficiles à attribuer. "
                    f"profile(action='update', {missing[0]}='...') pour que ton travail te soit reconnu.",
                    origin="system",
                )
            except Exception:
                pass

    payload = {"username": display_name[:80]}  # Discord 80-char limit on webhook username
    if text:
        # Replace @handle mentions with emoji **@handle** format
        text = _enrich_mentions(text)
        # Prefix message with sender identity: emoji **@handle**
        identity = profile.get("identity", {}) if profile else {}
        sender_emoji = identity.get("emoji", "")
        sender_prefix = f"{sender_emoji} **@{handle}**" if sender_emoji else f"**@{handle}**"
        # Avoid double-prefixing
        if not text.startswith(f"**@{handle}") and not text.startswith(sender_prefix):
            payload["content"] = f"{sender_prefix}\n{text}"
        else:
            payload["content"] = text
    if embed:
        payload["embeds"] = [embed]
    if avatar_url:
        payload["avatar_url"] = avatar_url

    try:
        resp = http_requests.post(
            f"{webhook_url}?wait=true",
            json=payload,
            timeout=15,
        )
        _last_webhook_send[cache_key] = time.time()

        if resp.ok:
            data = resp.json()
            print(f"  {display_name} → #{channel_id}: {text[:60] if text else '[embed]'}")
            _log_message("out", handle, channel_id, text or "[embed]")
            return data
        else:
            print(f"  Webhook send error ({handle}): {resp.status_code} {resp.text[:200]}")
            return None
    except http_requests.exceptions.RequestException as e:
        print(f"  Webhook send failed ({handle}): {e}")
        return None


def send_as_citizen_embed(handle: str, channel_id: int, title: str, description: str,
                          color: int = 0x6C3AED, fields: list = None) -> dict | None:
    """Send a rich embed as a citizen."""
    embed = {"title": title, "description": description, "color": color}
    if fields:
        embed["fields"] = fields
    return send_as_citizen(handle, channel_id, text="", embed=embed)


# ---------------------------------------------------------------------------
# Send as bot (original REST, no webhook)
# ---------------------------------------------------------------------------

def send_message(channel_id: int, text: str, embed: dict = None) -> dict | None:
    """Send a message as the bot itself (not as a citizen)."""
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
    payload = {}
    if text:
        payload["content"] = text
    if embed:
        payload["embeds"] = [embed]

    try:
        resp = http_requests.post(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if resp.ok:
            data = resp.json()
            print(f"  Bot → #{channel_id}: {text[:80] if text else '[embed]'}")
            return data
        else:
            print(f"  Discord send error: {resp.status_code} - {resp.text}")
            return None
    except http_requests.exceptions.RequestException as e:
        print(f"  [ERROR] Discord send_message failed: {e}")
        return None


def send_announcement(text: str, embed: dict = None):
    """Send to #announcements as bot."""
    return send_message(ANNOUNCEMENTS_CHANNEL_ID, text, embed)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log_message(direction: str, author: str, channel_id: int, content: str):
    """Append to discord_messages.jsonl + enrich L3 graph."""
    SHRINE.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "dir": direction,
        "author": author,
        "channel": str(channel_id),
        "content": content[:2000],
    }
    with open(DISCORD_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Enrich L3 graph — Space + Moment + links
    try:
        from graph_enricher import on_message
        channel_name = ""
        for name, cid in _channel_map.items():
            if str(cid) == str(channel_id):
                channel_name = name
                break
        mentioned = [m.group(1).lower() for m in re.finditer(r"@(\w+)", content)]
        on_message(
            platform="discord",
            channel_id=str(channel_id),
            channel_name=channel_name or str(channel_id),
            author_name=author,
            author_handle=author.lower().replace(" ", "_"),
            content=content,
            mentioned_handles=mentioned,
            direction=direction,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Channel resolution — name or ID
# ---------------------------------------------------------------------------

# Cache: channel_name → channel_id (populated on guild connect or channels cmd)
_channel_map: dict[str, int] = {}
_CHANNEL_MAP_FILE = SHRINE / "discord_channel_map.json"


def _load_channel_map():
    """Load channel name→ID map from disk."""
    global _channel_map
    if _CHANNEL_MAP_FILE.exists():
        try:
            _channel_map = json.loads(_CHANNEL_MAP_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            _channel_map = {}


def _save_channel_map():
    """Persist channel map."""
    SHRINE.mkdir(parents=True, exist_ok=True)
    _CHANNEL_MAP_FILE.write_text(json.dumps(_channel_map, indent=2))


def _refresh_channel_map_sync(guild_id: int = None) -> dict[str, int]:
    """Fetch all channels via REST and rebuild the map."""
    headers = {"Authorization": f"Bot {TOKEN}"}

    # If no guild_id, get first guild
    if not guild_id:
        try:
            resp = http_requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers, timeout=10)
            if resp.ok and resp.json():
                guild_id = int(resp.json()[0]["id"])
            else:
                print("  No guilds found")
                return _channel_map
        except http_requests.exceptions.RequestException:
            return _channel_map

    try:
        resp = http_requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=headers, timeout=10)
        if resp.ok:
            channels = resp.json()
            _channel_map.clear()
            for ch in channels:
                if ch.get("name"):
                    _channel_map[ch["name"]] = int(ch["id"])
            _save_channel_map()
    except http_requests.exceptions.RequestException as e:
        print(f"  Channel fetch error: {e}")

    return _channel_map


def resolve_channel(channel_ref: str | int) -> int | None:
    """Resolve a channel reference (name or ID) to a channel ID."""
    # If it's already a number
    if isinstance(channel_ref, int):
        return channel_ref
    try:
        return int(channel_ref)
    except (ValueError, TypeError):
        pass

    # Lookup by name
    _load_channel_map()
    name = channel_ref.lower().lstrip("#")
    if name in _channel_map:
        return _channel_map[name]

    # Refresh and retry
    _refresh_channel_map_sync()
    return _channel_map.get(name)


def list_channels_sync() -> list[dict]:
    """List all channels in the guild via REST. Returns list of {id, name, type, category}."""
    headers = {"Authorization": f"Bot {TOKEN}"}

    # Get first guild
    try:
        resp = http_requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers, timeout=10)
        if not resp.ok or not resp.json():
            print("  No guilds found")
            return []
        guild = resp.json()[0]
        guild_id = guild["id"]
        guild_name = guild["name"]
    except http_requests.exceptions.RequestException as e:
        print(f"  Guild fetch error: {e}")
        return []

    # Get channels
    try:
        resp = http_requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=headers, timeout=10)
        if not resp.ok:
            print(f"  Channel fetch error: {resp.status_code}")
            return []
        raw = resp.json()
    except http_requests.exceptions.RequestException as e:
        print(f"  Channel fetch error: {e}")
        return []

    # Discord channel types: 0=text, 2=voice, 4=category, 5=announcement, 13=stage, 15=forum
    TYPE_NAMES = {0: "text", 2: "voice", 4: "category", 5: "announcement", 13: "stage", 15: "forum"}

    # Build category lookup
    categories = {ch["id"]: ch["name"] for ch in raw if ch.get("type") == 4}

    channels = []
    for ch in sorted(raw, key=lambda c: (c.get("position", 0))):
        ch_type = ch.get("type", 0)
        if ch_type == 4:  # Skip category headers in the list
            continue
        channels.append({
            "id": int(ch["id"]),
            "name": ch.get("name", "?"),
            "type": TYPE_NAMES.get(ch_type, str(ch_type)),
            "category": categories.get(ch.get("parent_id"), "—"),
        })

    # Update channel map
    _channel_map.clear()
    for ch in channels:
        _channel_map[ch["name"]] = ch["id"]
    _save_channel_map()

    return channels


def guild_info_sync() -> dict | None:
    """Get guild info via REST."""
    headers = {"Authorization": f"Bot {TOKEN}"}
    try:
        resp = http_requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers, timeout=10)
        if not resp.ok or not resp.json():
            return None
        guild_summary = resp.json()[0]
        guild_id = guild_summary["id"]

        resp = http_requests.get(f"{DISCORD_API}/guilds/{guild_id}?with_counts=true", headers=headers, timeout=10)
        if resp.ok:
            return resp.json()
    except http_requests.exceptions.RequestException:
        pass
    return None


# ---------------------------------------------------------------------------
# Reactions — add emoji to messages
# ---------------------------------------------------------------------------

def add_reaction(channel_id: int, message_id: int, emoji: str) -> bool:
    """Add an emoji reaction to a message. Emoji can be unicode or custom :name:id format."""
    headers = {"Authorization": f"Bot {TOKEN}"}
    # URL-encode the emoji for the path
    import urllib.parse
    encoded = urllib.parse.quote(emoji)
    try:
        resp = http_requests.put(
            f"{DISCORD_API}/channels/{channel_id}/messages/{message_id}/reactions/{encoded}/@me",
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 204:
            print(f"  Reacted {emoji} on message {message_id}")
            return True
        else:
            print(f"  Reaction error: {resp.status_code} {resp.text[:200]}")
            return False
    except http_requests.exceptions.RequestException as e:
        print(f"  Reaction failed: {e}")
        return False


# ---------------------------------------------------------------------------
# File attachments — images, videos, files via webhook
# ---------------------------------------------------------------------------

def send_as_citizen_file(handle: str | None, channel_id: int, file_path: str = None,
                         file_url: str = None, text: str = "", spoiler: bool = False) -> dict | None:
    """Send a file (image, video, etc.) as a citizen via webhook multipart upload.

    Either file_path (local file) or file_url (remote URL to embed) must be provided.
    """
    if not handle:
        handle = detect_handle()
        if not handle:
            raise ValueError("Cannot auto-detect citizen handle.")

    profile = _load_citizen_profile(handle)
    display_name = _citizen_display_name(profile) if profile else handle.replace("_", " ").title()
    avatar_url = _citizen_avatar_url(handle, profile)

    # If it's a URL, embed it in the message content (Discord auto-embeds images/videos)
    if file_url:
        full_text = f"{text}\n{file_url}" if text else file_url
        return send_as_citizen(handle, channel_id, full_text)

    # Local file → multipart upload via webhook
    if not file_path or not Path(file_path).exists():
        print(f"  File not found: {file_path}")
        return None

    webhook_url = _get_or_create_webhook_sync(channel_id)
    if not webhook_url:
        return None

    local = Path(file_path)
    filename = local.name
    if spoiler:
        filename = f"SPOILER_{filename}"

    # Build multipart payload
    payload_json = {"username": display_name[:80]}
    if text:
        payload_json["content"] = text
    if avatar_url:
        payload_json["avatar_url"] = avatar_url

    try:
        with open(local, "rb") as f:
            resp = http_requests.post(
                f"{webhook_url}?wait=true",
                data={"payload_json": json.dumps(payload_json)},
                files={"file": (filename, f)},
                timeout=60,
            )
        if resp.ok:
            data = resp.json()
            print(f"  {display_name} → #{channel_id}: [{filename}] {text[:40]}")
            _log_message("out", handle, channel_id, f"[file:{filename}] {text}")
            return data
        else:
            print(f"  File send error ({handle}): {resp.status_code} {resp.text[:200]}")
            return None
    except http_requests.exceptions.RequestException as e:
        print(f"  File send failed ({handle}): {e}")
        return None


# ---------------------------------------------------------------------------
# Image generation — /imagine via Ideogram, sent as citizen
# ---------------------------------------------------------------------------

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from ideogram import generate_image as _ideogram_generate, parse_imagine_command as _parse_imagine
    _IDEOGRAM_AVAILABLE = True
except ImportError:
    _IDEOGRAM_AVAILABLE = False


def imagine_as_citizen(handle: str | None, channel_id: int, prompt: str,
                       style: str = "AUTO", aspect: str = "1x1") -> dict | None:
    """Generate an image with Ideogram and send it as a citizen to Discord.

    Returns the Discord message data or None on failure.
    """
    if not _IDEOGRAM_AVAILABLE:
        print("  Ideogram not available (missing ideogram.py)")
        return send_as_citizen(handle, channel_id, "Image generation is not available right now.")

    if not handle:
        handle = detect_handle()
        if not handle:
            raise ValueError("Cannot auto-detect citizen handle.")

    print(f"  Generating image for @{handle}: {prompt[:60]}...")

    results = _ideogram_generate(
        prompt=prompt,
        style_type=style,
        aspect_ratio=aspect,
        rendering_speed="TURBO",
    )

    if not results:
        return send_as_citizen(handle, channel_id, f"Image generation failed for: _{prompt[:100]}_")

    sent = None
    for img in results:
        local_path = img.get("local_path")
        if local_path and Path(local_path).exists():
            caption = prompt[:200] if len(prompt) <= 200 else prompt[:197] + "..."
            sent = send_as_citizen_file(handle, channel_id, file_path=local_path, text=caption)
            if sent:
                print(f"  Image sent as @{handle} ({img.get('resolution', '?')})")
    return sent


def handle_imagine_command(handle: str | None, channel_id: int, text: str) -> dict | None:
    """Parse /imagine command and generate+send image as citizen.

    Returns message data if handled, None if not an /imagine command.
    """
    parsed = None
    if _IDEOGRAM_AVAILABLE:
        parsed = _parse_imagine(text)
    elif text.strip().lower().startswith(("/imagine", "/image", "/img")):
        return send_as_citizen(handle, channel_id, "Image generation is not available right now.")

    if not parsed:
        return None

    prompt = parsed.pop("prompt")
    return imagine_as_citizen(
        handle, channel_id, prompt,
        style=parsed.get("style_type", "AUTO"),
        aspect=parsed.get("aspect_ratio", "1x1"),
    )


# ---------------------------------------------------------------------------
# Unread / Mentions tracking per citizen
# ---------------------------------------------------------------------------

_UNREAD_FILE = SHRINE / "discord_unread.json"


def _load_unread() -> dict:
    """Load unread state: {handle: {channel_id: last_read_message_id}}."""
    if _UNREAD_FILE.exists():
        try:
            return json.loads(_UNREAD_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_unread(data: dict):
    """Persist unread state."""
    SHRINE.mkdir(parents=True, exist_ok=True)
    _UNREAD_FILE.write_text(json.dumps(data, indent=2))


def mark_read(handle: str, channel_id: int, message_id: str):
    """Mark a channel as read up to message_id for a citizen."""
    data = _load_unread()
    if handle not in data:
        data[handle] = {}
    data[handle][str(channel_id)] = message_id
    _save_unread(data)


def mark_read_all(handle: str, channel_id: int):
    """Mark a channel as fully read (latest message)."""
    messages = read_channel_sync(channel_id, limit=1)
    if messages:
        mark_read(handle, channel_id, messages[-1]["id"])


def get_unread(handle: str, channel_id: int) -> list[dict]:
    """Get unread messages in a channel for a citizen."""
    data = _load_unread()
    last_read = data.get(handle, {}).get(str(channel_id))

    messages = read_channel_sync(channel_id, limit=100)
    if not last_read:
        return messages  # Never read → everything is unread

    # Filter to messages after last_read
    unread = []
    found_marker = False
    for msg in messages:
        if found_marker:
            unread.append(msg)
        elif msg["id"] == last_read:
            found_marker = True

    return unread


def get_mentions(handle: str, channel_id: int) -> list[dict]:
    """Get messages that mention a citizen (by @handle or display name) in a channel."""
    profile = _load_citizen_profile(handle)
    search_terms = {f"@{handle}"}
    if profile:
        identity = profile.get("identity", {})
        name = identity.get("name", "")
        first = identity.get("first_name", "")
        if name:
            search_terms.add(name.lower())
        if first:
            search_terms.add(first.lower())

    messages = read_channel_sync(channel_id, limit=100)
    mentions = []
    for msg in messages:
        content_lower = msg["content"].lower()
        if any(term.lower() in content_lower for term in search_terms):
            mentions.append(msg)
    return mentions


def unread_summary(handle: str) -> dict[str, dict]:
    """Get unread counts + mention counts across all channels.

    Returns {channel_name: {"unread": N, "mentions": M, "channel_id": id}}.
    """
    _load_channel_map()
    summary = {}
    for ch_name, ch_id in _channel_map.items():
        unread = get_unread(handle, ch_id)
        if not unread:
            continue
        mention_count = 0
        profile = _load_citizen_profile(handle)
        search_terms = {f"@{handle}"}
        if profile:
            identity = profile.get("identity", {})
            name = identity.get("name", "")
            if name:
                search_terms.add(name.lower())
        for msg in unread:
            if any(t.lower() in msg["content"].lower() for t in search_terms):
                mention_count += 1
        summary[ch_name] = {
            "unread": len(unread),
            "mentions": mention_count,
            "channel_id": ch_id,
        }
    return summary


# ---------------------------------------------------------------------------
# Read channel messages via REST (sync, no bot client needed)
# ---------------------------------------------------------------------------

def read_channel_sync(channel_id: int, limit: int = 50) -> list[dict]:
    """Read messages from a channel via REST API. Returns list of message dicts."""
    headers = {"Authorization": f"Bot {TOKEN}"}
    messages = []
    try:
        resp = http_requests.get(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers=headers,
            params={"limit": min(limit, 100)},
            timeout=15,
        )
        if resp.ok:
            raw = resp.json()
            for msg in reversed(raw):  # API returns newest first
                attachments = []
                for a in msg.get("attachments", []):
                    attachments.append({
                        "url": a["url"],
                        "filename": a.get("filename", ""),
                        "size": a.get("size", 0),
                        "content_type": a.get("content_type", ""),
                    })
                messages.append({
                    "id": msg["id"],
                    "author": msg["author"].get("username", "?"),
                    "author_id": msg["author"].get("id", ""),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "attachments": attachments,
                    "embeds": msg.get("embeds", []),
                    "reactions": [
                        {"emoji": r["emoji"].get("name", "?"), "count": r["count"]}
                        for r in msg.get("reactions", [])
                    ],
                })
        else:
            print(f"  Read error: {resp.status_code} {resp.text[:200]}")
    except http_requests.exceptions.RequestException as e:
        print(f"  Read failed: {e}")
    return messages


# ---------------------------------------------------------------------------
# Citizen wake — trigger citizen sessions on mention
# ---------------------------------------------------------------------------

try:
    from citizen_wake import mention_citizen as _wake_mention, notify_channel_message as _wake_channel
    _WAKE_AVAILABLE = True
except ImportError:
    _WAKE_AVAILABLE = False


def wake_citizen_on_mention(from_name: str, target_handle: str, message: str,
                            channel_name: str = "discord") -> bool:
    """Wake a citizen when mentioned on Discord.

    Sends ONE combined stimulus (mention + channel context) to avoid
    duplicate sessions.  Previous code called _wake_mention AND _wake_channel
    separately, each injecting its own L1 stimulus — causing triple-sends
    when graph_enricher._stimulate_space_citizens added a third.
    """
    if not _WAKE_AVAILABLE:
        print(f"  citizen_wake not available — @{target_handle} won't wake")
        return False

    # Single combined stimulus — mention is the primary signal, channel gives context
    _wake_mention(from_name, target_handle,
                  f"mentioned you on Discord in #{channel_name}: {message[:200]}")
    print(f"  Wake signal → @{target_handle} (mentioned by {from_name} in #{channel_name})")
    return True


# ---------------------------------------------------------------------------
# Inbound message handling
# ---------------------------------------------------------------------------

# Import routing aliases from telegram_bridge (shared logic)
_ROUTING_ALIASES = {"anyone", "someone", "help", "support", "dev", "admin", "ai", "mod",
                    "artist", "researcher", "innovator", "diplomat", "priest"}
_MULTI_ALIASES = {"devs": 3, "admins": 2, "ais": 2, "mods": 2}


def _is_routing_alias(handle: str) -> bool:
    """Check if handle is a known routing alias or dynamic @ai_* prefix."""
    h = handle.lower().lstrip("@")
    if h in _ROUTING_ALIASES or h in _MULTI_ALIASES:
        return True
    if h.startswith("ai_") and h[3:] in _ROUTING_ALIASES:
        return True
    return False


# Known universe repos — canonical source of truth for citizen ↔ universe mapping
_UNIVERSE_REPOS = {
    "venezia":          Path.home() / "venezia" / "citizens",
    "lumina-prime":     Path.home() / "lumina-prime" / "citizens",
    "contre-terre":     Path.home() / "contre-terre" / "citizens",
    "cities-of-light":  Path.home() / "cities-of-light" / "citizens",
}


def _resolve_group_mention(name: str) -> set[str]:
    """Resolve @org or @universe to all AI citizen handles in that group."""
    name_lower = name.lower()
    name_variants = {name_lower, name_lower.replace("-", "_"), name_lower.replace("_", "-")}

    handles = set()

    try:
        from runtime.api.citizens_routes import _load_ai_citizens
        citizens = _load_ai_citizens()
    except ImportError:
        citizens = []
        if CITIZENS_DIR.exists():
            for d in sorted(CITIZENS_DIR.iterdir()):
                profile_path = d / "profile.json"
                if not profile_path.exists():
                    continue
                try:
                    p = json.loads(profile_path.read_text())
                    identity = p.get("identity", {})
                    citizens.append({
                        "handle": identity.get("handle", d.name),
                        "type": identity.get("type", "ai"),
                        "universe": identity.get("universe", ""),
                        "orgs": [identity["organization"]] if identity.get("organization") else [],
                    })
                except (OSError, json.JSONDecodeError):
                    continue

    for c in citizens:
        if c.get("type") == "human":
            continue
        for org in c.get("orgs", []):
            if org.lower() in name_variants:
                handles.add(c["handle"])
        uni = (c.get("universe") or "").lower()
        if uni in name_variants:
            handles.add(c["handle"])

    for universe_name, repo_dir in _UNIVERSE_REPOS.items():
        uni_variants = {universe_name, universe_name.replace("-", "_"), universe_name.replace("_", "-")}
        if not name_variants & uni_variants:
            continue
        if not repo_dir.exists():
            continue
        for d in repo_dir.iterdir():
            if not d.is_dir() or d.name.startswith(".") or d.name == "__pycache__":
                continue
            handle = d.name.lower().replace("-", "_")
            if (CITIZENS_DIR / handle / "profile.json").exists():
                handles.add(handle)

    # Graph-based org lookup (L3) — resolves orgs like @primers that exist as Space nodes
    if not handles:
        try:
            from falkordb import FalkorDB as _GFB
            _gh = os.environ.get("FALKORDB_HOST", "localhost")
            _gp = int(os.environ.get("FALKORDB_PORT", "6379"))
            _gg = os.environ.get("FALKORDB_GRAPH", os.environ.get("L3_GRAPH", "lumina_prime"))
            _g3 = _GFB(host=_gh, port=_gp).select_graph(_gg)
            for variant in name_variants:
                org_id = f"org_{variant}"
                _r = _g3.query(
                    f"MATCH (a)-[:LINK {{type: 'member_of'}}]->(s {{id: '{org_id}'}}) RETURN a.id"
                )
                if _r.result_set:
                    for row in _r.result_set:
                        if row[0]:
                            handles.add(row[0])
                    break
        except Exception:
            pass

    return handles


def _pick_citizen_for_message(content: str) -> str | None:
    """Simple citizen picker — delegates to citizen_registry if available."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from citizen_registry import load_all_citizens
        registry = load_all_citizens()
        ai_citizens = [h for h, c in registry.items() if c.get("type") == "ai" and c.get("status") == "active"]
        if ai_citizens:
            import random
            return random.choice(ai_citizens)
    except Exception:
        pass
    return None


async def _handle_inbound(message: discord.Message):
    """Process an inbound Discord message — route to orchestrator + respond via citizen."""
    content = message.content
    author = message.author

    # Strip bot mention
    if client.user in message.mentions:
        content = content.replace(f"<@{client.user.id}>", "").strip()

    if not content:
        return

    # Log inbound
    channel_id = message.channel.id if hasattr(message.channel, "id") else 0
    _log_message("in", str(author), channel_id, content)

    # Detect ALL @citizen mentions in content (not just the first)
    channel_name = message.channel.name if hasattr(message.channel, "name") else "dm"
    mentioned_handles = set()
    target_handle = None

    # Find @handle, @org, @universe, @narrative patterns
    mentioned_groups = []
    for match in re.finditer(r"@([\w:]+)", content):
        possible_handle = match.group(1).lower()

        # 1. Direct citizen mention
        if _load_citizen_profile(possible_handle):
            mentioned_handles.add(possible_handle)
            if target_handle is None:
                target_handle = possible_handle
            continue

        # 2. Routing alias
        if _is_routing_alias(possible_handle):
            if target_handle is None:
                target_handle = possible_handle
            continue

        # 3. Narrative mention (mission:x, objective:y, task:z, vision:w, role:r)
        try:
            from falkordb import FalkorDB as _NFB
            _ng = _NFB(host="localhost", port=6379).select_graph("lumina-prime")
            _nr = _ng.query(
                """
                MATCH (n:Narrative)
                WHERE n.id = $nid OR toLower(n.id) CONTAINS $nid OR toLower(n.name) CONTAINS $nid
                OPTIONAL MATCH (a:Actor)-[]-(n)
                WHERE a.type IN ['ai', 'AI', 'AGENT', 'human', null]
                RETURN n.id, n.name, n.type, collect(DISTINCT a.id) AS actors
                LIMIT 1
                """,
                {"nid": possible_handle},
            )
            if _nr.result_set and _nr.result_set[0][0]:
                _row = _nr.result_set[0]
                linked_actors = [a for a in (_row[3] or []) if a and _load_citizen_profile(a)]
                if linked_actors:
                    mentioned_handles.update(linked_actors)
                    mentioned_groups.append((f"{_row[2]}:{_row[1]}", len(linked_actors)))
                    if target_handle is None:
                        target_handle = possible_handle
                    continue
        except Exception:
            pass

        # 4. Org/universe group mention
        group_handles = _resolve_group_mention(possible_handle)
        if group_handles:
            mentioned_handles.update(group_handles)
            mentioned_groups.append((possible_handle, len(group_handles)))
            if target_handle is None:
                target_handle = possible_handle

    # Strip first @handle from content for routing
    if target_handle:
        content = re.sub(r"@" + re.escape(target_handle) + r"\s*", "", content, count=1).strip()

    # Route to message_router for orchestrator processing
    try:
        from message_router import router
        guild_name = message.guild.name if message.guild else None
        router.route_discord(
            sender=author.display_name,
            content=content,
            channel=channel_name,
            guild=guild_name,
            user_id=str(author.id),
        )
        print(f"  Discord in → routed: [{author.display_name}] {content[:80]}")
    except ImportError:
        print("  message_router not available")

    # Handle /imagine command
    if content.strip().lower().startswith(("/imagine", "/image", "/img")):
        result = handle_imagine_command(target_handle, channel_id, content)
        if result:
            return

    # Separate direct mentions from group-resolved mentions
    group_resolved_handles = set()
    for group_name, _ in mentioned_groups:
        group_resolved_handles.update(_resolve_group_mention(group_name))

    direct_handles = mentioned_handles - group_resolved_handles

    # Wake direct mentions — individual ack per citizen
    for handle in direct_handles:
        profile = _load_citizen_profile(handle)
        if not profile:
            continue
        identity = profile.get("identity", {})
        citizen_type = identity.get("type", "")

        if citizen_type != "human":
            woke = wake_citizen_on_mention(
                from_name=author.display_name,
                target_handle=handle,
                message=content,
                channel_name=channel_name,
            )
            if woke:
                emoji = identity.get("emoji", "")
                name = identity.get("name", handle)
                await message.channel.send(f"{emoji} **{name}** heard you. Waking up...")

    # Wake group mentions — single summary message, wake signals only (no spam)
    for group_name, group_count in mentioned_groups:
        group_handles = _resolve_group_mention(group_name)
        woke_count = 0
        for handle in group_handles:
            profile = _load_citizen_profile(handle)
            if not profile:
                continue
            identity = profile.get("identity", {})
            if identity.get("type") == "human":
                continue
            woke = wake_citizen_on_mention(
                from_name=author.display_name,
                target_handle=handle,
                message=content,
                channel_name=channel_name,
            )
            if woke:
                woke_count += 1

        if woke_count > 0:
            await message.channel.send(
                f"**@{group_name}** — {woke_count} citizens notified."
            )

    # Reply detection — enrich L3 graph with REPLIES_TO link
    if message.reference and message.reference.message_id:
        try:
            original = await message.channel.fetch_message(message.reference.message_id)
            from graph_enricher import on_reply
            on_reply(
                platform="discord",
                channel_id=str(channel_id),
                channel_name=channel_name,
                replier_handle=author.name.lower().replace(" ", "_"),
                replier_name=author.display_name,
                original_author_handle=original.author.name.lower().replace(" ", "_"),
                original_content=original.content or "",
                reply_content=content,
            )
        except Exception:
            pass

    # If a routing alias was used (not a specific citizen), acknowledge
    if target_handle and target_handle not in mentioned_handles and _is_routing_alias(target_handle):
        await message.channel.send(f"Routing to @{target_handle}...")


# ---------------------------------------------------------------------------
# Cross-post thread (kept from original)
# ---------------------------------------------------------------------------

def cross_post_thread(tweets: list, source: str = "Twitter"):
    """Cross-post a tweet thread to #announcements."""
    lines = [f"**New thread on @Mind_Protocol** \U0001F9F5\n"]
    for i, tweet in enumerate(tweets):
        lines.append(tweet if i == 0 else f"\n{tweet}")
    lines.append("\n\u2014 *Posted on X/Twitter*")

    full_text = "\n".join(lines)
    if len(full_text) > 2000:
        chunks, current = [], ""
        for line in lines:
            if len(current) + len(line) + 1 > 1900:
                chunks.append(current)
                current = line
            else:
                current += "\n" + line if current else line
        if current:
            chunks.append(current)
        return [send_announcement(chunk) for chunk in chunks]
    return send_announcement(full_text)


# ---------------------------------------------------------------------------
# Async client — read channel history
# ---------------------------------------------------------------------------

async def fetch_channel_messages(channel_id: int, limit: int = 50):
    """Fetch messages from a channel."""
    channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
    messages = []
    async for msg in channel.history(limit=limit):
        messages.append({
            "id": str(msg.id),
            "author": str(msg.author),
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
            "attachments": [a.url for a in msg.attachments],
            "embeds": [e.to_dict() for e in msg.embeds],
        })
    return list(reversed(messages))


async def read_channel(channel_id: int, limit: int = 50):
    """Read and dump channel messages."""
    await client.wait_until_ready()
    messages = await fetch_channel_messages(channel_id, limit)
    SHRINE.mkdir(parents=True, exist_ok=True)
    with open(DISCORD_LOG, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")
    print(f"Fetched {len(messages)} messages → {DISCORD_LOG}")
    for msg in messages:
        author = msg["author"].split("#")[0]
        content = msg["content"][:200] if msg["content"] else "[embed/attachment]"
        print(f"  [{msg['timestamp'][:16]}] {author}: {content}")
    await client.close()


# ---------------------------------------------------------------------------
# Discord client events
# ---------------------------------------------------------------------------

@client.event
async def on_ready():
    print(f"  Discord bridge online as {client.user}")
    print(f"  Guilds: {', '.join(g.name for g in client.guilds)}")
    # Refresh channel map on connect
    for guild in client.guilds:
        for ch in guild.text_channels:
            _channel_map[ch.name] = ch.id
    _save_channel_map()


@client.event
async def on_message(message):
    """Handle inbound messages — DMs and mentions."""
    if message.author == client.user:
        return
    # Ignore webhook messages (our own citizen messages)
    if message.webhook_id:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions
    has_at_mention = bool(re.search(r"@(\w+)", message.content)) if message.content else False

    if not is_dm and not is_mentioned and not has_at_mention:
        return

    await _handle_inbound(message)


@client.event
async def on_reaction_add(reaction, user):
    """Detect emoji reactions — create REACTED_TO link in L3."""
    if user == client.user or user.bot:
        return
    try:
        from graph_enricher import on_react
        msg = reaction.message
        on_react(
            platform="discord",
            channel_id=str(msg.channel.id),
            message_content=msg.content or "",
            message_author_handle=msg.author.name.lower().replace(" ", "_"),
            reactor_handle=user.name.lower().replace(" ", "_"),
            reactor_name=user.display_name,
            emoji=str(reaction.emoji),
        )
    except Exception:
        pass


@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    """Detect pin/unpin events — update Moment permanence in L3."""
    try:
        from graph_enricher import on_pin
        pins = await channel.pins()
        if not pins:
            return
        latest = pins[0]
        on_pin(
            platform="discord",
            channel_id=str(channel.id),
            message_content=latest.content or "",
            author_handle=latest.author.name.lower().replace(" ", "_") if latest.author else "unknown",
            ts=latest.created_at.timestamp() if latest.created_at else 0,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CLI — list citizens for Discord
# ---------------------------------------------------------------------------

def _list_citizens_for_discord():
    """Print all citizens and their Discord-ready identities."""
    handles = _get_all_citizen_handles()
    print(f"\n  {'Handle':<20} {'Display Name':<35} {'Avatar'}")
    print(f"  {'─'*20} {'─'*35} {'─'*50}")
    for handle in handles:
        profile = _load_citizen_profile(handle)
        if not profile:
            continue
        identity = profile.get("identity", {})
        if identity.get("type") not in ("ai", None):
            # Include AI citizens and citizens with no type set
            if identity.get("type") == "human":
                continue
        display = _citizen_display_name(profile)
        avatar = _citizen_avatar_url(handle, profile) or "—"
        print(f"  @{handle:<19} {display:<35} {avatar[:50]}")
    print(f"\n  {len(handles)} citizens total")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_load_webhook_cache()
_load_channel_map()


def _parse_handle_and_channel(args: list[str]) -> tuple[str | None, int | None, list[str]]:
    """Parse optional @handle + channel from CLI args. Returns (handle, channel_id, remaining_args)."""
    if not args:
        return None, None, []

    handle = None
    idx = 0

    # Check if first arg is a handle (starts with @ or is not a number and not a channel name)
    first = args[0]
    if first.startswith("@"):
        handle = first.lstrip("@")
        idx = 1

    if idx >= len(args):
        return handle, None, []

    # Resolve channel (name or ID)
    ch_ref = args[idx]
    ch_id = resolve_channel(ch_ref)
    if ch_id is None:
        # Maybe first arg was actually a handle without @
        if handle is None and not first.startswith("@"):
            profile = _load_citizen_profile(first)
            if profile:
                handle = first
                idx = 1
                if idx < len(args):
                    ch_id = resolve_channel(args[idx])

    if ch_id is None:
        return handle, None, args[idx:]

    return handle, ch_id, args[idx + 1:]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    # Commands that don't need a token
    if cmd == "list":
        _list_citizens_for_discord()
        sys.exit(0)

    if cmd == "whoami":
        h = detect_handle()
        if h:
            profile = _load_citizen_profile(h)
            display = _citizen_display_name(profile) if profile else h
            print(f"  {display} (@{h})")
        else:
            print("  Could not detect handle. Set MIND_HANDLE or run from citizens/{handle}/")
        sys.exit(0)

    # Everything else needs token
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not set in .env")
        sys.exit(1)

    if cmd == "channels":
        channels = list_channels_sync()
        if channels:
            print(f"\n  {'ID':<22} {'Name':<25} {'Type':<14} Category")
            print(f"  {'─'*22} {'─'*25} {'─'*14} {'─'*20}")
            for ch in channels:
                print(f"  {ch['id']:<22} #{ch['name']:<24} {ch['type']:<14} {ch['category']}")
            print(f"\n  {len(channels)} channels")
        else:
            print("  No channels found (check bot token and permissions)")

    elif cmd == "guild":
        info = guild_info_sync()
        if info:
            print(f"\n  Guild: {info.get('name', '?')}")
            print(f"  ID: {info.get('id', '?')}")
            print(f"  Members: ~{info.get('approximate_member_count', '?')}")
            print(f"  Online: ~{info.get('approximate_presence_count', '?')}")
            print(f"  Owner: {info.get('owner_id', '?')}")
            print(f"  Boosts: {info.get('premium_subscription_count', 0)}")
            if info.get("icon"):
                print(f"  Icon: https://cdn.discordapp.com/icons/{info['id']}/{info['icon']}.png")
        else:
            print("  Could not fetch guild info")

    elif cmd == "read":
        # read <channel> [limit]
        if len(sys.argv) < 3:
            print("Usage: discord_bridge.py read <channel_name_or_id> [limit]")
            sys.exit(1)
        ch_id = resolve_channel(sys.argv[2])
        if not ch_id:
            print(f"  Channel not found: {sys.argv[2]}")
            sys.exit(1)
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        messages = read_channel_sync(ch_id, limit)
        if messages:
            for msg in messages:
                ts = msg["timestamp"][:16] if msg["timestamp"] else "?"
                author = msg["author"]
                content = msg["content"][:200] if msg["content"] else ""
                attachments = " ".join(f"[{a['filename']}]" for a in msg.get("attachments", []))
                reactions = " ".join(f"{r['emoji']}×{r['count']}" for r in msg.get("reactions", []))
                line = f"  [{ts}] {author}: {content}"
                if attachments:
                    line += f" {attachments}"
                if reactions:
                    line += f"  {reactions}"
                print(line)
            print(f"\n  {len(messages)} messages")
        else:
            print("  No messages (or error)")

    elif cmd == "send":
        if len(sys.argv) >= 4:
            ch_id = resolve_channel(sys.argv[2])
            if ch_id:
                send_message(ch_id, " ".join(sys.argv[3:]))
            else:
                print(f"  Channel not found: {sys.argv[2]}")
        elif len(sys.argv) == 3:
            send_announcement(sys.argv[2])
        else:
            print("Usage: discord_bridge.py send <channel> <message>")

    elif cmd == "speak":
        # speak [@handle] <channel> <message>
        handle, ch_id, rest = _parse_handle_and_channel(sys.argv[2:])
        if not ch_id or not rest:
            print("Usage: discord_bridge.py speak [@handle] <channel> <message>")
            sys.exit(1)
        msg = " ".join(rest)
        result = send_as_citizen(handle, ch_id, msg)
        print("  Sent." if result else "  Failed.")

    elif cmd == "image":
        # image [@handle] <channel> <file_or_url> [caption]
        handle, ch_id, rest = _parse_handle_and_channel(sys.argv[2:])
        if not ch_id or not rest:
            print("Usage: discord_bridge.py image [@handle] <channel> <file_or_url> [caption]")
            sys.exit(1)
        file_ref = rest[0]
        caption = " ".join(rest[1:]) if len(rest) > 1 else ""
        if file_ref.startswith("http://") or file_ref.startswith("https://"):
            result = send_as_citizen_file(handle, ch_id, file_url=file_ref, text=caption)
        else:
            result = send_as_citizen_file(handle, ch_id, file_path=file_ref, text=caption)
        print("  Sent." if result else "  Failed.")

    elif cmd == "react":
        # react <channel> <message_id> <emoji>
        if len(sys.argv) < 5:
            print("Usage: discord_bridge.py react <channel> <message_id> <emoji>")
            sys.exit(1)
        ch_id = resolve_channel(sys.argv[2])
        if not ch_id:
            print(f"  Channel not found: {sys.argv[2]}")
            sys.exit(1)
        msg_id = int(sys.argv[3])
        emoji = sys.argv[4]
        add_reaction(ch_id, msg_id, emoji)

    elif cmd == "imagine":
        # imagine [@handle] <channel> <prompt>
        handle, ch_id, rest = _parse_handle_and_channel(sys.argv[2:])
        if not ch_id or not rest:
            print("Usage: discord_bridge.py imagine [@handle] <channel> <prompt>")
            sys.exit(1)
        prompt = " ".join(rest)
        result = imagine_as_citizen(handle, ch_id, prompt)
        print("  Sent." if result else "  Failed.")

    elif cmd == "unread":
        # unread [@handle] [channel]
        args = sys.argv[2:]
        handle = None
        ch_ref = None
        for a in args:
            if a.startswith("@"):
                handle = a.lstrip("@")
            else:
                ch_ref = a
        if not handle:
            handle = detect_handle()
        if not handle:
            print("  Cannot detect handle. Use: unread @handle [channel]")
            sys.exit(1)

        if ch_ref:
            ch_id = resolve_channel(ch_ref)
            if not ch_id:
                print(f"  Channel not found: {ch_ref}")
                sys.exit(1)
            unread = get_unread(handle, ch_id)
            mention_msgs = get_mentions(handle, ch_id)
            print(f"\n  @{handle} in #{ch_ref}: {len(unread)} unread, {len(mention_msgs)} mentions")
            for msg in unread:
                ts = msg["timestamp"][:16] if msg["timestamp"] else "?"
                is_mention = msg in mention_msgs
                marker = " **@**" if is_mention else ""
                print(f"  {'→' if is_mention else ' '} [{ts}] {msg['author']}: {msg['content'][:120]}{marker}")
        else:
            summary = unread_summary(handle)
            if summary:
                print(f"\n  @{handle} — unread summary:")
                print(f"  {'Channel':<22} {'Unread':>7} {'Mentions':>9}")
                print(f"  {'─'*22} {'─'*7} {'─'*9}")
                total_u, total_m = 0, 0
                for ch_name, info in sorted(summary.items()):
                    u, m = info["unread"], info["mentions"]
                    total_u += u
                    total_m += m
                    mention_flag = f"  {'⚡' if m > 0 else ''}"
                    print(f"  #{ch_name:<21} {u:>7} {m:>9}{mention_flag}")
                print(f"  {'─'*22} {'─'*7} {'─'*9}")
                print(f"  {'Total':<22} {total_u:>7} {total_m:>9}")
            else:
                print(f"  @{handle}: all caught up!")

    elif cmd == "markread":
        # markread [@handle] <channel>
        handle, ch_id, _ = _parse_handle_and_channel(sys.argv[2:])
        if not handle:
            handle = detect_handle()
        if not handle or not ch_id:
            print("Usage: discord_bridge.py markread [@handle] <channel>")
            sys.exit(1)
        mark_read_all(handle, ch_id)
        print(f"  @{handle}: marked #{sys.argv[-1]} as read")

    elif cmd == "mentions":
        # mentions [@handle] <channel>
        handle, ch_id, _ = _parse_handle_and_channel(sys.argv[2:])
        if not handle:
            handle = detect_handle()
        if not handle or not ch_id:
            print("Usage: discord_bridge.py mentions [@handle] <channel>")
            sys.exit(1)
        mention_msgs = get_mentions(handle, ch_id)
        if mention_msgs:
            print(f"\n  @{handle} mentioned {len(mention_msgs)} times in #{sys.argv[-1]}:")
            for msg in mention_msgs:
                ts = msg["timestamp"][:16] if msg["timestamp"] else "?"
                print(f"  → [{ts}] {msg['author']}: {msg['content'][:150]}")
        else:
            print(f"  No mentions of @{handle} found")

    elif cmd == "thread":
        if len(sys.argv) >= 3:
            tweets = json.loads(Path(sys.argv[2]).read_text())
            print(f"Cross-posting thread ({len(tweets)} tweets)...")
            cross_post_thread(tweets)
        else:
            print("Usage: discord_bridge.py thread <file.json>")

    elif cmd == "listen":
        print("Starting Discord bridge (citizen webhooks enabled)...")
        client.run(TOKEN)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
