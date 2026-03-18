# Gaze System — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gaze_System.md
BEHAVIORS:       ./BEHAVIORS_Gaze_System.md
PATTERNS:        ./PATTERNS_Gaze_System.md
ALGORITHM:       ./ALGORITHM_Gaze_System.md
VALIDATION:      ./VALIDATION_Gaze_System.md
THIS:            IMPLEMENTATION_Gaze_System.md (you are here)
HEALTH:          ./HEALTH_Gaze_System.md
SYNC:            ./SYNC_Gaze_System.md

IMPL:            runtime/engine/gaze_system.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/
├── engine/
│   ├── __init__.py                              # exports GazeSystem
│   ├── gaze_system_three_force_compositor.py    # main gaze tick: target resolution, eye-head coord
│   ├── gaze_drive_modulator.py                  # drive-to-style parameter computation
│   ├── gaze_blink_state_machine.py              # blink rate, special blinks, eyelid animation
│   ├── gaze_lip_sync_and_emotional_mouth.py     # viseme mapping + emotional resting pose
│   └── gaze_config_and_dataclasses.py           # GazeState, GazeConfig, GazeOutput dataclasses
├── cognition/
│   ├── exteroception.py                         # (dependency) provides AwarenessOutput
│   ├── interoception.py                         # (dependency) provides drive intensities
│   ├── metabolism.py                            # (dependency) provides circadian_phase()
│   ├── proprioception.py                        # (dependency) receives head_pitch/yaw feedback
│   └── tick_runner_l1_cognitive_engine.py        # (dependency) provides tick events, integration point
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `gaze_config_and_dataclasses.py` | All data structures | `GazeState`, `GazeConfig`, `GazeOutput` | ~120 | OK |
| `gaze_system_three_force_compositor.py` | Main compositor | `gaze_tick()`, `resolve_target()`, `eye_head_coordination()` | ~250 | OK |
| `gaze_drive_modulator.py` | Drive-to-style mapping | `compute_drive_modulation()`, `emotional_mouth_corner()` | ~80 | OK |
| `gaze_blink_state_machine.py` | Blink system | `blink_tick()`, `compute_blink_rate()`, `trigger_special_blink()` | ~120 | OK |
| `gaze_lip_sync_and_emotional_mouth.py` | Mouth/lip control | `lip_sync_tick()`, `emotional_mouth_tick()`, `viseme_map()` | ~100 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (5-phase sequential processing per tick)

**Why this pattern:** Each phase depends on the output of the previous phase. Target resolution must happen before eye-head coordination. Drive modulation must happen before eyelid values are written. The pipeline ensures deterministic execution order and makes debugging straightforward — you can inspect the state after any phase.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| State Machine | `gaze_blink_state_machine.py:blink_tick()` | Blink has discrete phases (none/closing/opening) with transitions |
| Compositor | `gaze_system_three_force_compositor.py:resolve_target()` | Three forces (awareness, drives, events) compose into one gaze intent |
| Config Object | `gaze_config_and_dataclasses.py:GazeConfig` | All tunable parameters in one place, no magic numbers in logic |

### Anti-Patterns to Avoid

- **God file**: Don't let the compositor grow beyond 300 lines. If it needs more logic, extract into helper modules (drive modulation, blink, lip sync are already separated).
- **Random injection**: Never use `random.random()` without a seed. All stochastic behavior (social gaze timing, blink interval jitter) must be seeded by citizen_id for reproducibility.
- **Direct joint writing**: Never write to body model joints from outside `gaze_tick()`. All facial joint control flows through the gaze system to prevent conflicts.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Gaze computation | Target resolution, eye-head coord, blink, lip sync | Cognitive state computation, 3D rendering | `gaze_tick()` takes cognitive inputs, returns `GazeOutput` |
| Drive modulation | Parameter computation from drives | Drive generation (interoception), drive effects on cognition | `compute_drive_modulation(drives) -> StyleParams` |
| Blink system | Blink timing and eyelid animation | Circadian computation, arousal computation | `blink_tick(circadian_phase, arousal, boredom, dt) -> eyelid values` |

---

## SCHEMA

### GazeState

```yaml
GazeState:
  required:
    - eye_pitch: float            # current vertical eye angle (radians)
    - eye_yaw_left: float         # left eye horizontal (radians)
    - eye_yaw_right: float        # right eye horizontal (radians)
    - head_pitch: float           # head vertical (radians)
    - head_yaw: float             # head horizontal (radians)
    - eyelid_left: float          # 0=open, 1=closed
    - eyelid_right: float         # 0=open, 1=closed
    - jaw_angle: float            # 0=closed, 0.4=open
    - mouth_corner_left: float    # -0.5=frown, +0.8=smile
    - mouth_corner_right: float
    - blink_phase: str            # "none"|"closing"|"opening"
    - blink_timer: float          # seconds until next blink
    - in_conversation: bool
    - interrupt_active: bool
  constraints:
    - all joint values must be within citizen_body_model.yaml limits
    - blink_phase must be one of: "none", "closing", "opening"
```

### GazeOutput

```yaml
GazeOutput:
  required:
    - head_pitch: float
    - head_yaw: float
    - neck_pitch: float
    - neck_yaw: float
    - left_eye_pitch: float
    - left_eye_yaw: float
    - right_eye_pitch: float
    - right_eye_yaw: float
    - left_eyelid: float
    - right_eyelid: float
    - jaw_angle: float
    - mouth_corner_left: float
    - mouth_corner_right: float
    - pupil_dilation: float
  optional:
    - body_yaw_delta: float       # requested root rotation
    - gaze_cause: str             # traceability: "awareness"|"event"|"social"|"idle"
  relationships:
    - writes_to: BodyState (proprioception feedback)
    - writes_to: body model joints (engine)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `gaze_tick()` | `gaze_system_three_force_compositor.py:1` | tick_runner calls once per tick after cognition phases |
| `reset_gaze_state()` | `gaze_config_and_dataclasses.py:1` | citizen initialization (new citizen or session start) |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Per-Tick Gaze Computation

Explain what this flow covers: The complete pipeline from cognitive inputs to body model joint targets, executed once per tick. This is the only flow — the gaze system has no async or event-driven paths.

```yaml
flow:
  name: gaze_tick_pipeline
  purpose: Compute facial joint targets from cognitive state each tick
  scope: reads cognition outputs, writes body model joints
  steps:
    - id: step_1_resolve_target
      description: Evaluate three forces (events > awareness > idle) to determine gaze target
      file: runtime/engine/gaze_system_three_force_compositor.py
      function: resolve_target()
      input: exteroception_output, tick_events, conversation_state
      output: target_position, interrupt_state
      trigger: gaze_tick() called by tick_runner
      side_effects: updates GazeState.interrupt_*, GazeState.social_*

    - id: step_2_eye_head_coord
      description: Distribute target across eye and head joints with lerp and lag
      file: runtime/engine/gaze_system_three_force_compositor.py
      function: eye_head_coordination()
      input: target_position, GazeState, dt
      output: updated eye/head/neck joint values in GazeState
      trigger: after step_1
      side_effects: mutates GazeState joint fields

    - id: step_3_drive_modulation
      description: Compute eyelid openness, pupil dilation, saccade/fixation params from drives
      file: runtime/engine/gaze_drive_modulator.py
      function: compute_drive_modulation()
      input: drive_intensities
      output: StyleParams (eyelid_openness, pupil_dilation, saccade_rate, fixation_duration)
      trigger: after step_2
      side_effects: updates GazeState.eyelid_* (if not in blink)

    - id: step_4_blink
      description: Run blink state machine, compute eyelid animation
      file: runtime/engine/gaze_blink_state_machine.py
      function: blink_tick()
      input: circadian_phase, arousal, boredom, dt, GazeState.blink_*
      output: updated eyelid values, blink timer
      trigger: after step_3
      side_effects: overrides GazeState.eyelid_* during active blink

    - id: step_5_lip_mouth
      description: Compute jaw, lip, and mouth corner values from viseme or drives
      file: runtime/engine/gaze_lip_sync_and_emotional_mouth.py
      function: lip_sync_tick() or emotional_mouth_tick()
      input: tts_viseme or drive_intensities
      output: updated jaw/lip/mouth_corner values in GazeState
      trigger: after step_4
      side_effects: mutates GazeState.jaw_*, lip_*, mouth_corner_*

    - id: step_6_package
      description: Assemble GazeOutput from GazeState, clamp to body model limits
      file: runtime/engine/gaze_system_three_force_compositor.py
      function: package_output()
      input: GazeState, pupil_dilation, body_yaw_delta
      output: GazeOutput
      trigger: after step_5
      side_effects: none (pure assembly)

  docking_points:
    guidance:
      include_when: transformative boundaries (cognitive input -> joint output)
      omit_when: internal state mutations within a single file
      selection_notes: dock at input (cognitive state) and output (joint targets) boundaries
    available:
      - id: dock_input_cognitive
        type: event
        direction: input
        file: runtime/engine/gaze_system_three_force_compositor.py
        function: gaze_tick()
        trigger: tick_runner per-tick call
        payload: exteroception_output, drive_intensities, circadian_phase, tick_events, conversation_state, tts_viseme
        async_hook: not_applicable
        needs: none
        notes: all cognitive inputs arrive synchronously at tick boundary

      - id: dock_output_joints
        type: event
        direction: output
        file: runtime/engine/gaze_system_three_force_compositor.py
        function: gaze_tick()
        trigger: return from gaze_tick()
        payload: GazeOutput (all joint targets + proprioception feedback)
        async_hook: not_applicable
        needs: none
        notes: output consumed by engine body model and proprioception

    health_recommended:
      - dock_id: dock_input_cognitive
        reason: verify that gaze receives valid cognitive inputs (non-null exteroception, drive values in range)
      - dock_id: dock_output_joints
        reason: verify that all output joint values are within body model constraints (V1)
```

---

## LOGIC CHAINS

### LC1: Awareness to Eye Direction

**Purpose:** Translate the most salient environmental target into eye joint angles.

```
exteroception.top_target.position
  -> world_pos_to_head_angles(pos, citizen_pos, citizen_facing)
    -> (target_pitch, target_yaw)
      -> lerp(current_eye, target, 0.4)
        -> clamped eye joint values
```

**Data transformation:**
- Input: `Vec3` — world-space position of most salient node
- After step 1: `(float, float)` — pitch/yaw angles relative to citizen
- After step 2: `(float, float)` — interpolated eye angles (approaching target)
- Output: `(float, float)` — clamped to body model eye constraints

### LC2: Drives to Eyelid State

**Purpose:** Translate drive intensities into eyelid openness.

```
interoception.drives
  -> compute_drive_modulation(drives)
    -> eyelid_openness = 1.0 - 0.5*rest - 0.3*boredom + 0.2*curiosity
      -> clamp(0.0, 1.0)
        -> eyelid_blend = 1.0 - openness
          -> lerp(current_eyelid, eyelid_blend, 0.2)
```

### LC3: Circadian Phase to Blink Rate

**Purpose:** Translate time-of-day awareness into blink frequency.

```
metabolism.circadian_phase()
  -> blink_rate = 15 + 5*boredom - 3*arousal
    -> clamp(3.0, 30.0)
      -> blink_interval = 60.0 / blink_rate
        -> blink_timer countdown
          -> blink state machine trigger
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
gaze_system_three_force_compositor
    └── imports -> gaze_config_and_dataclasses (GazeState, GazeConfig, GazeOutput)
    └── imports -> gaze_drive_modulator (compute_drive_modulation)
    └── imports -> gaze_blink_state_machine (blink_tick)
    └── imports -> gaze_lip_sync_and_emotional_mouth (lip_sync_tick, emotional_mouth_tick)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `math` | `atan2`, `cos`, `sin`, `pi`, `sqrt` for angle computations | `gaze_system_three_force_compositor.py` |
| `dataclasses` | `@dataclass` for GazeState, GazeConfig, GazeOutput | `gaze_config_and_dataclasses.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| GazeState | per-citizen instance | citizen | created at citizen init, persists across ticks, reset at session boundaries |
| GazeConfig | per-citizen instance (but typically shared defaults) | citizen | created at citizen init, immutable during runtime |

### State Transitions

```
idle ──(salient target)──> tracking ──(target lost)──> idle
  |                           |
  +──(event interrupt)──> interrupt_hold ──(timer expires)──> tracking or idle
  |
  +──(conversation start)──> social_gaze ──(conversation end)──> idle or tracking
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Create GazeConfig with default parameters
2. Create GazeState with neutral joint values (eyes forward, eyelids open, mouth neutral)
3. Set blink_timer to initial interval (60 / 15 = 4 seconds)
4. Register gaze_tick() with tick_runner as post-cognition hook
```

### Main Loop / Request Cycle

```
1. tick_runner completes cognition phases (exteroception, interoception, laws)
2. tick_runner calls gaze_tick(exteroception_output, drives, circadian_phase, events, conversation, viseme, body_state, dt)
3. gaze_tick() runs 6 phases sequentially
4. gaze_tick() returns GazeOutput
5. tick_runner writes GazeOutput to body model and proprioception
```

### Shutdown

```
1. GazeState is serialized if citizen state is being persisted
2. No cleanup needed — no file handles, no network connections, no threads
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `eye_lerp_factor` | `GazeConfig` | `0.4` | Eye convergence speed per tick |
| `head_lerp_factor` | `GazeConfig` | `0.1` | Head convergence speed per tick |
| `head_lag_ms` | `GazeConfig` | `200.0` | Milliseconds eyes arrive before head |
| `social_look_ratio` | `GazeConfig` | `0.70` | Fraction of time looking at speaker |
| `blink_base_rate` | `GazeConfig` | `15.0` | Blinks per minute at neutral |
| `blink_rate_min` | `GazeConfig` | `3.0` | Minimum blinks/min (clamped) |
| `blink_rate_max` | `GazeConfig` | `30.0` | Maximum blinks/min (clamped) |
| `idle_sweep_speed` | `GazeConfig` | `0.1` | Radians/sec for idle exploration |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| (to be created) | - | `# DOCS: docs/engine/gaze_system/` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Phase 1 | `gaze_system_three_force_compositor.py:resolve_target()` |
| ALGORITHM Phase 2 | `gaze_system_three_force_compositor.py:eye_head_coordination()` |
| ALGORITHM Phase 3 | `gaze_drive_modulator.py:compute_drive_modulation()` |
| ALGORITHM Phase 4 | `gaze_blink_state_machine.py:blink_tick()` |
| ALGORITHM Phase 5 | `gaze_lip_sync_and_emotional_mouth.py:lip_sync_tick()` |
| VALIDATION V1 | (test to be written) |
| VALIDATION V2 | (test to be written) |
| VALIDATION V5 | (test to be written) |

---

## EXTRACTION CANDIDATES

No extraction needed at design time. All files are estimated under 250 lines.

---

## MARKERS

<!-- @mind:todo Create the runtime/engine/ directory and stub files with docstrings and empty function signatures. -->

<!-- @mind:todo Define the integration point with tick_runner. Where exactly in the tick loop does gaze_tick() get called? After Law 10? After all cognition phases? Document the hook mechanism. -->

<!-- @mind:todo Define the body model write interface. Does gaze_tick() return a GazeOutput that the tick_runner writes to a shared body state? Or does gaze_tick() write directly to a body state object? The former is cleaner (no side effects in gaze_tick). -->

<!-- @mind:proposition Consider making GazeConfig loadable from a YAML file per citizen archetype, so different citizen types can have different gaze characteristics (e.g., a nervous citizen type with higher saccade_rate_base). -->

<!-- @mind:escalation The gaze system needs a coordinate system convention agreed with the engine. The body model uses local coordinates (rest_position relative to parent joint). The gaze system needs world-space target positions from exteroception. Who does the transform? Document this handoff. -->
