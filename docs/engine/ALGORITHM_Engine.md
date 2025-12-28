# Engine — Algorithm: High-Level Flow

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Engine.md
BEHAVIORS:       ./BEHAVIORS_Engine.md
THIS:            ./ALGORITHM_Engine.md
VALIDATION:      ./VALIDATION_Engine.md
IMPLEMENTATION:  ./IMPLEMENTATION_Engine.md
HEALTH:          ./HEALTH_Engine.md
SYNC:            ./SYNC_Engine.md
```

---

## HIGH-LEVEL FLOW

1. Accept moments or events from ingestion paths.
2. Normalize inputs into the engine data model.
3. Apply physics and graph operations to update state.
4. Persist updated entities and emit outputs for downstream use.

Submodule-specific procedures live in their respective docs.
