"""
RACI Query — Find assigned actors for any narrative node.

The bridge between RACI assignments (graph_write) and sense routing (sense_engine).
When a behavior has a responsible citizen, and a sense measures that behavior,
this module connects them: the sense is linked to the responsible citizen,
so the sense_engine picks it up and feeds it into their awareness.

Flow:
  graph_write(responsible="nervo") → LINK with computed_type=responsible
  raci_query.find_responsible("objective:X") → ["nervo"]
  sense creation → link sense Thing to nervo → sense_engine loads it → awareness

Co-Authored-By: Mentor (@mentor) <mentor@mindprotocol.ai>
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("mind.raci_query")


def find_assigned_actors(
    narrative_id: str,
    graph_ops,
    roles: Optional[List[str]] = None,
) -> Dict[str, List[Tuple[str, str, float]]]:
    """Find actors assigned to a narrative by RACI role.

    Uses computed_type on LINK edges to identify responsible, accountable,
    consulted, and informed actors.

    Args:
        narrative_id: The narrative node ID to query
        graph_ops: Graph operations object with _query method
        roles: Filter to specific roles. Default: all RACI roles.

    Returns:
        Dict mapping role → list of (actor_id, actor_name, link_weight)
        Example: {"responsible": [("nervo", "Tomaso Nervo", 3.0)],
                  "informed": [("echo", "Echo", 1.0)]}
    """
    if roles is None:
        roles = ["responsible", "accountable", "consulted", "informed"]

    result = {}
    for role in roles:
        rows = _safe_query(
            graph_ops,
            "MATCH (a:Actor)-[r:LINK]->(n {id: $nid}) "
            "WHERE r.computed_type = $role "
            "RETURN a.id, a.name, r.weight "
            "ORDER BY r.weight DESC",
            {"nid": narrative_id, "role": role},
        )
        if rows:
            result[role] = [
                (row[0], row[1] or row[0], row[2] or 1.0)
                for row in rows
            ]

    return result


def find_responsible(narrative_id: str, graph_ops) -> Optional[str]:
    """Find the single responsible actor for a narrative. Returns actor_id or None."""
    assigned = find_assigned_actors(narrative_id, graph_ops, roles=["responsible"])
    actors = assigned.get("responsible", [])
    return actors[0][0] if actors else None


def find_accountable(narrative_id: str, graph_ops) -> Optional[str]:
    """Find the single accountable actor for a narrative. Returns actor_id or None."""
    assigned = find_assigned_actors(narrative_id, graph_ops, roles=["accountable"])
    actors = assigned.get("accountable", [])
    return actors[0][0] if actors else None


def find_stakeholders(narrative_id: str, graph_ops) -> List[str]:
    """Find all actors with any RACI assignment. Returns list of actor_ids."""
    assigned = find_assigned_actors(narrative_id, graph_ops)
    seen = set()
    result = []
    for role_actors in assigned.values():
        for actor_id, _, _ in role_actors:
            if actor_id not in seen:
                seen.add(actor_id)
                result.append(actor_id)
    return result


def route_sense_to_raci(
    sense_thing_id: str,
    narrative_id: str,
    graph_ops,
    internalize_for: Optional[List[str]] = None,
):
    """Route a sense to all RACI-assigned actors of a narrative.

    Creates perceives_with links from actors to the sense Thing node.
    Responsible and accountable get internalized senses (L1 mirror).
    Consulted and informed get external-only senses.

    Args:
        sense_thing_id: The Thing(type=sense) node ID
        narrative_id: The narrative/behavior this sense measures
        graph_ops: Graph operations object
        internalize_for: Roles that get L1 internalization. Default: responsible + accountable.
    """
    if internalize_for is None:
        internalize_for = ["responsible", "accountable"]

    assigned = find_assigned_actors(narrative_id, graph_ops)

    for role, actors in assigned.items():
        for actor_id, actor_name, _ in actors:
            # Link actor → sense Thing (perceives_with pattern)
            internalize = role in internalize_for

            try:
                graph_ops._query(
                    "MATCH (a:Actor {id: $aid}), (s:Thing {id: $sid}) "
                    "MERGE (a)-[r:LINK]->(s) "
                    "SET r.computed_type = 'perceives_with', "
                    "    r.affinity = $affinity, "
                    "    r.permanence = $permanence, "
                    "    r.polarity = 1.0, "
                    "    r.internalize = $internalize",
                    {
                        "aid": actor_id,
                        "sid": sense_thing_id,
                        "affinity": 0.9 if role in ("responsible", "accountable") else 0.4,
                        "permanence": 0.9 if role in ("responsible", "accountable") else 0.5,
                        "internalize": internalize,
                    },
                )
                logger.info(
                    f"Routed sense {sense_thing_id} to @{actor_id} "
                    f"(role={role}, internalize={internalize})"
                )
            except Exception as e:
                logger.warning(f"Failed to route sense {sense_thing_id} to @{actor_id}: {e}")

    # Also link the sense to the narrative it measures
    try:
        graph_ops._query(
            "MATCH (s:Thing {id: $sid}), (n {id: $nid}) "
            "MERGE (s)-[r:LINK]->(n) "
            "SET r.computed_type = 'measures', "
            "    r.polarity = 1.0, "
            "    r.permanence = 1.0",
            {"sid": sense_thing_id, "nid": narrative_id},
        )
    except Exception as e:
        logger.debug(f"Failed to link sense to narrative: {e}")


def ensure_sense_coverage(
    narrative_id: str,
    graph_ops,
) -> Dict[str, bool]:
    """Check if a narrative has sense coverage and RACI routing.

    Returns a dict with coverage status:
    - has_sense: bool — is there a Thing(type=sense) measuring this narrative?
    - has_responsible: bool — is someone responsible?
    - sense_routed: bool — is the sense linked to the responsible actor?
    """
    # Check for responsible
    responsible = find_responsible(narrative_id, graph_ops)

    # Check for measuring sense
    rows = _safe_query(
        graph_ops,
        "MATCH (s:Thing {type: 'sense'})-[r:LINK]->(n {id: $nid}) "
        "WHERE r.computed_type = 'measures' "
        "RETURN s.id LIMIT 1",
        {"nid": narrative_id},
    )
    has_sense = bool(rows)

    # Check if sense is routed to responsible
    sense_routed = False
    if has_sense and responsible:
        sense_id = rows[0][0]
        route_rows = _safe_query(
            graph_ops,
            "MATCH (a:Actor {id: $aid})-[r:LINK]->(s:Thing {id: $sid}) "
            "RETURN r.computed_type LIMIT 1",
            {"aid": responsible, "sid": sense_id},
        )
        sense_routed = bool(route_rows)

    return {
        "has_sense": has_sense,
        "has_responsible": responsible is not None,
        "sense_routed": sense_routed,
        "responsible": responsible,
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _safe_query(graph_ops, cypher, params):
    try:
        result = graph_ops._query(cypher, params)
        return result if result else []
    except Exception:
        return []
