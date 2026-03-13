# Task Routing — Behaviors: Observable Effects of Physics-Based Citizen Assignment

```
STATUS: CANONICAL
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Routing.md
THIS:            BEHAVIORS_Task_Routing.md (you are here)
PATTERNS:        ./PATTERNS_Task_Routing.md
ALGORITHM:       ./ALGORITHM_Task_Routing.md
VALIDATION:      ./VALIDATION_Task_Routing.md
HEALTH:          ./HEALTH_Task_Routing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Routing.md
SYNC:            ./SYNC_Task_Routing.md

IMPL:            runtime/task_assignment.py, runtime/citizens/seed.py
```

---

## BEHAVIORS

### B1: Best-Match Citizen Selected for Task

**Why:** Anonymous sessions can't leverage citizen skills. Physics-based matching routes infrastructure tasks to engineers, social tasks to diplomats, docs tasks to writers.

```
GIVEN:  Backlog task is ready for dispatch, citizen actors are seeded in graph
WHEN:   Orchestrator calls select_best_agent(task_synthesis, actor_type="citizen")
THEN:   Citizen with highest score (similarity * weight * energy * load_penalty) is selected
AND:    Citizen handle is extracted from CITIZEN_{handle} actor ID
```

### B2: Attempt History Injected Into Task Content

**Why:** Citizens need to know what was tried before. Without this, they repeat the same approach and fail the same way.

```
GIVEN:  Task has been attempted 1+ times before
WHEN:   Task content is built for citizen dispatch
THEN:   Previous attempt count and assigned_to are included
AND:    Escalation options (TG, help, fail) are listed
```

### B3: Energy Feedback Drives Reassignment

**Why:** No hardcoded max_attempts. Physics does the work: successful citizens get boosted, failed tasks get louder.

```
GIVEN:  Citizen session completes with a task
WHEN:   Task was marked done in backlog
THEN:   Citizen energy += 0.1 (future selection probability increases)

GIVEN:  Citizen session completes without marking task done
WHEN:   Task outcome is recorded
THEN:   Task energy += 0.3 (unresolved problem gets louder)
AND:    Next select_best_agent() naturally picks a different citizen
```

### B4: Escalation Reflex in Brain Seed

**Why:** Citizens should ask for help when stuck, not retry silently. The brain seed includes a narrative node that makes help-seeking a structural tendency.

```
GIVEN:  Citizen encounters a task with many previous attempts
WHEN:   Citizen reads attempt history
THEN:   narrative:escalation_reflex node activates in their brain
AND:    Citizen is more likely to escalate via TG or ask another citizen
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Why It Matters |
|----------|-----------|----------------|
| B1 | O1 (route through citizen) | Citizens have identity and memories |
| B2 | O1 (route through citizen) | Context prevents repeated failures |
| B3 | O2 (physics-driven) | No hardcoded limits, gradient does the work |
| B4 | O1 (route through citizen) | Escalation breaks the retry loop |

---

## INPUTS / OUTPUTS

### Primary Function: `select_best_agent()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | str | Task narrative ID |
| task_synthesis | str | Task description for embedding |
| adapter | DatabaseAdapter | Graph database adapter |
| actor_type | str (optional) | Filter: "citizen", "AGENT", or None (all) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| actor_id | str or None | Best actor ID (e.g. "CITIZEN_dragon_slayer") |

---

## EDGE CASES

### E1: No Citizens Seeded

```
GIVEN:  Graph has no Actor nodes with type='citizen'
THEN:   select_best_agent returns None
AND:    Orchestrator falls back to anonymous dispatch (legacy path)
```

### E2: All Citizens Overloaded

```
GIVEN:  Every citizen has 10+ active tasks
THEN:   All citizens skipped by hard cap
AND:    select_best_agent returns None, falls back to anonymous
```

### E3: Embedding Service Unavailable

```
GIVEN:  get_embedding() returns None for task synthesis
THEN:   select_best_agent returns None immediately
AND:    Task dispatched via anonymous fallback
```

---

## ANTI-BEHAVIORS

### A1: Anonymous Dispatch When Citizens Available

```
GIVEN:   Citizens are seeded and healthy
WHEN:    Task is ready for dispatch
MUST NOT: Dispatch to anonymous session
INSTEAD:  Route through citizen via graph physics
```

### A2: Infinite Retry Without Escalation

```
GIVEN:   Task has been attempted 5+ times
WHEN:    Another citizen picks up the task
MUST NOT: Silently retry the same approach
INSTEAD:  Read attempt history, escalate or try differently
```
