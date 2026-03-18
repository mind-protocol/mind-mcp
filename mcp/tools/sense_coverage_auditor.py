"""
Sense Coverage Auditor — Meta-sense that verifies 100% sensory coverage.

This is itself a sense: it continuously checks whether all behaviors/objectives
with RACI assignments have measuring senses routed to the responsible citizens.
Gaps produce tension in the graph — the system literally feels its blind spots.

Usage:
    auditor = SenseCoverageAuditor()
    report = auditor.audit(graph_ops, universe="lumina_prime")
    # report.gaps = [{"narrative_id": ..., "responsible": ..., "issue": "no_sense"}, ...]
    # report.coverage_ratio = 0.73  (73% of RACI narratives have routed senses)

Can also auto-fix by creating placeholder senses and routing them:
    auditor.auto_route(graph_ops, universe="lumina_prime")

Co-Authored-By: Mentor (@mentor) <mentor@mindprotocol.ai>
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.sense_coverage")


@dataclass
class CoverageGap:
    narrative_id: str
    narrative_name: str
    responsible: Optional[str]
    accountable: Optional[str]
    issue: str  # "no_sense", "no_routing", "no_responsible"


@dataclass
class CoverageReport:
    total_raci_narratives: int = 0
    covered: int = 0
    gaps: List[CoverageGap] = field(default_factory=list)

    @property
    def coverage_ratio(self) -> float:
        if self.total_raci_narratives == 0:
            return 1.0
        return self.covered / self.total_raci_narratives

    def summary(self) -> str:
        lines = [
            f"Sense coverage: {self.covered}/{self.total_raci_narratives} "
            f"({self.coverage_ratio:.0%})",
        ]
        if self.gaps:
            lines.append(f"Gaps ({len(self.gaps)}):")
            for gap in self.gaps[:20]:
                lines.append(
                    f"  • {gap.narrative_name or gap.narrative_id}: "
                    f"{gap.issue} (R: @{gap.responsible or '?'})"
                )
        return "\n".join(lines)


class SenseCoverageAuditor:
    """Audit sensory coverage across all RACI-assigned narratives."""

    def audit(self, graph_ops, universe: str = "lumina_prime") -> CoverageReport:
        """Scan all narratives with RACI assignments and check sense coverage.

        Returns a CoverageReport with gaps and coverage ratio.
        """
        report = CoverageReport()

        # Find all narratives that have at least one RACI link
        rows = _safe_query(
            graph_ops,
            "MATCH (a:Actor)-[r:LINK]->(n:Narrative) "
            "WHERE r.computed_type IN ['responsible', 'accountable'] "
            "RETURN DISTINCT n.id, n.name, "
            "       r.computed_type, a.id "
            "ORDER BY n.id",
        )

        if not rows:
            return report

        # Group by narrative
        narratives: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            nid, nname, role, actor_id = row[0], row[1], row[2], row[3]
            if nid not in narratives:
                narratives[nid] = {
                    "name": nname or nid,
                    "responsible": None,
                    "accountable": None,
                }
            if role == "responsible":
                narratives[nid]["responsible"] = actor_id
            elif role == "accountable":
                narratives[nid]["accountable"] = actor_id

        report.total_raci_narratives = len(narratives)

        # Check each narrative for sense coverage
        for nid, info in narratives.items():
            # Check if a sense measures this narrative
            sense_rows = _safe_query(
                graph_ops,
                "MATCH (s:Thing)-[r:LINK]->(n {id: $nid}) "
                "WHERE s.type = 'sense' AND r.computed_type = 'measures' "
                "RETURN s.id LIMIT 1",
                {"nid": nid},
            )

            if not sense_rows:
                report.gaps.append(CoverageGap(
                    narrative_id=nid,
                    narrative_name=info["name"],
                    responsible=info["responsible"],
                    accountable=info["accountable"],
                    issue="no_sense",
                ))
                continue

            sense_id = sense_rows[0][0]
            target_actor = info["responsible"] or info["accountable"]

            if not target_actor:
                report.gaps.append(CoverageGap(
                    narrative_id=nid,
                    narrative_name=info["name"],
                    responsible=None,
                    accountable=None,
                    issue="no_responsible",
                ))
                continue

            # Check if sense is routed to the responsible/accountable actor
            route_rows = _safe_query(
                graph_ops,
                "MATCH (a:Actor {id: $aid})-[:LINK]->(s:Thing {id: $sid}) "
                "RETURN a.id LIMIT 1",
                {"aid": target_actor, "sid": sense_id},
            )

            if not route_rows:
                report.gaps.append(CoverageGap(
                    narrative_id=nid,
                    narrative_name=info["name"],
                    responsible=info["responsible"],
                    accountable=info["accountable"],
                    issue="no_routing",
                ))
                continue

            # Fully covered
            report.covered += 1

        return report

    def auto_route(self, graph_ops, universe: str = "lumina_prime") -> int:
        """Auto-fix routing gaps by linking existing senses to RACI actors.

        Does NOT create new senses — only routes existing ones.
        Returns number of routes created.
        """
        from mcp.tools.raci_query import route_sense_to_raci

        report = self.audit(graph_ops, universe)
        routes_created = 0

        for gap in report.gaps:
            if gap.issue == "no_routing":
                # Sense exists but not routed — fix it
                sense_rows = _safe_query(
                    graph_ops,
                    "MATCH (s:Thing)-[r:LINK]->(n {id: $nid}) "
                    "WHERE s.type = 'sense' AND r.computed_type = 'measures' "
                    "RETURN s.id LIMIT 1",
                    {"nid": gap.narrative_id},
                )
                if sense_rows:
                    sense_id = sense_rows[0][0]
                    route_sense_to_raci(sense_id, gap.narrative_id, graph_ops)
                    routes_created += 1
                    logger.info(
                        f"Auto-routed sense {sense_id} to RACI actors of {gap.narrative_id}"
                    )

        return routes_created


def _safe_query(graph_ops, cypher, params=None):
    try:
        result = graph_ops._query(cypher, params or {})
        return result if result else []
    except Exception:
        return []
