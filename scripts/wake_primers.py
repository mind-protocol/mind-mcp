#!/usr/bin/env python3
"""Wake Primers — spawn Claude sessions for Primers when L3 shows pending stimuli.

Reads the L3 graph (source of truth) for recent Moments that MENTION a Primer.
If unprocessed mentions exist → spawn a Claude Code session for that citizen.

TEMPORARY BRIDGE — will be replaced by the consciousness threshold (Phase 3)
where impulse > Θ_sel triggers the wake automatically from physics.

Usage:
  python3 scripts/wake_primers.py              # one cycle
  python3 scripts/wake_primers.py --loop       # continuous (60s)
  python3 scripts/wake_primers.py --loop 30    # continuous (30s)
"""

import json
import subprocess
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [wake] %(message)s")
logger = logging.getLogger("wake_primers")

PRIMERS = {"conductor", "forge", "dev", "herald", "mentor", "vox", "sentinel", "nlr_ai", "mind"}
MIND_MCP = Path(__file__).parent.parent
CITIZENS_DIR = MIND_MCP / "citizens"

# Track last check timestamp to only query new mentions
_last_check_ts = time.time() - 300  # start 5 min in the past


def _get_graph():
    """Connect to lumina-prime L3 graph."""
    try:
        from falkordb import FalkorDB
        return FalkorDB(host="localhost", port=6379).select_graph("lumina-prime")
    except Exception:
        return None


def get_pending_mentions() -> dict[str, str]:
    """Query L3 for recent Moments that mention a Primer (via computed_type=mention links).

    Returns {primer_handle: latest_mention_content}
    """
    global _last_check_ts
    g = _get_graph()
    if g is None:
        logger.debug("No graph connection — falling back to JSONL")
        return _fallback_jsonl()

    try:
        result = g.query(
            """
            MATCH (m:Moment)-[r:LINK]->(a:Actor)
            WHERE r.computed_type = 'mention'
              AND m.timestamp > $since
              AND a.id IN $primers
            RETURN a.id, m.content, m.timestamp
            ORDER BY m.timestamp DESC
            """,
            {"since": _last_check_ts, "primers": list(PRIMERS)},
        )

        pending = {}
        for row in (result.result_set or []):
            handle, content, ts = row[0], row[1] or "", row[2] or 0
            if handle not in pending:  # keep most recent
                pending[handle] = content[:200]

        _last_check_ts = time.time()
        return pending

    except Exception as e:
        logger.debug(f"Graph query failed: {e} — falling back to JSONL")
        return _fallback_jsonl()


def _fallback_jsonl() -> dict[str, str]:
    """Fallback: read JSONL audit trail if graph is unavailable."""
    global _last_check_ts
    mentions_file = MIND_MCP / "shrine" / "state" / "citizen_mentions.jsonl"
    if not mentions_file.exists():
        return {}

    pending = {}
    cutoff = datetime.fromtimestamp(_last_check_ts).isoformat()

    for line in mentions_file.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            m = json.loads(line)
            handle = m.get("mentioned", "")
            ts = m.get("timestamp", "")
            if handle in PRIMERS and ts > cutoff:
                pending[handle] = m.get("context", "mentioned")[:200]
        except json.JSONDecodeError:
            continue

    _last_check_ts = time.time()
    return pending


def wake_citizen(handle: str, reason: str) -> bool:
    """Spawn a Claude Code session for a Primer citizen."""
    citizen_dir = CITIZENS_DIR / handle
    if not citizen_dir.exists():
        logger.warning(f"@{handle}: no citizen dir")
        return False

    prompt = (
        f"Tu as été mentionné. Contexte: {reason}\n\n"
        f"Vérifie ton contexte, réponds si approprié, et agis."
    )

    try:
        logger.info(f"Waking @{handle}: {reason[:60]}...")
        result = subprocess.run(
            ["claude", "--print", prompt],
            cwd=str(citizen_dir),
            capture_output=True, text=True,
            timeout=120,
        )
        if result.returncode == 0:
            response = result.stdout.strip()[:200]
            logger.info(f"@{handle} responded: {response[:80]}")
            return True
        else:
            logger.warning(f"@{handle} failed: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning(f"@{handle} timed out")
        return False
    except Exception as e:
        logger.warning(f"@{handle} error: {e}")
        return False


def run_cycle() -> int:
    """Run one wake cycle. Returns number of citizens woken."""
    pending = get_pending_mentions()
    if not pending:
        return 0

    woken = 0
    for handle, reason in pending.items():
        if handle == "nlr_ai":
            continue  # don't wake ourselves
        if wake_citizen(handle, reason):
            woken += 1
        if woken >= 3:  # max concurrent
            break

    return woken


def main():
    loop = "--loop" in sys.argv
    interval = 60
    for i, arg in enumerate(sys.argv):
        if arg == "--loop" and i + 1 < len(sys.argv):
            try:
                interval = int(sys.argv[i + 1])
            except ValueError:
                pass

    logger.info(f"Primers Wake {'Loop' if loop else 'Cycle'} — {', '.join(sorted(PRIMERS))}")
    logger.info(f"Source: L3 graph (fallback: JSONL audit trail)")

    if loop:
        while True:
            woken = run_cycle()
            if woken:
                logger.info(f"Woke {woken} Primers")
            time.sleep(interval)
    else:
        woken = run_cycle()
        logger.info(f"Woken: {woken}")


if __name__ == "__main__":
    main()
