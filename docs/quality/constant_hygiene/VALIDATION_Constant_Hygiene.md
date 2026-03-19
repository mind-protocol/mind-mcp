# Constant Hygiene — Validation

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
OBJECTIVES:      ./OBJECTIVES_Constant_Hygiene.md
PATTERNS:        ./PATTERNS_Constant_Hygiene.md
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
THIS:            VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md
```

---

## INVARIANTS

### V1: Detection Does Not Block Commits

**Why we care:** This is a nudge, not a gate. Blocking commits kills flow and creates resentment.

```
MUST:   The sense runs asynchronously in the maintenance loop, never in the commit path.
NEVER:  A commit is delayed, rejected, or modified by constant hygiene.
```

### V2: Safe Constants Are Never Flagged

**Why we care:** False positives on HTTP 200 or math.pi destroy trust in the signal.

```
MUST:   HTTP status codes, byte sizes, mathematical constants, version numbers,
        and comment lines are excluded before pattern matching.
NEVER:  A Concept node is created for a line matching only safe patterns.
```

### V3: Concepts Route to the Committing Citizen Only

**Why we care:** A constant in @pixel's commit should not appear in @nervo's awareness. Precision routing prevents noise.

```
MUST:   The OBSERVED_IN link connects the Concept to the citizen who authored the commit.
NEVER:  A constant hygiene Concept is broadcast to all citizens or to a fixed carrier.
```

### V4: The Sense Cannot Create New Failures

**Why we care:** Same as silence sentinel V2 — instrumentation must not break the system it monitors.

```
MUST:   If constant_hygiene.py fails to import, throws, or times out,
        the dispatcher maintenance loop continues normally.
NEVER:  A constant hygiene error propagates to the tick loop or crashes the dispatcher.
```

### V5: Scanned Commits Are Not Re-Processed

**Why we care:** Idempotency. Re-processing creates duplicate Concepts that inflate the citizen's WM with identical findings.

```
MUST:   Each commit Moment is marked constant_hygiene_scanned=true after processing.
NEVER:  The same commit generates multiple Concept nodes on separate cycles.
```

---

## PRIORITY

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Never blocks commits | CRITICAL |
| V2 | No false positives on safe constants | HIGH |
| V3 | Precision routing | HIGH |
| V4 | Can't break the dispatcher | CRITICAL |
| V5 | Idempotent scanning | MEDIUM |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
