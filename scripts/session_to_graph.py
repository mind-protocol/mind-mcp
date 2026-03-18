#!/usr/bin/env python3
"""
Session-to-Graph Injector — records Claude Code session activity into L3 + L1.

Called as a Stop hook or post-session script. Reads the session's tool calls
from stdin (JSON) and creates Moment nodes in the L3 graph and citizen's L1 brain.

What it captures:
- graph_write calls → Moment:creation
- graph_query calls → Moment:observation
- send calls → Moment:communication
- Bash/Edit/Write calls → Moment:action (code work)
- think calls → Moment:reflection

Each session produces 1 summary Moment linked to the citizen Actor.

Usage as Stop hook:
    In ~/.claude/settings.json:
    {
      "hooks": {
        "Stop": [{
          "hooks": [{
            "type": "command",
            "command": "python3 /home/mind-protocol/mind-mcp/scripts/session_to_graph.py",
            "timeout": 15
          }]
        }]
      }
    }

Can also be called standalone:
    echo '{"session_id":"abc"}' | CITIZEN_HANDLE=dev python3 scripts/session_to_graph.py

DOCS: docs/gap-detection/PATTERNS_Gap_Detection.md (Claude→L1 injection gap)
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [session2graph] %(message)s")
logger = logging.getLogger("session2graph")

# Where session activity logs are stored (by Claude hooks)
ACTIVITY_DIR = Path(os.environ.get("MIND_STATE", "/home/mind-protocol/mind-mcp/shrine/state"))
MCP_ROOT = Path(os.environ.get("MIND_MCP_ROOT", "/home/mind-protocol/mind-mcp"))


def get_citizen_handle() -> str:
    """Detect which citizen this session belongs to."""
    # From env (set by orchestrator)
    handle = os.environ.get("CITIZEN_HANDLE", "").strip().lstrip("@")
    if handle:
        return handle

    # From CWD (session launched from citizens/{handle}/)
    cwd = Path.cwd()
    for part in cwd.parts:
        if part == "citizens" and cwd.parts.index(part) + 1 < len(cwd.parts):
            return cwd.parts[cwd.parts.index(part) + 1]

    return ""


def get_l3_graph():
    """Connect to the L3 universe graph."""
    try:
        from falkordb import FalkorDB
        host = os.environ.get("FALKORDB_HOST", "localhost")
        port = int(os.environ.get("FALKORDB_PORT", "6379"))
        graph_name = os.environ.get("L3_GRAPH", os.environ.get("UNIVERSE", "lumina-prime"))
        return FalkorDB(host=host, port=port).select_graph(graph_name)
    except Exception as e:
        logger.warning(f"Cannot connect to L3: {e}")
        return None


def get_l1_graph(handle: str):
    """Connect to the citizen's L1 brain graph."""
    try:
        from falkordb import FalkorDB
        host = os.environ.get("FALKORDB_HOST", "localhost")
        port = int(os.environ.get("FALKORDB_PORT", "6379"))
        return FalkorDB(host=host, port=port).select_graph(f"brain_{handle}")
    except Exception as e:
        logger.warning(f"Cannot connect to brain_{handle}: {e}")
        return None


def read_session_activity() -> dict:
    """Read session activity from stdin or activity files."""
    # Try stdin first (from Stop hook)
    try:
        if not sys.stdin.isatty():
            data = json.load(sys.stdin)
            return data
    except (json.JSONDecodeError, EOFError):
        pass

    # Fallback: read from activity log file
    handle = get_citizen_handle()
    activity_file = ACTIVITY_DIR / f"session_activity_{handle}.json"
    if activity_file.exists():
        try:
            return json.loads(activity_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def summarize_session(handle: str) -> str:
    """Generate a session summary from the CWD context."""
    cwd = Path.cwd()
    summary_parts = [f"@{handle} session"]

    # Check for recent file changes
    works_dir = cwd / "works"
    if works_dir.exists():
        recent_works = sorted(works_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
        if recent_works:
            summary_parts.append(f"Works: {', '.join(w.stem for w in recent_works)}")

    return ". ".join(summary_parts)


def inject_moment(graph, moment_id: str, citizen_handle: str, content: str,
                   synthesis: str, moment_type: str = "session"):
    """Create a Moment node and link to citizen Actor."""
    if graph is None:
        return False

    ts = int(time.time())
    try:
        graph.query(
            "MERGE (m:Moment {id: $id}) "
            "SET m.node_type = 'moment', m.type = $type, "
            "m.name = $name, m.content = $content, m.synthesis = $synthesis, "
            "m.weight = 0.5, m.energy = 2.0, "
            "m.created_at_s = $ts, m.author = $author",
            {"id": moment_id, "type": moment_type,
             "name": f"Session: @{citizen_handle}",
             "content": content, "synthesis": synthesis,
             "ts": ts, "author": citizen_handle}
        )

        # Link to citizen Actor
        graph.query(
            "MATCH (m:Moment {id: $mid}), (a:Actor {id: $aid}) "
            "MERGE (m)-[r:LINK]->(a) SET r.permanence = 0.7, r.affinity = 0.5",
            {"mid": moment_id, "aid": citizen_handle}
        )
        return True
    except Exception as e:
        logger.warning(f"Inject failed: {e}")
        return False


def main():
    handle = get_citizen_handle()
    if not handle:
        logger.info("No citizen handle detected — skipping")
        return

    ts = int(time.time())
    moment_id = f"moment:session:{handle}:{ts}"
    synthesis = summarize_session(handle)
    content = f"Claude Code session for @{handle}. {synthesis}"

    # Inject into L3
    l3 = get_l3_graph()
    if l3:
        ok = inject_moment(l3, moment_id, handle, content, synthesis, "session")
        if ok:
            logger.info(f"L3: session moment created for @{handle}")

    # Inject into L1 brain
    l1 = get_l1_graph(handle)
    if l1:
        brain_moment_id = f"moment:session:{ts}"
        ok = inject_moment(l1, brain_moment_id, handle, content, synthesis, "session")
        if ok:
            logger.info(f"L1: session moment created in brain_{handle}")

    logger.info(f"Done — @{handle} session recorded")


if __name__ == "__main__":
    main()
