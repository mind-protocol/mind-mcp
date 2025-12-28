# Physics — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2024-12-18
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:       ../PATTERNS_Physics.md
BEHAVIORS:      ../BEHAVIORS_Physics.md
ALGORITHM:      ../ALGORITHM_Physics.md
VALIDATION:     ../VALIDATION_Physics.md
THIS:           ./IMPLEMENTATION_Physics.md (you are here)
IMPLEMENTATION: ./implementation/IMPLEMENTATION_Physics_Code_Structure.md
IMPLEMENTATION: ./implementation/IMPLEMENTATION_Physics_Architecture.md
IMPLEMENTATION: ./implementation/IMPLEMENTATION_Physics_Dataflow.md
IMPLEMENTATION: ./implementation/IMPLEMENTATION_Physics_Runtime.md
HEALTH:         ../HEALTH_Physics.md
SYNC:           ../SYNC_Physics.md
```

---

## OVERVIEW

Implementation documentation now delegates the detailed structure, schema, data flow, and runtime storytelling to individual files under `docs/physics/implementation/`. This keeps the top-level doc lightweight while still signalling where every major concern lives.

---

## DOCUMENT LAYOUT

- `implementation/IMPLEMENTATION_Physics_Code_Structure.md` — file inventory, responsibilities, and size thresholds.
- `implementation/IMPLEMENTATION_Physics_Architecture.md` — design patterns, schema overview, and entry points.
- `implementation/IMPLEMENTATION_Physics_Dataflow.md` — data flows, logic chains, and module dependencies.
- `implementation/IMPLEMENTATION_Physics_Runtime.md` — state management, runtime behavior, configuration, links, and runtime patterns.

---

## SIGNPOSTS

- `mind/physics/tick.py` remains the living world heart; refer to the code structure doc for line counts and responsibilities.
- Extraction candidates are tracked in the runtime doc, so follow that file when splitting graph query/write helpers.
- Bidirectional links table ensures the docs point back to the code paths that implement each behavior.
