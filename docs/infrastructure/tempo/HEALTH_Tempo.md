# Tempo Controller — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This HEALTH file verifies that the tempo loop advances ticks at the expected
cadence and surfaces canon without blocking. It protects pacing integrity and
player-visible timing. It does not verify narrator content quality or physics
correctness (those belong to their own modules).

---

## WHY THIS PATTERN

Tempo is a runtime pacing boundary where tests can pass but timing still drifts.
Health checks observe real ticks and confirm alignment with VALIDATION
invariants without modifying production code.

---

## HOW TO USE THIS TEMPLATE

The full chain was read. This HEALTH doc focuses on the `tempo_tick` flow from
IMPLEMENTATION and checks cadence and surfacing bounds via docking points.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tempo.md
BEHAVIORS:       ./BEHAVIORS_Tempo.md
ALGORITHM:       ./ALGORITHM_Tempo_Controller.md
VALIDATION:      ./VALIDATION_Tempo.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tempo.md
THIS:            HEALTH_Tempo.md
SYNC:            ./SYNC_Tempo.md

IMPL:            runtime/infrastructure/tempo/health_check.py (planned)
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: tempo_tick
    purpose: ensure pacing and canon surfacing remain stable
    triggers:
      - type: schedule
        source: runtime/infrastructure/tempo/tempo_controller.py:run
        notes: asyncio loop cadence
    frequency:
      expected_rate: 12/min
      peak_rate: 120/min
      burst_behavior: tick frequency scales with speed setting
    risks:
      - V1: cadence drift
      - V3: unbounded surfacing
    notes: monitor when speed changes quickly
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: tempo_tick_advances
    flow_id: tempo_tick
    priority: high
    rationale: cadence drift is immediately visible to players
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: file:...mind/state/health_tempo.json
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2025-12-20T00:00:00Z
    source: tempo_tick_advances
```

---

## DOCK TYPES (COMPLETE LIST)

- scheduler
- stream
- db
- graph_ops

---

## CHECKER INDEX

```yaml
checkers:
  - name: tempo_tick_advances
    purpose: verify tick cadence matches speed
    status: pending
    priority: high
```

---

## INDICATOR: tempo_tick_advances

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: tempo_tick_advances
  client_value: pacing stays consistent with speed controls
  validation:
    - validation_id: V1
      criteria: tick cadence matches speed mode
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed: [binary, float_0_1, enum, tuple, vector]
  selected: [enum]
  semantics:
    enum: OK/WARN/ERROR based on cadence drift threshold
  aggregation:
    method: worst_state
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: tempo_tick_in
    method: TempoController.run
    location: runtime/infrastructure/tempo/tempo_controller.py:~70
  output:
    id: canon_broadcast
    method: CanonHolder.record_to_canon
    location: runtime/infrastructure/canon/canon_holder.py:~50
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: measure tick interval and compare to configured speed
  steps:
    - record tick timestamps
    - compare intervals to expected cadence
  data_required: tick timestamps + speed state
  failure_mode: drift beyond threshold
```

### INDICATOR

```yaml
indicator:
  error:
    - name: cadence_drift
      linked_validation: [V1]
      meaning: tempo tick cadence is out of bounds
      default_action: warn
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/min
  burst_limit: 5
  backoff: linear
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: ...mind/state/health_tempo.json
      transport: file
      notes: consumed by mind doctor

display:
  locations:
    - surface: CLI
      location: mind doctor
      signal: enum
      notes: health summary line
```

### MANUAL RUN

```yaml
manual_run:
  command: mind health tempo --checker tempo_tick_advances
  notes: run after changing speed mapping or tick scheduling
```

---

## HOW TO RUN

```bash
# Run all health checks for this module
mind health tempo

# Run a specific checker
mind health tempo --checker tempo_tick_advances
```

---

## KNOWN GAPS

<!-- @mind:todo Implement checker runner in runtime/infrastructure/tempo/health_check.py -->
<!-- @mind:todo Define real cadence thresholds per speed mode -->

---

## MARKERS

<!-- @mind:todo Add a second indicator for canon surfacing bounds -->
<!-- @mind:proposition capture backpressure metrics for operator visibility -->
