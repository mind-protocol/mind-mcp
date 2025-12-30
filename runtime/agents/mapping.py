"""
Agent Mapping

Maps problem types to agent names for task assignment.
Agents are discovered dynamically from .mind/actors/ directory.

ID Pattern: TYPE_Name (e.g., AGENT_Witness, TASK_FixAuth)

DOCS: docs/agents/PATTERNS_Agent_System.md
"""

from pathlib import Path
from typing import Dict, List, Optional
import os

# =============================================================================
# PROBLEM → NAME MAPPING
# =============================================================================

TASK_TO_AGENT: Dict[str, str] = {
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

# Default when problem type not mapped
DEFAULT_NAME = "fixer"

# Static mapping: name -> actor_id
# Pattern: id = name = TYPE_Name
NAME_TO_ACTOR_ID: Dict[str, str] = {
    "witness": "AGENT_Witness",
    "groundwork": "AGENT_Groundwork",
    "keeper": "AGENT_Keeper",
    "weaver": "AGENT_Weaver",
    "voice": "AGENT_Voice",
    "scout": "AGENT_Scout",
    "architect": "AGENT_Architect",
    "fixer": "AGENT_Fixer",
    "herald": "AGENT_Herald",
    "steward": "AGENT_Steward",
}

def make_id(type_prefix: str, name: str) -> str:
    """Create ID in TYPE_Name format. TYPE is uppercase, Name is capitalized."""
    return f"{type_prefix.upper()}_{name.capitalize()}"


# =============================================================================
# DYNAMIC AGENT DISCOVERY
# =============================================================================


def discover_agents(target_dir: Optional[Path] = None) -> Dict[str, str]:
    """
    Discover agents by scanning .mind/actors/ directory.

    Args:
        target_dir: Project root (defaults to cwd)

    Returns:
        Dict mapping name -> actor_id (e.g., {"witness": "AGENT_Witness"})
    """
    if target_dir is None:
        target_dir = Path.cwd()

    actors_dir = target_dir / ".mind" / "actors"
    if not actors_dir.exists():
        return {}

    agents = {}
    for actor_dir in actors_dir.iterdir():
        if not actor_dir.is_dir():
            continue

        # Check if it has a prompt file (CLAUDE.md or AGENTS.md)
        has_prompt = (
            (actor_dir / "CLAUDE.md").exists() or
            (actor_dir / "AGENTS.md").exists()
        )
        if not has_prompt:
            continue

        name = actor_dir.name
        # ID pattern: TYPE_Name
        agent_id = f"AGENT_{name.capitalize()}"
        agents[name.lower()] = agent_id

    return agents


def get_agent_id(name: str, target_dir: Optional[Path] = None) -> str:
    """
    Get agent ID for a name, discovering from .mind/actors/.

    Args:
        name: Agent name (e.g., "witness")
        target_dir: Project root

    Returns:
        Agent ID (e.g., "AGENT_Witness")
    """
    agents = discover_agents(target_dir)
    if name in agents:
        return agents[name]
    # Fallback: generate ID from name
    return f"AGENT_{name.capitalize()}"


def list_agents(target_dir: Optional[Path] = None) -> List[str]:
    """
    List all available agent names.

    Args:
        target_dir: Project root

    Returns:
        List of agent names
    """
    return list(discover_agents(target_dir).keys())


def select_agent_for_task(task_type: str, target_dir: Optional[Path] = None) -> tuple:
    """
    Select best agent for a problem type.

    Args:
        task_type: Problem type string
        target_dir: Project root for agent discovery

    Returns:
        Tuple of (actor_id, name)
    """
    name = TASK_TO_AGENT.get(task_type, DEFAULT_NAME)
    actor_id = get_agent_id(name, target_dir)
    return actor_id, name


def get_name_description(name: str) -> str:
    """Get description for a name."""
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
    return descriptions.get(name, "general agent")
