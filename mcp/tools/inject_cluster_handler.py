"""
inject_cluster — YAML → L3 WorkspaceStore with physics defaults + dedup.

The single entry point for populating the L3 universe. Claude generates YAML,
this handler validates, defaults, embeds, deduplicates, and writes.

INVARIANTS:
  - 5 universal types only (actor, moment, narrative, space, thing)
  - IDs: {type}:{scope}:{slug}
  - relation_kind = null at L3 (always)
  - Endpoints must exist (Invariant V1)
  - synthesis auto-generated from name + content (never in YAML)
  - Embedding via FastEmbed (local, CPU, privacy-first) — mock fallback

DOCS: schema-l3.yaml, docs/schema/GRAMMAR_Link_Synthesis.md
"""

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger("mind.inject_cluster")

# ─── Schema Constants ─────────────────────────────────────────────────────────

VALID_TYPES = frozenset({"actor", "moment", "narrative", "space", "thing"})
WORKSPACE_PATH = Path.home() / ".mind-desktop" / "workspace.json"

# NodeBase defaults from schema-l1.yaml
NODE_DEFAULTS = {
    "weight": 0.5,       # mid-range — not max, not zero. Physics decides the rest.
    "energy": 0.3,       # moderate activation — just injected, not dominant
    "stability": 0.0,    # no consolidation history yet
    "recency": 1.0,      # brand new
    "valence": 0.0,      # neutral
    "type": None,        # semantic subtype — mandatory field name (schema v1.8.1)
    "subtype": None,     # optional secondary classifier
    "status": None,
    "content": None,
    "blocked_by": None,
    "assigned_to": None,
}

# LinkBase defaults from schema-l1.yaml / schema-l3.yaml
LINK_DEFAULTS = {
    "weight": 0.5,
    "energy": 0.1,
    "stability": 0.0,
    "recency": 1.0,
    "hierarchy": 0.0,     # neutral — not contains, not elaborates
    "permanence": 0.5,    # mid-range — not speculative, not definitive
    "trust": 0.0,         # no trust history
    "friction": 0.0,      # no friction
    "affinity": 0.0,      # no attraction
    "aversion": 0.0,      # no repulsion
    "polarity": [0.5, 0.5],
    "valence": 0.0,       # frozen at L3
    "ambivalence": 0.0,   # frozen at L3
}

# ─── Synthesis Generation ─────────────────────────────────────────────────────

def generate_synthesis(node: Dict[str, Any]) -> str:
    """Generate synthesis from name + content + physics state.

    synthesis is the embeddable summary — auto-generated, never user-provided.
    Format: "{Name}, {energy_state} ({importance})"
    """
    name = node.get("name", "")
    content = node.get("content", "")
    energy = node.get("energy", 0.3)
    weight = node.get("weight", 0.5)

    # Build descriptive synthesis
    parts = [name]

    # Energy state
    if energy > 5.0:
        parts.append("intensely active")
    elif energy > 2.0:
        parts.append("active")
    elif energy > 0.5:
        parts.append("present")
    # else: too low to mention

    # Weight/importance
    if weight > 3.0:
        parts.append("(central)")
    elif weight > 1.5:
        parts.append("(significant)")
    elif weight > 0.8:
        parts.append("(established)")
    # else: not notable enough

    synthesis = ", ".join(parts)

    # Append content summary if available (first 200 chars)
    if content:
        summary = content[:200].strip()
        if summary:
            synthesis = f"{synthesis}. {summary}"

    return synthesis

# ─── Embedding (FastEmbed — FAIL LOUD, no mock) ──────────────────────────────

_embed_model = None
_embed_error = None


def _init_embeddings():
    """Initialize FastEmbed. Stores error if unavailable — reported to caller."""
    global _embed_model, _embed_error
    if _embed_model is not None or _embed_error is not None:
        return

    try:
        from fastembed import TextEmbedding
        _embed_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("FastEmbed loaded (all-MiniLM-L6-v2, 384d)")
    except Exception as e:
        _embed_error = str(e)
        logger.error(f"CRITICAL: FastEmbed failed to load: {e}. Nodes will be inserted WITHOUT embeddings. Sim_vec dedup DISABLED. Install fastembed to fix.")


def get_embedding(text: str) -> Optional[List[float]]:
    """Get 384d embedding. Returns None if FastEmbed unavailable or per-text failure."""
    _init_embeddings()

    if _embed_model is None:
        return None

    try:
        embeddings = list(_embed_model.embed([text]))
        return embeddings[0].tolist()
    except Exception as e:
        logger.error(f"Embedding failed for text '{text[:50]}...': {e}")
        return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

# ─── Graph-Driven Validation ──────────────────────────────────────────────────
# Reads validation rules from the graph itself (taxonomy nodes with JSON content).
# Falls back to hardcoded VALID_TYPES only if the graph has no taxonomy yet (bootstrap).

class GraphValidator:
    """Builds validation rules by walking the workspace graph topology.

    Reads:
      - core_entities_taxonomy children → valid node_types
      - val_enum_node_type → allowed enum values
      - val_regex_id → ID format regex
      - group_physics_floats children + their rules → float field constraints
      - group_string_identifiers children + their rules → string field constraints
      - attr_polarity rules → polarity constraints
    """

    def __init__(self, workspace: Dict[str, Any]):
        self.valid_types = set(VALID_TYPES)  # fallback
        self.id_regex = None
        self.field_constraints: Dict[str, Dict[str, Any]] = {}  # field_name → {type, min, max, default, required}
        self._bootstrap = True

        nodes = workspace.get("nodes", [])
        links = workspace.get("links", [])
        if not nodes:
            return

        # Build lookup
        by_id = {n["id"]: n for n in nodes}

        # Build adjacency: target_id → list of (source_id, hierarchy)
        children_of: Dict[str, List[str]] = {}   # parent → children (hierarchy -1.0)
        rules_for: Dict[str, List[str]] = {}      # target → rules pointing at it (hierarchy +1.0)

        for l in links:
            src = l.get("source_id", l.get("source", ""))
            tgt = l.get("target_id", l.get("target", ""))
            h = l.get("hierarchy", 0.0)
            if h <= -0.5:
                children_of.setdefault(src, []).append(tgt)
            elif h >= 0.5:
                rules_for.setdefault(tgt, []).append(src)

        # --- Extract valid types from val_enum_node_type ---
        enum_node = by_id.get("narrative:taxonomy:val_enum_node_type")
        if enum_node:
            try:
                payload = json.loads(enum_node.get("content", "{}"))
                if payload.get("constraint") == "enum" and "values" in payload:
                    self.valid_types = set(payload["values"])
                    self._bootstrap = False
                    logger.info(f"Graph-driven valid_types: {self.valid_types}")
            except (json.JSONDecodeError, TypeError):
                pass

        # --- Extract ID regex from val_regex_id ---
        regex_node = by_id.get("narrative:taxonomy:val_regex_id")
        if regex_node:
            try:
                payload = json.loads(regex_node.get("content", "{}"))
                if payload.get("constraint") == "regex":
                    self.id_regex = re.compile(payload["value"])
                    logger.info(f"Graph-driven ID regex: {payload['value']}")
            except (json.JSONDecodeError, re.error, TypeError):
                pass

        # --- Extract field constraints from groups ---
        def _collect_constraints(attr_id: str) -> Dict[str, Any]:
            """Collect all validation rules pointing at an attribute (directly or via group)."""
            constraints: Dict[str, Any] = {}
            # Direct rules
            for rule_id in rules_for.get(attr_id, []):
                rule_node = by_id.get(rule_id)
                if not rule_node:
                    continue
                try:
                    payload = json.loads(rule_node.get("content", "{}"))
                    c = payload.get("constraint")
                    if c == "type":
                        constraints["type"] = payload["value"]
                        if "length" in payload:
                            constraints["length"] = payload["length"]
                    elif c == "required":
                        constraints["required"] = payload["value"]
                    elif c == "min":
                        constraints["min"] = payload["value"]
                    elif c == "max":
                        constraints["max"] = payload["value"]
                    elif c == "default":
                        constraints["default"] = payload["value"]
                    elif c == "regex":
                        constraints["regex"] = payload["value"]
                    elif c == "enum":
                        constraints["enum"] = payload["values"]
                except (json.JSONDecodeError, TypeError, KeyError):
                    pass
            return constraints

        # Walk groups to find attribute children and inherit group rules
        for group_id in ["narrative:taxonomy:group_physics_floats",
                         "narrative:taxonomy:group_string_identifiers"]:
            group_rules = _collect_constraints(group_id)
            for attr_id in children_of.get(group_id, []):
                attr_node = by_id.get(attr_id)
                if not attr_node:
                    continue
                # Extract field name from node name: "Attribute: weight" → "weight"
                attr_name = attr_node.get("name", "").replace("Attribute: ", "").strip().lower()
                if not attr_name:
                    continue
                # Start with inherited group rules, override with direct rules
                merged = dict(group_rules)
                merged.update(_collect_constraints(attr_id))
                self.field_constraints[attr_name] = merged

        # Polarity (standalone, not in a group)
        polarity_rules = _collect_constraints("narrative:taxonomy:attr_polarity")
        if polarity_rules:
            self.field_constraints["polarity"] = polarity_rules

        if self.field_constraints:
            self._bootstrap = False
            logger.info(f"Graph-driven field constraints: {list(self.field_constraints.keys())}")

    def validate_node(self, node: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a node against graph-derived rules."""
        nid = node.get("id", "")
        node_type = node.get("node_type", "")

        # 1. node_type must be in valid set (from graph or fallback)
        if node_type not in self.valid_types:
            return False, f"REJECTED node '{nid}': node_type '{node_type}' not in {self.valid_types}"

        # 2. ID format
        if self.id_regex:
            if not self.id_regex.match(nid):
                return False, f"REJECTED node '{nid}': ID does not match graph regex {self.id_regex.pattern}"
        else:
            parts = nid.split(":")
            if len(parts) < 3:
                return False, f"REJECTED node '{nid}': ID must be {{type}}:{{scope}}:{{slug}}, got {len(parts)} segments"

        # 3. name required
        if not node.get("name"):
            return False, f"REJECTED node '{nid}': missing 'name'"

        # 4. type field required (schema v1.8.1)
        if "subtype" in node and "type" not in node:
            return False, f"REJECTED node '{nid}': 'type' field required (schema v1.8.1). 'subtype' alone not enough."

        # 5. Physics field constraints from graph
        for field_name, rules in self.field_constraints.items():
            if field_name in ("source_id & target_id", "polarity"):
                continue  # link fields, not node fields
            val = node.get(field_name)
            if val is None:
                continue  # defaults applied later

            field_type = rules.get("type")
            if field_type == "float" and isinstance(val, (int, float)):
                fmin = rules.get("min")
                fmax = rules.get("max")
                if fmin is not None and val < fmin:
                    return False, f"REJECTED node '{nid}': {field_name}={val} below min {fmin} (graph rule)"
                if fmax is not None and val > fmax:
                    return False, f"REJECTED node '{nid}': {field_name}={val} above max {fmax} (graph rule)"

        return True, ""

    def validate_link(self, link: Dict[str, Any], node_ids: set) -> Tuple[bool, str]:
        """Validate a link against graph-derived rules."""
        src = link.get("source_id", "")
        tgt = link.get("target_id", "")

        if not src:
            return False, "REJECTED link: missing 'source_id'. Use source_id/target_id"
        if not tgt:
            return False, "REJECTED link: missing 'target_id'. Use source_id/target_id"

        if src not in node_ids:
            return False, f"REJECTED link: source_id '{src}' does not exist. Invariant V1 violated."
        if tgt not in node_ids:
            return False, f"REJECTED link: target_id '{tgt}' does not exist. Invariant V1 violated."

        # relation_kind must be null at L3
        rk = link.get("relation_kind")
        if rk is not None:
            return False, f"REJECTED link {src} → {tgt}: relation_kind must be null at L3, got '{rk}'"

        # Polarity: graph-driven or hardcoded
        pol = link.get("polarity")
        if pol is not None:
            pol_rules = self.field_constraints.get("polarity", {})
            expected_type = pol_rules.get("type", "float_array")
            expected_len = pol_rules.get("length", 2)

            if expected_type == "float_array":
                if not isinstance(pol, list) or len(pol) != expected_len:
                    return False, f"REJECTED link {src} → {tgt}: polarity must be array of {expected_len} floats, got {pol}"

            fmin = pol_rules.get("min", -1.0)
            fmax = pol_rules.get("max", 1.0)
            if isinstance(pol, list):
                for i, v in enumerate(pol):
                    if isinstance(v, (int, float)):
                        if v < fmin:
                            return False, f"REJECTED link {src} → {tgt}: polarity[{i}]={v} below min {fmin}"
                        if v > fmax:
                            return False, f"REJECTED link {src} → {tgt}: polarity[{i}]={v} above max {fmax}"

        # Physics float fields on links
        for field_name, rules in self.field_constraints.items():
            if field_name in ("polarity", "source_id & target_id", "id", "node_type"):
                continue
            val = link.get(field_name)
            if val is None:
                continue
            field_type = rules.get("type")
            if field_type == "float" and isinstance(val, (int, float)):
                fmin = rules.get("min")
                fmax = rules.get("max")
                if fmin is not None and val < fmin:
                    return False, f"REJECTED link {src} → {tgt}: {field_name}={val} below min {fmin} (graph rule)"
                if fmax is not None and val > fmax:
                    return False, f"REJECTED link {src} → {tgt}: {field_name}={val} above max {fmax} (graph rule)"

        return True, ""

    def apply_defaults(self, node: Dict[str, Any]) -> None:
        """Apply graph-derived defaults to missing fields."""
        for field_name, rules in self.field_constraints.items():
            if field_name in ("polarity", "source_id & target_id"):
                continue
            if field_name not in node and "default" in rules:
                node[field_name] = rules["default"]

    def apply_link_defaults(self, link: Dict[str, Any]) -> None:
        """Apply graph-derived defaults to missing link fields."""
        pol_rules = self.field_constraints.get("polarity", {})
        if "polarity" not in link and "default" in pol_rules:
            link["polarity"] = pol_rules["default"]

        for field_name, rules in self.field_constraints.items():
            if field_name in ("polarity", "source_id & target_id", "id", "node_type"):
                continue
            if field_name not in link and "default" in rules:
                link[field_name] = rules["default"]

# ─── Deduplication ────────────────────────────────────────────────────────────

# Sim_vec threshold: 0.92 to avoid false positives (prefer creating new over losing unique).
# Better to have 2 similar nodes than to merge 2 distinct concepts.
SIM_VEC_THRESHOLD = 0.92


class Deduplicator:
    def __init__(self, nodes: List[Dict[str, Any]]):
        self.by_id: Dict[str, int] = {}  # id → index in nodes list
        self.by_type_name: Dict[Tuple[str, str], int] = {}
        self._embeddings: Dict[str, List[float]] = {}

        for i, n in enumerate(nodes):
            self.by_id[n["id"]] = i
            key = (n.get("node_type", ""), n.get("name", "").lower().strip())
            self.by_type_name[key] = i

            # Cache existing embeddings
            emb = n.get("embedding")
            if emb and isinstance(emb, list):
                self._embeddings[n["id"]] = emb

    def check(self, node: Dict[str, Any], all_nodes: List[Dict[str, Any]]) -> Tuple[str, int]:
        """Returns ("new", -1) | ("id_match", idx) | ("lex_match", idx) | ("vec_match", idx)."""
        nid = node["id"]
        ntype = node.get("node_type", "")
        name = node.get("name", "")

        # A. Exact ID
        if nid in self.by_id:
            return "id_match", self.by_id[nid]

        # B. Sim_lex: same type + exact same name
        key = (ntype, name.lower().strip())
        if key in self.by_type_name:
            return "lex_match", self.by_type_name[key]

        # C. Sim_vec: semantic similarity
        node_synth = node.get("_synthesis", node.get("synthesis", ""))
        if node_synth and len(node_synth) > 15:
            node_emb = node.get("embedding")
            if not node_emb:
                node_emb = get_embedding(node_synth)

            best_sim = 0.0
            best_idx = -1
            for eid, emb in self._embeddings.items():
                # Only compare same type
                eidx = self.by_id.get(eid, -1)
                if eidx < 0:
                    continue
                if all_nodes[eidx].get("node_type") != ntype:
                    continue
                sim = cosine_similarity(node_emb, emb)
                if sim > best_sim:
                    best_sim = sim
                    best_idx = eidx

            if best_sim > SIM_VEC_THRESHOLD and best_idx >= 0:
                return "vec_match", best_idx

        return "new", -1

    def register(self, node: Dict[str, Any], idx: int):
        self.by_id[node["id"]] = idx
        key = (node.get("node_type", ""), node.get("name", "").lower().strip())
        self.by_type_name[key] = idx
        emb = node.get("embedding")
        if emb:
            self._embeddings[node["id"]] = emb

# ─── Merge ────────────────────────────────────────────────────────────────────

def merge_node(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """Merge incoming into existing. Richer content wins. Physics takes max."""
    merged = dict(existing)

    # Text fields: incoming wins if present and non-empty
    for f in ("name", "type", "subtype", "status", "assigned_to"):
        v = incoming.get(f)
        if v is not None:
            merged[f] = v

    # Content: longer wins
    for f in ("content", "synthesis"):
        old = existing.get(f, "") or ""
        new = incoming.get(f, "") or ""
        if len(new) > len(old):
            merged[f] = new

    # Physics: take max (the more consolidated/activated, the more important)
    for f in ("energy", "weight", "stability"):
        merged[f] = max(existing.get(f, 0), incoming.get(f, 0))

    # Embedding: prefer incoming if it has one
    if incoming.get("embedding"):
        merged["embedding"] = incoming["embedding"]

    merged["updated_at_s"] = int(time.time())

    return merged

# ─── Workspace I/O ────────────────────────────────────────────────────────────

def load_workspace() -> Dict[str, Any]:
    if WORKSPACE_PATH.exists():
        with open(WORKSPACE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"nodes": [], "links": []}


def save_workspace(ws: Dict[str, Any]):
    WORKSPACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(WORKSPACE_PATH, "w", encoding="utf-8") as f:
        json.dump(ws, f, indent=2, ensure_ascii=False, default=str)

# ─── Main Handler ─────────────────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "inject_cluster",
    "description": (
        "[ACT] Inject nodes and links into the L3 WorkspaceStore from YAML. "
        "Validates types, IDs, endpoints. Deduplicates via ID/name/embedding. "
        "Auto-generates synthesis and embeddings. Applies physics defaults."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "yaml": {
                "type": "string",
                "description": "YAML string with nodes: and links: arrays",
            },
        },
        "required": ["yaml"],
    },
}


def handle_inject_cluster(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Handle inject_cluster MCP tool call."""
    yaml_str = args.get("yaml", "")
    if not yaml_str:
        return {"content": [{"type": "text", "text": "ERROR: 'yaml' argument is required."}], "isError": True}

    # Parse YAML
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return {"content": [{"type": "text", "text": f"ERROR: Invalid YAML: {e}"}], "isError": True}

    if not data or not isinstance(data, dict):
        return {"content": [{"type": "text", "text": "ERROR: YAML must contain a dict with 'nodes' and/or 'links'"}], "isError": True}

    incoming_nodes = data.get("nodes", [])
    incoming_links = data.get("links", [])

    # Load workspace and build graph-driven validator
    ws = load_workspace()
    validator = GraphValidator(ws)
    dedup = Deduplicator(ws["nodes"])

    if validator._bootstrap:
        logger.info("Graph validator in BOOTSTRAP mode (no taxonomy nodes yet)")
    else:
        logger.info(f"Graph validator loaded: {len(validator.valid_types)} types, {len(validator.field_constraints)} field rules")

    stats = {"new": 0, "id_merge": 0, "lex_merge": 0, "vec_merge": 0, "rejected": 0}
    link_stats = {"added": 0, "rejected": 0, "duplicate": 0}
    errors = []
    now = int(time.time())

    # Surface embedding init error if any
    if _embed_error:
        errors.append(f"⚠ EMBEDDING UNAVAILABLE: {_embed_error}. All nodes inserted WITHOUT vectors. Sim_vec dedup DISABLED. Run: pip install fastembed")

    # ── Process nodes ──
    for raw_node in incoming_nodes:
        node = dict(raw_node)

        # Apply hardcoded defaults first, then graph-derived defaults override
        for field, default in NODE_DEFAULTS.items():
            if field not in node:
                node[field] = default
        validator.apply_defaults(node)

        # Timestamps
        node.setdefault("created_at_s", now)
        node["updated_at_s"] = now

        # Strip synthesis if provided (it's auto-generated)
        node.pop("synthesis", None)

        # Validate against graph topology
        ok, err = validator.validate_node(node)
        if not ok:
            errors.append(err)
            stats["rejected"] += 1
            logger.error(err)
            continue

        # Generate synthesis from name + content + physics
        node["synthesis"] = generate_synthesis(node)

        # Generate embedding — None if per-text failure (node still inserted, unembedded)
        emb = get_embedding(node["synthesis"])
        if emb is not None:
            node["embedding"] = emb
        else:
            errors.append(f"WARN: embedding failed for '{node['id']}' — inserted without vector")

        # Dedup check
        action, idx = dedup.check(node, ws["nodes"])

        if action == "new":
            ws["nodes"].append(node)
            new_idx = len(ws["nodes"]) - 1
            dedup.register(node, new_idx)
            stats["new"] += 1
        elif action == "id_match":
            ws["nodes"][idx] = merge_node(ws["nodes"][idx], node)
            dedup.register(ws["nodes"][idx], idx)
            stats["id_merge"] += 1
        elif action == "lex_match":
            ws["nodes"][idx] = merge_node(ws["nodes"][idx], node)
            dedup.register(ws["nodes"][idx], idx)
            stats["lex_merge"] += 1
        elif action == "vec_match":
            ws["nodes"][idx] = merge_node(ws["nodes"][idx], node)
            dedup.register(ws["nodes"][idx], idx)
            stats["vec_merge"] += 1

    # ── Process links ──
    all_ids = {n["id"] for n in ws["nodes"]}
    existing_pairs = {(l["source_id"], l["target_id"]) for l in ws["links"]
                      if "source_id" in l and "target_id" in l}

    for raw_link in incoming_links:
        link = dict(raw_link)

        # Apply hardcoded link defaults first, then graph-derived
        for field, default in LINK_DEFAULTS.items():
            if field not in link:
                link[field] = default
        validator.apply_link_defaults(link)

        link.setdefault("created_at_s", now)
        link["updated_at_s"] = now

        # Validate against graph topology
        ok, err = validator.validate_link(link, all_ids)
        if not ok:
            errors.append(err)
            link_stats["rejected"] += 1
            continue

        # Dedup by pair
        src = link["source_id"]
        tgt = link["target_id"]
        pair = (src, tgt)
        if pair in existing_pairs:
            link_stats["duplicate"] += 1
            continue

        ws["links"].append(link)
        existing_pairs.add(pair)
        link_stats["added"] += 1

    # ── Orphan detection + auto-linking ──
    # Collect IDs of nodes just inserted in this cluster
    inserted_ids = set()
    for raw_node in incoming_nodes:
        nid = raw_node.get("id", "")
        if nid in {n["id"] for n in ws["nodes"]}:
            inserted_ids.add(nid)

    # Check which inserted nodes have NO link to any pre-existing node
    pre_existing_ids = {n["id"] for n in ws["nodes"]} - inserted_ids
    orphan_ids = []
    auto_links_created = []

    for nid in inserted_ids:
        connected = False
        for l in ws["links"]:
            s = l.get("source_id", l.get("source", ""))
            t = l.get("target_id", l.get("target", ""))
            if (s == nid and t in pre_existing_ids) or \
               (t == nid and s in pre_existing_ids):
                connected = True
                break
        if not connected:
            orphan_ids.append(nid)

    # Auto-link orphans by embedding proximity to existing nodes
    if orphan_ids:
        for orphan_id in orphan_ids:
            orphan_node = next((n for n in ws["nodes"] if n["id"] == orphan_id), None)
            if not orphan_node or not orphan_node.get("embedding"):
                continue

            # Find closest pre-existing node by embedding
            best_sim = 0.0
            best_target = None
            for n in ws["nodes"]:
                if n["id"] in inserted_ids or not n.get("embedding"):
                    continue
                sim = cosine_similarity(orphan_node["embedding"], n["embedding"])
                if sim > best_sim:
                    best_sim = sim
                    best_target = n["id"]

            if best_target and best_sim > 0.3:
                auto_link = {
                    "source_id": orphan_id,
                    "target_id": best_target,
                    "weight": round(best_sim * 0.5, 3),  # proportional to similarity
                    "energy": 0.1,
                    "stability": 0.0,
                    "recency": 1.0,
                    "hierarchy": 0.0,
                    "permanence": 0.3,  # auto-generated = speculative
                    "trust": 0.0,
                    "friction": 0.0,
                    "affinity": round(best_sim * 0.3, 3),
                    "aversion": 0.0,
                    "polarity": [0.5, 0.5],
                    "valence": 0.0,
                    "ambivalence": 0.0,
                    "created_at_s": now,
                    "updated_at_s": now,
                }
                ws["links"].append(auto_link)
                auto_links_created.append({
                    "orphan": orphan_id,
                    "linked_to": best_target,
                    "similarity": round(best_sim, 3),
                })

    # ── Connectivity ratio ──
    if inserted_ids:
        links_touching_cluster = sum(
            1 for l in ws["links"]
            if l.get("source_id", l.get("source", "")) in inserted_ids
            or l.get("target_id", l.get("target", "")) in inserted_ids
        )
        connectivity_ratio = links_touching_cluster / len(inserted_ids)
    else:
        connectivity_ratio = 0.0

    # ── Save ──
    save_workspace(ws)

    # ── Build structured result ──
    result_lines = [
        f"Ingestion complete:",
        f"  Nodes: {stats['new']} new, {stats['id_merge']} ID-merged, "
        f"{stats['lex_merge']} lex-merged, {stats['vec_merge']} vec-merged, "
        f"{stats['rejected']} rejected",
        f"  Links: {link_stats['added']} added, {link_stats['duplicate']} duplicate, "
        f"{link_stats['rejected']} rejected",
        f"  Auto-links: {len(auto_links_created)} created by embedding proximity",
        f"  Connectivity: {connectivity_ratio:.2f} links/node "
        f"{'✓' if connectivity_ratio >= 0.5 else '⚠ below 0.5 — add more links'}",
        f"  Total: {len(ws['nodes'])} nodes, {len(ws['links'])} links",
    ]

    # Orphan warning with suggestions
    remaining_orphans = [oid for oid in orphan_ids
                         if oid not in {al["orphan"] for al in auto_links_created}]
    if remaining_orphans:
        result_lines.append(f"\n⚠ Orphan nodes (no link to existing graph):")
        for oid in remaining_orphans:
            result_lines.append(f"  {oid} — link it to an existing node")

    # Auto-link report
    if auto_links_created:
        result_lines.append(f"\nAuto-linked by embedding proximity:")
        for al in auto_links_created:
            result_lines.append(
                f"  {al['orphan']} → {al['linked_to']} (sim={al['similarity']})"
            )

    # Per-node/per-link rejection details
    if errors:
        result_lines.append(f"\nRejected ({len(errors)}):")
        for e in errors:
            result_lines.append(f"  {e}")

    return {"content": [{"type": "text", "text": "\n".join(result_lines)}]}
