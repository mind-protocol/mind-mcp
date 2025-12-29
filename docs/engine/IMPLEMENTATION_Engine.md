# Engine — Implementation: Code Mapping

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
VALIDATION:      ./VALIDATION_Engine.md
THIS:            ./IMPLEMENTATION_Engine.md
HEALTH:          ./HEALTH_Engine.md
SYNC:            ./SYNC_Engine.md
```

---

## CODE LOCATIONS

Primary code paths:

- `runtime/`
- `runtime/models/`
- `runtime/moments/`
- `runtime/moment_graph/`
- `runtime/physics/`
- `runtime/infrastructure/`

Submodule chains are documented in:

- `docs/mind/models/`
- `docs/runtime/moments/`
- `docs/runtime/moment-graph-mind/`
- `docs/physics/`
- `docs/infrastructure/`

---

## NOTES

Engine-level docs cover shared ownership and boundaries; submodules supply detailed behavior and implementation.
