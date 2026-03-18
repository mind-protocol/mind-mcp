# Gap Detection — Sync: Current State

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
- Three-pass scan architecture (missing links, duplicates, empty query gaps)
- Task creation via task_physics.create_task() with deterministic IDs
- Empty query gap hook on graph_query return path
- Content heuristics for Thing-link detection
- Integration points with tick loop and search system

**What's proposed (v2+):**
- Approximate nearest neighbor for duplicate detection on large graphs (>500 nodes)
- MCP tool exposure for on-demand gap scans
- Narrative node gap detection (missing CONTRIBUTES_TO links)
- Learned stop-word list per citizen for empty query filtering

---

## CURRENT STATE

The full doc chain is written. No code exists yet. The design specifies:

- `runtime/cognition/gap_detector.py` — main scanner with `scan_gaps()` and three passes
- `runtime/cognition/gap_query_hook.py` — `on_query_result()` hook for search integration
- `runtime/cognition/gap_detection_heuristics.py` — content analysis and query quality filters
- `runtime/cognition/gap_detection_constants.py` — thresholds and energy values

The design integrates with two existing systems:
1. **Task physics** (`runtime/organization/task_physics.py`) — `create_task()` for writing gap tasks
2. **Graph search** (`runtime/physics/graph/graph_queries_search.py`) — hook for empty query detection

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete
- **Context:** All 8 doc chain files written. Design captures NLR's specification: three gap sources (missing links, duplicates, empty queries), task routing via existing system, L7 handles cleanup.

---

## RECENT CHANGES

### 2026-03-18: Initial Design

- **What:** Full 8-doc chain created from NLR's specification
- **Why:** Gap detection is needed to close the loop on graph structural completeness. The graph grows through ingestion but nobody checks whether the ingested data is well-connected.
- **Files:** `docs/cognition/gap_detection/` (8 files)
- **Struggles/Insights:** The key design tension is between aggressive detection (surface everything) and noise management (don't flood citizens with tasks). Resolution: be aggressive in detection, rely on L7 forgetting for cleanup. False positives decay. False negatives persist.

---

## KNOWN ISSUES

### Thing-Link Heuristic Undefined

- **Severity:** medium
- **Symptom:** `content_mentions_objects()` has no concrete implementation design
- **Suspected cause:** Detecting "this content mentions concrete objects" is genuinely hard without an LLM. Pattern matching will have false negatives.
- **Attempted:** Nothing yet — needs design work on the heuristic vocabulary

### Query Hook Integration Point Unspecified

- **Severity:** medium
- **Symptom:** `on_query_result()` needs to be called from graph_queries_search.py but the exact wiring is not designed
- **Suspected cause:** Search code may not have a clean hook point. May need a small refactor.
- **Attempted:** Noted in IMPLEMENTATION markers

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementing from design docs)

**Where I stopped:** Design is complete. Implementation has not started.

**What you need to understand:**
The three scan passes are independent. Start with missing link scan — it's the simplest (batch Cypher, context assembly, task creation) and validates the full pipeline. Duplicate scan needs embedding vectors, which may not exist on all nodes yet. Empty query hook needs a wiring change in graph_queries_search.py.

**Watch out for:**
- Deterministic task IDs are critical (V2). If you use UUIDs, duplicate scans will create duplicate tasks every time they run.
- The `create_task()` function in task_physics.py expects specific parameters. Read its signature before designing the gap detector's task creation calls.
- FalkorDB can crash under heavy load (see feedback_falkordb_crashes_under_load.md). Batch your Cypher queries and don't load all nodes at once.

**Open questions I had:**
- Should gap detection run per-citizen (scan one brain at a time) or globally (scan all brains in one pass)? The design assumes per-citizen, but global scanning might be more efficient for duplicate detection across citizens.
- Should the empty query hook be synchronous (blocks search return) or asynchronous (fire-and-forget)? Async is safer for search latency but risks losing events.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full design documentation for the gap_detection module. Three gap sources designed: missing links on Moments, potential duplicate nodes via embedding similarity, and empty query gap markers from failed searches. The design integrates with existing task physics for task creation/routing and relies on L7 forgetting for cleanup of unresolved gaps.

**Decisions made:**
- Detector is read-only (creates tasks, never modifies graph structure)
- Duplicate detection uses cosine 0.85 threshold, distinct from crystallization
- Empty query gaps use logarithmic energy accumulation on repeats
- Small graphs (< 20 nodes) get lower initial gap energy to avoid flooding

**Needs your input:**
- Thing-link heuristic: what vocabulary of "object-indicating patterns" should `content_mentions_objects()` use?
- Per-citizen vs. global scanning for duplicate detection
- Whether empty query gap detection should be opt-in per citizen

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Entire module needs implementation (all 4 files)

### Tests to Run

```bash
pytest tests/cognition/test_gap_detector.py (to be created)
```

### Immediate

- [ ] Implement `gap_detection_constants.py` with all threshold values
- [ ] Implement `gap_detector.py` — start with `_scan_missing_links()` pass
- [ ] Implement `gap_detection_heuristics.py` — at least `content_mentions_objects()` stub
- [ ] Write tests for missing link scan with mock graph data

### Later

- [ ] Implement `_scan_duplicates()` pass — needs embedding vectors on test data
- [ ] Implement `gap_query_hook.py` and wire into graph_queries_search.py
- [ ] Add gap_detection to auto_task_taxonomy.yaml
- [ ] Benchmark scan performance on a real citizen graph (for V5 timeout values)
- IDEA: Expose `scan_gaps()` as an MCP tool for on-demand scanning

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The three-pass architecture is clean and each pass is independently testable. The integration with task_physics is straightforward. The main uncertainty is the Thing-link heuristic and the query hook wiring.

**Threads I was holding:**
- The duplicate scan's O(n^2) complexity is a concern for large graphs. The ANN fallback is noted but not designed in detail.
- Gap markers (empty query) are a new node type (type='gap_marker') distinct from tasks. Should they be tasks too? Currently they're passive markers that could be promoted to tasks if they accumulate enough energy.
- The energy refresh mechanism needs to be careful: refreshing too aggressively prevents L7 from cleaning up genuinely unimportant gaps.

**Intuitions:**
- Missing link scan will be the highest-value pass initially. Most graphs have many unlinked Moments.
- Duplicate detection may need a higher threshold (0.90) in practice to avoid false positives, especially for Actors with similar roles.
- Empty query gaps will be most useful once the knowledge acquisition system exists to act on them. Until then, they're markers waiting for a consumer.

**What I wish I'd known at the start:**
Read the auto_task_taxonomy.yaml first — it shows the exact pattern for how detection tasks are structured (detection query, resolution predicate, energy, category, links). The gap detector follows this same pattern.

---

## POINTERS

| What | Where |
|------|-------|
| Task physics (create_task) | `runtime/organization/task_physics.py` |
| Auto task taxonomy | `docs/organization/task_physics/auto_task_taxonomy.yaml` |
| Graph search (hook target) | `runtime/physics/graph/graph_queries_search.py` |
| L1 node types | `docs/cognition/l1_physics/PATTERNS_L1_Cognition.md` |
| L3 schema | `schema-l3.yaml` |
| L7 forgetting | `docs/cognition/l1_physics/ALGORITHM_L1_Physics.md` |
| Task handler (MCP) | `mcp/tools/task_handler.py` |
