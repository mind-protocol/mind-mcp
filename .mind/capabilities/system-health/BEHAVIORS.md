# System Health — Behaviors: Observable Effects of Self-Monitoring

```
STATUS: CANONICAL
CAPABILITY: system-health
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES.md
THIS:            BEHAVIORS.md (you are here)
VOCABULARY:      ./VOCABULARY.md
VALIDATION:      ./VALIDATION.md
HEALTH:          ./HEALTH.md
IMPLEMENTATION:  ./IMPLEMENTATION.md
SYNC:            ./SYNC.md

RUNTIME:         ./runtime/checks.py
TASKS:           ./tasks/
```

> **Contract:** Read OBJECTIVES first — every behavior traces to a ranked objective. Read VOCABULARY for problem types and thresholds. Read VALIDATION for the invariants each behavior must satisfy.

---

## BEHAVIORS

### B1: Stuck Agent Detected

**Why:** Objective #1 — detect stuck/dead agents before tasks rot. A stuck agent holds claimed tasks hostage. Without detection, the queue silently drains.

```
GIVEN:  An agent's last heartbeat is older than STUCK_THRESHOLD (300s)
        AND the agent's last heartbeat is within DEAD_THRESHOLD (600s)
WHEN:   stuck_agent_detection check runs (every 60s)
THEN:   Signal.degraded returned with:
        - agent_id of the first stuck agent
        - stuck_count (total number of stuck agents)
        - stuck_agents list (all stuck agent IDs)
AND:    Problem AGENT_STUCK surfaced
AND:    TASK_investigate_stuck_agent created for the first stuck agent
```

### B2: Dead Agent Detected and Tasks Released

**Why:** Objectives #1 and #2 — dead agents are the critical escalation of stuck, and their tasks must be auto-released. This is the highest-value self-repair behavior.

```
GIVEN:  An agent's last heartbeat is older than DEAD_THRESHOLD (600s)
WHEN:   stuck_agent_detection check runs (every 60s)
THEN:   Signal.critical returned with:
        - agent_id of the first dead agent
        - dead_count and dead_agents list
        - stuck_count (agents stuck but not yet dead)
AND:    Problem AGENT_DEAD surfaced
AND:    TASK_investigate_stuck_agent created
AND:    Orphan task detection (B3) will auto-release this agent's tasks on next cycle
```

### B3: Orphan Tasks Auto-Released

**Why:** Objective #2 — auto-heal what can be auto-healed. Dead agents never resume, so releasing their tasks is provably safe and unblocks the queue.

```
GIVEN:  One or more agents have status == DEAD
        AND those agents have claimed tasks in the throttler
WHEN:   orphan_task_detection check runs (every 60s)
THEN:   Each orphan task is released via throttler.on_abandon()
AND:    Signal.degraded returned with:
        - task_id of the first released task
        - orphan_count (total orphan tasks found)
        - released_tasks list (all released task IDs)
        - auto_fixed = True
AND:    Problem TASK_ORPHAN surfaced
AND:    TASK_release_orphan_task created for audit trail
```

### B4: No Orphan Tasks When No Dead Agents

**Why:** Objective #2 tradeoff — only release tasks for DEAD agents, never for RUNNING or STUCK. Releasing a live agent's task destroys in-progress work.

```
GIVEN:  No agents have status == DEAD
WHEN:   orphan_task_detection check runs
THEN:   Signal.healthy() returned
AND:    No tasks released
AND:    No problem surfaced
```

### B5: Health Check Crash Caught

**Why:** Objective #4 — self-monitoring completeness. A crashed check that returns no signal is the worst failure mode because the system appears healthy.

```
GIVEN:  Any check.py function crashes or times out during execution
WHEN:   Error is written to .mind/logs/health.log
THEN:   health_check_failure check fires immediately (stream-based trigger)
AND:    Signal.degraded returned with:
        - error message from the crash
        - capability name that owns the crashed check
AND:    Problem HEALTH_CHECK_FAILED surfaced
AND:    TASK_investigate_health_failure created
```

### B6: Queue Stall Warning

**Why:** Objective #5 — queue visibility. A full queue with no workers is the leading indicator of a system-wide stall.

```
GIVEN:  Pending unclaimed tasks >= 80% of max_pending capacity
        AND zero agents have status == RUNNING
WHEN:   agent_queue_health check runs (every 5 min)
THEN:   Signal.degraded returned with:
        - pending count and max_pending
        - no_workers = True
AND:    Problem QUEUE_UNHEALTHY surfaced
AND:    TASK_investigate_queue created
```

### B7: Queue Critical — Workers Stuck

**Why:** Objective #5 escalation — a full queue is bad, but a full queue with stuck workers is worse because the workers can't drain it.

```
GIVEN:  Pending unclaimed tasks >= 80% of max_pending capacity
        AND one or more agents have status == STUCK
WHEN:   agent_queue_health check runs (every 5 min)
THEN:   Signal.critical returned with:
        - pending count and max_pending
        - active_agents count (running)
        - stuck_agents count
AND:    Problem QUEUE_UNHEALTHY surfaced at CRITICAL severity
AND:    TASK_investigate_queue created
```

### B8: Healthy System Produces Zero Alerts

**Why:** Objective #3 tradeoff — fewer false positives over faster detection. If the system is healthy, all checks MUST return Signal.healthy(). Any signal on a healthy system is a bug in the monitoring.

```
GIVEN:  All agents have heartbeats within STUCK_THRESHOLD (< 300s old)
        AND no agents have status == DEAD
        AND queue is below 80% capacity
        AND no errors in health.log
WHEN:   Any check runs (stuck_agent_detection, orphan_task_detection,
        health_check_failure, agent_queue_health)
THEN:   Signal.healthy() returned
AND:    No problem surfaced
AND:    No task created
```

### B9: CRITICAL Overrides DEGRADED

**Why:** Objective #3 — accurate severity classification. When both stuck and dead agents exist, the signal must report CRITICAL (dead), not DEGRADED (stuck). Severity is always max(conditions), never averaged.

```
GIVEN:  Both stuck agents (heartbeat 300-600s old) and dead agents (heartbeat > 600s)
        exist simultaneously
WHEN:   stuck_agent_detection check runs
THEN:   Signal.critical returned (not degraded)
AND:    Signal includes both dead_count and stuck_count
AND:    agent_id is set to the first DEAD agent (highest severity gets primary handling)
```

### B10: Checks Run Independently

**Why:** Objective #4 + VALIDATION V8 — check isolation. A crash in one check must never prevent others from running.

```
GIVEN:  stuck_agent_detection crashes (import error, exception, timeout)
WHEN:   The runtime iterates the CHECKS registry
THEN:   orphan_task_detection still runs and returns its signal
AND:    health_check_failure still runs and returns its signal
AND:    agent_queue_health still runs and returns its signal
AND:    The crashed check is reported via H3 (health_check_failure)
```

### B11: Signals Carry Full Context

**Why:** Objective #5 in OBJECTIVES, V7 in VALIDATION — signal atomicity. Task handlers must act on the signal alone without re-querying the system.

```
GIVEN:  Any check detects a problem
WHEN:   It constructs its Signal response
THEN:   The signal includes:
        - Primary entity ID (agent_id for stuck/dead, task_id for orphan)
        - Counts (dead_count, stuck_count, orphan_count, pending, etc.)
        - Entity lists (dead_agents, stuck_agents, released_tasks)
        - Context flags (auto_fixed, no_workers, etc.)
AND:    The task handler can act immediately without calling get_registry()
        or get_throttler() again
```

---

## OBJECTIVES SERVED

| Behavior | Objective | What It Protects |
|----------|-----------|-----------------|
| B1 | #1 Detect stuck agents | Queue throughput — stuck agents hold tasks |
| B2 | #1 Detect dead agents | Queue throughput — dead agents block indefinitely |
| B3 | #2 Auto-heal | Queue recovery — orphan tasks released to pending |
| B4 | #2 Safety boundary | In-progress work — never release live agent's tasks |
| B5 | #4 Self-monitoring | Monitor trustworthiness — crashed checks are caught |
| B6 | #5 Queue visibility | Early warning — queue filling with no workers |
| B7 | #5 Queue escalation | Critical warning — queue full AND workers stuck |
| B8 | #3 No false positives | Operator trust — healthy system = zero alerts |
| B9 | #3 Severity accuracy | Correct escalation — CRITICAL always wins over DEGRADED |
| B10 | #4 Check isolation | Resilience — one crash doesn't kill all monitoring |
| B11 | #3 Signal completeness | Handler efficiency — act without re-querying |

---

## INPUTS / OUTPUTS

### Primary Functions: 4 @check-decorated functions in runtime/checks.py

**Inputs:**

| Parameter | Type | Source |
|-----------|------|--------|
| ctx | CheckContext | Runtime injects project_root, graph, trigger info |
| Agent registry | AgentRegistry | Lazy import from runtime.capability.agents |
| Throttler | Throttler | Lazy import from runtime.capability.throttler |
| health.log | Stream | Trigger source for H3 |

**Outputs:**

| Output | Type | Consumer |
|--------|------|----------|
| Signal.healthy() | dict | Runtime — no action |
| Signal.degraded(...) | dict | Task creator — spawns investigation task |
| Signal.critical(...) | dict | Task creator — spawns urgent task |

**Side Effects:**

- Orphan tasks released back to pending via throttler.on_abandon() (B3)
- TASK_* nodes created in graph for each problem detected
- Health check failures logged to .mind/logs/health.log

---

## EDGE CASES

### E1: Agent Recovers During STUCK Window

```
GIVEN:  Agent has been STUCK (no heartbeat for 5+ min)
        AND agent sends a heartbeat before reaching DEAD_THRESHOLD (10 min)
THEN:   Next check cycle sees fresh heartbeat
AND:    Agent is no longer flagged — Signal.healthy() returned
AND:    No task created (self-resolved)
```

### E2: All Agents Dead Simultaneously

```
GIVEN:  Every registered agent has status == DEAD
WHEN:   stuck_agent_detection runs
THEN:   Signal.critical with dead_count = total agent count
AND:    orphan_task_detection releases ALL claimed tasks on next cycle
AND:    agent_queue_health likely fires CRITICAL (queue full, zero running)
AND:    Three simultaneous CRITICAL signals — each creates its own task
```

### E3: Queue at Exactly 80%

```
GIVEN:  pending == max_pending * 0.8 (exact boundary)
WHEN:   agent_queue_health runs
THEN:   Condition `pending >= max_pending * 0.8` is TRUE
AND:    Signal fires (DEGRADED or CRITICAL depending on worker state)
AND:    Boundary is inclusive — 80% exactly triggers the alert
```

### E4: No Agents Registered

```
GIVEN:  Agent registry is empty (no agents have ever registered)
WHEN:   stuck_agent_detection runs
THEN:   No stuck or dead agents found (empty iteration)
AND:    Signal.healthy() returned
AND:    This is correct — no agents means no agents to be stuck
```

### E5: Health Check Crash During Orphan Release

```
GIVEN:  orphan_task_detection is mid-execution, has released 2 of 5 orphan tasks
        AND the function crashes on the 3rd release
THEN:   The 2 already-released tasks remain released (side effect committed)
AND:    The remaining 3 tasks are NOT released this cycle
AND:    H3 (health_check_failure) fires for the crash
AND:    Next cycle, orphan_task_detection runs again and picks up the remaining 3
```

---

## ANTI-BEHAVIORS

### A1: Never Release Live Agent Tasks

```
GIVEN:   Agent has status RUNNING or STUCK (heartbeat < DEAD_THRESHOLD)
WHEN:    orphan_task_detection runs
MUST NOT: Release any task claimed by this agent
INSTEAD:  Only release tasks for agents with status == DEAD
```

### A2: Never Downgrade DEAD to STUCK

```
GIVEN:   Agent was marked DEAD (heartbeat > 600s old)
WHEN:    Agent sends a single heartbeat
MUST NOT: Automatically restore to STUCK or RUNNING based on one heartbeat
INSTEAD:  Require explicit recovery event (re-registration or operator action)
```

### A3: Never Return DEGRADED When CRITICAL Conditions Met

```
GIVEN:   Dead agents exist (CRITICAL condition)
WHEN:    stuck_agent_detection evaluates severity
MUST NOT: Return Signal.degraded because stuck agents also exist
INSTEAD:  Return Signal.critical — highest severity wins
```

### A4: Never Swallow Check Exceptions

```
GIVEN:   A check function raises an unhandled exception
WHEN:    Runtime catches the exception
MUST NOT: Return Signal.healthy() as a default fallback
INSTEAD:  Let the exception propagate to health.log, triggering H3
```

### A5: Never Auto-Fix Non-Orphan Problems

```
GIVEN:   AGENT_STUCK, HEALTH_CHECK_FAILED, or QUEUE_UNHEALTHY detected
WHEN:    System-health processes the signal
MUST NOT: Attempt to restart agents, kill processes, or reconfigure the queue
INSTEAD:  Create an investigation task and let the appropriate agent/human handle it
```

---

## MARKERS

<!-- @mind:proposition B2 and B3 could be merged into a single "dead agent cleanup" behavior that both detects death AND releases tasks in one cycle, eliminating the 1-cycle delay between detection and release. Current design separates them for isolation (V8) but costs 60s of orphan persistence. -->
<!-- @mind:response B2_B3_MERGE: Keep them separate. The isolation benefit is worth the 60s.

Here's why: E5 already documents the failure mode — orphan_task_detection crashes mid-release, 2 of 5 tasks released, remaining 3 picked up next cycle. If B2+B3 are merged into one function, that same crash also kills the death detection signal. With separation: B2 crashes → B3 still releases. B3 crashes → B2 already surfaced AGENT_DEAD. Each function protects the other's failure mode. Merging eliminates that redundancy.

The 60s cost is bounded and predictable. Dead agents aren't coming back — their tasks aren't going anywhere in 60 seconds. And the orphan tasks are already unclaimed (the dead agent isn't processing them), so the only cost is 60s of queue capacity waste. In a system where DEAD_THRESHOLD is 600s, another 60s is noise.

BUT — if the 60s really bothers you, there's a third option that preserves isolation: make B3 event-driven instead of poll-driven. When B2 fires AGENT_DEAD, the signal triggers B3 immediately (same tick, separate function). The @check decorator already supports triggers.on_signal() — wire B3 to trigger on AGENT_DEAD instead of cron.every(60). Same-cycle release, full isolation, zero architectural compromise. Best of both worlds.

The current poll-poll design is simple and correct. The signal-trigger design is optimal. The merged design is a false economy. — @mind 2026-03-15 -->
