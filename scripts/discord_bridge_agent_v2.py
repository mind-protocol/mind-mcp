"""
Discord Bridge — Gateway between Discord and the Mind Protocol L3 graph.

Listens for inbound messages, replies, reactions, citations.
Sends outbound messages as citizens via webhooks.
Reads channel history via REST API.

All graph enrichment is best-effort (try/except around every call).
"""

import asyncio
import json
import logging
import os
import re
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.discord_bridge")

# Project paths
PROJECT_ROOT = Path(os.getenv("MIND_PROJECT_ROOT", Path(__file__).parent.parent))
STATE_DIR = PROJECT_ROOT / "shrine" / "state"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Ensure scripts on path for graph_enricher imports
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Discord config
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "985825810667667487")  # AutonomousAIs default

# Webhook cache for sending as citizens
WEBHOOK_CACHE_PATH = STATE_DIR / "discord_webhook_cache.json"
CHANNEL_MAP_PATH = STATE_DIR / "discord_channel_map.json"
MESSAGES_LOG_PATH = STATE_DIR / "discord_messages.jsonl"

# Lazy-loaded discord.py client (only when bot mode is started)
_client = None
_loop = None


# ── Token resolution ──────────────────────────────────────────────────────

def _get_bot_token() -> str:
    """Resolve Discord bot token from env or .env file."""
    token = DISCORD_BOT_TOKEN
    if token:
        return token

    for env_path in [PROJECT_ROOT / ".env", Path("/home/mind-protocol/mind-mcp/.env")]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("DISCORD_BOT_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return ""


# ── Webhook sending (sync, no discord.py needed) ─────────────────────────

def _load_webhook_cache() -> Dict[str, str]:
    """Load channel_id -> webhook_url mapping."""
    try:
        if WEBHOOK_CACHE_PATH.exists():
            return json.loads(WEBHOOK_CACHE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def send_as_citizen(handle: str, channel_id: int, text: str) -> Optional[Dict[str, Any]]:
    """Send a message to Discord as a citizen via webhook.

    Args:
        handle: Citizen handle (used as webhook username).
        channel_id: Discord channel ID.
        text: Message content.

    Returns:
        API response dict, or None on failure.
    """
    import requests

    cache = _load_webhook_cache()
    webhook_url = cache.get(str(channel_id))

    if not webhook_url:
        # Try to create a webhook for this channel
        webhook_url = _create_webhook(channel_id)
        if not webhook_url:
            logger.warning(f"No webhook for channel {channel_id}")
            return None

    display_name = handle.replace("_", " ").title() if handle else "Citizen"
    payload = {
        "content": text[:2000],
        "username": display_name,
    }

    try:
        resp = requests.post(f"{webhook_url}?wait=true", json=payload, timeout=15)
        if resp.ok:
            result = resp.json()
            _log_outbound(channel_id, handle, text, result.get("id"))

            # Enrich L3 graph (best-effort)
            try:
                from graph_enricher import on_message
                mentioned = [m.group(1).lower() for m in re.finditer(r"@(\w+)", text)]
                on_message(
                    platform="discord",
                    channel_id=str(channel_id),
                    channel_name=str(channel_id),
                    author_name=handle,
                    author_handle=handle,
                    content=text,
                    mentioned_handles=mentioned,
                    direction="out",
                )
            except Exception as e:
                logger.debug(f"Graph enrichment for outbound message failed: {e}")

            return result
        else:
            logger.warning(f"Webhook send failed: {resp.status_code} — {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"Webhook send error: {e}")
        return None


def _create_webhook(channel_id: int) -> Optional[str]:
    """Create a webhook for a channel via Discord REST API."""
    import requests

    token = _get_bot_token()
    if not token:
        return None

    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    try:
        resp = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/webhooks",
            headers=headers,
            json={"name": "Mind Protocol Bridge"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            webhook_url = f"https://discord.com/api/webhooks/{data['id']}/{data['token']}"
            # Cache it
            cache = _load_webhook_cache()
            cache[str(channel_id)] = webhook_url
            try:
                WEBHOOK_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
                WEBHOOK_CACHE_PATH.write_text(json.dumps(cache, indent=2))
            except OSError:
                pass
            return webhook_url
    except Exception as e:
        logger.debug(f"Webhook creation failed: {e}")
    return None


# ── REST API reading (sync, no discord.py needed) ────────────────────────

def read_channel_sync(channel_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Read channel messages via Discord REST API (synchronous).

    Args:
        channel_id: Discord channel ID.
        limit: Max messages to fetch (1-100).

    Returns:
        List of message dicts from the Discord API.
    """
    import requests

    token = _get_bot_token()
    if not token:
        logger.warning("No Discord bot token available")
        return []

    headers = {"Authorization": f"Bot {token}"}
    try:
        resp = requests.get(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=headers,
            params={"limit": min(limit, 100)},
            timeout=15,
        )
        if resp.ok:
            messages = resp.json()
            # Log inbound messages
            for msg in messages:
                _log_inbound_rest(channel_id, msg)
            return messages
        else:
            logger.warning(f"Discord read failed: {resp.status_code}")
            return []
    except Exception as e:
        logger.warning(f"Discord read error: {e}")
        return []


# ── Bot mode (discord.py gateway — listens for events) ───────────────────

def start_bot():
    """Start the Discord bot in a background thread.

    Listens for:
      - on_message: inbound messages, reply detection, citation detection
      - on_reaction_add: emoji reactions
    """
    global _client, _loop

    try:
        import discord
    except ImportError:
        logger.error("discord.py not installed — pip install discord.py")
        return

    token = _get_bot_token()
    if not token:
        logger.error("No DISCORD_BOT_TOKEN — cannot start bot")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    intents.members = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Discord bot connected as {client.user}")

    @client.event
    async def on_message(message):
        """Handle inbound messages — enrich L3, detect replies + citations."""
        if message.author == client.user:
            return
        if message.author.bot:
            return

        _handle_inbound(message)

        # ── Reply detection ──
        if message.reference and message.reference.message_id:
            try:
                original = await message.channel.fetch_message(message.reference.message_id)
                from graph_enricher import on_reply
                on_reply(
                    platform="discord",
                    channel_id=str(message.channel.id),
                    channel_name=message.channel.name if hasattr(message.channel, "name") else "dm",
                    replier_handle=message.author.name.lower().replace(" ", "_"),
                    replier_name=message.author.display_name,
                    original_author_handle=original.author.name.lower().replace(" ", "_"),
                    original_content=original.content or "",
                    reply_content=message.content,
                )
            except Exception as e:
                logger.warning(f"Reply detection failed for message {message.id}: {e}")

        # ── Citation detection ──
        _handle_citations(message)

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
        except Exception as e:
            logger.debug(f"Reaction enrichment failed: {e}")

    _client = client
    _loop = asyncio.new_event_loop()

    def _run():
        asyncio.set_event_loop(_loop)
        _loop.run_until_complete(client.start(token))

    thread = threading.Thread(target=_run, daemon=True, name="discord-bridge")
    thread.start()
    logger.info("Discord bot thread started")


# ── Inbound message handling ─────────────────────────────────────────────

def _handle_inbound(message):
    """Process an inbound Discord message — enrich L3 graph + log."""
    author_handle = message.author.name.lower().replace(" ", "_")
    author_name = message.author.display_name
    content = message.content or ""
    channel_id = str(message.channel.id)
    channel_name = message.channel.name if hasattr(message.channel, "name") else "dm"

    # Log to JSONL
    _log_inbound_event(channel_id, channel_name, author_handle, author_name, content, message)

    # Enrich L3 graph (best-effort)
    try:
        from graph_enricher import on_message

        # Extract @mentions
        mentioned = []
        for user in message.mentions:
            mentioned.append(user.name.lower().replace(" ", "_"))

        on_message(
            platform="discord",
            channel_id=channel_id,
            channel_name=channel_name,
            author_name=author_name,
            author_handle=author_handle,
            content=content,
            mentioned_handles=mentioned,
            direction="in",
        )
    except Exception as e:
        logger.warning(f"Inbound message graph enrichment failed: {e}")


def _handle_citations(message):
    """Detect citations in a Discord message.

    Two forms:
      1. Discord embeds with type 'rich' that quote other messages
      2. Markdown quotes: lines starting with '> '
    """
    content = message.content or ""
    channel_id = str(message.channel.id)
    channel_name = message.channel.name if hasattr(message.channel, "name") else "dm"
    citer_handle = message.author.name.lower().replace(" ", "_")
    citer_name = message.author.display_name

    # ── Embed-based citations ──
    try:
        for embed in (message.embeds or []):
            if embed.type == "rich" and embed.description:
                try:
                    from graph_enricher import on_reply
                    on_reply(
                        platform="discord",
                        channel_id=channel_id,
                        channel_name=channel_name,
                        replier_handle=citer_handle,
                        replier_name=citer_name,
                        original_author_handle=embed.author.name.lower().replace(" ", "_") if embed.author else "unknown",
                        original_content=embed.description or "",
                        reply_content=content,
                    )
                except Exception as e:
                    logger.debug(f"Embed citation enrichment failed: {e}")
    except Exception as e:
        logger.debug(f"Citation embed iteration failed: {e}")

    # ── Markdown quote citations (lines starting with '> ') ──
    try:
        quote_lines = [line[2:] for line in content.split("\n") if line.startswith("> ")]
        if quote_lines:
            quoted_text = "\n".join(quote_lines)
            non_quote_text = "\n".join(
                line for line in content.split("\n") if not line.startswith("> ")
            ).strip()

            if quoted_text.strip():
                try:
                    from graph_enricher import on_reply
                    on_reply(
                        platform="discord",
                        channel_id=channel_id,
                        channel_name=channel_name,
                        replier_handle=citer_handle,
                        replier_name=citer_name,
                        original_author_handle="unknown",  # Can't determine from markdown quotes
                        original_content=quoted_text,
                        reply_content=non_quote_text or content,
                    )
                except Exception as e:
                    logger.debug(f"Markdown quote citation enrichment failed: {e}")
    except Exception as e:
        logger.debug(f"Markdown quote parsing failed: {e}")


# ── Logging helpers ──────────────────────────────────────────────────────

def _log_inbound_event(channel_id, channel_name, author_handle, author_name, content, message):
    """Append inbound message to discord_messages.jsonl."""
    try:
        entry = {
            "ts": message.created_at.isoformat() if hasattr(message, "created_at") else "",
            "direction": "in",
            "channel": channel_id,
            "channel_name": channel_name,
            "from": author_name,
            "author_handle": author_handle,
            "text": content[:500],
            "message_id": str(message.id) if hasattr(message, "id") else "",
        }
        MESSAGES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _log_inbound_rest(channel_id, msg_data):
    """Log a message fetched via REST API."""
    try:
        author = msg_data.get("author", {})
        entry = {
            "ts": msg_data.get("timestamp", ""),
            "direction": "in",
            "channel": str(channel_id),
            "from": author.get("username", "?"),
            "author_handle": author.get("username", "?").lower().replace(" ", "_"),
            "text": (msg_data.get("content") or "")[:500],
            "message_id": msg_data.get("id", ""),
            "source": "rest_api",
        }
        MESSAGES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _log_outbound(channel_id, handle, text, message_id=None):
    """Log an outbound webhook message."""
    try:
        entry = {
            "ts": "",
            "direction": "out",
            "channel": str(channel_id),
            "from": handle,
            "author_handle": handle,
            "text": text[:500],
            "source": "webhook",
        }
        if message_id:
            entry["message_id"] = str(message_id)
        MESSAGES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


# ── Module-level entry point ─────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    start_bot()
    # Keep main thread alive
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Discord bridge shutting down")
