"""
MCP Tool Registry — central lookup for all tool handlers.

DOCS: docs/tools/mcp/IMPLEMENTATION_MCP_Tools.md
"""

from typing import Callable, Dict, Any, Optional

# Central registry: tool_name → handler function
MCP_TOOL_REGISTRY: Dict[str, Callable] = {}


def register_tool(
    name: str,
    handler: Callable,
    *,
    needs_ctx: bool = False,
    description: str = "",
) -> None:
    """Register an MCP tool handler in the central registry.

    Decouples tool lookup from tool implementation so that
    parse_action_command() can resolve tool names without importing
    every handler module.

    Args:
        name: Tool name (e.g. "graph_query", "send", "subcall")
        handler: The handler function (e.g. handle_graph_query)
        needs_ctx: Whether handler requires ServerContext injection
        description: One-line description for tool listing
    """
    MCP_TOOL_REGISTRY[name] = {
        "handler": handler,
        "needs_ctx": needs_ctx,
        "description": description,
    }


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """Look up a registered tool by name. Returns None if not found."""
    return MCP_TOOL_REGISTRY.get(name)


def list_tools() -> list[str]:
    """Return sorted list of registered tool names."""
    return sorted(MCP_TOOL_REGISTRY.keys())
