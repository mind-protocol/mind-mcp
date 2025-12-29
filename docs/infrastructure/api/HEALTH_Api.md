# API — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2024-12-18
UPDATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health checks and verification mechanics for the API surface. It ensures that the entry points for player interaction, playthrough management, and debug streaming are responsive and structurally sound.

What it protects:
- **Connectivity**: Availability of core API endpoints and graph database backends.
- **Contract Integrity**: Consistency of request/response schemas for gameplay actions.
- **Streaming Reliability**: Stability of SSE fan-out for real-time updates.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Api.md
BEHAVIORS:       ./BEHAVIORS_Api.md
ALGORITHM:       ./ALGORITHM_Api.md
VALIDATION:      ./VALIDATION_Api.md
IMPLEMENTATION:  ./IMPLEMENTATION_Api.md
THIS:            HEALTH_Api.md
SYNC:            ./SYNC_Api.md

IMPL:            runtime/infrastructure/api/app.py
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: action_loop
    purpose: Ensure player actions can be processed and returned.
    triggers:
      - type: manual
        source: curl /api/action
    frequency:
      expected_rate: 2/min (per active player)
      peak_rate: 20/min
      burst_behavior: Rate limited at transport layer (planned).
    risks:
      - Timeout on narrator generation
      - Broken SSE stream delivery
    notes: Primary interaction loop.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: api_availability
    flow_id: action_loop
    priority: high
    rationale: If the API is down, the game is unplayable.
  - name: graph_reachability
    flow_id: action_loop
    priority: high
    rationale: API depends on FalkorDB for all state.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: stdout
  result:
    representation: enum
    value: OK
    updated_at: 2025-12-20T10:05:00Z
    source: health_check
```

---

## DOCK TYPES (COMPLETE LIST)

- `api` (HTTP/RPC boundary)
- `db` (database reachability)

---

## CHECKER INDEX

```yaml
checkers:
  - name: connectivity_checker
    purpose: Verify API and DB availability.
    status: active
    priority: high
  - name: contract_checker
    purpose: Verify response schema compliance.
    status: pending
    priority: med
```

---

## INDICATOR: api_availability

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: api_availability
  client_value: Ensures the UI can always reach the backend services.
  validation:
    - validation_id: V1 (Conceptual)
      criteria: API returns 200 OK for /health.
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK, DEGRADED, DOWN
  aggregation:
    method: worst_case
    display: Dashboard
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: action_input
    method: engine.infrastructure.api.app.player_action
    location: runtime/infrastructure/api/app.py:120
  output:
    id: action_output
    method: engine.infrastructure.api.app.player_action
    location: runtime/infrastructure/api/app.py:150
```

---

## MANUAL RUN

```bash
# Verify API Health
curl http://localhost:8000/health

# Verify Action Loop
curl -X POST http://localhost:8000/api/action -d '{"playthrough_id": "test", "action": "look"}'
```

---

## KNOWN GAPS

- None. SSE load regression and router schema validation are now automated via `runtime/tests/test_moments_api.py`
  and `runtime/tests/test_router_schema_validation.py`.
