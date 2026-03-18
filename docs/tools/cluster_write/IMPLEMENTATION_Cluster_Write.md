# Cluster Write — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
BEHAVIORS:       ./BEHAVIORS_Cluster_Write.md
PATTERNS:        ./PATTERNS_Cluster_Write.md
ALGORITHM:       ./ALGORITHM_Cluster_Write.md
VALIDATION:      ./VALIDATION_Cluster_Write.md
THIS:            IMPLEMENTATION_Cluster_Write.md (you are here)
HEALTH:          ./HEALTH_Cluster_Write.md
SYNC:            ./SYNC_Cluster_Write.md

IMPL:            mcp/tools/cluster_write_handler.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mcp/tools/
├── cluster_write_handler.py           # Main handler: TOOL_SCHEMA, handle_cluster_write(), Phase 4 write logic
├── cluster_write_analyzer.py          # Phase 2: Gemini extraction, entity resolution, regex fallback
├── cluster_write_context.py           # Phase 1: pre-compute citizen context from graph
├── graph_write_handler.py             # Existing: infer_computed_type() reused for link creation
├── think_handler.py                   # Existing: Gemini API integration used for content analysis
└── context.py                         # Existing: ServerContext dependency injection
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines (est.) | Status |
|------|---------|----------------------|-------|--------|
| `cluster_write_handler.py` | Entry point, TOOL_SCHEMA, suggestion formatting, Phase 4 write | `handle_cluster_write()`, `_write_cluster()`, `_format_suggestions()` | ~300 | PLANNED |
| `cluster_write_analyzer.py` | Phase 2 content analysis, entity extraction, entity resolution | `analyze_content()`, `resolve_entity()`, `build_extraction_prompt()` | ~350 | PLANNED |
| `cluster_write_context.py` | Phase 1 pre-compute citizen context | `precompute_context()`, `CitizenContext` dataclass | ~100 | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (4-phase: Pre-compute → Analyze → Suggest → Write)

**Why this pattern:** Each phase has a clear input/output contract and a distinct responsibility. The pipeline can short-circuit (confirm=true skips Suggest) and degrade gracefully (Gemini failure falls back to regex in Analyze). The phases are separated into files because they have different dependency profiles: context reads from graph, analyzer calls Gemini + graph, handler writes to graph.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Dataclass | `CitizenContext`, `EntityCandidate`, `ExistingMatch` | Typed data structures for pipeline stages |
| Strategy | Entity resolution in `resolve_entity()` | Multiple resolution strategies (platform_id, email, handle, embedding) tried in priority order |
| Reuse | `infer_computed_type()` from `graph_write_handler.py` | Link type computation — same math, no duplication |

### Anti-Patterns to Avoid

- **God handler**: Don't put all 4 phases in one function. The handler orchestrates; phases are separate functions in separate files.
- **Silent fallback**: When Gemini fails, log it. When regex produces no results, say so. Never swallow extraction failures.
- **Premature optimization**: Don't batch graph queries before proving the single-query approach is too slow. FalkorDB is in-process.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| cluster_write_handler | TOOL_SCHEMA, orchestration, write phase, response formatting | Content analysis, context loading | `handle_cluster_write(args, ctx)` |
| cluster_write_analyzer | Gemini prompt construction, entity extraction, entity resolution | Graph writes, context loading | `analyze_content(content, platform, context, ctx) → list[EntityCandidate]` |
| cluster_write_context | Graph reads for citizen context | Analysis, writes | `precompute_context(ctx) → CitizenContext` |

---

## SCHEMA

### TOOL_SCHEMA (MCP Interface)

```yaml
cluster_write:
  required:
    - content: string          # Natural language event description
  optional:
    - space: string            # Explicit space ID (default: citizen's current)
    - actors: list[ActorRef]   # Platform-verified actor references
    - things: list[ThingRef]   # Explicit thing references
    - platform: PlatformMeta   # Source platform metadata
    - confirm: bool            # Skip suggestions, write immediately (default: false)
  constraints:
    - content must not be empty
    - actors[].platform_id requires actors[].platform
```

### ActorRef (nested in TOOL_SCHEMA)

```yaml
ActorRef:
  optional:
    - name: string             # Display name
    - platform_id: string      # Platform-specific ID
    - platform: string         # Platform name (telegram, discord, x, email, phone)
    - handle: string           # @handle
    - email: string            # Email address
    - phone: string            # Phone number
```

### PlatformMeta (nested in TOOL_SCHEMA)

```yaml
PlatformMeta:
  optional:
    - source: string           # Platform name
    - message_id: string       # Original message ID on platform
    - channel_id: string       # Channel/chat ID
    - timestamp: int           # Original message timestamp
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `handle_cluster_write()` | `cluster_write_handler.py:1` | MCP tool call "cluster_write" |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Cluster Write Flow: Content → Graph Cluster

Explain what this flow covers: the complete pipeline from a citizen's natural language content to a fully-linked graph cluster. This is the only flow in the module — there is one entry point and one output shape.

```yaml
flow:
  name: cluster_write_pipeline
  purpose: Transform content into Moment + Space + Actors + Things + links
  scope: citizen content in, graph cluster out
  steps:
    - id: precompute
      description: Load citizen's current context from graph
      file: mcp/tools/cluster_write_context.py
      function: precompute_context
      input: ServerContext (with graph_ops)
      output: CitizenContext
      trigger: handle_cluster_write called
      side_effects: graph reads only

    - id: analyze
      description: Extract entities from content, resolve against graph
      file: mcp/tools/cluster_write_analyzer.py
      function: analyze_content
      input: content (string), PlatformMeta, CitizenContext, ServerContext
      output: list[EntityCandidate]
      trigger: precompute completes
      side_effects: Gemini API call, graph reads for entity matching

    - id: suggest
      description: Format entity candidates for citizen review (if confirm=false)
      file: mcp/tools/cluster_write_handler.py
      function: _format_suggestions
      input: list[EntityCandidate]
      output: dict (suggestion response)
      trigger: analyze completes AND confirm=false
      side_effects: none

    - id: write
      description: Create all nodes and links atomically
      file: mcp/tools/cluster_write_handler.py
      function: _write_cluster
      input: content, list[EntityCandidate], CitizenContext, ServerContext
      output: Cluster (moment_id, actor_ids, thing_ids, links)
      trigger: analyze completes AND confirm=true
      side_effects: graph writes (nodes + links)

  docking_points:
    guidance:
      include_when: transformative steps, external API calls, graph mutations
      omit_when: internal data passing between functions
      selection_notes: Monitor Gemini call success and graph write atomicity
    available:
      - id: dock_gemini_call
        type: api
        direction: output
        file: mcp/tools/cluster_write_analyzer.py
        function: analyze_content
        trigger: content analysis request
        payload: {prompt: string, response: JSON}
        async_hook: optional
        needs: none (uses existing think_handler)
        notes: Gemini failure triggers regex fallback — monitor success rate

      - id: dock_entity_resolution
        type: graph_ops
        direction: input
        file: mcp/tools/cluster_write_analyzer.py
        function: resolve_entity
        trigger: per entity extracted
        payload: {entity_name: string, match_result: ExistingMatch|null}
        async_hook: not_applicable
        needs: none
        notes: KNN search + exact match queries — monitor dedup accuracy

      - id: dock_cluster_write
        type: graph_ops
        direction: output
        file: mcp/tools/cluster_write_handler.py
        function: _write_cluster
        trigger: confirm=true
        payload: {nodes_created: int, links_created: int, errors: list}
        async_hook: not_applicable
        needs: none
        notes: Critical — partial write = graph corruption. Monitor for rollback events.

    health_recommended:
      - dock_id: dock_gemini_call
        reason: External API — most likely failure point in the pipeline
      - dock_id: dock_cluster_write
        reason: Graph mutation — must verify atomicity invariant (V2)
```

---

## LOGIC CHAINS

### LC1: Full Pipeline (confirm=false)

**Purpose:** Content → suggestions for citizen review

```
handle_cluster_write(args, ctx)
  → cluster_write_context.precompute_context(ctx)       # CitizenContext
    → cluster_write_analyzer.analyze_content(...)        # list[EntityCandidate]
      → _format_suggestions(candidates)                  # suggestion dict
        → return suggestions to citizen
```

**Data transformation:**
- Input: `ClusterInput` — raw content + optional platform metadata
- After precompute: `CitizenContext` — citizen's spaces, recent actors, things
- After analyze: `list[EntityCandidate]` — extracted entities with matches and confidence
- Output: `dict` — formatted suggestions with match context

### LC2: Full Pipeline (confirm=true)

**Purpose:** Content → graph cluster

```
handle_cluster_write(args, ctx)
  → cluster_write_context.precompute_context(ctx)       # CitizenContext
    → cluster_write_analyzer.analyze_content(...)        # list[EntityCandidate]
      → _write_cluster(content, candidates, context, ctx)  # Cluster
        → return Cluster to citizen
```

**Data transformation:**
- Input: `ClusterInput` — raw content + confirm=true
- After precompute: `CitizenContext`
- After analyze: `list[EntityCandidate]`
- Output: `Cluster` — moment_id, space_id, actor_ids, thing_ids, links

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
cluster_write_handler
    └── imports → cluster_write_context  (precompute_context)
    └── imports → cluster_write_analyzer (analyze_content)
    └── imports → graph_write_handler    (infer_computed_type)
    └── imports → context                (ServerContext)

cluster_write_analyzer
    └── imports → think_handler          (handle_think for Gemini)
    └── imports → context                (ServerContext)

cluster_write_context
    └── imports → context                (ServerContext)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `runtime/identity.py` | Caller identification | `cluster_write_context.py` |
| `runtime/infrastructure/embeddings/service` | Embedding computation | `cluster_write_analyzer.py`, `cluster_write_handler.py` |
| `hashlib` | URL hashing for deterministic Thing IDs | `cluster_write_analyzer.py` |
| `re` | Regex extraction (URLs, @handles, $tokens) | `cluster_write_analyzer.py` |
| `uuid` | Fallback ID generation | `cluster_write_handler.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| CitizenContext | In-memory during pipeline | Per-request | Created in Phase 1, consumed in Phase 2-4, garbage collected |
| EntityCandidates | In-memory during pipeline | Per-request | Created in Phase 2, consumed in Phase 3-4, garbage collected |

No persistent state. The handler is stateless — all state lives in the graph (FalkorDB) and is read/written per request.

---

## RUNTIME BEHAVIOR

### Main Request Cycle

```
1. MCP framework calls handle_cluster_write(args, ctx)
2. Validate input (content required)
3. Phase 1: precompute_context(ctx) → CitizenContext
4. Phase 2: analyze_content(content, platform, context, ctx) → list[EntityCandidate]
5. If confirm=false: Phase 3: _format_suggestions(candidates) → return suggestions
6. If confirm=true: Phase 4: _write_cluster(content, candidates, context, ctx) → return Cluster
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Handler | sync | Single-threaded, one cluster_write at a time per citizen |
| Gemini call | sync (blocking) | Uses existing think_handler which is synchronous |
| Graph operations | sync | FalkorDB is in-process, no network I/O |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `GEMINI_MODEL` | env var | `gemini-2.5-flash` | Model used for content analysis |
| `SIMILARITY_THRESHOLD` | `cluster_write_analyzer.py` | `0.75` | Minimum embedding similarity to suggest a match |
| `AUTO_MERGE_THRESHOLD` | `cluster_write_analyzer.py` | `0.92` | Minimum similarity for auto-merge (with exact name) |
| `CONFIRMED_LINK_WEIGHT` | `cluster_write_handler.py` | `1.0` | Link weight for platform-confirmed entities |
| `UNCONFIRMED_LINK_WEIGHT` | `cluster_write_handler.py` | `0.5` | Link weight for text-mention entities |

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Phase 1 | `cluster_write_context.py:precompute_context()` |
| ALGORITHM Phase 2 | `cluster_write_analyzer.py:analyze_content()` |
| ALGORITHM Phase 3 | `cluster_write_handler.py:_format_suggestions()` |
| ALGORITHM Phase 4 | `cluster_write_handler.py:_write_cluster()` |
| BEHAVIOR B1 | `cluster_write_handler.py:_write_cluster()` |
| BEHAVIOR B2 | `cluster_write_analyzer.py:resolve_entity()` |
| BEHAVIOR B5 | `cluster_write_analyzer.py:analyze_content()` |
| VALIDATION V1 | Test: moment always created |
| VALIDATION V2 | Test: rollback on partial failure |
| VALIDATION V3 | Test: platform_id dedup |

---

## MARKERS

<!-- @mind:todo Implement cluster_write_handler.py with TOOL_SCHEMA and handle_cluster_write() -->
<!-- @mind:todo Implement cluster_write_analyzer.py with Gemini extraction prompt and entity resolution -->
<!-- @mind:todo Implement cluster_write_context.py with graph queries for citizen context -->
<!-- @mind:todo Register cluster_write in mcp/tools/__init__.py tool registry -->
<!-- @mind:proposition Consider extracting link creation helpers into a shared module used by both graph_write and cluster_write -->
