"""MCP adapter for question-driven recall over one sovereign L1 Space."""

from __future__ import annotations

import json
import hashlib
import logging
import os
import re
import time
import unicodedata
import uuid
from typing import Any, Iterable

from runtime.cognition.interoception_snapshot import resolve_l1_graph_name
from runtime.cognition.recall import (
    DEFAULT_MAX_TICKS,
    DEFAULT_RECALL_ENERGY,
    MAX_RECALL_ENERGY,
    MIN_RECALL_ENERGY,
    RecallGraphLink,
    RecallGraphNode,
    parse_embedding,
    run_recall,
)
from runtime.permissions.access_check import detect_citizen_handle

logger = logging.getLogger("mind.recall")
VIRTUAL_L1_SPACE_PREFIX = "space:l1-graph:"


TOOL_SCHEMA = {
    "name": "recall",
    "description": (
        "[THINK] Ask a question of your own L1. Creates a central Recall Moment, "
        "includes every node in the selected Space stimulus, injects bounded "
        "energy, runs L1 physics, and returns the nodes that resonate."
    ),
    "annotations": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    "inputSchema": {
        "type": "object",
        "required": ["question"],
        "properties": {
            "question": {
                "type": "string",
                "description": "Question posed to the current Citizen's L1.",
            },
            "intention": {
                "type": "string",
                "description": "Why this memory is being sought.",
            },
            "spaceId": {
                "type": "string",
                "description": "L1 Space to recall from. Defaults to the citizen's active Space.",
            },
            "energy": {
                "type": "number",
                "description": "Requested recall energy, bounded by L1 policy.",
                "default": DEFAULT_RECALL_ENERGY,
            },
            "maxTicks": {
                "type": "integer",
                "description": "Safety ceiling for recall physics.",
                "default": DEFAULT_MAX_TICKS,
            },
            "topK": {
                "type": "integer",
                "description": "Response limit only; never truncates the Space stimulus.",
                "default": 10,
            },
            "handle": {
                "type": "string",
                "description": "Citizen handle. Auto-detected if omitted.",
            },
        },
    },
}


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(payload, ensure_ascii=False, indent=2),
        }]
    }


def _err(message: str, *, code: str = "recall_failed") -> dict[str, Any]:
    return _ok({"status": "failed", "code": code, "error": message})


def _normalize_handle(value: Any) -> str:
    return str(value or "").strip().lstrip("@").lower().replace("-", "_")


def _rows(graph, query: str, params: dict[str, Any] | None = None) -> list:
    result = graph.query(query, params or {})
    return list(getattr(result, "result_set", result) or [])


def _resolve_graph(ctx, handle: str):
    injected = getattr(ctx, "recall_graph", None)
    if injected is not None:
        return injected, getattr(ctx, "recall_graph_name", "test_l1")

    from falkordb import FalkorDB

    db = FalkorDB(
        host=os.environ.get("FALKORDB_HOST", "localhost"),
        port=int(os.environ.get("FALKORDB_PORT", "6379")),
    )
    graph_name = resolve_l1_graph_name(handle, db=db)
    return db.select_graph(graph_name), graph_name


def _lexical_hash_embedding(text: str, dimension: int = 256) -> list[float]:
    """Deterministic degraded embedding when the semantic model is unavailable."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    tokens = re.findall(r"[a-z0-9]+", normalized)
    features = tokens + [
        token[index:index + 3]
        for token in tokens
        for index in range(max(0, len(token) - 2))
    ]
    vector = [0.0] * dimension
    for feature in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[bucket] += sign
    magnitude = sum(value * value for value in vector) ** 0.5
    return [value / magnitude for value in vector] if magnitude else vector


def _embed_question(question: str, ctx) -> tuple[list[float], str]:
    graph_queries = getattr(ctx, "graph_queries", None)
    embed_fn = getattr(graph_queries, "_embed_fn", None)
    if callable(embed_fn):
        return parse_embedding(embed_fn(question)), "configured"
    if graph_queries is not None and callable(getattr(graph_queries, "embed", None)):
        return parse_embedding(graph_queries.embed(question)), "configured"

    try:
        from runtime.infrastructure.embeddings.service import get_embedding_service

        service = get_embedding_service()
        if service is not None:
            embedding = parse_embedding(service.embed(question))
            if embedding:
                return embedding, "sentence_transformer"
    except (ImportError, RuntimeError):
        logger.warning(
            "Semantic embedding model unavailable; recall uses lexical hash fallback"
        )
    return _lexical_hash_embedding(question), "lexical_hash_fallback"


def _actor_id_candidates(handle: str) -> list[str]:
    slug = handle.replace("_", "-")
    return list(dict.fromkeys(filter(None, (
        handle,
        f"actor-{slug}",
        f"CITIZEN_{handle}",
        f"{handle}_ai",
    ))))


def _resolve_space_id(
    graph,
    requested: str,
    handle: str,
    graph_name: str,
) -> str:
    if requested:
        if requested.startswith(VIRTUAL_L1_SPACE_PREFIX):
            return requested
        exists = _rows(
            graph,
            "MATCH (s {id: $space_id}) RETURN s.id LIMIT 1",
            {"space_id": requested},
        )
        return str(exists[0][0]) if exists else ""

    actor_ids = _actor_id_candidates(handle)
    located = _rows(
        graph,
        """
        MATCH (actor)-[:LOCATED_IN]->(space)
        WHERE actor.id IN $actor_ids
        RETURN space.id
        ORDER BY coalesce(space.energy, 0.0) DESC, space.id
        LIMIT 1
        """,
        {"actor_ids": actor_ids},
    )
    if located:
        return str(located[0][0])

    active = _rows(
        graph,
        """
        MATCH (space)
        WHERE toLower(coalesce(space.nodeType, space.node_type, '')) = 'space'
        RETURN space.id
        ORDER BY coalesce(space.energy, 0.0) DESC, space.id
        LIMIT 1
        """,
    )
    if active:
        return str(active[0][0])
    return f"{VIRTUAL_L1_SPACE_PREFIX}{graph_name}"


def _load_graph_snapshot(graph) -> tuple[dict[str, RecallGraphNode], list[dict[str, Any]]]:
    node_rows = _rows(
        graph,
        """
        MATCH (n)
        RETURN n.id, coalesce(n.content, n.synthesis, n.summary, n.name, n.id),
               coalesce(n.nodeType, n.node_type, ''),
               coalesce(n.semanticType, n.type, ''),
               n.embedding,
               coalesce(n.currentActivation, n.activation, n.energy, 0.0),
               coalesce(n.weight, 0.1),
               coalesce(n.stability, 0.0), coalesce(n.recency, 1.0),
               coalesce(n.status, ''), coalesce(n.epistemicStatus, n.epistemic_status, 'unknown')
        """,
    )
    nodes: dict[str, RecallGraphNode] = {}
    for row in node_rows:
        if not row or not row[0]:
            continue
        node_id = str(row[0])
        nodes[node_id] = RecallGraphNode(
            id=node_id,
            content=str(row[1] or node_id),
            node_type=str(row[2] or "concept"),
            semantic_type=str(row[3] or ""),
            embedding=parse_embedding(row[4]),
            energy=float(row[5] or 0.0),
            weight=float(row[6] or 0.1),
            stability=float(row[7] or 0.0),
            recency=float(row[8] or 1.0),
            status=str(row[9] or ""),
            epistemic_status=str(row[10] or "unknown"),
        )

    link_rows = _rows(
        graph,
        """
        MATCH (a)-[r]->(b)
        RETURN a.id, b.id, type(r), coalesce(r.weight, 0.5),
               coalesce(r.activation_gain, 1.0), coalesce(r.friction, 0.0),
               coalesce(r.trust, 0.5), coalesce(r.hierarchy, 0.0)
        """,
    )
    links = [
        {
            "source": str(row[0]),
            "target": str(row[1]),
            "relation": str(row[2] or ""),
            "weight": float(row[3] or 0.5),
            "activation_gain": float(row[4] or 1.0),
            "friction": float(row[5] or 0.0),
            "trust": float(row[6] or 0.5),
            "hierarchy": float(row[7] or 0.0),
        }
        for row in link_rows
        if row and row[0] and row[1]
    ]
    return nodes, links


def _embed_missing_nodes(
    nodes: Iterable[RecallGraphNode],
    ctx,
    embedding_method: str,
) -> None:
    """Complete the semantic snapshot in batch without mutating node claims."""
    nodes = list(nodes)
    if embedding_method == "lexical_hash_fallback":
        for node in nodes:
            node.embedding = _lexical_hash_embedding(node.content)
        return

    missing = [node for node in nodes if not node.embedding and node.content.strip()]
    if not missing:
        return

    texts = [node.content for node in missing]
    graph_queries = getattr(ctx, "graph_queries", None)
    embed_batch = getattr(graph_queries, "embed_batch", None)
    embed_fn = getattr(graph_queries, "_embed_fn", None)
    if callable(embed_batch):
        embeddings = embed_batch(texts)
    elif callable(embed_fn):
        embeddings = [embed_fn(text) for text in texts]
    else:
        try:
            from runtime.infrastructure.embeddings.service import get_embedding_service

            service = get_embedding_service()
            if service is None:
                embeddings = [_lexical_hash_embedding(text) for text in texts]
            else:
                embeddings = service.embed_batch(texts)
                service.flush_cache()
        except (ImportError, RuntimeError):
            embeddings = [_lexical_hash_embedding(text) for text in texts]

    for node, embedding in zip(missing, embeddings):
        node.embedding = parse_embedding(embedding)


def _is_space(node: RecallGraphNode | None) -> bool:
    if node is None:
        return False
    return (
        node.node_type.strip().lower() == "space"
        or node.semantic_type.strip().lower() == "space"
    )


def _space_closure(
    space_id: str,
    nodes: dict[str, RecallGraphNode],
    links: list[dict[str, Any]],
) -> tuple[list[RecallGraphNode], list[RecallGraphLink]]:
    if space_id.startswith(VIRTUAL_L1_SPACE_PREFIX):
        closure = set(nodes)
        return (
            [nodes[node_id] for node_id in sorted(closure)],
            [
                RecallGraphLink(
                    source_id=link["source"],
                    target_id=link["target"],
                    relation=link["relation"],
                    weight=link["weight"],
                    activation_gain=link["activation_gain"],
                    friction=link["friction"],
                    trust=link["trust"],
                )
                for link in links
                if link["source"] in closure and link["target"] in closure
            ],
        )
    if space_id not in nodes:
        return [], []

    closure = {space_id}
    pending = [space_id]
    while pending:
        current_space = pending.pop()
        for link in links:
            relation = link["relation"].upper()
            target_id = link["target"]
            source_id = link["source"]
            member_id = None
            if source_id == current_space and (
                relation == "CONTAINS"
                or (relation == "LINK" and link["hierarchy"] < 0.0)
            ):
                member_id = target_id
            elif target_id == current_space and relation in {"LOCATED_IN", "OCCURS_IN"}:
                member_id = source_id
            if member_id is None or member_id in closure or member_id not in nodes:
                continue
            closure.add(member_id)
            if _is_space(nodes[member_id]):
                pending.append(member_id)

    closure_nodes = [nodes[node_id] for node_id in sorted(closure)]
    closure_links = [
        RecallGraphLink(
            source_id=link["source"],
            target_id=link["target"],
            relation=link["relation"],
            weight=link["weight"],
            activation_gain=link["activation_gain"],
            friction=link["friction"],
            trust=link["trust"],
        )
        for link in links
        if link["source"] in closure and link["target"] in closure
    ]
    return closure_nodes, closure_links


def _create_recall_moment(
    graph,
    *,
    moment_id: str,
    question: str,
    intention: str,
    embedding: list[float],
    space_id: str,
    energy: float,
    created_at: float,
    embedding_method: str,
) -> None:
    params = {
        "space_id": space_id,
        "moment_id": moment_id,
        "question": question,
        "intention": intention,
        "embedding": embedding,
        "energy": energy,
        "created_at": created_at,
        "embedding_method": embedding_method,
    }
    if space_id.startswith(VIRTUAL_L1_SPACE_PREFIX):
        created = _rows(
            graph,
            """
            MERGE (space:Space {id: $space_id})
            ON CREATE SET space.nodeType = 'Space',
                          space.semanticType = 'L1GraphSpace',
                          space.virtualProjection = true
            CREATE (moment:Moment {
              id: $moment_id, nodeType: 'Moment', semanticType: 'Recall',
              subtype: 'recall_query', status: 'running',
              question: $question, intention: $intention,
              embedding: $embedding, energy: $energy,
              embeddingMethod: $embedding_method,
              epistemicStatus: 'inquiry', createdAtEpoch: $created_at
            })
            CREATE (moment)-[:OCCURS_IN]->(space)
            RETURN moment.id
            """,
            params,
        )
    else:
        created = _rows(
            graph,
            """
            MATCH (space {id: $space_id})
            CREATE (moment:Moment {
              id: $moment_id, nodeType: 'Moment', semanticType: 'Recall',
              subtype: 'recall_query', status: 'running',
              question: $question, intention: $intention,
              embedding: $embedding, energy: $energy,
              embeddingMethod: $embedding_method,
              epistemicStatus: 'inquiry', createdAtEpoch: $created_at
            })
            CREATE (moment)-[:OCCURS_IN]->(space)
            RETURN moment.id
            """,
            params,
        )
    if not created:
        raise RuntimeError(
            f"Recall Moment could not be created in Space '{space_id}'."
        )


def _mark_recall_failed(graph, moment_id: str, reason: str) -> None:
    """Best-effort terminal status for a Moment created before a runtime error."""
    try:
        _rows(
            graph,
            """
            MATCH (moment:Moment {id: $moment_id})
            SET moment.status = 'failed',
                moment.failureReason = $reason,
                moment.completedAtEpoch = $completed_at
            RETURN moment.id
            """,
            {
                "moment_id": moment_id,
                "reason": reason[:1000],
                "completed_at": time.time(),
            },
        )
    except Exception:
        logger.exception("Could not mark Recall Moment %s failed", moment_id)


def _persist_outcome(graph, outcome, completed_at: float) -> None:
    energy_updates = [
        {"id": node_id, "energy": energy}
        for node_id, energy in outcome.final_energies.items()
    ]
    if energy_updates:
        _rows(
            graph,
            """
            UNWIND $updates AS update
            MATCH (node {id: update.id})
            SET node.energy = update.energy
            RETURN count(node)
            """,
            {"updates": energy_updates},
        )

    all_result_node_ids = [item.node_id for item in outcome.results]
    all_result_scores = {item.node_id: item.score for item in outcome.results}
    _rows(
        graph,
        """
        MATCH (moment:Moment {id: $moment_id})
        SET moment.status = $status,
            moment.completedAtEpoch = $completed_at,
            moment.recallSubentityId = $recall_subentity_id,
            moment.selectedSubentityId = $parent_subentity_id,
            moment.selectionSemanticScore = $selection_semantic,
            moment.selectionActivationScore = $selection_activation,
            moment.selectionCombinedScore = $selection_combined,
            moment.resultNodeIdsJson = $result_node_ids_json,
            moment.resultScoresJson = $result_scores_json,
            moment.ticksRun = $ticks_run,
            moment.stopReason = $stop_reason,
            moment.stimulusNodeCount = $stimulus_node_count,
            moment.stimulusLinkCount = $stimulus_link_count,
            moment.missingEmbeddingCount = $missing_embedding_count
            moment.energy = $remaining_question_energy
        RETURN moment.id
        """,
        {
            "moment_id": outcome.moment_id,
            "status": outcome.status,
            "completed_at": completed_at,
            "recall_subentity_id": outcome.recall_subentity_id,
            "parent_subentity_id": outcome.selection.parent_id,
            "selection_semantic": outcome.selection.semantic,
            "selection_activation": outcome.selection.activation,
            "selection_combined": outcome.selection.combined,
            "result_node_ids_json": json.dumps(all_result_node_ids),
            "result_scores_json": json.dumps(all_result_scores),
            "ticks_run": outcome.ticks_run,
            "stop_reason": outcome.stop_reason,
            "stimulus_node_count": outcome.stimulus_node_count,
            "stimulus_link_count": outcome.stimulus_link_count,
            "missing_embedding_count": outcome.missing_embedding_count,
            "remaining_question_energy": outcome.remaining_question_energy,
        },
    )
    if outcome.selection.parent_id:
        _rows(
            graph,
            """
            MATCH (moment:Moment {id: $moment_id}), (subentity {id: $subentity_id})
            MERGE (moment)-[route:ROUTED_TO]->(subentity)
            SET route.semantic = $semantic,
                route.activation = $activation,
                route.combined = $combined
            RETURN subentity.id
            """,
            {
                "moment_id": outcome.moment_id,
                "subentity_id": outcome.selection.parent_id,
                "semantic": outcome.selection.semantic,
                "activation": outcome.selection.activation,
                "combined": outcome.selection.combined,
            },
        )


def handle_recall(args: dict[str, Any], ctx=None) -> dict[str, Any]:
    """Create and execute one question-driven recall in the current L1."""
    question = str(args.get("question") or "").strip()
    if not question:
        return _err("'question' is required.", code="invalid_question")
    detected_handle = _normalize_handle(detect_citizen_handle())
    requested_handle = _normalize_handle(args.get("handle"))
    if (
        detected_handle
        and requested_handle
        and requested_handle != detected_handle
    ):
        return _err(
            "Recall can only query the current Citizen's L1.",
            code="sovereignty_violation",
        )
    handle = detected_handle or requested_handle
    if not handle:
        return _err("Citizen identity could not be resolved.", code="identity_unavailable")

    try:
        graph, graph_name = _resolve_graph(ctx, handle)
        space_id = _resolve_space_id(
            graph,
            str(args.get("spaceId") or ""),
            handle,
            graph_name,
        )
        if not space_id:
            return _err(
                "No accessible L1 Space could be resolved.",
                code="space_unavailable",
            )

        question_embedding, embedding_method = _embed_question(question, ctx)
        if not question_embedding:
            return _err(
                "Question embedding is unavailable; recall was not started.",
                code="missing_embedding",
            )

        all_nodes, all_links = _load_graph_snapshot(graph)
        nodes, links = _space_closure(space_id, all_nodes, all_links)
        if not nodes:
            return _err(
                f"Space '{space_id}' does not exist or could not be read.",
                code="space_unavailable",
            )
        source_missing_embedding_count = sum(
            1 for node in nodes if not node.embedding
        )
        _embed_missing_nodes(nodes, ctx, embedding_method)

        moment_id = f"moment:recall:{handle}:{int(time.time() * 1000)}:{uuid.uuid4().hex[:8]}"
        intention = str(args.get("intention") or question).strip()
        requested_energy = float(args.get("energy", DEFAULT_RECALL_ENERGY))
        energy = max(MIN_RECALL_ENERGY, min(MAX_RECALL_ENERGY, requested_energy))
        created_at = time.time()
        _create_recall_moment(
            graph,
            moment_id=moment_id,
            question=question,
            intention=intention,
            embedding=question_embedding,
            space_id=space_id,
            energy=energy,
            created_at=created_at,
            embedding_method=embedding_method,
        )
        try:
            outcome = run_recall(
                citizen_id=handle,
                moment_id=moment_id,
                question=question,
                question_embedding=question_embedding,
                nodes=nodes,
                links=links,
                energy=energy,
                max_ticks=int(args.get("maxTicks", DEFAULT_MAX_TICKS)),
                top_k=int(args.get("topK", 10)),
                source_missing_embedding_count=source_missing_embedding_count,
            )
            _persist_outcome(graph, outcome, time.time())
        except Exception as exc:
            _mark_recall_failed(graph, moment_id, str(exc))
            raise
        payload = outcome.to_dict()
        payload.update({
            "citizen": handle,
            "graph": graph_name,
            "spaceId": space_id,
            "embeddingMethod": embedding_method,
        })
        return _ok(payload)
    except (TypeError, ValueError) as exc:
        return _err(str(exc), code="invalid_arguments")
    except Exception as exc:
        logger.exception("Recall failed")
        return _err(str(exc))
