# Proprioception — Implementation: Where the Code Lives

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
PATTERNS:        ./PATTERNS_Proprioception.md
BEHAVIORS:       ./BEHAVIORS_Proprioception.md
ALGORITHM:       ./ALGORITHM_Proprioception.md
VALIDATION:      ./VALIDATION_Proprioception.md
THIS:            IMPLEMENTATION_Proprioception.md (you are here)
HEALTH:          ./HEALTH_Proprioception.md
SYNC:            ./SYNC_Proprioception.md

IMPL:            runtime/cognition/proprioception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update SYNC. Run tests.

---

## FILE MAP

### Primary Implementation

| File | Purpose | Status |
|------|---------|--------|
| `runtime/cognition/proprioception.py` | Main module: BodyState, ProprioceptionModule, 8 sense channels, stimulus generation | TO BE CREATED |

### Integration Points

| File | What It Needs | Status |
|------|---------------|--------|
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Call `proprioception.tick(body_state)` pre-Law-1, inject returned stimuli | NEEDS MODIFICATION |
| `runtime/cognition/metabolism.py` | Accept `record_light_input(luminosity)` for circadian cross-feed (B12), accept `rhythm_factor` for pressure cross-feed (B17/B18) | NEEDS MODIFICATION |

### Tests

| File | Purpose | Status |
|------|---------|--------|
| `tests/test_proprioception.py` | Unit tests for all 8 channels, hysteresis, edge cases | TO BE CREATED |

---

## DATA STRUCTURES

All defined in `runtime/cognition/proprioception.py`:

### BodyState

```python
@dataclass
class BodyState:
    # Position & Movement
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
    acceleration: float = 0.0

    # Limbs
    left_arm_angle: float = 0.0
    right_arm_angle: float = 0.0
    head_pitch: float = 0.0
    head_yaw: float = 0.0

    # Force (MCP Tool State)
    available_tools: list[str] = field(default_factory=list)
    broken_tools: list[str] = field(default_factory=list)
    tool_cooldowns: dict[str, int] = field(default_factory=dict)

    # Thermoception (somatic)
    temperature: float = 0.5        # 0.0=freezing, 1.0=hot
    luminosity: float = 0.5         # 0.0=dark, 1.0=bright
    nearby_actors: int = 0
    current_space_id: str = ""

    # Environmental (extended)
    wind_intensity: float = 0.0             # 0=calm, 1=gale
    wind_direction: tuple[float, float, float] = (0.0, 0.0, 0.0)  # unit vector
    water_level: float = 0.0               # 0=dry, 0.5=wading, 1.0=submerged
    pressure: float = 0.5                  # 0=vacuum, 0.5=normal, 1.0=crushing
    surface_texture: str = "stone"         # "stone"|"wood"|"grass"|"metal"|"water"|"sand"

    # Metadata
    timestamp: float = 0.0
```

### ChannelState

```python
@dataclass
class ChannelState:
    last_emission_tick: int = 0
    last_emitted_value: float = 0.0
    last_emitted_category: str = ""
    ticks_in_condition: int = 0
    previous_tool_set: set[str] = field(default_factory=set)
```

### ProprioceptionConfig

See ALGORITHM_Proprioception.md for the full config dataclass with all thresholds.

---

## MODULE STRUCTURE

```python
# runtime/cognition/proprioception.py

class ProprioceptionModule:
    """Eight-channel body sense translator: BodyState -> Stimulus[]"""

    def __init__(self, config: ProprioceptionConfig = None):
        self.config = config or ProprioceptionConfig()
        self.channel_states: dict[str, ChannelState] = {
            "limb": ChannelState(),
            "force": ChannelState(),
            "accelerometer": ChannelState(),
            "thermoception": ChannelState(),
            "vent": ChannelState(),
            "eau": ChannelState(),
            "pression": ChannelState(),
            "texture": ChannelState(),
        }
        self._stale_emitted = False
        self._texture_cache: dict[str, float] = {}
        self._texture_cache_tick: int = 0

    def tick(self, body_state: BodyState | None,
             current_tick: int,
             texture_history: dict[str, int] | None = None,
             metabolism = None) -> tuple[list[Stimulus], float, dict]:
        """
        Main entry point. Called once per tick.

        Returns:
            stimuli: list of Stimulus objects for Law 1 injection
            comfort_composite: float -1.0 to +1.0 overall comfort
            modifiers: dict of cross-module modifiers (stability_modifier, rhythm_factor)
        """
        ...

    # --- Somatic Channels ---
    def _sense_limb(self, bs: BodyState, tick: int) -> list[Stimulus]: ...
    def _sense_force(self, bs: BodyState, tick: int) -> list[Stimulus]: ...
    def _sense_accelerometer(self, bs: BodyState, tick: int) -> list[Stimulus]: ...
    def _sense_thermoception(self, bs: BodyState, tick: int) -> list[Stimulus]: ...

    # --- Environmental Channels ---
    def _sense_vent(self, bs: BodyState, tick: int) -> list[Stimulus]: ...
    def _sense_eau(self, bs: BodyState, tick: int) -> list[Stimulus]: ...
    def _sense_pression(self, bs: BodyState, tick: int) -> tuple[list[Stimulus], dict]: ...
    def _sense_texture(self, bs: BodyState, tick: int,
                       texture_history: dict[str, int] | None) -> tuple[list[Stimulus], dict]: ...

    # --- Helpers ---
    def _hysteresis_allows(self, channel: str, sub: str, tick: int, value: float) -> bool: ...
    def _apply_immersion_attenuation(self, stimuli: list[Stimulus], water_level: float) -> list[Stimulus]: ...
    def _compute_comfort_composite(self, somatic: list[Stimulus], env: list[Stimulus]) -> float: ...


# --- Standalone Helpers ---
def tool_to_body_metaphor(tool_name: str) -> str: ...
def select_cold_text(intensity: float) -> str: ...
def select_warm_text(intensity: float) -> str: ...
def select_wind_text(intensity: float, direction_text: str) -> str: ...
def select_wind_direction_text(wind_direction: tuple[float, float, float]) -> str: ...
```

---

## INTEGRATION WITH TICK RUNNER

The tick runner must call proprioception before Law 1 stimulus injection:

```python
# In tick_runner_l1_cognitive_engine.py, within the tick loop:

if proprioception_module and body_state:
    proprio_stimuli, comfort, modifiers = proprioception_module.tick(
        body_state=body_state,
        current_tick=tick_number,
        texture_history=texture_history,  # from graph cache
        metabolism=metabolism,
    )
    stimuli.extend(proprio_stimuli)

    # Cross-feed: comfort available to metabolism
    if metabolism and hasattr(metabolism, 'set_body_comfort'):
        metabolism.set_body_comfort(comfort)

    # Cross-feed: rhythm_factor from pressure
    if 'rhythm_factor' in modifiers and metabolism:
        metabolism.set_rhythm_factor(modifiers['rhythm_factor'])

    # Cross-feed: stability_modifier from texture
    if 'stability_modifier' in modifiers:
        # Available to stability calculations in physics laws
        tick_context.stability_modifier = modifiers['stability_modifier']
```

---

## MARKERS

<!-- @mind:todo Create runtime/cognition/proprioception.py with the BodyState, ChannelState, ProprioceptionConfig, and ProprioceptionModule classes -->

<!-- @mind:todo Create tests/test_proprioception.py with unit tests for all 8 channels, hysteresis, edge cases, and immersion attenuation -->

<!-- @mind:todo Add proprioception hook to tick_runner_l1_cognitive_engine.py -->

<!-- @mind:todo Add record_light_input() and set_rhythm_factor() methods to metabolism.py -->
