# HEALTH: Dense Clustering

## Health Indicators

### H-CLUSTER-EXTRACTION-SUCCESS

**What:** Document extraction completes without errors.

**Priority:** HIGH

**Mechanism:**
```python
def check_extraction_success(doc_path):
    try:
        structure = doc_extractor.extract(doc_path)
        result = cluster_builder.build_cluster(structure)
        return HealthResult(
            status='healthy',
            nodes_created=len(result.nodes),
            links_created=len(result.links),
        )
    except Exception as e:
        return HealthResult(
            status='error',
            error=str(e),
        )
```

**Thresholds:**
- healthy: Extraction completes, nodes > 0
- warning: Extraction completes, nodes = 0 (empty doc?)
- error: Extraction throws exception

**Verifies:** V-CLUSTER-FILE-NODE

### H-CLUSTER-ID-COLLISION

**What:** No duplicate node IDs after extraction.

**Priority:** CRITICAL

**Mechanism:**
```cypher
MATCH (n)
WITH n.id as id, count(*) as cnt
WHERE cnt > 1
RETURN id, cnt
```

**Thresholds:**
- healthy: 0 collisions
- error: 1+ collisions

**Verifies:** V-CLUSTER-ID-UNIQUE

### H-CLUSTER-MOMENT-CREATED

**What:** Every extraction creates a provenance moment.

**Priority:** HIGH

**Mechanism:**
```cypher
MATCH (m:Moment {type: 'ingest'})
WHERE m.created_at_s > $since
RETURN count(m) as recent_moments
```

**Thresholds:**
- healthy: Moments created for each extraction
- warning: Some extractions missing moments
- error: No moments created

**Verifies:** V-CLUSTER-PROVENANCE

### H-CLUSTER-ORPHAN-NODES

**What:** All extracted nodes belong to a space.

**Priority:** MED

**Mechanism:**
```cypher
MATCH (n:Narrative) WHERE n.type IN ['health', 'validation', 'todo', 'escalation']
WHERE NOT (s:Space)-[:CONTAINS]->(n)
RETURN count(n) as orphans
```

**Thresholds:**
- healthy: 0 orphans
- warning: 1-5 orphans
- error: 6+ orphans

**Verifies:** V-CLUSTER-CONTAINMENT

### H-CLUSTER-STUB-COUNT

**What:** Number of unresolved stub nodes.

**Priority:** MED

**Mechanism:**
```cypher
MATCH (n) WHERE n.stub = true
RETURN count(n) as stubs, collect(n.id) as stub_ids
```

**Thresholds:**
- healthy: 0-5 stubs (some expected during incremental build)
- warning: 6-20 stubs
- error: 21+ stubs (too many unresolved references)

**Verifies:** V-CLUSTER-STUB-MARKED, V-CLUSTER-REFERENCE-RESOLVED

### H-CLUSTER-DOCK-ATTACHED

**What:** All docks are attached to health indicators.

**Priority:** HIGH

**Mechanism:**
```cypher
MATCH (d:Thing {type: 'dock'})
WHERE NOT (d)-[:ATTACHED_TO]->(:Narrative {type: 'health'})
RETURN d.name as unattached_dock
```

**Thresholds:**
- healthy: 0 unattached docks
- error: 1+ unattached docks

**Verifies:** V-CLUSTER-DOCK-ATTACHMENT

### H-CLUSTER-UPSERT-STABLE

**What:** Re-extraction doesn't create duplicates.

**Priority:** CRITICAL

**Mechanism:**
```python
def check_upsert_stability(doc_path):
    # Count before
    before = graph.query("MATCH (n) RETURN count(n)")[0]

    # Extract twice
    cluster_builder.extract_and_upsert(doc_path)
    cluster_builder.extract_and_upsert(doc_path)

    # Count after
    after = graph.query("MATCH (n) RETURN count(n)")[0]

    # Should be same (second run is pure update)
    return before == after
```

**Thresholds:**
- healthy: Node count stable after re-extraction
- error: Node count increases (duplicates created)

**Verifies:** V-CLUSTER-UPSERT-IDEMPOTENT

## Docks

### Input Docks

| Dock | URI | Line | Direction |
|------|-----|------|-----------|
| doc_files | `runtime/doc_extractor.py::DocExtractor.extract` | — | input |
| yaml_parser | `runtime/doc_extractor.py::_extract_yaml_blocks` | — | input |
| marker_parser | `runtime/doc_extractor.py::_extract_markers` | — | input |

### Output Docks

| Dock | URI | Line | Direction |
|------|-----|------|-----------|
| cluster_result | `runtime/cluster_builder.py::ClusterBuilder.build_cluster` | — | output |
| upsert_stats | `runtime/cluster_builder.py::ClusterBuilder.upsert` | — | output |

## Checkers

| Checker | Status | Priority | Implementation |
|---------|--------|----------|----------------|
| cluster_health_check | PENDING | HIGH | `runtime/cluster_health.py::check_all` |
| cluster_coverage_query | PENDING | MED | Graph query in doctor |
| cluster_stability_test | PENDING | HIGH | `tests/test_cluster_stability.py` |

## Flow

```yaml
flow_id: dense_clustering_validation
name: "Dense Clustering Health"
triggers:
  - "manual: mind doctor --cluster"
  - "schedule: daily"
frequency: "1/day expected"

steps:
  1. Extract all docs
  2. Run H-CLUSTER-* checks
  3. Report coverage gaps
  4. Flag stub nodes for resolution
```

## Markers

@mind:todo Implement ClusterBuilder class
@mind:todo Add cluster health checks to doctor
@mind:todo Create stability tests

## Related

- VALIDATION_Dense_Clustering.md — Invariants being verified
- IMPLEMENTATION_Dense_Clustering.md — Code locations for docks
