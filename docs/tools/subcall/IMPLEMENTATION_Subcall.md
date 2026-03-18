# Subcall — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
BEHAVIORS:       ./BEHAVIORS_Subcall.md
PATTERNS:        ./PATTERNS_Subcall.md
ALGORITHM:       ./ALGORITHM_Subcall.md
VALIDATION:      ./VALIDATION_Subcall.md
THIS:            IMPLEMENTATION_Subcall.md (you are here)
HEALTH:          ./HEALTH_Subcall.md
SYNC:            ./SYNC_Subcall.md

IMPL:            mcp/tools/subcall_handler.py
                 mcp/tools/subcall_auto.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mcp/tools/
├── subcall_handler.py     # Main handler: schema, resonance engine, briefing formatters, 24 profiles
└── subcall_auto.py        # Auto-trigger: TriggerState, detect_trigger(), score_citizens(), select_diverse()
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `mcp/tools/subcall_handler.py` | Core subcall handler: tool schema, targeting, resonance, formatting, persistence | `handle_subcall()`, `_query_resonance()`, `_format_as_telemetry()`, `_format_as_inner_voice()`, `_broadcast()`, `SCENARIO_PROFILES`, `TOOL_SCHEMA` | ~2229 | SPLIT |
| `mcp/tools/subcall_auto.py` | Auto-trigger detection and smart citizen scoring | `detect_trigger()`, `score_citizens()`, `select_diverse()`, `auto_subcall()`, `TriggerState` | ~810 | WATCH |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with Strategy Dispatch

The main handler is a pipeline (resolve -> target -> probe -> score -> format -> persist) with strategy dispatch at the targeting stage (6 modes). The formatting stage uses strategy pattern for output modes (telemetry/structured/inner_voice for single, broadcast/centroid for multi).

**Why this pattern:** The 6 targeting modes have very different discovery mechanisms but share the same downstream pipeline (probe -> score -> format). Strategy dispatch at the targeting stage keeps each mode's logic isolated while the common pipeline avoids duplication.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy dispatch | `handle_subcall()` targeting section | 6 targeting modes without deep nesting |
| Dict-based configuration | `SCENARIO_PROFILES` | 24 scenarios as data, not code paths |
| Fallback chain | `_query_resonance()` | Vector -> keyword -> empty result |
| Builder | `_build_stimulus_cluster()` | Incremental construction of multi-segment injection |
| Template method | `_format_as_inner_voice()` | Whisper variants selected by content hash |

### Anti-Patterns to Avoid

- **Adding scenario-specific if/elif chains**: The 24 scenarios MUST remain as dict entries. Adding `if scenario == "emergency": ...` breaks the thermodynamic design. See V2.
- **Splitting the handler into per-scenario files**: The formula is one mathematical expression. Fragmenting it across files would destroy comprehensibility.
- **Caching resonance results**: Subcall modifies the target graph (energy injection). Cached results would be stale by definition.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Subcall module | Targeting, resonance, formatting, persistence | Graph operations, embedding computation | `handle_subcall(args, ctx)` via `ServerContext` |
| Auto-trigger module | Trigger detection, citizen scoring, diverse selection | Full subcall execution | `detect_trigger()`, `score_citizens()`, `select_diverse()` |

---

## SCHEMA

### TOOL_SCHEMA (MCP Tool Definition)

```yaml
SubcallInput:
  required:
    - query: str                    # The question or topic
  optional:
    - target: str                   # @handle, team, trade:X, random:N
    - scenario: str                 # One of 24 limbic profiles
    - mode: str                     # best, top3, all, centroid
    - intention: str                # Why asking (displayed in header)
    - context: str                  # Situational context
    - min_trust: float              # Trust filter (0.0-1.0)
    - top_k: int                    # Max nodes per citizen (1-10)
    - output: str                   # inline, background, md, csv
    - save_to: str                  # Folder for file output
    - cypher: str                   # Custom Cypher for targeting
    - universe: str                 # Which graph
    - actor_id: str                 # Caller ID override
  constraints:
    - top_k capped at 10
    - random:N capped at 500
    - mode must be one of: best, top3, all, centroid
    - scenario must be one of the 24 SCENARIO_PROFILES keys
```

### Moment Node (Created by subcall)

```yaml
SubcallMoment:
  required:
    - id: str                       # "moment_subcall_{uuid_hex[:10]}"
    - type: "subcall"
    - status: "completed"
    - speaker: str                  # caller_id
    - direction: str                # "pull" for subcall, "push" for broadcast
    - creating_drive: str           # mapped from trigger/scenario
    - trigger: str                  # scenario name or trigger type
    - settlement_status: "tracking"
    - origin_citizen: str           # caller name
  optional:
    - intention: str
    - resonance_count: int
  relationships:
    - CREATED: from caller Actor
    - CONTRIBUTED: from each responder Actor (weight = resonance score)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `handle_subcall()` | `subcall_handler.py:1844` | MCP tool dispatch (server.py routes "subcall" tool calls here) |
| `auto_subcall()` | `subcall_auto.py:670` | L1 tick runner or MCP middleware (after each message/tool output) |
| `detect_trigger()` | `subcall_auto.py:271` | Called by auto_subcall() to check if auto-trigger should fire |
| `score_citizens()` | `subcall_auto.py:406` | Called by auto_subcall() and by handle_subcall() in auto-select mode |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Single-Target Subcall (Flagship Path)

This is the richest flow — explicit @handle target, full briefing output, moment persistence. High impact because it produces the 3-layer intelligence briefing and creates economic settlement anchors.

```yaml
flow:
  name: single_target_subcall
  purpose: Probe one citizen's subconscious, produce intelligence briefing, anchor economics
  scope: query text -> intelligence briefing + graph mutations
  steps:
    - id: resolve
      description: Resolve caller ID, normalize target handle, lookup scenario profile
      file: mcp/tools/subcall_handler.py
      function: handle_subcall (lines 1844-1882)
      input: args dict, ServerContext
      output: caller_id, target_handle, limbic_profile, graph ops
      trigger: MCP tool dispatch
      side_effects: may construct new GraphOps for universe switch
    - id: find_target
      description: Resolve @handle to actor ID via multiple ID format attempts
      file: mcp/tools/subcall_handler.py
      function: _find_target_actor_id()
      input: handle string, graph_ops
      output: target_actor_id or None
      trigger: single-handle path in handle_subcall
      side_effects: none (read-only)
    - id: embed
      description: Compute query embedding vector
      file: mcp/tools/subcall_handler.py
      function: _embed_query()
      input: query string, ServerContext
      output: List[float] or None
      trigger: after target resolution
      side_effects: external embedding service call
    - id: probe
      description: KNN vector search + keyword fallback on target's subgraph
      file: mcp/tools/subcall_handler.py
      function: _query_resonance()
      input: target_actor_id, query_text, query_embedding, top_k, graph_ops
      output: resonance dict (nodes, actor_state, match_method)
      trigger: after embedding
      side_effects: multiple Cypher queries (read-only)
    - id: format
      description: Generate 3-layer intelligence briefing
      file: mcp/tools/subcall_handler.py
      function: _format_as_telemetry(), _format_resonance(), _format_as_inner_voice()
      input: resonance dict, target_handle, query
      output: combined text string (3 layers separated by ---)
      trigger: after probe
      side_effects: none (pure formatting)
    - id: persist
      description: Create subcall moment node with CREATED/CONTRIBUTED links
      file: mcp/tools/subcall_handler.py
      function: _create_subcall_moment()
      input: caller_id, query, responders, scenario
      output: moment_id or None
      trigger: after format
      side_effects: graph writes (add_moment, link creation)
  docking_points:
    available:
      - id: dock_embed_output
        type: api
        direction: output
        file: mcp/tools/subcall_handler.py
        function: _embed_query()
        trigger: embedding service response
        payload: List[float] (768-1536 dim)
        async_hook: not_applicable
        needs: none
        notes: embedding quality directly affects resonance quality
      - id: dock_resonance_output
        type: graph_ops
        direction: output
        file: mcp/tools/subcall_handler.py
        function: _query_resonance()
        trigger: after KNN search completes
        payload: resonance dict
        async_hook: not_applicable
        needs: none
        notes: core data structure that feeds all formatters
      - id: dock_moment_created
        type: graph_ops
        direction: output
        file: mcp/tools/subcall_handler.py
        function: _create_subcall_moment()
        trigger: after graph write
        payload: moment_id string
        async_hook: not_applicable
        needs: none
        notes: settlement anchor — critical for economics
    health_recommended:
      - dock_id: dock_resonance_output
        reason: resonance quality is the core value proposition
      - dock_id: dock_moment_created
        reason: moment persistence is the economic settlement anchor
```

### Flow 2: Auto-Select Subcall

Covers the no-target path where 50 citizens are scored and 3-5 diverse viewpoints selected.

```yaml
flow:
  name: auto_select_subcall
  purpose: Broad citizen scan with diverse selection when no target specified
  scope: query text -> diverse citizen selection + resonance summary
  steps:
    - id: enrich
      description: Add git repo URL and active tasks to query
      file: mcp/tools/subcall_handler.py
      function: _enrich_query()
      input: query string, ServerContext
      output: enriched query string
      trigger: auto-select path
      side_effects: subprocess call for git remote URL
    - id: score
      description: Score all citizens via Thermodynamic Resonance Formula
      file: mcp/tools/subcall_auto.py
      function: score_citizens()
      input: caller_id, query, context, graph_ops, limbic_state
      output: sorted list of scored citizens
      trigger: after enrichment
      side_effects: multiple Cypher queries (read-only)
    - id: probe_candidates
      description: Probe top 50 candidates for graph resonance
      file: mcp/tools/subcall_handler.py
      function: _query_resonance() x50
      input: each candidate's actor_id
      output: resonance data per candidate
      trigger: after scoring
      side_effects: 50 * 5 KNN searches (read-only)
    - id: select_diverse
      description: Pick 3-5 citizens maximizing viewpoint spread
      file: mcp/tools/subcall_auto.py
      function: select_diverse()
      input: resonated citizens, method="diverse"
      output: 3-5 selected citizens
      trigger: after probing
      side_effects: none (pure selection)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
subcall_handler.py
    ├── imports → mcp/tools/context.py (ServerContext)
    ├── imports → mcp/tools/subcall_auto.py (score_citizens, select_diverse)
    ├── imports → runtime/identity.py (resolve_actor_id)
    └── imports → runtime/physics/graph/GraphOps (universe switch)

subcall_auto.py
    └── imports → mcp/tools/subcall_handler.py (_query_resonance — for auto_subcall flow)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `logging` | Logger for debug/info/warning | Both files |
| `uuid` | Moment node ID generation | subcall_handler.py |
| `re` | Keyword extraction, handle parsing, trigger patterns | Both files |
| `math` | sqrt for centroid divergence, various calculations | subcall_auto.py |
| `hashlib` | Deterministic whisper variant selection (MD5) | subcall_handler.py |
| `subprocess` | Git remote URL resolution in _enrich_query | subcall_handler.py |
| `random` | Random citizen sampling in _discover_random | subcall_handler.py |

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Module import — TOOL_SCHEMA dict and SCENARIO_PROFILES dict are created at import time
2. No initialization needed — handlers are stateless (except TriggerState in auto module)
3. ServerContext injected at call time — provides graph_ops, graph_queries, runner
```

### Main Request Cycle

```
1. MCP server receives tool call with name="subcall"
2. server.py dispatches to handle_subcall(args, ctx)
3. Resolve caller, target, scenario, universe
4. One of 6 targeting paths executes
5. Resonance probing via KNN + fallback
6. Format into briefing
7. Persist moment node
8. Return MCP response {"content": [...]}
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `HOME_ID` | Environment variable | `lumina_prime` | Default graph/universe name |
| `FALKORDB_GRAPH` | Environment variable | `lumina_prime` | Fallback graph name |
| top_k cap | `subcall_handler.py:1848` | 10 | Maximum resonating nodes per citizen |
| random cap | `subcall_handler.py:1569` | 500 | Maximum random sample size |
| cooldown | `subcall_auto.py:268` | 5 messages | Auto-trigger cooldown after firing |
| activation_threshold | `subcall_handler.py:293` | 0.15 | Minimum energy for cluster harvesting |

---

## EXTRACTION CANDIDATES

Files approaching WATCH/SPLIT status — identify what can be extracted:

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `subcall_handler.py` | ~2229L | <700L | `subcall_formatters.py` | `_format_as_telemetry()`, `_format_resonance()`, `_format_as_inner_voice()`, `_format_centroid()`, `_generate_recommendation()` (~560L) |
| `subcall_handler.py` | ~2229L | <700L | `subcall_targeting.py` | `_discover_team()`, `_discover_by_trade()`, `_discover_random()`, `_broadcast()` (~310L) |
| `subcall_handler.py` | ~2229L | <700L | `subcall_resonance.py` | `_query_resonance()`, `_build_stimulus_cluster()`, `_build_response_cluster()` (~350L) |
| `subcall_auto.py` | ~810L | <700L | (merge trigger patterns into config) | `QUESTION_PATTERNS`, `VERIFICATION_PATTERNS`, `FRUSTRATION_PATTERNS` (~240L of pattern lists) |

---

## MARKERS

<!-- @mind:proposition Extract subcall_handler.py into 4 files: handler (core pipeline), formatters, targeting, resonance — each under 600 lines -->
<!-- @mind:proposition Move trigger regex patterns from subcall_auto.py into a YAML config file for easier bilingual maintenance -->
