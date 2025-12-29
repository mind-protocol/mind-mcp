# Scene Memory System — Behavior (Legacy)

```
STATUS: DEPRECATED
CREATED: 2024-12-16
UPDATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
PATTERNS:        ./PATTERNS_Scene_Memory.md
THIS:            BEHAVIORS_Scene_Memory.md (you are here)
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

Legacy behaviors for the pre-Moment-Graph Scene Memory design. Use current
Moment Graph docs for canonical behavior definitions:
- `docs/runtime/moments/`
- `docs/runtime/moment-graph-mind/`
- `docs/physics/`

===============================================================================
## LEGACY BEHAVIOR SUMMARY
===============================================================================

### Inputs
- Narrator outputs structured scene data (when/where/present + narration lines).
- Player inputs (click/freeform/choice) provide named actions.

### Outputs
- Each narration line, hint, and player action becomes a Moment node.
- Narratives are created from mutations and link to source Moments (`FROM`).
- Characters present when narratives are created gain BELIEVES links.
- Transcript entries are appended for every displayed line/action.

### Queryable Behaviors (legacy expectations)
- Trace narrative sources via `FROM` links.
- Retrieve character speech via `SAID` links.
- Locate moments by place via `AT` links.

===============================================================================
## BEHAVIORS
===============================================================================

- Capture every narration line, hint, and player action as a Moment record so
  later systems can reconstruct what happened without reinterpreting text.
- Ensure narratives and beliefs are linked to their source Moments for
  traceability in debugging and story audits, even in the legacy flow.
- Append each displayed line to the transcript in order so the history is
  readable, append-only, and consistent with the scene playback order.

===============================================================================
## INPUTS / OUTPUTS
===============================================================================

**Inputs:**
- Structured scene payloads (who/where/when) and narration lines from the
  narrator, plus explicit player action selections or freeform inputs.
- Presence updates that indicate which characters are in the scene when a
  narrative is created, used to assign beliefs.

**Outputs:**
- Moment nodes and relationships (`FROM`, `SAID`, `AT`, `BELIEVES`) that encode
  the legacy memory graph, plus ordered transcript entries for UI playback.
- Metadata-enriched IDs for ambiguous names to preserve uniqueness across the
  legacy scene boundaries.

===============================================================================
## ANTI-BEHAVIORS
===============================================================================

- Do not overwrite or reorder transcript entries to "fix" story flow; the
  legacy system relies on append-only history for auditability.
- Do not create beliefs for characters who were not present when a narrative
  was created, even if they appear later in the same scene.
- Do not collapse multiple narration lines into a single Moment; each line is
  its own unit of memory for downstream linking.

===============================================================================
## MARKERS
===============================================================================

- Gap: The legacy design assumes scene containers, but the canonical Moment
  Graph uses global moment lifecycle states; reconcile any remaining docs.
- Idea: Provide a migration note that maps legacy `SAID`/`FROM` links to the
  modern moment graph query helpers for easier cross-referencing.
- Question: Should legacy name-expansion rules be fully retired once all
  moments are minted through the canonical processor?

===============================================================================
## LEGACY EDGE CASES
===============================================================================

- Duplicate short names in one scene require suffixing to keep IDs unique.
- Characters arriving mid-scene only gain beliefs for narratives created while
  present.

===============================================================================
## NEXT IN CHAIN
===============================================================================

→ **ALGORITHM_Scene_Memory.md** — Legacy processing outline.
