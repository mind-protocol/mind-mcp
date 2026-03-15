"""
mind swarm - Run multiple agents in parallel with live streaming.

Usage:
    mind swarm --agents 3              # Run 3 agents in parallel (foreground)
    mind swarm --agents 3 --background # Run in background
    mind swarm --status                # Show running agents
    mind swarm --stop                  # Stop all agents
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # Agent colors (cycle through these)
    AGENTS = [
        "\033[36m",  # Cyan
        "\033[33m",  # Yellow
        "\033[35m",  # Magenta
        "\033[32m",  # Green
        "\033[34m",  # Blue
        "\033[91m",  # Light Red
        "\033[92m",  # Light Green
        "\033[93m",  # Light Yellow
        "\033[94m",  # Light Blue
        "\033[95m",  # Light Magenta
    ]
    # Status colors
    SUCCESS = "\033[32m"  # Green
    ERROR = "\033[31m"    # Red
    WARNING = "\033[33m"  # Yellow
    INFO = "\033[36m"     # Cyan
    MOMENT = "\033[35m"   # Magenta

# Agent color mapping
_agent_colors = {}
_color_index = 0

def _get_agent_color(agent_id: str) -> str:
    """Get consistent color for an agent."""
    global _color_index
    if agent_id not in _agent_colors:
        _agent_colors[agent_id] = Colors.AGENTS[_color_index % len(Colors.AGENTS)]
        _color_index += 1
    return _agent_colors[agent_id]

# PID file for tracking background processes
SWARM_DIR = Path(".mind/swarm")
PID_FILE = SWARM_DIR / "pids.json"
LOG_DIR = SWARM_DIR / "logs"


def _ensure_dirs():
    """Create swarm directories."""
    SWARM_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _get_available_agents() -> List[str]:
    """Get list of available AGENT_* actors."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        result = adapter.query("""
            MATCH (a:Actor)
            WHERE a.type = 'AGENT' AND COALESCE(a.status, 'idle') <> 'paused'
            RETURN a.id
            ORDER BY a.id
        """)
        return [r[0] for r in result] if result else []
    except Exception:
        return []


def _get_pending_tasks() -> List[dict]:
    """Get pending tasks for agents to claim."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        result = adapter.query("""
            MATCH (t:Narrative {type: 'task_run', status: 'pending'})
            RETURN t.id, t.synthesis
            LIMIT 50
        """)
        return [{"id": r[0], "synthesis": r[1]} for r in result] if result else []
    except Exception:
        return []


def _build_agent_script(agent_id: str, log_file: Path, target_dir: Path) -> str:
    """Build the Python script for an agent process."""
    agent_name = agent_id.replace("AGENT_", "")
    return f'''
import sys
import asyncio
import logging
from pathlib import Path

# Setup logging - both file and stderr for live output
logging.basicConfig(
    level=logging.INFO,
    format='[{agent_name}] %(message)s',
    handlers=[
        logging.FileHandler("{log_file}"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger()

async def main():
    try:
        from runtime.infrastructure.database import get_database_adapter
        from runtime.agents import run_work_agent
        from runtime.task_assignment import assign_single_task

        adapter = get_database_adapter()
        logger.info("Agent started")

        tasks_completed = 0
        max_tasks = 50  # Safety limit

        while tasks_completed < max_tasks:
            # Find a task claimed by this agent
            result = adapter.query("""
                MATCH (t:Narrative {{type: 'task_run', status: 'claimed'}})-[:LINK {{verb: 'claimed_by'}}]->(a:Actor {{id: $agent_id}})
                RETURN t.id, t.synthesis
                LIMIT 1
            """, {{"agent_id": "{agent_id}"}})

            if not result or not result[0]:
                # No claimed tasks - try to claim a pending one via physics
                pending = adapter.query("""
                    MATCH (t:Narrative {{type: 'task_run', status: 'pending'}})
                    OPTIONAL MATCH (t)-[r:LINK {{verb: 'claimed_by'}}]->(a:Actor)
                    WITH t, a WHERE a IS NULL
                    RETURN t.id, t.synthesis
                    LIMIT 1
                """)

                if pending and pending[0]:
                    task_id, synthesis = pending[0]
                    if synthesis:
                        assigned = assign_single_task(task_id, synthesis, adapter)
                        if assigned == "{agent_id}":
                            logger.info(f"Claimed: {{task_id}}")
                            continue  # Go work on it

                # No pending tasks for this agent
                logger.info(f"No more tasks. Completed {{tasks_completed}} tasks.")
                break

            task_id, synthesis = result[0]
            logger.info(f"Working on: {{task_id}}")

            # Get more task context - linked problems and target
            context_result = adapter.query("""
                MATCH (t:Narrative {{id: $task_id}})
                OPTIONAL MATCH (t)-[:LINK {{verb: 'concerns'}}]->(problem)
                OPTIONAL MATCH (t)-[:LINK {{verb: 'targets'}}]->(target)
                RETURN t.content, problem.synthesis, problem.content, target.id
                LIMIT 1
            """, {{"task_id": task_id}})

            task_content = ""
            problem_info = ""
            target_path = ""
            if context_result and context_result[0]:
                ctx = context_result[0]
                task_content = ctx[0] or ""
                if ctx[1] or ctx[2]:
                    problem_info = f"Problem: {{ctx[1] or ctx[2]}}"
                target_path = ctx[3] or ""

            # Get implements chain: task_run --serves--> TASK --uses--> SKILL --executes--> PROCEDURE
            chain_parts = []
            chain_result = adapter.query("""
                MATCH (run:Narrative {{id: $task_id}})
                OPTIONAL MATCH (run)-[:LINK {{verb: 'serves'}}]->(template:Narrative)
                OPTIONAL MATCH (template)-[:LINK {{verb: 'uses'}}]->(skill:Narrative)
                OPTIONAL MATCH (skill)-[:LINK {{verb: 'executes'}}]->(proc)
                RETURN template.id, template.path, template.synthesis,
                       skill.id, skill.path, skill.synthesis,
                       proc.id, proc.path, proc.content
            """, {{"task_id": task_id}})

            if chain_result:
                seen_templates = set()
                seen_skills = set()
                seen_procs = set()
                for row in chain_result:
                    tmpl_id, tmpl_path, tmpl_synth = row[0], row[1], row[2]
                    skill_id, skill_path, skill_synth = row[3], row[4], row[5]
                    proc_id, proc_path, proc_content = row[6], row[7], row[8]

                    # Load task template content from file
                    if tmpl_id and tmpl_id not in seen_templates:
                        seen_templates.add(tmpl_id)
                        if tmpl_path:
                            try:
                                tmpl_content = Path(tmpl_path).read_text()[:2000]
                                chain_parts.append(f"## Task Template: {{tmpl_id}}\\n{{tmpl_content}}")
                            except Exception:
                                if tmpl_synth:
                                    chain_parts.append(f"## Task Template: {{tmpl_id}}\\n{{tmpl_synth}}")
                        elif tmpl_synth:
                            chain_parts.append(f"## Task Template: {{tmpl_id}}\\n{{tmpl_synth}}")

                    # Load skill content from file
                    if skill_id and skill_id not in seen_skills:
                        seen_skills.add(skill_id)
                        if skill_path:
                            try:
                                skill_content = Path(skill_path).read_text()[:3000]
                                chain_parts.append(f"## Skill: {{skill_id}}\\n{{skill_content}}")
                            except Exception:
                                if skill_synth:
                                    chain_parts.append(f"## Skill: {{skill_id}}\\n{{skill_synth}}")
                        elif skill_synth:
                            chain_parts.append(f"## Skill: {{skill_id}}\\n{{skill_synth}}")

                    # Load procedure content from file
                    if proc_id and proc_id not in seen_procs:
                        seen_procs.add(proc_id)
                        if proc_path:
                            try:
                                proc_file_content = Path(proc_path).read_text()[:1500]
                                chain_parts.append(f"## Procedure: {{proc_id}}\\n{{proc_file_content}}")
                            except Exception:
                                if proc_content:
                                    chain_parts.append(f"## Procedure: {{proc_id}}\\n{{proc_content}}")
                        elif proc_content:
                            chain_parts.append(f"## Procedure: {{proc_id}}\\n{{proc_content}}")

            # Mark as running
            adapter.execute(
                "MATCH (t:Narrative {{id: $id}}) SET t.status = 'running'",
                {{"id": task_id}}
            )

            # Run the agent work
            try:
                # Build meaningful prompt from task context
                prompt_parts = []
                if synthesis:
                    prompt_parts.append(synthesis)
                if problem_info:
                    prompt_parts.append(problem_info)
                if task_content:
                    prompt_parts.append(f"Details: {{task_content[:500]}}")
                if target_path:
                    prompt_parts.append(f"Target: {{target_path}}")

                # Add implements chain (skills, procedures, templates)
                if chain_parts:
                    prompt_parts.append("\\n# Implements Chain\\n")
                    prompt_parts.extend(chain_parts)

                prompt = "\\n".join(prompt_parts) if prompt_parts else f"Execute task {{task_id}}"
                target_dir = Path("{target_dir}")

                run_result = await run_work_agent(
                    actor_id="{agent_id}",
                    prompt=prompt,
                    target_dir=target_dir,
                    task_id=task_id,
                    timeout=600.0,
                )

                if run_result.success:
                    adapter.execute(
                        "MATCH (t:Narrative {{id: $id}}) SET t.status = 'completed'",
                        {{"id": task_id}}
                    )
                    logger.info(f"Completed: {{task_id}}")
                    # Log moment if created
                    if run_result.completion_moment_id:
                        # Get moment synthesis
                        m = adapter.query(
                            "MATCH (m:Moment {{id: $id}}) RETURN m.synthesis",
                            {{"id": run_result.completion_moment_id}}
                        )
                        if m and m[0] and m[0][0]:
                            logger.info(f"Moment: {{m[0][0][:80]}}")
                    tasks_completed += 1
                else:
                    adapter.execute(
                        "MATCH (t:Narrative {{id: $id}}) SET t.status = 'failed', t.error = $error",
                        {{"id": task_id, "error": run_result.error or "Unknown error"}}
                    )
                    logger.error(f"Failed: {{task_id}} - {{run_result.error}}")
                    tasks_completed += 1  # Count failures too

            except Exception as e:
                adapter.execute(
                    "MATCH (t:Narrative {{id: $id}}) SET t.status = 'failed', t.error = $error",
                    {{"id": task_id, "error": str(e)}}
                )
                logger.error(f"Failed: {{task_id}} - {{e}}")
                tasks_completed += 1

    except Exception as e:
        logger.error(f"Agent error: {{e}}")

asyncio.run(main())
'''


def _run_agent_silent(agent_id: str, log_file: Path, target_dir: Path):
    """Run an agent silently, logging only to file."""
    script = _build_agent_script(agent_id, log_file, target_dir)

    proc = subprocess.Popen(
        [sys.executable, "-c", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    proc.wait()
    return proc.returncode


def _spawn_agent_background(agent_id: str, log_file: Path, target_dir: Path) -> Optional[int]:
    """Spawn an agent in background. Returns PID."""
    script = _build_agent_script(agent_id, log_file, target_dir)

    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return proc.pid
    except Exception as e:
        print(f"Failed to spawn {agent_id}: {e}")
        return None


def _save_pids(pids: dict):
    """Save PIDs to file."""
    _ensure_dirs()
    PID_FILE.write_text(json.dumps(pids, indent=2))


def _load_pids() -> dict:
    """Load PIDs from file."""
    if PID_FILE.exists():
        try:
            return json.loads(PID_FILE.read_text())
        except Exception:
            pass
    return {}


def _is_running(pid: int) -> bool:
    """Check if process is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _fire_capability_trigger(trigger_type: str, target_dir: Path) -> int:
    """Fire a capability trigger to generate tasks. Returns tasks created."""
    try:
        from runtime.capability_integration import CapabilityManager
        from runtime.physics.graph import GraphOps
        from runtime.infrastructure.database import get_database_adapter

        graph_ops = GraphOps()
        manager = CapabilityManager(target_dir, graph_ops)
        manager.initialize()

        # For scheduled triggers (cron.*), discover modules and run checks for each
        if trigger_type.startswith("cron."):
            adapter = get_database_adapter()
            # Get all module/space IDs from graph
            modules_result = adapter.query("""
                MATCH (s:Space)
                WHERE s.id IS NOT NULL
                RETURN s.id
                LIMIT 50
            """)
            module_ids = [r[0] for r in modules_result] if modules_result else ["runtime"]

            total_created = 0
            for module_id in module_ids:
                result = manager.fire_trigger(
                    trigger_type,
                    payload={"module_id": module_id, "modules": module_ids},
                    create_tasks=True
                )
                total_created += result.get("tasks_created", 0)
            return total_created
        else:
            result = manager.fire_trigger(trigger_type, create_tasks=True)
            return result.get("tasks_created", 0)
    except Exception as e:
        print(f"Trigger failed: {e}")
        return 0


def _get_pending_task_count() -> int:
    """Get count of pending tasks."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        result = adapter.query("""
            MATCH (t:Narrative {type: 'task_run', status: 'pending'})
            RETURN count(t)
        """)
        return result[0][0] if result else 0
    except Exception:
        return 0


def run_swarm(num_agents: int, log_file: Optional[Path] = None, background: bool = False):
    """Start N agents in parallel."""
    _ensure_dirs()
    target_dir = Path.cwd()

    # First, assign pending tasks to agents using physics scoring
    try:
        from runtime.task_assignment import startup_assign
        assigned, skipped = startup_assign()
        if assigned > 0:
            print(f"Assigned {assigned} tasks to agents")
    except Exception as e:
        print(f"Task assignment: {e}")

    # If no pending tasks, try to generate some via derive-tasks
    pending = _get_pending_task_count()
    if pending == 0:
        print("No pending tasks - firing derive-tasks...")
        created = _fire_capability_trigger("cron.daily", target_dir)
        if created > 0:
            print(f"Created {created} new tasks")
            # Re-assign
            try:
                from runtime.task_assignment import startup_assign
                startup_assign()
            except Exception:
                pass

    # Get agents that have claimed tasks, ordered by weight × energy (best first)
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        result = adapter.query("""
            MATCH (t:Narrative {type: 'task_run'})-[:LINK {verb: 'claimed_by'}]->(a:Actor)
            WHERE t.status IN ['claimed', 'pending']
            RETURN DISTINCT a.id, COALESCE(a.weight, 1.0) * COALESCE(a.energy, 1.0) AS score
            ORDER BY score DESC
        """)
        agents = [r[0] for r in result] if result else []
    except Exception:
        agents = []

    if not agents:
        print("No agents have claimed tasks")
        return

    # Limit to requested number
    agents = agents[:num_agents]
    print(f"Starting {len(agents)} agents: {', '.join(a.replace('AGENT_', '') for a in agents)}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if background:
        # Background mode - spawn and exit
        pids = {}
        for agent_id in agents:
            agent_name = agent_id.replace("AGENT_", "").lower()
            agent_log = log_file or (LOG_DIR / f"{agent_name}_{timestamp}.log")

            pid = _spawn_agent_background(agent_id, agent_log, target_dir)
            if pid:
                pids[agent_id] = {"pid": pid, "log": str(agent_log), "started": timestamp}
                print(f"  ✓ {agent_id} (pid={pid})")

        _save_pids(pids)
        print(f"\nSwarm started in background. Logs in {LOG_DIR}/")
        print("Use 'mind swarm --status' to check progress")
        print("Use 'mind swarm --logs' to tail logs")
    else:
        # Foreground mode - run agents in threads, stream moments from graph
        print()  # Blank line before agent output

        # Track which moments we've seen
        seen_moments = set()
        seen_claims = set()
        stop_streaming = threading.Event()

        def stream_new_moments():
            """Poll graph for new moments and display them."""
            try:
                from runtime.infrastructure.database import get_database_adapter
                adapter = get_database_adapter()
                last_ts = int(time.time()) - 5  # Start from 5 seconds ago (seconds, not ms)

                while not stop_streaming.is_set():
                    try:
                        # Check for newly claimed tasks (claimed_by: task -> agent)
                        claims = adapter.query("""
                            MATCH (t:Narrative {type: 'task_run'})-[r:LINK {verb: 'claimed_by'}]->(a:Actor)
                            WHERE t.status IN ['claimed', 'running']
                            RETURN a.id, t.id, t.synthesis, t.status
                        """)
                        for claim in claims:
                            actor_id, task_id, synth, status = claim
                            key = f"{actor_id}:{task_id}"
                            if key not in seen_claims:
                                seen_claims.add(key)
                                agent_name = (actor_id or "?").replace("AGENT_", "")
                                color = _get_agent_color(actor_id or "?")
                                # Show synthesis + task ID suffix for uniqueness
                                synth_short = (synth or "")[:40]
                                task_suffix = task_id.split(":")[-1][:8] if task_id else ""
                                print(f"{color}{Colors.BOLD}[{agent_name}]{Colors.RESET} {Colors.INFO}▶ assigned:{Colors.RESET} {synth_short} [{task_suffix}]")

                        # Get moments with actor and task info
                        result = adapter.query("""
                            MATCH (m:Moment)
                            WHERE m.created_at_s > $last_ts
                            OPTIONAL MATCH (a:Actor)-[:LINK {verb: 'creates'}]->(m)
                            OPTIONAL MATCH (m)-[:LINK]->(t:Narrative {type: 'task_run'})
                            RETURN m.id, m.created_at_s, a.id, m.synthesis, m.type,
                                   t.synthesis, t.status
                            ORDER BY m.created_at_s ASC
                            LIMIT 20
                        """, {"last_ts": last_ts})

                        for r in result:
                            moment_id, ts, actor_id, synthesis, moment_type, task_synth, task_status = r
                            if moment_id and moment_id not in seen_moments:
                                seen_moments.add(moment_id)
                                last_ts = max(last_ts, ts or 0)

                                # Format agent name
                                agent_name = (actor_id or "?").replace("AGENT_", "").replace("actor:", "")
                                color = _get_agent_color(actor_id or "?")

                                # Format task
                                task_name = (task_synth or "")[:40]

                                # Format status with color
                                status = task_status or moment_type or "active"
                                if status in ["completed", "COMPLETION"]:
                                    status_color = Colors.SUCCESS
                                    status_icon = "✓"
                                elif status in ["failed", "error"]:
                                    status_color = Colors.ERROR
                                    status_icon = "✗"
                                elif status in ["running", "CONVERSATION"]:
                                    status_color = Colors.INFO
                                    status_icon = "→"
                                else:
                                    status_color = Colors.DIM
                                    status_icon = "•"

                                # Format synthesis (moment's own synthesis)
                                synth = (synthesis or "")[:70]

                                # Single line: [Agent] ✓ status | task | synthesis
                                parts = [f"{color}{Colors.BOLD}[{agent_name}]{Colors.RESET}"]
                                parts.append(f"{status_color}{status_icon} {status}{Colors.RESET}")
                                if task_name:
                                    parts.append(f"{Colors.WARNING}{task_name}{Colors.RESET}")
                                if synth:
                                    parts.append(synth)

                                print(" | ".join(parts))

                    except Exception:
                        pass  # Ignore query errors during streaming

                    time.sleep(0.5)  # Poll every 500ms

            except Exception:
                pass  # Ignore setup errors

        # Track subprocess PIDs for cleanup
        agent_procs = []

        def run_agent_subprocess(agent_id: str):
            agent_name = agent_id.replace("AGENT_", "").lower()
            agent_log = log_file or (LOG_DIR / f"{agent_name}_{timestamp}.log")
            script = _build_agent_script(agent_id, agent_log, target_dir)
            proc = subprocess.Popen(
                [sys.executable, "-c", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            agent_procs.append(proc)
            proc.wait()

        def cleanup_on_interrupt():
            """Kill agents and reset running tasks to claimed."""
            print(f"\n{Colors.WARNING}Interrupted - cleaning up...{Colors.RESET}")

            # Kill all agent subprocesses
            for proc in agent_procs:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass

            # Reset running tasks back to claimed
            try:
                from runtime.infrastructure.database import get_database_adapter
                db = get_database_adapter()
                db.execute("""
                    MATCH (t:Narrative {type: 'task_run', status: 'running'})
                    SET t.status = 'claimed'
                """)
                print(f"{Colors.INFO}Reset running tasks to claimed{Colors.RESET}")
            except Exception as e:
                print(f"Failed to reset tasks: {e}")

        # Start moment streamer
        moment_thread = threading.Thread(target=stream_new_moments, daemon=True)
        moment_thread.start()

        # Start agent threads (using subprocesses for clean termination)
        agent_threads = []
        try:
            for agent_id in agents:
                t = threading.Thread(target=run_agent_subprocess, args=(agent_id,))
                t.start()
                agent_threads.append(t)

            # Wait for all agents to complete
            for t in agent_threads:
                t.join()

        except KeyboardInterrupt:
            stop_streaming.set()
            cleanup_on_interrupt()
            return

        # Stop moment streaming
        stop_streaming.set()
        time.sleep(1)  # Give moment thread time to show final moments

        print(f"\n{Colors.SUCCESS}Swarm complete.{Colors.RESET} Logs saved to {LOG_DIR}/")


def show_status():
    """Show status of running agents."""
    pids = _load_pids()

    if not pids:
        print("No swarm running")
        return

    print("Swarm Status:\n")

    running = 0
    for agent_id, info in pids.items():
        pid = info["pid"]
        status = "running" if _is_running(pid) else "stopped"
        if status == "running":
            running += 1
        print(f"  {agent_id}: {status} (pid={pid})")

    print(f"\n{running}/{len(pids)} agents running")

    # Show recent moments
    print("\nRecent moments:")
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()
        result = adapter.query("""
            MATCH (m:Moment)
            RETURN m.id, substring(COALESCE(m.synthesis, m.name, ''), 0, 50)
            ORDER BY m.created_at_s DESC
            LIMIT 5
        """)
        for r in result:
            print(f"  {r[0][:30]:30} | {r[1]}")
    except Exception as e:
        print(f"  (query failed: {e})")


def stop_swarm():
    """Stop all running agents."""
    pids = _load_pids()

    if not pids:
        print("No swarm running")
        return

    stopped = 0
    for agent_id, info in pids.items():
        pid = info["pid"]
        if _is_running(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                stopped += 1
                print(f"  Stopped {agent_id} (pid={pid})")
            except Exception as e:
                print(f"  Failed to stop {agent_id}: {e}")

    # Clear PID file
    if PID_FILE.exists():
        PID_FILE.unlink()

    print(f"\nStopped {stopped} agents")


def stream_moments(follow: bool = True):
    """Stream moments to console."""
    try:
        from runtime.infrastructure.database import get_database_adapter
        adapter = get_database_adapter()

        last_ts = 0
        print("Streaming moments (Ctrl+C to stop)...\n")

        while True:
            result = adapter.query("""
                MATCH (m:Moment)
                WHERE m.created_at_s > $last_ts
                OPTIONAL MATCH (a:Actor)-[:LINK {verb: 'creates'}]->(m)
                RETURN m.id, m.created_at_s, a.id,
                       substring(COALESCE(m.synthesis, m.name, ''), 0, 60)
                ORDER BY m.created_at_s ASC
                LIMIT 20
            """, {"last_ts": last_ts})

            for r in result:
                moment_id, ts, actor, synth = r
                last_ts = max(last_ts, ts or 0)
                actor_short = (actor or "?").replace("AGENT_", "").replace("actor:", "")[:10]
                print(f"[{actor_short:10}] {synth}")

            if not follow:
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped")
    except Exception as e:
        print(f"Error: {e}")


def tail_logs(lines: int = 20):
    """Tail recent log entries."""
    _ensure_dirs()

    log_files = sorted(LOG_DIR.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)

    if not log_files:
        print("No log files found")
        return

    print(f"Recent logs ({len(log_files)} files):\n")

    # Combine and sort by timestamp
    all_lines = []
    for log_file in log_files[:5]:  # Last 5 log files
        try:
            with open(log_file) as f:
                for line in f.readlines()[-lines:]:
                    all_lines.append(line.strip())
        except Exception:
            pass

    # Print last N lines
    for line in all_lines[-lines:]:
        print(line)


def run(
    agents: int = 0,
    status: bool = False,
    stop: bool = False,
    stream: bool = False,
    logs: bool = False,
    log_file: str = None,
    background: bool = False,
):
    """
    Run multiple agents in parallel.

    Args:
        agents: Number of agents to spawn
        status: Show swarm status
        stop: Stop all agents
        stream: Stream moments live
        logs: Tail log files
        log_file: Custom log file path
        background: Run in background (default: foreground)
    """
    if status:
        show_status()
    elif stop:
        stop_swarm()
    elif stream:
        stream_moments()
    elif logs:
        tail_logs()
    elif agents > 0:
        log_path = Path(log_file) if log_file else None
        run_swarm(agents, log_path, background=background)
    else:
        print("Usage:")
        print("  mind swarm --agents N    Start N agents (foreground)")
        print("  mind swarm --agents N --background   Start in background")
        print("  mind swarm --status      Show agent status")
        print("  mind swarm --stream      Stream moments live")
        print("  mind swarm --logs        Tail log files")
        print("  mind swarm --stop        Stop all agents")
