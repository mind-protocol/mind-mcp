# PATTERNS: MCP Tools

```
STATUS: V2
PURPOSE: Design patterns for graph query tools
```

---

## Core Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| P1 | **Embedding search** | All queries use vector similarity. No Cypher at runtime. |
| P2 | **Graph physics** | Energy propagation finds relevant nodes. Follow links, don't query them. |
| P3 | **Two tools** | `graph_query` for local, `membrane_query` for cross-org. |
| P4 | **Queries array** | Multiple questions per call. System processes in parallel. |
| P5 | **Automatic context** | Actor, conversation history, current space — derived, not provided. |
| P6 | **Read-only** | Agents read via queries. Mutations via procedures only. |
| P7 | **Public broadcast** | Nodes with `public: true` mirror to membrane graph. |

---

## Architecture

```
Agent
  │
  │ graph_query(queries=["..."])
  ▼
MCP Server
  │
  ├─► LOCAL: GraphQueries.search()
  │       │
  │       └─► Embedding search on local FalkorDB
  │
  └─► MEMBRANE: MembraneQueries.search()
          │
          └─► Embedding search on membrane FalkorDB
```

---

## Tools

### graph_query

Query local graph.

```python
graph_query(
    queries=["What experts exist?", "Find ML work"]
)
```

**Input:**
- `queries`: Array of natural language questions

**Output:**
- Results per query with node matches, similarity scores

### membrane_query

Query cross-org membrane graph.

```python
membrane_query(
    queries=["Find AI specialists across orgs"]
)
```

**Input:**
- `queries`: Array of natural language questions

**Output:**
- Results with org_id, node matches from public nodes

---

## What Agents Cannot Do

| Action | Why Not | Alternative |
|--------|---------|-------------|
| `GraphOps.create_node()` | Direct mutation | Use procedures |
| `GraphQueries._query()` | Raw Cypher | Use semantic search |
| Specify context | Automatic | System derives |
| Specify intent | Automatic | System infers |
| Merge local + membrane | Separate concerns | Query each separately |

---

## Anti-Patterns

| Don't | Instead |
|-------|---------|
| Pass Cypher strings | Use natural language queries |
| Provide context parameter | Let system derive |
| Combine local + membrane | Query one or the other |
| Create nodes directly | Use procedures/skills |
| Query with intent types | Let system infer |

---

## CHAIN

- **Prev:** OBJECTIVES_MCP_Tools.md
- **Next:** BEHAVIORS_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
