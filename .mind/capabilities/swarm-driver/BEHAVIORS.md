# Swarm Driver — Behaviors

```
STATUS: CANONICAL
CAPABILITY: swarm-driver
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES.md
PATTERNS:        ./PATTERNS.md
THIS:            BEHAVIORS.md (you are here)
ALGORITHM:       ./ALGORITHM.md
VALIDATION:      ./VALIDATION.md
IMPLEMENTATION:  ./IMPLEMENTATION.md
HEALTH:          ./HEALTH.md
SYNC:            ./SYNC.md
```

---

## PURPOSE

Observable behaviors of the swarm driver. Each behavior maps to a detection pattern (PATTERNS.md) or algorithm step (ALGORITHM.md). GIVEN/WHEN/THEN format — if you can't observe it, it doesn't belong here.

---

## B1: Error Detection

**When:** New lines appear in error logs

```
GIVEN:  New content in errors.log or agent_*.log
WHEN:   Driver cycle runs (every 2 minutes)
THEN:   Scan for "ERROR" or "FAILED" patterns
AND:    Extract target (module/file) and context (surrounding lines)
AND:    Create Signal(type="ERROR_DETECTED", priority=10)
```

**Effect:** Errors surface within 2 minutes. Fixer gets dispatched.

---

## B2: Stuck Agent Detection

**When:** Agent shows retry/timeout patterns

```
GIVEN:  New content in agent_*.log
WHEN:   Driver cycle runs
THEN:   Scan for "retrying" or "timeout" patterns
AND:    Identify stuck agent from log source filename
AND:    Create Signal(type="AGENT_STUCK", priority=8)
```

**Effect:** Stuck agents get help from Weaver within one cycle.

---

## B3: SYNC Drift Detection

**When:** Completions not reflected in project state

```
GIVEN:  New content in completions.log or agent_*.log
WHEN:   Driver cycle runs
THEN:   Scan for "completed" or "done" patterns
AND:    Create Signal(type="SYNC_UPDATE_NEEDED", priority=5)
```

**Effect:** SYNC stays current. Witness updates project state.

---

## B4: Idle Agent Detection

**When:** No pending tasks available

```
GIVEN:  New content in tasks.log
WHEN:   Driver cycle runs
AND:    "pending" count in tasks.log is 0
THEN:   Create Signal(type="NO_TASKS_AVAILABLE", priority=7)
```

**Effect:** Scout scans for new work. Agents never idle if work exists.

---

## B5: Signal Priority Resolution

**When:** Multiple signals detected in one cycle

```
GIVEN:  analyze_logs() returns multiple signals
WHEN:   Driver selects action
THEN:   Pick signal with highest priority
AND:    Ignore lower-priority signals this cycle
AND:    Lower signals will fire on next cycle if they persist
```

**Effect:** Critical issues (errors=10) always outrank lower signals.

---

## B6: Singleton Enforcement

**When:** Previous driver task still active

```
GIVEN:  state.last_task_id is set
WHEN:   Driver cycle runs
AND:    is_task_active(last_task_id) returns true
THEN:   Skip task creation entirely
AND:    Do not update positions (signals preserved for next cycle)
```

**Effect:** Never more than one driver-created task active at a time. No task flooding.

---

## B7: Task Creation

**When:** Signal selected, no active task blocking

```
GIVEN:  Signal with highest priority selected
AND:    No active driver task (singleton check passed)
WHEN:   Driver creates task
THEN:   Map signal type to task template:
        - ERROR_DETECTED    → TASK_investigate_error
        - AGENT_STUCK       → TASK_unblock
        - SYNC_UPDATE_NEEDED → TASK_update_sync
        - NO_TASKS_AVAILABLE → TASK_scan_for_work
AND:    Map signal type to agent:
        - ERROR_DETECTED    → AGENT_Fixer
        - AGENT_STUCK       → AGENT_Weaver
        - SYNC_UPDATE_NEEDED → AGENT_Witness
        - NO_TASKS_AVAILABLE → AGENT_Scout
AND:    Create task_run node in graph with signal context
```

**Effect:** Right task reaches right agent with right context.

---

## B8: Reactivation

**When:** Issue recurs after previous task completed

```
GIVEN:  Previous driver task has completed (not active)
WHEN:   Same signal type fires again on next cycle
THEN:   Create new task — singleton allows it because previous completed
AND:    New task carries fresh context from latest logs
```

**Effect:** Recurring issues get re-addressed. No "fixed once, ignored forever."

---

## B9: Position Tracking

**When:** Every cycle, regardless of signals

```
GIVEN:  Driver reads log files
WHEN:   Cycle completes (with or without task creation)
THEN:   Update file positions in driver_state.json
AND:    Record last_run timestamp
AND:    Only save if positions changed (skip no-op writes)
```

**Effect:** Logs are never re-read. Positions survive restarts.

---

## B10: SYNC Update

**When:** Task created

```
GIVEN:  task_run created from signal
WHEN:   create_task() succeeds
THEN:   Append driver action entry to SYNC_Project_State.md:
        - Signal type
        - Target
        - Task ID
        - Priority
        - Timestamp
```

**Effect:** Project state reflects driver actions. Full audit trail.

---

## B11: No-Op Cycle

**When:** No new log content exists

```
GIVEN:  All log file sizes <= stored positions
WHEN:   Driver cycle runs
THEN:   Return immediately — no reads, no analysis, no state changes
```

**Effect:** Zero work when there's nothing new. No wasted cycles.

---

## BEHAVIOR SUMMARY

| Trigger | Behavior | Output |
|---------|----------|--------|
| ERROR/FAILED in logs | B1: Error detection | Signal(priority=10) |
| retrying/timeout in logs | B2: Stuck detection | Signal(priority=8) |
| completed/done in logs | B3: SYNC drift | Signal(priority=5) |
| Zero pending tasks | B4: Idle detection | Signal(priority=7) |
| Multiple signals | B5: Priority resolution | Highest wins |
| Active task exists | B6: Singleton | Skip creation |
| Signal + no blocker | B7: Task creation | task_run in graph |
| Issue recurs | B8: Reactivation | New task_run |
| Every cycle | B9: Position tracking | State persisted |
| Task created | B10: SYNC update | Audit entry |
| Nothing new | B11: No-op | Early return |
