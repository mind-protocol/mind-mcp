"""
Shared context object passed to all MCP tool handlers.

Holds references to graph, procedure, and capability subsystems
so handlers don't depend on the server class directly.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ServerContext:
    """Dependencies shared across all tool handlers."""
    graph_ops: Any = None
    graph_queries: Any = None
    runner: Any = None  # ConnectomeRunner
    target_dir: Path = field(default_factory=Path.cwd)
    capability_manager: Any = None
    connectomes_dir: Optional[Path] = None
