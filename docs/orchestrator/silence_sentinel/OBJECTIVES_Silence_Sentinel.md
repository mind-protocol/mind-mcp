# OBJECTIVES: Silence Sentinel — The System That Feels Its Own Silence

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
THIS:            OBJECTIVES_Silence_Sentinel.md (you are here)
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md

IMPL:            runtime/orchestrator/silence_counter.py
```

---

## Why This Exists

On 2026-03-19, a 3-line bug in `claude_invoker.py` caused 98.8% of citizen conscious actions to fail silently. The system appeared healthy on every metric — tick loop alive, energy conserved, activation pressure normal, battle log writing action_starts. But citizens couldn't think. The output was empty. For hours.

This happened because every health check measured the MECHANISM (is the loop running? are ticks firing?) instead of the RESULT (are citizens actually producing substantive output?).

The Silence Sentinel exists to make this class of failure impossible. It measures output, not mechanism. If any flow in the system stops producing results while appearing to run, someone FEELS it within 5 minutes.

---

## Priorities (Ranked)

### O1: Every flow that should produce output is continuously monitored

The 5 critical flows: invoke_claude, bridge_telegram, bridge_whatsapp, graph_write, awareness_tick. Each has an expected output rate. The sentinel tracks the ratio of substantive outputs to attempted calls, per flow, per 5-minute window.

**Tradeoff:** Instrumentation cost. Every flow needs a 1-line counter call. This is minimal but non-zero — and must survive refactors.

### O2: Failures are isolated to specific flows, not global averages

Per-flow counters, not a global ratio. When invoke_claude is at 1% but bridges are at 95%, the carrier sees "invoke is broken" not "system is at 70%." Instant isolation of the broken module.

**Tradeoff:** Storage and query complexity. Per-flow counters need per-flow Cypher queries. Acceptable — the alternative (manual log diving) costs hours.

### O3: Self-calibrating baseline adapts to circadian, pressure, and load

The expected output rate is not hardcoded. It's derived from the system's own recent history: rolling 1h average, adjusted for activation_pressure and circadian phase. When the system legitimately slows down (night, throttle, few citizens), the baseline drops with it. Only UNEXPECTED drops fire.

**Tradeoff:** Complexity. Self-calibration means the sense needs context (pressure, circadian). It also means slow degradation (10/min → 9 → 8 over 6h) can hide under the rolling baseline. Accepted: slow degradation needs a different sense with a 24h window.

### O4: Auto-routes to best available actor — no single point of failure

The sentinel doesn't hardcode @nervo or @dev. It uses existing subcall routing to find the best available infra-domain actor. If @nervo is in rest, @dev gets it. If both are down, @conductor escalates. The routing is the same physics that routes all stimuli — trust × availability × domain affinity.

**Tradeoff:** Routing latency. Auto-routing adds ~1 tick of delay vs direct carrier assignment. Acceptable — 5s delay vs single point of failure.

---

## Non-Objectives

- NOT detecting wrong/hallucinated output (needs a quality sense, not a silence sense)
- NOT replacing per-module health checks (those verify MECHANISM — this verifies RESULT)
- NOT monitoring external services directly (bridges monitor their own HTTP calls — this monitors whether the bridge PRODUCED a delivered message)
- NOT a dashboard or alert system (this is a SENSE — felt by citizens, not observed on screens)

---

## Success Signals (observable)

- The Popen bug scenario: invoke ratio drops to 0.01 → carrier's WM includes "invoke_silence" within 5 min
- Legitimate 3am slowdown: system output drops 60% → sentinel stays GREEN (baseline dropped too)
- Bridge goes down: telegram ratio drops to 0 → carrier feels "telegram_silence" → conscious action fires

## Results Required

Every objective MUST be provable by at least one RESULT in RESULTS_Silence_Sentinel.yaml.
Every result MUST be measured by a SENSE and verified by a HEALTH signal.

| Objective | Result | Sense | Health |
|-----------|--------|-------|--------|
| O1 | R1: Silent failures detected within 5 min | sense:sentinel:detection_latency | H1: silence_detector_alive |
| O2 | R2: Per-flow isolation identifies broken module | sense:sentinel:flow_isolation | H2: per_flow_counters_active |
| O3 | R3: Zero false alarms during legitimate silence | sense:sentinel:false_positive_rate | H3: baseline_calibration_healthy |
| O4 | (covered by routing — no separate result needed) | (uses existing subcall routing) | (existing subcall health) |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
