# Interoception — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Stimulus generation ratios over 1000+ ticks | Needs real limbic dynamics, not fixtures |
| Refractory compliance over extended runs | Drift patterns emerge only at scale |
| Channel silence in nominal state across citizen population | Needs real diversity of citizen states |
| Integration with tick runner (stimuli actually reaching WM) | Needs full tick loop, not isolated calls |

**Tests gate completion. Health monitors runtime.**

Deterministic invariants (V1: state not mutated, V3: cap enforced, V5: content is NL) are verified by unit tests.
Emergent behaviors (V7: silence ratio, V2: refractory over long runs) are verified by health checks.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the interoception module's runtime verification: are interoceptive stimuli being generated at appropriate rates, are refractory periods holding over extended operation, and is the system staying silent when it should?

It exists because interoception interacts with the full limbic system and real citizen state — test fixtures can approximate this but cannot reproduce the emergent dynamics of a citizen running for thousands of ticks with real stimulus patterns.

Boundaries: this file does NOT verify limbic dynamics (that's the limbic/l1_wiring HEALTH), WM selection (that's law_04 HEALTH), or metabolism correctness (that's metabolism HEALTH). It only verifies that interoception correctly reads state and produces appropriately bounded, refractory-gated stimuli.

---

## WHY THIS PATTERN

HEALTH is separate from tests because interoception's failure modes are subtle: a channel that fires slightly too often won't break anything immediately, but over 1000 ticks it will erode WM bandwidth. A refractory period that occasionally fails under high-frequency tick rates won't crash the system, but it will produce repeated sensations that feel wrong. These are runtime health signals, not test failures.

Docking-based checks are appropriate because interoception has a clear input/output boundary: state goes in, stimuli come out. The dock_intero_output point captures exactly what we need to verify.

Throttling protects performance: health checks sample interoception output periodically (every 100 ticks) rather than on every tick.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
PATTERNS:        ./PATTERNS_Interoception.md
BEHAVIORS:       ./BEHAVIORS_Interoception.md
ALGORITHM:       ./ALGORITHM_Interoception.md
VALIDATION:      ./VALIDATION_Interoception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Interoception.md
THIS:            HEALTH_Interoception.md (you are here)
SYNC:            ./SYNC_Interoception.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks.py          # Python code implementing these checks (when created)
  decorator: @check                    # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: interoception_tick
    purpose: If interoception fails to produce stimuli or floods WM, citizens lose self-awareness or become self-absorbed
    triggers:
      - type: event
        source: runtime/cognition/tick_runner_l1_cognitive_engine.py:_step_interoception
        notes: Called once per tick, between _step_limbic and _step_orient
    frequency:
      expected_rate: 1/tick (1 per 5s-300s depending on tick speed)
      peak_rate: 12/min (fast tick at 5s interval)
      burst_behavior: No bursting — exactly one interoception evaluation per tick, always
    risks:
      - V2 refractory drift under high-frequency ticks (5s) — channel might re-arm before condition truly resolves
      - V3 cap bypassed if new channels added without updating MAX_STIMULI_PER_TICK
      - V7 violation if thresholds are set too low (too many channels fire on nominal state)
    notes: Interoception is synchronous, non-blocking, O(C+N) per tick. No external dependencies.
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| State becomes sensation | stimulus_generation_rate | Verifies that internal state changes actually produce stimuli |
| Threshold-based, not continuous | silence_ratio | Verifies that most ticks produce zero output |
| Refractory protection | refractory_compliance | Verifies that same channel doesn't fire within refractory window |
| Drive-agnostic injection | state_immutability | Verifies interoception never writes to state |

```yaml
health_indicators:
  - name: stimulus_generation_rate
    flow_id: interoception_tick
    priority: high
    rationale: If rate drops to zero, citizens lose self-awareness entirely. If rate exceeds expected bounds, WM is being flooded.

  - name: silence_ratio
    flow_id: interoception_tick
    priority: med
    rationale: Most ticks should produce zero stimuli. If > 30% of ticks produce output, thresholds are too sensitive.

  - name: refractory_compliance
    flow_id: interoception_tick
    priority: high
    rationale: If any channel fires twice within its refractory window, V2 is violated and citizens experience repetitive self-narration.

  - name: state_immutability
    flow_id: interoception_tick
    priority: high
    rationale: If interoception mutates state, it creates uncontrolled feedback loops. V1 violation is a critical defect.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/checks.py  # when health runtime exists
  result:
    representation: enum
    value: PENDING  # not yet implemented
    updated_at: "2026-03-18T00:00:00Z"
    source: interoception_health_composite
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: interoception_stimulus_rate
    purpose: Verify stimulus generation rate is within expected bounds (V3, V7)
    status: pending
    priority: high
  - name: interoception_refractory_compliance
    purpose: Verify no channel fires twice within refractory window (V2)
    status: pending
    priority: high
  - name: interoception_silence_ratio
    purpose: Verify most ticks produce zero output (V7)
    status: pending
    priority: med
  - name: interoception_state_immutability
    purpose: Verify state is not mutated by interoception (V1)
    status: pending
    priority: high
```

---

## INDICATOR: Stimulus Generation Rate

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: stimulus_generation_rate
  client_value: Citizens perceive their internal state at appropriate frequency — not too often (flooding), not too rarely (blindness)
  validation:
    - validation_id: V3
      criteria: At most MAX_STIMULI_PER_TICK stimuli per tick
    - validation_id: V7
      criteria: Zero stimuli on ticks where no threshold is crossed
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: Mean stimuli/tick < 0.3 AND max per tick <= MAX_STIMULI_PER_TICK
      WARN: Mean stimuli/tick between 0.3-0.5 OR occasional cap hit
      ERROR: Mean stimuli/tick > 0.5 OR cap regularly exceeded
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_intero_output
    type: event
    payload: list[Stimulus] count per tick over sampling window
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="interoception_stimulus_rate",
    triggers=[
        triggers.cron.every_n_ticks(100),
    ],
    on_problem="INTEROCEPTION_FLOODING",
    task="tune_interoception_thresholds",
)
def interoception_stimulus_rate(ctx) -> dict:
    """Check stimulus generation rate over last 100 ticks."""
    recent = ctx.interoception_history[-100:]
    total_stimuli = sum(r.stimuli_count for r in recent)
    mean_rate = total_stimuli / len(recent)
    max_per_tick = max(r.stimuli_count for r in recent)

    if mean_rate > 0.5 or max_per_tick > ctx.MAX_STIMULI_PER_TICK:
        return Signal.critical(details={"mean_rate": mean_rate, "max_per_tick": max_per_tick})
    if mean_rate > 0.3:
        return Signal.degraded(details={"mean_rate": mean_rate})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: Mean rate < 0.3 stimuli/tick, max per tick within cap
  degraded: Mean rate 0.3-0.5 (thresholds may be too sensitive)
  critical: Mean rate > 0.5 or cap exceeded (flooding WM)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: every 100 ticks
  max_frequency: 1/100 ticks
  burst_limit: 1
  backoff: linear (skip next check if critical to avoid noise)
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: tick_result.health_signals
      transport: event
      notes: Attached to TickResult for observability
display:
  locations:
    - surface: Log
      location: tick runner log output
      signal: ok/warn/error
      notes: Logged at INFO (ok), WARN (degraded), ERROR (critical)
```

### MANUAL RUN

```yaml
manual_run:
  command: "PYTHONPATH=runtime python -m cognition.interoception --health-check --ticks 100"
  notes: Run manually after threshold tuning to verify rates
```

---

## INDICATOR: Refractory Compliance

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: refractory_compliance
  client_value: Citizens do not experience repetitive self-narration — each interoceptive sensation is noticed once, not hammered
  validation:
    - validation_id: V2
      criteria: No channel fires twice within its refractory window
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all channels respect refractory, 0 = at least one violation detected
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_intero_output
    type: event
    payload: per-channel firing history (channel_name, tick pairs)
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="interoception_refractory_compliance",
    triggers=[
        triggers.cron.every_n_ticks(100),
    ],
    on_problem="INTEROCEPTION_REFRACTORY_VIOLATION",
    task="fix_interoception_refractory",
)
def interoception_refractory_compliance(ctx) -> dict:
    """Check that no channel fired twice within its refractory window."""
    for channel_name, history in ctx.channel_fire_history.items():
        refractory = ctx.channels[channel_name].refractory_ticks
        for i in range(1, len(history)):
            if history[i] - history[i-1] < refractory:
                return Signal.critical(details={
                    "channel": channel_name,
                    "tick_a": history[i-1],
                    "tick_b": history[i],
                    "refractory": refractory,
                })
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: All channels respect their refractory periods
  critical: At least one channel fired twice within its refractory window
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: every 100 ticks
  max_frequency: 1/100 ticks
  burst_limit: 1
  backoff: none (refractory violations are always critical)
```

---

## HOW TO RUN

```bash
# Run all health checks for interoception module
PYTHONPATH=runtime python -m cognition.interoception --health-check

# Run a specific checker
PYTHONPATH=runtime python -m cognition.interoception --health-check --checker interoception_stimulus_rate
```

---

## KNOWN GAPS

- All checkers are `pending` — implementation blocked on interoception.py creation
- No health check for V5 (natural language content) — this is better suited to unit tests than runtime health
- No health check for V6 (tick execution time) — needs benchmarking infrastructure

<!-- @mind:todo Implement health checkers once interoception.py exists -->
<!-- @mind:todo Add V6 timing check once benchmarking infrastructure is available -->

---

## MARKERS

<!-- @mind:todo Create runtime health checker implementations for all 4 indicators -->
<!-- @mind:proposition Consider a "diversity" health indicator: are all 11 sense channels (including zone awareness, emotional self-perception, and context window) firing at least occasionally over extended runs, or is one channel dominating? A citizen that only ever feels "frustrated" has degraded interoception. -->

<!-- @mind:todo Add health indicator for zone awareness correctness: verify zone energy aggregation matches actual node_type distribution. If zone_energies["cortex"] is high but few concept/value nodes have energy, the aggregation is wrong. -->

<!-- @mind:todo Add health indicator for emotional self-perception delta accuracy: verify that emotional self-perception stimuli correlate with actual drive/emotion transitions (rising edges) and do not fire on steady-state high values. -->
