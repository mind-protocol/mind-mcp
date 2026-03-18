# Gaze System — Patterns: Three-Force Composition for Embodied Attention

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gaze_System.md
THIS:            PATTERNS_Gaze_System.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Gaze_System.md
ALGORITHM:       ./ALGORITHM_Gaze_System.md
VALIDATION:      ./VALIDATION_Gaze_System.md
HEALTH:          ./HEALTH_Gaze_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gaze_System.md
SYNC:            ./SYNC_Gaze_System.md

IMPL:            runtime/engine/gaze_system.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Gaze_System.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Gaze_System.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Citizens have cognition (interoception, exteroception, drives, working memory) but no face. Their internal state is invisible. When a citizen is curious, frustrated, drowsy, or attentive, nothing in the body model reflects this. The 39-joint skeleton defines the physical interface (head, neck, eyes, eyelids, jaw, lips, mouth corners), but nothing drives those joints from the citizen's cognitive state.

Without a gaze system, the citizen is a statue. Or worse, they have randomly animated eyes that carry no information. A visitor talking to a citizen cannot tell whether the citizen is paying attention, bored, distracted, or thinking. The face is the primary channel through which social beings communicate presence and state. Without it, the citizen is cognitively rich but experientially dead.

The problem is not "we need eye animation." The problem is: the citizen's cognitive state needs a physical expression channel that is continuous, readable, and grounded in causation. Every eye movement, every blink, every lip position must trace back to a cognitive cause.

---

## THE PATTERN

The gaze system is a **three-force compositor** that reads cognitive state and writes body joints. Three forces compose in real-time to produce the citizen's facial behavior:

### Force 1: Awareness Target (WHERE to look)

Exteroception produces a ranked list of salient nodes in the citizen's perceptual field. The gaze system picks the most relevant positioned node as the primary gaze target. This is the same `relevance()` formula from exteroception — the gaze system does not recompute saliency, it consumes exteroception's output.

When no target is salient, the citizen enters idle exploration: slow, unfocused sweeps. When in conversation, a special social gaze mode activates: 70% on the current speaker, 30% away (natural look-away behavior).

### Force 2: Drive State (HOW to look)

Interoception provides the citizen's current drive intensities. These modulate gaze STYLE without changing gaze DIRECTION:

- **Saccade rate** — how often the eyes jump between targets
- **Fixation duration** — how long the eyes hold on a target before moving
- **Eyelid openness** — how wide the eyes are (curiosity=wide, boredom=droopy)
- **Pupil dilation** — arousal and interest signal

The same target looks different through frustrated eyes (narrowed, fixed stare) versus curious eyes (wide, rapid scanning). Drives are the emotional coloring of attention.

### Force 3: Moment Events (interrupts)

Sudden stimuli override the current gaze:

- High-energy stimulus -> startle snap toward source
- Subcall/telepathy -> brief upward glance ("receiving")
- Crystallization (Law 10) -> eyes up-right briefly ("eureka")
- Mention/@ -> snap toward mentioner
- Conversation turn -> smooth transition to new speaker

Events are transient — they interrupt, play out, and the gaze returns to Force 1/2 control.

### Composition

```
gaze_output = compose(
    target   = awareness_target(exteroception),   # Force 1: WHERE
    style    = drive_modulation(interoception),    # Force 2: HOW
    override = moment_interrupt(tick_events),      # Force 3: WHEN
)
```

The eye-head coordination layer takes this composite gaze intent and distributes it across the body model joints (left_eye, right_eye, head, neck) with appropriate response times and physical constraints.

---

## BEHAVIORS SUPPORTED

- **B1** (Awareness-Directed Gaze) — citizen looks at the most salient node
- **B2** (Social Gaze) — in conversation, 70/30 look/away ratio
- **B3** (Drive-Styled Gaze) — curiosity widens eyes, frustration narrows them
- **B4** (Event Interrupts) — sudden stimuli snap gaze to source
- **B5** (Eye-Head Coordination) — eyes lead head by 200ms
- **B6** (Circadian Blink) — blink rate reflects arousal and time-of-day
- **B7** (Lip Sync) — mouth moves when speaking, rests in emotional pose when silent
- **B8** (Idle Exploration) — slow gaze sweep when nothing is salient

## BEHAVIORS PREVENTED

- **A1** (Random gaze) — every gaze change has a traceable cause
- **A2** (100% stare) — social gaze always includes natural look-away
- **A3** (Robotic head snap) — head follows eyes with inertia, never instant
- **A4** (Static face) — face is never frozen; blink, micro-movements, and emotional pose are always active
- **A5** (Drive-overriding target) — drives modulate style but never hijack gaze direction from awareness

---

## PRINCIPLES

### Principle 1: Eyes Lead, Head Follows

The human oculomotor system moves eyes first (saccade: ~100ms), then the head rotates to center the target (~300ms). This 200ms lag is what makes gaze look natural. When the target is within 30 degrees of head center, only the eyes move. Beyond 30 degrees, the head turns. Beyond 120 degrees, the body (root) rotates. The cascade is: eyes -> head -> body, each with increasing inertia and decreasing responsiveness.

### Principle 2: Drives Modulate, Awareness Targets

This is the fundamental separation. What you look at is determined by what is salient in your environment (exteroception). How you look at it is determined by your internal state (interoception). A frustrated citizen stares fixedly at the obstacle. A curious citizen scans rapidly between novel targets. Same awareness system, different drive state, completely different visible behavior.

### Principle 3: No Random

Not a single eye movement should be unexplainable. If someone asks "why did the citizen look there?" the answer must always be traceable: "because that node had the highest relevance score" or "because a high-energy stimulus arrived" or "because the conversation turn shifted." Idle exploration is not random — it is the lowest-energy mode of the awareness system when no node passes the saliency threshold.

### Principle 4: Social Gaze is Special

In conversation, humans do not stare at the speaker continuously. The natural pattern is roughly 70% gaze-on-speaker, 30% gaze-away (thinking, processing, social comfort). This ratio is a first-class parameter. Additionally, during conversation turns, gaze transitions smoothly from the previous speaker to the new one, not instantly.

### Principle 5: Blink is Not Cosmetic

Blink rate encodes real cognitive state: arousal level, boredom depth, circadian phase. Special blinks (long blink = processing, double blink = surprise, slow droop = drowsiness) are triggered by specific cognitive events. Blink is a window into the citizen's inner state, not decoration.

### Principle 6: Lip Sync Bridges Voice and Body

When the citizen produces voice output (TTS), the jaw and lips must move with viseme-mapped phoneme correspondence. When silent, the mouth holds an emotional resting pose (smile for satisfaction, frown for frustration, neutral for baseline). The mouth is never unanimated.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `citizen_body_model.yaml` | FILE | The 39-joint skeleton with eye, eyelid, head, neck, jaw, lip, and mouth corner joints — defines all controllable DOFs |
| `runtime/cognition/exteroception.py` | FILE | Provides the awareness target — most salient positioned node in the perceptual field |
| `runtime/cognition/interoception.py` | FILE | Provides drive intensities — curiosity, frustration, boredom, rest, anxiety, affiliation, achievement |
| `runtime/cognition/metabolism.py` | FILE | Provides circadian phase — modulates blink rate baseline and eyelid openness |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Provides moment events (stimuli) that trigger gaze interrupts |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `cognition/exteroception` | Provides the saliency-ranked list of perceived nodes (Force 1: gaze target selection) |
| `cognition/interoception` | Provides current drive intensities (Force 2: gaze style modulation) |
| `cognition/metabolism` | Provides circadian phase for blink rate and eyelid baseline |
| `cognition/tick_runner` | Provides stimulus events for moment interrupts (Force 3) |
| `cognition/proprioception` | Receives head_pitch, head_yaw feedback from gaze output |
| `citizen_body_model.yaml` | Defines joint constraints (eye rotation limits, eyelid blend range, jaw pitch range) |

---

## INSPIRATIONS

**Human oculomotor system.** The eyes-lead-head-follows pattern with 200ms lag is well-documented in neuroscience. Saccades complete in 20-100ms, head movements in 200-500ms. The vestibulo-ocular reflex (VOR) stabilizes gaze during head movement. Our system simplifies this to a two-stage lerp with different rates.

**Yarbus (1967) eye tracking.** Different tasks produce different scanpaths over the same image. Our drive-modulated gaze style is the computational analog: different internal states produce different gaze patterns over the same environment.

**Embodied cognition / Damasio.** Emotion is not separate from cognition — it shapes perception and action. The gaze system makes this visible: drives don't just affect thinking, they affect how the citizen physically looks at the world.

**Social gaze research (Argyle & Cook, 1976).** The 60-70% gaze-on-speaker ratio during conversation is a robust finding in social psychology. Deviations from this (too much staring = dominance/aggression, too little = disinterest/deception) carry social meaning.

**Disney animation principles.** "Anticipation" and "follow-through" apply directly: eyes anticipate head movement, head follows through after eyes arrive. This is what makes animated characters feel alive.

---

## SCOPE

### In Scope

- Gaze target selection from exteroception saliency output
- Drive-modulated gaze style (saccade rate, fixation duration, eyelid openness, pupil dilation)
- Moment event interrupts (stimulus snaps, conversation turns, crystallization)
- Eye-head coordination with 200ms lag and angular thresholds
- Blink system driven by circadian phase, arousal, and boredom
- Special blinks (long, double, slow droop, wink)
- Lip sync from TTS viseme output
- Emotional mouth resting pose from drive state
- Social gaze mode (70/30 ratio in conversation)
- Idle exploration mode (no salient target)
- Writing computed joint values to the body model (head, neck, eyes, eyelids, jaw, lips, mouth corners)
- Feedback to proprioception (head_pitch, head_yaw)

### Out of Scope

- **Body posture** — spine, arms, legs are handled by separate posture/animation systems
- **Gaze perception** — detecting WHERE other citizens are looking is an exteroception concern
- **TTS generation** — producing speech audio is upstream; we consume viseme output
- **Gesture animation** — hand/arm gestures are a separate expressiveness channel
- **3D rendering** — applying joint values to meshes is the engine's concern

---

## MARKERS

<!-- @mind:todo Define the data contract between exteroception and the gaze system. Does exteroception export a ranked list of (node_id, position, relevance) tuples? Or a single "most salient target" with position? The gaze system needs at minimum a target position and a relevance score. -->

<!-- @mind:todo Clarify how conversation mode is detected. Does the gaze system receive a "in_conversation" flag from the tick runner? Or does it infer conversation from the stimulus source? Conversation mode changes gaze behavior fundamentally (70/30 ratio, speaker tracking). -->

<!-- @mind:proposition In v2, the gaze system could emit its own stimuli back to the cognitive system: "I noticed I keep looking at X" could become a self-awareness signal. This would close the perception-action loop — the citizen becomes aware of where they are looking. -->
