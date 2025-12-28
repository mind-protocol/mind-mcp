# Moment Graph — Validation: Invariants

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Moments.md
BEHAVIORS:      ./BEHAVIORS_Moment_Lifecycle.md
ALGORITHM:      ./ALGORITHM_Moment_Graph_Operations.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Stub.md
TEST:           ./TEST_Moment_Graph_Coverage.md
SYNC:           ./SYNC_Moments.md
THIS:           VALIDATION_Moment_Graph_Invariants.md (you are here)
IMPL:           mind/moments/__init__.py
```

---

## INVARIANTS

### INV-1: Required Fields Exist

Each moment must include id, text, type, and status fields. The canonical
schema lives in `docs/schema/SCHEMA_Moments.md`.

### INV-2: Status Is Valid

Status must be one of the allowed lifecycle states (possible, active, spoken).

### INV-3: Links Resolve

Links to place, speaker, narrative, and other moment references must point to
existing nodes.

---

## VERIFICATION NOTES

These invariants are not enforced in this module yet. Validation currently
happens through schema checks and downstream systems (canon, memory, physics).
