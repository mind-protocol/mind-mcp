# OBJECTIVES — Schema

```
STATUS: STABLE
CREATED: 2025-12-23
VERIFIED: 2025-12-23 against schema.yaml v1.0
```

## PRIMARY OBJECTIVES (ranked)

1. **Project-agnostic foundation** — The schema works for any project without modification to core types. Projects extend via free-string `type`, not schema changes.

2. **Minimal surface area** — Fewer fields = easier reasoning. Only ~15 essential fields on NodeBase/LinkBase. Game-specific attributes belong in project schemas, not here.

3. **Physics-ready structure** — Every node/link has `weight` and `energy` fields that the physics engine operates on. Schema is designed for graph traversal and energy propagation.

4. **Polarity-enabled links** — Links carry `polarity` [-1, +1] to enable contradiction pressure mechanics. Narratives that contradict create tension.

5. **Extensible through layering** — Base schema in `docs/schema/schema.yaml` defines structure. Projects overlay constraints via `runtime/graph/health/schema.yaml`.

## NON-OBJECTIVES

- **Domain-specific attributes** — Skills, face, voice, atmosphere do NOT belong in base schema. These are project extensions.
- **Computed fields** — Trust, relationship strength, etc. are derived from graph queries, not stored in schema.
- **UI/rendering hints** — View layer concerns, not schema concerns.
- **Historical provenance** — Use links or separate tracking, not node fields.
- **Backwards compatibility** — When schema changes, fix implementations. No cruft accumulation.

## TRADEOFFS (canonical decisions)

- When **simplicity** conflicts with **expressiveness**, choose simplicity. Add fields only when three+ projects need them.
- We accept **loose typing on `type` field** to preserve project flexibility. Validation happens in project-specific overlays.
- We accept **no versioning in node structure** to keep nodes lean. History is tracked via `moment` nodes and `then` links.
- When **physics fields** conflict with **domain semantics**, physics wins. `weight` and `energy` have fixed meanings.

## SUCCESS SIGNALS (observable)

- A new project can model its domain using only `actor|space|thing|narrative|moment` and free `type` strings.
- `check_health.py` validates any graph against schema invariants without modification.
- Physics mechanisms operate on any schema-compliant graph.
- Any project can share the same base schema with zero conflicts.

---

## MARKERS

<!-- @mind:resolved MODELS_ALIGNMENT: RESOLVED 2025-12-23 — Models now use generic schema types (Actor, Space, Thing). All game-specific "Character", "Place" references removed. Pydantic models match base schema. -->

<!-- @mind:resolved CONTEXT_CLEANUP: RESOLVED 2025-12-23 — Removed game-specific Blood Ledger references from mind/ files. Schema is now project-agnostic. -->
