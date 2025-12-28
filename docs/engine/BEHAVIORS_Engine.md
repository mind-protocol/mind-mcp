# Engine — Behaviors: Runtime Effects

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Engine.md
THIS:            ./BEHAVIORS_Engine.md
ALGORITHM:       ./ALGORITHM_Engine.md
VALIDATION:      ./VALIDATION_Engine.md
IMPLEMENTATION:  ./IMPLEMENTATION_Engine.md
HEALTH:          ./HEALTH_Engine.md
SYNC:            ./SYNC_Engine.md
```

---

## BEHAVIORS

### B1: Runtime Coordination

```
GIVEN:  Engine subsystems are invoked
WHEN:   Moments, models, and physics routines run
THEN:   State updates flow through the shared engine boundaries
AND:    Submodules remain consistent with the shared data model contracts
```

### B2: Submodule Delegation

```
GIVEN:  A subsystem has its own documentation chain
WHEN:   Engine-level flows touch that subsystem
THEN:   Detailed behavior is delegated to the subsystem docs
```
