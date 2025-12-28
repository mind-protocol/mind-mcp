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

- `mind/`
- `mind/models/`
- `mind/moments/`
- `mind/moment_graph/`
- `mind/physics/`
- `mind/infrastructure/`

Submodule chains are documented in:

- `docs/mind/models/`
- `docs/mind/moments/`
- `docs/mind/moment-graph-mind/`
- `docs/physics/`
- `docs/infrastructure/`

---

## NOTES

Engine-level docs cover shared ownership and boundaries; submodules supply detailed behavior and implementation.
