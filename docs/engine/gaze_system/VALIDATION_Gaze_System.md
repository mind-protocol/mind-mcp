# Gaze System — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gaze_System.md
PATTERNS:        ./PATTERNS_Gaze_System.md
BEHAVIORS:       ./BEHAVIORS_Gaze_System.md
THIS:            VALIDATION_Gaze_System.md (you are here)
ALGORITHM:       ./ALGORITHM_Gaze_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gaze_System.md
HEALTH:          ./HEALTH_Gaze_System.md
SYNC:            ./SYNC_Gaze_System.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, would mean the gaze system has failed its purpose: the citizen's face would look wrong, robotic, or disconnected from their cognitive state.

---

## INVARIANTS

### V1: Eyes Within Mechanical Limits

**Why we care:** If eye rotation exceeds the body model constraints, the rendered mesh will deform unnaturally — eyes clipping through the head, eyelids inverting, visually broken citizen.

```
MUST:   left_eye_pitch in [-0.5, 0.5], left_eye_yaw in [-0.7, 0.3]
        right_eye_pitch in [-0.5, 0.5], right_eye_yaw in [-0.3, 0.7]
        head_pitch in [-0.3, 0.3], head_yaw in [-0.5, 0.5]
        neck_pitch in [-0.5, 0.7], neck_yaw in [-1.2, 1.2]
        eyelid_left and eyelid_right in [0.0, 1.0]
        jaw_angle in [0.0, 0.4] (mapped to jaw pitch [-0.5, 0])
        mouth_corner_left and mouth_corner_right in [-0.5, 0.8]
NEVER:  any joint value outside the constraints defined in citizen_body_model.yaml
```

### V2: Blink Rate Within Biological Range

**Why we care:** Blink rate outside [3, 30] blinks/min looks inhuman. Below 3 makes the citizen appear frozen or dead. Above 30 makes them appear to be seizing. Either destroys the illusion of a living being.

```
MUST:   computed blink_rate always in [3.0, 30.0] blinks per minute
        regardless of any combination of arousal, boredom, and circadian phase
NEVER:  blink_rate < 3.0 or blink_rate > 30.0 after clamping
```

### V3: Every Gaze Change Has a Traceable Cause

**Why we care:** Random eye movement destroys the perception of intelligence. If the citizen's gaze moves for no reason, observers cannot read their attention, and the gaze becomes noise rather than signal.

```
MUST:   every gaze direction change maps to exactly one of:
        - awareness target (exteroception saliency)
        - event interrupt (stimulus with energy > 0.5)
        - social gaze alternation (in conversation, timed toggle)
        - idle exploration (no salient target, slow sweep)
NEVER:  gaze changes that are not attributable to one of these four causes
```

### V4: Eyes Lead Head by At Least 100ms

**Why we care:** Simultaneous eye-head movement looks robotic. The 200ms lag is what makes gaze look natural. If the head arrives at the same time as the eyes, the citizen looks like a turret, not a person.

```
MUST:   when gaze target changes by > 10 degrees, eyes begin moving
        before head begins moving (head_lag >= 100ms)
NEVER:  head rotation beginning simultaneously with or before eye saccade
```

### V5: Social Gaze Never Stares 100%

**Why we care:** Unbroken eye contact for more than ~5 seconds is perceived as aggressive or abnormal by human observers. The 70/30 ratio is a well-established social norm. Violating it makes the citizen feel threatening or uncanny.

```
MUST:   in conversation mode, the citizen looks away from the speaker
        at least 20% of the time (allowing 10% tolerance below the 30% target)
        no single unbroken look-at-speaker phase exceeds 5 seconds
NEVER:  100% sustained gaze at speaker for > 5 continuous seconds
```

### V6: Smooth Transitions Between States

**Why we care:** Discontinuous jumps in joint values produce visible popping artifacts. Eyelids snapping open, head teleporting, jaw jumping. All transitions must be smoothed via lerp or equivalent interpolation.

```
MUST:   all joint value changes use lerp or smoothstep interpolation
        maximum per-tick change for head pitch/yaw < 0.15 radians
        maximum per-tick change for eyelid blend < 0.3
NEVER:  discontinuous (>0.3 radian) head rotation in a single tick
        (exception: initial startup when no previous state exists)
```

### V7: Drive Modulation Does Not Override Target

**Why we care:** If drives could hijack gaze direction, the citizen would look at things that are not salient just because they are frustrated or curious. Drives modulate style (how fast the eyes move, how open they are) but never redirect gaze to a different target.

```
MUST:   drive intensities only affect: saccade_rate, fixation_duration,
        eyelid_openness, pupil_dilation
        gaze direction is always determined by Force 1 (awareness) or
        Force 3 (events), never by drives alone
NEVER:  a drive state causing gaze to snap to a target not identified
        by exteroception or an event interrupt
```

### V8: Lip Sync Only During Speech

**Why we care:** If the jaw and lips animate viseme patterns when the citizen is silent, it looks like they are speaking when they are not. Conversely, if the mouth is frozen during speech, the citizen appears disconnected from their voice.

```
MUST:   viseme-driven lip animation only active when TTS output is active
        emotional resting pose only active when TTS is NOT active
NEVER:  viseme animation during silence
NEVER:  frozen mouth during active speech
```

### V9: Eyelid Openness Coherent With Drives

**Why we care:** If the citizen is curious but their eyelids are drooping, the face contradicts the cognitive state. The eyelid must reflect the dominant emotional tone — wide for curiosity, narrow for frustration, droopy for boredom/rest.

```
MUST:   curiosity > 0.7 produces eyelid_openness > 0.8
        boredom > 0.7 produces eyelid_openness < 0.5
        rest > 0.7 produces eyelid_openness < 0.6
        frustration > 0.7 produces eyelid_openness < 0.5
NEVER:  eyelid state contradicting the dominant drive by more than 0.3
```

### V10: Blink Completes Before Gaze Snap

**Why we care:** If a gaze snap interrupts a mid-blink, the eyelid can get stuck in a partially closed state or produce a jarring visual discontinuity. Blinks are atomic — they always complete.

```
MUST:   if a blink is in progress when an event interrupt arrives,
        the blink completes before the gaze snap executes
NEVER:  a blink abandoned mid-close or mid-open by an interrupt
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Eyes within mechanical limits | CRITICAL |
| V2 | Blink rate within biological range | CRITICAL |
| V3 | Every gaze change has a traceable cause | HIGH |
| V4 | Eyes lead head by at least 100ms | HIGH |
| V5 | Social gaze never stares 100% | HIGH |
| V6 | Smooth transitions between states | HIGH |
| V7 | Drive modulation does not override target | HIGH |
| V8 | Lip sync only during speech | MEDIUM |
| V9 | Eyelid openness coherent with drives | MEDIUM |
| V10 | Blink completes before gaze snap | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write unit tests for V1 (joint clamping) — fuzz test with extreme drive combinations to verify no joint exceeds body model constraints. -->

<!-- @mind:todo Write unit tests for V2 (blink rate bounds) — exhaustive sweep of arousal [0,1] x boredom [0,1] x circadian [0,1] to verify the formula always produces [3,30]. -->

<!-- @mind:todo Write integration tests for V4 (eye-head lag) — simulate a target jump and verify that eye position converges before head position begins moving. -->

<!-- @mind:todo Write integration tests for V5 (social gaze ratio) — run 60 seconds of simulated conversation and verify the look/away ratio is within 60-80% look range. -->

<!-- @mind:escalation V3 (traceable cause) is hard to test automatically. Consider adding a gaze_cause field to GazeOutput that records which force produced the current target. This would make the invariant verifiable by inspection. -->
