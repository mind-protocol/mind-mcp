"""
[THINK] Graph Write — Create nodes and links in the knowledge graph.

Usage via MCP:
    graph_write(node_type="narrative", name="My thought", content="...")
    graph_write(node_type="actor", name="new_agent", type="agent")
    graph_write(node_type="narrative", content="...", link_to=["node_123"])
"""

import logging
import time
import uuid
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.graph_write")


TOOL_SCHEMA = {
    "name": "graph_write",
    "description": (
        "[THINK] Create a new node in the knowledge graph. "
        "Supports narrative nodes (thoughts, facts, tasks) and actor nodes (agents, characters). "
        "Optionally link to existing nodes. Returns the created node ID."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "node_type": {
                "type": "string",
                "enum": ["narrative", "actor"],
                "description": "Type of node: 'narrative' for thoughts/facts/tasks, 'actor' for agents/characters.",
            },
            "id": {
                "type": "string",
                "description": "Unique node ID. Auto-generated if not provided.",
            },
            "type": {
                "type": "string",
                "description": "Subtype (e.g., 'task_run', 'fact', 'thought', 'agent', 'character').",
            },
            "name": {
                "type": "string",
                "description": "Display name for the node.",
            },
            "content": {
                "type": "string",
                "description": "Full content/description of the node.",
            },
            "synthesis": {
                "type": "string",
                "description": "Short summary (used for embedding). Auto-generated from content if not provided.",
            },
            "weight": {
                "type": "number",
                "description": "Importance weight (default: 1.0).",
            },
            "energy": {
                "type": "number",
                "description": "Activity energy (default: 1.0).",
            },
            "link_to": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Node IDs to link this node to.",
            },
        },
        "required": ["node_type"],
    },
}


def handle_graph_write(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Create a new node in the graph."""
    node_type = args.get("node_type")
    if not node_type:
        return _err("'node_type' is required (narrative or actor).")

    node_id = args.get("id") or f"{args.get('type', node_type)}_{uuid.uuid4().hex[:8]}"
    subtype = args.get("type", "thought" if node_type == "narrative" else "agent")
    name = args.get("name", node_id)
    content = args.get("content", "")
    synthesis = args.get("synthesis") or (content[:100] if content else name)
    weight = args.get("weight", 1.0)
    energy = args.get("energy", 1.0)
    link_to = args.get("link_to", [])

    if not ctx.graph_ops:
        return _err("No graph connection available.")

    try:
        # Compute embedding
        embedding = None
        try:
            from runtime.infrastructure.embeddings.service import get_embedding_service
            embed_service = get_embedding_service()
            embedding = embed_service.embed(synthesis)
        except Exception as e:
            logger.warning(f"Could not compute embedding: {e}")

        if node_type == "narrative":
            ctx.graph_ops.add_narrative(
                id=node_id,
                name=name,
                content=content,
                type=subtype,
                weight=weight,
                embedding=embedding,
            )
            ctx.graph_ops._query(
                "MATCH (n {id: $id}) SET n.synthesis = $synthesis, n.energy = $energy, n.created_at_s = $ts",
                {"id": node_id, "synthesis": synthesis, "energy": energy, "ts": int(time.time())},
            )
        elif node_type == "actor":
            ctx.graph_ops.add_character(
                id=node_id,
                name=name,
                type=subtype,
                weight=weight,
                energy=energy,
                embedding=embedding,
            )
        else:
            return _err(f"Unknown node_type '{node_type}'. Use 'narrative' or 'actor'.")

        # Create links
        links_created = []
        for target_id in link_to:
            try:
                ctx.graph_ops._query("""
                    MATCH (source {id: $source_id})
                    MATCH (target {id: $target_id})
                    MERGE (source)-[r:link]->(target)
                    SET r.weight = 1.0, r.energy = 1.0
                """, {"source_id": node_id, "target_id": target_id})
                links_created.append(target_id)
            except Exception as e:
                logger.warning(f"Could not link to {target_id}: {e}")

        lines = [
            f"Created {node_type} node:",
            f"  ID: {node_id}",
            f"  Type: {subtype}",
            f"  Name: {name}",
            f"  Weight: {weight}",
            f"  Energy: {energy}",
        ]
        if content:
            lines.append(f"  Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        if links_created:
            lines.append(f"  Links created: {', '.join(links_created)}")

        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Node creation failed")
        return _err(f"Creating node: {e}")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
