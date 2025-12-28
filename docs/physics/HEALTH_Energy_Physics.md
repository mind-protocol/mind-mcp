# Energy Physics — Health: Verification Mechanics and Coverage

```
@mind:id: HEALTH.PHYSICS.ENERGY.V1.2
STATUS: DRAFT
CREATED: 2024-12-23
```

---

## PURPOSE OF THIS FILE

This HEALTH file verifies the energy physics system operates correctly at runtime. It protects:
- **Energy conservation**: No leaks, no infinite accumulation, no negative values
- **Link state integrity**: Hot/cold transitions follow rules, top-N filter works correctly
- **Tick ordering**: Phases execute in correct sequence, no race conditions
- **Moment lifecycle**: State transitions follow allowed paths
- **Agent-physics boundary**: Agents create moments, physics flows energy (never crossed)

Who relies on it:
- **Players**: Narrative coherence depends on correct energy flow
- **Narrator/World Builder agents**: Their outputs must produce valid moments
- **Operators**: System stability under load

Boundaries:
- This file verifies physics runtime behavior
- Does NOT verify agent LLM output quality (separate concern)
- Does NOT verify graph database operations (separate HEALTH file)

---

## WHY THIS PATTERN

Tests pass but runtime fails when:
- Energy accumulates over thousands of ticks (not caught in short tests)
- Link cooling rate causes all links to go cold (dead world)
- Top-N filter excludes critical links under load
- Moment creation rate exceeds physics tick rate

Docking-based checks work here because:
- Physics has clear input/output boundaries (tick start → tick end)
- Energy values are observable without changing implementation
- Link states can be sampled without interrupting flow

Throttling protects:
- Physics runs at 5-second ticks; health checks run at 1-minute intervals
- Burst checks during high-activity scenes limited to 10/minute

---

## LINK TYPES (Simplified v1.2)

### Energy Flow Links

| Type | From → To | Energy Phase |
|------|-----------|--------------|
| `expresses` | Actor → Moment | Draw |
| `about` | Moment → Any | Flow |
| `relates` | Any → Any | Flow, Backflow |
| `attached_to` | Thing → Actor/Space | Flow |

### Structural Links (No Energy)

| Type | From → To |
|------|-----------|
| `contains` | Space → Actor/Thing |
| `leads_to` | Space → Space |
| `sequence` | Moment → Moment |
| `primes` | Moment → Moment |
| `can_become` | Thing → Thing |

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Physics.md
BEHAVIORS:       ./BEHAVIORS_Physics.md
ALGORITHM:       ./ALGORITHM_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Physics.md
THIS:            HEALTH_Energy_Physics.md
SYNC:            ./SYNC_Physics.md

IMPL:            mind/physics/health/checker.py
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: tick_execution
    purpose: Complete physics tick with all phases in order
    triggers:
      - type: schedule
        source: mind/infrastructure/orchestration/world_runner.py:tick
        notes: Called by world runner loop every 5 seconds
    frequency:
      expected_rate: 12/min
      peak_rate: 12/min (fixed)
      burst_behavior: Ticks queue if previous incomplete; backpressure via world_runner
    risks:
      - V-TICK-ORDER: Phases execute out of order
      - V-TICK-COMPLETE: Tick doesn't complete all phases
    notes: Fixed rate, but phase duration varies with graph size

  - flow_id: energy_generation
    purpose: Actors generate energy gated by player proximity
    triggers:
      - type: event
        source: mind/physics/tick.py:phase_generate
        notes: Phase 1 of tick
    frequency:
      expected_rate: 12/min (per tick)
      peak_rate: 12/min
      burst_behavior: N/A (part of tick)
    risks:
      - V-GEN-PROXIMITY: Proximity calculation incorrect
      - V-GEN-OVERFLOW: Actor energy grows unbounded
    notes: Must respect path resistance for proximity

  - flow_id: moment_draw
    purpose: Possible and active moments draw from actors
    triggers:
      - type: event
        source: mind/physics/tick.py:phase_draw
        notes: Phase 2 of tick
    frequency:
      expected_rate: 12/min
      peak_rate: 12/min
      burst_behavior: N/A
    risks:
      - V-DRAW-NEGATIVE: Actor energy goes negative
      - V-DRAW-ORDER: Moments not processed by priority
    notes: Both POSSIBLE and ACTIVE draw

  - flow_id: moment_flow
    purpose: Active moments radiate to connected nodes
    triggers:
      - type: event
        source: mind/physics/tick.py:phase_flow
        notes: Phase 3 of tick
    frequency:
      expected_rate: 12/min
      peak_rate: 12/min
      burst_behavior: N/A
    risks:
      - V-FLOW-DURATION: Radiation rate doesn't match duration
      - V-FLOW-DEPLETE: Moment doesn't deplete as it radiates
    notes: Duration determines radiation rate

  - flow_id: link_traversal
    purpose: Every energy flow updates link energy, strength, emotions
    triggers:
      - type: event
        source: mind/physics/flow.py:energy_flows_through
        notes: Called on every transfer
    frequency:
      expected_rate: 100-1000/tick (depends on graph)
      peak_rate: 5000/tick (large scene)
      burst_behavior: Synchronous within tick
    risks:
      - V-TRAV-STRENGTH: Strength formula incorrect
      - V-TRAV-EMOTION: Emotion blending incorrect
    notes: Critical path - called frequently

  - flow_id: link_cooling
    purpose: Hot links cool, energy returns to nodes or becomes strength
    triggers:
      - type: event
        source: mind/physics/tick.py:phase_link_cooling
        notes: Phase 5 of tick
    frequency:
      expected_rate: 12/min
      peak_rate: 12/min
      burst_behavior: N/A
    risks:
      - V-COOL-DEAD: All links go cold (dead world)
      - V-COOL-LEAK: Energy lost during cooling
    notes: No arbitrary decay - energy conserved

  - flow_id: moment_lifecycle
    purpose: Moments transition through valid states
    triggers:
      - type: event
        source: mind/infrastructure/canon/canon_holder.py:transition
        notes: Canon holder validates transitions
    frequency:
      expected_rate: 5-20/min (moment creation rate)
      peak_rate: 100/min (busy scene)
      burst_behavior: Queue if physics can't keep up
    risks:
      - V-LIFE-INVALID: Invalid state transition
      - V-LIFE-STUCK: Moment stuck in state
    notes: POSSIBLE → ACTIVE → COMPLETED main path

  - flow_id: top_n_filter
    purpose: Only top 20 links per node participate in physics
    triggers:
      - type: event
        source: mind/physics/tick.py:get_hot_links
        notes: Called per node per phase
    frequency:
      expected_rate: 500-2000/tick
      peak_rate: 10000/tick
      burst_behavior: Synchronous
    risks:
      - V-TOPN-CRITICAL: Critical link excluded
      - V-TOPN-STALE: Filter uses stale energy values
    notes: Filter by energy × weight
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Energy Conservation | energy_balance, no_negative_energy | Leaks cause dead worlds or runaway accumulation |
| Link Integrity | link_hot_cold_ratio, link_strength_growth | All cold = dead; no growth = no memory |
| Tick Correctness | tick_phase_order, tick_completion_rate | Wrong order = wrong physics |
| Moment Lifecycle | moment_state_validity, moment_throughput | Stuck moments = frozen narrative |
| Proximity Calculation | proximity_bounds, proximity_correlation | Wrong proximity = wrong generation |

```yaml
health_indicators:
  - name: energy_balance
    flow_id: tick_execution
    priority: high
    rationale: Total system energy should be bounded; unbounded growth or leaks break narrative

  - name: no_negative_energy
    flow_id: moment_draw
    priority: high
    rationale: Negative energy is invalid state; indicates formula error

  - name: link_hot_cold_ratio
    flow_id: link_cooling
    priority: high
    rationale: If ratio drops below threshold, world goes dead; if never cools, memory explodes

  - name: link_strength_growth
    flow_id: link_traversal
    priority: med
    rationale: Zero growth means no persistent memory; runaway growth indicates formula error

  - name: tick_phase_order
    flow_id: tick_execution
    priority: high
    rationale: Out-of-order phases produce wrong physics results

  - name: tick_completion_rate
    flow_id: tick_execution
    priority: high
    rationale: Incomplete ticks leave system in invalid state

  - name: moment_state_validity
    flow_id: moment_lifecycle
    priority: high
    rationale: Invalid transitions break narrative coherence

  - name: moment_throughput
    flow_id: moment_lifecycle
    priority: med
    rationale: Throughput mismatch indicates backpressure or stuck moments

  - name: proximity_bounds
    flow_id: energy_generation
    priority: med
    rationale: Proximity outside [0,1] indicates path calculation error

  - name: top_n_coverage
    flow_id: top_n_filter
    priority: med
    rationale: Important links excluded = narrative holes
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: mind/physics/health/status.json
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2024-12-23T00:00:00Z
    source: health_aggregator
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: energy_conservation_checker
    purpose: Verify total energy bounded and no negative values
    status: pending
    priority: high
    file: mind/physics/health/checkers/energy_conservation.py

  - name: link_state_checker
    purpose: Verify hot/cold ratio healthy and strength growing
    status: pending
    priority: high
    file: mind/physics/health/checkers/link_state.py

  - name: tick_integrity_checker
    purpose: Verify phases execute in order and complete
    status: pending
    priority: high
    file: mind/physics/health/checkers/tick_integrity.py

  - name: moment_lifecycle_checker
    purpose: Verify state transitions valid and no stuck moments
    status: pending
    priority: high
    file: mind/physics/health/checkers/moment_lifecycle.py

  - name: proximity_checker
    purpose: Verify proximity values in bounds and correlate with graph distance
    status: pending
    priority: med
    file: mind/physics/health/checkers/proximity.py

  - name: top_n_checker
    purpose: Verify critical links not excluded by filter
    status: pending
    priority: med
    file: mind/physics/health/checkers/top_n.py
```

---

## INDICATOR: energy_balance

Verifies system energy stays bounded and conserved through tick cycles.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: energy_balance
  client_value: Prevents dead worlds (all energy leaked) or runaway accumulation (system instability)
  validation:
    - validation_id: V-ENERGY-BOUNDED
      criteria: Total system energy stays within [MIN_ENERGY, MAX_ENERGY] bounds
    - validation_id: V-ENERGY-CONSERVED
      criteria: Energy change per tick equals generation minus cooling-to-strength conversion
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
    - enum
  semantics:
    float_0_1: ratio of (actual_total / expected_total); 1.0 = perfect conservation
    enum: OK (0.95-1.05), WARN (0.8-0.95 or 1.05-1.2), ERROR (<0.8 or >1.2)
  aggregation:
    method: min across last 10 ticks
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-TICK-START
    method: engine.physics.tick.snapshot_energy_state
    location: mind/physics/tick.py:99
  output:
    id: DOCK-TICK-END
    method: engine.physics.tick.snapshot_energy_state
    location: mind/physics/tick.py:145
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Compare total energy before and after tick; verify delta matches expected (generation - strength_conversion)
  steps:
    - Snapshot total energy at tick start (actors + moments + narratives + links)
    - Snapshot total energy at tick end
    - Calculate expected delta (sum of generation - sum of strength conversion)
    - Compare actual delta to expected delta
    - Flag if ratio outside [0.95, 1.05]
  data_required: Energy values on all nodes and links via docks
  failure_mode: Ratio outside bounds indicates leak or accumulation
```

### INDICATOR

```yaml
indicator:
  error:
    - name: ENERGY_LEAK
      linked_validation: [V-ENERGY-CONSERVED]
      meaning: Energy disappeared from system (ratio < 0.8)
      default_action: alert
    - name: ENERGY_RUNAWAY
      linked_validation: [V-ENERGY-BOUNDED]
      meaning: Energy growing unbounded (ratio > 1.2)
      default_action: alert
  warning:
    - name: ENERGY_DRIFT
      linked_validation: [V-ENERGY-CONSERVED]
      meaning: Small leak or accumulation (0.8-0.95 or 1.05-1.2)
      default_action: warn
  info:
    - name: ENERGY_STABLE
      linked_validation: [V-ENERGY-BOUNDED, V-ENERGY-CONSERVED]
      meaning: Energy conservation within tolerance
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: 1/min
  burst_limit: 5
  backoff: exponential (2x) on repeated WARN/ERROR
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: mind/physics/health/status.json
      transport: file
      notes: Aggregated status for Doctor
    - location: logs/physics_health.log
      transport: file
      notes: Detailed per-tick values
display:
  locations:
    - surface: CLI
      location: mind health physics
      signal: green/yellow/red
      notes: Color-coded status
    - surface: Log
      location: logs/physics_health.log
      signal: JSON per tick
      notes: Full detail for debugging
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker energy_balance
  notes: Run after schema changes or suspected leak
```

---

## INDICATOR: no_negative_energy

Verifies no node or link has negative energy (invalid state).

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: no_negative_energy
  client_value: Negative energy breaks all formulas; must never occur
  validation:
    - validation_id: V-ENERGY-NON-NEGATIVE
      criteria: All energy values >= 0 at all times
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all non-negative, 0 = at least one negative
  aggregation:
    method: AND across all nodes/links
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-ALL-ENERGIES
    method: engine.physics.graph.get_all_energies
    location: mind/physics/graph/graph_queries.py:88
  output:
    id: DOCK-ALL-LINK-ENERGIES
    method: engine.physics.graph.get_all_link_energies
    location: mind/physics/graph/graph_queries.py:95
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Scan all energy values; flag if any < 0
  steps:
    - Query all node energies
    - Query all link energies
    - Check each value >= 0
    - Return first violation if any
  data_required: All energy values
  failure_mode: Any negative value indicates draw exceeded available
```

### INDICATOR

```yaml
indicator:
  error:
    - name: NEGATIVE_ENERGY
      linked_validation: [V-ENERGY-NON-NEGATIVE]
      meaning: At least one energy value is negative
      default_action: page
  info:
    - name: ENERGY_NON_NEGATIVE
      linked_validation: [V-ENERGY-NON-NEGATIVE]
      meaning: All values non-negative
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: 12/min (every tick)
  burst_limit: 12
  backoff: none (critical check)
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker no_negative
  notes: Run after any formula change
```

---

## INDICATOR: link_hot_cold_ratio

Verifies healthy ratio of hot to cold links (not all dead, not all hot).

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: link_hot_cold_ratio
  client_value: All cold = dead world (no physics). All hot = memory explosion.
  validation:
    - validation_id: V-LINK-ALIVE
      criteria: At least 10% of links hot at any time during active scene
    - validation_id: V-LINK-BOUNDED
      criteria: No more than 50% of links hot (memory bounded)
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
    - enum
  semantics:
    float_0_1: ratio of hot_links / total_links
    enum: OK (0.1-0.5), WARN_LOW (<0.1), WARN_HIGH (>0.5), ERROR_DEAD (0), ERROR_EXPLOSION (>0.8)
  aggregation:
    method: moving average over 10 ticks
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-ALL-LINK-ENERGIES
    method: engine.physics.graph.get_all_link_energies
    location: mind/physics/graph/graph_queries.py:95
  output:
    id: DOCK-LINK-HOT-COLD
    method: engine.physics.tick.count_hot_cold_links
    location: mind/physics/tick.py:get_hot_links
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Count hot vs cold links; verify ratio in healthy range
  steps:
    - Get all link energies and weights
    - Calculate energy × weight for each
    - Count hot (above COLD_THRESHOLD) and cold
    - Calculate ratio
    - Compare to bounds [0.1, 0.5]
  data_required: Link energies, weights, threshold constant
  failure_mode: Ratio outside bounds indicates cooling misconfiguration
```

### INDICATOR

```yaml
indicator:
  error:
    - name: WORLD_DEAD
      linked_validation: [V-LINK-ALIVE]
      meaning: Zero hot links; physics stopped
      default_action: page
    - name: MEMORY_EXPLOSION
      linked_validation: [V-LINK-BOUNDED]
      meaning: >80% links hot; memory growing unbounded
      default_action: alert
  warning:
    - name: WORLD_COOLING
      linked_validation: [V-LINK-ALIVE]
      meaning: <10% hot; world going dead
      default_action: warn
    - name: WORLD_HEATING
      linked_validation: [V-LINK-BOUNDED]
      meaning: >50% hot; memory pressure increasing
      default_action: warn
  info:
    - name: LINK_RATIO_HEALTHY
      linked_validation: [V-LINK-ALIVE, V-LINK-BOUNDED]
      meaning: Ratio in healthy range
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: 1/min
  burst_limit: 5
  backoff: linear on WARN
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker link_ratio
  notes: Run after adjusting cooling rates
```

---

## INDICATOR: tick_phase_order

Verifies tick phases execute in correct sequence.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: tick_phase_order
  client_value: Out-of-order phases produce wrong physics (draw before generate = overdraw)
  validation:
    - validation_id: V-TICK-ORDER
      criteria: Phases execute in order 1→2→3→4→5→6
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = correct order, 0 = out of order
  aggregation:
    method: AND across phases
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-PHASE-TIMESTAMP
    method: engine.physics.tick.get_phase_timestamps
    location: mind/physics/tick.py:_record_phase
  output:
    id: DOCK-TICK-END
    method: engine.physics.tick.get_tick_complete
    location: mind/physics/tick.py:145
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Compare phase start timestamps; verify monotonically increasing
  steps:
    - Record timestamp at each phase start
    - Verify phase 1 < phase 2 < phase 3 < phase 4 < phase 5 < phase 6
    - Flag if any out of order
  data_required: Phase timestamps from instrumentation
  failure_mode: Timestamp inversion indicates concurrency bug or code error
```

### INDICATOR

```yaml
indicator:
  error:
    - name: PHASE_ORDER_VIOLATION
      linked_validation: [V-TICK-ORDER]
      meaning: Phases executed out of order
      default_action: page
  info:
    - name: PHASE_ORDER_CORRECT
      linked_validation: [V-TICK-ORDER]
      meaning: All phases in order
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: 12/min
  burst_limit: 12
  backoff: none (critical)
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker tick_order
  notes: Run after any tick refactoring
```

---

## INDICATOR: moment_state_validity

Verifies moment state transitions follow allowed paths.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: moment_state_validity
  client_value: Invalid transitions break narrative (completed → possible makes no sense)
  validation:
    - validation_id: V-MOMENT-TRANSITIONS
      criteria: Only allowed transitions occur (POSSIBLE→ACTIVE, ACTIVE→COMPLETED, etc.)
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
    - vector
  semantics:
    binary: 1 = all valid, 0 = at least one invalid
    vector: per-moment transition history for debugging
  aggregation:
    method: AND across all transitions
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-MOMENT-TRANSITION
    method: engine.models.nodes.Moment.status
    location: mind/models/nodes.py:Moment
  output:
    id: DOCK-MOMENT-TRANSITION
    method: engine.infrastructure.canon.canon_holder.transition
    location: mind/infrastructure/canon/canon_holder.py:78
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Log all state transitions; verify each against allowed transition matrix
  steps:
    - Hook canon_holder.transition
    - Record (moment_id, old_state, new_state)
    - Compare to allowed transitions matrix
    - Flag if transition not in allowed set
  data_required: Transition events from canon holder
  failure_mode: Invalid transition indicates canon holder bug or corrupted state
```

### INDICATOR

```yaml
indicator:
  error:
    - name: INVALID_TRANSITION
      linked_validation: [V-MOMENT-TRANSITIONS]
      meaning: Moment transitioned to invalid state
      default_action: alert
  info:
    - name: TRANSITIONS_VALID
      linked_validation: [V-MOMENT-TRANSITIONS]
      meaning: All transitions valid
      default_action: log
```

### ALLOWED TRANSITIONS

```yaml
allowed_transitions:
  possible: [active, rejected]
  active: [completed, interrupted, overridden]
  completed: []  # terminal
  rejected: []   # terminal
  interrupted: []  # terminal
  overridden: []   # terminal
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: state_transition
  max_frequency: 100/min
  burst_limit: 50
  backoff: none
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker moment_states
  notes: Run after canon holder changes
```

---

## INDICATOR: link_strength_growth

Verifies link strength grows according to formula (not zero, not runaway).

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: link_strength_growth
  client_value: Zero growth = no persistent memory. Runaway growth = overflow.
  validation:
    - validation_id: V-STRENGTH-FORMULA
      criteria: Strength grows per formula with diminishing returns
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: average growth rate across sampled links (normalized)
  aggregation:
    method: mean
    display: float_0_1
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: DOCK-TRAVERSAL
    method: engine.physics.flow.energy_flows_through
    location: mind/physics/flow.py:15
  output:
    id: DOCK-TRAVERSAL
    method: engine.physics.flow.energy_flows_through
    location: mind/physics/flow.py:25
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Sample link strength before/after traversals; verify growth matches formula
  steps:
    - Sample 100 random traversals per tick
    - Record strength before and after
    - Calculate actual growth
    - Calculate expected growth from formula
    - Compare (allow 1% tolerance for float precision)
  data_required: Link strength values, traversal parameters
  failure_mode: Mismatch indicates formula implementation error
```

### INDICATOR

```yaml
indicator:
  error:
    - name: STRENGTH_FORMULA_ERROR
      linked_validation: [V-STRENGTH-FORMULA]
      meaning: Actual growth doesn't match expected
      default_action: alert
  warning:
    - name: STRENGTH_ZERO_GROWTH
      linked_validation: [V-STRENGTH-FORMULA]
      meaning: No strength growth detected (possible dead traversals)
      default_action: warn
  info:
    - name: STRENGTH_GROWING
      linked_validation: [V-STRENGTH-FORMULA]
      meaning: Growth matches formula
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: tick_complete
  max_frequency: 1/min
  burst_limit: 3
  backoff: linear
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.physics.health.checker strength_growth
  notes: Run after formula changes
```

---

## HOW TO RUN

```bash
# Run all health checks for physics
python -m engine.physics.health.checker all

# Run specific checker
python -m engine.physics.health.checker energy_balance
python -m engine.physics.health.checker no_negative
python -m engine.physics.health.checker link_ratio
python -m engine.physics.health.checker tick_order
python -m engine.physics.health.checker moment_states
python -m engine.physics.health.checker strength_growth

# Run with verbose output
python -m engine.physics.health.checker all --verbose

# Run continuous monitoring
python -m engine.physics.health.checker all --watch
```

---

## KNOWN GAPS

<!-- @mind:todo Missing checker for V-GEN-PROXIMITY-BOUNDS (proximity_bounds indicator) -->
<!-- @mind:todo Missing checker for V-GEN-PROXIMITY-CORRELATION (proximity correlation) -->
<!-- @mind:todo Missing checker for V-TOPN-CRITICAL (top_n_coverage indicator) -->
<!-- @mind:todo Missing checker for V-TOPN-DETERMINISTIC (filter determinism) -->
<!-- @mind:todo Missing checker for V-EMOTION-BASELINE (emotion blending correctness) -->
<!-- @mind:todo Missing checker for V-EMOTION-BLEND (emotion intensity bounds) -->
<!-- @mind:todo Missing checker for V-CRYSTAL-ON-COMPLETE (crystallization link creation) -->
<!-- @mind:todo Missing checker for V-BACKFLOW-GATED (backflow only to focused) -->
<!-- @mind:todo Missing checker for V-MOMENT-DRAW-BOUNDS (draw doesn't exceed available) -->
<!-- @mind:todo Missing checker for V-MOMENT-DURATION-RATE (radiation rate matches duration) -->
<!-- @mind:todo No integration test for full tick under load -->
<!-- @mind:todo Docking points not yet instrumented in tick.py -->
<!-- @mind:todo Health checker CLI not yet implemented -->

---

## VALIDATION IDS REFERENCE

> See VALIDATION_Energy_Physics.md for full criteria definitions.

| @mind:id | Category | Priority | Checker Status |
|-----------|----------|----------|----------------|
| V-ENERGY-BOUNDED | Conservation | HIGH | pending |
| V-ENERGY-CONSERVED | Conservation | HIGH | pending |
| V-ENERGY-NON-NEGATIVE | Conservation | HIGH | pending |
| V-LINK-ALIVE | Link State | HIGH | pending |
| V-LINK-BOUNDED | Link State | HIGH | pending |
| V-LINK-STRENGTH-GROWTH | Link State | MED | pending |
| V-TICK-ORDER | Tick Execution | HIGH | pending |
| V-TICK-COMPLETE | Tick Execution | HIGH | pending |
| V-MOMENT-TRANSITIONS | Moment Lifecycle | HIGH | pending |
| V-MOMENT-DRAW-BOUNDS | Moment Lifecycle | HIGH | pending |
| V-MOMENT-DURATION-RATE | Moment Lifecycle | MED | pending |
| V-GEN-PROXIMITY-BOUNDS | Generation | MED | pending |
| V-GEN-PROXIMITY-CORRELATION | Generation | MED | pending |
| V-TOPN-CRITICAL | Filter | MED | pending |
| V-TOPN-DETERMINISTIC | Filter | LOW | pending |
| V-BACKFLOW-GATED | Backflow | MED | pending |
| V-CRYSTAL-ON-COMPLETE | Crystallization | MED | pending |
| V-EMOTION-BASELINE | Emotions | LOW | pending |
| V-EMOTION-BLEND | Emotions | LOW | pending |

---

## MARKERS

<!-- @mind:todo Implement energy_conservation_checker (maps to V-ENERGY-BOUNDED, V-ENERGY-CONSERVED) -->
<!-- @mind:todo Implement no_negative_checker (maps to V-ENERGY-NON-NEGATIVE) -->
<!-- @mind:todo Implement link_state_checker (maps to V-LINK-ALIVE, V-LINK-BOUNDED) -->
<!-- @mind:todo Implement tick_integrity_checker (maps to V-TICK-ORDER, V-TICK-COMPLETE) -->
<!-- @mind:todo Implement moment_lifecycle_checker (maps to V-MOMENT-TRANSITIONS) -->
<!-- @mind:todo Implement strength_growth_checker (maps to V-LINK-STRENGTH-GROWTH) -->
<!-- @mind:todo Implement proximity_checker (maps to V-GEN-PROXIMITY-BOUNDS) -->
<!-- @mind:todo Implement top_n_checker (maps to V-TOPN-CRITICAL) -->
<!-- @mind:todo Add docking point instrumentation to tick.py -->
<!-- @mind:todo Create health checker CLI entry point -->
<!-- @mind:todo Set up status.json output format -->
