# Graph Enricher — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Structural enrichment: on_message() creates Moment/Actor/Space nodes with dimensional LINK edges
- @handle mention extraction: bridge-provided mentioned_handles create LINK(mention) edges
- Reply enrichment: on_reply() creates reply Moment, links to original, inherits narrative/space links
- Reaction enrichment: on_react() creates Actor→Moment LINK(reaction) with emoji
- Commit enrichment: on_commit() creates commit Moment linked to repo Space and author Actor
- File change enrichment: on_file_change() creates Thing nodes for significant files
- Pin/unpin: on_pin/on_unpin() toggle permanence on Moment nodes
- Read tracking: on_read() creates/updates Actor→Space presence links
- Space stimulus: AI citizens present in a Space receive L1 stimulus when a message arrives
- Trust propagation: mention events trigger trust EMA updates

**What's still being designed:**
- Tier 1 pattern extraction: URLs, $tokens, @handles from message content (regex-based, confirmed)
- Tier 2 LLM extraction: names, organizations, places from free text (Gemini structured output, unconfirmed)
- Entity resolution: embedding similarity match against existing nodes
- Platform handle fields on Actor nodes (telegram_id, discord_id, x_handle, etc.)
- Auto-merge on deterministic signals (same platform_id, email, phone)
- Merge proposal creation on embedding similarity (0.85-0.95 range)
- Confidence threshold filtering (>= 0.6 for LLM extractions)

**What's proposed (v2+):**
- Relationship extraction between entities ("Florent works at CeSIA" → Actor-Thing link)
- Retroactive enrichment of existing Moments (batch job)
- Entity type refinement (e.g., "CeSIA is an AI safety research institute")
- Batched Gemini extraction (collect 5-10 messages, extract in one API call)
- Adaptive extraction confidence thresholds based on observed precision

---

## CURRENT STATE

The graph enricher is implemented and running in production. It is called by discord_bridge.py, telegram_bridge.py, and whatsapp_bridge.py on every message event. The git post-commit hook calls on_commit() and on_file_change().

The current enricher handles structural graph records comprehensively: messages, replies, reactions, commits, file changes, pins, reads. It creates dimensional LINK edges using infer_computed_type() from the graph_write_handler. It stimulates AI citizens present in a Space when a message arrives. It propagates trust on mention interactions.

What it does NOT do: extract entities from free text. The only entity extraction today is @handle mentions provided by the bridge (Discord's built-in mention detection, Telegram's @username parsing). No URLs, no $tokens, no person names, no organization names, no place names are extracted from message content. The graph is blind to everything that isn't a structured @mention.

The file is at ~985 lines (SPLIT status) and needs to be broken up before adding new functionality.

---

## IN PROGRESS

### Documentation chain creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** complete
- **Context:** Full 8-doc chain created from the existing implementation + NLR design conversation for the entity extraction upgrade. All docs are at DESIGNING status. The design covers the full pipeline: tier 1 pattern extraction, tier 2 LLM extraction, entity resolution with embedding match, platform handle fields, auto-merge, and merge proposals.

---

## RECENT CHANGES

### 2026-03-18: Documentation chain created

- **What:** Full 8-doc DESIGNING chain for cognition/graph_enricher module
- **Why:** The enricher is being upgraded from @handle-only extraction to full entity extraction. The doc chain captures the existing implementation (what works today) and the design for the upgrade (what needs to be built). This makes the gap between v1 and v2 explicit.
- **Files:** docs/cognition/graph_enricher/ (all 8 files)
- **Insights:** The existing graph_enricher.py is at SPLIT status (985 lines). The file grew organically as new event types were added (reply, react, commit, pin, read). Before adding entity extraction, the file needs to be split into focused modules. The naming convention follows the protocol: graph_enricher_tier1_pattern_entity_extractor.py, graph_enricher_tier2_llm_entity_extractor.py, etc.

---

## KNOWN ISSUES

### File size at SPLIT threshold

- **Severity:** medium
- **Symptom:** graph_enricher.py is ~985 lines, well above the 700-line SPLIT threshold
- **Suspected cause:** Organic growth — on_reply, on_react, on_commit, on_file_change, on_pin, on_read were all added to the same file
- **Attempted:** Not yet addressed. The planned extraction (tier1/tier2/resolver/merger files) will naturally reduce the main file, but existing helper functions (_sanitize_handle, _moment_id) should also be extracted.

### FalkorDB crashes under heavy load

- **Severity:** high (infra, not code)
- **Symptom:** Graph connection drops when processing many concurrent messages (observed with 278 citizens)
- **Suspected cause:** FalkorDB memory limits or connection pool exhaustion
- **Attempted:** Known issue documented in memory. Tests use mocks. Not addressable by the enricher code.

### No fallback when graph is unavailable

- **Severity:** low
- **Symptom:** If _get_graph() returns None, on_message() silently returns without enrichment
- **Suspected cause:** By design — the enricher fails gracefully when FalkorDB is unavailable
- **Attempted:** This is intentional. The enricher should not block bridge processing when the graph is down. But this means enrichment is silently lost during outages.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement (building the entity extraction pipeline)

**Where I stopped:** Documentation chain is complete. All 8 docs describe the existing v1 implementation and the designed-but-not-built v2 entity extraction pipeline.

**What you need to understand:**
The enricher is the most-called function in the system — every message from every bridge passes through it. Latency matters. The design splits extraction into two tiers precisely because tier 2 (Gemini) adds ~300ms. Tier 1 (regex) adds <1ms. The structural enrichment (Step 1) must never be blocked by tier 2.

The graph_enricher.py file is at SPLIT (985 lines). Before adding entity extraction inline, split the file. The planned helper files (tier1, tier2, resolver, merger) provide the splitting plan. Don't add more code to the main file without splitting first.

**Watch out for:**
- FalkorDB vector index support — verify that `CALL db.idx.vector.queryNodes` works on the current deployment before implementing embedding-based entity resolution. If not available, you need to create the vector index first.
- The enricher uses a lazy global `_graph` connection. This is a singleton. If the process runs multiple enrichment calls concurrently (e.g., from different bridge threads), they share the same connection. FalkorDB handles concurrent queries, but be aware of this shared state.
- The `infer_computed_type()` import has a fallback (returns "relates" if import fails). This means enrichment works even without the graph_write_handler. Don't break this by adding hard dependencies.

**Open questions I had:**
- Should tier 2 extraction be fully async (background task) or inline with a timeout? Inline is simpler but adds latency. Async requires a queue and delayed graph updates.
- Should the enricher batch Gemini calls? Processing 1 message = 1 API call. But 10 messages in 5 seconds could be batched into 1 call with 10 texts. Batching reduces cost but adds latency for the first message.
- What embedding model to use for entity resolution? Gemini embedding? Local model? The choice affects latency, cost, and quality.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete DESIGNING documentation chain created for the graph enricher module. 8 files covering objectives, patterns, behaviors, algorithm, validation, implementation, health, and sync. The docs capture the existing v1 implementation (structural enrichment, @handle mentions) and the designed v2 upgrade (full entity extraction from free text, platform handle fields, dedup/merge pipeline).

**Decisions made:**
- Two-tier extraction: regex (confirmed, sync) + Gemini (unconfirmed, potentially async)
- Platform handles as fields on Actor nodes (not separate nodes)
- Three-tier dedup: platform_id auto-merge, email/phone auto-merge, embedding similarity merge proposal
- Confidence threshold at 0.6 for LLM extractions
- Embedding similarity thresholds: >0.95 auto-match, >0.85 propose merge, <0.85 create new

**Needs your input:**
- Gemini API budget for per-message extraction. At 200 messages/day and ~$0.001/call, that is ~$6/month. Acceptable?
- Should tier 2 extraction be inline (simpler, +300ms latency) or async (complex, no latency impact)?
- Which embedding model for entity resolution? Gemini embeddings are convenient (same API), local models avoid external dependency.
- Priority: should entity extraction be implemented before or after the graph_enricher.py file split?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Implement tier 1 pattern extraction (URLs, $tokens) — BEHAVIORS B3, B4
- [ ] DOCS->IMPL: Implement tier 2 LLM extraction (Gemini) — BEHAVIOR B5, B6, B7
- [ ] DOCS->IMPL: Implement entity resolution with embedding match — ALGORITHM Step 5
- [ ] DOCS->IMPL: Implement platform handle fields on Actor nodes — BEHAVIOR B8
- [ ] DOCS->IMPL: Implement auto-merge on deterministic signals — BEHAVIOR B9
- [ ] DOCS->IMPL: Implement merge proposal creation — BEHAVIOR B10
- [ ] DOCS->IMPL: Add counter instrumentation for health checks
- [ ] DOCS->IMPL: Split graph_enricher.py (SPLIT status at 985 lines)

### Tests to Run

```bash
# No dedicated tests exist yet for graph_enricher
# Tests use mocks due to FalkorDB crash issues under load
```

### Immediate

- [ ] Split graph_enricher.py into focused modules (prerequisite for all new functionality)
- [ ] Implement tier 1: extract_urls(), extract_tokens() — lowest effort, highest immediate value
- [ ] Add platform handle fields to Actor MERGE queries

### Later

- [ ] Implement tier 2: Gemini structured output extraction
- [ ] Implement entity resolution with embedding similarity
- [ ] Implement auto-merge + merge proposal
- [ ] Add health check counter instrumentation
- IDEA: Retroactive enrichment job that processes existing Moments to backfill entity nodes
- IDEA: Adaptive confidence thresholds that learn from merge proposal resolutions

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the documentation accuracy for the existing v1 implementation — every claim traces to specific lines in graph_enricher.py. The v2 design is clear in intent but untested — the thresholds (0.95, 0.85, 0.6) are informed guesses that will need tuning against real data.

**Threads I was holding:**
- The enricher is called from multiple bridges (Discord, Telegram, WhatsApp) and the git hook. Each caller passes slightly different metadata. The platform handle update step needs to handle all these variations.
- The _stimulate_space_citizens() function queries the graph for AI citizens with presence links to the Space. This query could be expensive if many citizens are present. It currently has no caching or throttling.
- Trust propagation (step 9 in the existing pipeline) has a bare `except: pass` clause. This is intentional (trust is non-critical) but means trust propagation failures are invisible.

**Intuitions:**
- Batching Gemini calls will probably be necessary at scale. One API call per message is too many round-trips. The natural batch boundary is "all messages in the last N seconds" or "all messages in the current tick."
- The 0.85 embedding threshold for merge proposals will need to be tuned per entity type. Person names have much higher collision rates than organization names. "Jean Martin" and "Jean-Martin Dupont" have similar embeddings but are different people.
- The enricher should eventually emit events that other systems can subscribe to (e.g., "new Actor discovered," "merge proposed"). This enables downstream systems to react without polling the graph.

**What I wish I'd known at the start:**
The graph_enricher.py file grew to 985 lines because each new event type (reply, react, commit, pin, read) was added as a new function in the same file. The functions share the same _get_graph() connection and the same infer_computed_type() import, but otherwise they are independent. Splitting would be straightforward — each on_* function is self-contained.

---

## POINTERS

| What | Where |
|------|-------|
| Graph enricher implementation | `scripts/graph_enricher.py` |
| Discord bridge (caller) | `scripts/discord_bridge.py` (lines 473-476, 1273-1276, 1394-1397, 1413-1416) |
| Telegram bridge (caller) | `runtime/bridges/telegram_bridge.py` (line 766) |
| Citizen wake (stimulus injection) | `scripts/citizen_wake.py` |
| Trust propagation | `runtime/economy/trust_propagation.py` |
| infer_computed_type | `mcp/tools/graph_write_handler.py` |
| L3 schema (node types, Actor identity fields) | `schema-l3.yaml` |
| FalkorDB crash issue | Memory: feedback_falkordb_crashes_under_load.md |
| Stimulus router (parallel module) | `docs/cognition/stimulus_router/` |
