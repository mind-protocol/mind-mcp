# Cluster Write — Patterns: Atomic Moment Clusters with Identity Resolution

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
THIS:            PATTERNS_Cluster_Write.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Cluster_Write.md
ALGORITHM:       ./ALGORITHM_Cluster_Write.md
VALIDATION:      ./VALIDATION_Cluster_Write.md
HEALTH:          ./HEALTH_Cluster_Write.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cluster_Write.md
SYNC:            ./SYNC_Cluster_Write.md

IMPL:            mcp/tools/cluster_write_handler.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read mcp/tools/cluster_write_handler.py

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Cluster_Write.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Cluster_Write.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

graph_write creates one node at a time. A citizen who had a meeting with three people at a specific place, discussing a document with a URL, must call graph_write 7+ times (1 moment + 1 space + 3 actors + 1 thing + 1 URL thing) and manually create every link between them. This is:

1. **Fragile** — If any call fails mid-sequence, the graph has orphaned nodes with missing links. There is no transactional boundary.
2. **Tedious** — The citizen must manually identify which actors already exist, resolve handles, decide on IDs. Every interaction becomes a data-entry exercise.
3. **Lossy** — The citizen must manually extract entities from their own content. "Had coffee with Florent" should automatically produce an Actor candidate for Florent; today it produces nothing unless the citizen explicitly calls graph_write for Florent.
4. **Context-blind** — graph_write has no knowledge of who exists in the graph, where the citizen currently is, or what actors they recently interacted with. Every write starts from zero.

---

## THE PATTERN

**Pre-compute → Analyze → Suggest → Write.** A four-phase pipeline that transforms raw citizen content into a complete, linked graph cluster.

The key insight: **identity resolution is a write-time concern, not a post-processing step.** When a citizen mentions "Florent", the system should immediately check: does an actor with that name exist? Is there a platform-verified match? Is there an embedding-similar actor? This happens before a single node is created, so the cluster is born correct.

The second insight: **confidence is dimensional, not binary.** A Telegram message from user_id=12345 produces a confirmed actor link because the platform verified the identity. A text mention "my friend Florent" produces an unconfirmed actor link with lower weight. Both are valid — they just start at different points on the trust/weight spectrum. The physics (L5/L6/L7) handles convergence over time.

The third insight: **the citizen's current context is free information.** Before analyzing content, we already know: which space the citizen is in, which actors they recently interacted with, which things they recently referenced. This pre-computed context makes entity matching vastly more accurate — "Florent" in a conversation about CeSIA is almost certainly Florent Berthet, not some other Florent.

---

## BEHAVIORS SUPPORTED

- B1: Single call produces complete cluster — Moment + Space + Actors + Things + links
- B2: Platform-verified entities get confirmed status — auto-merge on matching platform_id
- B3: Text-mention entities get unconfirmed status — lower link weight, physics evolves
- B4: Pre-computed context improves entity matching — recent actors, current space
- B5: Gemini extracts entities from content — names, places, URLs, handles, tokens
- B6: Citizen reviews suggestions before write — enough context to decide without re-searching
- B7: URLs auto-create Thing nodes — confirmed status, no citizen action needed

## BEHAVIORS PREVENTED

- Orphaned nodes from partial writes — the cluster is atomic
- Duplicate actors from platform-verified sources — platform_id dedup is automatic
- Silent entity extraction failures — unrecognized entities surface as unconfirmed, never silently dropped
- Manual entity tagging — the citizen writes natural language, the tool does extraction

---

## PRINCIPLES

### Principle 1: Platform Truth Over Text Guessing

When an entity comes from a platform (Telegram sender_id, Discord snowflake, X user_id, email address, phone number), it is treated as ground truth. The identity is confirmed, the link weight is full, dedup is automatic (same platform_id = same actor). When an entity comes from text analysis ("my friend Florent"), it is treated as a hypothesis. The identity is unconfirmed, the link weight is reduced, and the citizen is asked to confirm.

This is not a quality judgment — both sources are valuable. But they carry different epistemic weight, and the graph should reflect that.

### Principle 2: Context Narrows the Search Space

Before analyzing content, the system pre-computes the citizen's context: active spaces, recent actors (last 50 interactions), known things. This context serves as a prior for entity matching. "Florent" in a conversation thread about CeSIA resolves to Florent Berthet with much higher confidence than "Florent" in isolation. The context is free — it requires only graph reads that are already fast.

### Principle 3: Atomic Clusters, Not Sequential Nodes

The entire cluster (Moment + Space + Actors + Things + all links) is written as one logical operation. If any part fails, nothing is written. This prevents the graph from accumulating orphaned nodes and half-formed relationships that pollute search results and confuse the physics.

### Principle 4: Physics Handles the Long Term

Cluster write sets initial conditions. It creates links with appropriate initial weights based on confidence (confirmed = full weight, unconfirmed = reduced weight). After creation, the standard physics laws take over: L5 (co-activation reinforcement) strengthens links that are used together, L6 (consolidation) builds weight over time, L7 (forgetting) prunes links that are never reinforced. The cluster write tool does not try to predict long-term relationship strength — it just gives the physics accurate starting conditions.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `mcp/tools/cluster_write_handler.py` | FILE | Main handler (to be created) |
| `mcp/tools/graph_write_handler.py` | FILE | Existing single-node writer — reference for link creation patterns |
| `mcp/tools/think_handler.py` | FILE | Gemini integration for content analysis |
| `mcp/tools/context.py` | FILE | ServerContext — graph_ops, graph_queries, runner |
| `schema-l3.yaml` | FILE | L3 schema — node types, link dimensions, trust model |
| FalkorDB graph | DB | Citizen's universe graph — existing actors, spaces, things for matching |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mcp/tools/think_handler.py` | Gemini API for structured entity extraction from content |
| `runtime/physics/graph/GraphOps` | Graph reads (KNN search, existing actor lookup) and writes (node creation, link creation) |
| `runtime/infrastructure/embeddings/service` | EmbeddingService for computing synthesis embeddings and entity similarity matching |
| `runtime/identity.py` | resolve_actor_id() for identifying the calling citizen |
| `mcp/tools/context.py` | ServerContext dependency injection |
| `mcp/tools/graph_write_handler.py` | infer_computed_type() for link dimension → computed_type mapping |

---

## INSPIRATIONS

- **graph_write's link creation patterns** — The _create_link helper with dimensional signatures and infer_computed_type is the proven pattern for L3 link creation. Cluster write reuses this, not reinvents.
- **Subcall's pre-compute phase** — Subcall pre-computes the caller's activated context before probing targets. Cluster write mirrors this: pre-compute the citizen's context before analyzing content.
- **Contact resolution in email clients** — Gmail's "did you mean..." when you type a partial name. Cluster write does the same for graph actors: partial name match → suggest with context.

---

## SCOPE

### In Scope

- Moment cluster creation (Moment + Space + Actors + Things + all links)
- Pre-computation of citizen context (active spaces, recent actors, known things)
- Content analysis via Gemini (entity extraction: names, places, URLs, handles, tokens)
- Identity resolution against existing graph actors (platform_id match, email/phone match, embedding similarity)
- Confidence grading of links (confirmed vs unconfirmed, reflected in link weight)
- Suggestion presentation for citizen review
- URL auto-creation as Thing nodes
- Dedup on platform_id and email/phone (auto-merge)
- Dedup on embedding similarity (suggest merge, do not auto-merge)

### Out of Scope

- Crystallization (L10) → see: physics laws, handled automatically by tick
- Long-term relationship evolution → see: L5/L6/L7 physics
- Single-node creation → see: graph_write (graph_write_handler.py)
- LLM conversation with other citizens → see: /call (call_handler.py)
- Cross-universe writes → future scope
- Graph reads/queries → see: graph_query (graph_query_handler.py)

---

## MARKERS

<!-- @mind:todo Design the Gemini system prompt for structured entity extraction -->
<!-- @mind:todo Define the exact link weight values for confirmed vs unconfirmed entities -->
<!-- @mind:proposition Consider batch mode for importing many moments from a platform dump -->
