"""WhatsApp bridge shim — wraps runtime.bridges.whatsapp_bridge for MCP send_handler compatibility.

send_handler.py imports `from whatsapp_bridge import send_text` from PROJECT_ROOT/scripts/.
The actual bridge lives in mind-mcp/runtime/bridges/whatsapp_bridge.py and exports send_message().
This shim bridges the gap.
"""

import os
import sys
import logging
import requests

logger = logging.getLogger("bridge.whatsapp.shim")

WAHA_URL = os.environ.get("WAHA_URL", "http://localhost:3001")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")


def _waha_headers():
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY
    return headers


def send_text(chat_id: str, text: str) -> bool:
    """Send a text message via WAHA REST API. Returns True on success."""
    if not WAHA_URL:
        logger.error("WAHA_URL not configured")
        return False

    # Ensure chat_id has @c.us suffix for personal chats
    if not chat_id.endswith("@c.us") and not chat_id.endswith("@g.us"):
        chat_id = f"{chat_id}@c.us"

    url = f"{WAHA_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": WAHA_SESSION,
    }

    try:
        resp = requests.post(url, json=payload, headers=_waha_headers(), timeout=15)
        if resp.status_code == 200 or resp.status_code == 201:
            logger.info(f"WhatsApp sent to {chat_id}: {text[:50]}...")
            return True
        else:
            logger.error(f"WAHA error {resp.status_code}: {resp.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"WAHA unreachable at {WAHA_URL}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False
