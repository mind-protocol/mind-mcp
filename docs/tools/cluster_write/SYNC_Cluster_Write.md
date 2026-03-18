# Cluster Write — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — module is in design phase

**What's still being designed:**
- The four-phase pipeline (Pre-compute → Analyze → Suggest → Write)
- TOOL_SCHEMA for MCP interface
- Gemini extraction prompt and structured output format
- Entity resolution algorithm (platform_id → email/phone → handle → embedding similarity)
- Confidence grading: confirmed (1.0 weight) vs unconfirmed (0.5 weight)
- Rollback mechanism for partial write failures
- Suggestion format for citizen review

**What's proposed (v2+):**
- Batch mode for importing many moments from a platform dump
- "Learn" mode where citizen corrections feed back into prompt tuning
- Cross-universe cluster writes
- Streaming entity resolution (real-time extraction as citizen types)

---

## CURRENT STATE

The full documentation chain has been written in DESIGNING status. No implementation exists yet. The design covers:

1. **OBJECTIVES** — 5 ranked objectives: atomic clusters, identity resolution, content analysis, confidence grading, citizen-in-the-loop
2. **PATTERNS** — Pre-compute → Analyze → Suggest → Write pipeline with identity resolution as a write-time concern
3. **BEHAVIORS** — 7 behaviors (B1-B7) with GIVEN/WHEN/THEN specs, 5 edge cases, 4 anti-behaviors
4. **ALGORITHM** — Detailed 4-phase pipeline with pseudocode, data structures, key decisions, helper functions
5. **VALIDATION** — 8 invariants (V1-V8) ranked by priority
6. **IMPLEMENTATION** — 3-file code structure, design patterns, data flow with docking points
7. **HEALTH** — 4 health indicators with 2 fully specified checkers (cluster_atomicity, platform_dedup_accuracy)

The design builds on the existing graph_write_handler.py for link creation (reuses infer_computed_type) and think_handler.py for Gemini integration.

---

## IN PROGRESS

### Documentation chain

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** complete (all 8 docs written)
- **Context:** This is a redesign of graph_write for cluster creation. The existing graph_write remains for individual nodes. cluster_write is specifically for Moment clusters with identity resolution.

---

## RECENT CHANGES

### 2026-03-18: Initial design documentation

- **What:** Created full 8-doc chain for cluster_write module
- **Why:** graph_write creates one node at a time, forcing N calls for a cluster. cluster_write creates whole clusters atomically with intelligent entity extraction.
- **Files:** `docs/tools/cluster_write/OBJECTIVES_Cluster_Write.md` through `SYNC_Cluster_Write.md`
- **Insights:** The key design tension is between auto-merging (fast, risky) and suggesting (slower, safer). The resolution: auto-merge only on platform_id (ground truth), suggest on everything else. Physics (L5/L6/L7) handles convergence over time.

---

## KNOWN ISSUES

None yet — module is in design phase, no implementation to have issues with.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Design is complete across all 8 docs. Implementation has not started.

**What you need to understand:**
The pipeline has 4 phases that must execute in order: Pre-compute loads context, Analyze extracts entities via Gemini + regex and resolves them against the graph, Suggest presents candidates for citizen review (skippable with confirm=true), Write creates all nodes and links atomically. The 3-file structure (handler, analyzer, context) maps to these phases.

**Watch out for:**
- The Gemini extraction prompt is critical — it must produce valid JSON with actors/spaces/urls/handles/tokens fields. Design it carefully.
- FalkorDB does not have true ACID transactions. The "atomicity" of Phase 4 requires manual cleanup on failure (try/except with rollback of created node IDs).
- infer_computed_type() in graph_write_handler.py is imported and reused — do not duplicate the link type computation logic.
- The TOOL_SCHEMA must be registered in mcp/tools/__init__.py alongside the other tools.

**Open questions I had:**
- Should SIMILARITY_THRESHOLD be 0.75 or something else? Needs testing against real graph data.
- Should the regex fallback (when Gemini fails) be silent or surfaced to the citizen?
- Should we enforce platform_id uniqueness at the FalkorDB index level or just at the application level?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full design documentation chain created for cluster_write — the new MCP tool that replaces sequential graph_write calls with atomic Moment cluster creation. The design covers a 4-phase pipeline (Pre-compute → Analyze → Suggest → Write) with identity resolution, confidence grading, and Gemini-powered entity extraction. No implementation exists yet.

**Decisions made:**
- Platform-verified data (Telegram/Discord/X sender_id, email, phone) auto-merges with existing actors. Text mentions only suggest matches. This is the core safety design.
- Confirmed entities get full link weight (1.0), unconfirmed get reduced (0.5). Physics evolves from there.
- 3-file code structure: handler (orchestration + write), analyzer (Gemini + resolution), context (graph reads).
- Reuses infer_computed_type() from graph_write — no link logic duplication.

**Needs your input:**
- Exact embedding similarity thresholds for suggest vs auto-merge (proposed: 0.75 suggest, 0.92 auto-merge with exact name match)
- Whether to enforce platform_id uniqueness at FalkorDB index level
- Priority of implementation vs other pending work

---

## TODO

### Immediate

- [ ] Implement `mcp/tools/cluster_write_handler.py` with TOOL_SCHEMA and handle_cluster_write()
- [ ] Implement `mcp/tools/cluster_write_analyzer.py` with Gemini extraction prompt and entity resolution
- [ ] Implement `mcp/tools/cluster_write_context.py` with graph queries for citizen context
- [ ] Register cluster_write in mcp/tools/__init__.py tool registry
- [ ] Design and test the Gemini extraction system prompt
- [ ] Write unit tests for entity resolution (platform_id match, embedding match, no match)
- [ ] Write integration test for full pipeline (content → cluster)

### Later

- [ ] Implement rollback mechanism for partial write failures
- [ ] Create runtime/checks/cluster_write_checks.py with health checkers
- [ ] Test similarity thresholds against production graph data
- IDEA: Batch import mode for Telegram/Discord message history
- IDEA: Streaming entity resolution for real-time extraction

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The 4-phase pipeline is clean and each phase has clear responsibilities. The confidence grading (confirmed vs unconfirmed) with physics handling the long term feels right — it avoids both over-committing (false auto-merges) and under-committing (dropping text mentions).

**Threads I was holding:**
- The Gemini extraction prompt is the highest-risk design decision. It must produce structured JSON reliably. The prompt needs careful engineering.
- FalkorDB transaction semantics are unclear — manual rollback may be the only option, which means tracking all created node IDs during Phase 4.
- The interaction between cluster_write and the existing graph_write needs documentation — when to use which.

**Intuitions:**
- The pre-compute phase (Phase 1) will prove more valuable than it looks. The recent actor list is essentially a "who is this citizen likely to mention" prior that dramatically improves name matching.
- The confirm=false → review → confirm=true flow may feel like too many steps. Consider adding a "confidence threshold" mode where high-confidence matches auto-confirm and only ambiguous ones require review.

**What I wish I'd known at the start:**
That graph_write_handler.py already has a sophisticated link creation system with dimensional inference. Building on it (rather than designing a new one) saved significant complexity.

---

## POINTERS

| What | Where |
|------|-------|
| Existing graph_write handler | `mcp/tools/graph_write_handler.py` |
| Gemini integration (think) | `mcp/tools/think_handler.py` |
| L3 schema | `schema-l3.yaml` |
| Link dimension mapping | `L3_LINK_DIMENSION_MAPPING.yaml` |
| ServerContext | `mcp/tools/context.py` |
| Subcall docs (style reference) | `docs/tools/subcall/PATTERNS_Subcall.md` |
| Identity resolution | `runtime/identity.py` |
| Embedding service | `runtime/infrastructure/embeddings/service.py` |
