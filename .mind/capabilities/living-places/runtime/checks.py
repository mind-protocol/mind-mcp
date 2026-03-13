"""
Health Checks: living-places

Runtime health monitoring for the Living Places system.
Detects stale places, orphaned moments, inconsistent presence,
energy decay failures, capacity violations, and idle presences.

DOCS: capabilities/living-places/HEALTH.md
"""

import time
import logging
from typing import Optional

from runtime.capability import check, Signal, triggers

log = logging.getLogger("mind.capability.living_places")


# =============================================================================
# GRAPH ACCESS
# =============================================================================

def _get_graph():
    """Get a database adapter for graph queries."""
    from runtime.infrastructure.database.factory import get_database_adapter
    return get_database_adapter(graph_name="manemus")


# =============================================================================
# THRESHOLDS
# =============================================================================

LIVENESS_WINDOW_S = 30 * 60       # 30 minutes — no moments = degraded
STALE_PRESENCE_S = 60 * 60        # 1 hour — presence with no recent moments
ENERGY_DECAY_AGE_S = 60 * 60      # 1 hour — moments older than this should have decayed
ENERGY_DECAY_FLOOR = 0.01         # Below this, energy is effectively zero
ENERGY_DECAY_MAX_UNDECAYED = 100  # V1 has no decay, so threshold is high
IDLE_PRESENCE_S = 5 * 60          # 5 minutes — AT link with no recent moments


# =============================================================================
# HEALTH CHECKS
# =============================================================================

@check(
    id="place_liveness",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="PLACE_DEAD",
    task="TASK_investigate_dead_place",
)
def check_place_liveness(ctx) -> Signal:
    """
    H1: Detect active places with no recent moments.

    Queries all places with status='active' and checks whether any moments
    have been created in the last 30 minutes. Active places without recent
    activity are a sign the system may not be routing conversations correctly.

    Returns DEGRADED if any active place has zero recent moments.
    Returns HEALTHY otherwise.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"place_liveness: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    threshold = int(time.time()) - LIVENESS_WINDOW_S

    try:
        rows = graph.query(
            "MATCH (s:Space {type: 'place', status: 'active'}) "
            "OPTIONAL MATCH (m:Moment)-[:link {type: 'IN'}]->(s) "
            "WHERE m.created_at_s > $threshold "
            "RETURN s.id, s.name, count(m)",
            {"threshold": threshold},
        )
    except Exception as e:
        log.error(f"place_liveness: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    dead_places = []
    for row in rows:
        place_id, place_name, moment_count = row[0], row[1], row[2]
        if moment_count == 0:
            dead_places.append({"id": place_id, "name": place_name})

    if dead_places:
        return Signal.degraded(
            dead_places=dead_places,
            count=len(dead_places),
            window_minutes=LIVENESS_WINDOW_S // 60,
        )

    return Signal.healthy()


@check(
    id="moment_persistence",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="ORPHANED_MOMENTS",
    task="TASK_fix_orphaned_moments",
)
def check_moment_persistence(ctx) -> Signal:
    """
    H2: Detect moments without an IN link to any Space.

    Every utterance moment must be placed in a Space. Orphaned moments
    indicate a failure in the placement pipeline — moments were created
    but never linked to their containing place.

    Returns CRITICAL if orphaned moments exist.
    Returns HEALTHY if all moments are properly placed.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"moment_persistence: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    try:
        rows = graph.query(
            "MATCH (m:Moment {type: 'utterance'}) "
            "WHERE NOT (m)-[:link {type: 'IN'}]->(:Space) "
            "RETURN count(m)",
        )
    except Exception as e:
        log.error(f"moment_persistence: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    orphan_count = rows[0][0] if rows else 0

    if orphan_count > 0:
        return Signal.critical(
            orphaned_moment_count=orphan_count,
        )

    return Signal.healthy()


@check(
    id="presence_consistency",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="STALE_PRESENCE",
    task="TASK_cleanup_stale_presence",
)
def check_presence_consistency(ctx) -> Signal:
    """
    H3: Detect AT links with very old joined_at timestamps (stale presence).

    If an actor has an AT link to a place but the joined_at is over 1 hour
    old and the actor has no recent moments in that place, the presence is
    stale — the actor likely disconnected without proper cleanup.

    Returns DEGRADED if stale presences found.
    Returns HEALTHY otherwise.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"presence_consistency: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    stale_cutoff = int(time.time()) - STALE_PRESENCE_S
    recent_cutoff = int(time.time()) - IDLE_PRESENCE_S

    try:
        # Get all AT presences with joined_at
        rows = graph.query(
            "MATCH (a)-[r:link {type: 'AT'}]->(s:Space {type: 'place'}) "
            "WHERE r.joined_at IS NOT NULL AND r.joined_at < $stale_cutoff "
            "OPTIONAL MATCH (m:Moment)-[:link {type: 'IN'}]->(s) "
            "WHERE m.created_at_s > $recent_cutoff "
            "AND (m)-[:link {type: 'BY'}]->(a) "
            "RETURN a.id, s.id, s.name, r.joined_at, count(m)",
            {"stale_cutoff": stale_cutoff, "recent_cutoff": recent_cutoff},
        )
    except Exception as e:
        log.error(f"presence_consistency: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    stale_presences = []
    for row in rows:
        actor_id, space_id, space_name, joined_at, recent_moments = (
            row[0], row[1], row[2], row[3], row[4],
        )
        if recent_moments == 0:
            stale_presences.append({
                "actor_id": actor_id,
                "space_id": space_id,
                "space_name": space_name,
                "joined_at": joined_at,
            })

    if stale_presences:
        return Signal.degraded(
            stale_presences=stale_presences,
            count=len(stale_presences),
        )

    return Signal.healthy()


@check(
    id="energy_decay",
    triggers=[
        triggers.cron.every("15m"),
    ],
    on_problem="ENERGY_DECAY_STALLED",
    task="TASK_investigate_energy_decay",
)
def check_energy_decay(ctx) -> Signal:
    """
    H4: Detect moments older than 1 hour with energy still above floor.

    In a healthy system, moment energy decays over time. If old moments
    still have high energy, the decay process is not running.

    Note: V1 has no decay implemented, so this checker is expected to
    return DEGRADED. The threshold is set high (100 undecayed moments)
    to avoid noise until decay is built.

    Returns DEGRADED if undecayed count exceeds threshold.
    Returns HEALTHY otherwise.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"energy_decay: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    one_hour_ago = int(time.time()) - ENERGY_DECAY_AGE_S

    try:
        rows = graph.query(
            "MATCH (m:Moment)-[:link {type: 'IN'}]->(s:Space {type: 'place'}) "
            "WHERE m.created_at_s < $one_hour_ago AND m.energy > $floor "
            "RETURN count(m)",
            {"one_hour_ago": one_hour_ago, "floor": ENERGY_DECAY_FLOOR},
        )
    except Exception as e:
        log.error(f"energy_decay: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    undecayed_count = rows[0][0] if rows else 0

    if undecayed_count > ENERGY_DECAY_MAX_UNDECAYED:
        return Signal.degraded(
            undecayed_moment_count=undecayed_count,
            threshold=ENERGY_DECAY_MAX_UNDECAYED,
            note="V1 has no decay — this is expected until decay is implemented",
        )

    return Signal.healthy()


@check(
    id="orphaned_utterances",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="ORPHANED_UTTERANCES",
    task="TASK_fix_orphaned_moments",
)
def check_orphaned_moments(ctx) -> Signal:
    """
    H5: Detect utterance moments with no Space link.

    Specifically targets type='utterance' moments that lack an IN link to
    any Space node. These are conversation fragments that were created but
    never placed — data that exists outside the spatial structure.

    Returns CRITICAL if any orphaned utterances found.
    Returns HEALTHY if all utterances are placed.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"orphaned_utterances: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    try:
        rows = graph.query(
            "MATCH (m:Moment {type: 'utterance'}) "
            "WHERE NOT (m)-[:link {type: 'IN'}]->(:Space) "
            "RETURN count(m)",
        )
    except Exception as e:
        log.error(f"orphaned_utterances: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    orphan_count = rows[0][0] if rows else 0

    if orphan_count > 0:
        return Signal.critical(
            orphaned_utterance_count=orphan_count,
        )

    return Signal.healthy()


@check(
    id="capacity_enforcement",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="PLACE_OVERCROWDED",
    task="TASK_enforce_place_capacity",
)
def check_capacity_enforcement(ctx) -> Signal:
    """
    H6: Detect places where participant count exceeds capacity.

    Each place may define a capacity limit. If the number of actors
    currently AT a place exceeds that limit, something bypassed the
    admission check — or capacity was reduced after actors joined.

    Returns CRITICAL if any place is overcrowded.
    Returns HEALTHY otherwise.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"capacity_enforcement: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    try:
        rows = graph.query(
            "MATCH (s:Space {type: 'place'}) "
            "WHERE s.capacity IS NOT NULL "
            "OPTIONAL MATCH (a)-[:link {type: 'AT'}]->(s) "
            "WITH s, count(a) AS occupants "
            "WHERE occupants > s.capacity "
            "RETURN s.id, s.name, s.capacity, occupants",
        )
    except Exception as e:
        log.error(f"capacity_enforcement: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    if not rows:
        return Signal.healthy()

    overcrowded = []
    for row in rows:
        overcrowded.append({
            "space_id": row[0],
            "space_name": row[1],
            "capacity": row[2],
            "occupants": row[3],
        })

    return Signal.critical(
        overcrowded_places=overcrowded,
        count=len(overcrowded),
    )


@check(
    id="stale_presence",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="IDLE_PRESENCE",
    task="TASK_cleanup_idle_presence",
)
def check_stale_presence(ctx) -> Signal:
    """
    H7: Detect actors with AT link but no recent moments (idle > 5 min).

    Actors who are marked as present in a place but haven't said anything
    in 5 minutes may have disconnected without leaving. This is a lighter
    check than H3 (presence_consistency) — it catches shorter idle periods
    to keep presence data fresh.

    Returns DEGRADED if idle presences found.
    Returns HEALTHY otherwise.
    """
    try:
        graph = _get_graph()
    except Exception as e:
        log.error(f"stale_presence: cannot connect to graph: {e}")
        return Signal.degraded(error=f"graph_connection_failed: {e}")

    idle_cutoff = int(time.time()) - IDLE_PRESENCE_S

    try:
        rows = graph.query(
            "MATCH (a)-[r:link {type: 'AT'}]->(s:Space {type: 'place'}) "
            "OPTIONAL MATCH (m:Moment)-[:link {type: 'IN'}]->(s) "
            "WHERE (m)-[:link {type: 'BY'}]->(a) "
            "WITH a, s, max(m.created_at_s) AS last_moment "
            "WHERE last_moment IS NULL OR last_moment < $idle_cutoff "
            "RETURN a.id, s.id, s.name, last_moment",
            {"idle_cutoff": idle_cutoff},
        )
    except Exception as e:
        log.error(f"stale_presence: query failed: {e}")
        return Signal.degraded(error=f"query_failed: {e}")

    idle_presences = []
    for row in rows:
        actor_id, space_id, space_name, last_moment = (
            row[0], row[1], row[2], row[3],
        )
        idle_presences.append({
            "actor_id": actor_id,
            "space_id": space_id,
            "space_name": space_name,
            "last_moment_at": last_moment,
        })

    if idle_presences:
        return Signal.degraded(
            idle_presences=idle_presences,
            count=len(idle_presences),
            idle_threshold_seconds=IDLE_PRESENCE_S,
        )

    return Signal.healthy()


# =============================================================================
# REGISTRY
# =============================================================================

CHECKS = [
    check_place_liveness,
    check_moment_persistence,
    check_presence_consistency,
    check_energy_decay,
    check_orphaned_moments,
    check_capacity_enforcement,
    check_stale_presence,
]
