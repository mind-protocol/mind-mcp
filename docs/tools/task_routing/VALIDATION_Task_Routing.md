# Task Routing — Validation: What Must Be True

```
STATUS: CANONICAL
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Routing.md
PATTERNS:        ./PATTERNS_Task_Routing.md
BEHAVIORS:       ./BEHAVIORS_Task_Routing.md
THIS:            VALIDATION_Task_Routing.md (you are here)
ALGORITHM:       ./ALGORITHM_Task_Routing.md
HEALTH:          ./HEALTH_Task_Routing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Routing.md
SYNC:            ./SYNC_Task_Routing.md
```

---

## PURPOSE

These invariants protect the core value of task routing: every backlog task reaches a citizen with identity and context, and the system self-corrects through energy physics rather than hardcoded limits.

---

## INVARIANTS

### V1: No Anonymous Dispatch When Citizens Available

**Why we care:** Anonymous sessions are amnesiac. They retry indefinitely without learning. The entire system exists to prevent this.

```
MUST:   When citizen actors are seeded and at least one is not paused/overloaded,
        pick_autonomous_task() returns a request with source="citizen" and citizen_handle set
NEVER:  Dispatch to anonymous session when citizens are available in the graph
```

### V2: Physics Drives Reassignment

**Why we care:** Hardcoded retry limits are arbitrary. Energy physics are adaptive. If we add max_attempts we've failed the design.

```
MUST:   Task reassignment happens through energy gradients:
        failed tasks get louder (energy += 0.3), successful citizens get boosted (energy += 0.1)
NEVER:  Use a max_attempts constant to stop retrying a task
NEVER:  Hardcode which citizen gets which task type
```

### V3: Attempt History Reaches the Citizen

**Why we care:** Without context about previous attempts, citizens repeat the same approach. The history is what breaks the retry loop.

```
MUST:   When task.attempts > 0, the task content includes attempt count and escalation options
NEVER:  Dispatch a previously-attempted task without its attempt history
```

### V4: Citizen Seeding Is Idempotent

**Why we care:** The orchestrator seeds on every startup. Double-seeding must not create duplicates or corrupt existing energy values.

```
MUST:   seed_citizen_actors() uses MERGE (not CREATE)
MUST:   Existing energy values are preserved on re-seed (ON CREATE SET, not SET)
NEVER:  Create duplicate Actor nodes for the same citizen handle
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Citizens receive tasks, not anonymous sessions | CRITICAL |
| V2 | Energy physics replace hardcoded limits | HIGH |
| V3 | Attempt history prevents blind retries | HIGH |
| V4 | Idempotent seeding preserves state | MEDIUM |
