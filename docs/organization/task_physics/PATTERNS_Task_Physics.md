# Task Physics — Patterns: Thermodynamic Tasks in the Organizational Graph

```
STATUS: CANONICAL
CREATED: 2026-03-15
LAYER: L2 (Organization)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Physics.md
THIS:            PATTERNS_Task_Physics.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Task_Physics.md
ALGORITHM:       ./ALGORITHM_Task_Physics.md
VALIDATION:      ./VALIDATION_Task_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

RELATED:         docs/tools/task_routing/ (L1 routing — WHO does the task)
IMPL:            runtime/organization/task_physics.py
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

The current task system treats tasks as flat work items: created → routed → done. Energy feedback exists but is primitive (+0.3 on failure, +0.1 on success). There is no model for:

- **Dependency pressure**: a task blocking 5 others should be more urgent than an isolated task
- **Cascade effects**: completing a blocker should immediately activate downstream work
- **Artifact production**: completed tasks vanish instead of leaving permanent knowledge
- **Structural learning**: the network doesn't learn which collaboration patterns succeed

The organization has no thermodynamic model. Tasks exist in a vacuum instead of in a pressure field.

---

## THE PATTERN

**Tasks are gravity wells.** A task node accumulates energy proportional to the organizational pressure it carries. Pressure comes from three sources:

1. **Intrinsic urgency** — the task's own priority and deadline proximity
2. **Dependency pressure** — energy transmitted via `CONTRIBUTES_TO` links from critical objectives
3. **Blocking pressure** — energy accumulated from dammed downstream tasks via `BLOCKS` links

When a task is completed:

1. **Energy collapse** — the task's energy drops rapidly (half-life configurable, default 2h)
2. **Dam break** — `BLOCKS` links are severed, releasing accumulated energy into downstream tasks
3. **Crystallization** — concrete artifact nodes are created and linked to the task via `IMPLEMENTS`/`RESOLVES`
4. **Learning** — structural weights on collaboration links are updated based on the TRACE evaluation

This creates a self-organizing priority system where urgency emerges from topology, not from human labels.

---

## KEY CONCEPTS

### Task as Gravity Well

```
              ┌─────────────────┐
              │   OBJECTIVE A    │
              │  (high energy)   │
              └────────┬────────┘
                       │ CONTRIBUTES_TO (pressure flows down)
                       ▼
              ┌─────────────────┐
              │    TASK X        │◄── energy accumulates here
              │  urgency = f(    │    from objective pressure
              │    deps + blocks │    + blocking pressure
              │    + intrinsic)  │    + intrinsic priority
              └───┬─────────┬───┘
                  │ BLOCKS  │ BLOCKS
                  ▼         ▼
              ┌───────┐ ┌───────┐
              │TASK Y │ │TASK Z │  ← energy dammed (can't flow past BLOCKS)
              └───────┘ └───────┘
```

### Completion Cascade

```
TASK X completed
    │
    ├──► energy collapse (half-life 2h)
    │
    ├──► BLOCKS links severed
    │       │
    │       ├──► TASK Y energy surges (dam break)
    │       │       └──► citizen Y wakes (threshold crossed)
    │       │
    │       └──► TASK Z energy surges (dam break)
    │               └──► citizen Z wakes (threshold crossed)
    │
    ├──► crystallize artifacts
    │       ├──► Code node ──IMPLEMENTS──► TASK X
    │       └──► Document node ──RESOLVES──► TASK X
    │
    └──► update weights
            ├──► citizen.expertise_link.weight += δ
            └──► collaboration_link.weight += δ
```

---

## LINK TYPES (L2 task topology)

| Link Verb | Source → Target | Semantics | Energy Effect |
|-----------|----------------|-----------|---------------|
| `CONTRIBUTES_TO` | Task → Objective | Task feeds an objective | Pressure flows from objective to task |
| `BLOCKS` | Task → Task | Must complete before downstream | Energy dammed behind blocker |
| `REQUIRES` | Task → Task | Soft dependency (not blocking) | Pressure propagates but doesn't dam |
| `IMPLEMENTS` | Artifact → Task | Code/Doc produced by task | Created on completion |
| `RESOLVES` | Artifact → Task | Decision/fix produced by task | Created on completion |
| `MEMBER_OF` | Actor → Task | Citizen assigned to task | Weight updated by outcome |

---

## BEHAVIORS SUPPORTED

- B1 (urgency accumulation) — task energy reflects organizational pressure
- B2 (cascade unblocking) — completing a blocker wakes downstream citizens
- B3 (crystallization) — completion produces persistent artifacts
- B4 (structural learning) — weights evolve based on outcomes
- B5 (rapid decay) — completed tasks fade from consciousness

## BEHAVIORS PREVENTED

- A1 (flat priority) — urgency is never a static number; it's a dynamic energy field
- A2 (silent completion) — completing a task always has graph-wide effects
- A3 (knowledge loss) — completed work is crystallized, not deleted

---

## PRINCIPLES

### Principle 1: Urgency Is Emergent

No priority field on the task. Urgency = energy, and energy comes from topology: how many things this task blocks, how critical the objectives it feeds, how long it's been active. The graph computes priority, not humans.

### Principle 2: Completion Is Productive

A completed task is not a deleted task. It's a task that produced something — code, a document, a decision. These artifacts persist in the graph with stable weight while the task itself fades.

### Principle 3: The Network Learns

Every task completion is a training signal. The weights on `MEMBER_OF` and expertise links shift based on success/failure. Over hundreds of tasks, the network develops an accurate model of who is good at what.

### Principle 4: Physics Over Status Fields

No `status` enum with 12 values. A task's state is its energy level:
- High energy = active, urgent
- Medium energy = in progress, stable
- Low energy = completed or stale
- Near-zero energy = pruning candidate

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| FalkorDB `blood_ledger` | DB | Task nodes, dependency links, artifact nodes |
| Task TRACE output | Event | Evaluation data for weight updates |
| `mission.completed` event | Event | Trigger for cascade + crystallization |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/` | Energy propagation, decay, Laws 1-7 |
| `runtime/cognition/laws/` | Law 5 (co-activation), Law 6 (consolidation), Law 7 (pruning) |
| `runtime/organization/` | L2 org layer (access, lifecycle) |
| `docs/tools/task_routing/` | L1 citizen selection (upstream) |

---

## SCOPE

### In Scope

- Energy accumulation model for task nodes
- `BLOCKS`/`CONTRIBUTES_TO`/`REQUIRES` link physics
- Completion cascade algorithm
- Artifact crystallization on completion
- Structural weight learning from outcomes
- Task decay configuration (per node-type half-life)

### Out of Scope

- Task creation UI (owned by orchestrator/backlog)
- Citizen selection algorithm (owned by `docs/tools/task_routing/`)
- L1 brain physics (owned by `runtime/cognition/`)
- $MIND token settlement (owned by `runtime/organization/settlement_engine.py`)
