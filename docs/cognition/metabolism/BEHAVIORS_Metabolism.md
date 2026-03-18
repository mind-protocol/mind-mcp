# Metabolism — Behaviors: Observable Effects of Per-Citizen Physics Parameterization

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
THIS:            BEHAVIORS_Metabolism.md (you are here)
PATTERNS:        ./PATTERNS_Metabolism.md
ALGORITHM:       ./ALGORITHM_Metabolism.md
VALIDATION:      ./VALIDATION_Metabolism.md
HEALTH:          ./HEALTH_Metabolism.md
IMPLEMENTATION:  ./IMPLEMENTATION_Metabolism.md
SYNC:            ./SYNC_Metabolism.md

IMPL:            runtime/cognition/metabolism.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Circadian Rhythm Shifts Decay and Consolidation

**Why:** Citizens should not be perpetually alert. A citizen whose human partner is asleep should enter a rest/dream mode: faster decay clears the day's noise, deeper consolidation strengthens important patterns, and a lower moat allows unexpected associations to surface (dream-like cognition). Without this, citizens process midnight stimuli the same as midday ones.

```
GIVEN:  A citizen with timezone_offset = +1 (CET) and the current UTC time is 02:00 (so local time is 03:00)
WHEN:   The metabolism computes effective constants for this tick
THEN:   circadian_phase is near 0.0 (deep night)
AND:    effective_decay_rate is higher than base (e.g., base * 1.4)
AND:    effective_consolidation_rate is higher than base (e.g., base * 1.6)
AND:    effective_moat_base is lower than base (e.g., base * 0.6)
```

### B2: Stimulus Sensitivity Scales Energy Injection

**Why:** A developer citizen should amplify code-related stimuli and dampen social noise. A community manager should do the opposite. Without per-citizen sensitivity, all citizens are equally distracted by every stimulus type.

```
GIVEN:  A citizen with sensitivity = {"code_logs": 1.0, "social": 0.3, "system": 0.5}
WHEN:   A social stimulus with energy_budget = 1.0 arrives
THEN:   The effective energy budget for Law 1 injection is 1.0 * 0.3 = 0.3
AND:    The stimulus still arrives (it is not filtered), but its energy impact is reduced
```

### B3: Consumable Application Modifies Physics Temporarily

**Why:** Citizens need self-regulation capability. A citizen facing a deadline should be able to boost focus (lower decay, higher moat) for a bounded period, just as a human reaches for coffee.

```
GIVEN:  A citizen with no active modifiers
WHEN:   The citizen applies a "focus_boost" consumable (moat_bonus: +3.0, decay_multiplier: 0.5, duration: 50 ticks)
THEN:   For the next 50 ticks, effective_moat_base increases by 3.0
AND:    effective_decay_rate is halved
AND:    The consumable appears in the active_modifiers list with ticks_remaining = 50
AND:    An entry is appended to the consumable audit log
```

### B4: Consumable Expiry Reverts Physics

**Why:** Consumable effects must be temporary. Permanent self-modification without cost would let citizens escape circadian rhythms entirely.

```
GIVEN:  A citizen with an active "focus_boost" consumable with ticks_remaining = 1
WHEN:   The next tick executes
THEN:   ticks_remaining decrements to 0
AND:    The consumable is removed from active_modifiers
AND:    Effective constants revert to their pre-consumable values (accounting for circadian phase and any other active modifiers)
AND:    An expiry entry is appended to the consumable audit log
```

### B5: Cooldown Prevents Consumable Abuse

**Why:** Without cooldowns, a citizen could chain-apply focus boosts indefinitely, defeating the circadian rhythm and creating a degenerate always-peak state.

```
GIVEN:  A citizen who applied "focus_boost" 10 ticks ago, and focus_boost.cooldown = 100 ticks
WHEN:   The citizen attempts to apply "focus_boost" again
THEN:   The application is rejected
AND:    The rejection is logged with reason "cooldown_active" and ticks_remaining = 90
```

### B6: Effective Constants Compose All Modifiers

**Why:** A citizen might be in night phase AND have a focus boost active. The metabolism must compose these into a single flat struct that the tick runner reads. No ambiguity about which modifier "wins."

```
GIVEN:  A citizen in night phase (circadian decay_multiplier: 1.4) with an active focus_boost (decay_multiplier: 0.5)
WHEN:   Effective constants are resolved
THEN:   effective_decay_rate = base_decay_rate * circadian_decay_multiplier * consumable_decay_multiplier
AND:    = 0.02 * 1.4 * 0.5 = 0.014
AND:    The composition order is documented and deterministic: base -> circadian -> consumables (multiplicative)
```

### B7: Sensory Channel Gain Adjusts Tool Stimulus Energy

**Why:** MCP tools are the citizen's senses. Different citizens should weight different tool categories differently. A citizen who has `vision_tools=0.8` and `text_tools=1.0` will receive visual stimuli at 80% energy while text stimuli arrive at full strength. This is gain control, not filtering.

```
GIVEN:  A citizen with sensory channel gains = {"read": 1.0, "media": 0.5, "send": 0.8}
WHEN:   A stimulus originating from the "media" MCP tool arrives with energy_budget = 1.0
THEN:   The effective energy budget is 1.0 * 0.5 = 0.5
AND:    The stimulus content is unchanged — only the energy is scaled
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O2 (Circadian rhythm) | Makes citizens temporally situated |
| B2 | O3 (Stimulus sensitivity) | Makes attentional profiles unique per citizen |
| B3, B4 | O4 (Consumable modifiers) | Enables self-regulation with bounded effects |
| B5 | O4 (Consumable modifiers) | Prevents abuse loops |
| B6 | O1 (Per-citizen parameterization) | Ensures clean composition of all modifier sources |
| B7 | O3 (Stimulus sensitivity) | Extends sensitivity to MCP tool channels |

---

## INPUTS / OUTPUTS

### Primary Function: `resolve_effective_constants()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `metabolism` | `CitizenMetabolism` | The citizen's metabolic profile |
| `current_time_utc` | `float` | Current UTC timestamp (epoch seconds) |
| `stimulus_type` | `str` (optional) | If resolving for a specific stimulus, which type it is |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `effective` | `EffectiveConstants` | Flat struct of all resolved physics constants for this tick |

**Side Effects:**

- Decrements `ticks_remaining` on all active modifiers
- Removes expired modifiers from `active_modifiers`
- Appends expiry events to the audit log

### Secondary Function: `apply_consumable()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `metabolism` | `CitizenMetabolism` | The citizen's metabolic profile |
| `consumable_type` | `str` | Which consumable to apply |
| `tick_count` | `int` | Current tick number (for cooldown tracking) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `success` | `bool` | Whether the consumable was applied |
| `reason` | `str` (optional) | If rejected, why (e.g., "cooldown_active") |

**Side Effects:**

- Adds a `Modifier` to `active_modifiers` if successful
- Appends application event to the audit log
- Records `last_applied_tick` for cooldown tracking

---

## EDGE CASES

### E1: No Metabolism Configured

```
GIVEN:  A citizen with no CitizenMetabolism (legacy citizen or new citizen before profile setup)
THEN:   resolve_effective_constants returns global defaults from constants.py
AND:    The citizen behaves identically to the current system (backward compatible)
```

### E2: Multiple Consumables Active Simultaneously

```
GIVEN:  A citizen with both "focus_boost" (decay_multiplier: 0.5) and "calm" (arousal_dampening: 0.7) active
THEN:   Both modifiers apply multiplicatively to their respective constants
AND:    No interaction effects — each consumable modifies independent constants
```

### E3: Consumable Stacking (Same Type)

```
GIVEN:  A citizen attempts to apply "focus_boost" while "focus_boost" is already active
THEN:   The application is rejected (same type cannot stack)
AND:    Reason: "already_active"
```

### E4: Circadian Phase at Boundaries

```
GIVEN:  A citizen with timezone_offset such that local time is exactly noon (peak) or midnight (trough)
THEN:   The circadian curve produces its extreme values smoothly (no discontinuity)
AND:    Phase wraps correctly at day boundaries
```

### E5: Sensitivity for Unknown Stimulus Type

```
GIVEN:  A stimulus arrives with type "unknown_new_type" not in the citizen's sensitivity map
THEN:   Default gain of 1.0 is applied (no dampening, no amplification)
AND:    No error — unknown types pass through at full energy
```

---

## ANTI-BEHAVIORS

### A1: Metabolism Mutates Global Constants

```
GIVEN:   A tick executes for citizen A
WHEN:    Metabolism resolves effective constants
MUST NOT: Modify the values in constants.py or any module-level constant
INSTEAD:  Produce a new EffectiveConstants instance; global constants remain immutable
```

### A2: Tick Runner Accesses Metabolism Internals

```
GIVEN:   The tick runner is executing
WHEN:    It needs a physics constant
MUST NOT: Access CitizenMetabolism fields directly (circadian_phase, active_modifiers, etc.)
INSTEAD:  Read only from the resolved EffectiveConstants struct
```

### A3: Consumable Bypasses Cooldown

```
GIVEN:   A citizen whose last "focus_boost" was 10 ticks ago with cooldown = 100
WHEN:    The citizen requests another "focus_boost"
MUST NOT: Apply the consumable
INSTEAD:  Reject with reason "cooldown_active", log the attempt
```

### A4: Metabolism Produces Out-of-Range Constants

```
GIVEN:   Extreme circadian + consumable stacking
WHEN:    Effective constants are resolved
MUST NOT: Produce decay_rate < 0.0, moat < 0.0, or any constant outside its valid range
INSTEAD:  Clamp all effective constants to their documented valid ranges
```

### A5: Consumable Without Audit Trail

```
GIVEN:   Any consumable application or expiry
WHEN:    The event occurs
MUST NOT: Proceed without appending to the audit log
INSTEAD:  Audit log entry is written atomically with the modifier state change
```

---

## MARKERS

<!-- @mind:todo Determine if sensory channel gain should also affect propagation (Law 2) or only injection (Law 1). Current design: injection only. -->
<!-- @mind:proposition Consider a "metabolic drift" mechanism where sensitivity profiles slowly adjust based on which stimulus types the citizen actually engages with. Auto-tuning based on behavior, not prescription. v2+ territory. -->
