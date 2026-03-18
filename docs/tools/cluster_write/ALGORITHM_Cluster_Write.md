# Cluster Write — Algorithm: Pre-compute, Analyze, Suggest, Write Pipeline

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
BEHAVIORS:       ./BEHAVIORS_Cluster_Write.md
PATTERNS:        ./PATTERNS_Cluster_Write.md
THIS:            ALGORITHM_Cluster_Write.md (you are here)
VALIDATION:      ./VALIDATION_Cluster_Write.md
HEALTH:          ./HEALTH_Cluster_Write.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cluster_Write.md
SYNC:            ./SYNC_Cluster_Write.md

IMPL:            mcp/tools/cluster_write_handler.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Cluster write transforms natural language content into a complete, linked graph cluster through a four-phase pipeline: Pre-compute, Analyze, Suggest, Write. Each phase feeds the next — context informs analysis, analysis produces candidates, candidates become suggestions, suggestions become graph writes. The pipeline is designed so that confidence flows forward: platform-verified data enters at full confidence and stays there; text mentions enter at low confidence and may be upgraded by citizen confirmation.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Atomic cluster creation | B1, B7 | The write phase creates all nodes and links in one logical operation |
| Identity resolution at write time | B2, B3, B4 | Pre-compute + analyze phases resolve entities before any writes happen |
| Intelligent content analysis | B4, B5 | Gemini analysis with pre-computed context extracts entities accurately |
| Confidence-graded links | B2, B3 | Each entity carries a source-derived confidence that maps to link weight |
| Citizen-in-the-loop suggestions | B6 | Suggest phase presents candidates with enough context for fast decisions |

---

## DATA STRUCTURES

### ClusterInput

```
ClusterInput:
  content:     string         # Natural language description of the event
  space:       string | null  # Explicit space ID, or null (use citizen's current space)
  actors:      list[ActorRef] # Explicit actor references (from platform metadata)
  things:      list[ThingRef] # Explicit thing references
  platform:    PlatformMeta   # Platform source metadata (if from a platform message)
  confirm:     bool           # Skip suggestion phase, write immediately
```

### ActorRef

```
ActorRef:
  name:         string         # Display name
  platform_id:  string | null  # Platform-specific ID (telegram_user_id, discord_snowflake)
  platform:     string | null  # Platform name (telegram, discord, x, email, phone)
  handle:       string | null  # @handle if known
  email:        string | null  # Email if known
  phone:        string | null  # Phone if known
```

### EntityCandidate

```
EntityCandidate:
  extracted_text:  string                    # The text that triggered this candidate
  entity_type:     actor | space | thing     # What kind of entity
  source:          platform | text | url | handle | token  # How it was identified
  status:          confirmed | unconfirmed   # Confidence level
  match:           ExistingMatch | null      # Matched existing entity, if any
  proposed_id:     string                    # ID to use if creating new
  proposed_name:   string                    # Name to use
  link_weight:     float                     # Initial link weight (1.0 confirmed, 0.5 unconfirmed)
```

### ExistingMatch

```
ExistingMatch:
  node_id:       string   # Existing node's graph ID
  name:          string   # Existing node's display name
  handle:        string   # @handle if actor
  sid:           string   # Sovereign ID if actor
  last_active:   string   # Human-readable last activity
  match_method:  string   # How matched: platform_id | email | phone | embedding | handle
  match_score:   float    # Confidence of match (1.0 = exact platform match, 0.0-0.99 = similarity)
```

### Cluster (output)

```
Cluster:
  moment_id:    string                    # Created moment node ID
  space_id:     string                    # Space node ID (created or matched)
  actor_ids:    list[string]              # Actor node IDs (created or matched)
  thing_ids:    list[string]              # Thing node IDs (created or matched)
  links:        list[LinkRecord]          # All links created
  suggestions:  list[EntityCandidate]     # For citizen review (only if confirm=false)
```

### CitizenContext (pre-computed)

```
CitizenContext:
  citizen_id:     string          # Calling citizen's actor ID
  citizen_sid:    string          # Calling citizen's SID
  current_space:  string | null   # Citizen's most recent space link
  recent_actors:  list[ActorSummary]  # Last 50 actors interacted with (id, name, handle, sid, recency)
  known_things:   list[ThingSummary]  # Recently referenced things (id, name, type, recency)
```

---

## ALGORITHM: handle_cluster_write()

### Phase 1: Pre-compute Context

**What happens:** Before analyzing any content, load the citizen's current graph context. This context serves as a prior for entity matching in Phase 2 — it narrows the search space and boosts match confidence for contextually relevant entities.

```
1. Resolve caller identity
   caller_id = resolve_actor_id(ctx)
   caller_sid = lookup_sid(caller_id)

2. Load current space
   current_space = query: MATCH (a {id: caller_id})-[r:LINK]->(s)
                          WHERE s.node_type = 'space'
                          ORDER BY r.recency DESC LIMIT 1
                          RETURN s.id

3. Load recent actors (last 50 interactions)
   recent_actors = query: MATCH (a {id: caller_id})-[r:LINK]-(b)
                          WHERE b.node_type = 'actor' AND b.id <> caller_id
                          ORDER BY r.recency DESC LIMIT 50
                          RETURN b.id, b.name, b.sid, b.handle, r.recency

4. Load known things (last 30 referenced)
   known_things = query: MATCH (a {id: caller_id})-[r:LINK]-(t)
                         WHERE t.node_type = 'thing'
                         ORDER BY r.recency DESC LIMIT 30
                         RETURN t.id, t.name, t.type, r.recency

5. Assemble CitizenContext
   context = CitizenContext(caller_id, caller_sid, current_space, recent_actors, known_things)
```

**Why this phase exists:** Entity matching without context is a cold search across the entire graph. With context, "Florent" immediately finds the Florent Berthet that the citizen interacted with 2 days ago, rather than requiring an expensive full-graph embedding search.

### Phase 2: Analyze Content

**What happens:** Extract entities from the content using two parallel paths: (a) platform metadata (if present) provides confirmed entities, (b) Gemini analyzes the text for unconfirmed entities. Then resolve each extracted entity against the graph.

```
1. Extract platform-verified entities (if platform metadata provided)
   For each actor in args.actors:
     if actor.platform_id:
       match = query: MATCH (a) WHERE a.{platform}_id = actor.platform_id RETURN a
       if match:
         candidate = EntityCandidate(source=platform, status=confirmed, match=match, link_weight=1.0)
       else:
         candidate = EntityCandidate(source=platform, status=confirmed, match=null, link_weight=1.0)
     if actor.email:
       match = query: MATCH (a) WHERE a.email = actor.email RETURN a
       ... (same pattern)
     if actor.phone:
       match = query: MATCH (a) WHERE a.phone = actor.phone RETURN a
       ... (same pattern)

2. Extract text entities via Gemini
   prompt = build_extraction_prompt(content, context.recent_actors)
   response = think(message=prompt, system_prompt=EXTRACTION_SYSTEM_PROMPT, json_mode=true)
   gemini_entities = parse_extraction_response(response)

   Gemini returns:
   {
     "actors": [{"name": "Florent", "context_clue": "discussed CeSIA paper"}],
     "spaces": [{"name": "Cafe de Flore", "context_clue": "location of meeting"}],
     "urls": ["https://cesai.org/paper.pdf"],
     "handles": ["@florent-berthet"],
     "tokens": ["$MIND"]
   }

3. Extract regex entities (always, as supplement to Gemini)
   urls = regex_extract_urls(content)         # URL regex
   handles = regex_extract_handles(content)   # @\w+ pattern
   tokens = regex_extract_tokens(content)     # \$\w+ pattern

4. Merge Gemini + regex extractions (deduplicate)
   all_urls = unique(gemini_entities.urls + urls)
   all_handles = unique(gemini_entities.handles + handles)
   all_tokens = unique(gemini_entities.tokens + tokens)

5. Resolve each extracted entity against the graph

   For each actor name from Gemini:
     a. Check context.recent_actors for name match (case-insensitive partial)
        if match with high confidence: EntityCandidate(source=text, status=unconfirmed, match=match, link_weight=0.5)
     b. Check graph for handle match
        query: MATCH (a) WHERE a.node_type='actor' AND toLower(a.name) CONTAINS toLower(name)
     c. Embedding similarity search
        embed = embed_service.embed(name + " " + context_clue)
        knn = graph_ops.knn_search("actor", embed, top_k=3)
        if best_match.score > SIMILARITY_THRESHOLD:
          EntityCandidate(source=text, status=unconfirmed, match=best_match, link_weight=0.5)
        else:
          EntityCandidate(source=text, status=unconfirmed, match=null, link_weight=0.5)

   For each @handle:
     query: MATCH (a) WHERE a.handle = handle OR a.id = handle
     if match: EntityCandidate(source=handle, status=confirmed, match=match, link_weight=1.0)
     else: EntityCandidate(source=handle, status=unconfirmed, match=null, link_weight=0.5)

   For each URL:
     url_hash = sha256(url)[:12]
     domain = extract_domain(url)
     proposed_id = f"thing:url:{domain}:{url_hash}"
     match = query: MATCH (t {id: proposed_id}) RETURN t
     EntityCandidate(source=url, status=confirmed, match=match, link_weight=1.0)

   For each $token:
     proposed_id = f"thing:token:{token.lower()}"
     match = query: MATCH (t {id: proposed_id}) RETURN t
     EntityCandidate(source=token, status=confirmed if match else unconfirmed, link_weight=1.0 if match else 0.7)

   For each space name from Gemini:
     embed = embed_service.embed(space_name)
     knn = graph_ops.knn_search("space", embed, top_k=3)
     if best_match.score > SPACE_SIMILARITY_THRESHOLD:
       EntityCandidate(source=text, status=unconfirmed, match=best_match, link_weight=0.5)
     else:
       EntityCandidate(source=text, status=unconfirmed, match=null, link_weight=0.5)
```

**Why this phase exists:** This is where raw content transforms into structured entity candidates with confidence levels. The dual-path approach (platform + Gemini) ensures that verified data is never degraded and that unverified data is still captured.

### Phase 3: Suggest

**What happens:** If `confirm=false` (default), present the extracted entities with their matches and confidence for citizen review. If `confirm=true`, skip this phase entirely.

```
1. Build suggestion list
   suggestions = []
   for each EntityCandidate:
     suggestion = {
       "extracted_text": candidate.extracted_text,
       "type": candidate.entity_type,
       "source": candidate.source,
       "status": candidate.status,
       "proposed_action": "match_existing" if candidate.match else "create_new",
     }
     if candidate.match:
       suggestion["match"] = {
         "id": candidate.match.node_id,
         "name": candidate.match.name,
         "handle": candidate.match.handle,
         "sid": candidate.match.sid,
         "last_active": candidate.match.last_active,
         "method": candidate.match.match_method,
         "score": candidate.match.match_score,
       }
     suggestions.append(suggestion)

2. Return suggestions
   return {
     "phase": "suggest",
     "moment_preview": {
       "content": content[:200],
       "space": space_id or context.current_space,
     },
     "entities": suggestions,
     "instructions": "Review entities. Call cluster_write again with confirm=true and any adjustments.",
   }
```

**Why this phase exists:** Auto-merging on uncertain matches creates false connections that are hard to undo. Showing the citizen "Is this @florent-berthet? (last seen 2 days ago in #primers)" takes 2 seconds to confirm and prevents graph pollution.

### Phase 4: Write Cluster

**What happens:** Create all nodes and links atomically. This phase only runs when `confirm=true` or when all entities are confirmed (no suggestions needed).

```
1. Create the Moment node
   moment_id = f"moment:{caller_id}:{hash(content)[:8]}"
   graph_ops.add_moment(id=moment_id, text=content, type="event", weight=1.0, embedding=embed(content))

2. Resolve or create the Space
   if explicit space provided:
     space_id = args.space
   else:
     space_id = context.current_space or f"space:{caller_id}:default"
   ensure_node_exists(space_id, node_type="space")

3. Create Moment→Space link (occurred_in)
   create_link(moment_id, space_id,
     dims={hierarchy: 1.0, polarity: 1.0},
     source_label="moment", target_label="space")

4. Create caller→Moment link (created)
   create_link(caller_id, moment_id,
     dims={hierarchy: -1.0, permanence: 1.0, polarity: 1.0},
     tag="CREATED",
     source_label="actor", target_label="moment")

5. For each Actor candidate:
   if candidate.match and candidate.status == "confirmed":
     actor_id = candidate.match.node_id     # Reuse existing
   elif candidate.match and citizen confirmed the match:
     actor_id = candidate.match.node_id     # Citizen confirmed
   else:
     actor_id = generate_actor_id(candidate)
     graph_ops.add_character(id=actor_id, name=candidate.proposed_name,
                             type="person", weight=0.5, embedding=embed(candidate.proposed_name))
     if candidate has platform_id:
       set_property(actor_id, f"{candidate.platform}_id", candidate.platform_id)
     if candidate has email:
       set_property(actor_id, "email", candidate.email)

   # Create Moment→Actor link (mention)
   create_link(moment_id, actor_id,
     dims={polarity: 0.5, recency: now()},
     weight_override=candidate.link_weight,     # 1.0 confirmed, 0.5 unconfirmed
     source_label="moment", target_label="actor")

   # If actor has status:unconfirmed, tag the node
   if candidate.status == "unconfirmed":
     set_property(actor_id, "status", "unconfirmed")

6. For each Thing candidate:
   if candidate.match:
     thing_id = candidate.match.node_id
   else:
     thing_id = candidate.proposed_id
     graph_ops.add_thing(id=thing_id, name=candidate.proposed_name,
                         type=infer_thing_type(candidate), weight=1.0,
                         embedding=embed(candidate.proposed_name))
     if candidate.source == "url":
       set_property(thing_id, "url", candidate.extracted_text)

   # Create Moment→Thing link (relates)
   create_link(moment_id, thing_id,
     dims={recency: now(), polarity: 0.5},
     weight_override=candidate.link_weight,
     source_label="moment", target_label="thing")

7. For each Space candidate (beyond the primary space):
   # Additional spaces mentioned in content
   if candidate.match:
     extra_space_id = candidate.match.node_id
   else:
     extra_space_id = candidate.proposed_id
     ensure_node_exists(extra_space_id, node_type="space", name=candidate.proposed_name)

   create_link(moment_id, extra_space_id,
     dims={hierarchy: 1.0, polarity: 0.5},
     weight_override=candidate.link_weight,
     source_label="moment", target_label="space")

8. Return the complete Cluster
   return Cluster(moment_id, space_id, actor_ids, thing_ids, links, suggestions=[])
```

**Why this phase exists:** All the analysis and resolution in phases 1-3 culminates in a single atomic write. Every node and link is created together, so the graph is never in a half-formed state.

---

## KEY DECISIONS

### D1: Platform Match — Auto-Merge or Create New?

```
IF platform_id matches an existing actor:
    Auto-merge: reuse the existing actor node, update recency.
    Why: Platform verification is ground truth. Two messages from the same
    telegram_user_id are definitionally the same person.
ELSE:
    Create new actor with platform_id stored.
    Why: First encounter — the actor needs to exist in the graph.
```

### D2: Text-Mention Match — Auto-Merge or Suggest?

```
IF embedding similarity > 0.92 AND name is exact case-insensitive match:
    Auto-merge: the evidence is strong enough.
    Why: "florent" matching actor "Florent Berthet" with 0.95 similarity
    in the citizen's recent context is beyond reasonable doubt.
ELIF embedding similarity > 0.75:
    Suggest: present match to citizen for confirmation.
    Why: "Flo" might be Florent or Florence. Let the citizen decide.
ELSE:
    Create new unconfirmed actor.
    Why: No reasonable match found. Better to create a new node
    than to force a false merge.
```

### D3: Gemini Fails — What Happens?

```
IF Gemini API call fails (timeout, error, rate limit):
    Fall back to regex-only extraction.
    Extract: URLs, @handles, $tokens (all structurally unambiguous).
    Do NOT extract: names, places (require NLU, regex is unreliable).
    Log warning.
    Why: The moment should still be created with whatever entities
    can be reliably extracted. Names require LLM analysis — guessing
    with regex is worse than not extracting.
```

### D4: Confirm=true vs Confirm=false

```
IF confirm=true:
    Skip Phase 3 (Suggest). Go directly to Phase 4 (Write).
    All unconfirmed entities are written as-is with reduced weight.
    Why: The citizen has already reviewed (from a previous suggest call)
    or explicitly wants fast writing without review.
ELSE (confirm=false, the default):
    Return after Phase 3 with suggestions.
    The citizen reviews and calls again with confirm=true.
    Why: Identity resolution benefits from human judgment.
    The cost is one extra tool call, the benefit is graph accuracy.
```

### D5: Same Entity from Platform AND Text

```
IF an entity appears in both platform metadata (confirmed) AND text content:
    The confirmed version wins. Only one EntityCandidate is produced.
    The link is status:confirmed with full weight.
    Why: Platform verification supersedes text analysis.
    Creating two candidates for the same entity would produce
    duplicate links or confusing suggestions.
```

---

## DATA FLOW

```
ClusterInput (content, platform metadata, explicit actors/things)
    |
    v
Phase 1: PRE-COMPUTE
    Read citizen's graph context (spaces, actors, things)
    → CitizenContext
    |
    v
Phase 2: ANALYZE
    Platform metadata → confirmed EntityCandidates
    Gemini analysis → actor/space/URL/handle/token extractions
    Regex extraction → URLs, @handles, $tokens (supplementary)
    Entity resolution → match each extraction against graph
    → list[EntityCandidate]
    |
    v
Phase 3: SUGGEST (if confirm=false)
    Build suggestion list with match context
    → Return suggestions to citizen
    (citizen reviews, calls again with confirm=true)
    |
    v
Phase 4: WRITE (if confirm=true or all entities confirmed)
    Create Moment node
    Resolve/create Space node
    Create caller→Moment CREATED link
    For each actor: resolve/create, link Moment→Actor
    For each thing: resolve/create, link Moment→Thing
    For each extra space: resolve/create, link Moment→Space
    → Return complete Cluster
```

---

## COMPLEXITY

**Time:** O(A + T + G) where A = number of actors to resolve, T = number of things, G = Gemini API latency (~500ms-2s)

The dominant cost is the Gemini API call (Phase 2). Graph queries for entity resolution are fast (KNN search is O(log N) per query against FalkorDB's vector index). Node creation is O(1) per node.

**Space:** O(C) where C = size of CitizenContext (bounded: 50 recent actors + 30 recent things)

**Bottlenecks:**
- Gemini API latency (500ms-2s) — mitigated by the regex fallback path
- KNN vector search for embedding similarity — mitigated by searching only within node type + context
- Multiple graph writes in Phase 4 — mitigated by FalkorDB's in-process architecture (no network round-trips)

---

## HELPER FUNCTIONS

### `build_extraction_prompt(content, recent_actors)`

**Purpose:** Construct the Gemini prompt that extracts entities from content, with recent actors listed so Gemini can match names to known people.

**Logic:** System prompt defines the extraction schema (JSON output). The user message includes the content text and a list of recent actor names/handles as context. Gemini returns structured JSON with actors, spaces, URLs, handles, tokens.

### `resolve_entity_against_graph(entity, entity_type, context, graph_ops, embed_service)`

**Purpose:** Take an extracted entity (name, URL, handle, token) and find the best match in the existing graph.

**Logic:** Ordered resolution: (1) platform_id exact match, (2) email/phone exact match, (3) handle exact match, (4) name match in recent context, (5) embedding similarity KNN search. Returns ExistingMatch or null.

### `create_link(source, target, dims, tag, source_label, target_label, weight_override)`

**Purpose:** Create a :LINK edge with dimensional properties and computed_type, reusing the pattern from graph_write_handler.

**Logic:** Calls infer_computed_type() from graph_write_handler, sets dimensional properties, optionally sets r.type tag. Weight_override allows setting the link weight independent of dimensions (for confidence grading).

### `ensure_node_exists(node_id, node_type, name)`

**Purpose:** MERGE a node if it does not exist, without overwriting if it does.

**Logic:** `MERGE (n {id: $id}) ON CREATE SET n.node_type = $type, n.name = $name`

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mcp/tools/think_handler.py` | `handle_think()` with extraction prompt | Structured JSON: actors, spaces, URLs, handles, tokens |
| `runtime/physics/graph/GraphOps` | `add_moment()`, `add_character()`, `add_thing()`, `_query()`, KNN search | Node creation, link creation, entity matching |
| `runtime/infrastructure/embeddings/service` | `embed()` | Vector embeddings for synthesis and entity similarity |
| `runtime/identity.py` | `resolve_actor_id()` | Calling citizen's actor ID |
| `mcp/tools/graph_write_handler.py` | `infer_computed_type()` | Computed link type from dimensional signatures |

---

## MARKERS

<!-- @mind:todo Define EXTRACTION_SYSTEM_PROMPT for Gemini — must produce valid JSON with actors/spaces/urls/handles/tokens -->
<!-- @mind:todo Define SIMILARITY_THRESHOLD and SPACE_SIMILARITY_THRESHOLD values (design decision, needs testing) -->
<!-- @mind:todo Design the exact Gemini prompt that includes recent actor context for better name matching -->
<!-- @mind:proposition Consider a "learn" mode where the citizen can correct entity extraction and the corrections feed back into prompt tuning -->
<!-- @mind:escalation Should Phase 4 use a FalkorDB transaction for true atomicity, or is sequential-with-cleanup sufficient? -->
