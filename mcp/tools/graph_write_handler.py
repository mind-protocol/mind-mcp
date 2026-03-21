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


def infer_computed_type(dims: dict, source_label: str = "", target_label: str = "", target_type: str = "") -> str:
    """Infer the computed_type of a link by scoring against type signatures.

    Each type has an ideal dimensional signature (a vector of weights per dimension).
    For each candidate type, we compute a score = dot product of the link's actual
    dimensions with the type's signature, filtered by node-type compatibility.

    The highest-scoring compatible type wins. No hardcoded thresholds.

    If dimensions evolve (trust decays, affinity grows), the computed_type
    changes automatically — the link literally transforms its meaning.

    See: L3_LINK_DIMENSION_MAPPING.yaml → computed_type_grammar
    """
    sl = source_label.lower()
    tl = target_label.lower()

    # Extract dimensional values (default 0 for missing)
    h = dims.get("hierarchy", 0)
    a = dims.get("affinity", 0)
    p = dims.get("permanence", 0)
    pol = dims.get("polarity", 0)
    t = dims.get("trust", 0)
    rec = dims.get("recency", 0)
    v = dims.get("valence", 0)
    fr = dims.get("friction", 0)
    av = dims.get("aversion", 0)
    emoji = dims.get("emoji")
    ic = dims.get("interaction_count", 0)

    # Derived: how "ownership-like" is this link?
    ownership = max(0, -h)  # hierarchy < 0 = ownership
    extension = max(0, h)   # hierarchy > 0 = extends/elaborates

    # ── Type signatures: (score_formula, node_type_filter) ──
    # Score formula uses the actual dimension values.
    # Node filter: (source_types, target_types) — empty = any.
    candidates = {
        "created": (
            ownership * 3 + p * 2 + pol,
            ({"actor"}, {"moment", "thing"}),
        ),
        "responsible": (
            ownership * 2 + a * 3 + p * 2 + pol,
            ({"actor"}, {"narrative"}),
        ),
        "accountable": (
            ownership * 2 + p * 4 + pol,  # permanence dominates
            ({"actor"}, {"narrative"}),
        ),
        "role_holder": (
            ownership * 2 + a * 2 + p * 2 + pol,  # base score same range as responsible
            ({"actor"}, {"narrative"}),
            # Only wins when target_type=role gives the +5 bonus below
        ),
        "consulted": (
            t * 4 + a * 2 + pol + (1 - ownership) * 2,
            ({"actor"}, {"narrative"}),
        ),
        "informed": (
            (1 - a) * 2 + pol + (1 - ownership) * 2 + (1 - t) * 2,
            ({"actor"}, {"narrative"}),
        ),
        "contributes": (
            extension * 4 + pol * 2 + p,
            ({"narrative"}, {"narrative"}),
        ),
        "presence": (
            a * 3 + rec + (1 - ownership),
            ({"actor"}, {"space"}),
        ),
        "occurred_in": (
            extension * 3 + pol * 2,
            ({"moment"}, {"space"}),
        ),
        "mention": (
            pol * 3 + rec * 2,
            ({"moment", "narrative"}, {"actor"}),
        ),
        "reply": (
            extension * 3 + pol * 2 + rec,
            ({"moment"}, {"moment"}),
        ),
        "reaction": (
            3.0 if emoji else 0,  # emoji presence is the dominant signal
            ({"actor"}, {"moment"}),
        ),
        "follows": (
            a * 3 + pol * 2 + (1 - ownership),
            ({"actor"}, {"actor"}),
        ),
        "interaction": (
            min(ic, 10) * 0.3 + rec + a,  # interaction_count scaled
            ({"actor"}, {"actor"}),
        ),
    }

    # Role holder gets a bonus if the target is a role node
    if target_type == "role":
        score, filt = candidates["role_holder"]
        candidates["role_holder"] = (score + 5.0, filt)

    # Score each candidate, filter by node compatibility
    best_type = "relates"
    best_score = 0.0

    for ctype, (score, (src_filter, tgt_filter)) in candidates.items():
        # Node type compatibility
        if src_filter and sl and sl not in src_filter:
            continue
        if tgt_filter and tl and tl not in tgt_filter:
            continue

        if score > best_score:
            best_score = score
            best_type = ctype

    return best_type


TOOL_SCHEMA = {
    "name": "graph_write",
    "description": (
        "[THINK] Create a new node in the knowledge graph. "
        "Supports all 5 node types: narrative, actor, thing, moment, space. "
        "For narratives, use type to set the subtype: vision, mission, objective, "
        "initiative, project, programme, task, role, thought, fact, problem. "
        "Problem nodes gain weight while unresolved — use 'blocks' to link to blocked objectives. "
        "Use parent to auto-link into the hierarchy (CONTRIBUTES_TO). "
        "Use responsible/accountable/consulted/informed for RACI assignment. "
        "@mentions in content auto-create MENTIONS links."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "node_type": {
                "type": "string",
                "enum": ["narrative", "actor", "thing", "moment", "space"],
                "description": "The 5 universal node types.",
            },
            "id": {
                "type": "string",
                "description": (
                    "Unique node ID. Convention: {type}:{scope}:{slug}. "
                    "Example: 'objective:primers:raci_in_l3'. Auto-generated if omitted."
                ),
            },
            "type": {
                "type": "string",
                "description": (
                    "Subtype. For narratives: vision, mission, objective, initiative, "
                    "project, programme, task, role, thought, fact, problem."
                ),
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
                "description": "Short summary (for embedding). Auto-generated from content.",
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
                "description": "Node IDs to link to (generic link).",
            },
            "parent": {
                "type": "string",
                "description": "Parent narrative ID — creates CONTRIBUTES_TO link. For hierarchy: task→project→objective→mission→vision.",
            },
            "responsible": {
                "type": "string",
                "description": "Actor handle who does the work. Creates ASSIGNED_TO link with responsible=1.0.",
            },
            "accountable": {
                "type": "string",
                "description": "Actor handle who owns the outcome. Creates ASSIGNED_TO link with accountable=1.0.",
            },
            "consulted": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Actor handles to consult. Creates ASSIGNED_TO links with consultation=0.5.",
            },
            "informed": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Actor handles to inform. Creates ASSIGNED_TO links with information=0.3.",
            },
            "spaces": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Space IDs this narrative is relevant to. Creates OCCURRED_IN links.",
            },
            "things": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Thing IDs related to this narrative. Creates RELATES_TO links.",
            },
            "holder": {
                "type": "string",
                "description": "For type=role: the actor handle who holds this role. Creates HOLDS link.",
            },
            "blocks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "For type=problem: narrative IDs that this problem blocks. Creates tension links with negative polarity.",
            },
        },
        "required": ["node_type"],
    },
}

# Valid parent types for each narrative subtype
_VALID_PARENTS = {
    "task": {"project", "programme", "objective", "initiative", "mission"},
    "project": {"initiative", "programme", "objective"},
    "programme": {"initiative", "objective"},
    "initiative": {"objective", "mission"},
    "objective": {"mission"},
    "mission": {"vision"},
    "role": set(),  # roles don't have parents in the hierarchy
    "vision": set(),
    "problem": {"objective", "project", "initiative", "task"},  # problems block things
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
    # Problems start heavier — they create immediate tension in the graph
    default_weight = 3.0 if subtype == "problem" else 1.0
    default_energy = 1.5 if subtype == "problem" else 1.0
    weight = args.get("weight", default_weight)
    energy = args.get("energy", default_energy)
    link_to = args.get("link_to", [])

    if not ctx.graph_ops:
        return _err(
            "No graph connection available. "
            "FalkorDB may be unreachable — run `wsl -d Ubuntu-22.04 -- docker exec falkordb redis-cli PING` "
            "to wake WSL and verify the database is up, then retry."
        )

    # ── Schema validation — enforce invariants before any write ──
    try:
        from runtime.schema.validation import validate_node
        node_dict = {
            "type": subtype,
            "weight": weight,
            "energy": energy,
            "media": args.get("media", {}),
            "drives": args.get("drives", {}),
            "stress": args.get("stress"),
        }
        vr = validate_node(node_dict, layer="l1")
        if not vr.valid:
            error_msgs = "; ".join(f"[{e.invariant}] {e.message}" for e in vr.errors)
            return _err(f"Schema validation failed: {error_msgs}")
    except ImportError:
        pass  # validation module not yet available — proceed without

    try:
        # Compute embedding
        embedding = None
        try:
            from runtime.infrastructure.embeddings.service import get_embedding_service
            embed_service = get_embedding_service()
            embedding = embed_service.embed(synthesis)
        except Exception as e:
            logger.warning(f"Could not compute embedding: {e}")

        ts = int(time.time())

        if node_type == "narrative":
            ctx.graph_ops.add_narrative(
                id=node_id,
                name=name,
                content=content,
                type=subtype,
                weight=weight,
                embedding=embedding,
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
        elif node_type == "thing":
            ctx.graph_ops.add_thing(
                id=node_id,
                name=name,
                type=subtype,
                weight=weight,
                embedding=embedding,
            )
        elif node_type == "moment":
            ctx.graph_ops.add_moment(
                id=node_id,
                text=content or name,
                type=subtype,
                weight=weight,
                embedding=embedding,
            )
        elif node_type == "space":
            ctx.graph_ops._query(
                "MERGE (s {id: $id}) "
                "SET s.node_type = 'space', s.type = $type, "
                "s.name = $name, s.content = $content, "
                "s.synthesis = $synthesis, s.weight = $weight, "
                "s.energy = $energy, s.created_at_s = $ts",
                {"id": node_id, "type": subtype, "name": name,
                 "content": content, "synthesis": synthesis,
                 "weight": weight, "energy": energy, "ts": ts},
            )
        else:
            return _err(f"Unknown node_type '{node_type}'. Use: narrative, actor, thing, moment, space.")

        # Set common properties (synthesis, energy, timestamp) on all types
        ctx.graph_ops._query(
            "MATCH (n {id: $id}) SET n.synthesis = $synthesis, n.energy = $energy, n.created_at_s = $ts",
            {"id": node_id, "synthesis": synthesis, "energy": energy, "ts": ts},
        )

        # ── Smart auto-linking (all links are :LINK with dimensions) ──
        # Schema: schema-l3.yaml — relation_kind is ALWAYS null at L3
        # Semantics emerge from the 13 dimensional values, not from labels.
        # See: L3_LINK_DIMENSION_MAPPING.yaml for dimension signatures.
        links_created = []

        def _create_link(source, target, dims, tag=None, desc="",
                         source_label="", target_label="", target_type_field=""):
            """Create a :LINK with dimensional properties + computed_type."""
            # Infer computed_type from dimensions
            ct = infer_computed_type(dims, source_label, target_label, target_type_field)
            dim_sets = ", ".join(f"r.{k} = {v}" for k, v in dims.items() if isinstance(v, (int, float)))
            dim_sets += f", r.computed_type = '{ct}'"
            if tag:
                dim_sets += f", r.type = '{tag}'"
            try:
                ctx.graph_ops._query(
                    f"MATCH (s {{id: $s}}), (t {{id: $t}}) "
                    f"MERGE (s)-[r:LINK]->(t) SET {dim_sets}",
                    {"s": source, "t": target},
                )
                links_created.append(f"[{ct}] {desc}" if desc else f"[{ct}]→{target}")
            except Exception as e:
                logger.warning(f"Link failed ({desc}): {e}")

        # 1. Generic link_to
        for target_id in link_to:
            _create_link(node_id, target_id, {"recency": ts}, desc=f"link→{target_id}")

        # 2. Parent hierarchy (child contributes to parent)
        parent_id = args.get("parent")
        if parent_id:
            _create_link(node_id, parent_id,
                         {"hierarchy": 1.0, "polarity": 1.0, "permanence": 0.5},
                         tag="CONTRIBUTED", desc=f"→{parent_id}",
                         source_label="narrative", target_label="narrative")

        # 3. RACI — dimensional signatures
        responsible = args.get("responsible")
        if responsible:
            responsible = responsible.lstrip("@")
            ctx.graph_ops._query("MERGE (:Actor {id: $h})", {"h": responsible})
            _create_link(responsible, node_id,
                         {"hierarchy": -1.0, "affinity": 0.8, "permanence": 0.8, "polarity": 1.0},
                         desc=f"←@{responsible}",
                         source_label="actor", target_label="narrative")

        accountable = args.get("accountable")
        if accountable:
            accountable = accountable.lstrip("@")
            ctx.graph_ops._query("MERGE (:Actor {id: $h})", {"h": accountable})
            _create_link(accountable, node_id,
                         {"hierarchy": -1.0, "permanence": 1.0, "polarity": 1.0},
                         desc=f"←@{accountable}",
                         source_label="actor", target_label="narrative")

        for handle in (args.get("consulted") or []):
            handle = handle.lstrip("@")
            ctx.graph_ops._query("MERGE (:Actor {id: $h})", {"h": handle})
            _create_link(handle, node_id,
                         {"trust": 0.5, "affinity": 0.3, "polarity": 0.5},
                         desc=f"←@{handle}",
                         source_label="actor", target_label="narrative")

        for handle in (args.get("informed") or []):
            handle = handle.lstrip("@")
            ctx.graph_ops._query("MERGE (:Actor {id: $h})", {"h": handle})
            _create_link(handle, node_id,
                         {"affinity": 0.1, "polarity": 0.3},
                         desc=f"←@{handle}",
                         source_label="actor", target_label="narrative")

        # 4. Spaces
        for space_id in (args.get("spaces") or []):
            ctx.graph_ops._query("MERGE (:Space {id: $s})", {"s": space_id})
            _create_link(node_id, space_id,
                         {"hierarchy": 1.0, "polarity": 1.0},
                         desc=f"→{space_id}",
                         source_label=node_type, target_label="space")

        # 5. Things
        for thing_id in (args.get("things") or []):
            _create_link(node_id, thing_id, {"recency": ts},
                         desc=f"→{thing_id}",
                         source_label=node_type, target_label="thing")

        # 6. Role holder
        holder = args.get("holder")
        if holder and subtype == "role":
            holder = holder.lstrip("@")
            ctx.graph_ops._query("MERGE (:Actor {id: $h})", {"h": holder})
            _create_link(holder, node_id,
                         {"hierarchy": -1.0, "affinity": 0.9, "permanence": 0.9, "polarity": 1.0},
                         tag="HOLDS", desc=f"←@{holder}",
                         source_label="actor", target_label="narrative", target_type_field="role")

        # 7. @mentions in content
        import re
        for mentioned in re.findall(r"@(\w+)", content or ""):
            mentioned = mentioned.lower()
            ctx.graph_ops._query("MERGE (:Actor {id: $m})", {"m": mentioned})
            _create_link(node_id, mentioned,
                         {"polarity": 0.5, "recency": ts},
                         desc=f"→@{mentioned}",
                         source_label=node_type, target_label="actor")

        # 8. Problem blocks links
        if subtype == "problem":
            for blocked_id in (args.get("blocks") or []):
                _create_link(node_id, blocked_id,
                             {"polarity": -1.0, "permanence": 0.8, "friction": 0.5,
                              "hierarchy": 1.0},
                             desc=f"→blocks:{blocked_id}",
                             source_label="narrative", target_label="narrative")

        # 9. Auto-create sense + RACI routing for RACI-assigned narratives
        raci_gap = None
        sense_created = False
        if node_type == "narrative" and (responsible or accountable):
            try:
                from mcp.tools.raci_query import ensure_sense_coverage, route_sense_to_raci

                coverage = ensure_sense_coverage(node_id, ctx.graph_ops)

                if not coverage["has_sense"]:
                    # Auto-create a minimal sense that monitors this narrative's energy/weight
                    sense_id = f"sense:{node_id}"
                    import yaml
                    sense_def = {
                        "measure_query": (
                            f"MATCH (n {{id: '{node_id}'}}) "
                            f"RETURN n.energy, n.weight"
                        ),
                        "variables": ["energy", "weight"],
                        "outcomes": [],
                        "score": "first_outcome",
                        "eval_interval": 20,
                        "internalize": True,
                    }
                    ctx.graph_ops._query(
                        "CREATE (s:Thing {"
                        "  id: $sid, type: 'sense', "
                        "  name: $sname, "
                        "  content: $content, "
                        "  weight: 1.0, energy: 1.0"
                        "})",
                        {
                            "sid": sense_id,
                            "sname": f"Sense: {name}",
                            "content": yaml.dump(sense_def),
                        },
                    )
                    # Link sense → narrative (measures)
                    _create_link(sense_id, node_id,
                                 {"polarity": 1.0, "permanence": 1.0},
                                 desc=f"measures→{node_id}",
                                 source_label="thing", target_label="narrative")
                    # Route to RACI actors
                    route_sense_to_raci(sense_id, node_id, ctx.graph_ops)
                    sense_created = True
                    logger.info(f"Auto-created sense {sense_id} and routed to RACI actors")

                elif not coverage["sense_routed"]:
                    # Sense exists but not routed — fix routing
                    sense_rows = ctx.graph_ops._query(
                        "MATCH (s:Thing {type: 'sense'})-[r:LINK]->(n {id: $nid}) "
                        "WHERE r.computed_type = 'measures' "
                        "RETURN s.id LIMIT 1",
                        {"nid": node_id},
                    )
                    if sense_rows:
                        route_sense_to_raci(sense_rows[0][0], node_id, ctx.graph_ops)
                        sense_created = True
                        logger.info(f"Auto-routed existing sense to RACI actors of {node_id}")
                    else:
                        raci_gap = f"Sense routing failed for {node_id}"

            except ImportError:
                raci_gap = f"No sense (raci_query not available)"
            except Exception as e:
                logger.debug(f"RACI sense auto-creation failed: {e}")
                raci_gap = f"Sense auto-creation failed: {e}"

        lines = [
            f"Created {node_type} node:",
            f"  ID: {node_id}",
            f"  Type: {subtype}",
            f"  Name: {name}",
        ]
        if content:
            lines.append(f"  Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        if links_created:
            lines.append(f"  Links ({len(links_created)}):")
            for lk in links_created:
                lines.append(f"    {lk}")
        if sense_created:
            lines.append(f"  ✓ Sense auto-created and routed to RACI actors")
        if raci_gap:
            lines.append(f"  ⚠ Sense gap: {raci_gap}")

        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Node creation failed")
        return _err(f"Creating node: {e}")


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
