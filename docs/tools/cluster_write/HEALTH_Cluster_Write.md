# Cluster Write — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Gemini API reliability over time | Success rate varies with load, model updates, rate limits |
| Dedup accuracy in production | Real data has edge cases fixtures cannot predict |
| Cluster atomicity under real load | Partial write failures emerge under concurrent access |
| Entity resolution quality | Match accuracy depends on graph density and real name patterns |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file covers the `cluster_write` module — the MCP tool that creates Moment clusters with identity resolution.

It exists to verify that: (a) Gemini analysis continues to produce valid entity extractions, (b) graph writes remain atomic (no partial clusters), (c) platform dedup remains correct (no duplicate actors from verified sources), and (d) link confidence grading is accurate.

**Boundaries:** This file does NOT verify graph_write (separate tool), physics behavior (L5/L6/L7 — separate system), or Gemini model quality (external dependency).

---

## WHY THIS PATTERN

Tests can verify that a known input produces a known output. They cannot verify that Gemini will extract "Florent" from "had coffee with Florent" next week (model updates), that FalkorDB will not leave orphaned nodes under concurrent writes (infra behavior), or that embedding similarity thresholds work correctly on real graph data with 200+ actors (density effects). Health checks dock into the running system and measure these properties.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
PATTERNS:        ./PATTERNS_Cluster_Write.md
BEHAVIORS:       ./BEHAVIORS_Cluster_Write.md
ALGORITHM:       ./ALGORITHM_Cluster_Write.md
VALIDATION:      ./VALIDATION_Cluster_Write.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cluster_Write.md
THIS:            HEALTH_Cluster_Write.md (you are here)
SYNC:            ./SYNC_Cluster_Write.md
```

---

## IMPLEMENTS

```yaml
implements:
  runtime: runtime/checks/cluster_write_checks.py  # to be created
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: cluster_write_pipeline
    purpose: "If this flow fails, moments are lost or graph is corrupted with partial writes"
    triggers:
      - type: event
        source: mcp/tools/cluster_write_handler.py:handle_cluster_write
        notes: "Triggered by citizen calling cluster_write MCP tool"
    frequency:
      expected_rate: 5-20/hour
      peak_rate: 100/hour
      burst_behavior: "Gemini rate limits may throttle; graph writes are in-process so no backpressure"
    risks:
      - "V2: Partial writes leave orphaned nodes (CRITICAL)"
      - "V3: Duplicate actors from platform-verified sources (CRITICAL)"
      - "V1: Moment not created despite success return (CRITICAL)"
    notes: "Pipeline has external dependency (Gemini API) and graph mutation — both need monitoring"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Atomic cluster creation | cluster_atomicity, gemini_extraction_success | If writes are not atomic, graph is corrupted. If Gemini fails, extraction degrades. |
| Identity resolution at write time | platform_dedup_accuracy | If platform dedup fails, actor graph becomes incoherent |
| Confidence-graded links | link_confidence_accuracy | If confidence grading is wrong, physics starts from bad initial conditions |

```yaml
health_indicators:
  - name: cluster_atomicity
    flow_id: cluster_write_pipeline
    priority: high
    rationale: "If clusters are not atomic, the graph accumulates orphaned nodes that pollute search and confuse physics"

  - name: gemini_extraction_success
    flow_id: cluster_write_pipeline
    priority: high
    rationale: "If Gemini fails silently or returns invalid JSON, entities are lost from moments"

  - name: platform_dedup_accuracy
    flow_id: cluster_write_pipeline
    priority: high
    rationale: "If platform-verified actors create duplicates, citizen identity graph becomes incoherent"

  - name: link_confidence_accuracy
    flow_id: cluster_write_pipeline
    priority: med
    rationale: "If confirmed entities get low weight or unconfirmed get high weight, physics initial conditions are wrong"
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: health_log
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-18T00:00:00Z
    source: cluster_atomicity
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: cluster_atomicity_checker
    purpose: "Verify no orphaned nodes exist from failed cluster_write operations (V2)"
    status: pending
    priority: high
  - name: gemini_extraction_checker
    purpose: "Verify Gemini returns valid structured JSON with entity fields (V7, B5)"
    status: pending
    priority: high
  - name: platform_dedup_checker
    purpose: "Verify no duplicate actors exist with same platform_id (V3)"
    status: pending
    priority: high
  - name: link_confidence_checker
    purpose: "Verify confirmed links have weight >= 1.0 and unconfirmed <= 0.5 (V4)"
    status: pending
    priority: med
```

---

## INDICATOR: cluster_atomicity

Every successful cluster_write must produce a complete cluster. Every failed cluster_write must leave zero traces.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: cluster_atomicity
  client_value: "Citizens trust that their moments are either fully recorded or not at all — no phantom nodes"
  validation:
    - validation_id: V1
      criteria: "Every successful cluster_write produces exactly one Moment node"
    - validation_id: V2
      criteria: "Failed cluster_write leaves no nodes or links"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: "No orphaned nodes detected, all recent clusters complete"
      WARN: "1-2 orphaned nodes found, may indicate intermittent write failures"
      ERROR: "Multiple orphaned nodes, cluster atomicity is broken"
  aggregation:
    method: worst-case
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_cluster_write
    type: graph_ops
    payload: {nodes_created: int, links_created: int, errors: list}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="cluster_atomicity",
    triggers=[
        triggers.cron.hourly(),
    ],
    on_problem="ORPHANED_CLUSTER_NODES",
    task="fix_orphaned_nodes",
)
def cluster_atomicity(ctx) -> dict:
    """Check for Moment nodes without CREATED links (orphaned from failed writes)."""
    orphans = ctx.graph_ops._query(
        "MATCH (m) WHERE m.node_type = 'moment' "
        "AND NOT ()-[:LINK {type: 'CREATED'}]->(m) "
        "RETURN count(m) as count"
    )
    count = orphans[0]["count"] if orphans else 0
    if count == 0:
        return Signal.healthy()
    if count <= 2:
        return Signal.degraded(details=f"{count} orphaned moments found")
    return Signal.critical(details=f"{count} orphaned moments — atomicity broken")
```

### SIGNALS

```yaml
signals:
  healthy: "Zero orphaned moments in graph"
  degraded: "1-2 orphaned moments (possible intermittent failure)"
  critical: "3+ orphaned moments (systematic atomicity failure)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.hourly
  max_frequency: 1/hour
  burst_limit: 1
  backoff: "No backoff — check is lightweight (single COUNT query)"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: health_log
      transport: file
      notes: "Persistent record for trend analysis"
display:
  locations:
    - surface: CLI
      location: "mind doctor"
      signal: OK/WARN/ERROR
      notes: "Shows in module health summary"
```

### MANUAL RUN

```yaml
manual_run:
  command: "mind doctor --check cluster_atomicity"
  notes: "Run after any cluster_write failures or graph maintenance"
```

---

## INDICATOR: platform_dedup_accuracy

No two actor nodes should share the same platform_id value.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: platform_dedup_accuracy
  client_value: "Citizens see one unified identity per platform account, not confusing duplicates"
  validation:
    - validation_id: V3
      criteria: "No two actor nodes have the same {platform}_id value"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary:
      1: "No duplicate platform IDs found"
      0: "Duplicate platform IDs detected — identity dedup is broken"
  aggregation:
    method: all-pass
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_entity_resolution
    type: graph_ops
    payload: {entity_name: string, match_result: ExistingMatch|null}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="platform_dedup_accuracy",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="DUPLICATE_PLATFORM_ACTORS",
    task="merge_duplicate_actors",
)
def platform_dedup_accuracy(ctx) -> dict:
    """Check for duplicate actors sharing the same platform ID."""
    platforms = ["telegram_id", "discord_id", "x_id", "email", "phone"]
    duplicates = []
    for field in platforms:
        dupes = ctx.graph_ops._query(
            f"MATCH (a) WHERE a.node_type = 'actor' AND a.{field} IS NOT NULL "
            f"WITH a.{field} AS pid, collect(a.id) AS actors "
            f"WHERE size(actors) > 1 RETURN pid, actors"
        )
        if dupes:
            duplicates.extend(dupes)
    if not duplicates:
        return Signal.healthy()
    return Signal.critical(details=f"{len(duplicates)} duplicate platform IDs: {duplicates[:5]}")
```

### SIGNALS

```yaml
signals:
  healthy: "No duplicate platform IDs across all actors"
  critical: "Duplicate platform IDs found — identity dedup has failed"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.daily
  max_frequency: 1/day
  burst_limit: 1
  backoff: "None — check is a single aggregation query"
```

### MANUAL RUN

```yaml
manual_run:
  command: "mind doctor --check platform_dedup_accuracy"
  notes: "Run after bulk imports or platform integration changes"
```

---

## HOW TO RUN

```bash
# Run all health checks for cluster_write
mind doctor --module cluster_write

# Run a specific checker
mind doctor --check cluster_atomicity
mind doctor --check platform_dedup_accuracy
```

---

## KNOWN GAPS

- `gemini_extraction_checker` is pending — needs Gemini response logging before it can verify extraction quality
- `link_confidence_checker` is pending — needs cluster_write implementation to exist before verifying weight values

<!-- @mind:todo Implement gemini_extraction_checker once response logging is in place -->
<!-- @mind:todo Implement link_confidence_checker once cluster_write_handler.py exists -->

---

## MARKERS

<!-- @mind:todo Create runtime/checks/cluster_write_checks.py with checker implementations -->
<!-- @mind:proposition Consider a "cluster integrity" dashboard that visualizes orphaned nodes over time -->
