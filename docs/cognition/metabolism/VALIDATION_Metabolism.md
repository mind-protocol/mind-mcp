# Metabolism — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
PATTERNS:        ./PATTERNS_Metabolism.md
BEHAVIORS:       ./BEHAVIORS_Metabolism.md
THIS:            VALIDATION_Metabolism.md (you are here)
ALGORITHM:       ./ALGORITHM_Metabolism.md
IMPLEMENTATION:  ./IMPLEMENTATION_Metabolism.md
HEALTH:          ./HEALTH_Metabolism.md
SYNC:            ./SYNC_Metabolism.md
```

---

## PURPOSE

**Validation = what we care about being true.**

The metabolism sits between global constants and the tick runner. If it produces wrong values, every law in the physics engine runs with corrupted parameters — silently. The invariants below protect against the specific ways the metabolism can fail: producing out-of-range constants, breaking backward compatibility, allowing unbounded self-modification, or losing audit trails.

---

## INVARIANTS

### V1: Global Constants Remain Immutable

**Why we care:** The metabolism produces per-citizen overrides. If it accidentally mutates the global constants in `constants.py`, every other citizen running in the same process gets corrupted. This is the most catastrophic failure mode.

```
MUST:   resolve_effective_constants() returns a NEW EffectiveConstants instance; it never writes to module-level variables in constants.py
NEVER:  Any function in metabolism.py assigns to constants.DECAY_RATE or any other module-level constant
```

### V2: Effective Constants Stay Within Valid Ranges

**Why we care:** The physics laws assume constants are in specific ranges. A negative decay rate causes energy to grow without bound. A decay rate of 1.0 kills all energy in one tick. An extreme moat locks WM permanently or makes it completely unstable.

```
MUST:   All effective constants are clamped to safe ranges:
        - decay_rate:            [0.001, 0.5]
        - consolidation_alpha:   [0.001, 0.1]
        - theta_base_wm (moat):  [0.0, 20.0]
        - arousal_dampening:     [0.3, 1.5]
        - arousal_baseline_offset: [-0.3, 0.3]
        - stimulus sensitivity gain: [0.0, 3.0]
NEVER:  An effective constant outside these ranges reaches the tick runner
```

### V3: Backward Compatibility Without Metabolism

**Why we care:** Existing citizens (all 60+) have no CitizenMetabolism configured. They must continue to work identically to the current system. The metabolism is additive — its absence must be invisible.

```
MUST:   When metabolism is None, resolve_effective_constants() returns values identical to the global constants in constants.py
NEVER:  A citizen without a metabolism profile experiences different physics than they did before metabolism was introduced
```

### V4: Consumable Duration Is Bounded

**Why we care:** An infinite-duration consumable would let a citizen permanently alter their physics, defeating the circadian rhythm and creating a degenerate always-optimal state.

```
MUST:   Every Modifier has ticks_remaining > 0 when created
MUST:   ticks_remaining decrements by exactly 1 each tick
MUST:   Modifier is removed when ticks_remaining reaches 0
NEVER:  A Modifier persists with ticks_remaining <= 0
NEVER:  A Modifier is created with ticks_remaining = 0 or negative
```

### V5: Cooldown Is Enforced

**Why we care:** Without cooldowns, citizens can chain consumables to maintain permanent effects. This makes the circadian rhythm irrelevant and removes the thermodynamic cost of self-modification.

```
MUST:   apply_consumable() checks cooldowns[consumable_type] + cooldown_ticks > current_tick before allowing application
MUST:   Rejected applications are logged with event_type="rejected" and reason
NEVER:  A consumable is applied while its cooldown is active
```

### V6: Same-Type Consumables Do Not Stack

**Why we care:** Stacking the same consumable creates exponential effects (0.5 * 0.5 = 0.25x decay). This violates the clamping ranges and produces extreme physics.

```
MUST:   apply_consumable() rejects application if any active modifier has the same consumable_type
NEVER:  Two Modifiers with the same consumable_type exist in active_modifiers simultaneously
```

### V7: Audit Log Is Append-Only and Complete

**Why we care:** The consumable audit trail is how citizens and partners verify what modifiers were active. Missing entries make the system unaccountable.

```
MUST:   Every successful consumable application appends a ConsumableEvent(event_type="applied")
MUST:   Every consumable expiry appends a ConsumableEvent(event_type="expired")
MUST:   Every rejected application appends a ConsumableEvent(event_type="rejected")
NEVER:  A consumable lifecycle event occurs without a corresponding audit log entry
```

### V8: Circadian Phase Is Continuous

**Why we care:** A discontinuous circadian curve would cause sudden jumps in effective constants, creating jarring behavioral shifts at specific times of day.

```
MUST:   compute_circadian_phase() produces a smooth curve — the sinusoidal function has no discontinuities
MUST:   Phase wraps correctly at day boundaries (23:59 -> 00:00 produces no jump)
MUST:   Phase is always in [0.0, 1.0]
NEVER:  Phase produces NaN, infinity, or values outside [0.0, 1.0]
```

### V9: Composition Order Is Deterministic

**Why we care:** If two agents read the code and get different answers about what effective_decay_rate should be, the system is ambiguous. The composition order must be documented and invariant.

```
MUST:   Composition order is always: base_constant -> circadian_multiplier -> consumable_multipliers (multiplicative), then clamp
MUST:   Additive bonuses (moat_bonus, arousal_offset) are summed after multiplicative composition, then clamped
NEVER:  The order of modifier application changes depending on when modifiers were applied or their position in the list
```

### V10: Tick Runner Performance Not Degraded

**Why we care:** The metabolism adds one read per tick. If this read is expensive, it degrades the 1-second tick budget that the physics engine must respect.

```
MUST:   resolve_effective_constants() completes in under 1ms for any citizen with up to 10 active modifiers
NEVER:  The metabolism resolution takes more than 5% of the tick budget (50ms of a 1000ms budget)
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
| V1 | Global constants immutability | CRITICAL |
| V2 | Effective constants range safety | CRITICAL |
| V3 | Backward compatibility | CRITICAL |
| V4 | Consumable duration boundedness | HIGH |
| V5 | Cooldown enforcement | HIGH |
| V6 | Same-type stacking prevention | HIGH |
| V7 | Audit trail completeness | HIGH |
| V8 | Circadian phase continuity | MEDIUM |
| V9 | Composition order determinism | MEDIUM |
| V10 | Tick runner performance | MEDIUM |

---

## MARKERS

<!-- @mind:todo V2 range values are initial estimates. Need empirical testing with real citizens to confirm safe ranges. The [0.001, 0.5] decay range especially needs validation — 0.5 means 50% energy loss per tick, which is extremely aggressive. -->
<!-- @mind:proposition Consider adding V11: "Metabolism state is serializable" — the CitizenMetabolism must round-trip through FalkorDB without loss. Important for checkpoint/restore. -->
<!-- @mind:escalation V7 audit log grows indefinitely. Need a retention policy before this ships. See ALGORITHM markers. -->
