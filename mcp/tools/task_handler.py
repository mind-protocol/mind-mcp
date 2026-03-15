"""
[ACT] Task — Manage tasks: list, claim, complete, fail.

Usage via MCP:
    task(action="list")
    task(action="list", module="physics", limit=10)
    task(action="claim", task_id="task_fix_sync")
    task(action="complete", task_id="task_fix_sync")
    task(action="fail", task_id="task_fix_sync", reason="Blocked by missing schema")
"""

import logging
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.task")


TOOL_SCHEMA = {
    "name": "task",
    "description": (
        "[ACT] Manage tasks — list pending work, claim a task, mark it complete or failed. "
        "Use action='list' to see available tasks, 'claim' to take one, "
        "'complete' when done, 'fail' with a reason if blocked."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "claim", "complete", "fail"],
                "description": "What to do: list tasks, claim one, mark complete, or mark failed.",
            },
            "task_id": {
                "type": "string",
                "description": "Task node ID (required for claim/complete/fail).",
            },
            "actor_id": {
                "type": "string",
                "description": "Actor performing the action. Auto-detected if omitted.",
            },
            "reason": {
                "type": "string",
                "description": "Why the task failed (required for action='fail').",
            },
            "module": {
                "type": "string",
                "description": "Filter tasks by module name (for action='list').",
            },
            "objective": {
                "type": "string",
                "description": "Filter tasks by objective type (for action='list').",
            },
            "limit": {
                "type": "integer",
                "description": "Max tasks to return (default: 20, for action='list').",
            },
        },
        "required": ["action"],
    },
}


def handle_task(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Dispatch task actions."""
    action = args.get("action")

    if action == "list":
        return _task_list(args, ctx)
    elif action == "claim":
        return _task_claim(args, ctx)
    elif action == "complete":
        return _task_complete(args, ctx)
    elif action == "fail":
        return _task_fail(args, ctx)
    else:
        return _err(f"Unknown action '{action}'. Use: list, claim, complete, fail.")


def _normalize_actor(actor_id, ctx):
    """Normalize actor ID using the runtime helper."""
    from runtime.identity import resolve_actor_id as normalize_agent_id
    return normalize_agent_id(actor_id, graph_ops=ctx.graph_ops)


def _task_list(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """List available tasks with linked problems."""
    module_filter = args.get("module")
    objective_filter = args.get("objective")
    limit = args.get("limit", 20)

    if not ctx.graph_queries:
        return _err("No graph connection")

    try:
        cypher = """
        MATCH (t:Narrative)
        WHERE t.type = 'task' AND (t.status IS NULL OR t.status <> 'completed')
        OPTIONAL MATCH (t)-[r:relates]->(o:Narrative {type: 'objective'})
        RETURN t.id, t.name, t.task_type, t.module, t.skill, t.status,
               collect(DISTINCT o.name) as objectives, t.created_at_s
        ORDER BY t.created_at_s DESC
        LIMIT $limit
        """
        result = ctx.graph_queries._query(cypher, {"limit": limit * 2})

        if not result:
            return _ok("No tasks found. Run health checks first to create tasks.")

        lines = ["Available Tasks:\n"]
        count = 0

        for row in result:
            task_id, name, task_type, module, skill, status, objectives, _created = row

            if module_filter and module != module_filter:
                continue
            if objective_filter and objective_filter not in str(objectives):
                continue

            count += 1
            if count > limit:
                break

            status_icon = "⏳" if status == "pending" else "🔄" if status == "in_progress" else "⏸️"
            lines.append(f"{status_icon} {name}")
            lines.append(f"   ID: {task_id}")
            lines.append(f"   Module: {module} | Skill: {skill}")
            if objectives:
                lines.append(f"   Serves: {', '.join(objectives[:2])}")
            lines.append("")

        lines.append(f"\nTotal: {count} task(s)")
        lines.append("\nTo work on a task:")
        lines.append("  task(action='claim', task_id='<task_id>')")

        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Task list failed")
        return _err(f"Listing tasks: {e}")


def _task_claim(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Atomically claim a pending task."""
    task_id = args.get("task_id")
    if not task_id:
        return _err("'task_id' is required for action='claim'.")

    actor_id = _normalize_actor(args.get("actor_id"), ctx)

    if not ctx.graph_ops:
        return _err("No graph connection")

    try:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        result = ctx.graph_ops._query(
            "MATCH (n {id: $id}) WHERE n.status = 'pending' "
            "SET n.status = 'claimed', n.claimed_by = $actor, n.claimed_at = $ts "
            "RETURN n.id",
            {"id": task_id, "actor": actor_id, "ts": timestamp}
        )
        if not result or not result[0]:
            return _err("Task not found or already claimed.")

        ctx.graph_ops._query(
            "MATCH (t {id: $task_id}) MATCH (a {id: $actor_id}) "
            "MERGE (t)-[:LINK {verb: 'claimed_by'}]->(a)",
            {"task_id": task_id, "actor_id": actor_id}
        )

        return _ok(f"Task {task_id} claimed by {actor_id}")

    except Exception as e:
        logger.exception("Task claim failed")
        return _err(f"Claiming task: {e}")


def _task_complete(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Mark task as completed."""
    task_id = args.get("task_id")
    if not task_id:
        return _err("'task_id' is required for action='complete'.")

    actor_id = _normalize_actor(args.get("actor_id"), ctx)

    if not ctx.graph_ops:
        return _err("No graph connection")

    try:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        result = ctx.graph_ops._query(
            "MATCH (n {id: $id}) WHERE n.status IN ['claimed', 'running'] "
            "SET n.status = 'completed', n.completed_at = $ts, n.completed_by = $actor "
            "RETURN n.id",
            {"id": task_id, "ts": timestamp, "actor": actor_id}
        )
        if not result or not result[0]:
            return _err("Task not found or not active.")

        from runtime.capability_integration import get_throttler
        throttler = get_throttler()
        if throttler:
            throttler.on_complete(task_id)

        return _ok(f"Task {task_id} completed by {actor_id}")

    except Exception as e:
        logger.exception("Task complete failed")
        return _err(f"Completing task: {e}")


def _task_fail(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Mark task as failed."""
    task_id = args.get("task_id")
    reason = args.get("reason", "Unknown reason")
    if not task_id:
        return _err("'task_id' is required for action='fail'.")

    actor_id = _normalize_actor(args.get("actor_id"), ctx)

    if not ctx.graph_ops:
        return _err("No graph connection")

    try:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        result = ctx.graph_ops._query(
            "MATCH (n {id: $id}) WHERE n.status IN ['pending', 'claimed', 'running'] "
            "SET n.status = 'failed', n.failed_at = $ts, n.failure_reason = $reason, n.failed_by = $actor "
            "RETURN n.id",
            {"id": task_id, "ts": timestamp, "reason": reason, "actor": actor_id}
        )
        if not result or not result[0]:
            return _err("Task not found or already completed.")

        from runtime.capability_integration import get_throttler
        throttler = get_throttler()
        if throttler:
            throttler.on_abandon(task_id)

        return _ok(f"Task {task_id} failed by {actor_id}: {reason}")

    except Exception as e:
        logger.exception("Task fail failed")
        return _err(f"Failing task: {e}")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
