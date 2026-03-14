# Task Routing — Implementation: Code Architecture and Structure

```
STATUS: CANONICAL
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Routing.md
BEHAVIORS:       ./BEHAVIORS_Task_Routing.md
PATTERNS:        ./PATTERNS_Task_Routing.md
ALGORITHM:       ./ALGORITHM_Task_Routing.md
VALIDATION:      ./VALIDATION_Task_Routing.md
THIS:            IMPLEMENTATION_Task_Routing.md (you are here)
HEALTH:          ./HEALTH_Task_Routing.md
SYNC:            ./SYNC_Task_Routing.md

IMPL:            runtime/task_assignment.py, runtime/citizens/seed.py
```

---

## CODE STRUCTURE

```
mind-mcp/runtime/
├── task_assignment.py             # Score computation, agent/citizen selection, outcome recording
├── agents/
│   └── mapping.py                 # ID normalization (AGENT_, CITIZEN_, HUMAN_ prefixes)
├── citizens/
│   ├── __init__.py                # Exports: seed_citizen_actors, load/list/permissions
│   ├── seed.py                    # Seed citizen Actor nodes into graph
│   ├── identity_loader.py         # Load citizen identity from filesystem
│   └── prompt_builder.py          # Build citizen session prompts
└── infrastructure/
    ├── embeddings/                # get_embedding(), cosine_similarity()
    └── database/                  # get_database_adapter()

runtime/orchestrator/
└── orchestrator.py                # Integration: _select_citizen_for_task(), _seed_citizen_actors_on_startup(), _record_citizen_task_outcome()

mind-mcp/runtime/
└── seed_brain_from_source_docs_dynamic_generator.py  # narrative:escalation_reflex, action:escalate_when_stuck
```

### File Responsibilities

| File | Purpose | Key Functions | Status |
|------|---------|---------------|--------|
| `runtime/task_assignment.py` | Score, select, assign, record outcome | `select_best_agent()`, `record_task_outcome()` | OK |
| `runtime/citizens/seed.py` | Seed citizen actors into graph | `seed_citizen_actors()` | OK |
| `runtime/agents/mapping.py` | ID normalization for all actor types | `normalize_citizen_id()`, `extract_citizen_handle()` | OK |
| `runtime/orchestrator/dispatcher.py` | Bridge: backlog → graph routing → citizen dispatch | `_select_citizen_for_task()`, `pick_autonomous_task()` | WATCH |

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `select_best_agent()` | `runtime/task_assignment.py:33` | Orchestrator's `_select_citizen_for_task()` |
| `seed_citizen_actors()` | `runtime/citizens/seed.py:39` | Orchestrator startup (background thread) |
| `record_task_outcome()` | `runtime/task_assignment.py:217` | Orchestrator session completion |
| `_select_citizen_for_task()` | `runtime/orchestrator/dispatcher.py` | `pick_autonomous_task()` |

---

## DATA FLOW AND DOCKING

### Task Dispatch Flow

```yaml
flow:
  name: task_dispatch
  purpose: Route backlog task to best citizen via graph physics
  steps:
    - id: pick_task
      description: Select next autonomous task from JSONL backlog
      file: runtime/orchestrator/dispatcher.py
      function: pick_autonomous_task
    - id: select_citizen
      description: Query graph for best citizen match
      file: runtime/orchestrator/dispatcher.py
      function: _select_citizen_for_task
    - id: graph_routing
      description: Score all citizen actors against task embedding
      file: runtime/task_assignment.py
      function: select_best_agent
    - id: build_request
      description: Build citizen request with handle, mode, attempt history
      file: runtime/orchestrator/dispatcher.py
      function: pick_autonomous_task
    - id: dispatch
      description: Queue citizen request for main loop
      file: runtime/orchestrator/dispatcher.py
      function: orchestrate (main loop)
```

### Energy Feedback Flow

```yaml
flow:
  name: energy_feedback
  purpose: Update citizen energy and task energy based on outcome
  steps:
    - id: session_complete
      description: Citizen session finishes
      file: runtime/orchestrator/dispatcher.py
      function: invoke_claude
    - id: check_outcome
      description: Check if backlog task was marked done
      file: runtime/orchestrator/dispatcher.py
      function: _record_citizen_task_outcome
    - id: update_graph
      description: Boost citizen or task energy
      file: runtime/task_assignment.py
      function: record_task_outcome
```

---

## LOGIC CHAINS

### LC1: Backlog → Citizen Dispatch

```
backlog.pick_next_autonomous()
  → _select_citizen_for_task(task)
    → select_best_agent(task.id, synthesis, adapter, actor_type="citizen")
      → get_embedding(synthesis)
      → query Actor WHERE type='citizen'
      → score each: similarity * weight * energy * 0.5^active
      → return CITIZEN_{handle}
    → extract handle
  → build citizen request with attempt history
  → return (request, session_id, task)
```

### LC2: Session Complete → Energy Feedback

```
invoke_claude() completes
  → _record_citizen_task_outcome(handle, task_id, has_response)
    → backlog.get(task_id) → check if done
    → record_task_outcome(actor_id, task_id, success, adapter)
      → success: actor energy += 0.1, task status = done
      → failure: task energy += 0.3, task status = pending
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
task_assignment.py
    └── imports → infrastructure/embeddings (get_embedding, cosine_similarity)
citizens/seed.py
    └── imports → infrastructure/embeddings (get_embedding)
    └── imports → infrastructure/database (adapter)
agents/mapping.py
    └── no external imports (pure functions)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `falkordb` | Graph database | `infrastructure/database` |
| `sentence_transformers` | Local embeddings | `infrastructure/embeddings` |
