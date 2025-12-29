# Scene Memory System — Sync

```
LAST_UPDATED: 2025-12-20
UPDATED_BY: Codex (repair agent)
STATUS: CANONICAL
```

===============================================================================
## ARCHITECTURE EVOLUTION
===============================================================================

**Original Design (2024-12):** Scene-based memory with Scene containers holding Moments

**Current Design (2025):** Moment Graph architecture
- Moments are first-class nodes with lifecycle states
- Weight-based surfacing replaces scene containers
- Click traversal targets <50ms response
- Transcript.json preserves full text history

===============================================================================
## IMPLEMENTATION STATUS
===============================================================================

| Component | Status | Location |
|-----------|--------|----------|
| Moment model | CANONICAL | `runtime/models/nodes.py:189` |
| MomentProcessor | CANONICAL | `runtime/infrastructure/memory/moment_processor.py` |
| Graph moment ops | CANONICAL | `runtime/physics/graph/graph_ops.py:792` |
| Moment lifecycle | CANONICAL | `runtime/physics/graph/graph_ops_moments.py` |
| Moment queries | CANONICAL | `runtime/physics/graph/graph_queries_moments.py` |
| Moment Graph engine | CANONICAL | `runtime/moment_graph/` |
| API endpoints | CANONICAL | `runtime/infrastructure/api/moments.py` |
| Tests | CANONICAL | `runtime/tests/test_moment*.py` (5 files) |

===============================================================================
## MATURITY
===============================================================================

STATUS: CANONICAL

What's canonical (v1):
- MomentProcessor flow and moment graph persistence are stable in production
  code paths and treated as the authoritative runtime behavior.

What's still being designed:
- None for the legacy Scene Memory wrapper; new design work lives in the
  Moment Graph docs and should not be staged here.

What's proposed (v2):
- Optional cleanup to consolidate legacy docs into a single pointer once the
  migration narrative no longer needs the full chain.

===============================================================================
## CURRENT STATE
===============================================================================

Scene Memory remains a legacy documentation wrapper around the canonical
Moment Graph implementation; the code and runtime behavior live in
`runtime/infrastructure/memory/` and graph ops, while this SYNC tracks
documentation alignment and repair history for drift checks.

===============================================================================
## IN PROGRESS
===============================================================================

- Verifying the remaining legacy references in the Scene Memory chain still
  accurately point to canonical Moment Graph docs, without reintroducing
  deprecated details or duplicate descriptions.

===============================================================================
## KNOWN ISSUES
===============================================================================

- The legacy doc chain can appear stale relative to active Moment Graph work,
  so readers must treat these files as historical context rather than primary
  design sources.

===============================================================================
## HANDOFF: FOR AGENTS
===============================================================================

Use VIEW_Implement_Write_Or_Modify_Code. Keep changes scoped to template drift
or legacy alignment only; canonical behavior updates belong in Moment Graph
docs and should be referenced here instead of duplicated.

===============================================================================
## HANDOFF: FOR HUMAN
===============================================================================

Scene Memory docs are maintained purely for legacy continuity. If you want
them retired or condensed, confirm whether we should archive the full chain
and replace it with a single pointer to Moment Graph documentation.

===============================================================================
## TODO
===============================================================================

<!-- @mind:todo Decide whether to fully archive legacy Scene Memory docs after migration -->
      sign-off, and document the decision in this SYNC.

===============================================================================
## CONSCIOUSNESS TRACE
===============================================================================

Keeping the Scene Memory chain aligned is mostly a hygiene task; the core
behavior is stable elsewhere, so the focus is preserving clarity without
drifting into duplicate specifications.

===============================================================================
## POINTERS
===============================================================================

- Canonical Moment Graph behavior and schemas live in `docs/runtime/moments/`.
- Runtime traversal and query mechanics live in `docs/runtime/moment-graph-mind/`.
- Graph physics interactions live in `docs/physics/`.

===============================================================================
## REPAIR LOG (2025-12-20)
===============================================================================

- Verified `runtime/infrastructure/memory/moment_processor.py` already implements
  `_write_transcript`, `last_moment_id`, `transcript_line_count`, and
  `get_moment_processor` for repair #16; no code changes required.
## OPEN QUESTIONS
===============================================================================

<!-- @mind:todo Should the deprecated legacy docs be removed entirely after a future -->
      migration sign-off?

===============================================================================

---

## ARCHIVE

Older content archived to: `SYNC_Scene_Memory_archive_2025-12.md`
