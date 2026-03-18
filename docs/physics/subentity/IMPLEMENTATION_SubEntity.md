# SubEntity Traversal Engine — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
BEHAVIORS:       ./BEHAVIORS_SubEntity.md
PATTERNS:        ./PATTERNS_SubEntity.md
ALGORITHM:       ./ALGORITHM_SubEntity.md
VALIDATION:      ./VALIDATION_SubEntity.md
THIS:            IMPLEMENTATION_SubEntity.md (you are here)
HEALTH:          ./HEALTH_SubEntity.md
SYNC:            ./SYNC_SubEntity.md

IMPL:            runtime/physics/subentity.py
                 runtime/physics/exploration.py
                 runtime/physics/link_scoring.py
                 runtime/physics/crystallization.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/physics/
├── subentity.py             # SubEntity dataclass, state machine, energy injection, link scoring (in-file)
├── exploration.py           # ExplorationRunner, GraphInterface, async state handlers
├── link_scoring.py          # Link score formula, branch detection, polarity/permanence
├── crystallization.py       # Crystallization embedding, novelty check, narrative creation
├── flow.py                  # Energy flow primitives (inject_node_energy, backward_color_path)
├── synthesis.py             # Narrative text generation (synthesize_from_crystallization)
├── traversal_logger.py      # Step-by-step exploration logging
├── cluster_presentation.py  # Result presentation as readable clusters
└── constants.py             # Shared constants (COLD_THRESHOLD, TOP_N_LINKS)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `subentity.py` | SubEntity dataclass, ExplorationContext, state machine, energy injection, in-file link scoring, factory | `SubEntity`, `ExplorationContext`, `SubEntityState`, `VALID_TRANSITIONS`, `STATE_MULTIPLIER`, `compute_link_score`, `create_subentity`, `should_child_crystallize` | ~1044 | SPLIT |
| `exploration.py` | Async exploration runner with per-state handlers, GraphInterface, ExplorationResult | `ExplorationRunner`, `GraphInterface`, `ExplorationConfig`, `ExplorationResult`, `run_exploration`, `present_exploration_result` | ~1110 | SPLIT |
| `link_scoring.py` | Link scoring formula, permanence, polarity, self-novelty, sibling divergence, branch detection | `calculate_link_score`, `score_outgoing_links`, `should_branch`, `select_branch_candidates`, `get_target_node_id`, `calculate_permanence`, `get_polarity` | ~380 | OK |
| `crystallization.py` | Crystallization embedding computation, novelty checking, narrative creation, link generation | `compute_crystallization_embedding`, `check_novelty`, `crystallize`, `CrystallizedNarrative`, `SubEntityCrystallizationState`, `generate_crystallization_links` | ~506 | WATCH |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size
- **WATCH** (400-700 lines): Getting large
- **SPLIT** (>700 lines): Must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** State Machine + Async Coroutine Tree

**Why this pattern:** The SubEntity state machine provides rigid, validated transitions that prevent invalid behavior. The async coroutine tree (parent spawns children, awaits them, merges results) maps naturally to graph branching. asyncio.gather enables concurrent child exploration without threading complexity.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| State Machine | `SubEntity.state`, `VALID_TRANSITIONS` | Enforce valid exploration lifecycle |
| Lazy Reference (Registry) | `ExplorationContext`, `parent_id`/`sibling_ids`/`children_ids` | Break circular references, enable serialization |
| Factory | `create_subentity()` | Consistent initialization with defaults and optional context registration |
| Strategy | `GraphInterface` (dataclass of callables) | Abstract graph operations for testability |
| Template Method | `ExplorationRunner._run_subentity()` dispatching to `_step_{state}()` | Per-state behavior with shared loop structure |

### Anti-Patterns to Avoid

- **Fallback scoring**: If a link has no embedding, the score should be 0.5 (neutral), not 0.0. A score of 0.0 eliminates the link entirely. The current code correctly uses 0.5 as the semantic fallback in `calculate_link_score()`.
- **Mutable default arguments**: SubEntity fields use `field(default_factory=...)` for all list/dict defaults. Never use `[]` or `{}` as defaults.
- **Direct state assignment in handlers**: Handlers should use `se.transition_to()` (validated) not `se.state = ...` (unchecked). Exception: `_step_merging` and the depth check in `_run_subentity` which set terminal states directly.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| SubEntity state | State machine, energy injection, crystallization embedding | Graph queries, narrative creation | `SubEntity` dataclass methods |
| ExplorationRunner | State dispatch, timeout, step logging | Graph storage, embedding computation | `GraphInterface` (abstract callables) |
| Link scoring | Score formula, branch detection | Traversal decisions | `score_outgoing_links()`, `should_branch()` |
| Crystallization | Embedding computation, novelty check | Graph persistence | `crystallize()`, `CrystallizedNarrative` |

---

## SCHEMA

### SubEntity (runtime dataclass)

```yaml
SubEntity:
  required:
    - id: str                              # "se_{uuid8}"
    - actor_id: str                        # Spawning actor
    - state: SubEntityState                # Current state
    - position: str                        # Current node ID
    - path: List[Tuple[str, str]]          # [(link_id, node_id), ...]
    - depth: int                           # Current depth
    - query: str                           # What to find
    - found_narratives: Dict[str, float]   # {id: max_alignment}
    - satisfaction: float                  # [0, 1]
  optional:
    - origin_moment: str                   # Triggering moment
    - parent_id: str                       # Parent SubEntity ID
    - query_embedding: List[float]         # Embedding of query
    - intention: str                       # Why finding it
    - intention_embedding: List[float]     # Embedding of intention
    - crystallization_embedding: List[float]  # Evolving embedding
    - crystallized: str                    # Created narrative ID
  constraints:
    - satisfaction in [0.0, 1.0]
    - depth >= 0
    - state must be in SubEntityState enum
```

### ExplorationResult

```yaml
ExplorationResult:
  required:
    - subentity_id: str
    - actor_id: str
    - state: SubEntityState
    - found_narratives: Dict[str, float]
    - satisfaction: float
    - depth: int
    - duration_s: float
  optional:
    - origin_moment: str
    - crystallized: str
    - children_results: List[ExplorationResult]
```

### CrystallizedNarrative

```yaml
CrystallizedNarrative:
  required:
    - id: str                              # Empty if not novel
    - embedding: List[float]
    - synthesis: str
    - found_narratives: List[Tuple[str, float]]
    - created_at_s: int
    - is_novel: bool
    - max_similarity: float
  optional:
    - origin_moment: str
    - most_similar_id: str
```

---

## ENTRY POINTS

| Entry Point | File:Function | Triggered By |
|-------------|---------------|--------------|
| Exploration start | `exploration.py:ExplorationRunner.explore()` | `graph_query` MCP tool, `subcall` MCP tool, physics tick |
| Sync exploration | `exploration.py:run_exploration_sync()` | Synchronous callers (scripts, tests) |
| Result presentation | `exploration.py:present_exploration_result()` | Post-exploration formatting for MCP response |
| SubEntity factory | `subentity.py:create_subentity()` | ExplorationRunner.explore() |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Exploration Flow: Query to Result

This is the primary flow. It transforms a natural-language query into structured exploration results, creating graph side effects along the way.

```yaml
flow:
  name: exploration_query_to_result
  purpose: Transform query+intention into found narratives and crystallized knowledge
  scope: From explore() call to ExplorationResult return
  steps:
    - id: create_root
      description: Create root SubEntity with query, intention, embeddings
      file: runtime/physics/exploration.py
      function: ExplorationRunner.explore()
      input: actor_id, query, query_embedding, intention, intention_embedding
      output: SubEntity registered in ExplorationContext
      trigger: MCP tool call (graph_query, subcall) or physics tick
      side_effects: SubEntity registered in ExplorationContext._registry

    - id: state_loop
      description: Run state machine loop dispatching to per-state handlers
      file: runtime/physics/exploration.py
      function: ExplorationRunner._run_subentity()
      input: SubEntity in active state
      output: SubEntity in MERGING state
      trigger: explore() after root creation
      side_effects: Graph node energy/weight modified, new narratives created, links colored

    - id: link_scoring
      description: Score outgoing links at each SEEKING step
      file: runtime/physics/link_scoring.py
      function: score_outgoing_links()
      input: links, from_node_id, intention_embedding, path_embeddings, sibling_embeddings
      output: Sorted list of (link, score, components)
      trigger: _step_seeking() at each position
      side_effects: None (read-only scoring)

    - id: energy_injection
      description: Inject energy into traversed node
      file: runtime/physics/flow.py
      function: inject_node_energy()
      input: node dict, criticality, state_multiplier
      output: Modified node with increased energy
      trigger: _step_seeking(), _step_absorbing()
      side_effects: node.energy increased, node.weight may increase

    - id: crystallization
      description: Create new narrative from exploration
      file: runtime/physics/exploration.py
      function: ExplorationRunner._step_crystallizing()
      input: SubEntity with crystallization_embedding, path, found_narratives
      output: New narrative node and links in graph
      trigger: State transition to CRYSTALLIZING
      side_effects: New narrative node created, 2 links created, path links colored

    - id: collect_result
      description: Assemble final ExplorationResult from completed SubEntity
      file: runtime/physics/exploration.py
      function: collect_result()
      input: Completed SubEntity (MERGING state)
      output: ExplorationResult dataclass
      trigger: explore() after state loop completes
      side_effects: None

  docking_points:
    guidance:
      include_when: State transitions, energy mutations, narrative creation
      omit_when: Internal scoring computations, embedding math
      selection_notes: Focus on graph-mutating steps and state boundaries
    available:
      - id: dock_explore_entry
        type: api
        direction: input
        file: runtime/physics/exploration.py
        function: ExplorationRunner.explore()
        trigger: MCP tool call
        payload: actor_id, query, query_embedding, intention, intention_embedding
        async_hook: required
        needs: none
        notes: Primary entry point for all graph exploration

      - id: dock_state_transition
        type: event
        direction: output
        file: runtime/physics/subentity.py
        function: SubEntity.transition_to()
        trigger: Every state change
        payload: old_state, new_state, SubEntity.id
        async_hook: not_applicable
        needs: add event emission for monitoring
        notes: State transitions are the heartbeat of exploration

      - id: dock_energy_injection
        type: graph_ops
        direction: output
        file: runtime/physics/flow.py
        function: inject_node_energy()
        trigger: Every SEEKING and ABSORBING step
        payload: node_id, energy_injected, weight_gained
        async_hook: optional
        needs: none
        notes: Mutates graph node energy and weight

      - id: dock_narrative_creation
        type: graph_ops
        direction: output
        file: runtime/physics/exploration.py
        function: _step_crystallizing()
        trigger: CRYSTALLIZING state entry
        payload: narrative_id, embedding, synthesis, linked_node_ids
        async_hook: required
        needs: none
        notes: Creates new knowledge in the graph

      - id: dock_result_return
        type: api
        direction: output
        file: runtime/physics/exploration.py
        function: collect_result()
        trigger: Exploration completion
        payload: ExplorationResult
        async_hook: not_applicable
        needs: none
        notes: Final result returned to caller

    health_recommended:
      - dock_id: dock_state_transition
        reason: State transition monitoring catches invalid transitions and infinite loops
      - dock_id: dock_energy_injection
        reason: Energy injection correctness is V3 (HIGH priority invariant)
      - dock_id: dock_narrative_creation
        reason: Narrative quality is V4 (HIGH priority — no duplicates)
```

---

## LOGIC CHAINS

### LC1: Query to Narratives

**Purpose:** Find existing narratives relevant to a query

```
explore(actor_id, query, embedding)
  -> create_subentity() -> SubEntity(SEEKING)
    -> _step_seeking() -> score_outgoing_links()
      -> traverse best link -> inject_node_energy()
        -> if narrative: _step_resonating() -> found_narratives[id] = alignment
          -> if satisfied: MERGING -> collect_result()
```

**Data transformation:**
- Input: `(str, str, List[float])` — actor, query text, embedding
- After scoring: `List[(link, score, components)]` — ranked candidates
- After resonating: `Dict[str, float]` — narrative IDs with alignments
- Output: `ExplorationResult` — found narratives, satisfaction, depth, duration

### LC2: Exploration to Crystallization

**Purpose:** Create new knowledge when exploration discovers novel patterns

```
explore(actor_id, query, embedding)
  -> SubEntity(SEEKING) -> traverse -> no matching narratives
    -> REFLECTING (satisfaction <= 0.5)
      -> CRYSTALLIZING
        -> compute crystallization_embedding
        -> check_novelty (< 0.85)
        -> create_narrative() -> create_link() x 2
        -> backward_color_path()
        -> MERGING -> collect_result()
```

**Data transformation:**
- Input: `(str, str, List[float])` — actor, query, embedding
- After path traversal: `List[(link_id, node_id)]` — traversal path
- After crystallization: `CrystallizedNarrative` with embedding, synthesis, links
- Output: `ExplorationResult` with `crystallized = narrative_id`

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
exploration.py
    └── imports -> subentity.py (SubEntity, ExplorationContext, create_subentity, STATE_MULTIPLIER)
    └── imports -> link_scoring.py (score_outgoing_links, get_target_node_id, should_branch, select_branch_candidates)
    └── imports -> crystallization.py (compute_crystallization_embedding, check_novelty)
    └── imports -> flow.py (inject_node_energy, backward_color_path, blend_embeddings, regenerate_node_synthesis_if_drifted, add_node_weight_on_resonating)
    └── imports -> synthesis.py (synthesize_from_crystallization)
    └── imports -> cluster_presentation.py (present_cluster, ClusterNode, ClusterLink, RawCluster)
    └── imports -> traversal_logger.py (DecisionInfo, LinkCandidate, MovementInfo)

subentity.py
    └── imports -> (no internal deps — self-contained dataclass + scoring)

link_scoring.py
    └── imports -> (no internal deps — standalone scoring)

crystallization.py
    └── imports -> link_scoring.py (cosine_similarity, max_cosine_against_set)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `asyncio` | Concurrent child exploration, timeout | `exploration.py` |
| `dataclasses` | SubEntity, ExplorationResult, GraphInterface, configs | All files |
| `uuid` | SubEntity ID generation, narrative ID generation | `subentity.py`, `crystallization.py` |
| `time` | Duration tracking, timestamps | `exploration.py`, `crystallization.py` |
| `math.sqrt` | Permanence calculation | `link_scoring.py` |
| `enum.Enum` | SubEntityState | `subentity.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| SubEntity instances | `ExplorationContext._registry` | Per-exploration | Created at explore(), garbage collected after result collection |
| Step counter | `ExplorationRunner._step_counter` | Per-runner | Lives for runner lifetime |
| Tick counter | `ExplorationRunner._tick` | Per-runner | Incremented externally |

### State Transitions

```
SEEKING ──(narrative found)──> RESONATING
SEEKING ──(branch point)──> BRANCHING
SEEKING ──(no links)──> REFLECTING
SEEKING ──(content node)──> ABSORBING
BRANCHING ──(children done)──> REFLECTING
ABSORBING ──(high alignment+novelty)──> CRYSTALLIZING
ABSORBING ──(low alignment)──> SEEKING
RESONATING ──(satisfied)──> MERGING
RESONATING ──(unsatisfied)──> SEEKING
REFLECTING ──(satisfied)──> MERGING
REFLECTING ──(unsatisfied)──> CRYSTALLIZING
CRYSTALLIZING ──(always)──> MERGING
MERGING ──(terminal)──> [end]
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| ExplorationRunner | async (single-threaded event loop) | Each SubEntity runs as a coroutine |
| Child branching | asyncio.gather | Children run concurrently, not parallel |
| Graph operations | async callables in GraphInterface | Database I/O is awaited |
| Embedding computation | synchronous (pure Python math) | CPU-bound; does not yield to event loop |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `max_depth` | `ExplorationConfig` | 10 | Maximum traversal depth per SubEntity |
| `max_children` | `ExplorationConfig` | 3 | Maximum branches at one point |
| `timeout_s` | `ExplorationConfig` | 30.0 | Hard timeout in seconds |
| `min_branch_links` | `ExplorationConfig` | 2 | Minimum scored links to trigger branching |
| `satisfaction_threshold` | `ExplorationConfig` | 0.8 | Satisfaction level to stop exploring |
| `novelty_threshold` | `ExplorationConfig` / `crystallization.py` | 0.85 | Max similarity for narrative creation |
| `min_link_score` | `ExplorationConfig` | 0.1 | Minimum link score to consider traversal |
| `INTENTION_WEIGHT` | `subentity.py` | 0.25 | Weight of intention vs query in link scoring |
| `STATE_MULTIPLIER` | `subentity.py` | See table | Per-state energy injection multiplier |
| `CRYSTALLIZATION_WEIGHTS` | `crystallization.py` | intention=0.4, position=0.3, found=0.2, path=0.1 | Embedding component weights |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Line | Reference |
|------|------|-----------|
| `subentity.py` | 7 | `DOCS: docs/schema/ALGORITHM_Schema.md` |
| `exploration.py` | 27 | `DOCS: docs/physics/ALGORITHM_Physics.md (v1.8 SubEntity section)` |
| `link_scoring.py` | 21 | `DOCS: docs/physics/ALGORITHM_Physics.md (v1.7.2 SubEntity section)` |
| `crystallization.py` | 14 | `DOCS: docs/physics/ALGORITHM_Physics.md (v1.6.1 CRYSTALLIZING section)` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 2 (state loop) | `exploration.py:ExplorationRunner._run_subentity()` |
| ALGORITHM Step 3 (SEEKING) | `exploration.py:ExplorationRunner._step_seeking()` |
| ALGORITHM Step 4 (BRANCHING) | `exploration.py:ExplorationRunner._step_branching()` |
| ALGORITHM Step 5 (ABSORBING) | `exploration.py:ExplorationRunner._step_absorbing()` |
| ALGORITHM Step 6 (RESONATING) | `exploration.py:ExplorationRunner._step_resonating()` |
| ALGORITHM Step 7 (REFLECTING) | `exploration.py:ExplorationRunner._step_reflecting()` |
| ALGORITHM Step 8 (CRYSTALLIZING) | `exploration.py:ExplorationRunner._step_crystallizing()` |
| ALGORITHM D1 (link score) | `subentity.py:compute_link_score()`, `link_scoring.py:calculate_link_score()` |
| BEHAVIOR B4 (energy injection) | `subentity.py:SubEntity.inject_energy_to_node()`, `flow.py:inject_node_energy()` |
| VALIDATION V1 (transitions) | `subentity.py:SubEntity.transition_to()`, `VALID_TRANSITIONS` |
| VALIDATION V4 (novelty) | `crystallization.py:check_novelty()` |

---

## EXTRACTION CANDIDATES

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `subentity.py` | ~1044L | <400L | `subentity_scoring.py` | `cosine_similarity`, `compute_self_novelty`, `compute_sibling_divergence`, `compute_link_score` (lines 821-958) — these duplicate functions in `link_scoring.py` |
| `subentity.py` | ~1044L | <400L | `subentity_tree.py` | `run_child`, `set_sibling_references`, `merge_child_results`, `should_child_crystallize` (lines 670-988) — tree operations |
| `exploration.py` | ~1110L | <400L | `exploration_handlers.py` | `_step_seeking`, `_step_branching`, `_step_absorbing`, `_step_resonating`, `_step_reflecting`, `_step_crystallizing`, `_step_merging` (lines 380-914) — per-state handlers |
| `exploration.py` | ~1110L | <400L | `exploration_presentation.py` | `present_exploration_result` (lines 1016-1111) — presentation concerns |

---

## MARKERS

<!-- @mind:todo subentity.py contains duplicate link scoring functions (cosine_similarity, compute_link_score) that also exist in link_scoring.py — consolidate -->
<!-- @mind:todo exploration.py at SPLIT threshold — extract per-state handlers into exploration_handlers.py -->
<!-- @mind:proposition GraphInterface should be a Protocol (typing.Protocol) rather than a dataclass of callables, for better type checking -->
