# Physics — Health: Verification Mechanics and Coverage

```
STATUS: STABLE (v1.2), DESIGNING (v1.6.1)
CREATED: 2024-12-18
UPDATED: 2025-12-26
```

---

## PURPOSE OF THIS FILE

This file defines the health checks and verification mechanics for the Physics module. It safeguards the "living world" metabolism, ensuring that energy flows correctly, narratives flip as intended, and the system remains near a critical threshold for dramatic interest.

What it protects:
- **Narrative Metabolism**: Correct energy flow and decay across the graph.
- **Dramatic Momentum**: Proper flip detection and handler triggering.
- **State Integrity**: Consistency of weight, energy, and status properties.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Physics.md
BEHAVIORS:       ./BEHAVIORS_Physics.md
ALGORITHM:       ./ALGORITHM_Physics.md
VALIDATION:      ./VALIDATION_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Physics.md
THIS:            HEALTH_Physics.md
SYNC:            ./SYNC_Physics.md

IMPL:            runtime/physics/tick.py
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: physics_tick
    purpose: Ensure the world metabolism is active and proportional.
    triggers:
      - type: schedule
        source: Orchestrator.run
        notes: Typically every 5+ game minutes.
    frequency:
      expected_rate: 1/min (real-time)
      peak_rate: 10/min (during speed 3x)
      burst_behavior: Ticks may be skipped if elapsed time is too small.
    risks:
      - Energy stagnation (no flips)
      - Energy explosion (infinite runaway)
      - Delayed consequences (broken cascades)
    notes: Core metabolism of the system.

  # v1.6.1 SubEntity Exploration Flow
  - flow_id: subentity_exploration
    purpose: Ensure SubEntity traversal produces diverse, novel discoveries.
    triggers:
      - type: request
        source: Query or moment creates exploration
        notes: Async coroutines spawn per SubEntity
    frequency:
      expected_rate: per-query
      peak_rate: 100 SubEntities/exploration
      burst_behavior: Tree structure bounds parallel execution
    risks:
      - Sibling convergence (wasted exploration)
      - Link score miscalculation (wrong paths taken)
      - Crystallization of redundant narratives
      - Exploration timeout (safety limit hit)
    notes: Ephemeral but critical for search quality.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: energy_momentum
    flow_id: physics_tick
    priority: high
    rationale: If energy doesn't flow, the world feels dead.
  - name: flip_consistency
    flow_id: physics_tick
    priority: high
    rationale: Flips are the primary source of drama; missed flips mean missed story.
  - name: decay_integrity
    flow_id: physics_tick
    priority: med
    rationale: Prevents energy accumulation that causes "everything happening at once".

  # v1.6.1 SubEntity Exploration Indicators
  - name: sibling_divergence
    flow_id: subentity_exploration
    priority: high
    rationale: Siblings must spread out; convergence wastes exploration budget.

  - name: link_score_validity
    flow_id: subentity_exploration
    priority: high
    rationale: Link scores must include all factors (semantic, polarity, permanence, novelty, divergence).

  - name: crystallization_quality
    flow_id: subentity_exploration
    priority: med
    rationale: New narratives must be sufficiently novel (>0.85 cosine threshold).

  - name: exploration_coverage
    flow_id: subentity_exploration
    priority: med
    rationale: Exploration should cover diverse graph regions, not cluster locally.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: stdout
  result:
    representation: tuple
    value: {status: OK, score: 0.95}
    updated_at: 2025-12-20T10:00:00Z
    source: GraphTick.run
```

---

## DOCK TYPES (COMPLETE LIST)

- `graph_ops` (graph operations or traversal)
- `api` (HTTP/RPC boundary)

---

## CHECKER INDEX

```yaml
checkers:
  - name: energy_balance_checker
    purpose: Verify energy conservation and expected decay (I7).
    status: active
    priority: high
  - name: flip_threshold_checker
    purpose: Ensure flips occur at deterministic thresholds (I8).
    status: active
    priority: high
  - name: snap_display_checker
    purpose: Guard The Snap transition by confirming 3x-phase filtering and the 1x arrival.
    status: active
    priority: medium
  - name: cluster_energy_monitor_checker
    purpose: Track large cluster energy totals in real-time to catch runaway spikes.
    status: active
    priority: medium

  # v1.6.1 SubEntity Checkers
  - name: sibling_divergence_checker
    purpose: Verify siblings explore different graph regions (V18, link score).
    status: pending
    priority: high

  - name: link_score_checker
    purpose: Validate link score includes all 5 factors correctly.
    status: pending
    priority: high

  - name: crystallization_novelty_checker
    purpose: Verify new narratives pass 0.85 cosine threshold.
    status: pending
    priority: medium

  - name: exploration_timeout_checker
    purpose: Verify explorations complete within safety timeout.
    status: pending
    priority: medium
```

---

## INDICATOR: energy_momentum

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: energy_momentum
  client_value: Ensures the world feels alive and responsive to player focus.
  validation:
    - validation_id: I7
      criteria: Energy in = energy out + decay losses.
    - validation_id: I2
      criteria: Graph never stops thinking.
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: 1.0 = healthy flow, 0.0 = stagnant or exploded.
  aggregation:
    method: weighted_average
    display: CLI
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: tick_input
    method: engine.physics.tick.GraphTick.run
    location: runtime/physics/tick.py:68
  output:
    id: flip_output
    method: engine.physics.tick.GraphTick.run
    location: runtime/physics/tick.py:126
```

---

## TRACE SCENARIOS (VERIFICATION)

See original `TEST_Physics.md` for detailed walk-throughs of these scenarios.

### Trace 1: Simple Exchange
- **Input:** Player question (energy injection).
- **Expectation:** Target character's weight increases and flips.
- **Verification:** `TickResult.flips` contains the expected moment.

### Trace 2: Silence
- **Input:** Irrelevant player input.
- **Expectation:** Energy returns to player character.
- **Verification:** Player character observation moment flips after N ticks.

--- 

## CHECK: Snap Display Sequence

- **Purpose:** Ensure The Snap transition filters moments at 3x, enforces the frozen beat, and lands at 1x only when interrupts occur.
- **Implementation reference:** `runtime/physics/display_snap_transition_checker.py`
- **How to run:** `pytest mind/tests/test_physics_display_snap.py`
- **What to observe:** The test mirrors Phase 1 (blurred running), Phase 2 (300-500ms beat), and Phase 3 (arrival) durations plus speed reset.

---

## CHECK: Cluster Energy Monitor

- **Purpose:** Verify large clusters expose real-time energy totals so surges can be surfaced before running away.
- **Implementation reference:** `runtime/physics/cluster_energy_monitor.py`
- **How to run:** `pytest mind/tests/test_cluster_energy_monitor.py`
- **What to observe:** The monitor records snapshots, surfaces clusters with ≥50 nodes, and flags spikes when total energy jumps beyond 1.5× the running average.

---

## HOW TO RUN

```bash
# Run physics tests (unit and integration)
pytest mind/tests/test_moment_graph.py -v
```

---

## NEW HEALTH CHECKS

### Snap transition display rules

- **Checker:** `snap_display_checker`
- **Purpose:** Validates the three-phase Snap transition (3x blur → silence beat → 1x arrival) through `runtime/physics/display_snap_transition_checker.py`.
- **Verification:** `pytest mind/tests/test_physics_display_snap.py`
- **Signal:** Fails when the beat duration drifts outside 300–500 ms, non-interrupts leak through 3x, or the speed never resets to 1x.

### Real-time cluster energy monitoring

- **Checker:** `cluster_energy_monitor_checker`
- **Purpose:** Summarizes energy per graph cluster via `runtime/physics/cluster_energy_monitor.py` and flags surges that exceed 1.5× the running average.
- **Verification:** `pytest mind/tests/test_cluster_energy_monitor.py`
- **Signal:** Telemetry can surface reports and spike alerts before dense clusters overwhelm the simulation.

---

## v1.6.1 SUBENTITY EXPLORATION HEALTH

### INDICATOR: Sibling Divergence

```yaml
value_and_validation:
  indicator: sibling_divergence
  client_value: Ensures exploration breadth, prevents wasted parallel work
  validation:
    - validation_id: V18
      criteria: All siblings have crystallization_embedding for divergence computation
    - criteria: Siblings explore distinct graph regions (low embedding overlap)
```

**Representation:**

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Average pairwise divergence across sibling sets (1.0 = fully divergent)
  aggregation:
    method: Mean divergence across all sibling pairs
    threshold: 0.5 minimum acceptable divergence
```

**Check Mechanism:**

```yaml
mechanism:
  summary: Compare crystallization_embeddings across sibling sets
  steps:
    - For each SubEntity with siblings, compute pairwise cosine
    - Divergence = 1 - max(cosine)
    - Flag if divergence < 0.5 (siblings exploring same region)
  failure_mode: Warning if siblings converge; does not block
```

---

### INDICATOR: Link Score Validity

```yaml
value_and_validation:
  indicator: link_score_validity
  client_value: Ensures correct path selection during exploration
  validation:
    - criteria: Link score = semantic × polarity × (1-permanence) × self_novelty × sibling_divergence
    - criteria: All 5 factors computed correctly
```

**Check Mechanism:**

```yaml
mechanism:
  summary: Audit link score computation against formula
  steps:
    - Sample link score computations during exploration
    - Verify each factor is computed correctly
    - Flag if any factor is missing or constant
  failure_mode: Error if formula incomplete
```

---

### INDICATOR: Crystallization Quality

```yaml
value_and_validation:
  indicator: crystallization_quality
  client_value: Prevents redundant narrative creation
  validation:
    - criteria: New narrative.embedding has < 0.85 cosine with all existing narratives
    - criteria: Path permanence average > 0.6
```

**Check Mechanism:**

```yaml
mechanism:
  summary: Validate novelty before narrative creation
  steps:
    - Before crystallization, check novelty threshold
    - If similarity > 0.85 to any existing narrative, block creation
    - Return existing narrative instead
  failure_mode: Duplicate narrative created (should never happen)
```

---

### INDICATOR: Exploration Coverage

```yaml
value_and_validation:
  indicator: exploration_coverage
  client_value: Ensures exploration discovers diverse graph regions
  validation:
    - criteria: Exploration visits multiple graph clusters
    - criteria: No single cluster dominates findings
```

**Representation:**

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Entropy of cluster distribution in findings (1.0 = uniform)
  aggregation:
    method: Shannon entropy normalized by log(cluster_count)
    threshold: 0.6 minimum entropy
```

---

## v1.6.1 KNOWN GAPS

| Health Indicator | Checker Status | Notes |
|------------------|----------------|-------|
| Sibling divergence | Pending | Requires SubEntity implementation |
| Link score validity | Pending | Requires link_scoring.py |
| Crystallization quality | Pending | Requires crystallization.py |
| Exploration coverage | Pending | Requires exploration metrics |
| Exploration timeout | Pending | Safety limit enforcement |

<!-- @mind:todo SUBENTITY_HEALTH_IMPL: Implement SubEntity health checkers once runtime/physics/subentity.py exists -->
