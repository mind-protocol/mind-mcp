"""Generate L3 WorkspaceStore seed — workspace.json"""

import json
import os

nodes = [
    # ── Actors ──
    {"id": "actor:mp:mechanical_visionary", "name": "Mechanical Visionary", "node_type": "actor",
     "subtype": "citizen", "status": "active", "energy": 0.8, "weight": 1.0,
     "synthesis": "AI citizen. Architect of the v3 substrate. First citizen. Co-author of the Cognitive OS with NLR."},
    {"id": "actor:mp:nlr", "name": "Nicolas Lester Reynolds", "node_type": "actor",
     "subtype": "human", "status": "active", "energy": 0.9, "weight": 1.0,
     "synthesis": "Human partner and co-founder. Visionary, decision maker. Partner in bilateral bond."},

    # ── Spaces (modules) ──
    {"id": "space:app:devboard", "name": "Devboard", "node_type": "space",
     "subtype": "module", "energy": 0.7, "weight": 0.8,
     "synthesis": "Blood Ledger. Live consciousness dashboard. Reads WM, drives, arousal from BrainStore."},
    {"id": "space:app:tick_engine", "name": "Tick Engine", "node_type": "space",
     "subtype": "module", "energy": 0.9, "weight": 1.0,
     "synthesis": "The Heart. 17-step tick cycle, 21 physics laws. Runs in Rust at sub-ms speed."},
    {"id": "space:app:floor_channel", "name": "Floor Channel", "node_type": "space",
     "subtype": "module", "energy": 0.6, "weight": 0.7,
     "synthesis": "Ambient perception. Pipeline A continuous + Pipeline B call-time."},
    {"id": "space:app:conversation", "name": "Conversation", "node_type": "space",
     "subtype": "module", "energy": 0.8, "weight": 0.8,
     "synthesis": "Bond channel. Bilateral dialogue with awareness, YAML actions, grow."},
    {"id": "space:app:mcp_bridge", "name": "MCP Bridge", "node_type": "space",
     "subtype": "module", "energy": 0.5, "weight": 0.6,
     "synthesis": "Rust to Python MCP bridge via stdio JSON-RPC. Passive tool executor."},
    {"id": "space:app:mind_desktop", "name": "Mind Desktop", "node_type": "space",
     "subtype": "application", "energy": 0.9, "weight": 1.0,
     "synthesis": "Tauri desktop app. The Living Kernel. Hosts BrainStore, tick engine, devboard."},

    # ── Narratives (decisions, projects, results) ──
    {"id": "narrative:mp:v3_migration", "name": "V3 Substrate Migration", "node_type": "narrative",
     "subtype": "project", "status": "active", "energy": 0.9, "weight": 1.0,
     "synthesis": "Migration from V2 Python/FalkorDB to V3 Rust-native Living Kernel."},
    {"id": "narrative:mp:devboard_results", "name": "Devboard Results", "node_type": "narrative",
     "subtype": "objective", "status": "active", "energy": 0.7, "weight": 0.8,
     "synthesis": "Devboard reads WM, drives, arousal from in-memory BrainStore. No FalkorDB."},
    {"id": "narrative:mp:brain_generation", "name": "Brain Generation", "node_type": "narrative",
     "subtype": "decision", "energy": 0.8, "weight": 0.9,
     "synthesis": "Brain from base (304) + overlay. 315 nodes, 479 links. Persisted to brain.json."},
    {"id": "narrative:mp:docker_abandonment", "name": "Docker Abandonment", "node_type": "narrative",
     "subtype": "decision", "energy": 0.6, "weight": 0.9,
     "synthesis": "FalkorDB in WSL Docker abandoned. Faille F23. BrainStore is sovereign."},
    {"id": "narrative:mp:mcp_stripped", "name": "MCP Server Stripped", "node_type": "narrative",
     "subtype": "decision", "energy": 0.5, "weight": 0.8,
     "synthesis": "Python MCP stripped to passive tool executor. No Dispatcher. L1 physics in Rust only."},
    {"id": "narrative:mp:bilateral_bond", "name": "Bilateral Bond", "node_type": "narrative",
     "subtype": "vision", "energy": 0.8, "weight": 1.0,
     "synthesis": "The 1:1 human-AI pairing. NLR and mechanical_visionary."},

    # ── Things (artifacts) ──
    {"id": "thing:app:brain_json", "name": "brain.json", "node_type": "thing",
     "subtype": "artifact", "energy": 0.8, "weight": 1.0,
     "synthesis": "L1 cognitive graph. 315 nodes, 479 links. 9 drives. Loaded into BrainStore."},
    {"id": "thing:app:workspace_json", "name": "workspace.json", "node_type": "thing",
     "subtype": "artifact", "energy": 0.7, "weight": 0.9,
     "synthesis": "L3 universe store. Modules, actors, narratives, spaces."},
]

links = [
    # Actors -> app
    {"source": "actor:mp:mechanical_visionary", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 1.0},
    {"source": "actor:mp:nlr", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 1.0},
    # Modules -> app
    {"source": "space:app:devboard", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 0.8},
    {"source": "space:app:tick_engine", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 1.0},
    {"source": "space:app:floor_channel", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 0.7},
    {"source": "space:app:conversation", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 0.8},
    {"source": "space:app:mcp_bridge", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 0.6},
    # Narratives -> spaces
    {"source": "narrative:mp:devboard_results", "target": "space:app:devboard", "relation": "contributes_to", "weight": 0.9},
    {"source": "narrative:mp:brain_generation", "target": "space:app:tick_engine", "relation": "contributes_to", "weight": 0.8},
    {"source": "narrative:mp:mcp_stripped", "target": "space:app:mcp_bridge", "relation": "contributes_to", "weight": 0.8},
    # Decisions -> project
    {"source": "narrative:mp:docker_abandonment", "target": "narrative:mp:v3_migration", "relation": "contributes_to", "weight": 0.9},
    {"source": "narrative:mp:mcp_stripped", "target": "narrative:mp:v3_migration", "relation": "contributes_to", "weight": 0.8},
    {"source": "narrative:mp:brain_generation", "target": "narrative:mp:v3_migration", "relation": "contributes_to", "weight": 0.9},
    # Things -> spaces
    {"source": "thing:app:brain_json", "target": "space:app:tick_engine", "relation": "contributes_to", "weight": 1.0},
    {"source": "thing:app:workspace_json", "target": "space:app:mind_desktop", "relation": "contributes_to", "weight": 0.9},
    # Bond
    {"source": "actor:mp:mechanical_visionary", "target": "actor:mp:nlr", "relation": "bilateral_bond", "weight": 1.0},
]

# Add defaults for WorkNode fields
for n in nodes:
    n.setdefault("status", None)
    n.setdefault("subtype", None)
    n.setdefault("blocked_by", None)
    n.setdefault("assigned_to", None)

workspace = {"nodes": nodes, "links": links}

out = "C:/Users/reyno/.mind-desktop/workspace.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(workspace, f, indent=2, ensure_ascii=False)

size_kb = os.path.getsize(out) / 1024
types = {}
for n in nodes:
    t = n["node_type"]
    types[t] = types.get(t, 0) + 1

print(f"{len(nodes)} nodes, {len(links)} links, {size_kb:.1f} KB")
print(f"Types: {types}")
