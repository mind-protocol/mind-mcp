# Swarm Driver — Validation

```
STATUS: CANONICAL
CAPABILITY: swarm-driver
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES.md
PATTERNS:        ./PATTERNS.md
BEHAVIORS:       ./BEHAVIORS.md
ALGORITHM:       ./ALGORITHM.md
THIS:            VALIDATION.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION.md
HEALTH:          ./HEALTH.md
SYNC:            ./SYNC.md
```

---

## PURPOSE

Invariants that MUST hold for correct driver operation. If any of these break, the swarm is flying blind or flooding.

---

## INVARIANTS

### V1: Task Singleton

```
INVARIANT: At most ONE driver-created task active at any time

MUST:
  - Check is_task_active(last_task_id) before creating
  - Skip creation if active task exists
  - Only create after previous task completed or no previous exists

NEVER:
  - Create task while another driver task is pending/claimed/in_progress
  - Create multiple tasks in a single cycle

CHECK: Query graph for task_runs where source="swarm-driver" AND status IN (pending, claimed, in_progress). Count MUST be 0 or 1.
```

### V2: Position Monotonicity

```
INVARIANT: File positions never go backward

MUST:
  - New position >= old position for every log file
  - Position equals f.tell() after reading
  - Positions persist across restarts via driver_state.json

NEVER:
  - Re-read lines already processed
  - Reset positions to 0 (except on explicit driver reset)
  - Lose position data on crash (write state before creating task)

CHECK: For each file in positions: current_position >= previous_position
```

### V3: Signal-to-Task Mapping Correctness

```
INVARIANT: Every signal type maps to exactly one template and one agent

MUST:
  - ERROR_DETECTED    → TASK_investigate_error → AGENT_Fixer
  - AGENT_STUCK       → TASK_unblock          → AGENT_Weaver
  - SYNC_UPDATE_NEEDED → TASK_update_sync     → AGENT_Witness
  - NO_TASKS_AVAILABLE → TASK_scan_for_work   → AGENT_Scout

NEVER:
  - Route error signals to Scout
  - Route stuck signals to Witness
  - Create task with unknown signal type and no fallback
  - Default mapping: unknown type → TASK_investigate → AGENT_Fixer

CHECK: task_run.template matches SIGNAL_TO_TEMPLATE[signal.type]
CHECK: task_run.agent matches SIGNAL_TO_AGENT[signal.type]
```

### V4: Priority Ordering

```
INVARIANT: Highest-priority signal always wins selection

MUST:
  - max(signals, key=priority) is the one that creates a task
  - Priority values: ERROR=10, STUCK=8, IDLE=7, SYNC=5
  - Ties broken by signal order (first detected wins)

NEVER:
  - Create task from lower-priority signal when higher exists
  - Skip a signal without evaluating its priority

CHECK: Created task's signal.priority >= all other signals' priorities in same cycle
```

### V5: No-Op Safety

```
INVARIANT: Driver cycle with no new content produces zero side effects

MUST:
  - Return immediately if all file sizes <= stored positions
  - No state file writes on no-op
  - No graph writes on no-op
  - No SYNC updates on no-op

NEVER:
  - Create signals from stale (already-processed) log content
  - Write driver_state.json when nothing changed
  - Append to SYNC on no-op cycle

CHECK: If collect_new_lines() returns empty, no state mutations occur
```

### V6: Context Preservation

```
INVARIANT: Every task carries actionable context from the triggering logs

MUST:
  - ERROR_DETECTED includes error message and surrounding lines
  - AGENT_STUCK includes last 5 lines from agent log
  - SYNC_UPDATE_NEEDED includes completion entries
  - NO_TASKS_AVAILABLE includes confirmation of zero pending

NEVER:
  - Create task with empty context
  - Include entire log file as context (extract relevant lines only)

CHECK: task_run.context is non-empty and contains lines from triggering log
```

### V7: Cycle Frequency

```
INVARIANT: Driver runs every 2 minutes, no faster

MUST:
  - Minimum 2-minute interval between cycles
  - Optional fast-path via file_watch (but still rate-limited)
  - last_run timestamp updated on every cycle that runs

NEVER:
  - Run back-to-back cycles without interval
  - Stack multiple cycles if previous is slow

CHECK: current_time - state.last_run >= 120 seconds
```

### V8: State File Integrity

```
INVARIANT: driver_state.json is always valid JSON with required fields

MUST:
  - Contains: positions (dict), last_task_id (string|null), last_run (ISO timestamp)
  - Written atomically (write temp + rename)
  - Readable on next cycle without error

NEVER:
  - Write partial JSON
  - Corrupt state on crash (atomic write protects)
  - Omit required fields

CHECK: json.loads(driver_state.json) succeeds and contains all required keys
```

---

## VALIDATION CHECKS

| Check | Pass Condition |
|-------|----------------|
| Singleton | 0-1 active driver tasks in graph |
| Position monotonicity | All positions >= previous values |
| Mapping correctness | Template + agent match signal type |
| Priority ordering | Highest-priority signal selected |
| No-op safety | Zero mutations on empty cycle |
| Context present | task_run.context is non-empty |
| Cycle frequency | >= 120s between runs |
| State integrity | Valid JSON, all fields present |

---

## ERROR MESSAGES

| Violation | Message |
|-----------|---------|
| Duplicate task | `Singleton violated: {count} active driver tasks` |
| Position regression | `Position went backward: {file} {old} -> {new}` |
| Wrong mapping | `Signal {type} routed to wrong agent: {actual} (expected {expected})` |
| Priority skip | `Lower-priority signal {low} selected over {high}` |
| No-op mutation | `State mutated on no-op cycle` |
| Empty context | `Task {id} created with empty context` |
| Rapid fire | `Cycle ran {seconds}s after previous (min 120s)` |
| Corrupt state | `driver_state.json parse error: {error}` |

---

## TASK COMPLETION CRITERIA

A driver cycle is **correct** when:

1. Only new log content was processed (positions advanced, never regressed)
2. All detection patterns ran against new content
3. Highest-priority signal was selected (or no signals found)
4. Singleton was enforced (no task if one already active)
5. Created task has correct template, agent, and non-empty context
6. SYNC was updated with driver action
7. State file written atomically with new positions

If any invariant fails, the driver MUST log the violation and skip task creation for that cycle rather than create an incorrect task.
