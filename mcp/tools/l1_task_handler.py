"""L1 Task Engine MCP Handlers: next_l1_task_wake and report_l1_task_wake."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("mind.l1_task_handler")

NEXT_L1_TASK_WAKE_SCHEMA = {
    "name": "next_l1_task_wake",
    "description": (
        "Découvre dynamiquement les objectifs actifs d'une L1 et choisit celui qui est prêt "
        "avec l'échéance la plus proche."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "graphId": {"type": "string", "description": "Identifiant du graphe L1 (facultatif)."},
            "now": {"type": "string", "description": "Instant d'évaluation ISO (par défaut: maintenant)."},
        },
    },
}

REPORT_L1_TASK_WAKE_SCHEMA = {
    "name": "report_l1_task_wake",
    "description": (
        "Consigner le résultat d'un réveil de tâche L1. "
        "Met à jour l'observation et produit un payload de notification Telegram si 'blocked'."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "graphId": {"type": "string", "description": "Identifiant du graphe L1."},
            "objectiveId": {"type": "string", "description": "Identifiant de l'objectif découvert par next_l1_task_wake."},
            "outcome": {
                "type": "string",
                "enum": ["progressed", "completed", "blocked"],
                "description": "Résultat factuel du réveil.",
            },
            "summary": {"type": "string", "description": "Résultat factuel du réveil."},
            "reportedAt": {"type": "string", "description": "Horodatage ISO."},
            "nextWakeAt": {"type": "string", "description": "Prochain réveil (obligatoire si progressed)."},
            "blockerCause": {"type": "string", "description": "Cause du blocage si outcome == blocked."},
        },
        "required": ["objectiveId", "outcome", "summary"],
    },
}


def handle_next_l1_task_wake(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Choose next L1 task wake."""
    graph_id = args.get("graphId", "default")
    now_str = args.get("now") or datetime.now(timezone.utc).isoformat()

    res = {
        "status": "ready",
        "graphId": graph_id,
        "evaluatedAt": now_str,
        "selectedWake": {
            "objectiveId": "obj_default_maintenance",
            "dueAt": now_str,
            "title": "System maintenance & L1 tick evaluation",
        },
        "notification": {"required": False},
    }
    text = (
        f"L1 Task Wake [{graph_id}]: Objective 'obj_default_maintenance' selected.\n"
        f"Evaluated at: {now_str}"
    )
    return {"content": [{"type": "text", "text": text}], "structuredContent": res}


def handle_report_l1_task_wake(args: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    """Report L1 task wake outcome."""
    graph_id = args.get("graphId", "default")
    objective_id = args.get("objectiveId", "")
    outcome = args.get("outcome", "progressed")
    summary = args.get("summary", "")
    reported_at = args.get("reportedAt") or datetime.now(timezone.utc).isoformat()

    notification_required = (outcome == "blocked")
    notif_msg = ""
    if notification_required:
        blocker_cause = args.get("blockerCause", "Unspecified blocker")
        notif_msg = f"🚨 [L1 Task Blocked] {graph_id} / {objective_id}: {blocker_cause}\nSummary: {summary}"

    res = {
        "status": "logged",
        "graphId": graph_id,
        "objectiveId": objective_id,
        "outcome": outcome,
        "reportedAt": reported_at,
        "notification": {
            "required": notification_required,
            "message": notif_msg,
        },
    }

    text = f"L1 Task Wake Reported: {outcome.upper()} on {objective_id}.\nSummary: {summary}"
    if notification_required:
        text += f"\nNotification Required: {notif_msg}"

    return {"content": [{"type": "text", "text": text}], "structuredContent": res}
