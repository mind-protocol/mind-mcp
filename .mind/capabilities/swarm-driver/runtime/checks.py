"""
Health Checks: swarm-driver

Decorator-based health checks for the swarm driver daemon.
Monitors driver liveness, log processing backlog, and task singleton.

DOCS: capabilities/swarm-driver/HEALTH.md
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from runtime.capability import check, Signal, triggers


# =============================================================================
# CONSTANTS
# =============================================================================

DRIVER_STALE_SECONDS = 300       # 5 minutes — driver should run every 2 min
LOG_BACKLOG_WARN_BYTES = 10240   # 10 KB
LOG_BACKLOG_CRIT_BYTES = 102400  # 100 KB


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_driver_state(root: Path) -> dict | None:
    """Load driver_state.json if it exists."""
    state_file = root / ".mind" / "swarm" / "driver_state.json"
    if not state_file.exists():
        return None
    try:
        return json.loads(state_file.read_text())
    except Exception:
        return None


def get_log_backlog(root: Path, positions: dict) -> list[dict]:
    """Calculate unprocessed bytes per log file."""
    logs_dir = root / ".mind" / "swarm" / "logs"
    if not logs_dir.exists():
        return []

    backlogs = []
    for log_file in logs_dir.glob("*.log"):
        name = log_file.name
        try:
            size = log_file.stat().st_size
            pos = positions.get(name, 0)
            gap = size - pos
            if gap > 0:
                backlogs.append({
                    "file": name,
                    "size": size,
                    "position": pos,
                    "gap_bytes": gap,
                })
        except Exception:
            continue

    return backlogs


# =============================================================================
# HEALTH CHECKS
# =============================================================================

@check(
    id="driver_active",
    triggers=[
        triggers.cron.every(minutes=2),
        triggers.init.startup(),
    ],
    on_problem="DRIVER_STALE",
    task=None,  # Auto-restart, no task needed
)
def driver_active(ctx) -> dict:
    """
    H1: Check if the swarm driver is running.

    Reads driver_state.json and verifies last_run is within 5 minutes.
    Returns CRITICAL if driver not running or stale.
    Returns HEALTHY if driver ran recently.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    state = load_driver_state(root)

    if state is None:
        return Signal.critical(
            reason="driver_state.json not found — driver never started",
        )

    last_run = state.get("last_run")
    if not last_run:
        return Signal.critical(
            reason="No last_run timestamp in driver state",
        )

    try:
        last_dt = datetime.fromisoformat(last_run)
        elapsed = (datetime.now() - last_dt).total_seconds()

        if elapsed > DRIVER_STALE_SECONDS:
            return Signal.critical(
                reason="Driver stale",
                last_run=last_run,
                elapsed_seconds=int(elapsed),
                threshold=DRIVER_STALE_SECONDS,
            )
    except ValueError:
        return Signal.critical(
            reason=f"Cannot parse last_run: {last_run}",
        )

    return Signal.healthy(
        last_run=last_run,
        elapsed_seconds=int(elapsed),
    )


@check(
    id="log_processing",
    triggers=[
        triggers.cron.every(minutes=5),
        triggers.file.on_modify(".mind/swarm/logs/*.log"),
    ],
    on_problem="LOG_BACKLOG",
    task=None,  # Advisory — driver should catch up on next cycle
)
def log_processing(ctx) -> dict:
    """
    H2: Check if driver is keeping up with log ingestion.

    Compares file sizes to tracked positions.
    Returns CRITICAL if gap > 100KB.
    Returns DEGRADED if gap > 10KB.
    Returns HEALTHY if processing keeps up.
    """
    root = Path(ctx.project_root) if ctx.project_root else Path(".")
    state = load_driver_state(root)

    if state is None:
        # No state file means driver hasn't started; H1 catches that
        return Signal.healthy(message="No driver state — deferred to H1")

    positions = state.get("positions", {})
    backlogs = get_log_backlog(root, positions)

    if not backlogs:
        return Signal.healthy()

    total_gap = sum(b["gap_bytes"] for b in backlogs)

    if total_gap > LOG_BACKLOG_CRIT_BYTES:
        return Signal.critical(
            backlogs=backlogs,
            total_gap_bytes=total_gap,
        )

    if total_gap > LOG_BACKLOG_WARN_BYTES:
        return Signal.degraded(
            backlogs=backlogs,
            total_gap_bytes=total_gap,
        )

    return Signal.healthy(
        total_gap_bytes=total_gap,
    )


@check(
    id="task_singleton",
    triggers=[
        triggers.cron.every(minutes=5),
    ],
    on_problem="SINGLETON_VIOLATED",
    task=None,  # Auto-cancel duplicates
)
def task_singleton(ctx) -> dict:
    """
    H3: Verify driver maintains singleton task pattern.

    Queries graph for active driver tasks — should be 0 or 1.
    Returns CRITICAL if > 1 active driver task.
    Returns HEALTHY if singleton holds.
    """
    try:
        results = ctx.query_nodes(
            node_type="narrative",
            filters={
                "type": "task_run",
                "source": "swarm-driver",
                "status": ["pending", "claimed", "running"],
            },
        )
    except Exception:
        # If graph unavailable, check via state file
        root = Path(ctx.project_root) if ctx.project_root else Path(".")
        state = load_driver_state(root)
        if state and state.get("last_task_id"):
            return Signal.healthy(
                message="Graph unavailable — singleton assumed from state file",
                last_task_id=state["last_task_id"],
            )
        return Signal.healthy(message="Graph unavailable, no active tasks in state")

    active_count = len(results) if results else 0

    if active_count > 1:
        task_ids = [r.get("id", "unknown") for r in results]
        return Signal.critical(
            active_count=active_count,
            active_tasks=task_ids,
            message="Singleton violated — multiple driver tasks active",
        )

    return Signal.healthy(
        active_count=active_count,
    )


# =============================================================================
# REGISTRY
# =============================================================================

CHECKS = [
    driver_active,
    log_processing,
    task_singleton,
]
