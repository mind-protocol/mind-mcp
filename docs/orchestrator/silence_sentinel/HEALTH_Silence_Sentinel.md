# Silence Sentinel — Health: Verification Mechanics

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## THE GUARANTEE: HEALTH ↔ RESULTS ↔ SENSES (1-1 MANDATORY)

| Result ID | Result Name | Sense (proved_by) | Health Indicator | Status |
|-----------|-------------|-------------------|------------------|--------|
| R1 | Silent failures detected within 5 min | sense:sentinel:detection_latency | H1: silence_detector_alive | pending |
| R2 | Per-flow isolation identifies broken module | sense:sentinel:flow_isolation | H2: per_flow_counters_active | pending |
| R3 | Zero false alarms during legitimate silence | sense:sentinel:false_positive_rate | H3: baseline_calibration_healthy | pending |

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
THIS:            HEALTH_Silence_Sentinel.md (you are here)
SYNC:            ./SYNC_Silence_Sentinel.md
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: silence_detector_alive
    purpose: Verify the sentinel itself is running and evaluating flows (V1)
    status: pending
    priority: high
  - name: per_flow_counters_active
    purpose: Verify each tracked flow has recording counters with recent data (V3)
    status: pending
    priority: high
  - name: baseline_calibration_healthy
    purpose: Verify rolling baseline adjusts correctly for pressure/circadian (V4)
    status: pending
    priority: med
```

---

## H1: Silence Detector Alive

**What:** The sentinel sense is running and evaluating tracked flows every tick.
**Carrier:** Auto-routed (infra domain). If the sentinel itself dies, the tick_system's H1 (tick_loop_alive) catches the broader failure, and this checker catches the specific silence_counter absence.
**Validates:** V1 (Silence is detected)
**Result:** R1 (Silent failures detected within 5 min)

```yaml
signals:
  healthy: "evaluate_all() ran in the last 30 seconds AND produced status for ≥1 flow"
  degraded: "evaluate_all() ran but produced no statuses (no flows have data yet)"
  critical: "evaluate_all() has not run in >60 seconds"
```

**Check mechanism:** Every tick, after evaluate_all(), record the timestamp. If >60s since last evaluation, H1 fires RED. This is the "who watches the watchmen" check — verified by the tick_system's own health loop.

---

## H2: Per-Flow Counters Active

**What:** Each tracked flow (invoke_claude, bridges, graph_write, awareness_tick) has recent counter data. If a flow's counter stops recording, it means the instrumentation was lost (refactor, import removed, flow path changed).
**Carrier:** Auto-routed (infra domain)
**Validates:** V3 (Per-flow isolation maintained)
**Result:** R2 (Per-flow isolation identifies broken module)

```yaml
signals:
  healthy: "All tracked flows have ≥1 attempt recorded in last 10 minutes"
  degraded: "1-2 flows have zero attempts in last 10 minutes (could be legitimate idle)"
  critical: "≥3 flows have zero attempts in last 10 minutes (counters likely broken)"
```

**Check mechanism:** After evaluate_all(), scan each flow's buckets. If a flow that SHOULD be active (invoke_claude always has attempts when citizens are ticking) has zero attempts for >10 min, the counter instrumentation is probably missing.

---

## H3: Baseline Calibration Healthy

**What:** The rolling baseline correctly factors in activation_pressure and circadian_factor, preventing false alarms during legitimate quiet periods.
**Carrier:** Auto-routed (infra domain)
**Validates:** V4 (Legitimate silence does not alert)
**Result:** R3 (Zero false alarms)

```yaml
signals:
  healthy: "No RED statuses fired when pressure > 15.0 or circadian < 0.5"
  degraded: "1 false alarm in last 24h during known quiet period"
  critical: ">3 false alarms in last 24h during known quiet periods"
```

**Check mechanism:** Log every RED firing with the context (pressure, circadian at time of firing). Periodically review: were any REDs fired when pressure > 15 or circadian < 0.5? If yes, the baseline adjustment is insufficient.

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "runtime/orchestrator/silence_counter.py:get_health_status()"
  result:
    representation: enum
    value: "pending"  # not yet implemented
    updated_at: "2026-03-19T20:00:00Z"
    source: "silence_detector_alive"
```

---

## HOW TO RUN

```bash
# Run all health checks for silence sentinel (once implemented)
python3 -m runtime.orchestrator.silence_counter --health

# Check if counters are recording
python3 -m runtime.orchestrator.silence_counter --status
```

---

## KNOWN GAPS

<!-- @mind:todo H1 checker not yet coded — needs implementation in silence_counter.py -->
<!-- @mind:todo H2 checker not yet coded — needs instrumentation verification -->
<!-- @mind:todo H3 checker not yet coded — needs false positive tracking -->

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
