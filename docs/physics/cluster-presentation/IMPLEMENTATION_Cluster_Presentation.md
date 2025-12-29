# Cluster Presentation Implementation

```
STATUS: STABLE (v1.9.1)
UPDATED: 2025-12-26
```

## Overview

Implementation of the cluster presentation system that transforms raw exploration clusters into readable, actionable Markdown presentations.

**v1.9.1**: Added content blocks — each node in path displays its content in a ``` block after synthesis.

---

## File Locations

| File | Purpose |
|------|---------|
| `runtime/physics/cluster_presentation.py` | Core presentation logic |
| `runtime/physics/synthesis_unfold.py` | Synthesis to prose conversion |
| `runtime/physics/__init__.py` | Exports (v1.9 additions) |
| `runtime/tests/test_cluster_presentation.py` | Tests (34 cases) |

---

## Core Classes

### Data Structures

```python
# runtime/physics/cluster_presentation.py

@dataclass
class ClusterNode:
    id: str
    node_type: str
    name: str
    synthesis: str
    embedding: List[float]
    weight: float
    energy: float
    status: Optional[str]
    type: Optional[str]
    content: Optional[str]  # v1.9.1: Node content for display in path

@dataclass
class ClusterLink:
    id: str
    source_id: str
    target_id: str
    synthesis: str
    embedding: List[float]
    weight: float
    energy: float
    permanence: float
    trust_disgust: float

@dataclass
class RawCluster:
    nodes: List[ClusterNode]
    links: List[ClusterLink]
    traversed_link_ids: Set[str]

@dataclass
class PresentedCluster:
    markdown: str
    nodes: List[ClusterNode]
    links: List[ClusterLink]
    stats: ClusterStats
    responses: List[ClusterNode]
    tensions: List[ClusterNode]
    convergences: List[ClusterNode]
    gaps: List[Gap]
    available_details: List[str]
```

### Synthesis Parsing

```python
# runtime/physics/synthesis_unfold.py

@dataclass
class ParsedNodeSynthesis:
    prefixes: List[str]      # Emotion prefixes
    name: str                # Core name
    energy: str              # Energy level
    status: Optional[str]    # Status

@dataclass
class ParsedLinkSynthesis:
    pre_modifiers: List[str]   # Before verb
    verb: str                  # Base verb
    post_modifiers: List[str]  # After verb
```

---

## Key Functions

### Point of Interest Detection

```python
find_direct_response(nodes, intention_type, query_embedding) -> List[ClusterNode]
find_convergences(nodes, links) -> List[ClusterNode]
find_tensions(nodes, links) -> List[ClusterNode]
find_divergences(nodes, links, traversed_link_ids) -> List[ClusterNode]
find_gaps(nodes, links, intention_type) -> List[Gap]
```

### Path Building

```python
build_main_path(start_id, response_nodes, links, intention_embedding) -> List[List[str]]
get_path_node_ids(paths, links) -> Set[str]
```

### Scoring and Selection

```python
score_node(node, response_ids, main_path_ids, ...) -> float
select_nodes(nodes, links, responses, ..., max_nodes=30) -> List[ClusterNode]
filter_links(links, presented_node_ids) -> List[ClusterLink]
```

### Synthesis Unfolding

```python
parse_node_synthesis(synthesis) -> ParsedNodeSynthesis
parse_link_synthesis(synthesis) -> ParsedLinkSynthesis
unfold_node(synthesis, node_type, lang) -> str
unfold_link(synthesis, target_name, lang) -> str
unfold_node_link_node(source_name, link_synthesis, target_name, lang) -> str
```

### Content Block Formatting (v1.9.1)

```python
format_content_block(content: Optional[str], indent: str = "") -> List[str]
format_path_tree(path, nodes, links, response_ids, branching_ids) -> str
format_branching(node, outgoing_links, targets) -> str
```

### Main Entry Point

```python
present_cluster(
    raw_cluster: RawCluster,
    query: str,
    intention: str,
    intention_type: IntentionType,
    query_embedding: List[float],
    intention_embedding: List[float],
    start_id: str,
    max_nodes: int = 30,
) -> PresentedCluster
```

---

## Integration with ExplorationRunner

After running exploration, call `present_cluster`:

```python
from mind.physics import (
    ExplorationRunner,
    present_cluster,
    cluster_from_dicts,
    IntentionType,
)

# Run exploration
runner = ExplorationRunner(graph, config)
exploration_result = await runner.explore(
    actor_id='actor_edmund',
    query='Events in Great Hall',
    query_embedding=embed(query),
    intention='Find what Edmund can do',
    intention_embedding=embed(intention),
    intention_type='find_next',
)

# Convert to raw cluster
raw_cluster = cluster_from_dicts(
    nodes=exploration_result.traversed_nodes,
    links=exploration_result.traversed_links,
    traversed_link_ids=exploration_result.traversed_link_ids,
)

# Present
presented = present_cluster(
    raw_cluster=raw_cluster,
    query='Events in Great Hall',
    intention='Find what Edmund can do',
    intention_type=IntentionType.FIND_NEXT,
    query_embedding=embed(query),
    intention_embedding=embed(intention),
    start_id='actor_edmund',
)

print(presented.markdown)
```

---

## Markdown Output Format

**v1.9.1**: Each node in the path now includes its content in a ``` block.

```markdown
**Query:** "Events in Great Hall"

**Intention:** "Find what Edmund can do"

---

### Response

the Choice of Edmund (possible)

---

### Path

Edmund, intensely present (central)
\`\`\`
Edmund surveys the Great Hall, weighing his options.
\`\`\`
  │
  └─ definitely challenges, with sadness
     │
     ▼
the Confrontation, burning (ongoing)
\`\`\`
Gloucester confronts Edmund with the truth.
\`\`\`
  │
  └─ probably leads to, inevitably
     │
     ▼
the Choice of Edmund (possible)  ◆ RESPONSE
\`\`\`
Edmund must choose: confess or persist.
\`\`\`

---

### Branching (if multiple outgoing links)

the Confrontation, burning (ongoing)  ◆ BRANCHING
\`\`\`
Gloucester confronts Edmund with the truth.
\`\`\`
  │
  ├── probably leads to → the Choice (possible)
  │   \`\`\`
  │   Edmund must choose: confess or persist.
  │   \`\`\`
  │
  └── possibly triggers → the Escape (possible)
      \`\`\`
      Edmund considers fleeing before the truth emerges.
      \`\`\`

---

### Tensions

⚡ On **the Confrontation**:

| Source | Relation |
|--------|----------|
| the Revelation | suddenly establishes |
| Edmund | clearly believes, with disgust |

---

### Cluster Stats

- Nodes traversed: 150
- Nodes presented: 24
- Links traversed: 200
- Links presented: 30
```

---

## Language Support

Both French and English are supported for synthesis unfolding:

```python
# French (default)
unfold_node(synthesis, node_type='narrative', lang='fr')

# English
unfold_node(synthesis, node_type='narrative', lang='en')
```

Adjective → adverb and verb → participle conversions use lookup tables for common cases, with grammatical rules as fallback.

---

## Test Coverage

34 tests in `runtime/tests/test_cluster_presentation.py`:

- Point of interest detection (9 tests)
- Path building (1 test)
- Synthesis parsing (5 tests)
- Adverb/participle conversion (4 tests)
- Unfolding (2 tests)
- Compact forms (2 tests)
- Full presentation (3 tests)
- Cluster from dicts (1 test)
- Markers (1 test)
- **Content blocks (6 tests)** — v1.9.1

---

## Related Documents

- PATTERNS_Cluster_Presentation.md — Design patterns
- ALGORITHM_Cluster_Presentation.md — Selection and formatting algorithms
- docs/physics/PATTERNS_Physics.md (P11) — SubEntity exploration
- docs/schema/schema.yaml (v1.8) — Query/intention fields
