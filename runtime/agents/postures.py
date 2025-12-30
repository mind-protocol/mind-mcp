"""
Agent Posture Configuration

Maps problem types to agent postures for optimal task assignment.

The 10 postures (cognitive stances, not roles):
- witness: evidence-first, traces what actually happened
- groundwork: foundation-first, builds scaffolding
- keeper: verification-first, checks before declaring done
- weaver: connection-first, patterns across modules
- voice: naming-first, finds right words for concepts
- scout: exploration-first, navigates and surveys
- architect: structure-first, shapes systems
- fixer: work-first, resolves without breaking
- herald: communication-first, broadcasts changes
- steward: coordination-first, prioritizes and assigns

DOCS: docs/agents/PATTERNS_Agent_System.md
"""

from typing import Dict

# =============================================================================
# PROBLEM → POSTURE MAPPING
# =============================================================================

PROBLEM_TO_POSTURE: Dict[str, str] = {
    # witness: evidence-first (traces, investigations)
    "STALE_SYNC": "witness",
    "STALE_IMPL": "witness",
    "DOC_DELTA": "witness",
    "NEW_UNDOC_CODE": "witness",

    # groundwork: foundation-first (scaffolding, structure)
    "UNDOCUMENTED": "groundwork",
    "INCOMPLETE_CHAIN": "groundwork",
    "MISSING_TESTS": "groundwork",

    # keeper: verification-first (validation, checks)
    "INVARIANT_COVERAGE": "keeper",
    "TEST_VALIDATES": "keeper",
    "COMPLETION_GATE": "keeper",
    "VALIDATION_BEHAVIORS_LIST": "keeper",

    # weaver: connection-first (patterns, links)
    "BROKEN_IMPL_LINK": "weaver",
    "BROKEN_IMPL_LINKS": "weaver",
    "DOC_LINK_INTEGRITY": "weaver",
    "ORPHAN_DOCS": "weaver",

    # voice: naming-first (naming, terminology)
    "NAMING_CONVENTION": "voice",
    "NONSTANDARD_DOC_TYPE": "voice",

    # scout: exploration-first (discovery, navigation)
    "MONOLITH": "scout",
    "LARGE_DOC_MODULE": "scout",

    # architect: structure-first (design, patterns)
    "DOC_TEMPLATE_DRIFT": "architect",
    "YAML_DRIFT": "architect",
    "PLACEHOLDER_DOCS": "architect",
    "PLACEHOLDER": "architect",

    # fixer: work-first (fixes, patches)
    "STUB_IMPL": "fixer",
    "INCOMPLETE_IMPL": "fixer",
    "NO_DOCS_REF": "fixer",
    "UNDOC_IMPL": "fixer",
    "MAGIC_VALUES": "fixer",
    "HARDCODED_SECRET": "fixer",
    "HARDCODED_SECRETS": "fixer",
    "LONG_STRINGS": "fixer",

    # herald: communication-first (docs, announcements)
    "DOC_GAPS": "herald",
    "DOC_DUPLICATION": "herald",
    "PROMPT_DOC_REFERENCE": "herald",
    "PROMPT_VIEW_TABLE": "herald",
    "PROMPT_CHECKLIST": "herald",

    # steward: coordination-first (conflicts, priorities)
    "ESCALATION": "steward",
    "SUGGESTION": "steward",
    "CONFLICTS": "steward",
    "PROPOSITION": "steward",
}

# Posture → Agent ID
POSTURE_TO_AGENT_ID: Dict[str, str] = {
    "witness": "agent_witness",
    "groundwork": "agent_groundwork",
    "keeper": "agent_keeper",
    "weaver": "agent_weaver",
    "voice": "agent_voice",
    "scout": "agent_scout",
    "architect": "agent_architect",
    "fixer": "agent_fixer",
    "herald": "agent_herald",
    "steward": "agent_steward",
}

# Default when problem type not mapped
DEFAULT_POSTURE = "fixer"


def select_agent_for_problem(problem_type: str) -> tuple:
    """
    Select best agent for a problem type.

    Returns:
        Tuple of (agent_id, posture)
    """
    posture = PROBLEM_TO_POSTURE.get(problem_type, DEFAULT_POSTURE)
    agent_id = POSTURE_TO_AGENT_ID.get(posture, f"agent_{DEFAULT_POSTURE}")
    return agent_id, posture


def get_posture_description(posture: str) -> str:
    """Get description for a posture."""
    descriptions = {
        "witness": "evidence-first, traces what actually happened",
        "groundwork": "foundation-first, builds scaffolding",
        "keeper": "verification-first, checks before declaring done",
        "weaver": "connection-first, patterns across modules",
        "voice": "naming-first, finds right words for concepts",
        "scout": "exploration-first, navigates and surveys",
        "architect": "structure-first, shapes systems",
        "fixer": "work-first, resolves without breaking",
        "herald": "communication-first, broadcasts changes",
        "steward": "coordination-first, prioritizes and assigns",
    }
    return descriptions.get(posture, "general agent")
