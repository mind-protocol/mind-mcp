# Swarm Driver — Implementation

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
VALIDATION:      ./VALIDATION.md
THIS:            IMPLEMENTATION.md (you are here)
HEALTH:          ./HEALTH.md
SYNC:            ./SYNC.md
```

---

## PURPOSE

Where swarm-driver code lives and how it's structured.

---

## FILE STRUCTURE

```
capabilities/swarm-driver/                    # Self-contained capability
├── OBJECTIVES.md
├── PATTERNS.md
├── BEHAVIORS.md
├── ALGORITHM.md
├── VALIDATION.md
├── IMPLEMENTATION.md                         # You are here
├── HEALTH.md
├── SYNC.md
├── tasks/
│   ├── TASK_investigate_error.md            # Dispatch to Fixer
│   ├── TASK_unblock.md                      # Dispatch to Weaver
│   ├── TASK_update_sync.md                  # Dispatch to Witness
│   └── TASK_scan_for_work.md               # Dispatch to Scout
├── skills/
│   └── SKILL_swarm_driver.md               # Agent skill for running driver
├── procedures/
│   └── PROCEDURE_swarm_driver.yaml         # Step-by-step driver procedure
└── runtime/                                 # MCP-executable code
    ├── __init__.py                          # Exports CHECKS list + run_cycle
    ├── driver.py                            # Main loop (A1-A5 from ALGORITHM)
    ├── signals.py                           # Signal dataclass + detection logic
    └── checks.py                            # @check decorated health functions
```

### Runtime State

```
.mind/swarm/
├── driver_state.json                        # Positions, last_task_id, last_run
└── logs/
    ├── agent_*.log                          # Per-agent activity logs
    ├── tasks.log                            # Task lifecycle events
    ├── errors.log                           # Failures and exceptions
    └── completions.log                      # Finished work
```

---

## KEY COMPONENTS

### Signal Dataclass

```python
# capabilities/swarm-driver/runtime/signals.py

from dataclasses import dataclass

@dataclass
class Signal:
    type: str           # ERROR_DETECTED | AGENT_STUCK | SYNC_UPDATE_NEEDED | NO_TASKS_AVAILABLE
    target: str         # What's affected (module, agent, file)
    priority: int       # 10=error, 8=stuck, 7=idle, 5=sync
    context: list[str]  # Relevant log lines for task context
```

### Main Driver

```python
# capabilities/swarm-driver/runtime/driver.py

import json
from pathlib import Path
from datetime import datetime
from .signals import Signal

LOG_DIR = Path(".mind/swarm/logs")
STATE_FILE = Path(".mind/swarm/driver_state.json")
SYNC_FILE = Path(".mind/state/SYNC_Project_State.md")

SIGNAL_TO_TEMPLATE = {
    "ERROR_DETECTED":     "TASK_investigate_error",
    "AGENT_STUCK":        "TASK_unblock",
    "SYNC_UPDATE_NEEDED": "TASK_update_sync",
    "NO_TASKS_AVAILABLE": "TASK_scan_for_work",
}

SIGNAL_TO_AGENT = {
    "ERROR_DETECTED":     "AGENT_Fixer",
    "AGENT_STUCK":        "AGENT_Weaver",
    "SYNC_UPDATE_NEEDED": "AGENT_Witness",
    "NO_TASKS_AVAILABLE": "AGENT_Scout",
}


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"positions": {}, "last_task_id": None, "last_run": None}


def save_state(state: dict):
    """Atomic write: temp file + rename."""
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.rename(STATE_FILE)


def collect_new_lines(positions: dict) -> dict:
    new_lines = {}
    for log_file in LOG_DIR.glob("*.log"):
        name = log_file.name
        pos = positions.get(name, 0)
        size = log_file.stat().st_size
        if size <= pos:
            continue
        with open(log_file) as f:
            f.seek(pos)
            lines = f.readlines()
            new_lines[name] = lines
            positions[name] = f.tell()
    return new_lines


def analyze_logs(new_lines: dict) -> list[Signal]:
    signals = []
    for source, lines in new_lines.items():
        text = "".join(lines)

        if "ERROR" in text or "FAILED" in text:
            signals.append(Signal(
                type="ERROR_DETECTED",
                target=source,
                priority=10,
                context=[l for l in lines if "ERROR" in l or "FAILED" in l][:10],
            ))

        if "retrying" in text.lower() or "timeout" in text.lower():
            signals.append(Signal(
                type="AGENT_STUCK",
                target=source.replace("agent_", "").replace(".log", ""),
                priority=8,
                context=lines[-5:],
            ))

        if "completed" in text.lower() or "done" in text.lower():
            signals.append(Signal(
                type="SYNC_UPDATE_NEEDED",
                target="SYNC_Project_State",
                priority=5,
                context=[l for l in lines if "completed" in l.lower() or "done" in l.lower()][:5],
            ))

        if source == "tasks.log" and "pending" in text:
            if text.count("pending") == 0:
                signals.append(Signal(
                    type="NO_TASKS_AVAILABLE",
                    target="task_scan",
                    priority=7,
                    context=["No pending tasks, agents may idle"],
                ))

    return sorted(signals, key=lambda s: -s.priority)


def run_cycle(graph) -> str | None:
    """
    One driver cycle. Called every 2 minutes.
    Returns task_id if created, None otherwise.
    """
    state = load_state()

    # 1. Collect new lines
    new_lines = collect_new_lines(state["positions"])
    if not new_lines:
        return None

    # 2. Analyze
    signals = analyze_logs(new_lines)
    if not signals:
        save_state(state)
        return None

    # 3. Pick highest priority
    best = signals[0]  # Already sorted descending

    # 4. Singleton check
    last_id = state.get("last_task_id")
    if last_id and graph.is_task_active(last_id):
        return None

    # 5. Create task
    template = SIGNAL_TO_TEMPLATE.get(best.type, "TASK_investigate")
    agent = SIGNAL_TO_AGENT.get(best.type, "AGENT_Fixer")
    task_id = f"TASK_RUN_{best.type}_{hash(best.target) & 0xFFFFFFFF:08x}"

    graph.create_task_run(
        id=task_id,
        template=template,
        target=best.target,
        agent=agent,
        priority=best.priority,
        context=best.context,
    )

    # 6. Update SYNC
    entry = (
        f"\n## Driver Action: {datetime.now().isoformat()}\n\n"
        f"- **Signal:** {best.type}\n"
        f"- **Target:** {best.target}\n"
        f"- **Task:** {task_id}\n"
        f"- **Priority:** {best.priority}\n"
    )
    with open(SYNC_FILE, "a") as f:
        f.write(entry)

    # 7. Save state
    state["last_task_id"] = task_id
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    return task_id
```

### Health Checks

```python
# capabilities/swarm-driver/runtime/checks.py

from mind.capability import check, Signal, triggers

@check(
    id="driver_running",
    triggers=[triggers.cron.every("5m")],
    on_problem="DRIVER_STALE",
    task="TASK_restart_driver",
)
def driver_running(ctx) -> dict:
    """H1: Is the driver running?"""
    state = load_driver_state()
    if not state or not state.get("last_run"):
        return Signal.critical(reason="No driver state found")

    age_minutes = minutes_since(state["last_run"])
    if age_minutes > 5:
        return Signal.critical(age_minutes=age_minutes)
    return Signal.healthy()


@check(
    id="log_processing",
    triggers=[triggers.cron.every("10m")],
    on_problem="LOG_BACKLOG",
    task="TASK_investigate_error",
)
def log_processing(ctx) -> dict:
    """H2: Is log processing keeping up?"""
    state = load_driver_state()
    total_gap = 0
    for log_file in LOG_DIR.glob("*.log"):
        pos = state["positions"].get(log_file.name, 0)
        gap = log_file.stat().st_size - pos
        total_gap += max(0, gap)

    if total_gap > 100_000:
        return Signal.critical(backlog_bytes=total_gap)
    if total_gap > 10_000:
        return Signal.degraded(backlog_bytes=total_gap)
    return Signal.healthy()


@check(
    id="task_singleton",
    triggers=[triggers.cron.every("5m")],
    on_problem="SINGLETON_VIOLATED",
    task="TASK_cancel_duplicates",
)
def task_singleton(ctx) -> dict:
    """H3: At most one active driver task?"""
    active = ctx.graph.query(
        "MATCH (t:TaskRun) WHERE t.source = 'swarm-driver' "
        "AND t.status IN ['pending', 'claimed', 'in_progress'] "
        "RETURN count(t) AS c"
    )
    count = active[0]["c"]
    if count > 1:
        return Signal.critical(active_count=count)
    return Signal.healthy()
```

---

## INTEGRATION POINTS

### Triggers

| Trigger | When | Calls |
|---------|------|-------|
| cron:2m | Every 2 minutes | run_cycle() — main driver loop |
| cron:5m | Every 5 minutes | H1: driver_running, H3: task_singleton |
| cron:10m | Every 10 minutes | H2: log_processing |
| init.startup | Server boot | Start driver cron |
| file.swarm_logs | Log file change | Optional fast-path run_cycle() |

### Graph Nodes Created

| Node | Type | When |
|------|------|------|
| task_run | narrative:task_run | Signal detected, singleton clear |
| driver_action | narrative:moment | SYNC update appended |

### Links Created

| From | To | Nature |
|------|----|--------|
| task_run | TASK_* template | serves |
| task_run | signal target | concerns |
| task_run | assigned agent | assigned_to |

### Dependencies

| Component | Role |
|-----------|------|
| `.mind/swarm/logs/` | Input — log files written by agents and orchestrator |
| `.mind/swarm/driver_state.json` | State — positions and last task tracking |
| `.mind/state/SYNC_Project_State.md` | Output — driver actions appended here |
| Graph (FalkorDB) | Output — task_run nodes created here |
| Cron scheduler | Trigger — calls run_cycle() every 2 minutes |

---

## DATA FLOWS

```
                    ┌─────────────────┐
                    │  Agent Logs     │
                    │  errors.log     │
                    │  tasks.log      │
                    │  completions.log│
                    └────────┬────────┘
                             │ read new lines (position-tracked)
                             ▼
                    ┌─────────────────┐
                    │  analyze_logs() │
                    │  pattern match  │
                    └────────┬────────┘
                             │ signals (sorted by priority)
                             ▼
                    ┌─────────────────┐
                    │  singleton      │
                    │  check          │
                    └────────┬────────┘
                             │ if clear
                             ▼
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐          ┌─────────────────┐
    │  create_task()  │          │  update_sync()  │
    │  → graph node   │          │  → SYNC file    │
    └─────────────────┘          └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │  save_state()   │
    │  → atomic write │
    └─────────────────┘
```
