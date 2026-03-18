# Cluster Write — Behaviors: Observable Effects of Atomic Moment Creation

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
THIS:            BEHAVIORS_Cluster_Write.md (you are here)
PATTERNS:        ./PATTERNS_Cluster_Write.md
ALGORITHM:       ./ALGORITHM_Cluster_Write.md
VALIDATION:      ./VALIDATION_Cluster_Write.md
HEALTH:          ./HEALTH_Cluster_Write.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cluster_Write.md
SYNC:            ./SYNC_Cluster_Write.md

IMPL:            mcp/tools/cluster_write_handler.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Single Call Produces Complete Cluster

**Why:** graph_write requires N calls for N nodes. A meeting with 3 people at a location requires 7+ calls plus manual link creation. This is fragile (partial writes), tedious (manual entity resolution), and lossy (entities in content go unlinked). A single call that produces the entire cluster eliminates all three problems.

```
GIVEN:  citizen calls cluster_write with content describing an event
WHEN:   the tool completes successfully
THEN:   the graph contains: 1 Moment node, 1 Space node (matched or created),
        N Actor nodes (matched or created), M Thing nodes (matched or created),
        and all links between them — Moment→Space (occurred_in), Moment→Actor (mention),
        Actor→Moment (created for the calling citizen), Moment→Thing (relates)
AND:    the response contains the full cluster summary for citizen review
```

### B2: Platform-Verified Entities Get Confirmed Status

**Why:** When a Moment originates from Telegram, Discord, X, or email, the sender's identity is platform-verified. The platform has already authenticated this person. Treating them as unconfirmed would lose valuable ground truth.

```
GIVEN:  cluster_write receives platform metadata (e.g., telegram_user_id, discord_snowflake)
WHEN:   the tool resolves the entity against the graph
THEN:   if a matching actor exists with the same platform_id: auto-merge (no duplicate created)
AND:    the link from Moment to Actor has status:confirmed and full weight (1.0)
AND:    if no matching actor exists: a new actor is created with the platform_id stored
```

### B3: Text-Mention Entities Get Unconfirmed Status

**Why:** When content says "met my friend Florent", we know there is a person named Florent but we do not know which Florent in the graph (if any). The link should exist (it is real information) but at reduced confidence. The physics will either reinforce it (co-activation) or prune it (forgetting).

```
GIVEN:  Gemini extracts a name from content text (not from platform metadata)
WHEN:   the tool creates an actor for this name
THEN:   the actor is created with status:unconfirmed
AND:    the link from Moment to Actor has reduced weight (0.5)
AND:    if a likely match exists in the graph (embedding similarity > threshold),
        the suggestion includes the match with context: "Is this @florent-berthet? (SID: ..., last active: ...)"
```

### B4: Pre-Computed Context Improves Entity Matching

**Why:** The citizen's recent context (active spaces, recent actors, known things) provides strong priors for entity resolution. "Florent" in a conversation about CeSIA has one obvious candidate. Without context, the system would have to guess among all Florents in the graph.

```
GIVEN:  a citizen with active spaces, recent interactions, and known things in their graph
WHEN:   cluster_write begins processing
THEN:   the pre-compute phase loads: current space (from citizen's most recent space link),
        recent actors (last 50 interaction links), known things (recently referenced)
AND:    entity matching uses this context to boost match scores for contextually relevant entities
```

### B5: Gemini Extracts Entities from Content

**Why:** Citizens write natural language. They should not have to manually tag entities. "Had coffee with Florent at Cafe de Flore, we discussed the cesai.org/paper.pdf" contains 1 person, 1 place, and 1 URL — all extractable by LLM analysis.

```
GIVEN:  cluster_write receives content text
WHEN:   the analyze phase runs
THEN:   Gemini returns structured extraction:
        names → Actor candidates,
        places → Space candidates,
        URLs → Thing auto-create (confirmed),
        @handles → Actor match (confirmed if handle exists in graph),
        $tokens → Thing candidates
```

### B6: Citizen Reviews Suggestions Before Write

**Why:** Auto-merging on uncertain matches would create false connections. The citizen needs enough context to make a fast decision: "Yes, that is the right Florent" or "No, this is someone new."

```
GIVEN:  the analyze phase has produced entity candidates with varying confidence
WHEN:   the suggest phase runs
THEN:   the tool returns a structured suggestion list:
        each entity shows: extracted text, proposed match (if any), match confidence,
        match context (SID, handle, last activity), and proposed status (confirmed/unconfirmed)
AND:    the citizen can accept all, reject specific matches, or override matches
```

### B7: URLs Auto-Create Thing Nodes

**Why:** A URL is a concrete, unambiguous reference. There is no identity resolution needed — the URL is the identity. Creating a Thing for it immediately is always correct.

```
GIVEN:  Gemini extracts a URL from content
WHEN:   the tool processes URL entities
THEN:   a Thing node is created with id="thing:url:{domain}:{path_hash}",
        the URL stored in content, status:confirmed
AND:    the link from Moment to Thing has full weight (1.0)
AND:    if a Thing with the same URL already exists, it is reused (no duplicate)
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Atomic cluster creation | Eliminates partial writes and manual multi-call sequences |
| B2 | Identity resolution at write time | Platform ground truth is never lost |
| B3 | Confidence-graded links | Text mentions are recorded without over-claiming certainty |
| B4 | Intelligent content analysis | Context makes matching accurate, not just possible |
| B5 | Intelligent content analysis | Natural language in, structured graph out |
| B6 | Citizen-in-the-loop suggestions | Human judgment where it matters, automation where it is safe |
| B7 | Atomic cluster creation | URLs are unambiguous — zero friction |

---

## INPUTS / OUTPUTS

### Primary Function: `handle_cluster_write()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | string | Natural language description of the moment/event |
| `space` | string (optional) | Explicit space ID. If omitted, uses citizen's current space |
| `actors` | list[dict] (optional) | Explicit actor references with platform metadata |
| `things` | list[dict] (optional) | Explicit thing references |
| `platform` | dict (optional) | Platform metadata: source (telegram/discord/x/email), message_id, sender_id, channel_id |
| `confirm` | bool | If true, skip suggestion phase and write immediately. Default: false |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `cluster` | dict | The full cluster: moment_id, space_id, actor_ids, thing_ids, link_ids, suggestion list (if confirm=false) |

**Side Effects:**

- Creates nodes in the FalkorDB graph (Moment, Space, Actor, Thing)
- Creates links between all cluster nodes with dimensional properties
- Calls Gemini API for content analysis (one API call per cluster_write)
- Reads existing graph state for entity matching (pre-compute phase)

---

## EDGE CASES

### E1: Empty Content

```
GIVEN:  cluster_write is called with empty or whitespace-only content
THEN:   return error: "content is required — describe what happened"
```

### E2: No Entities Extracted

```
GIVEN:  Gemini analysis finds no names, places, URLs, handles, or tokens in content
THEN:   create a Moment node with the content, linked to the citizen (created) and their current space (occurred_in)
AND:    return the minimal cluster (Moment + Space + caller Actor)
```

### E3: Gemini API Failure

```
GIVEN:  the Gemini API call fails (timeout, rate limit, error)
THEN:   fall back to regex-based extraction: URLs via URL regex, @handles via @\w+ regex, $tokens via \$\w+ regex
AND:    log a warning: "Gemini analysis failed, using regex fallback"
AND:    text-mention names are NOT extracted (no regex can reliably extract names from prose)
```

### E4: Ambiguous Actor Match

```
GIVEN:  a text-mention name matches multiple existing actors with similar confidence
THEN:   present all candidates in the suggestion list, ranked by match score
AND:    do not auto-merge any of them — the citizen decides
```

### E5: Confirmed and Unconfirmed References to Same Actor

```
GIVEN:  platform metadata confirms actor A, and text content also mentions actor A by name
THEN:   the confirmed identification wins — the link is status:confirmed with full weight
AND:    the text mention is silently absorbed (no duplicate link)
```

---

## ANTI-BEHAVIORS

### A1: Silent Entity Dropping

```
GIVEN:   Gemini extracts an entity from content
WHEN:    the entity cannot be matched to any existing actor
MUST NOT: silently drop the entity
INSTEAD:  create an unconfirmed actor with the extracted name, linked with reduced weight
```

### A2: False Auto-Merge on Name Similarity

```
GIVEN:   a text-mention name is similar to an existing actor (embedding similarity)
WHEN:    the similarity is above threshold but below certainty
MUST NOT: auto-merge the text mention with the existing actor
INSTEAD:  present the match as a suggestion for citizen review
```

### A3: Partial Cluster Write

```
GIVEN:   a cluster_write operation is in progress
WHEN:    any node or link creation fails mid-cluster
MUST NOT: leave the partially-written nodes in the graph
INSTEAD:  roll back all created nodes and links, return error with details
```

### A4: Duplicate Platform-Verified Actors

```
GIVEN:   an actor with telegram_user_id=12345 already exists in the graph
WHEN:    a new cluster_write arrives with the same telegram_user_id
MUST NOT: create a second actor node for the same platform identity
INSTEAD:  reuse the existing actor, update recency on the link
```

---

## MARKERS

<!-- @mind:todo Define the exact embedding similarity threshold for "suggest merge" vs "create new" -->
<!-- @mind:todo Design the suggestion response format (JSON structure for citizen review) -->
<!-- @mind:escalation Should the regex fallback (E3) be silent or should it be surfaced to the citizen? -->
