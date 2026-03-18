# Spatial Presence — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Position drift over time | Needs real graph evolution, not fixtures |
| Zone distribution balance | Emergent from real node population |
| Quaternion denormalization accumulation | Only happens after many engine updates |
| Scale/mass divergence from weight | Requires real weight changes over time |

**Tests gate completion. Health monitors runtime.**

If behavior is deterministic with known inputs (e.g., log1p formula) -> write a test.
If behavior emerges from real data over time (e.g., zone clustering balance) -> write a health check.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the 6 spatial fields on NodeBase: position, orientation, scale, velocity, mass, zone_id. It verifies that these fields maintain their invariants (VALIDATION V1-V9) in production, where real graph evolution can cause drift, denormalization, and inconsistency that unit tests with fixtures cannot catch.

It exists because spatial fields are derived from cognitive fields that change continuously. Weight changes -> scale and mass should update. Affinities shift -> position should migrate. Without health checks, divergence between cognitive state and spatial state accumulates silently.

Boundaries: This file verifies spatial field integrity. It does NOT verify rendering correctness (engine responsibility), barycentrique formula accuracy (tested in unit tests), or vision cone computation (vision system responsibility).

---

## WHY THIS PATTERN

Tests pass but runtime fails when: (1) the spatial mapper has not run after significant graph changes, (2) quaternion denormalization accumulates across hundreds of engine updates, (3) weight consolidation (Law 6) changes weight but scale is stale, (4) new nodes are created without spatial fields and never mapped.

Docking-based checks are the right tradeoff because the spatial mapper and engine write to FalkorDB — we can verify post-write state without modifying the mapper or engine code.

Throttling protects signal quality because the spatial mapper runs periodically (not per-tick), so health checks should run after mapper completion, not continuously.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
PATTERNS:        ./PATTERNS_Spatial_Presence.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Presence.md
ALGORITHM:       ./ALGORITHM_Spatial_Presence.md
VALIDATION:      ./VALIDATION_Spatial_Presence.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Presence.md
THIS:            HEALTH_Spatial_Presence.md (you are here)
SYNC:            ./SYNC_Spatial_Presence.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks/spatial_presence_health.py  # TBD — not yet created
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: spatial_mapping
    purpose: If position/zone_id computation fails or produces out-of-bounds results, nodes disappear from the 3D world or appear in wrong districts
    triggers:
      - type: schedule
        source: scripts/spatial_mapper.py:map_graph()
        notes: CLI invocation or periodic scheduler (expected cadence TBD)
    frequency:
      expected_rate: 1/5min
      peak_rate: 1/min
      burst_behavior: Sequential runs — mapper locks on graph, no parallel execution
    risks:
      - V1 violation: positions out of world bounds
      - V5 violation: zone_id mismatches highest affinity
      - V8 violation: position set but zone_id null (or vice versa)
    notes: Graph queries all nodes — performance sensitive at 1000+ nodes

  - flow_id: engine_spatial_update
    purpose: If orientation denormalizes or velocity is non-null when stationary, vision and proprioception produce incorrect results
    triggers:
      - type: event
        source: engine/ Three.js client
        notes: On actor movement or rotation
    frequency:
      expected_rate: 10/s per active actor
      peak_rate: 30/s per actor (movement every frame)
      burst_behavior: Throttled writes — engine batches updates, does not write every frame
    risks:
      - V2 violation: quaternion denormalization
      - V7 violation: phantom velocity on stationary actors
    notes: Engine-side — health checks verify FalkorDB state, not engine internals
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Physical presence | position_bounds, spatial_consistency | Nodes must exist in valid 3D space |
| O2: Derived fields | scale_weight_coherence, mass_derivation | Spatial fields must track their cognitive sources |
| O3: Visual stability | zone_distribution | Balanced distribution indicates mapping is working |
| O4: Vision + proprioception | quaternion_integrity, velocity_stationary | Orientation and velocity must be valid for perception |

```yaml
health_indicators:
  - name: position_bounds
    flow_id: spatial_mapping
    priority: high
    rationale: Out-of-bounds positions make nodes invisible in the renderer. Directly impacts O1.

  - name: quaternion_integrity
    flow_id: engine_spatial_update
    priority: high
    rationale: Denormalized quaternions corrupt vision cone direction. Directly impacts O4.

  - name: scale_weight_coherence
    flow_id: spatial_mapping
    priority: med
    rationale: Stale scale misrepresents node importance. Impacts O2.

  - name: spatial_consistency
    flow_id: spatial_mapping
    priority: high
    rationale: Partial spatial state (position without zone_id) causes query failures. Impacts O1.

  - name: zone_distribution
    flow_id: spatial_mapping
    priority: med
    rationale: All nodes in one zone means the affinity formula is broken. Impacts O2.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: .mind/state/health/spatial_presence.yaml
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-18T00:00:00Z
    source: spatial_presence_health
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_position_bounds
    purpose: Verify all positioned nodes have position within world bounds (V1)
    status: pending
    priority: high
  - name: check_quaternion_integrity
    purpose: Verify all non-null orientations are unit quaternions (V2)
    status: pending
    priority: high
  - name: check_scale_weight_coherence
    purpose: Verify scale matches 1.0 + log1p(weight) within tolerance (V3)
    status: pending
    priority: med
  - name: check_mass_derivation
    purpose: Verify mass matches weight * (1 + 0.1 * link_count) within tolerance (V4)
    status: pending
    priority: med
  - name: check_spatial_consistency
    purpose: Verify position and zone_id are both null or both non-null (V8)
    status: pending
    priority: high
  - name: check_zone_distribution
    purpose: Verify no single zone contains >60% of all positioned nodes (V5 proxy)
    status: pending
    priority: med
```

---

## INDICATOR: position_bounds

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: position_bounds
  client_value: Nodes with out-of-bounds positions are invisible in the 3D renderer. Citizens and visitors cannot see or interact with them.
  validation:
    - validation_id: V1
      criteria: For every node with non-null position, |x| <= 500, |y| <= 300, |z| <= 500. No NaN or Infinity.
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Fraction of positioned nodes within bounds. 1.0 = all in bounds. <0.95 = degraded.
  aggregation:
    method: count(in_bounds) / count(positioned)
    display: float_0_1
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_position_output
    type: db
    payload: {node_id, position [x,y,z]}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="position_bounds",
    triggers=[
        triggers.schedule.after_mapper_run(),
    ],
    on_problem="SPATIAL_OUT_OF_BOUNDS",
    task="fix_spatial_positions",
)
def check_position_bounds(ctx) -> dict:
    """Verify all positioned nodes are within world bounds."""
    nodes = ctx.graph.query("MATCH (n) WHERE n.position IS NOT NULL RETURN n.id, n.position")
    total = len(nodes)
    violations = []
    for node_id, pos in nodes:
        x, y, z = pos
        if abs(x) > 500 or abs(y) > 300 or abs(z) > 500:
            violations.append(node_id)
        if any(math.isnan(v) or math.isinf(v) for v in pos):
            violations.append(node_id)
    score = (total - len(violations)) / max(total, 1)
    if score >= 0.99:
        return Signal.healthy(score=score)
    if score >= 0.90:
        return Signal.degraded(score=score, details={"violations": violations[:10]})
    return Signal.critical(score=score, details={"violations": violations[:20]})
```

### SIGNALS

```yaml
signals:
  healthy: All positioned nodes within bounds (score >= 0.99)
  degraded: 1-10% of positioned nodes out of bounds (score >= 0.90)
  critical: More than 10% of positioned nodes out of bounds (score < 0.90)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: After spatial mapper run
  max_frequency: 1/5min
  burst_limit: 3
  backoff: Exponential — double interval on consecutive degraded signals
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind/state/health/spatial_presence.yaml
      transport: file
      notes: Persistent health state for Doctor
display:
  locations:
    - surface: CLI
      location: mind doctor spatial
      signal: green/yellow/red
      notes: Traffic light based on score
```

### MANUAL RUN

```yaml
manual_run:
  command: python3 -c "from runtime.checks.spatial_presence_health import check_position_bounds; check_position_bounds()"
  notes: Run after mapper to verify positions
```

---

## INDICATOR: quaternion_integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: quaternion_integrity
  client_value: Denormalized quaternions produce incorrect vision cones. Citizens see wrong nodes or miss visible ones.
  validation:
    - validation_id: V2
      criteria: magnitude([qx,qy,qz,qw]) within [0.999, 1.001]. No NaN. No zero quaternion.
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Fraction of oriented nodes with valid unit quaternions. 1.0 = all valid.
  aggregation:
    method: count(valid) / count(oriented)
    display: float_0_1
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_orientation_write
    type: db
    payload: {actor_id, orientation [qx,qy,qz,qw]}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="quaternion_integrity",
    triggers=[
        triggers.schedule.every("5min"),
    ],
    on_problem="QUATERNION_DENORMALIZED",
    task="fix_quaternion_normalization",
)
def check_quaternion_integrity(ctx) -> dict:
    """Verify all orientations are unit quaternions."""
    nodes = ctx.graph.query("MATCH (n) WHERE n.orientation IS NOT NULL RETURN n.id, n.orientation")
    total = len(nodes)
    violations = []
    for node_id, q in nodes:
        if len(q) != 4:
            violations.append((node_id, "wrong_length"))
            continue
        mag = math.sqrt(sum(v*v for v in q))
        if abs(mag - 1.0) > 0.001:
            violations.append((node_id, f"mag={mag:.4f}"))
        if any(math.isnan(v) for v in q):
            violations.append((node_id, "nan"))
        if all(v == 0 for v in q):
            violations.append((node_id, "zero_quaternion"))
    score = (total - len(violations)) / max(total, 1)
    if score >= 0.99:
        return Signal.healthy(score=score)
    return Signal.degraded(score=score, details={"violations": violations[:10]})
```

### SIGNALS

```yaml
signals:
  healthy: All oriented nodes have valid unit quaternions (score >= 0.99)
  degraded: Some quaternions denormalized (score < 0.99)
  critical: N/A — denormalization is auto-correctable by renormalization
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: Every 5 minutes
  max_frequency: 1/5min
  burst_limit: 1
  backoff: None — fixed interval
```

---

## INDICATOR: spatial_consistency

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: spatial_consistency
  client_value: Inconsistent spatial state (position without zone_id or vice versa) causes query failures and rendering errors.
  validation:
    - validation_id: V8
      criteria: If position is non-null then zone_id is non-null. If zone_id is non-null then position is non-null.
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all nodes consistent. 0 = at least one inconsistent node.
  aggregation:
    method: All-or-nothing — one violation fails the check
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_graph_write
    type: db
    payload: {node_id, position, zone_id}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="spatial_consistency",
    triggers=[
        triggers.schedule.after_mapper_run(),
    ],
    on_problem="SPATIAL_INCONSISTENCY",
    task="fix_spatial_consistency",
)
def check_spatial_consistency(ctx) -> dict:
    """Verify position and zone_id are both null or both non-null."""
    inconsistent = ctx.graph.query(
        "MATCH (n) WHERE (n.position IS NOT NULL AND n.zone_id IS NULL) "
        "OR (n.position IS NULL AND n.zone_id IS NOT NULL) "
        "RETURN n.id"
    )
    if len(inconsistent) == 0:
        return Signal.healthy()
    return Signal.critical(details={"inconsistent_nodes": [r[0] for r in inconsistent]})
```

### SIGNALS

```yaml
signals:
  healthy: All nodes have consistent spatial state
  degraded: N/A
  critical: At least one node has position XOR zone_id
```

---

## HOW TO RUN

```bash
# Run all spatial presence health checks
python3 -m runtime.checks.spatial_presence_health

# Run a specific checker
python3 -c "from runtime.checks.spatial_presence_health import check_position_bounds; print(check_position_bounds())"
```

---

## KNOWN GAPS

- V3 (scale coherence) checker: defined in index but not fully specified — needs production weight data to calibrate tolerance
- V4 (mass derivation) checker: defined in index but not fully specified — needs link_count query
- V6 (no teleportation) checker: cannot verify from graph state alone — requires engine-side instrumentation
- V7 (velocity null when stationary) checker: needs correlation between position history and velocity field
- V9 (default orientation) checker: simple but not yet implemented

<!-- @mind:todo Implement check_scale_weight_coherence with tolerance epsilon = 0.01 -->
<!-- @mind:todo Implement check_mass_derivation — requires link_count per node query -->
<!-- @mind:todo Design engine-side V6 teleportation check — log max frame displacement -->

---

## MARKERS

<!-- @mind:todo Create runtime/checks/spatial_presence_health.py implementing these checkers -->
<!-- @mind:todo Define .mind/state/health/spatial_presence.yaml schema for Doctor integration -->
<!-- @mind:proposition Add check_unmapped_nodes: fraction of L3 nodes that still have null position after mapper run -->
<!-- @mind:escalation Mapper run frequency not yet defined — health check throttling depends on this decision -->
