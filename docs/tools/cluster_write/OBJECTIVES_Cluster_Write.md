# OBJECTIVES — Cluster Write

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Cluster_Write.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Cluster_Write.md
BEHAVIORS:      ./BEHAVIORS_Cluster_Write.md
ALGORITHM:      ./ALGORITHM_Cluster_Write.md
VALIDATION:     ./VALIDATION_Cluster_Write.md
IMPLEMENTATION: ./IMPLEMENTATION_Cluster_Write.md
HEALTH:         ./HEALTH_Cluster_Write.md
SYNC:           ./SYNC_Cluster_Write.md

IMPL:           mcp/tools/cluster_write_handler.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Atomic cluster creation** — A single tool call produces a complete Moment cluster (Moment + Space + Actors + Things + all links), never leaving the graph in a half-written state. Today graph_write forces N sequential calls to build what is conceptually one event.

2. **Identity resolution at write time** — Platform-verified entities (X sender_id, Telegram user_id, Discord snowflake, email, phone) are matched against existing graph actors immediately, not left as dangling text. Text mentions ("my friend Florent") produce unconfirmed actors with lower link weight. Dedup happens at creation, not as a separate pass.

3. **Intelligent content analysis** — The tool uses Gemini (via /think) to extract entity references from natural language content: names become Actor candidates, places become Space candidates, URLs become Things, @handles become Actor matches, $tokens become Things. The citizen never hand-tags entities.

4. **Confidence-graded links** — Every link in the cluster carries a confidence signal derived from how the entity was identified. Platform-verified = status:confirmed, full link weight. Text mention = status:unconfirmed, reduced link weight. The physics (L5/L6/L7) then evolves these links over time — co-activation reinforces, forgetting prunes.

5. **Citizen-in-the-loop suggestions** — Before writing, the tool presents extracted entities with enough context for the citizen to confirm/reject without re-searching. "Is this @florent-berthet? (SID: a7f9b2c1, last seen: 2 days ago in #primers)".

## NON-OBJECTIVES

- **Crystallization** — This is NOT crystallization (L10). Crystallization is an automatic physics process that collapses dense clusters into hub narratives. Cluster write is identity resolution at creation time.
- **Long-term relationship management** — The physics (L5 co-activation, L6 consolidation, L7 forgetting) handle the long game. Cluster write only sets initial conditions.
- **Cross-universe writes** — Cluster write operates within the citizen's current universe graph. Cross-universe moments are out of scope.
- **LLM conversation** — The Gemini call is for structured extraction only, not open-ended conversation. That is /call.
- **Replacing graph_write** — graph_write remains for creating individual nodes (narratives, roles, spaces). Cluster write is specifically for Moment clusters.

## TRADEOFFS (canonical decisions)

- When speed conflicts with completeness of entity extraction, choose **completeness**. A missing actor link is worse than an extra 500ms of Gemini analysis.
- When dedup certainty conflicts with false merges, choose **suggesting over auto-merging**. Same platform_id and same email/phone auto-merge. Similar embedding only suggests.
- When confirmed and unconfirmed entities conflict on the same target, choose **confirmed**. A platform-verified identity always overrides a text-mention guess.
- We accept the cost of a Gemini API call per cluster_write to preserve the quality of entity extraction.

## SUCCESS SIGNALS (observable)

- A single cluster_write call for "Had coffee with Florent at Cafe de Flore, discussed the CeSIA paper (cesai.org/paper.pdf)" produces: 1 Moment, 1 Space (Cafe de Flore or matched existing), 2 Actors (caller + Florent matched or unconfirmed), 2 Things (CeSIA paper + URL), and all links — in one operation.
- Platform-verified actors from Telegram/Discord/X messages never create duplicate actor nodes.
- Text-mention actors that later get platform-verified auto-merge on the next encounter.
- The citizen can see all extracted entities before the write commits.
