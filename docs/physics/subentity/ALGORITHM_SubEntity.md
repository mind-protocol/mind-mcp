# SubEntity Traversal Engine — Algorithm: State Machine, Link Scoring, and Crystallization

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against runtime/physics/subentity.py v2.1
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
BEHAVIORS:       ./BEHAVIORS_SubEntity.md
PATTERNS:        ./PATTERNS_SubEntity.md
THIS:            ALGORITHM_SubEntity.md (you are here)
VALIDATION:      ./VALIDATION_SubEntity.md
HEALTH:          ./HEALTH_SubEntity.md
IMPLEMENTATION:  ./IMPLEMENTATION_SubEntity.md
SYNC:            ./SYNC_SubEntity.md

IMPL:            runtime/physics/subentity.py
                 runtime/physics/exploration.py
                 runtime/physics/link_scoring.py
                 runtime/physics/crystallization.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The SubEntity traversal engine walks the knowledge graph by evaluating outgoing links at each node, following the most semantically aligned path, branching at decision points, and crystallizing new narratives when exploration discovers novel patterns. The engine operates as an async state machine with 7 states, dispatched by the ExplorationRunner. At every step, energy is injected into traversed nodes proportional to the SubEntity's criticality and state, creating heat trails that persist in the graph.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Semantic graph traversal | B1, B3, B7 | Link scoring formula directs traversal toward relevant content |
| Knowledge crystallization | B5 | CRYSTALLIZING state creates new narrative nodes with novelty gating |
| Energy injection | B4, B8 | Heat trails and path backpropagation connect traversal to physics |
| Bounded exploration | B6, E4, E5 | Fatigue detection, depth limits, and timeout prevent runaway walks |
| Parallel branching | B2 | BRANCHING spawns children with divergence scoring |

---

## DATA STRUCTURES

### SubEntity

```
SubEntity:
  Identity:
    id: str                     # "se_{uuid8}" — unique per exploration
    actor_id: str               # Who spawned this exploration
    origin_moment: str          # Moment that triggered it

  Tree Structure (lazy refs):
    parent_id: str | None       # Parent SubEntity ID (null for root)
    sibling_ids: List[str]      # IDs of other children of same parent
    children_ids: List[str]     # IDs of spawned children
    _context: ExplorationContext  # Registry for lazy resolution

  State Machine:
    state: SubEntityState       # Current state (7 possible values)
    position: str               # Current node ID in the graph
    run_position: str           # Node ID where this SubEntity was created
    path: List[(link_id, node_id)]  # Full traversal history
    depth: int                  # Current depth (increments each step)

  Awareness (v2.0):
    awareness_depth: [float, float]  # [UP, DOWN] unbounded accumulators
    progress_history: List[float]    # Delta toward intention per step

  Query + Intention (v2.1):
    query: str                       # WHAT to find
    query_embedding: List[float]     # Embedding of query
    intention: str                   # WHY finding it
    intention_embedding: List[float] # Embedding of intention (semantic, not enum)

  Findings:
    found_narratives: Dict[str, float]  # {narrative_id: max_alignment}
    crystallization_embedding: List[float]  # Evolving embedding of what this SE would become
    satisfaction: float                    # [0, 1] how much of intention is satisfied
    crystallized: str | None               # Narrative ID if one was created
```

### ExplorationContext

```
ExplorationContext:
  _registry: Dict[str, SubEntity]  # All active SubEntities by ID

  Methods:
    register(se) -> None           # Add to registry, set se._context
    get(id) -> SubEntity | None    # Lookup by ID
    exists(id) -> bool             # Check existence
    unregister(id) -> None         # Remove from registry
    all_active() -> List[SubEntity]  # Non-terminal SubEntities
```

### ExplorationConfig

```
ExplorationConfig:
  max_depth: int = 10              # Maximum traversal depth
  max_children: int = 3            # Maximum branches at one point
  timeout_s: float = 30.0          # Hard timeout in seconds
  min_branch_links: int = 2        # Minimum links to trigger branching
  satisfaction_threshold: float = 0.8   # Satisfaction to stop exploring
  novelty_threshold: float = 0.85       # Max similarity for crystallization
  min_link_score: float = 0.1           # Minimum score to consider a link
```

---

## ALGORITHM: State Machine Execution

### Step 1: Initialization

The caller invokes `ExplorationRunner.explore()` with actor_id, query, query_embedding, intention, and intention_embedding. A root SubEntity is created via `create_subentity()` and registered with the shared ExplorationContext. The root starts in SEEKING state at the origin_moment (if provided) or at the actor node.

```
root = create_subentity(actor_id, origin_moment, query, query_embedding, intention, intention_embedding, start_position, context)
root.crystallization_embedding = copy(query_embedding)  # Initial crystallization = what we search for
```

### Step 2: State Machine Loop

`_run_subentity(se)` loops while `se.is_active` (not MERGING), dispatching to the handler for the current state. A hard limit of MAX_STEPS=1000 prevents infinite loops.

```
while se.is_active and step_count < 1000:
    dispatch to _step_{state}(se)
    if depth >= max_depth and state in (SEEKING, BRANCHING, ABSORBING):
        force state = REFLECTING
```

### Step 3: SEEKING — Follow Best Link

1. Fetch outgoing links from current position
2. If no links: transition to REFLECTING
3. Collect path embeddings (for self-novelty) and sibling crystallization embeddings (for divergence)
4. Score all links using `score_outgoing_links()` with min_score threshold
5. If no scored links: transition to REFLECTING
6. Check for branching: if position is a Moment node AND 2+ links have positive scores, transition to BRANCHING
7. Take the top-scoring link, advance position, increment depth
8. Inject energy into the target node: `inject_node_energy(node, criticality, STATE_MULTIPLIER[SEEKING])`
9. Update crystallization embedding
10. If target is a narrative: transition to RESONATING
11. If target is a Moment with 2+ outgoing links: transition to BRANCHING
12. Otherwise: stay SEEKING

### Step 4: BRANCHING — Spawn Children

1. Score outgoing links from current position
2. Select up to `max_children` branch candidates (relative score >= 0.5 of top)
3. If only 1 candidate: fall back to SEEKING
4. For each candidate: call `se.run_child(target_position, via_link, context)` — creates child, registers with context, inherits query/intention/embeddings
5. Call `se.set_sibling_references()` — sets sibling_ids for all children
6. Run all children concurrently: `asyncio.gather(*child_tasks)`
7. Merge results: for each child, propagate found_narratives with max(alignment) merge
8. Average children's satisfaction into parent satisfaction
9. Update crystallization embedding
10. Transition to REFLECTING

### Step 5: ABSORBING — Process Content

1. Get current node embedding
2. Compute alignment with intention: `cosine(intention_embedding, node_embedding)`
3. Compute novelty against path embeddings
4. Inject energy: `inject_node_energy(node, criticality, STATE_MULTIPLIER[ABSORBING])`
5. If alignment > 0.7 AND novelty > 0.7: transition to CRYSTALLIZING
6. Otherwise: transition to SEEKING

### Step 6: RESONATING — Measure Narrative Match

1. Get narrative embedding
2. Compute alignment: `cosine(intention_embedding, narrative_embedding)`
3. If alignment > 0: record in `found_narratives` with max(alignment) merge
4. Boost satisfaction: `boost = alignment / (sum_found_alignments + 1)`
5. Add weight to node on resonating: `add_node_weight_on_resonating(node, criticality)`
6. Update crystallization embedding
7. If satisfaction >= 0.8: transition to MERGING (done)
8. If satisfaction < 0.8: transition to SEEKING (continue)

### Step 7: REFLECTING — Backpropagate and Decide

1. If satisfaction > 0.5 and path is non-empty:
   - Fetch all path links
   - Backpropagate color with intention embedding (attenuation 0.8/hop, permanence boost = 0.05 x satisfaction)
   - Persist colored links to graph
2. If satisfaction > 0.5: transition to MERGING
3. If satisfaction <= 0.5: transition to CRYSTALLIZING

### Step 8: CRYSTALLIZING — Create New Narrative

1. Get run_node and focus_node data
2. Compute mean hierarchy/permanence from path links
3. Generate narrative name via `synthesize_from_crystallization()`
4. Create narrative node with crystallization_embedding
5. Create links: run_node -> narrative and narrative -> focus_node
6. Set `se.crystallized = narrative_id`
7. Update satisfaction (crystallization counts as finding something)
8. Backpropagate color along path with crystallization embedding
9. Transition to MERGING (always, v2.0.1 — prevents infinite loop)

### Step 9: MERGING — Terminal State

1. Mark completion time
2. State is MERGING (terminal, no transitions out)
3. Results are collected by parent (if any) or returned as ExplorationResult

---

## KEY DECISIONS

### D1: Link Score Formula

```
query_alignment = cosine(query_embedding, link_embedding)
intention_alignment = cosine(intention_embedding, link_embedding)
alignment = 0.75 x query_alignment + 0.25 x intention_alignment

score = alignment x polarity x (1 - permanence) x self_novelty x sibling_divergence
```

**Why this formula:**
- Query dominates (75%) because WHAT to find matters more than WHY
- `(1 - permanence)` means less permanent (newer, lighter) links are more explorable
- Self-novelty prevents backtracking (penalizes links similar to path)
- Sibling divergence prevents children from exploring the same direction

### D2: Branching Only on Moment Nodes

```
IF position.node_type == 'moment' AND scored_links >= 2:
    BRANCH
ELSE:
    FOLLOW best link
```

**Why moments:** Moments represent events, decisions, interactions — natural fork points in the narrative graph. Branching on actor or thing nodes would branch on structural adjacency, not narrative decision points.

### D3: Children Crystallize, Parents Don't Aggregate (v2.0)

```
IF child found 90%+ match narrative:
    DON'T crystallize (knowledge exists)
ELSE:
    CRYSTALLIZE to graph (persist the journey)
```

**Why no propagation:** The graph is the source of truth. Having children propagate results to parents creates a parallel memory system. With crystallization, child discoveries live in the graph where anyone can find them.

### D4: Crystallization Always Goes to MERGING (v2.0.1)

```
After creating narrative:
    ALWAYS transition to MERGING
    NEVER return to SEEKING
```

**Why:** The original design allowed CRYSTALLIZING -> SEEKING if satisfaction was low. This caused infinite loops: low satisfaction -> crystallize -> seek -> reflect -> low satisfaction -> crystallize. Crystallization IS a result. After creating a narrative, the SubEntity's job is done.

### D5: Fatigue Window = 5 Steps, Threshold = 0.05

```
IF last 5 progress_history deltas all have |delta| < 0.05:
    SubEntity is fatigued (should stop)
```

**Why these values:** 5 steps gives enough signal to distinguish plateau from temporary dip. 0.05 threshold accounts for floating-point noise while catching genuine stagnation.

---

## DATA FLOW

```
query + intention + embeddings
    |
    v
create_subentity() -> SubEntity(SEEKING, position=start)
    |
    v
_run_subentity() loop:
    |
    +-> SEEKING: score_outgoing_links() -> traverse best link
    |       |                                   |
    |       +-> inject_node_energy()            +-> update_crystallization_embedding()
    |       |
    |       +-> if narrative: -> RESONATING
    |       +-> if branch:    -> BRANCHING
    |
    +-> BRANCHING: spawn children -> asyncio.gather -> merge results
    |
    +-> ABSORBING: check alignment+novelty -> CRYSTALLIZING or SEEKING
    |
    +-> RESONATING: measure alignment -> update satisfaction -> MERGING or SEEKING
    |
    +-> REFLECTING: backprop color -> MERGING or CRYSTALLIZING
    |
    +-> CRYSTALLIZING: create_narrative() + create_link() -> MERGING
    |
    +-> MERGING: terminal
    |
    v
collect_result() -> ExplorationResult
```

---

## COMPLEXITY

**Time:** O(D x L x E) per SubEntity — where D=max_depth, L=average outgoing links, E=embedding dimension. Link scoring computes cosine similarity for each candidate link at each depth level. Branching multiplies by up to `max_children` (3).

**Space:** O(D x E + N) — path stores (link_id, node_id) pairs up to depth D, crystallization embedding is E-dimensional, found_narratives grows with discovered narratives N. ExplorationContext stores all active SubEntities.

**Bottlenecks:**
- **Embedding fetches** — Each SEEKING step fetches path embeddings and sibling embeddings from the graph. For deep explorations (depth 10) with many path links, this means 10+ graph queries per step.
- **Cosine similarity computation** — Pure Python loop over embedding dimensions. For high-dimensional embeddings (768+), this is slow. Consider numpy if profiling shows this is a bottleneck.
- **Concurrent children** — Branching runs children via asyncio.gather, which is concurrent but not parallel (single-threaded event loop). CPU-bound embedding comparisons don't benefit from async.

---

## HELPER FUNCTIONS

### `cosine_similarity(a, b)`

**Purpose:** Compute cosine similarity between two embedding vectors.

**Logic:** dot(a,b) / (norm(a) x norm(b)). Returns 0.0 if either vector is None, empty, or zero-norm. Defined in both `subentity.py` (with None-checking) and `link_scoring.py` (stricter typing).

### `compute_self_novelty(subentity, link_embedding, path_embeddings)`

**Purpose:** Penalize links similar to already-traversed path to prevent backtracking.

**Logic:** `1 - max(cosine(link_embedding, p) for p in path_embeddings)`. Returns 1.0 if no path exists (fully novel).

### `compute_sibling_divergence(subentity, link_embedding)`

**Purpose:** Penalize links pointing toward where siblings are exploring to spread coverage.

**Logic:** `1 - max(cosine(link_embedding, s.crystallization_embedding) for s in active_siblings)`. Returns 1.0 if no siblings.

### `should_child_crystallize(child)`

**Purpose:** Determine if a child should crystallize after merging (v2.0).

**Logic:** If child found a narrative with alignment >= 0.9, return False (knowledge exists). Otherwise return True (crystallize the journey).

### `create_subentity(actor_id, origin_moment, query, ...)`

**Purpose:** Factory function to create and optionally register a root SubEntity.

**Logic:** Defaults intention to query if not provided. Defaults intention_embedding to query_embedding. Defaults start_position to actor_id. Registers with ExplorationContext if provided.

### `compute_crystallization_embedding(intention, position, found, path)`

**Purpose:** Compute the final crystallization embedding from multiple sources.

**Logic:** Weighted sum: intention (0.4), position (0.3), mean(found narratives) (0.2), mean(path links) (0.1). Normalized by total weight.

### `check_novelty(embedding, existing, threshold=0.85)`

**Purpose:** Determine if a crystallization embedding is sufficiently novel.

**Logic:** Compute max cosine similarity against all existing narrative embeddings. Novel if max_sim < threshold.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/physics/flow.py` | `inject_node_energy(node, criticality, state_mult)` | Energy injection into graph node |
| `runtime/physics/flow.py` | `backward_color_path(path_links, final_embedding, ...)` | Colored links with attenuated embedding signal |
| `runtime/physics/flow.py` | `blend_embeddings(a, b, ratio)` | Blended embedding for post-crystallization update |
| `runtime/physics/flow.py` | `regenerate_node_synthesis_if_drifted(node, ...)` | Regenerated synthesis text if embedding drifted |
| `runtime/physics/synthesis.py` | `synthesize_from_crystallization(intention, found, path)` | (name, content) tuple for new narrative |
| `runtime/physics/cluster_presentation.py` | `present_cluster(raw_cluster, ...)` | PresentedCluster with markdown rendering |

---

## MARKERS

<!-- @mind:todo Consider extracting the BRANCHING merge logic (lines 578-593 of exploration.py) into a separate function for testability -->
<!-- @mind:proposition The cosine_similarity function exists in both subentity.py and link_scoring.py — consolidate to one canonical location -->
