# Task Physics — Algorithm: Energy Accumulation, Cascades, Crystallization, Learning

```
STATUS: CANONICAL
CREATED: 2026-03-15
LAYER: L2 (Organization)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Physics.md
PATTERNS:        ./PATTERNS_Task_Physics.md
BEHAVIORS:       ./BEHAVIORS_Task_Physics.md
THIS:            ALGORITHM_Task_Physics.md (you are here)
VALIDATION:      ./VALIDATION_Task_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

IMPL:            runtime/organization/task_physics.py
```

---

## OVERVIEW

Four algorithms govern task physics:

1. **Urgency accumulation** — how task energy reflects organizational pressure
2. **Completion cascade** — how finishing a task propagates energy through the dependency graph
3. **Crystallization** — how completed tasks produce permanent artifacts
4. **Structural learning** — how task outcomes modify graph weights

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Algorithm |
|-----------|---------------------|-----------|
| O1 (energy manipulators) | B1 | Urgency accumulation |
| O2 (dependency cascades) | B2 | Completion cascade |
| O3 (crystallization) | B3 | Crystallization |
| O4 (weight learning) | B4 | Structural learning |
| O5 (rapid decay) | B5 | Decay configuration |

---

## DATA STRUCTURES

### Task Node (L2)

```
Task {
  id: str,                          # e.g. "TASK_fix_auth_middleware"
  node_type: "Narrative",           # tasks are narratives in the graph
  type: "task",                     # narrative subtype
  synthesis: str,                   # embeddable description
  embedding: float[1536],           # computed from synthesis
  energy: float,                    # current urgency level
  weight: float,                    # structural importance (grows with learning)
  status: "pending"|"active"|"done",# lifecycle state
  created_at: float,                # epoch timestamp
  completed_at: float|null,         # epoch timestamp when done
  half_life_hours: float,           # decay rate after completion (default: 2.0)
  category: str,                    # task category for expertise matching
}
```

### Dependency Links

```
BLOCKS {
  source: Task.id,                  # blocker task
  target: Task.id,                  # blocked task
  verb: "blocks",
  energy: float,                    # accumulated dam pressure
  weight: float,                    # structural importance
}

CONTRIBUTES_TO {
  source: Task.id,
  target: Objective.id,             # organizational objective
  verb: "contributes_to",
  weight: float,                    # contribution strength
}

REQUIRES {
  source: Task.id,                  # dependent task
  target: Task.id,                  # prerequisite task
  verb: "requires",
  weight: float,
}
```

### Artifact Nodes

```
Artifact {
  id: str,                          # e.g. "CODE_auth_middleware_v2"
  node_type: "Thing",               # artifacts are Things in the graph
  type: "code"|"document"|"decision",
  synthesis: str,
  weight: 0.5,                      # stable — no rapid decay
  energy: 0.3,                      # low but persistent
}
```

---

## ALGORITHM 1: URGENCY ACCUMULATION

Runs every physics tick for active task nodes.

### Step 1: Compute Intrinsic Urgency

```
intrinsic = task.base_energy
if task.deadline:
    hours_remaining = (task.deadline - now) / 3600
    deadline_pressure = 1.0 / max(hours_remaining, 1.0)
    intrinsic += deadline_pressure × DEADLINE_PRESSURE_FACTOR  # default: 0.5
```

### Step 2: Compute Dependency Pressure (from objectives)

```
objective_pressure = 0.0
for link in task.outgoing("CONTRIBUTES_TO"):
    objective = link.target
    objective_pressure += objective.energy × link.weight × OBJECTIVE_PRESSURE_RATE
    # default OBJECTIVE_PRESSURE_RATE: 0.2
```

### Step 3: Compute Blocking Pressure (from blocked tasks)

```
blocking_pressure = 0.0
for link in task.outgoing("BLOCKS"):
    blocked_task = link.target
    # Downstream tasks "push back" on their blocker
    blocking_pressure += blocked_task.energy × BLOCKING_PRESSURE_RATE
    # default BLOCKING_PRESSURE_RATE: 0.3
    # More blocked tasks = more pressure
```

### Step 4: Update Task Energy

```
target_energy = intrinsic + objective_pressure + blocking_pressure
task.energy = task.energy + (target_energy - task.energy) × ENERGY_CONVERGENCE_RATE
# default ENERGY_CONVERGENCE_RATE: 0.1 (smooth convergence, no oscillation)
# Energy is clamped to [0.0, 5.0]
```

---

## ALGORITHM 2: COMPLETION CASCADE

Triggered when a task's status transitions to "done".

### Step 1: Record Completion

```
task.status = "done"
task.completed_at = now()
task.half_life_hours = TASK_COMPLETED_HALF_LIFE  # default: 2.0
energy_at_completion = task.energy
```

### Step 2: Sever BLOCKS Links and Surge Downstream

```
for link in task.outgoing("BLOCKS"):
    downstream = link.target
    surge = energy_at_completion × CASCADE_SURGE_FACTOR × link.weight
    # default CASCADE_SURGE_FACTOR: 0.6

    downstream.energy += surge

    # Remove the BLOCKS link (dam is broken)
    delete(link)

    # Check if downstream citizen should wake
    citizen = downstream.incoming("MEMBER_OF").source
    if citizen and downstream.energy > citizen.activation_threshold:
        emit("citizen.wake", citizen_id=citizen.id, task_id=downstream.id)
```

### Step 3: Propagate Cascade (bounded)

```
cascade_queue = [(downstream, 1) for downstream in just_unblocked]
while cascade_queue:
    task, depth = cascade_queue.pop(0)
    if depth >= MAX_CASCADE_DEPTH:  # default: 5
        continue

    # Check if this task was also blocking others
    for link in task.outgoing("BLOCKS"):
        # Don't sever these — only completed tasks sever their own BLOCKS
        # But propagate pressure notification
        link.target.energy += task.energy × CASCADE_DECAY_PER_HOP × link.weight
        # default CASCADE_DECAY_PER_HOP: 0.3
        cascade_queue.append((link.target, depth + 1))
```

### Step 4: Emit Completion Event

```
emit("mission.completed", {
    task_id: task.id,
    completed_by: citizen_handle,
    energy_released: energy_at_completion,
    tasks_unblocked: [t.id for t in just_unblocked],
})

# Broadcast graph delta for real-time consumers
broadcast("graph.delta.node.upsert", {
    node_id: task.id,
    status: "done",
    energy: task.energy,
})
```

---

## ALGORITHM 3: CRYSTALLIZATION

Triggered after completion cascade, using the TRACE evaluation.

### Step 1: Parse TRACE for Artifacts

```
artifacts = trace.get("artifacts", [])
# Each artifact: { type: "code"|"document"|"decision", description: str, ref: str }
```

### Step 2: Create Artifact Nodes

```
for artifact in artifacts:
    node_id = f"{artifact.type.upper()}_{task.id}_{hash(artifact.ref)[:8]}"

    MERGE (a:Thing {id: $node_id})
    ON CREATE SET
        a.type = artifact.type,
        a.synthesis = artifact.description,
        a.weight = 0.5,
        a.energy = 0.3,
        a.created_at = now()

    # Link artifact to task
    link_verb = "implements" if artifact.type == "code" else "resolves"
    MERGE (a)-[:LINK {verb: $link_verb, weight: 0.8}]->(task)
```

### Step 3: Link to Objectives (transitive)

```
for obj_link in task.outgoing("CONTRIBUTES_TO"):
    # Artifacts transitively contribute to objectives
    MERGE (artifact)-[:LINK {verb: "contributes_to", weight: 0.3}]->(obj_link.target)
```

---

## ALGORITHM 4: STRUCTURAL LEARNING

Triggered after crystallization, using TRACE evaluation score.

### Step 1: Compute Learning Signal

```
trace_score = trace.get("score", 0.5)  # 0.0 = failure, 1.0 = perfect
learning_delta = (trace_score - 0.5) × LEARNING_RATE  # default LEARNING_RATE: 0.1
# Delta is [-0.05, +0.05] — small but cumulative
```

### Step 2: Update MEMBER_OF Link

```
member_link = task.incoming("MEMBER_OF", source=citizen)
if member_link:
    member_link.weight = clamp(member_link.weight + learning_delta, 0.01, 1.0)
```

### Step 3: Update Expertise Links

```
if task.category:
    expertise_link = citizen.outgoing("EXPERTISE", target_type=task.category)
    if expertise_link:
        expertise_link.weight = clamp(expertise_link.weight + learning_delta, 0.01, 1.0)
    elif trace_score > 0.7:
        # Create new expertise link (citizen discovered a new skill)
        CREATE (citizen)-[:LINK {verb: "expert_in", weight: 0.3}]->(category_node)
```

### Step 4: Update Collaboration Links

```
collaborators = trace.get("collaborators", [])
for collab_handle in collaborators:
    collab = get_citizen(collab_handle)
    trust_link = citizen.link_to(collab)
    if trust_link:
        trust_link.weight = clamp(trust_link.weight + abs(learning_delta), 0.01, 1.0)
        # Note: collaboration always strengthens trust (abs), even on failure
        # Failing together is still working together
```

---

## ALGORITHM 5: COMPLETED TASK DECAY

Runs every physics tick for completed task nodes.

```
if task.status == "done" and task.completed_at:
    elapsed_hours = (now() - task.completed_at) / 3600
    decay_factor = 0.5 ^ (elapsed_hours / task.half_life_hours)
    task.energy = task.energy_at_completion × decay_factor

    # Pruning candidate when energy is negligible
    if task.energy < TASK_PRUNE_THRESHOLD:  # default: 0.01
        task.prunable = true
        # Actual pruning is handled by Law 7 (garbage collection)
```

---

## CONSTANTS

| Constant | Default | Description |
|----------|---------|-------------|
| `DEADLINE_PRESSURE_FACTOR` | 0.5 | How much deadline proximity adds to urgency |
| `OBJECTIVE_PRESSURE_RATE` | 0.2 | Rate of pressure flow from objectives to tasks |
| `BLOCKING_PRESSURE_RATE` | 0.3 | Rate of back-pressure from blocked tasks |
| `ENERGY_CONVERGENCE_RATE` | 0.1 | Smoothing factor for energy updates |
| `CASCADE_SURGE_FACTOR` | 0.6 | Fraction of blocker energy transferred on completion |
| `CASCADE_DECAY_PER_HOP` | 0.3 | Energy attenuation per cascade hop |
| `MAX_CASCADE_DEPTH` | 5 | Maximum cascade propagation depth |
| `TASK_COMPLETED_HALF_LIFE` | 2.0 | Hours — completed task energy half-life |
| `TASK_PRUNE_THRESHOLD` | 0.01 | Energy below which a completed task is prunable |
| `LEARNING_RATE` | 0.1 | Weight adjustment per task outcome |
| `ARTIFACT_INITIAL_WEIGHT` | 0.5 | Weight of crystallized artifact nodes |

---

## COMPLEXITY

**Urgency accumulation:** O(T × D) per tick where T = active tasks, D = avg dependencies per task

**Completion cascade:** O(C) where C = cascade chain length (bounded by MAX_CASCADE_DEPTH)

**Crystallization:** O(A) where A = artifacts produced (typically 1-3)

**Structural learning:** O(K) where K = collaborators on the task (typically 1-2)

**Total per tick:** Dominated by urgency accumulation. At 500 tasks with avg 3 deps, ~1500 link traversals — negligible.

---

## DATA FLOW

```
                    ┌──────────────────────────────────────────────┐
                    │           PHYSICS TICK (every 5s)            │
                    │                                              │
                    │  for each active task:                       │
                    │    compute_urgency(task)  ─── Algorithm 1    │
                    │                                              │
                    │  for each completed task:                    │
                    │    apply_decay(task)      ─── Algorithm 5    │
                    └──────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────┐
                    │       ON mission.completed EVENT             │
                    │                                              │
                    │  cascade(task)            ─── Algorithm 2    │
                    │       │                                      │
                    │       ▼                                      │
                    │  crystallize(task, trace) ─── Algorithm 3    │
                    │       │                                      │
                    │       ▼                                      │
                    │  learn(task, trace)       ─── Algorithm 4    │
                    └──────────────────────────────────────────────┘
```
