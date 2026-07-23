"""[THINK] Sense — return attention plus the citizen's situated environment.

The Global Workspace says what currently occupies attention. Direct Space
presence says what is around the citizen without implying that it is already
conscious. The two sources remain explicitly separated in the returned JSON.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable

from runtime.permissions.access_check import detect_citizen_handle

logger = logging.getLogger("mind.sense")

_MIND_MCP_ROOT = Path(__file__).resolve().parent.parent.parent
MAX_SITUATED_SPACES = 16
MAX_NODES_PER_SPACE = 100


TOOL_SCHEMA = {
    "name": "sense",
    "description": (
        "Read your current Global Workspace and the nodes present in Spaces "
        "where you are explicitly located."
    ),
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    "inputSchema": {
        "type": "object",
        "properties": {
            "handle": {
                "type": "string",
                "description": "Citizen handle. Auto-detected if omitted.",
            },
        },
    },
}


def handle_sense(args: dict, ctx=None) -> Dict[str, Any]:
    """Return attention and directly situated nodes without conflating them."""
    citizen_handle = _normalize_handle(args.get("handle") or detect_citizen_handle())

    workspace = _read_global_workspace(citizen_handle)
    if workspace is not None:
        result = dict(workspace)
        result["situatedEnvironment"] = _read_situated_environment(
            citizen_handle,
            actor_id=workspace.get("actorId"),
        )
        return _ok(json.dumps(result, ensure_ascii=False, indent=2))

    if not getattr(ctx, "disable_home_bridge", False):
        remote_text = _read_home_server_workspace(citizen_handle)
        if remote_text:
            return _ok(remote_text)

    who = citizen_handle or "undetected citizen"
    return _ok(
        json.dumps(
            {
                "status": "unavailable",
                "citizen": who,
                "reason": "No current Global Workspace was found for this citizen.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def _workspace_path_candidates() -> Iterable[Path]:
    """Yield configured and conventional Global Workspace locations."""
    seen: set[Path] = set()
    configured = (
        os.environ.get("MIND_GLOBAL_WORKSPACE_PATH", "").strip(),
        os.environ.get("GLOBAL_WORKSPACE_PATH", "").strip(),
    )
    conventional = (
        _MIND_MCP_ROOT.parent / "body-suit" / "artifacts" / "autonomy" / "global-workspace.json",
        Path.cwd() / "artifacts" / "autonomy" / "global-workspace.json",
    )
    for raw_path in (*configured, *conventional):
        if not raw_path:
            continue
        path = Path(raw_path).expanduser().resolve()
        if path not in seen:
            seen.add(path)
            yield path


def _read_global_workspace(citizen_handle: str) -> dict | None:
    """Read the citizen workspace from the canonical persisted workspace file."""
    citizen_handle = _normalize_handle(citizen_handle)
    for path in _workspace_path_candidates():
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Cannot read Global Workspace at %s: %s", path, exc)
            continue

        workspace = _select_citizen_workspace(payload, citizen_handle)
        if workspace is not None:
            return workspace
    return None


def _select_citizen_workspace(payload: Any, citizen_handle: str) -> dict | None:
    """Select one bounded citizen workspace without inventing missing state."""
    if not isinstance(payload, dict):
        return None

    citizens = payload.get("citizens")
    if not isinstance(citizens, dict):
        return payload if _workspace_matches(payload, citizen_handle) else None

    if citizen_handle:
        for citizen_id, workspace in citizens.items():
            if not isinstance(workspace, dict):
                continue
            if _normalize_handle(citizen_id) == citizen_handle:
                return workspace
            if _workspace_matches(workspace, citizen_handle):
                return workspace

    if not citizen_handle and len(citizens) == 1:
        only_workspace = next(iter(citizens.values()))
        return only_workspace if isinstance(only_workspace, dict) else None
    return None


def _workspace_matches(workspace: dict, citizen_handle: str) -> bool:
    if not citizen_handle:
        return False
    identities = (
        workspace.get("actorId"),
        workspace.get("citizenId"),
        (workspace.get("sense") or {}).get("handle")
        if isinstance(workspace.get("sense"), dict)
        else None,
    )
    return any(_normalize_handle(identity) == citizen_handle for identity in identities if identity)


def _read_home_server_workspace(citizen_handle: str) -> str:
    """Fallback for MCP processes that do not share the workspace filesystem."""
    if not citizen_handle:
        return ""
    base_url = os.environ.get("MIND_HOME_SERVER_URL", "http://127.0.0.1:8765").rstrip("/")
    url = f"{base_url}/api/sense/{urllib.parse.quote(citizen_handle)}"
    try:
        with urllib.request.urlopen(url, timeout=2.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return str(payload.get("text") or "").strip()
    except Exception as exc:
        logger.debug("Home Global Workspace unavailable for %s: %s", citizen_handle, exc)
        return ""


def _actor_id_candidates(citizen_handle: str, explicit_actor_id: str | None = None) -> list[str]:
    """Resolve transport handles to the actor IDs used across graph layers."""
    normalized = _normalize_handle(citizen_handle)
    slug = normalized.replace("_", "-")
    candidates = [
        explicit_actor_id,
        citizen_handle,
        normalized,
        f"actor-{slug}" if slug else None,
        f"l3-actor-{slug}" if slug else None,
        f"CITIZEN_{normalized}" if normalized else None,
        f"{normalized}_ai" if normalized else None,
    ]
    return list(dict.fromkeys(str(item) for item in candidates if item))


def _space_graph_names(db) -> list[str]:
    """Use configured graphs or every non-personal graph available locally."""
    configured = os.environ.get("MIND_SENSE_SPACE_GRAPHS", "").strip()
    if configured:
        return list(dict.fromkeys(
            name.strip() for name in configured.split(",") if name.strip()
        ))
    try:
        graph_names = [str(name) for name in db.list_graphs()]
    except Exception:
        return []
    return sorted(
        name
        for name in graph_names
        if not name.startswith(("l1_", "brain_"))
        and name not in {"nlr_ai"}
    )


def _node_projection(row) -> dict:
    return {
        "id": row[0],
        "name": row[1],
        "nodeType": row[2],
        "semanticType": row[3],
        "summary": row[4],
        "energy": row[5],
        "status": row[6],
        "presenceRelation": row[7],
    }


def _read_space_nodes(graph, space_id: str, actor_ids: list[str]) -> list[dict]:
    """Read only direct presence/containment; no nearest-neighbour inference."""
    params = {
        "space_id": space_id,
        "actor_ids": actor_ids,
        "limit": MAX_NODES_PER_SPACE,
    }
    inbound = graph.query(
        """
        MATCH (node)-[presence]->(space {id: $space_id})
        WHERE type(presence) IN ['LOCATED_IN', 'OCCURS_IN']
          AND NOT node.id IN $actor_ids
        RETURN node.id, coalesce(node.name, node.id),
               coalesce(node.nodeType, node.node_type, ''),
               coalesce(node.semanticType, node.type, ''),
               coalesce(node.summary, node.synthesis, node.content, ''),
               coalesce(node.energy, 0.0), coalesce(node.status, ''),
               type(presence)
        ORDER BY coalesce(node.energy, 0.0) DESC, node.id
        LIMIT $limit
        """,
        params,
    )
    outbound = graph.query(
        """
        MATCH (space {id: $space_id})-[presence]->(node)
        WHERE (
            type(presence) IN ['CONTAINS', 'OCCURS_IN']
            OR (
                type(presence) = 'link'
                AND coalesce(presence.hierarchy, 0.0) = -1.0
            )
        )
          AND NOT node.id IN $actor_ids
        RETURN node.id, coalesce(node.name, node.id),
               coalesce(node.nodeType, node.node_type, ''),
               coalesce(node.semanticType, node.type, ''),
               coalesce(node.summary, node.synthesis, node.content, ''),
               coalesce(node.energy, 0.0), coalesce(node.status, ''),
               type(presence)
        ORDER BY coalesce(node.energy, 0.0) DESC, node.id
        LIMIT $limit
        """,
        params,
    )
    nodes: dict[str, dict] = {}
    for row in [*(inbound.result_set or []), *(outbound.result_set or [])]:
        projection = _node_projection(row)
        if projection["id"]:
            nodes.setdefault(str(projection["id"]), projection)
    return list(nodes.values())[:MAX_NODES_PER_SPACE]


def _read_situated_environment(
    citizen_handle: str,
    *,
    actor_id: str | None = None,
    db=None,
) -> dict:
    """Read nodes in Spaces carrying an explicit citizen location."""
    actor_ids = _actor_id_candidates(citizen_handle, actor_id)
    if not actor_ids:
        return {
            "measurementStatus": "not_measured",
            "reason": "citizen_identity_unavailable",
            "spaces": [],
        }

    if db is None:
        try:
            from falkordb import FalkorDB

            db = FalkorDB(
                host=os.environ.get("FALKORDB_HOST", "localhost"),
                port=int(os.environ.get("FALKORDB_PORT", "6379")),
            )
        except Exception as exc:
            logger.debug("Situated environment database unavailable: %s", exc)
            return {
                "measurementStatus": "measurement_failed",
                "reason": "graph_database_unavailable",
                "spaces": [],
            }

    graph_names = _space_graph_names(db)
    spaces: dict[tuple[str, str], dict] = {}
    failed_graphs = 0
    queried_graphs = 0
    for graph_name in graph_names:
        try:
            graph = db.select_graph(graph_name)
            located = graph.query(
                """
                MATCH (actor)-[location:LOCATED_IN]->(space)
                WHERE actor.id IN $actor_ids
                  AND toLower(coalesce(space.nodeType, space.node_type, '')) = 'space'
                RETURN actor.id, space.id, coalesce(space.name, space.id),
                       'LOCATED_IN'
                ORDER BY actor.id, space.id
                LIMIT $limit
                """,
                {"actor_ids": actor_ids, "limit": MAX_SITUATED_SPACES},
            )
            rows = list(located.result_set or [])
            if not rows:
                by_property = graph.query(
                    """
                    MATCH (actor), (space)
                    WHERE actor.id IN $actor_ids
                      AND space.id = actor.currentSpaceId
                      AND toLower(coalesce(space.nodeType, space.node_type, '')) = 'space'
                    RETURN actor.id, space.id, coalesce(space.name, space.id),
                           'currentSpaceId'
                    ORDER BY actor.id, space.id
                    LIMIT $limit
                    """,
                    {"actor_ids": actor_ids, "limit": MAX_SITUATED_SPACES},
                )
                rows = list(by_property.result_set or [])
            queried_graphs += 1
            for row in rows:
                key = (graph_name, str(row[1]))
                spaces[key] = {
                    "graph": graph_name,
                    "actorId": row[0],
                    "id": row[1],
                    "name": row[2],
                    "locationEvidence": row[3],
                    "nodes": _read_space_nodes(graph, str(row[1]), actor_ids),
                }
                if len(spaces) >= MAX_SITUATED_SPACES:
                    break
        except Exception as exc:
            failed_graphs += 1
            logger.debug(
                "Situated environment unavailable in %s for %s: %s",
                graph_name,
                citizen_handle,
                exc,
            )
        if len(spaces) >= MAX_SITUATED_SPACES:
            break

    if spaces:
        status = "partial" if failed_graphs else "observed"
    elif queried_graphs:
        status = "unknown" if failed_graphs else "known_absent"
    else:
        status = "measurement_failed"
    return {
        "measurementStatus": status,
        "source": "explicit_space_location",
        "graphsQueried": queried_graphs,
        "graphsFailed": failed_graphs,
        "spaces": list(spaces.values()),
    }


def _normalize_handle(raw: str | None) -> str:
    """Normalize transport and actor identifiers to a comparable citizen key."""
    if not raw:
        return ""
    handle = str(raw).strip().lstrip("@").lower().replace("-", "_")
    for prefix in ("citizen_", "actor_", "l3_actor_"):
        if handle.startswith(prefix):
            handle = handle[len(prefix):]
            break
    if handle.endswith("_ai"):
        handle = handle[:-3]
    return handle.strip("_")


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}
