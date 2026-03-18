# Exteroception — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — the module is being redesigned from scratch

**What's still being designed:**
- The 1-2-3 hop scan algorithm (ALGORITHM doc written, code not yet)
- State-biased smart selection: base relevance * limbic bias * goal alignment * habituation decay * change/novelty boost
- Limbic bias: drive intensities modulate which node types cross the perception threshold (B11)
- Goal alignment: cosine similarity between node embeddings and active desire/task embeddings (B12)
- Habituation decay: unchanged nodes fade from awareness over repeated exposures (B13)
- Previous-awareness feedback: change detection and novelty boosts for temporal continuity (B14)
- Sensory channel definitions and refractory periods
- Awareness text generation and TTL caching
- WM serializer integration for awareness text injection
- All 12 validation invariants (defined in VALIDATION, untested)

**What's proposed (v2+):**
- Event-driven exteroception (L3 pushes changes instead of per-tick polling)
- Async L3 queries for non-blocking tick
- "Focus" mechanism for directed environmental attention
- Shared Channel/SensoryChannel module with interoception
- Pre-computed "adjacent space activity" L3 aggregates for faster 3-hop awareness
- Two-tier cache (fast-changing moments + slow-changing topology)

---

## CURRENT STATE

A draft implementation exists at `runtime/cognition/exteroception.py` (~220 lines). It was a first pass that only scans for new Moments in directly linked Spaces — a flat, recent-only scan using raw Cypher queries. NLR feedback identified several gaps:

1. **Missing multi-hop awareness.** The draft only scans 1-hop (direct Spaces). NLR's design specifies 1-2-3 hop concentric scanning with energy gradients per hop level.
2. **Missing awareness text output.** The draft only produces stimuli. NLR's design specifies a second output: a natural-language awareness summary injected into the system prompt as a persistent environmental context layer.
3. **Missing state-biased selection.** The draft returns whatever L3 gives it (up to LIMIT). NLR's design specifies a four-factor scoring function: base relevance (hops, recency, energy) multiplied by limbic bias, goal alignment, and habituation decay, with change/novelty boosts from previous awareness.
4. **Missing node type diversity.** The draft only looks for Moments. NLR's design includes all 5 L3 node types: Spaces (activity level), Actors (who's nearby), Moments (what happened), Narratives (project state), Things (available tools/objects).
5. **Missing absence detection.** The draft doesn't detect silence — only new events. NLR's design includes detecting when a normally active Space goes quiet.
6. **Missing limbic bias.** The citizen's drives should shape what they perceive — a frustrated citizen sees obstacles, a curious citizen sees novelty. Not in the draft.
7. **Missing goal alignment.** The citizen's active desires and tasks should focus the perceptual field via embedding similarity. Not in the draft.
8. **Missing habituation.** Unchanged nodes should fade from awareness over repeated exposures. Not in the draft.
9. **Missing temporal continuity.** Previous awareness should feed current perception — changes highlighted, novelty boosted. Not in the draft.

The full doc chain (8 files) has been written to capture NLR's redesign specification. The implementation needs to be rewritten to match.

---

## IN PROGRESS

### Full Doc Chain Creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete
- **Context:** All 8 doc chain files created: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, HEALTH, IMPLEMENTATION, SYNC. Design captured from NLR's feedback. Ready for implementation.

---

## RECENT CHANGES

### 2026-03-18: Doc Chain Created from NLR Design Feedback

- **What:** Complete 8-file documentation chain for exteroception module redesign
- **Why:** NLR provided detailed feedback that the current draft is too narrow (Moment-only, 1-hop-only, stimuli-only). The redesign adds 1-2-3 hop scanning, smart selection, awareness text generation, all 5 L3 node types, and absence detection.
- **Files:** All files in `docs/cognition/exteroception/`
- **Struggles/Insights:** The key design tension is between query depth (3-hop gives rich awareness) and query speed (FalkorDB may struggle with 3-level MATCH on 45K nodes). The ALGORITHM doc proposes a latency-adaptive approach: skip 3-hop if 1-hop is already slow.

---

## KNOWN ISSUES

### Draft Implementation Does Not Match Design

- **Severity:** high
- **Symptom:** `runtime/cognition/exteroception.py` implements a flat Moment scanner; the doc chain specifies a multi-hop, multi-type, dual-output perception engine
- **Suspected cause:** Draft was written before NLR's design feedback
- **Attempted:** Nothing yet — the doc chain was written first per PRINCIPLES (understand before building)

### WM Serializer Has No Awareness Hook

- **Severity:** medium
- **Symptom:** `wm_prompt_serializer.py` has no integration point for exteroceptive awareness text
- **Suspected cause:** Feature didn't exist when the serializer was written
- **Attempted:** Not yet — needs design decision on coupling pattern (field on state vs direct engine call)

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation), fixer (redesign existing code)

**Where I stopped:** Doc chain is complete. The ALGORITHM doc has the full tick algorithm with 7 steps, data structures, query templates, scoring formula, and constants. The code needs to be rewritten to match.

**What you need to understand:**
The critical insight is that exteroception produces TWO outputs, not one. The stimuli go into Law 1 (per tick, discrete events). The awareness text goes into the system prompt (periodic, persistent context). These have different rhythms and different consumers. Don't conflate them.

**Watch out for:**
- The query_fn signature — it's `query_fn(cypher, params) -> rows`. Verify it supports the parameterized multi-hop queries in the ALGORITHM doc.
- FalkorDB uses different label semantics than Neo4j. The Cypher in the ALGORITHM doc uses Neo4j-style labels (`:Actor`, `:Space`). FalkorDB may need `node_type` field checks instead. Check the actual L3 graph driver.
- The tick runner already has the exteroception integration point (line ~932). It passes `state._l3_query_fn` as the query function. Make sure the new engine's `tick()` signature stays compatible.

**Open questions I had:**
- Should the awareness text be a field on CitizenCognitiveState that the serializer reads? Or should the serializer directly call the engine's get_awareness_text()? The former is cleaner separation, the latter avoids state duplication.
- The SensoryChannel is identical to interoception's Channel. Should we extract a shared base class now or wait until v2?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete 8-file doc chain written for the exteroception redesign based on NLR's feedback. The design specifies 1-2-3 hop L3 scanning, smart selection with relevance scoring, dual output (stimuli + awareness text), all 5 L3 node types, and graceful degradation. The current draft implementation needs to be rewritten to match. No code changes made yet — docs first, per PRINCIPLES.

**Decisions made:**
- MAX_STIMULI_PER_TICK = 3 (matching interoception)
- MAX_PERCEPTION_NODES = 50 (based on Dunbar-like cognitive constraint)
- AWARENESS_TTL_TICKS = 10 (regenerate every 10 ticks)
- HOP_WEIGHT = {1: 1.0, 2: 0.5, 3: 0.2} (energy gradient by distance)
- SCAN_WINDOW_S = 300 (5 minutes for stimulus detection)
- RECENCY_WINDOW_S = 3600 (1 hour for relevance scoring)

**Needs your input:**
- The ALGORITHM doc proposes Cypher queries for 1-2-3 hop scans. These need validation against the actual FalkorDB L3 graph schema — the label/field naming may differ.
- The awareness text integration point in wm_prompt_serializer.py needs a design decision: field on state vs direct engine call.
- 3-hop query cost on 45K nodes needs benchmarking before committing to the design. The doc proposes latency-adaptive skipping as a fallback.

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Full doc chain written. Implementation needs complete redesign to match ALGORITHM spec.
- [ ] DOCS->IMPL: wm_prompt_serializer.py needs awareness text integration point.

### Tests to Run

```bash
# After implementation, run:
python -m pytest runtime/cognition/tests/test_exteroception.py -v
```

### Immediate

- [ ] Redesign `runtime/cognition/exteroception.py` to match ALGORITHM doc
- [ ] Add PerceptionNode dataclass, HabituationState, and four-factor scoring function
- [ ] Implement _query_neighborhood() with 1-2-3 hop queries
- [ ] Implement limbic bias: DRIVE_AFFINITIES per node type, drives from CitizenCognitiveState
- [ ] Implement goal alignment: cosine similarity with active desire/task embeddings
- [ ] Implement habituation decay: times_seen tracking, content hash change detection
- [ ] Implement previous-awareness feedback: change_detection_boost and novelty_boost
- [ ] Implement _build_awareness_text() for natural-language rendering
- [ ] Add get_awareness_text() public method with TTL cache
- [ ] Add awareness text hook in wm_prompt_serializer.py
- [ ] Create test_exteroception.py with V1, V3, V4, V6, V9, V10, V11, V12 tests
- [ ] Add DOCS: comment at top of exteroception.py

### Later

- [ ] Benchmark 3-hop query on production-scale FalkorDB (45K nodes)
- [ ] Calibrate refractory periods against real tick rates
- [ ] Calibrate SCAN_WINDOW_S and RECENCY_WINDOW_S against real data
- [ ] Extract shared Channel/SensoryChannel base class with interoception
- IDEA: "Social temperature" metric per Space — rolling average of Moment frequency for richer spatial perception
- IDEA: Event-driven exteroception in v2 — L3 pushes instead of per-tick polling

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident about the design. NLR's feedback was clear and specific. The 1-2-3 hop model with dual output (stimuli + awareness text) feels right — it mirrors how biological exteroception works (discrete sensory events + continuous perceptual field). The doc chain captures the full design.

**Threads I was holding:**
- The FalkorDB query efficiency question. 3-hop MATCH patterns on large graphs can be expensive. The latency-adaptive approach (skip 3-hop if slow) is a pragmatic fallback, but the real solution might be pre-computed aggregates in L3.
- The WM serializer integration. The serializer currently renders WM nodes, emotions, orientation. Adding an awareness layer is a new concern. It needs to fit within the ~5000 char system prompt budget.
- The SensoryChannel duplication with interoception. It works fine as a copy, but it's technical debt.

**Intuitions:**
- The awareness text will be more impactful than the stimuli. Stimuli are momentary interrupts. The awareness text is persistent context that shapes EVERYTHING the citizen says. Getting the awareness text right — natural, concise, situationally rich — is the high-leverage work.
- 50 nodes is probably too many for awareness text rendering. The text will need aggressive compression. Most of the 50 will inform the text's tone (busy/quiet/alone) without being individually mentioned.

**What I wish I'd known at the start:**
The distinction between stimuli and awareness text is the core of the redesign. The original draft only produced stimuli. Once you see that the citizen needs both "what just changed" (stimuli) and "what my world looks like" (awareness), the architecture falls into place.

---

## POINTERS

| What | Where |
|------|-------|
| Current draft implementation | `runtime/cognition/exteroception.py` |
| Interoception (sibling pattern) | `runtime/cognition/interoception.py` |
| Tick runner integration point | `runtime/cognition/tick_runner_l1_cognitive_engine.py` line ~929 |
| WM serializer (awareness consumer) | `runtime/cognition/wm_prompt_serializer.py` |
| L3 schema | `schema-l3.yaml` |
| Interoception patterns doc (style reference) | `docs/cognition/interoception/PATTERNS_Interoception.md` |
