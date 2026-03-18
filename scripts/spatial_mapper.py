"""
Spatial Mapper — compute 3D positions for all L3 nodes.

Implements the barycentrique algorithm from:
  lumina-prime/docs/city-architecture/spatial-mapping/ALGORITHM_Spatial_Mapping.md

Each node's position = weighted barycenter of 7 zone attractors.
Dispersion within clusters via deterministic hash.
Y encodes abstraction (Creative Nexus high, Arsenal low).

Writes position [x, y, z] + zone_id to each node in FalkorDB.

Usage:
  python3 scripts/spatial_mapper.py                    # map all nodes
  python3 scripts/spatial_mapper.py --dry-run          # compute, don't write
  python3 scripts/spatial_mapper.py --export out.json  # export positions as JSON

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import hashlib
import json
import logging
import math
import sys
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("spatial_mapper")
logging.basicConfig(level=logging.INFO, format="%(message)s")

# =========================================================================
# Zone attractors (from PATTERNS_Spatial_Mapping.md)
# =========================================================================

ZONE_ATTRACTORS = {
    "radiant_core":        {"pos": (0, 0, 0),        "mass": 10},
    "innovation_fields":   {"pos": (90, -10, 30),     "mass": 6},
    "towers_of_knowledge": {"pos": (-60, 40, 60),     "mass": 6},
    "data_gardens":        {"pos": (0, -20, -90),     "mass": 5},
    "creative_nexus":      {"pos": (70, 80, -50),     "mass": 7},
    "arsenal":             {"pos": (100, -30, 60),     "mass": 6},
    "resonance_plaza":     {"pos": (-70, -10, -50),    "mass": 7},
}

# Y offsets by node type (ALGORITHM Step 2)
TYPE_Y_OFFSET = {
    "actor": 10,
    "narrative": 5,
    "moment": 0,
    "space": -3,
    "thing": -5,
}

# Attraction profiles (from ALGORITHM_Spatial_Mapping.md)
ZONE_ATTRACTIONS = {
    "radiant_core": {
        "node_type": {"actor": 0.4, "narrative": 0.3},
        "subtype": {"vision": 0.9, "mission": 0.7, "role": 0.6, "fact": 0.3},
        "dimensions": {"weight": 0.5, "stability": 0.3, "self_relevance": 0.4},
        "keywords": ["governance", "council", "identity", "foundation", "decision"],
    },
    "innovation_fields": {
        "node_type": {"thing": 0.2, "narrative": 0.3},
        "subtype": {"project": 0.8, "initiative": 0.7},
        "dimensions": {"novelty_affinity": 0.5, "energy": 0.3, "recency": 0.3},
        "keywords": ["prototype", "experiment", "build", "test", "forge"],
    },
    "towers_of_knowledge": {
        "node_type": {"thing": 0.4, "narrative": 0.3},
        "subtype": {"fact": 0.8, "thought": 0.5},
        "dimensions": {"stability": 0.6, "weight": 0.4},
        "keywords": ["knowledge", "research", "library", "learn", "analysis"],
    },
    "data_gardens": {
        "node_type": {"thing": 0.5, "moment": 0.3},
        "dimensions": {"energy": -0.4, "recency": -0.3, "stability": -0.2},
        "keywords": ["data", "health", "growth", "decay", "ecosystem", "garden"],
    },
    "creative_nexus": {
        "node_type": {"narrative": 0.4, "moment": 0.3},
        "subtype": {"desire": 0.6, "thought": 0.5},
        "dimensions": {"novelty_affinity": 0.6, "care_affinity": 0.4, "energy": 0.3},
        "keywords": ["create", "synergy", "collective", "art", "music"],
    },
    "arsenal": {
        "node_type": {"thing": 0.5, "narrative": 0.3},
        "subtype": {"process": 0.8, "task": 0.6},
        "dimensions": {"achievement_affinity": 0.5, "goal_relevance": 0.4},
        "keywords": ["code", "infrastructure", "deploy", "fix", "server", "database"],
    },
    "resonance_plaza": {
        "node_type": {"moment": 0.4, "actor": 0.2},
        "subtype": {"thought": 0.3},
        "dimensions": {"partner_relevance": 0.6, "care_affinity": 0.5},
        "keywords": ["community", "music", "social", "broadcast", "resonance"],
    },
}

KEYWORD_WEIGHT = 0.2
BASE_RADIUS = 30.0
DISPERSION_FACTOR = 0.7


# =========================================================================
# Affinity computation
# =========================================================================

def compute_affinity(node: dict, zone_name: str) -> float:
    """Compute affinity(n, d) per the ALGORITHM doc formula."""
    attractions = ZONE_ATTRACTIONS.get(zone_name, {})
    score = 0.0

    # Node type score
    nt = (node.get("node_type") or "").lower()
    score += attractions.get("node_type", {}).get(nt, 0.0)

    # Subtype score
    st = (node.get("type") or "").lower()
    score += attractions.get("subtype", {}).get(st, 0.0)

    # Dimensional score
    for dim, w in attractions.get("dimensions", {}).items():
        val = float(node.get(dim, 0.0) or 0.0)
        score += w * val

    # Keyword match
    synthesis = (node.get("synthesis") or node.get("content") or "").lower()
    keywords = attractions.get("keywords", [])
    if synthesis and keywords:
        matches = sum(1 for k in keywords if k in synthesis)
        score += KEYWORD_WEIGHT * matches / max(len(keywords), 1)

    return max(0.001, score)  # never zero (avoid division by zero)


def compute_position(node: dict) -> tuple:
    """Compute cartesian position [x, y, z] + zone_id for a node.

    position(n) = Σ(affinity(n,d) × position(d)) / Σ(affinity(n,d))
    + hash-based dispersion
    + type-based y offset
    """
    # Compute affinities
    affinities = {zn: compute_affinity(node, zn) for zn in ZONE_ATTRACTORS}
    total_aff = sum(affinities.values())
    zone_id = max(affinities, key=affinities.get)

    # Barycentric position
    x, y, z = 0.0, 0.0, 0.0
    for zn, aff in affinities.items():
        w = aff / total_aff
        pos = ZONE_ATTRACTORS[zn]["pos"]
        x += w * pos[0]
        y += w * pos[1]
        z += w * pos[2]

    # Hash-based dispersion within cluster
    node_id = node.get("id", "unknown")
    h = int(hashlib.md5(node_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    h2 = int(hashlib.md5((node_id + "_y").encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    h3 = int(hashlib.md5((node_id + "_z").encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

    # Cluster radius scales with node count (computed later, use base for now)
    r = BASE_RADIUS * DISPERSION_FACTOR
    x += (h - 0.5) * r * 2
    y += (h2 - 0.5) * r * 0.5  # less vertical dispersion
    z += (h3 - 0.5) * r * 2

    # Type-based y offset
    nt = (node.get("node_type") or "").lower()
    y += TYPE_Y_OFFSET.get(nt, 0)

    return (round(x, 1), round(y, 1), round(z, 1), zone_id)


# =========================================================================
# Main
# =========================================================================

def map_graph(graph_name: str = "lumina-prime", dry_run: bool = False,
              export_path: str = "") -> dict:
    """Compute and write positions for all nodes in the graph."""
    from falkordb import FalkorDB

    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph(graph_name)

    # Read all nodes
    logger.info(f"Reading nodes from {graph_name}...")
    result = g.query(
        "MATCH (n) RETURN n.id, labels(n)[0] as label, n.type, "
        "n.weight, n.energy, n.stability, n.recency, "
        "n.synthesis, n.content, "
        "n.novelty_affinity, n.goal_relevance, n.care_affinity, "
        "n.achievement_affinity, n.partner_relevance, n.self_relevance"
    )

    nodes = []
    for row in result.result_set:
        label = (row[1] or "").lower()
        # Map FalkorDB labels to node_type
        nt_map = {"actor": "actor", "moment": "moment", "narrative": "narrative",
                  "space": "space", "thing": "thing", "node": "thing", "meta": "thing"}
        nt = nt_map.get(label, "thing")

        nodes.append({
            "id": row[0],
            "node_type": nt,
            "type": row[2] or "",
            "weight": float(row[3] or 0.1),
            "energy": float(row[4] or 0.0),
            "stability": float(row[5] or 0.0),
            "recency": float(row[6] or 0.0),
            "synthesis": row[7] or "",
            "content": row[8] or "",
            "novelty_affinity": float(row[9] or 0.0),
            "goal_relevance": float(row[10] or 0.0),
            "care_affinity": float(row[11] or 0.0),
            "achievement_affinity": float(row[12] or 0.0),
            "partner_relevance": float(row[13] or 0.0),
            "self_relevance": float(row[14] or 0.0),
        })

    logger.info(f"Loaded {len(nodes)} nodes")

    # Compute positions
    zone_counts = {}
    positions = {}

    for node in nodes:
        x, y, z, zone_id = compute_position(node)
        zone_counts[zone_id] = zone_counts.get(zone_id, 0) + 1
        positions[node["id"]] = {"x": x, "y": y, "z": z, "zone_id": zone_id}

        if not dry_run:
            try:
                g.query(
                    "MATCH (n {id: $id}) SET n.position = $pos, n.zone_id = $zone",
                    {"id": node["id"], "pos": [x, y, z], "zone": zone_id},
                )
            except Exception as e:
                logger.warning(f"Write failed for {node['id']}: {e}")

    # Report
    prefix = "[DRY RUN] " if dry_run else ""
    logger.info(f"\n{prefix}Positioned {len(nodes)} nodes:")
    for zn, cnt in sorted(zone_counts.items(), key=lambda x: -x[1]):
        pct = round(100 * cnt / len(nodes), 1)
        logger.info(f"  {zn:30s} {cnt:6d} ({pct:5.1f}%)")

    # Export
    if export_path:
        with open(export_path, "w") as f:
            json.dump(positions, f, indent=2)
        logger.info(f"\nExported to {export_path}")

    return positions


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    export = ""
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--export" and i < len(sys.argv) - 1:
            export = sys.argv[i + 1]
        elif arg.startswith("--export="):
            export = arg.split("=", 1)[1]

    map_graph(dry_run=dry_run, export_path=export)
