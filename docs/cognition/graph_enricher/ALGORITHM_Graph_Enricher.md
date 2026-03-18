# Graph Enricher — Algorithm: Entity Extraction and Resolution Pipeline

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
THIS:            ALGORITHM_Graph_Enricher.md (you are here)
VALIDATION:      ./VALIDATION_Graph_Enricher.md
HEALTH:          ./HEALTH_Graph_Enricher.md
IMPLEMENTATION:  ./IMPLEMENTATION_Graph_Enricher.md
SYNC:            ./SYNC_Graph_Enricher.md

IMPL:            scripts/graph_enricher.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The graph enricher processes every Moment creation event and extracts entities from the Moment's content. The extraction pipeline has two tiers: a synchronous pattern-matching tier for deterministic entities (URLs, @handles, $tokens, platform IDs) and an LLM-assisted tier for free-text entity names (people, places, organizations, tools). Each extracted entity goes through a resolution step: match against existing graph nodes, then either link to an existing node, auto-merge, create a new node, or propose a merge task.

The pipeline is designed to never block the critical write path. Tier 1 runs inline with on_message(). Tier 2 (Gemini extraction) runs as a post-processing step that can be async.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Entity extraction | B1, B3, B4, B5, B6, B7 | Converts free text into graph nodes |
| O2: Dedup and merge | B9, B10 | Prevents ghost nodes, resolves duplicate identities |
| O3: Confidence-aware | B3, B4, B5, B6, B7 | confirmed vs unconfirmed status |
| O4: Platform handles | B8, B9 | Platform IDs as Actor fields, cross-platform matching |
| O5: Minimal latency | B1, B3, B4 | Pattern extraction is O(n) on text length, no I/O |

---

## DATA STRUCTURES

### ExtractionResult (from Gemini structured output)

```
A single entity extracted from free text by the LLM.

Fields:
  name: str               # The entity name as it appears in text
  entity_type: str         # "person" | "organization" | "place" | "tool" | "document"
  confidence: float        # 0.0 to 1.0 — LLM's confidence in the extraction
  context: str             # Surrounding text snippet that justifies the extraction
```

### PlatformHandles (fields on Actor node)

```
Platform-specific identifiers stored directly on the Actor node.

Fields (all nullable):
  telegram_id: str         # Telegram user_id (numeric string)
  discord_id: str          # Discord user_id (snowflake)
  x_handle: str            # X/Twitter handle (without @)
  linkedin_url: str        # LinkedIn profile URL
  email: str               # Email address
  phone: str               # Phone number (E.164 format)
```

### MergeProposal (task for human review)

```
Created when embedding similarity suggests two nodes might be the same entity.

Fields:
  source_node_id: str      # The newly created node
  target_node_id: str      # The existing node it might match
  similarity: float        # Cosine similarity between embeddings
  evidence: str            # Why we think these might be the same
  status: str              # "pending" | "approved" | "rejected"
```

---

## ALGORITHM: Enrichment Pipeline

### Step 1: Structural Enrichment (existing — on_message)

This step exists today. It creates the structural Moment/Actor/Space nodes and their relationships. Every message event goes through this step.

```
1. MERGE Space node for the channel (id: space:{platform}:{channel_id})
2. MERGE Actor node for the author (id: author_handle or sanitized name)
3. CREATE Moment node (id: moment_{hash}, content, synthesis, timestamp)
4. CREATE LINK(presence) Actor→Space (affinity=0.3, recency=ts)
5. CREATE LINK(occurred_in) Moment→Space (hierarchy=1.0, polarity=1.0)
6. CREATE LINK(created) Actor→Moment (hierarchy=-1.0, permanence=0.8)
7. For each @mentioned handle: MERGE Actor, CREATE LINK(mention) Moment→Actor
8. Inject L1 stimulus to AI citizens present in the Space
9. Propagate trust for each mention
```

### Step 2: Platform Handle Update

After the Author Actor is merged/created, update their platform handle fields from bridge metadata.

```
IF platform == "telegram" AND metadata.user_id:
    SET Actor.telegram_id = metadata.user_id
    CHECK: does another Actor already have telegram_id = metadata.user_id?
    IF yes: trigger auto-merge (Step 6)

IF platform == "discord" AND metadata.user_id:
    SET Actor.discord_id = metadata.user_id
    CHECK: does another Actor already have discord_id = metadata.user_id?
    IF yes: trigger auto-merge (Step 6)

(Same pattern for email, phone, x_handle, linkedin_url when available)
```

### Step 3: Tier 1 — Pattern Extraction (synchronous)

Extract entities from the Moment content using regex patterns. No LLM, no I/O, no graph queries.

```
url_pattern = r'https?://[^\s<>"\')]+'
token_pattern = r'\$[A-Z]{2,10}\b'
handle_pattern = r'@[\w-]{2,40}\b'

FOR each URL match in content:
    url = match.group()
    thing_id = "thing:url:" + sha256(url)[:12]
    MERGE Thing(id=thing_id, type="url", status="confirmed", name=url, content=url)
    CREATE LINK(mentions) Moment→Thing (polarity=0.5, recency=ts)

FOR each $TOKEN match in content:
    symbol = match.group()  # e.g. "$MIND"
    thing_id = "thing:token:" + symbol.lower()
    MERGE Thing(id=thing_id, type="token", status="confirmed", name=symbol)
    CREATE LINK(mentions) Moment→Thing (polarity=0.5, recency=ts)

FOR each @handle match in content NOT already in mentioned_handles:
    handle = match.group().lstrip("@").lower()
    MERGE Actor(id=handle)
    CREATE LINK(mentions) Moment→Actor (polarity=0.5, recency=ts)
```

### Step 4: Tier 2 — LLM Extraction (Gemini structured output)

Send the Moment content to Gemini with a structured output schema requesting entity extraction.

```
prompt = """Extract all named entities from this text.
For each entity, provide:
- name: the entity name as it appears
- entity_type: one of "person", "organization", "place", "tool", "document"
- confidence: 0.0 to 1.0
- context: the surrounding text that justifies this extraction

Text: {content}

Only extract entities that are clearly named. Do not extract pronouns or generic terms.
Do not extract @handles, URLs, or $TOKEN symbols (these are handled separately).
"""

response = gemini.generate(prompt, response_schema=list[ExtractionResult])

FOR each extraction in response:
    IF extraction.confidence < 0.6:
        SKIP  # Too uncertain
    GOTO Step 5 (Entity Resolution)
```

### Step 5: Entity Resolution (embedding match)

For each LLM-extracted entity, determine if it already exists in the graph.

```
embedding = compute_embedding(extraction.name + " " + extraction.context)

# Query existing nodes of the same type
IF extraction.entity_type == "person":
    candidates = query_actors_by_embedding(embedding, top_k=5)
    node_label = "Actor"
ELIF extraction.entity_type == "place":
    candidates = query_spaces_by_embedding(embedding, top_k=5)
    node_label = "Space"
ELSE:
    candidates = query_things_by_embedding(embedding, top_k=5)
    node_label = "Thing"

best_match = None
best_similarity = 0.0

FOR each candidate in candidates:
    sim = cosine_similarity(embedding, candidate.embedding)
    IF sim > best_similarity:
        best_similarity = sim
        best_match = candidate

IF best_similarity > AUTO_MATCH_THRESHOLD (0.95):
    # High confidence match — link to existing node
    CREATE LINK(mentions) Moment→best_match (polarity=0.5, recency=ts)

ELIF best_similarity > PROPOSE_MERGE_THRESHOLD (0.85):
    # Possible match — create new node AND propose merge
    new_node = CREATE {node_label}(status="unconfirmed", name=extraction.name)
    CREATE LINK(mentions) Moment→new_node
    CREATE MergeProposal(source=new_node.id, target=best_match.id, similarity=best_similarity)

ELSE:
    # No match — create new node
    new_node = CREATE {node_label}(status="unconfirmed", name=extraction.name)
    CREATE LINK(mentions) Moment→new_node

# Store embedding on the node for future matching
SET new_node.embedding = embedding (if new node was created)
```

### Step 6: Auto-Merge on Deterministic Signal

When a deterministic identity signal matches (same platform_id, same email, same phone):

```
FUNCTION auto_merge(keep_node, discard_node):
    # Transfer all links from discard to keep
    FOR each link FROM discard:
        IF link does not already exist on keep:
            RECREATE link with keep as source
    FOR each link TO discard:
        IF link does not already exist pointing to keep:
            RECREATE link with keep as target

    # Merge properties (keep's values take priority, fill gaps from discard)
    FOR each field in discard:
        IF keep.{field} is null AND discard.{field} is not null:
            SET keep.{field} = discard.{field}

    # Delete the discard node
    DELETE discard_node

    LOG "Auto-merged {discard_node.id} into {keep_node.id} (signal: {match_type})"
```

---

## KEY DECISIONS

### D1: Gemini vs Claude for Entity Extraction

```
CHOICE: Gemini structured output
WHY:    Gemini supports structured output natively (response_schema parameter),
        making entity extraction a single API call with typed responses.
        Claude is the citizen's reasoning engine and should not be used for
        low-level NER tasks. Using a different model for extraction also
        avoids contaminating the citizen's conversation context.
```

### D2: Embedding Match vs String Match for Entity Resolution

```
CHOICE: Embedding similarity as the primary resolution mechanism
WHY:    String matching fails on variations: "Florent Berthet" vs "F. Berthet"
        vs "Florent." Embeddings capture semantic similarity. The tradeoff is
        cost (embedding computation per entity) vs accuracy (catching variations).

        Deterministic signals (platform_id, email, phone) use exact match
        and bypass embedding entirely.
```

### D3: Two Thresholds for Merge Decisions

```
IF similarity > 0.95:
    Auto-match (link to existing node, don't create new)
    WHY: Very high similarity means this is almost certainly the same entity.
         False positive rate is low enough to auto-resolve.

ELIF similarity > 0.85:
    Create new node AND propose merge
    WHY: Moderate similarity could be a match or could be a different entity
         with a similar name. Human review is needed. Creating the new node
         ensures no data is lost if the merge is rejected.

ELSE:
    Create new node, no merge proposal
    WHY: Low similarity means these are likely different entities.
```

### D4: Platform Handles as Fields vs Nodes

```
CHOICE: Fields on Actor node
WHY:    A Telegram ID is not a "thing" — it is a facet of a person's identity.
        Storing it as a field enables simple MATCH queries:
          MATCH (a:Actor {telegram_id: "12345"})
        If it were a separate node, resolving identity would require a join:
          MATCH (a:Actor)-[:HAS_HANDLE]->(h:Handle {platform: "telegram", id: "12345"})
        Fields are simpler, faster, and semantically correct.
```

---

## DATA FLOW

```
Message event (from bridge)
    |
    v
Step 1: Structural enrichment (existing on_message)
    |-- Moment, Actor, Space nodes created
    |-- @mention links created
    |-- L1 stimulus injected
    v
Step 2: Platform handle update
    |-- Author Actor gets platform_id field set
    |-- Check for platform_id collision → auto-merge if found
    v
Step 3: Tier 1 — Pattern extraction
    |-- URLs → Thing(url, confirmed)
    |-- $TOKENS → Thing(token, confirmed)
    |-- @handles (not already in mentions) → Actor match
    v
Step 4: Tier 2 — LLM extraction (Gemini)
    |-- Names → ExtractionResult list
    |-- Filtered by confidence >= 0.6
    v
Step 5: Entity resolution (per extraction)
    |-- Compute embedding
    |-- Query candidates by embedding similarity
    |-- sim > 0.95: link to existing
    |-- sim > 0.85: create + propose merge
    |-- sim < 0.85: create new node
    v
Step 6: Auto-merge (if deterministic signal found)
    |-- Transfer links, merge properties, delete duplicate
    v
Enriched graph
```

---

## COMPLEXITY

**Time:** O(P + L + E*K) per message, where:
- P = pattern extraction: O(n) on text length for regex matching
- L = LLM extraction: O(1) API call but ~200-500ms latency
- E = number of extracted entities, K = candidates per entity for embedding match

For a typical message: P is sub-millisecond, L is ~300ms (Gemini), E*K is ~5*5=25 embedding comparisons (~10ms). Total: ~310ms dominated by the Gemini call.

**Space:** O(E) per message — one node per extracted entity, plus link edges. Nodes are small (a few hundred bytes each). No accumulation concern.

**Bottlenecks:**
- Gemini API latency is the dominant cost. If extraction runs synchronously, it adds ~300ms to every message processing.
- Embedding computation for entity resolution adds ~10ms per entity. For messages mentioning 5+ entities, this accumulates.
- FalkorDB MERGE operations are cheap individually but compound under high message volume.

---

## HELPER FUNCTIONS

### `extract_urls(text: str) -> list[str]`

**Purpose:** Extract all URLs from text using regex.

**Logic:** Match `https?://[^\s<>"')]+`, return unique matches.

### `extract_tokens(text: str) -> list[str]`

**Purpose:** Extract all $TOKEN mentions from text.

**Logic:** Match `\$[A-Z]{2,10}\b`, return unique matches.

### `extract_handles(text: str) -> list[str]`

**Purpose:** Extract all @handles from text that aren't already in the bridge-provided mentioned_handles list.

**Logic:** Match `@[\w-]{2,40}\b`, filter against known mentions, return unique.

### `resolve_entity(name: str, context: str, entity_type: str, graph) -> (node_id, action)`

**Purpose:** Given an extracted entity, determine if it matches an existing node or needs creation.

**Logic:** Compute embedding, query graph by embedding similarity, apply threshold logic, return (node_id, "matched"|"created"|"merge_proposed").

### `auto_merge(keep_id: str, discard_id: str, graph)`

**Purpose:** Merge two nodes that are deterministically the same entity.

**Logic:** Transfer links, merge properties (keep wins), delete discard node.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mcp/tools/graph_write_handler` | `infer_computed_type()` | Computed type string for LINK edges from dimensional properties |
| `scripts/citizen_wake` | `_inject_l1_stimulus()` | L1 stimulus injection for AI citizens in the Space |
| `runtime/economy/trust_propagation` | `propagate_trust()` | Trust EMA update on mention interactions |
| Gemini API | `generate()` with response_schema | Structured entity extraction results |
| FalkorDB | `graph.query()` | Node/link CRUD, embedding similarity search |

---

## MARKERS

<!-- @mind:todo Implement tier 1 pattern extraction (URLs, $tokens) as separate functions -->
<!-- @mind:todo Implement tier 2 Gemini extraction pipeline with structured output -->
<!-- @mind:todo Implement entity resolution with embedding similarity thresholds -->
<!-- @mind:todo Implement auto-merge function for deterministic signals -->
<!-- @mind:escalation Gemini API cost: at 1000 messages/day, extraction costs ~$X/day. Need budget approval. -->
<!-- @mind:proposition Consider batching tier 2 extraction: collect 5-10 messages, extract in one Gemini call -->
