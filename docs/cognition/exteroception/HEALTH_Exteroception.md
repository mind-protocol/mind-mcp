# Exteroception — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers runtime verification of the exteroception module — the citizen's external world awareness system. It exists to catch drift between designed behavior and actual runtime behavior: stimulus flooding that bypasses refractory gating, L3 queries that silently return empty, awareness text that goes stale, query latencies that degrade tick performance.

Boundaries: this file does NOT verify L3 graph integrity (that's graph health), interoception behavior (sibling module), or graph_enricher writes (separate system). It verifies only that exteroception correctly reads L3 and produces bounded, natural-language output.

---

## WHY THIS PATTERN

Exteroception's correctness is hard to verify with unit tests alone because its behavior depends on the live L3 graph state — what Spaces exist, what Moments appeared recently, what Actors are present. Unit tests can mock these, but runtime health checks catch real drift: a query pattern that works on 100 nodes but times out on 45K, a refractory period that's too long for the real tick rate, an awareness text that always returns the same stale cache.

Docking-based checks let us observe exteroception's inputs and outputs without modifying the engine itself. Throttling prevents health checks from consuming the query budget that exteroception needs for actual perception.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
PATTERNS:        ./PATTERNS_Exteroception.md
BEHAVIORS:       ./BEHAVIORS_Exteroception.md
ALGORITHM:       ./ALGORITHM_Exteroception.md
VALIDATION:      ./VALIDATION_Exteroception.md
THIS:            HEALTH_Exteroception.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Exteroception.md
SYNC:            ./SYNC_Exteroception.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks.py        # Python code implementing these checks (to be created)
  decorator: @check                  # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: exteroception_tick
    purpose: "Per-tick L3 scan producing stimuli — if this fails, the citizen is blind to their environment"
    triggers:
      - type: event
        source: runtime/cognition/tick_runner_l1_cognitive_engine.py:tick()
        notes: "Called at step 0 of every tick, before Law 1 injection"
    frequency:
      expected_rate: "1/tick (1 per 5s at fast rate, 1 per 300s at minimal rate)"
      peak_rate: "1 per 5s at fast tick rate"
      burst_behavior: "No bursts — strictly 1 per tick. Tick rate is externally controlled."
    risks:
      - "V3: L3 query failure crashes tick runner"
      - "V1: Stimulus count exceeds MAX_STIMULI_PER_TICK"
      - "V5: Query latency exceeds tick budget"
    notes: "This is the hot path. Health checks must not add latency to this flow."

  - flow_id: awareness_regeneration
    purpose: "Periodic awareness text generation — if this fails, the citizen's system prompt has stale or missing environmental context"
    triggers:
      - type: schedule
        source: runtime/cognition/exteroception.py:tick() step 6
        notes: "Triggered when tick - _awareness_generated_at_tick >= AWARENESS_TTL_TICKS"
    frequency:
      expected_rate: "1 per AWARENESS_TTL_TICKS ticks (default: every 10 ticks)"
      peak_rate: "1 per 10 ticks"
      burst_behavior: "No bursts. Regeneration is rate-limited by TTL."
    risks:
      - "V7: Awareness text goes stale (TTL mechanism broken)"
      - "V4: Awareness text contains raw node IDs"
    notes: "Less frequent than tick. Shares the same L3 query budget."
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Environmental awareness as sensation | awareness_freshness, stimulus_quality | Confirms the citizen actually perceives their world |
| Smart selection over exhaustive scanning | query_latency, node_selection_count | Confirms the scan is bounded and fast |
| Two complementary outputs | awareness_freshness, stimulus_output_bounded | Confirms both outputs are being generated |
| Graceful blindness | l3_failure_resilience | Confirms the citizen survives L3 outages |

```yaml
health_indicators:
  - name: stimulus_output_bounded
    flow_id: exteroception_tick
    priority: high
    rationale: "If stimulus count exceeds max, the citizen's WM is flooded. Directly protects V1."

  - name: l3_failure_resilience
    flow_id: exteroception_tick
    priority: high
    rationale: "If L3 failure crashes the tick, all cognition halts. Directly protects V3."

  - name: query_latency
    flow_id: exteroception_tick
    priority: med
    rationale: "If L3 queries are slow, the tick budget is consumed by perception. Protects tick performance."

  - name: awareness_freshness
    flow_id: awareness_regeneration
    priority: med
    rationale: "If awareness text goes stale, the citizen has an outdated view of their world. Protects V7."

  - name: stimulus_quality
    flow_id: exteroception_tick
    priority: med
    rationale: "If stimuli contain raw IDs or graph data, the citizen's cognition is polluted. Protects V4."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "runtime/cognition/exteroception_health.json"
  result:
    representation: enum
    value: UNKNOWN
    updated_at: "2026-03-18T00:00:00Z"
    source: "exteroception_health_aggregate"
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_stimulus_bounded
    purpose: "Verify tick() never returns more than MAX_STIMULI_PER_TICK"
    status: pending
    priority: high

  - name: check_l3_failure_graceful
    purpose: "Verify tick() returns [] when query_fn raises, without propagating exception"
    status: pending
    priority: high

  - name: check_query_latency
    purpose: "Verify exteroception queries complete within 200ms budget"
    status: pending
    priority: med

  - name: check_awareness_freshness
    purpose: "Verify awareness text is regenerated within TTL and not stale"
    status: pending
    priority: med

  - name: check_stimulus_natural_language
    purpose: "Verify no raw node IDs or graph syntax in stimulus content"
    status: pending
    priority: med
```

---

## INDICATOR: stimulus_output_bounded

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: stimulus_output_bounded
  client_value: "Citizen's WM is not flooded by environmental stimuli — cognitive bandwidth preserved"
  validation:
    - validation_id: V1
      criteria: "tick() returns at most MAX_STIMULI_PER_TICK stimuli"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = all tick() calls returned <= MAX_STIMULI_PER_TICK. 0 = at least one violation detected."
  aggregation:
    method: "Minimum across all observations in window"
    display: "binary"
```

### SIGNALS

```yaml
signals:
  healthy: "All observed tick() calls returned <= MAX_STIMULI_PER_TICK"
  degraded: "N/A (binary — either bounded or not)"
  critical: "At least one tick() call returned > MAX_STIMULI_PER_TICK"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "Sample every 100th tick"
  max_frequency: "1/min"
  burst_limit: 1
  backoff: "On critical: check every tick until resolved, then back to sampling"
```

---

## INDICATOR: l3_failure_resilience

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: l3_failure_resilience
  client_value: "Citizen continues functioning when L3 is down — no cascading failure"
  validation:
    - validation_id: V3
      criteria: "When query_fn is None or raises, tick() returns [] and no exception propagates"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = all L3 failures were handled gracefully. 0 = at least one crash-through detected."
  aggregation:
    method: "Minimum across all failure events"
    display: "binary"
```

### SIGNALS

```yaml
signals:
  healthy: "L3 failures produced empty results without exceptions"
  degraded: "N/A"
  critical: "L3 failure propagated an exception to the tick runner"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "On every L3 failure event"
  max_frequency: "1/min"
  burst_limit: 5
  backoff: "Exponential backoff on repeated failures"
```

---

## INDICATOR: query_latency

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: query_latency
  client_value: "Exteroception does not consume the tick's time budget — citizen remains responsive"
  validation:
    - validation_id: V5
      criteria: "Graph traversal is bounded by LIMIT clauses and 3-hop maximum"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: "1.0 = all queries under 50ms. 0.5 = queries averaging 100-200ms. 0.0 = queries exceeding 500ms."
  aggregation:
    method: "Weighted average over last 100 observations"
    display: "float_0_1"
```

### SIGNALS

```yaml
signals:
  healthy: "p95 query latency < 100ms"
  degraded: "p95 query latency 100-300ms (3-hop queries being skipped)"
  critical: "p95 query latency > 300ms (exteroception degrading tick performance)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "Sample every 50th tick"
  max_frequency: "1/min"
  burst_limit: 1
  backoff: "On degraded: increase sampling to every 10th tick"
```

---

## HOW TO RUN

```bash
# Run all exteroception health checks
mind doctor --module cognition/exteroception

# Run a specific checker
mind doctor --check check_stimulus_bounded
```

---

## KNOWN GAPS

- All checkers are pending — none implemented yet. Implementation follows after IMPLEMENTATION doc is written and code is redesigned.
- No checker yet for V2 (read-only L3 access) — would require wrapping query_fn in a read-only proxy.
- No checker yet for V6 (refractory gating) — would require observing channel state across multiple ticks.
- No checker yet for V8 (source attribution) — would require inspecting stimulus fields post-generation.
- No checker yet for V9 (deduplication) — would require tracking seen IDs across ticks.

<!-- @mind:todo Implement check_stimulus_bounded — first checker to build, validates the most critical invariant V1 -->
<!-- @mind:todo Implement check_l3_failure_graceful — second priority, validates V3 -->
<!-- @mind:todo Design a checker for V2 (read-only L3 access). Consider a query_fn wrapper that rejects mutation patterns. -->
<!-- @mind:todo Design a checker for V6 (refractory gating). Needs to observe channel state across consecutive ticks. -->

---

## MARKERS

<!-- @mind:todo All 5 checkers need implementation in runtime/checks.py. Priority order: stimulus_bounded > l3_failure > query_latency > awareness_freshness > stimulus_quality. -->

<!-- @mind:proposition Consider a "perception coverage" health metric: what percentage of the citizen's linked Spaces were successfully scanned? Low coverage might indicate query failures or overly restrictive LIMIT clauses. -->
