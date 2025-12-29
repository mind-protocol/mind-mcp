"""
Agent orchestration for autonomous issue fixing.

This module provides:
- Agent spawning and execution
- Graph-based status tracking
- Posture-based agent selection
- Verification and retry logic

DOCS: docs/agents/PATTERNS_Agent_System.md

Usage:
    from runtime.agents import spawn_work_agent, AgentGraph

    # Spawn agent for issue
    result = await spawn_work_agent(
        issue_type="STALE_SYNC",
        path="docs/physics/SYNC.md",
        target_dir=Path("."),
        agent_provider="claude",
    )

    # Or spawn for task
    result = await spawn_for_task(
        task_id="narrative:task:TASK_create_doc",
        target_dir=Path("."),
    )
"""

# Re-export from submodules for clean API
from .graph import AgentGraph, AgentInfo
from .postures import (
    PROBLEM_TO_POSTURE,
    POSTURE_TO_AGENT_ID,
    DEFAULT_POSTURE,
    select_agent_for_problem,
)
from .cli import build_agent_command, normalize_agent, AgentCommand
from .spawn import (
    spawn_work_agent,
    spawn_agent_for_problem,
    SpawnResult,
)
from .prompts import (
    AGENT_SYSTEM_PROMPT,
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
    # Postures
    "PROBLEM_TO_POSTURE",
    "POSTURE_TO_AGENT_ID",
    "DEFAULT_POSTURE",
    "select_agent_for_problem",
    # CLI
    "build_agent_command",
    "normalize_agent",
    "AgentCommand",
    # Spawn
    "spawn_work_agent",
    "spawn_agent_for_problem",
    "SpawnResult",
    # Prompts
    "AGENT_SYSTEM_PROMPT",
    "build_agent_prompt",
    "get_learnings_content",
    # Verification
    "verify_completion",
    "VerificationResult",
    "all_passed",
]
