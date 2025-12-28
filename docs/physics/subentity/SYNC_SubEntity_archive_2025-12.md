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
| mind/physics/subentity.py | 984 | OK | 2025-12-26 |
| mind/physics/exploration.py | 1033 | OK | 2025-12-26 |
| mind/physics/traversal_logger.py | 1247 | OK | 2025-12-26 |
| mind/physics/link_scoring.py | ~200 | OK | 2025-12-26 |
| mind/physics/crystallization.py | ~100 | OK | 2025-12-26 |
| mind/physics/flow.py | ~300 | OK | 2025-12-26 |

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

