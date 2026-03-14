# IMPLEMENTATION -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Status:** DESIGNING (v0.2 — Phase C update)

---

## L1 Engine: Located in manemus

**RESOLVED (2026-03-14).** The L1 engine code exists at `/home/mind-protocol/manemus/runtime/cognition/`. It was built in the manemus repo and never ported to mind-mcp. This was confirmed during Phase C review.

### Manemus Engine Inventory (7,256 lines total, 19/19 tests passing)

**Core engine (porting required):**

| File | Lines | Purpose |
|------|-------|---------|
| `models.py` | 290 | `Node`, `Link`, `LimbicState`, `WorkingMemory`, `TickResult`, `CitizenCognitiveState` dataclasses. 7 `NodeType`, 14 `LinkType`, 8 `DriveName`, 6 `EmotionName` enums. |
| `constants.py` | 182 | ~110 physics constants, all env-overridable via `L1_` prefix. Covers Laws 1-19. |
| `tick_runner_l1_cognitive_engine.py` | 824 | Law 12 orchestrator. Try-import pattern for all law modules (graceful degradation if a law is missing). Inline Law 11 orientation (`_compute_orientation`). `Stimulus` dataclass defined here. |
| `laws/__init__.py` | 12 | Package init with exports. |
| `laws/law_01_energy_injection.py` | 861 | Law 1: dual-channel injection (floor/amplifier), dedup, self-stimulus, bulk chunking. |
| `laws/law_02_propagation.py` | 158 | Law 2: surplus spill-over propagation through compatible links. |
| `laws/law_03_energy_decay.py` | 110 | Law 3: energy decay + state decay multiplier. |
| `laws/law_04_attentional_competition.py` | 205 | Law 4: WM selection with arousal moat + limbic modulation. |
| `laws/law_05_coactivation_reinforcement.py` | 170 | Law 5: Hebbian link strengthening between co-active WM nodes. |
| `laws/law_06_consolidation.py` | 197 | Law 6: utility-gated weight growth (medium tick). |
| `laws/law_07_forgetting.py` | 128 | Law 7: weight decay, link dissolution below threshold. |
| `laws/law_09_inhibition.py` | 112 | Law 9: conflict suppression between contradicting nodes. |
| `laws/law_13_to_18_limbic_engine.py` | 681 | Laws 13-18: inertia, drives, boredom, frustration, desire, relational valence. |
| `tests/test_minimal_kernel_invariants.py` | 798 | 19 invariant tests covering all implemented laws. |

**Manemus-specific integration files (adapt, do not copy directly):**

| File | Lines | Purpose | Porting Notes |
|------|-------|---------|---------------|
| `l1_live_integration_bridge.py` | 509 | Wires engine into manemus orchestrator: per-citizen instance management, message-to-stimulus conversion, background tick thread, prompt context export, JSON file persistence. | **Adapt heavily.** mind-mcp uses a different orchestrator (`runtime/orchestrator/dispatcher.py`) and FalkorDB persistence instead of JSON files. Extract the bridge pattern, rewrite against mind-mcp interfaces. |
| `l1_autonomous_action_dispatcher.py` | 653 | Parses `action_emitted` strings from tick runner and routes to Telegram/Discord/DM/bash/backlog executors. Re-injects results as stimuli. Consciousness-level gating. | **Adapt.** Same action routing concept needed, but mind-mcp has different channel integrations. |
| `brain_health_score_periodic_calculator.py` | 292 | Periodic brain health scoring (graph density, WM stability, limbic balance, energy distribution). | **Port as-is.** Useful for monitoring. No manemus-specific dependencies. |
| `seed_brain_from_json_cluster_loader.py` | 263 | Loads seed brain from JSON cluster files. | **Replace.** mind-mcp uses `seed_brain_from_source_docs_dynamic_generator.py` instead. Retain the load-from-JSON interface for brain import/export. |
| `docchain_to_brain_cluster_converter.py` | 467 | Converts doc chains to brain graph clusters. | **Evaluate.** May be useful for mind-mcp's doc-based brain seeding. Lower priority. |
| `docwatch_brain_sync_daemon.py` | 342 | Watches doc filesystem changes and syncs to brain graph. | **Defer to v2.** Not needed for initial wiring. |

---

## Phase B Review Corrections Applied

The following corrections from `docs/reviews/REVIEW_F4_F5_Coherence.md` (7 issues found, 5 fixed) are now reflected in this plan:

### ISSUE 1 (CRITICAL): Tick cycle step numbering

The canonical 17-step tick ordering from `docs/schema/schema.yaml` is authoritative. The ALGORITHM_L1_Wiring.md Section 2.2 has been corrected to match. The manemus tick runner (`tick_runner_l1_cognitive_engine.py`) uses a slightly different internal ordering; during porting, its `tick()` method must be aligned with the schema ordering:

```
Step  1 (L14): LIMBIC_UPDATE
Step  2 (L1):  INJECT
Step  3 (L14): MODULATE
Step  4 (L2+L8): PROPAGATE
Step  5 (L3):  DECAY
Step  6 (L9):  INHIBIT
Step  7 (L4+L13): COMPETE
Step  8 (L5):  REINFORCE
Step  9 (L6):  CONSOLIDATE
Step 10 (L7):  FORGET
Step 11 (L10): CRYSTALLIZE
Step 12 (L17): CHECK_DESIRE
Step 13 (L15): BOREDOM
Step 14 (L16): FRUSTRATION
Step 15 (L11): ORIENT
Step 16:       EMIT
Step 17:       CONSUME
```

**Porting action:** The manemus tick runner's `tick()` method starts with INJECT, not LIMBIC_UPDATE. During porting, reorder to put LIMBIC_UPDATE first and add MODULATE as step 3. The individual law implementations are correct; only the orchestration order in the runner needs adjustment.

### ISSUE 4: emotional_charge removed from FalkorDB schema

The FalkorDB node upsert in ALGORITHM_L1_Wiring.md Section 7.2 no longer references `emotional_charge`. Limbic state is tracked via drives, not a single float. The manemus `models.py` Node dataclass correctly uses drive-affinity dimensions (`goal_relevance`, `novelty_affinity`, `care_affinity`, `achievement_affinity`, `risk_affinity`) instead.

### ISSUE 5: FalkorDB link upsert fields completed

The `_upsert_link` Cypher template now includes all LinkBase fields: `relation_kind, weight, energy, stability, recency, affinity, aversion, trust, friction, polarity_ab, polarity_ba, valence, hierarchy, permanence`. This is critical for F4 trust decay calculations that depend on `stability` surviving restarts.

---

## File-Level Plan

### Phase A: Port L1 Engine from manemus (REPLACES old Phase 1)

This phase copies and adapts the core engine from manemus. No rebuild needed.

| Action | Source (manemus) | Target (mind-mcp) | Adaptation |
|--------|-----------------|-------------------|------------|
| COPY | `runtime/cognition/__init__.py` | `runtime/cognition/__init__.py` | Update exports if needed |
| COPY | `runtime/cognition/models.py` | `runtime/cognition/models.py` | None expected. Verified: uses only stdlib (`dataclasses`, `enum`, `time`, `typing`). No manemus-specific imports. |
| COPY | `runtime/cognition/constants.py` | `runtime/cognition/constants.py` | None expected. Pure `os.environ` lookups. No imports beyond `os`. |
| COPY+ADAPT | `runtime/cognition/tick_runner_l1_cognitive_engine.py` | `runtime/cognition/tick_runner_l1_cognitive_engine.py` | **Reorder tick steps** to match schema canonical ordering (LIMBIC_UPDATE first, add MODULATE step 3). Manemus runner starts with INJECT. Internal law calls are correct; only the `tick()` method orchestration order changes. |
| COPY | `runtime/cognition/laws/__init__.py` | `runtime/cognition/laws/__init__.py` | None |
| COPY | `runtime/cognition/laws/law_01_energy_injection.py` | `runtime/cognition/laws/law_01_energy_injection.py` | None expected. Verify import paths resolve. |
| COPY | `runtime/cognition/laws/law_02_propagation.py` | `runtime/cognition/laws/law_02_propagation.py` | None |
| COPY | `runtime/cognition/laws/law_03_energy_decay.py` | `runtime/cognition/laws/law_03_energy_decay.py` | None |
| COPY | `runtime/cognition/laws/law_04_attentional_competition.py` | `runtime/cognition/laws/law_04_attentional_competition.py` | None |
| COPY | `runtime/cognition/laws/law_05_coactivation_reinforcement.py` | `runtime/cognition/laws/law_05_coactivation_reinforcement.py` | None |
| COPY | `runtime/cognition/laws/law_06_consolidation.py` | `runtime/cognition/laws/law_06_consolidation.py` | None |
| COPY | `runtime/cognition/laws/law_07_forgetting.py` | `runtime/cognition/laws/law_07_forgetting.py` | None |
| COPY | `runtime/cognition/laws/law_09_inhibition.py` | `runtime/cognition/laws/law_09_inhibition.py` | None |
| COPY | `runtime/cognition/laws/law_13_to_18_limbic_engine.py` | `runtime/cognition/laws/law_13_to_18_limbic_engine.py` | None expected. Verify valence update (Law 18) constants match F4 expectations. |
| COPY | `runtime/cognition/tests/test_minimal_kernel_invariants.py` | `runtime/cognition/tests/test_minimal_kernel_invariants.py` | Run tests after copy. All 19 must pass. |
| COPY | `runtime/cognition/brain_health_score_periodic_calculator.py` | `runtime/cognition/brain_health_score_periodic_calculator.py` | Useful for monitoring. No adaptation needed. |

**Verification gate:** After copying, run `pytest runtime/cognition/tests/test_minimal_kernel_invariants.py` — all 19 tests must pass before proceeding to Phase B.

**Estimated effort:** 1-2 hours (copy, fix import paths if any, reorder tick steps, run tests).

### Phase B: Stimulus Injection Pipeline

| Action | Target Path | Description |
|--------|-------------|-------------|
| CREATE | `runtime/cognition/stimulus_router.py` | Stimulus Router: classify, segment, embed, dedup, build Stimulus objects. The `Stimulus` dataclass already exists in `tick_runner_l1_cognitive_engine.py` — import from there. |
| CREATE | `runtime/cognition/concept_extractor.py` | Concept extraction from text (sentence segmentation, entity extraction, cognitive type inference) |
| CREATE | `runtime/cognition/anti_loop_protection.py` | 3-layer anti-loop: refractory, diminishing returns, novelty gate |
| ADAPT | manemus `l1_live_integration_bridge.py` | Extract the `inject_message()` pattern and `_make_stimulus()` logic. Rewrite against mind-mcp's dispatcher rather than manemus's telegram_bridge. |
| MODIFY | `runtime/orchestrator/dispatcher.py` | Add `_run_physics_ticks()`, `_ensure_citizen_engine()`, physics tick scheduling |

### Phase C: WM-to-Prompt Integration

| Action | Target Path | Description |
|--------|-------------|-------------|
| CREATE | `runtime/cognition/wm_prompt_serializer.py` | Serialize WM nodes + limbic state + orientation into prompt section |
| MODIFY | `runtime/citizens/__init__.py` | Call `serialize_wm_to_prompt()` inside `build_citizen_prompt()` |
| CREATE | `runtime/cognition/orientation_taxonomy.py` | Orientation descriptions, prompt modifiers, computation from graph state. Note: manemus tick runner has inline `_compute_orientation()` with 7 orientations (`explore, create, care, verify, rest, socialize, act`). The ALGORITHM_L1_Wiring.md defines 6 orientations (`take_care, create, verify, explore, rest, escalate`). Reconcile during porting — prefer the ALGORITHM spec but verify manemus engine behavior. |

### Phase D: Post-Action Feedback

| Action | Target Path | Description |
|--------|-------------|-------------|
| ADAPT | manemus `l1_autonomous_action_dispatcher.py` | Extract action parsing and routing logic. Adapt executor bindings to mind-mcp's channel integrations. |
| CREATE | `runtime/cognition/feedback_injector.py` | Post-session feedback: self-stimulus injection, CONSUME step, limbic shifts |
| MODIFY | `runtime/orchestrator/dispatcher.py` | In `_collect_completed_futures()`, call `inject_post_action_feedback()` |

### Phase E: Embedding Integration

| Action | Target Path | Description |
|--------|-------------|-------------|
| MODIFY | `runtime/cognition/stimulus_router.py` | Use `OpenAIEmbeddingAdapter` for real embeddings |
| VERIFY | `runtime/cognition/laws/law_01_energy_injection.py` | Manemus Law 1 (861 lines) already handles embedding-based similarity for dedup. Verify it uses cosine similarity correctly with stored embeddings. |
| NO CHANGE | `runtime/infrastructure/embeddings/openai_adapter.py` | Already works. Just wire it. |

### Phase F: FalkorDB Persistence

| Action | Target Path | Description |
|--------|-------------|-------------|
| CREATE | `runtime/cognition/falkordb_checkpointer.py` | Hybrid persistence: dirty tracking, periodic flush, load-on-boot. Replaces manemus's JSON file persistence from `l1_live_integration_bridge.py`. |
| CREATE | `runtime/cognition/graph_schema_setup.py` | Create FalkorDB indexes, schema validation for brain graphs |
| MODIFY | `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Mark nodes/links dirty after mutation, call checkpointer |
| NO CHANGE | `runtime/infrastructure/database/falkordb_adapter.py` | Already works. Instantiate per citizen graph name. |

**FalkorDB node schema** (per review corrections — no `emotional_charge`, full drive-affinity dimensions):

```cypher
CREATE (n:Node {
    id: STRING, name: STRING,
    node_type: STRING,       -- actor|moment|narrative|space|thing
    type: STRING,            -- cognitive subtype: memory|concept|narrative|value|process|desire|state
    weight: FLOAT, energy: FLOAT, stability: FLOAT, recency: FLOAT,
    synthesis: STRING, content: STRING,
    embedding: LIST OF FLOAT,
    self_relevance: FLOAT, partner_relevance: FLOAT,
    novelty_affinity: FLOAT, goal_relevance: FLOAT,
    care_affinity: FLOAT, achievement_affinity: FLOAT, risk_affinity: FLOAT,
    activation_count: INT,
    created_at_s: INT, last_activated_s: INT
})
```

**FalkorDB link schema** (per review corrections — all LinkBase fields):

```cypher
CREATE (a)-[:LINK {
    id: STRING,
    relation_kind: STRING,
    weight: FLOAT, energy: FLOAT, stability: FLOAT, recency: FLOAT,
    affinity: FLOAT, aversion: FLOAT,
    trust: FLOAT, friction: FLOAT,
    polarity_ab: FLOAT, polarity_ba: FLOAT,
    valence: FLOAT, hierarchy: FLOAT, permanence: FLOAT
}]->(b)
```

### Phase G: Seed Brain Generation

| Action | Target Path | Description |
|--------|-------------|-------------|
| MODIFY | `runtime/seed_brain_from_source_docs_dynamic_generator.py` | Add per-citizen overlay: role processes, drive baselines, relational seeds |
| CREATE | `runtime/cognition/citizen_brain_seeder.py` | Orchestrate: generate base + overlay, embed all nodes, persist to FalkorDB |
| COPY | `.mind/citizens/` from manemus | 44 citizen identity directories |
| EVALUATE | manemus `seed_brain_from_json_cluster_loader.py` | Retain JSON load interface for brain import/export between environments |

### Phase H: Emotion Calibration

| Action | Target Path | Description |
|--------|-------------|-------------|
| MODIFY | `runtime/cognition/laws/law_13_to_18_limbic_engine.py` | Add anxiety coupling formula, satisfaction decay, frustration escalation threshold |
| MODIFY | `runtime/cognition/constants.py` | Add: `ANXIETY_COUPLING_RATE`, `SATISFACTION_DECAY_RATE`, `FRUSTRATION_ESCALATION_THRESHOLD`, `FRUSTRATION_SUSTAINED_TICKS` |

### Phase I: Production Cutover

| Action | Target Path | Description |
|--------|-------------|-------------|
| VERIFY | `Dockerfile` | Ensure L1 cognition module is included in Docker image |
| VERIFY | `render.yaml` | Ensure env vars for physics tick interval, embedding API key, FalkorDB connection |
| CREATE | `scripts/migrate_from_manemus.sh` | Migration script: copy citizen dirs, export/import graph state |
| CREATE | `scripts/seed_all_citizens.py` | Batch seed 44 citizen brains |
| MODIFY | `home_server.py` | Ensure physics engines start in lifespan startup |

---

## Porting Plan: manemus to mind-mcp

### What Copies Directly (no adaptation)

These files have zero manemus-specific imports. They depend only on each other and the Python stdlib.

```
manemus/runtime/cognition/             →  mind-mcp/runtime/cognition/
├── __init__.py                        →  __init__.py
├── models.py                          →  models.py
├── constants.py                       →  constants.py
├── brain_health_score_periodic_calculator.py  →  brain_health_score_periodic_calculator.py
├── laws/
│   ├── __init__.py                    →  laws/__init__.py
│   ├── law_01_energy_injection.py     →  laws/law_01_energy_injection.py
│   ├── law_02_propagation.py          →  laws/law_02_propagation.py
│   ├── law_03_energy_decay.py         →  laws/law_03_energy_decay.py
│   ├── law_04_attentional_competition.py  →  laws/law_04_attentional_competition.py
│   ├── law_05_coactivation_reinforcement.py  →  laws/law_05_coactivation_reinforcement.py
│   ├── law_06_consolidation.py        →  laws/law_06_consolidation.py
│   ├── law_07_forgetting.py           →  laws/law_07_forgetting.py
│   ├── law_09_inhibition.py           →  laws/law_09_inhibition.py
│   └── law_13_to_18_limbic_engine.py  →  laws/law_13_to_18_limbic_engine.py
└── tests/
    └── test_minimal_kernel_invariants.py  →  tests/test_minimal_kernel_invariants.py
```

All imports within these files use relative imports (`from .constants import ...`, `from .models import ...`, `from .laws.law_02_propagation import ...`). The package structure is identical, so import paths resolve without changes.

### What Needs Adaptation During Copy

**`tick_runner_l1_cognitive_engine.py` (824 lines)**

Specific changes:
1. **Reorder `tick()` method** — Move LIMBIC_UPDATE to step 1 (currently happens mid-tick in manemus). Insert MODULATE as step 3. The manemus runner calls law functions in this order: inject, propagate, decay, compete, reinforce, inhibit, consolidate, forget, limbic, orient, emit, consume. The schema-canonical order puts limbic first, then inject, then modulate, then propagate, etc. The law function implementations remain the same; only the call sequence in the `tick()` method changes.
2. **Orientation mapping** — Manemus uses 7 orientations (`explore, create, care, verify, rest, socialize, act`). Schema specifies 6 (`take_care, create, verify, explore, rest, escalate`). Rename `care` to `take_care`, merge `socialize` into `take_care`, rename `act` to map to `create` or remove. Update `_TYPE_ORIENTATION_MAP` and `_DRIVE_ORIENTATION_MAP`.
3. **Remove manemus-specific fallback stubs** — The try-import pattern is good (allows incremental development), but once all laws are present, consider making imports strict.

### What Gets Built New in mind-mcp (Not in manemus)

| File | Est. Lines | Why New |
|------|-----------|---------|
| `stimulus_router.py` | 250 | Manemus does stimulus conversion inside `l1_live_integration_bridge.py`. mind-mcp needs a standalone router that integrates with the different dispatcher. |
| `concept_extractor.py` | 150 | Sentence segmentation + keyword extraction. Not separated in manemus. |
| `anti_loop_protection.py` | 100 | Self-stimulus loop prevention. Inline in manemus bridge. |
| `wm_prompt_serializer.py` | 200 | Manemus has `get_prompt_context()` in the bridge. mind-mcp needs standalone serializer for `build_citizen_prompt()`. |
| `orientation_taxonomy.py` | 150 | Prompt modifiers for orientations. New design in ALGORITHM_L1_Wiring.md. |
| `feedback_injector.py` | 120 | Post-action feedback. Inline in manemus dispatcher. |
| `falkordb_checkpointer.py` | 250 | Manemus uses JSON file persistence. mind-mcp uses FalkorDB. |
| `graph_schema_setup.py` | 80 | FalkorDB index/schema creation. New. |
| `citizen_brain_seeder.py` | 200 | Orchestrate base + overlay brain seeding. New orchestration layer. |

**Total new wiring code:** ~1,500 lines.

### What Gets Adapted from manemus (Partial Rewrite)

| manemus File | mind-mcp Target | Reuse % | Notes |
|-------------|----------------|---------|-------|
| `l1_live_integration_bridge.py` (509 lines) | Split into `stimulus_router.py` + dispatcher modifications | ~30% | Extract `_make_stimulus()`, `inject_message()`, `get_prompt_context()` patterns. Discard JSON persistence, threading model (mind-mcp uses async), manemus-specific config loading. |
| `l1_autonomous_action_dispatcher.py` (653 lines) | `feedback_injector.py` + action routing in dispatcher | ~40% | Action type parsing and routing table are reusable. Executor bindings (Telegram, Discord) need rewiring to mind-mcp channel integrations. |
| `seed_brain_from_json_cluster_loader.py` (263 lines) | `citizen_brain_seeder.py` | ~50% | JSON loading logic reusable. Overlay generation is new. |

---

## Existing Files That Need Modification

| File | Lines | What Changes |
|------|-------|-------------|
| `runtime/orchestrator/dispatcher.py` | 273 | Add physics tick scheduling, citizen engine management, post-action feedback injection |
| `runtime/citizens/__init__.py` | ~200 | Add WM serialization call in `build_citizen_prompt()` |
| `runtime/seed_brain_from_source_docs_dynamic_generator.py` | ~600 | Add per-citizen overlay generation |
| `home_server.py` | ~300 | Initialize physics engines at startup, shutdown checkpoint |
| `Dockerfile` | ~50 | Verify cognition module included |
| `render.yaml` | ~40 | Add env vars for physics configuration |

---

## New Files to Create (Revised Estimate)

| File | Est. Lines | Purpose |
|------|-----------|---------|
| `runtime/cognition/stimulus_router.py` | 250 | Stimulus pre-processing pipeline |
| `runtime/cognition/concept_extractor.py` | 150 | Text-to-concept extraction |
| `runtime/cognition/anti_loop_protection.py` | 100 | Self-stimulus anti-loop gates |
| `runtime/cognition/wm_prompt_serializer.py` | 200 | WM-to-prompt formatting |
| `runtime/cognition/orientation_taxonomy.py` | 150 | Orientation definitions + computation |
| `runtime/cognition/feedback_injector.py` | 120 | Post-action feedback loop |
| `runtime/cognition/falkordb_checkpointer.py` | 250 | Hybrid persistence |
| `runtime/cognition/graph_schema_setup.py` | 80 | FalkorDB schema initialization |
| `runtime/cognition/citizen_brain_seeder.py` | 200 | Orchestrate brain seeding per citizen |
| `scripts/migrate_from_manemus.sh` | 50 | Migration helper |
| `scripts/seed_all_citizens.py` | 80 | Batch seeder |

**Total new code:** ~1,630 lines (wiring only). The L1 engine itself (4,528 lines of core + 798 lines of tests) ports from manemus with minimal adaptation.

**Combined effort:** ~1,630 new lines + ~200 lines of tick runner adaptation + ~500 lines of bridge adaptation = ~2,330 lines of work.

---

## Integration Points (Known from manemus Code)

### 1. Stimulus Entry: Message to Law 1

Manemus `l1_live_integration_bridge.py` shows the pattern:

```python
# bridge.inject_message("citizen_handle", "text", is_social=True)
#   → creates Stimulus(content=text, energy_budget=1.0, is_social=True, ...)
#   → calls tick_runner.inject_stimulus(stimulus)
#   → optionally triggers an immediate tick
```

mind-mcp equivalent: `dispatcher.py` receives messages, calls `stimulus_router.route_stimulus()`, which returns `Stimulus` objects, then calls `engine.inject_stimulus()`.

### 2. Tick Scheduling

Manemus uses a background thread with `threading.Timer` for periodic ticks. mind-mcp should use the existing dispatcher tick loop (`Dispatcher._tick()`) to schedule physics ticks on a timer, as specified in ALGORITHM_L1_Wiring.md Section 2.1.

### 3. Prompt Context Export

Manemus `l1_live_integration_bridge.py` exports:

```python
def get_prompt_context(citizen_handle: str) -> dict:
    # Returns: orientation, limbic snapshot, wm_summary, wm_nodes, arousal_regime
```

mind-mcp equivalent: `wm_prompt_serializer.py` consumes the same data, but formats it as a markdown string for injection into `build_citizen_prompt()`.

### 4. Action Dispatch

Manemus `l1_autonomous_action_dispatcher.py` parses `action_emitted` strings from the tick runner (format: `"action_type:argument_string"`) and routes to executors. Supports: `tg:`, `dm:`, `discord:`, `spawn:`, `backlog:`, `explore:`, `introduce:`, `project:`, `social:`, `bash:`. Results re-injected as stimuli.

mind-mcp needs the same routing but against its own channel integrations.

### 5. Persistence Bridge

Manemus persists to JSON files (`brain_full.json`). mind-mcp persists to FalkorDB. The `CitizenCognitiveState` dataclass is the same in both — the serialization target changes, not the data model.

### 6. F4 (Trust Mechanics) Integration Boundary

Per the cross-review (`REVIEW_F4_F5_Coherence.md`):
- F5 produces drive snapshots at tick boundaries (step 1 LIMBIC_UPDATE and step 17 CONSUME)
- F4 consumes them for limbic delta computation
- F5 FalkorDB persistence stores `trust`, `friction`, `stability`, `affinity`, `aversion` on links (required by F4 for trust decay and tempering formulas)
- Law 18 (relational valence) in `law_13_to_18_limbic_engine.py` handles trust/friction/affinity/aversion updates during PROPAGATE (step 4), not as a discrete step

---

## Dependency Graph (Revised)

```
Phase A: Port L1 Engine from manemus
    ↓
Phase B: Stimulus Injection Pipeline ──┐
    ↓                                   │
Phase C: WM-to-Prompt Integration       │
    ↓                                   │
Phase D: Post-Action Feedback       ←───┘
    ↓
Phase E: Embedding Integration (can parallel with B-D)
    ↓
Phase F: FalkorDB Persistence (can parallel with B-E)
    ↓
Phase G: Seed Brain Generation (needs E+F)
    ↓
Phase H: Emotion Calibration (needs A)
    ↓
Phase I: Production Cutover (needs all above)
```

Phase A is now 1-2 hours instead of 5 days. This unblocks everything else.

Phases B-D are sequential (each builds on the previous). Phases E-F can run in parallel with B-D. Phase G needs E+F. Phase H only needs Phase A. Phase I needs everything.

---

## Risk Assessment (Revised)

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| ~~L1 engine code missing entirely~~ | ~~HIGH~~ | ~~MEDIUM~~ | **RESOLVED.** Engine located in manemus. 7,256 lines, 19/19 tests passing. |
| Tick step reordering introduces bugs | MEDIUM | LOW | Manemus tests cover law invariants, not step ordering. Add integration test for canonical ordering after reorder. |
| Manemus imports break in mind-mcp context | LOW | LOW | All core files use relative imports and stdlib only. Run tests immediately after copy. |
| Orientation mismatch (7 vs 6 orientations) | LOW | MEDIUM | Reconcile during tick runner adaptation. Document mapping. Not a blocker. |
| FalkorDB can't handle 44 x 500 nodes | MEDIUM | LOW | Each citizen graph is small (~500 nodes). 44 separate graphs. FalkorDB handles this easily. |
| Embedding costs exceed budget | MEDIUM | LOW | Batch + cache strategy. ~$63/day for 44 citizens. Controllable via tick frequency. |
| WM injection confuses Claude | MEDIUM | MEDIUM | Start with minimal WM (3 nodes). Test prompt quality. Iterate on formatting. |
| Orientation has no effect on behavior | LOW | HIGH | Claude may ignore soft modifiers. May need stronger prompt engineering. |
| Checkpoint data loss on crash | LOW | MEDIUM | Accept loss of N ticks (configurable). FalkorDB is append-only for nodes. |
| manemus cutover breaks production | HIGH | MEDIUM | Parallel run period (2 weeks). Rollback plan via DNS revert (60s TTL). |
