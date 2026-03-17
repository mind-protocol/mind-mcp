"""
Phase 9a: Task Urgency — Active tasks accumulate energy from dependency topology.

Energy comes from three sources:
  - Intrinsic urgency (base energy + deadline proximity)
  - Objective pressure (CONTRIBUTES_TO links)
  - Blocking pressure (back-pressure from downstream BLOCKS)

DOCS: docs/organization/task_physics/ALGORITHM_Task_Physics.md
"""

import logging
import time
from typing import Tuple
from runtime.physics.graph import GraphQueries, GraphOps
from runtime.organization.task_constants import (
    BLOCKING_PRESSURE_RATE,
    DEADLINE_PRESSURE_FACTOR,
    ENERGY_CONVERGENCE_RATE,
    ENERGY_MAX,
    ENERGY_MIN,
    OBJECTIVE_PRESSURE_RATE,
)

logger = logging.getLogger(__name__)


def phase_task_urgency(read: GraphQueries, write: GraphOps) -> Tuple[float, int]:
    """
    Run Phase 9a: Task Urgency Accumulation.

    For each active task, recompute energy from dependency topology.

    Returns:
        (total_energy_delta, tasks_updated)
    """
    total_delta = 0.0
    tasks_updated = 0

    try:
        # Fetch all active tasks with their dependency data in one query
        rows = read.query("""
        MATCH (t:Narrative)
        WHERE t.type = 'task' AND COALESCE(t.status, 'pending') <> 'done'
        OPTIONAL MATCH (t)-[c:LINK {verb: 'contributes_to'}]->(obj)
        OPTIONAL MATCH (t)-[b:LINK {verb: 'blocks'}]->(blocked)
        WITH t,
             collect(DISTINCT [obj.energy, c.weight]) AS objectives,
             collect(DISTINCT [blocked.energy, b.weight]) AS blocks
        RETURN t.id AS id, t.energy AS energy, t.deadline AS deadline,
               objectives, blocks
        """)

        if not rows:
            return 0.0, 0

        now = time.time()

        for row in rows:
            task_id = row.get('id')
            if not task_id:
                continue

            current_energy = float(row.get('energy') or 0.5)
            deadline = row.get('deadline')
            objectives_raw = row.get('objectives') or []
            blocks_raw = row.get('blocks') or []

            # Step 1: Intrinsic urgency
            intrinsic = current_energy
            if deadline:
                try:
                    hours_remaining = max((float(deadline) - now) / 3600.0, 1.0)
                    intrinsic += (1.0 / hours_remaining) * DEADLINE_PRESSURE_FACTOR
                except (TypeError, ValueError):
                    pass

            # Step 2: Objective pressure
            objective_pressure = 0.0
            for obj_data in objectives_raw:
                if obj_data and len(obj_data) >= 2 and obj_data[0] is not None:
                    objective_pressure += (
                        float(obj_data[0] or 0.0)
                        * float(obj_data[1] or 1.0)
                        * OBJECTIVE_PRESSURE_RATE
                    )

            # Step 3: Blocking pressure (back-pressure from downstream)
            blocking_pressure = 0.0
            for block_data in blocks_raw:
                if block_data and len(block_data) >= 2 and block_data[0] is not None:
                    blocking_pressure += (
                        float(block_data[0] or 0.0) * BLOCKING_PRESSURE_RATE
                    )

            # Step 4: Smooth convergence
            target_energy = intrinsic + objective_pressure + blocking_pressure
            new_energy = current_energy + (target_energy - current_energy) * ENERGY_CONVERGENCE_RATE
            new_energy = max(ENERGY_MIN, min(ENERGY_MAX, new_energy))

            delta = abs(new_energy - current_energy)
            if delta < 0.001:
                continue  # Skip negligible changes

            write._query(f"""
            MATCH (t:Narrative {{id: '{task_id}'}})
            SET t.energy = {new_energy}
            """)

            total_delta += delta
            tasks_updated += 1

    except Exception as e:
        logger.warning(f"[Task Urgency] Phase failed: {e}")

    if tasks_updated > 0:
        logger.debug(f"[Task Urgency] Updated {tasks_updated} tasks, total delta={total_delta:.2f}")

    return total_delta, tasks_updated
