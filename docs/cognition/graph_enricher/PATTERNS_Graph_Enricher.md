# Graph Enricher — Patterns: Materializing the Implicit World

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Graph_Enricher.md
THIS:            PATTERNS_Graph_Enricher.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Graph_Enricher.md
ALGORITHM:       ./ALGORITHM_Graph_Enricher.md
VALIDATION:      ./VALIDATION_Graph_Enricher.md
HEALTH:          ./HEALTH_Graph_Enricher.md
IMPLEMENTATION:  ./IMPLEMENTATION_Graph_Enricher.md
SYNC:            ./SYNC_Graph_Enricher.md

IMPL:            scripts/graph_enricher.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Graph_Enricher.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Graph_Enricher.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

The L3 graph today sees only what is explicitly structured: @handles from Discord mentions, channel IDs from bridge events, commit hashes from git hooks. But the richest information flows through free text. When a citizen writes "I had lunch with Florent Berthet from CeSIA — he's interested in the bilateral civilization concept," the current enricher captures none of this. Florent does not exist in the graph. CeSIA does not exist. The citizen's relationship to both is invisible.

This means:
- Context assembly for LLM conversations cannot reference people, organizations, or places mentioned in prior messages
- Cross-platform identity resolution is impossible — the same person on Telegram, Discord, and email appears as three unrelated handles
- The graph cannot accumulate weight on real-world relationships because the entities involved are never materialized as nodes

The graph enricher must become the perceptual system of the L3 universe: everything mentioned in text that matters to the citizen should become a node, correctly typed, deduplicated against existing nodes, and linked to the Moment where it appeared.

---

## THE PATTERN

**Two-tier extraction: deterministic patterns first, LLM-assisted extraction second.**

The enricher separates entity extraction into two tiers based on confidence and cost:

**Tier 1 — Pattern matching (synchronous, zero-cost, confirmed):**
Easily recognizable patterns are extracted with regex and create nodes directly with `status:confirmed`. These are ground truth:
- URLs → Thing(type:url, status:confirmed)
- @handles → Actor match by handle
- $TOKEN mentions → Thing(type:token, status:confirmed)
- Platform sender_id from bridge metadata → Actor field update (telegram_id, discord_id, etc.)

**Tier 2 — LLM extraction (async-capable, costs tokens, unconfirmed):**
Free-text entity names require language understanding. Gemini structured output extracts `{name, entity_type, confidence, context}` tuples. Each extraction is matched against existing L3 nodes by embedding similarity. If a match exceeds threshold, the existing node is linked. If not, a new node is created with `status:unconfirmed`.

The key insight: **tier 1 should never need tier 2, and tier 2 should never create what tier 1 can catch.** URLs are URLs. @handles are handles. Only names and fuzzy references need LLM help.

**Platform handles are fields, not nodes.** A person's Telegram ID, Discord ID, X handle, LinkedIn, email, and phone number are all properties of a single Actor node. When a bridge event includes a sender_id, the enricher writes that ID onto the Actor's corresponding platform field. This enables the dedup rule: same platform_id on the same platform = same Actor, auto-merge.

---

## BEHAVIORS SUPPORTED

- **B1: Pattern-based entities create confirmed nodes** — URLs, tokens, and other deterministic patterns produce nodes immediately with status:confirmed.
- **B2: Free-text names produce unconfirmed nodes** — LLM-extracted names create Actor nodes with status:unconfirmed, pending verification.
- **B3: Platform identity updates Actor fields** — Bridge sender_ids are stored as fields on Actor nodes, not as separate entities.
- **B4: Same platform_id auto-merges** — If a newly identified platform_id already exists on another Actor, the two are merged automatically.
- **B5: Similar embeddings propose merge** — If a new name's embedding is close to an existing Actor's embedding but not identical by platform_id, a merge task is created for review.

## BEHAVIORS PREVENTED

- **A1: Ghost node proliferation** — Without dedup, every mention of "Florent" would create a new Actor. Embedding match and platform_id match prevent this.
- **A2: False merges** — Embedding similarity alone is not enough to auto-merge. Only deterministic signals (same platform_id, same email, same phone) trigger auto-merge. Similar names create a merge proposal.
- **A3: Enrichment blocking the write path** — Pattern extraction is synchronous. LLM extraction is managed separately to avoid stalling the message pipeline.

---

## PRINCIPLES

### Principle 1: Confirmed by Structure, Unconfirmed by Inference

The enricher distinguishes between facts and guesses. A platform sender_id is a fact — the bridge verified it. A name extracted from free text is a guess — the LLM inferred it. This distinction is encoded in the `status` field on every created node. Confirmed nodes participate fully in context assembly and trust computation. Unconfirmed nodes are flagged and can be promoted or pruned.

### Principle 2: Platform Handles Are Identity Facets, Not Entities

A Telegram ID is not a separate thing from the person. It is a facet of the person's identity. Storing platform handles as fields on the Actor node (telegram_id, discord_id, x_handle, linkedin_url, email, phone) means the Actor node IS the single source of truth for who someone is across all platforms. When you know someone's Telegram ID, you know who they are everywhere.

### Principle 3: Dedup Is a Gradient, Not a Binary

Auto-merge (same platform_id) is one end. Manual review (embedding similarity) is the middle. Creation of a new node (no match) is the other end. The enricher operates along this gradient, choosing the action that matches the confidence level of the signal.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `scripts/graph_enricher.py` | FILE | Current implementation — handles @mentions, creates Space/Actor/Moment/links |
| `schema-l3.yaml` | FILE | L3 schema — Actor identity fields (sid, handle, voices), node types |
| `runtime/bridges/telegram_bridge.py` | FILE | Telegram bridge — calls graph_enricher.on_message() with sender metadata |
| `scripts/discord_bridge.py` | FILE | Discord bridge — calls graph_enricher.on_message() and on_reply() |
| `mcp/tools/graph_write_handler.py` | FILE | graph_write MCP tool — infer_computed_type() imported by enricher |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mcp/tools/graph_write_handler` | Imports `infer_computed_type()` for computing LINK computed_type from dimensions |
| `scripts/citizen_wake` | Imports `_inject_l1_stimulus()` for stimulating AI citizens present in a Space |
| `runtime/economy/trust_propagation` | Imports `propagate_trust()` for trust EMA updates on mentions |
| FalkorDB (falkordb package) | Graph database for node/link storage |
| Gemini API (google-generativeai) | Structured output for free-text entity extraction (tier 2, to be added) |

---

## INSPIRATIONS

**Named Entity Recognition (NER) in NLP.** The enricher's tier 2 extraction is a specialized NER task: identify person names, organization names, and place names in free text. But unlike traditional NER, the enricher must also resolve these entities against a known graph — it is not enough to tag "Florent Berthet" as PERSON; the enricher must determine if this is an existing Actor or a new one.

**Identity resolution in data engineering.** Master Data Management (MDM) systems solve the same dedup problem: multiple records referring to the same real-world entity. The enricher's three-tier dedup (platform_id → email/phone → embedding) mirrors the MDM pattern of deterministic match → probabilistic match → human review.

**Knowledge graph population.** The enricher is a simplified knowledge graph population pipeline. It extracts entities from unstructured text, types them, resolves them against an existing graph, and creates new nodes when needed. The difference from enterprise KG systems is scale (thousands of nodes, not millions) and latency requirements (real-time enrichment, not batch).

---

## SCOPE

### In Scope

- Extracting entities (Actors, Spaces, Things) from Moment content
- Creating or matching L3 nodes for extracted entities
- Linking extracted entities to the Moment where they appeared
- Storing platform handles as fields on Actor nodes
- Auto-merging on deterministic signals (same platform_id, same email/phone)
- Proposing merge tasks on probabilistic signals (embedding similarity)
- Pattern-based extraction of URLs, @handles, $tokens
- LLM-assisted extraction of names, organizations, places from free text

### Out of Scope

- **Relationship extraction** — The enricher links entities to Moments, not to each other. "Florent works at CeSIA" does not create an Actor→Thing link. That is a separate concern.
- **Entity classification refinement** — The enricher assigns initial types (Actor, Space, Thing). Refinement (e.g., "CeSIA is specifically an AI safety research institute") belongs to a downstream classification module.
- **Retroactive enrichment** — Processing existing Moments is a batch job, not the real-time enricher's responsibility.
- **Trust computation** — Trust lives on links and is computed by physics. The enricher creates structural links; trust accumulates through co-activation (L5) and consolidation (L6).

---

## MARKERS

<!-- @mind:todo Implement tier 2 (Gemini structured output) extraction pipeline -->
<!-- @mind:todo Add platform handle fields to Actor schema in graph_enricher -->
<!-- @mind:todo Design merge task creation for embedding-similar but not identical entities -->
<!-- @mind:escalation Gemini API cost model for per-message extraction — need budget estimate before implementation -->
