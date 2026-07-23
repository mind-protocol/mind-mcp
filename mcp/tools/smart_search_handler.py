"""
smart_search — Fuzzy, entity-aware search over the L3 workspace graph.

Where graph_query does raw keyword substring matching, smart_search is built
for *disambiguation*: give it a name (or a fuzzy/typo'd fragment of one) and it
returns a ranked shortlist of candidate entities — citizens, humans, agents,
organizations, modules, things, moments — each annotated with just enough
context to pick the right one.

For every candidate it surfaces:
  - a human-friendly kind label (citizen / human / organization / module / …)
  - the canonical id + scope + status
  - *why* it matched (exact name, fuzzy name, id, content …)
  - a one-line synthesis snippet
  - a few linked entities, for disambiguation ("the Mind connected to NLR")

Matching is accent-insensitive and typo-tolerant (difflib), so "mecanical
visionnaire" still finds "Mechanical Visionary". Pure in-memory, reads
workspace.json directly — no FalkorDB, no side effects.

Usage via MCP:
    smart_search(query="mechanical visionary")
    smart_search(query="devboard", kinds=["organization", "module"])
    smart_search(query="nlr", kinds=["citizen", "human"], limit=5)
"""

import json
import logging
import unicodedata
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

# Reuse the battle-tested loaders from graph_query — same workspace, same links.
from mcp.tools.graph_query_handler import _load_workspace, _expand_neighbors

# Optional semantic layer — reuse the FastEmbed model already wired for injection.
# The import always succeeds; get_embedding() returns None at call time if the
# fastembed package isn't installed, so semantic mode degrades gracefully.
try:
    from mcp.tools.inject_cluster_handler import get_embedding, cosine_similarity
except Exception:  # pragma: no cover — defensive: never let this break lexical search
    get_embedding = None
    cosine_similarity = None

logger = logging.getLogger("mind.smart_search")

# Cache computed node embeddings across calls: {(id, updated_at_s): vector}.
# Nodes rarely change between searches, so this makes repeated semantic queries cheap.
_EMBED_CACHE: Dict[Tuple[str, Any], List[float]] = {}


# ─── Normalization ────────────────────────────────────────────────────────────

def _normalize(text: Optional[str]) -> str:
    """Lowercase + strip accents so 'Mécanique' matches 'mecanique'."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.lower().strip()


# ─── Entity kind derivation ───────────────────────────────────────────────────
# The 5 universal node_types (actor/space/thing/moment/narrative) are too coarse
# for a person picking an entity. We derive a friendlier label from subtype, id
# scope, and embedded [type: …] tags in content.

def _entity_kind(node: Dict) -> str:
    """Human-friendly kind label for display and filtering."""
    ntype = (node.get("node_type") or "").lower()
    subtype = _normalize(node.get("subtype") or node.get("type"))
    nid = (node.get("id") or "").lower()
    blob = _normalize(f"{node.get('name') or ''} {node.get('content') or ''}")

    if ntype == "actor":
        if subtype == "human":
            return "human"
        if subtype == "citizen" or "citizenai" in blob.replace(" ", ""):
            return "citizen"
        if subtype == "agent" or ":agent:" in nid or "operationalagent" in blob.replace(" ", ""):
            return "agent"
        return "actor"
    if ntype == "space":
        if subtype in ("module", "application"):
            return subtype
        if subtype == "cluster" or ":cluster:" in nid:
            return "cluster"
        # Spaces are the L3 home of organizations, teams, rooms, worlds.
        return "organization"
    return ntype or "unknown"


# Alias → filter spec. Each spec matches on node_type and/or derived kind.
# Passing an exact node_type or kind label also works (see _matches_kinds).
_KIND_ALIASES: Dict[str, Dict[str, set]] = {
    "citizen":      {"kind": {"citizen"}},
    "human":        {"kind": {"human"}},
    "agent":        {"kind": {"agent"}},
    "person":       {"node_type": {"actor"}},
    "people":       {"node_type": {"actor"}},
    "actor":        {"node_type": {"actor"}},
    "organization": {"kind": {"organization"}},
    "organisation": {"kind": {"organization"}},
    "org":          {"kind": {"organization"}},
    "space":        {"node_type": {"space"}},
    "module":       {"kind": {"module"}},
    "app":          {"kind": {"module", "application"}},
    "application":  {"kind": {"application"}},
    "cluster":      {"kind": {"cluster"}},
    "thing":        {"node_type": {"thing"}},
    "object":       {"node_type": {"thing"}},
    "artifact":     {"node_type": {"thing"}},
    "moment":       {"node_type": {"moment"}},
    "event":        {"node_type": {"moment"}},
    "narrative":    {"node_type": {"narrative"}},
    "note":         {"node_type": {"narrative"}},
    "concept":      {"node_type": {"narrative"}},
}


def _matches_kinds(node: Dict, requested: List[str]) -> bool:
    """True if node satisfies any requested kind alias / node_type / kind label."""
    if not requested:
        return True
    ntype = (node.get("node_type") or "").lower()
    kind = _entity_kind(node)
    for raw in requested:
        alias = _normalize(raw)
        spec = _KIND_ALIASES.get(alias)
        if spec:
            if ntype in spec.get("node_type", set()):
                return True
            if kind in spec.get("kind", set()):
                return True
        else:
            # Unknown alias: allow direct node_type or kind match as a fallback.
            if alias in (ntype, kind):
                return True
    return False


# ─── Scoring ──────────────────────────────────────────────────────────────────

def _best_token_fuzz(token: str, field: str) -> float:
    """Best fuzzy ratio of `token` against any word in `field`."""
    best = 0.0
    for word in field.split():
        r = SequenceMatcher(None, token, word).ratio()
        if r > best:
            best = r
    return best


def _score(node: Dict, query_norm: str, tokens: List[str]) -> Tuple[float, List[str]]:
    """Score a node against the query. Returns (score, reasons)."""
    name = _normalize(node.get("name"))
    nid = _normalize(node.get("id"))
    subtype = _normalize(node.get("subtype") or node.get("type"))
    body = _normalize(f"{node.get('synthesis') or ''} {node.get('content') or ''}")

    score = 0.0
    reasons: List[str] = []

    # ── Whole-phrase matches (strongest signals) ──
    if query_norm and query_norm == name:
        score += 60.0
        reasons.append("exact name")
    elif query_norm and name.startswith(query_norm):
        score += 30.0
        reasons.append("name prefix")
    elif query_norm and query_norm in name:
        score += 22.0
        reasons.append("name contains query")

    if query_norm and query_norm in nid:
        score += 20.0
        reasons.append("id match")
    if query_norm and len(query_norm) >= 3 and query_norm in body:
        score += 10.0
        reasons.append("in description")

    # ── Per-token matches ──
    tok_name_hits = 0
    for tok in tokens:
        if len(tok) < 2:
            continue
        if tok in name:
            score += 8.0
            tok_name_hits += 1
        elif tok in nid:
            score += 6.0
        elif tok in subtype:
            score += 5.0
        elif tok in body:
            score += 3.0
    if tok_name_hits and tok_name_hits == len([t for t in tokens if len(t) >= 2]):
        score += 6.0  # every meaningful token landed in the name
        reasons.append("all terms in name")

    # ── Fuzzy (typo tolerance) — only meaningful when nothing solid matched ──
    if name:
        phrase_ratio = SequenceMatcher(None, query_norm, name).ratio()
        if phrase_ratio >= 0.6:
            score += 40.0 * phrase_ratio
            if "exact name" not in reasons and phrase_ratio < 0.99:
                reasons.append(f"fuzzy name ~{int(phrase_ratio * 100)}%")
        tok_fuzz = max((_best_token_fuzz(t, name) for t in tokens if len(t) >= 3), default=0.0)
        if tok_fuzz >= 0.75:
            score += 15.0 * tok_fuzz

    return score, reasons


# ─── Semantic layer (optional) ────────────────────────────────────────────────

def _node_embedding(node: Dict) -> Optional[List[float]]:
    """Embedding for a node — stored vector if present, else computed & cached."""
    stored = node.get("embedding")
    if isinstance(stored, list) and stored:
        return stored

    if get_embedding is None:
        return None

    key = (node.get("id") or "", node.get("updated_at_s"))
    if key in _EMBED_CACHE:
        return _EMBED_CACHE[key]

    text = node.get("synthesis") or f"{node.get('name') or ''}. {node.get('content') or ''}".strip(". ")
    if not text:
        return None
    vec = get_embedding(text)
    if vec is not None:
        _EMBED_CACHE[key] = vec
    return vec


# ─── Formatting ───────────────────────────────────────────────────────────────

_KIND_GLYPH = {
    "citizen": "🤖", "human": "🧑", "agent": "⚙", "actor": "◆",
    "organization": "🏛", "module": "▦", "application": "▦", "cluster": "❖",
    "thing": "●", "moment": "◷", "narrative": "≡",
}


def _scope_of(node: Dict) -> str:
    """Extract the scope segment from an id of shape {type}:{scope}:{slug}."""
    parts = (node.get("id") or "").split(":")
    return parts[1] if len(parts) >= 3 else ""


def _snippet(node: Dict, length: int = 160) -> str:
    text = node.get("synthesis") or node.get("content") or ""
    if text.startswith("{"):
        try:
            text = json.loads(text).get("_description") or text
        except (json.JSONDecodeError, TypeError):
            pass
    text = " ".join(text.split())
    return text[: length - 3] + "..." if len(text) > length else text


def _format_candidate(rank: int, score: float, node: Dict, reasons: List[str], links_str: str) -> str:
    kind = _entity_kind(node)
    glyph = _KIND_GLYPH.get(kind, "·")
    name = node.get("name") or "(unnamed)"
    nid = node.get("id") or "?"
    scope = _scope_of(node)
    status = node.get("status")

    meta = [f"kind: {kind}"]
    if scope:
        meta.append(f"scope: {scope}")
    if status:
        meta.append(f"status: {status}")

    lines = [
        f"#{rank}  {glyph} {name}   ·  score {score:.0f}",
        f"    id: {nid}   ({'   '.join(meta)})",
    ]
    if reasons:
        lines.append(f"    why: {', '.join(reasons)}")
    snip = _snippet(node)
    if snip:
        lines.append(f"    ↳ {snip}")
    if links_str:
        lines.append(f"    ↔ linked: {links_str}")
    return "\n".join(lines)


# ─── Tool Schema ──────────────────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "smart_search",
    "description": (
        "[THINK] Smart entity search over the workspace graph. Give it a name or "
        "fuzzy fragment and it returns a RANKED SHORTLIST of candidate entities "
        "(citizens, humans, agents, organizations, modules, things, moments) with "
        "disambiguation info: kind, id, status, why it matched, a description "
        "snippet, and linked entities. Accent- and typo-tolerant. Use this to "
        "resolve 'who/what did they mean' before acting. Filter with `kinds`."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Name or fuzzy fragment to search for (e.g. 'mechanical visionary', 'devboard', 'nlr').",
            },
            "kinds": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Optional filter by entity kind. Friendly aliases: 'citizen', "
                    "'human', 'agent', 'person', 'organization', 'module', 'cluster', "
                    "'thing', 'moment', 'narrative'. Also accepts raw node_types "
                    "(actor/space/thing/moment/narrative)."
                ),
            },
            "scope": {
                "type": "string",
                "description": "Optional: restrict to ids containing this scope (e.g. 'mp', 'taxonomy', 'app').",
            },
            "limit": {
                "type": "integer",
                "description": "Max candidates to return (default 8).",
            },
            "min_score": {
                "type": "number",
                "description": "Minimum score to include a candidate (default 5).",
            },
            "semantic": {
                "type": "boolean",
                "description": (
                    "Also rank by meaning, not just name (e.g. 'consciousness dashboard' → "
                    "Devboard). Uses local embeddings; slower first call. Degrades to lexical "
                    "if unavailable. Default false."
                ),
            },
        },
        "required": ["query"],
    },
}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}], "isError": True}


def handle_smart_search(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Ranked, disambiguation-friendly entity search over workspace.json."""
    query = (args.get("query") or "").strip()
    kinds = args.get("kinds") or []
    scope = _normalize(args.get("scope") or "")
    limit = max(1, int(args.get("limit", 8)))
    min_score = float(args.get("min_score", 5.0))
    semantic = bool(args.get("semantic", False))

    if not query:
        return _err("'query' is required.")

    ws = _load_workspace()
    if ws is None:
        return _err("Workspace not found at ~/.mind-desktop/workspace.json")

    nodes = ws.get("nodes", [])
    query_norm = _normalize(query)
    tokens = query_norm.split()

    # ── Optional semantic query vector ──
    q_emb = None
    semantic_note = ""
    if semantic:
        q_emb = get_embedding(query) if get_embedding is not None else None
        if q_emb is None:
            semantic_note = "semantic requested but embeddings unavailable — lexical only"

    scored: List[Tuple[float, List[str], Dict]] = []
    for node in nodes:
        if scope and scope not in (node.get("id") or "").lower():
            continue
        if not _matches_kinds(node, kinds):
            continue
        score, reasons = _score(node, query_norm, tokens)

        # Semantic boost — surfaces meaning-matches even with zero name overlap.
        if q_emb is not None:
            node_emb = _node_embedding(node)
            if node_emb is not None and cosine_similarity is not None:
                sim = cosine_similarity(q_emb, node_emb)
                if sim >= 0.3:
                    score += sim * 50.0
                    reasons.append(f"semantic ~{int(sim * 100)}%")

        if score > 0:
            scored.append((score, reasons, node))

    scored.sort(key=lambda x: -x[0])

    strong = [s for s in scored if s[0] >= min_score]
    fallback_used = False
    if not strong and scored:
        # Nothing crossed the bar — show the closest few anyway rather than nothing.
        strong = scored[:3]
        fallback_used = True

    top = strong[:limit]

    # ── Header ──
    filt = []
    if kinds:
        filt.append(f"kinds={kinds}")
    if scope:
        filt.append(f"scope='{scope}'")
    if semantic and not semantic_note:
        filt.append("semantic=on")
    filt_str = f"  ({', '.join(filt)})" if filt else ""

    out: List[str] = [f"# smart_search: \"{query}\"{filt_str}"]
    if semantic_note:
        out.append(f"\n⚠ {semantic_note}")
    if not scored:
        out.append("\nNo candidates matched. Try a shorter fragment, drop the `kinds` filter, "
                    "or check spelling. (Search is accent/typo-tolerant but needs *some* overlap.)")
        out.append(f"\n---\nWorkspace: {len(nodes)} nodes, {len(ws.get('links', []))} links")
        return {"content": [{"type": "text", "text": "\n".join(out)}]}

    if fallback_used:
        out.append(f"\nNo strong match (all below score {min_score:g}). Closest candidates:")
    else:
        out.append(f"\n{len(strong)} candidate(s), showing top {len(top)}:")
    out.append("")

    for rank, (score, reasons, node) in enumerate(top, 1):
        neighbors = _expand_neighbors(ws, {node["id"]}, depth=1)
        links_str = ", ".join(
            n.get("name") or n.get("id") or "?" for n in neighbors[:4]
        )
        out.append(_format_candidate(rank, score, node, reasons, links_str))
        out.append("")

    out.append(f"---\nWorkspace: {len(nodes)} nodes, {len(ws.get('links', []))} links")
    return {"content": [{"type": "text", "text": "\n".join(out)}]}
