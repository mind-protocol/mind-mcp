# Task Physics — Health: Verification Mechanics and Coverage

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
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
THIS:            HEALTH_Task_Physics.md (you are here)
SYNC:            ./SYNC_Task_Physics.md

IMPL:            runtime/organization/task_physics.py
```

---

## PURPOSE

This health file monitors the runtime behavior of task physics. Tests verify the algorithms. Health monitors whether the thermodynamic effects actually manifest in production with real tasks and real dependency graphs.

---

## WHY THIS PATTERN

Task physics effects are emergent — they depend on real dependency topologies, real citizen behaviors, and real completion patterns. Unit tests can verify the math. Health checkers detect:

- Cascades that should have fired but didn't (V2 violation)
- Completed tasks that still have BLOCKS links (crash recovery gap)
- Energy stagnation (urgency not reflecting topology)
- Knowledge loss (completed tasks without artifacts)

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: orphaned_blocks_on_completed_tasks
    invariant: V2
    priority: critical
    rationale: >
      A completed task with outgoing BLOCKS links means the cascade failed
      or was interrupted. Downstream tasks are dammed behind a completed blocker.
    query: |
      MATCH (t:Narrative {type: 'task', status: 'done'})-[b:LINK {verb: 'blocks'}]->(downstream)
      RETURN t.id, downstream.id
    threshold: count = 0
    action: Re-run cascade_completion() for each orphaned blocker

  - name: circular_blocks_detection
    invariant: V4
    priority: critical
    rationale: >
      Circular BLOCKS create deadlocks. Should never exist if validation works,
      but corruption or manual graph edits could introduce them.
    query: |
      MATCH path = (a:Narrative {type: 'task'})-[:LINK {verb: 'blocks'}*2..10]->(a)
      RETURN DISTINCT a.id, length(path) AS cycle_length
    threshold: count = 0
    action: Break the weakest link in the cycle (lowest weight)

  - name: energy_topology_correlation
    invariant: V1
    priority: high
    rationale: >
      Tasks with many downstream BLOCKS should have higher energy than isolated tasks.
      If the correlation is weak, urgency accumulation isn't working.
    query: |
      MATCH (t:Narrative {type: 'task', status: 'active'})
      OPTIONAL MATCH (t)-[:LINK {verb: 'blocks'}]->(blocked)
      WITH t, count(blocked) AS block_count
      RETURN avg(CASE WHEN block_count > 0 THEN t.energy ELSE null END) AS avg_blocker_energy,
             avg(CASE WHEN block_count = 0 THEN t.energy ELSE null END) AS avg_isolated_energy
    threshold: avg_blocker_energy > avg_isolated_energy
    action: Investigate urgency accumulation algorithm

  - name: completed_task_decay_rate
    invariant: V7
    priority: medium
    rationale: >
      Completed tasks should lose 50% energy per half-life period.
      If they're not decaying, the decay algorithm isn't running.
    query: |
      MATCH (t:Narrative {type: 'task', status: 'done'})
      WHERE t.completed_at IS NOT NULL
        AND (timestamp() - t.completed_at) / 3600000 > 4
        AND t.energy > 0.3
      RETURN t.id, t.energy, (timestamp() - t.completed_at) / 3600000 AS hours_since_completion
    threshold: count = 0 (no completed task should have >0.3 energy after 4 hours)
    action: Check if apply_task_decay() is running in tick loop

  - name: crystallization_rate
    invariant: V3
    priority: high
    rationale: >
      Completed tasks with TRACE artifacts should have corresponding Thing nodes.
      Missing artifacts mean crystallization failed.
    query: |
      MATCH (t:Narrative {type: 'task', status: 'done'})
      WHERE t.completed_at IS NOT NULL
      OPTIONAL MATCH (a:Thing)-[:LINK {verb: 'implements'}]->(t)
      OPTIONAL MATCH (b:Thing)-[:LINK {verb: 'resolves'}]->(t)
      WITH t, count(a) + count(b) AS artifact_count
      WHERE artifact_count = 0
      RETURN t.id
    threshold: count / total_completed < 0.5 (at least 50% of completed tasks should have artifacts)
    action: Check crystallization algorithm and TRACE format
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (energy manipulators) | energy_topology_correlation | Urgency must reflect dependency pressure |
| O2 (cascades) | orphaned_blocks_on_completed_tasks | Cascade failures leave the org stalled |
| O3 (crystallization) | crystallization_rate | Missing artifacts = organizational amnesia |
| O4 (learning) | (future: expertise_weight_drift) | Weights should reflect actual success |
| O5 (rapid decay) | completed_task_decay_rate | Completed tasks must fade |

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_orphaned_blocks
    purpose: V2 — no BLOCKS on completed tasks
    status: pending
    priority: critical

  - name: check_circular_blocks
    purpose: V4 — no deadlock cycles
    status: pending
    priority: critical

  - name: check_energy_topology
    purpose: V1 — urgency reflects dependency graph
    status: pending
    priority: high

  - name: check_decay_rate
    purpose: V7 — completed tasks decay on schedule
    status: pending
    priority: medium

  - name: check_crystallization
    purpose: V3 — completed work produces artifacts
    status: pending
    priority: high
```

---

## KNOWN GAPS

<!-- @mind:todo Implement all health checkers — code not yet written -->
<!-- @mind:todo Add expertise_weight_drift checker for O4 (learning) -->
<!-- @mind:todo Add cascade_latency checker — time from completion to downstream wake -->
