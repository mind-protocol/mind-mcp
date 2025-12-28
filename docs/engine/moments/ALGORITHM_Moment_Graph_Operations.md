# Moment Graph — Algorithm: Graph Operations

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Moments.md
BEHAVIORS:      ./BEHAVIORS_Moment_Lifecycle.md
VALIDATION:     ./VALIDATION_Moment_Graph_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Stub.md
TEST:           ./TEST_Moment_Graph_Coverage.md
SYNC:           ./SYNC_Moments.md
THIS:           ALGORITHM_Moment_Graph_Operations.md (you are here)
IMPL:           mind/moments/__init__.py
```

---

## OVERVIEW

The moment graph algorithm is not implemented yet. This document captures the
intended flow so future implementation aligns with the schema contract.

---

## TARGET FLOW

1. **Create moment node** with required properties (id, text, type, status).
2. **Attach contextual links** to place, speaker, and narrative sources.
3. **Promote status** from possible to active when readiness conditions are met.
4. **Record as spoken** once surfaced to the player or narrator.
5. **Archive or decay** moments based on weight/energy rules in the physics
   layer.

---

## DATA SOURCES

- `docs/schema/SCHEMA_Moments.md` defines fields and link types.
- Canon holder logic queries moment readiness and recording.
- Scene memory ingests moments as part of transcript persistence.
