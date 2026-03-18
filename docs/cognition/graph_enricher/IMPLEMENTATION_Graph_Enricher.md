# Graph Enricher — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Graph_Enricher.md
BEHAVIORS:       ./BEHAVIORS_Graph_Enricher.md
PATTERNS:        ./PATTERNS_Graph_Enricher.md
ALGORITHM:       ./ALGORITHM_Graph_Enricher.md
VALIDATION:      ./VALIDATION_Graph_Enricher.md
THIS:            IMPLEMENTATION_Graph_Enricher.md (you are here)
HEALTH:          ./HEALTH_Graph_Enricher.md
SYNC:            ./SYNC_Graph_Enricher.md

IMPL:            scripts/graph_enricher.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

### Current (v1 — @handle extraction only)

```
scripts/
├── graph_enricher.py              # All enrichment logic: on_message, on_reply, on_react, on_commit, on_pin, on_read
├── citizen_wake.py                # _inject_l1_stimulus (imported by enricher for space stimulus)
├── discord_bridge.py              # Calls graph_enricher.on_message/on_reply/on_react
└── ...

runtime/bridges/
├── telegram_bridge.py             # Calls graph_enricher.on_message
├── whatsapp_bridge.py             # Calls graph_enricher.on_message
└── ...

mcp/tools/
└── graph_write_handler.py         # infer_computed_type() imported by enricher
```

### Target (v2 — full entity extraction)

```
scripts/
├── graph_enricher.py                                   # Structural enrichment + orchestration (existing, extended)
├── graph_enricher_tier1_pattern_entity_extractor.py     # Tier 1: URL, $token, @handle regex extraction
├── graph_enricher_tier2_llm_entity_extractor.py         # Tier 2: Gemini structured output extraction
├── graph_enricher_entity_resolver.py                    # Embedding match + threshold logic
├── graph_enricher_node_merger.py                        # Auto-merge + merge proposal creation
├── citizen_wake.py                                      # (unchanged)
└── ...
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `scripts/graph_enricher.py` | Structural enrichment: Moment/Actor/Space creation, @mention links, space stimulus, trust propagation, reply/react/commit/pin/read handlers | `on_message`, `on_reply`, `on_react`, `on_commit`, `on_file_change`, `on_pin`, `on_unpin`, `on_read`, `_stimulate_space_citizens` | ~985 | WATCH |
| `scripts/graph_enricher_tier1_pattern_entity_extractor.py` | Regex extraction of URLs, $tokens, @handles from text | `extract_urls`, `extract_tokens`, `extract_handles` | ~80 (est.) | PLANNED |
| `scripts/graph_enricher_tier2_llm_entity_extractor.py` | Gemini structured output for name/org/place extraction | `extract_entities_from_text`, `ExtractionResult` | ~120 (est.) | PLANNED |
| `scripts/graph_enricher_entity_resolver.py` | Embedding similarity match against existing graph nodes | `resolve_entity`, `query_by_embedding` | ~150 (est.) | PLANNED |
| `scripts/graph_enricher_node_merger.py` | Auto-merge on deterministic signal, merge proposal creation | `auto_merge`, `propose_merge`, `check_platform_id_collision` | ~120 (est.) | PLANNED |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size
- **WATCH** (400-700 lines): Getting large, consider extraction
- **SPLIT** (>700 lines): Must split before adding more code

> `graph_enricher.py` is at ~985 lines (SPLIT). Before adding entity extraction inline, the new functionality should be extracted into the planned helper files. The existing file should be trimmed by extracting helper functions (`_sanitize_handle`, `_moment_id`, `_get_graph`).

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with fan-out

**Why this pattern:** Entity extraction is naturally a pipeline (text → patterns → LLM → resolution → graph). But Step 3 (tier 1) and Step 4 (tier 2) can run in parallel since they are independent. Step 5 (resolution) fans out per entity. The pipeline shape makes rejection points explicit and the flow testable.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Lazy singleton | `_get_graph()` | Global FalkorDB connection, initialized once on first use |
| MERGE-then-SET | All node creation | Idempotent node creation — safe to call multiple times |
| Dimensional links | All LINK creation | `:LINK` with dimensional properties + `infer_computed_type()` |
| Guard clause | `on_message()` entry | Early return if graph unavailable |

### Anti-Patterns to Avoid

- **Inline LLM calls in on_message()**: Gemini extraction should not block the structural write path. Extract to a separate function that runs after structural enrichment completes.
- **String-matching for entity resolution**: Don't use Levenshtein distance or substring matching for name dedup. Embeddings handle linguistic variations that string metrics miss.
- **Creating handle nodes**: Platform handles are fields on Actor nodes, not separate nodes. Don't create Thing or Actor nodes for Telegram IDs.
- **Merging on embedding alone**: Auto-merge requires deterministic signal. Embedding similarity creates proposals, not merges.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Graph Enricher | Entity extraction, node creation, dedup, merge | Physics (weight/energy), trust computation, context assembly | `on_message()`, `on_reply()`, `on_react()`, `on_commit()` |
| Tier 1 Extractor | Regex pattern matching | LLM calls, embedding computation | `extract_urls(text)`, `extract_tokens(text)`, `extract_handles(text)` |
| Tier 2 Extractor | Gemini API call, response parsing | Entity resolution, graph mutation | `extract_entities_from_text(content) -> list[ExtractionResult]` |
| Entity Resolver | Embedding computation, similarity search, threshold logic | Node creation, merge execution | `resolve_entity(name, context, type, graph) -> (node_id, action)` |
| Node Merger | Link transfer, property merge, node deletion | Entity recognition, similarity computation | `auto_merge(keep_id, discard_id, graph)` |

---

## SCHEMA

### Actor Node (with platform handle fields)

```yaml
Actor:
  required:
    - id: str                    # handle or SID
    - name: str                  # display name
  optional:
    - sid: str                   # Sovereign ID (sha256[:16])
    - handle: str                # Human-readable alias
    - type: str                  # "human" | "ai" | "agent" | "bot" | "service"
    - status: str                # "confirmed" | "unconfirmed"
    - telegram_id: str           # Telegram user_id
    - discord_id: str            # Discord user_id (snowflake)
    - x_handle: str              # X/Twitter handle
    - linkedin_url: str          # LinkedIn profile URL
    - email: str                 # Email address
    - phone: str                 # Phone number (E.164)
    - embedding: vector          # Name embedding for similarity search
  constraints:
    - At most one Actor per (platform, platform_id) pair
    - status defaults to "confirmed" for bridge-verified Actors
```

### Thing Node (enriched types)

```yaml
Thing:
  required:
    - id: str                    # thing:{subtype}:{scope}:{slug}
    - name: str                  # Display name or URL
  optional:
    - type: str                  # "url" | "token" | "organization" | "tool" | "document"
    - status: str                # "confirmed" | "unconfirmed"
    - content: str               # Full content (URL string, document reference, etc.)
    - embedding: vector          # Content/name embedding
  constraints:
    - URLs use id format: thing:url:{hash}
    - Tokens use id format: thing:token:{symbol}
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `on_message()` | `graph_enricher.py:67` | Discord bridge, Telegram bridge, WhatsApp bridge |
| `on_reply()` | `graph_enricher.py:313` | Discord bridge on reply events |
| `on_react()` | `graph_enricher.py:550` | Discord bridge on reaction events |
| `on_commit()` | `graph_enricher.py:647` | Git post-commit hook |
| `on_file_change()` | `graph_enricher.py:790` | Git post-commit hook for significant files |
| `on_pin()` / `on_unpin()` | `graph_enricher.py:877/908` | Discord bridge on pin events |
| `on_read()` | `graph_enricher.py:937` | Discord bridge on channel read |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Message Enrichment: Bridge Event to Enriched Graph

The primary flow: a message event arrives from a bridge, the enricher creates structural nodes, extracts entities, resolves them against the graph, and creates or links nodes.

```yaml
flow:
  name: message_enrichment
  purpose: Extract entities from message text and materialize them as L3 graph nodes
  scope: bridge callback -> on_message -> tier 1 + tier 2 extraction -> entity resolution -> graph
  steps:
    - id: step_1_structural
      description: Create Moment/Actor/Space nodes and structural links (existing behavior)
      file: scripts/graph_enricher.py
      function: on_message
      input: platform, channel_id, channel_name, author_name, author_handle, content, mentioned_handles
      output: Moment node, Actor node, Space node, structural LINK edges
      trigger: Bridge callback (discord_bridge, telegram_bridge)
      side_effects: Graph nodes created, AI citizens stimulated, trust propagated

    - id: step_2_platform_handles
      description: Update Author Actor with platform-specific sender_id
      file: scripts/graph_enricher.py (to be added)
      function: _update_platform_handles
      input: Actor node, platform, bridge metadata (sender_id)
      output: Actor node with platform_id field set
      trigger: After structural enrichment
      side_effects: May trigger auto-merge if platform_id collision detected

    - id: step_3_tier1
      description: Regex extraction of URLs, $tokens, @handles
      file: scripts/graph_enricher_tier1_pattern_entity_extractor.py (planned)
      function: extract_urls, extract_tokens, extract_handles
      input: Moment content text
      output: List of (entity_type, value) tuples
      trigger: After structural enrichment
      side_effects: Thing nodes created for URLs/tokens, LINK(mentions) edges

    - id: step_4_tier2
      description: LLM extraction of names, organizations, places
      file: scripts/graph_enricher_tier2_llm_entity_extractor.py (planned)
      function: extract_entities_from_text
      input: Moment content text
      output: List[ExtractionResult] with name, type, confidence, context
      trigger: After tier 1 (can be async)
      side_effects: Gemini API call

    - id: step_5_resolve
      description: Match each extraction against existing nodes by embedding similarity
      file: scripts/graph_enricher_entity_resolver.py (planned)
      function: resolve_entity
      input: ExtractionResult, graph reference
      output: (node_id, "matched"|"created"|"merge_proposed")
      trigger: Per extraction from step 4
      side_effects: New nodes created, LINK(mentions) edges, merge proposals

  docking_points:
    available:
      - id: dock_structural_complete
        type: graph_ops
        direction: output
        file: scripts/graph_enricher.py
        function: on_message
        trigger: After step 1 completes
        payload: moment_id, actor_id, space_id
        async_hook: not_applicable
        needs: none
        notes: Marks completion of the existing v1 enrichment

      - id: dock_entities_extracted
        type: event
        direction: output
        file: scripts/graph_enricher_tier2_llm_entity_extractor.py
        function: extract_entities_from_text
        trigger: After Gemini returns
        payload: list[ExtractionResult]
        async_hook: optional
        needs: add event emission
        notes: Important for monitoring extraction quality and volume

      - id: dock_entity_resolved
        type: graph_ops
        direction: output
        file: scripts/graph_enricher_entity_resolver.py
        function: resolve_entity
        trigger: Per entity after resolution
        payload: (node_id, action, similarity_score)
        async_hook: not_applicable
        needs: add logging
        notes: Tracks match vs create vs merge_proposed ratio

      - id: dock_merge_executed
        type: graph_ops
        direction: output
        file: scripts/graph_enricher_node_merger.py
        function: auto_merge
        trigger: Platform ID collision detected
        payload: (keep_id, discard_id, merge_type)
        async_hook: not_applicable
        needs: add logging
        notes: Critical for monitoring identity resolution correctness

    health_recommended:
      - dock_id: dock_structural_complete
        reason: V1 — verify every message produces structural graph state
      - dock_id: dock_entities_extracted
        reason: Monitor Gemini extraction volume, latency, and error rate
      - dock_id: dock_entity_resolved
        reason: V8 — track match/create/merge ratio for threshold tuning
      - dock_id: dock_merge_executed
        reason: V4, V5 — verify merges preserve links and enforce uniqueness
```

---

## LOGIC CHAINS

### LC1: URL in Message to Thing Node

**Purpose:** Trace how a URL in a message becomes a Thing node in the graph.

```
Bridge callback (message containing "https://arxiv.org/paper")
  -> on_message(content="Check this https://arxiv.org/paper", ...)
    -> Step 1: Moment/Actor/Space created (structural)
    -> Step 3: extract_urls(content) -> ["https://arxiv.org/paper"]
      -> MERGE Thing(id="thing:url:{hash}", type="url", status="confirmed")
        -> CREATE LINK(mentions) Moment -> Thing
```

**Data transformation:**
- Input: raw message text containing URL
- After regex: list of URL strings
- After node creation: Thing node in graph
- Output: LINK(mentions) connecting Moment to Thing

### LC2: Name in Free Text to Unconfirmed Actor

**Purpose:** Trace how a person name mentioned in text becomes an Actor node.

```
Bridge callback (message containing "I talked to Florent Berthet from CeSIA")
  -> on_message(content=..., ...)
    -> Step 1: structural enrichment
    -> Step 4: extract_entities_from_text(content) via Gemini
      -> [{name: "Florent Berthet", type: "person", confidence: 0.9, context: "from CeSIA"},
          {name: "CeSIA", type: "organization", confidence: 0.85, context: "Florent Berthet from CeSIA"}]
    -> Step 5: resolve_entity("Florent Berthet", "from CeSIA", "person", graph)
      -> compute_embedding("Florent Berthet from CeSIA")
      -> query_actors_by_embedding(embedding, top_k=5) -> no match (similarity < 0.85)
      -> CREATE Actor(status="unconfirmed", name="Florent Berthet", embedding=...)
      -> CREATE LINK(mentions) Moment -> Actor
    -> Step 5: resolve_entity("CeSIA", ..., "organization", graph)
      -> CREATE Thing(status="unconfirmed", type="organization", name="CeSIA")
      -> CREATE LINK(mentions) Moment -> Thing
```

### LC3: Platform ID Collision to Auto-Merge

**Purpose:** Trace how a Telegram message from a known sender triggers identity resolution.

```
Telegram bridge (message from user_id=12345, display_name="Flo")
  -> on_message(author_handle="flo", ...)
    -> Step 1: MERGE Actor(id="flo", name="Flo")
    -> Step 2: SET Actor(id="flo").telegram_id = "12345"
      -> CHECK: any other Actor with telegram_id="12345"?
      -> FOUND: Actor(id="florent-berthet", telegram_id="12345")
      -> auto_merge(keep="florent-berthet", discard="flo")
        -> Transfer all links from "flo" to "florent-berthet"
        -> DELETE Actor(id="flo")
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
graph_enricher.py
    ├── imports -> mcp/tools/graph_write_handler.py  (infer_computed_type)
    ├── imports -> scripts/citizen_wake.py  (_inject_l1_stimulus)
    └── imports -> runtime/economy/trust_propagation.py  (propagate_trust)

graph_enricher_tier2_llm_entity_extractor.py (planned)
    └── imports -> google.generativeai  (Gemini client)

graph_enricher_entity_resolver.py (planned)
    └── imports -> embedding computation (google or local model)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `falkordb` | Graph database connection and queries | `graph_enricher.py` |
| `hashlib` | SHA256 for moment IDs, URL hashes | `graph_enricher.py` |
| `re` | Regex for handle sanitization, URL/token extraction | `graph_enricher.py`, `tier1_extractor` |
| `google-generativeai` | Gemini structured output for entity extraction | `tier2_extractor` (planned) |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Graph connection | `_graph` module global | Process | Lazy-initialized on first use, lives for process lifetime |
| Graph name | `_graph_name` module global | Process | Set at module load ("lumina-prime") |
| Extracted entities | Function-local | Per-message | Created during extraction, consumed by resolution, then discarded |
| Merge proposals | Graph nodes (Thing or Narrative, TBD) | Persistent | Created on similarity match, resolved by human or agent |

### State Transitions

```
Message arrives ──on_message()──> Structural nodes created
    ──tier 1──> Pattern entities created (confirmed)
    ──tier 2──> LLM entities extracted
    ──resolution──> Entities matched or created (unconfirmed)
    ──merge check──> Platform ID collision? → auto_merge
                     Embedding similarity? → merge proposal
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Module import: _graph = None (lazy)
2. First on_message() call: _get_graph() connects to FalkorDB
3. All subsequent calls use cached _graph connection
```

### Main Loop (per message)

```
1. Bridge delivers message event
2. on_message() called with platform, channel, author, content, mentions
3. Step 1: Structural enrichment (existing — MERGE Space, Actor, CREATE Moment, links)
4. Step 2: Platform handle update (set telegram_id/discord_id on Actor)
5. Step 3: Tier 1 pattern extraction (regex: URLs, $tokens, @handles)
6. Step 4: Tier 2 LLM extraction (Gemini: names, orgs, places)
7. Step 5: Entity resolution per extraction (embedding match, threshold logic)
8. Step 6: Auto-merge if platform_id collision detected
9. Space stimulus: inject L1 stimulus to present AI citizens
10. Trust propagation for mentions
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `_graph_name` | `graph_enricher.py` | `"lumina-prime"` | FalkorDB graph name |
| `AUTO_MATCH_THRESHOLD` | `entity_resolver.py` (planned) | `0.95` | Embedding similarity for auto-match to existing node |
| `PROPOSE_MERGE_THRESHOLD` | `entity_resolver.py` (planned) | `0.85` | Embedding similarity for merge proposal |
| `MIN_EXTRACTION_CONFIDENCE` | `tier2_extractor.py` (planned) | `0.6` | Minimum confidence for LLM-extracted entities |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Line | Reference |
|------|------|-----------|
| `graph_enricher.py` | 1-18 | Module docstring describes the enrichment pipeline |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 1 (Structural) | `graph_enricher.py:on_message()` lines 67-230 |
| ALGORITHM Step 1 (Reply) | `graph_enricher.py:on_reply()` lines 313-548 |
| ALGORITHM Step 1 (React) | `graph_enricher.py:on_react()` lines 550-644 |
| ALGORITHM Step 1 (Commit) | `graph_enricher.py:on_commit()` lines 647-788 |
| BEHAVIOR B1 | `graph_enricher.py:on_message()` |
| BEHAVIOR B2 | `graph_enricher.py:on_message()` lines 212-230 |
| BEHAVIOR B3-B10 | PLANNED — not yet implemented |

---

## EXTRACTION CANDIDATES

`graph_enricher.py` is at ~985 lines (SPLIT status). Before adding entity extraction:

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `graph_enricher.py` | ~985L | <700L | `graph_enricher_tier1_pattern_entity_extractor.py` | URL, token, handle regex extraction |
| `graph_enricher.py` | ~985L | <700L | `graph_enricher_node_merger.py` | Auto-merge logic, merge proposal creation |
| `graph_enricher.py` | ~985L | <700L | Inline utilities | `_sanitize_handle`, `_moment_id` could be shared utilities |

---

## MARKERS

<!-- @mind:todo Split graph_enricher.py (985 lines, SPLIT status) before adding entity extraction -->
<!-- @mind:todo Create graph_enricher_tier1_pattern_entity_extractor.py -->
<!-- @mind:todo Create graph_enricher_tier2_llm_entity_extractor.py -->
<!-- @mind:todo Create graph_enricher_entity_resolver.py -->
<!-- @mind:todo Create graph_enricher_node_merger.py -->
<!-- @mind:todo Add platform handle fields to Actor MERGE queries -->
<!-- @mind:escalation FalkorDB vector index: does the current deployment support CALL db.idx.vector.queryNodes? Need to verify. -->
