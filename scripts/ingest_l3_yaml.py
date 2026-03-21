"""
L3 YAML Ingestion Engine — YAML → WorkspaceStore with deduplication physics.

Applies V3 invariants:
  - 5 universal types only (actor, moment, narrative, space, thing)
  - IDs follow {type}:{scope}:{slug}
  - relation_kind forced to null at L3
  - Endpoint existence check on links (Invariant V1)
  - 3-tier deduplication: ID match → Sim_lex → Sim_vec (cosine > 0.85)

Usage:
    python scripts/ingest_l3_yaml.py data/my_nodes.yaml
    python scripts/ingest_l3_yaml.py data/my_nodes.yaml --dry-run
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("ingest")

# ─── Constants ────────────────────────────────────────────────────────────────

WORKSPACE_PATH = Path("C:/Users/reyno/.mind-desktop/workspace.json")
VALID_TYPES = {"actor", "moment", "narrative", "space", "thing"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*:[a-z0-9_]+:[a-z0-9_]+")
CRYSTALLIZATION_THRESHOLD = 0.85

# ─── Workspace I/O ────────────────────────────────────────────────────────────

def load_workspace() -> Dict[str, Any]:
    if WORKSPACE_PATH.exists():
        with open(WORKSPACE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"nodes": [], "links": []}


def save_workspace(ws: Dict[str, Any]) -> None:
    WORKSPACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACE_PATH, "w", encoding="utf-8") as f:
        json.dump(ws, f, indent=2, ensure_ascii=False, default=str)
    log.info(f"Saved {len(ws['nodes'])} nodes, {len(ws['links'])} links to {WORKSPACE_PATH}")

# ─── Validation ───────────────────────────────────────────────────────────────

def validate_node(node: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a node against V3 invariants. Returns (ok, reason)."""
    nid = node.get("id", "")
    node_type = node.get("node_type", "")

    if node_type not in VALID_TYPES:
        return False, f"REJECTED: '{nid}' has invalid type '{node_type}'. Must be one of {VALID_TYPES}"

    if ":" not in nid:
        return False, f"REJECTED: '{nid}' does not follow {{type}}:{{scope}}:{{slug}} format"

    if not node.get("name"):
        return False, f"REJECTED: '{nid}' has no name"

    if not node.get("synthesis"):
        return False, f"REJECTED: '{nid}' has no synthesis"

    return True, ""


def validate_link(link: Dict[str, Any], node_ids: set) -> Tuple[bool, str]:
    """Validate a link against V3 invariants. Returns (ok, reason)."""
    src = link.get("source", "")
    dst = link.get("target", "")

    if src not in node_ids:
        return False, f"CRITICAL: link source '{src}' does not exist in graph. Invariant V1 violated."

    if dst not in node_ids:
        return False, f"CRITICAL: link target '{dst}' does not exist in graph. Invariant V1 violated."

    return True, ""

# ─── Deduplication Engine ─────────────────────────────────────────────────────

class DeduplicationEngine:
    """3-tier dedup: ID match → Sim_lex (name) → Sim_vec (embedding cosine)."""

    def __init__(self, existing_nodes: List[Dict[str, Any]]):
        # Index by ID
        self.by_id: Dict[str, Dict[str, Any]] = {}
        # Index by (type, name_lower) for lexical match
        self.by_type_name: Dict[Tuple[str, str], str] = {}
        # Embeddings cache for Sim_vec
        self._embeddings: Dict[str, List[float]] = {}
        self._embed_fn = None

        for n in existing_nodes:
            nid = n["id"]
            self.by_id[nid] = n
            key = (n.get("node_type", ""), n.get("name", "").lower().strip())
            self.by_type_name[key] = nid

    def _get_embed_fn(self):
        """Lazy-load embedding function."""
        if self._embed_fn is None:
            try:
                from runtime.infrastructure.embeddings import get_embedding
                self._embed_fn = get_embedding
                log.info("Sim_vec enabled (local embeddings)")
            except Exception as e:
                log.warning(f"Sim_vec disabled — embeddings unavailable: {e}")
                self._embed_fn = lambda _: None
        return self._embed_fn

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        if text in self._embeddings:
            return self._embeddings[text]
        embed = self._get_embed_fn()(text)
        if embed is not None:
            self._embeddings[text] = embed
        return embed

    def check(self, node: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Check if node is a duplicate.

        Returns:
            ("new", None) — no duplicate found, insert as new
            ("update_id", existing_id) — exact ID match, update existing
            ("update_lex", existing_id) — lexical match, update existing
            ("update_vec", existing_id) — semantic match, update existing
        """
        nid = node.get("id", "")
        node_type = node.get("node_type", "")
        name = node.get("name", "")
        synthesis = node.get("synthesis", "")

        # A. ID match (absolute)
        if nid in self.by_id:
            return "update_id", nid

        # B. Sim_lex — same type + same name
        key = (node_type, name.lower().strip())
        if key in self.by_type_name:
            return "update_lex", self.by_type_name[key]

        # C. Sim_vec — semantic similarity > 0.85
        if synthesis and len(synthesis) > 20:
            new_emb = self._get_embedding(synthesis)
            if new_emb is not None:
                from runtime.utils import cosine_similarity
                best_sim = 0.0
                best_id = None
                for existing in self.by_id.values():
                    if existing.get("node_type") != node_type:
                        continue
                    existing_synth = existing.get("synthesis", "")
                    if not existing_synth:
                        continue
                    existing_emb = self._get_embedding(existing_synth)
                    if existing_emb is None:
                        continue
                    sim = cosine_similarity(new_emb, existing_emb)
                    if sim > best_sim:
                        best_sim = sim
                        best_id = existing["id"]

                if best_sim > CRYSTALLIZATION_THRESHOLD and best_id:
                    return "update_vec", best_id

        return "new", None

    def register(self, node: Dict[str, Any]):
        """Register a newly inserted node in the dedup indices."""
        nid = node["id"]
        self.by_id[nid] = node
        key = (node.get("node_type", ""), node.get("name", "").lower().strip())
        self.by_type_name[key] = nid

# ─── Merge Logic ──────────────────────────────────────────────────────────────

def merge_node(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge incoming node into existing. Incoming wins on non-empty fields.
    Energy and weight take the max of both. synthesis concatenates if different."""
    merged = dict(existing)

    # Scalar fields — incoming wins if present
    for field in ("name", "subtype", "status", "assigned_to"):
        val = incoming.get(field)
        if val is not None:
            merged[field] = val

    # Physics fields — take max
    for field in ("energy", "weight"):
        merged[field] = max(existing.get(field, 0), incoming.get(field, 0))

    # Synthesis — keep richer version
    old_synth = existing.get("synthesis", "")
    new_synth = incoming.get("synthesis", "")
    if len(new_synth) > len(old_synth):
        merged["synthesis"] = new_synth

    return merged

# ─── Main Ingestion ───────────────────────────────────────────────────────────

def ingest(yaml_path: str, dry_run: bool = False):
    # Load YAML
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        log.error(f"Empty or invalid YAML: {yaml_path}")
        sys.exit(1)

    incoming_nodes = data.get("nodes", [])
    incoming_links = data.get("links", [])
    log.info(f"YAML: {len(incoming_nodes)} nodes, {len(incoming_links)} links from {yaml_path}")

    # Load workspace
    ws = load_workspace()
    log.info(f"Workspace: {len(ws['nodes'])} nodes, {len(ws['links'])} links")

    # Build dedup engine from existing nodes
    dedup = DeduplicationEngine(ws["nodes"])

    # Build node index for existing nodes (for link validation)
    node_index: Dict[str, int] = {n["id"]: i for i, n in enumerate(ws["nodes"])}

    stats = {"new": 0, "update_id": 0, "update_lex": 0, "update_vec": 0, "rejected": 0}
    link_stats = {"added": 0, "rejected": 0, "duplicate": 0}

    # ── Process nodes ──
    for node in incoming_nodes:
        # Validate
        ok, reason = validate_node(node)
        if not ok:
            log.error(reason)
            stats["rejected"] += 1
            continue

        # Dedup check
        action, existing_id = dedup.check(node)

        if action == "new":
            if not dry_run:
                ws["nodes"].append(node)
                node_index[node["id"]] = len(ws["nodes"]) - 1
                dedup.register(node)
            stats["new"] += 1
            log.debug(f"  NEW: {node['id']}")

        elif action.startswith("update"):
            if not dry_run and existing_id:
                idx = node_index.get(existing_id)
                if idx is not None:
                    ws["nodes"][idx] = merge_node(ws["nodes"][idx], node)
                    dedup.register(ws["nodes"][idx])
            stats[action] += 1
            match_type = action.split("_")[1].upper()
            log.debug(f"  {match_type} MERGE: {node['id']} → {existing_id}")

    # ── Process links ──
    all_node_ids = {n["id"] for n in ws["nodes"]}
    existing_link_set = {(l["source"], l["target"]) for l in ws["links"]}

    for link in incoming_links:
        # Force relation_kind to null (L3 invariant)
        link.pop("relation_kind", None)

        # Validate endpoints
        ok, reason = validate_link(link, all_node_ids)
        if not ok:
            log.warning(reason)
            link_stats["rejected"] += 1
            continue

        # Dedup links
        pair = (link["source"], link["target"])
        if pair in existing_link_set:
            link_stats["duplicate"] += 1
            continue

        if not dry_run:
            ws["links"].append(link)
            existing_link_set.add(pair)
        link_stats["added"] += 1

    # ── Save ──
    if not dry_run:
        save_workspace(ws)

    # ── Report ──
    print(f"\n{'DRY RUN — ' if dry_run else ''}Ingestion complete:")
    print(f"  Nodes: {stats['new']} new, {stats['update_id']} ID-merged, "
          f"{stats['update_lex']} lex-merged, {stats['update_vec']} vec-merged, "
          f"{stats['rejected']} rejected")
    print(f"  Links: {link_stats['added']} added, {link_stats['duplicate']} duplicate, "
          f"{link_stats['rejected']} rejected (broken endpoints)")
    print(f"  Workspace total: {len(ws['nodes'])} nodes, {len(ws['links'])} links")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path.yaml> [--dry-run]")
        sys.exit(1)

    yaml_file = sys.argv[1]
    dry = "--dry-run" in sys.argv

    if not Path(yaml_file).exists():
        log.error(f"File not found: {yaml_file}")
        sys.exit(1)

    ingest(yaml_file, dry_run=dry)
