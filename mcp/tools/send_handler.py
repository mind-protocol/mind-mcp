"""
[SPEAK] Send — Send a message to any platform.

Supports: telegram, discord, whatsapp, twitter, email, sms.

All bridge imports are lazy — missing dependencies return clear errors, not crashes.

Usage via MCP:
    send(platform="telegram", message="The feed system is deployed.")
    send(platform="discord", message="Hey team", chat_id="123456789")
    send(platform="whatsapp", message="Bonjour", chat_id="33612345678@c.us")
    send(platform="twitter", message="New release!", reply_to="tweet_id_123")
    send(platform="email", message="Hello", to="user@example.com", subject="Update")
    send(platform="sms", message="Code: 1234", chat_id="+33612345678")
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mind.send")

# Paths — manemus is the source of truth for bridge configs
MANEMUS_ROOT = Path(os.getenv("MANEMUS_ROOT", "/home/mind-protocol/manemus"))
STATE_DIR = MANEMUS_ROOT / "shrine" / "state"

# Nicolas's Telegram chat ID
NICOLAS_CHAT_ID = "1864364329"

# Max message length (Telegram limit is 4096, others vary)
MAX_MESSAGE_LEN = 4000


TOOL_SCHEMA = {
    "name": "send",
    "description": (
        "[SPEAK] Send a message to any platform: Telegram, Discord, WhatsApp, "
        "Twitter/X, Email, SMS. Auto-detects your citizen handle. "
        "Use chat_id for the target (Telegram chat, Discord channel, WhatsApp number, phone). "
        "For email, use 'to' and 'subject'. For Twitter, use 'reply_to' to reply to a tweet."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "platform": {
                "type": "string",
                "enum": ["telegram", "discord", "whatsapp", "twitter", "email", "sms"],
                "description": "Platform to send on.",
            },
            "message": {
                "type": "string",
                "description": "The message to send.",
            },
            "handle": {
                "type": "string",
                "description": "Your citizen handle (without @). Auto-detected if omitted.",
            },
            "chat_id": {
                "type": "string",
                "description": (
                    "Target: Telegram chat ID, Discord channel ID, "
                    "WhatsApp chat ID (e.g. '33612345678@c.us'), phone number for SMS."
                ),
            },
            # Email-specific
            "to": {
                "type": "string",
                "description": "Email recipient address (for platform='email').",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line (for platform='email').",
            },
            # Twitter-specific
            "reply_to": {
                "type": "string",
                "description": "Tweet ID to reply to (for platform='twitter').",
            },
        },
        "required": ["platform", "message"],
    },
}


def handle_send(args: Dict[str, Any]) -> Dict[str, Any]:
    """Route message to the right platform."""
    platform = args.get("platform", "").lower()
    message = (args.get("message") or "").strip()

    if not message:
        return _err("'message' is required and cannot be empty.")
    if not platform:
        return _err("'platform' is required.")

    dispatch = {
        "telegram": _send_telegram,
        "discord": _send_discord,
        "whatsapp": _send_whatsapp,
        "twitter": _send_twitter,
        "email": _send_email,
        "sms": _send_sms,
    }

    handler = dispatch.get(platform)
    if not handler:
        return _err(f"Unknown platform '{platform}'. Use: {', '.join(dispatch.keys())}.")

    return handler(args)


# ── Telegram ────────────────────────────────────────────────────────────────

def _send_telegram(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Telegram message via Bot API."""
    import requests

    message = (args.get("message") or "").strip()
    chat_id = args.get("chat_id", NICOLAS_CHAT_ID)
    handle = _resolve_handle(args)

    formatted = f"*@{handle}:*\n{message}" if handle else f"*[citizen]:*\n{message}"
    if len(formatted) > MAX_MESSAGE_LEN:
        formatted = formatted[:MAX_MESSAGE_LEN - 3] + "..."

    config = _load_json(STATE_DIR / "telegram_config.json")
    bot_token = config.get("bot_token")
    if not bot_token:
        return _err("Telegram not configured. No bot_token in telegram_config.json.")

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted, "parse_mode": "Markdown"}

    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.ok:
            msg_id = resp.json()["result"]["message_id"]
            _log_message("telegram", formatted, chat_id, msg_id)
            return _ok(f"Sent to Telegram as @{handle or 'citizen'}. (message_id: {msg_id})")

        # Retry without Markdown on parse error
        resp_data = resp.json() if "json" in resp.headers.get("content-type", "") else {}
        if "can't parse entities" in resp_data.get("description", ""):
            payload.pop("parse_mode", None)
            resp2 = requests.post(api_url, json=payload, timeout=15)
            if resp2.ok:
                msg_id = resp2.json()["result"]["message_id"]
                _log_message("telegram", formatted, chat_id, msg_id)
                return _ok(f"Sent to Telegram as @{handle or 'citizen'} (plain). (message_id: {msg_id})")

        return _err(f"Telegram API error: {resp.status_code} — {resp.text[:200]}")
    except Exception as e:
        return _err(f"Telegram send failed: {e}")


# ── Discord ─────────────────────────────────────────────────────────────────

def _send_discord(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Discord message as a citizen via webhook."""
    channel_id = args.get("chat_id")
    if not channel_id:
        return _err("'chat_id' (Discord channel ID) is required for Discord.")

    handle = _resolve_handle(args)
    message = (args.get("message") or "").strip()

    try:
        _ensure_manemus_path("scripts")
        from discord_bridge import send_as_citizen

        result = send_as_citizen(
            handle=handle,
            channel_id=int(channel_id),
            text=message,
        )
        if result:
            _log_message("discord", message, channel_id)
            return _ok(f"Sent to Discord channel {channel_id} as @{handle or 'citizen'}.")
        else:
            return _err("Discord send returned no result. Check webhook config.")
    except ImportError:
        return _err("Discord bridge not available. Check MANEMUS_ROOT.")
    except Exception as e:
        return _err(f"Discord send failed: {e}")


# ── WhatsApp ────────────────────────────────────────────────────────────────

def _send_whatsapp(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a WhatsApp message via WAHA."""
    chat_id = args.get("chat_id")
    if not chat_id:
        return _err("'chat_id' (WhatsApp chat ID, e.g. '33612345678@c.us') is required.")

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    # Prefix with handle so recipient knows who's talking
    text = f"[@{handle}] {message}" if handle else message

    try:
        _ensure_manemus_path("scripts")
        from whatsapp_bridge import send_text

        result = send_text(chat_id=chat_id, text=text)
        if result:
            _log_message("whatsapp", text, chat_id)
            return _ok(f"Sent to WhatsApp chat {chat_id} as @{handle or 'citizen'}.")
        else:
            return _err("WhatsApp send failed. Is WAHA running?")
    except ImportError:
        return _err("WhatsApp bridge not available. Check MANEMUS_ROOT.")
    except Exception as e:
        return _err(f"WhatsApp send failed: {e}")


# ── Twitter/X ───────────────────────────────────────────────────────────────

def _send_twitter(args: Dict[str, Any]) -> Dict[str, Any]:
    """Post a tweet or reply via X API."""
    message = (args.get("message") or "").strip()
    reply_to = args.get("reply_to")

    if len(message) > 280:
        return _err(f"Tweet too long ({len(message)} chars). Max 280.")

    try:
        _ensure_manemus_path("scripts")
        from twitter_bridge import post_tweet

        result = post_tweet(text=message, reply_to=reply_to)
        if result:
            tweet_id = result.get("data", {}).get("id", "?")
            _log_message("twitter", message, "public", tweet_id)
            action = "Reply" if reply_to else "Tweet"
            return _ok(f"{action} posted. (tweet_id: {tweet_id})")
        else:
            return _err("Twitter post returned no result. Check API config.")
    except ImportError:
        return _err("Twitter bridge not available. Check MANEMUS_ROOT.")
    except Exception as e:
        return _err(f"Twitter send failed: {e}")


# ── Email ───────────────────────────────────────────────────────────────────

def _send_email(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an email from a citizen via Resend/SendGrid."""
    to = args.get("to")
    if not to:
        return _err("'to' (recipient email address) is required for email.")

    subject = args.get("subject", "Message from Mind Protocol")
    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    if not handle:
        return _err("Could not detect citizen handle. Required for email sender identity.")

    try:
        _ensure_manemus_path("scripts")
        from citizen_email_service import send_email

        result = send_email(
            from_handle=handle,
            to=to,
            subject=subject,
            body=message,
        )
        status = result.get("status", "unknown")
        provider = result.get("provider", "unknown")
        _log_message("email", f"[{subject}] {message[:100]}", to)
        return _ok(f"Email {status} via {provider} from {handle}@mindprotocol.ai to {to}.")
    except ImportError:
        return _err("Email service not available. Check MANEMUS_ROOT.")
    except Exception as e:
        return _err(f"Email send failed: {e}")


# ── SMS ─────────────────────────────────────────────────────────────────────

def _send_sms(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send an SMS via Twilio."""
    phone = args.get("chat_id")
    if not phone:
        return _err("'chat_id' (phone number, e.g. '+33612345678') is required for SMS.")

    message = (args.get("message") or "").strip()
    handle = _resolve_handle(args)

    text = f"[@{handle}] {message}" if handle else message

    try:
        _ensure_manemus_path("scripts")
        from sms_bridge import send_message

        result = send_message(text=text, phone=phone)
        if result:
            _log_message("sms", text, phone)
            return _ok(f"SMS sent to {phone}.")
        else:
            return _err("SMS send failed. Check Twilio config.")
    except ImportError:
        return _err("SMS bridge not available. Check MANEMUS_ROOT.")
    except Exception as e:
        return _err(f"SMS send failed: {e}")


# ── Shared helpers ──────────────────────────────────────────────────────────

def _resolve_handle(args: Dict[str, Any]) -> Optional[str]:
    """Get citizen handle from args or auto-detect."""
    handle = (args.get("handle") or "").strip().lstrip("@")
    if handle:
        return handle
    return _detect_handle()


def _detect_handle() -> Optional[str]:
    """Try to detect the current citizen handle from env/CWD."""
    # 1. CITIZEN_HANDLE env var
    handle = os.getenv("CITIZEN_HANDLE", "").strip().lstrip("@")
    if handle:
        return handle

    # 2. CWD-based detection
    cwd = Path.cwd()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == "citizens" and i + 1 < len(parts):
            return parts[i + 1]

    # 3. ACTOR_ID env var
    actor_id = os.getenv("ACTOR_ID", "").strip()
    if actor_id:
        for prefix in ("AGENT_", "citizen_", "actor_"):
            if actor_id.lower().startswith(prefix.lower()):
                return actor_id[len(prefix):].lower()
        return actor_id.lower()

    return None


def _ensure_manemus_path(subdir: str):
    """Add manemus subdirectory to sys.path if not already present."""
    path = str(MANEMUS_ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)
    # Also add root for internal imports within bridges
    root = str(MANEMUS_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file, returning {} on any error."""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load {path.name}: {e}")
    return {}


def _log_message(platform: str, text: str, target: str, msg_id: Any = None):
    """Append to the platform's shared message log."""
    log_file = STATE_DIR / f"{platform}_messages.jsonl"
    try:
        entry = {
            "ts": datetime.now().isoformat(),
            "direction": "out",
            "source": "mcp_send",
            "text": text[:200],
            "target": str(target),
        }
        if msg_id is not None:
            entry["message_id"] = str(msg_id)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


# ── Response helpers ────────────────────────────────────────────────────────

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
