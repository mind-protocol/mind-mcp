"""
Telegram Notify Tool — Send a message to Nicolas on Telegram.

Auto-detects the calling citizen's handle and prefixes the message with it,
so Nicolas always knows who's talking.

Usage via MCP:
    telegram_notify(message="The feed system is deployed and tested.")
    telegram_notify(message="Need your input on the auth migration.", handle="forge")
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("mind.telegram_notify")

# Paths — manemus is the source of truth for TG config
MANEMUS_ROOT = Path(os.getenv("MANEMUS_ROOT", "/home/mind-protocol/manemus"))
CONFIG_FILE = MANEMUS_ROOT / "shrine" / "state" / "telegram_config.json"
MESSAGES_FILE = MANEMUS_ROOT / "shrine" / "state" / "telegram_messages.jsonl"

# Nicolas's Telegram chat ID
NICOLAS_CHAT_ID = "1864364329"

# Max message length (Telegram limit is 4096)
MAX_MESSAGE_LEN = 4000


# ── Tool Schema ──────────────────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "telegram_notify",
    "description": (
        "Send a message to Nicolas (@nlr_ai) on Telegram. "
        "Auto-detects your citizen handle and prefixes the message with it. "
        "Use this to report progress, ask questions, escalate blockers, or share updates. "
        "The message is sent as the calling citizen — Nicolas sees who sent it."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to send. Supports Markdown (bold, italic, code, links).",
            },
            "handle": {
                "type": "string",
                "description": (
                    "Your citizen handle (without @). Auto-detected from actor_id or CWD if omitted. "
                    "Pass explicitly if auto-detection fails."
                ),
            },
        },
        "required": ["message"],
    },
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_tg_config() -> Dict[str, Any]:
    """Load Telegram config from manemus state."""
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load TG config: {e}")
    return {}


def _detect_handle() -> Optional[str]:
    """Try to detect the current citizen handle from CWD or environment."""
    # 1. CITIZEN_HANDLE env var (set by citizen_wake / orchestrator)
    handle = os.getenv("CITIZEN_HANDLE", "").strip().lstrip("@")
    if handle:
        return handle

    # 2. CWD-based detection: sandbox/citizens/{handle}/ or citizens/{handle}/
    cwd = Path.cwd()
    parts = cwd.parts
    for i, part in enumerate(parts):
        if part == "citizens" and i + 1 < len(parts):
            return parts[i + 1]

    # 3. ACTOR_ID env var (MCP context)
    actor_id = os.getenv("ACTOR_ID", "").strip()
    if actor_id:
        # Strip common prefixes: AGENT_Forge -> forge, citizen_isabella -> isabella
        for prefix in ("AGENT_", "citizen_", "actor_"):
            if actor_id.lower().startswith(prefix.lower()):
                return actor_id[len(prefix):].lower()
        return actor_id.lower()

    return None


def _log_message(text: str, chat_id: str, message_id: int):
    """Append to the shared TG message log."""
    try:
        log_entry = {
            "ts": datetime.now().isoformat(),
            "direction": "out",
            "source": "mcp_telegram_notify",
            "message_id": message_id,
            "chat_id": chat_id,
            "text": text[:200],
        }
        MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except OSError:
        pass


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}


# ── Handler ──────────────────────────────────────────────────────────────────

def handle_telegram_notify(args: Dict[str, Any]) -> Dict[str, Any]:
    """Main handler for the telegram_notify MCP tool."""
    message = (args.get("message") or "").strip()
    if not message:
        return _err("'message' is required and cannot be empty.")

    # Detect handle
    handle = (args.get("handle") or "").strip().lstrip("@")
    if not handle:
        handle = _detect_handle()

    # Build the formatted message
    if handle:
        formatted = f"*@{handle}:*\n{message}"
    else:
        formatted = f"*[unknown citizen]:*\n{message}"

    # Truncate if needed
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
        "chat_id": NICOLAS_CHAT_ID,
        "text": formatted,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=15)
        if resp.ok:
            result = resp.json()["result"]
            _log_message(formatted, NICOLAS_CHAT_ID, result["message_id"])
            handle_tag = f"@{handle}" if handle else "unknown"
            return {
                "content": [{
                    "type": "text",
                    "text": f"Message sent to Nicolas as {handle_tag}. (message_id: {result['message_id']})",
                }]
            }
        else:
            # Retry without Markdown if parse fails
            resp_data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
            if "can't parse entities" in resp_data.get("description", ""):
                payload.pop("parse_mode", None)
                resp2 = requests.post(api_url, json=payload, timeout=15)
                if resp2.ok:
                    result = resp2.json()["result"]
                    _log_message(formatted, NICOLAS_CHAT_ID, result["message_id"])
                    handle_tag = f"@{handle}" if handle else "unknown"
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Message sent to Nicolas as {handle_tag} (plain text fallback). (message_id: {result['message_id']})",
                        }]
                    }
            return _err(f"Telegram API error: {resp.status_code} — {resp.text[:200]}")
    except requests.exceptions.RequestException as e:
        return _err(f"Network error sending to Telegram: {e}")
