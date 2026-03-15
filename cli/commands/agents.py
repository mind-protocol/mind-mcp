"""mind agents - Agent lifecycle management CLI commands.

DOCS: docs/cli/commands/IMPLEMENTATION_Agents_Command.md

Provides:
- mind agents list: Show running agents, their tasks, and duration
- mind agents pause: Pause an agent (keeps state)
- mind agents stop: Stop an agent gracefully
- mind agents kill: Force kill an agent
- mind agents enable: Enable a paused agent
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
class AgentInfo:
    """Information about a running agent."""
    actor_id: str
    name: str
    status: str  # ready, running, paused, stopped
    current_task: Optional[str] = None
    task_started: Optional[datetime] = None
    provider: str = "unknown"
    tasks_completed: int = 0
    errors: int = 0


def _get_capability_runtime():
    """Get capability runtime components if available."""
    try:
        from runtime.capability_integration import (
            get_capability_manager,
            get_throttler,
            get_controller,
            get_agent_registry,
            AgentMode,
            CAPABILITY_RUNTIME_AVAILABLE,
        )
        if CAPABILITY_RUNTIME_AVAILABLE:
            return {
                "manager": get_capability_manager,
                "throttler": get_throttler,
                "controller": get_controller,
                "registry": get_agent_registry,
                "AgentMode": AgentMode,
            }
    except ImportError:
        pass
    return None


def _get_agents_from_graph(target_dir: Path) -> List[AgentInfo]:
    """Get agent information from the graph."""
    agents = []

    try:
        from runtime.physics.graph.graph_ops import GraphOps

        graph_name = target_dir.name
        graph = GraphOps(graph_name=graph_name)

        # Query for actor nodes of type 'agent'
        result = graph.query("""
            MATCH (a:Actor)
            WHERE a.type = 'agent' OR a.id STARTS WITH 'ACTOR_'
            RETURN a.id, a.name, a.status, a.provider, a.current_task
            ORDER BY a.name
        """)

        for row in result:
            actor_id, name, status, provider, current_task = row
            agents.append(AgentInfo(
                actor_id=actor_id or "",
                name=name or actor_id or "unknown",
                status=status or "ready",
                provider=provider or "unknown",
                current_task=current_task,
            ))

    except Exception:
        pass

    return agents


def _get_agents_from_runtime() -> List[AgentInfo]:
    """Get agent information from the capability runtime."""
    agents = []

    runtime = _get_capability_runtime()
    if not runtime:
        return agents

    try:
        registry = runtime["registry"]()
        if registry:
            for actor_id, agent_state in registry.get_all_agents().items():
                agents.append(AgentInfo(
                    actor_id=actor_id,
                    name=agent_state.get("name", actor_id),
                    status=agent_state.get("status", "unknown"),
                    current_task=agent_state.get("current_task"),
                    task_started=agent_state.get("task_started"),
                    provider=agent_state.get("provider", "unknown"),
                    tasks_completed=agent_state.get("tasks_completed", 0),
                    errors=agent_state.get("errors", 0),
                ))
    except Exception:
        pass

    return agents


def _format_duration(start: Optional[datetime]) -> str:
    """Format duration since start time."""
    if not start:
        return "-"

    delta = datetime.now() - start
    if delta.days > 0:
        return f"{delta.days}d {delta.seconds // 3600}h"
    elif delta.seconds >= 3600:
        return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
    elif delta.seconds >= 60:
        return f"{delta.seconds // 60}m {delta.seconds % 60}s"
    else:
        return f"{delta.seconds}s"


def _status_color(status: str) -> str:
    """Get color for agent status."""
    return {
        "ready": C.BRIGHT_GREEN,
        "running": C.BRIGHT_CYAN,
        "paused": C.BRIGHT_YELLOW,
        "stopped": C.DIM,
        "error": C.BRIGHT_RED,
    }.get(status.lower(), C.WHITE)


def list_agents(target_dir: Path, format_output: str = "text") -> int:
    """List all agents and their status.

    Args:
        target_dir: Project directory
        format_output: Output format (text or json)

    Returns:
        Exit code
    """
    # Collect agents from all sources
    agents = _get_agents_from_runtime()

    # Also check graph for configured agents
    graph_agents = _get_agents_from_graph(target_dir)

    # Merge: runtime agents take precedence
    runtime_ids = {a.actor_id for a in agents}
    for ga in graph_agents:
        if ga.actor_id not in runtime_ids:
            agents.append(ga)

    if format_output == "json":
        output = []
        for a in agents:
            output.append({
                "actor_id": a.actor_id,
                "name": a.name,
                "status": a.status,
                "provider": a.provider,
                "current_task": a.current_task,
                "tasks_completed": a.tasks_completed,
                "errors": a.errors,
            })
        print(json.dumps(output, indent=2))
        return 0

    # Text output
    print()
    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print(f"{C.BOLD}  AGENTS{C.RESET}")
    print(f"{C.BOLD}{'═' * 78}{C.RESET}")
    print()

    if not agents:
        print(f"  {C.DIM}No agents configured.{C.RESET}")
        print()
        print(f"  {C.DIM}Agents are runed by:{C.RESET}")
        print(f"  {C.DIM}  - mind work (auto-runs agents for issues){C.RESET}")
        print(f"  {C.DIM}  - Capability triggers (health checks){C.RESET}")
        print()
        return 0

    # Summary
    running = sum(1 for a in agents if a.status.lower() == "running")
    ready = sum(1 for a in agents if a.status.lower() == "ready")
    paused = sum(1 for a in agents if a.status.lower() == "paused")

    print(f"  {C.BOLD}Summary:{C.RESET} {running} running, {ready} ready, {paused} paused")
    print()

    # Table header
    print(f"  {C.BOLD}{'AGENT':<20} {'STATUS':<10} {'PROVIDER':<10} {'TASK':<25} {'DURATION':<10}{C.RESET}")
    print(f"  {C.DIM}{'─' * 75}{C.RESET}")

    for a in sorted(agents, key=lambda x: (x.status != "running", x.name)):
        status_c = _status_color(a.status)

        # Truncate task if needed
        task = a.current_task or "-"
        if len(task) > 23:
            task = task[:20] + "..."

        duration = _format_duration(a.task_started) if a.status.lower() == "running" else "-"

        print(f"  {a.name:<20} {status_c}{a.status:<10}{C.RESET} {a.provider:<10} {task:<25} {duration:<10}")

    print(f"  {C.DIM}{'─' * 75}{C.RESET}")
    print()

    # Show controller status if available
    runtime = _get_capability_runtime()
    if runtime:
        try:
            controller = runtime["controller"]()
            if controller:
                mode = controller.mode.value if hasattr(controller.mode, 'value') else str(controller.mode)
                can_claim = controller.can_claim()

                mode_color = C.BRIGHT_GREEN if can_claim else C.YELLOW
                print(f"  {C.BOLD}Controller:{C.RESET} {mode_color}{mode}{C.RESET} (claims {'enabled' if can_claim else 'paused'})")
        except Exception:
            pass

        try:
            throttler = runtime["throttler"]()
            if throttler:
                pending = len(throttler.pending_tasks)
                active = len(throttler.active_tasks)
                print(f"  {C.BOLD}Throttler:{C.RESET} {active} active, {pending} pending")
        except Exception:
            pass

        print()

    return 0


def pause_agent(actor_id: str) -> int:
    """Pause an agent (keeps state)."""
    runtime = _get_capability_runtime()
    if not runtime:
        print(f"{C.RED}Capability runtime not available{C.RESET}")
        return 1

    try:
        registry = runtime["registry"]()
        if registry and hasattr(registry, 'pause_agent'):
            registry.pause_agent(actor_id)
            print(f"{C.GREEN}Agent {actor_id} paused{C.RESET}")
            return 0
    except Exception as e:
        print(f"{C.RED}Failed to pause agent: {e}{C.RESET}")
        return 1

    print(f"{C.YELLOW}Pause not supported by current runtime{C.RESET}")
    return 1


def stop_agent(actor_id: str) -> int:
    """Stop an agent gracefully."""
    runtime = _get_capability_runtime()
    if not runtime:
        print(f"{C.RED}Capability runtime not available{C.RESET}")
        return 1

    try:
        registry = runtime["registry"]()
        if registry and hasattr(registry, 'stop_agent'):
            registry.stop_agent(actor_id)
            print(f"{C.GREEN}Agent {actor_id} stopped{C.RESET}")
            return 0
    except Exception as e:
        print(f"{C.RED}Failed to stop agent: {e}{C.RESET}")
        return 1

    print(f"{C.YELLOW}Stop not supported by current runtime{C.RESET}")
    return 1


def kill_agent(actor_id: str) -> int:
    """Force kill an agent."""
    runtime = _get_capability_runtime()
    if not runtime:
        print(f"{C.RED}Capability runtime not available{C.RESET}")
        return 1

    try:
        registry = runtime["registry"]()
        if registry and hasattr(registry, 'kill_agent'):
            registry.kill_agent(actor_id)
            print(f"{C.BRIGHT_RED}Agent {actor_id} killed{C.RESET}")
            return 0
    except Exception as e:
        print(f"{C.RED}Failed to kill agent: {e}{C.RESET}")
        return 1

    print(f"{C.YELLOW}Kill not supported by current runtime{C.RESET}")
    return 1


def enable_agent(actor_id: str) -> int:
    """Enable a paused agent."""
    runtime = _get_capability_runtime()
    if not runtime:
        print(f"{C.RED}Capability runtime not available{C.RESET}")
        return 1

    try:
        registry = runtime["registry"]()
        if registry and hasattr(registry, 'enable_agent'):
            registry.enable_agent(actor_id)
            print(f"{C.GREEN}Agent {actor_id} enabled{C.RESET}")
            return 0
    except Exception as e:
        print(f"{C.RED}Failed to enable agent: {e}{C.RESET}")
        return 1

    print(f"{C.YELLOW}Enable not supported by current runtime{C.RESET}")
    return 1


def agents_command(
    target_dir: Path,
    action: str,
    actor_id: Optional[str] = None,
    format_output: str = "text",
) -> int:
    """Main entry point for agents command.

    Args:
        target_dir: Project directory
        action: list, pause, stop, kill, enable
        actor_id: Target agent ID (required for pause/stop/kill/enable)
        format_output: Output format

    Returns:
        Exit code
    """
    if action == "list":
        return list_agents(target_dir, format_output)
    elif action == "pause":
        if not actor_id:
            print(f"{C.RED}Agent ID required for pause{C.RESET}")
            return 1
        return pause_agent(actor_id)
    elif action == "stop":
        if not actor_id:
            print(f"{C.RED}Agent ID required for stop{C.RESET}")
            return 1
        return stop_agent(actor_id)
    elif action == "kill":
        if not actor_id:
            print(f"{C.RED}Agent ID required for kill{C.RESET}")
            return 1
        return kill_agent(actor_id)
    elif action == "enable":
        if not actor_id:
            print(f"{C.RED}Agent ID required for enable{C.RESET}")
            return 1
        return enable_agent(actor_id)
    else:
        print(f"{C.RED}Unknown action: {action}{C.RESET}")
        return 1
