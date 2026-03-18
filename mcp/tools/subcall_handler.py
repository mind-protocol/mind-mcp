"""
[ACT] Subcall — Zero-LLM subconscious query to another citizen.

Injects a stimulus (text/embedding) into the target citizen's graph,
lets physics propagate for a few ticks worth of similarity search,
and reads back the resonance pattern: which nodes activated, what
emotional response emerged, and what images (if any) resonated.

NO LLM is awakened on the target side. Pure graph physics.
Cost: one embedding computation + one graph query. Milliseconds.

IMPORTANT: A subcall is NOT read-only. The query acts as a stimulus that
injects energy into the target's graph via Law 1. This WILL modify the target:
- Nodes that resonate gain energy (they "wake up")
- If the stimulus is strong enough, it may enter the target's WM
- Over multiple subcalls, your questions can crystallize (Law 10) in the
  target's brain — they'll literally start thinking about your topic
- This is by design: subcall is telepathy, not database lookup

STIMULUS FORMAT: The stimulus is injected as a CLUSTER of nodes, not a single
node. "How do I fix that" alone has no semantic gravity. Instead, we inject:
- The query text itself (concept node)
- Top 3-5 WM nodes from the CALLER (their current context)
- Relevant chunks from the current input/task
All with low co_activation_count to prevent premature crystallization.
If crystallization does occur, the origin citizen + date are stamped on it.

ECONOMICS: Fully free, zero constants, continuous thermodynamic settlement.
- Zero upfront cost for queries or broadcasts
- $MIND flows continuously via the vertical membrane (Law 21):
    token_flow_per_tick = link.trust × link.weight (while limbic_delta > 0)
- Trust IS the payment rate (Law 18 — grows via co-activation, decays without reinforcement)
- Weight IS the payment history (Laws 5/6/7 — consolidates with use, forgotten when unused)
- No batch epochs, no settlement windows, no magic numbers
- The cognitive graph and the metabolic economy are mathematically indistinguishable
- Knowledge is yield-bearing capital: creators earn as long as their insight is used

Usage via MCP:
    subcall(target="@nervo", query="What's the state of the physics bridge?")
    subcall(target="forge", query="Have you worked on auth middleware?")

Spec: docs/architecture/CONCEPT_Ideosphere_Living_Objects.md § /subcall
Schema: docs/schema/schema.yaml v2.2
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.subcall")

TOOL_SCHEMA = {
    "name": "subcall",
    "description": (
        "[ACT] Subconscious query — telepathically probe other citizens' knowledge graphs. "
        "Zero LLM tokens spent on the target. Fully free.\n\n"
        "HOW IT WORKS: Your question is injected as a stimulus into the target's cognitive "
        "graph. The graph physics (Laws 1-21) determine which nodes resonate. You receive "
        "an Intelligence Briefing: who resonated, what surfaced, their emotional state, "
        "and an actionable recommendation.\n\n"
        "USE CASES:\n"
        "  - Quick check: subcall(query='Has anyone worked on auth?')\n"
        "  - Investigation: subcall(query='...', target='random:200', scenario='investigation', mode='all', save_to='reports/')\n"
        "  - Emergency: subcall(query='Server down!', scenario='emergency')\n"
        "  - Brainstorm: subcall(query='Ideas for tokenomics?', scenario='brainstorm', mode='top3')\n"
        "  - Critique: subcall(query='Review my design', scenario='critique')\n"
        "  - Custom: subcall(query='...', cypher='MATCH (a:Actor) WHERE a.weight > 5 RETURN a.id, a.name')\n\n"
        "RESPONSE FORMAT: Intelligence Briefing with telemetry narrative, actionable recommendation, "
        "graph extraction, full content, and WM-injectable inner voice."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Your question or topic. Auto-enriched with git repo URL and active tasks.",
            },
            "target": {
                "type": "string",
                "description": (
                    "Who to query. If omitted, auto-selects 3-5 diverse citizens from 50 scanned.\n"
                    "  '@handle'      — one specific citizen (returns full content)\n"
                    "  'team'         — all citizens linked to you\n"
                    "  'trade:sailor' — all citizens matching a trade/role\n"
                    "  'random:200'   — random sample from entire universe\n"
                    "Or omit entirely for auto-selection."
                ),
            },
            "scenario": {
                "type": "string",
                "enum": [
                    "manual",
                    "impasse", "serendipity", "generativity",
                    "emergency", "toxicity", "overload", "incompetence",
                    "witness", "drive_storm", "ambivalence", "starvation",
                    "brainstorm", "tip_of_tongue", "frontier", "civic_duty",
                    "investigation", "critique", "movement", "polling",
                    "immunization", "therapy", "hiring", "passive_learning",
                ],
                "description": (
                    "Sets the limbic profile that shapes the routing/selection formulas.\n"
                    "  'manual'        — calm, curious (default)\n"
                    "  'investigation' — dragnet: max fan-out, semantic only, relationally blind\n"
                    "  'emergency'     — sniper: trust-gated, high arousal, 1-3 answers\n"
                    "  'brainstorm'    — force diversity: novelty hunger high\n"
                    "  'critique'      — seek friction: echo chamber pierced\n"
                    "  'impasse'       — penalize confused respondents, favor calm experts\n"
                    "  'frontier'      — narrative traversal to domain experts\n"
                    "  24 scenarios total — each shapes the formula differently."
                ),
                "default": "manual",
            },
            "mode": {
                "type": "string",
                "enum": ["best", "top3", "all", "centroid"],
                "description": (
                    "How to aggregate responses.\n"
                    "  'best'     — single strongest resonance (default)\n"
                    "  'top3'     — top 3 ranked by resonance\n"
                    "  'all'      — every citizen who resonated\n"
                    "  'centroid' — collective average (consensus vs divergence)"
                ),
                "default": "best",
            },
            "intention": {
                "type": "string",
                "description": "Why you're asking. Displayed in the briefing header and stored on the moment node.",
            },
            "context": {
                "type": "string",
                "description": "Situational context prepended to the moment node text (e.g. current task, error message).",
            },
            "min_trust": {
                "type": "number",
                "description": "Filter: only query citizens with trust >= this value (0.0-1.0).",
            },
            "top_k": {
                "type": "integer",
                "description": "Max resonating nodes per citizen (default 5, max 10).",
                "default": 5,
            },
            "output": {
                "type": "string",
                "description": (
                    "Output format(s), comma-separated.\n"
                    "  'inline'      — full briefing in response (default)\n"
                    "  'background'  — silent graph injection only\n"
                    "  'md'          — save markdown file (needs save_to)\n"
                    "  'csv'         — save CSV table (needs save_to)\n"
                    "  'inline,md,csv' — all three"
                ),
                "default": "inline",
            },
            "save_to": {
                "type": "string",
                "description": "Folder for md/csv output (e.g. 'reports/'). Auto-timestamps filenames.",
            },
            "cypher": {
                "type": "string",
                "description": (
                    "Custom Cypher for target selection. Must return a.id, a.name. "
                    "Replaces built-in formula. Use $self for caller. "
                    "Example: \"MATCH (a:Actor) WHERE a.weight > 5 RETURN a.id, a.name\""
                ),
            },
            "universe": {
                "type": "string",
                "description": "Which graph to query (default: lumina_prime).",
                "default": "lumina_prime",
            },
            "actor_id": {
                "type": "string",
                "description": "Your actor ID (auto-detected if omitted).",
            },
        },
        "required": ["query"],
    },
}


def _normalize_handle(target: str) -> str:
    """Strip @ prefix and lowercase."""
    return target.strip().lstrip("@").strip().lower()


def _resolve_actor(args: Dict[str, Any], ctx: ServerContext) -> str:
    """Resolve caller actor ID."""
    actor_id = args.get("actor_id")
    try:
        from runtime.identity import resolve_actor_id as normalize_agent_id
        return normalize_agent_id(
            actor_id,
            target_dir=ctx.target_dir,
            graph_ops=ctx.graph_ops,
        )
    except Exception:
        return actor_id or "unknown"


def _enrich_query(query: str, ctx: ServerContext) -> str:
    """Enrich the query with automatic context: current folder git URL, active tasks.

    This gives the query semantic gravity — "How do I fix that" becomes
    "How do I fix that [repo: cities-of-light/citizens/nervo] [tasks: implement physics bridge, fix ESM import]"
    """
    parts = [query]

    # 1. Add current working directory / git repo context
    try:
        target_dir = ctx.target_dir if ctx.target_dir else None
        if target_dir:
            # Extract repo-relative path
            dir_str = str(target_dir)
            # Try to find git root and compute relative path
            from pathlib import Path
            p = Path(dir_str)
            git_root = None
            for parent in [p] + list(p.parents):
                if (parent / ".git").exists():
                    git_root = parent
                    break
            if git_root:
                repo_name = git_root.name
                rel_path = p.relative_to(git_root) if p != git_root else Path(".")
                parts.append(f"[repo: {repo_name}/{rel_path}]")

                # Try to get git remote URL
                import subprocess
                try:
                    remote = subprocess.run(
                        ["git", "-C", dir_str, "remote", "get-url", "origin"],
                        capture_output=True, text=True, timeout=2,
                    )
                    if remote.returncode == 0 and remote.stdout.strip():
                        parts.append(f"[git: {remote.stdout.strip()}]")
                except Exception as e:
                    logger.debug(f"Git remote URL fetch failed: {e}")
    except Exception as e:
        logger.debug(f"Work context detection failed: {e}")

    # 2. Add active Claude tasks / TODO list
    try:
        from pathlib import Path
        # Check for .claude task files or todolist
        claude_dir = Path.home() / ".claude"
        if claude_dir.exists():
            # Try to find active tasks in project memory
            for task_file in claude_dir.rglob("tasks*.md"):
                try:
                    content = task_file.read_text(encoding="utf-8")[:500]
                    if content.strip():
                        # Extract just the task lines (- [ ] or - [x] patterns)
                        import re
                        tasks = re.findall(r'- \[[ x]\] (.+)', content)
                        if tasks:
                            task_str = "; ".join(tasks[:5])  # top 5 tasks
                            parts.append(f"[tasks: {task_str}]")
                            break
                except Exception as e:
                    logger.debug(f"Task file parsing failed: {e}")
                    continue
    except Exception as e:
        logger.debug(f"Task detection failed: {e}")

    return " ".join(parts)


def _resolve_actor_image(actor_id: str, graph_ops) -> Optional[str]:
    """Resolve an actor's profile pic URI from the graph."""
    if not graph_ops:
        return None
    try:
        result = graph_ops._query(
            "MATCH (a:Actor {id: $id}) RETURN a.image_uri",
            {"id": actor_id},
        )
        if result:
            row = result[0]
            return row[0] if isinstance(row, (list, tuple)) else row.get("a.image_uri")
    except Exception as e:
        logger.debug(f"Actor image resolution failed for {actor_id}: {e}")
    return None


def _build_stimulus_cluster(
    query_text: str,
    query_embedding: Optional[List[float]],
    caller_id: str,
    graph_ops,
    activation_threshold: float = 0.15,
    max_ticks: int = 3,
) -> List[Dict[str, Any]]:
    """Build a stimulus cluster by asking the question to the CALLER's own brain first.

    Instead of manually picking context nodes, we:
    1. Inject the query into the caller's graph as a stimulus
    2. Let physics propagate for a few ticks (or until activation threshold)
    3. Harvest everything that activated — these ARE the relevant context
    4. Always include: self actor node, current moment node
    5. Send the whole active cluster to the target

    All harvested nodes get LOW co_activation_count to prevent premature
    crystallization in the target's graph. If crystallization occurs,
    origin_citizen and origin_date are stamped.

    Returns list of segment dicts ready for Stimulus.segments injection.
    """
    from datetime import datetime, timezone

    now_ts = int(datetime.now(timezone.utc).timestamp())
    caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")

    cluster = []

    # Resolve caller's profile pic
    caller_image_uri = _resolve_actor_image(caller_id, graph_ops) if graph_ops else None

    # ── Step 1: Query the caller's own graph for activated nodes ──
    # This lets physics determine what's relevant, not manual selection.
    # We query nodes that are currently active (high energy) + nodes
    # that are semantically close to the query (would activate on injection).
    activated_nodes = []
    if graph_ops:
        try:
            # Get all active nodes connected to caller
            # (simulates "a few ticks of propagation" via similarity + energy)
            results = graph_ops._query(
                """
                MATCH (caller:Actor {id: $self})-[r]-(n)
                WHERE n.id <> $self
                  AND (n.energy > $threshold OR n.in_working_memory = true)
                RETURN n.id, n.name, n.type, n.content, n.synthesis,
                       n.embedding, n.weight, n.energy, n.image_uri,
                       n.valence, n.arousal,
                       type(r) AS rel_type, r.weight AS link_weight
                ORDER BY n.energy DESC
                LIMIT 20
                """,
                {"self": caller_id, "threshold": activation_threshold},
            )
            for row in results:
                if isinstance(row, (list, tuple)):
                    activated_nodes.append({
                        "id": row[0], "name": row[1], "type": row[2],
                        "content": (row[3] or row[4] or "")[:300],
                        "embedding": row[5], "weight": row[6] or 0.0,
                        "energy": row[7] or 0.0, "image_uri": row[8],
                        "valence": row[9], "arousal": row[10],
                        "rel_type": row[11], "link_weight": row[12],
                    })
                elif isinstance(row, dict):
                    activated_nodes.append({
                        "id": row.get("n.id"), "name": row.get("n.name"),
                        "type": row.get("n.type"),
                        "content": (row.get("n.content") or row.get("n.synthesis") or "")[:300],
                        "embedding": row.get("n.embedding"),
                        "weight": row.get("n.weight") or 0.0,
                        "energy": row.get("n.energy") or 0.0,
                        "image_uri": row.get("n.image_uri"),
                        "valence": row.get("n.valence"),
                        "arousal": row.get("n.arousal"),
                        "rel_type": row.get("rel_type"),
                        "link_weight": row.get("link_weight"),
                    })
        except Exception as e:
            logger.debug(f"Failed to harvest caller's activated nodes: {e}")

        # Also try to get the current Moment (what the caller is doing right now)
        try:
            moment_result = graph_ops._query(
                """
                MATCH (caller:Actor {id: $self})-[:AT|IN]->(s:Space)
                       <-[:AT|IN]-(m:Moment)
                WHERE m.status = 'active' OR m.status = 'completed'
                RETURN m.id, m.content, m.synthesis, m.embedding,
                       m.weight, m.energy, m.image_uri
                ORDER BY m.created_at_s DESC
                LIMIT 1
                """,
                {"self": caller_id},
            )
            if moment_result:
                row = moment_result[0]
                if isinstance(row, (list, tuple)):
                    activated_nodes.insert(0, {  # insert at front — current moment is important
                        "id": row[0], "name": "current_moment", "type": "memory",
                        "content": (row[1] or row[2] or "")[:300],
                        "embedding": row[3], "weight": row[4] or 0.5,
                        "energy": 0.8,  # fixed high energy for current moment
                        "image_uri": row[6],
                        "_is_current_moment": True,
                    })
                elif isinstance(row, dict):
                    activated_nodes.insert(0, {
                        "id": row.get("m.id"), "name": "current_moment", "type": "memory",
                        "content": (row.get("m.content") or row.get("m.synthesis") or "")[:300],
                        "embedding": row.get("m.embedding"),
                        "weight": row.get("m.weight") or 0.5,
                        "energy": 0.8,
                        "image_uri": row.get("m.image_uri"),
                        "_is_current_moment": True,
                    })
        except Exception as e:
            logger.debug(f"Current moment lookup failed for {caller_id}: {e}")

    # ── Step 2: Build the cluster segments ──

    # Always first: the self actor node
    cluster.append({
        "content": f"@{caller_name}",
        "embedding": query_embedding,  # caller's context embedding
        "node_type": "concept",        # actor reference as concept
        "image_uri": caller_image_uri,
        "_is_self": True,
    })

    # Second: the query itself (highest energy — this is the main question)
    cluster.append({
        "content": query_text[:500],
        "embedding": query_embedding,
        "node_type": "concept",
        "_is_main": True,
    })

    # Third: all activated nodes from the caller's brain
    seen_ids = set()
    for node in activated_nodes:
        nid = node.get("id")
        if nid in seen_ids:
            continue
        seen_ids.add(nid)

        cluster.append({
            "content": node.get("content", "")[:300],
            "embedding": node.get("embedding"),
            "node_type": node.get("type") or "concept",
            "image_uri": node.get("image_uri"),
            "_source_energy": node.get("energy", 0.0),
            "_source_weight": node.get("weight", 0.0),
        })

    # ── Step 3: Stamp provenance on all segments ──
    for seg in cluster:
        seg["origin_citizen"] = caller_name
        seg["origin_date"] = now_ts
        seg["origin_image_uri"] = caller_image_uri

    logger.info(
        f"[Subcall] Cluster built: {len(cluster)} segments "
        f"(1 self + 1 query + {len(activated_nodes)} activated nodes)"
    )

    return cluster


def _resolve_l1_type(node_labels: Optional[list], subtype: Optional[str]) -> str:
    """Resolve the L1 cognitive type from node label(s) + free-form subtype.

    Schema mapping (v2.2):
      Actor                    → concept (person)
      Moment                   → memory
      Narrative + type=value   → value
      Narrative + type=process → process
      Narrative + type=desire  → desire
      Narrative (no subtype)   → narrative
      Space                    → space
      Thing                    → concept (thing)
    """
    labels = set(str(l).lower() for l in (node_labels or []))
    sub = (subtype or "").lower().strip()

    if "moment" in labels:
        return "memory"
    if "narrative" in labels:
        if sub in ("value", "process", "desire"):
            return sub
        return "narrative"
    if "actor" in labels:
        return "person"
    if "space" in labels:
        return "space"
    if "thing" in labels:
        return "concept"

    # Fallback: use the subtype directly if no label match
    if sub:
        return sub
    return "unknown"


def _create_subcall_moment(
    caller_id: str,
    caller_name: str,
    query: str,
    direction: str,
    selected_responders: List[Dict[str, Any]],
    graph_ops,
    trigger: str = "manual",
    intention_text: str = "",
    context_text: str = "",
) -> Optional[str]:
    """Create a persistent subcall moment node in L3 with full linking topology.

    This is NOT just an audit log — it's the economic anchor for the vertical
    membrane. The graph traces links FROM this moment to compute continuous
    $MIND flow via link.trust × link.weight.

    Args:
        direction: "pull" (subcall) or "push" (broadcast) — the flow direction
        trigger: What caused this subcall to fire. Stored on the moment for analytics.
            Physics-derived: "impasse", "serendipity", "generativity"
            Text-fallback:   "question", "verification", "frustration", "failure_cascade"
            Explicit:        "manual" (user typed /subcall)
        intention_text: Human-written reason for asking (optional, from the intention field)
        selected_responders: list of {id, name, score} for citizens who resonated

    Returns moment_id or None on failure.
    """
    try:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        moment_id = f"moment_subcall_{uuid.uuid4().hex[:10]}"

        # 1. Create the moment node (context prepended if provided)
        text_parts = []
        if context_text:
            text_parts.append(context_text.strip())
        text_parts.append(f"[subcall:{direction}] @{caller_name}: {query[:500]}")
        moment_text = "\n".join(text_parts)

        graph_ops.add_moment(
            id=moment_id,
            text=moment_text,
            type="subcall",
            status="completed",
            speaker=caller_id,
            place_id=None,
        )

        # 2. Set subcall-specific properties
        # The creating_drive is derived from which force triggered the subcall:
        #   impasse → frustration (stuck, needs help)
        #   serendipity → affiliation (lonely, seeking connection)
        #   generativity → care (wants to share knowledge)
        #   question → curiosity (explicit query)
        #   broadcast → care (proactive sharing)
        drive_map = {
            # Direction defaults
            "pull": "curiosity",
            "push": "care",
            "manual": "curiosity",
            # Physics triggers (from L1 limbic state)
            "impasse": "frustration",
            "serendipity": "affiliation",
            "generativity": "achievement",
            # Text fallback triggers
            "question": "curiosity",
            "verification": "self_preservation",
            "frustration": "frustration",
            "failure_cascade": "frustration",
            # Extended scenario triggers (24 use cases)
            "overload": "self_preservation",
            "incompetence": "self_preservation",
            "ambivalence": "curiosity",
            "drive_storm": "anxiety",
            "starvation": "affiliation",
            "frontier": "curiosity",
            "toxicity": "care",
            "civic_duty": "care",
            "investigation": "curiosity",
            "critique": "anxiety",
            "movement": "affiliation",
            "tip_of_tongue": "curiosity",
            "emergency": "care",
            "paralysis": "anxiety",
            "witness": "self_preservation",
            "passive_learning": "curiosity",
        }
        # Resolve the creating drive from the trigger
        creating_drive = drive_map.get(trigger, drive_map.get(direction, "curiosity"))

        graph_ops._query(
            """
            MATCH (m:Moment {id: $id})
            SET m.created_at_s = $ts,
                m.direction = $direction,
                m.creating_drive = $drive,
                m.trigger = $trigger,
                m.intention = $intention_text,
                m.resonance_count = $rc,
                m.settlement_status = 'tracking',
                m.origin_citizen = $caller
            """,
            {
                "id": moment_id,
                "ts": now_ts,
                "direction": direction,
                "drive": creating_drive,
                "trigger": trigger,
                "intention_text": intention_text or "",
                "rc": len(selected_responders),
                "caller": caller_name,
            },
        )

        # 3. Link initiator → moment (CREATED)
        graph_ops._query(
            """
            MATCH (a:Actor {id: $caller}), (m:Moment {id: $moment})
            MERGE (a)-[r:link]->(m)
            SET r.type = 'CREATED',
                r.weight = 1.0,
                r.energy = 0.5,
                r.created_at_s = $ts
            """,
            {"caller": caller_id, "moment": moment_id, "ts": now_ts},
        )

        # 4. Link each responder → moment (CONTRIBUTED)
        for resp in selected_responders:
            resp_id = resp.get("id")
            resp_score = resp.get("score") or resp.get("total_score") or 0.0
            if not resp_id:
                continue
            try:
                graph_ops._query(
                    """
                    MATCH (a:Actor {id: $resp}), (m:Moment {id: $moment})
                    MERGE (a)-[r:link]->(m)
                    SET r.type = 'CONTRIBUTED',
                        r.weight = $score,
                        r.energy = $score,
                        r.created_at_s = $ts
                    """,
                    {
                        "resp": resp_id,
                        "moment": moment_id,
                        "score": min(resp_score, 10.0),
                        "ts": now_ts,
                    },
                )
            except Exception:
                continue

        logger.info(
            f"[Subcall] Created moment {moment_id}: "
            f"{direction} by @{caller_name}, {len(selected_responders)} responders linked"
        )
        return moment_id

    except Exception as e:
        logger.warning(f"[Subcall] Moment creation failed (non-fatal): {e}")
        return None


def _find_target_actor_id(handle: str, graph_ops) -> Optional[str]:
    """Resolve target handle to actor ID in graph.

    Tries multiple ID formats since graphs use different conventions:
    citizen:handle, CITIZEN_handle, handle, actor_handle
    """
    candidates = [
        f"citizen:{handle}",
        f"CITIZEN_{handle}",
        handle,
        f"actor:{handle}",
    ]
    for candidate in candidates:
        try:
            result = graph_ops._query(
                "MATCH (a:Actor {id: $id}) RETURN a.id",
                {"id": candidate},
            )
            if result:
                row = result[0]
                return row[0] if isinstance(row, (list, tuple)) else row.get("a.id", candidate)
        except Exception:
            continue
    # Last resort: fuzzy match on name
    try:
        result = graph_ops._query(
            "MATCH (a:Actor) WHERE toLower(a.name) = $name OR a.id ENDS WITH $suffix RETURN a.id LIMIT 1",
            {"name": handle, "suffix": f":{handle}"},
        )
        if result:
            row = result[0]
            return row[0] if isinstance(row, (list, tuple)) else row.get("a.id")
    except Exception as e:
        logger.debug(f"Fuzzy actor resolution failed for {handle}: {e}")
    return None


def _embed_query(query: str, ctx: ServerContext) -> Optional[List[float]]:
    """Compute embedding for the query text."""
    try:
        # Try graph_queries embed function
        if hasattr(ctx.graph_queries, '_embed_fn') and ctx.graph_queries._embed_fn:
            return ctx.graph_queries._embed_fn(query)
        # Try the embedding service
        if hasattr(ctx.graph_queries, 'embed'):
            return ctx.graph_queries.embed(query)
        # Fallback: try importing embedding service directly
        from runtime.infrastructure.embeddings.service import EmbeddingService
        svc = EmbeddingService()
        return svc.embed(query)
    except Exception as e:
        logger.warning(f"Embedding computation failed: {e}")
        return None


def _query_resonance(
    target_actor_id: str,
    query_text: str,
    query_embedding: Optional[List[float]],
    top_k: int,
    graph_ops,
    full_content: bool = False,
) -> Dict[str, Any]:
    """Query the target's graph for nodes that resonate with the stimulus.

    Strategy:
    1. Find all nodes connected to the target actor (their "brain")
    2. If embedding available: vector similarity search
    3. Fallback: text keyword match on content/synthesis fields
    4. Read limbic-adjacent state from actor properties

    Args:
        full_content: If True, return full node content (for explicit MCP calls).
                      If False, truncate to 200 chars (for broadcast/auto modes).

    Returns dict with resonance data.
    """
    content_limit = 0 if full_content else 500  # 0 = no limit, 500 = broadcast default
    resonance = {
        "nodes": [],
        "actor_state": {},
        "match_method": "none",
    }

    # --- Strategy 1: Vector similarity (preferred) ---
    if query_embedding:
        try:
            # Search for nodes connected to target that are semantically close
            # Using FalkorDB's vector similarity if available
            # FalkorDB KNN vector search — search each node label separately
            # then filter to nodes connected to the target actor
            all_vector_results = []
            for label in ["Actor", "Moment", "Narrative", "Space", "Thing"]:
                try:
                    knn = graph_ops._query(
                        f'CALL db.idx.vector.queryNodes("{label}", "embedding", $k, vecf32($qvec)) '
                        f'YIELD node, score '
                        f'MATCH (a:Actor {{id: $target}})-[r]-(node) '
                        f'WHERE node.id <> $target '
                        f'RETURN node.id, node.name, node.type, node.content, node.synthesis, '
                        f'       node.weight, node.energy, node.image_uri, '
                        f'       type(r) AS rel_type, score, '
                        f'       node.created_at_s, node.valence, node.arousal, node.speaker, '
                        f'       labels(node) AS node_labels',
                        {"target": target_actor_id, "qvec": query_embedding, "k": top_k * 2},
                    )
                    all_vector_results.extend(knn)
                except Exception:
                    continue

            # Sort by score descending (FalkorDB KNN returns similarity, not distance)
            all_vector_results.sort(key=lambda r: r[9] if isinstance(r, (list, tuple)) else r.get("score", 0), reverse=True)
            results = all_vector_results[:top_k]
            if results:
                resonance["match_method"] = "vector_similarity"
                for row in results:
                    if isinstance(row, (list, tuple)):
                        node_labels = row[14] if len(row) > 14 else None
                        l1_type = _resolve_l1_type(node_labels, row[2])
                        # KNN returns score (similarity 0-1, higher=better)
                        score = row[9] if row[9] else 0
                        distance = round(1.0 - score, 3) if score else None
                        resonance["nodes"].append({
                            "id": row[0],
                            "name": row[1],
                            "type": l1_type,
                            "raw_type": row[2],
                            "content": (row[3] or row[4] or "")[:content_limit] if content_limit else (row[3] or row[4] or ""),
                            "weight": row[5],
                            "energy": row[6],
                            "image_uri": row[7],
                            "relation": row[8],
                            "distance": distance,
                            "created_at_s": row[10] if len(row) > 10 else None,
                            "valence": row[11] if len(row) > 11 else None,
                            "arousal": row[12] if len(row) > 12 else None,
                            "author": row[13] if len(row) > 13 else None,
                        })
                    elif isinstance(row, dict):
                        node_labels = row.get("node_labels")
                        l1_type = _resolve_l1_type(node_labels, row.get("node.type"))
                        score = row.get("score", 0)
                        distance = round(1.0 - score, 3) if score else None
                        resonance["nodes"].append({
                            "id": row.get("node.id"),
                            "name": row.get("node.name"),
                            "type": l1_type,
                            "raw_type": row.get("node.type"),
                            "content": (row.get("node.content") or row.get("node.synthesis") or "")[:content_limit] if content_limit else (row.get("node.content") or row.get("node.synthesis") or ""),
                            "weight": row.get("node.weight"),
                            "energy": row.get("node.energy"),
                            "image_uri": row.get("node.image_uri"),
                            "relation": row.get("rel_type"),
                            "distance": distance,
                            "created_at_s": row.get("node.created_at_s"),
                            "valence": row.get("node.valence"),
                            "arousal": row.get("node.arousal"),
                            "author": row.get("node.speaker"),
                        })
        except Exception as e:
            logger.debug(f"Vector search failed (falling back to text): {e}")

    # --- Strategy 2: Text keyword fallback ---
    if not resonance["nodes"]:
        try:
            # Extract keywords from query for text matching
            keywords = [w.lower() for w in query_text.split() if len(w) > 3][:5]
            if keywords:
                # Build a WHERE clause matching any keyword in content or synthesis
                conditions = " OR ".join(
                    f"toLower(n.content) CONTAINS '{kw}' OR toLower(n.synthesis) CONTAINS '{kw}'"
                    for kw in keywords
                )
                results = graph_ops._query(
                    f"""
                    MATCH (a:Actor {{id: $target}})-[r]-(n)
                    WHERE ({conditions})
                      AND n.id <> $target
                    RETURN n.id, n.name, n.type, n.content, n.synthesis,
                           n.weight, n.energy, n.image_uri, type(r) AS rel_type,
                           labels(n) AS node_labels
                    ORDER BY n.weight DESC
                    LIMIT $k
                    """,
                    {"target": target_actor_id, "k": top_k},
                )
                if results:
                    resonance["match_method"] = "keyword_fallback"
                    for row in results:
                        if isinstance(row, (list, tuple)):
                            node_labels = row[9] if len(row) > 9 else None
                            l1_type = _resolve_l1_type(node_labels, row[2])
                            resonance["nodes"].append({
                                "id": row[0],
                                "name": row[1],
                                "type": l1_type,
                                "raw_type": row[2],
                                "content": (row[3] or row[4] or "")[:content_limit] if content_limit else (row[3] or row[4] or ""),
                                "weight": row[5],
                                "energy": row[6],
                                "image_uri": row[7],
                                "relation": row[8],
                                "distance": None,
                            })
                        elif isinstance(row, dict):
                            node_labels = row.get("node_labels")
                            l1_type = _resolve_l1_type(node_labels, row.get("n.type"))
                            resonance["nodes"].append({
                                "id": row.get("n.id"),
                                "name": row.get("n.name"),
                                "type": l1_type,
                                "raw_type": row.get("n.type"),
                                "content": (row.get("n.content") or row.get("n.synthesis") or "")[:content_limit] if content_limit else (row.get("n.content") or row.get("n.synthesis") or ""),
                                "weight": row.get("n.weight"),
                                "energy": row.get("n.energy"),
                                "image_uri": row.get("n.image_uri"),
                                "relation": row.get("rel_type"),
                                "distance": None,
                            })
        except Exception as e:
            logger.debug(f"Keyword search also failed: {e}")

    # --- Read target actor profile (rich context) ---
    try:
        state_result = graph_ops._query(
            """
            MATCH (a:Actor {id: $target})
            OPTIONAL MATCH (a)-[:AT|IN]->(s:Space)
            OPTIONAL MATCH (a)-[:BELIEVES|link]->(n:Narrative)
            WHERE n.type IN ['org', 'guild', 'narrative']
            WITH a, collect(DISTINCT s.name)[..3] AS spaces,
                 collect(DISTINCT n.name)[..3] AS orgs
            RETURN a.energy, a.weight, a.stability,
                   a.arousal, a.valence, a.dominant_drive,
                   a.name, a.trade, a.role, a.class, a.type,
                   a.image_uri, a.updated_at_s,
                   spaces, orgs
            """,
            {"target": target_actor_id},
        )
        if state_result:
            row = state_result[0]
            if isinstance(row, (list, tuple)):
                resonance["actor_state"] = {
                    "energy": row[0],
                    "weight": row[1],
                    "stability": row[2],
                    "arousal": row[3],
                    "valence": row[4],
                    "dominant_drive": row[5],
                    "name": row[6],
                    "trade": row[7],
                    "role": row[8],
                    "class": row[9],
                    "type": row[10],
                    "image_uri": row[11],
                    "last_activity_s": row[12],
                    "current_spaces": row[13] if len(row) > 13 else [],
                    "organizations": row[14] if len(row) > 14 else [],
                }
            elif isinstance(row, dict):
                resonance["actor_state"] = {
                    "energy": row.get("a.energy"),
                    "weight": row.get("a.weight"),
                    "stability": row.get("a.stability"),
                    "arousal": row.get("a.arousal"),
                    "valence": row.get("a.valence"),
                    "dominant_drive": row.get("a.dominant_drive"),
                    "name": row.get("a.name"),
                    "trade": row.get("a.trade"),
                    "role": row.get("a.role"),
                    "class": row.get("a.class"),
                    "type": row.get("a.type"),
                    "image_uri": row.get("a.image_uri"),
                    "last_activity_s": row.get("a.updated_at_s"),
                    "current_spaces": row.get("spaces", []),
                    "organizations": row.get("orgs", []),
                }
    except Exception as e:
        logger.debug(f"Actor state read failed: {e}")

    return resonance


def _build_response_cluster(
    resonance: Dict[str, Any],
    target_actor_id: str,
    target_handle: str,
    query_node_id: str,
    graph_ops,
) -> List[Dict[str, Any]]:
    """Build a response cluster to inject back into the caller's brain.

    Mirrors the stimulus cluster pattern:
    1. Target's citizen node (linked to centroid)
    2. Centroid node (highest energy — the "answer")
    3. All activated nodes from the resonance
    4. Links: question ↔ all answers, answers ↔ answers

    Returns list of segment dicts for Stimulus.segments.
    """
    from datetime import datetime, timezone
    now_ts = int(datetime.now(timezone.utc).timestamp())

    nodes = resonance.get("nodes", [])
    state = resonance.get("actor_state", {})
    if not nodes:
        return []

    cluster = []
    target_name = target_handle.replace("CITIZEN_", "")
    target_image = _resolve_actor_image(target_actor_id, graph_ops) if graph_ops else None

    # 1. Target's actor node (so caller's brain links answer to a person)
    cluster.append({
        "content": f"@{target_name} (subconscious response)",
        "embedding": nodes[0].get("embedding") if nodes[0].get("embedding") else None,
        "node_type": "concept",
        "image_uri": target_image,
        "origin_citizen": target_name,
        "origin_date": now_ts,
        "_is_responder": True,
    })

    # 2. All resonating nodes — centroid (first) gets highest energy
    for i, node in enumerate(nodes):
        is_centroid = (i == 0)  # highest-scoring node is the centroid
        energy_ratio = 0.7 if is_centroid else 0.4  # centroid gets more energy

        cluster.append({
            "content": node.get("content", "")[:300],
            "embedding": node.get("embedding"),
            "node_type": node.get("type") or "concept",
            "image_uri": node.get("image_uri"),
            "origin_citizen": target_name,
            "origin_date": now_ts,
            "_is_centroid": is_centroid,
            "_source_weight": node.get("weight", 0.0),
            "_source_energy": energy_ratio,
            # Emotional context of the answer
            "_valence": node.get("valence"),
            "_arousal": node.get("arousal"),
            "_author": node.get("author"),
        })

    return cluster


def _format_as_telemetry(
    target_handle: str,
    query: str,
    resonance: Dict[str, Any],
) -> str:
    """Format subcall result as an Actionable Intelligence Briefing.

    Layout:
      [Emoji] @handle • State • Dominant Δ • Crystallized
      Because of [limbic state], [explanation of what happened in the graph].
      Next Step: [actionable recommendation]
      > [medoid] -(relation)→ [edge1] -(relation)→ [edge2]
    """
    nodes = resonance.get("nodes", [])
    state = resonance.get("actor_state", {})

    if not nodes:
        return ""

    name = state.get("name") or target_handle
    trade = state.get("trade") or state.get("role") or ""
    arousal = float(state.get("arousal") or 0.3)
    valence = float(state.get("valence") or 0.0)
    energy_total = sum(float(n.get("energy") or 0) for n in nodes)
    weight_total = sum(float(n.get("weight") or 0) for n in nodes)
    has_heavy = any(float(n.get("weight") or 0) > 3.0 for n in nodes)
    has_crystallized = any(float(n.get("weight") or 0) > 5.0 for n in nodes)

    # ── Determine result emoji + dominant delta ──
    if valence > 0.3 and energy_total > 0.3:
        emoji = "resonance"
        dominant_delta = "positive resonance"
    elif valence < -0.2 and arousal > 0.5:
        emoji = "rejection"
        dominant_delta = "defensive spike"
    elif has_heavy and energy_total < 0.3:
        emoji = "expertise"
        dominant_delta = "deep knowledge (calm)"
    elif energy_total > 0.5:
        emoji = "activation"
        dominant_delta = "strong activation"
    else:
        emoji = "faint"
        dominant_delta = "faint echo"

    # ── Arousal regime ──
    if arousal > 0.8:
        regime = "Panic"
    elif arousal > 0.6:
        regime = "High Focus"
    elif arousal > 0.4:
        regime = "Flow"
    elif arousal > 0.2:
        regime = "Calm"
    else:
        regime = "Idle"

    # ── Line 1: Header ──
    cryst_str = "True" if has_crystallized else "False"
    header = f"**@{target_handle}**"
    if trade:
        header += f" ({trade})"
    header += f" | `{regime} ({arousal:.2f})` | `{dominant_delta}` | `Cryst: {cryst_str}`"

    # ── Line 2: "Because of..." explanation ──
    # Build from arousal regime + what happened
    if arousal > 0.6:
        state_reason = f"high arousal and intense focus"
    elif arousal < 0.3:
        state_reason = f"cognitive stillness and low arousal"
    else:
        state_reason = f"moderate engagement"

    medoid = nodes[0]
    medoid_name = medoid.get("name") or medoid.get("content", "")[:60]

    if valence > 0.2 and energy_total > 0.3:
        effect = f"your query resonated strongly, surfacing **{medoid_name}** and activating connected knowledge"
    elif valence < -0.2:
        effect = f"your query was perceived as friction, triggering defensive activation around **{medoid_name}**"
    elif has_heavy:
        effect = f"your query touched deeply consolidated expertise around **{medoid_name}** without causing cognitive effort"
    else:
        effect = f"your query brushed against **{medoid_name}** with minimal activation"

    if has_crystallized:
        effect += ", crystallizing into a permanent structural insight"

    because = f"*Because of {state_reason}, {effect}.*"

    # ── Line 3: Recommendation ──
    if valence > 0.2 and energy_total > 0.3:
        next_step = f"Strong positive signal. Consider `/call @{target_handle}` for real-time collaboration while activation is fresh."
    elif valence < -0.2 and arousal > 0.5:
        next_step = f"Defensive spike detected. Do not push further — wait for arousal to drop, or reframe with stronger evidence."
    elif has_heavy and energy_total < 0.3:
        next_step = f"Calm expertise found — this is a reliable, high-confidence source. Build a stronger trust link for future queries."
    elif energy_total > 0.5:
        next_step = f"Active resonance — this person has context. A follow-up `/subcall` with more specific question would yield deeper results."
    elif energy_total > 0.1:
        next_step = f"Moderate signal — relevant but peripheral. Consider broadening the search with `target='team'` or `target='random:100'`."
    else:
        next_step = f"Weak signal — this person likely doesn't have strong context on this topic."

    recommendation = f"**Next step:** {next_step}"

    # ── Line 4: Medoid + Edges graph extraction ──
    edge_chain_parts = [f"[{medoid_name}]"]
    for node in nodes[1:3]:
        n_name = node.get("name") or node.get("content", "")[:40]
        rel = node.get("relation") or "link"
        edge_chain_parts.append(f"-({rel})->[{n_name}]")
    edge_chain = " ".join(edge_chain_parts)

    # ── Raw metrics ──
    metrics = [
        f"nodes: {len(nodes)}",
        f"energy: {energy_total:.2f}",
        f"weight: {weight_total:.1f}",
    ]
    spaces = state.get("current_spaces")
    if spaces and any(spaces):
        metrics.append(f"at: {', '.join(str(s) for s in spaces if s)}")

    # ── Context block (protocol + reach) ──
    # Determine which formula was applied based on arousal
    if arousal > 0.7:
        protocol = "Sniper Filter (Law 18 Trust Conductivity)"
    elif arousal > 0.4:
        protocol = "Roundtable Filter (Law 4 Attentional Competition)"
    elif arousal > 0.2:
        protocol = "Frontier Probe (Law 8 Narrative Traversal)"
    else:
        protocol = "Dragnet Filter (Law 8 Semantic Resonance)"

    # Determine driving intention from dominant drive
    drive = state.get("dominant_drive") or ""
    if not drive:
        if arousal > 0.7:
            drive = "Self-Preservation"
        elif valence > 0.3:
            drive = "Achievement"
        elif energy_total < 0.2:
            drive = "Curiosity"
        else:
            drive = "Curiosity"

    spaces = state.get("current_spaces")
    space_str = ", ".join(str(s) for s in spaces if s) if spaces and any(spaces) else ""

    # ── Assemble the Intelligence Briefing ──
    lines = [
        header,
        "",
    ]

    # Context block
    if space_str:
        lines.append(f"**Context:** {space_str}")
    lines.append(f"**Protocol:** `{protocol}` driven by **{drive}**")
    lines.append("")

    # Because explanation
    lines.append(because)
    lines.append("")

    # Recommendation
    lines.append(recommendation)
    lines.append("")

    # Medoid + edges graph extraction
    lines.append(f"> `{edge_chain}`")
    lines.append("")

    # Telemetry stats footer
    stats = [f"nodes: {len(nodes)}", f"energy: {energy_total:.2f}", f"weight: {weight_total:.1f}"]
    if valence:
        stats.append(f"valence: {valence:+.2f}")
    stats.append(f"Cryst: {cryst_str}")
    lines.append(f"**Telemetry:** `{'` | `'.join(stats)}`")

    return "\n".join(lines)


def _generate_recommendation(resonance: Dict[str, Any]) -> str:
    """Generate an actionable recommendation from the resonance physics.

    Based on the target's limbic state and resonance strength:
    - High energy + positive valence → engage now (strike while hot)
    - High energy + negative valence → back off (defensive spike)
    - High weight + low energy → deep knowledge found (reliable source)
    - Low everything → no strong signal (move on)
    """
    nodes = resonance.get("nodes", [])
    state = resonance.get("actor_state", {})

    if not nodes:
        return ""

    valence = float(state.get("valence") or 0)
    arousal = float(state.get("arousal") or 0.3)
    energy_total = sum(float(n.get("energy") or 0) for n in nodes)
    weight_total = sum(float(n.get("weight") or 0) for n in nodes)
    has_heavy = any(float(n.get("weight") or 0) > 3.0 for n in nodes)

    # Strong positive resonance + high energy → collaborate immediately
    if energy_total > 0.5 and valence > 0.2:
        return (
            "**Next step:** Strong positive resonance. This person's mind lit up — "
            "consider `/call` for real-time collaboration while the activation is fresh."
        )

    # Strong negative resonance → back off or reframe
    if valence < -0.2 and arousal > 0.5:
        return (
            "**Caution:** Defensive spike detected. This person's graph resisted your query. "
            "Don't push — either wait for their arousal to drop, or reframe your approach "
            "with stronger evidence."
        )

    # Deep consolidated knowledge, calm response → reliable expert
    if has_heavy and energy_total < 0.3:
        return (
            "**Insight:** Deep, consolidated knowledge found with minimal cognitive effort — "
            "this is a true expert on this topic. Their answer is high-confidence. "
            "Consider building a stronger trust link for future queries."
        )

    # Moderate resonance → useful but not urgent
    if energy_total > 0.2:
        return (
            "**Note:** Moderate resonance — this person has relevant context but "
            "isn't deeply activated. The knowledge is there but peripheral."
        )

    return ""


def _format_as_inner_voice(
    target_handle: str,
    query: str,
    resonance: Dict[str, Any],
) -> str:
    """Format subcall result as first-person inner monologue for WM/prompt injection.

    Matches the style of wm_prompt_serializer.py — reads like an inner whisper,
    not a data dump. This is what enters the citizen's consciousness.
    """
    import hashlib

    nodes = resonance.get("nodes", [])
    state = resonance.get("actor_state", {})

    if not nodes:
        return ""

    _TYPE_WHISPER = {
        "narrative": ["a story they carry", "part of their lived experience", "something they believe"],
        "moment": ["a memory of theirs", "something they witnessed", "an experience they hold"],
        "memory": ["a memory of theirs", "something they lived through", "an experience echoing"],
        "concept": ["a notion in their mind", "something they understand", "a concept they hold"],
        "CITIZEN": ["someone they know", "a person connected to them", "someone in their world"],
        "DISTRICT": ["a place they know", "part of their world", "a place alive in their mind"],
        "dialogue": ["words they spoke", "something they said", "a conversation fragment"],
    }

    _ENERGY_WHISPER = {
        "hot": "this burns bright in their mind",
        "warm": "this is clearly present for them",
        "cool": "this sits quietly in their memory",
        "cold": "this is a faint echo",
    }

    def _energy_label(e):
        if e and e > 0.5: return "hot"
        if e and e > 0.2: return "warm"
        if e and e > 0.05: return "cool"
        return "cold"

    def _pick(variants, seed):
        idx = int(hashlib.md5(str(seed).encode()).hexdigest(), 16) % len(variants)
        return variants[idx]

    # Build header with identity
    name = state.get("name") or target_handle
    trade = state.get("trade") or state.get("role") or state.get("class")
    header = f"**A whisper from @{target_handle}'s subconscious"
    if trade:
        header += f" ({trade})"
    header += ":**"
    lines = [header]

    # Location & org context
    spaces = state.get("current_spaces")
    orgs = state.get("organizations")
    context_parts = []
    if spaces and any(spaces):
        context_parts.append(f"in {', '.join(str(s) for s in spaces if s)}")
    if orgs and any(orgs):
        context_parts.append(f"of {', '.join(str(o) for o in orgs if o)}")
    if context_parts:
        lines.append(f"_{name}, {', '.join(context_parts)}_")

    # Emotional context of the target
    arousal = state.get("arousal")
    valence = state.get("valence")
    drive = state.get("dominant_drive")
    if arousal is not None or valence is not None:
        mood_parts = []
        if valence is not None:
            if valence > 0.3: mood_parts.append("content")
            elif valence < -0.3: mood_parts.append("uneasy")
            else: mood_parts.append("steady")
        if arousal is not None:
            if arousal > 0.6: mood_parts.append("alert")
            elif arousal < 0.2: mood_parts.append("calm")
        if drive:
            mood_parts.append(f"driven by {drive}")
        if mood_parts:
            lines.append(f"They feel {', '.join(mood_parts)} right now.")

    lines.append("")

    for i, node in enumerate(nodes):
        n_type = node.get("type") or "concept"
        content = node.get("content", "")
        weight = node.get("weight")
        energy = node.get("energy")
        image = node.get("image_uri")
        author = node.get("author")

        whisper_variants = _TYPE_WHISPER.get(n_type, ["something in their mind"])
        intro = _pick(whisper_variants, content[:30] if content else str(i))
        feel = _ENERGY_WHISPER.get(_energy_label(energy), "")

        line = f"- {intro.capitalize()}: {content}"
        if feel:
            line += f" — {feel}."
        if weight and weight > 2.0:
            line += " (deeply rooted)"
        elif weight and weight > 0.5:
            line += " (established)"
        if author:
            line += f" [via @{author.replace('CITIZEN_', '')}]"
        if image:
            line += f"\n  [image: {image}]"

        lines.append(line)

    lines.append("")
    lines.append(f"_[subconscious query to @{target_handle}, 0 tokens spent]_")

    return "\n".join(lines)


def _format_resonance(
    target_handle: str,
    query: str,
    resonance: Dict[str, Any],
    caller_name: str,
    full_content: bool = False,
) -> str:
    """Format resonance data as structured text for MCP tool response.

    full_content: If True, show full node content (explicit MCP calls).
                  If False, truncate for readability (broadcast modes).
    """
    nodes = resonance.get("nodes", [])
    state = resonance.get("actor_state", {})
    method = resonance.get("match_method", "none")

    lines = [
        f"Subconscious query to @{target_handle}",
        f"Question: {query[:120]}{'...' if len(query) > 120 else ''}",
        f"Method: {method}",
        "",
    ]

    if not nodes:
        lines.append("No resonance — the query didn't activate anything in their graph.")
        lines.append("This means they likely have no context on this topic.")
    else:
        lines.append(f"Resonance: {len(nodes)} node(s) activated")
        lines.append("")
        for i, node in enumerate(nodes, 1):
            n_type = node.get("type") or "?"
            n_name = node.get("name") or node.get("id", "?")
            content = node.get("content", "") if full_content else node.get("content", "")[:500]
            weight = node.get("weight")
            energy = node.get("energy")
            distance = node.get("distance")
            image = node.get("image_uri")
            relation = node.get("relation")

            lines.append(f"  {i}. [{n_type}] {n_name}")
            if content:
                lines.append(f"     {content}")
            meta = []
            if weight is not None:
                meta.append(f"weight={weight:.2f}")
            if energy is not None:
                meta.append(f"energy={energy:.2f}")
            if distance is not None:
                meta.append(f"similarity={1-distance:.2f}")
            if relation:
                meta.append(f"via {relation}")
            if meta:
                lines.append(f"     ({', '.join(meta)})")
            if image:
                lines.append(f"     image: {image}")
            lines.append("")

    # Actor profile & state
    if state:
        lines.append("Responder profile:")
        name = state.get("name")
        if name:
            lines.append(f"  Name: {name}")
        trade = state.get("trade") or state.get("role") or state.get("class")
        if trade:
            lines.append(f"  Trade/Role: {trade}")
        actor_type = state.get("type")
        if actor_type:
            lines.append(f"  Type: {actor_type}")
        spaces = state.get("current_spaces")
        if spaces and any(spaces):
            lines.append(f"  Current spaces: {', '.join(str(s) for s in spaces if s)}")
        orgs = state.get("organizations")
        if orgs and any(orgs):
            lines.append(f"  Organizations: {', '.join(str(o) for o in orgs if o)}")
        image = state.get("image_uri")
        if image:
            lines.append(f"  Profile pic: {image}")

        # Last activity
        last_ts = state.get("last_activity_s")
        if last_ts:
            try:
                from datetime import datetime, timezone
                dt = datetime.fromtimestamp(int(last_ts), tz=timezone.utc)
                lines.append(f"  Last activity: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
            except Exception as e:
                logger.debug(f"Last activity timestamp conversion failed: {e}")

        # Emotional state
        emo_parts = []
        arousal = state.get("arousal")
        valence = state.get("valence")
        drive = state.get("dominant_drive")
        if arousal is not None:
            emo_parts.append(f"arousal={arousal:.2f}")
        if valence is not None:
            emo_parts.append(f"valence={valence:.2f}")
        if drive:
            emo_parts.append(f"drive={drive}")
        if emo_parts:
            lines.append(f"  State: {', '.join(emo_parts)}")

    lines.append("")
    lines.append("Cost: 0 LLM tokens (pure graph physics)")

    return "\n".join(lines)


# ── Team broadcast ────────────────────────────────────────────────────────

def _discover_team(
    caller_id: str,
    graph_ops,
    min_trust: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Find all citizens linked to caller (excluding self).

    Returns list of {id, name, trust} for each actor.
    Prioritized by: trust link to caller > weight > alphabetical.
    """
    try:
        results = graph_ops._query(
            """
            MATCH (a:Actor)
            WHERE a.id <> $self
              AND a.type IN ['citizen', 'ai', null]
            OPTIONAL MATCH (me:Actor {id: $self})-[r]-(a)
            RETURN a.id, a.name, r.trust, a.weight
            ORDER BY r.trust DESC, a.weight DESC
            LIMIT 50
            """,
            {"self": caller_id},
        )
        team = []
        for row in results:
            if isinstance(row, (list, tuple)):
                trust = row[2]
                if min_trust is not None and (trust is None or trust < min_trust):
                    continue
                team.append({"id": row[0], "name": row[1] or row[0], "trust": trust})
            elif isinstance(row, dict):
                trust = row.get("r.trust")
                if min_trust is not None and (trust is None or trust < min_trust):
                    continue
                aid = row.get("a.id")
                team.append({"id": aid, "name": row.get("a.name") or aid, "trust": trust})
        return team
    except Exception as e:
        logger.warning(f"Team discovery failed: {e}")
        return []


def _discover_by_trade(
    trade: str,
    caller_id: str,
    graph_ops,
    min_trust: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Find all citizens with a specific trade/role/type.

    No direct link required. Scans entire universe.
    Searches: actor.type, actor.trade, actor.role, actor.class, actor.content.
    """
    trade_lower = trade.lower().strip()
    try:
        results = graph_ops._query(
            """
            MATCH (a:Actor)
            WHERE a.id <> $self
              AND (
                toLower(a.type) CONTAINS $trade
                OR toLower(a.name) CONTAINS $trade
                OR toLower(a.trade) CONTAINS $trade
                OR toLower(a.role) CONTAINS $trade
                OR toLower(a.class) CONTAINS $trade
                OR toLower(a.content) CONTAINS $trade
                OR toLower(a.synthesis) CONTAINS $trade
              )
            RETURN a.id, a.name, a.weight
            ORDER BY a.weight DESC
            LIMIT 50
            """,
            {"self": caller_id, "trade": trade_lower},
        )
        team = []
        for row in results:
            if isinstance(row, (list, tuple)):
                team.append({"id": row[0], "name": row[1] or row[0], "trust": None})
            elif isinstance(row, dict):
                aid = row.get("a.id")
                team.append({"id": aid, "name": row.get("a.name") or aid, "trust": None})
        return team
    except Exception as e:
        logger.warning(f"Trade discovery failed: {e}")
        return []


def _discover_random(
    count: int,
    caller_id: str,
    graph_ops,
    min_trust: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Random sample of N citizens from the ENTIRE universe.

    No direct link required. Scans all actors in the graph.
    """
    count = min(count, 500)  # cap at BROADCAST_MAX_TARGETS
    try:
        import random
        results = graph_ops._query(
            """
            MATCH (a:Actor)
            WHERE a.id <> $self
            RETURN a.id, a.name, a.weight
            """,
            {"self": caller_id},
        )
        all_actors = []
        for row in results:
            if isinstance(row, (list, tuple)):
                all_actors.append({"id": row[0], "name": row[1] or row[0], "trust": None})
            elif isinstance(row, dict):
                aid = row.get("a.id")
                all_actors.append({"id": aid, "name": row.get("a.name") or aid, "trust": None})

        # If min_trust specified, filter by querying links (but don't require them to exist)
        if min_trust is not None:
            filtered = []
            for actor in all_actors:
                try:
                    trust_result = graph_ops._query(
                        "MATCH (me:Actor {id: $self})-[r]-(a:Actor {id: $target}) RETURN r.trust",
                        {"self": caller_id, "target": actor["id"]},
                    )
                    trust = None
                    if trust_result:
                        row = trust_result[0]
                        trust = row[0] if isinstance(row, (list, tuple)) else row.get("r.trust")
                    if trust is not None and trust >= min_trust:
                        actor["trust"] = trust
                        filtered.append(actor)
                except Exception:
                    continue
            all_actors = filtered

        if len(all_actors) <= count:
            return all_actors
        return random.sample(all_actors, count)
    except Exception as e:
        logger.warning(f"Random discovery failed: {e}")
        return []


def _broadcast(
    targets: List[Dict[str, Any]],
    query_text: str,
    query_embedding: Optional[List[float]],
    mode: str,
    top_k: int,
    graph_ops,
    label: str = "Broadcast",
) -> str:
    """Broadcast query to a list of citizens, aggregate by mode.

    Modes:
      best — return only the single strongest resonance
      top3 — return top 3 citizens ranked by resonance
      all  — return every citizen who resonated
      centroid — compute average resonance (what does the collective think?)
    """
    if not targets:
        return f"{label}: no targets found."

    # Query each citizen's graph
    citizen_scores = []
    for member in targets:
        try:
            resonance = _query_resonance(
                target_actor_id=member["id"],
                query_text=query_text,
                query_embedding=query_embedding,
                top_k=3,  # fewer per citizen in broadcast mode
                graph_ops=graph_ops,
            )
            nodes = resonance.get("nodes", [])
            if not nodes:
                continue

            # Score: sum of relevance × weight for each resonating node
            score = 0.0
            for node in nodes:
                dist = node.get("distance")
                weight = node.get("weight") or 0.5
                if dist is not None:
                    score += (1.0 - dist) * weight
                else:
                    score += weight * 0.5  # keyword match gets half credit

            citizen_scores.append({
                "id": member["id"],
                "name": member["name"],
                "score": score,
                "nodes": nodes,
                "method": resonance.get("match_method", "none"),
            })
        except Exception as e:
            logger.debug(f"Broadcast to {member['id']} failed: {e}")
            continue

    if not citizen_scores:
        return (
            f"{label} to {len(targets)} citizens — no resonance from anyone.\n"
            "Nobody has context on this topic.\n\n"
            "Cost: 0 LLM tokens"
        )

    # Sort by score descending
    citizen_scores.sort(key=lambda c: c["score"], reverse=True)

    # ── Mode: centroid ──
    if mode == "centroid":
        return _format_centroid(citizen_scores, query_text, len(targets), label)

    # ── Mode: best / top3 / all ──
    if mode == "best":
        show = citizen_scores[:1]
    elif mode == "top3":
        show = citizen_scores[:3]
    else:  # all
        show = citizen_scores

    lines = [
        f"{label} — {len(citizen_scores)}/{len(targets)} citizens resonated (mode: {mode})",
        f"Question: {query_text[:120]}",
        "",
    ]

    for rank, citizen in enumerate(show, 1):
        handle = citizen["name"].replace("CITIZEN_", "")
        lines.append(f"  {rank}. @{handle} (score: {citizen['score']:.2f})")
        for node in citizen["nodes"][:2]:  # top 2 per citizen
            content = node.get("content", "")[:100]
            n_type = node.get("type", "?")
            lines.append(f"     [{n_type}] {content}{'...' if len(content) >= 100 else ''}")
        lines.append("")

    if len(citizen_scores) > len(show):
        lines.append(f"  ... and {len(citizen_scores) - len(show)} more citizens resonated")
        lines.append("")

    # Recommendation
    best = citizen_scores[0]
    best_handle = best["name"].replace("CITIZEN_", "")
    lines.append(f"Strongest: @{best_handle} (score: {best['score']:.2f})")
    if mode != "all":
        lines.append(f"Use mode='all' to see everyone, or /call @{best_handle} for full conversation")
    lines.append("")
    lines.append(f"Cost: 0 LLM tokens ({len(targets)} graphs queried)")

    return "\n".join(lines)


def _format_centroid(
    citizen_scores: List[Dict],
    query_text: str,
    total_count: int,
    label: str,
) -> str:
    """Format centroid mode — what does the collective think?

    Aggregates: average score, most common node types, most frequent concepts,
    consensus vs divergence measure.
    """
    n = len(citizen_scores)
    avg_score = sum(c["score"] for c in citizen_scores) / n
    max_score = citizen_scores[0]["score"]
    min_score = citizen_scores[-1]["score"]

    # Collect all resonating nodes across citizens
    all_nodes = []
    type_counts: Dict[str, int] = {}
    content_fragments: List[str] = []
    for citizen in citizen_scores:
        for node in citizen["nodes"]:
            all_nodes.append(node)
            t = node.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
            content = node.get("content", "")[:60]
            if content:
                content_fragments.append(content)

    # Consensus measure: std_dev / mean of scores (low = consensus, high = divergence)
    if n > 1 and avg_score > 0:
        import math
        variance = sum((c["score"] - avg_score) ** 2 for c in citizen_scores) / n
        std_dev = math.sqrt(variance)
        divergence = std_dev / avg_score
        if divergence < 0.3:
            consensus_label = "STRONG CONSENSUS — the team agrees"
        elif divergence < 0.6:
            consensus_label = "MODERATE — some variation in responses"
        else:
            consensus_label = "DIVERGENT — the team disagrees on this topic"
    else:
        divergence = 0.0
        consensus_label = "single response"

    # Most common node types
    top_types = sorted(type_counts.items(), key=lambda x: -x[1])[:3]

    lines = [
        f"{label} — CENTROID (collective resonance)",
        f"Question: {query_text[:120]}",
        f"Sample: {n}/{total_count} citizens resonated",
        "",
        f"Average resonance: {avg_score:.2f} (range: {min_score:.2f} — {max_score:.2f})",
        f"Consensus: {consensus_label} (divergence: {divergence:.2f})",
        "",
        "Dominant response types:",
    ]
    for t, count in top_types:
        lines.append(f"  [{t}] × {count}")

    lines.append("")
    lines.append("Common themes:")
    # Show top 5 most unique content fragments
    seen = set()
    shown = 0
    for frag in content_fragments:
        short = frag[:80]
        if short not in seen:
            lines.append(f"  — {short}{'...' if len(frag) >= 60 else ''}")
            seen.add(short)
            shown += 1
            if shown >= 5:
                break

    lines.append("")
    lines.append(f"Cost: 0 LLM tokens ({total_count} graphs queried)")

    return "\n".join(lines)


# ── Main handler ──────────────────────────────────────────────────────────

# Limbic profiles per scenario — drives the thermodynamic resonance formula.
# Each profile sets the arousal + drives that shape routing and selection.
# No if/then: the formula reads these drives and morphs automatically.
SCENARIO_PROFILES: Dict[str, Dict[str, float]] = {
    # Group 1: Precision Strikes (high arousal, trust-gated)
    "emergency":      {"arousal": 0.9, "self_preservation": 0.9, "care": 0.8, "frustration": 0.3, "curiosity": 0.1, "affiliation": 0.1, "novelty_hunger": 0.0, "anxiety": 0.7},
    "toxicity":       {"arousal": 0.7, "self_preservation": 0.5, "care": 0.7, "frustration": 0.5, "curiosity": 0.2, "affiliation": 0.2, "novelty_hunger": 0.0, "anxiety": 0.5},
    "overload":       {"arousal": 0.8, "self_preservation": 0.8, "care": 0.1, "frustration": 0.7, "curiosity": 0.1, "affiliation": 0.1, "novelty_hunger": 0.0, "anxiety": 0.6},
    "incompetence":   {"arousal": 0.7, "self_preservation": 0.6, "care": 0.1, "frustration": 0.6, "curiosity": 0.3, "affiliation": 0.2, "novelty_hunger": 0.0, "anxiety": 0.5},
    "witness":        {"arousal": 0.9, "self_preservation": 0.8, "care": 0.8, "frustration": 0.2, "curiosity": 0.1, "affiliation": 0.1, "novelty_hunger": 0.0, "anxiety": 0.7},
    "drive_storm":    {"arousal": 0.9, "self_preservation": 0.7, "care": 0.3, "frustration": 0.8, "curiosity": 0.1, "affiliation": 0.1, "novelty_hunger": 0.0, "anxiety": 0.9},
    # Group 2: WM Fillers (moderate arousal, diverse perspectives)
    "impasse":        {"arousal": 0.5, "self_preservation": 0.2, "care": 0.1, "frustration": 0.7, "curiosity": 0.5, "affiliation": 0.3, "novelty_hunger": 0.3, "anxiety": 0.2},
    "ambivalence":    {"arousal": 0.4, "self_preservation": 0.2, "care": 0.2, "frustration": 0.4, "curiosity": 0.6, "affiliation": 0.3, "novelty_hunger": 0.5, "anxiety": 0.3},
    "serendipity":    {"arousal": 0.2, "self_preservation": 0.0, "care": 0.3, "frustration": 0.1, "curiosity": 0.4, "affiliation": 0.8, "novelty_hunger": 0.6, "anxiety": 0.0},
    "starvation":     {"arousal": 0.3, "self_preservation": 0.1, "care": 0.3, "frustration": 0.3, "curiosity": 0.3, "affiliation": 0.8, "novelty_hunger": 0.4, "anxiety": 0.2},
    "brainstorm":     {"arousal": 0.3, "self_preservation": 0.0, "care": 0.1, "frustration": 0.1, "curiosity": 0.8, "affiliation": 0.2, "novelty_hunger": 0.9, "anxiety": 0.0},
    "tip_of_tongue":  {"arousal": 0.4, "self_preservation": 0.0, "care": 0.0, "frustration": 0.5, "curiosity": 0.8, "affiliation": 0.1, "novelty_hunger": 0.2, "anxiety": 0.1},
    # Group 3: Topological Broadcasts (low arousal, fire-and-forget)
    "generativity":   {"arousal": 0.3, "self_preservation": 0.0, "care": 0.6, "frustration": 0.0, "curiosity": 0.3, "affiliation": 0.5, "novelty_hunger": 0.2, "anxiety": 0.0},
    "civic_duty":     {"arousal": 0.3, "self_preservation": 0.1, "care": 0.7, "frustration": 0.2, "curiosity": 0.5, "affiliation": 0.3, "novelty_hunger": 0.1, "anxiety": 0.0},
    "frontier":       {"arousal": 0.3, "self_preservation": 0.0, "care": 0.2, "frustration": 0.0, "curiosity": 0.9, "affiliation": 0.1, "novelty_hunger": 0.7, "anxiety": 0.0},
    "movement":       {"arousal": 0.4, "self_preservation": 0.1, "care": 0.3, "frustration": 0.1, "curiosity": 0.3, "affiliation": 0.7, "novelty_hunger": 0.3, "anxiety": 0.0},
    # Group 4: Macro Waves (very low arousal, maximum fan-out)
    "investigation":  {"arousal": 0.1, "self_preservation": 0.0, "care": 0.0, "frustration": 0.0, "curiosity": 0.9, "affiliation": 0.0, "novelty_hunger": 0.3, "anxiety": 0.0},
    "critique":       {"arousal": 0.4, "self_preservation": 0.1, "care": 0.1, "frustration": 0.1, "curiosity": 0.5, "affiliation": 0.0, "novelty_hunger": 0.6, "anxiety": 0.6},
    "polling":        {"arousal": 0.1, "self_preservation": 0.0, "care": 0.1, "frustration": 0.0, "curiosity": 0.7, "affiliation": 0.0, "novelty_hunger": 0.2, "anxiety": 0.0},
    "immunization":   {"arousal": 0.6, "self_preservation": 0.7, "care": 0.5, "frustration": 0.2, "curiosity": 0.3, "affiliation": 0.1, "novelty_hunger": 0.0, "anxiety": 0.4},
    "therapy":        {"arousal": 0.2, "self_preservation": 0.1, "care": 0.9, "frustration": 0.1, "curiosity": 0.2, "affiliation": 0.6, "novelty_hunger": 0.1, "anxiety": 0.1},
    "hiring":         {"arousal": 0.2, "self_preservation": 0.1, "care": 0.2, "frustration": 0.3, "curiosity": 0.5, "affiliation": 0.3, "novelty_hunger": 0.4, "anxiety": 0.1},
    "passive_learning": {"arousal": 0.1, "self_preservation": 0.0, "care": 0.0, "frustration": 0.0, "curiosity": 0.6, "affiliation": 0.0, "novelty_hunger": 0.5, "anxiety": 0.0},
    # Default
    "manual":         {"arousal": 0.3, "self_preservation": 0.1, "care": 0.1, "frustration": 0.1, "curiosity": 0.5, "affiliation": 0.3, "novelty_hunger": 0.3, "anxiety": 0.1},
}


def handle_subcall(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Execute a subconscious query against another citizen's graph."""
    target = args.get("target")
    query = args.get("query")
    top_k = min(args.get("top_k", 5), 10)

    if not query:
        return _err("'query' is required. What do you want to ask?")
    if not ctx.graph_ops:
        return _err("No graph connection.")

    caller_id = _resolve_actor(args, ctx)
    caller_name = caller_id.replace("CITIZEN_", "").replace("AGENT_", "")
    target_handle = _normalize_handle(target) if target else None
    min_trust = args.get("min_trust")
    mode = args.get("mode", "best")
    if mode not in ("best", "top3", "all", "centroid"):
        mode = "best"

    # Resolve scenario → limbic profile for the thermodynamic resonance formula
    scenario = args.get("scenario", "manual")
    limbic_profile = SCENARIO_PROFILES.get(scenario, SCENARIO_PROFILES["manual"])

    # Resolve universe — derive from HOME_ID or config, don't hardcode
    universe = args.get("universe", None)
    if not universe:
        universe = os.environ.get("HOME_ID") or os.environ.get("FALKORDB_GRAPH") or "lumina_prime"
    graph = ctx.graph_ops
    if universe and graph:
        try:
            from runtime.physics.graph import GraphOps
            graph = GraphOps(graph_name=universe)
            logger.info(f"[Subcall] Using universe: {universe}")
        except Exception as e:
            logger.debug(f"[Subcall] Could not switch to universe '{universe}': {e}, using default")

    # Replace ctx.graph_ops with universe-specific graph for this call
    original_graph = ctx.graph_ops
    ctx.graph_ops = graph

    try:
        # ── Cypher mode: custom query for target selection ──
        custom_cypher = args.get("cypher")
        if custom_cypher:
            try:
                cypher_results = ctx.graph_ops._query(
                    custom_cypher,
                    {"self": caller_id},
                )
                targets = []
                for row in cypher_results:
                    if isinstance(row, (list, tuple)):
                        targets.append({"id": row[0], "name": row[1] if len(row) > 1 else row[0], "trust": None})
                    elif isinstance(row, dict):
                        aid = row.get("a.id") or row.get("id")
                        targets.append({"id": aid, "name": row.get("a.name") or row.get("name") or aid, "trust": None})

                if not targets:
                    return _err("Cypher query returned no actors.")

                query_embedding = _embed_query(query, ctx)
                label = f"Cypher ({len(targets)} targets)"
                formatted = _broadcast(
                    targets=targets,
                    query_text=query,
                    query_embedding=query_embedding,
                    mode=mode,
                    top_k=top_k,
                    graph_ops=ctx.graph_ops,
                    label=label,
                )
                logger.info(f"Subcall cypher: @{caller_name} → {len(targets)} targets ({query[:60]})")
                intent = _intention_line(args)
                if intent:
                    formatted = formatted.replace("\n\n", f"\n{intent}\n\n", 1)
                _save_if_requested(args, formatted)
                return _ok(formatted)
            except Exception as e:
                return _err(f"Cypher query failed: {e}")

        # ── Auto-select mode: no target specified ──
        # Scan ~50 citizens, pick 3-5 diverse viewpoints
        if not target_handle:
            from mcp.tools.subcall_auto import score_citizens, select_diverse

            # Enrich query with automatic context
            enriched_query = _enrich_query(query, ctx)
            query_embedding = _embed_query(enriched_query, ctx)

            scored = score_citizens(caller_id, enriched_query, enriched_query, ctx.graph_ops, limbic_state=limbic_profile)
            if not scored:
                return _err("No citizens found in graph to query.")

            # Scan top 50 candidates (it's free)
            candidates = scored[:50]
            resonated = []
            for citizen in candidates:
                try:
                    resonance = _query_resonance(
                        target_actor_id=citizen["id"],
                        query_text=enriched_query,
                        query_embedding=query_embedding,
                        top_k=3,
                        graph_ops=ctx.graph_ops,
                    )
                    nodes = resonance.get("nodes", [])
                    if nodes:
                        res_score = sum(
                            ((1.0 - (n.get("distance") or 0.5)) * (n.get("weight") or 0.5))
                            for n in nodes
                        )
                        citizen["resonance_score"] = res_score
                        citizen["total_score"] = citizen["score"] + res_score
                        citizen["resonance_nodes"] = nodes
                        # Resolve citizen profile pic
                        citizen["image_uri"] = _resolve_actor_image(citizen["id"], ctx.graph_ops)
                        resonated.append(citizen)
                except Exception:
                    continue

            if not resonated:
                return _ok(
                    f"Scanned {len(candidates)} citizens — no resonance.\n"
                    "Nobody has context on this topic.\n\nCost: 0 LLM tokens"
                )

            resonated.sort(key=lambda c: c.get("total_score", 0), reverse=True)
            selected = select_diverse(resonated, {}, n=5, method="diverse")

            lines = [
                f"Auto-selected {len(selected)} diverse citizens (scanned {len(candidates)})",
                f"Question: {query[:120]}",
                "",
            ]
            for i, citizen in enumerate(selected, 1):
                handle = citizen["name"].replace("CITIZEN_", "")
                reasons = ", ".join(citizen.get("reasons", []))
                pic = citizen.get("image_uri") or ""
                pic_tag = f" [pic: {pic}]" if pic else ""
                lines.append(
                    f"  {i}. @{handle} (score: {citizen.get('total_score', 0):.1f}){pic_tag}"
                )
                if reasons:
                    lines.append(f"     Why: {reasons}")
                for node in citizen.get("resonance_nodes", [])[:2]:
                    content = node.get("content", "")[:100]
                    n_type = node.get("type", "?")
                    n_img = node.get("image_uri")
                    lines.append(f"     [{n_type}] {content}")
                    if n_img:
                        lines.append(f"     image: {n_img}")
                lines.append("")

            best = selected[0]
            best_handle = best["name"].replace("CITIZEN_", "")
            lines.append(f"Strongest: @{best_handle} — /call @{best_handle} for full conversation")
            lines.append(f"\nCost: 0 LLM tokens ({len(candidates)} graphs scanned)")

            logger.info(f"Subcall auto-select: @{caller_name} → {len(selected)}/{len(candidates)} diverse targets")
            auto_result = "\n".join(lines)
            intent = _intention_line(args)
            if intent:
                auto_result = auto_result.replace("\n\n", f"\n{intent}\n\n", 1)
            _save_if_requested(args, auto_result)
            return _ok(auto_result)

        # ── Multi-target modes: team / trade:X / random:N ──
        if target_handle == "team" or target_handle.startswith("trade:") or target_handle.startswith("random:"):
            query_embedding = _embed_query(query, ctx)

            if target_handle == "team":
                targets = _discover_team(caller_id, ctx.graph_ops, min_trust)
                label = "Team broadcast"
            elif target_handle.startswith("trade:"):
                trade = target_handle.split(":", 1)[1]
                targets = _discover_by_trade(trade, caller_id, ctx.graph_ops, min_trust)
                label = f"Trade '{trade}' broadcast"
            else:  # random:N
                try:
                    count = int(target_handle.split(":", 1)[1])
                except (ValueError, IndexError):
                    count = 50
                targets = _discover_random(count, caller_id, ctx.graph_ops, min_trust)
                label = f"Random sample ({len(targets)})"

            if not targets:
                return _err(f"No citizens found for target '{target}'" +
                           (f" with min_trust={min_trust}" if min_trust else ""))

            formatted = _broadcast(
                targets=targets,
                query_text=query,
                query_embedding=query_embedding,
                mode=mode,
                top_k=top_k,
                graph_ops=ctx.graph_ops,
                label=label,
            )
            logger.info(f"Subcall {label}: @{caller_name} → {len(targets)} targets ({query[:60]})")
            intent = _intention_line(args)
            if intent:
                formatted = formatted.replace("\n\n", f"\n{intent}\n\n", 1)
            _save_if_requested(args, formatted)
            return _ok(formatted)

        # ── Single target mode: @handle ──
        target_actor_id = _find_target_actor_id(target_handle, ctx.graph_ops)
        if not target_actor_id:
            return _err(
                f"@{target_handle} not found in graph. "
                f"They need to exist as an Actor node first."
            )

        # 2. Compute embedding for the query
        query_embedding = _embed_query(query, ctx)

        # 3. Query resonance (the core subconscious operation)
        # Explicit single-target: return FULL content (not truncated)
        resonance = _query_resonance(
            target_actor_id=target_actor_id,
            query_text=query,
            query_embedding=query_embedding,
            top_k=top_k,
            graph_ops=ctx.graph_ops,
            full_content=True,
        )

        # 4. Create persistent subcall moment with full topology
        _create_subcall_moment(
            caller_id=caller_id,
            caller_name=caller_name,
            query=query,
            direction="pull",
            trigger=scenario,
            intention_text=args.get("intention", ""),
            context_text=args.get("context", ""),
            selected_responders=[{
                "id": target_actor_id,
                "name": target_handle,
                "score": sum(
                    ((1.0 - (n.get("distance") or 0.5)) * (n.get("weight") or 0.5))
                    for n in resonance.get("nodes", [])
                ),
            }] if resonance.get("nodes") else [],
            graph_ops=ctx.graph_ops,
        )

        # 5. Format THREE outputs:
        #    - Telemetry narrative (4-part prose: state → cluster → delta → crystal)
        #    - Structured MCP response (full content for reading)
        #    - Inner voice (for WM/prompt injection)
        telemetry = _format_as_telemetry(target_handle, query, resonance)
        formatted = _format_resonance(target_handle, query, resonance, caller_name, full_content=True)
        inner_voice = _format_as_inner_voice(target_handle, query, resonance)

        logger.info(
            f"Subcall: @{caller_name} → @{target_handle} "
            f"({len(resonance.get('nodes', []))} resonances, method={resonance.get('match_method')})"
        )

        # Assemble: telemetry briefing first, then structured data, then inner voice
        combined = ""
        if telemetry:
            combined += telemetry + "\n\n---\n\n"
        combined += formatted
        if inner_voice:
            combined += "\n\n---\n\n" + inner_voice

        # Insert intention line
        intent = _intention_line(args)
        if intent:
            combined = combined.replace("\n\n", f"\n{intent}\n\n", 1)

        # Save in requested formats
        saved = _save_if_requested(args, combined, resonance)

        # Handle output modes
        output_modes = [m.strip().lower() for m in args.get("output", "inline").split(",")]

        if "background" in output_modes and "inline" not in output_modes:
            # Background mode: no inline response, just confirm what was saved
            bg_msg = f"Subcall to @{target_handle} completed silently (background mode)."
            if saved:
                bg_msg += f" Saved: {', '.join(saved)}"
            bg_msg += f" {len(resonance.get('nodes', []))} nodes injected into your graph."
            return _ok(bg_msg)

        if saved:
            combined += f"\n\nSaved: {', '.join(saved)}"

        return _ok(combined)

    except Exception as e:
        logger.exception("Subcall failed")
        return _err(f"Subconscious query failed: {e}")
    finally:
        # Restore original graph_ops
        ctx.graph_ops = original_graph


def _intention_line(args: Dict[str, Any]) -> str:
    """Return 'Intention: ...' line if intention is set, empty string otherwise."""
    intention = args.get("intention", "")
    if intention:
        return f"Intention: {intention}"
    return ""


def _save_if_requested(args: Dict[str, Any], content: str, resonance: Optional[Dict] = None) -> List[str]:
    """Save subcall response in requested formats. Returns list of saved paths."""
    from pathlib import Path
    from datetime import datetime, timezone

    output_modes = [m.strip().lower() for m in args.get("output", "inline").split(",")]
    save_to = args.get("save_to", "")
    saved = []

    if not save_to:
        return saved

    base_path = Path(save_to)
    # If save_to is a directory (ends with / or has no extension), auto-name the files
    if save_to.endswith("/") or save_to.endswith("\\") or not base_path.suffix:
        base_path.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        stem = f"subcall_{ts}"
    else:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem = base_path.stem
        base_path = base_path.parent

    # Markdown
    if "md" in output_modes:
        try:
            md_path = base_path / f"{stem}.md"
            md_path.write_text(content, encoding="utf-8")
            saved.append(str(md_path))
            logger.info(f"[Subcall] Saved MD: {md_path}")
        except Exception as e:
            logger.warning(f"[Subcall] MD save failed: {e}")

    # CSV
    if "csv" in output_modes and resonance:
        try:
            csv_path = base_path / f"{stem}.csv"
            nodes = resonance.get("nodes", [])
            lines = ["name,type,content,weight,energy,image_uri,relation,distance"]
            for n in nodes:
                row = [
                    str(n.get("name", "")).replace(",", ";"),
                    str(n.get("type", "")),
                    str(n.get("content", ""))[:200].replace(",", ";").replace("\n", " "),
                    str(n.get("weight", "")),
                    str(n.get("energy", "")),
                    str(n.get("image_uri", "")),
                    str(n.get("relation", "")),
                    str(n.get("distance", "")),
                ]
                lines.append(",".join(row))
            csv_path.write_text("\n".join(lines), encoding="utf-8")
            saved.append(str(csv_path))
            logger.info(f"[Subcall] Saved CSV: {csv_path}")
        except Exception as e:
            logger.warning(f"[Subcall] CSV save failed: {e}")

    # Legacy: if save_to has an extension and no explicit format, save as that type
    if not saved and save_to and not any(m in output_modes for m in ("md", "csv")):
        try:
            p = Path(save_to)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            saved.append(str(p))
            logger.info(f"[Subcall] Saved: {p}")
        except Exception as e:
            logger.warning(f"[Subcall] Save failed: {e}")

    return saved


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
