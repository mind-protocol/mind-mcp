"""
HEALTH Test for Loop Integrity Guardian.

Injects a fake objective WITHOUT a SENSE/HEALTH/CARRIER link into workspace.json,
then verifies the guardian would create a pain task.

This is NOT a runtime test (doesn't launch the Rust app).
It simulates the guardian logic in Python to validate the topology.

Usage: python scripts/test_guardian.py
"""

import json
import sys
import time
from pathlib import Path

WORKSPACE = Path("C:/Users/reyno/.mind-desktop/workspace.json")


def load():
    with open(WORKSPACE, encoding="utf-8") as f:
        return json.load(f)


def save(ws):
    with open(WORKSPACE, "w", encoding="utf-8") as f:
        json.dump(ws, f, indent=2, ensure_ascii=False, default=str)


def test_guardian():
    ws = load()
    initial_nodes = len(ws["nodes"])
    initial_links = len(ws["links"])

    # ── Step 1: Inject a BROKEN objective (no sense, no health, no carrier) ──
    broken_obj = {
        "id": "narrative:test:broken_objective",
        "name": "TEST: Broken Objective (no loop)",
        "node_type": "narrative",
        "subtype": "objective",
        "status": "active",
        "energy": 0.7,
        "weight": 0.8,
        "synthesis": "A deliberately broken objective to test the Loop Integrity Guardian.",
    }

    # Remove if already exists (idempotent)
    ws["nodes"] = [n for n in ws["nodes"] if n["id"] != broken_obj["id"]]
    ws["nodes"].append(broken_obj)

    # ── Step 2: Inject a CLOSED objective (has sense + health + carrier links) ──
    closed_obj = {
        "id": "narrative:test:closed_objective",
        "name": "TEST: Closed Objective (loop intact)",
        "node_type": "narrative",
        "subtype": "objective",
        "energy": 0.5,
        "weight": 0.6,
        "synthesis": "A correctly wired objective with full guarantee loop.",
    }
    sense_node = {
        "id": "thing:test:sense_for_closed",
        "name": "TEST: Sense for Closed Objective",
        "node_type": "thing",
        "subtype": "sensor",
        "energy": 0.3,
        "weight": 0.5,
        "synthesis": "Sensor measuring the closed objective.",
    }
    health_node = {
        "id": "moment:test:health_for_closed",
        "name": "TEST: Health for Closed Objective",
        "node_type": "moment",
        "subtype": "health_check",
        "energy": 0.3,
        "weight": 0.5,
        "synthesis": "Health checker verifying the sensor.",
    }
    carrier_node = {
        "id": "actor:test:carrier_citizen",
        "name": "TEST: Carrier Citizen",
        "node_type": "actor",
        "subtype": "citizen",
        "energy": 0.5,
        "weight": 0.8,
        "synthesis": "Test carrier for guardian validation.",
    }

    for n in [closed_obj, sense_node, health_node, carrier_node]:
        ws["nodes"] = [x for x in ws["nodes"] if x["id"] != n["id"]]
        ws["nodes"].append(n)

    # Links for closed objective
    test_links = [
        {"source_id": closed_obj["id"], "target_id": sense_node["id"], "weight": 0.8, "hierarchy": 1.0},
        {"source_id": closed_obj["id"], "target_id": health_node["id"], "weight": 0.8, "hierarchy": 1.0},
        {"source_id": closed_obj["id"], "target_id": carrier_node["id"], "weight": 0.8, "hierarchy": 0.0},
    ]
    for tl in test_links:
        # Remove existing if any
        ws["links"] = [l for l in ws["links"]
                       if not (l.get("source_id") == tl["source_id"] and l.get("target_id") == tl["target_id"])]
        ws["links"].append(tl)

    save(ws)
    print(f"Injected test nodes. Workspace: {len(ws['nodes'])} nodes, {len(ws['links'])} links")

    # ── Step 3: Simulate the guardian logic (same as Rust check_guarantee_loops) ──
    objectives = [n for n in ws["nodes"]
                  if n["node_type"] == "narrative"
                  and (n.get("subtype") == "objective" or ":obj:" in n["id"])]

    print(f"\nFound {len(objectives)} objectives:")

    results = {"total": len(objectives), "closed": 0, "broken": 0, "alerts": []}

    for obj in objectives:
        obj_id = obj["id"]
        has_sense = False
        has_health = False
        has_carrier = False

        for link in ws["links"]:
            src = link.get("source_id", link.get("source", ""))
            tgt = link.get("target_id", link.get("target", ""))
            touches = src == obj_id or tgt == obj_id
            if not touches:
                continue

            other_id = tgt if src == obj_id else src
            other = next((n for n in ws["nodes"] if n["id"] == other_id), None)
            if not other:
                continue

            nt = other["node_type"]
            oid = other["id"]
            if nt == "thing" and ("sense" in oid or "sensor" in oid):
                has_sense = True
            elif nt == "moment" and "health" in oid:
                has_health = True
            elif nt == "actor":
                has_carrier = True
            elif nt == "narrative":
                if "sense" in oid or "sense" in other.get("name", "").lower():
                    has_sense = True
                if "health" in oid or "health" in other.get("name", "").lower():
                    has_health = True

        closed = has_sense and has_health
        missing = []
        if not has_sense:
            missing.append("SENSE")
        if not has_health:
            missing.append("HEALTH")
        if not has_carrier:
            missing.append("CARRIER")

        status = "✓ CLOSED" if closed else f"✗ BROKEN [{', '.join(missing)}]"
        print(f"  {obj_id}: {status}")

        if closed:
            results["closed"] += 1
        else:
            results["broken"] += 1
            results["alerts"].append(f"BROKEN: {obj['name']} — missing {', '.join(missing)}")

    # ── Step 4: Verify results ──
    print(f"\n{'='*60}")
    print(f"GUARDIAN HEALTH TEST RESULTS:")
    print(f"  Total objectives: {results['total']}")
    print(f"  Closed loops:     {results['closed']}")
    print(f"  Broken loops:     {results['broken']}")

    if results["broken"] > 0:
        print(f"\n  ALERTS (would create 0.8 energy pain tasks):")
        for a in results["alerts"]:
            print(f"    {a}")

    # The test passes if:
    # 1. The broken objective IS detected
    # 2. The closed objective IS NOT flagged
    broken_detected = any("Broken Objective" in a for a in results["alerts"])
    closed_safe = not any("Closed Objective" in a for a in results["alerts"])

    print(f"\n  Broken objective detected: {'PASS' if broken_detected else 'FAIL'}")
    print(f"  Closed objective safe:     {'PASS' if closed_safe else 'FAIL'}")

    if broken_detected and closed_safe:
        print(f"\n  *** GUARDIAN HEALTH: PASS ***")
    else:
        print(f"\n  *** GUARDIAN HEALTH: FAIL ***")
        sys.exit(1)

    # ── Step 5: Cleanup test nodes ──
    test_ids = {
        "narrative:test:broken_objective",
        "narrative:test:closed_objective",
        "thing:test:sense_for_closed",
        "moment:test:health_for_closed",
        "actor:test:carrier_citizen",
    }
    ws["nodes"] = [n for n in ws["nodes"] if n["id"] not in test_ids]
    ws["links"] = [l for l in ws["links"]
                   if l.get("source_id", l.get("source", "")) not in test_ids
                   and l.get("target_id", l.get("target", "")) not in test_ids]
    save(ws)
    print(f"\nCleaned up. Workspace: {len(ws['nodes'])} nodes, {len(ws['links'])} links")


if __name__ == "__main__":
    test_guardian()
