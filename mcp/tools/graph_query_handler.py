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
import time
from typing import Any, Dict, List, Optional

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.graph_query")


def _record_query_gap(query: str, actor_id: str, ctx: ServerContext):
    """Record an empty query result as a gap marker in the L3 graph.

    When a query returns nothing, it means the graph lacks knowledge
    about this topic. Gap markers accumulate energy logarithmically —
    the 20th failure for the same topic is not 20x as urgent as the first.

    Gap markers can be used to prioritize knowledge acquisition.
    L7 (forgetting) handles cleanup of stale gaps nobody cares about.
    """
    import hashlib
    import math

    gap_id = "gap_" + hashlib.sha256(query.lower().strip().encode()).hexdigest()[:12]

    try:
        # MERGE: if the gap already exists, increment its energy (logarithmic)
        ctx.graph_queries._query(
            """
            MERGE (g:Narrative {id: $gap_id})
            ON CREATE SET
                g.name = $name,
                g.type = 'gap',
                g.content = $query,
                g.synthesis = $synthesis,
                g.energy = 0.3,
                g.weight = 0.1,
                g.hit_count = 1,
                g.first_asked_by = $actor_id,
                g.created_at_s = $ts
            ON MATCH SET
                g.energy = g.energy + 0.3 / (1 + log(g.hit_count + 1)),
                g.hit_count = g.hit_count + 1,
                g.last_asked_by = $actor_id,
                g.updated_at_s = $ts
            """,
            {
                "gap_id": gap_id,
                "name": f"Knowledge gap: {query[:80]}",
                "query": query,
                "synthesis": f"The graph has no knowledge about: {query}. Asked by {actor_id}.",
                "actor_id": actor_id,
                "ts": int(time.time()),
            },
        )
        logger.debug(f"Gap recorded: {gap_id} for query '{query[:60]}'")
    except Exception as e:
        logger.debug(f"Gap recording failed: {e}")


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


def _try_fast_path(query: str, actor_id: str, ctx: ServerContext) -> Optional[str]:
    """Fast-path for direct lookups — bypasses SubEntity when a Cypher shortcut works.

    Patterns detected:
      - Actor/citizen lookup: "genesis citizen", "Who is nervo"
      - Space lookup: "Innovation Fields district"
      - Node by ID: any known node_type + keyword
      - "my nodes/links/connections": actor's direct neighborhood
    Returns formatted markdown or None (fall through to SubEntity).
    """
    import re
    q = query.lower().strip()

    # Pattern 1: Direct actor lookup — "{handle} citizen/actor/node" or "who is {handle}"
    actor_match = re.match(
        r"(?:who is |find |get |show )?@?(\w+)\s*(?:citizen|actor|node|profile|info)?$", q
    )
    if not actor_match:
        actor_match = re.match(r"(?:.*\s)?(\w+)\s+(?:citizen|actor)\s*(?:node)?$", q)
    if actor_match:
        handle = actor_match.group(1)
        rows = ctx.graph_queries._query(
            """MATCH (a:Actor {id: $h})
               OPTIONAL MATCH (a)-[r]->(n)
               RETURN a.id, a.name, a.type, a.synthesis,
                      type(r) AS rel, labels(n)[0] AS label, n.id AS nid, n.name AS nname,
                      r.weight, r.trust, r.computed_type
               LIMIT 20""",
            {"h": handle},
        )
        if rows:
            a = rows[0]
            lines = [f"**{a[1] or a[0]}** (Actor, type={a[2]})", ""]
            if a[3]:
                lines.append(f"> {a[3]}")
                lines.append("")
            lines.append("| Rel | Target | Type | Weight | Trust |")
            lines.append("|-----|--------|------|--------|-------|")
            for r in rows:
                if r[4]:
                    lines.append(f"| {r[10] or r[4]} | {r[7] or r[6]} ({r[5]}) | {r[10] or '-'} | {r[8] or '-'} | {r[9] or '-'} |")
            return "\n".join(lines)

    # Pattern 2: Space/district lookup — "{name} district/space/channel"
    space_match = re.match(r"(.+?)\s+(?:district|space|channel|room|place)\b", q)
    if space_match:
        name = space_match.group(1).strip()
        rows = ctx.graph_queries._query(
            """MATCH (s:Space)
               WHERE toLower(s.name) CONTAINS $name OR toLower(s.id) CONTAINS $name
               OPTIONAL MATCH (a:Actor)-[r:LINK]->(s) WHERE r.computed_type = 'presence'
               RETURN s.id, s.name, s.space_hint, collect(a.id)[0..10] AS members
               LIMIT 5""",
            {"name": name.lower()},
        )
        if rows:
            lines = []
            for r in rows:
                lines.append(f"**{r[1]}** (Space, id={r[0]}, hint={r[2]})")
                members = r[3] or []
                if members:
                    lines.append(f"Members: {', '.join('@'+m for m in members)}")
                lines.append("")
            return "\n".join(lines)

    # Pattern 3: "my nodes/links/connections/graph"
    if re.match(r"(?:my|self|own)\s+(?:nodes?|links?|connections?|graph|info|state)", q):
        rows = ctx.graph_queries._query(
            """MATCH (a:Actor {id: $h})-[r]->(n)
               RETURN type(r) AS rel, labels(n)[0] AS label, n.id, n.name,
                      r.weight, r.computed_type, r.trust
               ORDER BY r.weight DESC
               LIMIT 25""",
            {"h": actor_id},
        )
        if rows:
            lines = [f"**@{actor_id}** — {len(rows)} connections\n"]
            lines.append("| Rel | Target | Type | Weight | Trust |")
            lines.append("|-----|--------|------|--------|-------|")
            for r in rows:
                lines.append(f"| {r[5] or r[0]} | {r[3] or r[2]} ({r[1]}) | {r[5] or '-'} | {r[4] or '-'} | {r[6] or '-'} |")
            return "\n".join(lines)

    # Pattern 4: Organization/group members — "{name} organization/org/members"
    org_match = re.match(r"(.+?)\s+(?:organization|org|members|team|group)\b", q)
    if org_match:
        name = org_match.group(1).strip()
        rows = ctx.graph_queries._query(
            """MATCH (n:Narrative)
               WHERE toLower(n.name) CONTAINS $name OR toLower(n.id) CONTAINS $name
               OPTIONAL MATCH (a:Actor)-[]->(n)
               RETURN n.id, n.name, n.type, collect(DISTINCT a.id)[0..20] AS actors
               LIMIT 5""",
            {"name": name.lower()},
        )
        if rows and any(r[3] for r in rows):
            lines = []
            for r in rows:
                actors = r[3] or []
                lines.append(f"**{r[1]}** ({r[2]}, id={r[0]})")
                if actors:
                    lines.append(f"Linked actors: {', '.join('@'+a for a in actors)}")
                lines.append("")
            return "\n".join(lines)

    # Pattern 5: Generic entity search — if query mentions a specific term + node type keyword,
    # try a broad search before falling to expensive SubEntity
    type_keywords = {
        "actor": "Actor", "citizen": "Actor", "person": "Actor", "character": "Actor",
        "space": "Space", "district": "Space", "channel": "Space", "room": "Space", "place": "Space",
        "narrative": "Narrative", "mission": "Narrative", "task": "Narrative", "objective": "Narrative",
        "organization": "Narrative", "org": "Narrative", "team": "Narrative", "group": "Narrative",
        "moment": "Moment", "event": "Moment",
        "thing": "Thing", "object": "Thing", "tool": "Thing",
    }
    for kw, label in type_keywords.items():
        if kw in q:
            # Extract the search term (everything except the keyword)
            search_term = q.replace(kw, "").strip().strip("?").strip()
            if len(search_term) >= 2:
                rows = ctx.graph_queries._query(
                    f"""MATCH (n:{label})
                       WHERE toLower(n.name) CONTAINS $term OR toLower(n.id) CONTAINS $term
                       RETURN n.id, n.name, labels(n)[0] AS label
                       LIMIT 5""",
                    {"term": search_term.lower()},
                )
                if rows:
                    lines = [f"Found {len(rows)} {label} node(s) matching '{search_term}':\n"]
                    for r in rows:
                        lines.append(f"- **{r[1]}** (id={r[0]}, type={r[2]})")
                    return "\n".join(lines)
                else:
                    _record_query_gap(query, actor_id, ctx)
                    return f"No {label} nodes found matching '{search_term}' in the graph."
            break

    return None  # No fast-path match → fall through to SubEntity


async def _ask_single(
    query: str,
    actor_id: str,
    intent: Optional[str],
    timeout: float,
    debug: bool,
    debug_lines: List[str],
    ctx: ServerContext,
) -> str:
    """SubEntity exploration for a single query, with fast-path for direct lookups."""
    import time
    start = time.time()

    # Fast-path: direct Cypher for simple lookups (< 100ms vs 30s)
    fast = _try_fast_path(query, actor_id, ctx)
    if fast is not None:
        elapsed = time.time() - start
        if debug:
            debug_lines.append(f"Fast-path hit for: {query} ({elapsed*1000:.0f}ms)")
        return fast

    from runtime.infrastructure.embeddings.service import get_embedding_service

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
            _record_query_gap(query, actor_id, ctx)
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
