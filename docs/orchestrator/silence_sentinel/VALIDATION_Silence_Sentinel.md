# Silence Sentinel — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
THIS:            VALIDATION_Silence_Sentinel.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md
```

---

## INVARIANTS

### V1: Silence Is Detected

**Why we care:** The entire module exists for this. If silence goes undetected, we're back to the Popen bug scenario — hours of invisible failure.

```
MUST:   When a tracked flow's output ratio drops below 50% of rolling baseline
        for ≥5 minutes with ≥10 attempts, the sense MUST fire with status RED.
NEVER:  A flow with ratio < 0.1 and sample ≥ 10 stays GREEN for more than 1 tick.
```

### V2: Counter Calls Cannot Create New Failures

**Why we care:** Instrumentation that breaks the instrumented flow is worse than no instrumentation. The cure must not be the disease.

```
MUST:   silence_counter.record_attempt() and record_success() complete in < 1ms
        and NEVER raise exceptions to the caller.
NEVER:  A counter call propagates an exception to the instrumented flow.
        All exceptions are caught internally and logged as warnings.
```

### V3: Per-Flow Isolation Is Maintained

**Why we care:** Global averages hide module-specific failures. The Popen bug was invisible in aggregate.

```
MUST:   Each tracked flow has independent counters, independent baseline,
        independent evaluation. RED on invoke_claude does NOT affect
        bridge_telegram's status.
NEVER:  Ratios are averaged across flows. Each flow is evaluated alone.
```

### V4: Legitimate Silence Does Not Alert

**Why we care:** Alert fatigue kills the signal. If the sentinel fires every night, nobody will care when it fires for real.

```
MUST:   When activation_pressure > 15.0 (most citizens throttled by design),
        the expected baseline adjusts downward proportionally.
MUST:   When circadian_factor < 0.6 (night phase for most citizens),
        the expected baseline adjusts downward proportionally.
NEVER:  The sentinel fires RED when the system is legitimately quiet
        (zero attempts = not a failure, it's idle).
```

### V5: No Single Point of Failure in Routing

**Why we care:** If the only carrier is @nervo and @nervo is in rest phase, nobody feels the silence.

```
MUST:   Stimulus routing uses existing inject_stimulus with domain="infra"
        which auto-selects based on trust × availability × domain affinity.
NEVER:  A single hardcoded citizen_handle appears in the routing path.
```

### V6: Calibration Prevents False Alarms on Boot

**Why we care:** At startup, all counters are zero. Without calibration, everything looks broken.

```
MUST:   For the first min_observations (default 5) evaluations per flow,
        status = CALIBRATING and normal weight_rules DO NOT fire.
MUST:   During calibration, only the "broken" rule fires: complete absence
        (ratio = 0.0 with ≥10 attempts for ≥10 minutes).
NEVER:  A fresh boot triggers RED on flows that haven't had time to produce output.
```

---

## PRIORITY

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Silence is detected | CRITICAL |
| V2 | Counter can't break flows | CRITICAL |
| V3 | Per-flow isolation | HIGH |
| V4 | No false alarms | HIGH |
| V5 | No single point of failure | HIGH |
| V6 | Boot calibration | MEDIUM |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
