# Gap Detection — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
BEHAVIORS:       ./BEHAVIORS_Gap_Detection.md
PATTERNS:        ./PATTERNS_Gap_Detection.md
ALGORITHM:       ./ALGORITHM_Gap_Detection.md
VALIDATION:      ./VALIDATION_Gap_Detection.md
THIS:            IMPLEMENTATION_Gap_Detection.md (you are here)
HEALTH:          ./HEALTH_Gap_Detection.md
SYNC:            ./SYNC_Gap_Detection.md

IMPL:            runtime/cognition/gap_detector.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── gap_detector.py                     # Main scanner: scan_gaps(), three passes
├── gap_query_hook.py                   # on_query_result() hook for empty query gaps
├── gap_detection_heuristics.py         # content_mentions_objects(), query quality checks
└── gap_detection_constants.py          # Thresholds, intervals, energy values
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `gap_detector.py` | Core scan logic: missing links, duplicate candidates, task creation | `scan_gaps()`, `_scan_missing_links()`, `_scan_duplicates()` | ~250 est. | PLANNED |
| `gap_query_hook.py` | Hook into graph_query return path for empty query gap detection | `on_query_result()`, `_create_or_energize_gap_marker()` | ~100 est. | PLANNED |
| `gap_detection_heuristics.py` | Content analysis heuristics and query quality filters | `content_mentions_objects()`, `is_quality_query()` | ~80 est. | PLANNED |
| `gap_detection_constants.py` | All configurable thresholds and energy values | Constants only | ~30 est. | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with independent scan passes

**Why this pattern:** Each scan pass (missing links, duplicates, empty queries) is independent. They share no mutable state, can run in any order, and can be enabled/disabled independently. This makes the system easy to extend (add a new pass) and easy to debug (run one pass at a time).

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy | Each scan pass is a separate function | Can be composed, tested, and toggled independently |
| Hook/Observer | `on_query_result()` | Captures search failures without modifying search code |
| Deterministic ID | Task IDs derived from gap content | Enables idempotent task creation (V2) |

### Anti-Patterns to Avoid

- **God Scanner**: Don't put all three passes in one monolithic function. Each pass is its own function with its own tests.
- **Eager Loading**: Don't load all nodes into memory for duplicate scan. Use batched Cypher queries and streaming comparison.
- **LLM in the Loop**: Don't use LLM calls for content analysis in `content_mentions_objects()`. Pure heuristics only. LLM calls would make scans unpredictably slow and expensive.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Gap detection | Scan logic, gap descriptors, task creation calls | Graph mutations, node merging, link creation | `scan_gaps()` returns gap list, creates tasks as side effect |
| Query hook | Result inspection, gap marker creation | Search algorithm, embedding computation | `on_query_result()` called by search, returns bool |

---

## SCHEMA

### Gap Task Node (Narrative)

```yaml
GapTask:
  required:
    - id: string              # Deterministic: "gap:{actor}:{type}:{hash}"
    - name: string            # Human-readable gap description
    - type: "task"            # Standard task type
    - node_type: "narrative"  # Universal schema
    - synthesis: string       # Rich context for resolution (embeddable)
    - status: "pending"       # Initial status
    - category: "gap_detection"
  optional:
    - sub_type: string        # 'missing_actor_link', 'missing_space_link', 'missing_thing_link', 'potential_duplicate_actor', 'potential_duplicate_space'
    - energy: float           # Initial urgency (0.2 - 0.85)
    - source_node_id: string  # What node the gap is about
    - target_node_id: string  # Second node (for duplicates)
  relationships:
    - CONTRIBUTES_TO: "citizen_operational" meta-objective
```

### Gap Marker Node (for empty queries)

```yaml
GapMarker:
  required:
    - id: string              # "gap:{actor}:query:{embedding_hash}"
    - name: string            # "Knowledge gap: {query summary}"
    - type: "gap_marker"      # Distinct from task — this is a signal, not actionable work (yet)
    - node_type: "narrative"
    - synthesis: string       # The query text and context
    - energy: float           # Accumulates with repeated failed queries
  optional:
    - query_text: string      # Original query
    - first_seen: timestamp   # When first detected
    - hit_count: int          # How many times this gap was triggered
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `scan_gaps()` | `gap_detector.py` (main) | Physics tick loop (every N ticks) or manual invocation |
| `on_query_result()` | `gap_query_hook.py` (main) | `graph_queries_search.py` after search completes |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Periodic Gap Scan

Explain: This flow is triggered every GAP_SCAN_INTERVAL ticks by the physics tick loop. It scans the citizen's L1 brain graph for missing links and duplicate candidates, then creates tasks. This flow matters because it's the primary mechanism for graph self-repair.

```yaml
flow:
  name: periodic_gap_scan
  purpose: Detect structural gaps in L1 brain graph and create resolution tasks
  scope: L1 brain graph of one citizen -> task nodes in the graph
  steps:
    - id: trigger
      description: Physics tick loop checks tick counter against GAP_SCAN_INTERVAL
      file: runtime/cognition/tick_runner_l1_cognitive_engine.py (integration point)
      function: tick() -> calls scan_gaps() when counter hits interval
      input: tick_count (int)
      output: boolean (should scan)
      trigger: Every tick
      side_effects: None
    - id: missing_link_scan
      description: Batch query for Moments without Actor/Space/Thing links
      file: runtime/cognition/gap_detector.py
      function: _scan_missing_links()
      input: actor_id, adapter
      output: list[GapDescriptor]
      trigger: scan_gaps() call
      side_effects: None (read-only)
    - id: duplicate_scan
      description: Pairwise embedding comparison for Actor and Space nodes
      file: runtime/cognition/gap_detector.py
      function: _scan_duplicates()
      input: actor_id, adapter, embed_fn
      output: list[GapDescriptor]
      trigger: scan_gaps() call
      side_effects: None (read-only)
    - id: task_creation
      description: For each GapDescriptor, check existing task, create or refresh
      file: runtime/cognition/gap_detector.py
      function: _create_or_refresh_task()
      input: GapDescriptor, adapter
      output: bool (created or refreshed)
      trigger: Gap found in scan
      side_effects: Creates Narrative nodes via task_physics.create_task()
  docking_points:
    guidance:
      include_when: Transformative step (gap detection) or write step (task creation)
      omit_when: Pure data pass-through
      selection_notes: The scan outputs and task creation are the significant docks
    available:
      - id: dock_scan_output
        type: graph_ops
        direction: output
        file: runtime/cognition/gap_detector.py
        function: scan_gaps()
        trigger: Periodic tick
        payload: "{gaps_found: list, tasks_created: int, tasks_refreshed: int}"
        async_hook: not_applicable
        needs: none
        notes: Primary output dock for health monitoring
      - id: dock_task_write
        type: graph_ops
        direction: output
        file: runtime/organization/task_physics.py
        function: create_task()
        trigger: Gap found
        payload: "{task_id, synthesis, energy, category}"
        async_hook: not_applicable
        needs: none
        notes: Graph write — creates Narrative node
    health_recommended:
      - dock_id: dock_scan_output
        reason: Verifies gaps are being found and tasks created (not silently failing)
      - dock_id: dock_task_write
        reason: Verifies task creation succeeds (graph is writable)
```

### Flow 2: Empty Query Gap Capture

Explain: This flow intercepts search results and captures failed queries as gap markers. It matters because it closes the loop between search and knowledge acquisition.

```yaml
flow:
  name: empty_query_gap_capture
  purpose: Turn failed graph_query results into knowledge acquisition targets
  scope: graph_query return value -> gap marker node
  steps:
    - id: query_completes
      description: graph_query finishes and returns results to caller
      file: runtime/physics/graph/graph_queries_search.py
      function: search() return path
      input: query results
      output: query results (pass-through)
      trigger: Any graph_query call
      side_effects: Calls on_query_result hook
    - id: gap_evaluation
      description: Check if results are empty or below resonance threshold
      file: runtime/cognition/gap_query_hook.py
      function: on_query_result()
      input: query_text, actor_id, results, resonance_threshold
      output: gap_created (bool)
      trigger: Query completion
      side_effects: Creates or energizes gap marker nodes
  docking_points:
    available:
      - id: dock_query_hook
        type: event
        direction: input
        file: runtime/cognition/gap_query_hook.py
        function: on_query_result()
        trigger: Search completion
        payload: "{query_text, actor_id, results, resonance_threshold}"
        async_hook: optional
        needs: Add hook call in graph_queries_search.py
        notes: Must not slow down search — fire-and-forget if async
      - id: dock_gap_marker_write
        type: graph_ops
        direction: output
        file: runtime/cognition/gap_query_hook.py
        function: _create_or_energize_gap_marker()
        trigger: Failed query detected
        payload: "{marker_id, synthesis, energy}"
        async_hook: not_applicable
        needs: none
        notes: Graph write for gap marker creation
    health_recommended:
      - dock_id: dock_query_hook
        reason: Verifies the hook is being called (search integration is wired)
```

---

## LOGIC CHAINS

### LC1: Missing Link Detection Chain

**Purpose:** Find Moments without required links and create tasks

```
L1 Brain Graph
  -> _scan_missing_links(actor_id, adapter)     # Batch Cypher: find unlinked Moments
    -> describe_links(moment)                   # Format existing links as context
      -> task_exists(deterministic_id)           # Check for existing gap task
        -> create_task() OR refresh_energy()     # Write to graph
          -> GapDescriptor                       # Return to caller
```

**Data transformation:**
- Input: `actor_id` (str) — which citizen's brain to scan
- After Cypher: `list[Moment]` — Moments missing link types
- After context assembly: `list[GapDescriptor]` — enriched with content and questions
- Output: `{gaps_found, tasks_created, tasks_refreshed}` — summary

### LC2: Duplicate Detection Chain

**Purpose:** Find similar nodes and create merge-candidate tasks

```
L1 Brain Graph
  -> _scan_duplicates(actor_id, adapter, embed_fn)  # Load embeddings for node type
    -> cosine_similarity(A.embedding, B.embedding)    # Pairwise comparison
      -> build_duplicate_context(A, B, sim)            # Side-by-side comparison text
        -> task_exists(deterministic_id)                # Dedup check
          -> create_task()                              # Write to graph
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/cognition/gap_detector.py
    └── imports -> runtime/organization/task_physics.py (create_task)
    └── imports -> runtime/cognition/gap_detection_constants.py
    └── imports -> runtime/cognition/gap_detection_heuristics.py

runtime/cognition/gap_query_hook.py
    └── imports -> runtime/cognition/gap_detection_constants.py
    └── imports -> runtime/cognition/gap_detection_heuristics.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `hashlib` | Deterministic task IDs | `gap_detector.py` |
| `math` | Logarithmic energy increment | `gap_query_hook.py` |
| `numpy` (if available) | Cosine similarity | `gap_detector.py` |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `GAP_SCAN_INTERVAL` | `gap_detection_constants.py` | 100 | Run gap scan every N physics ticks |
| `COSINE_DUPLICATE_THRESHOLD` | `gap_detection_constants.py` | 0.85 | Minimum cosine similarity for duplicate candidates |
| `MAX_CANDIDATES_PER_SCAN` | `gap_detection_constants.py` | 50 | Cap on duplicate pairs per scan |
| `MISSING_ACTOR_ENERGY` | `gap_detection_constants.py` | 0.5 | Initial energy for missing Actor link tasks |
| `MISSING_SPACE_ENERGY` | `gap_detection_constants.py` | 0.4 | Initial energy for missing Space link tasks |
| `MISSING_THING_ENERGY` | `gap_detection_constants.py` | 0.3 | Initial energy for missing Thing link tasks |
| `EMPTY_QUERY_RESONANCE_THRESHOLD` | `gap_detection_constants.py` | 0.3 | Below this, query results count as "empty" |
| `EMPTY_QUERY_MIN_WORDS` | `gap_detection_constants.py` | 3 | Minimum words for a query to generate a gap marker |
| `SMALL_GRAPH_NODE_THRESHOLD` | `gap_detection_constants.py` | 20 | Graphs below this size get lower initial gap energy |
| `SMALL_GRAPH_INITIAL_ENERGY` | `gap_detection_constants.py` | 0.2 | Initial energy for gaps in small graphs |
| `NORMAL_INITIAL_ENERGY` | `gap_detection_constants.py` | 0.5 | Initial energy for gaps in normal-sized graphs |

---

## MARKERS

<!-- @mind:todo Wire scan_gaps() into the L1 tick runner — determine exact integration point -->
<!-- @mind:todo Wire on_query_result() hook into graph_queries_search.py return path -->
<!-- @mind:proposition Consider exposing gap detection as an MCP tool so citizens can trigger scans on-demand -->
