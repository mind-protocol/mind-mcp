# System Health — Implementation

```
STATUS: CANONICAL
CAPABILITY: system-health
```

---

## CHAIN

```
VOCABULARY:      ./VOCABULARY.md
THIS:            IMPLEMENTATION.md (you are here)
HEALTH:          ./HEALTH.md
```

---

## PURPOSE

Self-monitoring capability for the capability runtime itself. Detects stuck agents, orphan tasks, failed health checks, and unhealthy queues. Provides auto-healing for recoverable problems and creates investigation tasks for the rest.

---

## FILE STRUCTURE

```
capabilities/system-health/                    # Self-contained capability
├── VOCABULARY.md                              # Problem IDs, thresholds, auto-resolution
├── IMPLEMENTATION.md                          # You are here
├── HEALTH.md                                  # Health indicators H1-H4
├── tasks/
│   ├── TASK_investigate_stuck_agent.md         # For AGENT_STUCK
│   ├── TASK_release_orphan_task.md             # For TASK_ORPHAN (auto-fixed)
│   └── TASK_investigate_health_failure.md      # For HEALTH_CHECK_FAILED
└── runtime/
    ├── __init__.py                            # Exports CHECKS list
    └── checks.py                              # @check decorated functions
```

### After `mind init`

```
.mind/capabilities/system-health/              # Full copy
└── [same structure]
```

---

## KEY COMPONENTS

### Runtime Code

```python
# capabilities/system-health/runtime/checks.py

from runtime.capability import check, Signal, triggers

STUCK_THRESHOLD = 300   # 5 minutes
DEAD_THRESHOLD = 600    # 10 minutes

@check(
    id="stuck_agent_detection",
    triggers=[triggers.cron.every(60)],
    on_problem="AGENT_STUCK",
    task="TASK_investigate_stuck_agent",
)
def stuck_agent_detection(ctx) -> dict:
    """H1: Detect agents with no heartbeat for >5 minutes."""
    # Queries AgentRegistry for agents with stale heartbeats
    # Returns DEGRADED for stuck (5-10 min), CRITICAL for dead (>10 min)
    # Dead agents trigger orphan task release downstream

@check(
    id="orphan_task_detection",
    triggers=[triggers.cron.every(60)],
    on_problem="TASK_ORPHAN",
    task="TASK_release_orphan_task",
)
def orphan_task_detection(ctx) -> dict:
    """H2: Detect tasks claimed by dead agents."""
    # Cross-references Throttler active slots with dead agents
    # Auto-releases orphan tasks via throttler.on_abandon()
    # Returns DEGRADED with auto_fixed=True

@check(
    id="health_check_failure",
    triggers=[triggers.stream.on_error(".mind/logs/health.log")],
    on_problem="HEALTH_CHECK_FAILED",
    task="TASK_investigate_health_failure",
)
def health_check_failure(ctx) -> dict:
    """H3: Detect failed health check execution."""
    # Triggered reactively when any check.py crashes or times out
    # Error details come from ctx.trigger_source

@check(
    id="agent_queue_health",
    triggers=[triggers.cron.every(5)],
    on_problem="QUEUE_UNHEALTHY",
    task="TASK_investigate_queue",
)
def agent_queue_health(ctx) -> dict:
    """H4: Monitor task queue health."""
    # Checks pending/max_pending ratio from Throttler stats
    # DEGRADED: queue >80% full + no active agents
    # CRITICAL: queue >80% full + agents stuck
```

### Internal Dependencies

| Module | Import Path | Used By |
|--------|-------------|---------|
| AgentRegistry | `runtime.capability.agents.get_registry` | H1, H2, H4 |
| AgentStatus | `runtime.capability.agents.AgentStatus` | H1, H2, H4 |
| Throttler | `runtime.capability.throttler.get_throttler` | H2, H4 |

### Task Templates

| Task | Purpose | Problem | Auto-Fixed? |
|------|---------|---------|-------------|
| TASK_investigate_stuck_agent | Investigate stale heartbeat | AGENT_STUCK | No |
| TASK_release_orphan_task | Release tasks from dead agents | TASK_ORPHAN | Yes |
| TASK_investigate_health_failure | Debug crashed check.py | HEALTH_CHECK_FAILED | No |

---

## INTEGRATION POINTS

### Triggers

| Trigger | Interval | Calls |
|---------|----------|-------|
| cron:60s | Every 60 seconds | H1 (stuck_agent), H2 (orphan_task) |
| cron:5m | Every 5 minutes | H4 (queue_health) |
| stream:on_error | Reactive (on crash) | H3 (health_check_failure) |

### Graph Nodes Created

| Node | Type | When |
|------|------|------|
| task_run | narrative:task_run | on_signal degraded/critical |

### Links Created

| From | To | Nature |
|------|-----|--------|
| task_run | TASK_* | serves |
| task_run | agent | concerns |
| task_run | problem | resolves |
| agent | task_run | claims |

---

## EXECUTION MODES

### Automated (Self-Healing)

- **TASK_ORPHAN**: Fully automated — `orphan_task_detection` calls `throttler.on_abandon()` inline, releases tasks back to pending. No agent needed.
- **AGENT_DEAD**: Partial — agent marked dead automatically at 10-min threshold, orphan tasks released. But root cause requires investigation.

### Agent Required

- **AGENT_STUCK**: Agent investigates whether the stuck agent is on a slow operation or actually dead (5-10 min ambiguity window).
- **HEALTH_CHECK_FAILED**: Agent must read logs, find the bug in the failing check.py, and fix it.
- **QUEUE_UNHEALTHY**: Agent determines whether to spawn more agents or investigate why existing agents are stuck.

---

## DATA FLOW

```
                    ┌─────────────────┐
                    │  cron (60s/5m)  │
                    │  stream:error   │
                    └────────┬────────┘
                             │ trigger
                             ▼
                    ┌─────────────────┐
                    │   checks.py     │
                    │  H1/H2/H3/H4   │
                    └────────┬────────┘
                             │ Signal
               ┌─────────────┼─────────────┐
               ▼             ▼             ▼
          ┌─────────┐  ┌──────────┐  ┌──────────┐
          │ healthy │  │ degraded │  │ critical │
          │ (noop)  │  │          │  │          │
          └─────────┘  └────┬─────┘  └────┬─────┘
                            │              │
                            ▼              ▼
                    ┌─────────────────┐
                    │   task_run      │
                    │  (+ auto-fix    │
                    │   if applicable)│
                    └─────────────────┘
```

### Signal Payloads

**H1 — stuck_agent_detection:**
- CRITICAL: `{agent_id, dead_count, dead_agents[], stuck_count}`
- DEGRADED: `{agent_id, stuck_count, stuck_agents[]}`

**H2 — orphan_task_detection:**
- DEGRADED: `{task_id, orphan_count, released_tasks[], auto_fixed: true}`

**H3 — health_check_failure:**
- DEGRADED: `{error, capability}`

**H4 — agent_queue_health:**
- CRITICAL: `{pending, max_pending, active_agents, stuck_agents}`
- DEGRADED: `{pending, max_pending, no_workers: true}`

---

## THRESHOLDS

| Constant | Value | Location | Purpose |
|----------|-------|----------|---------|
| STUCK_THRESHOLD | 300s (5 min) | checks.py:20 | Agent considered stuck |
| DEAD_THRESHOLD | 600s (10 min) | checks.py:21 | Agent considered dead |
| HEARTBEAT_INTERVAL | 60s | @check trigger | Expected heartbeat cadence |
| QUEUE_WARNING | 80% | checks.py:185 | Queue fullness threshold |
