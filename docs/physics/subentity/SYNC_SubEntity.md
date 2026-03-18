# SubEntity Traversal Engine — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo (documentation chain creation)
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v2.1):**
- SubEntity dataclass with 7-state machine (SEEKING, BRANCHING, ABSORBING, RESONATING, REFLECTING, CRYSTALLIZING, MERGING)
- ExplorationContext for lazy reference resolution
- Query/intention separation with fixed INTENTION_WEIGHT=0.25 (semantic via embedding, no enum)
- Link scoring formula: alignment x polarity x (1-permanence) x self_novelty x sibling_divergence
- Energy injection at each step: criticality x STATE_MULTIPLIER[state]
- Crystallization with novelty threshold 0.85
- Awareness depth tracking (up/down unbounded accumulator)
- Fatigue detection (5-step window, 0.05 threshold)
- ExplorationRunner with async state dispatch, timeout, and MAX_STEPS=1000
- CRYSTALLIZING always transitions to MERGING (v2.0.1 fix for infinite loop)
- Children crystallize to graph; no child-to-parent result propagation (v2.0)

**What's still being designed:**
- Health check runtime implementation (checkers defined in HEALTH doc but not yet coded)
- Whether ABSORBING->CRYSTALLIZING path is exercised in practice (both alignment > 0.7 AND novelty > 0.7 required)

**What's proposed (v3+):**
- Numpy-accelerated cosine similarity for large embedding dimensions
- Extraction of subentity.py (currently SPLIT at ~1044 lines) into subentity_scoring.py and subentity_tree.py
- Extraction of exploration.py (currently SPLIT at ~1110 lines) into exploration_handlers.py
- GraphInterface as typing.Protocol instead of dataclass of callables
- Exploration result caching for repeated identical queries

---

## CURRENT STATE

The SubEntity traversal engine is the backbone of `graph_query`, `subcall`, and the cognitive tick loop. It is feature-complete at v2.1 with all core algorithms implemented and functional. The state machine, link scoring, energy injection, branching, and crystallization all work as designed.

The code is well-documented at the source level (docstrings with formulas, design decisions, and version history). Two files are above the SPLIT threshold: `subentity.py` (~1044 lines) and `exploration.py` (~1110 lines). This documentation chain is the first formal doc chain for the module.

The `link_scoring.py` module exists as a standalone implementation of the scoring formula, but `subentity.py` also contains its own versions of `cosine_similarity`, `compute_self_novelty`, `compute_sibling_divergence`, and `compute_link_score`. The ExplorationRunner in `exploration.py` primarily uses `link_scoring.py`'s functions. The duplication in `subentity.py` should be consolidated.

---

## RECENT CHANGES

### 2026-03-18: Documentation Chain Created

- **What:** Complete doc chain (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC) for the SubEntity module
- **Why:** Most critical undocumented module in mind-mcp. Powers graph_query, subcall, and the cognitive tick loop. Documentation was needed for onboarding, maintenance, and health monitoring.
- **Files:** `docs/physics/subentity/` (8 files)
- **Insights:** The code is mature and well-structured but has accumulated duplication between subentity.py and link_scoring.py. The v2.0/v2.0.1/v2.1 changes show good iterative refinement (removing enum rigidity, fixing infinite loops, simplifying child-to-parent propagation).

### v2.1: Semantic Intention

- **What:** Removed IntentionType enum and INTENTION_WEIGHTS dict. Intention weight is now a fixed constant (0.25). Intention meaning is fully semantic via intention_embedding.
- **Why:** The enum (SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE) was rigid and keyword-based. Semantic embedding carries richer meaning without predefined categories.
- **Files:** `subentity.py` (removed IntentionType, INTENTION_WEIGHTS; added INTENTION_WEIGHT constant)

### v2.0.1: Crystallization Always Merges

- **What:** Changed CRYSTALLIZING to always transition to MERGING (previously could return to SEEKING if satisfaction was low)
- **Why:** The CRYSTALLIZING->SEEKING path caused infinite loops: low satisfaction -> crystallize -> seek -> reflect -> low satisfaction -> crystallize
- **Files:** `exploration.py:_step_crystallizing()` (line ~900)

### v2.0: Awareness Depth + No Child Propagation

- **What:** Added awareness_depth tracking (up/down accumulator), progress_history for fatigue detection. Removed child-to-parent result propagation — children crystallize to graph instead.
- **Why:** Graph is the source of truth, not parent memory. Fatigue provides a softer stopping condition than hard timeout.
- **Files:** `subentity.py` (awareness_depth, progress_history, is_fatigued), `exploration.py` (merge_child_results simplified)

### v1.9: Energy Injection

- **What:** SubEntity injects energy at each traversal step. Added ABSORBING state. Added STATE_MULTIPLIER per-state weights.
- **Why:** Traversal should not be read-only. Energy injection creates heat trails that connect the cognitive layer to the physics tick.
- **Files:** `subentity.py` (inject_energy_to_node, inject_energy_to_link, STATE_MULTIPLIER, ABSORBING state)

---

## KNOWN ISSUES

### Duplicate Link Scoring Functions

- **Severity:** medium
- **Symptom:** `subentity.py` contains `cosine_similarity`, `compute_self_novelty`, `compute_sibling_divergence`, `compute_link_score` which duplicate functions in `link_scoring.py`
- **Suspected cause:** Organic growth — scoring started in subentity.py, then link_scoring.py was created as a standalone module, but the originals were not removed
- **Attempted:** Nothing yet — needs consolidation

### Files Above SPLIT Threshold

- **Severity:** medium
- **Symptom:** `subentity.py` (~1044 lines) and `exploration.py` (~1110 lines) are both above the 700-line SPLIT threshold
- **Suspected cause:** Feature accumulation across v1.6-v2.1
- **Attempted:** Extraction candidates identified in IMPLEMENTATION doc

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (for extraction/consolidation) or fixer (for duplicate removal)

**Where I stopped:** Complete doc chain created. No code changes made.

**What you need to understand:**
The SubEntity module is the most interconnected physics module — it imports from flow.py, synthesis.py, link_scoring.py, crystallization.py, cluster_presentation.py, and traversal_logger.py. Any extraction or consolidation must preserve all import paths. The ExplorationRunner uses `link_scoring.py` functions, not the duplicate functions in `subentity.py`.

**Watch out for:**
- `subentity.py:compute_link_score` and `link_scoring.py:calculate_link_score` have slightly different signatures and None-handling. The subentity.py version handles Optional types; the link_scoring.py version expects concrete values. Don't blindly delete one.
- The depth check in `_run_subentity()` (line ~373) directly sets `se.state = SubEntityState.REFLECTING` without using `transition_to()` — this is intentional (avoiding SubEntityTransitionError when forcing a depth limit), but it bypasses the validation in V1.
- `_step_merging()` also sets `se.state` directly rather than calling `transition_to()` because MERGING is terminal with no outgoing transitions.

**Open questions I had:**
- Is the ABSORBING->CRYSTALLIZING transition exercised in production? Both conditions (alignment > 0.7 AND novelty > 0.7) must be true, which may be rare.
- Should the duplicate scoring functions in subentity.py be the canonical ones (since they handle Optional better) or should link_scoring.py be canonical (since it's the dedicated module)?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain created for the SubEntity traversal engine — the most critical undocumented module in mind-mcp. All 8 docs (OBJECTIVES through SYNC) are written from direct code reading, not templates. The module is feature-complete at v2.1 with good iterative design. Two code issues identified: duplicate scoring functions and files above SPLIT threshold.

**Decisions made:**
- Documented the v2.0 design decision (graph is source of truth, no child-to-parent propagation) as canonical
- Identified 4 health indicators for future implementation
- Marked extraction candidates for both oversized files

**Needs your input:**
- Priority of extracting subentity.py and exploration.py (code quality) vs new features
- Whether health check runtime implementation should be prioritized

---

## TODO

### Doc/Impl Drift

- [ ] IMPL->DOCS: `subentity.py` DOCS header references `docs/schema/ALGORITHM_Schema.md` — should also reference `docs/physics/subentity/`
- [ ] IMPL->DOCS: `exploration.py` DOCS header references `docs/physics/ALGORITHM_Physics.md` — should also reference `docs/physics/subentity/`

### Immediate

- [ ] Consolidate duplicate cosine_similarity and scoring functions between subentity.py and link_scoring.py
- [ ] Add DOCS reference to this doc chain in subentity.py and exploration.py headers

### Later

- [ ] Extract subentity.py into subentity.py + subentity_scoring.py + subentity_tree.py
- [ ] Extract exploration.py into exploration.py + exploration_handlers.py + exploration_presentation.py
- [ ] Implement health check runtime in runtime/physics/health/subentity_health.py
- [ ] Convert GraphInterface from dataclass of callables to typing.Protocol
- IDEA: Add exploration result caching for repeated identical queries (keyed by actor_id + query_embedding hash)

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the documentation accuracy — every formula, constant, and behavior was verified against the source code. The module is well-designed with clear version history showing thoughtful iteration.

**Threads I was holding:**
- The duplicate scoring functions are not identical (different None-handling) — consolidation needs care
- The depth check bypassing transition_to() is a known pattern, not a bug, but it means V1 has a documented exception
- ExplorationRunner._step_branching() merges child results (lines 578-593) in a way that contradicts the v2.0 "no propagation" design — it still merges found_narratives and averages satisfaction from children. This may be intentional (branching is different from general child crystallization) but it's worth examining.

**Intuitions:**
The ABSORBING state feels underused. It was added in v1.9 but the transition conditions (alignment > 0.7 AND novelty > 0.7) are stringent. In practice, most SubEntities likely skip ABSORBING entirely, going directly SEEKING->RESONATING or SEEKING->REFLECTING.

**What I wish I'd known at the start:**
That `exploration.py:_step_branching()` still propagates child results despite v2.0's "no propagation" design. The `merge_child_results()` method in SubEntity follows the v2.0 design (children crystallize, parent doesn't aggregate), but the actual branching handler in ExplorationRunner manually merges found_narratives and averages satisfaction. This inconsistency should be resolved.

---

## POINTERS

| What | Where |
|------|-------|
| SubEntity dataclass + state machine | `runtime/physics/subentity.py` |
| ExplorationRunner + async handlers | `runtime/physics/exploration.py` |
| Link scoring formula | `runtime/physics/link_scoring.py` |
| Crystallization + novelty check | `runtime/physics/crystallization.py` |
| Energy flow primitives | `runtime/physics/flow.py` |
| Synthesis for crystallization | `runtime/physics/synthesis.py` |
| Traversal step logger | `runtime/physics/traversal_logger.py` |
| Cluster result presentation | `runtime/physics/cluster_presentation.py` |
| Physics constants | `runtime/physics/constants.py` |
