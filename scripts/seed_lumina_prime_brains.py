#!/usr/bin/env python3
"""
Seed brains for all Lumina Prime citizens.

Pipeline: generate base brain → per-citizen overlay → persist to FalkorDB.

Usage:
    cd /home/mind-protocol/mind-mcp
    python scripts/seed_lumina_prime_brains.py
    python scripts/seed_lumina_prime_brains.py --citizen vox
    python scripts/seed_lumina_prime_brains.py --dry-run
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
)
logger = logging.getLogger("seed_brains")

REGISTRY_PATH = Path("/home/mind-protocol/mind-platform/data/registry.json")
CITIZENS_DIR = Path("/home/mind-protocol/lumina-prime/citizens")


def get_lumina_citizens(citizen_filter=None):
    """Load Lumina Prime citizens from L4 registry."""
    if citizen_filter:
        return [{"id": citizen_filter}]

    data = json.loads(REGISTRY_PATH.read_text())
    citizens = []
    for c in data.get("citizens", []):
        universe = c.get("universe", "")
        if universe in ("", "lumina_prime"):
            # Only include citizens that have a directory in lumina-prime
            if (CITIZENS_DIR / c["id"]).is_dir():
                citizens.append(c)
    return citizens


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed Lumina Prime citizen brains")
    parser.add_argument("--citizen", help="Seed a single citizen")
    parser.add_argument("--dry-run", action="store_true", help="Don't persist to FalkorDB")
    args = parser.parse_args()

    # Step 1: Generate base brain from source docs
    logger.info("Generating base brain from source docs...")
    from runtime.seed_brain_from_source_docs_dynamic_generator import generate_seed_brain
    base_brain = generate_seed_brain()
    base_nodes = len(base_brain.get("nodes", []))
    base_links = len(base_brain.get("links", []))
    logger.info(f"Base brain: {base_nodes} nodes, {base_links} links")

    # Step 2: Get citizen list
    citizens = get_lumina_citizens(args.citizen)
    logger.info(f"Seeding {len(citizens)} citizens...")

    # Step 3: Per-citizen overlay + persist
    from runtime.cognition.citizen_brain_seeder import generate_citizen_brain

    seeded = 0
    failed = 0
    start = time.time()

    for c in citizens:
        handle = c["id"]
        try:
            brain = generate_citizen_brain(handle, base_brain=base_brain)
            total_nodes = len(brain.get("nodes", []))
            total_links = len(brain.get("links", []))
            overlay_nodes = total_nodes - base_nodes

            if args.dry_run:
                logger.info(f"  [DRY] {handle}: {total_nodes} nodes ({overlay_nodes} overlay), {total_links} links")
            else:
                from runtime.cognition.citizen_brain_seeder import load_brain_into_state
                from runtime.cognition.falkordb_checkpointer import FalkorDBBrainCheckpointer

                state = load_brain_into_state(brain, handle)
                checkpointer = FalkorDBBrainCheckpointer(
                    citizen_handle=handle,
                    db_host=os.environ.get("FALKORDB_HOST", "localhost"),
                    db_port=int(os.environ.get("FALKORDB_PORT", "6379")),
                )
                if checkpointer.connect():
                    checkpointer.flush_all(state)
                    logger.info(
                        f"  {handle}: {len(state.nodes)} nodes, {len(state.links)} links "
                        f"→ brain_{handle}"
                    )
                else:
                    logger.error(f"  {handle}: FalkorDB connection failed")
                    failed += 1
                    continue

            seeded += 1
        except Exception as e:
            logger.error(f"  {handle}: FAILED — {e}")
            failed += 1

    elapsed = time.time() - start
    logger.info(
        f"Done: {seeded} seeded, {failed} failed, {elapsed:.1f}s"
    )


if __name__ == "__main__":
    main()
