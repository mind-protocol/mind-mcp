# Spatial Geometry — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Geometry generation rate over time | Needs real crystallization events, not fixtures |
| GLTF validity across diverse zone configurations | Real zones produce combinations tests cannot enumerate |
| LOD budget adherence across the full city | 45K spaces — vertex budget violations emerge at scale |
| Zone coherence drift | Subtle modulation bugs accumulate across many generations |

**Tests gate completion. Health monitors runtime.**

Unit tests verify that `generate_base_mesh()` returns valid vertices for a known zone config. Health checks verify that over 1000 real crystallization events, every generated GLTF passes validation and every space has geometry.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the spatial geometry module's runtime verification: does the generation pipeline produce valid, performant, zone-coherent GLTF assets for every Space node created by L10 crystallization?

It exists to catch drift and degradation that unit tests miss: zone YAML changes that break generation, weight distributions that produce degenerate scales, accumulating position collisions, and storage failures that leave spaces without geometry.

**Boundaries:** This file does NOT verify rendering performance (that is the engine's concern), zone YAML authoring quality (that is worldbuilding's concern), or graph physics correctness (that is the physics module's concern). It verifies only the generation pipeline's output quality.

---

## WHY THIS PATTERN

Tests pass but runtime fails when: (1) a zone YAML has an unusual attribute combination not covered by test fixtures, (2) crystallization events arrive faster than generation can process, causing queue overflow, (3) storage fills up and GLTF exports silently fail, (4) semantic modulation produces degenerate values for an unexpected synthesis string. Docking-based health checks catch these by monitoring real pipeline output at safe cadences, without modifying the generation code.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Geometry.md
PATTERNS:        ./PATTERNS_Spatial_Geometry.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Geometry.md
ALGORITHM:       ./ALGORITHM_Spatial_Geometry.md
VALIDATION:      ./VALIDATION_Spatial_Geometry.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Geometry.md
THIS:            HEALTH_Spatial_Geometry.md (you are here)
SYNC:            ./SYNC_Spatial_Geometry.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/infrastructure/spatial_geometry/health_checks.py  # to be created
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: crystallization_geometry_generation
    purpose: Every crystallized Space gets valid GLTF geometry. If this flow fails, spaces are invisible.
    triggers:
      - type: event
        source: runtime/physics/ L10 macro-crystallization
        notes: Fires when a dense cluster of co-activated nodes exceeds crystallization threshold
    frequency:
      expected_rate: 5/hour
      peak_rate: 50/hour
      burst_behavior: Crystallization bursts occur during high-activity periods. Generation queue absorbs burst; excess events wait in queue. Bounded semaphore limits concurrent generations to 2.
    risks:
      - V1 violation — Space created but media.geometry never populated
      - V2 violation — GLTF structurally invalid
      - V4 violation — LOD vertex budget exceeded
      - V6 violation — Generation takes >30s, blocking pipeline
    notes: This is the only flow in the module. All health checks dock into this flow.
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Graph physics drive form | geometry_coverage | Confirms every crystallized Space has geometry |
| O2: Zone coherence | zone_shape_consistency | Confirms sub-spaces match parent zone shape family |
| O4: Scalable rendering | lod_budget_adherence | Confirms vertex budgets hold across all LOD levels |
| O5: GLTF universal format | gltf_structural_validity | Confirms assets are standards-compliant |

```yaml
health_indicators:
  - name: geometry_coverage
    flow_id: crystallization_geometry_generation
    priority: high
    rationale: If crystallized Spaces lack media.geometry, the city has invisible holes. Directly protects V1.

  - name: gltf_structural_validity
    flow_id: crystallization_geometry_generation
    priority: high
    rationale: Invalid GLTFs crash the renderer or show as missing objects. Directly protects V2.

  - name: lod_budget_adherence
    flow_id: crystallization_geometry_generation
    priority: high
    rationale: LOD budget violations cause frame drops at scale. Directly protects V4.

  - name: zone_shape_consistency
    flow_id: crystallization_geometry_generation
    priority: med
    rationale: Shape family mismatch breaks district visual identity. Protects V3 but is less critical than invisible spaces.

  - name: generation_time_bounded
    flow_id: crystallization_geometry_generation
    priority: med
    rationale: Unbounded generation blocks the pipeline. Protects V6. Medium priority because queue absorbs bursts.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/infrastructure/spatial_geometry/health_checks.py
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-18T00:00:00Z
    source: geometry_coverage
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: geometry_coverage_checker
    purpose: Verify all crystallized Space nodes have media.geometry populated (V1)
    status: pending
    priority: high

  - name: gltf_validity_checker
    purpose: Validate a sample of generated GLTF files pass glTF-Validator (V2)
    status: pending
    priority: high

  - name: lod_budget_checker
    purpose: Verify vertex counts across LOD levels are within budget (V4)
    status: pending
    priority: high

  - name: zone_shape_consistency_checker
    purpose: Verify sub-space primary_shape matches parent zone (V3)
    status: pending
    priority: med

  - name: generation_time_checker
    purpose: Verify generation time stays under 30s threshold (V6)
    status: pending
    priority: med
```

---

## INDICATOR: geometry_coverage

This indicator protects the foundational promise: every Space gets geometry.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: geometry_coverage
  client_value: Visitors see a complete city with no invisible holes. Every crystallized space is visually present.
  validation:
    - validation_id: V1
      criteria: Every Space node created by L10 has non-null media.geometry within 30s
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
    - enum
  semantics:
    float_0_1: ratio of crystallized Spaces with media.geometry / total crystallized Spaces
    enum: OK if ratio >= 0.99, WARN if 0.95-0.99, ERROR if < 0.95
  aggregation:
    method: minimum of float score across all zones
    display: enum (OK/WARN/ERROR)
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_graph_write
    type: graph_ops
    payload: {space_node_id, media.geometry presence}
  - point: dock_event_input
    type: event
    payload: {space_node_id, timestamp}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="geometry_coverage",
    triggers=[
        triggers.cron.hourly(),
    ],
    on_problem="SPACE_WITHOUT_GEOMETRY",
    task="generate_missing_geometry",
)
def geometry_coverage(ctx) -> dict:
    """Check that all crystallized Space nodes have media.geometry."""
    total = ctx.graph_query("MATCH (s:space) WHERE s.crystallized = true RETURN count(s)")
    with_geometry = ctx.graph_query(
        "MATCH (s:space) WHERE s.crystallized = true AND s.media_geometry_uri IS NOT NULL RETURN count(s)"
    )
    ratio = with_geometry / total if total > 0 else 1.0
    if ratio >= 0.99:
        return Signal.healthy(details={"ratio": ratio, "total": total})
    if ratio >= 0.95:
        return Signal.degraded(details={"ratio": ratio, "missing": total - with_geometry})
    return Signal.critical(details={"ratio": ratio, "missing": total - with_geometry})
```

### SIGNALS

```yaml
signals:
  healthy: 99%+ of crystallized Spaces have media.geometry
  degraded: 95-99% coverage — some spaces missing, generation may be lagging
  critical: <95% coverage — systematic generation failure
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.hourly
  max_frequency: 1/hour
  burst_limit: 1
  backoff: double interval on repeated critical (max 4 hours)
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: health_checks.log
      transport: file
      notes: Persistent record for trend analysis
display:
  locations:
    - surface: CLI
      location: mind doctor --module spatial_geometry
      signal: OK/WARN/ERROR
      notes: Green dot for OK, yellow for WARN, red for ERROR
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m runtime.infrastructure.spatial_geometry.health_checks geometry_coverage
  notes: Run after batch generation or zone reconfiguration
```

---

## INDICATOR: gltf_structural_validity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: gltf_structural_validity
  client_value: Generated 3D assets load correctly in any GLTF-compatible renderer
  validation:
    - validation_id: V2
      criteria: Every generated GLTF passes glTF-Validator with zero errors
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
    - enum
  semantics:
    float_0_1: ratio of sampled GLTFs passing validation / sample size
    enum: OK if 100% pass, WARN if 95-99% pass, ERROR if <95% pass
  aggregation:
    method: strict — any validation failure is significant
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_gltf_write
    type: file
    payload: GLB file path
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="gltf_structural_validity",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="INVALID_GLTF_GENERATED",
    task="regenerate_invalid_gltf",
)
def gltf_structural_validity(ctx) -> dict:
    """Validate a random sample of generated GLTFs."""
    all_gltfs = list_generated_gltfs(ctx.storage_root)
    sample = random.sample(all_gltfs, min(50, len(all_gltfs)))
    failures = []
    for path in sample:
        result = run_gltf_validator(path)
        if not result.valid:
            failures.append({"path": path, "errors": result.errors})
    ratio = (len(sample) - len(failures)) / len(sample) if sample else 1.0
    if ratio == 1.0:
        return Signal.healthy(details={"sampled": len(sample)})
    if ratio >= 0.95:
        return Signal.degraded(details={"failures": failures})
    return Signal.critical(details={"failures": failures})
```

### SIGNALS

```yaml
signals:
  healthy: All sampled GLTFs pass validation
  degraded: 1-5% of sampled GLTFs have validation errors
  critical: >5% failure rate — systematic generation bug
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.daily
  max_frequency: 1/day
  burst_limit: 1
  backoff: none (daily is already infrequent)
```

---

## INDICATOR: lod_budget_adherence

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: lod_budget_adherence
  client_value: The renderer maintains 30+ FPS because vertex budgets are respected at every LOD level
  validation:
    - validation_id: V4
      criteria: LOD 0 < 5000 verts, LOD 1 < 500 verts, LOD 2 < 50 verts
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK if all sampled assets within budget, WARN if any LOD 1/2 over, ERROR if any LOD 0 over
  aggregation:
    method: worst-case across sample
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_mesh_output
    type: custom
    payload: vertex count per LOD level
```

### SIGNALS

```yaml
signals:
  healthy: All LOD levels within vertex budgets
  degraded: LOD 1 or LOD 2 slightly over budget (< 10% excess)
  critical: LOD 0 over 5000 vertices — renderer performance at risk
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.daily
  max_frequency: 1/day
  burst_limit: 1
  backoff: none
```

---

## HOW TO RUN

```bash
# Run all health checks for spatial geometry
python -m runtime.infrastructure.spatial_geometry.health_checks

# Run a specific checker
python -m runtime.infrastructure.spatial_geometry.health_checks geometry_coverage
python -m runtime.infrastructure.spatial_geometry.health_checks gltf_structural_validity
python -m runtime.infrastructure.spatial_geometry.health_checks lod_budget_adherence
```

---

## KNOWN GAPS

- V3 (zone coherence) checker is defined but implementation requires embedding the shape family classification logic
- V6 (generation time) checker is defined but requires timer instrumentation in the generation pipeline
- V7 (weight-to-scale monotonicity) has no checker yet — needs graph query comparing weight/scale pairs
- V8 (positioning within bounds) has no checker yet — needs spatial distance computation

<!-- @mind:todo Implement geometry_coverage_checker as the first health check — highest priority, protects V1 -->
<!-- @mind:todo Implement gltf_validity_checker — requires glTF-Validator binary or npm package accessible from Python -->
<!-- @mind:todo Implement lod_budget_checker — requires reading vertex counts from generated GLTF metadata -->
<!-- @mind:todo Design zone_shape_consistency_checker — how to classify a mesh's "shape family" from its vertices? Consider: aspect ratio, convexity, vertex distribution statistics -->
<!-- @mind:todo Design generation_time_checker — add timing instrumentation to generate_space_geometry() that logs to a metrics file -->

---

## MARKERS

<!-- @mind:todo Create the health_checks.py runtime file once the generation pipeline is implemented -->
<!-- @mind:proposition Consider a "geometry freshness" health indicator that flags spaces whose geometry was generated before their zone YAML was last modified — indicating stale geometry that needs regeneration -->
<!-- @mind:escalation glTF-Validator is an npm package. Running it from Python requires either a subprocess call or a Python GLTF validation library. Decide which approach to use. -->
