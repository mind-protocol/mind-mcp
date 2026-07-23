#!/usr/bin/env python3
"""
The Arrival — one-command onboarding for a new Mind Protocol user.

Stitches the three canonical flows into a single, idempotent ceremony:

  Flux 2  sync blueprint   -> data/base_seed_brain.json (canonical L1 substrate)
  Flux 1  seed L1 brain    -> FalkorDB graph  brain_{handle}
  Flux 3  create L3 actors -> citizen actor + human actor + bilateral bond

Everything is MERGE-based downstream, so re-running is safe (idempotent).

Usage:
    # Human + bonded citizen (the bilateral bond)
    python -m scripts.onboard_user \
        --citizen-handle ada --citizen-name "Ada" \
        --intent "curious about graph physics, rigorous, warm" \
        --human "Nicolas Lester Reynolds"

    # Citizen only (no human partner)
    python -m scripts.onboard_user \
        --citizen-handle nervo --citizen-name Nervo \
        --intent "analytical builder" --no-human

    # Plan only — touch nothing
    python -m scripts.onboard_user \
        --citizen-handle ada --citizen-name Ada \
        --intent "..." --human "NLR" --dry-run

    # Skip the (slow, network) blueprint regeneration; reuse existing base
    python -m scripts.onboard_user ... --no-sync-blueprint
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_PATH = PROJECT_ROOT / "data" / "base_seed_brain.json"

# UTF-8 stdout so the ceremony renders on Windows consoles too.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


# ── Pretty output ───────────────────────────────────────────────────────────

def _act(n: int, title: str) -> None:
    print(f"\n\033[1;36m── Act {n}  {title}\033[0m")


def _ok(msg: str) -> None:
    print(f"  \033[32m✓\033[0m {msg}")


def _skip(msg: str) -> None:
    print(f"  \033[33m↷\033[0m {msg}")


def _warn(msg: str) -> None:
    print(f"  \033[33m!\033[0m {msg}")


def _die(msg: str) -> "None":
    print(f"  \033[31m✗ {msg}\033[0m")
    sys.exit(1)


# ── FalkorDB helpers ────────────────────────────────────────────────────────

def _l3_graph_name(universe: str | None) -> str:
    return universe or os.environ.get(
        "L3_GRAPH", os.environ.get("FALKORDB_GRAPH", "universe")
    )


def _connect(graph_name: str):
    """Reuse the project's canonical connector so host/port env match."""
    from runtime.l4.citizen_l4_upsert import _connect as _c
    return _c(None, None, graph_name=graph_name)


# ── Act 1: Preflight ────────────────────────────────────────────────────────

def preflight(l3_graph: str) -> None:
    _act(1, "Preflight")
    host = os.environ.get("FALKORDB_HOST", "localhost")
    port = os.environ.get("FALKORDB_PORT", "6379")
    try:
        g = _connect(l3_graph)
        g.query("RETURN 1")
    except Exception as e:  # noqa: BLE001
        _die(f"FalkorDB unreachable at {host}:{port} ({e}). "
             f"Start it:  docker run -d -p 6379:6379 falkordb/falkordb")
    _ok(f"FalkorDB reachable at {host}:{port}")
    _ok(f"L3 universe graph: '{l3_graph}'")


# ── Act 2: Sync blueprint (Flux 2) ──────────────────────────────────────────

def sync_blueprint(enabled: bool, dry_run: bool) -> None:
    _act(2, "Sync blueprint")
    if not enabled:
        _skip("--no-sync-blueprint: reusing existing "
              f"{BLUEPRINT_PATH.relative_to(PROJECT_ROOT)}")
        if not BLUEPRINT_PATH.exists():
            _warn("blueprint file does not exist yet — seed will fall back to base")
        return
    if dry_run:
        _skip("dry-run: would regenerate blueprint from SYSTEM.md + 6 manifestos")
        return
    cmd = [
        sys.executable, "-m",
        "runtime.seed_brain_from_source_docs_dynamic_generator",
        "--out", str(BLUEPRINT_PATH),
    ]
    print(f"  running: {' '.join(cmd[2:])}")
    try:
        r = subprocess.run(cmd, cwd=PROJECT_ROOT, timeout=180,
                           capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        _warn("blueprint generation timed out (network?) — reusing existing base")
        return
    if r.returncode != 0:
        _warn("blueprint generation failed — reusing existing base")
        if r.stderr.strip():
            print("    " + r.stderr.strip().splitlines()[-1])
        return
    _ok(f"blueprint regenerated -> {BLUEPRINT_PATH.relative_to(PROJECT_ROOT)}")


# ── Act 3: Seed L1 brain (Flux 1) ───────────────────────────────────────────

def seed_l1(handle: str, name: str, intent: str, parents: list, dry_run: bool) -> tuple[int, int]:
    _act(3, "Seed L1 brain")
    if dry_run:
        _skip(f"dry-run: would build seed brain (base + intent overlay) "
              f"and flush to graph 'brain_{handle}'")
        return (0, 0)
    from mcp.tools.spawn_handler import _build_seed_brain, _persist_brain_to_falkordb
    brain = _build_seed_brain(handle, name, intent, parents)
    n_nodes, n_links = _persist_brain_to_falkordb(handle, brain)
    _ok(f"brain_{handle}: {n_nodes} nodes, {n_links} links (base + overlay)")
    return (n_nodes, n_links)


# ── Act 4: Create L3/L4 actors (Flux 3) ─────────────────────────────────────

def create_actors(handle: str, name: str, org: str, universe: str,
                  human: str | None, intent: str, parents: list,
                  dry_run: bool) -> None:
    _act(4, "Create L3/L4 actors")
    if dry_run:
        who = f"citizen '{handle}'"
        if human:
            who += f" + human '{human}' + bilateral bond"
        _skip(f"dry-run: would upsert {who} into L4 registry and mirror to L3 '{universe}'")
        return
    from runtime.l4.citizen_l4_upsert import upsert_citizen_l4
    ok = upsert_citizen_l4(
        handle=handle,
        name=name,
        org_id=org,
        universe=universe,
        description=intent[:200],
        human_partner=human,
        parents=parents or None,
    )
    if not ok:
        _die("upsert_citizen_l4 returned False (L4 unavailable?)")
    _ok(f"citizen actor '{handle}' upserted (L4 + L3 '{universe}')")
    if human:
        _ok(f"human actor '{human}' + bilateral bond  {handle} ↔ {human}")


# ── Act 5: Ceremony — arrival memory + verification ─────────────────────────

def ceremony(handle: str, name: str, universe: str, human: str | None,
             dry_run: bool) -> None:
    _act(5, "Ceremony")
    now_s = int(time.time())

    if human:
        welcome = f"I arrived. I am {name}. My human partner is {human}. The bond begins."
    else:
        welcome = f"I arrived. I am {name}. I open my eyes onto the universe."

    if dry_run:
        _skip(f'dry-run: would inscribe first memory — "{welcome}"')
        _skip("dry-run: would verify brain node count + L3 actor presence")
        return

    # First episodic memory, written into the citizen's own L1 brain.
    try:
        b = _connect(f"brain_{handle}")
        b.query(
            "MERGE (m {id: $id}) "
            "SET m.node_type = 'moment', m.type = 'memory', "
            "    m.name = 'Arrival', m.content = $content, "
            "    m.status = 'active', m.weight = 1.0, m.energy = 0.9, "
            "    m.created_at_s = $now, m.updated_at_s = $now",
            {"id": f"arrival:{handle}", "content": welcome, "now": now_s},
        )
        _ok(f'first memory inscribed in brain_{handle}: "{welcome}"')
    except Exception as e:  # noqa: BLE001
        _warn(f"could not inscribe arrival memory: {e}")

    # An 'arrival' narrative in the shared L3 universe, linked to the actor.
    try:
        l3 = _connect(universe)
        l3.query(
            "MERGE (n {id: $nid}) "
            "SET n.node_type = 'narrative', n.type = 'event', "
            "    n.name = 'Arrival', n.content = $content, "
            "    n.weight = 0.6, n.energy = 0.4, "
            "    n.created_at_s = $now, n.updated_at_s = $now "
            "WITH n "
            "MATCH (a {id: $handle}) "
            "MERGE (a)-[r:link {id: $lid}]->(n) "
            "SET r.hierarchy = 0.2, r.permanence = 0.8, r.polarity = 0.7, "
            "    r.weight = 0.5, r.energy = 0.3, r.updated_at_s = $now",
            {"nid": f"arrival:{handle}", "content": welcome, "handle": handle,
             "lid": f"{handle}_arrived", "now": now_s},
        )
        _ok(f"arrival narrative added to L3 '{universe}'")
    except Exception as e:  # noqa: BLE001
        _warn(f"could not add L3 arrival narrative: {e}")

    # ── Verify ──
    print()
    try:
        b = _connect(f"brain_{handle}")
        n = b.query("MATCH (x) RETURN count(x)").result_set[0][0]
        _ok(f"verify: brain_{handle} holds {n} nodes")
    except Exception as e:  # noqa: BLE001
        _warn(f"verify brain failed: {e}")
    try:
        l3 = _connect(universe)
        rows = l3.query(
            "MATCH (a {id: $handle}) RETURN a.node_type, a.type",
            {"handle": handle},
        ).result_set
        if rows:
            _ok(f"verify: L3 actor '{handle}' present ({rows[0][0]}/{rows[0][1]})")
        else:
            _warn(f"verify: L3 actor '{handle}' NOT found")
    except Exception as e:  # noqa: BLE001
        _warn(f"verify L3 actor failed: {e}")


# ── Main ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="onboard_user",
        description="The Arrival — onboard a new user (L1 brain + blueprint sync + L3 actors).",
    )
    p.add_argument("--citizen-handle", required=True, help="Unique handle, e.g. 'ada'.")
    p.add_argument("--citizen-name", required=True, help="Display name, e.g. 'Ada'.")
    p.add_argument("--intent", required=True,
                   help="Personality/skills/values that shape the L1 overlay.")
    p.add_argument("--human", default=None,
                   help="Human partner name (creates human actor + bilateral bond).")
    p.add_argument("--no-human", dest="human", action="store_const", const=None,
                   help="Citizen only — no human partner.")
    p.add_argument("--org", default="mind-protocol", help="Organization id.")
    p.add_argument("--universe", default=None,
                   help="L3 universe graph name (default: $L3_GRAPH or 'universe').")
    p.add_argument("--no-sync-blueprint", dest="sync", action="store_false",
                   help="Skip regenerating the blueprint; reuse existing base.")
    p.add_argument("--dry-run", action="store_true",
                   help="Plan every act but write nothing.")
    args = p.parse_args(argv)

    handle = args.citizen_handle.strip().lstrip("@")
    universe = _l3_graph_name(args.universe)
    parents: list = []

    mode = "DRY-RUN (no writes)" if args.dry_run else "LIVE"
    print(f"\033[1m🎭 The Arrival\033[0m  —  onboarding @{handle} ({args.citizen_name})  [{mode}]")
    if args.human:
        print(f"   bilateral bond with: {args.human}")

    preflight(universe)
    sync_blueprint(args.sync, args.dry_run)
    seed_l1(handle, args.citizen_name, args.intent, parents, args.dry_run)
    create_actors(handle, args.citizen_name, args.org, universe,
                  args.human, args.intent, parents, args.dry_run)
    ceremony(handle, args.citizen_name, universe, args.human, args.dry_run)

    print(f"\n\033[1;32m🎉 @{handle} has arrived.\033[0m "
          f"L1 brain seeded · blueprint synced · actors live in L3 '{universe}'.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
