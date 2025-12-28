# World Runner — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-19
UPDATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health checks and verification mechanics for the World Runner module. It ensures that off-screen time passage and narrative flips are resolved into valid graph mutations and narrative injections without corrupting the simulation state.

What it protects:
- **Off-screen Continuity**: Consistent evolution of world state when player is not present.
- **Fail-safe Operation**: Graceful handling of agent CLI timeouts or errors.
- **Schema Compliance**: Ensuring background changes follow the canonical world model.

---

## CHAIN

```
PATTERNS:       ./PATTERNS_World_Runner.md
BEHAVIORS:      ./BEHAVIORS_World_Runner.md
ALGORITHM:      ./ALGORITHM_World_Runner.md
VALIDATION:     ./VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_World_Runner_Service_Architecture.md
THIS:           TEST_World_Runner_Coverage.md
SYNC:           ./SYNC_World_Runner.md

IMPL:           mind/infrastructure/orchestration/world_runner.py
```

> **Contract:** HEALTH checks verify intent and failure modes without touching core agent logic.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: world_evolution
    purpose: Advance background story beats during time passage.
    triggers:
      - type: event
        source: Orchestrator
        notes: Triggered on significant time passage or movement.
    frequency:
      expected_rate: 0.5/min
      peak_rate: 5/min (during travel skips)
      burst_behavior: Limited by subprocess timeout (10m).
    risks:
      - Agent hallucination of world facts
      - CLI failure leaving graph stale
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: background_consistency
    flow_id: world_evolution
    priority: high
    rationale: Off-screen events must not contradict the known graph state.
  - name: adapter_resilience
    flow_id: world_evolution
    priority: high
    rationale: CLI failures must result in safe fallbacks, not crashes.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: logs
  result:
    representation: enum
    value: OK
    updated_at: 2025-12-20T10:15:00Z
    source: manual_inspection
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: fallback_validator
    purpose: Ensure _fallback_response matches schema.
    status: active
    priority: high
  - name: mutation_safety_checker
    purpose: Verify background mutations apply cleanly.
    status: pending
    priority: med
```

---

## INDICATOR: adapter_resilience

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: adapter_resilience
  client_value: Prevents game stalls if the background agent fails.
  validation:
    - validation_id: V3 (Runner)
      criteria: Failures degrade safely via fallback.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: runner_input
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService.process_flips
    location: mind/infrastructure/orchestration/world_runner.py:34
  output:
    id: runner_output
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService._call_claude
    location: mind/infrastructure/orchestration/world_runner.py:84
```

---

## KNOWN GAPS

<!-- @mind:todo No automated regression for CLI timeout handling. -->
<!-- @mind:todo Lack of schema validation for background injection payloads. -->