# OBJECTIVES — Graph Enricher

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Graph_Enricher.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Graph_Enricher.md
BEHAVIORS:      ./BEHAVIORS_Graph_Enricher.md
ALGORITHM:      ./ALGORITHM_Graph_Enricher.md
VALIDATION:     ./VALIDATION_Graph_Enricher.md
IMPLEMENTATION: ./IMPLEMENTATION_Graph_Enricher.md
HEALTH:         ./HEALTH_Graph_Enricher.md
SYNC:           ./SYNC_Graph_Enricher.md

IMPL:           scripts/graph_enricher.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Entity extraction from free text** — Every message, commit, and event flowing through the system contains implicit references to people, places, organizations, tools, and URLs. These references are invisible to the graph unless the enricher extracts them and materializes them as nodes. Without this, the L3 universe knows only about @handles and channel names — it cannot represent "my friend Florent from CeSIA" or "the paper we discussed yesterday."

2. **Accurate deduplication and merge** — The same real-world entity appears under many names across platforms: "Florent Berthet" in a Telegram message, "@florent-berthet" on Discord, "florent.berthet@cesia.eu" in an email. The enricher must recognize these as one Actor and merge them, or at minimum propose a merge. Without dedup, the graph fills with ghost nodes — fragmentary representations of the same person that never accumulate weight or trust.

3. **Confidence-aware node creation** — Not every mention deserves a confirmed node. A verified sender_id from a bridge is ground truth. A name extracted from free text by an LLM is a guess. The enricher must track this distinction: platform-verified entities are `status:confirmed`, LLM-extracted entities are `status:unconfirmed`. Unconfirmed nodes can be promoted by subsequent verification or merged by a human.

4. **Platform handle aggregation** — An Actor is not their Telegram ID or their Discord handle. An Actor is a person who has many platform identities. Platform handles (X, Telegram, Discord, LinkedIn, email, phone) must be stored ON the Actor node as fields, not as separate nodes. This enables cross-platform matching: when someone with a known Telegram ID appears on Discord, the enricher recognizes them.

5. **Minimal latency on the write path** — The enricher runs on every Moment creation (post-processing after graph_write/cluster_write). It must not stall the message pipeline. Easily recognizable patterns (URLs, @handles, $tokens) are extracted synchronously. Free-text entity extraction via Gemini is the expensive step and must be managed to avoid blocking.

## NON-OBJECTIVES

- **Relationship extraction between entities** — The enricher creates nodes and links them to the Moment where they were mentioned. It does not infer relationships between extracted entities ("Florent works at CeSIA" implies an Actor-Thing relationship, but the enricher does not create that link). Relationship inference is a separate concern.
- **Sentiment or intent analysis** — The enricher extracts what entities exist, not what the speaker feels about them. Sentiment lives in the link dimensions (polarity, valence) computed by physics.
- **Historical backfill** — The enricher processes new Moments as they arrive. Retroactive enrichment of existing Moments is a separate batch operation.
- **Entity disambiguation beyond embedding match** — When two names have similar embeddings but are actually different people, the enricher proposes a merge task rather than auto-merging. Human resolution is required for ambiguous cases.

## TRADEOFFS (canonical decisions)

- When **extraction recall** conflicts with **precision**, choose precision. A missed entity can be caught on the next mention. A false entity creates a garbage node that pollutes the graph and confuses context assembly. Better to miss a name than to hallucinate one.
- When **auto-merge certainty** conflicts with **speed**, choose certainty. Same platform_id or same email/phone = auto-merge (deterministic). Similar embedding = propose merge task (requires review). We accept slower dedup to avoid merging distinct people.
- When **write-path latency** conflicts with **extraction completeness**, choose latency for recognizable patterns and defer free-text extraction. URLs, @handles, and $tokens are extracted synchronously. Name extraction via Gemini can be async or batched.

## SUCCESS SIGNALS (observable)

- A message containing "I met Florent Berthet from CeSIA yesterday" produces an Actor node (Florent Berthet, status:unconfirmed) and a Thing node (CeSIA, type:organization, status:unconfirmed), both linked to the Moment
- A URL pasted in a message produces a Thing node (status:confirmed, type:url) with the URL as content
- When a known Telegram user sends a message, their platform_id matches an existing Actor node, and the Actor's telegram_id field is populated or confirmed
- When "@florent-berthet" appears in Discord and "Florent Berthet" was previously extracted from text, the enricher proposes a merge task (embedding similarity above threshold) rather than creating a duplicate
- The write-path latency for pattern-based extraction (URLs, handles, tokens) is under 10ms
