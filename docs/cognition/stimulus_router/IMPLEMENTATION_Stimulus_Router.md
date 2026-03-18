# Stimulus Router — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
BEHAVIORS:       ./BEHAVIORS_Stimulus_Router.md
PATTERNS:        ./PATTERNS_Stimulus_Router.md
ALGORITHM:       ./ALGORITHM_Stimulus_Router.md
VALIDATION:      ./VALIDATION_Stimulus_Router.md
THIS:            IMPLEMENTATION_Stimulus_Router.md (you are here)
HEALTH:          ./HEALTH_Stimulus_Router.md
SYNC:            ./SYNC_Stimulus_Router.md

IMPL:            runtime/cognition/stimulus_router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── stimulus_router.py                          # IncomingEvent, AntiLoopGate, StimulusRouter, extract_concepts
├── feedback_injector.py                        # inject_post_action_feedback, episodic memory creation
├── tick_runner_l1_cognitive_engine.py           # Stimulus dataclass (consumed by router), L1CognitiveTickRunner
├── laws/
│   └── law_01_energy_injection.py              # Law 1 — dual-channel injection that consumes Stimulus objects
├── constants.py                                # Injection constants (REFRACTORY_TICKS, SELF_STIMULUS_RATIO, etc.)
└── tests/
    └── test_l1_wiring_integration.py           # Integration tests covering stimulus routing
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `stimulus_router.py` | Event-to-Stimulus conversion, anti-loop, dedup, concept extraction | `IncomingEvent`, `AntiLoopGate`, `StimulusRouter`, `extract_concepts` | ~245 | OK |
| `feedback_injector.py` | Post-action feedback loop: self-stimulus, episodic memory, limbic updates | `inject_post_action_feedback`, `_create_episodic_memories`, `_update_limbic_from_outcome` | ~241 | OK |
| `tick_runner_l1_cognitive_engine.py` | Defines Stimulus dataclass, orchestrates tick loop | `Stimulus`, `L1CognitiveTickRunner` | ~968 | WATCH |
| `laws/law_01_energy_injection.py` | Dual-channel injection consuming Stimulus objects | `inject_energy`, `InjectionResult`, `_preprocess_stimulus` | ~925 | WATCH |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (linear filter chain)

**Why this pattern:** The routing problem is inherently sequential — each stage (anti-loop, dedup, classify, budget, build) depends on the previous stage's decision. A pipeline makes the rejection points explicit and the flow testable. Each stage is a pure function of its inputs plus gate state.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Dataclass | `IncomingEvent`, `Stimulus` | Lightweight immutable-ish value objects with default field factories |
| Guard clause | `AntiLoopGate.check()` | Each layer is a guard: if rejected, return early |
| Instance-per-citizen | `StimulusRouter` | Isolated state per citizen prevents cross-contamination |
| Sliding window | `_recent_stimulus_hashes`, `_recent_hashes` | Bounded-memory dedup with FIFO eviction |

### Anti-Patterns to Avoid

- **Global dedup state**: Don't share dedup histories across citizens. Each citizen's perception is independent.
- **Embedding in the hot path**: Don't add LLM calls or model inference to the route() pipeline. The embed_fn parameter exists for async pre-computation, not synchronous blocking.
- **Energy constants in the router**: Energy multipliers (1.0, 1.2, 0.8) are currently hardcoded. When metabolism arrives, these must be pulled from the citizen's metabolic state, not from new constants.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Stimulus Router | Event classification, anti-loop, dedup, energy budgeting | Graph mutation, node creation, embedding generation | `StimulusRouter.route(event) -> Optional[Stimulus]` |
| Feedback Injector | Memory creation, limbic updates, self-stimulus routing | LLM invocation, WM prompt assembly | `inject_post_action_feedback(state, router, output, success) -> Optional[Stimulus]` |
| Anti-Loop Gate | Refractory tracking, diminishing returns, novelty hashing | Content semantics, embedding similarity | `AntiLoopGate.check(event) -> (bool, float)` |

---

## SCHEMA

### IncomingEvent

```yaml
IncomingEvent:
  required:
    - content: str              # Event text content
    - source: str               # Origin: "telegram" | "whatsapp" | "discord" | "mcp" | "system" | "self"
    - citizen_handle: str       # Target citizen identifier
  optional:
    - is_social: bool           # Social interaction flag (default False)
    - is_failure: bool          # Error/failure flag (default False)
    - is_progress: bool         # Success/progress flag (default False)
    - metadata: dict            # Source-specific metadata (default {})
    - timestamp: float          # Unix timestamp (default time.time())
  constraints:
    - content can be empty string but not None
    - source must be one of the known source strings
```

### StimulusRouter Instance State

```yaml
StimulusRouter:
  required:
    - citizen_handle: str                    # Owning citizen
  optional:
    - embed_fn: Optional[callable]           # Async embedding function (not yet used)
  internal_state:
    - anti_loop: AntiLoopGate                # Per-citizen anti-loop gate instance
    - _recent_stimulus_hashes: list[str]     # Dedup window (max 50 12-char MD5 prefixes)
    - _dedup_window: int                     # Window size (50)
  constraints:
    - One instance per citizen, never shared
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `StimulusRouter.route()` | `stimulus_router.py:174` | Dispatcher calls after receiving message from bridge or MCP |
| `StimulusRouter.record_action()` | `stimulus_router.py:233` | Feedback injector calls after LLM output |
| `inject_post_action_feedback()` | `feedback_injector.py:35` | Dispatcher calls after Claude session completes |
| `extract_concepts()` | `stimulus_router.py:107` | Called internally by route() |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### External Event Routing: Bridge Message to Stimulus

Covers the primary flow: an external message (e.g., Telegram) arriving at the dispatcher, being converted to an IncomingEvent, routed through the StimulusRouter, and injected as a Stimulus into the tick loop.

```yaml
flow:
  name: external_event_routing
  purpose: Convert incoming bridge messages into L1 stimuli for cognitive processing
  scope: dispatcher -> StimulusRouter -> Stimulus -> tick_runner
  steps:
    - id: step_1_create_event
      description: Dispatcher creates IncomingEvent from bridge message
      file: runtime/orchestrator/dispatcher.py
      function: _inject_stimulus
      input: content (str), source (str), citizen_handle (str), flags
      output: IncomingEvent
      trigger: Message received from bridge callback
      side_effects: None

    - id: step_2_route
      description: StimulusRouter.route() runs the pipeline (anti-loop, dedup, classify, build)
      file: runtime/cognition/stimulus_router.py
      function: StimulusRouter.route
      input: IncomingEvent
      output: Optional[Stimulus]
      trigger: Called by dispatcher._inject_stimulus
      side_effects: Updates dedup history, anti-loop state

    - id: step_3_tick
      description: Stimulus injected into L1 tick runner
      file: runtime/cognition/tick_runner_l1_cognitive_engine.py
      function: L1CognitiveTickRunner.run_tick
      input: Stimulus
      output: TickResult
      trigger: Called by dispatcher after route() returns non-None
      side_effects: Graph energy mutated, WM updated, limbic state changed

  docking_points:
    available:
      - id: dock_event_created
        type: event
        direction: input
        file: runtime/orchestrator/dispatcher.py
        function: _inject_stimulus
        trigger: Bridge callback
        payload: IncomingEvent
        async_hook: not_applicable
        needs: none
        notes: Entry point for all external stimuli

      - id: dock_route_output
        type: event
        direction: output
        file: runtime/cognition/stimulus_router.py
        function: StimulusRouter.route
        trigger: Called by dispatcher
        payload: Optional[Stimulus]
        async_hook: not_applicable
        needs: none
        notes: None means event was filtered (dedup/anti-loop)

      - id: dock_dedup_state
        type: custom
        direction: output
        file: runtime/cognition/stimulus_router.py
        function: StimulusRouter.route
        trigger: Each route() call
        payload: _recent_stimulus_hashes list
        async_hook: not_applicable
        needs: add watcher
        notes: Dedup window size and contents for health monitoring

    health_recommended:
      - dock_id: dock_route_output
        reason: Critical to verify external events produce stimuli (V1)
      - dock_id: dock_dedup_state
        reason: Monitor dedup rejection rate for V4 compliance
```

### Feedback Loop: LLM Output to Self-Stimulus

Covers the feedback path: LLM output -> episodic memory creation -> self-stimulus routing -> limbic update.

```yaml
flow:
  name: feedback_loop
  purpose: Close the perception-action loop by feeding LLM output back as self-stimulus
  scope: feedback_injector -> StimulusRouter -> Stimulus + episodic memories + limbic updates
  steps:
    - id: step_1_record_action
      description: Record action timestamp for refractory period
      file: runtime/cognition/feedback_injector.py
      function: inject_post_action_feedback
      input: router (StimulusRouter)
      output: None (side effect on router)
      trigger: Called by dispatcher after Claude session
      side_effects: Sets anti_loop._last_action_time

    - id: step_2_create_memories
      description: Extract memory-worthy segments and create episodic memory nodes
      file: runtime/cognition/feedback_injector.py
      function: _create_episodic_memories
      input: CitizenCognitiveState, action_output (str), success (bool)
      output: list[str] (created memory node IDs)
      trigger: Called if len(action_output) >= 30
      side_effects: New memory nodes added to state, links to WM nodes created

    - id: step_3_route_self
      description: Truncate output and route as self-stimulus through StimulusRouter
      file: runtime/cognition/feedback_injector.py
      function: inject_post_action_feedback
      input: IncomingEvent(source="self")
      output: Optional[Stimulus]
      trigger: After memory creation
      side_effects: Router dedup/anti-loop state updated

    - id: step_4_limbic_update
      description: Update limbic drives and emotions based on action outcome
      file: runtime/cognition/feedback_injector.py
      function: _update_limbic_from_outcome
      input: CitizenCognitiveState, success (bool), response_time_ms
      output: None (side effect on limbic state)
      trigger: Always called, regardless of self-stimulus filter result
      side_effects: satisfaction/frustration/anxiety/achievement modified

  docking_points:
    available:
      - id: dock_feedback_entry
        type: event
        direction: input
        file: runtime/cognition/feedback_injector.py
        function: inject_post_action_feedback
        trigger: Dispatcher after LLM session
        payload: action_output, success, response_time_ms
        async_hook: not_applicable
        needs: none
        notes: Primary feedback entry point

      - id: dock_memories_created
        type: graph_ops
        direction: output
        file: runtime/cognition/feedback_injector.py
        function: _create_episodic_memories
        trigger: Output >= 30 chars
        payload: list[str] memory node IDs
        async_hook: not_applicable
        needs: none
        notes: Up to 3 memory nodes per session

      - id: dock_limbic_delta
        type: custom
        direction: output
        file: runtime/cognition/feedback_injector.py
        function: _update_limbic_from_outcome
        trigger: Every feedback call
        payload: satisfaction/frustration/anxiety deltas
        async_hook: not_applicable
        needs: add watcher
        notes: Important for verifying V7 (perception-action loop integrity)

    health_recommended:
      - dock_id: dock_feedback_entry
        reason: Verify feedback loop is being called (V7)
      - dock_id: dock_limbic_delta
        reason: Verify limbic state updates reflect success/failure correctly
```

---

## LOGIC CHAINS

### LC1: External Message to Working Memory

**Purpose:** Trace how a Telegram message becomes a node in working memory.

```
Bridge callback (Telegram message received)
  -> Dispatcher._inject_stimulus(content, "telegram", handle, is_social=True)
    -> StimulusRouter.route(IncomingEvent)                          # classify, dedup, budget
      -> Stimulus(energy=1.2, is_social=True)
        -> L1CognitiveTickRunner.run_tick(stimulus)
          -> Law 1 inject_energy(): distribute energy to matching nodes
            -> Law 4 select_working_memory(): stimulus-boosted nodes compete for WM
              -> WM updated: Telegram message content now in working memory
```

**Data transformation:**
- Input: `str` (raw message text) + `str` (source="telegram")
- After StimulusRouter: `Stimulus` (energy=1.2, is_social=True, concepts extracted)
- After Law 1: Energy distributed to matching/new nodes in the graph
- Output: TickResult with updated WM containing stimulus-relevant nodes

### LC2: LLM Output to Self-Stimulus

**Purpose:** Trace how a citizen's own output re-enters its cognitive graph.

```
Claude session completes with output text
  -> Dispatcher calls inject_post_action_feedback(state, router, output, success)
    -> router.record_action()                                      # set refractory timestamp
    -> _create_episodic_memories(state, output, success)           # create memory nodes
    -> StimulusRouter.route(IncomingEvent(source="self"))
      -> AntiLoopGate.check(): refractory OK? diminishing energy? novel hash?
        -> Stimulus(energy=base * 0.5^(n/3), source="self")
          -> Returned to dispatcher for next tick injection
    -> _update_limbic_from_outcome(state, success)                 # satisfaction/frustration
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
stimulus_router.py
    └── imports -> tick_runner_l1_cognitive_engine.py  (Stimulus dataclass)

feedback_injector.py
    ├── imports -> models.py  (CitizenCognitiveState, Node, NodeType, Link, LinkType)
    ├── imports -> tick_runner_l1_cognitive_engine.py  (Stimulus)
    └── imports -> stimulus_router.py  (StimulusRouter, IncomingEvent)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `hashlib` | MD5 content hashing for dedup and anti-loop | `stimulus_router.py` |
| `time` | Timestamps for refractory period tracking | `stimulus_router.py`, `feedback_injector.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Anti-loop gate state | `StimulusRouter.anti_loop` (AntiLoopGate instance) | Per-citizen | Created with StimulusRouter, lives for citizen lifetime |
| Dedup history | `StimulusRouter._recent_stimulus_hashes` | Per-citizen | FIFO sliding window, max 50 entries |
| Anti-loop hash history | `AntiLoopGate._recent_hashes` | Per-citizen | FIFO sliding window, max 20 entries |
| Self-stimulus count | `AntiLoopGate._self_stimulus_count` | Per-citizen | Reset to 0 on any external event |
| Last action time | `AntiLoopGate._last_action_time` | Per-citizen | Updated by record_action(), read by check() |
| Citizen routers | `Dispatcher._citizen_routers` | Global (dispatcher) | Dict of citizen_handle -> StimulusRouter, lazy-initialized |

### State Transitions

```
External event ──route()──> dedup updated, anti_loop.count reset to 0

Self event (allowed) ──route()──> dedup updated, anti_loop.count++, hash added

Self event (rejected) ──route()──> no state change (event dropped)

Action taken ──record_action()──> anti_loop._last_action_time = now
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Dispatcher creates StimulusRouter(citizen_handle) on first message for that citizen
2. StimulusRouter creates AntiLoopGate with default parameters
3. Both dedup and anti-loop histories start empty
4. embed_fn is None (no embedding capability initially)
```

### Main Loop (per message)

```
1. Bridge delivers message to dispatcher
2. Dispatcher calls _inject_stimulus(content, source, handle, flags)
3. _inject_stimulus creates IncomingEvent
4. StimulusRouter.route(event) runs pipeline
5. If Stimulus returned: runner.run_tick(stimulus=stimulus)
6. If None returned: event was filtered, no tick triggered by this event
```

### Feedback (after LLM session)

```
1. Claude session completes with output
2. Dispatcher calls inject_post_action_feedback(state, router, output, success)
3. Feedback injector: record_action -> create memories -> route self-stimulus -> update limbic
4. Self-stimulus (if not filtered) available for next tick
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `refractory_seconds` | `AntiLoopGate.__init__` | `5.0` | Seconds after action before self-stimuli allowed |
| `diminishing_half_life` | `AntiLoopGate.__init__` | `3` | Number of self-stimuli for energy to halve |
| `novelty_threshold` | `AntiLoopGate.__init__` | `0.85` | Cosine sim threshold (reserved for future use) |
| `history_size` | `AntiLoopGate.__init__` | `20` | Max entries in anti-loop hash history |
| `_dedup_window` | `StimulusRouter.__init__` | `50` | Max entries in content dedup history |
| `_MEMORY_WEIGHT` | `feedback_injector.py` | `0.35` | Base weight for episodic memory nodes |
| `_MEMORY_STABILITY` | `feedback_injector.py` | `0.3` | Stability of episodic memory nodes |
| `_MEMORY_MIN_LENGTH` | `feedback_injector.py` | `30` | Minimum output length for memory creation |
| `_MEMORY_MAX_PER_SESSION` | `feedback_injector.py` | `3` | Max memory nodes per feedback call |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Line | Reference |
|------|------|-----------|
| `stimulus_router.py` | 4 | `Spec: docs/l1_wiring/ALGORITHM_L1_Wiring.md Section 2.1` |
| `feedback_injector.py` | 2 | `Spec: docs/l1_wiring/ALGORITHM_L1_Wiring.md Section 4` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 1 (Anti-Loop) | `stimulus_router.py:AntiLoopGate.check()` |
| ALGORITHM Step 2 (Dedup) | `stimulus_router.py:StimulusRouter.route()` lines 184-191 |
| ALGORITHM Step 3 (Classify) | `stimulus_router.py:StimulusRouter.route()` lines 194-195 |
| ALGORITHM Step 4 (Concepts) | `stimulus_router.py:extract_concepts()` |
| ALGORITHM Step 5 (Energy) | `stimulus_router.py:StimulusRouter.route()` lines 201-206 |
| ALGORITHM Step 6 (Build) | `stimulus_router.py:StimulusRouter.route()` lines 209-220 |
| ALGORITHM Feedback Step 1 | `feedback_injector.py:inject_post_action_feedback()` line 60 |
| ALGORITHM Feedback Step 2 | `feedback_injector.py:_create_episodic_memories()` |
| ALGORITHM Feedback Step 3 | `feedback_injector.py:inject_post_action_feedback()` lines 68-83 |
| ALGORITHM Feedback Step 4 | `feedback_injector.py:_update_limbic_from_outcome()` |
| BEHAVIOR B1 | `stimulus_router.py:AntiLoopGate.check()` lines 77-79 |
| BEHAVIOR B2 | `stimulus_router.py:AntiLoopGate.check()` lines 89-90 |
| BEHAVIOR B3 | `stimulus_router.py:AntiLoopGate.check()` lines 83-85 |
| BEHAVIOR B4 | `stimulus_router.py:StimulusRouter.route()` lines 184-191 |
| BEHAVIOR B5 | `stimulus_router.py:StimulusRouter.route()` lines 202-203 |
| VALIDATION V1 | `runtime/cognition/tests/test_l1_wiring_integration.py` |

---

## EXTRACTION CANDIDATES

No files are at SPLIT status. `tick_runner_l1_cognitive_engine.py` and `law_01_energy_injection.py` are at WATCH (~925-968 lines) but they belong to the L1 physics module, not the stimulus router.
