# Task Routing — Algorithm: Score-Based Citizen Selection and Energy Feedback

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
THIS:            ALGORITHM_Task_Routing.md (you are here)
VALIDATION:      ./VALIDATION_Task_Routing.md
HEALTH:          ./HEALTH_Task_Routing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Routing.md
SYNC:            ./SYNC_Task_Routing.md

IMPL:            runtime/task_assignment.py
```

---

## OVERVIEW

The routing algorithm selects the best citizen for a backlog task using a composite score that combines semantic similarity, citizen weight, citizen energy, and load penalty. After task completion, energy feedback updates the graph to improve future routing decisions.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 (citizen routing) | B1, B2, B4 | Selects best citizen, injects context |
| O2 (physics-driven) | B3 | Energy feedback replaces hardcoded limits |

---

## DATA STRUCTURES

### Actor Node (type='citizen')

```
Actor {
  id: "CITIZEN_{handle}",        # e.g. "CITIZEN_dragon_slayer"
  type: "citizen",
  node_type: "actor",
  synthesis: str,                 # embeddable description
  embedding: float[768],          # computed from synthesis
  weight: float,                  # default 0.5
  energy: float,                  # autonomy_level / 10.0
  status: "idle" | "paused"
}
```

### Task Synthesis (computed, not stored)

```
"{title}. {description}. Category: {category}. Repo: {repo}."
```

---

## ALGORITHM: select_best_agent()

### Step 1: Embed Task

Compute embedding of task synthesis using the configured embedding provider (local all-mpnet-base-v2 or remote).

### Step 2: Query Available Actors

```cypher
MATCH (a:Actor)
WHERE a.type = $actor_type AND COALESCE(a.status, 'idle') <> 'paused'
OPTIONAL MATCH (a)<-[r:LINK {verb: 'claimed_by'}]-(t:Narrative {type: 'task_run'})
WHERE t.status IN ['claimed', 'running']
WITH a, count(t) as active_tasks
RETURN a.id, a.synthesis, a.weight, a.energy, a.embedding, active_tasks
```

### Step 3: Score Each Actor

For each actor:
```
similarity = cosine_similarity(task_embedding, actor_embedding)
weight = max(actor_weight, 0.1)
energy = max(actor_energy, 0.1)
base_score = similarity * weight * energy

# Hard cap: skip if active_tasks >= 10
load_penalty = 0.5 ^ active_tasks
final_score = base_score * load_penalty
```

### Step 4: Select Best

Return actor_id with highest final_score. Return None if no actors available.

---

## KEY DECISIONS

### D1: Actor Type Filtering

```
IF actor_type is provided:
    Filter WHERE a.type = $actor_type
    This separates citizen routing from agent routing
ELSE:
    Match all actors (both AGENT_ and CITIZEN_)
    Useful for general-purpose assignment
```

### D2: Fallback on No Match

```
IF select_best_agent returns None:
    Orchestrator uses anonymous dispatch (legacy path)
    This preserves backwards compatibility
ELSE:
    Build citizen request with handle, mode, task content
```

---

## DATA FLOW

```
backlog task
    |
    v
build task synthesis string
    |
    v
get_embedding(synthesis)
    |
    v
query Actor nodes (type=citizen, not paused)
    |
    v
score each: similarity * weight * energy * 0.5^active_tasks
    |
    v
select highest score
    |
    v
extract handle from CITIZEN_{handle}
    |
    v
build citizen request with attempt history
```

---

## COMPLEXITY

**Time:** O(N) where N = number of citizen actors — one cosine similarity per actor

**Space:** O(N) — embeddings held in query result

**Bottlenecks:**
- Embedding computation for task synthesis (one call per dispatch)
- Graph query for all citizen actors (one query per dispatch)
- At 245 citizens, both are negligible (<100ms total)

---

## HELPER FUNCTIONS

### `record_task_outcome()`

**Purpose:** Update graph energy based on task success/failure

**Logic:** Success → actor energy += 0.1. Failure → task energy += 0.3, status → pending.

### `seed_citizen_actors()`

**Purpose:** Ensure citizen Actor nodes exist in graph with current metadata

**Logic:** MERGE on id, recompute embedding only if synthesis changed.

### `_build_citizen_synthesis()`

**Purpose:** Build embeddable string from citizen metadata

**Logic:** Concatenate name, role, tags, home project, first sentence of bio.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/infrastructure/embeddings` | `get_embedding(text)` | 768-dim float vector |
| `runtime/infrastructure/embeddings` | `cosine_similarity(a, b)` | float similarity score |
| `runtime/infrastructure/database` | `adapter.query()` / `adapter.execute()` | Query results / mutation |
