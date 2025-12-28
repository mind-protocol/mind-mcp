# Scene Memory System — Validation (Legacy)

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
BEHAVIORS:       ./BEHAVIORS_Scene_Memory.md
ALGORITHM:       ./ALGORITHM_Scene_Memory.md
THIS:            VALIDATION_Scene_Memory.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Scene_Memory.md
TEST:            ./TEST_Scene_Memory.md
SYNC:            ./SYNC_Scene_Memory.md
ARCHIVE:         ./archive/SYNC_archive_2024-12.md
```

===============================================================================
## STATUS
===============================================================================

Legacy validation expectations for the pre-Moment-Graph Scene Memory design.
Current invariants and tests live under:
- `docs/mind/moments/`
- `docs/mind/moment-graph-mind/`
- `docs/physics/`

===============================================================================
## LEGACY INVARIANTS (SUMMARY)
===============================================================================

- Expanded Moment names are unique within and across scenes.
- Narratives always have at least one `FROM` link to a Moment.
- Dialogue Moments always have a `SAID` link from a Character.
- All Moments link to a Place via `AT`.
- All characters present during narrative creation have beliefs.
- Embeddings are generated for text longer than the threshold.

===============================================================================
## PROPERTIES
===============================================================================

- Legacy Scene Memory output must remain deterministic for the same input
  transcript, so replaying the same lines yields the same Moment IDs and links.
- Moment creation should be append-only; no earlier transcript entry is mutated
  or deleted once recorded, preserving auditability and replay debugging.
- Scene-level aggregation should not alter Moment contents; it only groups
  Moments for retrieval and does not change the source text payloads.

===============================================================================
## ERROR CONDITIONS
===============================================================================

- If a narration line cannot be resolved to a Place, the legacy invariant
  `AT` link creation fails and the Scene container is considered invalid.
- If a speaker cannot be resolved to a Character node, the expected `SAID`
  link is missing and the Moment is rejected or flagged for repair.
- If name expansion produces a collision with an existing Moment, the legacy
  rules demand a deterministic disambiguation rather than silent overwrite.

===============================================================================
## LEGACY TEST NOTES
===============================================================================

- Name expansion and collision handling.
- Moment creation for narration, dialogue, hints, and player actions.
- Scene linking and belief creation integrity.

Detailed legacy test sketches were moved to the archive.

===============================================================================
## TEST COVERAGE
===============================================================================

- Legacy tests validate that link expectations (`FROM`, `SAID`, `AT`) are
  created for each Moment type and that missing links are surfaced quickly.
- Coverage also checks that belief creation occurs for all present characters,
  even when multiple narratives are recorded in the same scene.
- Replay-style tests ensure transcript append-only behavior and stable ordering
  for downstream provenance tooling and audit logs.

===============================================================================
## VERIFICATION PROCEDURE
===============================================================================

1. Review Moment processing output for a known transcript fixture.
2. Confirm all required links (`FROM`, `SAID`, `AT`) exist and resolve to nodes.
3. Verify name expansion outputs are unique and consistent across replays.
4. Compare transcript logs to ensure append-only ordering is preserved.
5. Cross-check with canonical Moment Graph validation docs for gaps.

===============================================================================
## MARKERS
===============================================================================

- Which legacy invariants still need explicit regression tests once the
  Moment Graph validation suite fully supersedes this file?
- Should the legacy verification steps be archived entirely after the
  Moment Graph test suite is declared canonical?
- Are there any Scene-level behaviors still relied upon by external tooling?

===============================================================================
## NEXT IN CHAIN
===============================================================================

→ **IMPLEMENTATION_Scene_Memory.md** — Current implementation notes.
