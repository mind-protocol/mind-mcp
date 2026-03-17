# Task Physics — Validation: Invariants That Must Hold

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
ALGORITHM:       ./ALGORITHM_Task_Physics.md
THIS:            VALIDATION_Task_Physics.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

IMPL:            runtime/organization/task_physics.py
```

---

## PURPOSE

These invariants protect the core value of task physics: tasks are thermodynamic objects whose urgency, cascades, crystallization, and learning effects are governed by graph topology — not by static fields or manual intervention.

---

## INVARIANTS

### V1: Urgency Is Topological, Never Static

**Why we care:** A static priority field can't capture dependency pressure. A task blocking 10 others MUST be more urgent than an isolated low-priority task, regardless of labels.

```
MUST:   Task energy reflects dependency topology (CONTRIBUTES_TO pressure + BLOCKS back-pressure)
MUST:   Energy updates run every physics tick for active tasks
NEVER:  Use a static priority field as the primary urgency signal
NEVER:  Allow manual priority to override topological pressure (it can add to it)
```

**Priority:** CRITICAL

### V2: Completion Always Triggers Cascade

**Why we care:** Silent completion defeats the entire system. If a blocker is marked done but downstream tasks don't receive the energy surge, the organization stalls.

```
MUST:   When task.status transitions to "done", all outgoing BLOCKS links are severed
MUST:   Downstream tasks receive energy surge proportional to CASCADE_SURGE_FACTOR
MUST:   Citizens assigned to unblocked tasks are notified (citizen.wake event)
NEVER:  Mark a task complete without executing the cascade algorithm
NEVER:  Leave orphaned BLOCKS links on completed tasks
```

**Priority:** CRITICAL

### V3: Crystallization Preserves Knowledge

**Why we care:** Without crystallization, completed tasks decay to nothing and the organization loses the memory of what was built. Artifacts are the permanent trace.

```
MUST:   When TRACE contains artifacts, corresponding Thing nodes are created in the graph
MUST:   Artifact nodes have stable weight (≥ 0.5) and do NOT undergo rapid decay
MUST:   Artifact → Task links use IMPLEMENTS or RESOLVES verbs
NEVER:  Delete artifact nodes when their parent task is pruned
NEVER:  Apply task half-life decay to artifact nodes
```

**Priority:** HIGH

### V4: No Circular BLOCKS Dependencies

**Why we care:** Circular BLOCKS create deadlocks — no task in the cycle can ever complete because each waits for the other. This is a topological impossibility.

```
MUST:   Before creating a BLOCKS link A → B, verify B does not transitively BLOCKS A
MUST:   Reject circular BLOCKS with an explicit error
NEVER:  Allow a BLOCKS cycle to exist in the graph
```

**Priority:** CRITICAL

### V5: Cascade Depth Is Bounded

**Why we care:** Unbounded cascades can create runaway energy amplification, waking hundreds of citizens simultaneously and exhausting the compute budget.

```
MUST:   Cascade propagation stops at MAX_CASCADE_DEPTH (default: 5)
MUST:   Only the directly blocked task (depth 1) receives full surge energy
MUST:   Energy attenuates by CASCADE_DECAY_PER_HOP at each subsequent depth
NEVER:  Allow cascade to propagate indefinitely
```

**Priority:** HIGH

### V6: Learning Is Monotonic for Collaboration

**Why we care:** Failing together is still working together. Trust links between collaborators should strengthen regardless of task outcome — the act of collaboration itself has value.

```
MUST:   Collaboration trust links increase on both success and failure (abs(learning_delta))
MUST:   Expertise links increase only on success (positive learning_delta)
NEVER:  Decrease trust between collaborators based on a single task failure
```

**Priority:** MEDIUM

### V7: Completed Task Decay Is Rapid

**Why we care:** Active consciousness should not be cluttered with completed work. The organization's attention must focus on what needs doing, not what's been done.

```
MUST:   Completed tasks decay with configured half-life (default: 2 hours)
MUST:   After 3× half-life (~6 hours), task energy < 12.5% of original
MUST:   Tasks below TASK_PRUNE_THRESHOLD are flagged as prunable
NEVER:  Apply rapid decay to active (non-completed) tasks
NEVER:  Apply rapid decay to crystallized artifact nodes
```

**Priority:** MEDIUM

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System produces incorrect organizational state | Deadlocks, lost cascades, phantom urgency |
| **HIGH** | Major organizational value lost | Knowledge disappears, budget wasted |
| **MEDIUM** | Partial value lost | Suboptimal learning, cluttered attention |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Urgency reflects reality, not labels | CRITICAL |
| V2 | Completions cascade through the dependency graph | CRITICAL |
| V3 | Completed work leaves permanent artifacts | HIGH |
| V4 | No deadlocks from circular blocking | CRITICAL |
| V5 | Cascades don't cause runaway amplification | HIGH |
| V6 | Collaboration trust is never punished | MEDIUM |
| V7 | Completed tasks fade, artifacts persist | MEDIUM |
