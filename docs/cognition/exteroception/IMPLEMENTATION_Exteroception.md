# Exteroception — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
BEHAVIORS:       ./BEHAVIORS_Exteroception.md
PATTERNS:        ./PATTERNS_Exteroception.md
ALGORITHM:       ./ALGORITHM_Exteroception.md
VALIDATION:      ./VALIDATION_Exteroception.md
THIS:            IMPLEMENTATION_Exteroception.md (you are here)
HEALTH:          ./HEALTH_Exteroception.md
SYNC:            ./SYNC_Exteroception.md

IMPL:            runtime/cognition/exteroception.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── exteroception.py           # ExteroceptionEngine — main module (to be redesigned)
├── interoception.py           # InteroceptionEngine — sibling pattern reference
├── tick_runner_l1_cognitive_engine.py  # Integration point: calls exteroception at step 0
├── wm_prompt_serializer.py    # Awareness text consumer: calls get_awareness_text()
├── models.py                  # CitizenCognitiveState, Stimulus (shared types)
└── tests/
    └── test_exteroception.py  # Unit tests (to be created)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `exteroception.py` | External world awareness engine | `ExteroceptionEngine`, `SensoryChannel`, `PerceptionNode` | ~220 (current draft) | REDESIGN |
| `interoception.py` | Internal state awareness engine (sibling) | `InteroceptionEngine`, `Channel` | ~318 | OK |
| `tick_runner_l1_cognitive_engine.py` | Tick orchestrator | `CognitiveTick.tick()` step 0 | ~1000+ | WATCH (but not our concern) |
| `wm_prompt_serializer.py` | System prompt builder | `serialize_wm()` | ~400 | WATCH |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Sensor Engine (same as interoception)

**Why this pattern:** The Channel-based sensor engine pattern is proven by interoception. Channels encapsulate threshold/refractory logic per sense. The engine orchestrates scan, score, classify, gate. This separation of concerns keeps each channel independently configurable while the engine handles the pipeline.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Channel/Sensor | `SensoryChannel` | Encapsulate refractory gating per perception type |
| Pipeline | `tick()` steps 0-7 | Sequential scan-score-classify-gate-render pipeline |
| Cache with TTL | `_cached_awareness` | Awareness text regenerated periodically, not every tick |
| Graceful Degradation | `tick()` step 0 guard | No query_fn = empty output, no crash |

### Anti-Patterns to Avoid

- **Direct Cypher in engine**: Don't embed raw Cypher strings throughout the class. Centralize query templates as module-level constants or a query builder.
- **Awareness in tick return**: Don't return awareness text from tick(). It's a separate output on a different rhythm. Return stimuli from tick(), expose awareness via get_awareness_text().
- **Mutation via query_fn**: Never pass mutation queries through query_fn. The function is for reads only. Consider a read-only wrapper in v2.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Exteroception Engine | L3 scanning, scoring, stimulus generation, awareness text | L3 writes, tick orchestration, prompt assembly | `tick() -> list[Stimulus]`, `get_awareness_text() -> str` |
| Channel Gating | Refractory state, fire/rearm logic | Scoring, classification | `can_fire(tick) -> bool`, `fire(tick)` |
| Awareness Cache | Text generation, TTL management | Prompt injection | `get_awareness_text() -> str` |

---

## SCHEMA

### SensoryChannel

```yaml
SensoryChannel:
  required:
    - name: str              # unique channel identifier
    - priority: int          # higher = fires first (0-100)
    - refractory_ticks: int  # minimum ticks between firings
  optional:
    - last_fired_tick: int   # defaults to -999 (never fired)
    - is_armed: bool         # defaults to True
  constraints:
    - priority in range [0, 100]
    - refractory_ticks >= 1
```

### PerceptionNode

```yaml
PerceptionNode:
  required:
    - node_id: str
    - node_type: str         # actor | moment | narrative | space | thing
    - name: str
    - hop: int               # 1, 2, or 3
  optional:
    - content: str
    - energy: float          # defaults to 0.0
    - recency: float         # computed, defaults to 0.0
    - relevance_score: float # computed
    - space_name: str | None
    - author_name: str | None
    - author_id: str | None
  constraints:
    - hop in {1, 2, 3}
    - energy >= 0.0
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `ExteroceptionEngine.tick()` | `exteroception.py` | `tick_runner_l1_cognitive_engine.py` step 0 (line ~943) |
| `ExteroceptionEngine.get_awareness_text()` | `exteroception.py` | `wm_prompt_serializer.py` during prompt assembly |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Exteroception Tick: L3 Scan to Stimulus Generation

This is the primary flow — runs every tick, transforms L3 graph state into L1 stimuli. High-impact because it determines what environmental information reaches the citizen's cognition.

```yaml
flow:
  name: exteroception_tick
  purpose: "Scan L3 neighborhood, score nodes, generate stimuli for Law 1"
  scope: "Input: citizen_id, tick, query_fn. Output: list[Stimulus]."
  steps:
    - id: step_0_guard
      description: "Check if query_fn is available. If not, return empty list."
      file: runtime/cognition/exteroception.py
      function: ExteroceptionEngine.tick()
      input: "query_fn: Callable | None"
      output: "[] if None, else continue"
      trigger: "tick_runner step 0"
      side_effects: "none"

    - id: step_1_query_l3
      description: "Execute 1-hop, 2-hop, 3-hop, and mention queries against L3"
      file: runtime/cognition/exteroception.py
      function: ExteroceptionEngine.tick() -> _query_neighborhood()
      input: "citizen_id, scan_window timestamps"
      output: "list[PerceptionNode]"
      trigger: "step_0 passed"
      side_effects: "none (read-only L3 queries)"

    - id: step_2_score
      description: "Score each PerceptionNode by hop_weight * (recency + energy)"
      file: runtime/cognition/exteroception.py
      function: _score_node()
      input: "list[PerceptionNode]"
      output: "list[PerceptionNode] sorted by relevance_score, truncated to top 50"
      trigger: "step_1 complete"
      side_effects: "none"

    - id: step_3_classify
      description: "Classify scored nodes into sensory channels"
      file: runtime/cognition/exteroception.py
      function: _classify_node()
      input: "PerceptionNode"
      output: "candidate tuple (priority, channel, content, energy, extra)"
      trigger: "step_2 complete"
      side_effects: "none"

    - id: step_4_gate
      description: "Fire candidates through channel gating (refractory check)"
      file: runtime/cognition/exteroception.py
      function: tick() gating loop
      input: "sorted candidates"
      output: "list[Stimulus], max MAX_STIMULI_PER_TICK"
      trigger: "step_3 complete"
      side_effects: "channel state updated (last_fired_tick, is_armed)"

    - id: step_5_rearm
      description: "Rearm channels whose refractory period expired"
      file: runtime/cognition/exteroception.py
      function: tick() rearm loop
      input: "channel state, current tick"
      output: "updated channel states"
      trigger: "step_4 complete"
      side_effects: "channel is_armed updated"

  docking_points:
    guidance:
      include_when: "L3 query boundary, stimulus output boundary"
      omit_when: "Internal scoring/classification steps (pure computation)"
      selection_notes: "Dock at L3 query (input) and stimulus list (output) — the two boundaries"
    available:
      - id: dock_l3_query_input
        type: graph_ops
        direction: input
        file: runtime/cognition/exteroception.py
        function: _query_neighborhood()
        trigger: "tick() step 1"
        payload: "citizen_id, scan_window timestamps, query strings"
        async_hook: not_applicable
        needs: none
        notes: "Observe what queries are sent to L3. Can verify read-only (V2)."

      - id: dock_l3_query_output
        type: graph_ops
        direction: output
        file: runtime/cognition/exteroception.py
        function: _query_neighborhood()
        trigger: "L3 response"
        payload: "list[PerceptionNode] or exception"
        async_hook: not_applicable
        needs: none
        notes: "Observe what L3 returned. Can measure latency and node counts."

      - id: dock_stimulus_output
        type: event
        direction: output
        file: runtime/cognition/exteroception.py
        function: tick()
        trigger: "step 4 complete"
        payload: "list[Stimulus]"
        async_hook: not_applicable
        needs: none
        notes: "Observe stimuli produced. Can verify V1 (bounded), V4 (natural language), V8 (source attribution)."

    health_recommended:
      - dock_id: dock_l3_query_output
        reason: "Verifies L3 connectivity, query latency, graceful failure handling (V3, V5)"
      - dock_id: dock_stimulus_output
        reason: "Verifies stimulus bounds (V1), content quality (V4), source tags (V8)"

### Awareness Regeneration: L3 Data to System Prompt Layer

Periodic flow — transforms collected PerceptionNodes into a natural-language awareness text cached for the WM serializer.

```yaml
flow:
  name: awareness_regeneration
  purpose: "Generate natural-language environmental awareness for system prompt injection"
  scope: "Input: list[PerceptionNode]. Output: cached awareness text string."
  steps:
    - id: step_ttl_check
      description: "Check if awareness TTL has expired"
      file: runtime/cognition/exteroception.py
      function: tick() step 6
      input: "current tick, _awareness_generated_at_tick"
      output: "boolean: regenerate or not"
      trigger: "tick() step 6"
      side_effects: "none"

    - id: step_build_text
      description: "Render PerceptionNodes as natural-language awareness summary"
      file: runtime/cognition/exteroception.py
      function: _build_awareness_text()
      input: "list[PerceptionNode]"
      output: "str (awareness text, ~500 chars)"
      trigger: "TTL expired"
      side_effects: "_cached_awareness updated, _awareness_generated_at_tick updated"

  docking_points:
    available:
      - id: dock_awareness_output
        type: event
        direction: output
        file: runtime/cognition/exteroception.py
        function: _build_awareness_text()
        trigger: "TTL expiry"
        payload: "str (awareness text)"
        async_hook: not_applicable
        needs: none
        notes: "Observe awareness text quality. Can verify V4 (natural language) and V7 (freshness)."

    health_recommended:
      - dock_id: dock_awareness_output
        reason: "Verifies awareness text content (V4) and freshness (V7)"
```

---

## LOGIC CHAINS

### LC1: Tick Runner to Stimuli

**Purpose:** How environmental perception flows from L3 to Law 1

```
tick_runner.tick()
  -> ExteroceptionEngine.tick(citizen_id, tick, query_fn)
    -> _query_neighborhood(citizen_id, query_fn)     # L3 queries
      -> _score_node() per node                       # relevance scoring
        -> _classify_node() per scored node            # channel assignment
          -> channel.can_fire(tick)                    # refractory gate
            -> Stimulus(content, energy, source="exteroception")
  -> tick_runner._step_inject(stimulus)               # Law 1 energy injection
```

**Data transformation:**
- Input: `citizen_id` (str) + L3 graph (remote)
- After step 1: `list[PerceptionNode]` (~50 nodes, scored)
- After step 3: `list[candidate]` (classified into channels)
- Output: `list[Stimulus]` (0-3 natural-language stimuli)

### LC2: Awareness Text to System Prompt

**Purpose:** How environmental context reaches the LLM

```
ExteroceptionEngine.tick() step 6
  -> _build_awareness_text(perception_nodes)        # render text
    -> _cached_awareness = "## What I See Right Now\n..."
wm_prompt_serializer.serialize_wm(state)
  -> extero = state._exteroception_engine            # access engine
    -> extero.get_awareness_text()                    # read cache
      -> inject into system prompt between WM and conversation layers
```

**Data transformation:**
- Input: `list[PerceptionNode]` (from tick step 2)
- After build: `str` (~500 chars, first-person perception)
- Output: Part of system prompt seen by LLM

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
exteroception.py
    └── imports -> tick_runner_l1_cognitive_engine.py (Stimulus dataclass)
    └── imports -> models.py (CitizenCognitiveState, NodeType)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `time` | Timestamp comparison for recency scoring | `exteroception.py` |
| `logging` | Debug/error logging | `exteroception.py` |
| `dataclasses` | SensoryChannel, PerceptionNode definitions | `exteroception.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Channel states (armed, last_fired) | `ExteroceptionEngine.channels` | instance | Created at engine init, persists across ticks |
| Seen Moment IDs | `ExteroceptionEngine._seen_moment_ids` | instance | Grows per tick, pruned at MAX_SEEN_IDS |
| Cached awareness text | `ExteroceptionEngine._cached_awareness` | instance | Regenerated every AWARENESS_TTL_TICKS |
| Awareness generation tick | `ExteroceptionEngine._awareness_generated_at_tick` | instance | Updated on awareness regeneration |
| Habituation times_seen | `ExteroceptionEngine._habituation.times_seen` | instance | Incremented per awareness cycle, reset on content change |
| Habituation content hashes | `ExteroceptionEngine._habituation.last_content_hash` | instance | Updated per awareness cycle for change detection |
| Previous awareness IDs | `ExteroceptionEngine._habituation.previous_awareness_ids` | instance | Updated per awareness cycle for novelty detection |

### State Transitions

```
Engine created (all channels armed, no seen IDs, no awareness, empty habituation)
    --tick()--> channels fire, seen IDs grow, awareness generated
    --tick()--> channels in refractory, new Moments scanned
    --refractory expires--> channels rearm
    --TTL expires--> awareness regenerated, habituation updated, previous_awareness refreshed
    --content change--> habituation.times_seen reset for changed node
    --prune--> seen IDs reduced to MAX/2
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. ExteroceptionEngine() — create channels dict, empty _seen_moment_ids, no cached awareness
2. Lazy init from tick_runner: first tick() call initializes the engine
3. First tick always regenerates awareness text (tick 0, TTL is 0)
```

### Main Loop (Per Tick)

```
1. Guard: query_fn available?
2. Query L3: 1-hop, 2-hop, 3-hop, mentions (within try/except)
3. Score + select top 50 nodes
4. Classify into channels
5. Gate: fire through refractory channels (max 3 stimuli)
6. Rearm expired channels
7. Maybe regenerate awareness text (if TTL expired)
8. Prune deduplication set
9. Return stimuli list
```

### Shutdown

```
1. No explicit shutdown needed — engine is garbage collected with the tick runner
2. No persistent state — all state is in-memory per citizen instance
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| ExteroceptionEngine | sync | Runs within the synchronous tick() call. No threads, no async. |
| L3 queries via query_fn | sync (blocking) | query_fn is expected to be synchronous. Async L3 access is v2. |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `MAX_STIMULI_PER_TICK` | `exteroception.py` constant | 3 | Maximum stimuli per tick |
| `MAX_PERCEPTION_NODES` | `exteroception.py` constant | 50 | Max nodes after scoring |
| `MAX_SEEN_IDS` | `exteroception.py` constant | 200 | Deduplication set cap |
| `SCAN_WINDOW_S` | `exteroception.py` constant | 300.0 | Moment timestamp filter (5 min) |
| `RECENCY_WINDOW_S` | `exteroception.py` constant | 3600.0 | Recency scoring window (1 hour) |
| `AWARENESS_TTL_TICKS` | `exteroception.py` constant | 10 | Awareness regeneration frequency |
| `HOP_WEIGHT` | `exteroception.py` constant | {1: 1.0, 2: 0.5, 3: 0.2} | Relevance multiplier per hop |
| `EXTERO_SOURCE` | `exteroception.py` constant | "exteroception" | Stimulus source tag |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/cognition/exteroception.py` | ~4 | `DOCS: docs/cognition/exteroception/ALGORITHM_Exteroception.md` (to be added) |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 0 (guard) | `exteroception.py:tick()` first lines |
| ALGORITHM step 1 (query) | `exteroception.py:_query_neighborhood()` (to be created) |
| ALGORITHM step 2 (score) | `exteroception.py:_score_node()` (to be created) |
| ALGORITHM step 3 (classify) | `exteroception.py:_classify_node()` (to be created) |
| ALGORITHM step 4 (gate) | `exteroception.py:tick()` gating loop |
| ALGORITHM step 6 (awareness) | `exteroception.py:_build_awareness_text()` (to be created) |
| BEHAVIOR B10 (awareness text) | `wm_prompt_serializer.py` awareness injection (to be added) |
| VALIDATION V1 (bounded) | `test_exteroception.py:test_max_stimuli` (to be created) |
| VALIDATION V3 (graceful) | `test_exteroception.py:test_l3_failure` (to be created) |

---

## EXTRACTION CANDIDATES

The current draft (`exteroception.py`, ~220 lines) is well within OK range. After redesign, estimate ~350-400 lines. If it approaches WATCH:

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `exteroception.py` | ~220L | <400L | `exteroception_queries.py` | Cypher query templates and _query_neighborhood() |

---

## MARKERS

<!-- @mind:todo Redesign exteroception.py to match the ALGORITHM doc. Current draft is a flat Moment-only scanner. New design needs: PerceptionNode struct, 1-2-3 hop queries, scoring function, awareness text cache, _build_awareness_text(), get_awareness_text() public method. -->

<!-- @mind:todo Add awareness text integration point in wm_prompt_serializer.py. The serializer needs to call exteroception.get_awareness_text() and inject the result as a "## What I See Right Now" section in the system prompt. -->

<!-- @mind:todo Create test_exteroception.py with tests for: V1 (max stimuli), V3 (graceful blindness), V4 (natural language), V6 (refractory gating), V9 (deduplication). Use mock query_fn. -->

<!-- @mind:todo Add DOCS: comment at top of exteroception.py pointing to this doc chain once the file is redesigned. -->

<!-- @mind:proposition Consider extracting SensoryChannel to a shared module with interoception's Channel — they're identical in structure. A shared cognition/channels.py would reduce duplication. -->
