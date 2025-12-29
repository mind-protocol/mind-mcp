# Moment Graph Engine — Validation: Simultaneity + CONTRADICTS (Stub)

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
THIS:            VALIDATION_Simultaneity_Contradiction.md
IMPL:            ../../../../../runtime/infrastructure/canon/canon_holder.py
                 ../../../../../runtime/moment_graph/surface.py

# Note: PATTERNS and BEHAVIORS files planned but not yet created
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | One spoken per beat window | Prevents multi-spoken ambiguity |
| B2 | Non-chosen candidates persist | Preserves contradictions as visible alternatives |

---

## INVARIANTS

### VSIM1: Exactly One Spoken Per Beat Window

```
Within a beat window, at most one candidate becomes completed.
```

### VSIM2: Alternatives Get CONTRADICTS Links

```
Non-chosen candidates are preserved and linked via CONTRADICTS.
```

### VSIM3: CONTRADICTS Visibility Aligns With Interrupts

```
CONTRADICTS visibility in player neighborhood triggers interrupt.
```

---

## PROPERTIES

### PSIM1: Deterministic Selection

```
Given identical candidates + context, selection is deterministic.
```

---

## ERROR CONDITIONS

### ESIM1: Double Spoken

```
WHEN:    two candidates become spoken in same beat window
THEN:    error
SYMPTOM: contradictory canon
```

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] One spoken per beat window
[ ] CONTRADICTS links exist for non-chosen candidates
```

### Automated

```bash
pytest tests/runtime/test_simultaneity_contradicts.py
```

---

## MARKERS

<!-- @mind:todo Define beat window boundaries (tick window or epoch id). -->
