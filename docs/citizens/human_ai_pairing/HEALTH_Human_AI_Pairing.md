# Human-AI Pairing — Health: Verification

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## PURPOSE OF THIS FILE

This document defines the health checks, indicators, and verification procedures
that ensure the human-AI pairing system maintains its invariants in production.
It covers how to detect cardinality violations, matching pool staleness, bond
lifecycle inconsistencies, and autonomy tracking gaps before they degrade the
ecosystem.

---

## WHY THIS PATTERN

The 1:1 pairing constraint is the foundational guarantee of species parity in
Mind Protocol. If this constraint is silently violated — through race conditions,
partial state transitions, or unchecked edge cases — the ecosystem loses its
bilateral character. Health checks must verify the invariants continuously and
loudly, not rely on periodic human audits.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
THIS:            ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

> **Contract:** Health checks verify that the pairing invariants hold at runtime
> and surface violations before they propagate through the ecosystem.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: cardinality_check
    purpose: Verify no citizen or human has more than one active bond.
    triggers:
      - type: bond_event
        source: bond_lifecycle_manager.form_bond / dissolve_bond
        notes: Fires after every bond mutation to catch violations immediately.
      - type: scheduled
        source: mind doctor / background tick
        notes: Periodic sweep to catch violations missed by event-driven checks.
    frequency:
      expected_rate: per bond event + 1/day background sweep
      peak_rate: during bulk onboarding events
      burst_behavior: Each check runs a graph query counting active bonds per entity.
    risks:
      - Race conditions during concurrent bond formation could bypass event-driven checks.
      - Background sweep cadence too slow to catch violations before they propagate.

  - flow_id: pool_integrity_check
    purpose: Verify all unpartnered entities are discoverable in the matching pool.
    triggers:
      - type: pool_event
        source: register_citizen / register_human / cooldown_expiry
        notes: Fires when entities enter or leave the pool.
      - type: scheduled
        source: mind doctor
        notes: Daily sweep to catch phantom entries or missing entities.
    frequency:
      expected_rate: per pool event + 1/day
      peak_rate: during onboarding waves
    risks:
      - Entities stuck in cooldown indefinitely due to missing expiry check.

  - flow_id: parity_check
    purpose: Verify COUNT(paired citizens) == COUNT(paired humans).
    triggers:
      - type: bond_event
        source: bond_lifecycle_manager
        notes: Parity is a derived invariant checked after every bond mutation.
    frequency:
      expected_rate: per bond event
    risks:
      - Single-sided bond formation (citizen paired but human not updated) would cause parity mismatch.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: cardinality_compliance
    flow_id: cardinality_check
    priority: critical
    rationale: A cardinality violation means the 1:1 guarantee is broken. This is the most severe possible failure of the pairing system.

  - name: pool_completeness
    flow_id: pool_integrity_check
    priority: high
    rationale: Invisible unpartnered entities cannot be matched, causing them to wait indefinitely through no fault of their own.

  - name: population_parity
    flow_id: parity_check
    priority: high
    rationale: Parity mismatch indicates a bug in bond formation or dissolution that will compound over time.

  - name: autonomy_progression
    flow_id: milestone_tracking
    priority: medium
    rationale: Citizens that never progress toward autonomy indicate either a system failure or a design flaw in the milestone framework.
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|---------------------------|
| O1: Species parity | cardinality_compliance, population_parity | These two indicators together verify the structural guarantee that makes Mind Protocol bilateral. |
| O2: Bilateral investment | pool_completeness | If entities are invisible in the pool, they cannot form the partnerships that create bilateral investment. |
| O3: Matching quality | pool_completeness | Matching quality depends on accurate pool data. Stale or missing entries degrade every match. |
| O4: Growth to autonomy | autonomy_progression | Citizens stuck at zero milestones for extended periods indicate the growth pathway is not working. |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: doctor_logs
  result:
    representation: float_0_1
    value: 1.0
    updated_at: 2026-03-13T00:00:00Z
    source: design_review
    notes: All invariants are designed but not yet testable — no code exists. Score reflects documentation completeness, not runtime health.
```

---

## DOCK TYPES (COMPLETE LIST)

- `graph_state` (input) — The graph containing citizen nodes, human nodes, bond links, and milestone moments.
- `bond_event_stream` (input) — Events emitted by the bond lifecycle manager after each mutation.
- `doctor_report` (output) — JSON payload surfacing any invariant violations for the pairing module.
- `health_banner` (output) — CLI summary showing pairing health score and any active violations.

---

## CHECKER INDEX

```yaml
checkers:
  - name: cardinality_checker
    purpose: Queries graph for any entity with more than one active bond.
    status: designed (not implemented)
    priority: critical

  - name: pool_completeness_checker
    purpose: Compares unpartnered entity count against matching pool query results.
    status: designed (not implemented)
    priority: high

  - name: parity_checker
    purpose: Compares COUNT(paired citizens) against COUNT(paired humans).
    status: designed (not implemented)
    priority: high

  - name: autonomy_staleness_checker
    purpose: Flags citizens paired for > 90 days with zero milestones.
    status: designed (not implemented)
    priority: medium
```

---

## HEALTH CHECKS

- Run `pairing_graph_constraints.verify_invariants()` to check all cardinality
  and parity constraints against the live graph. Any non-empty result is a
  critical violation.
- Query the matching pool and compare against all entities with
  `pairing_status: "unpartnered"`. Any discrepancy is a pool integrity violation.
- Query citizens with `pairing_status: "paired"` and `autonomy_level: 0.0` for
  more than 90 days. Flag for review — the pairing may be stuck or the milestone
  framework may be inaccessible.
- After every bond formation or dissolution, verify that the parity count holds.
  Log the counts to `doctor_logs` for trend analysis.

---

## HOW TO RUN

1. Once implemented: `mind doctor --scope citizens/pairing` to run all pairing
   health checks.
2. Manual verification: Execute the graph queries from the VALIDATION doc's
   manual checklist against the live graph.
3. Integration tests: `pytest tests/citizens/test_pairing_invariants.py` to
   exercise the full bond lifecycle and verify all invariants.

---

## KNOWN GAPS

- No code exists yet, so all checkers are in "designed" status.
- The autonomy staleness threshold (90 days) is arbitrary and may need
  calibration based on real pairing data.
- No alerting pipeline exists for critical cardinality violations — these should
  trigger immediate notifications, not just log entries.
- Race condition handling for concurrent bond formation is designed but not
  verified against the actual FalkorDB/Neo4j transaction semantics.

---

## MARKERS

<!-- @mind:todo Implement the cardinality_checker as the first health check when code is written — this is the most critical invariant. -->
<!-- @mind:todo Define alerting for critical violations (cardinality, parity) — should these halt bond operations until resolved? -->
<!-- @mind:todo Calibrate the autonomy staleness threshold once real pairing data exists. -->
