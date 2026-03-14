"""
[THINK] Graph Query — Semantic search across the knowledge graph.

Supports multiple concurrent queries, SubEntity traversal, intent-based filtering,
and cluster presentation.

Usage via MCP:
    graph_query(queries=["Who is Edmund?", "What oaths exist?"])
    graph_query(queries=["How does physics work?"], intent="summarize")
"""

import asyncio
import json
import logging
import random
from typing import Any, Dict, List, Optional

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.graph_query")


TOOL_SCHEMA = {
    "name": "graph_query",
    "description": (
        "[THINK] Query the knowledge graph using natural language. Supports multiple queries at once. "
        "Uses SubEntity traversal to find relevant nodes and their connections."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "One or more natural language queries (e.g., ['Who is Edmund?', 'What oaths exist?'])",
            },
            "intent": {
                "type": "string",
                "description": "WHY you're searching — affects traversal strategy (e.g., 'find contradictions', 'summarize events', 'verify claims').",
            },
            "actor_id": {
                "type": "string",
                "description": "Actor performing the query (default: actor_claude).",
            },
            "debug": {
                "type": "boolean",
                "description": "Enable debug mode with traversal logs (default: false).",
            },
            "timeout": {
                "type": "number",
                "description": "Query timeout in seconds (default: 30).",
            },
        },
        "required": ["queries"],
    },
}


def handle_graph_query(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Query the graph using natural language via SubEntity exploration."""
    queries = args.get("queries", [])
    intent = args.get("intent")
    actor_id = args.get("actor_id", "actor_claude")
    debug = args.get("debug", False)
    timeout = args.get("timeout", 30.0)

    if not queries:
        return _err("'queries' array is required.")

    if not ctx.graph_queries:
        return _err("No graph connection available.")

    actor_id = _resolve_actor(actor_id, ctx, debug)

    debug_lines: List[str] = []
    if debug:
        debug_lines.append("=== DEBUG MODE ===")
        debug_lines.append(f"Actor: {actor_id}")
        debug_lines.append(f"Intent: {intent or '(none)'}")
        debug_lines.append(f"Timeout: {timeout}s")
        debug_lines.append("")

    try:
        results = asyncio.run(
            _ask_async(queries, actor_id, intent, timeout, debug, debug_lines, ctx)
        )

        output_lines: List[str] = []
        if debug:
            output_lines.extend(debug_lines)
            output_lines.append("")

        for i, item in enumerate(results, 1):
            if len(results) > 1:
                output_lines.append(f"## Query {i}: {item['query']}\n")
            output_lines.append(
                item["result"] if isinstance(item["result"], str)
                else json.dumps(item["result"], indent=2)
            )
            output_lines.append("")

        return _ok("\n".join(output_lines))

    except Exception as e:
        logger.exception("Graph query failed")
        error_msg = f"Query failed: {e}"
        if debug:
            import traceback
            error_msg += f"\n\nTraceback:\n{traceback.format_exc()}"
        return _err(error_msg)


def _resolve_actor(actor_id: str, ctx: ServerContext, debug: bool = False) -> str:
    """Resolve actor ID: return existing actor or pick random one."""
    if not ctx.graph_queries:
        return actor_id

    result = ctx.graph_queries._query(
        "MATCH (a:Actor {id: $actor_id}) RETURN a.id",
        {"actor_id": actor_id}
    )
    if result and result[0]:
        return actor_id

    actors = ctx.graph_queries._query(
        "MATCH (a:Actor) RETURN a.id LIMIT 20"
    )
    if actors:
        random_actor = random.choice(actors)[0]
        if debug:
            logger.info(f"Actor {actor_id} not found, using random actor: {random_actor}")
        return random_actor

    return actor_id


async def _ask_async(
    queries: List[str],
    actor_id: str,
    intent: Optional[str],
    timeout: float,
    debug: bool,
    debug_lines: List[str],
    ctx: ServerContext,
) -> List[Dict[str, Any]]:
    """Run multiple queries concurrently."""
    valid_queries = [q for q in queries if q and q.strip()]
    if not valid_queries:
        return []

    if debug:
        debug_lines.append(f"Running {len(valid_queries)} queries concurrently...")

    tasks = [
        _ask_single(query, actor_id, intent, timeout, debug, debug_lines, ctx)
        for query in valid_queries
    ]
    results_raw = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for query, result in zip(valid_queries, results_raw):
        if isinstance(result, Exception):
            results.append({"query": query, "result": f"Error: {result}"})
        else:
            results.append({"query": query, "result": result})
    return results


async def _ask_single(
    query: str,
    actor_id: str,
    intent: Optional[str],
    timeout: float,
    debug: bool,
    debug_lines: List[str],
    ctx: ServerContext,
) -> str:
    """SubEntity exploration for a single query."""
    import time
    from runtime.infrastructure.embeddings.service import get_embedding_service
    start = time.time()

    try:
        from runtime.explore_cmd import run_exploration

        if debug:
            debug_lines.append(f"Starting SubEntity exploration...")
            debug_lines.append(f"Actor: {actor_id}, Timeout: {timeout}s")

        embed_service = get_embedding_service()
        moment_id = ctx.graph_queries._create_query_moment(
            query=query,
            embed_fn=embed_service.embed,
            initial_energy=1.0,
        )

        # Link actor to moment
        ctx.graph_queries._query("""
            MATCH (a {id: $actor_id})
            MATCH (m {id: $moment_id})
            MERGE (a)-[r:link]->(m)
            SET r.weight = 1.0, r.energy = 1.0
        """, {'actor_id': actor_id, 'moment_id': moment_id})

        # Link to previous actor moment
        prev_moment = ctx.graph_queries._query("""
            MATCH (a {id: $actor_id})-[:link]->(m:Moment)
            WHERE m.id <> $moment_id
            RETURN m.id
            ORDER BY m.created_at_s DESC
            LIMIT 1
        """, {'actor_id': actor_id, 'moment_id': moment_id})
        if prev_moment:
            prev_id = prev_moment[0][0] if prev_moment[0] else None
            if prev_id:
                ctx.graph_queries._query("""
                    MATCH (prev {id: $prev_id})
                    MATCH (curr {id: $curr_id})
                    MERGE (prev)-[r:link]->(curr)
                    SET r.weight = 1.0, r.energy = 0.0
                """, {'prev_id': prev_id, 'curr_id': moment_id})
                if debug:
                    debug_lines.append(f"Linked to previous: {prev_id}")

        if debug:
            debug_lines.append(f"Created moment: {moment_id}")

        result, log_path = await run_exploration(
            query=query,
            actor_id=actor_id,
            intention=intent,
            graph_name=None,
            origin_moment=moment_id,
            timeout=timeout,
            debug=debug,
        )

        elapsed = time.time() - start

        if debug:
            debug_lines.append(f"Exploration completed in {elapsed:.2f}s")
            debug_lines.append(f"State: {result.state.value}")
            debug_lines.append(f"Satisfaction: {result.satisfaction:.2f}")
            debug_lines.append(f"Found narratives: {len(result.found_narratives)}")
            if log_path:
                debug_lines.append(f"Log: {log_path}.txt")

        # Format result using cluster presentation
        from runtime.physics.cluster_presentation import (
            ClusterNode,
            ClusterLink,
            RawCluster,
            present_cluster,
            IntentionType,
        )

        if not result.found_narratives:
            return "No relevant narratives found."

        # Parse intention type
        intent_type = IntentionType.EXPLORE
        if intent:
            intent_lower = intent.lower()
            if "summar" in intent_lower:
                intent_type = IntentionType.SUMMARIZE
            elif "verif" in intent_lower or "check" in intent_lower:
                intent_type = IntentionType.VERIFY
            elif "find" in intent_lower or "next" in intent_lower:
                intent_type = IntentionType.FIND_NEXT
            elif "retriev" in intent_lower or "get" in intent_lower:
                intent_type = IntentionType.RETRIEVE

        # Fetch content for each found narrative
        nodes = []
        query_embedding = embed_service.embed(query)

        for narr_id, alignment in result.found_narratives.items():
            narr_data = ctx.graph_queries._query("""
                MATCH (n {id: $narr_id})
                RETURN n.name, n.content, n.synthesis, n.node_type, n.energy, n.weight
            """, {'narr_id': narr_id})

            if narr_data and narr_data[0]:
                name = narr_data[0][0] or narr_id
                content = narr_data[0][1] or ""
                synthesis = narr_data[0][2] or name
                node_type = narr_data[0][3] or "narrative"
                energy = narr_data[0][4] or 1.0
                weight = narr_data[0][5] or alignment

                display_text = synthesis if synthesis else (content[:200] if content else name)

                nodes.append(ClusterNode(
                    id=narr_id,
                    node_type=node_type,
                    name=name,
                    synthesis=display_text,
                    embedding=query_embedding,
                    weight=weight,
                    energy=energy,
                ))

        # Add actor node
        nodes.append(ClusterNode(
            id=actor_id,
            node_type='actor',
            name=actor_id,
            synthesis=f"Explorer: {actor_id}",
            embedding=query_embedding,
            weight=1.0,
            energy=1.0,
        ))

        # Create links from actor to narratives
        links = []
        for narr_id, alignment in result.found_narratives.items():
            links.append(ClusterLink(
                id=f"link_{actor_id}_{narr_id}",
                source_id=actor_id,
                target_id=narr_id,
                synthesis=f"found (alignment: {alignment:.2f})",
                embedding=query_embedding,
                weight=alignment,
                energy=alignment,
                permanence=0.5,
            ))

        raw_cluster = RawCluster(
            nodes=nodes,
            links=links,
            traversed_link_ids={l.id for l in links},
        )

        presented = present_cluster(
            raw_cluster=raw_cluster,
            query=query,
            intention=intent or query,
            intention_type=intent_type,
            query_embedding=query_embedding,
            intention_embedding=query_embedding,
            start_id=actor_id,
        )

        output = presented.markdown
        if result.crystallized:
            output += f"\n\n*Crystallized: {result.crystallized}*"

        return output

    except Exception as e:
        if debug:
            debug_lines.append(f"Ask failed: {e}")
        return f"Ask failed: {e}"


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
