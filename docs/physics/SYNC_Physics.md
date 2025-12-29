# Physics — Current State

STATUS: DESIGNING (v1.6.1)
UPDATED: 2025-12-26

## CURRENT STATE

**v1.2 Implementation:** Complete
**v1.6.1 Design:** In progress (schema complete, code pending)
**Integration:** v1.2 done (Orchestrator uses v1.2 by default)
**Verification:** 67 tests passing in `test_energy_v1_2.py`

## KNOWN ISSUES

- Handler runtime and speed controller wiring pending
- SubEntity exploration runner not yet wired to TraversalLogger
- Forward/backward coloring not yet integrated with SubEntity

## FILES

| File | Purpose | Status |
|------|---------|--------|
| `runtime/physics/tick_v1_2.py` | 8-phase tick orchestrator | v1.2 OK |
| `runtime/physics/phases/*.py` | Phase implementations | v1.2 OK |
| `runtime/physics/flow.py` | Traversal primitives | v1.2 (needs v1.6.1) |
| `runtime/physics/subentity.py` | SubEntity class | **v1.7.2 DONE** |
| `runtime/physics/traversal_logger.py` | Exploration logging | **v1.0 DONE** |
| `runtime/physics/health/checkers/subentity.py` | SubEntity health checkers | **DONE** |
| `docs/schema/schema.yaml` | Schema spec | v1.6.1 |
| `docs/physics/PATTERNS_Physics.md` | Design philosophy | v1.6 |
| `docs/physics/ALGORITHM_Physics.md` | System overview | v1.6 |
| `docs/physics/traversal_logger/` | TraversalLogger docs | v1.0 |

## ARCHIVE REFERENCES

- `docs/physics/archive/SYNC_Physics_archive_2025-12.md` holds the 2025-12 detailed changelog
- `docs/physics/archive/SYNC_archive_2024-12.md` preserves the prior year snapshot

## HANDOFF NOTES

**For agents implementing v1.6.1:**
1. Schema is complete in `docs/schema/schema.yaml` v1.6.1
2. SubEntities track tree structure (origin_moment, siblings, children)
3. found_narratives stores (narrative_id, alignment) tuples
4. crystallization_embedding computed EACH step for sibling divergence
5. Link score includes self_novelty and sibling_divergence factors
6. All rates derived from graph properties (no magic numbers)

**Key v1.6.1 refinements:**
- Siblings naturally spread exploration via divergence scoring
- Continuous crystallization_embedding enables comparison
- Alignment scores in found_narratives for weighted aggregation
- crystallized field tracks if SubEntity created a Narrative

**Key files to modify:**
- `runtime/physics/subentity.py` (new)
- `runtime/physics/flow.py` (add forward coloring + link scoring)
- `runtime/models/links.py` (add embedding field)


---

## ARCHIVE

Older content archived to: `SYNC_Physics_archive_2025-12.md`
