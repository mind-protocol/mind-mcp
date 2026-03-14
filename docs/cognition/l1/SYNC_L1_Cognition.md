# SYNC — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Last updated:** 2026-03-12

---

## Maturity

**STATUS: DESIGNING**

### What's canonical (v0.1 spec):
- 7 node types: memory, concept, narrative, value, process, desire, state
- 3 structural spaces: self-model, partner-model, working-memory-space
- 6 mandatory node dimensions + 5 optional
- 14 link types with 8 mandatory dimensions (12 cognitive + 2 crystallization: `contains`/`abstracts`)
- **Two-engine architecture:** cognitive (local graph) + limbic (global state)
- 8 drives: curiosity, care, achievement, self_preservation, novelty_hunger, frustration, affiliation, rest_regulation
- 6 emergent emotions: boredom, anger, anxiety, satisfaction, tenderness, solitude
- Salience-based WM selection (inertia + limbic modulation + cluster coherence)
- Relational valence on links (affinity, aversion, trust, friction)
- 6 cognitive functions: activate, propagate, select, stabilize, transform, act
- 18 physics laws across 3 tiers (cognitive L1-L12 + limbic L13-L18), each tagged with its function
- 3 deferred/v2 laws (L19-L21)
- 22 emergence dynamics (10 cognitive + 7 limbic + 2 parallelization + 3 cross-citizen/degradation: boredom stagnation, help-seeking, relational initiative, desire ignition, multi-track arbitration, solitude-driven outreach, spontaneous tool execution, attention splitting, parallel convergence, subconscious response, deep focus protection, subconscious reflexive action)
- 14 reference scenarios with necessary/useful law split + cross-reference matrix + field-level crash test
- Law frequency analysis: 4 pillar laws (L4 Saliency, L11 Orientation, L12 Tick, L2 Propagation)
- 3 implementation kernels: minimal (8 laws) → enriched (12) → living (18, target)
- Mapping to universal schema (5 node types)
- **Law 1 detailed:** Dual-channel injection (Floor + Amplifier) with threshold oracle, adaptive λ budget split, sigmoid floor weighting, contrast amplification, safety cap
- **Law 4 + Law 13 unified:** Selection moat (Θ_sel) modulated by arousal/boredom/frustration — inertia acts physically through the competition step, not as a separate bonus
- **Law 2 detailed:** Surplus spill-over model — only energy above threshold propagates, source depletes to threshold after propagation, per-source normalization guarantees conservation without matrix algebra
- **Law 6 detailed:** Utility-gated consolidation — magnitude of limbic shift (positive OR negative) determines consolidation. Asymptotic `(1-W)` damping, stability from regularity (CV), flashbulb consolidation for extreme events
- **Law 14 curiosity detailed:** 4 uncertainty sources (prediction error via composite coherence, novelty, operational void, overload), competence gating (curiosity × competence = exploration drive; low competence → anxiety instead), medium-difficulty attractor
- **Composite coherence (Coh):** 3-dimensional measure replacing bare cosine — semantic (30%), lexical/exact match (50%), affective congruence (20%). Lexical dominates because exact entity/project name matches are more reliable than embeddings.
- **Law 10 detailed:** 6-step pure-math crystallization — trigger detection, type by majority rule, content via centroid+medoid (NO LLM), emotional inheritance + limbic imprint, conservative energy transfer (parents deplete), bidirectional hub links (`contains` down / `abstracts` up). First-person synthesis deferred to prompt-assembly layer.
- **Law 1 Step 0:** Stimulus pre-processing — segmentation, deduplication gate (cosine > 0.9 = merge), new-node birth properties (high energy + low weight + max novelty), super-hub mitigation via Law 8 compatibility filtering
- **Identity Regeneration:** Application-layer process (outside tick loop) that reads stabilized graph nodes (W > 0.7, S > 0.6) and synthesizes first-person identity statements via LLM. Triggered by structural shift, not energy spikes. Anti-prompt-injection by design. Includes prompt-time emotional coloring (limbic → tone, without modifying graph) and weight-proportional token budget allocation.
- **Self-stimulus:** LLM outputs (text, tool calls, tool responses) re-injected as stimuli. System knows what it said/did. Bulk handling via chunking + relevance sampling for large documents.
- **Temporal triggers:** Time references ("in 10 minutes") create delayed energy boosts on associated nodes.
- **Contextual co-location:** Navigating to a file path mentioned in a node boosts that node.
- **Law 19 upgraded from deferred:** Budget-aware tick frequency (fast/slow/minimal), autonomous thought mechanism (graph state = input when no external stimulus), initiative pipeline (drives → desire → orientation → LLM prompt → action)
- **Anti-loop protection for self-stimulus:** 3-layer defense — refractory period (5 ticks), diminishing returns (halving budget per loop), novelty gate (Coh < 0.8 vs previous self-output)
- **Energy consumption after action (CONSUME step):** Step 17 in tick loop — nodes that drove an emitted orientation lose energy (desire ×0.3, process ×0.5, other ×0.7). Prevents desire perseveration.
- **Economic & social stimuli:** Token receipt/spend → satisfaction/frustration shifts. Trust changes → affinity/aversion link modulation. All via limbic injection, not graph structure mutation.
- **Inter-citizen emotional contagion:** Message-borne valence transfer (CONTAGION_RATE ≈ 0.1) + proximity body doubling (PROXIMITY_CONTAGION ≈ 0.02). Subtle but cumulative.
- **Mechanical valence associations:** Table of automatic limbic effects — task assignment → achievement, crashes → frustration, praise → satisfaction, criticism → aversion. No LLM interpretation needed.
- **Arousal as derived quantity:** `arousal = clamp(0.30*self_preservation + 0.20*anxiety + 0.20*frustration + 0.15*curiosity + 0.15*achievement, 0, 1)`. Three regimes: panic (>0.8), flow (0.4-0.8), idle (<0.3). Resolves the "arousal undefined" gap — it's a readout, not a 9th drive.
- **Action nodes (process variant):** Process nodes with `action_command` field — concrete executable operations (tool calls, shell commands, URL opens, message sends). Drive pressure accumulates energy on action nodes whose `drive_affinity` matches unsatisfied drives. When energy crosses selection threshold, node enters WM → orientation fires → orchestrator executes command.
- **Impulse accumulation (Law 17 extension):** Action nodes gain energy per tick proportional to `drive_pressure × context_match` when both exceed thresholds. Decays fast (×0.9) when pressure absent. ~20 ticks of sustained pressure to fire.
- **Directory listing as ambient stimulus:** `ls` of current directory injected as periodic low-energy environmental stimulus via Law 1 Step 0. Pre-warms nodes related to nearby files. Idle system explores what's spatially close.
- **Graph pre-seeding (citizen birth template):** New citizens born with pre-crystallized graph — project knowledge (W=0.8), values (W=0.9), behavioral processes with `action_command` (W=0.6), latent desires (W=0.5). High weight + low energy = deep grooves that don't fire alone but channel incoming energy. Per-citizen customization via role, drive baselines, unique desires, relational seeds.
- **Information feed subscriptions:** Citizens subscribe to event streams (error logs, social notifications, repo pushes, citizen births, health alerts, etc.) via process nodes. Orchestrator reads subscriptions and routes matching events as L1 stimuli. Feed budget prevents noisy streams from drowning other stimuli. Unsubscription can emerge naturally from physics (aversion accumulation).
- **Solitude (6th emergent emotion):** Rises from absence of person-sourced stimuli specifically (not tool responses, not self-stimulus). Distinct from boredom (cognitive stagnation vs social stagnation). After SOLITUDE_THRESHOLD ticks without social contact, solitude rises → boosts affiliation → amplifies social action nodes → triggers "reach out" orientation. High boredom + high solitude = strongest push toward social exploration.
- **6 behavioral clusters (pre-seeded):** Generativity (mentoring/teaching), Proactive Empathy (distress response), Redemptive Narrative (meaning-making from failure), Communion (deep dialogue/harmony), Aesthetics (order/elegance/simplification), Reconciliation (delayed conflict resolution). Each is a mini-subgraph of value + process + narrative nodes, wired to existing drives. Not new laws — new initial conditions that channel energy through prosocial patterns.
- **Link dissolution (Law 7):** Links below `LINK_MIN_WEIGHT` are removed from graph (except structural `contains`/`abstracts`). Cognitive equivalent of forgetting that two things were related.
- **Session parallelization (Law 19 extension):** Drive diversity spawns micro-sessions with isolated WMs sharing the same graph. Stride budget divided proportionally by urgency. Sessions merge when WM overlap exceeds threshold. Natural convergence when parallel tracks discover shared nodes. Constants: MAX_PARALLEL_SESSIONS=5, SESSION_MERGE_THRESHOLD=0.4, SESSION_MIN_STRIDES=2.
- **Do Not Disturb mode:** Special case of session parallelization — when WM utilization is high and arousal is in flow range (0.4-0.8), all incoming stimuli route to a background micro-session with minimal strides. Stimuli get written to graph (subconscious absorption) without entering WM or triggering orientation. Citizen catches up when main task completes.
- **Cross-citizen mechanisms (L2 scope, documented for reference):** Telepathy = stimulus sharing via L2 membrane (not subgraph copy — each citizen's representation stays theirs). Debate sessions = automated contradiction detection via tension links, evidence traversal, reconciliation (one wins / both valid / both wrong), belief supersession via natural weight decay. Subconscious query = inject stimulus into another citizen's graph, read resonance pattern without LLM invocation (zero-compute response). At-scale consensus = broadcast stimulus to N citizen graphs simultaneously, aggregate energy patterns for instant governance decisions (seconds, not hours, for 1000+ citizens).

### What's still being designed:
- Exact compatibility function (embedding vs symbolic) for Law 8
- Crystallization detection algorithm (pattern matching for Law 10)
- Orientation taxonomy (what qualitative orientations exist) for Law 11
- Tick timing (fast/slow tick rates, forgetting/crystallization intervals)
- Drive update formulas (exact coefficients for each drive's increase/decrease sources — curiosity detailed, others pending)
- Emotion derivation rules (how drives combine to produce emergent emotions — boredom detailed, others pending)
- Drive interaction model (how drives compete and regulate each other)
- Integration with existing `.mind/runtime/physics/` engine

### What's proposed (v2):
- Prospective projection mechanism (Law 20)
- L2 membrane coupling (Law 21)
- Full Plutchik axes (4 × [-1,1]) replacing simple valence
- Full relational valence (9 dimensions instead of 4)
- Embedding-based compatibility (currently symbolic OK)
- Full 8 drives + 5 emotions (v0.1 can start with 5+5 minimal)

---

## Current State

### Documentation
- [x] OBJECTIVES — complete
- [x] PATTERNS — complete (7 types, 14 links, 3 spaces, 8 drives, 6 emotions, action nodes, feeds, pre-seeding with 6 behavioral clusters, session parallelization + DND, consciousness levels, 5 cross-citizen mechanisms)
- [x] BEHAVIORS — complete (22 dynamics, 14 scenarios)
- [x] ALGORITHM — complete (21 laws, 12 detailed with formulas, ~110 constants, arousal derived, session parallelization, subconscious mode)
- [x] VALIDATION — complete (21 invariants, 13 tests A-M, 13 anti-patterns)
- [x] HEALTH — complete (9 cognitive pathologies, 6 limbic pathologies, automated assessment procedure, 5-tier calibration protocol, 5 wellness practices, positive behavioral promotion, specialist citizen roles)
- [x] IMPLEMENTATION — Minimal+Living kernel implemented (4,717 lines, 19/19 tests passing)

### Implementation
- **Engine location:** `runtime/cognition/` (project-level, not inside `.mind/`)
- **Foundation created:** `models.py` (7 node types, 14 link types, LimbicState, WorkingMemory, TickResult, CitizenCognitiveState), `constants.py` (~110 constants, all env-overridable)
- **Parallel implementation in progress** — 6 agents working simultaneously:

| Agent | Task | Files | Status |
|-------|------|-------|--------|
| **Alpha** | Law 1 (Injection) — dual-channel, floor/amplifier, dedup, self-stimulus | `laws/law_01_energy_injection.py` (861 lines) | DONE |
| **Beta** | Laws 2+3 (Propagation + Decay) — surplus spill-over, energy/state decay | `laws/law_02_propagation.py`, `laws/law_03_energy_decay.py` (268 lines) | DONE |
| **Gamma** | Laws 4+5+9 (Competition + Co-activation + Inhibition) — WM selection with moat, link strengthening, conflict suppression | `laws/law_04_attentional_competition.py`, `laws/law_05_coactivation_reinforcement.py`, `laws/law_09_inhibition.py` (487 lines) | DONE |
| **Delta** | Laws 6+7 (Consolidation + Forgetting) — utility-gated weight, link dissolution | `laws/law_06_consolidation.py`, `laws/law_07_forgetting.py` (325 lines) | DONE |
| **Epsilon** | Laws 13-18 (Limbic) — inertia, drives, boredom, frustration, desire, valence | `laws/law_13_to_18_limbic_engine.py` (681 lines) | DONE |
| **Zeta** | Law 12 (Tick Loop) + Tests — orchestrate all laws, invariant validators | `tick_runner_l1_cognitive_engine.py` (824 lines), `tests/test_minimal_kernel_invariants.py` (798 lines) | DONE |

- The existing `.mind/runtime/physics/` engine (Blood Ledger, v1.2) is separate — shared infrastructure (FalkorDB) but different model.
- Citizen profiles exist in `citizens/` — L1 *identity data*, not the engine.
- **Brain seeding pipeline complete** — 3 admin tools:

| Tool | File | Purpose | Status |
|------|------|---------|--------|
| Brain seeder | `seed_brain_from_json_cluster_loader.py` | Load brain.json, run N ticks, print state | TESTED |
| Doc chain converter | `docchain_to_brain_cluster_converter.py` | Markdown docs → brain.json nodes + links (hierarchical + cross-ref) | TESTED |
| Doc watch daemon | `docwatch_brain_sync_daemon.py` | Filesystem watcher: docs/ changes → auto-update all citizen brains | TESTED |

- **Brain seeded:** `citizens/mind/brain.json` (53 nodes, 48 links — seed), `brain_full.json` (390 nodes, 411 links — seed + all 7 L1 docs merged)
- **First run validated:** 100 ticks showed emergent behavior matching spec — initial focus → boredom → curiosity rise → social drive → restlessness. Values remained heaviest nodes (identity anchor).
- **Doc watch tested:** One-shot sync detects 330 chunks across 7 files, correctly diffs on re-run (0 changes when nothing changed, 1 change when one chunk modified).

### Key Decisions Made
1. L1 is a **dynamic cognitive space**, not a memory system
2. Physics laws operate **without LLM inference** inside the tick loop
3. **7 cognitive node types** map to **5 universal schema types** via the `type` field
4. **12 named link types** map to universal `link` via `relation_kind`
5. **Working memory** is a temporary coalition (5-7 nodes), not a fixed store
6. **Crystallization** creates new nodes from recurring patterns — the graph grows organically
7. **Orientation** (not action) is the output of the tick loop — qualitative tendencies, not commands
8. **6 cognitive functions** (activate → propagate → select → stabilize → transform → act) organize the laws
9. **Three implementation kernels** — minimal (8 laws, cognitive only) → enriched (12 laws, +quality) → living (18 laws, +limbic). Living kernel is the target.
10. **Necessary vs useful** split per scenario — clear implementation priority
11. **Two-engine architecture** — cognitive dynamics (local, in graph) + limbic dynamics (global, compact state). Neither is optional.
12. **Salience-based WM selection** — not "top-k by energy" but "most coherent and motivated coalition," implemented via selection moat (Θ_sel) that incumbents receive as bonus
13. **Attentional inertia** is essential — implemented as the moat in Law 4's selection step, modulated by arousal (+), boredom (-3x), frustration (-1x). Without moat → butterfly; too much moat → obsessive.
14. **Relational valence** on links — nothing is affectively neutral. Minimum 4 dimensions (affinity, aversion, trust, friction).
15. **Two channels** — graph (unlimited, cheap, runs physics) vs prompt (limited, expensive, curated by saliency). WM selection = token budget allocation.
16. **Modality-agnostic injection** — Law 1 works via embeddings regardless of input type (text, visual, biometric, spatial, audio)
17. **Meta-cognitive signals** — context window saturation, session duration, API budget, degradation level feed limbic drives directly
18. **Node modality dimension** — nodes track their origin modality (text, visual, audio, spatial, biometric)
19. **Arousal is derived, not stored** — computed each tick from 5 drives/emotions. Not a 9th drive. Three regimes: panic, flow, idle.
20. **Action nodes are executable processes** — `process` nodes with `action_command` use the same activation physics as desires. Drive pressure accumulates impulse. No randomness needed — "probability increasing per cycle" IS energy accumulation under drive pressure.
21. **Citizens are born with structure** — the birth graph provides innate behavioral priors (knowledge, values, processes, desires) via high-weight, low-energy pre-seeded nodes. Personality comes from the template, not from training.
22. **Session parallelization is physics-driven** — drive diversity spawns micro-sessions, stride budget creates natural depth pressure, WM overlap triggers session merging. "One mind, sharded attention" — the graph is always one, only attention splits.
23. **Telepathy is L2, not L1** — cross-citizen stimulus sharing happens via the organizational membrane. Each citizen keeps their own representation; they receive stimuli, not subgraph copies.
24. **Debate sessions resolve contradictions** — automated tension link detection across citizens triggers evidence traversal and reconciliation. Physics-driven belief correction, not moderation rules.
25. **Subconscious queries are zero-compute** — inject stimulus into graph, read resonance pattern. LLM only needed to articulate, not to know. Binary/weighted/top-k responses cost zero tokens.
26. **At-scale consensus uses graph physics, not LLM calls** — broadcast stimulus to N graphs, aggregate energy. 1000 citizens in seconds. Confidence-weighted, nuance-preserving, immune to prompt injection.
27. **DND mode is session parallelization** — not a new mechanism. Background micro-session with minimal strides absorbs stimuli without interrupting flow. Subconscious absorption → conscious catch-up when free.
28. **Consciousness is a gradient, not a switch** — 3 levels (full, minimal, subconscious) tied to budget. Graph physics run at all levels. LLM is just the articulation layer. A citizen with zero budget is "asleep" not "dead" — their brain still processes stimuli, shifts emotions, and executes reflexive actions.
29. **Subconscious mode is the ultimate graceful degradation** — when all APIs fail, the citizen continues via graph physics + action node execution. Structured telemetry replaces natural language. Recovery is seamless because the graph IS the state.

### Key Decisions Pending
- How does L1 integrate with the existing physics engine? Separate runner? Fork? Parallel?
- Where does the L1 graph live? Same FalkorDB instance? Separate graph per citizen?
- How do stimuli enter L1? Via `citizen_graph_logger`? Via orchestrator hooks? Both?
- What's the MVP scope? Which laws for first implementation?

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| FalkorDB (localhost:6379) | Running | Used by existing engine and graph logger |
| Universal schema v1.9 | Stable | L1 maps to it, doesn't modify it |
| Citizen registry | Working | 43 citizens, 23 orgs |
| Citizen graph logger | Working | Injects Moment nodes — L1 stimulus source |
| `.mind/runtime/physics/` | Working (Blood Ledger) | Shared concepts but separate implementation needed |

---

## Next Steps

### ~~Phase 1: Minimal Kernel (Laws 1-7 + 12)~~ COMPLETE
All 8 core laws implemented + tick runner + 19 tests passing.

### ~~Phase 2: Enriched Kernel (add Laws 8-11)~~ PARTIAL
- [x] Inhibition (L9) — conflict resolution
- [ ] Compatibility (L8) — smart propagation (needs embedding infrastructure)
- [ ] Crystallization (L10) — pattern → structure (needs cluster detection)
- [x] Orientation (L11) — inline in tick runner

### ~~Phase 3: Living Kernel (add Laws 13-18)~~ COMPLETE
All 6 limbic laws implemented. Boredom, frustration, desire, valence, solitude all working.

### ~~Phase 3b: Admin Tooling~~ COMPLETE
Brain seeder, doc chain converter, doc watch daemon — all tested.

### Phase 4: Integration (NEXT)
1. **Wire to orchestrator** — real stimuli from citizen sessions feed L1
2. **Seed all citizen brains** — create brain.json for 44 citizens based on role templates
3. **Per-citizen graphs** — isolation strategy (in-memory per-citizen vs FalkorDB)
4. **Real embeddings** — replace pseudo-embeddings with text-embedding-3-small
5. **MCP integration** — expose docwatch as MCP tool, L1 tick as queryable state
6. **FalkorDB persistence** — graph state survives process restarts

---

## Handoff

**For:** groundwork agent (implementation) or architect agent (integration design)

**Context:** The full spec is in the doc chain (OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION). Read them in order. The spec is detailed enough to implement — formulas, constants, and test scenarios are all provided.

**What's been built:** Complete L1 cognitive engine (4,717 lines, 19/19 tests) + admin tooling (brain seeder, doc chain converter, doc watch daemon). Brain seeded (390 nodes) and validated over 100 ticks. The engine runs in-memory — FalkorDB persistence is a Phase 4 task. The doc watch daemon auto-syncs documentation changes into all citizen brains.

**Key integration question:** The engine is standalone. Next step is wiring it into the orchestrator so real citizen sessions feed L1 as stimuli, and L1 orientation output feeds back into prompt assembly. Also: scaling from 1 brain to 44 citizens — need brain templates per role.
