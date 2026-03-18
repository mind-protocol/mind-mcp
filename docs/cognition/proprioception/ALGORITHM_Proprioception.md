# Proprioception — Algorithm: BodyState to Stimulus Translation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
BEHAVIORS:       ./BEHAVIORS_Proprioception.md
PATTERNS:        ./PATTERNS_Proprioception.md
THIS:            ALGORITHM_Proprioception.md (you are here)
VALIDATION:      ./VALIDATION_Proprioception.md
HEALTH:          ./HEALTH_Proprioception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Proprioception.md
SYNC:            ./SYNC_Proprioception.md

IMPL:            runtime/cognition/proprioception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The proprioception algorithm translates a `BodyState` snapshot into zero or more `Stimulus` objects per tick. It runs eight sense channels in sequence — four somatic (limb, force, accelerometer, thermoception) and four environmental (vent, eau, pression, texture) — each producing zero or more stimuli. Channels maintain hysteresis state to prevent stimulus spam. The output is a flat list of stimuli that enters the normal stimulus pipeline (Law 1 injection).

The algorithm is pure computation with one exception: the texture channel requires a graph lookup for familiarity scoring (how often has this citizen stood on this texture type). All other channels require no graph access, no network calls, no LLM. Given a `BodyState` and channel states, the algorithm produces stimuli deterministically.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Body awareness as sensation | B1, B4, B5 | Translates position/movement into felt stimuli |
| Tool presence as force | B2, B3 | Translates tool state changes into immediate sensation |
| Environment shapes cognition | B6-B12 | Translates thermoception/luminosity/crowd data into cognitive input |
| Environmental immersion | B13-B20 | Wind, water, pressure, texture as felt forces on body |
| Engine reads, mind translates | All | Clean translation boundary — no 3D physics in mind-mcp |

---

## DATA STRUCTURES

### BodyState

The engine provides this per citizen per tick. All fields have documented ranges.

```python
@dataclass
class BodyState:
    # === Position & Movement ===
    position: tuple[float, float, float]       # (x, y, z) world coordinates
    rotation: tuple[float, float, float, float] # quaternion (w, x, y, z)
    velocity: tuple[float, float, float]        # units/tick
    acceleration: float                         # magnitude, units/tick^2

    # === Limbs ===
    left_arm_angle: float    # 0.0 = resting at side, pi = fully raised
    right_arm_angle: float   # same range
    head_pitch: float        # -pi/2 = looking down, pi/2 = looking up
    head_yaw: float          # -pi = looking full left, pi = looking full right

    # === Force (MCP Tool State) ===
    available_tools: list[str]    # currently working tool names
    broken_tools: list[str]       # currently offline tool names
    tool_cooldowns: dict[str, int] # tool_name -> ticks remaining

    # === Thermoception (somatic channel 4) ===
    temperature: float        # 0.0 = freezing, 1.0 = maximum warmth
    luminosity: float         # 0.0 = pitch dark, 1.0 = maximum brightness
    nearby_actors: int        # count of actors within sensing radius
    current_space_id: str     # ID of the space node the citizen occupies

    # === Vent / Wind (environmental channel 5) ===
    wind_intensity: float     # 0.0 = calm, 1.0 = gale
    wind_direction: tuple[float, float, float]  # normalized vector (relative to citizen facing)

    # === Eau / Water (environmental channel 6) ===
    water_level: float        # 0.0 = dry, 0.5 = wading, 1.0 = fully submerged

    # === Pression / Pressure (environmental channel 7) ===
    pressure: float           # 0.0 = vacuum, 0.5 = normal, 1.0 = crushing

    # === Texture (environmental channel 8) ===
    surface_texture: str      # "stone" | "wood" | "grass" | "metal" | "sand" | "water"

    # === Metadata ===
    timestamp: float          # epoch seconds when this state was captured
```

### ChannelState (hysteresis tracker per channel)

```python
@dataclass
class ChannelState:
    last_emission_tick: int = 0          # tick when this channel last emitted
    last_emitted_value: float = 0.0      # the value that triggered last emission
    last_emitted_category: str = ""      # the category of last emission (e.g. "cold", "warm")
    ticks_in_condition: int = 0          # how many ticks the current condition has persisted
    previous_tool_set: set[str] = field(default_factory=set)  # for force channel: diff detection
```

### ProprioceptionConfig (tunable thresholds)

```python
@dataclass
class ProprioceptionConfig:
    # Limb channel
    fatigue_threshold_ticks: int = 100
    fatigue_energy_base: float = 0.6
    fatigue_energy_scale: float = 0.005   # per tick over threshold

    # Force channel
    tool_loss_energy: float = 1.5
    tool_recovery_energy: float = 1.0
    all_tools_lost_energy: float = 3.0

    # Accelerometer channel
    movement_excitement_threshold: float = 2.0
    stillness_threshold_ticks: int = 50
    movement_energy_base: float = 0.8
    stillness_energy: float = 0.5

    # Thermoception channel (somatic)
    cold_threshold: float = 0.3
    warm_threshold: float = 0.7
    dark_threshold: float = 0.2
    bright_threshold: float = 0.8
    crowd_threshold: int = 5
    isolation_grace_ticks: int = 20      # ticks after losing all nearby actors before isolation fires
    environment_energy_base: float = 0.7    # used by thermoception sub-channels

    # Vent channel (environmental)
    wind_strong_threshold: float = 0.6
    wind_calm_threshold: float = 0.15
    wind_energy_base: float = 0.8

    # Eau channel (environmental) — uses water_level: 0=dry, 0.5=wading, 1.0=submerged
    water_wading_threshold: float = 0.5      # above this: immersion effects begin
    water_proximity_threshold: float = 0.05  # above 0: feet-wet / near-water effects
    water_immersion_attenuation: float = 0.5 # multiplier for muffling other channels

    # Pression channel (environmental) — uses pressure: 0=vacuum, 0.5=normal, 1.0=crushing
    pressure_high_threshold: float = 0.7
    pressure_low_threshold: float = 0.3
    pressure_energy_base: float = 0.8

    # Texture channel (environmental)
    texture_familiar_threshold: float = 0.6
    texture_unfamiliar_threshold: float = 0.2
    texture_energy_base: float = 0.4

    # Hysteresis
    hysteresis_ticks: int = 15           # minimum ticks between re-emission on same channel
    value_change_threshold: float = 0.15 # minimum value change to bypass hysteresis timer

    # Staleness
    stale_threshold_seconds: float = 30.0
```

---

## ALGORITHM: `proprioception_tick()`

### Step 1: Validate BodyState

Check for null or stale body state. If no engine is connected, return empty. If state is stale (timestamp too old), emit one "fading" stimulus and mark as disconnected.

```
IF body_state is None:
    RETURN []

IF (now - body_state.timestamp) > config.stale_threshold_seconds:
    IF not already_marked_stale:
        EMIT stimulus("body sense fading, losing connection to world", energy=0.5)
        mark_stale()
    RETURN stimuli
```

### Step 2: Run Limb Position Channel

Check for sustained posture conditions. Track how long arms have been raised above a threshold angle.

```
arm_raised = max(body_state.left_arm_angle, body_state.right_arm_angle) > (pi * 0.6)

IF arm_raised:
    channel.ticks_in_condition += 1
ELSE:
    channel.ticks_in_condition = 0

IF channel.ticks_in_condition > config.fatigue_threshold_ticks:
    IF hysteresis_allows(channel):
        energy = config.fatigue_energy_base + config.fatigue_energy_scale * (ticks_in_condition - threshold)
        energy = min(energy, 2.0)  # cap
        EMIT stimulus("arms getting heavy, been holding this position", energy=energy)
        update_hysteresis(channel)
```

### Step 3: Run Force Channel (Tool State)

Diff the current tool sets against previous tick. Detect losses and recoveries.

```
current_available = set(body_state.available_tools)
current_broken = set(body_state.broken_tools)
previous_available = channel.previous_tool_set

newly_broken = previous_available - current_available
newly_recovered = current_available - previous_available  # tools that were missing and came back

IF len(newly_broken) > 0:
    IF newly_broken == previous_available AND len(previous_available) > 1:
        # All tools lost at once
        EMIT stimulus("lost all reach — every tool went dark", energy=config.all_tools_lost_energy, is_failure=true)
    ELSE:
        FOR tool in newly_broken:
            human_name = tool_to_body_metaphor(tool)
            EMIT stimulus(f"lost reach — {human_name} went dark", energy=config.tool_loss_energy, is_failure=true)

IF len(newly_recovered) > 0:
    FOR tool in newly_recovered:
        human_name = tool_to_body_metaphor(tool)
        EMIT stimulus(f"reach restored — {human_name} is back", energy=config.tool_recovery_energy, is_progress=true)

# Check cooldowns: tools about to come back
FOR tool, ticks_left in body_state.tool_cooldowns.items():
    IF ticks_left == 1:
        human_name = tool_to_body_metaphor(tool)
        EMIT stimulus(f"{human_name} almost ready again", energy=0.3)

channel.previous_tool_set = current_available
```

### Step 4: Run Accelerometer Channel

Detect movement intensity and prolonged stillness.

```
speed = magnitude(body_state.velocity)

IF body_state.acceleration > config.movement_excitement_threshold:
    IF hysteresis_allows(channel):
        energy = config.movement_energy_base + 0.1 * body_state.acceleration
        energy = min(energy, 2.0)
        EMIT stimulus("moving fast, rushing through space", energy=energy, is_novelty=true)
        update_hysteresis(channel)
        channel.ticks_in_condition = 0  # reset stillness counter

ELIF speed < 0.1:
    channel.ticks_in_condition += 1
    IF channel.ticks_in_condition > config.stillness_threshold_ticks:
        IF hysteresis_allows(channel):
            EMIT stimulus("settled in place, still for a while", energy=config.stillness_energy)
            update_hysteresis(channel)
ELSE:
    channel.ticks_in_condition = 0  # moving but not fast
```

### Step 5: Run Environment Channel

Check temperature, luminosity, pressure, and nearby actors. Each sub-channel has independent hysteresis.

```
# --- Temperature ---
IF body_state.temperature < config.cold_threshold:
    IF hysteresis_allows(channel, "temperature"):
        intensity = 1.0 - (body_state.temperature / config.cold_threshold)  # 0..1
        text = select_cold_text(intensity)  # "cool breeze" / "cold here" / "freezing"
        EMIT stimulus(text, energy=config.environment_energy_base * (0.5 + intensity))
        update_hysteresis(channel, "temperature", body_state.temperature)

ELIF body_state.temperature > config.warm_threshold:
    IF hysteresis_allows(channel, "temperature"):
        intensity = (body_state.temperature - config.warm_threshold) / (1.0 - config.warm_threshold)
        text = select_warm_text(intensity)
        EMIT stimulus(text, energy=0.5 + 0.3 * intensity)
        update_hysteresis(channel, "temperature", body_state.temperature)

# --- Luminosity ---
IF body_state.luminosity < config.dark_threshold:
    IF hysteresis_allows(channel, "luminosity"):
        EMIT stimulus("dark here, hard to see", energy=0.7)
        update_hysteresis(channel, "luminosity", body_state.luminosity)

ELIF body_state.luminosity > config.bright_threshold:
    IF hysteresis_allows(channel, "luminosity"):
        EMIT stimulus("bright here, everything visible", energy=0.5)
        update_hysteresis(channel, "luminosity", body_state.luminosity)

# --- Crowd / Isolation ---
IF body_state.nearby_actors > config.crowd_threshold:
    IF hysteresis_allows(channel, "crowd"):
        energy = 0.5 + 0.1 * min(body_state.nearby_actors, 20)
        EMIT stimulus("crowded, lots of presence nearby", energy=energy, is_social=true)
        update_hysteresis(channel, "crowd", float(body_state.nearby_actors))

ELIF body_state.nearby_actors == 0:
    channel.isolation_ticks += 1
    IF channel.isolation_ticks > config.isolation_grace_ticks:
        IF hysteresis_allows(channel, "isolation"):
            EMIT stimulus("alone here, no one nearby", energy=0.6)
            update_hysteresis(channel, "isolation", 0.0)
ELSE:
    channel.isolation_ticks = 0

# --- Luminosity -> Metabolism cross-feed (B12) ---
IF metabolism is not None:
    metabolism.record_light_input(body_state.luminosity)
```

### Step 6: Run Vent Channel (Wind)

Detect wind intensity changes and transitions between calm and exposed. Uses `wind_direction` vector to determine felt direction relative to citizen facing. Suppressed when `water_level > 0.7` (wind cannot reach a submerged body).

```
# Wind is suppressed underwater
IF body_state.water_level > 0.7:
    SKIP this channel entirely

IF body_state.wind_intensity > config.wind_strong_threshold:
    IF hysteresis_allows(channel, "wind"):
        energy = config.wind_energy_base + 0.4 * body_state.wind_intensity
        direction_text = select_wind_direction_text(body_state.wind_direction)
        text = select_wind_text(body_state.wind_intensity, direction_text)
        # e.g., "wind hammering from the north, body leaning into it, each step a fight"
        EMIT stimulus(text, energy=energy)
        update_hysteresis(channel, "wind", body_state.wind_intensity)

ELIF body_state.wind_intensity < config.wind_calm_threshold:
    IF channel.last_emitted_category == "wind_strong":  # transition from windy to calm
        EMIT stimulus("air is calm here, sheltered, comfortable", energy=0.4)
        update_hysteresis(channel, "wind", body_state.wind_intensity)
```

### Step 7: Run Eau Channel (Water)

Detect water level. Uses a single `water_level` field (0=dry, 0.5=wading, 1.0=submerged). Immersion is an extreme sensory event that attenuates other channels.

```
IF body_state.water_level > 0.5:
    # Immersion range: wading to submerged
    IF hysteresis_allows(channel, "water"):
        depth = body_state.water_level
        IF depth > 0.9:
            text = "submerged, all sound gone except my own presence, pressure everywhere"
        ELIF depth > 0.7:
            text = "deep now, world above receding, everything muffled and heavy"
        ELSE:
            text = "water rising, drag on every movement, sounds growing distant"
        energy = 0.8 + 0.8 * depth
        EMIT stimulus(text, energy=energy)
        update_hysteresis(channel, "water", depth)

ELIF body_state.water_level > 0.0:
    # Near-water / feet-wet range
    IF hysteresis_allows(channel, "water"):
        EMIT stimulus("water lapping at my feet, different ground now, sounds changed", energy=0.5)
        update_hysteresis(channel, "water", body_state.water_level)
```

### Step 8: Run Pression Channel (Pressure)

Detect atmospheric/social pressure extremes. Uses `pressure` field (0=vacuum, 0.5=normal, 1.0=crushing). High pressure = compression, faster/shallower cognitive rhythm. Low pressure = expansion, slower/deeper cognitive rhythm. Emits a `rhythm_factor` modifier for metabolism.

```
IF body_state.pressure > config.pressure_high_threshold:
    IF hysteresis_allows(channel, "pressure"):
        EMIT stimulus("pressing in from all sides, hard to breathe deep, thoughts coming quick and shallow",
                      energy=config.pressure_energy_base)
        # Cognitive rhythm modifier: higher pressure = faster but shallower processing
        rhythm_factor = 1.0 + (body_state.pressure - 0.5) * 0.6
        EMIT modifier("rhythm_factor", rhythm_factor)
        update_hysteresis(channel, "pressure", body_state.pressure)

ELIF body_state.pressure < config.pressure_low_threshold:
    IF hysteresis_allows(channel, "pressure"):
        EMIT stimulus("open here, breathing deep, space to think, thoughts settling into longer arcs",
                      energy=0.5)
        # Cognitive rhythm modifier: lower pressure = slower but deeper processing
        rhythm_factor = 1.0 - (0.5 - body_state.pressure) * 0.4
        EMIT modifier("rhythm_factor", rhythm_factor)
        update_hysteresis(channel, "pressure", body_state.pressure)
```

### Step 9: Run Texture Channel (Surface)

Detect surface texture and compute familiarity from graph history. This is the only channel that reads from the graph.

```
IF body_state.surface_texture != "":
    # Look up texture familiarity from graph
    # texture_familiarity = count of Space nodes the citizen has visited with this texture / total visits
    familiarity = lookup_texture_familiarity(citizen_id, body_state.surface_texture)

    IF familiarity > config.texture_familiar_threshold:
        IF hysteresis_allows(channel, "texture"):
            EMIT stimulus("familiar ground underfoot, solid footing", energy=config.texture_energy_base)
            update_hysteresis(channel, "texture", familiarity)

    ELIF familiarity < config.texture_unfamiliar_threshold:
        IF hysteresis_allows(channel, "texture"):
            EMIT stimulus("unfamiliar surface, uncertain footing", energy=0.5, is_novelty=true)
            update_hysteresis(channel, "texture", familiarity)
```

### Step 10: Apply Immersion Attenuation

If the citizen is partially or fully submerged, non-water stimuli are muffled.

```
IF body_state.water_level > 0.3:
    attenuation = 1.0 - body_state.water_level * 0.5
    FOR each stimulus NOT from eau_channel:
        stimulus.energy_budget *= attenuation
        # Optionally prefix with muffling qualifier at high water levels
        IF body_state.water_level > 0.7:
            stimulus.content = f"through the water, distantly: {stimulus.content}"
```

### Step 11: Compute Comfort Composite

Weighted average of all channel valences to produce an overall body-comfort score.

```
somatic_valences = [valence for stimulus in somatic_stimuli]       # weight 1.0 each
environmental_valences = [valence for stimulus in env_stimuli]     # weight 0.8 each

IF len(somatic_valences) + len(environmental_valences) > 0:
    comfort_composite = weighted_mean(somatic_valences, 1.0, environmental_valences, 0.8)
ELSE:
    comfort_composite = 0.0  # neutral if no stimuli

# comfort_composite range: -1.0 (extreme discomfort) to +1.0 (extreme comfort)
```

### Step 12: Collect and Return

Gather all stimuli from all eight channels. Set common fields. Package modifiers.

```
FOR each stimulus in collected:
    stimulus.source = "proprioception"
    stimulus.timestamp = body_state.timestamp

modifiers = {}
IF texture_stability_modifier != 0:
    modifiers["stability_modifier"] = texture_stability_modifier
IF rhythm_factor is set:
    modifiers["rhythm_factor"] = rhythm_factor

RETURN (stimuli, updated_channel_states, comfort_composite, modifiers)
```

---

## KEY DECISIONS

### D1: Hysteresis Check

```
IF (current_tick - channel.last_emission_tick) >= config.hysteresis_ticks:
    ALLOW emission (timer expired)
ELIF abs(current_value - channel.last_emitted_value) > config.value_change_threshold:
    ALLOW emission (significant change overrides timer)
ELSE:
    SUPPRESS emission
```

### D2: Tool Name to Body Metaphor Translation

```
MAPPING:
    "mcp__mind__send"     -> "voice" (ability to send messages)
    "mcp__mind__call"     -> "hands" (ability to invoke actions)
    "mcp__mind__read"     -> "eyes" (ability to read/perceive)
    "mcp__mind__media"    -> "vision" (ability to see/create images)
    "mcp__mind__place"    -> "spatial sense" (ability to navigate)
    "mcp__mind__bond"     -> "social sense" (ability to form connections)
    "mcp__mind__think"    -> "inner voice" (ability to reflect)
    "mcp__mind__alarm"    -> "time sense" (ability to schedule)
    default               -> "a limb" (generic tool reference)
```

### D3: Temperature Text Selection

```
IF intensity < 0.3:
    "cool breeze, slight chill"
ELIF intensity < 0.7:
    "cold here, exposed"
ELSE:
    "freezing, dangerously cold"
```

### D4: When to Emit vs Suppress (Environment Sub-Channels)

Each environment sub-channel (temperature, luminosity, crowd, isolation) maintains independent hysteresis. A stimulus about temperature does not reset the luminosity timer. This allows the citizen to feel "cold AND dark" in the same tick but not "cold, cold, cold" in consecutive ticks.

---

## DATA FLOW

```
BodyState (from 3D engine)
    |
    v
validate_body_state()
    |
    v
SOMATIC CHANNELS:
+--> limb_channel.sense(body_state)          -> list[Stimulus]
+--> force_channel.sense(body_state)         -> list[Stimulus]
+--> accelerometer_channel.sense(body_state) -> list[Stimulus]
+--> thermoception_channel.sense(body_state) -> list[Stimulus]
    |
ENVIRONMENTAL CHANNELS:
+--> vent_channel.sense(body_state)          -> list[Stimulus]
+--> eau_channel.sense(body_state)           -> list[Stimulus]
+--> pression_channel.sense(body_state)      -> list[Stimulus]
+--> texture_channel.sense(body_state, graph)-> list[Stimulus]
    |
    v
collect + tag source="proprioception"
    |
    v
list[Stimulus] -> Stimulus Router -> Law 1
```

---

## COMPLEXITY

**Time:** O(T) where T = number of tools, plus one graph read for the texture channel. Seven of eight channels are O(1). The force channel iterates over tool sets for diffing (O(T), typically T < 20). The texture channel performs a single graph lookup (O(1) amortized with caching).

**Space:** O(T) for the previous_tool_set in ChannelState. All other state is fixed-size scalars. Texture familiarity cache is O(S) where S = number of distinct texture types the citizen has encountered (typically < 10).

**Bottlenecks:**
- The texture channel graph lookup could be slow if uncached. Mitigation: cache texture familiarity scores per citizen, refresh every N ticks (not every tick).
- All other channels are pure arithmetic and string construction. No embeddings, no LLM, no network calls.

---

## HELPER FUNCTIONS

### `hysteresis_allows(channel, sub_channel?)`

**Purpose:** Check whether a channel is allowed to emit based on hysteresis rules.

**Logic:** Returns true if enough ticks have passed since last emission OR if the current value has changed significantly from the last emitted value. See D1.

### `tool_to_body_metaphor(tool_name)`

**Purpose:** Translate internal MCP tool names into first-person body metaphors.

**Logic:** Dictionary lookup with a default fallback. See D2. Never exposes internal tool names to stimulus content.

### `select_cold_text(intensity)` / `select_warm_text(intensity)`

**Purpose:** Choose graduated sensation text based on how extreme the temperature is.

**Logic:** Intensity tiers map to different descriptions. See D3. Future: randomize within tier for variety.

### `magnitude(vector)`

**Purpose:** Compute the Euclidean magnitude of a 3D velocity vector.

**Logic:** `sqrt(x^2 + y^2 + z^2)`. Standard vector norm.

### `lookup_texture_familiarity(citizen_id, texture_type)`

**Purpose:** Query the citizen's graph for how familiar they are with a surface texture.

**Logic:** Count Space nodes the citizen has visited that have this texture attribute, divided by total Space visits. Returns float [0, 1]. Cached per citizen, refreshed every 50 ticks to avoid per-tick graph queries.

### `select_wind_text(intensity, direction_text)`

**Purpose:** Choose sensation text for wind based on intensity and direction string.

**Logic:** Intensity tiers: breeze (0.3-0.5) / wind (0.5-0.8) / gale (0.8+). Combined with direction text for full stimulus like "gale from the north, body braced against it."

### `select_wind_direction_text(wind_direction_vector)`

**Purpose:** Convert the wind_direction unit vector into a felt directional label.

**Logic:** Map the vector to a cardinal/intercardinal direction ("from the north", "sweeping from the east"). If citizen orientation is available, compute relative direction (headwind / tailwind / crosswind) and use resistance-appropriate language.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| 3D engine (cities-of-light) | WebSocket receive / shared state read | `BodyState` snapshot |
| `runtime/cognition/metabolism.py` | `metabolism.record_light_input(luminosity)` | Circadian cross-feed (B12) |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Returns `list[Stimulus]` | Injected into Law 1 via normal stimulus pipeline |
| FalkorDB graph (via adapter) | `lookup_texture_familiarity(citizen_id, texture)` | Texture familiarity score for grounding channel |

---

## MARKERS

<!-- @mind:todo Implement the full sensation text vocabulary. The algorithm currently uses fixed strings per condition — a richer system would have pools of variations per tier to avoid repetitive sensation. -->

<!-- @mind:todo Define the metabolism.record_light_input() interface. This method does not exist yet on CitizenMetabolism. It should adjust circadian weighting based on ambient light. -->

<!-- @mind:proposition Consider head_yaw and head_pitch as directional attention indicators. If the citizen is "looking at" another actor (head direction aligned with actor position), this could produce a "noticing someone" stimulus. Requires spatial reasoning beyond current scope — v2 consideration. -->

<!-- @mind:proposition The force channel could also sense tool cooldowns approaching zero and produce "almost ready" anticipatory stimuli. Partially implemented in Step 3 but needs design validation. -->
