"""
Phase 9b: Task Decay — Completed tasks lose energy with configurable half-life.

Default half-life: 2 hours. After ~6h energy < 12.5% of original.
Tasks below TASK_PRUNE_THRESHOLD are flagged as prunable.

DOCS: docs/organization/task_physics/ALGORITHM_Task_Physics.md
"""

import logging
import math
import time
from typing import Tuple
from runtime.physics.graph import GraphQueries, GraphOps
from runtime.organization.task_constants import (
    ENERGY_MIN,
    ENERGY_MAX,
    TASK_COMPLETED_HALF_LIFE,
    TASK_PRUNE_THRESHOLD,
)

logger = logging.getLogger(__name__)


def phase_task_decay(read: GraphQueries, write: GraphOps) -> Tuple[float, int]:
    """
    Run Phase 9b: Completed Task Decay.

    Applies rapid half-life decay to all completed tasks.

    Returns:
        (total_energy_decayed, tasks_decayed)
    """
    total_decayed = 0.0
    tasks_decayed = 0

    try:
        rows = read.query("""
        MATCH (t:Narrative)
        WHERE t.type = 'task'
          AND t.status = 'done'
          AND t.completed_at IS NOT NULL
          AND t.completed_at > 0
          AND COALESCE(t.prunable, false) = false
        RETURN t.id AS id,
               t.energy AS energy,
               t.completed_at AS completed_at,
               COALESCE(t.half_life_hours, 2.0) AS half_life,
               COALESCE(t.energy_at_completion, t.energy) AS energy_at_completion
        """)

        if not rows:
            return 0.0, 0

        now = time.time()

        for row in rows:
            task_id = row.get('id')
            if not task_id:
                continue

            completed_at = float(row.get('completed_at') or 0)
            half_life = float(row.get('half_life') or TASK_COMPLETED_HALF_LIFE)
            energy_at_completion = float(row.get('energy_at_completion') or 0.5)
            current_energy = float(row.get('energy') or 0.0)

            if completed_at <= 0 or half_life <= 0:
                continue

            elapsed_hours = (now - completed_at) / 3600.0
            decay_factor = math.pow(0.5, elapsed_hours / half_life)
            new_energy = max(ENERGY_MIN, min(ENERGY_MAX, energy_at_completion * decay_factor))

            decayed = current_energy - new_energy
            if decayed < 0.001:
                continue

            prunable = new_energy < TASK_PRUNE_THRESHOLD

            write._query(f"""
            MATCH (t:Narrative {{id: '{task_id}'}})
            SET t.energy = {new_energy}, t.prunable = {str(prunable).lower()}
            """)

            total_decayed += decayed
            tasks_decayed += 1

            if prunable:
                logger.debug(f"[Task Decay] {task_id} prunable (energy={new_energy:.4f})")

    except Exception as e:
        logger.warning(f"[Task Decay] Phase failed: {e}")

    if tasks_decayed > 0:
        logger.debug(f"[Task Decay] Decayed {tasks_decayed} tasks, total={total_decayed:.2f}")

    return total_decayed, tasks_decayed
