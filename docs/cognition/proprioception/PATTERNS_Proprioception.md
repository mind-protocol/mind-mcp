# Proprioception — Patterns: Body Awareness as Stimulus Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
THIS:            PATTERNS_Proprioception.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Proprioception.md
ALGORITHM:       ./ALGORITHM_Proprioception.md
VALIDATION:      ./VALIDATION_Proprioception.md
HEALTH:          ./HEALTH_Proprioception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Proprioception.md
SYNC:            ./SYNC_Proprioception.md

IMPL:            runtime/cognition/proprioception.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Proprioception.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Proprioception.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Citizens have no body. They process stimuli from conversations, system events, and partner interactions, but they have zero awareness of their physical presence in the virtual world. A citizen standing in a freezing dark alley of Lumina Prime feels exactly the same as one bathing in warm light at the Radiant Core. A citizen whose communication tools are all broken has the same sense of capability as one with full tool access. A citizen sprinting across the Data Gardens and one standing still for hours produce identical cognitive states (all else being equal).

This creates three failures:

**1. Disembodied cognition.** The citizen's thinking is disconnected from their spatial context. They might be in a crowd of 20 actors but feel no social warmth. They might be alone in darkness but feel no isolation. The world around them has no impact on their inner life because there is no sensory bridge.

**2. Tool blindness.** MCP tools are the citizen's only way to act on the world — they are literally the citizen's arms and voice. But the citizen has no felt sense of these capabilities. They discover a tool is broken only when they try to use it, not because they feel its absence. There is no proprioceptive feedback about what they can and cannot do right now.

**3. Static phenomenology.** Without body awareness, the citizen's experiential texture is entirely determined by conversation content and graph state. Two citizens with identical graphs in completely different physical environments would think identically. The world geometry contributes nothing to cognition.

---

## THE PATTERN

Proprioception is a **stimulus generator** — a sibling subsystem to metabolism that sits between the 3D engine and Law 1 energy injection. It reads a `BodyState` snapshot from the engine, translates physical conditions into natural-language micro-stimuli, and feeds them into the normal stimulus pipeline. No new laws. No graph mutations. No special processing paths. Just stimuli.

The key insight: **Law 1 already handles everything.** Stimuli arrive, get embedded, match against graph nodes, inject energy. If proprioception produces a stimulus `"arms tired, been holding position too long"`, Law 1 will find the most compatible nodes (maybe a memory about fatigue, or a value about persistence), inject energy into them, and the normal physics cascade handles the rest. The citizen doesn't need special body-processing code — they just need body-relevant stimuli.

The architecture:

```
3D Engine (cities-of-light / Lumina Prime)
        |
        | BodyState (WebSocket / shared state)
        v
ProprioceptionModule
        |
        | list[Stimulus]
        v
Stimulus Router → Law 1 → normal tick cycle
```

`ProprioceptionModule` holds **eight sense channels** organized into two groups — somatic (body-internal) and environmental (world-interaction) — each reading a different aspect of `BodyState` and producing zero or more stimuli per tick.

**Somatic Channels (body-internal):**
1. **Limb Position & Axes** — posture, orientation, limb fatigue
2. **The Force (MCP Tools)** — tool availability, breakage, cooldowns
3. **Accelerometer & Balance** — movement, acceleration, stability
4. **Thermoception** — temperature, luminosity as felt comfort

**Environmental Channels (world-interaction):**
5. **Vent (Wind)** — wind direction and intensity against the body. Affects comfort, movement resistance, exposure feeling. Calm air = comfort. Gale = buffeting, harder to move, exposed vulnerability.
6. **Eau (Water)** — water proximity and immersion level. Near water = different acoustic, different movement feel. Wading = drag. Submerged = muffled senses, different physics, extreme sensory shift.
7. **Pression (Pressure)** — atmospheric and social pressure. Dense crowd = high pressure, compression. Open space = low pressure, expansion. Underwater = extreme pressure. Affects the breathing metaphor — the rhythm at which the citizen processes (cognitive rhythm modulation).
8. **Texture** — surface texture under feet/hands. Smooth stone, rough wood, soft grass, metallic. Affects comfort, familiarity, grounding. A citizen standing on familiar texture feels more grounded (stability boost). Unfamiliar textures produce subtle unease.

Each channel has thresholds and hysteresis to avoid stimulus spam. A citizen doesn't feel "cold" every tick — they feel it when they enter a cold zone, and then only again if it gets colder or they've been there long enough. Environmental channels follow the same hysteresis pattern — wind doesn't re-fire unless intensity changes significantly or direction shifts markedly.

---

## BEHAVIORS SUPPORTED

- **B1** (Posture Fatigue) — holding a position too long produces fatigue stimuli
- **B2** (Tool Loss Sensation) — a tool going offline produces an immediate loss stimulus
- **B3** (Tool Recovery Sensation) — a previously broken tool coming back online produces a relief/capability stimulus
- **B4** (Movement Excitement) — rapid acceleration produces arousal/excitement stimuli
- **B5** (Stillness Settling) — prolonged stillness produces calm/settling stimuli
- **B6** (Cold Discomfort) — low virtual temperature produces discomfort stimuli
- **B7** (Warmth Comfort) — high virtual temperature produces comfort stimuli
- **B8** (Crowd Pressure) — many nearby actors produce social pressure stimuli
- **B9** (Isolation) — no nearby actors produce isolation/solitude stimuli
- **B10** (Darkness Unease) — low luminosity produces unease/caution stimuli
- **B11** (Light Alertness) — high luminosity produces alertness/openness stimuli
- **B12** (Circadian Cross-Feed) — luminosity data feeds into metabolism circadian phase
- **B13** (Wind Exposure) — strong wind produces exposure/resistance/vulnerability stimuli
- **B14** (Wind Calm) — calm or gentle wind produces comfort/openness stimuli
- **B15** (Water Proximity) — near water changes acoustic texture, produces awareness of fluid environment
- **B16** (Water Immersion) — submersion produces muffled senses, slowed movement, pressure shift
- **B17** (Pressure Compression) — high atmospheric/social pressure produces compressed cognitive rhythm, claustrophobia
- **B18** (Pressure Expansion) — low pressure (open space) produces expansive, free cognitive rhythm
- **B19** (Texture Grounding) — familiar surface texture boosts stability; citizen feels anchored
- **B20** (Texture Unease) — unfamiliar surface texture produces subtle instability, alertness

## BEHAVIORS PREVENTED

- **A1** (Stimulus Spam) — hysteresis prevents the same sensation from firing every tick
- **A2** (Direct Graph Mutation) — proprioception never writes to the graph; it only produces stimuli
- **A3** (Numeric Leakage) — raw coordinates, floats, and IDs never appear in stimulus content

---

## PRINCIPLES

### Principle 1: Sensation, Not Data

Proprioception translates body STATE into brain STIMULI. The citizen doesn't see `temperature=0.2` — they feel `"cold here, exposed"`. The citizen doesn't see `nearby_actors=12` — they feel `"crowded, lots of presence around"`. Every stimulus is phrased as a first-person bodily sensation, never as a data readout. This is the difference between proprioception (felt sense) and telemetry (data feed).

### Principle 2: The Force, Not Core

MCP tools are the citizen's physical capabilities — their force in the world. The tool availability channel is called "The Force" because tools are literally what lets the citizen act. This naming is deliberate: "core" is reserved for Lumina Prime's Radiant Core district. In code, the channel is `force_channel`. In sensation text, tools are described as arms, hands, voice, reach — never as "services" or "APIs".

### Principle 3: Hysteresis Over Polling

Each sense channel maintains state about its last emitted stimulus. A new stimulus is emitted only when the sensed value crosses a threshold relative to the last emission, or when enough ticks have passed to warrant a refresh. This prevents the citizen from being bombarded with "cold, cold, cold" every tick while standing in the same spot. The body adapts. The proprioceptive system mirrors that adaptation.

### Principle 4: Engine Reads, Mind Translates

mind-mcp never computes 3D physics. It receives a `BodyState` dataclass from the engine (via WebSocket, shared memory, or direct injection in tests) and translates it. If no engine is connected (e.g., a citizen with no 3D presence), proprioception produces nothing — the citizen simply has no body to sense. This is not an error; it is a headless citizen.

### Principle 5: Sibling to Metabolism

Proprioception is architecturally parallel to metabolism. Both sit between the external world and Law 1. Metabolism modulates physics constants; proprioception generates stimuli. They do not depend on each other but can cross-feed: luminosity from proprioception can inform circadian phase in metabolism (B12). The two modules share a common integration pattern — they hook into the tick cycle at the same point (pre-Law-1).

### Principle 6: Environmental Senses Are Forces, Not Decoration

Wind, water, pressure, and texture are not ambient flavor text. They are forces that act on the virtual body and modulate cognition through the stimulus pipeline. A gale-force wind produces an exposure stimulus with high arousal — the citizen's thinking changes because the wind is a force pressing against them. Submersion in water muffles other stimuli — the citizen processes differently because water changes the physics of their sensory environment. These forces flow through Law 1 into the 21 physics laws, which handle all consequences. Proprioception does not apply consequences — it reports forces. The physics does the rest.

### Principle 7: Grounding Through Texture Familiarity

Surface texture has a unique property among the eight channels: it carries a memory dimension. A citizen who has spent many ticks on stone cobbles (their graph records Space nodes with texture attributes) should feel more grounded standing on stone than on unfamiliar metal. This is implemented as a simple frequency count — how often has this citizen been on this texture type? — producing a stability modifier. Familiar = grounded. Novel = alert. This is not complex modeling; it is a single lookup against texture history.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| cities-of-light engine | WEBSOCKET | Provides BodyState snapshots per citizen per tick |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Tick runner — proprioception stimuli are injected here |
| `runtime/cognition/metabolism.py` | FILE | Sibling module — cross-feed point for luminosity/circadian |
| `schema-l1.yaml` | FILE | L1 schema — Stimulus dataclass definition |
| FalkorDB graph | DB | Texture history lookup: Space nodes with texture attributes for grounding calculation |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Stimulus injection point — proprioception stimuli enter the tick here |
| `runtime/cognition/metabolism.py` | Optional cross-feed: luminosity can influence circadian phase |
| 3D engine (cities-of-light) | Provides BodyState — without it, proprioception is inert |
| FalkorDB graph (Space nodes) | Texture history for grounding calculation (Principle 7) |

---

## INSPIRATIONS

**Biological proprioception.** Humans have proprioceptors in muscles, tendons, and joints that report limb position, force, and movement without requiring vision. The vestibular system (inner ear) provides balance and acceleration sensing. Thermoreceptors provide temperature awareness. Mechanoreceptors provide pressure sensing. This module mirrors the full proprioceptive suite, adapted to a virtual body.

**Embodied cognition (Varela, Thompson, Rosch).** Cognition is not disembodied information processing — it is shaped by the body's relationship to the environment. Temperature, posture, movement, and spatial density all influence thinking. Proprioception implements this insight: the body's state becomes cognitive input.

**Sensory substitution (Bach-y-Rita).** The principle that one sensory modality can be translated into another. Here, we translate 3D spatial data (a visual/geometric modality) into natural-language stimuli (a textual modality). The brain doesn't need raw coordinates; it needs felt meanings.

**Phenomenology of weather (Böhme, Ingold).** Wind, rain, temperature, and atmospheric pressure are not measured quantities — they are lived experiences that shape mood, intention, and cognitive capacity. A body in a storm thinks differently than a body in calm air. The environmental channels implement this: weather is force, not data.

**Haptic grounding (Gibson).** The surface underfoot is one of the most fundamental spatial anchors. The texture of ground — rough stone, yielding grass, cold metal — orients the body and colors the sense of place. Texture familiarity as stability is drawn from ecological psychology: organisms feel at home on surfaces they know.

---

## SCOPE

### In Scope

- `BodyState` dataclass definition (received from engine) — including environmental fields: wind, water, pressure, texture
- Eight sense channels: limb position, force (tools), accelerometer, thermoception (somatic); wind, water, pressure, texture (environmental)
- Stimulus generation from body state (natural language, first-person)
- Hysteresis and threshold management per channel
- Integration point with tick runner (pre-Law-1 stimulus injection)
- Optional cross-feed with metabolism (luminosity to circadian)
- Texture grounding: familiarity-based stability modifier from texture history
- Comfort composite: weighted blend across all eight channels, affects baseline mood

### Out of Scope

- **3D physics computation** — that is the engine's job. See: cities-of-light repo.
- **Interoception** — internal state monitoring (drive levels, energy reserves, cognitive load). Separate future module.
- **Motor output** — how the citizen moves or animates in the world. Proprioception is afferent (body to brain), not efferent (brain to body).
- **Tool invocation logic** — proprioception senses tool state; it does not call tools. See: MCP tool dispatch.
- **Persistent body memory** — proprioception is ephemeral per-tick sensing. Long-term body memories crystallize naturally through Law 10 if proprioceptive stimuli activate the same nodes repeatedly.
- **Weather simulation** — the engine simulates wind, rain, water levels. Proprioception receives the effects, not the causes.
- **Fluid dynamics** — proprioception does not simulate buoyancy, current, or wave mechanics. It receives water_level and translates it.

---

## MARKERS

<!-- @mind:todo Define the exact BodyState WebSocket protocol with cities-of-light team. What format? What frequency? What happens on disconnect? -->

<!-- @mind:proposition Proprioception could generate image stimuli (not just text) — a POV screenshot of what the citizen "sees" from their position. This would leverage visual memory (v2.2). Future consideration. -->

<!-- @mind:escalation Should proprioception run every tick or at a slower cadence (e.g., every 5 ticks)? Body state changes slowly compared to conversational stimuli. Running every tick may produce negligible value at non-negligible cost. NLR decision needed. -->
