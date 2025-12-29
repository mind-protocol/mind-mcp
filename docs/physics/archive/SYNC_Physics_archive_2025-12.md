# Archived: SYNC_Physics.md

Archived on: 2025-12-19
Original file: SYNC_Physics.md

---

## MATURITY

STATUS: ARCHIVED. This file is a frozen snapshot from 2025-12-19 and should
not be treated as the live source of truth for the physics module.

## CURRENT STATE

This archive preserves a past physics SYNC state for traceability; it is not
updated and exists only for historical context.

## IN PROGRESS

No active work is tracked in this archive; any new or ongoing physics tasks
belong in the live SYNC file, not here.

## RECENT CHANGES

**2025-12-19: Repair 12 re-verified physics tick energy helpers**
- Confirmed `_flow_energy_to_narratives`, `_propagate_energy`, `_decay_energy`, and `_update_narrative_weights` in `runtime/physics/tick.py` already have implementations
- Repair task marked as stale; no runtime changes

**2025-12-19: Reconfirmed moment graph query helpers already implemented**
- Rechecked `get_dormant_moments`, `get_wait_triggers`, and `get_moments_attached_to_tension` in `runtime/moment_graph/queries.py`
- Repair task marked as stale; no runtime changes

**2025-12-19: Repair 13 verified physics tick energy helpers already implemented**
- Confirmed `_flow_energy_to_narratives`, `_propagate_energy`, `_decay_energy`, and `_update_narrative_weights` in `runtime/physics/tick.py` contain concrete logic
- Repair task marked as stale; no runtime changes

**2025-12-19: Verified moment graph traversal helpers already implemented**
- Confirmed `make_dormant` and `process_wait_triggers` in `runtime/moment_graph/traversal.py` already have concrete logic
- Repair task marked as stale; no runtime changes

**2025-12-19: Verified moment graph query helpers already implemented**
- Confirmed `get_dormant_moments`, `get_wait_triggers`, and `get_moments_attached_to_tension` in `runtime/moment_graph/queries.py` are implemented
- Repair task marked as stale; no runtime changes

**2025-12-19: Normalized moment graph query row handling**
- `runtime/moment_graph/queries.py` now normalizes dict/list query rows for dormant moments, wait triggers, and tension-attached moments
- Keeps traversal/reactivation logic stable across FalkorDB result formats

**2025-12-19: Moment API resolves playthrough graph names from configured directory**
- `runtime/infrastructure/api/moments.py` now reads `player.yaml` under the router's `playthroughs_dir` when resolving graph names
- Falls back to `get_playthrough_graph_name()` if no playthrough metadata is present

**2025-12-19: Consolidated physics algorithm docs**
- Merged physics algorithm content into `docs/physics/ALGORITHM_Physics.md`
- Removed standalone ALGORITHM_* docs to keep one canonical algorithm file
- Updated doc references to point at the consolidated algorithm

**2025-12-19: Split graph_ops.py monolith (1094 → 792 lines)**
- Extracted image generation helpers to `graph_ops_image.py` (163 lines)
  - `generate_node_image()`, `get_image_path()`, `_generate_node_image_async()`
  - Async image generation for characters, places, things
- Extracted event emitter to `graph_ops_events.py` (66 lines)
  - `add_mutation_listener()`, `remove_mutation_listener()`, `emit_event()`
  - Used by graph_ops_apply.py for mutation events
- Extracted types/exceptions to `graph_ops_types.py` (59 lines)
  - `WriteError`, `SimilarNode`, `ApplyResult`, `SIMILARITY_THRESHOLD`
- Removed `__main__` example block (98 lines of example code)
- Updated imports in graph_ops.py and graph_ops_apply.py
- Updated IMPLEMENTATION_Physics.md with new files in code structure and file responsibilities
- Updated modules.yaml with new internal files

**2025-12-19: Fixed BROKEN_IMPL_LINK validation errors in IMPLEMENTATION_Physics.md**
- Converted tree structure from Unicode box-drawing (├── │ └──) to ASCII (+-- | \--) to prevent file reference extraction from tree visualization
- Removed file extensions from tree structure names (clarity: they're all .py files, noted at end)
- Removed backticks from numeric config defaults (0.02, 0.8, etc.) that were being falsely detected as file references
- Removed backticks from code expressions (moment.weight, place.atmosphere, weight >= 0.8) that were false positives
- Updated planned module reference `runtime/handlers/base.py` to note it doesn't exist yet
- All 17 actual file references now validate correctly

**2025-12-19: Completed ApplyOperationsMixin extraction from graph_ops.py**
- `graph_ops_apply.py` (697 lines) contains ApplyOperationsMixin class with:
  - `apply()` method for mutation file/dict processing
  - `_get_existing_node_ids()`, `_node_has_links()`, `_validate_link_targets()`, `_link_id()` helpers
  - All `_extract_*` methods for node and link argument extraction
  - `_apply_node_update()`, `_apply_tension_update()` update helpers
- `graph_ops.py` reduced from 2252 lines to 1611 lines
- `GraphOps` now inherits from both `MomentOperationsMixin` and `ApplyOperationsMixin`
- Updated IMPLEMENTATION_Physics.md with line counts
- Updated modules.yaml with new internal file and updated notes

**2025-12-19: Extracted SearchQueryMixin from graph_queries.py**
- Created new file `graph_queries_search.py` (285 lines)
- Extracted search methods: `search()`, `_to_markdown()`, `_cosine_similarity()`, `_find_similar_by_embedding()`, `_get_connected_cluster()`
- `graph_queries.py` reduced from ~1132 lines to 892 lines
- Added `SearchQueryMixin` to `GraphQueries` class inheritance alongside `MomentQueryMixin`
- Updated IMPLEMENTATION_Physics.md with new file in code structure
- Updated modules.yaml with new file and corrected line counts

**2024-12-19: Fixed broken implementation links**
- Updated IMPLEMENTATION_Physics.md to clearly separate existing vs planned code
- Added full `runtime/` prefix to all file paths for clarity
- Added missing file `graph_ops_apply.py` to code structure
- Updated all test file references to match actual test files
- Separated "Existing" and "Planned" tables in File Responsibilities, Entry Points, Module Dependencies, and Bidirectional Links sections
- Updated CHAIN section to distinguish existing vs planned implementation paths

---

## KNOWN ISSUES

No archive-specific issues are tracked here; any active physics concerns are
documented in the current physics SYNC file instead. This snapshot should not
be used to infer active defects or blocker status.

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement_Write_Or_Modify_Code

**Where I stopped:** This archive is a closed snapshot; no active work
continues here, and updates should be logged in the live SYNC file.

**What you need to understand:**
The entries above are historical repair notes and should not be treated as
current TODOs without verifying the latest physics SYNC status.

**Watch out for:**
Avoid editing archive entries to reflect new work; record new work in
`docs/physics/SYNC_Physics.md` to prevent historical drift.

**Open questions I had:**
None recorded in this snapshot; consult the current SYNC for live questions.

## HANDOFF: FOR HUMAN

**Executive summary:**
This archive captures the physics doc state from 2025-12-19, including
verification notes and consolidation history. It is retained for
traceability only.

**Decisions made:**
Archived historical repair context rather than deleting it, preserving an
audit trail for physics documentation changes.

**Needs your input:**
None for this archive; any new physics decisions should be recorded in the
current SYNC file.

## TODO

### Doc/Impl Drift

This archive snapshot does not track active drift items. Use
`docs/physics/SYNC_Physics.md` for live doc/implementation alignment tasks.

### Tests to Run

No tests are associated with this archive record; see the current SYNC for
any pending physics test runs.

### Immediate

<!-- @mind:todo Review the current physics SYNC before acting on any archived notes. -->

### Later

<!-- @mind:proposition If archive length grows, split into smaller dated snapshots. -->

## CONSCIOUSNESS TRACE

This archive is intended as a stable memory of a completed repair pass. The
mental state at the time was focused on documentation hygiene and preserving
traceability without altering runtime behavior.

## POINTERS

| What | Where |
| --- | --- |
| Current physics SYNC | `docs/physics/SYNC_Physics.md` |
| Physics algorithm doc | `docs/physics/ALGORITHM_Physics.md` |

## Agent Observations

### Remarks
- Moments API now resolves graph names from the router-configured `playthroughs_dir` before falling back to `get_playthrough_graph_name()`.
- Moment graph query helpers now normalize FalkorDB dict/list row shapes for traversal workflows.
- Moment graph traversal helpers in `runtime/moment_graph/traversal.py` were already implemented; repair task was stale.
- Physics tick energy helper implementations in `runtime/physics/tick.py` were already present; repair task was stale.
- Reverified physics tick energy helper implementations for repair 12; no code changes needed.

### Suggestions

### Propositions
  - Moment decay by status: possible (0.02), active (0.01), spoken (0.03), dormant (0.005)
  - Weight decays only after 100 ticks without reinforcement (very slow: 0.001)
- SCHEMA updated with weight+energy fields on Character, Narrative, Moment
- TENSION node removed — pressure emerges from contradictions, deadlines, debts, secrets, oaths
- All docs unified to new model (Physics, Handlers, Behaviors, Tests, Implementation)
- ALGORITHM_Physics.md updated: character_pumping() no longer takes focus param
- INFRASTRUCTURE.md consolidated into IMPLEMENTATION_Physics.md (Runtime Patterns section)
  - Scene as query, time passage, character movement, backstory generation
- Implementation is next phase: create handlers/, canon/, physics/energy.py

---

*"There is no scene. There is only the graph."*


---

# Archived: SYNC_Physics.md

Archived on: 2025-12-20
Original file: SYNC_Physics.md

---

## RECENT CHANGES

### 2025-12-19: Expanded physics implementation design patterns

- **What:** Added an anti-pattern note about hidden writes in query helpers to keep
  the DESIGN PATTERNS section explicit about read/write separation.
- **Why:** Keep the implementation doc aligned with template expectations and clarity.
- **Files:** `docs/physics/IMPLEMENTATION_Physics.md`

### 2025-12-19: Updated physics patterns template sections

- **What:** Filled the missing PATTERNS sections (problem, pattern,
  principles, dependencies, inspirations, scope, gaps) and aligned the core
  principle text to the template guidance.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the physics patterns doc.
- **Files:** `docs/physics/PATTERNS_Physics.md`

### 2025-12-19: Filled validation template sections

- **What:** Expanded validation sections (invariants, properties, error
  conditions, test coverage, verification procedure, sync status) in
  `docs/physics/VALIDATION_Physics.md` to meet template guidance and add
  clearer verification notes.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the physics validation doc.
- **Files:** `docs/physics/VALIDATION_Physics.md`

### 2025-12-19: Verified physics patterns template coverage

- **What:** Rechecked `docs/physics/PATTERNS_Physics.md` to confirm the
  required template sections are present and sufficiently detailed.
- **Why:** Close the active DOC_TEMPLATE_DRIFT report for the patterns doc.
- **Files:** `docs/physics/PATTERNS_Physics.md`

### 2025-12-19: Added physics implementation design patterns

- **What:** Added the DESIGN PATTERNS section (architecture, code patterns, anti-patterns, boundaries) to `docs/physics/IMPLEMENTATION_Physics.md`.
- **Why:** Resolve the missing template section and align the implementation doc with the standard structure.
- **Files:** `docs/physics/IMPLEMENTATION_Physics.md`

### 2025-12-19: Completed archive SYNC template sections

- **What:** Expanded the archived physics SYNC with full handoff, TODO,
  consciousness trace, and pointers sections to satisfy the sync template.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the archive snapshot while keeping
  the live physics SYNC unchanged.
- **Files:** `docs/physics/SYNC_Physics_archive_2025-12.md`

### 2025-12-19: Expanded physics patterns template sections

- **What:** Added missing PATTERNS template sections (problem, pattern,
  principles, dependencies, inspirations, scope, gaps) and expanded the core
  principle text to meet template length guidance.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for `docs/physics/PATTERNS_Physics.md`.
- **Files:** `docs/physics/PATTERNS_Physics.md`

### 2025-12-19: Added implementation design patterns section

- **What:** Added the missing DESIGN PATTERNS section to
  `docs/physics/IMPLEMENTATION_Physics.md` and expanded it to template length.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the physics implementation doc.
- **Files:** `docs/physics/IMPLEMENTATION_Physics.md`

### 2025-12-19: Completed physics algorithm template compliance

- **What:** Added missing template sections (overview, data structures,
  algorithm summary, decisions, data flow, complexity, helpers, interactions,
  gaps) to `docs/physics/ALGORITHM_Physics.md`.
- **Why:** Resolve doc-template drift for the physics algorithm doc.
- **Files:** `docs/physics/ALGORITHM_Physics.md`

### 2025-12-19: Expanded physics test template sections

- **What:** Added missing test strategy, coverage, execution guidance, and gap
  tracking sections to `docs/physics/TEST_Physics.md`.
- **Why:** Resolve doc-template drift for physics test documentation.
- **Files:** `docs/physics/TEST_Physics.md`

### 2025-12-19: Restored missing SYNC template sections

- **What:** Added required template sections (maturity, current state, in
  progress, known issues, handoffs, todo, consciousness trace, pointers) and
  expanded short entries to meet length guidance.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the physics SYNC file.
- **Files:** `docs/physics/SYNC_Physics.md`

### 2025-12-19: Completed physics behaviors template sections

- **What:** Filled BEHAVIORS, INPUTS/OUTPUTS, EDGE CASES, ANTI-BEHAVIORS, and
  GAPS/IDEAS/QUESTIONS sections in `docs/physics/BEHAVIORS_Physics.md`.
- **Why:** Resolve doc-template drift for the physics behaviors spec.
- **Files:** `docs/physics/BEHAVIORS_Physics.md`

### 2025-12-19: Completed physics algorithm template sections

- **What:** Added missing template sections (overview, data structures, primary
  algorithm, decisions, data flow, complexity, helpers, interactions, gaps) in
  `docs/physics/ALGORITHM_Physics.md`.
- **Why:** Resolve doc-template drift for the physics algorithm document.
- **Files:** `docs/physics/ALGORITHM_Physics.md`

### 2025-12-19: Expanded physics validation template sections

- **What:** Added the required validation sections (invariants, properties,
  error conditions, test coverage, verification procedure, sync status, gaps)
  and expanded them to meet template length guidance in
  `docs/physics/VALIDATION_Physics.md`.
- **Why:** Resolve DOC_TEMPLATE_DRIFT for the physics validation doc.
- **Files:** `docs/physics/VALIDATION_Physics.md`

### 2025-12-19: Completed physics tick energy flow for repair 13

- **What:** Normalized belief-based injection and enforced zero-sum propagation with supersedes drain, clamping to `MIN_WEIGHT`.
- **Why:** Close the incomplete-impl gap for physics tick energy flow and align with the documented algorithm.
- **Files:** `runtime/physics/tick.py:300`, `runtime/physics/tick.py:342`, `docs/physics/IMPLEMENTATION_Physics.md`

### 2025-12-19: Documented physics module mapping

- **What:** Added `modules.yaml` entry for `runtime/physics/**` and linked `runtime/physics/tick.py` to the physics doc chain.
- **Why:** Close the undocumented module gap and make `mind context` resolve physics docs.
- **Files:** `modules.yaml`, `runtime/physics/tick.py`


## Agent Observations

### Remarks
- `mind validate` still reports the pre-existing missing VIEW and doc-chain gaps outside physics (schema/network/product/storms).
- Verified `docs/physics/BEHAVIORS_Physics.md` already includes the required template sections for repair #16.
- `pytest mind/tests/test_behaviors.py -q` failed: missing `pytest_xprocess` (anchorpy plugin import).
- `mind validate` still reports pre-existing doc gaps and broken CHAIN links (schema/tempo/world-builder).
- Filled the missing algorithm template sections in `docs/physics/ALGORITHM_Physics.md` for repair #16.
- Expanded `docs/physics/VALIDATION_Physics.md` to include all required validation template sections for repair #16.
- Refined validation guidance notes (invariants/procedure/sync status) for repair #16.
- Expanded `docs/physics/PATTERNS_Physics.md` with the missing template sections for repair #16.
- Reverified `docs/physics/PATTERNS_Physics.md` template coverage for repair #16.
- Logged the physics patterns template update in RECENT CHANGES for this repair.

### Suggestions
<!-- @mind:todo Install `pytest_xprocess` (or disable the anchorpy pytest plugin) to run the physics behavior tests. -->

### Propositions
- None.

---


---



---

# Archived: SYNC_Physics.md

Archived on: 2025-12-20
Original file: SYNC_Physics.md

---

## CHAIN



```

THIS:            SYNC_Physics.md (you are here)

PATTERNS:        ../PATTERNS_Physics.md

BEHAVIORS:       ../BEHAVIORS_Physics.md

ALGORITHMS:      ./ALGORITHM_Physics.md (consolidated: energy, tick, canon, handlers, input, actions, QA, speed)

SCHEMA:          ../schema/SCHEMA_Moments.md

API:             ./API_Physics.md

VALIDATION:      ../VALIDATION_Physics.md

IMPLEMENTATION:  ./IMPLEMENTATION_Physics.md (+ Runtime Patterns from INFRASTRUCTURE.md)

HEALTH:          ../HEALTH_Physics.md

IMPL (existing): ../../runtime/physics/tick.py, ../../runtime/physics/graph/

IMPL (planned):  ../../mind/handlers/, ../../mind/canon/, ../../runtime/infrastructure/orchestration/speed.py

```

---
