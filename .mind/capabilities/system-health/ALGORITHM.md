# System Health — Algorithm

```
STATUS: CANONICAL
CAPABILITY: system-health
```

---

## CHAIN

```
VOCABULARY:      ./VOCABULARY.md
PATTERNS:        ./PATTERNS.md
THIS:            ALGORITHM.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION.md
HEALTH:          ./HEALTH.md
```

---

## OVERVIEW

Four independent health checks, each triggered on its own schedule. All query runtime internals (AgentRegistry, Throttler) rather than parsing logs or files. H2 (orphan tasks) self-heals inline. The others create investigation tasks for agents.

---

## DATA STRUCTURES

### Signal

```python
Signal.healthy(message=...)       # No problem detected
Signal.degraded(**kwargs)         # Problem exists, non-critical
Signal.critical(**kwargs)         # Problem exists, urgent
```

### AgentStatus (from runtime.capability.agents)

```
RUNNING    # Agent alive, heartbeat fresh
STUCK      # No heartbeat for 5-10 minutes
DEAD       # No heartbeat for >10 minutes
```

### Throttler Stats (from runtime.capability.throttler)

```python
{
    "pending_unclaimed": int,   # Tasks waiting for a worker
    "max_pending": int,         # Queue capacity
    ...
}
```

### DriverState (driver_state.json)

```python
{
    "positions": {"file.log": int},
    "last_task_id": str | None,
    "last_run": str             # ISO timestamp
}
```

---

## ALGORITHM: H1 — Stuck Agent Detection

**Trigger:** `cron.every(60)` — runs every 60 seconds

```python
def stuck_agent_detection(ctx):
    registry = get_registry()

    # 1. Registry internally marks agents stuck/dead based on heartbeat age
    registry.check_stuck()

    # 2. Partition agents by status
    stuck  = [a for a in registry.agents.values() if a.status == STUCK]
    dead   = [a for a in registry.agents.values() if a.status == DEAD]

    # 3. Escalate by severity
    if dead:
        return Signal.critical(
            agent_id=dead[0].agent_id,
            dead_count=len(dead),
            dead_agents=[a.agent_id for a in dead],
            stuck_count=len(stuck),
        )

    if stuck:
        return Signal.degraded(
            agent_id=stuck[0].agent_id,
            stuck_count=len(stuck),
            stuck_agents=[a.agent_id for a in stuck],
        )

    return Signal.healthy()
```

### Key Decisions

```
IF any agent has no heartbeat for > DEAD_THRESHOLD (600s):
    → CRITICAL — agent is dead, its tasks will be orphaned
    → Primary agent_id set for atomic task handling
ELIF any agent has no heartbeat for > STUCK_THRESHOLD (300s):
    → DEGRADED — agent may be on slow op, investigate
ELSE:
    → HEALTHY
```

**Why dead outranks stuck:** A dead agent has orphaned tasks that block the pipeline. A stuck agent might recover on its own.

---

## ALGORITHM: H2 — Orphan Task Detection

**Trigger:** `cron.every(60)` — runs every 60 seconds

```python
def orphan_task_detection(ctx):
    throttler = get_throttler()
    registry = get_registry()

    # 1. Find all dead agents
    dead_ids = {
        a.agent_id for a in registry.agents.values()
        if a.status == DEAD
    }

    if not dead_ids:
        return Signal.healthy()

    # 2. Find tasks claimed by dead agents
    orphans = []
    for task_id, slot in throttler.active.items():
        if slot.claimed_by in dead_ids:
            orphans.append(task_id)
            # 3. AUTO-HEAL: release immediately
            throttler.on_abandon(task_id)

    # 4. Report what was fixed
    if orphans:
        return Signal.degraded(
            task_id=orphans[0],
            orphan_count=len(orphans),
            released_tasks=orphans,
            auto_fixed=True,
        )

    return Signal.healthy()
```

### Key Decisions

```
IF no dead agents:
    → HEALTHY — no orphans possible
ELIF dead agents have claimed tasks:
    → Release each task via throttler.on_abandon()
    → DEGRADED with auto_fixed=True (already healed)
ELSE (dead agents but no claimed tasks):
    → HEALTHY — dead agent had no active work
```

**Why auto-heal inline:** Orphan release is mechanical (call `on_abandon`). Waiting for an agent to claim a release task adds latency when the system is already degraded. The `auto_fixed=True` flag provides audit trail.

---

## ALGORITHM: H3 — Health Check Failure

**Trigger:** `stream.on_error(".mind/logs/health.log")` — reactive, fires on crash

```python
def health_check_failure(ctx):
    # Error details injected by the trigger system
    error = ctx.trigger_source or "Unknown error"

    return Signal.degraded(
        error=error,
        capability=ctx.capability,
    )
```

### Key Decisions

```
WHEN any check.py in any capability crashes or times out:
    → Stream trigger fires with error details
    → Always DEGRADED (never CRITICAL — one check failing doesn't kill the system)
    → Task created for agent to debug the failing check
```

**Why always DEGRADED, never CRITICAL:** A single check crash means one monitoring gap, not a system-wide failure. Other checks continue running. The investigation task handles root cause.

**Why no complex logic:** The trigger payload carries all context. This check is a thin passthrough — its job is to convert a stream event into a task, not to analyze the error.

---

## ALGORITHM: H4 — Queue Health

**Trigger:** `cron.every(5)` — runs every 5 minutes

```python
def agent_queue_health(ctx):
    throttler = get_throttler()
    registry = get_registry()
    stats = throttler.get_stats()

    pending = stats["pending_unclaimed"]
    max_pending = stats["max_pending"]

    active = count(a for a in registry.agents.values() if a.status == RUNNING)
    stuck  = count(a for a in registry.agents.values() if a.status == STUCK)

    # Decision matrix
    if pending >= max_pending * 0.8 and stuck > 0:
        return Signal.critical(
            pending=pending,
            max_pending=max_pending,
            active_agents=active,
            stuck_agents=stuck,
        )

    if pending >= max_pending * 0.8 and active == 0:
        return Signal.degraded(
            pending=pending,
            max_pending=max_pending,
            no_workers=True,
        )

    return Signal.healthy()
```

### Key Decisions

```
IF queue >= 80% full AND stuck agents exist:
    → CRITICAL — queue backing up AND workers jammed
    → Requires both agent investigation and possibly spawning new agents

ELIF queue >= 80% full AND zero active agents:
    → DEGRADED — queue backing up, no workers at all
    → May need to spawn agents or investigate why none are running

ELSE:
    → HEALTHY — queue has capacity or workers are draining it
```

**Why 80% threshold:** Leaves buffer before the queue is actually full. At 80%, there's time to react. At 100%, new tasks get dropped.

**Why stuck+full is CRITICAL but empty+full is only DEGRADED:** Stuck agents with a full queue means the system is actively failing — work is piling up AND workers are jammed. No agents with a full queue might just mean it's a cold start or quiet period that needs a spawn.

---

## DECISION TREE (all checks)

```
cron fires (60s)
├── H1: stuck_agent_detection
│   ├── dead agents?     → CRITICAL (mark dead, signal for orphan handling)
│   ├── stuck agents?    → DEGRADED (investigate)
│   └── all healthy?     → HEALTHY
│
├── H2: orphan_task_detection
│   ├── dead agents with claimed tasks?
│   │   ├── Yes → release each task inline → DEGRADED (auto_fixed)
│   │   └── No  → HEALTHY
│   └── no dead agents? → HEALTHY
│
cron fires (5m)
├── H4: agent_queue_health
│   ├── queue ≥80% + stuck agents?  → CRITICAL
│   ├── queue ≥80% + no workers?    → DEGRADED
│   └── otherwise?                  → HEALTHY
│
stream fires (on error)
└── H3: health_check_failure
    └── any check crashed? → DEGRADED (always)
```

---

## DATA FLOW

```
Runtime Internals                    Checks                    Output
─────────────────                    ──────                    ──────
AgentRegistry.agents ──────────────→ H1 (stuck detection) ──→ Signal
    .status (RUNNING/STUCK/DEAD)     H2 (orphan detection)    │
    .last_heartbeat                  H4 (queue health)        │
                                                              ▼
Throttler.active ──────────────────→ H2 (orphan detection) ──→ auto_fix (on_abandon)
    .claimed_by                                               │
                                                              ▼
Throttler.get_stats() ─────────────→ H4 (queue health) ─────→ Signal
    .pending_unclaimed                                        │
    .max_pending                                              ▼
                                                         task_run created
.mind/logs/health.log ─────────────→ H3 (check failure) ────→ (if degraded/critical)
    (stream trigger on error)
```

---

## COMPLEXITY

**Time:** O(A) per cycle where A = number of agents. Each check iterates the agent registry once.

**Space:** O(1) — no accumulated state. Checks are stateless; all state lives in AgentRegistry and Throttler.

**Bottlenecks:**
- `registry.check_stuck()` in H1 iterates all agents — negligible unless thousands of agents
- H2 iterates `throttler.active` (all claimed tasks) — same, negligible at current scale
- H4's `get_stats()` is a single dict read — O(1)
- H3 is reactive (no polling cost)

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|-------------|-------------|
| `runtime.capability.agents.get_registry()` | AgentRegistry singleton | Agent statuses, heartbeat ages |
| `runtime.capability.agents.AgentStatus` | Enum | RUNNING, STUCK, DEAD |
| `runtime.capability.throttler.get_throttler()` | Throttler singleton | Active task slots, queue stats |
| `runtime.capability.throttler.on_abandon(task_id)` | Release method | Task returned to pending |
| `runtime.capability.check` | Decorator | Registers check with trigger system |
| `runtime.capability.Signal` | Return type | healthy/degraded/critical factory |
| `runtime.capability.triggers` | Trigger config | cron.every(), stream.on_error() |
