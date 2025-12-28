# Engine — Validation: Membrane Modulation Invariants

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Membrane_Modulation.md
PATTERNS:        ./PATTERNS_Membrane_Scoping.md
BEHAVIORS:       ./BEHAVIORS_Membrane_Modulation.md
ALGORITHM:       ./ALGORITHM_Membrane_Modulation.md
THIS:            VALIDATION_Membrane_Modulation.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Membrane_Modulation.md
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL:            mind/physics/tick.py
IMPL:            mind/moment_graph/queries.py
IMPL:            mind/moment_graph/surface.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## INVARIANTS

These must ALWAYS be true:

### V1: Modulation Is Bounded

```
All modifier values are clamped to documented bounds.
```

**Checked by:** manual review (pending tests)

### V2: Modulation Is Idempotent

```
Same inputs produce the same ModulationFrame.
```

**Checked by:** manual review (pending tests)

### V3: No Canon Mutation

```
Membrane computation never writes to graph nodes/links/status.
```

**Checked by:** code inspection (pending tests)

### V4: No Magic Constants

```
Surfacing/traversal parameters are resolved via dynamic functions, not literals.
```

**Checked by:** code inspection (pending tests)

### V5: Per-Place Scope

```
Membrane state is keyed by place_id (or scene scope) and does not leak across places.
```

**Checked by:** manual review (pending tests)

---

## PROPERTIES

### P1: Neutral Default

```
FORALL missing inputs:
    compute_modulation_frame() == ModulationFrame.neutral()
```

**Verified by:** NOT YET VERIFIED — no tests

### P2: Scope Isolation

```
FORALL place_id A != B:
    frame(A) is computed from aggregates(A) only
```

**Verified by:** NOT YET VERIFIED — no tests

---

## ERROR CONDITIONS

### E1: Aggregates Missing

```
WHEN:    aggregates are unavailable
THEN:    return neutral frame
SYMPTOM: no modulation applied
```

**Verified by:** NOT YET VERIFIED — no tests

### E2: Scope Key Missing

```
WHEN:    place_id (or scene scope) is missing
THEN:    return neutral frame and skip caching
SYMPTOM: no cross-scene leakage
```

**Verified by:** NOT YET VERIFIED — no tests

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Bounded | frame_bounds_ok | ⚠ NOT YET VERIFIED |
| V2: Idempotent | frame_idempotent | ⚠ NOT YET VERIFIED |
| V3: No mutation | graph_unchanged | ⚠ NOT YET VERIFIED |
| V4: Dynamic functions | dynamic_params | ⚠ NOT YET VERIFIED |
| V5: Per-place scope | scope_isolated | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — spot-check clamps in membrane logic
[ ] V2 holds — recompute twice with same inputs
[ ] V3 holds — confirm no graph writes in membrane module
[ ] V5 holds — verify per-place keying and no shared state
```

### Automated

```bash
# No automated tests yet
mind validate
```

---

## MARKERS

<!-- @mind:todo Add unit tests for bounded modifiers and idempotency. -->
<!-- @mind:todo Add a check that rejects any graph writes from membrane code. -->
