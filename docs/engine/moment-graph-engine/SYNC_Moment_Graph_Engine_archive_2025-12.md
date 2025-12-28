# Archived: SYNC_Moment_Graph_Engine.md

Archived on: 2025-12-22
Original file: SYNC_Moment_Graph_Engine.md

---

## RECENT CHANGES

### 2025-12-21: Reorganized moment graph VALIDATION docs

- **What:** Moved the Player DMZ, Simultaneity/CONTRADICTS, and Void Tension validation stubs into dedicated subfolders under `validation/` so each path hosts only a single VALIDATION file.
- **Why:** Resolves DOC_DUPLICATION warnings while keeping a clear canonical location for each invariant document.
- **Files:** `docs/mind/moment-graph-mind/validation/player_dmz/VALIDATION_Player_DMZ.md`, `docs/mind/moment-graph-mind/validation/simultaneity_contradiction/VALIDATION_Simultaneity_Contradiction.md`, `docs/mind/moment-graph-mind/validation/void_tension/VALIDATION_Void_Tension.md`
- **Verification:** `mind validate` (fails: existing docs/connectome/health chains, naming, and broken CHAIN links unrelated to this change)

### 2025-12-20: Verified traversal helpers already implemented

- **What:** Re-checked `make_dormant` and `process_wait_triggers` in
  `mind/moment_graph/traversal.py` for the repair task.
- **Why:** Repair run `14-INCOMPLETE_IMPL-moment_graph-traversal` flagged these
  as incomplete.
- **Files:** `mind/moment_graph/traversal.py`
- **Result:** Implementations already present; no code changes required.

### 2025-12-20: Verified query helpers remain implemented

- **What:** Re-checked `get_dormant_moments` and `get_wait_triggers` in
  `mind/moment_graph/queries.py` for the repair task.
- **Why:** The INCOMPLETE_IMPL repair flagged these as empty.
- **Files:** `mind/moment_graph/queries.py`
- **Result:** Implementations already present; no code changes required.

### 2025-12-20: Restored MomentSurface implementation

- **What:** Implemented `MomentSurface` with flip/decay/scene-change helpers,
  plus `get_surface_stats` and `set_moment_weight`.
- **Why:** FastAPI startup was failing because `MomentSurface` was missing.
- **Files:** `mind/moment_graph/surface.py`
- **Result:** API module import succeeds; surface helpers match docs.

### 2025-12-20: Fix spoken location filter in get_current_view

- **What:** Rewrote the spoken-location filter to avoid `EXISTS` pattern errors in FalkorDB.
- **Why:** Query errors returned empty moment lists, causing UI to think no opening exists.
- **Files:** `mind/moment_graph/queries.py`
- **Result:** `get_current_view` returns moments without query failures.

### 2025-12-20: Add DOCS references for moment graph modules

- **What:** Added `DOCS:` references to the traversal and query modules.
- **Why:** Ensure `mind doctor` can link code back to this module's doc chain.
- **Files:** `mind/moment_graph/traversal.py`, `mind/moment_graph/queries.py`

### 2025-12-20: Added attention split + interrupt validation

- **What:** Moved attention split/interrupt validation to physics attention.
- **Why:** Keep physics-level invariants with attention patterns and behaviors.
- **Files:** `docs/physics/attention/VALIDATION_Attention_Split_And_Interrupts.md`

### 2025-12-21: Consolidated moment graph validation docs

- **What:** Relocated the Void Tension, Simultaneity/CONTRADICTS, and Player DMZ validation stubs into dedicated `validation/<topic>/` subfolders so `docs/mind/moment-graph-mind/` now hosts only the canonical traversal validation doc.
- **Why:** Keep a single VALIDATION doc per folder, which eliminates the DOC_DUPLICATION warning and makes the root chain the authoritative landing page for moment graph invariants.
- **Files:** `docs/mind/moment-graph-mind/validation/void_tension/VALIDATION_Void_Tension.md`, `docs/mind/moment-graph-mind/validation/simultaneity_contradiction/VALIDATION_Simultaneity_Contradiction.md`, `docs/mind/moment-graph-mind/validation/player_dmz/VALIDATION_Player_DMZ.md`
- **Verification:** `mind validate` (fails: connectome/health chain gaps already open)

### 2025-12-20: Added validation stubs (DMZ, Simultaneity, Void)

- **What:** Added validation stubs for Player DMZ, Simultaneity/CONTRADICTS, and Void Tension.
- **Why:** Reserve stable validation IDs and behavior mappings for upcoming behaviors.
- **Files:** `docs/mind/moment-graph-mind/validation/player_dmz/VALIDATION_Player_DMZ.md`, `docs/mind/moment-graph-mind/validation/simultaneity_contradiction/VALIDATION_Simultaneity_Contradiction.md`, `docs/mind/moment-graph-mind/validation/void_tension/VALIDATION_Void_Tension.md`

### 2025-12-19: Revalidated traversal helpers

- **What:** Checked `make_dormant` and `process_wait_triggers` in
  `mind/moment_graph/traversal.py`.
- **Why:** Repair task flagged the functions as incomplete.
- **Files:** `mind/moment_graph/traversal.py`
- **Result:** Implementations already present; no code changes required.

### 2025-12-19: Logged repair validation run

- **What:** Ran `mind validate` after confirming traversal helpers.
- **Why:** Protocol requires validation after changes.
- **Result:** Pre-existing doc-chain gaps remain in schema/tempo/world-builder.

### 2025-12-19: Documented moment graph engine module

- **What:** Added docs and mapped the module in `modules.yaml`.
- **Why:** Close the undocumented mind/moment_graph module gap.
- **Files:** `docs/mind/moment-graph-mind/`, `modules.yaml`,
  `mind/moment_graph/__init__.py`
- **Struggles/Insights:** Keeping this distinct from the schema-first
  `docs/mind/moments/` module avoids doc duplication.

### 2025-12-19: Clarified implementation references

- **What:** Removed class/method references that were misread as file paths.
- **Why:** Avoid false broken-link reports from health checks.
- **Files:** `docs/mind/moment-graph-mind/IMPLEMENTATION_Moment_Graph_Runtime_Layout.md`

### 2025-12-19: Verified moment graph query helpers

- **What:** Reviewed `get_dormant_moments`, `get_wait_triggers`, and
  pressure-attached moment queries in `mind/moment_graph/queries.py`.
- **Why:** Repair task flagged incomplete implementations.
- **Files:** `mind/moment_graph/queries.py`
- **Result:** Implementations already present; no code changes required.

---

