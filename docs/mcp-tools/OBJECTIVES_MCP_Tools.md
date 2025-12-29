# OBJECTIVES: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Use-case oriented graph interaction with workflow guidance
```

---

## Goals (Ranked)

| Rank | ID | Goal | Rationale |
|------|----|----|-----------|
| 1 | G1 | **Dense clusters, not sparse nodes** | Work creates richly linked subgraphs. Single isolated nodes are useless — meaning emerges from relationships. |
| 2 | G2 | **Use-case oriented** | Agent thinks in work ("add health coverage"), not node types ("create narrative node"). The system maps intent to structure. |
| 3 | G3 | **Workflow guided** | Protocols tell *when* to do things, membranes tell *how*. Agent follows choreographed sequences, not ad-hoc decisions. |
| 4 | G4 | **Context-rich** | Agent queries graph before deciding, describes after. Every step can enrich understanding. |
| 5 | G5 | **Traceable** | Every action creates moments with agent prose. The graph records *why*, not just *what*. |
| 6 | G6 | **Dependency aware** | Missing prerequisites trigger sub-work. Can't add health coverage without validations → spawn add_invariant first. |

---

## Tradeoffs

| If... | Then sacrifice... | Because... |
|-------|------------------|------------|
| Steps are slow (too many questions) | Some context richness | Agent productivity matters |
| Clusters are too large | Some linking density | Graph remains navigable |
| Dependency chains get deep | Spawn depth limits | Avoid infinite recursion |

---

## Non-Goals

- **Dynamic protocol generation** — v1 uses static protocol definitions
- **Parallel membranes** — v1 is sequential
- **Approval workflows** — v1 creates directly, no human-in-loop gating
- **Undo/rollback** — v1 commits immediately

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Nodes per membrane | 2-10 (cluster, not singleton) |
| Links per cluster | ≥1.5× node count (dense) |
| Agent description rate | 100% of ask steps have prose |
| Dependency resolution | Spawned membranes complete before parent |

---

## CHAIN

- **Next:** PATTERNS_MCP_Tools.md (design philosophy)
- **Validates:** VALIDATION_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
