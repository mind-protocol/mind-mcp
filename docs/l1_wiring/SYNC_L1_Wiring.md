# SYNC -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Last updated:** 2026-03-14

---

## Maturity

**STATUS: DESIGNING**

### What's canonical:
- L1 physics spec: 21 laws, formulas, constants (ALGORITHM_L1_Physics.md) -- complete, detailed
- Schema v2.0: 7 cognitive types, 14 relation_kinds, NodeBase/LinkBase with all fields
- Orchestrator: dispatcher loop with budget-driven ticks, Claude Code subprocess invocation
- FalkorDB adapter: working, tested, supports per-graph connections
- OpenAI embedding adapter: working, text-embedding-3-small and 3-large
- Seed brain generator: 209 nodes, 295 links from 6 manifestos + SYSTEM.md
- Orientation taxonomy: 6 orientations defined (take_care/create/verify/explore/rest/escalate)

### What's being designed (this doc chain):
- Stimulus injection pipeline (event to Law 1)
- Tick integration in orchestrator dispatcher
- WM-to-prompt serialization format
- Orientation-to-prompt modifier mapping
- Post-action self-stimulus feedback loop with anti-loop protection
- FalkorDB hybrid persistence (in-memory + periodic checkpoint)
- Per-citizen brain seeding (base + overlay pattern)
- Emotion calibration (anxiety, satisfaction, frustration formulas)
- Production cutover plan (parallel run, DNS, bot migration)

### What's proposed (v2):
- Laws 19-21 (energy budget, prospective projection, membrane coupling)
- Session parallelization (multi-track attention)
- Cross-citizen mechanisms (telepathy, debate, subconscious query)
- Biometric ingestion (Garmin HR -> limbic injection)
- Economic stimuli ($MIND tx -> satisfaction/frustration)

---

## Current State

### RESOLVED: L1 Engine Located in manemus (2026-03-14)

The L1 engine was built in the manemus repo at `manemus/runtime/cognition/` and never ported to mind-mcp. Confirmed: 7,256 lines of code, 19/19 tests passing.

**Source:** `/home/mind-protocol/manemus/runtime/cognition/`
**Core engine:** 14 files (models, constants, tick runner, 9 law files, tests)
**Integration files:** 5 additional files (live bridge, action dispatcher, health calculator, brain loader, doc converter)

**Blocker #1 is CLEARED.** The engine does not need to be rebuilt — it needs to be ported. Estimated effort: 1-2 hours for copy + tick step reorder + test validation. See IMPLEMENTATION_L1_Wiring.md Phase A for the detailed porting plan.

**Remaining blocker:** Citizen directories (`.mind/citizens/`) are still empty. Copy from manemus.

### Phase B Cross-Review Complete (2026-03-14)

`docs/reviews/REVIEW_F4_F5_Coherence.md` — 7 issues found, 5 fixed:
- Tick cycle numbering corrected to match schema.yaml canonical ordering
- `emotional_charge` removed from FalkorDB node schema (not in schema v2.0)
- FalkorDB link upsert now includes all LinkBase fields (stability, recency, polarity_ab/ba, valence, hierarchy, permanence)
- Trust update step corrected from step 9 to step 16 (Law 18, not Law 6)
- 2 design issues flagged (F4 value creation integration boundary, limbic delta theoretical bounds) — no fix needed, documented as cross-references

### What Exists (verified)

| Component | Path | Status | Lines |
|-----------|------|--------|-------|
| L1 spec (ALGORITHM) | `docs/cognition/l1/ALGORITHM_L1_Physics.md` | CANONICAL | ~2000 |
| Schema v2.0 | `docs/schema/schema.yaml` | CANONICAL | ~800 |
| **L1 engine (in manemus)** | `manemus/runtime/cognition/` | **WORKING, 19/19 tests** | **7,256** |
| v1.x physics engine | `runtime/physics/` | WORKING (but wrong model) | ~11,700 |
| Orchestrator dispatcher | `runtime/orchestrator/dispatcher.py` | WORKING | 273 |
| Claude invoker | `runtime/orchestrator/claude_invoker.py` | WORKING | ~200 |
| FalkorDB adapter | `runtime/infrastructure/database/falkordb_adapter.py` | WORKING | 209 |
| OpenAI embedding adapter | `runtime/infrastructure/embeddings/openai_adapter.py` | WORKING | 153 |
| Local embedding service | `runtime/infrastructure/embeddings/service.py` | WORKING | 224 |
| Seed brain generator | `runtime/seed_brain_from_source_docs_dynamic_generator.py` | WORKING | ~600 |
| Citizen identity | `runtime/citizens/__init__.py` | WORKING | ~200 |
| Citizen directories | `.mind/citizens/` | EMPTY | 0 |

### What Does NOT Exist in mind-mcp (needs porting or building)

| Component | Expected Path | Status |
|-----------|--------------|--------|
| L1 engine (laws, models, tick runner) | `runtime/cognition/` | **PORT FROM MANEMUS** |
| L1 tests | `runtime/cognition/tests/` | **PORT FROM MANEMUS** |
| Citizen identity files | `.mind/citizens/*/` | COPY FROM MANEMUS |
| Stimulus router | `runtime/cognition/stimulus_router.py` | NOT BUILT |
| WM prompt serializer | `runtime/cognition/wm_prompt_serializer.py` | NOT BUILT |
| FalkorDB checkpointer for brains | `runtime/cognition/falkordb_checkpointer.py` | NOT BUILT |
| Feedback injector | `runtime/cognition/feedback_injector.py` | NOT BUILT |
| Orientation taxonomy | `runtime/cognition/orientation_taxonomy.py` | NOT BUILT |

---

## v1.x vs. v2.0 Gap Analysis

### Physics Model Differences

| Aspect | v1.x (current code) | v2.0 (target, in schema/spec) |
|--------|---------------------|-------------------------------|
| **Core model** | SubEntity traversal (8 phases) | 21 physics laws (17-step tick) |
| **Node types** | actor, moment, narrative, space, thing | Same 5 + 7 cognitive subtypes (memory, concept, narrative, value, process, desire, state) |
| **Link types** | RELATES, ABOUT, etc. | Single `link` with 14 `relation_kind` values |
| **Energy model** | Generation → Draw → Flow → Backflow | Injection → Propagation → Decay → Competition → Consolidation → Forgetting |
| **Memory** | No working memory concept | WM: 5-7 nodes, saliency-selected |
| **Emotions** | Plutchik axes on links | 8 drives + 6 emergent emotions in LimbicState |
| **Crystallization** | SubEntity-based, embedding-weighted | Pattern detection → pure-math node creation (Law 10) |
| **Orientation** | None | 6 qualitative orientations from Law 11 |
| **Identity** | Seed data in node properties | Emerges from high-weight, high-stability nodes |
| **Self-stimulus** | None | LLM output re-injected (3-layer anti-loop) |
| **Persistence** | Mixed (some in FalkorDB) | Hybrid: in-memory physics, periodic FalkorDB checkpoint |

### What Can Be Reused from v1.x

| Component | Reusable? | Notes |
|-----------|-----------|-------|
| `runtime/physics/constants.py` | PARTIAL | Some constants (DECAY_RATE, energy flow rates) have v2.0 equivalents but different values. Plutchik functions reusable. |
| `runtime/physics/crystallization.py` | NO | v1.6.1 SubEntity model, completely different from Law 10 pure-math crystallization |
| `runtime/physics/tick_runner.py` | NO | v1.2 `GraphTickV1_2` class, wrong model |
| `runtime/physics/link_scoring.py` | PARTIAL | `cosine_similarity` function reusable |
| `runtime/infrastructure/embeddings/` | YES | Both adapters work, just wire them |
| `runtime/infrastructure/database/` | YES | FalkorDB adapter works, instantiate per citizen |

### What Must Be Built New (engine ports from manemus)

1. ~~L1 cognitive engine~~ **PORTS FROM MANEMUS** (7,256 lines, tick step reorder needed)
2. Stimulus router (event to Law 1 translation) — adapt from manemus bridge
3. WM prompt serializer — new
4. Orientation taxonomy + prompt mapping — new (reconcile 7 vs 6 orientations)
5. Feedback injector (self-stimulus + CONSUME) — adapt from manemus action dispatcher
6. FalkorDB checkpointer (brain-specific) — new (replaces manemus JSON persistence)
7. Per-citizen brain seeding pipeline — new orchestration, adapt manemus JSON loader
8. Migration scripts (manemus to mind-mcp) — new

---

## Open Questions

### Technical

1. ~~**Where is the L1 engine code?**~~ **ANSWERED.** Located at `manemus/runtime/cognition/`. 7,256 lines, 19/19 tests. Needs porting to mind-mcp with tick step reorder.

2. **Graph isolation strategy.** Decided: one graph per citizen (`brain_{handle}`). But: single FalkorDB instance with 44 graphs? Or separate instances? FalkorDB supports multiple graphs in one instance -- use that.

3. **Start with slow_tick (60s)?** Yes, during initial deployment. Downshift to minimal (300s) for idle citizens. Upshift to normal (15s) on stimulus. Fast (5s) only during panic arousal (>0.8).

4. **Embedding model: 3-small or 3-large?** The adapter defaults to 3-large (3072 dims). Schema specifies 1536 dims. Use 3-small (1536 dims, cheaper, matches schema).

### Operational

5. **Budget: how many Claude accounts for 44 citizens?** Current setup: round-robin across `~/.claude-accounts/{a,b,c}`. Three accounts may be insufficient. Need to calculate: if each citizen gets 1 session/hour, that's 44 sessions/hour across 3 accounts = ~15 sessions/hour/account. Claude Code can handle this if sessions are short (< 2 min each).

6. **manemus decommission timeline.** Proposed: 4-week plan (1 week parallel subset, 1 week parallel all, 1 week DNS cut, 1 week decommission). Depends on validation results.

7. **Citizen dir structure.** What files need copying from manemus? At minimum: identity.yaml (or equivalent), any persona/personality config, conversation history (if desired).

### Design

8. **Seed brain: same base for all, or customized per citizen?** Decided: same 209-node base (shared values, project knowledge) + per-citizen overlay (role processes, drive baselines, desires from identity file).

9. **WM token budget.** Proposed: 1200 tokens. 70% for node content, 30% for state/orientation/overhead. Too much? Test with real prompts. May need to reduce to 800 for long conversations.

10. **Orientation effect strength.** Start with soft modifiers (suggestions, not commands). If Claude ignores them, escalate to stronger language. If still ignored, consider structured output constraints.

---

## Dependencies

| Dependency | Status | Blocker? |
|-----------|--------|----------|
| L1 engine code (`runtime/cognition/`) | **LOCATED in manemus** | **NO** -- port needed (1-2 hours) |
| Citizen directories from manemus | MISSING | YES -- no identity data to seed brains |
| FalkorDB running | ASSUMED | NO -- dev can run locally |
| OpenAI API key | ASSUMED | NO -- exists in env |
| Render deployment config | EXISTS | NO |

### Cross-Force Integration Notes

**Force 4 (Trust Mechanics) dependency:**
- F5 tick cycle MUST snapshot drives at step 1 (LIMBIC_UPDATE) and step 17 (CONSUME) so that F4 can compute limbic delta between ticks
- F5 FalkorDB persistence MUST store `trust`, `friction`, `stability`, `affinity`, `aversion` on links (required by F4 for trust decay and tempering formulas)
- F5 does NOT need to implement value creation type detection -- F4 handles classification; F5 provides the raw limbic delta signal
- Canonical tick ordering is in `docs/schema/schema.yaml` (reviewed 2026-03-14, see `docs/reviews/REVIEW_F4_F5_Coherence.md`)

---

## Next Steps

### Immediate (Phase A — unblocked)

1. **Port L1 engine from manemus.** Copy core files, reorder tick steps to match schema canonical ordering, run 19 tests. Estimated: 1-2 hours.
2. **Copy citizen directories from manemus.** Still a blocker for brain seeding (Phase G).

### Wiring (Phases B-D)

3. Build stimulus router (event to Law 1) — adapt from manemus bridge
4. Wire tick loop into dispatcher
5. Build WM prompt serializer
6. Wire WM into `build_citizen_prompt()`
7. Build feedback injector — adapt from manemus action dispatcher
8. Wire feedback into `_collect_completed_futures()`

### Integration (Phases E-H)

9. Switch from pseudo-embeddings to OpenAI adapter
10. Build FalkorDB checkpointer (replaces manemus JSON persistence)
11. Build brain seeding pipeline
12. Seed all 44 citizens
13. Calibrate anxiety, satisfaction, frustration formulas

### Cutover (Phase I)

14. Deploy to Render
15. Parallel run validation
16. DNS cutover
17. manemus decommission

---

## Handoff

**For:** groundwork agent (implementation)

**Context:** This doc chain (6 files) fully specifies how to wire the L1 physics engine into the orchestrator. The physics design is complete (ALGORITHM_L1_Physics.md). The wiring design is in ALGORITHM_L1_Wiring.md. The implementation plan is in IMPLEMENTATION_L1_Wiring.md (updated v0.2 with manemus porting plan).

**Blocker #1: CLEARED.** L1 engine located at `manemus/runtime/cognition/` (7,256 lines, 19/19 tests). Port to mind-mcp with tick step reorder. No rebuild needed.

**Blocker #2:** Citizen directories (`.mind/citizens/`) are still empty. Copy from manemus. Only blocks Phase G (brain seeding), not Phases A-F.

**What to do first:** Phase A — port the engine (1-2 hours). Then Phase B — stimulus router + tick integration. This is the minimum viable wiring.

**Key files to read:**
- `manemus/runtime/cognition/tick_runner_l1_cognitive_engine.py` -- the engine to port (824 lines)
- `manemus/runtime/cognition/models.py` -- data structures (290 lines)
- `manemus/runtime/cognition/l1_live_integration_bridge.py` -- integration patterns to adapt (509 lines)
- `docs/l1_wiring/ALGORITHM_L1_Wiring.md` -- the wiring spec
- `docs/reviews/REVIEW_F4_F5_Coherence.md` -- cross-review corrections to apply during porting
- `runtime/orchestrator/dispatcher.py` -- where tick integration happens
- `runtime/citizens/__init__.py` -- where WM injection happens
