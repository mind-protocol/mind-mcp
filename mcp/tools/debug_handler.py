"""
[ACT] Debug — Start/stop trace sessions for entities.

When active, every @traceable function logs entry/exit as Moment nodes
in a debug Space. The trace is queryable via graph_query.

Usage via MCP:
    debug(action="start", entity="forge")
    debug(action="stop", entity="forge")
    debug(action="list")

After stopping, the debug Space persists. Query it:
    graph_query(queries=["debug_session_forge"])
"""

import logging
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.debug")


TOOL_SCHEMA = {
    "name": "debug",
    "description": (
        "[ACT] Start or stop a debug trace session for a citizen or entity. "
        "When active, all @traceable functions log entry/exit as Moment nodes "
        "in a debug Space in the graph. Use action='start' to begin, "
        "'stop' to end, 'list' to see active sessions."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["start", "stop", "list"],
                "description": "start/stop a debug session, or list active ones.",
            },
            "entity": {
                "type": "string",
                "description": "Entity to debug (citizen handle, org id, etc.).",
            },
        },
        "required": ["action"],
    },
}


def handle_debug(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Handle debug trace sessions."""
    action = args.get("action", "list")

    from runtime.debug.tracer import start_session, stop_session, list_sessions

    if action == "start":
        entity = args.get("entity", "")
        if not entity:
            return _err("'entity' is required for action='start'.")

        session = start_session(entity)
        return _ok(
            f"Debug session started for @{entity}.\n"
            f"  Space: {session.space_id}\n"
            f"  Graph: {session.graph_name}\n\n"
            f"All @traceable functions will now log to this Space.\n"
            f"Stop with: debug(action='stop', entity='{entity}')\n"
            f"Query traces: graph_query(queries=['debug_session_{entity}'])"
        )

    elif action == "stop":
        entity = args.get("entity", "")
        if not entity:
            return _err("'entity' is required for action='stop'.")

        session = stop_session(entity)
        if session:
            return _ok(
                f"Debug session stopped for @{entity}.\n"
                f"  Space: {session.space_id}\n"
                f"  Steps logged: {session.step_count}\n\n"
                f"Traces persist in the graph. Query with:\n"
                f"  graph_query(queries=['{session.space_id}'])"
            )
        else:
            return _err(f"No active debug session for '{entity}'.")

    elif action == "list":
        sessions = list_sessions()
        if not sessions:
            return _ok("No active debug sessions.")
        lines = ["Active debug sessions:"]
        for s in sessions:
            lines.append(
                f"  @{s['entity']}: {s['space_id']} "
                f"({s['steps']} steps, graph={s['graph']})"
            )
        return _ok("\n".join(lines))

    else:
        return _err(f"Unknown action '{action}'. Use: start, stop, list.")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
