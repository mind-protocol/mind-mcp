"""MCP broadcast tool for recurring announcements to the NLR Telegram channel."""

from __future__ import annotations

import os
from typing import Any, Dict

from mcp.tools.send_handler import handle_send


DEFAULT_BROADCAST_CHAT_ID = "-1001699255893"

TOOL_SCHEMA = {
    "name": "broadcast",
    "description": (
        "[SPEAK] Publish a professional, self-contained announcement in English to the configured "
        "NLR Telegram channel. Always provide enough context for a reader who has not followed the task. "
        "Use it several times per day when there is meaningful news: major changes, "
        "validation results, milestones, important blockers, or decisions. Do not use "
        "it for routine edit-by-edit status updates."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The concrete update, written in English.",
            },
            "title": {
                "type": "string",
                "description": "Short professional English headline.",
            },
            "context": {
                "type": "string",
                "description": "Why this work was needed and what problem it addresses, in English.",
            },
            "impact": {
                "type": "string",
                "description": "Why the update matters to agents, users, or the project, in English.",
            },
            "status": {
                "type": "string",
                "description": "Current validation or rollout status, in English.",
            },
            "next_step": {
                "type": "string",
                "description": "Optional next action or follow-up, in English.",
            },
            "category": {
                "type": "string",
                "enum": ["major_change", "validation", "milestone", "blocker", "decision", "general"],
                "default": "general",
            },
            "handle": {
                "type": "string",
                "description": "Optional citizen handle used as the announcement author.",
            },
        },
        "required": ["title", "context", "message", "impact", "status"],
    },
}


def handle_broadcast(args: Dict[str, Any]) -> Dict[str, Any]:
    required = ("title", "context", "message", "impact", "status")
    values = {key: str(args.get(key) or "").strip() for key in (*required, "next_step")}
    missing = [key for key in required if not values[key]]
    if missing:
        return {"content": [{
            "type": "text",
            "text": f"Error: broadcast requires non-empty English fields: {', '.join(missing)}.",
        }]}

    category = str(args.get("category") or "general").strip().replace("_", " ").upper()
    chat_id = os.environ.get("MIND_TELEGRAM_BROADCAST_CHAT_ID", DEFAULT_BROADCAST_CHAT_ID)
    sections = [
        f"📣 *{category}*",
        f"*{values['title']}*",
        f"*Context*\n{values['context']}",
        f"*What changed*\n{values['message']}",
        f"*Why it matters*\n{values['impact']}",
        f"*Status*\n{values['status']}",
    ]
    if values["next_step"]:
        sections.append(f"*Next step*\n{values['next_step']}")
    return handle_send({
        "platform": "telegram",
        "chat_id": chat_id,
        "message": "\n\n".join(sections),
        "handle": args.get("handle") or "mind",
    })
