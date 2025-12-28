# Physics — Sync History (2025-12)

This archive captures the detailed recent changes that were previously embedded in `docs/physics/SYNC_Physics.md`.

## RECENT CHANGES

### 2025-12-20: Attention split + interrupt patterns added

- **What:** Added attention split and interrupt-by-focus patterns plus behaviors under `docs/physics/attention/`.
- **Why:** Lock interrupt semantics as focus reconfiguration rather than heuristics.
- **Impact:** Documentation only; no runtime changes.

### 2025-12-20: Attention split validation added

- **What:** Added `VALIDATION_Attention_Split_And_Interrupts.md` under `docs/physics/attention/`.
- **Why:** Centralize attention/interrupt invariants with their patterns.
- **Impact:** Documentation only; no runtime changes.

### 2025-12-20: Physics mechanisms doc added

- **What:** Added `ALGORITHM_Physics_Mechanisms.md` to enumerate concrete mechanisms with code references.
- **Why:** Provide a precise, function-level map of energy/pressure/surfacing mechanics.
- **Impact:** Documentation only; no runtime changes.

### 2025-12-21: Physics mechanisms doc relocated to algorithms

- **What:** Moved `ALGORITHM_Physics_Mechanisms.md` into `docs/physics/algorithms/` and refreshed CHAIN/POINTERS so every physics doc links to the canonical mechanism map in the algorithms subfolder.
- **Why:** Squashed the duplicate ALGORITHM doc warning by keeping specialized mechanism docs in the algorithms folder while leaving `ALGORITHM_Physics.md` as the physics root overview.
- **Impact:** Documentation only; the root physics directory now hosts a single ALGORITHM doc while mechanism-level detail lives under `algorithms/`.

### 2025-12-21: Mechanism map folded into canonical physics algorithm

- **What:** Added the mechanism-level function map to `ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md` and converted `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md` into a deprecated stub that points readers to that consolidated section while keeping the implementation references intact.
- **Why:** Keep a single authoritative ALGORITHM doc while still letting mechanism-focused references resolve through the algorithms folder.
- **Impact:** Documentation only; no runtime changes.
- **Validation:** `mind validate`

### 2025-12-21: Implemented attention split, primes, contradiction pressure (v0)

- **What:** Added mechanism implementations for attention split, PRIMES lag/half-life, and contradiction pressure, plus unit tests.
- **Why:** Move v0 mechanisms from spec to executable, deterministic logic.
- **Impact:** New pure computation modules + tests; no runtime wiring yet.

### 2025-12-20: Pending external implementation references

- **What:** Replaced stub file paths with pending import notes in implementation docs.
- **Why:** Remove broken impl links until upstream code is imported.

### 2025-12-20: Physics tick energy helpers verified

- **What:** Verified `_flow_energy_to_narratives`, `_propagate_energy`, `_decay_energy`, and `_update_narrative_weights` in `mind/physics/tick.py` already contain concrete implementations.
- **Why:** Repair #16 flagged these helpers as empty; confirmed they are implemented and align with the physics algorithm.
- **Impact:** No code changes required; verification recorded to prevent repeat repairs.
- **Repair run:** `18-INCOMPLETE_IMPL-physics-tick`.

### 2025-12-21: Snap display rules + cluster monitor health checks

- **What:** Introduced `mind/physics/display_snap_transition_checker.py` and `mind/physics/cluster_energy_monitor.py` plus targeted tests so the documented Snap phases and large-cluster energy totals are asserted automatically.
- **Why:** Lock The Snap transition in the health suite and keep real-time watch over energy spikes inside dense clusters before they destabilize the living graph.
- **Impact:** Health documentation now lists dedicated checkers, algorithm docs point to the new modules, and the sync reflects the removal of the open gaps.
- **Verification:** `pytest mind/tests/test_physics_display_snap.py mind/tests/test_cluster_energy_monitor.py`.

### 2025-12-20: Mind Framework Refactor

- **What:** Refactored `IMPLEMENTATION_Physics.md` and renamed `TEST_Physics.md` to its new format (Health content).
- **Why:** To align with the new mind documentation standards and emphasize DATA FLOW AND DOCKING.
- **Impact:** Physics module documentation is now compliant with the latest protocol; Health checks are anchored to concrete docking points.
