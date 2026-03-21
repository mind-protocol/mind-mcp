"""
Export L3 Universe — FalkorDB → JSON snapshot

Extracts all nodes and links from the mind-protocol-v3 graph
into a clean, schema-aligned JSON file for BrainStore seeding.

Usage:
    python scripts/export_l3_to_json.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


def connect():
    from falkordb import FalkorDB
    host = os.environ.get("FALKORDB_HOST", "127.0.0.1")
    port = int(os.environ.get("FALKORDB_PORT", "6379"))
    graph_name = os.environ.get("FALKORDB_GRAPH", "mind-protocol-v3")
    db = FalkorDB(host=host, port=port)
    graph = db.select_graph(graph_name)
    print(f"Connected to {graph_name} at {host}:{port}")
    return graph, graph_name


def export_nodes(graph):
    """Extract all nodes with all properties."""
    result = graph.query(
        "MATCH (n) RETURN properties(n) AS props"
    )
    nodes = []
    for row in result.result_set:
        props = row[0]
        if isinstance(props, dict):
            nodes.append(props)
    return nodes


def export_links(graph):
    """Extract all links with source, target, and properties."""
    result = graph.query(
        "MATCH (a)-[r]->(b) "
        "RETURN a.id AS src, b.id AS dst, type(r) AS rel_type, properties(r) AS props"
    )
    links = []
    for row in result.result_set:
        src, dst, rel_type, props = row
        link = {
            "source": src,
            "target": dst,
            "relation_type": rel_type,
        }
        if isinstance(props, dict):
            link.update(props)
        links.append(link)
    return links


def main():
    graph, graph_name = connect()

    print("Exporting nodes...")
    nodes = export_nodes(graph)
    print(f"  {len(nodes)} nodes extracted")

    print("Exporting links...")
    links = export_links(graph)
    print(f"  {len(links)} links extracted")

    snapshot = {
        "graph_name": graph_name,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "node_count": len(nodes),
        "link_count": len(links),
        "nodes": nodes,
        "links": links,
    }

    out_path = Path(__file__).parent.parent / "data" / "l3_universe_snapshot.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False, default=str)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\nExported to {out_path}")
    print(f"  {len(nodes)} nodes, {len(links)} links, {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
