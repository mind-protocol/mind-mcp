# Physics — Validation: Procedures

```
STATUS: CANONICAL
UPDATED: 2025-12-21
```

---

## CHAIN

```
PATTERNS:       ../PATTERNS_Physics.md
BEHAVIORS:      ../BEHAVIORS_Physics.md
ALGORITHMS:     ../ALGORITHM_Physics.md
VALIDATION:     ./VALIDATION_Physics_Procedures.md
IMPLEMENTATION: ../IMPLEMENTATION_Physics.md
HEALTH:         ../HEALTH_Physics.md
SYNC:           ../SYNC_Physics.md
```

---

## PROPERTIES

Physics behavior is deterministic for a fixed graph state, conserves energy
with explicit decay, and keeps canon ordering stable regardless of display
speed. These properties are validated by the invariants and benchmarks here.
We expect repeatable outputs for identical seeds and graph snapshots.

## ERROR CONDITIONS

Validation must flag missing ticks, invalid status enums, weight values
outside bounds, or illegal links (e.g., THEN to non-Moment nodes). Handler
scope violations and non-deterministic flips are critical errors.
These should fail validation immediately rather than log and continue.

## TEST COVERAGE

Physics validation relies on integration tests in `runtime/tests/` plus schema
checks in the graph-health suite. See `docs/physics/TEST_Physics.md` for
specific cases, coverage notes, and known gaps.
Manual verification notes supplement tests when dependencies are missing.

## VERIFICATION PROCEDURE

1. Run automated physics and schema tests from `runtime/tests/`.
2. Execute a short simulated scenario at 1x and 3x to compare canon chains.
3. Inspect graph queries for invariant violations (status, weights, links).
4. Review SYNC notes for open gaps before claiming completion.
5. Record deviations or skipped steps in `docs/physics/SYNC_Physics.md`.

## SYNC STATUS

Validation guidance is aligned with `docs/physics/SYNC_Physics.md`. Update the
SYNC file whenever invariants or verification steps change to avoid drift.
If SYNC is stale, treat the validation result as incomplete.

## MARKERS

- Which validation checks should be automated vs. manual when handler and
  canon runtime scaffolding is still pending?
- Should physics invariants include explicit checks for proximity gating once
  the World Runner integration is fully wired?
- How should we record acceptable nondeterminism when LLM-driven handlers add
  variability to moment text but not structure?

*"Verification is how we know the system behaves as designed."*
