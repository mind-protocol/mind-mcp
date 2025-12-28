# Physics — Behaviors: What Should Happen

```
STATUS: CANONICAL
UPDATED: 2025-12-21
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Physics.md
THIS:           ./BEHAVIORS_Physics.md (you are here)
ALGORITHMS:
  - ./ALGORITHM_Physics.md      (Consolidated: energy, tick, canon, handlers, input, actions, QA, speed)
SCHEMA:         ../schema/SCHEMA_Moments.md
API:            ./API_Physics.md
VALIDATION:     ./VALIDATION_Physics.md
IMPLEMENTATION: ./IMPLEMENTATION_Physics.md
HEALTH:         ./HEALTH_Physics.md
SYNC:           ./SYNC_Physics.md
BEHAVIORS:      ./BEHAVIORS_Physics/BEHAVIORS_Physics_Overview.md
```

---

## SUMMARY

Physics behavior documentation now lives inside `BEHAVIORS_Physics/` to keep each file under 300 lines. The overview doc hosts the canonical table of B1–B12 entries and the early behaviors, while the extended doc continues from B7 and captures inputs, edge cases, anti-behaviors, and gaps.

## LINKS

- `BEHAVIORS_Physics/BEHAVIORS_Physics_Overview.md` — table, behavior anchors, and B1–B6 stories.
- `BEHAVIORS_Physics/BEHAVIORS_Physics_Behaviors_Advanced.md` — B7–B12, Cascades, inputs/outputs, anti-behaviors, gaps, and summaries.

## NOTABLE CHANGES SINCE PREVIOUS VERSION

- Behaviors are now split across an overview and advanced story doc so each remains concise while keeping the canonical descriptions intact.
