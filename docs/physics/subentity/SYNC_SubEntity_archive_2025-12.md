# Archived: SYNC_SubEntity.md

Archived on: 2025-12-26
Original file: SYNC_SubEntity.md

---

## MATURITY

**STATUS: CANONICAL (v1.9)**

### Canonical (v1.9)

These are stable, tested, and should not change without a version bump:

| Component | Status | Evidence |
|-----------|--------|----------|
| SubEntity state machine | CANONICAL | 7 states, valid transitions defined |
| Link scoring formula | CANONICAL | Alignment × polarity × (1-permanence) × self_novelty × sibling_divergence |
| Query vs Intention (v1.8) | CANONICAL | Separate embeddings, intent_weight by type |
| Energy injection (v1.9) | CANONICAL | criticality × STATE_MULTIPLIER per state |
| Crystallization embedding | CANONICAL | Weighted blend formula in ALGORITHM |
| Sibling divergence | CANONICAL | Lazy refs, divergence scoring |
| TraversalLogger | CANONICAL | JSONL + TXT output, anomaly detection |

### Designing (v1.10 candidates)

These are under active consideration but not yet finalized:

| Component | Status | Notes |
|-----------|--------|-------|
| Real-time health monitoring | DESIGNING | Currently post-hoc analysis only |
| Cross-exploration trend analysis | DESIGNING | Aggregate reports not yet implemented |
| Graph state diff verification | DESIGNING | Can't directly verify energy injection |

### Proposed (Future)

Ideas for future versions, not actively being worked:

| Idea | Rationale |
|------|-----------|
| Distributed exploration | Multiple SubEntities across nodes |
| Exploration replay | Recreate exploration from logs |
| Interactive debugging | Step through exploration in UI |

---


## RECENT CHANGES

### v1.9 (2025-12-26)

- **Energy injection per state**: Added STATE_MULTIPLIER table
  - SEEKING: 0.5, BRANCHING: 0.5, ABSORBING: 1.0
  - RESONATING: 2.0, REFLECTING: 0.5, CRYSTALLIZING: 1.5
  - MERGING: 0.0 (terminal)
- **Weight gain formula**: `weight_gain = injection × permanence`
- **ABSORBING state**: Content processing with alignment + novelty check
- **Full doc chain**: Created complete OBJECTIVES through SYNC

### v1.8 (Previous)

- **Query vs Intention separation**: Two embedding streams
- **Intention types**: SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE
- **Intent weight per type**: Different balancing for different goals

### v1.7.2 (Previous)

- **Lazy sibling references**: Store IDs, not objects
- **Timeout behavior**: Fail loud, no partial merge
- **ExplorationContext**: Registry for SubEntity lookup

---


## CODE STATUS

### Primary Files

| File | Lines | Status | Last Verified |
|------|-------|--------|---------------|
| runtime/physics/subentity.py | 984 | OK | 2025-12-26 |
| runtime/physics/exploration.py | 1033 | OK | 2025-12-26 |
| runtime/physics/traversal_logger.py | 1247 | OK | 2025-12-26 |
| runtime/physics/link_scoring.py | ~200 | OK | 2025-12-26 |
| runtime/physics/crystallization.py | ~100 | OK | 2025-12-26 |
| runtime/physics/flow.py | ~300 | OK | 2025-12-26 |

### Test Files

| File | Coverage | Status |
|------|----------|--------|
| mind/tests/test_subentity.py | V1, V2, V3 | OK |
| mind/tests/test_traversal_logger.py | Logging | OK |
| mind/tests/test_subentity_health.py | V4, V5, V7 | OK |

---


## DEPENDENCIES

### Internal

| Module | Depends On | For |
|--------|------------|-----|
| SubEntity | engine.physics.flow | Coloring, energy |
| SubEntity | engine.physics.link_scoring | Score computation |
| SubEntity | engine.physics.crystallization | Embedding computation |
| SubEntity | engine.physics.cluster_presentation | Content rendering |

### External

| Package | Version | For |
|---------|---------|-----|
| asyncio | stdlib | Parallel exploration |
| dataclasses | stdlib | Data structures |
| json | stdlib | Log serialization |

---


## VERIFICATION COMMANDS

```bash
# Run unit tests
pytest mind/tests/test_subentity.py -v

# Run traversal logger tests
pytest mind/tests/test_traversal_logger.py -v

# Run health validation tests
pytest mind/tests/test_subentity_health.py -v

# Check specific exploration
python -m engine.physics.health.check_subentity <exploration_id>

# Check all recent explorations
python -m engine.physics.health.check_subentity --all --since 1h
```

---



---

# Archived: SYNC_SubEntity.md

Archived on: 2025-12-29
Original file: SYNC_SubEntity.md

---

## INVARIANT STATUS

| ID | Name | Status | Last Checked |
|----|------|--------|--------------|
| V1 | State Machine Integrity | PASSING | 2025-12-26 |
| V2 | Tree Structure Consistency | PASSING | 2025-12-26 |
| V3 | Path Monotonicity | PASSING | 2025-12-26 |
| V4 | Satisfaction Monotonicity | PASSING | 2025-12-26 |
| V5 | Energy Conservation | PASSING | 2025-12-26 |
| V6 | Crystallization Novelty Gate | PASSING | 2025-12-26 |
| V7 | Child Crystallization (v2.0) | PASSING | 2025-12-26 |
| V8 | Timeout Behavior | PASSING | 2025-12-26 |
| V9 | Link Score Bounds | PASSING | 2025-12-26 |
| V10 | Embedding Dimension Consistency | PASSING | 2025-12-26 |
| V11 | Depth Accumulation (v2.0) | PASSING | 2025-12-26 |
| V12 | Progress History (v2.0) | PASSING | 2025-12-26 |
| V13 | Fatigue Stopping (v2.0) | PASSING | 2025-12-26 |

---


## NEXT ACTIONS

### v2.0 Implementation (Awareness Depth + Breadth) — COMPLETE ✓

All v2.0 features implemented in `runtime/physics/subentity.py`:
- `awareness_depth: List[float]` = [up, down] accumulator
- `progress_history: List[float]` = delta sequence toward intention
- `update_depth()`: Accumulates hierarchy on UP/DOWN links
- `update_progress()`: Tracks delta toward intention
- `is_fatigued()`: Stagnation detection for stopping
- `should_child_crystallize()`: Systematic crystallization (unless 90%+ match)
- `merge_child_results()`: Returns children to crystallize, NO propagation

All 70 tests passing in `runtime/tests/test_subentity.py`.

### Remaining Backlog

1. **Update traversal logger**: Include awareness_depth and progress in logs
2. **Implement health checker CLI**: `runtime/physics/health/check_subentity.py`
3. **Add CI integration**: Run health checks on exploration log commits
4. **Build aggregate reports**: Cross-exploration trend analysis

See: `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`

---


## v2.1 — Semantic Intention + Backprop Coloring (2025-12-29)

### 1. Removed IntentionType Enum

**Before:** Fixed enum with 5 types and hardcoded weights:
```python
class IntentionType(Enum):
    SUMMARIZE = "summarize"   # weight 0.3
    VERIFY = "verify"         # weight 0.5
    FIND_NEXT = "find_next"   # weight 0.2
    EXPLORE = "explore"       # weight 0.25
    RETRIEVE = "retrieve"     # weight 0.1
```

**After:** Fixed constant, intention is semantic via embedding:
```python
INTENTION_WEIGHT = 0.25  # Fixed, intention meaning is in embedding
```

**Rationale:** The enum was rigid (only 5 types) and keyword-based (parsing "summar" → SUMMARIZE). Now any intention string works, embedded semantically.

**Files:**
- `runtime/physics/subentity.py` — Removed enum, added constant
- `runtime/physics/cluster_presentation.py` — Moved IntentionType here (for presentation only)

### 2. Backprop Link Coloring

**Before:** Forward coloring during SEEKING (colored links before knowing if useful):
```python
# _step_seeking
forward_color_link(link, se.intention_embedding, energy_flow=0.1)
```

**After:** Backward coloring in REFLECTING/CRYSTALLIZING (when we know path was valuable):
```python
# _step_reflecting (if satisfaction > 0.5)
backward_color_path(path_links, se.intention_embedding, ...)

# _step_crystallizing (after creating narrative)
backward_color_path(path_links, se.crystallization_embedding, ...)
```

**Rationale:** Only color links that led to useful discoveries. This creates meaningful "memory traces" in the graph.

**Files:**
- `runtime/physics/exploration.py` — Removed forward_color_link, added backprop in reflecting/crystallizing

---


## Bug Fixes: v2.0.1 — Crystallization Loop (2025-12-29)

### Fix 1: Depth Check Overwrote Terminal States

**Problem:** When exploration reached max_depth with satisfaction=0, the state machine entered an infinite loop:

```
REFLECTING → CRYSTALLIZING → (depth check overwrites) → REFLECTING → ...
```

**Root Cause:** The depth check (line 382-383) unconditionally forced state to REFLECTING after every step, including after CRYSTALLIZING.

**Fix:** Depth check now only applies during active exploration states (SEEKING, BRANCHING, ABSORBING).

**File:** `runtime/physics/exploration.py:384-389`

### Fix 2: CRYSTALLIZING → SEEKING Loop

**Problem:** After fix 1, a secondary loop appeared:

```
CRYSTALLIZING → SEEKING → (no links) → REFLECTING → (sat=0) → CRYSTALLIZING → ...
```

**Root Cause:** After crystallizing, the code returned to SEEKING if depth > 0. But satisfaction wasn't updated, so REFLECTING sent it right back to CRYSTALLIZING.

**Fix:**
1. Update satisfaction after crystallization (`se.update_satisfaction(1.0, 1.0)`)
2. Always transition to MERGING after crystallizing (not SEEKING)

**File:** `runtime/physics/exploration.py:816-832`

### Result

Exploration now properly:
1. Traverses the graph
2. Crystallizes a narrative when satisfaction is low
3. Terminates in MERGING state
4. Returns the crystallized narrative

```
State: merging
Satisfaction: 0.50
Crystallized: narrative_cryst_xxx
Found narratives: 1
Duration: 0.26s
```

---

