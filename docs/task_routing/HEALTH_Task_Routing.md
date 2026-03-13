# Task Routing — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Routing.md
PATTERNS:        ./PATTERNS_Task_Routing.md
BEHAVIORS:       ./BEHAVIORS_Task_Routing.md
ALGORITHM:       ./ALGORITHM_Task_Routing.md
VALIDATION:      ./VALIDATION_Task_Routing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Routing.md
THIS:            HEALTH_Task_Routing.md (you are here)
SYNC:            ./SYNC_Task_Routing.md
```

---

## PURPOSE

This health file monitors the runtime behavior of citizen-based task routing. It catches:
- Regression to anonymous dispatch (V1 violation)
- Energy stagnation (V2 violation — physics not working)
- Citizen utilization imbalance (one citizen getting all tasks)
- Orphaned tasks (tasks stuck in-progress with no active citizen)

Tests can verify scoring math. Health monitors whether routing actually works in production with real citizens and real tasks.

---

## WHY THIS PATTERN

Tests run on fixtures. Health runs on the real graph with 245 citizens and real backlog tasks. The failure modes we care about — energy stagnation, utilization skew, orphaned tasks — only manifest over time with real data.

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: anonymous_dispatch_rate
    flow_id: task_dispatch
    priority: high
    rationale: If >10% of dispatches are anonymous when citizens are seeded, V1 is violated

  - name: avg_attempts_before_completion
    flow_id: task_lifecycle
    priority: high
    rationale: Should decrease over time as citizens learn. If increasing, energy feedback is broken.

  - name: citizen_utilization_distribution
    flow_id: task_dispatch
    priority: med
    rationale: Gini coefficient of task assignments. >0.8 means one citizen gets everything.

  - name: escalation_rate
    flow_id: task_lifecycle
    priority: med
    rationale: Citizens should escalate stuck tasks. Rate near zero means escalation reflex isn't working.

  - name: orphaned_task_count
    flow_id: task_lifecycle
    priority: high
    rationale: Tasks in-progress with no active citizen session. These are the zombies we're trying to eliminate.
```

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (citizen routing) | anonymous_dispatch_rate, orphaned_task_count | Detects regression to anonymous/zombie state |
| O2 (physics-driven) | avg_attempts_before_completion, citizen_utilization_distribution | Detects energy stagnation or routing imbalance |

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_anonymous_dispatch_rate
    purpose: V1 — no anonymous dispatch when citizens available
    status: pending
    priority: high
  - name: check_avg_attempts
    purpose: V2 — physics should reduce retry count over time
    status: pending
    priority: high
  - name: check_orphaned_tasks
    purpose: V1 — no zombie tasks stuck without active citizen
    status: pending
    priority: high
  - name: check_utilization_gini
    purpose: O2 — balanced distribution across citizens
    status: pending
    priority: med
```

---

## KNOWN GAPS

<!-- @mind:todo Implement check_anonymous_dispatch_rate — query journal for source="task" vs source="citizen" dispatches -->
<!-- @mind:todo Implement check_orphaned_tasks — query graph for claimed tasks with no active neuron -->
<!-- @mind:todo Implement check_avg_attempts — compute from backlog.jsonl completed tasks -->
