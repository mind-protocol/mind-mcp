# OBJECTIVES -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Status:** DESIGNING (v0.1)

---

## Purpose

Bridge the gap between the v1.x SubEntity physics engine (11.7k lines in `runtime/physics/`) and the v2.0 21-law L1 cognitive model (documented in `docs/cognition/l1/`). Wire the L1 engine into the orchestrator so citizens run on real physics with real stimuli, real embeddings, and persistent graph state.

This module does not redesign the physics. The physics design is complete (ALGORITHM_L1_Physics.md, 21 laws, 18 implemented). This module makes those physics **run in production**: stimuli flow in, working memory flows to prompts, orientations flow to actions, results flow back.

---

## Objectives (Ranked)

### O1: Wire Real Stimuli into L1 (Priority: Critical)

**What:** External events (Telegram messages, tool call results, bridge events, membrane stimuli, alarm firings) must enter L1 as proper Law 1 stimuli -- segmented, deduplicated, energy-budgeted.

**Why:** Without real stimuli, the engine runs in a vacuum. The 100-tick validation (manemus brain) used synthetic stimuli. Production needs the orchestrator to translate every citizen interaction into an L1 injection.

**Tradeoff:** Latency. Stimulus pre-processing (segmentation, dedup, embedding) adds time before a tick can run. Accept ~200ms per stimulus batch vs. the alternative of skipping pre-processing and flooding the graph.

### O2: Inject Working Memory into Citizen Prompts (Priority: Critical)

**What:** The 5-7 nodes selected by Law 4 (attentional competition) must appear in the Claude Code system prompt as contextual priming. The WM bridges graph state to LLM awareness.

**Why:** Without WM injection, the citizen has no memory, no emotional context, no active concerns. It's a blank slate every invocation. WM is the entire point of the cognitive substrate -- saliency-selected awareness.

**Tradeoff:** Token budget. WM injection consumes prompt tokens. A 7-node WM with full synthesis fields could consume 500-1500 tokens. Accept the cost: WM IS the value. Budget allocation should be weight-proportional (Law 12 spec).

### O3: Map Orientation to Action (Priority: High)

**What:** Law 11 produces an orientation (take_care / create / verify / explore / rest / escalate). This orientation must translate into prompt instructions that shape Claude's behavior during the session.

**Why:** Without orientation mapping, the physics compute internal state but never influence the citizen's actual behavior. The citizen "feels" boredom but never acts on it.

**Tradeoff:** Expressiveness vs. constraint. Loose orientation mapping ("you feel curious, explore") vs. strict ("you MUST explore, do NOT produce code"). Start loose -- citizens should feel the pull, not be commanded.

### O4: Replace Symbolic Similarity with Real Embeddings (Priority: High)

**What:** The L1 engine currently uses pseudo-embeddings (random vectors for testing). Law 8 (compatibility), Law 1 Step 0 (deduplication), and crystallization (Law 10) all require real cosine similarity. Wire OpenAI `text-embedding-3-small` via the existing adapter at `runtime/infrastructure/embeddings/openai_adapter.py`.

**Why:** Without real embeddings, similarity is noise. Dedup doesn't work. Propagation compatibility is random. Crystallization produces nonsense clusters.

**Tradeoff:** Cost. Each embedding call costs ~$0.00002/1k tokens. A citizen processing 50 nodes/tick at 1 tick/min = ~72k embedding calls/day = ~$1.44/day per citizen. For 44 citizens: ~$63/day. Acceptable at production scale. Batch calls reduce round-trips.

### O5: Persist Graph State in FalkorDB (Priority: High)

**What:** Currently the L1 engine runs in-memory. Graph state (nodes, links, energy, weight, embeddings) must survive process restarts. The FalkorDB adapter exists at `runtime/infrastructure/database/falkordb_adapter.py`.

**Why:** Restarts kill all accumulated knowledge, weight, identity. A citizen that ran for 10,000 ticks loses everything on deploy. Unacceptable for a living cognitive system.

**Tradeoff:** Performance. In-memory operations are ~100x faster than FalkorDB queries. Accept hybrid: run physics in-memory, checkpoint to FalkorDB every N ticks (e.g., every 10). On startup, load from FalkorDB into memory.

### O6: Seed All 44 Citizen Brains (Priority: Medium)

**What:** Generate brain.json for every citizen using the seed brain generator (209 base nodes, 295 links) plus per-citizen customization from identity files.

**Why:** Citizens need cognitive starting points -- values, processes, desires -- to behave coherently from first boot. Without seed brains, they're cognitively empty.

**Tradeoff:** Uniformity vs. personality. Same base for all (shared values) + per-citizen overlay (role-specific processes, drive baselines, unique desires from identity files).

### O7: Deploy to Production on Render (Priority: Medium)

**What:** Phase 7 cutover from manemus. Dockerfile ready, render.yaml ready. Parallel run, DNS switch, bot migration.

**Why:** manemus is the current production system. mind-mcp replaces it. Until cutover, everything built here is theoretical.

**Tradeoff:** Risk. Parallel run period adds infrastructure cost but prevents catastrophic migration failure. Plan: 1-2 weeks parallel, validate output parity, then cut DNS.

---

## Non-Objectives

- **Redesign the physics.** The 21-law spec is settled. This module wires it, not rethinks it.
- **Build a general-purpose graph database.** We use FalkorDB as-is. No custom query language.
- **Support multiple embedding providers.** text-embedding-3-small is the target. If we need to switch later, the adapter pattern supports it, but we don't design for it now.
- **Multi-universe graph.** Force 1 handles L3 universe graph. This module is L1 brain graphs only.
- **Economy integration.** Force 2 handles $MIND. Physics wiring is independent.

---

## Success Criteria

1. A citizen receives a Telegram message, and the corresponding L1 graph shows new nodes with injected energy within one tick
2. The citizen's Claude prompt contains WM nodes reflecting the current cognitive state
3. Law 11 orientation visibly changes the citizen's behavioral posture in responses
4. Embeddings are real (1536-dim, from OpenAI), not pseudo-random vectors
5. Graph state persists across process restarts
6. All 44 citizens boot with seeded brains and run independent tick loops
7. mind-mcp serves production traffic with no regression from manemus

---

## Dependencies

| Dependency | Owner | Status | Notes |
|-----------|-------|--------|-------|
| L1 ALGORITHM spec | docs/cognition/l1/ | CANONICAL | 21 laws, formulas, constants |
| L1 engine code | runtime/cognition/ (claimed) | MISSING from repo | SYNC says 4,717 lines built but directory absent -- needs locating or rebuilding |
| Orchestrator | runtime/orchestrator/ | CANONICAL | Dispatcher + Claude invoker working |
| FalkorDB adapter | runtime/infrastructure/database/ | CANONICAL | Working, tested |
| OpenAI embedding adapter | runtime/infrastructure/embeddings/ | CANONICAL | Working, tested |
| Seed brain generator | runtime/seed_brain_from_source_docs_dynamic_generator.py | CANONICAL | 209 nodes, 295 links |
| Citizen identity | runtime/citizens/ | CANONICAL | load_citizen_identity, build_citizen_prompt |
| Citizen directories | .mind/citizens/ | EMPTY | Need to copy from manemus |
