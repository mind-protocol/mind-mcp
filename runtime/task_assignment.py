"""
Auto-assign tasks to agents using graph physics.

Score = similarity * weight * energy

Assignment triggers:
- On task creation (immediate)
- On MCP startup (catch-up for pending tasks)
"""

import logging
from typing import List, Optional, Tuple

logger = logging.getLogger("mind.task_assignment")


def compute_agent_score(
    task_embedding: List[float],
    agent_embedding: List[float],
    agent_weight: float,
    agent_energy: float,
) -> float:
    """Compute assignment score: similarity * weight * energy."""
    from runtime.infrastructure.embeddings import cosine_similarity

    similarity = cosine_similarity(task_embedding, agent_embedding)
    weight = max(agent_weight, 0.1)
    energy = max(agent_energy, 0.1)

    return similarity * weight * energy


def select_best_agent(task_id: str, task_synthesis: str, adapter) -> Optional[str]:
    """Select best agent for a task using graph physics.

    Args:
        task_id: Task narrative ID
        task_synthesis: Task description for embedding
        adapter: Database adapter

    Returns:
        Best agent ID or None if no agents available
    """
    from runtime.infrastructure.embeddings import get_embedding

    # Get task embedding
    task_embedding = get_embedding(task_synthesis)
    if not task_embedding:
        logger.warning(f"Could not embed task: {task_id}")
        return None

    # Get available agents (not paused)
    # Uses AGENT type (uppercase) for new-format agents with synthesis
    # No hard limit - load penalty handles distribution
    result = adapter.query("""
        MATCH (a:Actor)
        WHERE a.type = 'AGENT' AND COALESCE(a.status, 'idle') <> 'paused'
        OPTIONAL MATCH (a)<-[r:LINK {verb: 'claimed_by'}]-(t:Narrative {type: 'task_run'})
        WHERE t.status IN ['claimed', 'running']
        WITH a, count(t) as active_tasks
        RETURN a.id, a.synthesis, a.weight, a.energy, a.embedding, active_tasks
    """)

    if not result:
        logger.debug("No available agents")
        return None

    best_agent = None
    best_score = -1.0

    for row in result:
        agent_id, synthesis, weight, energy, embedding, active_tasks = row

        if not embedding:
            # Try to get embedding from synthesis
            if synthesis:
                embedding = get_embedding(synthesis)
            if not embedding:
                continue

        score = compute_agent_score(
            task_embedding,
            embedding,
            weight or 1.0,
            energy or 1.0,
        )

        # Decrease score by 20% per active task (load balancing)
        load_penalty = 1.0 - (0.2 * (active_tasks or 0))
        score *= max(load_penalty, 0.2)  # Floor at 20%

        if score > best_score:
            best_score = score
            best_agent = agent_id

    if best_agent:
        logger.debug(f"Selected {best_agent} for {task_id} (score: {best_score:.3f})")

    return best_agent


def assign_task(task_id: str, agent_id: str, adapter) -> bool:
    """Create claimed_by link between task and agent.

    Returns True if assignment succeeded.
    """
    import time
    timestamp = int(time.time())

    try:
        adapter.execute("""
            MATCH (t:Narrative {id: $task_id})
            MATCH (a:Actor {id: $agent_id})
            MERGE (t)-[l:LINK {verb: 'claimed_by'}]->(a)
            SET t.status = 'claimed',
                l.created_at = $timestamp
        """, {"task_id": task_id, "agent_id": agent_id, "timestamp": timestamp})

        logger.info(f"Assigned {task_id} -> {agent_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to assign {task_id}: {e}")
        return False


def assign_single_task(task_id: str, task_synthesis: str, adapter) -> Optional[str]:
    """Assign a single task to best available agent.

    Call this on task creation.

    Returns assigned agent ID or None.
    """
    agent_id = select_best_agent(task_id, task_synthesis, adapter)

    if agent_id:
        if assign_task(task_id, agent_id, adapter):
            return agent_id

    return None


def assign_pending_tasks(adapter, limit: int = 20) -> Tuple[int, int]:
    """Assign all pending tasks without agents.

    Call this on MCP startup.

    Args:
        adapter: Database adapter
        limit: Max tasks to assign in one batch

    Returns:
        (assigned_count, skipped_count)
    """
    # Find pending tasks without claimed_by link
    result = adapter.query("""
        MATCH (t:Narrative {type: 'task_run', status: 'pending'})
        OPTIONAL MATCH (t)-[r:LINK {verb: 'claimed_by'}]->(a:Actor)
        WITH t, a
        WHERE a IS NULL
        RETURN t.id, t.synthesis
        LIMIT $limit
    """, {"limit": limit})

    if not result:
        logger.debug("No pending tasks to assign")
        return (0, 0)

    assigned = 0
    skipped = 0

    for row in result:
        task_id, synthesis = row

        if not synthesis:
            skipped += 1
            continue

        agent = assign_single_task(task_id, synthesis, adapter)
        if agent:
            assigned += 1
        else:
            skipped += 1

    if assigned > 0:
        logger.info(f"Auto-assigned {assigned} tasks ({skipped} skipped)")

    return (assigned, skipped)


def startup_assign(target_dir=None) -> Tuple[int, int]:
    """Run assignment on startup. Called from MCP server init.

    Returns (assigned, skipped) counts.
    """
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        return assign_pending_tasks(adapter)
    except Exception as e:
        logger.warning(f"Startup assignment failed: {e}")
        return (0, 0)
