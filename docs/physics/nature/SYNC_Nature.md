# Nature — Sync

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
HEALTH:          ./HEALTH_Nature.md
THIS:            SYNC_Nature.md (you are here)
```

---

## CURRENT STATE

### Maturity

| Component | Status |
|-----------|--------|
| OBJECTIVES | Canonical |
| PATTERNS | Canonical |
| BEHAVIORS | Canonical |
| ALGORITHM | Canonical |
| VALIDATION | Canonical |
| IMPLEMENTATION | Canonical |
| HEALTH | Canonical |

### Implementation Status

| Component | Status |
|-----------|--------|
| nature_physics.yaml | ✓ Complete |
| nature.py | ✓ Complete |
| __init__.py exports | ✓ Complete |
| Synonym resolution | ✓ Complete (261 synonyms) |
| Unit tests | ○ TODO |
| Health checks | ○ TODO |

---

## RECENT CHANGES

### 2024-12-29

- **Synonym system added** — 261 synonyms for resilient parsing
  - "fixes" → "resolves", "immediately" → "urgently", etc.
  - Word-boundary matching prevents substring conflicts
  - Validation ensures no synonym conflicts with canonical verbs
- Renamed from `link_vocab` to `nature`
- Moved physics definitions to `nature_physics.yaml`
- Created full doc chain in `docs/physics/nature/`
- Added workflow_verbs category (claims, resolves, detects)
- Backwards compatibility aliases maintained

---

## VERB CATEGORIES

Current verb count by category:

| Category | Count | Purpose |
|----------|-------|---------|
| base_verbs | 11 | Generic hierarchy/polarity |
| ownership_verbs | 6 | Thing↔Actor relations |
| evidential_verbs | 10 | Evidence→Narrative |
| spatial_verbs | 11 | Space↔Actor/Thing |
| actor_verbs | 6 | Actor→Moment/Narrative |
| narrative_verbs | 4 | Narrative→Narrative |
| temporal_verbs | 9 | Moment→Moment |
| workflow_verbs | 12 | Task/Actor workflow |
| **TOTAL** | **69** | |

---

## MODIFIER COUNTS

| Type | Count |
|------|-------|
| Pre-modifiers | 12 |
| Post-modifiers | 12 |
| Weight annotations | 3 |
| Intensifiers | 25 |

---

## NEXT STEPS

1. **Write unit tests** for all invariants
2. **Implement health check** function
3. **Add runtime sampling** for parse success tracking
4. **Create nature.yaml** (agent-facing, no physics) in platform

---

## BLOCKERS

None currently.

---

## HANDOFF

**For next agent:**

The nature system is fully implemented. It converts semantic nature strings to physics floats. The YAML (`nature_physics.yaml`) is the source of truth.

Key files:
- `runtime/physics/nature.py` — Parser
- `runtime/physics/nature_physics.yaml` — Definitions
- `docs/physics/nature/` — This doc chain

To add new verbs or modifiers, edit `nature_physics.yaml`. No code changes needed.

**Agent posture:** keeper (maintaining definitions) or groundwork (adding tests)


---

## ARCHIVE

Older content archived to: `SYNC_Nature_archive_2025-12.md`
