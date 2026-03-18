# Gaze System — Behaviors: Observable Facial and Ocular Effects

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gaze_System.md
THIS:            BEHAVIORS_Gaze_System.md (you are here)
PATTERNS:        ./PATTERNS_Gaze_System.md
ALGORITHM:       ./ALGORITHM_Gaze_System.md
VALIDATION:      ./VALIDATION_Gaze_System.md
HEALTH:          ./HEALTH_Gaze_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gaze_System.md
SYNC:            ./SYNC_Gaze_System.md

IMPL:            runtime/engine/gaze_system.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Citizen Looks at Most Salient Target

**Why:** The citizen's gaze must reflect what they are attending to. If exteroception identifies a salient node with a position, the citizen's eyes and head should orient toward it. This makes the citizen's attention visible and readable.

```
GIVEN:  exteroception has identified positioned nodes with relevance scores
WHEN:   gaze_tick() runs
THEN:   eyes orient toward the node with highest relevance score
AND:    head follows eyes with 200ms lag
AND:    if target is within 30deg of head center, only eyes move
```

### B2: Social Gaze Alternation in Conversation

**Why:** Staring at a speaker 100% of the time is unnatural and aggressive. Humans alternate between looking at the speaker and looking away. This behavior makes the citizen feel socially present rather than robotic.

```
GIVEN:  citizen is in an active conversation with one or more speakers
WHEN:   gaze_tick() runs during conversation mode
THEN:   citizen looks at the current speaker ~70% of the time
AND:    citizen looks away (random offset within FOV) ~30% of the time
AND:    transitions between speaker and away are smooth (lerp), not instant
```

### B3: Curiosity Widens Eyes and Increases Scanning

**Why:** A curious citizen should look visibly different from a bored or frustrated citizen. Curiosity drives wider eyelid openness, faster saccade rate, and more frequent target switches. This is the "how they look" dimension.

```
GIVEN:  interoception reports curiosity drive intensity > 0.5
WHEN:   drive modulation is applied to gaze style
THEN:   eyelid_openness increases by up to +0.2 (eyes widen)
AND:    saccade_rate increases (more frequent gaze shifts)
AND:    head turns more often (broader scanning pattern)
```

### B4: Frustration Narrows Eyes and Fixes Gaze

**Why:** Frustration produces visible facial tension — narrowed eyes, fixed stare at the obstacle. This communicates to observers that the citizen is struggling and focused on a problem.

```
GIVEN:  interoception reports frustration drive intensity > 0.5
WHEN:   drive modulation is applied to gaze style
THEN:   eyelid_openness decreases to ~0.3 (eyes narrow)
AND:    fixation_duration increases (eyes lock on target longer)
AND:    saccade_rate decreases (minimal scanning)
```

### B5: Anxiety Produces Rapid Darting and Elevated Blink

**Why:** Anxiety is visible in rapid, unfocused eye movement and elevated blink rate. The citizen never fixates long on any target, communicating unease and hypervigilance.

```
GIVEN:  interoception reports anxiety drive intensity > 0.5
WHEN:   drive modulation is applied to gaze style
THEN:   saccade_rate increases sharply (rapid darting between targets)
AND:    fixation_duration drops below 1 second
AND:    blink_rate increases above baseline
AND:    no sustained fixation on any single target
```

### B6: Boredom Droops Eyelids and Unfocuses Gaze

**Why:** A bored citizen should look bored. Heavy eyelids, unfocused gaze, no strong fixation on any target. This is the visible signal that the citizen is under-stimulated.

```
GIVEN:  interoception reports boredom drive intensity > 0.5
WHEN:   drive modulation is applied to gaze style
THEN:   eyelid_openness drops toward 0.6 (eyelids heavy)
AND:    gaze drifts without fixation (no target holds attention)
AND:    blink_rate increases (bored blinking)
```

### B7: Rest Lowers Head and Half-Closes Eyes

**Why:** A resting citizen at circadian trough should visibly wind down. Head slightly lowered, eyelids half-closed, gaze angled downward. This communicates that the citizen is at rest, not disengaged.

```
GIVEN:  interoception reports rest drive intensity > 0.5 OR circadian phase < 0.2
WHEN:   drive modulation is applied to gaze style
THEN:   eyelid_openness drops toward 0.5 (half-closed)
AND:    head_pitch decreases slightly (head lowers)
AND:    gaze direction angles downward
AND:    blink_rate decreases (slower, heavier blinks)
```

### B8: Achievement Produces Laser Focus

**Why:** A citizen working toward a goal should show visible concentration. Eyes locked on the work target, minimal social scanning, jaw set.

```
GIVEN:  interoception reports achievement drive intensity > 0.5
WHEN:   drive modulation is applied to gaze style
THEN:   fixation_duration increases on task-related target
AND:    saccade_rate decreases (minimal distraction scanning)
AND:    social gaze scanning is reduced
```

### B9: Affiliation Sustains Gaze on Interlocutor

**Why:** When a citizen feels socially connected, they sustain eye contact more comfortably. The look-away ratio decreases, eyelids relax, and the face softens.

```
GIVEN:  interoception reports affiliation drive intensity > 0.5
WHEN:   citizen is in conversation mode
THEN:   speaker gaze ratio increases toward 80% (from 70% default)
AND:    eyelid_openness is relaxed (not wide, not narrow)
AND:    fixation_duration on interlocutor increases
```

### B10: High-Energy Stimulus Snaps Gaze to Source

**Why:** Sudden events demand attention. When a stimulus arrives with energy > 0.5 and a position, the citizen's eyes should snap toward it immediately, followed by head rotation. This is the startle response.

```
GIVEN:  a stimulus arrives with energy > 0.5 and a source position
WHEN:   the moment interrupt is processed
THEN:   eyes snap to source position within 100ms
AND:    eyelids widen briefly (startle)
AND:    head follows toward source within 300ms
AND:    after 1-2 seconds, gaze returns to Force 1 control (awareness target)
```

### B11: Conversation Turn Shifts Gaze to New Speaker

**Why:** When the active speaker changes in a conversation, the citizen's gaze should smoothly transition to the new speaker, not snap instantly. This communicates natural conversation tracking.

```
GIVEN:  a conversation turn change is detected (new speaker)
WHEN:   the moment interrupt is processed
THEN:   eyes smoothly transition to new speaker position (lerp over ~300ms)
AND:    head follows eyes
AND:    social gaze 70/30 timer resets
```

### B12: Crystallization Produces Brief Upward Glance

**Why:** When Law 10 crystallization occurs (a new concept forms), the citizen's eyes briefly glance up and to the right — the "eureka" micro-expression. This is a brief interrupt that communicates insight.

```
GIVEN:  a crystallization event (Law 10) is detected
WHEN:   the moment interrupt is processed
THEN:   eyes glance up and to the right for ~500ms
AND:    eyelids widen slightly
AND:    gaze returns to previous target after 500ms
```

### B13: Circadian-Driven Blink Rate

**Why:** Blink rate is not constant. It reflects arousal (low arousal = fewer blinks per minute at extreme rest, but more heavy blinks), boredom (more blinks), and circadian phase (trough = slower, heavier blinks). This makes the citizen's temporal state readable.

```
GIVEN:  circadian phase, arousal level, and boredom level are known
WHEN:   blink system runs each tick
THEN:   blink_rate = 15 + 5 * boredom - 3 * arousal (clamped to [3, 30])
AND:    each blink is 0.15s close + 0.15s open
AND:    at circadian trough (phase < 0.2), blinks are slower and heavier (0.25s close)
```

### B14: Special Blinks Encode Cognitive Events

**Why:** Certain cognitive events produce distinctive blink patterns that carry meaning beyond the baseline rate.

```
GIVEN:  a cognitive event occurs (processing, surprise, drowsiness, deliberate social signal)
WHEN:   the blink system detects the event
THEN:   long blink (0.5s) for processing/thinking
AND:    rapid double-blink for surprise (stimulus energy > 0.7)
AND:    slow eyelid droop (0.8s) at circadian trough (phase < 0.15)
AND:    wink (one eye only) only when affiliation > 0.7 AND confidence > 0.7 (rare)
```

### B15: Lip Sync During Speech

**Why:** When the citizen speaks, the mouth must move. Viseme-mapped lip sync connects the citizen's voice to their body, making speech feel embodied rather than disembodied text.

```
GIVEN:  the citizen is producing speech output (TTS active)
WHEN:   viseme data is available for the current phoneme
THEN:   jaw_angle maps to the viseme's jaw target (0.0 closed to 0.4 open)
AND:    lip blend shapes map to the viseme's mouth shape (15 standard visemes)
AND:    transitions between visemes are smooth (lerp, not snap)
```

### B16: Emotional Mouth at Rest

**Why:** When the citizen is not speaking, the mouth should reflect their emotional state, not freeze in a neutral position. A satisfied citizen subtly smiles. A frustrated citizen subtly frowns. The face is never completely static.

```
GIVEN:  the citizen is not currently speaking
WHEN:   gaze_tick() computes mouth state
THEN:   mouth_corners reflect satisfaction (up) or frustration (down) based on drive intensities
AND:    satisfaction > 0.5 produces corners-up (smile)
AND:    frustration > 0.5 produces corners-down (frown)
AND:    curiosity > 0.5 produces slight jaw open (surprise micro-expression)
AND:    default is neutral (corners at 0)
```

### B17: Idle Exploration When Nothing Salient

**Why:** When exteroception identifies no target above the saliency threshold, the citizen should not stare at nothing. Instead, slow, unfocused sweeps give the impression of a resting but aware being.

```
GIVEN:  no positioned node has relevance above the saliency threshold
WHEN:   gaze target selection runs
THEN:   gaze enters idle exploration mode
AND:    eyes make slow sweeps across the FOV (low saccade rate)
AND:    head stays mostly centered, minimal movement
AND:    eyelids relax toward neutral openness
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Causally grounded gaze | Every gaze direction traces to a salient target |
| B2, B9, B11 | Natural eye-head coordination | Social gaze requires natural movement patterns |
| B3, B4, B5, B6, B7, B8 | Drive-modulated gaze style | Each drive produces a visibly different gaze behavior |
| B10, B12 | Causally grounded gaze | Event interrupts are traceable to specific stimuli |
| B13, B14 | Blink as biological signal | Blink rate and patterns encode cognitive state |
| B15, B16 | Lip sync bridges voice and body | Mouth is always expressive, speaking or silent |
| B17 | Causally grounded gaze | Even idle exploration has a cause (no salient target) |

---

## INPUTS / OUTPUTS

### Primary Function: `gaze_tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| exteroception_output | AwarenessOutput | Saliency-ranked list of perceived nodes with positions |
| drive_intensities | dict[str, float] | Current drive levels from interoception (curiosity, frustration, etc.) |
| circadian_phase | float | [0, 1] from metabolism — 0=trough, 1=peak |
| tick_events | list[Stimulus] | Recent stimuli from the tick runner (for interrupt detection) |
| conversation_state | ConversationState or None | Current conversation context (speaker, turn) |
| tts_viseme | Viseme or None | Current phoneme viseme data from TTS output |
| current_body_state | BodyState | Current joint positions (for computing deltas) |
| dt | float | Time delta since last tick (seconds) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| gaze_output | GazeOutput | Target values for head, neck, eyes, eyelids, jaw, lips, mouth corners |

**Side Effects:**

- Writes computed joint targets to the body model (head pitch/yaw, neck pitch/yaw/roll, left/right eye pitch/yaw, left/right eyelid blend, jaw pitch, lip blends, mouth corner blends)
- Feeds back head_pitch and head_yaw to proprioception

---

## EDGE CASES

### E1: No Exteroception Data Available

```
GIVEN:  exteroception returns empty (L3 unreachable, graceful blindness)
THEN:   gaze defaults to idle exploration mode (slow sweep, neutral eyelids)
AND:    drive modulation still applies (the citizen can be curious while blind)
```

### E2: Multiple High-Energy Stimuli in Same Tick

```
GIVEN:  two or more stimuli with energy > 0.5 arrive simultaneously
THEN:   gaze snaps to the stimulus with highest energy
AND:    if energies are within 0.1 of each other, prefer the closest (shortest angular distance)
```

### E3: Target Behind the Citizen (>120 degrees)

```
GIVEN:  the gaze target is more than 120 degrees from the citizen's current facing
THEN:   body (root) rotation begins toward target
AND:    head turns simultaneously
AND:    eyes lead by reaching their mechanical limit toward the target
AND:    once root rotation brings target within 60 degrees, normal eye-head coordination resumes
```

### E4: Eyelid Openness Formula Produces Value Outside [0, 1]

```
GIVEN:  the combined drive modulation computes eyelid_openness outside [0, 1]
THEN:   clamp to [0, 1]
AND:    0.0 = fully closed, 1.0 = fully open
```

### E5: Conversation Mode with No Speaker Position

```
GIVEN:  citizen is in conversation but the speaker has no known position
THEN:   maintain current gaze direction (do not snap to unknown position)
AND:    apply social gaze timing (70/30) around current forward direction
```

### E6: Blink During Gaze Snap (Event Interrupt)

```
GIVEN:  a blink is in progress when a high-energy event interrupt arrives
THEN:   complete the current blink before executing the gaze snap
AND:    the interrupt is queued, not dropped
```

---

## ANTI-BEHAVIORS

### A1: Random Eye Movement

```
GIVEN:   any gaze state
WHEN:    gaze_tick() runs
MUST NOT: produce eye movement with no traceable cause
INSTEAD:  every movement must map to awareness target, drive state, event, or idle exploration
```

### A2: 100% Stare in Conversation

```
GIVEN:   citizen is in conversation
WHEN:    social gaze mode is active
MUST NOT: maintain unbroken gaze at speaker for more than 5 seconds
INSTEAD:  follow the 70/30 alternation pattern with natural timing
```

### A3: Instant Head Snap

```
GIVEN:   gaze target changes
WHEN:    head needs to reorient
MUST NOT: head rotation complete faster than 200ms
INSTEAD:  head follows eyes with lerp factor 0.1 (slow, damped)
```

### A4: Static Face When Idle

```
GIVEN:   no active conversation, no salient target, no events
WHEN:    citizen is in idle state
MUST NOT: freeze all facial joints at current values
INSTEAD:  blink system continues, idle exploration runs, emotional mouth pose is active
```

### A5: Drives Override Target Direction

```
GIVEN:   any drive state
WHEN:    gaze target is computed
MUST NOT: drive modulation change WHERE the citizen looks (only HOW)
INSTEAD:  drives modulate saccade rate, fixation duration, eyelid openness, pupil dilation
```

### A6: Blink Rate Outside Biological Range

```
GIVEN:   any combination of arousal, boredom, and circadian phase
WHEN:    blink rate formula is computed
MUST NOT: produce blink rate below 3/min or above 30/min
INSTEAD:  clamp to [3, 30] blinks/min
```

---

## MARKERS

<!-- @mind:todo Define the ConversationState data structure. What fields does the gaze system need from conversation context? Minimum: is_active, current_speaker_id, current_speaker_position, turn_just_changed. -->

<!-- @mind:todo Define the Viseme data structure for lip sync. What fields does TTS provide? Minimum: phoneme, jaw_target, lip_blend_targets, duration. -->

<!-- @mind:todo Specify how idle exploration sweep pattern works. Is it a slow sinusoidal oscillation? A random walk within a small angular range? A perlin noise curve? The pattern should feel natural, not mechanical. -->

<!-- @mind:proposition Consider adding eyebrow control. The body model has eyelids but not explicit eyebrows. Eyebrow raise/lower could be approximated by eyelid-adjacent blend shapes. This would add expressiveness (raised eyebrows = surprise, furrowed = concentration). v2 consideration. -->
