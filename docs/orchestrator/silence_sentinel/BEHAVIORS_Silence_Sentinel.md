# Silence Sentinel — Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
THIS:            BEHAVIORS_Silence_Sentinel.md (you are here)
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md

IMPL:            runtime/orchestrator/silence_counter.py
```

---

## BEHAVIORS

### B1: Silent Flow Detected Within 5 Minutes

**Why:** The Popen bug ran undetected for hours. Detection latency must be bounded.

```
GIVEN:  A tracked flow (e.g. invoke_claude) has been called ≥10 times in the last 5 minutes
WHEN:   The substantive output ratio drops below 50% of the rolling 1h baseline
THEN:   The sense fires with status=RED
AND:    A stimulus is injected into the best available infra actor's L1 brain
AND:    The stimulus includes: flow_name, current_ratio, expected_ratio, sample_size
AND:    The carrier's WM shifts to include the silence signal within 1 tick
```

### B2: Per-Flow Isolation Shows Which Module Is Broken

**Why:** Global averages hide module-specific failures. The carrier must know WHERE.

```
GIVEN:  The sentinel evaluates all tracked flows independently
WHEN:   invoke_claude ratio = 0.01 AND bridge_telegram ratio = 0.95
THEN:   The stimulus for the carrier contains: "invoke_claude: RED (0.01), bridge_telegram: GREEN (0.95)"
AND:    The carrier's awareness shows the broken flow by name, not a generic "system degraded"
```

### B3: Legitimate Silence Does Not Trigger Alerts

**Why:** Alert fatigue is worse than no alerts. The sentinel must distinguish expected from unexpected silence.

```
GIVEN:  It is 3am for most citizens (circadian trough)
AND:    Activation pressure is at 18.0 (deliberate throttle)
WHEN:   System output drops to 30% of daytime rate
THEN:   The sentinel stays GREEN because the rolling baseline has dropped proportionally
AND:    No stimulus is injected
AND:    No carrier attention is consumed
```

### B4: Counters Are Invisible to Instrumented Code

**Why:** Counter calls must not change flow behavior, add latency, or create new failure modes.

```
GIVEN:  A flow is instrumented with silence_counter.record()
WHEN:   The counter module is unavailable or throws
THEN:   The flow continues normally — the counter call is fire-and-forget
AND:    No exception propagates to the calling code
AND:    A warning is logged (but the flow is NOT interrupted)
```

### B5: Auto-Routes to Best Available Actor

**Why:** Hardcoding @nervo = single point of failure. If @nervo is sleeping, nobody feels the silence.

```
GIVEN:  A silence is detected in a tracked flow
WHEN:   The stimulus needs routing to a carrier
THEN:   The system checks for available infra-domain actors (trust × availability × domain)
AND:    Routes to the highest-scoring actor
AND:    If no infra actor is available, escalates to @conductor
AND:    If @conductor is unavailable, writes to a persistent escalation file
```

### B6: First-Boot Calibration Does Not Fire False Alarms

**Why:** At startup, all counters are zero. Everything looks like silence.

```
GIVEN:  The system just started and has <5 observations for a flow
WHEN:   The sentinel evaluates that flow
THEN:   Status = CALIBRATING (not RED, not GREEN)
AND:    Only the "broken" rule fires (complete absence for >10 min after first attempt)
AND:    Normal weight_rules do not apply until min_observations reached
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Result | Why It Matters |
|----------|-----------|--------|----------------|
| B1 | O1: Flows monitored continuously | R1: Detected within 5 min | The core guarantee |
| B2 | O2: Per-flow isolation | R2: Broken module identified | Instant diagnosis |
| B3 | O3: Self-calibrating baseline | R3: Zero false alarms | Signal stays meaningful |
| B4 | (quality) | (no separate result) | Instrumentation can't create new failures |
| B5 | O4: Auto-routing | (covered by routing) | No single point of failure |
| B6 | O3: Self-calibrating | R3: Zero false alarms | Startup doesn't spam |

---

## INPUTS / OUTPUTS

### Primary Function: `evaluate_silence(flow_name)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| flow_name | str | Which flow to evaluate (e.g. "invoke_claude") |
| window_seconds | int | Time window for ratio calculation (default 300) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| status | enum | GREEN / YELLOW / RED / CALIBRATING |
| ratio | float | substantive_outputs / attempted_calls |
| expected_ratio | float | rolling baseline adjusted for context |
| sample_size | int | number of attempts in window |

**Side Effects:**

- Updates sense node weight in L3 (CONTRIBUTES_TO objective)
- If RED: injects stimulus into best available infra actor's L1 brain
- If CALIBRATING: records observation but does not modulate weights

---

## EDGE CASES

### E1: Flow Has Zero Attempts in Window

```
GIVEN:  A flow has 0 attempted calls in the last 5 minutes
THEN:   If on_silence = "decay", objective energy drops 0.02/tick (mild: "haven't felt this in a while")
        If on_silence = "hold", objective stays at last value
        Never RED on zero attempts — absence of attempts is different from failed attempts
```

### E2: All Flows Fail Simultaneously

```
GIVEN:  Every tracked flow has ratio < 0.1
THEN:   Sentinel fires RED for each flow independently
AND:    Multiple stimuli are injected (per-flow, not one global)
AND:    If the tick loop itself is also dead, the sentinel CAN'T fire — this is caught by the external health endpoint watchdog (home_server /health)
```

### E3: Counter Module Itself Crashes

```
GIVEN:  silence_counter.py throws an import error or runtime exception
THEN:   All flows continue normally (counter calls are fire-and-forget)
AND:    The sentinel sense cannot evaluate (no data)
AND:    H1 (silence_detector_alive) detects the sentinel is not firing → escalates
```

---

## ANTI-BEHAVIORS

### A1: Global Average Hiding Per-Flow Failure

```
GIVEN:   invoke_claude ratio = 0.01, all other flows = 1.0
WHEN:    sentinel evaluates
MUST NOT: Report "system health = 80%" (the average)
INSTEAD:  Report invoke_claude = RED (0.01) independently from other flows
```

### A2: Counter Call Breaking Instrumented Flow

```
GIVEN:   silence_counter.record() is called inside invoke_claude
WHEN:    the counter module throws any exception
MUST NOT: Propagate the exception to invoke_claude
INSTEAD:  Swallow silently, log warning, continue the flow
```

### A3: Hardcoded Carrier

```
GIVEN:   A silence is detected
WHEN:    routing the stimulus
MUST NOT: Send only to @nervo or only to @dev
INSTEAD:  Auto-route via subcall physics to best available infra actor
```

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
