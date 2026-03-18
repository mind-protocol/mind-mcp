# Graph Enricher — Behaviors: Observable Enrichment Effects

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Graph_Enricher.md
THIS:            BEHAVIORS_Graph_Enricher.md (you are here)
PATTERNS:        ./PATTERNS_Graph_Enricher.md
ALGORITHM:       ./ALGORITHM_Graph_Enricher.md
VALIDATION:      ./VALIDATION_Graph_Enricher.md
HEALTH:          ./HEALTH_Graph_Enricher.md
IMPLEMENTATION:  ./IMPLEMENTATION_Graph_Enricher.md
SYNC:            ./SYNC_Graph_Enricher.md

IMPL:            scripts/graph_enricher.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Messages Produce Structural Graph Records

**Why:** Every message event must materialize in the L3 graph as a Moment node linked to its Space (channel) and Actor (author). This is the foundation — without the structural record, no enrichment is possible. This behavior exists today in the current implementation.

```
GIVEN:  A message event arrives from any bridge (Discord, Telegram, WhatsApp)
WHEN:   graph_enricher.on_message() is called
THEN:   A Moment node is created with content, synthesis, timestamp, platform, direction
AND:    A Space node is MERGED for the channel (id: space:{platform}:{channel_id})
AND:    An Actor node is MERGED for the author (id: author_handle or sanitized name)
AND:    LINK(presence) is created/updated from Actor to Space
AND:    LINK(occurred_in) is created from Moment to Space
AND:    LINK(created) is created from Actor to Moment
```

### B2: @Handle Mentions Create Mention Links

**Why:** When a message contains @mentions (as detected by the bridge), the enricher creates LINK(mention) edges from the Moment to each mentioned Actor. This enables the graph to track who is talking about whom. This behavior exists today.

```
GIVEN:  A message event with mentioned_handles = ["@alice", "@bob"]
WHEN:   graph_enricher.on_message() is called
THEN:   For each handle: MERGE Actor node, CREATE LINK(mention) from Moment to Actor
AND:    Mentioned AI citizens in the Space receive L1 stimulus
AND:    Trust propagation fires for each mention (positive interaction signal)
```

### B3: URLs Produce Confirmed Thing Nodes

**Why:** A URL is an unambiguous reference to an external resource. It needs no LLM to recognize and no dedup logic — each unique URL is its own Thing. Extracting URLs ensures the graph captures references to documents, websites, APIs, and tools that citizens discuss.

```
GIVEN:  A Moment's content contains one or more URLs (http://, https://)
WHEN:   The enricher processes the Moment
THEN:   For each unique URL: a Thing node is created with type="url", status="confirmed"
AND:    LINK(mentions) is created from Moment to Thing
AND:    No LLM call is required
```

### B4: $TOKEN Mentions Produce Confirmed Thing Nodes

**Why:** Token mentions ($MIND, $SOL, $ETH) are recognizable by a simple regex pattern. They represent economic entities that should exist as nodes so the graph can track which conversations reference which tokens.

```
GIVEN:  A Moment's content contains "$MIND" or "$SOL" or any $UPPERCASE pattern
WHEN:   The enricher processes the Moment
THEN:   A Thing node is MERGED with type="token", status="confirmed", name=the token symbol
AND:    LINK(mentions) is created from Moment to Thing
```

### B5: Free-Text Names Produce Unconfirmed Actor Nodes

**Why:** When someone writes "I talked to Florent Berthet yesterday," the name "Florent Berthet" refers to a real person who should exist in the graph. The LLM (Gemini structured output) extracts the name with a confidence score and contextual snippet. The extracted entity is matched against existing Actors by embedding similarity. If no match, a new Actor is created with status:unconfirmed.

```
GIVEN:  A Moment's content contains a person's name in free text
WHEN:   Gemini structured output extracts {name: "Florent Berthet", type: "person", confidence: 0.9, context: "from CeSIA"}
THEN:   The name's embedding is computed and compared against existing Actor node embeddings
AND:    IF similarity > merge_threshold: LINK(mentions) is created to the existing Actor
AND:    IF similarity <= merge_threshold: a new Actor node is created (status="unconfirmed", name="Florent Berthet")
AND:    LINK(mentions) is created from Moment to the (matched or new) Actor
```

### B6: Free-Text Places Produce Unconfirmed Space Nodes

**Why:** Place names ("Paris," "the CeSIA office," "Venice") mentioned in text should exist as Space nodes. This enables location-aware context assembly and geographic relationship tracking.

```
GIVEN:  A Moment's content mentions a place
WHEN:   Gemini structured output extracts {name: "CeSIA office", type: "place", confidence: 0.85, context: "in Paris"}
THEN:   The place is matched against existing Space nodes by embedding similarity
AND:    IF match: LINK(mentions) to existing Space
AND:    IF no match: new Space node (status="unconfirmed", name="CeSIA office")
AND:    LINK(mentions) from Moment to Space
```

### B7: Organization and Tool Names Produce Unconfirmed Thing Nodes

**Why:** Organizations (CeSIA, SAS indicators, SARL indicators), tools, and document names represent real-world entities that should exist as nodes. These are typed as Thing with appropriate sub-type metadata.

```
GIVEN:  A Moment's content mentions an organization ("CeSIA"), a tool ("FalkorDB"), or a document
WHEN:   Gemini structured output extracts the entity with type and confidence
THEN:   A Thing node is MERGED or created (status="unconfirmed" for LLM-extracted, "confirmed" for pattern-matched)
AND:    LINK(mentions) from Moment to Thing
```

### B8: Platform Sender ID Updates Actor Node Fields

**Why:** When a bridge delivers a message, it includes the sender's platform-specific ID (e.g., Telegram user_id, Discord user_id). This is ground truth — the platform verified this identity. The enricher writes the platform ID as a field on the Actor node, enabling cross-platform identity resolution.

```
GIVEN:  A message event with platform="telegram" and sender metadata including user_id=12345
WHEN:   The enricher processes the message
THEN:   The Actor node for the author gets telegram_id=12345 set as a field
AND:    If another Actor already has telegram_id=12345, the two Actors are auto-merged
```

### B9: Same Platform ID Triggers Auto-Merge

**Why:** If two Actor nodes have the same telegram_id, they are the same person. This is deterministic and requires no human review. The enricher merges the nodes: the newer node's properties and links are transferred to the older node, and the newer node is deleted.

```
GIVEN:  A new Actor node is created or a platform_id is being set on an Actor
WHEN:   Another Actor node already has the same platform_id for the same platform
THEN:   The two Actor nodes are merged (links transferred, newer node deleted)
AND:    The merge is logged
```

### B10: Similar Embeddings Create Merge Task

**Why:** When a new Actor's name embedding is similar to an existing Actor's embedding but there is no deterministic match (no shared platform_id, email, or phone), the enricher creates a task for human review rather than auto-merging. This prevents false merges of people with similar names.

```
GIVEN:  A new unconfirmed Actor is created with name embedding E_new
WHEN:   An existing Actor has name embedding E_existing with cosine_similarity(E_new, E_existing) > propose_threshold (e.g., 0.85) but < auto_threshold (e.g., 0.95)
THEN:   A merge task is created: "Review: is '{new_name}' the same as '{existing_name}'?"
AND:    The new Actor is NOT merged automatically
AND:    Both Actor nodes remain in the graph until the task is resolved
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1, B2 | O1: Entity extraction | Structural foundation — messages become graph records |
| B3, B4, B5, B6, B7 | O1: Entity extraction | Different entity types extracted from text |
| B9, B10 | O2: Dedup and merge | Same entity under different names resolved |
| B5, B6, B7, B3, B4 | O3: Confidence-aware creation | confirmed vs unconfirmed status tracks certainty |
| B8, B9 | O4: Platform handle aggregation | Platform IDs stored on Actor, cross-platform matching enabled |
| B1, B3, B4 | O5: Minimal latency | Pattern-based extraction is synchronous, LLM extraction is deferred |

---

## INPUTS / OUTPUTS

### Primary Function: `on_message()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| platform | str | "discord", "telegram", "whatsapp" |
| channel_id | str | Platform-specific channel identifier |
| channel_name | str | Human-readable channel name |
| author_name | str | Display name of the message author |
| author_handle | str | Normalized handle (lowercase) |
| content | str | Message text — the raw material for entity extraction |
| mentioned_handles | list[str] | @handles explicitly mentioned (detected by bridge) |
| direction | str | "in" (received) or "out" (sent by citizen) |
| is_pinned | bool | Whether the message is pinned |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| (none) | void | The enricher operates by side effect on the graph |

**Side Effects:**

- Moment, Actor, Space nodes created or updated in FalkorDB
- LINK edges created between nodes
- AI citizens in the Space receive L1 stimulus
- Trust propagation fires for mentions
- (New) Thing nodes created for URLs, tokens, organizations
- (New) Unconfirmed Actor/Space/Thing nodes created from free-text extraction
- (New) Platform handle fields updated on Actor nodes
- (New) Merge tasks created for embedding-similar entities

---

## EDGE CASES

### E1: Message Contains Only a URL

```
GIVEN:  content = "https://arxiv.org/abs/2401.12345"
THEN:   A Thing(type:url, status:confirmed) node is created
AND:    A Moment is created with the URL as content
AND:    No LLM extraction is triggered (no free text to analyze)
```

### E2: Same Name, Different People

```
GIVEN:  "Marie" was previously extracted and exists as an Actor
AND:    A new message mentions a different "Marie"
THEN:   Embedding similarity determines the action:
        IF similar enough: LINK to existing Actor (may be wrong — but merge task catches this)
        IF not similar: create new Actor(name="Marie", status=unconfirmed)
```

### E3: Platform ID Conflict During Merge

```
GIVEN:  Actor A has telegram_id=111 and discord_id=222
AND:    Actor B has telegram_id=111 and discord_id=333
THEN:   telegram_id match triggers auto-merge
AND:    The merged Actor gets BOTH discord_id values (222 and 333) logged as potential conflict
AND:    A task is created to resolve the discord_id conflict
```

### E4: Empty Content Message

```
GIVEN:  content = "" (e.g., an image-only message)
THEN:   The structural Moment/Actor/Space nodes are still created
AND:    No entity extraction is attempted (no text to analyze)
AND:    Tier 1 pattern matching finds nothing, tier 2 is not called
```

---

## ANTI-BEHAVIORS

### A1: Ghost Node Proliferation

```
GIVEN:   The same person is mentioned 10 times under the same name
WHEN:    The enricher processes each mention
MUST NOT: Create 10 separate Actor nodes
INSTEAD:  The first mention creates the Actor; subsequent mentions link to the existing node via embedding match
```

### A2: False Auto-Merge on Similar Names

```
GIVEN:   Two different people share a similar name ("Jean Martin" and "Jean-Martin Dupont")
WHEN:    The enricher extracts both names
MUST NOT: Auto-merge them based on name embedding similarity alone
INSTEAD:  Create separate unconfirmed Actors and propose a merge task if similarity exceeds threshold
```

### A3: LLM Extraction Blocking the Write Path

```
GIVEN:   A message arrives and needs Gemini extraction
WHEN:    The Gemini API is slow (>2s response)
MUST NOT: Block the on_message() call, delaying bridge processing
INSTEAD:  Tier 1 patterns are extracted synchronously; tier 2 LLM extraction runs after the structural enrichment completes
```

### A4: Platform Handle Stored as Separate Node

```
GIVEN:   A Telegram sender_id is available from bridge metadata
WHEN:    The enricher processes the message
MUST NOT: Create a separate Thing or Actor node for the Telegram ID
INSTEAD:  Store telegram_id as a field on the author's Actor node
```

---

## MARKERS

<!-- @mind:todo Implement B3 (URL extraction) — regex + Thing node creation -->
<!-- @mind:todo Implement B4 ($TOKEN extraction) — regex + Thing node creation -->
<!-- @mind:todo Implement B5-B7 (free-text extraction via Gemini) -->
<!-- @mind:todo Implement B8 (platform handle field updates) -->
<!-- @mind:todo Implement B9 (auto-merge on platform_id) -->
<!-- @mind:todo Implement B10 (merge task creation on embedding similarity) -->
