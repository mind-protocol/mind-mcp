# ALGORITHM: Dense Clustering

## Overview

Dense clustering extracts structure from documents into graph nodes and links. One document becomes many nodes with explicit relationships.

## Main Extraction Flow

```
extract_document(doc_path):
    1. Create file node for the document itself
    2. Parse document structure
    3. Extract definitions (health, validation, checker, etc.)
    4. Extract markers (TODO, escalation, proposition)
    5. Resolve references (find or create targets)
    6. Create links (all relationships)
    7. Create moment (provenance)
    8. Upsert all to graph
```

## Phase 1: Create File Node

```yaml
# For every doc
- id: "thing_FILE_{slugify(path)}"
  node_type: thing
  type: file
  name: "{filename}"
  uri: "{relative_path}"
  lines: {line_count}
  language: markdown
  last_modified_s: {mtime}
```

## Phase 2: Parse Document Structure

### YAML Block Extraction

```python
def extract_yaml_blocks(content):
    """Find all ```yaml ... ``` blocks and parse them."""
    pattern = r'```yaml\n(.*?)\n```'
    for match in re.finditer(pattern, content, re.DOTALL):
        yield yaml.safe_load(match.group(1))
```

### Header Section Detection

```python
def extract_sections(content):
    """Extract ## Header sections."""
    sections = {}
    current = None
    for line in content.split('\n'):
        if line.startswith('## '):
            current = line[3:].strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    return sections
```

### Marker Extraction

```python
def extract_markers(content):
    """Extract @mind:type markers."""
    patterns = {
        'todo': r'@mind:todo\s+(.+)',
        'escalation': r'@mind:escalation\s+(.+)',
        'proposition': r'@mind:proposition\s+(.+)',
    }
    markers = []
    for type, pattern in patterns.items():
        for match in re.finditer(pattern, content):
            markers.append({
                'type': type,
                'content': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
    return markers
```

## Phase 3: Extract Definitions

### Health Indicators

```yaml
# Input YAML in doc:
health_indicators:
  - name: schema_compliance
    priority: high
    mechanism: "Query all nodes..."
    verifies: [V1, V6]

# Output node:
- id: "narrative_HEALTH_schema-compliance"
  node_type: narrative
  type: health
  name: "schema_compliance"
  priority: high
  mechanism: "Query all nodes..."
```

### Docks

```yaml
# Input YAML in doc:
docks:
  - name: dock_graph_connection
    direction: input
    uri: "mind/graph/health/check_health.py::GraphOps._query"
    line: 272

# Output node:
- id: "thing_DOCK_schema-compliance-input"
  node_type: thing
  type: dock
  name: "dock_graph_connection"
  direction: input
  uri: "mind/graph/health/check_health.py::GraphOps._query"
  line: 272
```

### Checkers

```yaml
# Input YAML in doc:
checkers:
  - name: check_health_cli
    status: active
    priority: high
    implemented_by: "mind/graph/health/check_health.py"

# Output node:
- id: "narrative_CHECKER_check-health-cli"
  node_type: narrative
  type: checker
  name: "check_health_cli"
  status: active
  priority: high
```

## Phase 4: Extract Markers

```python
def markers_to_nodes(markers, doc_id):
    nodes = []
    for marker in markers:
        node_id = f"narrative_{marker['type'].upper()}_{slugify(marker['content'][:50])}"
        nodes.append({
            'id': node_id,
            'node_type': 'narrative',
            'type': marker['type'],
            'content': marker['content'],
            'source_doc': doc_id,
            'source_line': marker['line'],
        })
    return nodes
```

## Phase 5: Resolve References

```python
def resolve_reference(ref_name, ref_type, existing_nodes):
    """Find or create referenced node."""
    expected_id = f"narrative_{ref_type.upper()}_{slugify(ref_name)}"

    # Check if exists
    if expected_id in existing_nodes:
        return expected_id, False  # exists, not created

    # Create stub
    stub = {
        'id': expected_id,
        'node_type': 'narrative',
        'type': ref_type,
        'name': ref_name,
        'stub': True,  # mark as stub for later resolution
    }
    return expected_id, stub
```

### Reference Patterns

| Pattern | Target Type |
|---------|-------------|
| "verifies V1" | narrative_VALIDATION |
| "implements PATTERNS_X" | thing_FILE |
| "at check_health.py:272" | thing_FILE + line |
| "blocks OBJ-1" | narrative_OBJECTIVE |
| "(V2)" in TODO | narrative_VALIDATION |

## Phase 6: Create Links

### Containment Links

```python
def create_containment_links(nodes, space_id):
    """All extracted nodes belong to the module's space."""
    links = []
    for node in nodes:
        links.append({
            'type': 'contains',
            'from': space_id,
            'to': node['id'],
        })
    return links
```

### Relationship Links

```python
def create_relationship_links(definitions):
    """Create links from parsed relationships."""
    links = []

    # Health verifies Validation
    for health in definitions.get('health_indicators', []):
        for v in health.get('verifies', []):
            links.append({
                'type': 'relates',
                'from': health['id'],
                'to': f"narrative_VALIDATION_{slugify(v)}",
                'direction': 'verifies',
            })

    # Dock attached to Health
    for dock in definitions.get('docks', []):
        links.append({
            'type': 'attached_to',
            'from': dock['id'],
            'to': dock['attached_to'],
            'direction': dock['direction'],
        })

    # Checker implemented by File
    for checker in definitions.get('checkers', []):
        if 'implemented_by' in checker:
            links.append({
                'type': 'relates',
                'from': checker['id'],
                'to': f"thing_FILE_{slugify(checker['implemented_by'])}",
                'direction': 'implemented_by',
            })

    return links
```

### Marker Reference Links

```python
def create_marker_links(markers):
    """Extract references from marker content."""
    links = []

    # Pattern: "(V2)" or "V2" reference
    validation_pattern = r'\(?(V\d+)\)?'

    for marker in markers:
        for match in re.finditer(validation_pattern, marker['content']):
            links.append({
                'type': 'relates',
                'from': marker['id'],
                'to': f"narrative_VALIDATION_{match.group(1)}",
                'direction': 'about',
            })

    return links
```

## Phase 7: Create Moment

```python
def create_extraction_moment(doc_id, nodes, actor_id):
    """Record this extraction event."""
    timestamp = int(time.time())
    moment_id = f"moment_INGEST_{slugify(doc_id)}-{timestamp}"

    moment = {
        'id': moment_id,
        'node_type': 'moment',
        'type': 'ingest',
        'text': f"Ingested {doc_id}: {len(nodes)} nodes",
        'status: "completed",
        'created_at_s': timestamp,
    }

    links = [
        # Actor expresses moment
        {'type': 'expresses', 'from': actor_id, 'to': moment_id},
    ]

    # Moment about all created nodes
    for node in nodes:
        links.append({
            'type': 'about',
            'from': moment_id,
            'to': node['id'],
        })

    return moment, links
```

## Phase 8: Upsert to Graph

```python
def upsert_all(nodes, links, graph_ops):
    """MERGE all nodes and links."""

    for node in nodes:
        # MERGE by ID, update properties
        query = """
        MERGE (n {id: $id})
        SET n += $props
        SET n:$label
        """
        graph_ops.query(query, {
            'id': node['id'],
            'props': node,
            'label': node_type_to_label(node['node_type']),
        })

    for link in links:
        # MERGE relationship
        query = """
        MATCH (a {id: $from})
        MATCH (b {id: $to})
        MERGE (a)-[r:$rel_type]->(b)
        SET r += $props
        """
        graph_ops.query(query, {
            'from': link['from'],
            'to': link['to'],
            'rel_type': link['type'].upper(),
            'props': {k:v for k,v in link.items() if k not in ('from','to','type')},
        })
```

## Complete Example

**Input:** HEALTH_Schema.md

```markdown
## Health Indicators

```yaml
health_indicators:
  - name: schema_compliance
    priority: high
    verifies: [V1, V6]
```

## Docks

```yaml
docks:
  - name: input_dock
    direction: input
    uri: "check_health.py::query"
    line: 272
```

<!-- @mind:todo Add physics range checks (V2) -->
```

**Output:**

Nodes (7):
1. `thing_FILE_docs-schema-HEALTH-Schema-md`
2. `narrative_HEALTH_schema-compliance`
3. `narrative_VALIDATION_V1` (stub if not exists)
4. `narrative_VALIDATION_V6` (stub if not exists)
5. `thing_DOCK_input-dock`
6. `narrative_TODO_add-physics-range-checks`
7. `moment_INGEST_health-schema-{ts}`

Links (10):
1. contains: space → file
2. contains: space → health
3. verifies: health → V1
4. verifies: health → V6
5. attached_to: dock → health
6. contains: space → todo
7. about: todo → V2
8. expresses: actor → moment
9. about: moment → file
10. about: moment → health (+ more)

## Related

- PATTERNS_Dense_Clustering.md — Design principles
- IMPLEMENTATION_Dense_Clustering.md — Code location
- VALIDATION_Dense_Clustering.md — What must hold
