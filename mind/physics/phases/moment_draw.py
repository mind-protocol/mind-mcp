"""
Phase 2: Moment Draw — Both POSSIBLE and ACTIVE moments draw from connected actors.

Formula: flow = actor.energy × DRAW_RATE × weight × emotion_factor
Received: flow × sqrt(moment.weight)

DOCS: docs/physics/IMPLEMENTATION_Physics.md
"""

import logging
import math
from typing import List, Dict
from mind.physics.graph import GraphOps
from mind.physics.constants import DRAW_RATE, TOP_N_LINKS, plutchik_proximity, PLUTCHIK_AXES

logger = logging.getLogger(__name__)


def _get_link_axes(link: Dict) -> Dict[str, float]:
    """Extract Plutchik axes from link dict."""
    return {axis: link.get(axis, 0.0) for axis in PLUTCHIK_AXES}


def phase_moment_draw(
    write: GraphOps,
    moments: List[Dict],
    queries: any,  # TickQueries
    energy_flows_through_func: callable
) -> float:
    """
    Run Phase 2: Moment Draw.

    Args:
        write: Graph write interface
        moments: List of moments to process
        queries: TickQueries instance
        energy_flows_through_func: Function to record energy flow through link

    Returns:
        total_drawn
    """
    total_drawn = 0.0

    # Sort moments by energy × weight
    sorted_moments = sorted(
        moments,
        key=lambda m: (m.get('energy', 0.0) or 0.0) * (m.get('weight', 1.0) or 1.0),
        reverse=True
    )

    for moment in sorted_moments:
        moment_id = moment.get('id')
        moment_weight = moment.get('weight', 1.0) or 1.0
        moment_energy = moment.get('energy', 0.0) or 0.0

        try:
            # Get weighted average Plutchik axes from moment's links
            moment_axes = queries.get_moment_axes(moment_id)

            # Get top 20 expresses links
            links = queries.get_hot_links_to_moment(moment_id, TOP_N_LINKS)

            for link in links:
                actor_id = link.get('actor_id')
                actor_energy = link.get('actor_energy', 0.0) or 0.0
                link_weight = link.get('weight', 1.0) or 1.0
                link_axes = _get_link_axes(link)

                # Calculate emotion factor using Plutchik proximity
                emotion_factor = plutchik_proximity(link_axes, moment_axes)

                # Calculate flow (v1.2: no conductivity)
                flow = actor_energy * DRAW_RATE * link_weight * emotion_factor
                received = flow * math.sqrt(moment_weight)

                if flow > 0.001:  # Skip tiny flows
                    # Update energies
                    actor_energy -= flow
                    moment_energy += received
                    total_drawn += flow

                    # Apply unified traversal (record in link)
                    energy_flows_through_func(
                        link, flow, moment_axes,
                        actor_id, actor_energy,
                        moment_id, moment_energy
                    )

                    # Update actor
                    write._query(f"""
                    MATCH (a:Actor {{id: '{actor_id}'}})
                    SET a.energy = {max(0, actor_energy)}
                    """)

            # Update moment
            write._query(f"""
            MATCH (m:Moment {{id: '{moment_id}'}})
            SET m.energy = {moment_energy}
            """)

        except Exception as e:
            logger.warning(f"[Phase 2] Draw error for {moment_id}: {e}")

    return total_drawn
