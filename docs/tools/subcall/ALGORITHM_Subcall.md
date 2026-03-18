# Subcall — Algorithm: Thermodynamic Resonance Pipeline

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against 3edd76b
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
BEHAVIORS:       ./BEHAVIORS_Subcall.md
PATTERNS:        ./PATTERNS_Subcall.md
THIS:            ALGORITHM_Subcall.md (you are here)
VALIDATION:      ./VALIDATION_Subcall.md
HEALTH:          ./HEALTH_Subcall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Subcall.md
SYNC:            ./SYNC_Subcall.md

IMPL:            mcp/tools/subcall_handler.py
                 mcp/tools/subcall_auto.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Subcall is a pipeline with 6 stages: **Resolve -> Target -> Probe -> Score -> Format -> Persist**. The caller's query enters as text, gets enriched with context and embedded into a vector, targets are discovered via one of 6 targeting modes, each target's graph is probed for resonance via KNN vector search (or keyword fallback), results are scored and selected, formatted into an intelligence briefing, and a persistent Moment node is written to the graph.

The central mechanism is the **Thermodynamic Resonance Formula** in the targeting stage, and the **KNN vector similarity search** in the probing stage. The formula determines WHO to ask; the KNN search determines WHAT resonated.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Zero-LLM telepathy | B1, B2, B3 | The entire pipeline operates on graph physics — embedding + Cypher queries only |
| O2: Thermodynamic routing | B2, B4 | The formula's limbic-driven morphing is the core targeting algorithm |
| O4: Intelligence briefing | B1 | The formatting stage converts raw resonance into actionable analysis |
| O5: Continuous economics | B1 | Moment creation with CREATED/CONTRIBUTED links anchors the vertical membrane |

---

## DATA STRUCTURES

### Stimulus Cluster

```
List of segment dicts injected into target's graph:
  [0] Self actor node     — content: "@caller_name", embedding: query_embedding
  [1] Query concept       — content: query_text[:500], _is_main: True
  [2..N] Activated nodes  — from caller's brain (energy > threshold OR in_working_memory)
  [N+1] Current moment    — if available, energy fixed at 0.8

All segments carry:
  origin_citizen: str     — caller's name
  origin_date: int        — UTC timestamp
  origin_image_uri: str   — caller's profile pic
```

### Resonance Result

```
{
  "nodes": [             — resonating nodes from target's graph
    {
      "id": str,         — node ID
      "name": str,       — node name
      "type": str,       — L1 cognitive type (memory, person, concept, value, process, desire, narrative, space)
      "content": str,    — node content (full or truncated by mode)
      "weight": float,   — consolidation level (Law 5-7)
      "energy": float,   — current activation level
      "distance": float, — 1 - similarity score (lower = more relevant)
      "image_uri": str,  — associated image
      "relation": str,   — relationship type to target actor
      "valence": float,  — emotional valence
      "arousal": float,  — emotional arousal
      "author": str,     — who created this node
    }
  ],
  "actor_state": {       — target citizen's current state
    "energy", "weight", "stability", "arousal", "valence", "dominant_drive",
    "name", "trade", "role", "class", "type", "image_uri",
    "last_activity_s", "current_spaces": [], "organizations": []
  },
  "match_method": str    — "vector_similarity" | "keyword_fallback" | "none"
}
```

### Scenario Profile (Limbic Profile)

```
Dict[str, float] with 8 drives:
  arousal           — 0.0-1.0, controls formula blending (sniper vs dragnet)
  self_preservation — 0.0-1.0, weights trust in routing
  affiliation       — 0.0-1.0, weights spatial co-presence
  curiosity         — 0.0-1.0, weights narrative traversal + semantic overlap
  care              — 0.0-1.0, drives generativity/therapy scenarios
  frustration       — 0.0-1.0, signals impasse/overload conditions
  novelty_hunger    — 0.0-1.0, drives brainstorm/critique diversity
  anxiety           — 0.0-1.0, signals emergency/drive_storm urgency
```

---

## ALGORITHM: handle_subcall()

### Step 1: Resolve (Caller + Target + Scenario)

Resolve the caller's actor ID via `runtime/identity.resolve_actor_id()`. Normalize the target handle (strip @, lowercase). Look up the scenario's limbic profile from SCENARIO_PROFILES dict. Resolve the universe (from args, HOME_ID env, or FALKORDB_GRAPH env). If universe differs from default, construct a new GraphOps instance for this call.

### Step 2: Target Discovery (6 modes)

The handler dispatches to one of 6 targeting paths based on the target parameter:

**2a. Cypher mode** (`cypher` parameter set):
Execute custom Cypher query with `$self` bound to caller ID. Returned actors become broadcast targets.

**2b. Auto-select mode** (no target specified):
1. Enrich query with git repo URL and active tasks via `_enrich_query()`
2. Compute query embedding
3. Score all citizens via `score_citizens()` using the Thermodynamic Resonance Formula
4. Probe top 50 candidates for graph resonance
5. Select 3-5 diverse viewpoints via `select_diverse()`

**2c. Team mode** (`target="team"`):
`_discover_team()` — all Actor nodes linked to caller, sorted by trust then weight, limit 50.

**2d. Trade mode** (`target="trade:X"`):
`_discover_by_trade()` — all Actor nodes where type/name/trade/role/class/content/synthesis CONTAINS the trade string, sorted by weight, limit 50.

**2e. Random mode** (`target="random:N"`):
`_discover_random()` — random sample of N actors from entire graph, cap 500.

**2f. Single handle mode** (`target="@handle"`):
`_find_target_actor_id()` — try multiple ID formats (citizen:X, CITIZEN_X, X, actor:X), then fuzzy match on name.

### Step 3: Probe (Graph Resonance Query)

`_query_resonance()` probes the target's subgraph:

**Strategy 1 — Vector similarity (preferred):**
For each of 5 node labels (Actor, Moment, Narrative, Space, Thing), run FalkorDB KNN vector search:
```
CALL db.idx.vector.queryNodes("Label", "embedding", K, vecf32(query_vector))
YIELD node, score
MATCH (target:Actor {id: $target})-[r]-(node)
```
Merge results across labels, sort by score descending, take top_k.

**Strategy 2 — Keyword fallback:**
If vector search yields nothing (no embeddings, index missing), extract top 5 keywords (>3 chars) from query and search:
```
MATCH (target:Actor {id: $target})-[r]-(n)
WHERE toLower(n.content) CONTAINS 'keyword' OR toLower(n.synthesis) CONTAINS 'keyword'
```

**Actor profile read:**
Regardless of match strategy, query the target actor's properties: energy, weight, stability, arousal, valence, dominant_drive, trade, role, current spaces, organizations.

### Step 4: Score and Select

**Single target:** No scoring needed — use the resonance directly.

**Multi-target / broadcast:**
Score = sum of `(1 - distance) * weight` for each resonating node. Sort citizens by score. Apply mode filter (best/top3/all/centroid).

**Auto-select:**
Combined score = targeting_score (from Thermodynamic Formula) + resonance_score (from probe). Then `select_diverse()` picks 3-5 citizens maximizing viewpoint spread via greedy farthest-point algorithm.

### Step 5: Format Output

**Single target** produces 3 layers:
1. `_format_as_telemetry()` — Intelligence Briefing: header line, arousal regime, because explanation, next step recommendation, medoid-edge graph extraction, telemetry stats
2. `_format_resonance()` — Structured data: method, numbered node list with content/weight/energy/distance, responder profile with spaces/orgs/emotional state
3. `_format_as_inner_voice()` — WM-injectable whisper: first-person narration with type-specific whisper variants, energy labels (hot/warm/cool/cold), emotional context

**Multi-target** produces:
- `_broadcast()` — Ranked list with per-citizen top-2 nodes and summary statistics
- `_format_centroid()` — For centroid mode: average score, consensus/divergence measure, common themes

### Step 6: Persist

`_create_subcall_moment()` creates a Moment node in the graph:
- Type: "subcall", status: "completed"
- Properties: direction (pull), creating_drive (mapped from trigger/scenario), trigger, intention, resonance_count
- Links: caller -[CREATED]-> moment, each responder -[CONTRIBUTED]-> moment
- Settlement status: "tracking" (for continuous $MIND flow via vertical membrane)

---

## KEY DECISIONS

### D1: Vector Search vs Keyword Fallback

```
IF embedding is available AND FalkorDB vector index exists:
    Use KNN vector search across 5 node labels
    match_method = "vector_similarity"
    WHY: Higher quality semantic matching, continuous similarity scores
ELSE:
    Extract top 5 keywords from query, text CONTAINS search
    match_method = "keyword_fallback"
    WHY: Works without embeddings, but lower quality (binary match)
```

### D2: Full Content vs Truncated Content

```
IF single @handle target (explicit MCP call):
    full_content = True, no truncation
    WHY: Caller explicitly asked about this citizen, wants complete data
ELSE (broadcast, auto-select):
    content truncated to 500 chars per node, 3 nodes per citizen
    WHY: 200 citizens * 5 nodes * full content would be unusably large
```

### D3: Diverse vs Centroid Selection

```
IF mode == "centroid":
    Pick citizens closest to the mean score (consensus viewpoints)
    WHY: Caller wants the collective average, not outliers
ELSE (diverse, default):
    Greedy farthest-point: at each step, add citizen most different from all selected
    WHY: Maximizes viewpoint spread, prevents echo chamber
```

### D4: Arousal Regime Classification

```
IF arousal > 0.8:  regime = "Panic"     — sniper: trust + explicit names only
IF arousal > 0.6:  regime = "High Focus" — trust weighted, some semantic
IF arousal > 0.4:  regime = "Flow"       — balanced: space + affinity + narrative
IF arousal > 0.2:  regime = "Calm"       — mostly semantic, some trust
ELSE:              regime = "Idle"       — pure dragnet, maximum fan-out
```

---

## DATA FLOW

```
query (text)
    |
    v
_enrich_query() -- add git repo URL + active tasks
    |
    v
_embed_query() -- compute embedding vector (~50ms)
    |
    v
[Target Discovery: 1 of 6 modes]
    |
    v
_build_stimulus_cluster() -- harvest caller's activated nodes
    |
    v
_query_resonance() per target -- KNN vector search or keyword fallback
    |
    v
[Score + Select: mode-dependent aggregation]
    |
    v
_format_as_telemetry() + _format_resonance() + _format_as_inner_voice()
    |
    v
_create_subcall_moment() -- persist to graph
    |
    v
_save_if_requested() -- write .md/.csv if requested
    |
    v
MCP response ({"content": [{"type": "text", "text": briefing}]})
```

---

## COMPLEXITY

**Time:** O(T * K * L) where T = number of targets, K = top_k nodes per target, L = 5 label types for KNN search. Single target: O(K * L) ~ O(50). Broadcast to 200: O(200 * 3 * 5) ~ O(3000 graph queries).

**Space:** O(T * K) for storing resonance results. Single target: O(10). Broadcast to 200: O(600).

**Bottlenecks:**
- Embedding computation (~50ms) — amortized once per call
- KNN vector search — depends on graph size and index quality; typically <10ms per label
- Sequential target probing in broadcast — not parallelized; 200 targets take ~2s
- Full actor profile read per target in single mode — additional graph query

---

## HELPER FUNCTIONS

### `_enrich_query(query, ctx)`

**Purpose:** Add semantic gravity to bare queries. Appends `[repo: name/path]`, `[git: remote_url]`, and `[tasks: task1; task2]` from the working directory and .claude task files.

**Logic:** Walk parent directories to find .git root, compute relative path, read git remote URL. Scan ~/.claude for task files, extract checkbox items.

### `_build_stimulus_cluster(query_text, query_embedding, caller_id, graph_ops)`

**Purpose:** Construct the multi-segment cluster injected into target's graph.

**Logic:** Query caller's graph for nodes with energy > 0.15 or in_working_memory=true. Harvest up to 20 activated nodes. Prepend self actor node and query concept. Stamp all with origin_citizen/origin_date provenance.

### `_resolve_l1_type(node_labels, subtype)`

**Purpose:** Map FalkorDB node labels (Actor, Moment, Narrative, Space, Thing) to L1 cognitive types (person, memory, value, process, desire, narrative, space, concept).

**Logic:** Check label set, then subtype field. Narrative with subtype "value"/"process"/"desire" maps to that subtype. Everything else maps by label directly.

### `_format_as_telemetry(target_handle, query, resonance)`

**Purpose:** Generate the intelligence briefing header from raw resonance data.

**Logic:** Classify dominant delta (positive resonance / defensive spike / deep knowledge / faint echo) from valence + energy + weight. Classify arousal regime (Panic/High Focus/Flow/Calm/Idle). Generate "Because of..." explanation and "Next step:" recommendation. Build medoid-edge graph extraction chain.

### `_format_as_inner_voice(target_handle, query, resonance)`

**Purpose:** Generate first-person whisper text for WM/prompt injection.

**Logic:** Use type-specific whisper variants (e.g., "a memory of theirs", "a notion in their mind") selected deterministically via MD5 hash of content. Add energy labels (hot/warm/cool/cold) and emotional context (content/uneasy/steady + alert/calm + driven by X).

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/physics/graph/GraphOps` | `_query()`, `add_moment()` | Cypher results, node creation |
| `runtime/infrastructure/embeddings/service` | `embed()` | Float vector for query text |
| `runtime/identity` | `resolve_actor_id()` | Caller's actor ID string |
| `mcp/tools/subcall_auto` | `score_citizens()`, `select_diverse()` | Scored citizen list, diverse selection |
| `mcp/tools/context` | `ServerContext` | graph_ops, graph_queries, runner, target_dir |

---

## THE THERMODYNAMIC RESONANCE FORMULA (Full Specification)

This is the central routing algorithm, implemented in `subcall_auto.py:score_citizens()`.

```
TARGET_ENERGY = Flow_topology * max(Compatibility, 0.1) * max(Target_weight, 0.1)
              + Baseline

Where:

  Flow_topology = Flow_spatial + Flow_relational

    Flow_spatial = (1 - friction) * D_affiliation
      -- only if citizens share a Space node

    Flow_relational = (trust * D_self_preservation + affinity * D_affiliation) * (1 - friction)
      -- from link properties between caller and candidate

  Compatibility = (1 - arousal) * Sim_vec + arousal * Sim_lex

    Sim_vec = 1.0 if candidate's trade/role/type appears in query text, else 0.0
      -- semantic domain match

    Sim_lex = 1.0 if candidate's handle is @-mentioned in text, else 0.0
      -- explicit name mention

  Target_weight = candidate actor's consolidated weight

  Baseline = target_weight * sim_vec * D_curiosity
    -- only if both target_weight > 0 and sim_vec > 0
    -- ensures heavy domain experts are discoverable even without personal links

Post-formula:
  + Narrative proximity bonus = sum(r1.energy * r2.energy) * (1 - arousal)
    -- citizens linked to the same active narratives
    -- weighted inversely with arousal (calm = traverse narratives, panic = skip)
```

**Behavior by arousal regime:**

| Arousal | Regime | Formula Effect |
|---------|--------|---------------|
| ~0.9 | Panic (Sniper) | Compatibility ~ Sim_lex (explicit names only), narrative bonus near zero |
| ~0.5 | Moderate (Roundtable) | Balanced: trust + domain + names + some narrative |
| ~0.3 | Flow (Frontier) | Compatibility ~ Sim_vec (domain match), narrative bonus active |
| ~0.1 | Calm (Dragnet) | Compatibility ~ Sim_vec (pure semantic), narrative bonus at maximum |
