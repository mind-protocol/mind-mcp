# Custom Senses — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

| Use Health For | Why |
|----------------|-----|
| Sense loading from real graph topology | Requires actual Thing(type=sense) nodes with real YAML content, not mocks |
| Filter accuracy against live node data | Node energy/weight/friction values vary in production; fixtures cannot predict distribution |
| Channel gating interaction with built-in channels | Emergent behavior from priority competition; not deterministic in isolation |
| Sense adoption patterns across citizens | Requires real ->perceives_with-> link topology |

---

## PURPOSE OF THIS FILE

This HEALTH file covers the custom senses subsystem within exteroception.py — the mechanism by which citizens extend their perceptual field via graph-linked Thing(type=sense) nodes.

It exists because the value of custom senses depends on runtime properties that unit tests cannot fully verify: do senses actually load from real graph links? Do YAML filters match the right nodes given real energy/weight distributions? Do custom channels compete fairly with built-in channels under production conditions?

Boundaries: This file does NOT verify exteroception correctness generally (that belongs to a broader exteroception HEALTH file), graph query correctness (that belongs to runtime/physics/graph health), or YAML library correctness (that belongs to PyYAML upstream).

---

## WHY THIS PATTERN

Unit tests can verify that `_match_filters({"energy": 0.8}, {"energy": "> 0.5"})` returns True. But they cannot verify that real Thing(type=sense) nodes in production contain well-formed YAML that actually matches real nodes with meaningful energy levels. Those are runtime health properties that emerge from real citizen behavior and graph state.

Docking-based checks are the right tradeoff because they observe the loading and evaluation outputs without modifying exteroception.py code. Throttling is straightforward because senses are evaluated per tick and the tick rate is already governed by the physics loop.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Custom_Senses.md
PATTERNS:        ./PATTERNS_Custom_Senses.md
BEHAVIORS:       ./BEHAVIORS_Custom_Senses.md
ALGORITHM:       ./ALGORITHM_Custom_Senses.md
VALIDATION:      ./VALIDATION_Custom_Senses.md
IMPLEMENTATION:  ./IMPLEMENTATION_Custom_Senses.md
THIS:            HEALTH_Custom_Senses.md (you are here)
SYNC:            ./SYNC_Custom_Senses.md
```

---

## IMPLEMENTS

```yaml
implements:
  runtime: runtime/checks.py
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: sense_loading
    purpose: Populate custom sense cache from graph — failure means citizen has no custom perception
    triggers:
      - type: event
        source: runtime/cognition/exteroception.py:tick()
        notes: First tick triggers _load_custom_senses when _custom_senses_loaded is False
    frequency:
      expected_rate: 1/engine_lifetime per citizen
      peak_rate: 1/engine_lifetime (no burst possible — runs once then caches)
      burst_behavior: Not applicable — single execution with flag guard
    risks:
      - Malformed YAML silently skipped — citizen loses a sense without notification (V2)
      - Graph query returns empty due to link type mismatch — zero senses loaded silently
    notes: Loading is a cold-start operation. No repeated execution unless engine is recreated.

  - flow_id: sense_evaluation
    purpose: Produce stimulus candidates from custom senses — failure means senses are defined but inert
    triggers:
      - type: event
        source: runtime/cognition/exteroception.py:tick()
        notes: Called every tick after built-in channel processing
    frequency:
      expected_rate: 1/tick (tick rate varies, typically 1-10/min for active citizens)
      peak_rate: 10/min during high-activity periods
      burst_behavior: Bounded by tick rate — no independent burst mechanism
    risks:
      - All senses gated out by refractory periods — no candidates produced for extended period
      - Filter conditions too strict — senses load but never match any nodes (V5 related)
      - Graph queries slow under load — contributes to tick budget pressure (V4)
    notes: Evaluation cost scales linearly with sense count (max 10) and nodes per query (max 20)
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Citizen-defined perception | sense_loading_success, sense_evaluation_producing | If senses load but never produce stimuli, perception is not actually extended |
| O3: Two-tier complexity (YAML) | yaml_parse_success_rate | If most YAML definitions fail to parse, the low-barrier tier is not working |
| O4: Seamless integration | custom_gating_fairness | If custom senses dominate or are always gated out, integration has failed |

```yaml
health_indicators:
  - name: sense_loading_success
    flow_id: sense_loading
    priority: high
    rationale: If senses fail to load from graph links, the entire custom sense system is inert. Citizens lose their extended perception silently.

  - name: yaml_parse_success_rate
    flow_id: sense_loading
    priority: med
    rationale: If the majority of Thing(type=sense) nodes contain malformed YAML, the ease-of-creation promise is broken. Citizens are creating senses that do not work.

  - name: sense_evaluation_producing
    flow_id: sense_evaluation
    priority: high
    rationale: Senses that load but never produce candidates mean the filter/keyword conditions are too strict or the graph state does not contain matching nodes. The feature exists but provides no value.

  - name: custom_gating_fairness
    flow_id: sense_evaluation
    priority: med
    rationale: If custom sense candidates are always gated out by higher-priority built-in channels, citizens cannot effectively extend their perception. If custom senses always win, built-in perception is broken.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: health_log
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-18T00:00:00Z
    source: sense_loading_success
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_sense_loading
    purpose: Verify that Thing(type=sense) nodes linked via ->perceives_with-> are successfully loaded and parsed
    status: pending
    priority: high
  - name: check_sense_evaluation
    purpose: Verify that loaded senses produce candidates when matching nodes exist in the graph
    status: pending
    priority: high
  - name: check_yaml_quality
    purpose: Verify the parse success rate of Thing(type=sense) content fields across all citizens
    status: pending
    priority: med
  - name: check_gating_ratio
    purpose: Verify that custom sense candidates are neither always gated out nor always winning
    status: pending
    priority: med
```

---

## INDICATOR: sense_loading_success

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: sense_loading_success
  client_value: Citizens with ->perceives_with-> links should have active custom perception channels
  validation:
    - validation_id: V3
      criteria: Zero overhead without senses — loading query returns empty for zero-link citizens
    - validation_id: V4
      criteria: Sense count bounded — at most 10 loaded per citizen
    - validation_id: V2
      criteria: Malformed senses do not crash the tick — errors caught per-sense
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK = senses loaded matching link count; WARN = some senses failed to parse; ERROR = no senses loaded despite existing links
  aggregation:
    method: worst-of across checked citizens
    display: enum
```

### SIGNALS

```yaml
signals:
  healthy: All linked Thing(type=sense) nodes parsed successfully into _custom_senses
  degraded: Some linked senses failed YAML parsing (parse errors logged, partial loading)
  critical: No senses loaded despite existing ->perceives_with-> links (query failure or all YAML invalid)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: engine initialization (first tick)
  max_frequency: 1/hour (re-check periodically for engine restarts)
  burst_limit: 1
  backoff: not applicable — single check per engine lifecycle
```

---

## INDICATOR: sense_evaluation_producing

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: sense_evaluation_producing
  client_value: Citizens with active custom senses should receive stimuli from them when matching graph state exists
  validation:
    - validation_id: V1
      criteria: Custom stimuli enter standard gating
    - validation_id: V5
      criteria: One match per sense per tick
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Ratio of ticks where at least one custom candidate was produced (over last 100 ticks) for citizens with active senses
  aggregation:
    method: average across citizens with loaded senses
    display: float_0_1
```

### SIGNALS

```yaml
signals:
  healthy: ">= 0.1 candidate production rate (at least 1 in 10 ticks produces a custom candidate)"
  degraded: "< 0.1 but > 0 (senses fire very rarely — filters may be too strict)"
  critical: "0.0 over 100+ ticks (senses are loaded but never produce candidates)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: every 100 ticks (sampled, not every tick)
  max_frequency: 1/10min
  burst_limit: 1
  backoff: double interval on repeated degraded signals
```

---

## HOW TO RUN

```bash
# Run all health checks for custom senses
mind doctor --module cognition/custom_senses

# Run a specific checker
mind doctor --checker check_sense_loading
```

---

## KNOWN GAPS

- All four checkers are pending implementation — no runtime verification exists yet
- No health check for the _match_filters function against production node data distributions
- No monitoring of sense adoption rate (how many citizens use custom senses over time)

<!-- @mind:todo Implement check_sense_loading checker in runtime/checks.py -->
<!-- @mind:todo Implement check_sense_evaluation checker in runtime/checks.py -->
<!-- @mind:todo Implement check_yaml_quality checker in runtime/checks.py -->
<!-- @mind:todo Implement check_gating_ratio checker in runtime/checks.py -->

---

## MARKERS

<!-- @mind:todo All four checkers need implementation — currently spec only -->
<!-- @mind:proposition Add a health indicator for sense adoption spread — how many citizens use custom senses, is it growing? -->
<!-- @mind:proposition Add a health indicator for sense diversity — are citizens creating varied senses or copying the same one? -->
