"""
Agent orchestration for autonomous problem fixing.

This module provides:
- Agent running and execution
- Graph-based status tracking
- Posture-based agent selection
- Verification and retry logic

DOCS: docs/agents/PATTERNS_Agent_System.md

Usage:
    from runtime.agents import run_work_agent, AgentGraph

    # Run agent for problem
    result = await run_work_agent(
        task_type="STALE_SYNC",
        path="docs/physics/SYNC.md",
        target_dir=Path("."),
        agent_provider="claude",
    )

    # Or run for task
    result = await run_for_task(
        task_id="narrative:task:TASK_create_doc",
        target_dir=Path("."),
    )
"""

# Re-export from submodules for clean API
from .graph import AgentGraph, AgentInfo
from .mapping import (
    TASK_TO_AGENT,
    NAME_TO_ACTOR_ID,
    DEFAULT_NAME,
    make_id,
    discover_agents,
    get_agent_id,
    list_agents,
    select_agent_for_task,
)
from .cli import build_agent_command, normalize_agent, AgentCommand
from .run import (
    run_work_agent,
    run_for_task,
    RunResult,
)
from .prompts import (
    get_agent_system_prompt,
    build_agent_prompt,
    get_learnings_content,
)
from .verification import (
    verify_completion,
    VerificationResult,
    all_passed,
)

__all__ = [
    # Graph
    "AgentGraph",
    "AgentInfo",
    # Agent Discovery
    "TASK_TO_AGENT",
    "NAME_TO_ACTOR_ID",
    "DEFAULT_NAME",
    "make_id",
    "discover_agents",
    "get_agent_id",
    "list_agents",
    "select_agent_for_task",
    # CLI
    "build_agent_command",
    "normalize_agent",
    "AgentCommand",
    # Run
    "run_work_agent",
    "run_for_task",
    "RunResult",
    # Prompts
    "get_agent_system_prompt",
    "build_agent_prompt",
    "get_learnings_content",
    # Verification
    "verify_completion",
    "VerificationResult",
    "all_passed",
]
