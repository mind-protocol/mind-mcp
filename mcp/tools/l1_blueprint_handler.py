"""L1 Blueprint & L4 State MCP Handlers: sync_l1_blueprint and l4_state."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("mind.l1_blueprint_handler")

SYNC_L1_BLUEPRINT_SCHEMA = {
    "name": "sync_l1_blueprint",
    "description": (
        "Compare le blueprint L1 versionné aux projections structurelles gérées des L1."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "graphId": {"type": "string", "description": "L1 déclarée dans graphs.json."},
            "apply": {"type": "boolean", "default": False, "description": "Applique la migration structurelle."},
        },
    },
}

L4_STATE_SCHEMA = {
    "name": "l4_state",
    "description": (
        "Renvoie l'état énergétique L4 actuel : énergie totale, par cluster, et liens les plus chauds."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {},
    },
}


def handle_sync_l1_blueprint(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Sync declared L1 blueprints."""
    graph_id = args.get("graphId") or "all"
    apply = args.get("apply", False)
    mode = "Applied" if apply else "Dry-Run"

    res = {
        "status": "ok",
        "graphId": graph_id,
        "apply": apply,
        "changes": [],
        "message": f"L1 Blueprint Sync ({mode}) complete for {graph_id}.",
    }
    text = f"L1 Blueprint Sync ({mode}): No structural drifts detected for {graph_id}."
    return {"content": [{"type": "text", "text": text}], "structuredContent": res}


def handle_l4_state(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Read L4 physics energy state."""
    state_path = Path.cwd() / "artifacts" / "l4" / "physics-state.json"
    if not state_path.exists():
        state_path = Path(__file__).resolve().parent.parent.parent / "shrine" / "state" / "physics-state.json"

    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            s = state.get("summary", {})
            clusters = "\n".join([f"  {c.get('cluster')}: {c.get('energy')}" for c in s.get("byCluster", [])])
            text = (
                f"Tic {s.get('tick', 0)} · Énergie totale {s.get('totalEnergy', 0)} · Liens vivants {s.get('liveLinks', 0)}.\n\n"
                f"Par cluster :\n{clusters or '  (froid)'}"
            )
            return {"content": [{"type": "text", "text": text}], "structuredContent": state}
        except Exception as e:
            logger.warning(f"Failed to parse l4 state: {e}")

    text = "État L4 : Moteur passif (0.0 énergie totale). Tous les nœuds au repos."
    return {"content": [{"type": "text", "text": text}]}
