# Scene Memory System — Pattern (Legacy)

```
STATUS: DEPRECATED
CREATED: 2024-12-16
UPDATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
THIS:            PATTERNS_Scene_Memory.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Scene_Memory.md
ALGORITHM:       ./ALGORITHM_Scene_Memory.md
VALIDATION:      ./VALIDATION_Scene_Memory.md
IMPLEMENTATION:  ./IMPLEMENTATION_Scene_Memory.md
TEST:            ./TEST_Scene_Memory.md
SYNC:            ./SYNC_Scene_Memory.md
ARCHIVE:         ./archive/SYNC_archive_2024-12.md
```

===============================================================================
## STATUS
===============================================================================

The original Scene Memory concept evolved into the **Moment Graph** system.
This document is kept as a legacy reference only.

**Canonical docs:**
- `docs/runtime/moments/`
- `docs/runtime/moment-graph-mind/`
- `docs/physics/`

===============================================================================
## PRINCIPLES
===============================================================================

- Preserve a single source of truth: capture narration and actions as moments
  so later systems can link beliefs and narratives without hidden rewrites.
- Favor append-only history: write transcript entries in order so debugging and
  provenance checks never depend on reconstructing past output.
- Keep identity stable: expand short names with scene context to avoid global
  collisions in downstream graph queries and export pipelines.

===============================================================================
## DEPENDENCIES
===============================================================================

- Moment Graph docs define the canonical model, lifecycle, and query patterns
  that supersede the legacy Scene Memory container assumptions in this file.
- Transcript persistence relies on engine infrastructure that writes readable,
  append-only logs for audit trails and replay debugging.
- Graph ops and schema models provide the APIs that the legacy pattern assumed
  for creating, linking, and reading Moment nodes.

===============================================================================
## INSPIRATIONS
===============================================================================

- Event-sourcing style logs where every narrative line is immutable and can be
  replayed for debugging, analytics, or retrospective story reconstruction.
- Memory systems that treat observations as primary facts and derive beliefs as
  secondary projections tied back to explicit sources.

===============================================================================
## SCOPE
===============================================================================

- This legacy pattern only documents the historical Scene Memory design and
  its transition into the Moment Graph system; it is not the canonical spec.
- In scope: high-level assumptions about moments, transcripts, and name
  expansion that still explain why the current system looks the way it does.
- Out of scope: new behavior, updated algorithms, or implementation details,
  which are documented in the Moment Graph and physics docs.

===============================================================================
## LEGACY PATTERN SUMMARY
===============================================================================

- **Moments are primary.** Every narration line, hint, and player action becomes
  a Moment node.
- **Narratives cite sources.** Narratives link to their originating Moments via
  `FROM` relationships.
- **Beliefs are automatic.** Characters present when a narrative is created gain
  witnessed beliefs without explicit narrator steps.
- **Name expansion.** Short names are expanded with scene context to ensure
  global uniqueness.
- **Transcript persistence.** All displayed text is appended to a transcript for
  traceability.

===============================================================================
## LEGACY LIMITS
===============================================================================

- The legacy design described Scene containers; the current system is fully
  Moment Graph based and does not rely on Scene containers for meaning.
- Detailed algorithms and examples were moved to the archive to reduce size.

===============================================================================
## NEXT IN CHAIN
===============================================================================

→ **BEHAVIORS_Scene_Memory.md** — Legacy behaviors summary.
