# IMPLEMENTATION: Cluster Metrics

## Overview

The cluster metrics system provides three capabilities for ensuring dense, well-connected graph clusters:

1. **Connection Scoring** - Calculate links_per_node, external_ratio, orphan_score
2. **Valid Target Enforcement** - Validate link types match schema constraints
3. **Suggestion Engine** - Find existing nodes to link to

## File Locations

| Component | File | Purpose |
|-----------|------|---------|
| ClusterMetrics | `mind/cluster_metrics.py` | Main metrics class |
| ClusterValidator | `mind/cluster_metrics.py` | Combined validation |
| Protocol Integration | `mind/protocol_runner.py` | Auto-validation after create |

## Core Classes

### ConnectionScore

Metrics calculated for a cluster:

```python
@dataclass
class ConnectionScore:
    total_nodes: int = 0
    total_links: int = 0
    internal_links: int = 0      # Links within cluster
    external_links: int = 0      # Links to existing nodes
    links_per_node: float = 0.0  # total_links / total_nodes
    external_ratio: float = 0.0  # external_links / total_links
    orphan_count: int = 0        # Nodes with only 1 link
    verdict: str = "UNKNOWN"     # FAIL, SPARSE, ACCEPTABLE, GOOD, EXCELLENT
```

**Thresholds:**

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| links_per_node | 2.0 | 3.5 | 5.0+ |
| external_ratio | 30% | 50% | 70%+ |
| orphan_count | 0 | 0 | 0 |

### ClusterMetrics

Main class for metrics and validation:

```python
class ClusterMetrics:
    def score_cluster(nodes, links, existing_ids=None) -> ConnectionScore
    def validate_targets(node_type, links, nodes) -> TargetValidation
    def suggest_links(node_id, node_type, space_id) -> List[LinkSuggestion]
```

### ClusterValidator

Combines all checks into one validation:

```python
class ClusterValidator:
    def validate_cluster(primary_type, nodes, links, space_id) -> Dict:
        # Returns:
        # - valid: bool
        # - score: ConnectionScore
        # - target_validation: TargetValidation
        # - suggestions: List[LinkSuggestion]
        # - report: str (formatted report)
```

## Valid Target Rules

From `VALID_TARGETS` dict:

```python
VALID_TARGETS = {
    'narrative.health': {
        'verifies': {'target': ['narrative.validation'], 'min': 1},
        'checks': {'target': ['narrative.algorithm'], 'min': 1, 'max': 1},
        'supports': {'target': ['narrative.objective'], 'min': 0},
        'attached_to': {'source': ['thing.dock'], 'exactly': 2},
    },
    'narrative.validation': {
        'ensures': {'target': ['narrative.behavior'], 'min': 1},
        'elaborates': {'target': ['narrative.pattern'], 'min': 0, 'max': 1},
        'supports': {'target': ['narrative.objective'], 'min': 0},
    },
    'narrative.implementation': {
        'realizes': {'target': ['narrative.algorithm'], 'min': 1, 'max': 1},
        'follows': {'target': ['narrative.pattern'], 'min': 0},
        'attached_to': {'source': ['thing.dock'], 'min': 1},
    },
    'narrative.algorithm': {
        'implements': {'target': ['narrative.pattern'], 'min': 1, 'max': 1},
        'enables': {'target': ['narrative.behavior'], 'min': 1},
    },
    'narrative.behavior': {
        'serves': {'target': ['narrative.objective'], 'min': 1},
    },
    'narrative.pattern': {
        'achieves': {'target': ['narrative.objective'], 'min': 1},
        'enables': {'target': ['narrative.behavior'], 'min': 1},
    },
    'thing.dock': {
        'attached_to': {'target': ['narrative.health', 'narrative.implementation'], 'exactly': 1},
        'observes': {'target': ['thing.func', 'thing.method', 'thing.class'], 'min': 1, 'max': 1},
    },
}
```

## Protocol Integration

The `ProtocolRunner` automatically runs cluster validation after creation and includes metrics in the completion moment:

```python
class ProtocolRunner:
    def __init__(self, graph_ops=None, validate_cluster=True):
        # validate_cluster enables/disables auto-validation

    def run(self, protocol_path, actor_id, initial_context):
        # ... execute protocol ...

        if self.validate_cluster:
            validator = ClusterValidator(self.graph)
            result = validator.validate_cluster(...)
            # Builds cluster_summary for moment
            # Prints validation report
            # Adds errors if invalid

        # Create moment WITH cluster metrics in description
        self._create_completion_moment(on_complete, actor_id, cluster_summary)
```

### Moment Description Format

The completion moment's `text` field includes cluster metrics:

```
Added health indicator for space_physics | Cluster: 4 nodes, 9 links | 2.2 links/node | 67% external | ACCEPTABLE
```

This provides:
- **Audit trail** - Quality metrics captured at creation time
- **Queryable** - Find clusters by searching moment text for verdict
- **Context** - Future agents understand cluster's initial state

### Moment NEXT Chain

Each moment is linked to the actor's previous moment via `NEXT`:

```
(actor)-[:EXPRESSES]->(moment_1)
(actor)-[:EXPRESSES]->(moment_2)
(moment_1)-[:NEXT]->(moment_2)
```

This creates a temporal chain of actions per agent, enabling:
- **History traversal** - Follow NEXT links to see action sequence
- **Timeline queries** - Find what happened before/after a specific action
- **Agent activity** - Reconstruct full protocol execution history

The `ProtocolResult` includes validation data:

```python
@dataclass
class ProtocolResult:
    success: bool
    nodes_created: List[str]
    links_created: int
    # ... standard fields ...
    connection_score: Optional[ConnectionScore]
    validation_report: str
    suggestions: List[LinkSuggestion]
```

## Usage Examples

### Score a Cluster

```python
from mind.cluster_metrics import ClusterMetrics

metrics = ClusterMetrics(graph_ops)

nodes = ['health_test', 'dock_input', 'dock_output', 'moment']
links = [
    {'from': 'space', 'to': 'health_test', 'type': 'contains'},
    {'from': 'health_test', 'to': 'validation', 'type': 'relates',
     'properties': {'direction': 'verifies'}},
    # ...
]

score = metrics.score_cluster(nodes, links)
print(metrics.format_score(score))
```

### Validate Link Targets

```python
result = metrics.validate_targets('narrative.health', links, node_defs)

if not result.valid:
    for error in result.errors:
        print(f"Error: {error}")
```

### Get Link Suggestions

```python
suggestions = metrics.suggest_links(
    node_id='health_new',
    node_type='narrative.health',
    space_id='space_MODULE_physics',
    exclude_ids={'already_linked_id'}
)

for s in suggestions:
    print(f"[{s.direction}] -> {s.target_name} ({s.reason})")
```

### Full Validation

```python
from mind.cluster_metrics import ClusterValidator

validator = ClusterValidator(graph_ops)

result = validator.validate_cluster(
    'narrative.health',
    nodes_created,
    links_created,
    space_id
)

print(result['report'])

if not result['valid']:
    for err in result['target_validation'].errors:
        print(f"Fix: {err}")
```

## Output Format

### Validation Report

```
╔══════════════════════════════════════════════════════════════╗
║                  CLUSTER VALIDATION REPORT                   ║
╚══════════════════════════════════════════════════════════════╝

Primary Node Type: narrative.health
Nodes Created: 4
Links Created: 9

NODES:
  - health_test
  - dock_input
  - dock_output
  - moment_create

LINKS:
  - about: 1
  - attached_to: 2
  - verifies: 1
  - ...

CONNECTION SCORE
========================================
Nodes: 4
Links: 9 (internal: 3, external: 6)
Links/node: 2.2 (min: 2.0, good: 3.5+)
External ratio: 67% (min: 30%, good: 50%+)
Orphan nodes: 0

VERDICT: ACCEPTABLE
========================================

TARGET VALIDATION:
  ✓ All link targets valid

============================================================
RESULT: ✓ CLUSTER VALID - Ready to commit
============================================================
```

## Design Decisions

### Why These Thresholds?

From `SKILL_Add_Cluster_Dynamic_Creation.md`:

- **2.0 links/node minimum**: Every node needs at least containment + one semantic link
- **3.5 links/node good**: Typical well-connected cluster
- **30% external ratio**: At least 1/3 of links should connect to existing graph
- **0 orphans**: Every node must be reachable

### Why Separate Internal vs External?

- **Internal links**: Within the cluster (dock -> health)
- **External links**: To pre-existing nodes (health -> validation)

High external ratio means the cluster is well-integrated with the existing graph. Low ratio means isolated.

### Why Track Primary Node Type?

Validation rules differ by type. Health indicators need exactly 2 docks. Validations need at least 1 behavior link. The primary type (first non-moment, non-dock node) determines which rules apply.

## Related

- `SKILL_Add_Cluster_Dynamic_Creation.md` - Full specification
- `mind/protocol_validator.py` - Cluster template validation
- `mind/protocol_runner.py` - Protocol execution with metrics
