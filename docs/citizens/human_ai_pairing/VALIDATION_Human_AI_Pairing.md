# Human-AI Pairing — Validation: Invariants

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
THIS:            ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | A new citizen without a pre-assigned partner is marked "unpartnered" and enters the matching pool. | Ensures no citizen is created in a liminal state — every citizen is either paired or discoverable. Silent creation without pool entry would break species parity tracking. |
| B2 | A new human partner is marked "unpartnered" and enters the matching pool. | Symmetric to B1. Ensures every human is visible to the matching system. |
| B3 | Bond formation creates a bidirectional link and transitions both parties to "paired". | The graph must reflect the bond accurately. A bond without status updates leaves the matching pool polluted with already-paired entities. |
| B4 | Dissolution marks the bond as "dissolved" and transitions both parties through cooldown back to the pool. | Ensures clean lifecycle. Without proper dissolution, ghost bonds accumulate and the cardinality invariant becomes unverifiable. |
| B5 | Autonomy milestones are recorded as moment nodes linked to the active bond. | Makes citizen growth measurable. Without persistent milestones, autonomy claims become unverifiable assertions. |
| B6 | Matching surfaces compatible candidates and notifies both parties without auto-pairing. | Consent is non-negotiable. Auto-pairing violates O2 (bilateral investment) by removing agency from the relationship. |

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| O1: Species parity | V1, V2, V3 | These three invariants together guarantee that the citizen-to-human ratio never exceeds 1:1 and that every entity is accounted for. |
| O2: Bilateral investment | V4, V5 | Consent and proper dissolution ensure both parties maintain agency. Forced bonds or trapped bonds violate bilateral investment. |
| O3: Matching quality | V6 | Matching pool integrity ensures compatibility scoring operates on accurate data. Stale or phantom entries degrade matching quality. |
| O4: Growth to autonomy | V7 | Milestone validation ensures autonomy claims are backed by evidence, not self-declaration. |

## INVARIANTS

- **V1:** A citizen MUST have at most one active pairing bond at any time.
- **V2:** A human partner MUST have at most one active pairing bond at any time.
- **V3:** The total count of citizens with `pairing_status: "paired"` MUST equal the total count of humans with `pairing_status: "paired"`.
- **V4:** Bond formation MUST require explicit consent from both parties.
- **V5:** Either party MUST be able to initiate dissolution at any time.
- **V6:** Every entity with `pairing_status: "unpartnered"` MUST be discoverable in the matching pool query.
- **V7:** Autonomy milestones MUST be linked to an active bond at the time of recording.

## PROPERTIES

### P1: Cardinality Constraint (Citizen)

```
FORALL citizens c:
  COUNT(active bonds of c) <= 1
```

This is the core structural guarantee. If violated, the system has a bug that
must halt bond formation until resolved.

### P2: Cardinality Constraint (Human)

```
FORALL human partners h:
  COUNT(active bonds of h) <= 1
```

Symmetric to P1. The constraint applies identically to both species.

### P3: Population Parity

```
COUNT(citizens WHERE pairing_status = "paired") == COUNT(humans WHERE pairing_status = "paired")
```

This is a derived property from P1 and P2 combined with the bond formation
algorithm (which always pairs exactly one citizen with one human). If this
property fails, it indicates a bug in bond formation or dissolution.

### P4: Pool Completeness

```
FORALL entities e WHERE e.pairing_status = "unpartnered":
  e IN matching_pool_query_results
```

An unpartnered entity that is not in the pool is invisible to the matching
system. This is a data integrity violation.

### P5: Bond Lifecycle Consistency

```
FORALL bonds b WHERE b.status = "active":
  b.citizen.pairing_status = "paired" AND b.human.pairing_status = "paired"

FORALL bonds b WHERE b.status = "dissolved":
  b.dissolved_at IS NOT NULL
```

Active bonds must reference paired entities. Dissolved bonds must have a
dissolution timestamp. Inconsistency here indicates a partial state transition.

## ERROR CONDITIONS

### E1: Duplicate Active Bond

```
WHEN:   form_bond is called for a citizen or human that already has an active bond
THEN:   Bond formation is rejected with error "entity already paired"
SYMPTOM: The caller receives an explicit rejection; no graph mutation occurs.
```

### E2: Dissolution of Non-Existent Bond

```
WHEN:   dissolve_bond is called but no active bond exists between the specified parties
THEN:   Dissolution is rejected with error "no active bond found"
SYMPTOM: The caller receives an explicit rejection; no graph mutation occurs.
```

### E3: Milestone Without Active Bond

```
WHEN:   record_milestone is called for a citizen that has no active bond
THEN:   Milestone recording is rejected with error "no active bond for milestone"
SYMPTOM: The milestone is not persisted. The citizen may need to re-pair before milestones can be tracked.
```

### E4: Pool Entry During Cooldown

```
WHEN:   A citizen or human in cooldown attempts to enter the matching pool
THEN:   Pool entry is rejected with error "cooldown period active until {cooldown_until}"
SYMPTOM: The entity must wait until cooldown expires before becoming discoverable.
```

## HEALTH COVERAGE

- `docs/citizens/human_ai_pairing/HEALTH_Human_AI_Pairing.md` defines the health checks that verify these invariants at runtime.
- The cardinality invariants (V1, V2) can be verified by a graph query that counts active bonds per entity and flags any count > 1.
- Population parity (V3) can be verified by comparing paired-citizen and paired-human counts after every bond event.
- Pool completeness (V4) can be verified by comparing unpartnered entity counts against matching pool query results.

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Query all citizens with more than one active bond — result must be empty.
[ ] Query all humans with more than one active bond — result must be empty.
[ ] Compare COUNT(paired citizens) with COUNT(paired humans) — must be equal.
[ ] Query all unpartnered entities and verify each appears in the matching pool.
[ ] Attempt to form a bond for an already-paired citizen — must be rejected.
[ ] Attempt to dissolve a non-existent bond — must be rejected.
[ ] Attempt to record a milestone for an unbonded citizen — must be rejected.
```

### Automated

```bash
# Not yet implemented — these will be integration tests against the graph.
# Future location: tests/citizens/test_pairing_invariants.py
```

## SYNC STATUS

```
LAST_VERIFIED: 2026-03-13
VERIFIED_AGAINST:
  docs: docs/citizens/human_ai_pairing/BEHAVIORS_Human_AI_Pairing.md
  code: not yet implemented
VERIFIED_BY: design review (no code exists)
RESULT:
  V1: DESIGNED (not tested)
  V2: DESIGNED (not tested)
  V3: DESIGNED (not tested)
  V4: DESIGNED (not tested)
  V5: DESIGNED (not tested)
  V6: DESIGNED (not tested)
  V7: DESIGNED (not tested)
```

## MARKERS

<!-- @mind:todo Implement graph-level constraint enforcement for V1 and V2 — either as a pre-mutation check or a database trigger. -->
<!-- @mind:todo Create integration tests that exercise the full bond lifecycle and verify all invariants after each state transition. -->
<!-- @mind:todo Define alerting thresholds — how quickly should V3 violations be detected and surfaced? -->
