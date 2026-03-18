# Gaze System — Algorithm: Three-Force Composition, Eye-Head Coordination, Blink, Lip Sync

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
THIS:            ALGORITHM_Gaze_System.md (you are here)
VALIDATION:      ./VALIDATION_Gaze_System.md
HEALTH:          ./HEALTH_Gaze_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gaze_System.md
SYNC:            ./SYNC_Gaze_System.md

IMPL:            runtime/engine/gaze_system.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The gaze system runs once per tick and computes target joint values for head, neck, eyes, eyelids, jaw, lips, and mouth corners. It consumes three inputs (awareness target from exteroception, drive intensities from interoception, moment events from the tick runner) and composes them into a unified gaze output that is written to the body model.

The algorithm has five phases executed in sequence: (1) resolve gaze target from the three forces, (2) distribute the target across eye and head joints with coordination lag, (3) compute blink state, (4) compute lip/mouth state, and (5) package output. Each phase is deterministic given its inputs — no randomness, no LLM, no graph queries.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Causally grounded gaze | B1, B10, B12, B17 | Target resolution always traces to awareness, event, or idle fallback |
| Natural eye-head coordination | B1, B2, B5, B11 | Two-stage lerp with angular thresholds produces human-like movement |
| Drive-modulated gaze style | B3, B4, B5, B6, B7, B8, B9 | Drive formulas modulate style parameters continuously |
| Blink as biological signal | B13, B14 | Blink rate formula + special blink triggers encode cognitive state |
| Lip sync bridges voice and body | B15, B16 | Viseme mapping + emotional resting pose keep the mouth alive |

---

## DATA STRUCTURES

### GazeState (persistent across ticks)

```python
@dataclass
class GazeState:
    # Current joint positions (radians or [0,1] for blend shapes)
    eye_pitch: float = 0.0          # shared vertical eye angle
    eye_yaw_left: float = 0.0       # left eye horizontal
    eye_yaw_right: float = 0.0      # right eye horizontal
    head_pitch: float = 0.0         # head vertical
    head_yaw: float = 0.0           # head horizontal
    neck_pitch: float = 0.0         # neck vertical
    neck_yaw: float = 0.0           # neck horizontal
    eyelid_left: float = 0.0        # 0=open, 1=closed
    eyelid_right: float = 0.0       # 0=open, 1=closed
    jaw_angle: float = 0.0          # 0=closed, 0.4=fully open (mapped to jaw pitch)
    upper_lip_vertical: float = 0.0
    lower_lip_vertical: float = 0.0
    mouth_corner_left: float = 0.0  # -0.5=frown, +0.8=smile
    mouth_corner_right: float = 0.0

    # Gaze target tracking
    current_target_pos: tuple[float,float,float] | None = None
    target_arrived: bool = False     # eyes have reached the target
    head_arrived: bool = False       # head has reached the target

    # Social gaze state
    in_conversation: bool = False
    social_timer: float = 0.0        # seconds since last look-away toggle
    looking_at_speaker: bool = True  # currently in "look at speaker" phase
    social_look_duration: float = 2.5  # seconds before toggling (varies)

    # Blink state
    blink_timer: float = 0.0         # seconds until next blink
    blink_phase: str = "none"        # "none" | "closing" | "closed" | "opening"
    blink_progress: float = 0.0      # progress through current blink phase [0, 1]
    blink_type: str = "normal"       # "normal" | "long" | "double" | "droop"

    # Event interrupt state
    interrupt_active: bool = False
    interrupt_target: tuple[float,float,float] | None = None
    interrupt_timer: float = 0.0     # seconds remaining for interrupt hold
    interrupt_type: str = ""         # "startle" | "eureka" | "receiving" | "turn_change"

    # Idle exploration state
    idle_angle: float = 0.0          # current sweep angle
    idle_direction: float = 1.0      # +1 or -1 (sweep direction)
```

### GazeConfig (tunable parameters)

```python
@dataclass
class GazeConfig:
    # Eye-head coordination
    eye_lerp_factor: float = 0.4       # eyes: fast convergence
    head_lerp_factor: float = 0.1      # head: slow with damping
    eye_response_ms: float = 100.0     # eye saccade speed
    head_response_ms: float = 300.0    # head rotation speed
    head_lag_ms: float = 200.0         # eyes arrive 200ms before head
    eye_only_threshold_deg: float = 30.0   # below this, eyes only
    head_turn_threshold_deg: float = 30.0  # above this, head turns
    body_turn_threshold_deg: float = 120.0 # above this, body rotates

    # Social gaze
    social_look_ratio: float = 0.70      # fraction of time looking at speaker
    social_look_min_sec: float = 1.5     # minimum duration of a look-at phase
    social_look_max_sec: float = 4.0     # maximum duration of a look-at phase
    social_away_min_sec: float = 0.5     # minimum duration of a look-away phase
    social_away_max_sec: float = 2.0     # maximum duration of a look-away phase
    social_away_max_angle_deg: float = 25.0  # max angular offset for look-away

    # Blink
    blink_base_rate: float = 15.0        # blinks per minute at neutral
    blink_close_duration: float = 0.15   # seconds
    blink_open_duration: float = 0.15    # seconds
    blink_long_close_duration: float = 0.5   # long blink (processing)
    blink_double_interval: float = 0.2       # seconds between double-blink
    blink_droop_close_duration: float = 0.8  # slow droop at circadian trough
    blink_rate_min: float = 3.0          # blinks/min minimum
    blink_rate_max: float = 30.0         # blinks/min maximum

    # Drive modulation parameters
    saccade_rate_base: float = 0.5       # Hz baseline
    saccade_rate_anxiety_coeff: float = 2.0
    saccade_rate_focus_coeff: float = -1.0
    fixation_duration_base: float = 2.0  # seconds baseline
    fixation_duration_affiliation_coeff: float = 3.0
    fixation_duration_boredom_coeff: float = -2.0
    eyelid_openness_base: float = 1.0    # fully open baseline
    eyelid_rest_coeff: float = -0.5
    eyelid_boredom_coeff: float = -0.3
    eyelid_curiosity_coeff: float = 0.2
    pupil_dilation_base: float = 0.3
    pupil_curiosity_coeff: float = 0.4
    pupil_arousal_coeff: float = 0.3

    # Lip sync
    viseme_lerp_factor: float = 0.5      # transition speed between visemes
    jaw_max_open: float = 0.4            # maximum jaw opening

    # Idle exploration
    idle_sweep_speed: float = 0.1        # radians per second
    idle_sweep_amplitude_deg: float = 15.0  # max sweep from center

    # Interrupt timing
    startle_hold_sec: float = 1.5        # how long startle holds
    eureka_hold_sec: float = 0.5         # how long eureka glance holds
    receiving_hold_sec: float = 0.8      # how long "receiving" glance holds
```

### GazeOutput (per-tick output)

```python
@dataclass
class GazeOutput:
    # Joint targets (to be written to body model)
    head_pitch: float     # radians, constrained by body model
    head_yaw: float       # radians
    neck_pitch: float     # radians
    neck_yaw: float       # radians
    neck_roll: float      # radians
    left_eye_pitch: float
    left_eye_yaw: float
    right_eye_pitch: float
    right_eye_yaw: float
    left_eyelid: float    # 0=open, 1=closed
    right_eyelid: float
    jaw_angle: float      # 0=closed to 0.4=open (mapped to jaw pitch constraint)
    upper_lip_vertical: float
    lower_lip_vertical: float
    upper_lip_width: float
    lower_lip_width: float
    mouth_corner_left: float
    mouth_corner_right: float
    pupil_dilation: float # [0, 1] — for rendering, not a joint

    # Proprioception feedback
    head_pitch_feedback: float
    head_yaw_feedback: float

    # Optional: body rotation request (when target > 120deg)
    body_yaw_delta: float = 0.0  # requested root rotation (radians)
```

---

## ALGORITHM: `gaze_tick()`

### Phase 1: Resolve Gaze Target

Determine what the citizen is looking at by evaluating the three forces in priority order: event interrupts (Force 3) override awareness target (Force 1), and if neither provides a target, idle exploration (fallback).

```
# Force 3: Check for active event interrupts
IF state.interrupt_active:
    IF state.interrupt_timer > 0:
        target_pos = state.interrupt_target
        state.interrupt_timer -= dt
    ELSE:
        state.interrupt_active = False
        # Fall through to Force 1

# Force 3: Check for NEW event interrupts (highest priority)
FOR stimulus in tick_events (sorted by energy, descending):
    IF stimulus.energy > 0.5 AND stimulus has source_position:
        state.interrupt_active = True
        state.interrupt_target = stimulus.source_position
        state.interrupt_type = "startle"
        state.interrupt_timer = config.startle_hold_sec
        target_pos = stimulus.source_position
        BREAK

    IF stimulus is crystallization_event:
        state.interrupt_active = True
        state.interrupt_target = UP_RIGHT_OFFSET  # (0.3, 0.5, 0.2) relative
        state.interrupt_type = "eureka"
        state.interrupt_timer = config.eureka_hold_sec
        target_pos = UP_RIGHT_OFFSET
        BREAK

    IF stimulus is subcall_event:
        state.interrupt_active = True
        state.interrupt_target = UP_OFFSET  # (0.0, 0.5, 0.0) relative
        state.interrupt_type = "receiving"
        state.interrupt_timer = config.receiving_hold_sec
        target_pos = UP_OFFSET
        BREAK

# Force 3: Conversation turn change
IF conversation_state AND conversation_state.turn_just_changed:
    state.interrupt_active = True
    state.interrupt_target = conversation_state.current_speaker_position
    state.interrupt_type = "turn_change"
    state.interrupt_timer = 0.3  # brief transition, then social gaze takes over
    target_pos = conversation_state.current_speaker_position
    state.in_conversation = True
    state.looking_at_speaker = True
    state.social_timer = 0.0

# Force 1: Awareness target (if no interrupt)
IF NOT state.interrupt_active:
    IF conversation_state AND conversation_state.is_active:
        # Social gaze mode (B2)
        state.in_conversation = True
        target_pos = social_gaze_target(state, conversation_state, dt, config)
    ELIF exteroception_output.top_target is not None:
        target_pos = exteroception_output.top_target.position
        state.in_conversation = False
    ELSE:
        # Idle exploration fallback (B17)
        target_pos = idle_exploration_target(state, dt, config)
        state.in_conversation = False

state.current_target_pos = target_pos
```

### Phase 2: Eye-Head Coordination

Distribute the resolved target across eye and head joints with appropriate response times and angular thresholds.

```
# Convert target_pos to angular offset from current head center
target_pitch, target_yaw = world_pos_to_head_angles(target_pos, citizen_position, citizen_facing)

# Compute angular distance from current head orientation
angular_distance = sqrt((target_pitch - state.head_pitch)^2 + (target_yaw - state.head_yaw)^2)
angular_distance_deg = degrees(angular_distance)

# Determine coordination mode
IF angular_distance_deg < config.eye_only_threshold_deg:
    # Eyes only — head stays
    eye_target_pitch = target_pitch
    eye_target_yaw = target_yaw
    head_target_pitch = state.head_pitch  # no change
    head_target_yaw = state.head_yaw
    body_yaw_delta = 0.0

ELIF angular_distance_deg < config.body_turn_threshold_deg:
    # Eyes + head
    eye_target_pitch = target_pitch
    eye_target_yaw = target_yaw
    head_target_pitch = target_pitch
    head_target_yaw = target_yaw
    body_yaw_delta = 0.0

ELSE:
    # Eyes + head + body rotation
    eye_target_pitch = target_pitch
    eye_target_yaw = target_yaw
    head_target_pitch = target_pitch
    head_target_yaw = target_yaw
    # Request body rotation to bring target within comfortable range
    body_yaw_delta = target_yaw - state.head_yaw
    body_yaw_delta = clamp(body_yaw_delta, -0.5, 0.5)  # max rotation per tick

# Apply lerp with different rates (eyes fast, head slow)
state.eye_pitch = lerp(state.eye_pitch, eye_target_pitch, config.eye_lerp_factor)
state.eye_yaw_left = lerp(state.eye_yaw_left, eye_target_yaw, config.eye_lerp_factor)
state.eye_yaw_right = lerp(state.eye_yaw_right, eye_target_yaw, config.eye_lerp_factor)

# Head follows with lag — only start moving head after eye_response_ms
IF state.head_lag_elapsed >= config.head_lag_ms / 1000.0:
    state.head_pitch = lerp(state.head_pitch, head_target_pitch, config.head_lerp_factor)
    state.head_yaw = lerp(state.head_yaw, head_target_yaw, config.head_lerp_factor)
    # Neck distributes ~40% of head rotation
    state.neck_pitch = state.head_pitch * 0.4
    state.neck_yaw = state.head_yaw * 0.4
ELSE:
    state.head_lag_elapsed += dt

# When eyes reach target, start lag timer for head
IF abs(state.eye_pitch - eye_target_pitch) < 0.01 AND abs(state.eye_yaw_left - eye_target_yaw) < 0.01:
    state.target_arrived = True
    IF NOT state.head_lag_started:
        state.head_lag_elapsed = 0.0
        state.head_lag_started = True

# Clamp all joints to body model constraints
state.eye_pitch = clamp(state.eye_pitch, -0.5, 0.5)          # from body model
state.eye_yaw_left = clamp(state.eye_yaw_left, -0.7, 0.3)   # left eye yaw
state.eye_yaw_right = clamp(state.eye_yaw_right, -0.3, 0.7)  # right eye yaw
state.head_pitch = clamp(state.head_pitch, -0.3, 0.3)
state.head_yaw = clamp(state.head_yaw, -0.5, 0.5)
state.neck_pitch = clamp(state.neck_pitch, -0.5, 0.7)
state.neck_yaw = clamp(state.neck_yaw, -1.2, 1.2)
```

### Phase 3: Drive Modulation (Gaze Style)

Compute style parameters from drive intensities. These modulate eyelid openness and pupil dilation (applied directly) and saccade rate and fixation duration (used by Phase 1 for timing).

```
# Read drive intensities
curiosity = drives.get("curiosity", 0.0)
frustration = drives.get("frustration", 0.0)
anxiety = drives.get("anxiety", 0.0)
affiliation = drives.get("affiliation", 0.0)
boredom = drives.get("boredom", 0.0)
rest = drives.get("rest", 0.0)
achievement = drives.get("achievement", 0.0)
arousal = drives.get("arousal", 0.0)

# Focus level: composite of achievement and inverse of boredom/anxiety
focus_level = max(0.0, achievement * 0.5 + (1.0 - boredom) * 0.3 - anxiety * 0.2)

# Saccade rate (Hz) — how often eyes jump between targets
saccade_rate = (config.saccade_rate_base
                + config.saccade_rate_anxiety_coeff * anxiety
                + config.saccade_rate_focus_coeff * focus_level)
saccade_rate = max(0.1, saccade_rate)  # minimum 0.1 Hz

# Fixation duration (seconds) — how long eyes hold on a target
fixation_duration = (config.fixation_duration_base
                     + config.fixation_duration_affiliation_coeff * affiliation
                     - config.fixation_duration_boredom_coeff * boredom)
fixation_duration = max(0.3, fixation_duration)  # minimum 0.3s

# Eyelid openness [0, 1] where 1 = fully open
eyelid_openness = (config.eyelid_openness_base
                   + config.eyelid_rest_coeff * rest
                   + config.eyelid_boredom_coeff * boredom
                   + config.eyelid_curiosity_coeff * curiosity)
eyelid_openness = clamp(eyelid_openness, 0.0, 1.0)

# Override for specific states
IF state.interrupt_type == "startle":
    eyelid_openness = 1.0  # eyes widen on startle
IF frustration > 0.5:
    eyelid_openness = min(eyelid_openness, 0.3 + (1.0 - frustration) * 0.4)  # eyes narrow

# Pupil dilation [0, 1]
pupil_dilation = (config.pupil_dilation_base
                  + config.pupil_curiosity_coeff * curiosity
                  + config.pupil_arousal_coeff * arousal)
pupil_dilation = clamp(pupil_dilation, 0.0, 1.0)

# Apply eyelid (convert openness to closure: eyelid blend = 1 - openness)
target_eyelid = 1.0 - eyelid_openness
# Don't override during blink
IF state.blink_phase == "none":
    state.eyelid_left = lerp(state.eyelid_left, target_eyelid, 0.2)
    state.eyelid_right = lerp(state.eyelid_right, target_eyelid, 0.2)
```

### Phase 4: Blink System

Compute blink timing and eyelid animation. Blink rate is driven by boredom, arousal, and circadian phase.

```
# Compute blink rate (blinks per minute)
blink_rate = config.blink_base_rate + 5.0 * boredom - 3.0 * arousal
blink_rate = clamp(blink_rate, config.blink_rate_min, config.blink_rate_max)

# At circadian trough, blinks are slower and heavier
IF circadian_phase < 0.2:
    close_duration = config.blink_droop_close_duration * (1.0 - circadian_phase * 5.0)
    # Blend between normal and droop based on how deep in the trough
ELSE:
    close_duration = config.blink_close_duration

# Blink interval (seconds between blinks)
blink_interval = 60.0 / blink_rate

# Blink state machine
IF state.blink_phase == "none":
    state.blink_timer -= dt
    IF state.blink_timer <= 0:
        # Time for a blink
        state.blink_phase = "closing"
        state.blink_progress = 0.0

        # Check for special blink triggers
        IF any stimulus has is_novelty AND energy > 0.7:
            state.blink_type = "double"
        ELIF circadian_phase < 0.15:
            state.blink_type = "droop"
        ELSE:
            state.blink_type = "normal"

ELIF state.blink_phase == "closing":
    state.blink_progress += dt / close_duration
    eyelid_value = smoothstep(0.0, 1.0, state.blink_progress)
    state.eyelid_left = max(state.eyelid_left, eyelid_value)
    state.eyelid_right = max(state.eyelid_right, eyelid_value)

    IF state.blink_progress >= 1.0:
        state.blink_phase = "opening"
        state.blink_progress = 0.0

ELIF state.blink_phase == "opening":
    state.blink_progress += dt / config.blink_open_duration
    eyelid_value = 1.0 - smoothstep(0.0, 1.0, state.blink_progress)
    target_resting = 1.0 - eyelid_openness  # return to drive-modulated openness
    state.eyelid_left = max(target_resting, eyelid_value)
    state.eyelid_right = max(target_resting, eyelid_value)

    IF state.blink_progress >= 1.0:
        IF state.blink_type == "double" AND NOT state.double_blink_done:
            # Second blink of double-blink
            state.blink_phase = "closing"
            state.blink_progress = 0.0
            state.double_blink_done = True
        ELSE:
            state.blink_phase = "none"
            state.blink_timer = blink_interval
            state.double_blink_done = False
```

### Phase 5: Lip and Mouth State

Compute jaw, lip, and mouth corner positions from TTS viseme data (speaking) or drive state (silent).

```
IF tts_viseme is not None AND tts_viseme.active:
    # Speaking: viseme-driven lip sync (B15)
    target_jaw = tts_viseme.jaw_target * config.jaw_max_open
    target_upper_lip_v = tts_viseme.upper_lip_vertical
    target_lower_lip_v = tts_viseme.lower_lip_vertical
    target_upper_lip_w = tts_viseme.upper_lip_width
    target_lower_lip_w = tts_viseme.lower_lip_width
    # Mouth corners stay at emotional baseline during speech
    target_corner_left = emotional_mouth_corner(drives)
    target_corner_right = emotional_mouth_corner(drives)

    # Smooth transitions between visemes
    state.jaw_angle = lerp(state.jaw_angle, target_jaw, config.viseme_lerp_factor)
    state.upper_lip_vertical = lerp(state.upper_lip_vertical, target_upper_lip_v, config.viseme_lerp_factor)
    state.lower_lip_vertical = lerp(state.lower_lip_vertical, target_lower_lip_v, config.viseme_lerp_factor)

ELSE:
    # Silent: emotional resting pose (B16)
    satisfaction = drives.get("satisfaction", 0.0)
    curiosity_val = drives.get("curiosity", 0.0)

    # Jaw: slight open for curiosity/surprise
    IF curiosity_val > 0.5:
        target_jaw = 0.05 * curiosity_val  # subtle open
    ELSE:
        target_jaw = 0.0

    # Mouth corners: smile/frown
    corner_value = emotional_mouth_corner(drives)
    target_corner_left = corner_value
    target_corner_right = corner_value

    state.jaw_angle = lerp(state.jaw_angle, target_jaw, 0.1)

state.mouth_corner_left = lerp(state.mouth_corner_left, target_corner_left, 0.1)
state.mouth_corner_right = lerp(state.mouth_corner_right, target_corner_right, 0.1)

# Clamp all mouth values to body model constraints
state.jaw_angle = clamp(state.jaw_angle, 0.0, config.jaw_max_open)
state.mouth_corner_left = clamp(state.mouth_corner_left, -0.5, 0.8)
state.mouth_corner_right = clamp(state.mouth_corner_right, -0.5, 0.8)
```

### Phase 6: Package Output

Assemble the GazeOutput from current state, constrained to body model limits.

```
output = GazeOutput(
    head_pitch = state.head_pitch,
    head_yaw = state.head_yaw,
    neck_pitch = state.neck_pitch,
    neck_yaw = state.neck_yaw,
    neck_roll = 0.0,  # roll not currently driven by gaze
    left_eye_pitch = state.eye_pitch,
    left_eye_yaw = state.eye_yaw_left,
    right_eye_pitch = state.eye_pitch,
    right_eye_yaw = state.eye_yaw_right,
    left_eyelid = state.eyelid_left,
    right_eyelid = state.eyelid_right,
    jaw_angle = state.jaw_angle,
    upper_lip_vertical = state.upper_lip_vertical,
    lower_lip_vertical = state.lower_lip_vertical,
    upper_lip_width = state.upper_lip_width,
    lower_lip_width = state.lower_lip_width,
    mouth_corner_left = state.mouth_corner_left,
    mouth_corner_right = state.mouth_corner_right,
    pupil_dilation = pupil_dilation,
    head_pitch_feedback = state.head_pitch,
    head_yaw_feedback = state.head_yaw,
    body_yaw_delta = body_yaw_delta,
)

RETURN output
```

---

## KEY DECISIONS

### D1: Social Gaze Alternation Timing

```
IF in conversation AND NOT interrupt_active:
    state.social_timer += dt
    IF state.looking_at_speaker:
        # Currently looking at speaker — check if time to look away
        IF state.social_timer >= state.social_look_duration:
            state.looking_at_speaker = False
            state.social_timer = 0.0
            # New away-duration: random between min and max
            state.social_look_duration = uniform(config.social_away_min_sec, config.social_away_max_sec)
    ELSE:
        # Currently looking away — check if time to look back
        IF state.social_timer >= state.social_look_duration:
            state.looking_at_speaker = True
            state.social_timer = 0.0
            state.social_look_duration = uniform(config.social_look_min_sec, config.social_look_max_sec)

    WHY: The 70/30 ratio emerges from the ratio of look-at durations to look-away durations.
         2.5s look / 1.0s away ≈ 71/29.
```

### D2: Idle Exploration Sweep

```
IF no salient target AND no conversation AND no interrupt:
    state.idle_angle += config.idle_sweep_speed * state.idle_direction * dt
    max_angle = radians(config.idle_sweep_amplitude_deg)

    IF abs(state.idle_angle) > max_angle:
        state.idle_direction *= -1  # reverse sweep

    target_pos = citizen_position + forward_vector * 10.0
                 + right_vector * sin(state.idle_angle) * 5.0

    WHY: Slow sinusoidal sweep feels contemplative, not mechanical.
         The low speed (0.1 rad/s) and small amplitude (15 deg) keep it subtle.
```

### D3: Interrupt Priority When Multiple Events Arrive

```
IF multiple stimuli in same tick:
    Sort by energy (descending)
    Take first that has source_position
    Ignore lower-energy interrupts for this tick

    WHY: Only one gaze snap per tick. The most energetic event wins.
         Lower-energy events are not queued — they affect awareness through
         normal exteroception saliency in subsequent ticks.
```

### D4: Emotional Mouth Corner Computation

```
def emotional_mouth_corner(drives) -> float:
    satisfaction = drives.get("satisfaction", 0.0)
    frustration = drives.get("frustration", 0.0)

    IF satisfaction > 0.5:
        RETURN 0.3 + 0.5 * (satisfaction - 0.5)  # 0.3 to 0.55 (smile)
    ELIF frustration > 0.5:
        RETURN -0.2 - 0.3 * (frustration - 0.5)  # -0.2 to -0.35 (frown)
    ELSE:
        RETURN 0.0  # neutral

    WHY: Mouth corners are the most readable facial expression signal.
         Satisfaction produces an upward curve, frustration a downward curve.
         Values are subtle (not extreme) to avoid cartoonish expressions.
```

---

## DATA FLOW

```
Exteroception                    Interoception               Tick Events
(awareness target)               (drive intensities)         (stimuli)
        |                              |                         |
        v                              v                         v
Phase 1: Resolve Target ───────────────────────────── Phase 1: Check Interrupts
        |
        v
Phase 2: Eye-Head Coordination (lerp, angular thresholds)
        |
        v
Phase 3: Drive Modulation ◄──── drives ────► (eyelid, saccade, fixation, pupil)
        |
        v
Phase 4: Blink System ◄──── circadian phase, arousal, boredom
        |
        v
Phase 5: Lip/Mouth State ◄──── TTS viseme OR drive-based emotional pose
        |
        v
Phase 6: Package GazeOutput → Body Model (joints) + Proprioception (feedback)
```

---

## COMPLEXITY

**Time:** O(E + S) per tick — E = number of exteroception targets to scan for top target (typically < 50), S = number of stimuli to check for interrupts (typically < 10). All other operations are O(1) arithmetic: lerps, clamps, drive formula evaluation, blink state machine.

**Space:** O(1) — GazeState is fixed-size. No dynamic allocations. No growing buffers.

**Bottlenecks:**
- `world_pos_to_head_angles()` requires a coordinate transform that depends on citizen position and facing. This is pure trig, O(1).
- If exteroception provides targets pre-sorted by relevance, Phase 1 is O(1) (take first). If unsorted, O(E) for argmax.

---

## HELPER FUNCTIONS

### `lerp(current, target, factor) -> float`

**Purpose:** Linear interpolation between current and target values.

**Logic:** `current + (target - current) * factor`. Factor in [0, 1] controls convergence speed.

### `smoothstep(edge0, edge1, x) -> float`

**Purpose:** Smooth Hermite interpolation for natural-looking blink transitions.

**Logic:** `t = clamp((x - edge0) / (edge1 - edge0), 0, 1); return t * t * (3 - 2 * t)`

### `world_pos_to_head_angles(target_pos, citizen_pos, citizen_facing) -> (pitch, yaw)`

**Purpose:** Convert a world-space target position to pitch/yaw angles relative to the citizen's head.

**Logic:** Compute direction vector from citizen to target, project onto citizen's local coordinate frame, extract pitch (vertical angle) and yaw (horizontal angle).

### `social_gaze_target(state, conversation, dt, config) -> position`

**Purpose:** Compute the social gaze target with 70/30 look-at/look-away alternation.

**Logic:** If in "look at speaker" phase, return speaker position. If in "look away" phase, return a position offset from the speaker by a small angle within the citizen's FOV. Toggle between phases based on timer.

### `idle_exploration_target(state, dt, config) -> position`

**Purpose:** Compute an idle gaze target for slow environmental sweep.

**Logic:** Sinusoidal sweep across the citizen's forward arc. Low speed, small amplitude, no abrupt changes.

### `emotional_mouth_corner(drives) -> float`

**Purpose:** Compute mouth corner target from drive intensities.

**Logic:** Satisfaction -> positive (smile), frustration -> negative (frown), neutral otherwise. See D4.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `cognition/exteroception` | Read awareness output | Top salient target with position and relevance |
| `cognition/interoception` | Read drive intensities | Dict of {drive_name: intensity} values |
| `cognition/metabolism` | `.circadian_phase()` | Float [0, 1] for blink rate modulation |
| `cognition/tick_runner` | Read tick events | List of stimuli for interrupt detection |
| `cognition/proprioception` | Write head_pitch, head_yaw | Feedback for body state awareness |
| Body model (engine) | Write joint targets | GazeOutput applied to 39-joint skeleton |

---

## MARKERS

<!-- @mind:todo Implement the GazeState head_lag tracking. The current pseudocode uses head_lag_elapsed and head_lag_started but the GazeState dataclass doesn't include these fields. Add them. -->

<!-- @mind:todo The social gaze 70/30 ratio uses uniform random for phase durations. Consider whether a seeded random (per citizen ID) would be better for reproducibility in testing. -->

<!-- @mind:todo The neck distributes 40% of head rotation. This ratio should be validated against the body model constraints. If neck yaw range (1.2 rad) and head yaw range (0.5 rad) don't support this split, adjust the distribution. -->

<!-- @mind:proposition Consider micro-saccades during fixation: small involuntary eye movements that happen even when fixating. These would add realism but increase complexity. Probably v2. -->

<!-- @mind:escalation The coordinate transform in world_pos_to_head_angles() assumes the engine provides citizen_position and citizen_facing in a known coordinate frame. Need to confirm the coordinate system convention with the engine team (Y-up? Z-forward?). -->
