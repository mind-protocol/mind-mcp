"""
Citizen identity resolution.

Detects and normalizes citizen IDs from environment, cwd, or config.
Used by MCP tool handlers that need to know which citizen is acting.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_citizen_id(handle: str) -> str:
    """Normalize a citizen handle to canonical CITIZEN_{handle} format.

    Strips leading @ if present. Lowercases the handle.

    Args:
        handle: e.g. "dragon_slayer", "@dragon_slayer", "CITIZEN_dragon_slayer"

    Returns:
        "CITIZEN_dragon_slayer"
    """
    handle = handle.strip().lstrip("@")
    if handle.upper().startswith("CITIZEN_"):
        handle = handle[8:]
    return f"CITIZEN_{handle.lower()}"


def extract_citizen_handle(citizen_id: str) -> str:
    """Extract the handle from a CITIZEN_ prefixed ID.

    Args:
        citizen_id: "CITIZEN_dragon_slayer"

    Returns:
        "dragon_slayer"
    """
    if citizen_id.startswith("CITIZEN_"):
        return citizen_id[8:]
    return citizen_id.lower()


def detect_citizen_id(target_dir: Optional[Path] = None) -> Optional[str]:
    """Detect current citizen from env var, cwd path, or target_dir config.

    Priority:
    1. MIND_CITIZEN_ID env var (explicit override)
    2. cwd within a citizens/ directory
    3. .mind/citizen_id file in target_dir (written by session setup)

    Returns CITIZEN_{handle} if detected, None otherwise.
    """
    # 1. Explicit env var
    citizen = os.environ.get("MIND_CITIZEN_ID")
    if citizen:
        return normalize_citizen_id(citizen)

    # 2. cwd within a citizens/ directory
    cwd = Path.cwd()
    parts = cwd.parts
    if "citizens" in parts:
        idx = parts.index("citizens")
        if idx + 1 < len(parts):
            return normalize_citizen_id(parts[idx + 1])

    # 3. .mind/citizen_id file (project-level config)
    if target_dir:
        cid_file = Path(target_dir) / ".mind" / "citizen_id"
        if cid_file.exists():
            try:
                handle = cid_file.read_text().strip()
                if handle:
                    return normalize_citizen_id(handle)
            except OSError:
                pass

    return None


def resolve_actor_id(
    actor_input: Optional[str] = None,
    target_dir: Optional[Path] = None,
    graph_ops=None,
) -> str:
    """Resolve an actor input string to a canonical actor ID.

    Handles citizen IDs (CITIZEN_*) and raw handles.
    Falls back to citizen detection from env/cwd, then graph HUMAN lookup.

    Args:
        actor_input: Optional explicit actor ID or handle
        target_dir: Project root for citizen detection
        graph_ops: Optional graph ops for HUMAN lookup

    Returns:
        Canonical actor ID (e.g. "CITIZEN_solen", "HUMAN_Nicolas")
    """
    if not actor_input:
        # 1. Check for citizen context
        citizen_id = detect_citizen_id(target_dir)
        if citizen_id:
            return citizen_id

        # 2. Find best HUMAN actor from graph
        if graph_ops:
            try:
                result = graph_ops._query(
                    """
                    MATCH (a)
                    WHERE a.node_type = 'actor' AND a.type = 'HUMAN'
                    RETURN a.id, COALESCE(a.weight, 1.0) * COALESCE(a.energy, 0.5) as score
                    ORDER BY score DESC
                    LIMIT 1
                    """
                )
                if result and result[0]:
                    return result[0][0]
            except Exception as e:
                logger.warning(f"Error resolving owner from graph: {e}")

        return "unknown"

    actor_input = actor_input.strip()

    # Already canonical
    if actor_input.startswith("CITIZEN_"):
        return actor_input
    if actor_input.startswith("HUMAN_"):
        return actor_input

    # Looks like a citizen handle
    return normalize_citizen_id(actor_input)
