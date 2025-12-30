"""
Canonical Graph Injection

Single entry point for injecting nodes and links into the graph.

Features:
- Nature string → physics floats conversion (BEFORE synthesis)
- Synthesis generation from physics state
- Embedding generation from synthesis
- Automatic context linking (actor, space, moment)
- Moment chaining (each moment links to actor's previous moment)
- Active task detection from graph (no manual setting)

Injection Context:
- Every inject from a query creates a moment
- Each moment links to actor's previous moment (temporal chain)
- Every node links to: active actor, active space, current moment

Task Detection:
- Queries graph for tasks linked to actor with status='running'
- If multiple running tasks, picks highest weight × energy

Space Resolution:
1. Detect active task → follow implements chain → find space
2. Fallback: actor's linked spaces, pick by weight × energy (logs warning)

Usage:
    from runtime.inject import inject, set_actor

    # Set active actor (task is auto-detected from graph)
    set_actor("actor:agent_witness")

    # Inject - automatically creates moment and links
    inject(adapter, {
        "id": "narrative:finding_123",
        "content": "Found the bug in line 42",
    })

DOCS: docs/ingest/PATTERNS_Graph_Injection.md
"""

import logging
import time
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# INJECTION CONTEXT
# =============================================================================

DEFAULT_ACTOR = "actor:human"  # Human user (you talking to the system)

_context: Dict[str, Any] = {
    "actor_id": DEFAULT_ACTOR,
    "last_moment_id": {},  # actor_id -> last moment_id
}


def set_actor(actor_id: str = None) -> None:
    """
    Set active actor for injection context.

    Args:
        actor_id: Active actor (default: "actor:human")
    """
    _context["actor_id"] = actor_id or DEFAULT_ACTOR


def clear_context() -> None:
    """Reset to default context (human actor)."""
    _context["actor_id"] = DEFAULT_ACTOR
    _context["last_moment_id"] = {}


def get_actor() -> str:
    """Get current actor (never None)."""
    return _context["actor_id"] or DEFAULT_ACTOR


def get_context() -> Dict[str, Any]:
    """Get current injection context."""
    return dict(_context)


# =============================================================================
# SPACE RESOLUTION
# =============================================================================

def _detect_active_task(adapter, actor_id: str) -> Optional[str]:
    """
    Detect active task for actor from graph.

    Resolution order:
    1. Tasks linked to actor with status='running' (pick highest weight × energy)
    2. Tasks linked to actor with status='claimed' → check throttler → promote to 'running'

    Returns:
        Task ID or None if no active task
    """
    # 1. Look for running tasks
    try:
        result = adapter.query(
            """
            MATCH (a {id: $actor_id})-[r:LINK]-(t)
            WHERE t.status = 'running'
            RETURN t.id, COALESCE(r.weight, 1.0) * COALESCE(r.energy, 0.1) as score
            ORDER BY score DESC
            LIMIT 1
            """,
            {"actor_id": actor_id}
        )
        if result and result[0]:
            return result[0][0]
    except Exception as e:
        logger.debug(f"Running task detection failed for {actor_id}: {e}")

    # 2. No running tasks - look for claimed, check throttler, promote to running
    try:
        result = adapter.query(
            """
            MATCH (a {id: $actor_id})-[r:LINK]-(t)
            WHERE t.status = 'claimed'
            RETURN t.id, COALESCE(r.weight, 1.0) * COALESCE(r.energy, 0.1) as score
            ORDER BY score DESC
            LIMIT 1
            """,
            {"actor_id": actor_id}
        )
        if result and result[0]:
            task_id = result[0][0]

            # Check throttler before promoting
            if not _throttler_allows_running(task_id, actor_id):
                logger.warning(f"Throttler blocked promotion of {task_id} to running")
                return None

            # Promote claimed → running
            adapter.execute(
                "MATCH (t {id: $task_id}) SET t.status = 'running'",
                {"task_id": task_id}
            )
            logger.info(f"Promoted task {task_id} from claimed → running")
            return task_id
    except Exception as e:
        logger.debug(f"Claimed task detection failed for {actor_id}: {e}")

    return None


def _throttler_allows_running(task_id: str, actor_id: str) -> bool:
    """Check if throttler allows promoting task to running.

    Checks:
    1. Agent mode not paused/stopped
    2. Running count < max_concurrent_agents
    """
    try:
        from .capability_integration import (
            get_throttler, get_controller,
            AgentMode, CAPABILITY_RUNTIME_AVAILABLE
        )
        if not CAPABILITY_RUNTIME_AVAILABLE:
            return True  # No capability runtime = allow

        # 1. Check agent mode
        controller = get_controller()
        if controller and controller.mode in (AgentMode.PAUSED, AgentMode.STOPPED):
            logger.info(f"Agent mode is {controller.mode.value}, blocking promotion")
            return False

        # 2. Check throttler limits
        throttler = get_throttler()
        if not throttler:
            return True

        # Count currently running tasks
        running_count = sum(
            1 for slot in throttler.active.values()
            if getattr(slot, 'status', None) == 'running'
        )
        max_concurrent = getattr(throttler, 'max_concurrent_agents', 5)

        if running_count >= max_concurrent:
            logger.info(f"Max concurrent ({max_concurrent}) reached, blocking promotion")
            return False

        return True
    except Exception as e:
        logger.debug(f"Throttler check failed: {e}")
        return True  # Fail open


def _resolve_active_space(adapter) -> Optional[str]:
    """
    Resolve the active space for injection context.

    Resolution order:
    1. Detect active task → follow implements chain → find space
    2. Fallback: actor's linked spaces, pick by weight × energy

    Returns:
        Space ID or None if resolution fails
    """
    actor_id = get_actor()

    # 1. Detect active task, then follow implements chain to space
    task_id = _detect_active_task(adapter, actor_id)
    if task_id:
        try:
            # Follow implements links from task until we hit a space
            result = adapter.query(
                """
                MATCH (t {id: $task_id})-[:LINK*1..5]->(s:Space)
                WHERE s.id STARTS WITH 'space:'
                RETURN s.id LIMIT 1
                """,
                {"task_id": task_id}
            )
            if result and result[0]:
                return result[0][0]
        except Exception as e:
            logger.debug(f"Task → space resolution failed: {e}")

    # 2. Fallback: actor's linked spaces by weight × energy
    try:
        result = adapter.query(
            """
            MATCH (a {id: $actor_id})-[r:LINK]-(s:Space)
            RETURN s.id, COALESCE(r.weight, 1.0) * COALESCE(r.energy, 0.1) as score
            ORDER BY score DESC
            LIMIT 1
            """,
            {"actor_id": actor_id}
        )
        if result and result[0]:
            space_id = result[0][0]
            logger.warning(f"Space resolution fallback: {actor_id} → {space_id} (no task context)")
            return space_id
    except Exception as e:
        logger.debug(f"Actor → space fallback failed: {e}")

    return None


# =============================================================================
# MOMENT CREATION AND CHAINING
# =============================================================================

def _create_moment(adapter, node_id: str, synthesis: str) -> Optional[str]:
    """
    Create a moment for this injection and chain to previous.

    Moments form a temporal chain per actor:
    moment_n → moment_n-1 → moment_n-2 → ...

    Args:
        adapter: Database adapter
        node_id: The node being injected (for synthesis)
        synthesis: Description of what happened

    Returns:
        Moment ID or None if creation failed
    """
    actor_id = get_actor()
    moment_id = f"moment:{int(time.time() * 1000)}"

    # Get previous moment for this actor
    prev_moment_id = _context["last_moment_id"].get(actor_id)

    # Create moment node
    moment_data = {
        "id": moment_id,
        "label": "Moment",
        "name": f"inject:{node_id.split(':')[-1]}",
        "synthesis": synthesis,
        "actor_id": actor_id,
        "timestamp": int(time.time()),
        "weight": 1.0,
        "energy": 1.0,
    }

    result = _inject_node(adapter, moment_data, generate_embedding=True)
    if result == "failed":
        return None

    # Link moment to actor
    _inject_link_raw(adapter, actor_id, moment_id, "creates")

    # Chain to previous moment
    if prev_moment_id:
        _inject_link_raw(adapter, moment_id, prev_moment_id, "follows")

    # Update last moment for this actor
    _context["last_moment_id"][actor_id] = moment_id

    return moment_id


def _apply_context_links(adapter, node_id: str, moment_id: str = None) -> None:
    """
    Link injected node to context: actor, space, moment.

    Every node gets linked to:
    - Active actor (who)
    - Active space (where)
    - Current moment (when)
    """
    actor_id = get_actor()
    space_id = _resolve_active_space(adapter)

    # Link to actor
    _inject_link_raw(adapter, actor_id, node_id, "touches")

    # Link to space
    if space_id:
        _inject_link_raw(adapter, space_id, node_id, "contains")

    # Link to moment
    if moment_id:
        _inject_link_raw(adapter, moment_id, node_id, "captures")


def _inject_link_raw(adapter, from_id: str, to_id: str, verb: str) -> None:
    """Raw link injection without context (avoids recursion). Fails loud."""
    adapter.execute(
        """
        MATCH (a {id: $from_id})
        MATCH (b {id: $to_id})
        MERGE (a)-[r:LINK]->(b)
        SET r.verb = $verb
        """,
        {"from_id": from_id, "to_id": to_id, "verb": verb}
    )


# =============================================================================
# NODE TYPE TO LABEL MAPPING
# =============================================================================

LABEL_MAP = {
    "actor": "Actor",
    "space": "Space",
    "thing": "Thing",
    "narrative": "Narrative",
    "moment": "Moment",
}


# =============================================================================
# SYNTHESIS GENERATION
# =============================================================================
#
# Synthesis = natural language summary GENERATED from physics.
# Example: "Edmund, intensely present (central)"
#
# Uses the grammar from docs/schema/GRAMMAR_Link_Synthesis.md
# Implemented in runtime/physics/synthesis.py

def _generate_node_synthesis(node: Dict[str, Any]) -> str:
    """Generate synthesis for a node from its physics state."""
    from .physics.synthesis import synthesize_node
    return synthesize_node(node)


def _generate_link_synthesis(link: Dict[str, Any]) -> str:
    """Generate synthesis for a link from its physics state."""
    from .physics.synthesis import synthesize_link_full
    return synthesize_link_full(link)


# =============================================================================
# EMBEDDING SERVICE (lazy loaded)
# =============================================================================

_embedding_service = None


def _get_embedding_service():
    """Get embedding service (lazy load)."""
    global _embedding_service
    if _embedding_service is None:
        try:
            from .infrastructure.embeddings import get_embedding_service
            _embedding_service = get_embedding_service()
        except Exception as e:
            logger.warning(f"Could not load embedding service: {e}")
            return None
    return _embedding_service


def _generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text."""
    service = _get_embedding_service()
    if service and text:
        try:
            return service.embed(text)
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
    return None


# =============================================================================
# NATURE TO PHYSICS
# =============================================================================

def _nature_to_physics(nature: str) -> Dict[str, Any]:
    """
    Convert nature string to physics floats.

    Returns dict with: hierarchy, polarity, permanence, trust_disgust, etc.
    """
    try:
        from .physics.nature import nature_to_floats
        return nature_to_floats(nature)
    except Exception as e:
        logger.warning(f"Nature parsing failed for '{nature}': {e}")
        return {}


# =============================================================================
# CANONICAL INJECT FUNCTION
# =============================================================================

def inject(
    adapter,
    data: Dict[str, Any],
    generate_embedding: bool = True,
    with_context: bool = True,
) -> Literal["created", "updated", "unchanged"]:
    """
    Inject a node or link into the graph.

    Detects whether data represents a node or link:
    - Link: has "from" and "to" keys
    - Node: has "id" key

    Context behavior (with_context=True):
    - Creates a moment for this injection
    - Chains moment to actor's previous moment
    - Links node to: actor, space, moment

    Args:
        adapter: Database adapter with execute() and query() methods
        data: Node or link data dict
        generate_embedding: If True, generate embedding for synthesis (default: True)
        with_context: If True, create moment and apply context links (default: True)

    Returns:
        "created" | "updated" | "unchanged"
        Raises exception on failure (fail loud).

    Node format:
        {
            "id": "actor:agent_witness",      # Required
            "label": "Actor",                  # Optional, inferred from id prefix
            "name": "witness",                 # Optional
            "content": "...",                  # Optional
            "synthesis": "...",                # Required for embedding
            ...props
        }

    Link format:
        {
            "from": "space:root",              # Required
            "to": "space:actors",              # Required
            "nature": "contains, with force",  # Optional, parsed to physics floats
            "verb": "contains",                # Optional (extracted from nature)
            "synthesis": "...",                # Optional
            ...props
        }
    """
    # Detect link vs node
    if "from" in data and "to" in data:
        return _inject_link(adapter, data, generate_embedding)
    elif "id" in data:
        result = _inject_node(adapter, data, generate_embedding)

        # Apply context if injection succeeded
        if with_context and result in ("created", "updated"):
            node_id = data["id"]

            # Skip moment creation if injected node IS a moment (avoid duplication)
            is_moment = (
                data.get("label") == "Moment" or
                node_id.startswith("moment:")
            )

            if is_moment:
                # Moment nodes: link to actor and chain to previous moment
                actor_id = get_actor()
                _inject_link_raw(adapter, actor_id, node_id, "creates")

                # Chain to actor's previous moment
                prev_moment_id = _context["last_moment_id"].get(actor_id)
                if prev_moment_id:
                    _inject_link_raw(adapter, node_id, prev_moment_id, "follows")

                # Update last moment for this actor
                _context["last_moment_id"][actor_id] = node_id
            else:
                synthesis = data.get("synthesis", data.get("name", node_id))

                # Create moment and chain
                moment_id = _create_moment(adapter, node_id, f"Injected {synthesis}")

                # Link node to actor, space, moment
                _apply_context_links(adapter, node_id, moment_id)

        return result
    else:
        raise ValueError(f"inject: data must have 'id' (node) or 'from'/'to' (link), got: {list(data.keys())}")


# =============================================================================
# NODE INJECTION
# =============================================================================

def _inject_node(
    adapter,
    node: Dict[str, Any],
    generate_embedding: bool = True,
) -> Literal["created", "updated", "unchanged"]:
    """
    Inject a node into the graph.

    - Auto-generates synthesis if missing
    - Generates embedding from synthesis
    - Compares synthesis to detect changes
    - Clears embedding on change (triggers regeneration)
    """
    node = dict(node)  # Copy to avoid mutating original
    node_id = node["id"]

    # Determine label
    label = node.get("label")
    if not label:
        node_type = node.get("node_type")
        if node_type:
            label = LABEL_MAP.get(node_type, "Thing")
        else:
            # Infer from id prefix: "actor:foo" -> "Actor"
            prefix = node_id.split(":")[0] if ":" in node_id else "thing"
            label = LABEL_MAP.get(prefix, "Thing")

    # Generate synthesis if missing
    if not node.get("synthesis"):
        node["synthesis"] = _generate_node_synthesis(node)

    # Check if node exists and compare synthesis
    exists = False
    needs_embedding = generate_embedding
    try:
        result = adapter.query(
            f"MATCH (n:{label} {{id: $id}}) RETURN n.synthesis, n.embedding",
            {"id": node_id}
        )

        if result and len(result) > 0:
            exists = True
            existing_synthesis = result[0][0] if result[0] else None
            existing_embedding = result[0][1] if len(result[0]) > 1 else None

            # Unchanged if synthesis matches
            if existing_synthesis == node.get("synthesis"):
                return "unchanged"

            # Changed - will need new embedding
            needs_embedding = generate_embedding

    except Exception:
        pass  # Node doesn't exist

    # Generate embedding
    if needs_embedding and node.get("synthesis"):
        embedding = _generate_embedding(node["synthesis"])
        if embedding:
            node["embedding"] = embedding

    # Build properties (exclude label, node_type from props)
    exclude = {"label", "node_type"}
    props = {k: v for k, v in node.items() if k not in exclude and v is not None}

    # Escape newlines in string fields
    for key in ["synthesis", "content", "name"]:
        if key in props and isinstance(props[key], str):
            props[key] = props[key].replace("\n", " ")

    props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
    query = f"MERGE (n:{label} {{id: $id}}) SET n += {{{props_str}}} RETURN n.id"
    adapter.execute(query, props)
    return "updated" if exists else "created"


# =============================================================================
# LINK INJECTION
# =============================================================================

def _inject_link(
    adapter,
    link: Dict[str, Any],
    generate_embedding: bool = True,
) -> Literal["created", "updated", "unchanged"]:
    """
    Inject a link into the graph.

    - Parses nature string to physics floats
    - Auto-generates synthesis if missing
    - Generates embedding from synthesis
    """
    link = dict(link)  # Copy to avoid mutating original
    from_id = link["from"]
    to_id = link["to"]

    # Parse nature to physics floats
    nature = link.get("nature")
    if nature:
        physics = _nature_to_physics(nature)
        # Apply physics floats to link
        for key, value in physics.items():
            if key not in link and value is not None:
                link[key] = value

        # Extract verb from nature if not provided
        if not link.get("verb"):
            try:
                from .physics.nature import parse_nature
                _, verb, _ = parse_nature(nature)
                if verb:
                    link["verb"] = verb
            except Exception:
                pass

    # Default verb
    verb = link.get("verb", "linked")

    # Generate synthesis if missing
    if not link.get("synthesis"):
        link["synthesis"] = _generate_link_synthesis(link)

    # Generate embedding
    if generate_embedding and link.get("synthesis"):
        embedding = _generate_embedding(link["synthesis"])
        if embedding:
            link["embedding"] = embedding

    # Build properties (exclude structural fields)
    exclude = {"from", "to", "nature"}
    props = {k: v for k, v in link.items() if k not in exclude and v is not None}

    # Ensure verb is set
    props["verb"] = verb

    # Build SET clause for properties
    if props:
        set_parts = [f"r.{k} = ${k}" for k in props.keys()]
        set_clause = "SET " + ", ".join(set_parts)
    else:
        set_clause = ""

    query = f"""
    MATCH (a {{id: $from_id}})
    MATCH (b {{id: $to_id}})
    MERGE (a)-[r:LINK]->(b)
    {set_clause}
    RETURN type(r)
    """

    params = {"from_id": from_id, "to_id": to_id, **props}
    adapter.execute(query, params)
    return "created"  # MERGE doesn't distinguish create/update


# =============================================================================
# BATCH INJECTION
# =============================================================================

def inject_batch(
    adapter,
    items: List[Dict[str, Any]],
    generate_embedding: bool = True,
    with_context: bool = False,
) -> Dict[str, int]:
    """
    Inject multiple nodes/links.

    Args:
        adapter: Database adapter
        items: List of node/link dicts
        generate_embedding: If True, generate embeddings (default: True)
        with_context: If True, create moments (default: False for batch)

    Returns:
        Stats dict: {"created": N, "updated": N, "unchanged": N}
        Raises exception on any failure (fail loud).
    """
    stats = {"created": 0, "updated": 0, "unchanged": 0}

    for item in items:
        result = inject(adapter, item, generate_embedding=generate_embedding, with_context=with_context)
        stats[result] += 1

    return stats


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def inject_node(
    adapter,
    node_id: str,
    label: str = None,
    name: str = None,
    content: str = None,
    synthesis: str = None,
    generate_embedding: bool = True,
    with_context: bool = True,
    **props,
) -> Literal["created", "updated", "unchanged"]:
    """
    Convenience function to inject a node.

    Args:
        adapter: Database adapter
        node_id: Node ID (e.g., "actor:agent_witness")
        label: Optional label (inferred from id prefix if not provided)
        name: Optional name
        content: Optional content
        synthesis: Optional synthesis (auto-generated if missing)
        generate_embedding: Generate embedding (default: True)
        **props: Additional properties

    Returns:
        "created" | "updated" | "unchanged" | "failed"
    """
    data = {"id": node_id, **props}
    if label:
        data["label"] = label
    if name:
        data["name"] = name
    if content:
        data["content"] = content
    if synthesis:
        data["synthesis"] = synthesis

    return inject(adapter, data, generate_embedding=generate_embedding)


def inject_link(
    adapter,
    from_id: str,
    to_id: str,
    nature: str = None,
    verb: str = None,
    synthesis: str = None,
    generate_embedding: bool = True,
    **props,
) -> Literal["created", "updated", "unchanged", "failed"]:
    """
    Convenience function to inject a link.

    Args:
        adapter: Database adapter
        from_id: Source node ID
        to_id: Target node ID
        nature: Optional nature string (parsed to physics floats)
        verb: Optional verb (extracted from nature if not provided)
        synthesis: Optional synthesis (auto-generated if missing)
        generate_embedding: Generate embedding (default: True)
        **props: Additional properties

    Returns:
        "created" | "updated" | "unchanged" | "failed"
    """
    data = {"from": from_id, "to": to_id, **props}
    if nature:
        data["nature"] = nature
    if verb:
        data["verb"] = verb
    if synthesis:
        data["synthesis"] = synthesis

    return inject(adapter, data, generate_embedding=generate_embedding)
