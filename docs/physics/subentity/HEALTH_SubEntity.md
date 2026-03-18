# SubEntity Traversal Engine — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Exploration termination under real graph topology | Real graphs have cycles, dead ends, and dense clusters that test fixtures cannot reproduce |
| Energy injection correctness over many traversals | Cumulative drift in energy/weight values only surfaces after hundreds of explorations |
| Crystallization novelty accuracy | Whether the 0.85 threshold produces good deduplication depends on the actual embedding distribution |
| Fatigue detection calibration | Whether 5-step window and 0.05 threshold are appropriate depends on real graph density and embedding quality |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file covers the SubEntity traversal engine: exploration termination, energy injection correctness, crystallization quality, and state machine integrity. It exists because exploration traverses live graph data with real embeddings, and emergent failure modes (infinite loops from graph cycles, energy accumulation drift, duplicate crystallizations) only manifest at runtime scale.

Boundaries: This file verifies SubEntity exploration behavior. It does NOT verify graph storage (database adapters), embedding model quality, or physics tick behavior. Those belong to their own HEALTH files.

---

## WHY THIS PATTERN

Tests verify that the state machine transitions correctly given mock inputs. Health verifies that the state machine produces correct outcomes given real graph structure. A test can verify `transition_to(RESONATING)` works; health verifies that explorations on the actual graph don't get stuck in SEEKING loops because every real link scores below threshold.

Docking-based checks are the right tradeoff here because:
- Energy injection and narrative creation are observable graph mutations (dock into graph_ops)
- State transitions are discrete events (dock into state change boundaries)
- Throttling is essential because explorations happen continuously during the tick loop

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
PATTERNS:        ./PATTERNS_SubEntity.md
BEHAVIORS:       ./BEHAVIORS_SubEntity.md
ALGORITHM:       ./ALGORITHM_SubEntity.md
VALIDATION:      ./VALIDATION_SubEntity.md
IMPLEMENTATION:  ./IMPLEMENTATION_SubEntity.md
THIS:            HEALTH_SubEntity.md (you are here)
SYNC:            ./SYNC_SubEntity.md
```

---

## IMPLEMENTS

```yaml
implements:
  runtime: runtime/physics/health/subentity_health.py
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: exploration_query_to_result
    purpose: If exploration fails silently (returns empty results, hangs, or injects wrong energy), graph_query and subcall return garbage — users see irrelevant or missing information
    triggers:
      - type: event
        source: MCP tool handler (graph_query, subcall)
        notes: Every graph_query triggers one exploration; subcall may trigger multiple
      - type: event
        source: Physics tick loop (tick_v1_2.py)
        notes: Tick may spawn explorations for actors with accumulated energy
    frequency:
      expected_rate: 2-10/min
      peak_rate: 50/min (during active conversation with multiple graph queries)
      burst_behavior: Each exploration runs independently; asyncio event loop serializes CPU-bound work but concurrent I/O overlaps
    risks:
      - Exploration never terminates (V2)
      - Energy injection produces negative values (V3)
      - Crystallization creates duplicates (V4)
      - State machine enters invalid state (V1)
    notes: Exploration touches multiple graph nodes and links per run; energy mutations are cumulative and non-reversible
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Semantic graph traversal | exploration_termination, state_machine_integrity | If exploration hangs or enters invalid state, traversal fails entirely |
| Knowledge crystallization | crystallization_novelty | Duplicate narratives pollute the graph and confuse future explorations |
| Energy injection | energy_injection_correctness | Wrong energy values cascade through the physics tick, corrupting graph weights |
| Bounded exploration | exploration_termination | Non-terminating exploration blocks the event loop |

```yaml
health_indicators:
  - name: exploration_termination
    flow_id: exploration_query_to_result
    priority: high
    rationale: Non-terminating exploration blocks the async event loop, making the entire system unresponsive. Users experience timeouts and lost queries.

  - name: energy_injection_correctness
    flow_id: exploration_query_to_result
    priority: high
    rationale: Incorrect energy injection causes graph weight drift. Over hundreds of explorations, this compounds — hot nodes get hotter indefinitely or cold nodes never warm up. The physics tick amplifies the error.

  - name: crystallization_novelty
    flow_id: exploration_query_to_result
    priority: med
    rationale: Duplicate narratives fragment knowledge. A user querying "What do I know about X?" gets multiple near-identical results instead of one authoritative answer. Graph grows without adding value.

  - name: state_machine_integrity
    flow_id: exploration_query_to_result
    priority: high
    rationale: Invalid state transitions mean the state machine contract is broken. Handlers receive unexpected states, causing silent failures or crashes. All exploration results become unreliable.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/physics/health/subentity_health_status.json
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-18T00:00:00Z
    source: subentity_health_aggregate
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_exploration_termination
    purpose: Verify all explorations reach MERGING or raise ExplorationTimeoutError within configured limits (V2)
    status: pending
    priority: high

  - name: check_energy_injection_non_negative
    purpose: Verify energy injection never produces negative values and node.energy only increases during traversal (V3)
    status: pending
    priority: high

  - name: check_crystallization_novelty
    purpose: Verify crystallized narratives have max cosine similarity < 0.85 to all existing narratives (V4)
    status: pending
    priority: med

  - name: check_state_transitions_valid
    purpose: Verify no SubEntityTransitionError is raised during normal operation and all transitions are in VALID_TRANSITIONS (V1)
    status: pending
    priority: high
```

---

## INDICATOR: exploration_termination

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: exploration_termination
  client_value: Users get responses to graph queries within 30 seconds. System never hangs on a single exploration.
  validation:
    - validation_id: V2
      criteria: Every exploration reaches MERGING or raises ExplorationTimeoutError
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK = all explorations terminated within limits; WARN = exploration terminated via MAX_STEPS (not ideal); ERROR = exploration timed out or hung
  aggregation:
    method: worst-case (any ERROR -> ERROR, any WARN -> WARN, else OK)
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_explore_entry
    type: event
    payload: exploration_id, actor_id, query, timeout_s
  - point: dock_result_return
    type: event
    payload: exploration_id, duration_s, depth, step_count, state
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="exploration_termination",
    triggers=[
        triggers.event.on("exploration.completed"),
    ],
    on_problem="EXPLORATION_HANG",
    task="investigate_exploration_termination",
)
def check_exploration_termination(ctx) -> dict:
    """Verify exploration terminated correctly."""
    result = ctx.event
    if result.state != "merging":
        return Signal.critical(details={"state": result.state, "exploration_id": result.id})
    if result.duration_s > 25.0:  # Near timeout
        return Signal.degraded(details={"duration_s": result.duration_s})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: Exploration reached MERGING state within 25 seconds
  degraded: Exploration reached MERGING but took more than 25 seconds (near timeout)
  critical: Exploration did not reach MERGING state (hung or invalid terminal state)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: exploration.completed event
  max_frequency: 1/10s
  burst_limit: 6 per minute
  backoff: exponential (2x) on consecutive degraded signals
```

---

## INDICATOR: energy_injection_correctness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: energy_injection_correctness
  client_value: Graph energy values remain physically meaningful. Frequently explored nodes are hotter (more visible in queries). Energy does not accumulate without bound or go negative.
  validation:
    - validation_id: V3
      criteria: Energy injection is non-negative; node.energy after >= node.energy before
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all energy injections non-negative; 0 = at least one negative injection detected
  aggregation:
    method: all-pass (any 0 -> 0)
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_energy_injection
    type: graph_ops
    payload: node_id, energy_before, energy_after, injection_amount, state_multiplier
```

### SIGNALS

```yaml
signals:
  healthy: All sampled energy injections are non-negative
  critical: Negative energy injection detected (energy_after < energy_before)
```

---

## INDICATOR: crystallization_novelty

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: crystallization_novelty
  client_value: New narratives are genuinely new knowledge, not duplicates of existing content
  validation:
    - validation_id: V4
      criteria: Crystallized narrative has max cosine similarity < 0.85 to all existing narratives
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Fraction of crystallizations that passed novelty check. 1.0 = all novel. 0.0 = all duplicates.
  aggregation:
    method: rolling average over last 100 crystallizations
    display: float_0_1
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_narrative_creation
    type: graph_ops
    payload: narrative_id, max_similarity, is_novel, existing_narrative_count
```

### SIGNALS

```yaml
signals:
  healthy: Novelty ratio > 0.9 (90%+ of crystallizations are genuinely novel)
  degraded: Novelty ratio between 0.7 and 0.9 (some near-duplicates being created)
  critical: Novelty ratio < 0.7 (most crystallizations are duplicating existing content)
```

---

## INDICATOR: state_machine_integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: state_machine_integrity
  client_value: Exploration state machine operates correctly — no invalid transitions, no stuck states
  validation:
    - validation_id: V1
      criteria: Every transition is in VALID_TRANSITIONS[current_state]
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = no SubEntityTransitionError raised; 0 = invalid transition attempted
  aggregation:
    method: all-pass
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_state_transition
    type: event
    payload: subentity_id, old_state, new_state, valid
```

### SIGNALS

```yaml
signals:
  healthy: No invalid state transitions detected
  critical: SubEntityTransitionError raised (invalid transition attempted)
```

---

## HOW TO RUN

```bash
# Run all health checks for SubEntity module
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.physics.health.subentity_health --all

# Run a specific checker
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.physics.health.subentity_health --check exploration_termination
```

---

## KNOWN GAPS

- All 4 checkers are `pending` — runtime implementation in `runtime/physics/health/subentity_health.py` does not yet exist
- No test for V2 under cyclic graph conditions (graph with loops)
- No monitoring for V9 (crystallization embedding completeness) — would require tracking embedding update frequency per step

<!-- @mind:todo Implement runtime/physics/health/subentity_health.py with the 4 defined checkers -->
<!-- @mind:todo Add V2 stress test with cyclic graph topology -->
<!-- @mind:todo Consider health indicator for fatigue detection calibration (V6-related) -->

---

## MARKERS

<!-- @mind:todo Implement all 4 checkers in runtime/physics/health/subentity_health.py -->
<!-- @mind:proposition Add a "graph mutation rate" indicator tracking narrative creation rate over time -->
