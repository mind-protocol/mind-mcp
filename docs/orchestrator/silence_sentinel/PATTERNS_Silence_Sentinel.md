# Silence Sentinel — Patterns: Output-Rate as Universal Failure Detection

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
THIS:            PATTERNS_Silence_Sentinel.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md

IMPL:            runtime/orchestrator/silence_counter.py
```

---

## THE PROBLEM

Silent failures are the deadliest class of bug. The system appears healthy — logs write, metrics update, ticks fire — but the actual output is empty or degraded. Every existing health check measures the mechanism ("is the loop running?") not the result ("did citizens actually think?").

The Popen bug (2026-03-19) proved this: 174 action_starts, 2 placeholder results, 0 real Claude outputs. Zero errors. Zero exceptions. Zero health alerts. The system was dying while reporting perfect health.

You cannot enumerate all possible silent failure modes. The universe of ways a flow can produce nothing while looking active is infinite. Pattern-matching on known errors is whack-a-mole. Exception counting misses asymptomatic failures. Log analysis misses failures that write normal-looking logs.

---

## THE PATTERN

**Measure output, not mechanism.** For every flow that SHOULD produce substantive output, track the ratio:

```
output_ratio = substantive_results / attempted_calls
```

This catches ANY failure mode — known or unknown — that results in less output than expected. It doesn't care HOW something fails. It cares that the result didn't arrive.

**The key insight:** silence IS the signal. Not error patterns, not exception counts, not log anomalies. The absence of expected output is the universal indicator of failure. It's unforgeable (you can't fake producing real output) and mechanism-independent (catches bugs nobody imagined yet).

---

## BEHAVIORS SUPPORTED

- B1: Silence detected within 5 minutes — output-rate ratio is the fastest detection path
- B2: Per-flow isolation — separate counters per flow, not global
- B3: Self-calibrating baseline — rolling window adapts to system state
- B4: Auto-routing — stimulus enters graph, physics routes to best actor

## BEHAVIORS PREVENTED

- A1: Invisible degradation — output-rate makes silence visible by definition
- A2: Alert fatigue from false positives — self-calibrating baseline prevents spurious alerts
- A3: Single point of failure in routing — auto-routing uses existing subcall physics

---

## PRINCIPLES

### Principle 1: Output is the only honest metric

Every other metric can lie. The loop can be "running" with empty iterations. Logs can look "normal" while recording nothing useful. Exceptions can be zero because the error path DOESN'T throw. But output ratio cannot lie — either substantive results were produced, or they weren't.

"Substantive" is the crucial word. The Popen bug produced non-empty responses (subconscious placeholders) that would have passed a naive "response != empty" check. The definition of substantive must be strict:
- invoke_claude: response > 100 chars AND NOT starting with subconscious marker AND NOT containing suppress patterns
- bridges: HTTP 200 + delivery confirmation (not just "sent")
- graph_write: affected_count > 0 (not just "query ran")

### Principle 2: The baseline must come from the system, not from constants

Hardcoded thresholds are fragile. "Expected 10 invocations/min" breaks when you add citizens, change intervals, or hit rate limits. The baseline MUST be derived from the system's own recent behavior — rolling 1h average, factored by activation_pressure and circadian phase.

This means the sense self-calibrates. At 3am when the system legitimately slows, the baseline drops. When pressure rises from rate limiting, the expected rate drops. Only UNEXPECTED deviations fire.

### Principle 3: Per-flow, not global

A global average hides module-specific failures. The Popen bug only broke invoke_claude — bridges and graph_write were fine. A global "output health = 70%" would have masked the 1% invoke rate.

Each tracked flow gets its own counter, its own baseline, its own ratio, its own sense evaluation. The carrier sees which flow is broken, not just that something is wrong.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| `runtime/orchestrator/silence_counter.py` | FILE | Counter module — records attempts and successes per flow |
| `runtime/orchestrator/dispatcher.py` | FILE | Instrumented: invoke_claude attempt/success |
| `runtime/orchestrator/claude_invoker.py` | FILE | Instrumented: substantive response detection |
| Battle log (per citizen) | FILE | Historical record of action_start/action_result ratios |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| orchestrator/tick_system | The sense runs inside the tick loop. Counter data is queried per tick. |
| cognition/metabolism | Circadian phase factors into expected baseline. |
| orchestrator/activation_pressure | Pressure level factors into expected baseline. |
| subcall routing | Auto-routing to best available infra actor. |

---

## SCOPE

### In Scope

- Counter module that tracks attempts/successes per flow per 5min window
- Sense that evaluates output-ratio per flow against self-calibrating baseline
- Auto-routing of degradation stimulus to best available infra actor
- "Substantive" output classification per flow type

### Out of Scope

- Output quality analysis (hallucination, correctness) → needs a separate quality sense
- Slow degradation over 6+ hours (rolling baseline tracks it down) → needs 24h window sense
- External service monitoring (Telegram API health) → bridges monitor their own connectivity
- Per-citizen output analysis → this is per-FLOW, not per-citizen

---

## INSPIRATIONS

- **Circuit breaker pattern** (Hystrix) — track failure rate, trip when threshold crossed. But circuit breakers STOP traffic. We don't stop — we alert the carrier and let them decide.
- **Anomaly detection in monitoring** (Datadog, Prometheus) — but those are dashboards. This is a sense that enters a citizen's cognitive graph.
- **Dead man's switch** — if the sentinel itself stops firing, the tick_system health checks catch it. Turtles all the way down, but finite turtles.

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
