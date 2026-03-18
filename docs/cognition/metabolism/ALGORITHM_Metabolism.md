# Metabolism — Algorithm: Per-Citizen Physics Constant Resolution

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
BEHAVIORS:       ./BEHAVIORS_Metabolism.md
PATTERNS:        ./PATTERNS_Metabolism.md
THIS:            ALGORITHM_Metabolism.md (you are here)
VALIDATION:      ./VALIDATION_Metabolism.md
HEALTH:          ./HEALTH_Metabolism.md
IMPLEMENTATION:  ./IMPLEMENTATION_Metabolism.md
SYNC:            ./SYNC_Metabolism.md

IMPL:            runtime/cognition/metabolism.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The metabolism resolves per-citizen, time-varying physics constants from three modifier sources: circadian rhythm, stimulus sensitivity, and active consumables. The resolution produces an `EffectiveConstants` struct — a flat bag of the same constant names the tick runner uses — with per-citizen values that replace the global defaults.

The algorithm has three phases:
1. **Circadian phase computation** — derive the current phase from UTC time + citizen timezone, then compute circadian multipliers for decay, consolidation, moat, and arousal.
2. **Consumable processing** — tick down active modifiers, expire finished ones, extract their parameter deltas.
3. **Composition** — multiply circadian and consumable modifiers onto base constants, clamp to valid ranges, return the flat struct.

Stimulus sensitivity is resolved separately on a per-stimulus basis (not per-tick) because it depends on the stimulus type, which is only known when a stimulus arrives.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 (Per-citizen parameterization) | B6 | Composes all modifier sources into a single flat struct |
| O2 (Circadian rhythm) | B1 | Translates timezone + clock into physics multipliers |
| O3 (Stimulus sensitivity) | B2, B7 | Scales energy budgets per stimulus type and sensory channel |
| O4 (Consumable modifiers) | B3, B4, B5 | Manages modifier lifecycle: application, ticking, expiry, cooldown |

---

## DATA STRUCTURES

### CitizenMetabolism

```python
@dataclass
class CitizenMetabolism:
    """Per-citizen metabolic profile. Persisted in the citizen's graph (actor node properties)."""

    # --- Circadian ---
    timezone_offset: float = 0.0         # hours from UTC (e.g., +1.0 for CET, -5.0 for EST)
    circadian_phase: float = 0.5         # computed: 0.0 = deep night, 1.0 = peak day
    circadian_amplitude: float = 0.4     # how strongly circadian modulates constants (0.0 = no effect)

    # --- Stimulus Sensitivity ---
    sensitivity: dict[str, float] = field(default_factory=lambda: {})
    # Keys are stimulus source types: "external", "self", "system", "directory", "temporal", "feed"
    # Or finer-grained: "code_logs", "social", "media", "notifications"
    # Values are gain multipliers: 1.0 = default, 0.3 = dampened, 1.5 = amplified
    # Missing keys default to 1.0

    # --- Sensory Channel Gains (MCP tools) ---
    channel_gains: dict[str, float] = field(default_factory=lambda: {})
    # Keys are MCP tool categories: "read", "send", "media", "graph_query", "think", etc.
    # Values are gain multipliers for stimuli originating from that tool
    # Missing keys default to 1.0

    # --- Active Modifiers (Consumables) ---
    active_modifiers: list[Modifier] = field(default_factory=list)

    # --- Base Overrides (citizen-specific defaults) ---
    base_decay_rate: float | None = None          # overrides DECAY_RATE if set
    base_moat: float | None = None                # overrides THETA_BASE_WM if set
    base_consolidation_alpha: float | None = None  # overrides CONSOLIDATION_ALPHA if set
    base_arousal_baseline: float | None = None     # additive offset to arousal computation

    # --- Consumable Cooldowns ---
    cooldowns: dict[str, int] = field(default_factory=dict)
    # Keys are consumable type names, values are tick number when last applied

    # --- Audit Log ---
    consumable_log: list[ConsumableEvent] = field(default_factory=list)
```

### Modifier

```python
@dataclass
class Modifier:
    """A temporary physics modifier from a consumable."""
    consumable_type: str           # e.g., "focus_boost", "calm", "deep_rest"
    ticks_remaining: int           # decremented each tick, removed at 0
    applied_at_tick: int           # tick number when applied

    # Multiplicative modifiers (1.0 = no change)
    decay_multiplier: float = 1.0         # multiplied onto effective_decay_rate
    consolidation_multiplier: float = 1.0 # multiplied onto effective_consolidation_rate

    # Additive modifiers (0.0 = no change)
    moat_bonus: float = 0.0               # added to effective_moat_base
    arousal_offset: float = 0.0           # added to arousal baseline

    # Dampening modifiers (1.0 = no change, 0.7 = 30% dampening)
    arousal_dampening: float = 1.0        # multiplied onto arousal computation
```

### ConsumableEvent

```python
@dataclass
class ConsumableEvent:
    """Audit trail entry for consumable lifecycle."""
    event_type: str        # "applied" | "expired" | "rejected"
    consumable_type: str   # which consumable
    tick: int              # when it happened
    reason: str = ""       # for rejections: "cooldown_active", "already_active"
    details: str = ""      # human-readable context
```

### ConsumableDefinition

```python
@dataclass
class ConsumableDefinition:
    """Registry entry defining a consumable type and its properties."""
    name: str
    duration_ticks: int       # how long the effect lasts
    cooldown_ticks: int       # minimum ticks between applications
    decay_multiplier: float = 1.0
    consolidation_multiplier: float = 1.0
    moat_bonus: float = 0.0
    arousal_offset: float = 0.0
    arousal_dampening: float = 1.0
    description: str = ""
```

### EffectiveConstants

```python
@dataclass
class EffectiveConstants:
    """Resolved physics constants for a single citizen for a single tick.

    The tick runner reads this instead of importing from constants.py.
    Every field corresponds to a constant in constants.py.
    """
    # Decay
    decay_rate: float              # base: 0.02
    long_term_decay: float         # base: 0.001

    # Consolidation
    consolidation_alpha: float     # base: 0.01
    consolidation_beta: float      # base: 0.005

    # Selection moat
    theta_base_wm: float          # base: 5.0
    arousal_moat_coeff: float     # base: 2.0
    boredom_moat_coeff: float     # base: 3.0
    frustration_moat_coeff: float # base: 1.0

    # Arousal
    arousal_baseline_offset: float # base: 0.0 (additive shift on arousal)
    arousal_dampening: float       # base: 1.0 (multiplicative on arousal)

    # All other constants pass through from globals unchanged
    # (the tick runner falls back to constants.py for anything not in this struct)
```

### Starter Consumable Registry

```python
CONSUMABLE_REGISTRY: dict[str, ConsumableDefinition] = {
    "focus_boost": ConsumableDefinition(
        name="focus_boost",
        duration_ticks=50,
        cooldown_ticks=150,
        decay_multiplier=0.5,           # decay at half rate
        moat_bonus=3.0,                 # higher moat = more focus stability
        description="Sharpens attention: halves decay, raises moat. 50 ticks, 150-tick cooldown."
    ),
    "calm": ConsumableDefinition(
        name="calm",
        duration_ticks=100,
        cooldown_ticks=200,
        arousal_dampening=0.7,          # 30% arousal reduction
        consolidation_multiplier=1.3,   # enhanced consolidation
        description="Calming effect: dampens arousal by 30%, boosts consolidation. 100 ticks, 200-tick cooldown."
    ),
    "deep_rest": ConsumableDefinition(
        name="deep_rest",
        duration_ticks=200,
        cooldown_ticks=500,
        decay_multiplier=2.0,           # double decay (aggressive cleanup)
        consolidation_multiplier=2.0,   # double consolidation
        moat_bonus=-3.0,                # much lower moat (dream-like)
        description="Deep rest mode: doubles both decay and consolidation, lowers moat drastically. 200 ticks, 500-tick cooldown."
    ),
}
```

---

## ALGORITHM: resolve_effective_constants()

### Step 1: Compute Circadian Phase

Given the citizen's `timezone_offset` and the current UTC time, compute the local hour and derive the circadian phase.

The circadian curve is sinusoidal with peak at 14:00 local time (early afternoon, when human cognitive performance peaks) and trough at 03:00 local time (deep night).

```python
def compute_circadian_phase(timezone_offset: float, utc_time: float) -> float:
    """
    Returns circadian_phase in [0.0, 1.0].
    0.0 = trough (deep night, ~03:00 local)
    1.0 = peak (early afternoon, ~14:00 local)
    """
    import math

    # Local hour as fractional [0.0, 24.0)
    utc_hour = (utc_time % 86400) / 3600.0
    local_hour = (utc_hour + timezone_offset) % 24.0

    # Phase: sinusoidal centered on peak at 14:00, trough at 02:00
    # Using cos with phase shift: cos(2*pi*(hour - 14)/24) maps 14:00 -> 1.0, 02:00 -> -1.0
    raw = math.cos(2.0 * math.pi * (local_hour - 14.0) / 24.0)

    # Normalize from [-1, 1] to [0, 1]
    phase = (raw + 1.0) / 2.0
    return phase
```

### Step 2: Derive Circadian Multipliers

The circadian phase modulates several constants. The `circadian_amplitude` controls how strongly the phase affects each constant. At amplitude 0.0, there is no circadian effect.

```python
def circadian_multipliers(phase: float, amplitude: float) -> dict[str, float]:
    """
    Compute per-constant multipliers from circadian phase.

    phase = 0.0 (deep night) -> higher decay, higher consolidation, lower moat
    phase = 1.0 (peak day)   -> lower decay, lower consolidation, higher moat

    amplitude scales the deviation from 1.0 (neutral).
    """
    # Night intensifies decay (clear the day's noise)
    # Day reduces decay (sustain attention)
    decay_mod = 1.0 + amplitude * (1.0 - 2.0 * phase)
    # At phase=0 (night): decay_mod = 1.0 + amplitude (e.g., 1.4 if amplitude=0.4)
    # At phase=1 (day):   decay_mod = 1.0 - amplitude (e.g., 0.6 if amplitude=0.4)

    # Night deepens consolidation (strengthen patterns during rest)
    # Day has normal consolidation
    consolidation_mod = 1.0 + amplitude * (1.0 - 2.0 * phase) * 0.6
    # Weaker effect than decay — consolidation shifts less dramatically

    # Night lowers moat (allow dream-like associations)
    # Day raises moat (focused attention)
    moat_mod = 1.0 + amplitude * (2.0 * phase - 1.0) * 0.5
    # At phase=0 (night): moat_mod = 1.0 - amplitude*0.5 (e.g., 0.8)
    # At phase=1 (day):   moat_mod = 1.0 + amplitude*0.5 (e.g., 1.2)

    # Arousal baseline shifts: higher during day, lower at night
    arousal_offset = amplitude * (2.0 * phase - 1.0) * 0.15
    # At phase=0: offset = -0.06 (slightly lower arousal at night)
    # At phase=1: offset = +0.06 (slightly higher arousal during day)

    return {
        "decay_multiplier": max(0.3, min(2.5, decay_mod)),
        "consolidation_multiplier": max(0.5, min(2.0, consolidation_mod)),
        "moat_multiplier": max(0.3, min(2.0, moat_mod)),
        "arousal_offset": max(-0.2, min(0.2, arousal_offset)),
    }
```

### Step 3: Process Active Modifiers

Tick down all active consumable modifiers. Remove expired ones and log their expiry.

```python
def process_modifiers(metabolism: CitizenMetabolism, current_tick: int) -> tuple[list[Modifier], list[ConsumableEvent]]:
    """
    Decrement ticks_remaining on each active modifier.
    Return (surviving_modifiers, expiry_events).
    """
    surviving = []
    events = []

    for mod in metabolism.active_modifiers:
        mod.ticks_remaining -= 1
        if mod.ticks_remaining <= 0:
            events.append(ConsumableEvent(
                event_type="expired",
                consumable_type=mod.consumable_type,
                tick=current_tick,
            ))
        else:
            surviving.append(mod)

    return surviving, events
```

### Step 4: Compose Effective Constants

Multiply all modifier sources onto the base constants. Order: base -> circadian -> consumables (all multiplicative; additive bonuses are summed).

```python
def resolve_effective_constants(
    metabolism: CitizenMetabolism | None,
    current_time_utc: float,
    current_tick: int,
) -> EffectiveConstants:
    """
    Full resolution pipeline.
    If metabolism is None, returns global defaults (backward compatibility).
    """
    from .constants import (
        DECAY_RATE, LONG_TERM_DECAY,
        CONSOLIDATION_ALPHA, CONSOLIDATION_BETA,
        THETA_BASE_WM, AROUSAL_MOAT_COEFF, BOREDOM_MOAT_COEFF, FRUSTRATION_MOAT_COEFF,
    )

    if metabolism is None:
        return EffectiveConstants(
            decay_rate=DECAY_RATE,
            long_term_decay=LONG_TERM_DECAY,
            consolidation_alpha=CONSOLIDATION_ALPHA,
            consolidation_beta=CONSOLIDATION_BETA,
            theta_base_wm=THETA_BASE_WM,
            arousal_moat_coeff=AROUSAL_MOAT_COEFF,
            boredom_moat_coeff=BOREDOM_MOAT_COEFF,
            frustration_moat_coeff=FRUSTRATION_MOAT_COEFF,
            arousal_baseline_offset=0.0,
            arousal_dampening=1.0,
        )

    # ---- Step 1: Base constants (citizen overrides or global defaults) ----
    base_decay = metabolism.base_decay_rate if metabolism.base_decay_rate is not None else DECAY_RATE
    base_consolidation = metabolism.base_consolidation_alpha if metabolism.base_consolidation_alpha is not None else CONSOLIDATION_ALPHA
    base_moat = metabolism.base_moat if metabolism.base_moat is not None else THETA_BASE_WM

    # ---- Step 2: Circadian modulation ----
    phase = compute_circadian_phase(metabolism.timezone_offset, current_time_utc)
    metabolism.circadian_phase = phase  # store for observability

    circ = circadian_multipliers(phase, metabolism.circadian_amplitude)

    eff_decay = base_decay * circ["decay_multiplier"]
    eff_consolidation = base_consolidation * circ["consolidation_multiplier"]
    eff_moat = base_moat * circ["moat_multiplier"]
    eff_arousal_offset = circ["arousal_offset"]
    eff_arousal_dampening = 1.0

    # ---- Step 3: Process consumable modifiers ----
    surviving, expiry_events = process_modifiers(metabolism, current_tick)
    metabolism.active_modifiers = surviving
    metabolism.consumable_log.extend(expiry_events)

    # Compose consumable effects (multiplicative stacking)
    total_moat_bonus = 0.0
    for mod in metabolism.active_modifiers:
        eff_decay *= mod.decay_multiplier
        eff_consolidation *= mod.consolidation_multiplier
        total_moat_bonus += mod.moat_bonus
        eff_arousal_offset += mod.arousal_offset
        eff_arousal_dampening *= mod.arousal_dampening

    eff_moat += total_moat_bonus

    # ---- Step 4: Clamp to valid ranges ----
    eff_decay = max(0.001, min(0.5, eff_decay))               # never zero, never catastrophic
    eff_consolidation = max(0.001, min(0.1, eff_consolidation)) # bounded consolidation
    eff_moat = max(0.0, min(20.0, eff_moat))                   # non-negative, bounded above
    eff_arousal_offset = max(-0.3, min(0.3, eff_arousal_offset))
    eff_arousal_dampening = max(0.3, min(1.5, eff_arousal_dampening))

    return EffectiveConstants(
        decay_rate=eff_decay,
        long_term_decay=LONG_TERM_DECAY,  # not modulated in v1
        consolidation_alpha=eff_consolidation,
        consolidation_beta=CONSOLIDATION_BETA,  # not modulated in v1
        theta_base_wm=eff_moat,
        arousal_moat_coeff=AROUSAL_MOAT_COEFF,   # not modulated in v1
        boredom_moat_coeff=BOREDOM_MOAT_COEFF,   # not modulated in v1
        frustration_moat_coeff=FRUSTRATION_MOAT_COEFF,  # not modulated in v1
        arousal_baseline_offset=eff_arousal_offset,
        arousal_dampening=eff_arousal_dampening,
    )
```

### Step 5: Stimulus Sensitivity Resolution (Per-Stimulus, Not Per-Tick)

This runs when a stimulus arrives, not during constant resolution. It scales the stimulus energy budget before Law 1 injection.

```python
def apply_stimulus_sensitivity(
    metabolism: CitizenMetabolism | None,
    stimulus_source: str,
    stimulus_tool: str | None,
    energy_budget: float,
) -> float:
    """
    Scale the stimulus energy budget by the citizen's sensitivity to this stimulus type.

    Checks two maps in order:
    1. channel_gains (MCP tool category) — most specific
    2. sensitivity (stimulus source type) — fallback
    3. Default gain = 1.0

    Returns the adjusted energy budget.
    """
    if metabolism is None:
        return energy_budget

    gain = 1.0

    # Check tool-specific channel gain first
    if stimulus_tool and stimulus_tool in metabolism.channel_gains:
        gain = metabolism.channel_gains[stimulus_tool]
    # Fall back to stimulus source sensitivity
    elif stimulus_source in metabolism.sensitivity:
        gain = metabolism.sensitivity[stimulus_source]

    # Clamp gain to prevent negative energy or extreme amplification
    gain = max(0.0, min(3.0, gain))

    return energy_budget * gain
```

---

## KEY DECISIONS

### D1: Multiplicative vs Additive Composition

```
DECISION: Circadian and consumable effects compose MULTIPLICATIVELY for rates (decay, consolidation)
          and ADDITIVELY for bonuses (moat bonus, arousal offset).
WHY:      Multiplicative composition for rates means effects scale proportionally.
          A 0.5x decay multiplier always halves decay regardless of the base rate.
          Additive composition for bonuses means effects are predictable in absolute terms.
          A +3.0 moat bonus always adds 3.0 regardless of the base moat.
```

### D2: Sensitivity Resolution Point

```
DECISION: Stimulus sensitivity is resolved per-stimulus at injection time,
          NOT baked into EffectiveConstants.
WHY:      The effective gain depends on the stimulus type, which is only known
          when a stimulus arrives. Baking it in would require either one
          EffectiveConstants per stimulus type (wasteful) or losing the
          per-type granularity (defeats the purpose).
```

### D3: Same-Type Consumable Stacking

```
DECISION: Same-type consumables do NOT stack. Applying "focus_boost" while one
          is active is rejected. Different types CAN be active simultaneously.
WHY:      Stacking the same consumable creates degenerate exponential effects
          (0.5 * 0.5 * 0.5 = 0.125x decay). Different types affecting different
          constants is safe and useful.
```

### D4: Circadian Peak and Trough Timing

```
DECISION: Peak at 14:00 local time, trough at ~02:00-03:00 local time.
WHY:      Human cognitive performance research (Monk & Carrier, 1997) shows
          performance peaks in early afternoon and troughs in early morning.
          This aligns the citizen's rhythm with their partner's likely state.
```

---

## DATA FLOW

```
UTC time + timezone_offset
    |
    v
compute_circadian_phase() -> phase [0.0, 1.0]
    |
    v
circadian_multipliers(phase, amplitude) -> {decay_mod, consolidation_mod, moat_mod, arousal_offset}
    |
    v
base_constants (citizen overrides or global defaults)
    |
    v
apply circadian multipliers
    |
    v
process_modifiers() -> surviving modifiers + expiry events
    |
    v
compose consumable effects (multiplicative/additive)
    |
    v
clamp to valid ranges
    |
    v
EffectiveConstants (flat struct)
    |
    v
Tick Runner reads EffectiveConstants instead of constants.py
```

---

## COMPLEXITY

**Time:** O(M) where M = number of active modifiers — typically 0-3, effectively O(1).

**Space:** O(M + L) where L = consumable audit log length. The log grows monotonically; consider periodic truncation in v2.

**Bottlenecks:**
- None expected. The entire resolution is <50 arithmetic operations.
- The sinusoidal computation in circadian phase is a single `cos()` call.
- Log growth: the consumable_log is append-only. For citizens that use consumables frequently, this could grow. Mitigation: truncate to last N entries periodically or archive old entries.

---

## HELPER FUNCTIONS

### `compute_circadian_phase()`

**Purpose:** Convert UTC time + timezone offset into a normalized circadian phase.

**Logic:** Local hour computed, sinusoidal mapping with peak at 14:00, normalized to [0, 1].

### `circadian_multipliers()`

**Purpose:** Translate circadian phase and amplitude into per-constant multipliers.

**Logic:** Linear interpolation from phase, scaled by amplitude, clamped to safe ranges.

### `process_modifiers()`

**Purpose:** Tick down active modifiers, expire finished ones.

**Logic:** Decrement, filter, emit expiry events.

### `apply_stimulus_sensitivity()`

**Purpose:** Scale stimulus energy budget by citizen's sensitivity to its type.

**Logic:** Look up gain in channel_gains (tool-specific) or sensitivity (source-specific), multiply onto budget.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `constants.py` | Import global defaults | Base constant values |
| `tick_runner_l1_cognitive_engine.py` | Provides EffectiveConstants | Runner uses our resolved values |
| `laws/law_01_energy_injection.py` | apply_stimulus_sensitivity() called before injection | Adjusted energy budget |
| `models.py` | CitizenCognitiveState | May carry metabolism reference |

---

## MARKERS

<!-- @mind:todo Design the integration point in L1CognitiveTickRunner.__init__() or run_tick(). The runner needs to receive EffectiveConstants. Options: (a) pass in constructor, (b) pass per-tick, (c) inject via CitizenCognitiveState. Recommendation: (c) since state already flows through. -->

<!-- @mind:proposition Consider adding a `metabolic_state_summary()` function that returns a human-readable snapshot: "Night mode (phase 0.12), focus boost active (32 ticks remaining), decay at 0.014". Useful for citizen self-awareness and debugging. -->

<!-- @mind:escalation The audit log grows indefinitely. Need a retention policy. Options: (a) keep last 1000 entries, (b) archive to graph as moment nodes, (c) prune on consolidation interval. NLR input needed. -->
