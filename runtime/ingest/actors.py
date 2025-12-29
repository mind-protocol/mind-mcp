"""
Actor ingestion for the mind graph.

Creates Actor nodes from .mind/actors/ACTOR_*.md files.
Each actor represents a work agent with a specific posture.

DOCS: .mind/docs/ACTOR_TEMPLATE.md
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def ingest_actors(
    target_dir: Path,
    graph_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ingest actors from .mind/actors/ into the graph.

    Reads ACTOR_*.md files and creates Actor nodes with:
    - id: actor:agent_{name}
    - synthesis: for embedding
    - content: purpose description

    Args:
        target_dir: Repository root (where .mind/ lives)
        graph_name: Graph to ingest into (default: from config)

    Returns:
        Stats dict: {actors, created, updated, unchanged}
    """
    from ..infrastructure.database import get_database_adapter
    from ..inject import inject

    actors_dir = target_dir / ".mind" / "actors"
    if not actors_dir.exists():
        return {"actors": 0, "created": 0, "updated": 0, "unchanged": 0}

    # Get database adapter
    adapter = get_database_adapter(graph_name=graph_name)

    stats = {
        "actors": 0,
        "created": 0,
        "updated": 0,
        "unchanged": 0,
    }

    # Create actors space (no context - init-time bulk operation)
    result = inject(adapter, {
        "id": "space:actors",
        "label": "Space",
        "name": "actors",
        "type": "system",
        "synthesis": "space:actors — Work agents that execute tasks with specific cognitive postures",
        "content": "Work agents that execute tasks with specific cognitive postures",
        "weight": 8.0,
        "energy": 0.0,
    }, with_context=False)
    logger.debug(f"space:actors: {result}")

    # Link actors space to root
    inject(adapter, {
        "from": "space:root",
        "to": "space:actors",
        "nature": "contains",
    }, with_context=False)

    # Process each ACTOR_*.md file
    actor_files = list(actors_dir.glob("ACTOR_*.md"))
    stats["actors"] = len(actor_files)

    for actor_file in sorted(actor_files):
        result = _ingest_actor(adapter, actor_file)
        stats[result] += 1

    return stats


def _ingest_actor(adapter, actor_file: Path) -> str:
    """
    Ingest a single actor file.

    Returns: "created", "updated", or "unchanged"
    """
    from ..inject import inject

    # Extract name from filename: ACTOR_Witness.md -> witness
    match = re.match(r"ACTOR_(\w+)\.md", actor_file.name)
    if not match:
        return "unchanged"

    name = match.group(1)
    actor_id = f"actor:agent_{name.lower()}"

    # Parse the file
    content = actor_file.read_text(encoding='utf-8', errors='ignore')

    # Extract purpose from ## Purpose section
    purpose_match = re.search(
        r"## Purpose\s*\n\s*\n(.+?)(?=\n\n|\n---|\n##|$)",
        content,
        re.DOTALL
    )
    purpose = purpose_match.group(1).strip() if purpose_match else f"{name} agent"

    # Extract move pattern
    move_match = re.search(r"\*\*Move:\*\*\s*(.+)", content)
    move = move_match.group(1).strip() if move_match else ""

    # Build synthesis for embedding
    synthesis = f"agent:{name.lower()} — {purpose[:150]}"
    if move:
        synthesis += f" ({move})"

    # Inject the actor node (no context - init-time)
    result = inject(adapter, {
        "id": actor_id,
        "label": "Actor",
        "name": name.lower(),
        "type": "agent",
        "synthesis": synthesis,
        "content": purpose,
        "status": "ready",
        "weight": 1.0,
        "energy": 0.0,
    }, with_context=False)

    # Link actor to actors space
    inject(adapter, {
        "from": "space:actors",
        "to": actor_id,
        "nature": "contains",
    }, with_context=False)

    return result
