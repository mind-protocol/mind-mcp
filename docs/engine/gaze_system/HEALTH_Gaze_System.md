# Gaze System — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Joint value drift over time | Needs 1000+ real ticks, not fixtures |
| Social gaze ratio health | Emergent behavior from timer interactions |
| Blink rate stability | Interaction of circadian + drives over real time |
| Drive-eyelid coherence | Needs real drive oscillation, not constant values |

**Tests gate completion. Health monitors runtime.**

If behavior is deterministic with known inputs -> write a test.
If behavior emerges from real data over time -> write a health check.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the gaze system module, verifying that facial joint outputs remain within mechanical limits, that blink and social gaze ratios stay within biological/social norms, and that drive-eyelid coherence holds over extended runtime. It exists because the gaze system's correctness depends on the interaction of three continuously varying inputs (awareness, drives, circadian) over time, which unit tests with fixed inputs cannot fully verify.

**Boundaries:** This file does NOT verify exteroception correctness (what the citizen sees), interoception correctness (what drives are active), or metabolism correctness (circadian phase computation). Those are verified by their own HEALTH files. We only verify that GIVEN valid inputs, the gaze system produces valid outputs.

---

## WHY THIS PATTERN

Tests pass but runtime fails when: drive combinations that never appear in test fixtures produce out-of-range joint values; social gaze timer interactions over 60+ seconds of real conversation produce a stare ratio outside the 70/30 norm; blink rate formula interacts with circadian phase in a way that produces biologically implausible rates under specific conditions. Docking-based checks at the output boundary catch these without modifying the gaze system code. Throttling at 1 check per 30 seconds prevents the health system from consuming tick budget.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gaze_System.md
PATTERNS:        ./PATTERNS_Gaze_System.md
BEHAVIORS:       ./BEHAVIORS_Gaze_System.md
ALGORITHM:       ./ALGORITHM_Gaze_System.md
VALIDATION:      ./VALIDATION_Gaze_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gaze_System.md
THIS:            HEALTH_Gaze_System.md (you are here)
SYNC:            ./SYNC_Gaze_System.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks/gaze_system_health_checker.py  # (to be created)
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: gaze_tick_pipeline
    purpose: "If gaze output is invalid, citizen's face breaks visually (mesh deformation, uncanny stare, frozen expression)"
    triggers:
      - type: schedule
        source: tick_runner per-tick call
        notes: "gaze_tick() is called once per tick, after all cognition phases"
    frequency:
      expected_rate: "1/tick (1 per 5-60 seconds depending on tick interval)"
      peak_rate: "1/tick (cannot exceed tick rate)"
      burst_behavior: "no bursts — strictly one call per tick"
    risks:
      - "V1: joint values outside body model constraints under extreme drive combinations"
      - "V2: blink rate formula producing values outside [3, 30] under edge-case inputs"
      - "V5: social gaze timer producing > 5s unbroken stare under certain timing conditions"
      - "V6: lerp factor producing > 0.3 radian head jump on large target changes"
    notes: "the gaze system is purely synchronous and single-threaded — no concurrency risks"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Causally grounded gaze | gaze_cause_traceability | If gaze changes without a cause, the citizen looks random |
| Natural eye-head coordination | eye_head_lag_preserved | If head moves with eyes, the citizen looks robotic |
| Drive-modulated gaze style | drive_eyelid_coherence | If eyelids contradict drives, the face is unreadable |
| Blink as biological signal | blink_rate_in_range | If blink rate is extreme, the citizen looks inhuman |
| Lip sync bridges voice and body | lip_sync_speech_coherence | If mouth animates during silence or freezes during speech, uncanny |

```yaml
health_indicators:
  - name: joint_limits_respected
    flow_id: gaze_tick_pipeline
    priority: high
    rationale: "if any joint exceeds body model constraints, the mesh deforms visually — immediate user-visible breakage"

  - name: blink_rate_in_range
    flow_id: gaze_tick_pipeline
    priority: high
    rationale: "blink rate outside [3, 30] makes the citizen appear frozen or seizing — destroys living-being illusion"

  - name: social_gaze_ratio_healthy
    flow_id: gaze_tick_pipeline
    priority: med
    rationale: "sustained stare > 5s in conversation makes the citizen feel threatening — social norm violation"

  - name: drive_eyelid_coherence
    flow_id: gaze_tick_pipeline
    priority: med
    rationale: "eyelid state contradicting dominant drive makes the face unreadable — conflicting signals"

  - name: smooth_transitions
    flow_id: gaze_tick_pipeline
    priority: med
    rationale: "discontinuous head jumps produce visible popping — breaks animation quality"
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "runtime/checks/gaze_system_health_checker.py output"
  result:
    representation: enum
    value: PENDING
    updated_at: "2026-03-18T00:00:00Z"
    source: gaze_system_health_composite
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_gaze_joint_limits
    purpose: "verify all output joint values are within citizen_body_model.yaml constraints (V1)"
    status: pending
    priority: high

  - name: check_gaze_blink_rate
    purpose: "verify computed blink rate is within [3, 30] blinks/min (V2)"
    status: pending
    priority: high

  - name: check_gaze_social_ratio
    purpose: "verify social gaze look/away ratio is within 60-80% over 60s windows (V5)"
    status: pending
    priority: med

  - name: check_gaze_eyelid_coherence
    purpose: "verify eyelid openness aligns with dominant drive state (V9)"
    status: pending
    priority: med

  - name: check_gaze_head_smoothness
    purpose: "verify no head rotation exceeds 0.15 rad per tick (V6)"
    status: pending
    priority: med
```

---

## INDICATOR: joint_limits_respected

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: joint_limits_respected
  client_value: "prevents mesh deformation and visual breakage in the 3D client"
  validation:
    - validation_id: V1
      criteria: "all eye, head, neck, eyelid, jaw, and mouth joint values within body model constraints"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = all joints in range this check window, 0 = at least one violation detected"
  aggregation:
    method: "all-pass — any single violation fails the indicator"
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_output_joints
    type: event
    payload: "GazeOutput with all joint target values"
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="joint_limits_respected",
    triggers=[
        triggers.schedule.every_n_ticks(30),
    ],
    on_problem="GAZE_JOINT_VIOLATION",
    task="fix_gaze_joint_clamping",
)
def joint_limits_respected(ctx) -> dict:
    """Verify all gaze output joint values are within body model constraints."""
    output = ctx.latest_gaze_output
    violations = []
    LIMITS = {
        "left_eye_pitch": (-0.5, 0.5), "left_eye_yaw": (-0.7, 0.3),
        "right_eye_pitch": (-0.5, 0.5), "right_eye_yaw": (-0.3, 0.7),
        "head_pitch": (-0.3, 0.3), "head_yaw": (-0.5, 0.5),
        "neck_pitch": (-0.5, 0.7), "neck_yaw": (-1.2, 1.2),
        "left_eyelid": (0.0, 1.0), "right_eyelid": (0.0, 1.0),
        "jaw_angle": (0.0, 0.4),
        "mouth_corner_left": (-0.5, 0.8), "mouth_corner_right": (-0.5, 0.8),
    }
    for joint, (lo, hi) in LIMITS.items():
        val = getattr(output, joint)
        if val < lo or val > hi:
            violations.append(f"{joint}={val:.3f} outside [{lo}, {hi}]")
    if violations:
        return Signal.critical(details={"violations": violations})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: "all joint values within body model constraints for the check window"
  degraded: "not applicable — joint violations are binary (in range or not)"
  critical: "one or more joint values exceeded body model constraints"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: every 30 ticks
  max_frequency: "1/30 ticks (~every 2-30 minutes depending on tick rate)"
  burst_limit: 1
  backoff: "none needed — fixed schedule"
```

### MANUAL RUN

```yaml
manual_run:
  command: "mind doctor --check gaze_joint_limits"
  notes: "run after modifying drive modulation formulas or joint clamping logic"
```

---

## INDICATOR: blink_rate_in_range

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: blink_rate_in_range
  client_value: "prevents inhuman blink behavior (frozen or seizing appearance)"
  validation:
    - validation_id: V2
      criteria: "computed blink rate always in [3.0, 30.0] blinks per minute"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = blink rate in range, 0 = blink rate out of range"
  aggregation:
    method: "all-pass"
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_output_joints
    type: event
    payload: "computed blink_rate value (exposed via GazeState or logged)"
```

### SIGNALS

```yaml
signals:
  healthy: "blink rate is within [3, 30] blinks/min"
  critical: "blink rate computed outside [3, 30] before clamping"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: every 60 ticks
  max_frequency: "1/60 ticks"
  burst_limit: 1
  backoff: "none"
```

---

## HOW TO RUN

```bash
# Run all health checks for the gaze system
mind doctor --module engine/gaze_system

# Run a specific checker
mind doctor --check gaze_joint_limits
```

---

## KNOWN GAPS

<!-- @mind:todo Missing checker for V3 (traceable cause). Need to add gaze_cause field to GazeOutput first, then write a checker that verifies every output has a non-empty cause. -->

<!-- @mind:todo Missing checker for V4 (eye-head lag). Need to instrument timing within gaze_tick to measure actual lag. Difficult to check from output alone — may need internal state exposure. -->

<!-- @mind:todo Missing checker for V8 (lip sync speech coherence). Need to correlate TTS active state with jaw/lip animation presence. Requires access to TTS state alongside GazeOutput. -->

<!-- @mind:todo Missing checker for V10 (blink completes before gaze snap). Need to verify that interrupt events are queued during active blink. Requires internal blink state visibility. -->

---

## MARKERS

<!-- @mind:todo Create runtime/checks/gaze_system_health_checker.py with stub implementations of all pending checkers. -->

<!-- @mind:proposition Consider a composite health score that rolls up all gaze checkers into a single float [0, 1] for the Doctor dashboard. Weight: joint_limits (0.3) + blink_rate (0.2) + social_ratio (0.2) + eyelid_coherence (0.15) + smoothness (0.15). -->

<!-- @mind:escalation The social gaze ratio checker needs to observe conversation state over time (60s windows). This requires either a rolling buffer in the gaze system or a separate observation layer. Design decision: where does this temporal observation state live? In the checker or in GazeState? -->
