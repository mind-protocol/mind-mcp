# Engine — Validation: Invariants

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Engine.md
BEHAVIORS:       ./BEHAVIORS_Engine.md
ALGORITHM:       ./ALGORITHM_Engine.md
THIS:            ./VALIDATION_Engine.md
IMPLEMENTATION:  ./IMPLEMENTATION_Engine.md
HEALTH:          ./HEALTH_Engine.md
SYNC:            ./SYNC_Engine.md
```

---

## INVARIANTS

- Engine-owned state updates must preserve model invariants defined by the models module.
- Engine routing cannot bypass subsystem boundaries without an explicit, documented reason.
- Engine runtime paths must remain observable through health checks and SYNC records.
