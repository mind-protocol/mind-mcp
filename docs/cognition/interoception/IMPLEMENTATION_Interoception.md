# Interoception — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
BEHAVIORS:       ./BEHAVIORS_Interoception.md
PATTERNS:        ./PATTERNS_Interoception.md
ALGORITHM:       ./ALGORITHM_Interoception.md
VALIDATION:      ./VALIDATION_Interoception.md
THIS:            IMPLEMENTATION_Interoception.md (you are here)
HEALTH:          ./HEALTH_Interoception.md
SYNC:            ./SYNC_Interoception.md

IMPL:            runtime/cognition/interoception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── interoception.py              # Main module: InteroceptionEngine, channels, snapshot
├── tick_runner_l1_cognitive_engine.py  # Modified: new _step_interoception() call
├── models.py                     # Existing: InteroceptionState added to CitizenCognitiveState
├── metabolism.py                 # Existing: read-only dependency
├── constants.py                  # Existing: interoception thresholds added
tests/cognition/
└── test_interoception_engine.py  # Unit tests for all validation invariants
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/cognition/interoception.py` | Interoception engine, channel definitions, snapshot management | `InteroceptionEngine`, `InteroceptionChannel`, `InteroceptionSnapshot`, `interoception_tick()` | ~500 est. | TO CREATE |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Tick loop orchestration — adds `_step_interoception()` between limbic and orient | `_step_interoception()` | +20 | TO MODIFY |
| `runtime/cognition/models.py` | Data models — adds `interoception` field to CitizenCognitiveState | `InteroceptionState` reference | +3 | TO MODIFY |
| `runtime/cognition/constants.py` | Global constants — adds interoception thresholds | `INTERO_*` constants | +30 | TO MODIFY |
| `tests/cognition/test_interoception_engine.py` | Unit tests for all invariants | test functions | ~250 est. | TO CREATE |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline — each channel is an independent evaluator in a pipeline, producing zero or one ChannelReading. Readings are collected, sorted by priority, capped, and converted to Stimuli.

**Why this pattern:** Channels are independent — energy perception doesn't need to know about social field awareness. Adding a new channel means adding one function and one configuration entry. No cross-channel coupling. The pipeline makes the system trivially extensible.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Evaluator Pipeline | Channel functions | Each channel is an independent check, no cross-channel coupling |
| Dataclass State | InteroceptionSnapshot, InteroceptionChannel | Immutable snapshots for trend detection, mutable channel state |
| Threshold + Hysteresis | All channels | Standard control theory pattern for noisy signal detection |

### Anti-Patterns to Avoid

- **Cross-channel dependencies**: Don't let one channel's output affect another's threshold. Each channel reads raw state, not other channels.
- **State mutation in evaluators**: Channel evaluation functions must be pure — read state, return ChannelReading. Never write to state.
- **Complex NLP generation**: Stimulus content is a template string, not generated text. No LLM calls, no string interpolation beyond drive/tonic name insertion.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Interoception module | Channel evaluation, refractory gating, snapshot management | Limbic state computation, WM selection, stimulus injection | `interoception_tick(state, metabolism) -> list[Stimulus]` |
| Tick runner integration | Calling `_step_interoception()` at the right point | Interoception logic | `_step_interoception()` method on L1CognitiveTickRunner |

---

## SCHEMA

### InteroceptionState (to be added to CitizenCognitiveState)

```yaml
InteroceptionState:
  required:
    - channels: dict[str, InteroceptionChannel]  # per-channel refractory state
  optional:
    - snapshot: InteroceptionSnapshot             # previous tick's readings
    - stimuli_generated_total: int                # lifetime observability counter
  constraints:
    - channels keys must match the canonical channel name list
    - snapshot is None on first tick (no previous state)
```

### ChannelReading (transient, not persisted)

```yaml
ChannelReading:
  required:
    - channel_name: str       # which channel produced this
    - fires: bool             # whether threshold was crossed
    - content: str            # natural-language stimulus text
    - energy_budget: float    # how loud this sensation is
    - priority: int           # ordering for cap enforcement
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `interoception_tick()` | `interoception.py:main` | Called by tick runner's `_step_interoception()` |
| `_step_interoception()` | `tick_runner.py:~960` | Called in `run_tick()` between `_step_limbic()` and `_step_orient()` |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Interoception Tick Flow: State to Stimulus

This is the primary (and only) flow. It reads internal state, evaluates channels, and produces stimuli. It matters because it is the mechanism by which internal state becomes conscious experience.

```yaml
flow:
  name: interoception_tick
  purpose: Transform internal state readings into natural-language stimuli for Law 1 injection
  scope:
    inputs: CitizenCognitiveState, CitizenMetabolism, InteroceptionState
    outputs: list[Stimulus], updated InteroceptionState
    boundaries: reads from cognitive + metabolic state, writes only to InteroceptionState and Stimulus list
  steps:
    - id: capture_state
      description: Read all relevant state into local variables
      file: runtime/cognition/interoception.py
      function: interoception_tick
      input: CitizenCognitiveState + CitizenMetabolism
      output: local variables (energy, drives, WM, etc.)
      trigger: tick runner calls _step_interoception()
      side_effects: none (pure reads)
    - id: evaluate_channels
      description: Run each channel's threshold + refractory check
      file: runtime/cognition/interoception.py
      function: evaluate_* helpers
      input: local state variables + InteroceptionChannel states
      output: list[ChannelReading]
      trigger: sequential after capture
      side_effects: none (pure functions)
    - id: gate_and_cap
      description: Sort by priority, cap at MAX_STIMULI_PER_TICK, update refractory state
      file: runtime/cognition/interoception.py
      function: interoception_tick (inline)
      input: list[ChannelReading]
      output: list[Stimulus] (capped)
      trigger: sequential after evaluation
      side_effects: InteroceptionChannel.last_fired_tick and .is_armed updated
    - id: update_snapshot
      description: Capture current state for next tick's trend detection
      file: runtime/cognition/interoception.py
      function: interoception_tick (inline)
      input: current state readings
      output: new InteroceptionSnapshot
      trigger: sequential after gating
      side_effects: InteroceptionState.snapshot updated
    - id: inject_stimuli
      description: Stimuli passed back to tick runner, injected via Law 1
      file: runtime/cognition/tick_runner_l1_cognitive_engine.py
      function: _step_interoception → _step_inject
      input: list[Stimulus]
      output: energy injected into graph nodes
      trigger: tick runner receives stimuli from interoception
      side_effects: node.energy modified (via standard Law 1)
  docking_points:
    guidance:
      include_when: transformative, risky, complex
      omit_when: trivial pass-through
      selection_notes: Focus on the input boundary (what state is read) and the output boundary (what stimuli are produced)
    available:
      - id: dock_intero_input
        type: event
        direction: input
        file: runtime/cognition/interoception.py
        function: interoception_tick
        trigger: tick runner calls _step_interoception
        payload: CitizenCognitiveState + CitizenMetabolism snapshot
        async_hook: not_applicable
        needs: none (state already available)
        notes: The full internal state available to interoception — useful for verifying what state was read
      - id: dock_intero_output
        type: event
        direction: output
        file: runtime/cognition/interoception.py
        function: interoception_tick return
        trigger: function return
        payload: list[Stimulus] + updated InteroceptionState
        async_hook: not_applicable
        needs: none
        notes: The stimuli produced and channel states — critical for V2 (refractory) and V3 (cap) verification
      - id: dock_intero_injection
        type: event
        direction: output
        file: runtime/cognition/tick_runner_l1_cognitive_engine.py
        function: _step_inject (called with interoceptive stimuli)
        trigger: tick runner injects interoceptive stimuli
        payload: Stimulus objects with source="interoception"
        async_hook: not_applicable
        needs: none
        notes: Where interoceptive stimuli enter the standard physics pipeline
    health_recommended:
      - dock_id: dock_intero_output
        reason: Critical for verifying refractory gating (V2), cap enforcement (V3), and silence at steady state (V7)
      - dock_id: dock_intero_input
        reason: Needed for verifying state is not mutated (V1) — compare state before and after
```

---

## LOGIC CHAINS

### LC1: Threshold Crossing to WM Entry

**Purpose:** Trace how an internal state change becomes a thought in Working Memory.

```
frustration = 0.75 (crosses 0.7 threshold)
  → interoception_tick() reads state.limbic.emotions["frustration"]
    → evaluate_drive_channels() detects frustration > 0.7
      → ChannelReading(channel="frustration_high", fires=True, content="I feel frustrated", energy=0.6)
        → interoception_tick() returns [Stimulus(content="I feel frustrated", source="interoception", energy_budget=0.6)]
          → tick_runner._step_interoception() receives list
            → tick_runner._step_inject(stimulus) injects energy into matching nodes (via Law 1)
              → Law 4 competition: "I feel frustrated" competes for WM based on salience
                → If salient enough: enters WM → citizen "feels" frustrated
```

**Data transformation:**
- Input: `float` (frustration intensity 0.75)
- After evaluation: `ChannelReading` (fires=True, content string)
- After gating: `Stimulus` (content + energy_budget + source tag)
- After injection: Energy distributed to graph nodes matching content embedding
- Output: Node in WM (if it wins attentional competition)

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
interoception.py
    └── imports → models.py (CitizenCognitiveState, Stimulus, Node, WorkingMemory, LimbicState)
    └── imports → metabolism.py (CitizenMetabolism) — optional, guarded by None check
    └── imports → constants.py (INTERO_* thresholds)
tick_runner_l1_cognitive_engine.py
    └── imports → interoception.py (interoception_tick or InteroceptionEngine)
```

### External Dependencies

None. Interoception uses only stdlib (dataclasses, typing) and existing cognition module types.

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Channel refractory state | `InteroceptionState.channels` on `CitizenCognitiveState` | per-citizen | Created on first tick, persists across ticks, reset on wake |
| Snapshot (trend data) | `InteroceptionState.snapshot` | per-citizen | Updated every tick, rolling windows auto-prune |
| Total stimuli counter | `InteroceptionState.stimuli_generated_total` | per-citizen | Monotonically increasing, observability only |

### State Transitions

```
Channel ARMED ──(threshold crossed)──> FIRED ──(refractory period)──> COOLING ──(refractory expired + hysteresis met)──> ARMED
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. InteroceptionState created with default channels (all armed, empty snapshot)
2. Attached to CitizenCognitiveState.interoception (lazy, on first tick)
3. First tick: snapshot is None, trend channels produce no output (need history)
```

### Main Loop (within tick)

```
1. _step_limbic() completes (drives and emotions updated for this tick)
2. _step_interoception() called:
   a. interoception_tick(state, metabolism) executes
   b. Returns list[Stimulus] (0 to MAX_STIMULI_PER_TICK)
   c. Each stimulus injected via _step_inject(stimulus) — standard Law 1
3. _step_orient() called (can now incorporate interoceptive content in WM)
```

### Shutdown

No special shutdown. InteroceptionState persists as part of CitizenCognitiveState serialization.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `INTERO_MAX_STIMULI_PER_TICK` | `constants.py` | `3` | Maximum interoceptive stimuli per tick |
| `INTERO_DEFAULT_REFRACTORY` | `constants.py` | `30` | Default refractory period in ticks |
| `INTERO_DEFAULT_HYSTERESIS` | `constants.py` | `0.1` | Default hysteresis band for threshold re-arming |
| `INTERO_ENERGY_QUIET_RATIO` | `constants.py` | `0.1` | Active-to-total ratio below which "mind feels quiet" |
| `INTERO_BUDGET_LOW_THRESHOLD` | `constants.py` | `0.2` | Global energy budget below which "running low" |
| `INTERO_FATIGUE_TICKS` | `constants.py` | `500` | Awake ticks before fatigue sensation |
| `INTERO_CIRCADIAN_TROUGH` | `constants.py` | `0.2` | Phase below which "I feel drowsy" |
| `INTERO_CIRCADIAN_PEAK` | `constants.py` | `0.8` | Phase above which "I feel alert" |
| `INTERO_WM_FULL` | `constants.py` | `7` | WM size at which "mind is full" |
| `INTERO_WM_CLEAR` | `constants.py` | `2` | WM size below which "mind feels clear" (if was >= 5) |
| `INTERO_FOCUS_TICKS` | `constants.py` | `30` | WM stability ticks for focus/stagnation detection |
| `INTERO_FRUSTRATION_THRESHOLD` | `constants.py` | `0.7` | Frustration above which sensation fires |
| `INTERO_ANXIETY_THRESHOLD` | `constants.py` | `0.6` | Anxiety above which sensation fires |
| `INTERO_SATISFACTION_THRESHOLD` | `constants.py` | `0.7` | Satisfaction above which sensation fires |
| `INTERO_DRIVE_DOMINANCE_HIGH` | `constants.py` | `0.7` | Drive intensity for "dominant drive" detection |
| `INTERO_DRIVE_DOMINANCE_LOW` | `constants.py` | `0.3` | Other drives must be below this for dominance |
| `INTERO_TRUST_HIGH` | `constants.py` | `0.5` | Trust threshold for counting deep connections |
| `INTERO_SHRINKAGE_RATIO` | `constants.py` | `0.05` | Node count drop ratio for "forgetting" sensation |
| `INTERO_TREND_WINDOW` | `constants.py` | `10` | Ticks of energy history for trend detection |
| `INTERO_NODE_HISTORY_WINDOW` | `constants.py` | `100` | Ticks of node count history for brain health |
| `INTERO_ZONE_MIN_NODES` | `constants.py` | `10` | Minimum nodes for zone awareness to fire |
| `INTERO_ZONE_DOMINANCE_RATIO` | `constants.py` | `2.0` | Zone energy must exceed mean by this ratio for dominance |
| `INTERO_ZONE_QUIET_THRESHOLD` | `constants.py` | `0.2` | Zone drops below this fraction of total → "quiet" |
| `INTERO_ZONE_QUIET_PREV_MIN` | `constants.py` | `0.3` | Zone must have been above this to trigger "quiet" |
| `INTERO_EMOTION_DELTA_THRESHOLD` | `constants.py` | `0.2` | Minimum drive/emotion delta for self-perception to fire |
| `INTERO_EMOTION_SPIKE_THRESHOLD` | `constants.py` | `0.5` | Delta for "sudden spike" detection |
| `INTERO_CONTEXT_MILD_THRESHOLD` | `constants.py` | `0.5` | Context usage for mild awareness |
| `INTERO_CONTEXT_PRESSURE_THRESHOLD` | `constants.py` | `0.8` | Context usage for clear pressure |
| `INTERO_CONTEXT_CRITICAL_THRESHOLD` | `constants.py` | `0.95` | Context usage for urgent pressure |
| `INTERO_MAX_CONTEXT_WINDOW` | `constants.py` | `200000` | Estimated max context window tokens for heuristic estimation |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation (to be added on implementation):

| File | Line | Reference |
|------|------|-----------|
| `runtime/cognition/interoception.py` | 1 | `# DOCS: docs/cognition/interoception/` |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | TBD | `# DOCS: docs/cognition/interoception/ (interoception step)` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1 (capture state) | `interoception.py:interoception_tick()` |
| ALGORITHM step 2 (evaluate channels) | `interoception.py:evaluate_*()` helpers |
| ALGORITHM step 3 (gate and cap) | `interoception.py:interoception_tick()` |
| ALGORITHM step 4 (update snapshot) | `interoception.py:interoception_tick()` |
| BEHAVIOR B1-B8 | `interoception.py:evaluate_*()` channel functions (somatic awareness) |
| BEHAVIOR B9 | `interoception.py:evaluate_zone_awareness_channels()` (metacognition) |
| BEHAVIOR B10 | `interoception.py:evaluate_emotional_self_perception_channels()` |
| BEHAVIOR B11 | `interoception.py:evaluate_context_window_channels()` |
| VALIDATION V1 | `tests/cognition/test_interoception_engine.py:test_state_not_mutated` |
| VALIDATION V2 | `tests/cognition/test_interoception_engine.py:test_refractory_gating` |
| VALIDATION V3 | `tests/cognition/test_interoception_engine.py:test_stimuli_cap` |
| VALIDATION V7 | `tests/cognition/test_interoception_engine.py:test_silence_at_steady_state` |

---

## EXTRACTION CANDIDATES

None anticipated. The module is designed to be a single file (~350 lines). If channels multiply beyond 30, consider extracting channel definitions to a separate `interoception_channels.py`.

---

## MARKERS

<!-- @mind:todo Create runtime/cognition/interoception.py implementing the InteroceptionEngine class -->
<!-- @mind:todo Add _step_interoception() to tick_runner between _step_limbic and _step_orient -->
<!-- @mind:todo Add InteroceptionState to CitizenCognitiveState in models.py -->
<!-- @mind:todo Add INTERO_* constants to constants.py -->
<!-- @mind:todo Create tests/cognition/test_interoception_engine.py with invariant tests -->
<!-- @mind:todo Add interoception stimuli to TickResult for observability (new field: interoception_stimuli_count) -->
