# Scene Memory System — Legacy Archive (2024-12)

```
STATUS: ARCHIVED
CREATED: 2024-12-16
ARCHIVED: 2025-12-19
```

===============================================================================
## PURPOSE
===============================================================================

This archive captures a concise summary of the original 2024-12 Scene Memory
spec. The full narrative and exhaustive examples were removed from the active
module to keep documentation size within project limits. Use this file when
tracking legacy intent or reading historical context.

===============================================================================
## LEGACY SUMMARY
===============================================================================

### Core Shape
- Every narration element, clickable hint, and player action becomes a Moment.
- Narratives link back to Moments via `FROM` relationships.
- Characters present when a narrative is created gain automatic beliefs.
- Names are expanded with scene context to avoid collisions.
- Transcript storage preserves the complete text stream.

### Legacy Data Relationships
- `Moment -[AT]-> Place`
- `Character -[SAID]-> Moment`
- `Narrative -[FROM]-> Moment`
- `Scene -[CONTAINS]-> Moment` (legacy-only container concept)

### Legacy Processing Steps (high level)
1. Expand short names using `{place}_{day}_{time}` prefixing.
2. Create Moment nodes for narration lines, hints, and player actions.
3. Store Scene node and connect it to present characters and moments.
4. Create Narrative nodes and link them to source Moments.
5. Generate witnessed beliefs for characters present in the scene.

===============================================================================
## CANONICAL REFERENCES
===============================================================================

The active system is the Moment Graph architecture. For current behavior and
implementation, use:
- `docs/runtime/moments/`
- `docs/runtime/moment-graph-mind/`
- `docs/physics/` (moment graph wiring and graph ops)

===============================================================================
## NOTE ON REMOVALS
===============================================================================

Detailed legacy algorithm walkthroughs, query examples, and extensive test
specifications were removed from the active module to reduce duplication and
keep the scene-memory docs aligned with the current Moment Graph system.
