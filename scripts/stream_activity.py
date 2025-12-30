#!/usr/bin/env python3
"""Stream real-time activity from files + database."""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add runtime to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.infrastructure.database import get_database_adapter


async def watch_sessions(target_dir: Path):
    """Watch for session file changes."""
    actors_dir = target_dir / ".mind" / "actors"
    known_sessions = {}

    while True:
        current = {}
        if actors_dir.exists():
            for agent_dir in actors_dir.iterdir():
                session_file = agent_dir / ".sessionId"
                if session_file.exists():
                    current[agent_dir.name] = session_file.read_text().strip()

        # Detect changes
        for name, sid in current.items():
            if name not in known_sessions:
                print(f"\033[32m▶ AGENT START\033[0m {name} (session: {sid[:8]}...)")

        for name in known_sessions:
            if name not in current:
                print(f"\033[31m■ AGENT STOP\033[0m  {name}")

        known_sessions = current
        await asyncio.sleep(1)


async def watch_moments():
    """Poll for new moments."""
    adapter = get_database_adapter()
    last_seen = set()

    while True:
        try:
            result = adapter.query("""
                MATCH (m:Moment)
                RETURN m.id, m.type, m.synthesis
                ORDER BY m.timestamp DESC
                LIMIT 20
            """)

            for row in result:
                mid, mtype, synthesis = row[0], row[1], row[2] or ""
                if mid not in last_seen:
                    last_seen.add(mid)
                    # Truncate synthesis
                    synth_short = synthesis[:60] + "..." if len(synthesis) > 60 else synthesis
                    synth_short = synth_short.replace("\n", " ")
                    print(f"\033[34m◆ MOMENT\033[0m {mtype:12} {mid}")
                    if synth_short:
                        print(f"          └─ {synth_short}")
        except Exception as e:
            print(f"\033[33m⚠ DB error: {e}\033[0m")

        await asyncio.sleep(2)


async def watch_actor_status():
    """Poll for actor status changes."""
    adapter = get_database_adapter()
    last_status = {}

    while True:
        try:
            result = adapter.query("""
                MATCH (a:Actor)
                WHERE a.type = 'AGENT'
                RETURN a.id, a.status, a.cwd
            """)

            for row in result:
                aid, status, cwd = row[0], row[1], row[2]
                key = (aid, status, cwd)
                if aid not in last_status or last_status[aid] != key:
                    if aid in last_status:
                        print(f"\033[35m↻ STATUS\033[0m {aid}: {status} @ {cwd or '.'}")
                    last_status[aid] = key
        except Exception:
            pass

        await asyncio.sleep(2)


async def main():
    target_dir = Path(".")

    print("\033[1m=== Mind Activity Stream ===\033[0m")
    print(f"Watching: {target_dir.absolute()}")
    print("Press Ctrl+C to stop\n")

    await asyncio.gather(
        watch_sessions(target_dir),
        watch_moments(),
        watch_actor_status(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
