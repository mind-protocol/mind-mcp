# Task Routing — Patterns: Citizens as Actor Nodes for Physics-Based Assignment

```
STATUS: CANONICAL
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Routing.md
THIS:            PATTERNS_Task_Routing.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Task_Routing.md
ALGORITHM:       ./ALGORITHM_Task_Routing.md
VALIDATION:      ./VALIDATION_Task_Routing.md
HEALTH:          ./HEALTH_Task_Routing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Routing.md
SYNC:            ./SYNC_Task_Routing.md

IMPL:            runtime/task_assignment.py, runtime/citizens/seed.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC: "Docs updated, implementation needs: {what}"

---

## THE PROBLEM

The orchestrator dispatches backlog tasks to anonymous Claude Code sessions. These sessions have no identity, no memories, no escalation awareness. When a task fails, the next session starts from scratch. Result: zombie tasks retry 300+ times because each session is amnesiac.

Meanwhile, mind-mcp already has a complete membrane-based task routing system (`select_best_agent()` with embedding similarity x weight x energy x load penalty) that was never connected to the orchestrator.

---

## THE PATTERN

**Bridge, not migrate.** The JSONL backlog stays as the creation/source layer. The graph becomes the routing layer. When a task is ready for dispatch, the orchestrator uses `select_best_agent()` with `actor_type="citizen"` to find the best citizen, then dispatches via the existing citizen session path (`build_citizen_prompt()`).

Citizens are represented as Actor nodes in the graph with type `"citizen"` and ID format `CITIZEN_{handle}`. Their synthesis field contains name, role, skills, and bio — making them matchable to tasks via embedding similarity.

**Key insight:** The same physics that route MCP procedures to agent subtypes (witness, fixer, etc.) now route backlog tasks to citizens. One routing algorithm, two actor pools.

---

## BEHAVIORS SUPPORTED

- B1 (citizen selected for task) — embedding similarity matches citizen skills to task description
- B2 (attempt history injected) — citizen reads what happened before, can decide to escalate
- B3 (energy feedback loop) — success boosts citizen energy, failure makes task louder
- B4 (escalation reflex) — brain seed includes narrative node that triggers help-seeking when stuck

## BEHAVIORS PREVENTED

- A1 (anonymous dispatch) — citizen routing is preferred; anonymous is fallback only
- A2 (infinite retry) — citizen reads attempt history and can escalate or fail explicitly

---

## PRINCIPLES

### Principle 1: Physics Over Rules

No `max_attempts` constant. No hardcoded retry limit. The energy gradient does the work: failed tasks get louder (energy += 0.3), failed citizens get lower effective score (load penalty from lingering claimed tasks). The system naturally reassigns.

### Principle 2: Bridge Architecture

JSONL backlog = creation layer (simple, file-based, human-editable). Graph = routing layer (physics-based, embedding-matched). Orchestrator = bridge between them. Neither layer knows about the other's internals.

### Principle 3: Reusable Components

`seed_citizen_actors()` and `select_best_agent(actor_type=...)` live in mind-mcp. Any project can seed its own citizen actors and route tasks through them. The orchestrator integration is in `runtime/orchestrator/`.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| `config/citizens.json` | FILE | Source of citizen metadata for seeding Actor nodes |
| `shrine/state/backlog.jsonl` | FILE | Source of tasks for routing |
| FalkorDB `mind` graph | DB | Actor nodes, task nodes, claimed_by links |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/infrastructure/embeddings` | Embedding computation for similarity matching |
| `runtime/infrastructure/database` | FalkorDB adapter for graph queries |
| `runtime/citizens/identity_loader` | Loading citizen identity for prompt building |

---

## SCOPE

### In Scope

- Seeding citizen Actor nodes from any citizen list
- Selecting best citizen for a task via graph physics
- Recording task outcomes to update energy
- Escalation reflex in brain seed

### Out of Scope

- Task creation/management (owned by shrine/backlog.py)
- Citizen identity/prompt building (owned by runtime/citizens/)
- Orchestrator dispatch mechanics (owned by runtime/orchestrator/dispatcher.py)
