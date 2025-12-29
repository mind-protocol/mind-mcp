# SubEntity — Sync

```
STATUS: CANONICAL
VERSION: v2.1
UPDATED: 2025-12-29
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
THIS:           ./SYNC_SubEntity.md
```

---

## HEALTH STATUS

Last health check: 2025-12-26

| Indicator | Threshold | Status | Notes |
|-----------|-----------|--------|-------|
| H1: Efficiency | ≥ 0.20 | HEALTHY | Typical: 0.20-0.30 |
| H2: Satisfaction velocity | ≥ 0.10 | HEALTHY | Typical: 0.10-0.15 |
| H3: Sibling divergence | ≥ 0.70 | HEALTHY | Typical: 0.70-0.85 |
| H4: Semantic quality | ≥ 0.60 | HEALTHY | Typical: 0.60-0.80 |
| H5: Backtrack rate | < 0.10 | HEALTHY | Typical: 0.03-0.08 |
| H6: Crystallization novelty | ≥ 0.85 | HEALTHY | Gate enforced |
| H7: Anomaly count | 0 | HEALTHY | Clean runs |

---

## KNOWN ISSUES

### Active Issues

| Issue | Impact | Workaround | Ticket |
|-------|--------|------------|--------|
| No real-time monitoring | Issues detected post-hoc | Log review in CI | — |
| No graph state diff | Can't verify energy directly | Check log claims | — |
| No cross-exploration trends | Missing drift detection | Manual aggregate | — |

### Resolved Issues

| Issue | Resolution | Version |
|-------|------------|---------|
| Circular sibling refs | Lazy ID refs | v1.7.2 |
| Partial merge on timeout | Fail loud | v1.7.2 |
| Query/intention conflation | Separate embeddings | v1.8 |
| Infinite loop at max depth | Depth check skips terminal states | v2.0.1 |
| CRYSTALLIZING → SEEKING loop | Always MERGING after crystallize | v2.0.1 |

---

## HANDOFFS

### For agent_witness (Health Verification)

Run health checks after exploration changes:

```bash
python -m engine.physics.health.check_subentity --all --since 1h
```

Check for:
- Any ERROR status in health indicators
- New anomaly patterns
- Efficiency degradation

### For agent_fixer (Bug Investigation)

When investigating SubEntity issues:

1. Read VALIDATION_SubEntity.md for invariants
2. Check traversal logs at `runtime/data/logs/traversal/`
3. Use log analysis functions from HEALTH_SubEntity.md
4. Focus on state transitions and energy injection

### For agent_weaver (Feature Development)

Before modifying SubEntity:

1. Read PATTERNS_SubEntity.md for design philosophy
2. Check ALGORITHM_SubEntity.md for current logic
3. Update VALIDATION_SubEntity.md if adding invariants
4. Add health checks for new behaviors

---

## DOCUMENTATION STATUS

| File | Status | Last Updated |
|------|--------|--------------|
| OBJECTIVES_SubEntity.md | COMPLETE | 2025-12-26 |
| PATTERNS_SubEntity.md | COMPLETE | 2025-12-26 |
| BEHAVIORS_SubEntity.md | COMPLETE | 2025-12-26 |
| ALGORITHM_SubEntity.md | COMPLETE | 2025-12-26 |
| VALIDATION_SubEntity.md | COMPLETE | 2025-12-26 |
| IMPLEMENTATION_SubEntity.md | COMPLETE | 2025-12-26 |
| HEALTH_SubEntity.md | COMPLETE | 2025-12-26 |
| SYNC_SubEntity.md | COMPLETE | 2025-12-26 |

**Chain complete.** All 8 documentation files present and current.

---

## HANDOFF — v2.0 Implementation (COMPLETED)

**Implementation completed 2025-12-26**

All v2.0 features have been implemented in `runtime/physics/subentity.py`:

1. **New fields added to SubEntity dataclass:**
   - `awareness_depth: List[float]` = [up, down] unbounded accumulator
   - `progress_history: List[float]` = delta sequence toward intention

2. **New methods implemented:**
   - `update_depth(link_hierarchy)`: Accumulates UP (>0.2) or DOWN (<-0.2)
   - `update_progress()`: Tracks delta = cos(crystallization, intention)
   - `is_fatigued(window=5, threshold=0.05)`: Stagnation detection

3. **New function added:**
   - `should_child_crystallize(child)`: True unless 90%+ match found

4. **Modified behavior:**
   - `merge_child_results()`: NO propagation to parent, returns children to crystallize
   - Graph is source of truth, not parent memory

**Tests added to `runtime/tests/test_subentity.py`:**
- TestAwarenessTracking: 4 tests for depth accumulation
- TestProgressTracking: 2 tests for progress history
- TestFatigueDetection: 4 tests for fatigue stopping
- TestChildCrystallization: 4 tests for crystallization rules

All 70 tests passing.

---

## ARCHIVE

Older content archived to: `SYNC_SubEntity_archive_2025-12.md`


---

## ARCHIVE

Older content archived to: `SYNC_SubEntity_archive_2025-12.md`
