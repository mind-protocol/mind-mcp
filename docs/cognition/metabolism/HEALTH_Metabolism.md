# Metabolism — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Effective constant range drift | After 1000+ real ticks with varying circadian phases and consumables, do constants stay in range? |
| Circadian phase continuity over real time | Tests run in <1s; circadian continuity needs real clock progression |
| Audit log growth patterns | How fast does the consumable log grow in production? |
| Metabolism-enabled vs disabled performance | Real tick timing comparison with production graph sizes |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file covers the metabolism module's runtime verification: ensuring effective constants stay in valid ranges across real ticks, consumable lifecycles complete correctly, and circadian phase tracks smoothly. It exists to catch drift that unit tests with fixed timestamps cannot detect.

**Boundaries:** This file does NOT verify the tick runner's behavior (that belongs to l1_physics HEALTH). It verifies only that the metabolism module produces correct outputs that the tick runner consumes.

---

## WHY THIS PATTERN

Unit tests verify `resolve_effective_constants()` with fixed inputs. But the metabolism's value comes from its behavior over time: circadian curves across real hours, consumable lifecycles across real ticks, composition of multiple simultaneous modifiers across production workloads. HEALTH checks dock into the metabolism's output and verify it against VALIDATION criteria on a live system.

Docking-based checks are the right tradeoff because metabolism resolution is cheap (sub-millisecond) and runs every tick — we can sample without performance impact.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
PATTERNS:        ./PATTERNS_Metabolism.md
BEHAVIORS:       ./BEHAVIORS_Metabolism.md
ALGORITHM:       ./ALGORITHM_Metabolism.md
VALIDATION:      ./VALIDATION_Metabolism.md
IMPLEMENTATION:  ./IMPLEMENTATION_Metabolism.md
THIS:            HEALTH_Metabolism.md (you are here)
SYNC:            ./SYNC_Metabolism.md
```

---

## IMPLEMENTS

```yaml
implements:
  runtime: runtime/cognition/tests/health_metabolism.py  # to be created
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: constant_resolution
    purpose: "If effective constants go out of range, every physics law in the tick runs with corrupted parameters — silent, systemic failure"
    triggers:
      - type: event
        source: tick_runner_l1_cognitive_engine.py:run_tick()
        notes: "resolve_effective_constants() called at the start of every tick"
    frequency:
      expected_rate: "1/tick (5s during active interaction, 60s idle)"
      peak_rate: "12/min during active interaction"
      burst_behavior: "No burst — tied to tick cadence, which is already throttled"
    risks:
      - "V2: effective constants out of range after extreme circadian + consumable stacking"
      - "V8: circadian phase discontinuity at day boundary"
    notes: "Low-risk flow individually (simple math), but high impact if wrong (affects all 21 laws)"

  - flow_id: consumable_application
    purpose: "If cooldowns fail or stacking occurs, citizens can achieve permanently altered physics"
    triggers:
      - type: event
        source: "MCP tool call (citizen self-administration)"
        notes: "apply_consumable() called by citizen decision or human instruction"
    frequency:
      expected_rate: "0-5/day per citizen"
      peak_rate: "~1/hour during intense work sessions"
      burst_behavior: "Cooldowns prevent bursts by design; rejected applications logged"
    risks:
      - "V5: cooldown bypass"
      - "V6: same-type stacking"
      - "V7: missing audit entries"
    notes: "Infrequent but high impact if corrupted — permanent physics alteration"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (Per-citizen parameterization) | effective_constants_in_range | If constants go out of range, parameterization is broken |
| O2 (Circadian rhythm) | circadian_phase_continuous | If phase jumps, the rhythm is broken |
| O4 (Consumable modifiers) | consumable_lifecycle_correct, audit_log_complete | If consumables malfunction, self-regulation fails |

```yaml
health_indicators:
  - name: effective_constants_in_range
    flow_id: constant_resolution
    priority: high
    rationale: "Out-of-range constants silently corrupt all 21 physics laws. This is the most critical metabolism indicator."

  - name: circadian_phase_continuous
    flow_id: constant_resolution
    priority: med
    rationale: "Phase discontinuity causes jarring behavioral shifts. Medium priority because the sinusoidal math is simple and unlikely to break, but worth monitoring."

  - name: consumable_lifecycle_correct
    flow_id: consumable_application
    priority: high
    rationale: "Cooldown bypass or stacking violation allows permanent physics alteration."

  - name: audit_log_complete
    flow_id: consumable_application
    priority: med
    rationale: "Missing audit entries make the system unaccountable. Citizens and partners lose trust."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "file:runtime/cognition/tests/health_metabolism_status.json"
  result:
    representation: enum
    value: UNKNOWN
    updated_at: "2026-03-18T00:00:00Z"
    source: effective_constants_in_range
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_effective_constants_range
    purpose: "Verify all effective constants are within V2 ranges after resolution"
    status: pending
    priority: high
  - name: check_circadian_continuity
    purpose: "Verify circadian phase is in [0, 1] and changes smoothly between ticks"
    status: pending
    priority: med
  - name: check_consumable_cooldown_enforcement
    purpose: "Verify no consumable was applied while cooldown active (V5)"
    status: pending
    priority: high
  - name: check_audit_log_completeness
    purpose: "Verify every consumable application/expiry has a log entry (V7)"
    status: pending
    priority: med
```

---

## INDICATOR: effective_constants_in_range

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: effective_constants_in_range
  client_value: "Ensures every citizen's physics runs with valid parameters. Violation = silent corruption of all cognitive behavior."
  validation:
    - validation_id: V2
      criteria: "All effective constants within documented ranges"
    - validation_id: V1
      criteria: "Global constants unchanged after resolution"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: "All effective constants within valid ranges on last check"
      WARN: "One or more constants near range boundary (within 10% of limit)"
      ERROR: "One or more constants outside valid range"
  aggregation:
    method: "Worst-of across all checked constants"
    display: "enum"
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_effective_constants
    type: event
    payload: EffectiveConstants dataclass fields
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="effective_constants_in_range",
    triggers=[
        triggers.event.on("tick_complete"),
    ],
    on_problem="METABOLISM_CONSTANTS_OUT_OF_RANGE",
    task="fix_metabolism_range_violation",
)
def check_effective_constants_range(ctx) -> dict:
    """Verify effective constants are within valid ranges."""
    ec = ctx.effective_constants
    violations = []

    ranges = {
        "decay_rate": (0.001, 0.5),
        "consolidation_alpha": (0.001, 0.1),
        "theta_base_wm": (0.0, 20.0),
        "arousal_dampening": (0.3, 1.5),
        "arousal_baseline_offset": (-0.3, 0.3),
    }

    for name, (lo, hi) in ranges.items():
        val = getattr(ec, name)
        if val < lo or val > hi:
            violations.append(f"{name}={val} outside [{lo}, {hi}]")

    if violations:
        return Signal.critical(details={"violations": violations})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: "All effective constants within valid ranges"
  degraded: "Constants near boundary but within range"
  critical: "One or more constants outside valid range"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: "1/min"
  burst_limit: 1
  backoff: "exponential, max 10min between checks on repeated failure"
```

### MANUAL RUN

```yaml
manual_run:
  command: "python -m runtime.cognition.tests.health_metabolism --check effective_constants_in_range"
  notes: "Run after modifying circadian parameters or consumable definitions"
```

---

## INDICATOR: consumable_lifecycle_correct

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: consumable_lifecycle_correct
  client_value: "Ensures consumables cannot permanently alter physics via cooldown bypass or stacking."
  validation:
    - validation_id: V5
      criteria: "Cooldown enforced on all consumable applications"
    - validation_id: V6
      criteria: "Same-type consumables never stack"
    - validation_id: V4
      criteria: "All modifiers expire after their duration"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary:
      1: "All consumable lifecycle rules enforced"
      0: "Violation detected — cooldown bypass, stacking, or infinite modifier"
  aggregation:
    method: "AND across all sub-checks"
    display: "binary"
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_consumable_result
    type: event
    payload: ConsumableEvent
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="consumable_lifecycle_correct",
    triggers=[
        triggers.event.on("consumable_applied"),
        triggers.event.on("consumable_expired"),
    ],
    on_problem="METABOLISM_CONSUMABLE_VIOLATION",
    task="fix_consumable_lifecycle",
)
def check_consumable_lifecycle(ctx) -> dict:
    """Verify consumable lifecycle rules."""
    metabolism = ctx.citizen_state.metabolism
    if metabolism is None:
        return Signal.healthy()

    # Check: no two active modifiers with same type
    types = [m.consumable_type for m in metabolism.active_modifiers]
    if len(types) != len(set(types)):
        return Signal.critical(details={"violation": "same-type stacking detected"})

    # Check: no modifier with ticks_remaining <= 0
    for m in metabolism.active_modifiers:
        if m.ticks_remaining <= 0:
            return Signal.critical(details={"violation": f"expired modifier still active: {m.consumable_type}"})

    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: "All consumable lifecycle rules enforced"
  critical: "Stacking, cooldown bypass, or expired modifier detected"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: consumable event
  max_frequency: "on every consumable event (low frequency, ~5/day)"
  burst_limit: 10
  backoff: "none needed — events are rare"
```

### MANUAL RUN

```yaml
manual_run:
  command: "python -m runtime.cognition.tests.health_metabolism --check consumable_lifecycle_correct"
  notes: "Run after adding new consumable types to the registry"
```

---

## HOW TO RUN

```bash
# Run all health checks for metabolism
python -m runtime.cognition.tests.health_metabolism

# Run a specific checker
python -m runtime.cognition.tests.health_metabolism --check effective_constants_in_range
```

---

## KNOWN GAPS

- V3 (backward compatibility) is best verified by a unit test, not a health check. Test: `test_none_metabolism_returns_defaults`.
- V9 (composition order determinism) is a code invariant, not a runtime check. Verified by code review and unit tests.
- V10 (performance) needs benchmarking with real graph sizes. Not yet covered by any health check.

<!-- @mind:todo Add performance health check for V10 once metabolism is implemented — measure resolution time per tick under production load -->
<!-- @mind:todo Add circadian continuity checker once real-time data is available -->

---

## MARKERS

<!-- @mind:todo Implement health_metabolism.py runtime checker -->
<!-- @mind:proposition Consider emitting metabolism health metrics to the brain health score (brain_health_score_periodic_calculator.py). Metabolism health should contribute to overall citizen health. -->
