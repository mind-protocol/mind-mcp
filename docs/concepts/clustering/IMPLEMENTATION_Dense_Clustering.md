# IMPLEMENTATION: Dense Clustering

## File Structure

```
mind/
├── symbol_extractor.py       # Code symbol extraction (existing)
├── doc_extractor.py          # Document structure extraction (new)
├── cluster_builder.py        # Dense clustering coordinator (new)
└── cli.py                    # CLI integration

mind/
└── physics/graph/
    └── graph_ops.py          # Graph operations (existing)
```

## Core Components

### DocExtractor (mind/doc_extractor.py)

Parses document structure into extractable elements.

```python
class DocExtractor:
    """Extract structure from markdown documents."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def extract(self, doc_path: Path) -> DocStructure:
        """Parse doc and return structured content."""
        content = doc_path.read_text()

        return DocStructure(
            file_node=self._create_file_node(doc_path),
            yaml_blocks=self._extract_yaml_blocks(content),
            sections=self._extract_sections(content),
            markers=self._extract_markers(content),
            references=self._extract_references(content),
        )

    def _extract_yaml_blocks(self, content: str) -> List[dict]:
        """Find and parse ```yaml blocks."""
        ...

    def _extract_markers(self, content: str) -> List[Marker]:
        """Find @mind:todo, @mind:escalation, etc."""
        ...

    def _extract_references(self, content: str) -> List[Reference]:
        """Find file paths, symbol references, validation refs."""
        ...
```

### ClusterBuilder (mind/cluster_builder.py)

Coordinates dense clustering from extracted structure.

```python
class ClusterBuilder:
    """Build dense node clusters from document structure."""

    def __init__(self, graph_ops: GraphOps, space_resolver: SpaceResolver):
        self.graph_ops = graph_ops
        self.space_resolver = space_resolver

    def build_cluster(
        self,
        doc_structure: DocStructure,
        actor_id: str = "actor_SYSTEM_doctor"
    ) -> ClusterResult:
        """Build nodes and links from doc structure."""

        nodes = []
        links = []

        # 1. File node
        nodes.append(doc_structure.file_node)

        # 2. Definition nodes (health, validation, checker, etc.)
        for block in doc_structure.yaml_blocks:
            definition_nodes, definition_links = self._process_yaml_block(block)
            nodes.extend(definition_nodes)
            links.extend(definition_links)

        # 3. Marker nodes (TODO, escalation, proposition)
        for marker in doc_structure.markers:
            marker_node, marker_links = self._process_marker(marker)
            nodes.append(marker_node)
            links.extend(marker_links)

        # 4. Resolve references
        resolved_links = self._resolve_references(
            doc_structure.references, nodes
        )
        links.extend(resolved_links)

        # 5. Containment links
        space_id = self.space_resolver.get_space_for_doc(doc_structure.file_node)
        for node in nodes:
            links.append(Link(
                type='contains',
                from_id=space_id,
                to_id=node.id,
            ))

        # 6. Create moment
        moment, moment_links = self._create_moment(
            doc_structure.file_node, nodes, actor_id
        )
        nodes.append(moment)
        links.extend(moment_links)

        return ClusterResult(nodes=nodes, links=links)

    def upsert(self, result: ClusterResult) -> UpsertStats:
        """MERGE all nodes and links to graph."""
        stats = UpsertStats()

        for node in result.nodes:
            self._upsert_node(node)
            stats.nodes += 1

        for link in result.links:
            self._upsert_link(link)
            stats.links += 1

        return stats
```

### Data Classes

```python
@dataclass
class DocStructure:
    """Parsed document structure."""
    file_node: Node
    yaml_blocks: List[dict]
    sections: Dict[str, List[str]]
    markers: List[Marker]
    references: List[Reference]

@dataclass
class Marker:
    """Extracted marker (@mind:todo, etc.)."""
    type: str  # 'todo', 'escalation', 'proposition'
    content: str
    line: int
    references: List[str]  # extracted refs like "(V2)"

@dataclass
class Reference:
    """A reference to another entity."""
    target: str  # "V1", "check_health.py", etc.
    ref_type: str  # 'validation', 'file', 'symbol'
    context: str  # surrounding text

@dataclass
class ClusterResult:
    """Result of cluster building."""
    nodes: List[Node]
    links: List[Link]

@dataclass
class Node:
    """Graph node to upsert."""
    id: str
    node_type: str
    type: str
    properties: dict

@dataclass
class Link:
    """Graph link to upsert."""
    type: str
    from_id: str
    to_id: str
    properties: dict = field(default_factory=dict)
```

## YAML Block Processors

Each YAML block type has a processor:

```python
class HealthIndicatorProcessor:
    """Process health_indicators YAML blocks."""

    def process(self, block: dict) -> Tuple[List[Node], List[Link]]:
        nodes = []
        links = []

        for indicator in block.get('health_indicators', []):
            node_id = f"narrative_HEALTH_{slugify(indicator['name'])}"

            nodes.append(Node(
                id=node_id,
                node_type='narrative',
                type='health',
                properties={
                    'name': indicator['name'],
                    'priority': indicator.get('priority', 'med'),
                    'mechanism': indicator.get('mechanism', ''),
                }
            ))

            # Links to validations
            for v in indicator.get('verifies', []):
                links.append(Link(
                    type='relates',
                    from_id=node_id,
                    to_id=f"narrative_VALIDATION_{slugify(v)}",
                    properties={'direction': 'verifies'}
                ))

        return nodes, links


class DockProcessor:
    """Process docks YAML blocks."""

    def process(self, block: dict, parent_health_id: str) -> Tuple[List[Node], List[Link]]:
        nodes = []
        links = []

        for dock in block.get('docks', []):
            node_id = f"thing_DOCK_{slugify(dock['name'])}"

            nodes.append(Node(
                id=node_id,
                node_type='thing',
                type='dock',
                properties={
                    'name': dock['name'],
                    'direction': dock['direction'],
                    'uri': dock['uri'],
                    'line': dock.get('line'),
                }
            ))

            links.append(Link(
                type='attached_to',
                from_id=node_id,
                to_id=parent_health_id,
                properties={'direction': dock['direction']}
            ))

        return nodes, links
```

## CLI Integration

### Doctor Integration

```python
# In runtime/doctor.py

def doctor_command(dir, ..., extract_docs=True):
    """Run doctor with optional dense clustering."""

    if extract_docs:
        # Extract structure from all docs
        doc_extractor = DocExtractor(dir)
        cluster_builder = ClusterBuilder(graph_ops, space_resolver)

        for doc_path in find_docs(dir):
            structure = doc_extractor.extract(doc_path)
            result = cluster_builder.build_cluster(structure)
            cluster_builder.upsert(result)
            print(f"  {doc_path.name}: {len(result.nodes)} nodes, {len(result.links)} links")

    # Continue with health checks...
```

### Standalone Command

```python
# In mind/cli.py

cluster_parser = subparsers.add_parser(
    "cluster",
    help="Extract dense clusters from documents"
)
cluster_parser.add_argument("--doc", "-d", help="Single doc to extract")
cluster_parser.add_argument("--all", action="store_true", help="All docs")
cluster_parser.add_argument("--dry-run", action="store_true")
```

## Graph Queries

### Upsert Node

```cypher
MERGE (n {id: $id})
SET n += $props
SET n:$label
RETURN n.id
```

### Upsert Link

```cypher
MATCH (a {id: $from})
MATCH (b {id: $to})
MERGE (a)-[r:$rel_type]->(b)
SET r += $props
RETURN type(r)
```

### Find Stub Nodes

```cypher
MATCH (n) WHERE n.stub = true
RETURN n.id, n.type, n.name
```

### Coverage Query

```cypher
MATCH (v:Narrative {type: 'validation'})
OPTIONAL MATCH (h:Narrative {type: 'health'})-[:RELATES {direction: 'verifies'}]->(v)
RETURN v.name, count(h) as coverage
ORDER BY coverage ASC
```

## Entry Points

| Entry Point | Description |
|-------------|-------------|
| `mind doctor --cluster` | Extract docs during doctor scan |
| `mind cluster --doc X` | Extract single document |
| `mind cluster --all` | Extract all documents |
| `ClusterBuilder.build_cluster()` | Programmatic API |

## Related

- ALGORITHM_Dense_Clustering.md — Extraction logic
- VALIDATION_Dense_Clustering.md — Invariants
- mind/symbol_extractor.py — Code symbol extraction (similar pattern)
