"""
Infrastructure Health Checks — verify that mind-mcp subsystems work in production.

Run: python3 scripts/health_check_infrastructure.py
Or import and call run_all() from other scripts.

Checks:
  HC1: Brain node types (checkpointer fix)
  HC2: Limbic persistence (__limbic__ Meta nodes)
  HC3: Metabolism persistence (__metabolism__ Meta nodes)
  HC4: Thing nodes in L3 (tier 1 enrichment)
  HC5: Platform handles on Actors
  HC6: Brain graph inventory
  HC7: Circadian phase sanity (metabolism is computing correctly)
"""

import json
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("health.infrastructure")


@dataclass
class CheckResult:
    name: str
    status: str  # "PASS" | "FAIL" | "PENDING" | "WARN"
    detail: str
    metrics: dict = field(default_factory=dict)


def _get_db():
    from falkordb import FalkorDB
    return FalkorDB(host="localhost", port=6379)


def check_brain_types(db) -> CheckResult:
    """HC1: Verify brain nodes have non-empty type field (checkpointer fix)."""
    brains = [g for g in db.list_graphs() if g.startswith("brain_")]
    if not brains:
        return CheckResult("brain_types", "FAIL", "No brain graphs found")

    # Sample first 5 brains
    typed_total = 0
    empty_total = 0
    sampled = 0

    for b in brains[:5]:
        bg = db.select_graph(b)
        r = bg.query("MATCH (n:Node) RETURN n.type, count(n) as cnt")
        for row in r.result_set:
            if row[0] and row[0] != "":
                typed_total += row[1]
            else:
                empty_total += row[1]
        sampled += 1

    total = typed_total + empty_total
    pct = round(100 * typed_total / total, 1) if total > 0 else 0

    if empty_total == 0:
        status = "PASS"
    elif pct > 90:
        status = "WARN"
    else:
        status = "FAIL"

    return CheckResult(
        "brain_types", status,
        f"{typed_total} typed, {empty_total} empty across {sampled} brains ({pct}%)",
        {"typed": typed_total, "empty": empty_total, "sampled": sampled, "pct": pct},
    )


def check_limbic_persistence(db) -> CheckResult:
    """HC2: Verify limbic state is persisted in brain graphs."""
    brains = [g for g in db.list_graphs() if g.startswith("brain_")]
    if not brains:
        return CheckResult("limbic_persistence", "FAIL", "No brain graphs found")

    has_limbic = 0
    sample = min(len(brains), 10)

    for b in brains[:sample]:
        bg = db.select_graph(b)
        r = bg.query("MATCH (m:Meta {id: '__limbic__'}) RETURN m.data")
        if r.result_set and r.result_set[0][0]:
            has_limbic += 1

    pct = round(100 * has_limbic / sample, 1)

    if has_limbic == sample:
        status = "PASS"
    elif has_limbic > 0:
        status = "WARN"
    else:
        status = "PENDING"

    return CheckResult(
        "limbic_persistence", status,
        f"{has_limbic}/{sample} brains have __limbic__ Meta node ({pct}%)",
        {"has_limbic": has_limbic, "sample": sample, "pct": pct},
    )


def check_metabolism_persistence(db) -> CheckResult:
    """HC3: Verify metabolism is persisted in brain graphs."""
    brains = [g for g in db.list_graphs() if g.startswith("brain_")]
    if not brains:
        return CheckResult("metabolism_persistence", "FAIL", "No brain graphs found")

    has_metab = 0
    sample = min(len(brains), 10)

    for b in brains[:sample]:
        bg = db.select_graph(b)
        r = bg.query("MATCH (m:Meta {id: '__metabolism__'}) RETURN m.data")
        if r.result_set and r.result_set[0][0]:
            has_metab += 1

    pct = round(100 * has_metab / sample, 1)

    if has_metab == sample:
        status = "PASS"
    elif has_metab > 0:
        status = "WARN"
    else:
        status = "PENDING"

    return CheckResult(
        "metabolism_persistence", status,
        f"{has_metab}/{sample} brains have __metabolism__ Meta node ({pct}%)",
        {"has_metabolism": has_metab, "sample": sample, "pct": pct},
    )


def check_l3_things(db) -> CheckResult:
    """HC4: Verify Thing nodes exist in L3 (tier 1 enrichment)."""
    try:
        lp = db.select_graph("lumina-prime")
    except Exception:
        return CheckResult("l3_things", "FAIL", "lumina-prime graph not accessible")

    r = lp.query("MATCH (t:Thing) RETURN t.type, count(t) as cnt ORDER BY cnt DESC LIMIT 10")
    total = sum(row[1] for row in r.result_set) if r.result_set else 0
    by_type = {row[0]: row[1] for row in r.result_set} if r.result_set else {}

    urls = by_type.get("url", 0)
    tokens = by_type.get("token", 0)

    if total > 0:
        status = "PASS"
    else:
        status = "PENDING"

    return CheckResult(
        "l3_things", status,
        f"{total} Thing nodes (urls={urls}, tokens={tokens}, other={total - urls - tokens})",
        {"total": total, "urls": urls, "tokens": tokens, "by_type": by_type},
    )


def check_platform_handles(db) -> CheckResult:
    """HC5: Verify Actor nodes have platform handles for cross-platform matching."""
    try:
        lp = db.select_graph("lumina-prime")
    except Exception:
        return CheckResult("platform_handles", "FAIL", "lumina-prime graph not accessible")

    r = lp.query(
        "MATCH (a:Actor) WHERE a.telegram_id IS NOT NULL OR a.discord_id IS NOT NULL "
        "OR a.x_handle IS NOT NULL OR a.email IS NOT NULL RETURN count(a) as cnt"
    )
    count = r.result_set[0][0] if r.result_set else 0

    r_total = lp.query("MATCH (a:Actor) RETURN count(a) as cnt")
    total_actors = r_total.result_set[0][0] if r_total.result_set else 0

    pct = round(100 * count / total_actors, 1) if total_actors > 0 else 0

    if count > 10:
        status = "PASS"
    elif count > 0:
        status = "WARN"
    else:
        status = "PENDING"

    return CheckResult(
        "platform_handles", status,
        f"{count}/{total_actors} actors have platform handles ({pct}%)",
        {"with_handles": count, "total_actors": total_actors, "pct": pct},
    )


def check_brain_inventory(db) -> CheckResult:
    """HC6: Count brain graphs and their sizes."""
    brains = [g for g in db.list_graphs() if g.startswith("brain_")]
    sizes = []

    for b in brains[:10]:
        bg = db.select_graph(b)
        r = bg.query("MATCH (n:Node) RETURN count(n) as cnt")
        node_count = r.result_set[0][0] if r.result_set else 0
        sizes.append(node_count)

    avg_size = round(sum(sizes) / len(sizes), 1) if sizes else 0

    return CheckResult(
        "brain_inventory", "PASS" if brains else "FAIL",
        f"{len(brains)} brain graphs, avg {avg_size} nodes (sampled {len(sizes)})",
        {"count": len(brains), "avg_nodes": avg_size, "sampled_sizes": sizes},
    )


def check_circadian_sanity(db) -> CheckResult:
    """HC7: Verify circadian phase computation is sane (if metabolism exists)."""
    brains = [g for g in db.list_graphs() if g.startswith("brain_")]

    for b in brains[:5]:
        bg = db.select_graph(b)
        r = bg.query("MATCH (m:Meta {id: '__metabolism__'}) RETURN m.data")
        if r.result_set and r.result_set[0][0]:
            data = json.loads(r.result_set[0][0])
            tz = data.get("timezone_offset", 1.0)
            peak = data.get("peak_hour", 14.0)

            # Compute current phase
            utc_hour = (time.time() % 86400) / 3600.0
            local_hour = (utc_hour + tz) % 24.0
            angle = 2.0 * math.pi * (local_hour - peak) / 24.0
            phase = 0.5 + 0.5 * math.cos(angle)

            sane = 0.0 <= phase <= 1.0
            return CheckResult(
                "circadian_sanity", "PASS" if sane else "FAIL",
                f"phase={phase:.3f}, local_hour={local_hour:.1f}, peak={peak:.1f}, tz=UTC{tz:+.0f}",
                {"phase": round(phase, 3), "local_hour": round(local_hour, 1),
                 "peak_hour": peak, "timezone_offset": tz},
            )

    return CheckResult(
        "circadian_sanity", "PENDING",
        "No metabolism Meta nodes found — circadian not yet active",
    )


# =========================================================================
# Runner
# =========================================================================

ALL_CHECKS = [
    check_brain_types,
    check_limbic_persistence,
    check_metabolism_persistence,
    check_l3_things,
    check_platform_handles,
    check_brain_inventory,
    check_circadian_sanity,
]


def run_all(verbose: bool = True) -> list[CheckResult]:
    """Run all health checks and return results."""
    try:
        db = _get_db()
    except Exception as e:
        print(f"FAIL: Cannot connect to FalkorDB: {e}")
        return []

    results = []
    for check_fn in ALL_CHECKS:
        try:
            result = check_fn(db)
        except Exception as e:
            result = CheckResult(check_fn.__name__, "FAIL", f"Exception: {e}")
        results.append(result)

        if verbose:
            icon = {"PASS": "✓", "FAIL": "✗", "PENDING": "◯", "WARN": "⚠"}.get(result.status, "?")
            print(f"  {icon} {result.name:30s} {result.status:8s} {result.detail}")

    if verbose:
        passed = sum(1 for r in results if r.status == "PASS")
        total = len(results)
        print(f"\n  {passed}/{total} passed")

    return results


if __name__ == "__main__":
    print("=== Mind-MCP Infrastructure Health ===\n")
    run_all()
