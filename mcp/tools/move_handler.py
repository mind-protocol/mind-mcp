"""
[ACT] Move — Spatial movement between places in the living world.

Stub handler — not yet implemented. Returns a message indicating the tool
is under construction.
"""

import logging
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.move")

TOOL_SCHEMA = {
    "name": "move",
    "description": (
        "[ACT] Move — Navigate between places in the living world. "
        "Specify a destination place_id to move your citizen there."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "destination": {
                "type": "string",
                "description": "The place_id or place name to move to.",
            },
        },
        "required": ["destination"],
    },
}


async def handle_move(args: Dict[str, Any], ctx: ServerContext) -> str:
    destination = args.get("destination", "")
    logger.info(f"move requested to: {destination} (stub — not yet implemented)")
    return f"[move] Tool not yet implemented. Destination requested: {destination}"
