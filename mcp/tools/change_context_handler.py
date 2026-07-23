"""Deterministic impact and batch pre-edit context MCP tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from mcp.tools.context import ServerContext
from runtime.code_context import change_context, impact


IMPACT_SCHEMA = {
    "name": "impact",
    "description": (
        "[THINK] Deterministic change-impact lookup by exact node ID or file path. "
        "Returns incoming/outgoing dependencies, decisions, risks, graph tests, and affected files."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "node_id": {"type": "string", "description": "Exact graph node ID."},
            "file_path": {"type": "string", "description": "Exact code-file path."},
            "project_root": {"type": "string", "description": "Root used to normalize file_path."},
            "graph_names": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "anyOf": [{"required": ["node_id"]}, {"required": ["file_path"]}],
    },
}


CHANGE_CONTEXT_SCHEMA = {
    "name": "change_context",
    "description": (
        "[THINK] Preferred batch call immediately before code edits. For each exact file path or node ID, "
        "combines impact analysis with deterministic filesystem test discovery. No semantic similarity."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "file_paths": {"type": "array", "items": {"type": "string"}},
            "node_ids": {"type": "array", "items": {"type": "string"}},
            "project_root": {"type": "string", "description": "Current repository root."},
            "graph_names": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "anyOf": [{"required": ["file_paths"]}, {"required": ["node_ids"]}],
    },
}


def handle_impact(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    try:
        result = impact(
            file_path=args.get("file_path"),
            node_id=args.get("node_id"),
            project_root=Path(args.get("project_root") or ctx.target_dir),
            graph_names=args.get("graph_names"),
            limit=args.get("limit", 50),
        )
        return _response(result)
    except Exception as exc:
        return _response({"error": str(exc)}, is_error=True)


def handle_change_context(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    try:
        result = change_context(
            file_paths=args.get("file_paths"),
            node_ids=args.get("node_ids"),
            project_root=Path(args.get("project_root") or ctx.target_dir),
            graph_names=args.get("graph_names"),
            limit=args.get("limit", 50),
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
