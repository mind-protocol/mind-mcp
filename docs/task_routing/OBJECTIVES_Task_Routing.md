# OBJECTIVES — Task Routing

```
STATUS: CANONICAL
CREATED: 2026-03-13
```

---

## CHAIN

```
THIS:            OBJECTIVES_Task_Routing.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Task_Routing.md
BEHAVIORS:      ./BEHAVIORS_Task_Routing.md
ALGORITHM:      ./ALGORITHM_Task_Routing.md
VALIDATION:     ./VALIDATION_Task_Routing.md
HEALTH:         ./HEALTH_Task_Routing.md
IMPLEMENTATION: ./IMPLEMENTATION_Task_Routing.md
SYNC:           ./SYNC_Task_Routing.md

IMPL:           runtime/task_assignment.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)
1. **Route every backlog task through a citizen** — Citizens have identity, memories, escalation awareness. Anonymous sessions are amnesiac and retry forever.
2. **Physics-driven assignment, no hardcoded limits** — Embedding similarity x weight x energy x load penalty selects the best citizen. No max_attempts, no manual routing.
3. **Reusable across ecosystem** — The citizen actor graph and routing generalization live in mind-mcp, usable by any project. The orchestrator integration is in `runtime/orchestrator/`.

## NON-OBJECTIVES
- Building a separate task management system (JSONL backlog stays as creation layer)
- Replacing the existing agent routing for MCP procedures (AGENT_ actors coexist with CITIZEN_ actors)
- Manual citizen assignment by humans

## TRADEOFFS (canonical decisions)
- When graph physics and manual assignment conflict, choose graph physics.
- We accept embedding computation cost at startup to preserve physics-driven routing at runtime.
- When no citizen matches, fall back to anonymous dispatch rather than blocking the task.

## SUCCESS SIGNALS (observable)
- Zero anonymous backlog dispatches when citizen actors are seeded
- Tasks with 300+ attempts get routed to a citizen who escalates or solves
- Citizen energy scores reflect their actual success rate over time
