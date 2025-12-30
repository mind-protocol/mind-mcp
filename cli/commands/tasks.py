"""mind tasks - Task listing and management CLI commands.

DOCS: docs/cli/commands/IMPLEMENTATION_Tasks_Command.md

Provides:
- mind tasks list: Show pending, running, stuck, and failed tasks
- mind tasks list --module X: Filter by module
- mind tasks list --capability Y: Filter by capability
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

# ANSI colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"


@dataclass
class TaskInfo:
    """Information about a task."""
    task_id: str
    name: str
    status: str  # pending, running, stuck, failed, completed
    capability: Optional[str] = None
    module: Optional[str] = None
    agent: Optional[str] = None
    created: Optional[datetime] = None
    started: Optional[datetime] = None
    task_type: Optional[str] = None
    path: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent


def _status_color(status: str) -> str:
    """Get color for task status."""
    return {
        "pending": C.YELLOW,
        "running": C.BRIGHT_CYAN,
        "stuck": C.BRIGHT_RED,
        "failed": C.RED,
        "completed": C.BRIGHT_GREEN,
    }.get(status.lower(), C.WHITE)


def _priority_indicator(priority: str) -> str:
    """Get indicator for priority."""
    return {
        "urgent": f"{C.BRIGHT_RED}!!!{C.RESET}",
        "high": f"{C.YELLOW}!! {C.RESET}",
        "normal": f"{C.DIM}   {C.RESET}",
        "low": f"{C.DIM}   {C.RESET}",
    }.get(priority.lower(), "   ")


def _get_tasks_from_graph(
    target_dir: Path,
    module: Optional[str] = None,
    capability: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[TaskInfo]:
    """Get tasks from the graph."""
    tasks = []

    try:
        from runtime.physics.graph.graph_ops import GraphOps

        graph_name = target_dir.name
        graph = GraphOps(graph_name=graph_name)

        # Build query for task_run nodes
        where_clauses = ["t.type = 'task_run' OR t.type = 'task'"]

        if status_filter:
            where_clauses.append(f"t.status = '{status_filter}'")

        if module:
            where_clauses.append(f"(t.module = '{module}' OR t.path CONTAINS '{module}')")

        if capability:
            where_clauses.append(f"t.capability = '{capability}'")

        where = " AND ".join(where_clauses)

        result = graph.query(f"""
            MATCH (t:Narrative)
            WHERE {where}
            OPTIONAL MATCH (t)-[:LINK]->(agent:Actor)
            RETURN t.id, t.name, t.status, t.capability, t.module,
                   t.task_type, t.path, t.priority, agent.name, t.created
            ORDER BY
                CASE t.status
                    WHEN 'stuck' THEN 0
                    WHEN 'failed' THEN 1
                    WHEN 'running' THEN 2
                    WHEN 'pending' THEN 3
                    ELSE 4
                END,
                CASE t.priority
                    WHEN 'urgent' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    ELSE 3
                END
            LIMIT 100
        """)

        for row in result:
            (task_id, name, status, cap, mod, task_type,
             path, priority, agent_name, created) = row

            # Parse created datetime if present
            created_dt = None
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                except Exception:
                    pass

            tasks.append(TaskInfo(
                task_id=task_id or "",
                name=name or task_id or "unknown",
                status=status or "pending",
                capability=cap,
                module=mod,
                agent=agent_name,
                created=created_dt,
                task_type=task_type,
                path=path,
                priority=priority or "normal",
            ))

    except Exception as e:
        # If graph not available, return empty list
        pass

    return tasks


def _get_tasks_from_throttler() -> List[TaskInfo]:
    """Get tasks from the capability throttler."""
    tasks = []

    try:
        from runtime.capability_integration import get_throttler, CAPABILITY_RUNTIME_AVAILABLE
        if not CAPABILITY_RUNTIME_AVAILABLE:
            return tasks

        throttler = get_throttler()
        if not throttler:
            return tasks

        # Get pending tasks
        for task_id, task_data in throttler.pending_tasks.items():
            tasks.append(TaskInfo(
                task_id=task_id,
                name=task_data.get("name", task_id),
                status="pending",
                capability=task_data.get("capability"),
                priority=task_data.get("priority", "normal"),
            ))

        # Get active tasks
        for task_id, task_data in throttler.active_tasks.items():
            tasks.append(TaskInfo(
                task_id=task_id,
                name=task_data.get("name", task_id),
                status="running",
                capability=task_data.get("capability"),
                agent=task_data.get("agent"),
                started=task_data.get("started"),
                priority=task_data.get("priority", "normal"),
            ))

    except Exception:
        pass

    return tasks


def _format_age(created: Optional[datetime]) -> str:
    """Format task age."""
    if not created:
        return "-"

    delta = datetime.now() - created
    if delta.days > 0:
        return f"{delta.days}d"
    elif delta.seconds >= 3600:
        return f"{delta.seconds // 3600}h"
    elif delta.seconds >= 60:
        return f"{delta.seconds // 60}m"
    else:
        return f"{delta.seconds}s"


def list_tasks(
    target_dir: Path,
    module: Optional[str] = None,
    capability: Optional[str] = None,
    status_filter: Optional[str] = None,
    format_output: str = "text",
    limit: int = 50,
) -> int:
    """List tasks with optional filters.

    Args:
        target_dir: Project directory
        module: Filter by module name
        capability: Filter by capability name
        status_filter: Filter by status (pending, running, stuck, failed)
        format_output: Output format (text or json)
        limit: Maximum number of tasks to show

    Returns:
        Exit code
    """
    # Collect tasks from all sources
    graph_tasks = _get_tasks_from_graph(target_dir, module, capability, status_filter)
    throttler_tasks = _get_tasks_from_throttler()

    # Merge: throttler tasks for running state, graph for rest
    tasks_by_id = {t.task_id: t for t in graph_tasks}
    for tt in throttler_tasks:
        if tt.task_id in tasks_by_id:
            # Update with runtime state
            existing = tasks_by_id[tt.task_id]
            existing.status = tt.status
            existing.agent = tt.agent or existing.agent
            existing.started = tt.started or existing.started
        else:
            tasks_by_id[tt.task_id] = tt

    tasks = list(tasks_by_id.values())[:limit]

    # Apply status filter if specified
    if status_filter:
        tasks = [t for t in tasks if t.status.lower() == status_filter.lower()]

    if format_output == "json":
        output = []
        for t in tasks:
            output.append({
                "task_id": t.task_id,
                "name": t.name,
                "status": t.status,
                "capability": t.capability,
                "module": t.module,
                "agent": t.agent,
                "task_type": t.task_type,
                "path": t.path,
                "priority": t.priority,
            })
        print(json.dumps(output, indent=2))
        return 0

    # Text output
    print()
    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print(f"{C.BOLD}  TASKS{C.RESET}")

    # Show active filters
    filters = []
    if module:
        filters.append(f"module={module}")
    if capability:
        filters.append(f"capability={capability}")
    if status_filter:
        filters.append(f"status={status_filter}")
    if filters:
        print(f"{C.DIM}  Filters: {', '.join(filters)}{C.RESET}")

    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print()

    if not tasks:
        print(f"  {C.DIM}No tasks found.{C.RESET}")
        print()
        return 0

    # Summary
    by_status: Dict[str, int] = {}
    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1

    summary_parts = []
    for status in ["stuck", "failed", "running", "pending", "completed"]:
        if status in by_status:
            color = _status_color(status)
            summary_parts.append(f"{color}{by_status[status]} {status}{C.RESET}")

    print(f"  {C.BOLD}Summary:{C.RESET} {', '.join(summary_parts)}")
    print()

    # Group by status for display
    status_order = ["stuck", "failed", "running", "pending"]

    for status in status_order:
        status_tasks = [t for t in tasks if t.status.lower() == status]
        if not status_tasks:
            continue

        status_c = _status_color(status)
        print(f"  {C.BOLD}{status_c}{status.upper()}{C.RESET} ({len(status_tasks)})")
        print(f"  {C.DIM}{'─' * 74}{C.RESET}")

        for t in status_tasks[:20]:
            prio = _priority_indicator(t.priority)

            # Truncate name/path
            display_name = t.name
            if t.path and len(t.path) < 50:
                display_name = t.path
            if len(display_name) > 45:
                display_name = display_name[:42] + "..."

            # Info parts
            info_parts = []
            if t.capability:
                info_parts.append(f"{C.CYAN}{t.capability}{C.RESET}")
            if t.module:
                info_parts.append(f"{C.BLUE}{t.module}{C.RESET}")
            if t.agent:
                info_parts.append(f"@{t.agent}")

            info = " | ".join(info_parts) if info_parts else ""

            age = _format_age(t.created)

            print(f"    {prio} {display_name:<45} {age:>5} {info}")

        if len(status_tasks) > 20:
            print(f"    {C.DIM}... and {len(status_tasks) - 20} more{C.RESET}")

        print()

    # Footer
    print(f"  {C.DIM}{'─' * 74}{C.RESET}")
    print(f"  {C.DIM}Use 'mind work --task <id>' to work on a specific task{C.RESET}")
    print()

    return 0


def tasks_command(
    target_dir: Path,
    action: str = "list",
    module: Optional[str] = None,
    capability: Optional[str] = None,
    status_filter: Optional[str] = None,
    format_output: str = "text",
    limit: int = 50,
) -> int:
    """Main entry point for tasks command.

    Args:
        target_dir: Project directory
        action: list (only action currently)
        module: Filter by module
        capability: Filter by capability
        status_filter: Filter by status
        format_output: Output format
        limit: Maximum tasks to show

    Returns:
        Exit code
    """
    if action == "list":
        return list_tasks(
            target_dir,
            module=module,
            capability=capability,
            status_filter=status_filter,
            format_output=format_output,
            limit=limit,
        )
    else:
        print(f"{C.RED}Unknown action: {action}{C.RESET}")
        return 1
