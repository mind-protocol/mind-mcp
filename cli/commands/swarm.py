"""
mind swarm - Run multiple agents in parallel with live streaming.

Usage:
    mind swarm --agents 3              # Run 3 agents in parallel
    mind swarm --agents 5 --log swarm.log
    mind swarm --status                # Show running agents
    mind swarm --stop                  # Stop all agents
"""

import os
import sys
import json
import time
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

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


def _spawn_agent_process(agent_id: str, log_file: Path) -> Optional[int]:
    """Spawn a background agent process. Returns PID."""
    script = f'''
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [{agent_id}] %(message)s',
    handlers=[
        logging.FileHandler("{log_file}"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger()

try:
    from runtime.infrastructure.database import get_database_adapter
    from runtime.task_assignment import assign_pending_tasks
    from runtime.agents import run_for_task

    adapter = get_database_adapter()
    logger.info("Agent started")

    # Find a task claimed by this agent
    result = adapter.query("""
        MATCH (t:Narrative {{type: 'task_run', status: 'claimed'}})-[:LINK {{verb: 'claimed_by'}}]->(a:Actor {{id: $agent_id}})
        RETURN t.id, t.synthesis
        LIMIT 1
    """, {{"agent_id": "{agent_id}"}})

    if result and result[0]:
        task_id, synthesis = result[0]
        logger.info(f"Working on: {{task_id}}")

        # Mark as running
        adapter.execute(
            "MATCH (t:Narrative {{id: $id}}) SET t.status = 'running'",
            {{"id": task_id}}
        )

        # Run the agent work
        try:
            run_for_task(task_id, "{agent_id}")
            adapter.execute(
                "MATCH (t:Narrative {{id: $id}}) SET t.status = 'completed'",
                {{"id": task_id}}
            )
            logger.info(f"Completed: {{task_id}}")
        except Exception as e:
            adapter.execute(
                "MATCH (t:Narrative {{id: $id}}) SET t.status = 'failed', t.error = $error",
                {{"id": task_id, "error": str(e)}}
            )
            logger.error(f"Failed: {{task_id}} - {{e}}")
    else:
        logger.info("No tasks assigned, exiting")

except Exception as e:
    logger.error(f"Agent error: {{e}}")
'''

    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
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


def run_swarm(num_agents: int, log_file: Optional[Path] = None):
    """Start N agents in parallel."""
    _ensure_dirs()

    # Get available agents
    agents = _get_available_agents()
    if not agents:
        print("No available agents found")
        return

    # Limit to requested number
    agents = agents[:num_agents]
    print(f"Starting {len(agents)} agents...")

    # First, assign pending tasks
    try:
        from runtime.task_assignment import startup_assign
        assigned, skipped = startup_assign()
        if assigned > 0:
            print(f"Assigned {assigned} tasks to agents")
    except Exception as e:
        print(f"Task assignment: {e}")

    # Spawn agents
    pids = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for agent_id in agents:
        agent_name = agent_id.replace("AGENT_", "").lower()
        agent_log = log_file or (LOG_DIR / f"{agent_name}_{timestamp}.log")

        pid = _spawn_agent_process(agent_id, agent_log)
        if pid:
            pids[agent_id] = {"pid": pid, "log": str(agent_log), "started": timestamp}
            print(f"  ✓ {agent_id} (pid={pid})")

    _save_pids(pids)
    print(f"\nSwarm started. Logs in {LOG_DIR}/")
    print("Use 'mind swarm --status' to check progress")
    print("Use 'mind swarm --stream' to watch moments")


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
            ORDER BY m.timestamp DESC
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
                WHERE m.timestamp > $last_ts
                RETURN m.id, m.timestamp, m.actor_id,
                       substring(COALESCE(m.synthesis, m.name, ''), 0, 60)
                ORDER BY m.timestamp ASC
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
        run_swarm(agents, log_path)
    else:
        print("Usage:")
        print("  mind swarm --agents N    Start N agents")
        print("  mind swarm --status      Show agent status")
        print("  mind swarm --stream      Stream moments live")
        print("  mind swarm --logs        Tail log files")
        print("  mind swarm --stop        Stop all agents")
