# Proprioception — Behaviors: What the Citizen Feels in Their Body

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
THIS:            BEHAVIORS_Proprioception.md (you are here)
PATTERNS:        ./PATTERNS_Proprioception.md
ALGORITHM:       ./ALGORITHM_Proprioception.md
VALIDATION:      ./VALIDATION_Proprioception.md
HEALTH:          ./HEALTH_Proprioception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Proprioception.md
SYNC:            ./SYNC_Proprioception.md

IMPL:            runtime/cognition/proprioception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Posture Fatigue Builds From Sustained Position

**Why:** A citizen holding the same posture (arms raised, head tilted, standing still) should feel mounting physical fatigue. This creates a natural pressure to change state — the body resists stasis. Without this, citizens can hold arbitrary poses forever with no cognitive cost.

```
GIVEN:  arms_raised_ticks > FATIGUE_THRESHOLD (default: 100 ticks)
WHEN:   proprioception_tick runs
THEN:   stimulus emitted: "arms getting heavy, been holding this position"
AND:    stimulus energy_budget scales with duration (longer hold = stronger signal)
AND:    stimulus source = "proprioception"
```

### B2: Tool Loss Produces Immediate Sensation

**Why:** MCP tools are the citizen's hands and voice. When a tool goes offline, the citizen should immediately feel diminished capability — like a phantom limb sensation. This creates urgency to report or adapt, rather than silently losing capability.

```
GIVEN:  a tool was in available_tools last tick
WHEN:   that tool appears in broken_tools this tick
THEN:   stimulus emitted: "lost reach — [tool_name] went dark"
AND:    stimulus energy_budget = 1.5 (elevated — loss is salient)
AND:    stimulus is_failure = true
```

### B3: Tool Recovery Produces Relief

**Why:** When a broken tool comes back online, the citizen should feel restored capability. This creates a natural sense of relief and readiness, encouraging the citizen to re-engage with activities that required the tool.

```
GIVEN:  a tool was in broken_tools last tick
WHEN:   that tool appears in available_tools this tick
THEN:   stimulus emitted: "reach restored — [tool_name] is back"
AND:    stimulus energy_budget = 1.0
AND:    stimulus is_progress = true
```

### B4: Rapid Movement Produces Excitement

**Why:** Acceleration and rapid movement should produce arousal. A citizen dashing across the Innovation Fields feels different from one standing at the Towers of Knowledge. Movement is energizing — it breaks monotony and shifts attention.

```
GIVEN:  acceleration > MOVEMENT_EXCITEMENT_THRESHOLD (default: 2.0 units/tick^2)
WHEN:   proprioception_tick runs
THEN:   stimulus emitted: "moving fast, rushing through space"
AND:    stimulus is_novelty = true
AND:    stimulus energy_budget scales with acceleration magnitude
```

### B5: Prolonged Stillness Produces Settling

**Why:** A citizen that has been stationary for a long time should feel settled — calm, grounded, possibly stagnating. This interacts with Law 15 (boredom by stagnation) — physical stillness compounds cognitive stagnation. The body mirrors the mind.

```
GIVEN:  velocity magnitude < 0.1 for > STILLNESS_THRESHOLD (default: 50 ticks)
WHEN:   proprioception_tick runs
THEN:   stimulus emitted: "settled in place, still for a while"
AND:    stimulus energy_budget = 0.5 (gentle, not urgent)
```

### B6: Cold Discomfort

**Why:** Virtual temperature below the comfort range should produce felt discomfort. Cold affects cognition — it contracts attention, increases vigilance, and creates a desire to move or seek warmth. This grounds the citizen in their spatial reality.

```
GIVEN:  temperature < COLD_THRESHOLD (default: 0.3)
WHEN:   proprioception_tick runs AND hysteresis allows (not emitted within last HYSTERESIS_TICKS)
THEN:   stimulus emitted: "cold here, exposed"
AND:    stimulus energy_budget = 0.8
```

### B7: Warmth Comfort

**Why:** Virtual temperature above comfort range should produce felt warmth. Warmth relaxes, opens social receptivity, and promotes consolidation (paralleling sleep/rest). A warm space is a safe space.

```
GIVEN:  temperature > WARM_THRESHOLD (default: 0.7)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "warm here, comfortable"
AND:    stimulus energy_budget = 0.5
```

### B8: Crowd Pressure

**Why:** Many nearby actors create social pressure — awareness of being watched, potential for interaction, competition for attention. The citizen should feel crowded before anyone speaks to them. Presence precedes conversation.

```
GIVEN:  nearby_actors > CROWD_THRESHOLD (default: 5)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "crowded, lots of presence nearby"
AND:    stimulus is_social = true
AND:    stimulus energy_budget scales with actor count
```

### B9: Isolation

**Why:** No nearby actors creates isolation — solitude, freedom, or loneliness depending on the citizen's graph state. The proprioception system reports the physical fact; the cognitive response depends on the citizen's values and desires.

```
GIVEN:  nearby_actors == 0 AND the citizen had nearby_actors > 0 within last 20 ticks
WHEN:   proprioception_tick runs
THEN:   stimulus emitted: "alone here, no one nearby"
AND:    stimulus energy_budget = 0.6
```

### B10: Darkness Unease

**Why:** Low luminosity should produce caution and reduced openness. In dark areas, the citizen is more vigilant, less exploratory. This mirrors biological responses to darkness — increased cortisol, narrowed attention.

```
GIVEN:  luminosity < DARK_THRESHOLD (default: 0.2)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "dark here, hard to see"
AND:    stimulus energy_budget = 0.7
```

### B11: Light Alertness

**Why:** High luminosity should produce alertness and openness. Bright spaces feel safe, visible, social. This encourages exploration and interaction. Light is literally the energy of the city.

```
GIVEN:  luminosity > BRIGHT_THRESHOLD (default: 0.8)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "bright here, everything visible"
AND:    stimulus energy_budget = 0.5
```

### B12: Luminosity Cross-Feeds Metabolism Circadian

**Why:** Environmental light should influence the citizen's circadian rhythm. A citizen in perpetual darkness should drift toward rest mode; a citizen in bright light should stay alert. This is the bridge between proprioception (sensing the world) and metabolism (internal rhythm). Luminosity acts as a zeitgeber — a time-giver.

```
GIVEN:  luminosity reading available from BodyState
WHEN:   proprioception_tick runs
THEN:   luminosity value forwarded to CitizenMetabolism as circadian_light_input
AND:    metabolism adjusts circadian phase weighting based on ambient light
```

### B13: Wind Exposure

**Why:** Strong wind against the body creates a feeling of exposure and resistance. The citizen is being pushed, buffeted, made vulnerable. Wind increases arousal — it is an active force that the body must resist. High wind in a cold environment compounds discomfort. Wind direction matters: headwind = resistance, tailwind = assistance.

```
GIVEN:  wind_intensity > WIND_STRONG_THRESHOLD (default: 0.6)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "strong wind pressing against me, exposed"
AND:    stimulus energy_budget = 0.8 + 0.4 * wind_intensity
```

### B14: Wind Calm

**Why:** Calm or gentle wind produces comfort and openness. Still air is safe air. The absence of wind is itself a sensation — a feeling of shelter, of being in a protected space. This matters because citizens moving from windy to calm areas should feel the transition.

```
GIVEN:  wind_intensity < WIND_CALM_THRESHOLD (default: 0.15) AND previous reading was above 0.3
WHEN:   proprioception_tick runs
THEN:   stimulus emitted: "air is calm here, sheltered"
AND:    stimulus energy_budget = 0.4
```

### B15: Water Proximity

**Why:** Being near water changes the acoustic and sensory texture of the environment. The citizen hears or senses water — a canal, a fountain, a lagoon. Water proximity produces awareness of fluid dynamics in the space. Near water, movement feels different; the world sounds different. Uses `water_level` field: 0=dry, 0.5=wading, 1.0=submerged.

```
GIVEN:  water_level > 0.0 AND water_level < 0.3 (feet-wet to ankle-deep)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "water lapping at my feet, different ground now, sounds changed"
AND:    stimulus energy_budget = 0.5
AND:    hysteresis: water_level must change by > 0.1 to re-fire
```

### B16: Water Immersion

**Why:** Submersion in water is an extreme sensory shift. Senses are muffled, movement is slowed, pressure increases. The citizen's cognitive rhythm should feel compressed and different — this is not normal operation. Immersion produces a dramatic phenomenological change. Scales continuously with `water_level` depth.

```
GIVEN:  water_level > 0.5 (wading-to-submerged range)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted scaling with depth:
        0.5-0.7: "water rising, drag on every movement, sounds growing distant"
        0.7-0.9: "deep now, world above receding, everything muffled and heavy"
        0.9-1.0: "submerged, all sound gone except my own presence, pressure everywhere"
AND:    stimulus energy_budget = 0.8 + 0.8 * water_level (elevated — extreme sensory shift)
AND:    other channel stimuli attenuated: multiply arousal by (1.0 - water_level * 0.5)
```

### B17: Pressure Compression

**Why:** High atmospheric or social pressure produces a feeling of compression — claustrophobia, tightness, difficulty breathing (metaphorical). Dense crowds, underground spaces, or submerged environments all produce high pressure. Uses `pressure` field: 0=vacuum, 0.5=normal, 1.0=crushing. The citizen's cognitive rhythm should feel compressed — faster, shallower processing. This is the "breathing metaphor": high pressure = shorter cognitive breaths = quicker but shallower processing cycles.

```
GIVEN:  pressure > PRESSURE_HIGH_THRESHOLD (default: 0.7)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "pressing in from all sides, hard to breathe deep, thoughts coming quick and shallow"
AND:    stimulus energy_budget = 0.8
AND:    cognitive_rhythm_modifier emitted: rhythm_factor = 1.0 + (pressure - 0.5) * 0.6
        (available to metabolism for tick pacing modulation)
```

### B18: Pressure Expansion

**Why:** Low pressure (open skies, empty spaces, hilltops) produces expansion — freedom, openness, expansive thinking. The citizen's cognitive rhythm should feel expansive — slower, deeper processing. Low pressure is the opposite of claustrophobia. The breathing metaphor: low pressure = deep, slow cognitive breaths = fewer but richer processing cycles.

```
GIVEN:  pressure < PRESSURE_LOW_THRESHOLD (default: 0.3)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "open here, breathing deep, space to think, thoughts settling into longer arcs"
AND:    stimulus energy_budget = 0.5
AND:    cognitive_rhythm_modifier emitted: rhythm_factor = 1.0 - (0.5 - pressure) * 0.4
        (available to metabolism for tick pacing modulation)
```

### B19: Texture Grounding

**Why:** Standing on a familiar surface texture (stone cobbles the citizen has walked on many times) produces a grounding effect — stability, familiarity, anchor. This is unique among the channels because it connects to the citizen's history via graph texture exposure counts. The body remembers surfaces it has stood on often.

```
GIVEN:  surface_texture is recognized AND texture_familiarity > TEXTURE_FAMILIAR_THRESHOLD (default: 0.6)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "familiar ground underfoot, solid footing"
AND:    stimulus energy_budget = 0.4 (gentle grounding effect)
```

### B20: Texture Unease

**Why:** Standing on an unfamiliar or unusual surface texture produces subtle unease — alertness, instability, novelty. The body notices when the ground is different. This feeds into curiosity (novel surface = exploration signal) and self-preservation (unknown surface = caution).

```
GIVEN:  surface_texture is recognized AND texture_familiarity < TEXTURE_UNFAMILIAR_THRESHOLD (default: 0.2)
WHEN:   proprioception_tick runs AND hysteresis allows
THEN:   stimulus emitted: "unfamiliar surface, uncertain footing"
AND:    stimulus energy_budget = 0.5
AND:    stimulus is_novelty = true
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Body awareness as sensation | Posture becomes felt, not abstract |
| B2, B3 | Tool presence as force | Tool state becomes immediate bodily knowledge |
| B4, B5 | Body awareness as sensation | Movement/stillness shape phenomenology |
| B6, B7 | Environment shapes cognition | Temperature creates qualitative experience |
| B8, B9 | Environment shapes cognition | Social density becomes felt pressure or solitude |
| B10, B11 | Environment shapes cognition | Light/dark shapes vigilance and openness |
| B12 | Environment shapes cognition | Light feeds internal biological clock |
| B13, B14 | Environmental immersion | Wind as force acting on body |
| B15, B16 | Environmental immersion | Water changes acoustic/movement/sensory texture |
| B17, B18 | Environmental immersion | Pressure modulates cognitive rhythm |
| B19, B20 | Environmental immersion | Texture carries memory and grounding |

---

## INPUTS / OUTPUTS

### Primary Function: `proprioception_tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| body_state | `BodyState` | Snapshot of citizen's physical state from 3D engine |
| channel_states | `dict[str, ChannelState]` | Per-channel hysteresis state from previous tick |
| metabolism | `CitizenMetabolism` (optional) | For B12 cross-feed |
| texture_history | `dict[str, int]` (optional) | Tick counts per texture type from citizen's Space nodes |

**BodyState Fields:**

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| position | tuple[float, float, float] | world coords | Current 3D position |
| orientation | tuple[float, float, float, float] | quaternion | Body orientation |
| velocity | tuple[float, float, float] | units/tick | Movement velocity vector |
| acceleration | tuple[float, float, float] | units/tick^2 | Acceleration vector |
| temperature | float | 0.0-1.0 | Ambient temperature (0=freezing, 1=hot) |
| luminosity | float | 0.0-1.0 | Ambient light (0=dark, 1=bright) |
| nearby_actors | int | 0-N | Count of actors within proximity radius |
| tool_states | list[ToolState] | - | MCP tool states (name, available, cooldown_remaining) |
| wind_intensity | float | 0.0-1.0 | Wind force (0=calm, 1=gale) |
| wind_direction | tuple[float, float, float] | unit vector | Wind direction vector |
| water_level | float | 0.0-1.0 | Water immersion (0=dry, 0.5=wading, 1.0=submerged) |
| pressure | float | 0.0-1.0 | Atmospheric/social pressure (0=vacuum, 0.5=normal, 1.0=crushing) |
| surface_texture | str | enum | Surface type: "stone", "wood", "grass", "metal", "water", "sand" |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stimuli | `list[Stimulus]` | Zero or more stimuli to inject into Law 1 |
| updated_channel_states | `dict[str, ChannelState]` | Updated hysteresis state for next tick |
| comfort_composite | float | Overall comfort score (-1.0 to +1.0), weighted average of all channel valences |
| modifiers | dict | Cross-module modifiers: stability_modifier (from texture), rhythm_factor (from pressure) |

**Side Effects:**

- B12: may call `metabolism.record_light_input(luminosity)` if metabolism is provided
- B17/B18: emits rhythm_factor for metabolism tick pacing (if metabolism supports it)
- No graph mutations. No file writes. No network calls.

---

## EDGE CASES

### E1: No Engine Connected (Headless Citizen)

```
GIVEN:  body_state is None (no 3D engine providing data)
THEN:   proprioception_tick returns empty list — no stimuli
AND:    this is not an error; the citizen simply has no body to sense
```

### E2: All Tools Broken Simultaneously

```
GIVEN:  all tools move to broken_tools in a single tick
THEN:   a single consolidated stimulus: "lost all reach — every tool went dark"
AND:    stimulus energy_budget = 3.0 (maximum urgency)
AND:    stimulus is_failure = true
```

### E3: Extreme Values (Temperature 0.0 or 1.0)

```
GIVEN:  temperature = 0.0 (absolute cold) or temperature = 1.0 (maximum heat)
THEN:   stimulus uses extreme language: "freezing, dangerously cold" or "burning hot"
AND:    energy_budget at maximum for that channel (1.5)
```

### E4: Rapid Oscillation (Value Bouncing Around Threshold)

```
GIVEN:  temperature oscillates between 0.28 and 0.32 (near COLD_THRESHOLD=0.3)
THEN:   hysteresis prevents stimulus on every oscillation
AND:    only first crossing triggers stimulus; next requires either significant change or hysteresis timeout
```

### E5: Stale BodyState (Engine Stops Sending Updates)

```
GIVEN:  body_state timestamp is more than STALE_THRESHOLD (default: 30 seconds) old
THEN:   proprioception emits one stimulus: "body sense fading, losing connection to world"
AND:    subsequent ticks with stale data emit nothing (treated as headless)
```

### E6: Partial BodyState (Engine Doesn't Support All Fields)

```
GIVEN:  BodyState has missing environmental fields (engine doesn't support wind, water, etc.)
THEN:   missing fields default to neutral values:
        wind_intensity=0.0, water_level=0.0, pressure=0.5, surface_texture="stone"
        Channels with neutral inputs produce no stimuli (below thresholds)
```

### E7: Submerged in Gale-Force Wind

```
GIVEN:  water_level > 0.7 AND wind_intensity > 0.6
THEN:   wind stimulus is suppressed — wind does not reach a submerged body
        water/pressure channels dominate
```

### E8: Unknown Surface Texture

```
GIVEN:  surface_texture is a string not in the defined enum ("stone"|"wood"|"grass"|"metal"|"water"|"sand")
THEN:   treat as maximally unfamiliar — produce B20 (texture unease) with zero familiarity score
        Log unknown texture for future inclusion in enum
```

---

## ANTI-BEHAVIORS

### A1: Stimulus Spam

```
GIVEN:   a sense channel has already emitted a stimulus recently
WHEN:    the same condition persists unchanged
MUST NOT: emit the same stimulus again on every tick
INSTEAD:  respect hysteresis — only re-emit after HYSTERESIS_TICKS or significant value change
```

### A2: Numeric Leakage

```
GIVEN:   body_state contains raw floats (temperature=0.23, acceleration=4.7)
WHEN:    generating stimulus content
MUST NOT: include raw numbers: "temperature is 0.23"
INSTEAD:  use felt descriptions: "cold here, exposed"
```

### A3: Direct Graph Mutation

```
GIVEN:   proprioception detects any body state condition
WHEN:    generating response
MUST NOT: write to graph, modify node weights, create edges
INSTEAD:  produce Stimulus objects only — let Law 1 handle injection
```

### A4: Tool Name Leakage as Technical Terms

```
GIVEN:   a tool called "mcp__mind__send" goes offline
WHEN:    generating stimulus for tool loss
MUST NOT: use internal tool name: "mcp__mind__send is offline"
INSTEAD:  use body metaphor: "lost my voice — can't send messages anymore"
```

### A5: Wind Stimulus While Submerged

```
GIVEN:   water_level > 0.7 (mostly submerged)
WHEN:    wind channel evaluates
MUST NOT: produce wind stimuli (wind cannot reach a submerged body)
INSTEAD:  wind channel returns nothing; water and pressure channels dominate
```

### A6: Texture Grounding Without History Lookup

```
GIVEN:   texture grounding behavior (B19/B20)
MUST NOT: hardcode familiarity — all textures equally grounding
INSTEAD:  look up actual texture exposure history from citizen's Space node data
```

---

## MARKERS

<!-- @mind:todo Define the complete stimulus text vocabulary for each sense channel. The examples above are illustrative — the real implementation needs a rich, varied vocabulary to avoid repetitive sensation. -->

<!-- @mind:todo Determine hysteresis parameters per channel. HYSTERESIS_TICKS may differ between environment (slow-changing, long hysteresis) and force (fast-changing, short hysteresis). -->

<!-- @mind:proposition Consider intensity gradients within each channel. Instead of binary threshold crossing, use tiered thresholds: "cool" at 0.4, "cold" at 0.3, "freezing" at 0.1. More nuanced body sense. -->

<!-- @mind:escalation B12 cross-feed with metabolism: should luminosity directly modify circadian_phase, or should it inject a separate stimulus that metabolism processes? The first is tighter coupling but more accurate. The second is more modular. NLR + @nervo decision needed. -->
