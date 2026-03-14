"""
[SPEAK] Read — Read messages and mentions from any platform.

Actions:
  history  — Read recent messages from a conversation (local JSONL logs or API)
  mentions — Read recent mentions of a citizen
  inbox    — Read email inbox (email platform only)

All bridge imports are lazy — missing dependencies return clear errors, not crashes.

Usage via MCP:
    read(action="history", platform="telegram", limit=20)
    read(action="history", platform="discord", chat_id="123456789", limit=10)
    read(action="mentions", platform="twitter", limit=5)
    read(action="inbox", platform="email", handle="forge")
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.read")

PROJECT_ROOT = Path(os.getenv("MIND_PROJECT_ROOT", Path(__file__).parent.parent.parent))
STATE_DIR = PROJECT_ROOT / "shrine" / "state"

# JSONL log files per platform
PLATFORM_LOGS = {
    "telegram": "telegram_messages.jsonl",
    "whatsapp": "whatsapp_messages.jsonl",
    "discord": "discord_messages.jsonl",
    "sms": "sms_messages.jsonl",
    "twitter": "twitter_mentions.jsonl",
}


TOOL_SCHEMA = {
    "name": "read",
    "description": (
        "[SPEAK] Read messages from any platform. "
        "Use action='history' to read recent messages from a conversation log. "
        "Use action='mentions' to see recent mentions. "
        "Use action='inbox' for email. "
        "Supports: telegram, discord, whatsapp, twitter, email, sms."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["history", "mentions", "inbox"],
                "description": "What to read: conversation history, mentions, or email inbox.",
            },
            "platform": {
                "type": "string",
                "enum": ["telegram", "discord", "whatsapp", "twitter", "email", "sms"],
                "description": "Platform to read from.",
            },
            "chat_id": {
                "type": "string",
                "description": (
                    "Filter by conversation. Telegram chat ID, Discord channel ID, "
                    "WhatsApp chat ID, phone number for SMS. "
                    "If omitted, returns all messages across conversations."
                ),
            },
            "handle": {
                "type": "string",
                "description": "Citizen handle (for email inbox, or filtering mentions).",
            },
            "limit": {
                "type": "integer",
                "description": "Max messages to return (default: 20, max: 100).",
            },
            "direction": {
                "type": "string",
                "enum": ["all", "in", "out"],
                "description": "Filter by direction: all, inbound only, outbound only. Default: all.",
            },
            "search": {
                "type": "string",
                "description": "Search term to filter messages by content.",
            },
        },
        "required": ["action", "platform"],
    },
}


def handle_read(args: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch read actions."""
    action = args.get("action")
    platform = (args.get("platform") or "").lower()

    if not action:
        return _err("'action' is required. Use: history, mentions, inbox.")
    if not platform:
        return _err("'platform' is required.")

    if action == "history":
        return _read_history(platform, args)
    elif action == "mentions":
        return _read_mentions(platform, args)
    elif action == "inbox":
        if platform != "email":
            return _err("action='inbox' is only available for platform='email'.")
        return _read_email_inbox(args)
    else:
        return _err(f"Unknown action '{action}'. Use: history, mentions, inbox.")


# ── History ─────────────────────────────────────────────────────────────────

def _read_history(platform: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Read message history from JSONL logs or platform API."""
    # Discord has a live API — use it when chat_id is provided
    if platform == "discord" and args.get("chat_id"):
        return _read_discord_api(args)

    # All platforms: read from local JSONL
    log_file_name = PLATFORM_LOGS.get(platform)
    if not log_file_name:
        if platform == "email":
            return _err("For email, use action='inbox' instead of action='history'.")
        return _err(f"No message log for platform '{platform}'.")

    log_path = STATE_DIR / log_file_name
    if not log_path.exists():
        return _ok(f"No message history found for {platform}. ({log_path.name} does not exist)")

    limit = min(args.get("limit") or 20, 100)
    chat_id = args.get("chat_id")
    direction = args.get("direction", "all")
    search = (args.get("search") or "").lower()

    messages = _read_jsonl(log_path)

    # Filter
    if chat_id:
        messages = [m for m in messages if _match_chat_id(m, chat_id)]
    if direction != "all":
        messages = [m for m in messages if m.get("direction", m.get("dir", "")) == direction]
    if search:
        messages = [m for m in messages if search in (m.get("text") or m.get("content") or "").lower()]

    # Take last N (newest)
    messages = messages[-limit:]

    if not messages:
        filters = []
        if chat_id:
            filters.append(f"chat_id={chat_id}")
        if direction != "all":
            filters.append(f"direction={direction}")
        if search:
            filters.append(f"search='{search}'")
        filter_str = f" (filters: {', '.join(filters)})" if filters else ""
        return _ok(f"No messages found for {platform}{filter_str}.")

    lines = [f"**{platform.title()} history** ({len(messages)} messages):"]
    lines.append("")
    for m in messages:
        lines.append(_format_message(m, platform))

    return _ok("\n".join(lines))


def _read_discord_api(args: Dict[str, Any]) -> Dict[str, Any]:
    """Read Discord channel messages via REST API."""
    channel_id = args.get("chat_id")
    limit = min(args.get("limit") or 20, 100)

    try:
        _ensure_project_path("scripts")
        from discord_bridge import read_channel_sync

        messages = read_channel_sync(channel_id=int(channel_id), limit=limit)
        if not messages:
            return _ok(f"No messages in Discord channel {channel_id}.")

        lines = [f"**Discord channel {channel_id}** ({len(messages)} messages):"]
        lines.append("")
        for m in messages:
            author = m.get("author", {}).get("username", "?")
            content = m.get("content", "")[:200]
            ts = m.get("timestamp", "")[:19]
            lines.append(f"  [{ts}] {author}: {content}")

        return _ok("\n".join(lines))
    except ImportError:
        # Fallback to local JSONL
        return _read_history_from_jsonl("discord", args)
    except Exception as e:
        return _err(f"Discord read failed: {e}")


def _read_history_from_jsonl(platform: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback: read from local JSONL when API is unavailable."""
    args_copy = dict(args)
    args_copy.pop("chat_id", None)  # Don't filter by chat_id for JSONL fallback
    return _read_history(platform, args_copy)


# ── Mentions ────────────────────────────────────────────────────────────────

def _read_mentions(platform: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Read recent mentions of a citizen."""
    handle = _resolve_handle(args)
    limit = min(args.get("limit") or 20, 100)

    if platform == "twitter":
        return _read_twitter_mentions(args, limit)

    # For other platforms, search JSONL logs for @handle mentions
    log_file_name = PLATFORM_LOGS.get(platform)
    if not log_file_name:
        return _err(f"No message log for platform '{platform}'.")

    log_path = STATE_DIR / log_file_name
    if not log_path.exists():
        return _ok(f"No message history for {platform}.")

    messages = _read_jsonl(log_path)

    # Filter for mentions of this handle
    if handle:
        mention_pattern = f"@{handle}"
        messages = [
            m for m in messages
            if mention_pattern.lower() in (m.get("text") or m.get("content") or "").lower()
        ]

    # Only inbound mentions
    messages = [m for m in messages if m.get("direction", m.get("dir", "")) in ("in", "")]
    messages = messages[-limit:]

    if not messages:
        return _ok(f"No mentions found for @{handle or '?'} on {platform}.")

    lines = [f"**Mentions on {platform.title()}** ({len(messages)}):"]
    lines.append("")
    for m in messages:
        lines.append(_format_message(m, platform))

    return _ok("\n".join(lines))


def _read_twitter_mentions(args: Dict[str, Any], limit: int) -> Dict[str, Any]:
    """Read Twitter mentions from local log or API."""
    log_path = STATE_DIR / "twitter_mentions.jsonl"
    if not log_path.exists():
        return _ok("No Twitter mentions log found.")

    messages = _read_jsonl(log_path)
    messages = messages[-limit:]

    if not messages:
        return _ok("No Twitter mentions found.")

    lines = [f"**Twitter mentions** ({len(messages)}):"]
    lines.append("")
    for m in messages:
        author = m.get("author", m.get("from", "?"))
        text = (m.get("text") or "")[:200]
        ts = m.get("ts", m.get("timestamp", ""))[:19]
        tweet_id = m.get("tweet_id", "")
        lines.append(f"  [{ts}] @{author}: {text}")
        if tweet_id:
            lines.append(f"    (tweet_id: {tweet_id})")

    return _ok("\n".join(lines))


# ── Email Inbox ─────────────────────────────────────────────────────────────

def _read_email_inbox(args: Dict[str, Any]) -> Dict[str, Any]:
    """Read a citizen's email inbox."""
    handle = _resolve_handle(args)
    if not handle:
        return _err("'handle' is required to read email inbox.")

    limit = min(args.get("limit") or 20, 100)
    direction = args.get("direction", "all")

    try:
        _ensure_project_path("scripts")
        from citizen_email_service import list_inbox, list_sent

        messages = []
        if direction in ("all", "in"):
            inbox = list_inbox(handle, limit=limit)
            for m in inbox:
                m["_dir"] = "in"
            messages.extend(inbox)

        if direction in ("all", "out"):
            sent = list_sent(handle, limit=limit)
            for m in sent:
                m["_dir"] = "out"
            messages.extend(sent)

        # Sort by timestamp, newest last
        messages.sort(key=lambda m: m.get("timestamp", m.get("ts", "")))
        messages = messages[-limit:]

        if not messages:
            return _ok(f"No emails for @{handle}.")

        lines = [f"**Email for @{handle}** ({len(messages)} messages):"]
        lines.append("")
        for m in messages:
            d = m.get("_dir", "?")
            arrow = "<-" if d == "in" else "->"
            frm = m.get("from", "?")
            to = m.get("to", "?")
            subj = m.get("subject", "(no subject)")
            ts = m.get("timestamp", m.get("ts", ""))[:19]
            read_status = " [unread]" if d == "in" and not m.get("read") else ""
            lines.append(f"  [{ts}] {arrow} {frm} → {to}{read_status}")
            lines.append(f"    Subject: {subj}")
            body = (m.get("body") or "")[:100]
            if body:
                lines.append(f"    {body}...")

        return _ok("\n".join(lines))
    except ImportError:
        return _err("Email service not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"Email read failed: {e}")


# ── Shared helpers ──────────────────────────────────────────────────────────

def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read all entries from a JSONL file."""
    messages = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError as e:
        logger.warning(f"Failed to read {path}: {e}")
    return messages


def _match_chat_id(msg: Dict[str, Any], chat_id: str) -> bool:
    """Check if a message matches the given chat_id."""
    chat_id_str = str(chat_id)
    for key in ("chat_id", "channel", "phone", "chatId"):
        val = msg.get(key)
        if val and str(val) == chat_id_str:
            return True
    return False


def _format_message(msg: Dict[str, Any], platform: str) -> str:
    """Format a single message for display."""
    ts = msg.get("ts", msg.get("timestamp", ""))[:19]
    direction = msg.get("direction", msg.get("dir", "?"))
    arrow = "<-" if direction == "in" else "->" if direction == "out" else "  "
    sender = msg.get("from", msg.get("author", msg.get("sender", msg.get("push_name", ""))))
    text = (msg.get("text") or msg.get("content") or "")[:200]

    if sender:
        return f"  [{ts}] {arrow} {sender}: {text}"
    else:
        return f"  [{ts}] {arrow} {text}"


def _resolve_handle(args: Dict[str, Any]) -> Optional[str]:
    """Get citizen handle from args or auto-detect."""
    handle = (args.get("handle") or "").strip().lstrip("@")
    if handle:
        return handle

    handle = os.getenv("CITIZEN_HANDLE", "").strip().lstrip("@")
    if handle:
        return handle

    cwd = Path.cwd()
    for i, part in enumerate(cwd.parts):
        if part == "citizens" and i + 1 < len(cwd.parts):
            return cwd.parts[i + 1]

    actor_id = os.getenv("ACTOR_ID", "").strip()
    if actor_id:
        for prefix in ("AGENT_", "citizen_", "actor_"):
            if actor_id.lower().startswith(prefix.lower()):
                return actor_id[len(prefix):].lower()
        return actor_id.lower()

    return None


def _ensure_project_path(subdir: str):
    """Add project subdirectory to sys.path if not already present."""
    path = str(PROJECT_ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


# ── Response helpers ────────────────────────────────────────────────────────

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
