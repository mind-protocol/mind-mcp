# OBJECTIVES — Gaze System

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Gaze_System.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Gaze_System.md
BEHAVIORS:      ./BEHAVIORS_Gaze_System.md
ALGORITHM:      ./ALGORITHM_Gaze_System.md
VALIDATION:     ./VALIDATION_Gaze_System.md
IMPLEMENTATION: ./IMPLEMENTATION_Gaze_System.md
HEALTH:         ./HEALTH_Gaze_System.md
SYNC:           ./SYNC_Gaze_System.md

IMPL:           runtime/engine/gaze_system.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Causally grounded gaze** — Every gaze change has an identifiable cause (a salient target from exteroception, a drive state from interoception, or a moment event from the tick runner). No random eye movement. The citizen's eyes tell you what they are attending to and how they feel about it.

2. **Natural eye-head coordination** — Eyes lead, head follows with a 200ms lag, matching human oculomotor behavior. Small targets within 30 degrees are tracked by eyes alone. Large redirections recruit head and body rotation. The result must look like a living being, not a turret.

3. **Drive-modulated gaze style** — Awareness (exteroception) determines WHERE the citizen looks. Drives (interoception) determine HOW they look: saccade rate, fixation duration, eyelid openness, pupil dilation. The same target looks different through frustrated eyes versus curious eyes.

4. **Blink as biological signal** — Blink rate is not cosmetic animation. It encodes arousal, boredom, and circadian state. Special blinks (long, double, slow droop) convey specific cognitive events. Blink must be bounded and physiologically plausible.

5. **Lip sync bridges voice and body** — When the citizen speaks, the mouth moves with viseme-mapped articulation. When silent, the mouth rests in an emotional pose driven by drives. The face is never static.

## NON-OBJECTIVES

- **Photorealistic facial animation** — We are not building AAA face capture. The system drives a 39-joint body model with blend shapes, not a photorealistic mesh.
- **Gaze AI / social inference** — The gaze system does not infer intent from OTHER citizens' gaze. It only controls THIS citizen's gaze output.
- **Procedural body animation** — Walking, gesturing, and posture are separate systems. The gaze system controls head, eyes, eyelids, jaw, and lips only.
- **Camera control** — The gaze system controls the citizen's eyes, not the viewer's camera.

## TRADEOFFS (canonical decisions)

- When naturalness conflicts with responsiveness, choose naturalness. A 200ms head lag is more important than instant head-snap to target.
- When drive modulation conflicts with target tracking, awareness target wins direction while drives modulate style. The citizen always looks where saliency demands, but how they look is colored by emotion.
- When blink rate formula produces values outside [3, 30] blinks/min, clamp. Biological plausibility over formula purity.
- We accept visible latency in head movement to preserve the eyes-lead-head-follows principle. The alternative (instant head tracking) looks robotic.

## SUCCESS SIGNALS (observable)

- A citizen in conversation alternates gaze 70/30 between speaker and away, never staring 100%.
- A curious citizen's eyes are wide open, scanning rapidly between novel targets.
- A bored citizen's eyelids droop, gaze drifts unfocused, blink rate is elevated.
- When a loud stimulus arrives, eyes snap to source, then head follows 200ms later.
- A speaking citizen's jaw and lips move in sync with phoneme output.
- A resting citizen has half-closed eyelids, lowered head pitch, and slow blink rate.
- Blink rate stays within [3, 30] blinks/min under all drive combinations.

---

## MARKERS

<!-- @mind:todo Define the exact interface between gaze_system and the 3D engine. The gaze system computes target joint values; how are these transmitted to Three.js? WebSocket per-tick update? Shared state buffer? -->

<!-- @mind:todo Determine whether lip sync input is phoneme-level (from TTS) or text-level (estimated from output text). Phoneme-level is more accurate but requires TTS integration. -->
