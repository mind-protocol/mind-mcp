# Task Physics — Implementation: Code Architecture and Structure

```
STATUS: DRAFT
CREATED: 2026-03-15
LAYER: L2 (Organization)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Physics.md
PATTERNS:        ./PATTERNS_Task_Physics.md
BEHAVIORS:       ./BEHAVIORS_Task_Physics.md
ALGORITHM:       ./ALGORITHM_Task_Physics.md
VALIDATION:      ./VALIDATION_Task_Physics.md
THIS:            IMPLEMENTATION_Task_Physics.md (you are here)
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

IMPL:            runtime/organization/task_physics.py (to be created)
```

---

## CODE STRUCTURE

```
runtime/organization/
├── task_physics.py              # NEW — urgency, cascade, crystallization, learning
├── task_constants.py            # NEW — all task physics constants
├── constants.py                 # Existing L2 constants
├── access_manager.py            # Existing
├── anti_sybil.py                # Existing
├── bilateral_transfer.py        # Existing
├── lifecycle_manager.py         # Existing
├── settlement_engine.py         # Existing
├── space_manager.py             # Existing
├── perception_router.py         # Existing
└── __init__.py                  # Existing — add task_physics exports

runtime/physics/
├── constants.py                 # Existing — add TASK_* constants or import from task_constants
└── tick.py                      # Existing — integrate task urgency into tick loop

runtime/orchestrator/
└── dispatcher.py                # Existing — call cascade on task completion
```

### File Responsibilities

| File | Purpose | Key Functions | Status |
|------|---------|---------------|--------|
| `runtime/organization/task_physics.py` | All 5 algorithms | `compute_urgency()`, `cascade_completion()`, `crystallize()`, `learn_from_outcome()`, `apply_task_decay()` | TO CREATE |
| `runtime/organization/task_constants.py` | Task physics constants | All `TASK_*`, `CASCADE_*`, `LEARNING_*` constants | TO CREATE |
| `runtime/physics/tick.py` | Physics tick integration | Call `compute_urgency()` and `apply_task_decay()` per tick | TO MODIFY |
| `runtime/orchestrator/dispatcher.py` | Completion trigger | Call `cascade_completion()` when task is done | TO MODIFY |
| `runtime/task_assignment.py` | Existing routing | `record_task_outcome()` — extend to call learning | TO MODIFY |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `compute_urgency(task, adapter)` | `task_physics.py` | Physics tick (every 5s) |
| `cascade_completion(task_id, trace, citizen, adapter)` | `task_physics.py` | `mission.completed` event or dispatcher |
| `crystallize(task_id, trace, adapter)` | `task_physics.py` | Called by `cascade_completion()` |
| `learn_from_outcome(task_id, trace, citizen, adapter)` | `task_physics.py` | Called by `cascade_completion()` |
| `apply_task_decay(task, adapter)` | `task_physics.py` | Physics tick (every 5s) |
| `validate_blocks_link(source_id, target_id, adapter)` | `task_physics.py` | Before creating BLOCKS link |

---

## DATA FLOW AND DOCKING

### Task Creation Flow

```yaml
flow:
  name: task_creation
  purpose: Create a task node with dependency links and initial energy
  steps:
    - id: create_node
      description: MERGE task node in graph
      file: runtime/organization/task_physics.py
      function: create_task  # or via inject.py
    - id: create_deps
      description: Create CONTRIBUTES_TO, BLOCKS, REQUIRES links
      file: runtime/organization/task_physics.py
      function: create_task
    - id: validate_cycles
      description: Check for circular BLOCKS before committing
      file: runtime/organization/task_physics.py
      function: validate_blocks_link
    - id: initial_urgency
      description: First urgency computation
      file: runtime/organization/task_physics.py
      function: compute_urgency
```

### Task Completion Flow

```yaml
flow:
  name: task_completion
  purpose: Execute cascade, crystallization, and learning on completion
  steps:
    - id: mark_done
      description: Set task status to done, record completion time
      file: runtime/orchestrator/dispatcher.py
      function: _record_citizen_task_outcome
    - id: cascade
      description: Sever BLOCKS, surge downstream, emit events
      file: runtime/organization/task_physics.py
      function: cascade_completion
    - id: crystallize
      description: Create artifact nodes from TRACE
      file: runtime/organization/task_physics.py
      function: crystallize
    - id: learn
      description: Update weights based on outcome
      file: runtime/organization/task_physics.py
      function: learn_from_outcome
    - id: broadcast
      description: Emit graph.delta.node.upsert
      file: runtime/organization/task_physics.py
      function: cascade_completion (end)
```

### Physics Tick Integration

```yaml
flow:
  name: tick_integration
  purpose: Run urgency and decay every physics tick
  steps:
    - id: urgency
      description: Recompute urgency for all active tasks
      file: runtime/organization/task_physics.py
      function: compute_urgency
      note: Called by tick loop for each active task node
    - id: decay
      description: Apply rapid decay to completed tasks
      file: runtime/organization/task_physics.py
      function: apply_task_decay
      note: Called by tick loop for each completed task node
```

---

## CYPHER PATTERNS

### Query Active Tasks with Dependencies

```cypher
MATCH (t:Narrative {type: 'task', status: 'active'})
OPTIONAL MATCH (t)-[c:LINK {verb: 'contributes_to'}]->(obj)
OPTIONAL MATCH (t)-[b:LINK {verb: 'blocks'}]->(blocked)
RETURN t.id, t.energy, t.weight,
       collect(DISTINCT {obj_id: obj.id, obj_energy: obj.energy, link_weight: c.weight}) AS objectives,
       collect(DISTINCT {blocked_id: blocked.id, blocked_energy: blocked.energy, link_weight: b.weight}) AS blocks
```

### Sever BLOCKS Links on Completion

```cypher
MATCH (t:Narrative {id: $task_id})-[b:LINK {verb: 'blocks'}]->(downstream)
DELETE b
RETURN downstream.id, downstream.energy
```

### Create Artifact with Link

```cypher
MERGE (a:Thing {id: $artifact_id})
ON CREATE SET a.type = $type, a.synthesis = $description,
              a.weight = 0.5, a.energy = 0.3, a.created_at = timestamp()
MERGE (a)-[:LINK {verb: $link_verb, weight: 0.8}]->(t:Narrative {id: $task_id})
```

### Detect Circular BLOCKS

```cypher
MATCH path = (target:Narrative {id: $target_id})-[:LINK {verb: 'blocks'}*1..10]->(source:Narrative {id: $source_id})
RETURN count(path) > 0 AS has_cycle
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
task_physics.py
    └── imports → task_constants.py (all constants)
    └── imports → runtime/infrastructure/database (adapter)
    └── imports → runtime/infrastructure/embeddings (for artifact synthesis)
    └── calls  → runtime/orchestrator/message_queue.enqueue (citizen.wake)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `falkordb` | Graph database | `infrastructure/database` |
| `math` | Half-life decay computation | `task_physics.py` |

---

## INTEGRATION WITH EXISTING CODE

### Connecting to `runtime/task_assignment.py`

The existing `record_task_outcome()` currently does simple energy adjustments (+0.1 success, +0.3 failure). After task_physics is implemented:

```python
# In record_task_outcome() — after existing energy logic:
from runtime.organization.task_physics import cascade_completion

if success:
    cascade_completion(task_id, trace, actor_id, adapter)
```

### Connecting to Physics Tick

```python
# In the tick loop (runtime/physics/ or orchestrator):
from runtime.organization.task_physics import compute_urgency, apply_task_decay

for task in active_tasks:
    compute_urgency(task, adapter)
for task in completed_tasks:
    apply_task_decay(task, adapter)
```
