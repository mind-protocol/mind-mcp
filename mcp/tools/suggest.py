"""
Fuzzy entity-suggestion helper — shared across MCP tool handlers.

When an entity lookup fails (a graph node, an Actor, a Space, a Task, an
alarm…), a tool should not stop at "not found". It should return an ordered
list of the closest-resembling entities so the caller can recover from a typo
or a slightly-wrong id — e.g. asking for `lumina_ai_graph` when the real node
is `lumina-ai-graphe` yields a ranked "Did you mean…?" list.

Candidate sources:
  • workspace.json (in-memory L3 store) — load_workspace_nodes()
  • FalkorDB (Cypher)                    — graph_candidates()

Matching uses rapidfuzz when available, falling back to stdlib difflib so the
suggestion path never itself raises ImportError. Every function is written to
degrade to an empty result rather than raise — a broken suggestion must never
turn a clean "not found" into a crash.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger("mind.suggest")

WORKSPACE_PATH = Path.home() / ".mind-desktop" / "workspace.json"


# ── Scorer: rapidfuzz preferred, difflib fallback ──────────────────────────
try:
    from rapidfuzz import fuzz as _rf_fuzz

    def _similarity(a: str, b: str) -> float:
        """Similarity between two strings on a 0–100 scale."""
        return float(_rf_fuzz.WRatio(a, b))

    BACKEND = "rapidfuzz"
except ImportError:  # pragma: no cover — fallback when rapidfuzz not installed
    from difflib import SequenceMatcher

    def _similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100.0

    BACKEND = "difflib"


# ── Ranking ─────────────────────────────────────────────────────────────────

def rank_candidates(
    query: str,
    candidates: Iterable[Dict[str, Any]],
    *,
    limit: int = 5,
    cutoff: float = 55.0,
) -> List[Dict[str, Any]]:
    """Rank candidates by resemblance to ``query``, best first.

    Each candidate is a dict with at least an ``id``; ``name`` is scored too
    when present, and the best of the two fields wins. Returns shallow copies
    with an added ``score`` float (0–100). Never raises.
    """
    if not query:
        return []
    q = str(query)
    scored: List[Dict[str, Any]] = []
    for cand in candidates:
        try:
            cid = str(cand.get("id") or "")
            name = str(cand.get("name") or "")
            best = 0.0
            for field in (cid, name):
                if field:
                    s = _similarity(q, field)
                    if s > best:
                        best = s
            if best >= cutoff:
                scored.append({**cand, "score": best})
        except Exception:
            continue
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:limit]


def suggestion_block(
    query: str,
    kind: str,
    candidates: Iterable[Dict[str, Any]],
    *,
    limit: int = 5,
    cutoff: float = 55.0,
) -> str:
    """Build a "Did you mean…?" text block, or ``""`` if nothing resembles.

    Returned with a leading blank line so it can be appended directly to an
    existing not-found error string.
    """
    ranked = rank_candidates(query, candidates, limit=limit, cutoff=cutoff)
    if not ranked:
        return ""
    lines = [f"\n\nDid you mean one of these {kind}s?"]
    for r in ranked:
        cid = str(r.get("id") or "")
        name = str(r.get("name") or "")
        label = f"{cid}  ({name})" if name and name != cid else cid
        lines.append(f"  • {label}  — {r['score']:.0f}% match")
    return "\n".join(lines)


# ── Candidate sources ────────────────────────────────────────────────────────

def load_workspace_nodes(path: Path = WORKSPACE_PATH) -> List[Dict[str, Any]]:
    """Return the node list from workspace.json, or ``[]`` on any failure."""
    try:
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            ws = json.load(f)
        nodes = ws.get("nodes", [])
        return nodes if isinstance(nodes, list) else []
    except Exception as e:
        logger.debug(f"load_workspace_nodes failed: {e}")
        return []


def graph_candidates(
    graph_ops: Any,
    *,
    label: Optional[str] = None,
    where: Optional[str] = None,
    limit: int = 2000,
) -> List[Dict[str, Any]]:
    """Enumerate ``{id, name}`` pairs from FalkorDB via ``graph_ops._query``.

    ``label`` and ``where`` are trusted — they come from handler code, never
    from user input. ``label`` is still guarded to an identifier as a safety
    net against accidental Cypher injection. Returns ``[]`` on any failure.
    """
    if graph_ops is None:
        return []
    lbl = ""
    if label:
        if not str(label).replace("_", "").isalnum():
            logger.debug(f"graph_candidates: rejecting non-identifier label {label!r}")
            return []
        lbl = f":{label}"
    clause = f"WHERE {where} " if where else ""
    query = f"MATCH (n{lbl}) {clause}RETURN n.id, n.name LIMIT {int(limit)}"
    try:
        rows = graph_ops._query(query) or []
    except Exception as e:
        logger.debug(f"graph_candidates query failed: {e}")
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        try:
            if isinstance(row, (list, tuple)):
                cid = row[0]
                name = row[1] if len(row) > 1 else None
            elif isinstance(row, dict):
                cid = row.get("n.id")
                name = row.get("n.name")
            else:
                cid, name = row, None
            if cid:
                out.append({"id": cid, "name": name})
        except Exception:
            continue
    return out
