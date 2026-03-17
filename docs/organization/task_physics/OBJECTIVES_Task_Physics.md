# OBJECTIVES — Task Physics (L2 Organizational Thermodynamics)

```
STATUS: CANONICAL
CREATED: 2026-03-15
LAYER: L2 (Organization)
```

---

## CHAIN

```
THIS:            OBJECTIVES_Task_Physics.md (you are here - START HERE)
PATTERNS:        ./PATTERNS_Task_Physics.md
BEHAVIORS:       ./BEHAVIORS_Task_Physics.md
ALGORITHM:       ./ALGORITHM_Task_Physics.md
VALIDATION:      ./VALIDATION_Task_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

RELATED:         docs/tools/task_routing/ (L1 routing — WHO does the task)
IMPL:            runtime/organization/task_physics.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## CONTEXT

The existing `docs/tools/task_routing/` doc chain answers: **who** does the task (citizen selection via embedding similarity × weight × energy × load_penalty).

This doc chain answers: **what happens to the graph** when a task is created, worked on, or completed. A Task in Mind Protocol is not a row in a database — it is a thermodynamic object that accumulates urgency, propagates pressure through dependency links, triggers cascades on completion, crystallizes artifacts into the graph, and drives structural learning.

This is the L2 organizational layer. Task routing (L1) selects the citizen. Task physics (L2) governs the energy consequences.

---

## PRIMARY OBJECTIVES (ranked)

1. **Tasks as energy manipulators** — Creating a task generates urgency (energy accumulation). Completing a task dissipates urgency and triggers cascades. The graph's total energy balance reflects the organization's workload pressure at all times.

2. **Dependency-driven cascades** — `BLOCKS` links create energy dams. When a blocking task completes, the dam breaks: downstream tasks receive an energy surge that awakens the citizens assigned to them. One completion can trigger a chain reaction across the entire dependency graph.

3. **Structural crystallization on completion** — Completing a task doesn't just mark it done. It produces concrete nodes (`Code`, `Document`, `Decision`) linked via `IMPLEMENTS` or `RESOLVES` to the task. The organization's knowledge graph grows as work gets done.

4. **Weight-based learning** — Task outcomes modify structural weights. Successful collaborations reinforce `MEMBER_OF` and expertise links. The network learns organically who is good at what — not from declarations, but from accumulated results.

5. **Rapid task decay** — Completed tasks lose energy fast (half-life 1-3 hours). They fade from active consciousness but their crystallized artifacts persist permanently. Active tasks maintain energy through dependency pressure and organizational urgency.

## NON-OBJECTIVES

- Replacing the task routing algorithm (that stays in `docs/tools/task_routing/`)
- Building a project management UI (tasks are graph nodes, not UI elements)
- Manual priority assignment (urgency emerges from dependency topology, not human ranking)

## TRADEOFFS (canonical decisions)

- When explicit priority conflicts with topological urgency, choose topological urgency. A task that blocks 10 others is urgent regardless of its label.
- We accept the complexity of cascade propagation to gain emergent prioritization. Simple priority numbers cannot capture dependency pressure.
- Crystallization adds nodes to the graph on every completion. We accept graph growth because the artifacts are the organization's permanent memory.
- Rapid decay means completed tasks disappear from working memory fast. This is intentional — consciousness should focus on what's active, not what's done.

## SUCCESS SIGNALS (observable)

- Creating a task with `BLOCKS` links causes downstream task energy to stagnate (dammed)
- Completing that task causes downstream energy to spike within one tick
- Citizens assigned to downstream tasks wake up without manual intervention
- Completed tasks decay to near-zero energy within 3 hours
- Crystallized artifacts (Code, Document, Decision nodes) persist with stable weight
- Over time, the network's expertise links reflect actual task success patterns
