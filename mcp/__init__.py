"""
mind-mcp MCP server

Exposes the mind graph system as MCP tools for AI agents.
"""

from .server import MindServer

__version__ = "0.2.1"
__all__ = ["MindServer", "__version__"]
