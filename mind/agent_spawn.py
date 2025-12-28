"""
Agent Spawn with Status Management

Spawns work agents with:
1. Graph status tracking (running/ready)
2. --continue retry logic (try with --continue, retry without on failure)
3. Posture-based system prompt loading

Usage:
    from mind.agent_spawn import spawn_work_agent

    result = await spawn_work_agent(
        agent_id="agent_witness",
        prompt="Fix the stale SYNC file at...",
        target_dir=Path("/path/to/project"),
        agent_provider="claude",
    )

DOCS: docs/membrane/PATTERNS_Membrane.md
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Awaitable, List

from .agent_graph import (
    AgentGraph,
    load_agent_prompt,
    POSTURE_TO_AGENT_ID,
)
from .agent_cli import build_agent_command, normalize_agent

logger = logging.getLogger(__name__)


@dataclass
class SpawnResult:
    """Result of spawning a work agent."""
    success: bool
    agent_id: str
    output: str
    error: Optional[str] = None
    duration_seconds: float = 0.0
    retried_without_continue: bool = False
    assignment_moment_id: Optional[str] = None  # ID of the assignment moment created


async def spawn_work_agent(
    agent_id: str,
    prompt: str,
    target_dir: Path,
    agent_provider: str = "claude",
    on_output: Optional[Callable[[str], Awaitable[None]]] = None,
    timeout: float = 300.0,
    use_continue: bool = True,
    task_id: Optional[str] = None,
    issue_ids: Optional[List[str]] = None,
) -> SpawnResult:
    """
    Spawn a work agent with status management and --continue retry.

    This function:
    1. Sets agent status to 'running' in the graph
    2. Creates graph links for task/issue assignment (if provided)
    3. Creates an assignment moment recording the spawn
    4. Loads the agent's posture-based system prompt
    5. Attempts spawn with --continue (if use_continue=True)
    6. On failure, retries without --continue
    7. Sets agent status back to 'ready' when done

    Args:
        agent_id: Agent ID (e.g., "agent_witness")
        prompt: The task prompt for the agent
        target_dir: Project root directory
        agent_provider: Provider (claude, gemini, codex, all)
        on_output: Optional callback for streaming output
        timeout: Maximum time in seconds
        use_continue: Whether to try --continue first
        task_id: Optional task narrative ID to link agent to
        issue_ids: Optional list of issue narrative IDs to link agent to

    Returns:
        SpawnResult with success status and output
    """
    agent_provider = normalize_agent(agent_provider)
    start_time = time.time()
    assignment_moment_id = None

    # Extract posture from agent_id
    posture = agent_id.replace("agent_", "") if agent_id.startswith("agent_") else agent_id

    # Initialize graph connection
    agent_graph = AgentGraph(graph_name="mind")

    # Set agent to running
    agent_graph.set_agent_running(agent_id)

    # Create assignment links and moment if task/issues provided
    if task_id or issue_ids:
        # assign_agent_to_work creates links AND moment, returns moment ID
        assignment_moment_id = agent_graph.assign_agent_to_work(
            agent_id, task_id or "", issue_ids
        )

    try:
        # Load posture-based system prompt
        system_prompt = load_agent_prompt(posture, target_dir, agent_provider) or ""

        # Build and run the agent command
        result = await _spawn_with_retry(
            prompt=prompt,
            system_prompt=system_prompt,
            target_dir=target_dir,
            agent_provider=agent_provider,
            on_output=on_output,
            timeout=timeout,
            use_continue=use_continue,
        )

        duration = time.time() - start_time

        # Boost energy on successful completion
        if result.success:
            agent_graph.boost_agent_energy(agent_id, 0.1)

        return SpawnResult(
            success=result.success,
            agent_id=agent_id,
            output=result.output,
            error=result.error,
            duration_seconds=duration,
            retried_without_continue=result.retried,
            assignment_moment_id=assignment_moment_id,
        )

    finally:
        # Always set agent back to ready
        agent_graph.set_agent_ready(agent_id)


@dataclass
class _InternalResult:
    """Internal result from spawn attempt."""
    success: bool
    output: str
    error: Optional[str] = None
    retried: bool = False


async def _spawn_with_retry(
    prompt: str,
    system_prompt: str,
    target_dir: Path,
    agent_provider: str,
    on_output: Optional[Callable[[str], Awaitable[None]]],
    timeout: float,
    use_continue: bool,
) -> _InternalResult:
    """
    Spawn agent with --continue retry logic.

    First attempts with --continue (if enabled).
    On failure, retries without --continue.
    """
    retried = False

    # First attempt: with --continue if enabled
    if use_continue:
        try:
            result = await _run_agent(
                prompt=prompt,
                system_prompt=system_prompt,
                target_dir=target_dir,
                agent_provider=agent_provider,
                continue_session=True,
                on_output=on_output,
                timeout=timeout,
            )

            if result.success:
                return _InternalResult(
                    success=True,
                    output=result.output,
                    retried=False,
                )
        except Exception as e:
            logger.warning(f"[spawn] --continue attempt failed: {e}, retrying without")
            retried = True

    # Second attempt: without --continue
    try:
        result = await _run_agent(
            prompt=prompt,
            system_prompt=system_prompt,
            target_dir=target_dir,
            agent_provider=agent_provider,
            continue_session=False,
            on_output=on_output,
            timeout=timeout,
        )

        return _InternalResult(
            success=result.success,
            output=result.output,
            error=result.error if not result.success else None,
            retried=retried,
        )

    except Exception as e:
        return _InternalResult(
            success=False,
            output="",
            error=str(e),
            retried=retried,
        )


@dataclass
class _RunResult:
    """Result from running an agent process."""
    success: bool
    output: str
    error: Optional[str] = None


async def _run_agent(
    prompt: str,
    system_prompt: str,
    target_dir: Path,
    agent_provider: str,
    continue_session: bool,
    on_output: Optional[Callable[[str], Awaitable[None]]],
    timeout: float,
) -> _RunResult:
    """
    Run an agent process and collect output.
    """
    # Build command
    agent_cmd = build_agent_command(
        agent=agent_provider,
        prompt=prompt,
        system_prompt=system_prompt,
        stream_json=True,
        continue_session=continue_session,
        add_dir=target_dir,
        allowed_tools="Bash(*) Read(*) Edit(*) Write(*) Glob(*) Grep(*) WebFetch(*) NotebookEdit(*) TodoWrite(*)",
    )

    # Start process
    process = await asyncio.create_subprocess_exec(
        *agent_cmd.cmd,
        cwd=str(target_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE if agent_cmd.stdin else None,
    )

    stdin_data = (agent_cmd.stdin + "\n").encode() if agent_cmd.stdin else None

    try:
        stdout_data, stderr_data = await asyncio.wait_for(
            process.communicate(input=stdin_data),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return _RunResult(
            success=False,
            output="",
            error=f"Agent timed out after {timeout}s",
        )

    stdout_str = stdout_data.decode(errors="replace")
    stderr_str = stderr_data.decode(errors="replace")

    # Parse output
    output_parts = []
    for line in stdout_str.split("\n"):
        line = line.strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            if isinstance(data, dict):
                if data.get("type") == "assistant":
                    msg_data = data.get("message", {})
                    if isinstance(msg_data, dict):
                        for content in msg_data.get("content", []):
                            if isinstance(content, dict):
                                if content.get("type") == "text":
                                    text = content.get("text", "")
                                    output_parts.append(text)
                                    if on_output:
                                        await on_output(text)
                elif data.get("type") == "result":
                    result = data.get("result", "")
                    if result:
                        output_parts.append(result)
                        if on_output:
                            await on_output(result)
        except json.JSONDecodeError:
            # Plain text output
            output_parts.append(line)
            if on_output:
                await on_output(line)

    output = "\n".join(output_parts)

    # Check exit code
    success = process.returncode == 0

    if not success and stderr_str:
        return _RunResult(
            success=False,
            output=output,
            error=stderr_str[:500],
        )

    return _RunResult(
        success=success,
        output=output,
    )


async def spawn_agent_for_issue(
    issue_type: str,
    prompt: str,
    target_dir: Path,
    agent_provider: str = "claude",
    on_output: Optional[Callable[[str], Awaitable[None]]] = None,
    timeout: float = 300.0,
    task_id: Optional[str] = None,
    issue_ids: Optional[List[str]] = None,
) -> SpawnResult:
    """
    Select and spawn the best agent for an issue type.

    This is a convenience function that:
    1. Selects the best agent based on posture mapping
    2. Spawns it with status management
    3. Creates graph links for task/issue assignment (if provided)

    Args:
        issue_type: Doctor issue type (e.g., "STALE_SYNC")
        prompt: The task prompt
        target_dir: Project root
        agent_provider: Provider name
        on_output: Optional output callback
        timeout: Maximum time
        task_id: Optional task narrative ID to link agent to
        issue_ids: Optional list of issue narrative IDs to link agent to

    Returns:
        SpawnResult
    """
    agent_graph = AgentGraph(graph_name="mind")

    # Select best agent for this issue type
    agent_id = agent_graph.select_agent_for_issue(issue_type)

    if not agent_id:
        # All agents busy, wait and try default
        logger.warning("[spawn] All agents busy, using default fixer")
        agent_id = POSTURE_TO_AGENT_ID.get("fixer", "agent_fixer")

    return await spawn_work_agent(
        agent_id=agent_id,
        prompt=prompt,
        target_dir=target_dir,
        agent_provider=agent_provider,
        on_output=on_output,
        timeout=timeout,
        task_id=task_id,
        issue_ids=issue_ids,
    )
