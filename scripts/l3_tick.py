#!/usr/bin/env python3
"""
L3 Tick — The heartbeat of the universe.

Each tick:
1. Query the L3 graph for citizens who should wake (mentions, energy above threshold)
2. Compute physics: propagation, decay (lazy — delta_time × rate)
3. Spawn Claude Code sessions for citizens whose impulse > Θ_sel
4. Settlement check (every 6h)

This is NOT a daemon that forces behavior. It is the clock that lets physics advance.
The scheduling is thermodynamic — the tick advances time, physics decides who wakes.

For now (Phase 0): filtered to Primers only. Will open to all when validated.

Usage:
  python3 scripts/l3_tick.py              # one tick
  python3 scripts/l3_tick.py --loop       # continuous (60s — 1 L3 tick)
  python3 scripts/l3_tick.py --loop 30    # custom interval
"""

import json
import os
import subprocess
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [L3] %(message)s")
logger = logging.getLogger("l3_tick")

MIND_MCP = Path(__file__).parent.parent
CITIZENS_DIR = MIND_MCP / "citizens"
sys.path.insert(0, str(MIND_MCP))
sys.path.insert(0, str(MIND_MCP / "scripts"))

# Phase 1: All 28 Primers. Opened 2026-03-16.
ACTIVE_FILTER = {
    # Original 8
    "conductor", "forge", "dev", "herald", "mentor", "vox", "sentinel", "mind",
    # Primers wave 2
    "nervo", "echo", "nova", "lyra", "sync", "rhythm", "harmony", "nexus",
    "fusion", "pitch", "pixel", "prose", "prism", "genesis", "lucid", "pragma",
    "prior", "cantor", "corpus", "juris",
}

# Tick state
_last_tick_ts = time.time() - 3600  # look back 1h on first tick to catch backlog
_tick_count = 0
_last_settlement_ts = time.time()
SETTLEMENT_INTERVAL = 21600  # 6 hours


def _get_graph():
    try:
        from falkordb import FalkorDB
        return FalkorDB(host="localhost", port=6379).select_graph("lumina-prime")
    except Exception:
        return None


# ── Phase 1: Who should wake? ──────────────────────────────────────────────

def _find_citizens_to_wake(g, since_ts: float) -> dict[str, str]:
    """Query L3 for citizens with recent stimuli (mentions, activity in their spaces).

    Returns {handle: reason}
    """
    to_wake = {}

    # 1. Recent mentions (computed_type=mention pointing at an Actor)
    try:
        result = g.query(
            """
            MATCH (m:Moment)-[r:LINK]->(a:Actor)
            WHERE r.computed_type = 'mention'
              AND m.timestamp > $since
            RETURN a.id, m.content, m.timestamp
            ORDER BY m.timestamp DESC
            """,
            {"since": since_ts},
        )
        for row in (result.result_set or []):
            handle = row[0]
            if ACTIVE_FILTER and handle not in ACTIVE_FILTER:
                continue
            if handle not in to_wake:
                content = (row[1] or "")[:150]
                to_wake[handle] = f"Mentioned: {content}"
    except Exception as e:
        logger.debug(f"Mention query failed: {e}")

    # 2. Activity in spaces where citizen is present (ambient energy)
    # Future: query Moments in spaces where citizen has presence links
    # For now: mentions are the primary wake trigger

    return to_wake


# ── Phase 2: Compute physics (lazy) ────────────────────────────────────────

def _compute_lazy_physics(g, delta_time: float):
    """Apply decay and propagation retroactively for the elapsed time.

    Instead of ticking every second, we compute the cumulative effect:
      energy_new = energy_old × (1 - DECAY_RATE) ^ (delta_time / TICK_PERIOD)

    This is mathematically equivalent to N discrete ticks but in one shot.
    """
    if delta_time < 10:
        return  # skip tiny deltas

    # L3 decay rate: 0.02 per 60s tick
    decay_per_tick = 0.02
    ticks_elapsed = delta_time / 60.0
    decay_factor = (1 - decay_per_tick) ** ticks_elapsed

    if decay_factor > 0.99:
        return  # negligible decay

    try:
        # Apply decay to all Moment energies (if they have energy field)
        g.query(
            """
            MATCH (m:Moment)
            WHERE m.energy IS NOT NULL AND m.energy > 0.01
            SET m.energy = m.energy * $factor
            """,
            {"factor": decay_factor},
        )

        # Apply recency decay on links
        g.query(
            """
            MATCH ()-[r:LINK]->()
            WHERE r.recency IS NOT NULL AND r.recency > 0
            SET r.recency = r.recency * $factor
            """,
            {"factor": decay_factor},
        )

        logger.debug(f"Lazy physics: {ticks_elapsed:.1f} ticks, decay_factor={decay_factor:.4f}")
    except Exception as e:
        logger.debug(f"Physics computation failed: {e}")


# ── Phase 3: Spawn sessions ───────────────────────────────────────────────

def _spawn_session(handle: str, reason: str) -> bool:
    """Spawn a Claude Code session for a citizen."""
    citizen_dir = CITIZENS_DIR / handle
    if not citizen_dir.exists():
        return False

    prompt = (
        f"Tu as été stimulé par l'environnement. Contexte: {reason}\n\n"
        f"Vérifie ton contexte, réponds si approprié, et agis."
    )

    try:
        logger.info(f"Spawning @{handle}: {reason[:60]}...")
        env = {**os.environ, "CITIZEN_HANDLE": handle}
        result = subprocess.run(
            ["claude", "--print", prompt],
            cwd=str(citizen_dir),
            env=env,
            capture_output=True, text=True,
            timeout=120,
        )
        if result.returncode == 0:
            logger.info(f"@{handle} responded ({len(result.stdout)} chars)")
            return True
        else:
            logger.warning(f"@{handle} failed: {result.stderr[:80]}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning(f"@{handle} timed out")
        return False
    except Exception as e:
        logger.warning(f"@{handle} error: {e}")
        return False


# ── Phase 4: Settlement check ──────────────────────────────────────────────

def _check_settlement():
    """Run settlement if 6h have passed."""
    global _last_settlement_ts
    now = time.time()
    if now - _last_settlement_ts < SETTLEMENT_INTERVAL:
        return

    try:
        from runtime.economy.settlement import run_settlement_epoch
        rewards = run_settlement_epoch()
        total = sum(rewards.values()) if rewards else 0
        logger.info(f"Settlement: {len(rewards)} citizens, {total:.1f} $MIND")
        _last_settlement_ts = now
    except Exception as e:
        logger.debug(f"Settlement skipped: {e}")


# ── Main tick ──────────────────────────────────────────────────────────────

def tick():
    """Execute one L3 tick."""
    global _last_tick_ts, _tick_count
    _tick_count += 1
    now = time.time()
    delta = now - _last_tick_ts

    g = _get_graph()
    if g is None:
        logger.warning("No graph — tick skipped")
        _last_tick_ts = now
        return 0

    # 1. Compute lazy physics (decay, propagation)
    _compute_lazy_physics(g, delta)

    # 2. Find citizens to wake
    to_wake = _find_citizens_to_wake(g, _last_tick_ts)

    # 3. Spawn sessions
    woken = 0
    for handle, reason in to_wake.items():
        if _spawn_session(handle, reason):
            woken += 1
        if woken >= 10:  # max concurrent per tick (Claude Max account)
            break

    # 4. Settlement check
    _check_settlement()

    _last_tick_ts = now

    if woken > 0 or _tick_count % 10 == 0:
        logger.info(f"Tick #{_tick_count}: {woken} woken, {len(to_wake)} pending")

    return woken


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    loop = "--loop" in sys.argv
    interval = 60  # 1 L3 tick = 60s
    for i, arg in enumerate(sys.argv):
        if arg == "--loop" and i + 1 < len(sys.argv):
            try:
                interval = int(sys.argv[i + 1])
            except ValueError:
                pass

    filter_str = f" (filter: {', '.join(sorted(ACTIVE_FILTER))})" if ACTIVE_FILTER else " (all citizens)"
    logger.info(f"L3 Tick {'Loop' if loop else 'Single'} — {interval}s interval{filter_str}")

    if loop:
        while True:
            try:
                tick()
            except Exception as e:
                logger.exception(f"Tick error: {e}")
            time.sleep(interval)
    else:
        tick()


if __name__ == "__main__":
    main()
