#!/usr/bin/env python3
# DOCS: Upgrade all embeddings to text-embedding-3-large (3072 dims)
"""
Re-embed all citizen brains and L3 graph with text-embedding-3-large.

Replaces existing embeddings (1536-dim small or 768-dim local) with
3072-dim large embeddings. Skips nodes without text content.

Usage:
    # Dry run (count what would be re-embedded)
    python3 scripts/reembed_all_brains.py --dry-run

    # Re-embed everything
    python3 scripts/reembed_all_brains.py

    # Re-embed specific citizen
    python3 scripts/reembed_all_brains.py --citizen genesis
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from falkordb import FalkorDB
from runtime.infrastructure.embeddings.factory import get_embedding_service

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("reembed")

BATCH_SIZE = 20  # embed this many texts per API call


def get_all_citizen_handles():
    """List all citizen brain graphs in FalkorDB."""
    db = FalkorDB(host="localhost", port=6379)
    graphs = db.list_graphs()
    handles = []
    for g in graphs:
        if g.startswith("brain_"):
            handles.append(g[6:])
    return sorted(handles)


def reembed_graph(graph_name: str, provider, db, dry_run: bool = False) -> dict:
    """Re-embed all text nodes in a graph.

    Returns stats dict.
    """
    g = db.select_graph(graph_name)

    # Get all nodes with content
    result = g.query(
        "MATCH (n) WHERE n.content IS NOT NULL AND n.content <> '' "
        "RETURN n.id, n.content, n.synthesis"
    )

    if not result.result_set:
        return {"graph": graph_name, "total": 0, "embedded": 0, "skipped": 0}

    nodes = []
    for row in result.result_set:
        node_id = row[0]
        content = row[1] or ""
        synthesis = row[2] or ""
        # Use synthesis if available (shorter, more focused), fall back to content
        text = synthesis if synthesis.strip() else content
        if len(text.strip()) < 5:
            continue
        nodes.append((node_id, text.strip()))

    if dry_run:
        return {"graph": graph_name, "total": len(nodes), "embedded": 0, "skipped": 0}

    embedded = 0
    for i in range(0, len(nodes), BATCH_SIZE):
        batch = nodes[i : i + BATCH_SIZE]
        texts = [t for _, t in batch]

        try:
            embeddings = [provider.embed(t) for t in texts]

            for (node_id, _), emb in zip(batch, embeddings):
                emb_json = json.dumps(emb)
                g.query(
                    f"MATCH (n {{id: '{node_id}'}}) "
                    f"SET n.embedding = {emb_json}"
                )
                embedded += 1

        except Exception as e:
            logger.error(f"  Batch {i}-{i+len(batch)} failed: {e}")

        if (i + BATCH_SIZE) % 100 == 0:
            logger.info(f"  {graph_name}: {embedded}/{len(nodes)} embedded...")

    return {"graph": graph_name, "total": len(nodes), "embedded": embedded, "skipped": len(nodes) - embedded}


def main():
    parser = argparse.ArgumentParser(description="Re-embed all brains with text-embedding-3-large")
    parser.add_argument("--dry-run", action="store_true", help="Count nodes without embedding")
    parser.add_argument("--citizen", type=str, help="Re-embed only this citizen")
    parser.add_argument("--l3-only", action="store_true", help="Re-embed only the L3 graph")
    args = parser.parse_args()

    provider = get_embedding_service(check_config=False)
    db = FalkorDB(host="localhost", port=6379)

    logger.info(f"Embedding model: {provider.model_name} ({provider.dimension}D)")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info("")

    start = time.time()
    results = []

    l3_graph = os.environ.get("L3_GRAPH", os.environ.get("UNIVERSE", "lumina-prime"))
    if args.l3_only:
        graphs = [l3_graph]
    elif args.citizen:
        graphs = [f"brain_{args.citizen}"]
    else:
        handles = get_all_citizen_handles()
        graphs = [f"brain_{h}" for h in handles] + [l3_graph]

    for graph_name in graphs:
        logger.info(f"Processing {graph_name}...")
        try:
            stats = reembed_graph(graph_name, provider, db, dry_run=args.dry_run)
            results.append(stats)
            logger.info(
                f"  {stats['graph']}: {stats['total']} nodes, "
                f"{stats['embedded']} embedded, {stats['skipped']} skipped"
            )
        except Exception as e:
            logger.error(f"  {graph_name}: FAILED ({e})")
            results.append({"graph": graph_name, "total": 0, "embedded": 0, "error": str(e)})

    elapsed = time.time() - start

    # Summary
    total_nodes = sum(r["total"] for r in results)
    total_embedded = sum(r["embedded"] for r in results)
    logger.info("")
    logger.info(f"=== SUMMARY ===")
    logger.info(f"Graphs: {len(results)}")
    logger.info(f"Total nodes: {total_nodes}")
    logger.info(f"Embedded: {total_embedded}")
    logger.info(f"Duration: {elapsed:.1f}s")
    logger.info(f"Model: {provider.model_name} ({provider.dimension}D)")


if __name__ == "__main__":
    main()
