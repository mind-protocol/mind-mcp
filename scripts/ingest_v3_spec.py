"""
Incremental V3 Spec Ingestion — reads conversation in blocks,
extracts atomic nodes, writes to workspace.json after each block.

Uses Gemini (via think tool pattern) to decompose each block into
atomic L3 nodes following the schema.

Usage:
    python scripts/ingest_v3_spec.py
"""

import json
import os
import sys
import re
import hashlib
from pathlib import Path

WORKSPACE_PATH = Path("C:/Users/reyno/.mind-desktop/workspace.json")
CONV_PATH = Path("C:/Users/reyno/mind-protocol-v3/data/import/v3_specification_conversation.txt")
BLOCK_SIZE = 80  # lines per block


def load_workspace():
    if WORKSPACE_PATH.exists():
        with open(WORKSPACE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"nodes": [], "links": []}


def save_workspace(ws):
    with open(WORKSPACE_PATH, "w", encoding="utf-8") as f:
        json.dump(ws, f, indent=2, ensure_ascii=False, default=str)


def slug(text):
    """Convert text to a valid slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9_\s]', '', s)
    s = re.sub(r'\s+', '_', s)
    return s[:50]


def make_id(node_type, scope, name_text):
    """Create deterministic ID from type:scope:slug."""
    s = slug(name_text)
    if not s:
        s = hashlib.md5(name_text.encode()).hexdigest()[:8]
    return f"{node_type}:{scope}:{s}"


def extract_nodes_from_block(lines, existing_ids):
    """Extract atomic knowledge nodes from a block of conversation text.

    This is rule-based extraction — no LLM needed.
    Patterns we look for:
    - Law N references → thing:physics:law_N
    - Faille/Failure FN → narrative:v2:failure_FN
    - Decisions (VALIDÉ/REJETÉ/RECADRAGE) → narrative:decision:*
    - Constants (UPPER_CASE_WITH_UNDERSCORES) → thing:physics:constant_name
    - Formulas (= clamp(...)) → thing:physics:formula_name
    - Module references → space:app:module_name
    - Pathology PN → narrative:problem:pathology_pN
    - Concepts in quotes or bold → narrative:spec:concept_name
    """
    nodes = []
    links = []
    text = "\n".join(lines)

    # --- Laws ---
    for m in re.finditer(r'(?:Loi|Law)\s+(\d+)\s*[\(:]?\s*([^)\n.]{5,60})', text):
        law_num = m.group(1)
        law_desc = m.group(2).strip().rstrip(')')
        nid = f"thing:physics:law_{law_num}"
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": f"Law {law_num}: {law_desc}",
                "node_type": "thing",
                "subtype": "physics_law",
                "status": None,
                "energy": 0.5,
                "weight": 1.0,
                "synthesis": f"Physics Law {law_num} — {law_desc}. One of 21 laws governing the L1 cognitive substrate.",
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)
            links.append({"source": nid, "target": "space:app:tick_engine", "relation": "contributes_to", "weight": 1.0})

    # --- Failures/Failles ---
    for m in re.finditer(r'(?:Faille|Failure|faille)\s+F(\d+)\s*[\(:]?\s*([^)\n.]{5,80})', text):
        fnum = m.group(1)
        fdesc = m.group(2).strip().rstrip(')')
        nid = f"narrative:v2:failure_f{fnum}"
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": f"V2 Failure F{fnum}: {fdesc}",
                "node_type": "narrative",
                "subtype": "problem",
                "status": None,
                "energy": 0.3,
                "weight": 0.7,
                "synthesis": f"V2 structural failure F{fnum} — {fdesc}. Identified in V2 assessment as broken guarantee loop.",
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)

    # --- Pathologies ---
    for m in re.finditer(r'(?:P|Patholog[ie]+)\s*(\d+)\s*[\(:]?\s*([^)\n.]{5,80})', text):
        pnum = m.group(1)
        pdesc = m.group(2).strip().rstrip(')')
        nid = f"narrative:health:pathology_p{pnum}"
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": f"Pathology P{pnum}: {pdesc}",
                "node_type": "narrative",
                "subtype": "problem",
                "status": None,
                "energy": 0.4,
                "weight": 0.8,
                "synthesis": f"Cognitive pathology P{pnum} — {pdesc}. Detectable via graph signatures in HEALTH framework.",
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)

    # --- Constants (UPPER_CASE names) ---
    for m in re.finditer(r'\b([A-Z][A-Z_]{3,30}(?:_[A-Z]+)*)\b', text):
        const_name = m.group(1)
        # Filter out common non-constant words
        if const_name in ("CLAUDE", "FAST", "SLOW", "EMIT", "CONSUME", "SEEKING", "BRANCHING",
                          "HEALTH", "SYNC", "RESULTS", "OBJECTIVES", "PATTERNS", "BEHAVIORS",
                          "ALGORITHM", "VALIDATION", "IMPLEMENTATION", "DRAFT", "STABLE",
                          "EXPANDED", "VALIDÉ", "ALERTE", "VIOLATION", "ERREUR", "MCP",
                          "THINK", "ACT", "SPEAK", "STOP", "TODO", "NOTE", "PROMPT",
                          "NOT", "AND", "THE", "FOR", "ALL", "NEW", "NONE", "NULL"):
            continue
        nid = f"thing:physics:{const_name.lower()}"
        if nid not in existing_ids:
            # Find context around the constant
            ctx_match = re.search(rf'{const_name}\s*[\(=:]\s*([^)\n]{{3,60}})', text)
            ctx = ctx_match.group(1).strip() if ctx_match else ""
            nodes.append({
                "id": nid,
                "name": const_name,
                "node_type": "thing",
                "subtype": "constant",
                "status": None,
                "energy": 0.3,
                "weight": 0.8,
                "synthesis": f"Physics constant {const_name}. {ctx}".strip(),
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)
            links.append({"source": nid, "target": "space:app:tick_engine", "relation": "contributes_to", "weight": 0.6})

    # --- Key concepts (bold or quoted terms) ---
    for m in re.finditer(r'"([^"]{5,80})"', text):
        concept = m.group(1).strip()
        if len(concept) < 8 or concept.startswith("http"):
            continue
        nid = make_id("narrative", "spec", concept)
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": concept,
                "node_type": "narrative",
                "subtype": "spec",
                "status": None,
                "energy": 0.4,
                "weight": 0.6,
                "synthesis": concept,
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)

    # --- Architectural decisions (VALIDÉ/REJETÉ sections) ---
    for m in re.finditer(r'(?:VALIDÉ|REJETÉ|RECADRAGE|DÉCISION|Decision)\s*:?\s*([^\n]{5,100})', text):
        decision = m.group(1).strip()
        nid = make_id("narrative", "decision", decision)
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": decision,
                "node_type": "narrative",
                "subtype": "decision",
                "status": None,
                "energy": 0.6,
                "weight": 0.9,
                "synthesis": f"Architectural decision: {decision}",
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)

    # --- Module/tool references ---
    modules = {
        "tick_engine": "space:app:tick_engine",
        "devboard": "space:app:devboard",
        "floor_channel": "space:app:floor_channel",
        "mcp_bridge": "space:app:mcp_bridge",
        "conversation": "space:app:conversation",
        "mind_desktop": "space:app:mind_desktop",
        "chrome_sentinel": "space:app:chrome_sentinel",
    }
    for mod_name, mod_id in modules.items():
        if mod_name.replace("_", " ") in text.lower() or mod_name in text.lower():
            if mod_id not in existing_ids:
                nodes.append({
                    "id": mod_id,
                    "name": mod_name.replace("_", " ").title(),
                    "node_type": "space",
                    "subtype": "module",
                    "status": None,
                    "energy": 0.7,
                    "weight": 0.8,
                    "synthesis": f"Module: {mod_name}",
                    "blocked_by": None,
                    "assigned_to": None,
                })
                existing_ids.add(mod_id)

    # --- Paragraph-level semantic nodes (each substantial paragraph = 1 node) ---
    paragraphs = re.split(r'\n\s*\n', text)
    for para in paragraphs:
        para = para.strip()
        if len(para) < 100:  # Skip short fragments
            continue
        # First sentence as name, full para as synthesis
        first_sentence = re.split(r'[.!?]\s', para)[0][:100]
        if not first_sentence or len(first_sentence) < 15:
            continue
        nid = make_id("narrative", "spec", first_sentence)
        if nid not in existing_ids:
            nodes.append({
                "id": nid,
                "name": first_sentence,
                "node_type": "narrative",
                "subtype": "spec",
                "status": None,
                "energy": 0.3,
                "weight": 0.5,
                "synthesis": para[:500],
                "blocked_by": None,
                "assigned_to": None,
            })
            existing_ids.add(nid)

    return nodes, links


def main():
    # Load existing workspace
    ws = load_workspace()
    existing_ids = {n["id"] for n in ws["nodes"]}

    # Ensure base module nodes exist
    base_modules = [
        {"id": "space:app:tick_engine", "name": "Tick Engine", "node_type": "space", "subtype": "module",
         "energy": 0.9, "weight": 1.0, "synthesis": "The Heart. 17-step tick cycle, 21 physics laws. Runs in Rust."},
        {"id": "space:app:devboard", "name": "Devboard", "node_type": "space", "subtype": "module",
         "energy": 0.7, "weight": 0.8, "synthesis": "Blood Ledger. Live consciousness dashboard."},
        {"id": "space:app:mind_desktop", "name": "Mind Desktop", "node_type": "space", "subtype": "application",
         "energy": 0.9, "weight": 1.0, "synthesis": "Tauri desktop app. The Living Kernel."},
    ]
    for mod in base_modules:
        if mod["id"] not in existing_ids:
            mod.update({"status": None, "blocked_by": None, "assigned_to": None})
            ws["nodes"].append(mod)
            existing_ids.add(mod["id"])

    # Read conversation
    with open(CONV_PATH, encoding="utf-8") as f:
        all_lines = f.readlines()

    total_lines = len(all_lines)
    total_new_nodes = 0
    total_new_links = 0
    block_num = 0

    print(f"Processing {total_lines} lines in blocks of {BLOCK_SIZE}...")

    for i in range(0, total_lines, BLOCK_SIZE):
        block = all_lines[i:i + BLOCK_SIZE]
        block_num += 1

        new_nodes, new_links = extract_nodes_from_block(
            [l.rstrip() for l in block], existing_ids
        )

        if new_nodes or new_links:
            ws["nodes"].extend(new_nodes)
            ws["links"].extend(new_links)
            total_new_nodes += len(new_nodes)
            total_new_links += len(new_links)

            # Save after each block
            save_workspace(ws)

            print(f"  Block {block_num} (lines {i+1}-{i+len(block)}): "
                  f"+{len(new_nodes)} nodes, +{len(new_links)} links "
                  f"(total: {len(ws['nodes'])} nodes, {len(ws['links'])} links)")

    print(f"\nDone. {total_new_nodes} new nodes, {total_new_links} new links added.")
    print(f"Workspace: {len(ws['nodes'])} nodes, {len(ws['links'])} links")

    # Node type breakdown
    types = {}
    for n in ws["nodes"]:
        t = n.get("subtype", n.get("node_type", "?"))
        types[t] = types.get(t, 0) + 1
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
