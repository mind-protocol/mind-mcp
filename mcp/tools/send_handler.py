"""
[SPEAK] Send — Send a message to any platform.

Currently supports: telegram.
Future: discord, whatsapp, twitter, email, sms, linkedin.

Usage via MCP:
    send(platform="telegram", message="The feed system is deployed.")
    send(platform="telegram", message="Need input.", handle="forge")
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("mind.send")

# Paths — manemus is the source of truth for TG config
MANEMUS_ROOT = Path(os.getenv("MANEMUS_ROOT", "/home/mind-protocol/manemus"))
TG_CONFIG_FILE = MANEMUS_ROOT / "shrine" / "state" / "telegram_config.json"
TG_MESSAGES_FILE = MANEMUS_ROOT / "shrine" / "state" / "telegram_messages.jsonl"

# Nicolas's Telegram chat ID
NICOLAS_CHAT_ID = "1864364329"

# Max message length (Telegram limit is 4096)
MAX_MESSAGE_LEN = 4000

# Supported platforms
SUPPORTED_PLATFORMS = ["telegram"]


TOOL_SCHEMA = {
    "name": "send",
    "description": (
        "[SPEAK] Send a message to any platform. Currently supports Telegram. "
        "Auto-detects your citizen handle and prefixes the message with it, "
        "so the recipient always knows who's talking."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "platform": {
                "type": "string",
                "enum": ["telegram", "discord", "whatsapp", "twitter", "email", "sms"],
                "description": "Platform to send on. Currently only 'telegram' is active.",
            },
            "message": {
                "type": "string",
                "description": "The message to send. Supports Markdown (bold, italic, code, links).",
            },
            "handle": {
                "type": "string",
                "description": (
                    "Your citizen handle (without @). Auto-detected from actor_id or CWD if omitted."
                ),
            },
            "chat_id": {
                "type": "string",
                "description": "Target chat ID. Defaults to Nicolas's chat for Telegram.",
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

    if platform == "telegram":
        return _send_telegram(args)
    else:
        return _err(f"Platform '{platform}' not yet supported. Available: {', '.join(SUPPORTED_PLATFORMS)}.")


# ── Telegram ────────────────────────────────────────────────────────────────

def _send_telegram(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a Telegram message (absorbed from telegram_notify.py)."""
    message = (args.get("message") or "").strip()
    chat_id = args.get("chat_id", NICOLAS_CHAT_ID)

    # Detect handle
    handle = (args.get("handle") or "").strip().lstrip("@")
    if not handle:
        handle = _detect_handle()

    # Build formatted message
    if handle:
        formatted = f"*@{handle}:*\n{message}"
    else:
        formatted = f"*[unknown citizen]:*\n{message}"

    if len(formatted) > MAX_MESSAGE_LEN:
        formatted = formatted[:MAX_MESSAGE_LEN - 3] + "..."

    # Load config
    config = _load_tg_config()
    bot_token = config.get("bot_token")
    if not bot_token:
        return _err("Telegram not configured. No bot_token in telegram_config.json.")

    # Send
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": formatted,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.ok:
            result = resp.json()["result"]
            _log_tg_message(formatted, chat_id, result["message_id"])
            handle_tag = f"@{handle}" if handle else "unknown"
            return _ok(f"Message sent to Telegram as {handle_tag}. (message_id: {result['message_id']})")
        else:
            # Retry without Markdown if parse fails
            resp_data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
            if "can't parse entities" in resp_data.get("description", ""):
                payload.pop("parse_mode", None)
                resp2 = requests.post(api_url, json=payload, timeout=15)
                if resp2.ok:
                    result = resp2.json()["result"]
                    _log_tg_message(formatted, chat_id, result["message_id"])
                    handle_tag = f"@{handle}" if handle else "unknown"
                    return _ok(f"Message sent to Telegram as {handle_tag} (plain text). (message_id: {result['message_id']})")
            return _err(f"Telegram API error: {resp.status_code} — {resp.text[:200]}")
    except requests.exceptions.RequestException as e:
        return _err(f"Network error sending to Telegram: {e}")


# ── Telegram helpers ────────────────────────────────────────────────────────

def _load_tg_config() -> Dict[str, Any]:
    """Load Telegram config from manemus state."""
    try:
        if TG_CONFIG_FILE.exists():
            return json.loads(TG_CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load TG config: {e}")
    return {}


def _detect_handle() -> Optional[str]:
    """Try to detect the current citizen handle."""
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


def _log_tg_message(text: str, chat_id: str, message_id: int):
    """Append to the shared TG message log."""
    try:
        log_entry = {
            "ts": datetime.now().isoformat(),
            "direction": "out",
            "source": "mcp_send",
            "message_id": message_id,
            "chat_id": chat_id,
            "text": text[:200],
        }
        TG_MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TG_MESSAGES_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except OSError:
        pass


# ── Response helpers ────────────────────────────────────────────────────────

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
