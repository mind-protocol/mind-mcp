# System Health — Validation: What Must Be True

```
STATUS: CANONICAL
CAPABILITY: system-health
```

---

## CHAIN

```
VOCABULARY:      ./VOCABULARY.md
THIS:            VALIDATION.md (you are here)
HEALTH:          ./HEALTH.md
RUNTIME:         ./runtime/checks.py
TASKS:           ./tasks/
```

---

## PURPOSE

Invariants that MUST hold for the self-monitoring capability to be trustworthy. If system-health lies about agent state, misclassifies severity, or silently fails, the entire capability runtime flies blind. A broken health monitor is worse than no health monitor — it creates false confidence.

---

## INVARIANTS

### V1: Stuck Detection Accuracy

**Why we care:** A false positive kills a healthy agent's work. A false negative lets a dead agent hold tasks hostage indefinitely.

```
MUST:
  - Agent marked STUCK only when last_heartbeat > now - STUCK_THRESHOLD (300s)
  - Agent marked DEAD only when last_heartbeat > now - DEAD_THRESHOLD (600s)
  - STUCK → DEAD transition is monotonic: once DEAD, stays DEAD until explicit recovery
  - Every STUCK/DEAD signal includes agent_id for atomic handling

NEVER:
  - Mark an agent with a recent heartbeat (< 300s) as STUCK
  - Mark a STUCK agent (300-600s) as DEAD
  - Downgrade DEAD back to STUCK without explicit recovery event
  - Omit agent_id from the signal (handler can't act without it)

CHECK: For every agent flagged, (now - last_heartbeat) > STUCK_THRESHOLD
CHECK: DEAD agents have (now - last_heartbeat) > DEAD_THRESHOLD
```

### V2: Severity Escalation Correctness

**Why we care:** Returning DEGRADED when conditions are CRITICAL delays emergency response. Returning CRITICAL for a minor issue wastes human attention.

```
MUST:
  - CRITICAL returned when dead_agents > 0 (stuck_agent_detection)
  - CRITICAL returned when queue >= 80% full AND stuck_agents > 0 (agent_queue_health)
  - DEGRADED returned for stuck-but-not-dead agents
  - DEGRADED returned for queue >= 80% full AND zero active workers
  - HEALTHY returned when no conditions match any threshold

NEVER:
  - Return DEGRADED when CRITICAL conditions are met
  - Return HEALTHY when any threshold is breached
  - Return CRITICAL for conditions that only warrant DEGRADED
```

### V3: Orphan Task Auto-Release Safety

**Why we care:** Orphan tasks block the work queue. But releasing a task claimed by a live agent destroys in-progress work.

```
MUST:
  - Only release tasks claimed by agents with status == DEAD
  - Release via throttler.on_abandon() (proper state transition)
  - Return auto_fixed=True in signal so downstream knows it's already handled
  - Include released_tasks list for audit trail

NEVER:
  - Release a task claimed by a RUNNING or STUCK agent
  - Release a task without verifying the claiming agent is DEAD
  - Release the same task twice in one cycle (idempotent check)
  - Silently release without reporting in the signal
```

### V4: Self-Monitoring Completeness

**Why we care:** A health check that crashes silently is the worst failure mode — the system thinks it's healthy because no alarm fired.

```
MUST:
  - health_check_failure (H3) fires when any check.py crashes or times out
  - H3 trigger is stream-based (on_error), not cron-based — catches failures immediately
  - H3 signal includes capability name and error details
  - All 4 checks registered in CHECKS list and discoverable by the runtime

NEVER:
  - Swallow exceptions in check functions
  - Let a crashed check return Signal.healthy() by default
  - Omit a check from the CHECKS registry
```

### V5: Threshold Consistency

**Why we care:** If runtime constants drift from documented thresholds, the system behaves differently than operators expect. Debugging becomes impossible.

```
MUST:
  - STUCK_THRESHOLD == 300 (5 minutes), matching VOCABULARY.md
  - DEAD_THRESHOLD == 600 (10 minutes), matching VOCABULARY.md
  - HEARTBEAT_INTERVAL check frequency == 60s, matching VOCABULARY.md
  - QUEUE_WARNING threshold == 80% (0.8 multiplier), matching VOCABULARY.md

NEVER:
  - Change a threshold in checks.py without updating VOCABULARY.md
  - Change a threshold in VOCABULARY.md without updating checks.py
  - Use magic numbers — all thresholds must reference named constants
```

### V6: No False Positives on Healthy Systems

**Why we care:** False alarms erode trust in the monitoring system. After enough false positives, operators ignore real alerts.

```
MUST:
  - Return Signal.healthy() when all agents have recent heartbeats
  - Return Signal.healthy() when no dead agents exist (orphan check)
  - Return Signal.healthy() when queue is below 80% capacity
  - Return Signal.healthy() when no errors in health.log

NEVER:
  - Fire AGENT_STUCK for a healthy system (no stuck agents)
  - Fire TASK_ORPHAN when no dead agents exist
  - Fire QUEUE_UNHEALTHY when queue has capacity and workers are running
```

### V7: Signal Atomicity

**Why we care:** Each signal must contain enough information for its task handler to act without re-querying. Incomplete signals force duplicate work.

```
MUST:
  - stuck_agent_detection: includes agent_id, dead_count, stuck_count, agent lists
  - orphan_task_detection: includes task_id, orphan_count, released_tasks, auto_fixed
  - health_check_failure: includes error message and capability name
  - agent_queue_health: includes pending count, max_pending, active_agents, stuck_agents

NEVER:
  - Return a signal without the primary entity ID (agent_id or task_id)
  - Return counts without the corresponding ID lists
  - Force the task handler to re-run detection logic
```

### V8: Check Isolation

**Why we care:** A failure in one check must not cascade to other checks. Each check must be independently callable.

```
MUST:
  - Each check imports its dependencies inside the function body (lazy imports)
  - Each check handles its own errors without affecting others
  - Each check returns a valid Signal (healthy, degraded, or critical)
  - CHECKS registry is a flat list — runtime iterates independently

NEVER:
  - Share mutable state between check functions
  - Let one check's exception prevent other checks from running
  - Import registry/throttler at module level (circular import risk)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Monitoring is untrustworthy |
| **HIGH** | Major value lost | Alerts are wrong or incomplete |
| **MEDIUM** | Partial value lost | Works but creates noise or confusion |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Stuck detection accuracy | CRITICAL |
| V2 | Severity escalation correctness | CRITICAL |
| V3 | Orphan task auto-release safety | HIGH |
| V4 | Self-monitoring completeness | CRITICAL |
| V5 | Threshold consistency | HIGH |
| V6 | No false positives on healthy systems | HIGH |
| V7 | Signal atomicity | MEDIUM |
| V8 | Check isolation | MEDIUM |

---

## VALIDATION CHECKS

| Check | Pass Condition |
|-------|----------------|
| Stuck accuracy | Flagged agents have heartbeat gap > threshold |
| Severity ordering | CRITICAL returned whenever CRITICAL conditions exist |
| Orphan safety | Only dead-agent tasks released |
| Self-monitoring | H3 fires on any check crash |
| Threshold match | Runtime constants == VOCABULARY values |
| No false positives | Healthy system → all checks return healthy |
| Signal completeness | Every signal has primary entity ID + counts |
| Check isolation | Each check callable independently, lazy imports |

---

## ERROR MESSAGES

| Violation | Message |
|-----------|---------|
| False stuck | `Agent {id} flagged STUCK but last heartbeat was {seconds}s ago (threshold: 300s)` |
| Severity mismatch | `DEGRADED returned but {count} dead agents exist (should be CRITICAL)` |
| Unsafe release | `Task {id} released but claiming agent {agent} status is {status} (expected DEAD)` |
| Silent failure | `Check {id} crashed but health_check_failure did not fire` |
| Threshold drift | `{constant} is {actual} in checks.py but {expected} in VOCABULARY.md` |
| False positive | `{check_id} returned {severity} but no threshold conditions met` |
| Incomplete signal | `Signal from {check_id} missing required field: {field}` |
| Cascade failure | `Check {id} exception propagated to {other_id}` |

---

## TASK COMPLETION CRITERIA

A system-health check cycle is **correct** when:

1. Every agent's heartbeat gap is accurately measured against documented thresholds
2. Severity levels match conditions exactly (CRITICAL for dead agents/stuck+full queue, DEGRADED for stuck/empty queue)
3. Orphan tasks are released only for verified-dead agents, never for running/stuck
4. All 4 checks run independently — one failure doesn't block others
5. Every signal carries the primary entity ID and actionable context
6. Healthy systems produce zero alerts
7. Runtime constants match VOCABULARY.md exactly

If any invariant fails, the check MUST return Signal.degraded() or Signal.critical() with the violation details — never Signal.healthy().
