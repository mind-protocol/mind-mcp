"""
Tick Result Types for v1.2 Energy Physics.

DOCS: docs/physics/IMPLEMENTATION_Physics.md
"""

# DEPRECATED: L3 universe tick eliminated per DECISION_One_Physics_Engine.md
# The L1 cognitive tick is the only physics engine. This code is retained
# for reference but is no longer called from the dispatcher or home_server.

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class TickResultV1_2:
    """Result of a v1.2 graph tick."""
    # Phase stats
    energy_generated: float = 0.0
    energy_drawn: float = 0.0
    energy_flowed: float = 0.0
    energy_interacted: float = 0.0
    energy_backflowed: float = 0.0
    energy_cooled: float = 0.0

    # Counts
    actors_updated: int = 0
    moments_active: int = 0
    moments_possible: int = 0
    moments_completed: int = 0
    moments_rejected: int = 0
    links_cooled: int = 0
    links_crystallized: int = 0

    # Completions
    completions: List[Dict[str, Any]] = field(default_factory=list)
    rejections: List[Dict[str, Any]] = field(default_factory=list)

    # Hot/cold stats
    hot_links: int = 0
    cold_links: int = 0

    # Task physics (L2)
    tasks_urgency_updated: int = 0
    tasks_urgency_delta: float = 0.0
    tasks_decayed: int = 0
    tasks_energy_decayed: float = 0.0
