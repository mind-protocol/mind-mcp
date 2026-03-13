"""
[ACT] Agent — Manage work agents: list, run, status.

Usage via MCP:
    agent(action="list")
    agent(action="run", task_id="task_fix_sync")
    agent(action="run", task_type="STALE_SYNC", path="docs/physics/")
    agent(action="status", actor_id="agent_witness")
    agent(action="status", actor_id="agent_witness", set_status="ready")
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.agent")


TOOL_SCHEMA = {
    "name": "agent",
    "description": (
        "[ACT] Manage work agents — list available agents, run one on a task, or check/set status. "
        "Use action='list' to see agents, 'run' to execute one on a task, "
        "'status' to inspect or change an agent's state."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "run", "status"],
                "description": "What to do: list agents, run one, or get/set status.",
            },
            "task_id": {
                "type": "string",
                "description": "Task node ID to work on (for action='run'). If provided, task_type/path are ignored.",
            },
            "task_type": {
                "type": "string",
                "description": "Problem type (for action='run' without task_id).",
            },
            "path": {
                "type": "string",
                "description": "Path of the problem to fix (for action='run' without task_id).",
            },
            "actor_id": {
                "type": "string",
                "description": "Agent ID (e.g., agent_witness). Required for 'status', optional for 'run'.",
            },
            "provider": {
                "type": "string",
                "enum": ["claude", "gemini", "codex"],
                "description": "LLM provider for action='run' (default: claude).",
            },
            "set_status": {
                "type": "string",
                "enum": ["ready", "running"],
                "description": "Set agent status (for action='status').",
            },
        },
        "required": ["action"],
    },
}


def handle_agent(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Dispatch agent actions."""
    action = args.get("action")

    if action == "list":
        return _agent_list(ctx)
    elif action == "run":
        return _agent_run(args, ctx)
    elif action == "status":
        return _agent_status(args, ctx)
    else:
        return _err(f"Unknown action '{action}'. Use: list, run, status.")


def _agent_list(ctx: ServerContext) -> Dict[str, Any]:
    """List all agents with status and session liveness."""
    from runtime.agents.liveness import check_agent_liveness

    agents = ctx.agent_graph.get_all_agents()

    liveness = check_agent_liveness(Path.cwd())
    session_alive = liveness.get("alive", False)
    most_recent_age = liveness.get("most_recent_age")
    active_count = liveness.get("active_sessions", 0)

    lines = ["Work Agents:\n"]

    if session_alive:
        lines.append(f"  Session: ACTIVE ({active_count} sessions, last: {most_recent_age:.1f}s ago)\n")
    else:
        age_str = f"{most_recent_age:.0f}s ago" if most_recent_age else "unknown"
        lines.append(f"  Session: IDLE (last: {age_str})\n")

    for agent in agents:
        status_icon = "🟢" if agent.status == "ready" else "🔴"
        lines.append(f"  {status_icon} {agent.id} ({agent.name})")
        lines.append(f"     Status: {agent.status}")
        lines.append(f"     Energy: {agent.energy:.2f}")
        lines.append("")

    return _ok("\n".join(lines))


def _agent_status(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Get or set agent status."""
    from runtime.agents.liveness import check_agent_liveness

    actor_id = args.get("actor_id")
    set_status = args.get("set_status")

    if not actor_id:
        return _err("'actor_id' is required for action='status'.")

    if set_status:
        if set_status == "running":
            ctx.agent_graph.set_agent_running(actor_id)
        else:
            ctx.agent_graph.set_agent_ready(actor_id)
        return _ok(f"Agent {actor_id} status set to {set_status}")

    agents = {a.id: a for a in ctx.agent_graph.get_all_agents()}
    if actor_id not in agents:
        return _err(f"Agent {actor_id} not found.")

    agent = agents[actor_id]

    liveness = check_agent_liveness(Path.cwd())
    session_alive = liveness.get("alive", False)
    most_recent_age = liveness.get("most_recent_age")

    lines = [
        f"Agent: {agent.id}",
        f"Posture: {agent.name}",
        f"Graph Status: {agent.status}",
        f"Session Alive: {session_alive}",
    ]
    if most_recent_age is not None:
        lines.append(f"Last Activity: {most_recent_age:.1f}s ago")
    lines.extend([
        f"Energy: {agent.energy:.2f}",
        f"Weight: {agent.weight:.2f}",
    ])
    return _ok("\n".join(lines))


def _agent_run(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Run a work agent to fix a problem or work on a task."""
    from runtime.agents import (
        DEFAULT_NAME,
        run_work_agent,
        get_learnings_content,
        build_agent_command,
    )

    task_id = args.get("task_id")
    task_type = args.get("task_type")
    path = args.get("path")
    actor_id = args.get("actor_id")
    provider = args.get("provider", "claude")

    task_content = None
    task_type_resolved = None
    prompt = None

    # If task_id provided, fetch from graph
    if task_id:
        if not ctx.graph_queries:
            return _err("No graph connection for task lookup.")

        try:
            cypher = """
            MATCH (t:Narrative {id: $task_id})
            OPTIONAL MATCH (t)-[:relates]->(o:Narrative {type: 'objective'})
            OPTIONAL MATCH (p:Narrative {type: 'problem'})-[:relates]->(t)
            RETURN t.id, t.name, t.content, t.type, t.module, t.skill, t.task_type,
                   collect(DISTINCT {id: o.id, name: o.name, type: o.objective_type}) as objectives,
                   collect(DISTINCT {id: p.id, type: p.task_type, path: p.path, message: p.message, severity: p.severity}) as problems
            """
            result = ctx.graph_queries._query(cypher, {"task_id": task_id})
            if not result or not result[0]:
                return _err(f"Task '{task_id}' not found in graph.")

            row = result[0]
            task_name = row[1] if len(row) > 1 else task_id
            task_content = row[2] if len(row) > 2 else None
            task_type_resolved = row[3] if len(row) > 3 else "task"
            task_module = row[4] if len(row) > 4 else ""
            task_skill = row[5] if len(row) > 5 else ""
            task_subtype = row[6] if len(row) > 6 else ""
            objectives = row[7] if len(row) > 7 else []
            problems = row[8] if len(row) > 8 else []

            if not task_type_resolved and problems:
                first_problem = problems[0] if isinstance(problems[0], dict) else {}
                task_type_resolved = first_problem.get("type", "TASK")
            elif not task_type_resolved:
                task_type_resolved = task_subtype.upper() if task_subtype else "TASK"

            prompt_lines = [
                f"# Task: {task_name}",
                f"Module: {task_module}",
                f"Skill: {task_skill}",
                "",
            ]
            if objectives:
                prompt_lines.append("## Objectives this serves:")
                for obj in objectives[:3]:
                    if isinstance(obj, dict) and obj.get("name"):
                        prompt_lines.append(f"- {obj.get('name')}")
                prompt_lines.append("")
            if problems:
                prompt_lines.append("## Problems to fix:")
                for prob in problems[:10]:
                    if isinstance(prob, dict) and prob.get("path"):
                        prompt_lines.append(f"- [{prob.get('severity', 'warning')}] {prob.get('type')}: {prob.get('path')}")
                        if prob.get("message"):
                            prompt_lines.append(f"  {prob.get('message')[:200]}")
                prompt_lines.append("")
            if task_content:
                prompt_lines.append("## Task description:")
                prompt_lines.append(task_content)
            prompt_lines.append("\n## Instructions:")
            prompt_lines.append("Fix all the problems listed above. Follow project conventions.")
            prompt = "\n".join(prompt_lines)

        except Exception as e:
            logger.warning(f"Failed to fetch task {task_id}: {e}")
            return _err(f"Fetching task: {e}")

    elif not task_type or not path:
        return _err("Either task_id OR (task_type + path) required for action='run'.")

    # Select agent if not specified
    if not actor_id:
        task_synthesis = f"{task_type_resolved or task_type or 'task'}: {path or 'unknown'}"
        if prompt:
            task_synthesis += f" - {prompt[:100]}"
        actor_id = ctx.agent_graph.select_agent_for_task(task_synthesis)
        if not actor_id:
            actor_id = f"AGENT_{DEFAULT_NAME.capitalize()}"

    # Check availability
    agents = {a.id: a for a in ctx.agent_graph.get_all_agents()}
    if actor_id in agents and agents[actor_id].status == "running":
        return _err(f"{actor_id} is already running. Choose another agent or wait.")

    name = actor_id.replace("ACTOR_", "")
    moments_created: List = []

    # Derive space from path
    space_id = None
    if path:
        path_parts = Path(path).parts[:2]
        if path_parts:
            space_id = f"space_{'_'.join(path_parts)}"
    elif task_id:
        space_id = ctx.agent_graph.get_task_space(task_id)

    if space_id:
        ctx.agent_graph.set_agent_space(actor_id, space_id)
        if task_id:
            ctx.agent_graph.link_task_to_space(task_id, space_id)

    # Upsert problem/task narratives
    problem_ids = None
    if task_type and path:
        problem_narrative_id = ctx.agent_graph.upsert_problem_narrative(
            task_type=task_type,
            path=path,
            message=f"Problem detected: {task_type} at {path}",
            severity="warning",
        )
        if problem_narrative_id:
            problem_ids = [problem_narrative_id]
            problem_moment = ctx.agent_graph.create_moment(
                actor_id=actor_id,
                moment_type="problem_detected",
                prose=f"Detected {task_type} at {path}",
                about_ids=[problem_narrative_id],
                space_id=space_id,
                extra_props={"task_type": task_type, "path": path},
            )
            if problem_moment:
                moments_created.append(("problem_detected", problem_moment, f"Detected {task_type} at {path}"))

        if not prompt:
            prompt = f"""Fix the problem:
Problem Type: {task_type}
Path: {path}

Please investigate and fix this problem. Follow the project's coding standards and documentation patterns."""

    assignment_task_id = task_id
    if not assignment_task_id and task_type:
        assignment_task_id = ctx.agent_graph.upsert_task_narrative(
            task_type=f"FIX_{task_type}",
            content=f"Fix {task_type} at {path}",
            name=f"Fix {task_type}",
        )
        if assignment_task_id:
            task_moment = ctx.agent_graph.create_moment(
                actor_id=actor_id,
                moment_type="task_created",
                prose=f"Created task to fix {task_type}",
                about_ids=[assignment_task_id] + (problem_ids or []),
                space_id=space_id,
                extra_props={"task_id": assignment_task_id, "task_type": f"FIX_{task_type}"},
            )
            if task_moment:
                moments_created.append(("task_created", task_moment, f"Created task: Fix {task_type}"))

    # Execute agent
    try:
        coro = run_work_agent(
            actor_id=actor_id,
            prompt=prompt,
            target_dir=ctx.target_dir,
            agent_provider=provider,
            timeout=300.0,
            use_continue=True,
            task_id=assignment_task_id,
            problem_ids=problem_ids,
        )
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                run_result = pool.submit(asyncio.run, coro).result()
        except RuntimeError:
            run_result = asyncio.run(coro)

        # Build response
        lines = [
            "# Agent Execution Complete",
            "",
            "## Agent",
            f"- **ID:** {actor_id}",
            f"- **Posture:** {name}",
            f"- **Provider:** {provider}",
            f"- **Success:** {run_result.success}",
            f"- **Duration:** {run_result.duration_seconds:.1f}s",
        ]

        if task_id or assignment_task_id:
            lines.extend(["", "## Task", f"- **ID:** {task_id or assignment_task_id}"])
            if not task_id and task_type:
                lines.extend([
                    f"- **Type:** FIX_{task_type}",
                    f"- **Name:** Fix {task_type}",
                ])

        if run_result.assignment_moment_id:
            moments_created.append(("assignment", run_result.assignment_moment_id, f"Agent {actor_id} assigned to task"))

        if moments_created:
            lines.extend(["", "## Moment Chain", f"*Actor: {actor_id}*"])
            if space_id:
                lines.append(f"*Space: {space_id}*")
            lines.append("")
            for i, (moment_type, moment_id, prose) in enumerate(moments_created):
                prefix = "→ " if i > 0 else "● "
                lines.append(f"{prefix}**{moment_type}**: {prose}")
                lines.append(f"  `{moment_id}`")
                if i < len(moments_created) - 1:
                    lines.append(f"  ↓ follows")

        cmd_info = build_agent_command(
            agent=provider,
            prompt="<prompt>",
            system_prompt="<system_prompt>",
            stream_json=True,
            continue_session=True,
            add_dir=ctx.target_dir,
            allowed_tools="Bash Read Edit Write Glob Grep WebFetch NotebookEdit TodoWrite",
        )
        lines.extend(["", "## Command", "```", f"{' '.join(cmd_info.cmd[:8])}...", "```"])

        if run_result.retried_without_continue:
            lines.append("  Note: Retried without --continue")
        if run_result.error:
            lines.append(f"  Error: {run_result.error[:200]}")
        if run_result.output:
            lines.extend(["", "Agent Output:", run_result.output[:1000] + ("..." if len(run_result.output) > 1000 else "")])

        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Agent run failed")
        return _err(f"Executing agent: {e}")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
