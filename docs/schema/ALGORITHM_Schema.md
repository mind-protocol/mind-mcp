# Schema — Algorithm: Schema Loading and Validation Procedures

```
STATUS: STABLE (v1.3), DESIGNING (v1.6.1)
CREATED: 2025-12-23
UPDATED: 2025-12-26
VERIFIED: 2025-12-23 against check_health.py, test_schema.py (v1.3)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Schema.md
BEHAVIORS:      ./BEHAVIORS_Schema.md
PATTERNS:       ./PATTERNS_Schema.md
THIS:           ALGORITHM_Schema.md (you are here)
VALIDATION:     ./VALIDATION_Schema.md
IMPLEMENTATION: ./IMPLEMENTATION_Schema.md
HEALTH:         ./HEALTH_Schema.md
SYNC:           ./SYNC_Schema.md

IMPL:           mind/graph/health/check_health.py
                mind/graph/health/test_schema.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The schema module has two key algorithms:

1. **Schema Loading** — Load base schema, overlay project-specific constraints
2. **Graph Validation** — Check all nodes/links against loaded schema

Both are deterministic, no-LLM, and designed for fast execution on large graphs.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Extensible through layering | B6 | Schema loading merges base + project |
| Physics-ready structure | B3 | Validation enforces range constraints |
| Project-agnostic foundation | B1, B4 | Validation uses base rules first |

---

## DATA STRUCTURES

### Schema Definition (YAML)

```yaml
NodeBase:
  fields:
    id: {type: string, required: true}
    name: {type: string, required: true}
    node_type: {type: enum, values: [actor, space, thing, narrative, moment]}
    type: {type: string, required: true}  # free string
    weight: {type: float, range: [0, 1], default: 0.5}
    energy: {type: float, range: [0, 1], default: 0.0}

LinkBase:
  fields:
    type: {type: enum, values: [at, contains, leads_to, ...]}
    polarity: {type: float, range: [-1, 1], default: 0.0}
```

### Issue Report

```python
@dataclass
class Issue:
    node_type: str      # "Character", "BELIEVES", etc.
    node_id: str        # The failing node/link ID
    issue_type: str     # missing_required, invalid_enum, type_error
    field: str          # Which field failed
    message: str        # Human-readable error
    severity: str       # error, warning, info
```

---

## ALGORITHM: Schema Loading

### Step 1: Load Base Schema

Load `docs/schema/schema.yaml` as authoritative base.

```python
base = yaml.safe_load(BASE_SCHEMA_PATH)
schema = {'nodes': {}, 'links': {}, 'invariants': []}

for node_type, node_def in base['nodes'].items():
    schema['nodes'][node_type] = {
        'required': ['id', 'name'],
        'optional': [],
        'enums': {}
    }
```

### Step 2: Overlay Project Schema

Load `runtime/graph/health/schema.yaml` and merge.

```python
project = yaml.safe_load(PROJECT_SCHEMA_PATH)

for node_type, node_def in project['nodes'].items():
    if node_type not in schema['nodes']:
        schema['nodes'][node_type] = {}
    schema['nodes'][node_type].update(node_def)  # Project wins
```

### Step 3: Return Merged Schema

The result has base structure + project constraints.

---

## ALGORITHM: Graph Validation

### Step 1: Query All Nodes by Type

```cypher
MATCH (n:Character) RETURN n
MATCH (n:Place) RETURN n
MATCH (n:Thing) RETURN n
MATCH (n:Narrative) RETURN n
MATCH (n:Moment) RETURN n
```

### Step 2: Validate Each Node

For each node:

```python
def validate_node(node, node_type, schema, report):
    node_schema = schema['nodes'].get(node_type)

    # Check required fields
    for field in node_schema.get('required', []):
        if field not in node or node[field] is None:
            report.add_issue(Issue(..., issue_type="missing_required"))

    # Check enum values
    for field, valid_values in node_schema.get('enums', {}).items():
        if node.get(field) not in valid_values:
            report.add_issue(Issue(..., issue_type="invalid_enum"))
```

### Step 3: Count Links by Type

```cypher
MATCH ()-[r:BELIEVES]->() RETURN count(r)
MATCH ()-[r:AT]->() RETURN count(r)
...
```

### Step 4: Validate Link Structure

For critical links, verify from/to node types.

### Step 5: Generate Report

```python
return HealthReport(
    graph_name=graph.graph_name,
    total_nodes={...},
    total_links={...},
    issues=[...]
)
```

---

## KEY DECISIONS

### D1: Missing Required Field

```
IF field is in required AND (field not in node OR node[field] is None OR node[field] == ''):
    Add error issue
ELSE:
    Field is valid
```

### D2: Invalid Enum Value

```
IF field in enums AND node[field] not in valid_values:
    Add warning issue (not error — allows project flexibility)
ELSE:
    Value is valid
```

### D3: Unknown Node Type

```
IF node_type not in schema['nodes']:
    Add error issue "unknown_type"
    Skip further validation for this node
```

---

## DATA FLOW

```
docs/schema/schema.yaml (base)
    ↓
load_schema()
    ↓
mind/graph/health/schema.yaml (project overlay)
    ↓
merged schema dict
    ↓
check_graph_health(graph, schema)
    ↓
HealthReport
```

---

## COMPLEXITY

**Time:** O(N + L) where N = nodes, L = links — linear scan

**Space:** O(I) where I = issues found

**Bottlenecks:**
- Large graphs with many issues can generate verbose reports
- Cypher queries run sequentially (could parallelize by node type)

---

## HELPER FUNCTIONS

### `load_schema()`

**Purpose:** Merge base and project schemas

**Logic:** Load YAML, deep merge dicts, project wins on conflicts

### `validate_node(node, node_type, schema, report)`

**Purpose:** Check one node against schema

**Logic:** Required fields → enum values → add issues

### `get_nodes_missing_field(graph, node_type, field)`

**Purpose:** Find all nodes missing a specific field

**Logic:** Cypher query with IS NULL check

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `db.graph_ops.GraphOps` | `_query(cypher)` | Query results from FalkorDB |
| `yaml` | `safe_load()` | Parsed schema dict |
| `pathlib.Path` | `.exists()` | Check schema file exists |

---

## v1.6.1 ALGORITHM ADDITIONS

### Link Validation (v1.4.1+)

With single `linked` type, validation checks properties instead of type:

```python
def validate_link_v16(link, report):
    # Polarity is bidirectional array
    if not isinstance(link.get('polarity'), list) or len(link['polarity']) != 2:
        report.add_issue("polarity must be [a→b, b→a] array")

    # Polarity values in [0, 1]
    for i, p in enumerate(link.get('polarity', [0.5, 0.5])):
        if p < 0 or p > 1:
            report.add_issue(f"polarity[{i}]={p} outside [0, 1]")

    # Permanence in [0, 1]
    perm = link.get('permanence', 0.5)
    if perm < 0 or perm > 1:
        report.add_issue(f"permanence={perm} outside [0, 1]")

    # Emotions in [-1, +1]
    for axis in ['joy_sadness', 'trust_disgust', 'fear_anger', 'surprise_anticipation']:
        val = link.get(axis, 0)
        if val < -1 or val > 1:
            report.add_issue(f"{axis}={val} outside [-1, +1]")
```

### SubEntity Validation (v1.6)

SubEntity state machine constraints:

```python
def validate_subentity_transition(se, new_state, report):
    # Only branch on Moments
    if new_state == 'BRANCHING':
        pos = get_node(se.position)
        if pos.node_type != 'moment':
            report.add_issue("BRANCHING only allowed on Moment nodes")

    # Valid transitions
    valid = {
        'SEEKING': ['BRANCHING', 'RESONATING', 'REFLECTING'],
        'BRANCHING': ['REFLECTING'],
        'RESONATING': ['SEEKING', 'REFLECTING', 'MERGING'],
        'REFLECTING': ['CRYSTALLIZING', 'MERGING'],
        'CRYSTALLIZING': ['MERGING'],
        'MERGING': []  # terminal
    }

    if new_state not in valid.get(se.state, []):
        report.add_issue(f"Invalid transition {se.state} → {new_state}")
```

### Crystallization Validation (v1.6)

Narrative creation constraints:

```python
def validate_crystallization(se, narrative, existing_narratives, report):
    # Check novelty threshold
    for existing in existing_narratives:
        sim = cosine(narrative.embedding, existing.embedding)
        if sim > 0.85:
            report.add_issue(f"Narrative too similar to {existing.id} (sim={sim})")

    # Check path permanence
    avg_perm = mean([get_link(l).permanence for l in se.path])
    if avg_perm < 0.6:
        report.add_issue(f"Path permanence too low: {avg_perm} < 0.6")
```

### Link Score Computation (v1.6.1)

```python
def compute_link_score(se, link, direction):
    """Full link score with self_novelty and sibling_divergence"""
    semantic = cosine(se.intention_embedding, link.embedding)

    # Self-novelty: avoid backtracking
    if se.path:
        self_novelty = 1 - max(cosine(link.embedding, get_link(l).embedding) for l, _ in se.path)
    else:
        self_novelty = 1.0

    # Sibling divergence: avoid siblings' exploration space
    if se.siblings:
        sibling_divergence = 1 - max(cosine(link.embedding, s.crystallization_embedding) for s in se.siblings)
    else:
        sibling_divergence = 1.0

    return semantic * link.polarity[direction] * (1 - link.permanence) * self_novelty * sibling_divergence
```

### Crystallization Embedding Update (v1.6.1)

```python
def update_crystallization_embedding(se):
    """Called at EVERY step, not just at crystallization"""
    se.crystallization_embedding = weighted_sum([
        (0.4, se.intention_embedding),
        (0.3, get_node(se.position).embedding),
        (0.2, mean([get_node(n).embedding for n, _ in se.found_narratives]) if se.found_narratives else zero_vector()),
        (0.1, mean([get_link(l).embedding for l, _ in se.path]) if se.path else zero_vector())
    ])
```

### SubEntity Tree Validation (v1.6.1)

```python
def validate_subentity_tree(se, report):
    # Siblings must share parent
    if se.siblings:
        for sib in se.siblings:
            if sib.parent != se.parent:
                report.add_issue(f"Sibling {sib.id} has different parent")

    # Children must have this as parent
    for child in se.children:
        if child.parent != se:
            report.add_issue(f"Child {child.id} doesn't point to parent")

    # found_narratives must be tuples
    for item in se.found_narratives:
        if not isinstance(item, tuple) or len(item) != 2:
            report.add_issue(f"found_narratives item must be (id, alignment) tuple")
```

---

## MARKERS

<!-- @mind:todo Parallelize node type queries — currently sequential, could run in parallel for large graphs. -->

<!-- @mind:proposition Add --fix flag to check_health.py that applies safe auto-fixes (e.g., set default values for missing optional fields). Currently read-only. -->

<!-- @mind:escalation LINK_TYPE_VALIDATION: check_health.py counts links but doesn't validate valid_from/valid_to constraints from schema. Should it? Would catch semantic errors but adds complexity. -->

<!-- @mind:todo V16_LINK_VALIDATION: Implement validate_link_v16() for single linked type with bidirectional polarity. -->

<!-- @mind:todo V16_SUBENTITY_VALIDATION: Implement SubEntity state machine validation once SubEntity class exists. -->
