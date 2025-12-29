# OBJECTIVES: MCP Tools

```
STATUS: V2
PURPOSE: Graph query interface for agents
```

---

## Goals (Ranked)

| Rank | Goal | Rationale |
|------|------|-----------|
| 1 | **Semantic search only** | No Cypher queries at runtime. Embedding-based search. Graph physics does the work. |
| 2 | **Two graphs, same interface** | Local graph OR membrane graph. Same query format. |
| 3 | **Context is automatic** | Agent doesn't provide context. System derives from conversation, actor, history. |
| 4 | **Queries as array** | Multiple questions in one call. Batch for efficiency. |
| 5 | **Read-only for agents** | Agents query. Mutations via procedures/skills only. |
| 6 | **Cross-org via membrane** | Public nodes visible across orgs through membrane graph. |

---

## Tradeoffs

| If... | Then... | Because... |
|-------|---------|------------|
| Query is ambiguous | Return broad results | Agent refines with follow-up |
| No matches found | Return empty, not error | Absence is valid information |
| Membrane slow | Local still fast | Graphs are independent |

---

## Non-Goals

- **Cypher access** — No raw queries, embedding search only
- **GraphOps for agents** — No create/update/delete directly
- **Merged results** — Local OR membrane, not both combined
- **Intent types** — System infers, agent doesn't specify
- **Context parameter** — Automatic, not provided

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Query latency | < 2s for local, < 5s for membrane |
| Result relevance | Top-3 contains answer 80% of time |
| Zero Cypher leaks | No raw queries in agent code |

---

## CHAIN

- **Next:** PATTERNS_MCP_Tools.md
- **Validates:** VALIDATION_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
