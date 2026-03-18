# Stimulus Router — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers the stimulus router module (stimulus_router.py + feedback_injector.py) and its runtime verification. It reduces the risk of silent failures in the sensory gateway: events being dropped, feedback loops forming, or dedup misbehaving under real traffic patterns that unit tests cannot replicate.

The stimulus router is verified at runtime because its critical properties (loop termination, dedup effectiveness, energy budget distribution) depend on real event patterns, timing, and citizen-specific state that emerge only in production.

This file will NOT verify: Law 1 energy injection (covered by l1_physics HEALTH), LLM invocation quality, bridge protocol handling.

---

## WHY THIS PATTERN

Tests verify that route() produces correct output for known inputs. But the router's critical failure modes are emergent:
- A feedback loop that only manifests under specific timing conditions (refractory edge cases)
- Dedup effectiveness degrading as the window fills with similar-but-not-identical hashes
- Energy budget distributions drifting as metabolism modulation is introduced

Docking-based runtime checks catch these without modifying the router code. Throttling keeps verification cheap (the router processes hundreds of events per minute; health checks sample at 1/min).

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
PATTERNS:        ./PATTERNS_Stimulus_Router.md
BEHAVIORS:       ./BEHAVIORS_Stimulus_Router.md
ALGORITHM:       ./ALGORITHM_Stimulus_Router.md
VALIDATION:      ./VALIDATION_Stimulus_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stimulus_Router.md
THIS:            HEALTH_Stimulus_Router.md (you are here)
SYNC:            ./SYNC_Stimulus_Router.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code will live in runtime:

```yaml
implements:
  runtime: runtime/checks.py       # Python code implementing these checks
  decorator: @check                # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: external_event_routing
    purpose: Verify external events produce stimuli — if this fails, citizens are deaf
    triggers:
      - type: event
        source: runtime/orchestrator/dispatcher.py:_inject_stimulus
        notes: Bridge message received from Telegram/Discord/WhatsApp/MCP
    frequency:
      expected_rate: 5-20/min per citizen
      peak_rate: 100/min (group chat or bridge flood)
      burst_behavior: All events queued and processed sequentially. Dedup catches duplicates. No backpressure mechanism.
    risks:
      - V1 violation: external event silently dropped
      - V4 violation: dedup false positive rejects a unique event
    notes: This is the most frequently exercised flow. Health must sample, not instrument every call.

  - flow_id: feedback_loop
    purpose: Verify LLM output correctly re-enters the graph — if this fails, citizens lose self-awareness
    triggers:
      - type: event
        source: runtime/orchestrator/dispatcher.py (post Claude session)
        notes: inject_post_action_feedback called after each LLM invocation
    frequency:
      expected_rate: 1-5/min per citizen
      peak_rate: 15/min (rapid conversation)
      burst_behavior: Each feedback call is synchronous. Anti-loop gate prevents accumulation.
    risks:
      - V2/V3 violation: self-stimulus energy not decreasing or loop not terminating
      - V7 violation: record_action() not called, disabling refractory period
    notes: Lower frequency than external routing, but higher criticality per event.
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Faithful signal transduction | external_event_pass_rate | Confirms external events reach the tick loop |
| O2: Anti-loop integrity | self_stimulus_attenuation, feedback_loop_termination | Confirms self-stimuli attenuate and loops terminate |
| O4: Dedup fidelity | dedup_rejection_rate | Confirms dedup catches duplicates without false positives |
| O5: Metabolism readiness | energy_budget_distribution | Confirms energy budgets are being assigned per classification |

```yaml
health_indicators:
  - name: external_event_pass_rate
    flow_id: external_event_routing
    priority: high
    rationale: If external events are being dropped, the citizen is effectively deaf. This is the most critical indicator.

  - name: self_stimulus_attenuation
    flow_id: feedback_loop
    priority: high
    rationale: If self-stimulus energy is not decreasing geometrically, feedback loops will form, burning compute and producing incoherent behavior.

  - name: feedback_loop_termination
    flow_id: feedback_loop
    priority: high
    rationale: Verifies that no citizen enters an unbounded self-stimulus chain. Complements self_stimulus_attenuation by checking the termination property directly.

  - name: dedup_rejection_rate
    flow_id: external_event_routing
    priority: med
    rationale: Monitors the ratio of dedup rejections to total events. Too high suggests false positives (unique events rejected). Too low during known duplicate scenarios suggests dedup failure.

  - name: energy_budget_distribution
    flow_id: external_event_routing
    priority: med
    rationale: Verifies that social events get 1.2x and failures get 0.8x energy. Baseline for metabolism modulation testing.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/checks.py
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-18T00:00:00Z
    source: stimulus_router_health
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_external_event_pass_rate
    purpose: Verify V1 — external events produce stimuli at expected rates
    status: pending
    priority: high

  - name: check_self_stimulus_attenuation
    purpose: Verify V2/V3 — self-stimulus energy is bounded and decreasing
    status: pending
    priority: high

  - name: check_dedup_effectiveness
    purpose: Verify V4 — duplicate content does not inject twice
    status: pending
    priority: med

  - name: check_social_classification
    purpose: Verify V5 — social sources consistently classified
    status: pending
    priority: med
```

---

## INDICATOR: external_event_pass_rate

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: external_event_pass_rate
  client_value: Citizens must respond to messages. If external events are dropped, users see silence.
  validation:
    - validation_id: V1
      criteria: Every IncomingEvent with source != "self" and unique content produces a non-None Stimulus
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Ratio of external events that produced non-None Stimulus to total external events in sample window. 1.0 = all passed. Below 0.95 = degraded. Below 0.80 = critical.
  aggregation:
    method: Rolling average over 5-minute windows
    display: float_0_1 surfaced in health dashboard
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_route_output
    type: event
    payload: IncomingEvent source + route() return value (Stimulus or None)
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="external_event_pass_rate",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="STIMULUS_ROUTER_DROP",
    task="investigate_event_drops",
)
def check_external_event_pass_rate(ctx) -> dict:
    """Verify external events produce stimuli at expected rates."""
    # Sample: count external events vs stimuli produced in last 5 minutes
    # from router instrumentation counters (to be added)
    total_external = ctx.get_counter("stimulus_router.external_events")
    total_stimuli = ctx.get_counter("stimulus_router.external_stimuli_produced")
    if total_external == 0:
        return Signal.healthy(details="No external events in window")
    rate = total_stimuli / total_external
    if rate >= 0.95:
        return Signal.healthy(details=f"Pass rate: {rate:.2%}")
    if rate >= 0.80:
        return Signal.degraded(details=f"Pass rate dropped: {rate:.2%}")
    return Signal.critical(details=f"Pass rate critical: {rate:.2%}")
```

### SIGNALS

```yaml
signals:
  healthy: Pass rate >= 95% of external events produce stimuli
  degraded: Pass rate between 80-95% (some events being incorrectly filtered)
  critical: Pass rate below 80% (citizen is becoming deaf)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron every 5 minutes
  max_frequency: 1/5min
  burst_limit: 1
  backoff: Suppress repeated critical alerts for 15 minutes after first alert
```

---

## INDICATOR: self_stimulus_attenuation

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: self_stimulus_attenuation
  client_value: Citizens must not enter infinite self-talk loops that burn compute and produce gibberish.
  validation:
    - validation_id: V2
      criteria: Consecutive self-stimuli have strictly decreasing energy
    - validation_id: V3
      criteria: Self-stimulus chains terminate (energy < 0.01 or duplicate rejected)
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK = no citizen has self-stimulus chain > 10 with non-trivial energy. WARN = one citizen at chain length 10-15. ERROR = any citizen at chain length > 15.
  aggregation:
    method: Worst-case across all active citizens
    display: enum surfaced in health dashboard
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_feedback_entry
    type: event
    payload: router.anti_loop._self_stimulus_count per citizen
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="self_stimulus_attenuation",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="STIMULUS_ROUTER_LOOP",
    task="investigate_feedback_loop",
)
def check_self_stimulus_attenuation(ctx) -> dict:
    """Verify no citizen is in a self-stimulus feedback loop."""
    # Inspect all active routers' anti-loop state
    max_chain = 0
    worst_citizen = None
    for handle, router in ctx.get_citizen_routers().items():
        chain_len = router.anti_loop._self_stimulus_count
        if chain_len > max_chain:
            max_chain = chain_len
            worst_citizen = handle
    if max_chain <= 10:
        return Signal.healthy(details=f"Max self-chain: {max_chain}")
    if max_chain <= 15:
        return Signal.degraded(details=f"Citizen {worst_citizen} at chain {max_chain}")
    return Signal.critical(details=f"Citizen {worst_citizen} stuck in loop at chain {max_chain}")
```

### SIGNALS

```yaml
signals:
  healthy: No citizen has a self-stimulus chain longer than 10
  degraded: A citizen has chain length 10-15 (attenuation working but slow)
  critical: A citizen has chain length > 15 (possible loop, investigate)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron every 5 minutes
  max_frequency: 1/5min
  burst_limit: 1
  backoff: Escalate after 2 consecutive critical readings
```

---

## HOW TO RUN

```bash
# Run all health checks for stimulus router
python -m runtime.checks --module stimulus_router

# Run a specific checker
python -m runtime.checks --check check_external_event_pass_rate
```

---

## KNOWN GAPS

- No instrumentation counters exist yet on StimulusRouter.route() — the check_external_event_pass_rate checker needs counter hooks added to the implementation.
- The self_stimulus_attenuation checker accesses private state (router.anti_loop._self_stimulus_count). A public accessor method should be added.
- No checker yet for V6 (per-citizen state isolation) — this is better verified by unit tests.
- No checker yet for V7 (feedback injector calling record_action) — needs call-trace instrumentation.

<!-- @mind:todo Add counter instrumentation to StimulusRouter.route() for health check support -->
<!-- @mind:todo Add public accessor for anti-loop chain length on StimulusRouter -->
<!-- @mind:proposition Consider embedding-based novelty detection as metabolism feature lands -->
