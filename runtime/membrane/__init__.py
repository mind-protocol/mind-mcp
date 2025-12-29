"""
Membrane module.

Cross-org communication layer via shared membrane graph.

Rules (from L4):
- P7: Membrane only — single gate, all rules applied here
- P8: Graph MCP calls — no Cypher, graph physics does the work
"""

from .config import MEMBRANE_HOST, MEMBRANE_PORT, MEMBRANE_GRAPH
from .client import MembraneQueries, get_membrane_queries
from .broadcast import MembraneBroadcast, get_broadcast, on_node_public, on_node_private
from .stimulus import StimulusHandler, get_stimulus_handler

__all__ = [
    # Config
    "MEMBRANE_HOST",
    "MEMBRANE_PORT",
    "MEMBRANE_GRAPH",
    # Client (query membrane)
    "MembraneQueries",
    "get_membrane_queries",
    # Broadcast (sync public nodes)
    "MembraneBroadcast",
    "get_broadcast",
    "on_node_public",
    "on_node_private",
    # Stimulus (receive cross-org queries)
    "StimulusHandler",
    "get_stimulus_handler",
]
