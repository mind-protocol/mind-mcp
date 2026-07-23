"""MCP handler for canonical JSON versus FalkorDB runtime drift."""

from __future__ import annotations

import json
from typing import Any, Dict

from mcp.tools.context import ServerContext
from runtime.graph_diff import graph_diff


TOOL_SCHEMA = {
    "name": "graph_diff",
    "description": (
        "[THINK] Compare active FalkorDB graphs with their canonical JSON datasets. "
        "Reports runtime-only mutations that may disappear on seed, missing runtime data, and property drift. Read-only."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "manifest_path": {
                "type": "string",
                "description": "Path to graphs.json. Defaults to MIND_GRAPH_MANIFEST.",
            },
            "graph_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional manifest graph IDs to compare, for example ['design'].",
            },
            "include_property_changes": {"type": "boolean", "default": True},
            "include_unmaterialized_properties": {
                "type": "boolean",
                "default": False,
                "description": "Also report canonical fields the seed projection intentionally does not materialize.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1000,
                "description": "Maximum detailed entries per drift category; counts always remain complete.",
            },
        },
    },
}


def handle_graph_diff(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    try:
        result = graph_diff(
            args.get("manifest_path"),
            graph_ids=args.get("graph_ids"),
            include_property_changes=args.get("include_property_changes", True),
            include_unmaterialized_properties=args.get("include_unmaterialized_properties", False),
            limit=args.get("limit", 100),
        )
        return _response(result)
    except Exception as exc:
        return _response({"error": str(exc)}, is_error=True)


def _response(payload: dict[str, Any], *, is_error: bool = False) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]
    }
    if is_error:
        response["isError"] = True
    return response
