"""
graph_query — Search the L3 workspace graph in memory.

V3: No FalkorDB, no Cypher. Pure in-memory search on workspace.json.
Searches by keyword match on id, name, content, synthesis.
Supports scope filtering and topological expansion.

Usage via MCP:
    graph_query(queries=["tick engine", "devboard"])
    graph_query(queries=["GraphCare"], scope_filter="module_graphcare")
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.graph_query")

WORKSPACE_PATH = Path.home() / ".mind-desktop" / "workspace.json"


def _load_workspace():
    """Load workspace.json into memory."""
    if not WORKSPACE_PATH.exists():
        return None
    try:
        with open(WORKSPACE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load workspace: {e}")
        return None


def _score_node(node: Dict, keywords: List[str], scope_filter: Optional[str] = None) -> float:
    """Score a node against search keywords. Higher = better match."""
    if scope_filter and scope_filter not in node.get("id", ""):
        return 0.0

    score = 0.0
    searchable = " ".join([
        node.get("id") or "",
        node.get("name") or "",
        node.get("content") or "",
        node.get("synthesis") or "",
    ]).lower()

    for kw in keywords:
        kw_lower = kw.lower()
        # Exact match in ID = highest score
        if kw_lower in (node.get("id") or "").lower():
            score += 3.0
        # Match in name
        if kw_lower in (node.get("name") or "").lower():
            score += 2.0
        # Match in content/synthesis
        if kw_lower in searchable:
            score += 1.0

    return score


def _expand_neighbors(ws: Dict, node_ids: set, depth: int = 1) -> List[Dict]:
    """Find neighboring nodes connected by links."""
    if depth <= 0:
        return []

    neighbors = []
    seen = set(node_ids)

    for link in ws.get("links", []):
        src = link.get("source_id") or link.get("source") or ""
        tgt = link.get("target_id") or link.get("target") or ""

        if src in node_ids and tgt not in seen:
            seen.add(tgt)
            node = next((n for n in ws["nodes"] if n["id"] == tgt), None)
            if node:
                neighbors.append(node)
        elif tgt in node_ids and src not in seen:
            seen.add(src)
            node = next((n for n in ws["nodes"] if n["id"] == src), None)
            if node:
                neighbors.append(node)

    return neighbors


def _format_node(node: Dict) -> str:
    """Format a node for display."""
    nid = node.get("id") or "?"
    name = node.get("name") or "?"
    ntype = node.get("node_type") or "?"
    subtype = node.get("subtype") or node.get("type") or ""
    energy = node.get("energy") or 0
    weight = node.get("weight") or 0
    content = node.get("content") or node.get("synthesis") or ""

    # Try to parse JSON content for description
    desc = content
    if content and content.startswith("{"):
        try:
            parsed = json.loads(content)
            desc = parsed.get("_description") or content
        except (json.JSONDecodeError, TypeError):
            pass

    # Truncate
    if len(desc) > 300:
        desc = desc[:297] + "..."

    type_str = f"{ntype}"
    if subtype:
        type_str += f"/{subtype}"

    return f"[{type_str}] {name}\n  ID: {nid}\n  W={weight:.1f} E={energy:.1f}\n  {desc}"


# ─── Tool Schema ──────────────────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "graph_query",
    "description": (
        "[THINK] Search the L3 workspace graph by keywords. "
        "Returns matching nodes with their content. "
        "Use scope_filter to narrow to a module (e.g. 'module_graphcare'). "
        "Use expand_depth to include neighbors."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords to search for (e.g. ['tick engine', 'devboard'])",
            },
            "scope_filter": {
                "type": "string",
                "description": "Filter to nodes whose ID contains this scope (e.g. 'module_graphcare', 'taxonomy')",
            },
            "node_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by node_type (e.g. ['narrative', 'space'])",
            },
            "expand_depth": {
                "type": "integer",
                "description": "Include neighbors up to this depth (default 0, max 2)",
            },
            "limit": {
                "type": "integer",
                "description": "Max results per query (default 10)",
            },
        },
        "required": ["queries"],
    },
}


def handle_graph_query(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Search the workspace graph by keywords — no FalkorDB, pure in-memory."""
    queries = args.get("queries", [])
    scope_filter = args.get("scope_filter")
    node_types = args.get("node_types")
    expand_depth = min(args.get("expand_depth", 0), 2)
    limit = args.get("limit", 10)

    if not queries:
        return _err("'queries' array is required.")

    ws = _load_workspace()
    if ws is None:
        return _err("Workspace not found at ~/.mind-desktop/workspace.json")

    nodes = ws.get("nodes", [])
    output_lines = []

    for i, query in enumerate(queries, 1):
        if not query or not isinstance(query, str):
            output_lines.append(f"## Query {i}: (skipped — empty or non-string)")
            output_lines.append("")
            continue
        keywords = query.lower().split()

        # Score all nodes
        scored = []
        for node in nodes:
            # Type filter
            if node_types and node.get("node_type") not in node_types:
                continue

            score = _score_node(node, keywords, scope_filter)
            if score > 0:
                scored.append((score, node))

        # Sort by score descending
        scored.sort(key=lambda x: -x[0])
        top = scored[:limit]

        output_lines.append(f"## Query {i}: {query}")
        output_lines.append(f"Found {len(scored)} matches (showing top {len(top)})\n")

        matched_ids = set()
        for score, node in top:
            output_lines.append(_format_node(node))
            output_lines.append("")
            matched_ids.add(node["id"])

        # Expand neighbors
        if expand_depth > 0 and matched_ids:
            neighbors = _expand_neighbors(ws, matched_ids, expand_depth)
            if neighbors:
                output_lines.append(f"### Neighbors (depth {expand_depth}): {len(neighbors)} nodes\n")
                for n in neighbors[:10]:
                    output_lines.append(f"  → [{n.get('node_type') or '?'}] {n.get('name') or '?'} ({n.get('id') or '?'})")
                output_lines.append("")

    # Stats
    output_lines.append(f"\n---\nWorkspace: {len(nodes)} nodes, {len(ws.get('links', []))} links")

    return {"content": [{"type": "text", "text": "\n".join(output_lines)}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}], "isError": True}
