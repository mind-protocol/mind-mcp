"""MCP tool that enriches an agent immediately before a code-file edit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from mcp.tools.context import ServerContext
from runtime.code_context import env_enabled, enrich_code_path


TOOL_SCHEMA = {
    "name": "code_context",
    "description": (
        "[THINK] Optional pre-edit graph augmentation. When code-context enrichment is enabled, "
        "call this immediately before modifying a code file. It searches the selected FalkorDB "
        "graphs for Thing nodes with the exact same path, traverses their local neighborhood, "
        "and returns that design context. Read-only and fail-open."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Code-file path, absolute or relative to project_root."},
            "enabled": {
                "type": "boolean",
                "description": "Per-call opt-in/out. Defaults to MIND_CODE_CONTEXT_ENABLED.",
            },
            "project_root": {
                "type": "string",
                "description": "Project root used to derive relative path variants. Defaults to the MCP target directory.",
            },
            "graph_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional FalkorDB graph allow-list. Defaults to MIND_CODE_CONTEXT_GRAPHS or all graphs.",
            },
            "depth": {
                "type": "integer",
                "minimum": 0,
                "maximum": 3,
                "description": "Undirected local traversal depth (default 1).",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum roots and traversal paths per graph (default 50).",
            },
        },
        "required": ["path"],
    },
}


def handle_code_context(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    file_path = args.get("path")
    if not isinstance(file_path, str) or not file_path.strip():
        return _response({"enabled": False, "error": "'path' is required."}, is_error=True)

    enabled = args.get("enabled")
    if enabled is None:
        enabled = env_enabled()
    if not enabled:
        return _response({
            "enabled": False,
            "file": file_path,
            "message": "Code-context enrichment is disabled. Set MIND_CODE_CONTEXT_ENABLED=true or pass enabled=true.",
        })

    project_root = Path(args.get("project_root") or ctx.target_dir)
    try:
        result = enrich_code_path(
            file_path,
            project_root=project_root,
            graph_names=args.get("graph_names"),
            depth=args.get("depth", 1),
            limit=args.get("limit", 50),
        )
    except Exception as exc:  # optional context must never block the edit
        result = {
            "enabled": True,
            "file": file_path,
            "matches": 0,
            "error": str(exc),
            "message": "FalkorDB context unavailable; continue without augmentation.",
        }
    return _response(result)


def _response(payload: dict[str, Any], *, is_error: bool = False) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
    }
    if is_error:
        response["isError"] = True
    return response
