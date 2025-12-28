"""
Physics Health Checkers

Individual health check implementations.

DOCS: docs/physics/HEALTH_Energy_Physics.md
DOCS: docs/physics/HEALTH_Physics.md (v1.6.1 SubEntity)
"""

from .energy_conservation import EnergyConservationChecker
from .no_negative import NoNegativeEnergyChecker
from .link_state import LinkStateChecker
from .tick_integrity import TickIntegrityChecker
from .moment_lifecycle import MomentLifecycleChecker

# v1.6.1 SubEntity checkers
from .subentity import (
    SubEntityTreeChecker,
    FoundNarrativesChecker,
    CrystallizationEmbeddingChecker,
    CrystallizedConsistencyChecker,
    SiblingDivergenceChecker,
    LinkScoreChecker,
    CrystallizationNoveltyChecker,
    validate_subentity,
    is_subentity_healthy,
)

__all__ = [
    # v1.2 Physics checkers
    "EnergyConservationChecker",
    "NoNegativeEnergyChecker",
    "LinkStateChecker",
    "TickIntegrityChecker",
    "MomentLifecycleChecker",
    # v1.6.1 SubEntity checkers
    "SubEntityTreeChecker",
    "FoundNarrativesChecker",
    "CrystallizationEmbeddingChecker",
    "CrystallizedConsistencyChecker",
    "SiblingDivergenceChecker",
    "LinkScoreChecker",
    "CrystallizationNoveltyChecker",
    "validate_subentity",
    "is_subentity_healthy",
]
