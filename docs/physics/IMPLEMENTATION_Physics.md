# Physics — Implementation: Code Architecture & Runtime

```
STATUS: STABLE (v1.2), IMPLEMENTING (v1.8)
UPDATED: 2025-12-26
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Physics.md
BEHAVIORS:      ./BEHAVIORS_Physics.md
ALGORITHMS:     ./ALGORITHM_Physics.md
VALIDATION:     ./VALIDATION_Physics.md
THIS:           ./IMPLEMENTATION_Physics.md (you are here)
HEALTH:         ./HEALTH_Physics.md
SYNC:           ./SYNC_Physics.md
ARCHIVE:        ./archive/IMPLEMENTATION_Physics_archive_2025-12.md
```

---

## SUMMARY

The physics implementation ensures graph-first orchestration where all state lives in FalkorDB. The system uses a tick-based metabolism (GraphTick) to propagate energy and detect salience flips. This document covers code structure, design patterns, state management, runtime behavior, and module dependencies.

---

## CODE STRUCTURE & RESPONSIBILITIES

### Code Structure Snapshot

- `runtime/physics/tick_v1_2.py`: Main entry point, orchestrates the 8-phase loop.
- `runtime/physics/tick_v1_2_types.py`: Dataclasses for tick results.
- `runtime/physics/tick_v1_2_queries.py`: Helper class for complex graph queries.
- `runtime/physics/phases/`: Directory containing implementation of each phase:
    - `runtime/physics/phases/generation.py`: Phase 1 - Energy generation (proximity-gated).
    - `runtime/physics/phases/moment_draw.py`: Phase 2 - Moments draw from actors.
    - `runtime/physics/phases/moment_flow.py`: Phase 3 - Moments radiate to targets.
    - `runtime/physics/phases/moment_interaction.py`: Phase 4 - Support/contradict between moments.
    - `runtime/physics/phases/narrative_backflow.py`: Phase 5 - Narratives radiate to actors.
    - `runtime/physics/phases/link_cooling.py`: Phase 6 - Links drain to nodes.
    - `runtime/physics/phases/completion.py`: Phase 7 - Mark moments as completed.
    - `runtime/physics/phases/rejection.py`: Phase 8 - Handle rejected moments.
- `runtime/physics/flow.py`: Unified traversal primitives (energy, weight, emotions).
- `runtime/physics/constants.py`: Physics constants and emotion math.
- `runtime/physics/graph/graph_query_utils.py`: Path resistance (Dijkstra) and property extraction.
- `runtime/moment_graph/*`: Traversal helpers for interactions.
- `runtime/models/*`: Pydantic models for nodes and links.

The tick is the orchestrator; it does not store state beyond an ephemeral context.

### v1.6.1 Code Structure (Implemented)

```
runtime/physics/
├── link_scoring.py        # IMPLEMENTED: compute_link_score() with self_novelty, sibling_divergence
├── flow.py                # IMPLEMENTED: forward_color_link(), backward_color_path(), compute_query_emotion()
├── crystallization.py     # IMPLEMENTED: crystallize(), check_novelty(), SubEntityCrystallizationState
├── synthesis.py           # IMPLEMENTED: synthesize_link(), parse_phrase() (bidirectional grammar)
├── exploration.py         # IMPLEMENTED: ExplorationRunner (async), SubEntity, spawn_subentity()
└── subentity.py           # EXISTING: SubEntity dataclass + StateEnum
```

Key v1.6.1 implementations:
- `link_scoring.py`: Link score formula: `semantic × polarity × (1-permanence) × self_novelty × sibling_divergence`
- `flow.py`: Forward/backward coloring, query emotion computation
- `crystallization.py`: Novelty check (cosine > 0.85), SubEntityCrystallizationState
- `synthesis.py`: Bidirectional grammar (floats ↔ phrases) per GRAMMAR_Link_Synthesis.md
- `exploration.py`: Async SubEntity runner with tree structure (parent, siblings, children)
- `runtime/models/links.py`: Added `embedding` field and `permanence` property

### File Responsibilities (Highlight)

| Artifact | Purpose | Owner | Status |
|----------|---------|-------|--------|
| `runtime/physics/tick_v1_2.py` | 8-phase tick orchestrator | GraphTick | v1.2 OK |
| `runtime/physics/phases/*.py` | Individual phase implementations | Physics | v1.2 OK |
| `runtime/physics/tick_v1_2_queries.py` | Complex graph queries | TickQueries | v1.2 OK |
| `runtime/physics/flow.py` | Unified traversal primitives | Physics | v1.2 OK |
| `runtime/physics/graph/graph_query_utils.py` | Dijkstra & property helpers | Utilities | v1.2 OK |
| `runtime/physics/exploration.py` | SubEntity class + async exploration runner | Physics | **v1.6.1 OK** |
| `runtime/physics/link_scoring.py` | Link score with self_novelty, sibling_divergence | Physics | **v1.6.1 OK** |
| `runtime/physics/flow.py` | Forward/backward coloring, query emotions | Physics | **v1.6.1 OK** |
| `runtime/physics/crystallization.py` | Novelty check, narrative creation | Physics | **v1.6.1 OK** |
| `runtime/physics/synthesis.py` | Bidirectional grammar (floats ↔ phrases) | Physics | **v1.6.1 OK** |

### Schema & Entrypoints

- **Moment node:** `id`, `text`, `type`, `status`, `weight`, `energy`.
- **Links (v1.2):** expresses, about, relates, attached_to, contains, leads_to, sequence, primes, can_become.

**Entry points:**
- Physics tick: `runtime/physics/tick.py:run()` invoked by the orchestrator.
- Click traversal: `runtime/moment_graph/traversal.py:handle_click()`.
- Player input: `runtime/infrastructure/api/moments.py`.

---

## DESIGN & RUNTIME PATTERNS

### Design Patterns

- **Graph-first orchestration:** GraphTick reads/writes the graph; all state lives there.
- **Query/Command separation:** `graph_queries` vs `graph_ops` keeps reads and writes distinct.
- **Facades + mixins:** GraphOps composes command mixins (attention split, PRIMES, contradictions) so plumbing stays composable.
- **Observer/Events:** `graph_ops_events.py` emits hooks for downstream listeners without inlining the logic.

### Runtime Patterns

- **Scene as query:** Scenes are query results, not objects.
- **Time passage:** `advance_time(minutes)` called on completed moments to drive ticks.
- **Character movement:** Travel moments update `AT` links and spawn consequence moments.

### Anti-patterns to avoid

- Hidden writes in query helpers.
- Stateful orchestrators that cache moment state instead of always querying the graph.

---

## STATE MANAGEMENT

- **Graph state:** Lives in FalkorDB (`Moment`, `Link`, `Narrative` nodes). No cached state outside the graph.
- **Active pressures:** Derived from contradictions/demands; persist as relationships, not dedicated nodes.
- **Energy:** Stored on node properties; decays each tick.

---

## TICK METABOLISM (FLOWS)

### physics_tick Flow (v1.2)

```
ACTOR (generates energy via proximity)
   ↓ expresses
MOMENT (routes, doesn't generate)
   ↓ about
NODE (receives)
   ↓ relates
NODE (flows)
```

1. Actors generate energy (proximity-gated) — `phases/generation.py`.
2. Active moments draw from actors via `expresses` links — `phases/moment_draw.py`.
3. Moments radiate to targets via `about` links — `phases/moment_flow.py`.
4. Moment interactions (support/contradict) — `phases/moment_interaction.py`.
5. Narratives backflow to actors via `relates` links — `phases/narrative_backflow.py`.
6. Links cool (30% drain to nodes, 10% weight growth) — `phases/link_cooling.py`.
7. Completion processing — `phases/completion.py`.
8. Rejection processing — `phases/rejection.py`.

Salience is computed (weight × energy); flips surface when thresholds cross.

### Logic Chains

- **Flip detection:** Energy crosses threshold → `TickResult.flips` → orchestrator dispatch → handler output.
- **Action queue:** Action moment actualizes → queued by `process_actions` → updates graph (AT, possession, pressure) → cascade occurs.
- **Drama cascade:** One actualization energizes witnesses → new flips follow (B8 behavior).

---

## CONCURRENCY, CONFIG & DEPENDENCIES

### Concurrency & Config

- Physics tick runs synchronously; energy math is linear.
- Handlers execute asynchronously (LLM calls) but writing occurs sequentially through graph ops.
- Configs: `DECAY_RATE`, `BELIEF_FLOW_RATE` stored in `runtime/physics/constants.py`.

### Module Dependencies

- `runtime/infrastructure/orchestration/orchestrator.py` → imports `runtime/physics/tick.py` and `runtime/moment_graph/queries.py`.
- `runtime/physics/tick.py` → reads via `graph_queries.py`, writes via `graph_ops.py`, coordinates `graph_ops_events.py` for listeners.
- `runtime/physics/graph/graph_ops.py` → composes mixins for attention split, PRIMES decay, contradiction pressure.
- `runtime/physics/graph/graph_ops_read_only_interface.py` → consumed by Connectome search + GraphReadOps for seed queries.

**External packages:**
- `falkordb` for graph database access.
- `pydantic` for node/link models.

---

## OBSERVABILITY & LINKS

### Bidirectional Links

- **Code → Docs:** tick, display snaps, cluster monitors point to `docs/physics/PATTERNS_Physics.md` and `algorithms/ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md`.
- **Docs → Code:** ALGORITHM steps map to `_flow_energy_to_narratives`, `_decay_energy`, `_detect_flips`.

### Docking & Observability

- **start:** orchestrator calls GraphTick with elapsed time.
- **flip_output:** returns flip list for handler/canon scheduling.
- **health anchor:** `docs/physics/algorithms/ALGORITHM_Physics_Mechanisms.md` references the per-mechanism functions for monitoring.

---

## PHYSICS-BASED SEARCH (v1.2)

### Overview

Search is unified with graph physics. Instead of computing scores with a formula, queries inject energy into the graph and results emerge from activation.

### Algorithm

```
1. CREATE      query moment (embedding, energy=10.0)
2. BRIDGE      semantic search → link to top-k similar nodes (weight=similarity)
3. CONTEXT     link to actor (EXPRESSES), task/space (ABOUT)
4. TICK(5)     local energy diffusion with semantic + emotional flow
5. FILTER      activated moments connected to actor (max 3 hops)

For each activated moment (top 10):
    6. CREATE   expansion moment → activated + actor
    7. TICK(3)  physics propagates with semantic + emotional flow
    8. COLLECT  activated nodes around root = cluster

9. RETURN      clusters ordered by root energy
```

### Energy Flow Formula (v1.2)

Energy propagation uses the complete semantic + emotional formula:

```
flow = source.energy × link.weight × semantic_sim × (1 + emotional_sim) × FLOW_RATE
```

Where:
- `source.energy`: Current energy of the source node
- `link.weight`: Weight of the traversed link [0-∞]
- `semantic_sim = cos(query_embedding, target.embedding)`: Semantic similarity to query
- `emotional_sim = Σ cos(query_embedding, embed(emotion)) × intensity`: Emotional alignment
- `FLOW_RATE = 0.3`: Fraction of energy that flows per tick

**Why this formula works:**
- **semantic_sim** makes search truly semantic — energy flows toward nodes related to the query
- **emotional_sim** amplifies paths that are emotionally aligned with the query
- The multiplier `(1 + emotional_sim)` ensures emotions boost but don't block flow
- Energy drains from source as it flows, preventing infinite accumulation

**Emotional similarity computation:**
```python
emotional_sim = 0
for emotion_name, intensity in link.emotions.items():
    sim = cos(query_embedding, embed(emotion_name))
    if sim > 0:
        emotional_sim += sim * intensity
```

This embeds each emotion name (e.g., "joy", "anger", "fear") and computes how semantically
aligned it is with the query. A query about "betrayal" will have higher similarity to "anger"
and "guilt" than to "joy", naturally boosting paths with those emotions.

### Step 5: Filter (Actor Connection)

Only moments with path to actor are returned:
```cypher
MATCH (actor)-[*1..3]-(moment:Moment)
WHERE moment.energy > threshold
```

This ensures results are in actor's "perspective" — their reachable subgraph.

### Steps 6-8: Physics-Based Expansion

Expansion is also physics, not static traversal:

```
For each activated moment:
    1. CREATE expansion moment (energy=5.0)
    2. LINK expansion → activated moment (RELATES, direction='expands')
    3. LINK actor → expansion (EXPRESSES, role='expander')
    4. TICK(3) from expansion moment
    5. COLLECT nodes with energy > 0.05 within 2 hops of root
```

The cluster emerges from energy flow, not graph topology.

### Cluster Structure

```python
{
    'root': {'id': 'moment_123', 'energy': 3.2, 'content': '...'},
    'nodes': [
        {'id': 'actor_claude', 'type': 'actor', 'energy': 0.5},
        {'id': 'narrative_oath', 'type': 'narrative', 'energy': 0.3},
    ],
    'expansion_id': 'moment_expand_moment_123_1703520000'
}
```

Nodes are ordered by energy (activation level), not distance.

### Implementation

| File | Purpose |
|------|---------|
| `runtime/physics/graph/graph_queries_search.py` | SearchQueryMixin with `search()` method |
| `runtime/physics/graph/graph_query_utils.py` | Property extraction, path utilities |

### Key Functions

- `search()`: Main API - creates moment, bridges, ticks, returns clusters
- `_create_query_moment()`: Creates Moment node with query embedding
- `_create_semantic_bridges()`: Finds similar nodes, creates RELATES links
- `_tick_local()`: Propagates energy from start node through local subgraph
- `_get_activated_moments()`: Returns moments with energy > threshold
- `_expand_cluster()`: Gets 2-hop neighborhood around activated moment

### Why Physics-Based

| Aspect | Benefit |
|--------|---------|
| Graph-native | Query becomes permanent moment in graph |
| Unified model | No separate scoring formula, just energy flow |
| Contextual | Actor/task context affects results |
| Coherent clusters | Results include connected context, not isolated nodes |
| Graph learns | Repeated queries strengthen paths |

### Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `ticks` | 5 | Energy propagation iterations |
| `top_k_bridges` | 10 | Semantic bridges to create |
| `energy_threshold` | 0.1 | Minimum activation for results |
| `initial_energy` | 10.0 | Energy injected into query moment |

### Usage

```python
from mind.physics.graph.graph_queries import GraphQueries

graph = GraphQueries()
results = graph.search(
    query="Who broke the oath?",
    actor_id="actor_claude",
    embed_fn=get_embedding
)

for cluster in results['clusters']:
    moment = cluster['root']
    print(f"{moment['id']} (energy: {moment['energy']:.2f})")
    for node in cluster['nodes']:
        print(f"  - {node['name']} ({node['type']})")
```

---

## SUBENTITY EXPLORATION (v1.8)

### Overview

SubEntity exploration is the intentional graph traversal system. Unlike physics-based search (which injects energy and lets it propagate), SubEntity exploration follows a state machine with explicit scoring, branching, and crystallization.

**v1.8 Key Change:** Query (WHAT to find) is now separate from Intention (WHY finding).

### End-to-End Flow: Query → Graph → Response

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INPUT                                                         │
│    query: "What does Edmund believe?"  ← WHAT to find           │
│    intention: "summarize his beliefs"  ← WHY finding            │
│    intention_type: SUMMARIZE           ← HOW to traverse        │
│                                                                  │
│    embed(query) → query_embedding                               │
│    embed(intention) → intention_embedding                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1.5. CONTEXT SETUP (Automatic Linking)                          │
│                                                                  │
│    The exploration is automatically bridged to context:         │
│                                                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ ACTIVE ACTOR                                             │  │
│    │   query_moment ──EXPRESSES──→ actor                     │  │
│    │   (the actor doing the exploration)                      │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ OTHER ACTORS IN SPACE                                    │  │
│    │   query_moment ──ABOUT──→ other_actors_at_same_space    │  │
│    │   (who else is relevant to this query)                   │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │ PREVIOUS COMPLETED MOMENT                                │  │
│    │   query_moment ──THEN──→ actor's_last_completed_moment  │  │
│    │   (temporal continuity with recent context)              │  │
│    └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│    FIRST LINK EMBEDDING:                                        │
│    - The EXPRESSES link from query to actor gets               │
│      embedding = intention_embedding (not query!)              │
│    - This colors the exploration path from the start           │
│    - WHY we're searching affects the traversal, not just WHAT  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. SPAWN                                                        │
│    root = create_subentity(                                     │
│        actor_id, query, query_embedding,                        │
│        intention, intention_embedding, intention_type,          │
│        start_position=actor_id, context=ExplorationContext()    │
│    )                                                            │
│                                                                  │
│    Initial state:                                               │
│    - position = actor node                                      │
│    - found_narratives = {}                                      │
│    - satisfaction = 0.0                                         │
│    - state = SEEKING                                            │
│                                                                  │
│    TraversalLogger.exploration_start(exploration_id, actor_id,  │
│        origin_moment, intention, ...)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. STATE MACHINE                                                │
│                                                                  │
│    SEEKING ──┬──→ BRANCHING ──→ (spawn children) ──→ MERGING   │
│              │         ↓                                        │
│              │    (parallel exploration)                        │
│              │                                                  │
│              ├──→ RESONATING ──→ REFLECTING ──→ MERGING        │
│              │         ↓              ↓                         │
│              │   (absorb narrative)  CRYSTALLIZING              │
│              │                            ↓                     │
│              └──→ REFLECTING ────────→ MERGING                 │
│                        ↓                                        │
│                  (backprop colors)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. SEEKING: Link Scoring                                        │
│                                                                  │
│    link_score = semantic × polarity × (1-permanence)            │
│                 × self_novelty × sibling_divergence             │
│                                                                  │
│    v1.8: alignment combines query + intention:                  │
│    alignment = (1 - intent_weight) × query_align                │
│              + intent_weight × intention_align                  │
│                                                                  │
│    ┌──────────────────┬────────────────────────────────────────┐│
│    │ Factor           │ Purpose                                ││
│    ├──────────────────┼────────────────────────────────────────┤│
│    │ semantic         │ cos(query_embedding, link.embedding)   ││
│    │ polarity         │ link.polarity_ab or polarity_ba        ││
│    │ permanence       │ weight / (weight + 1) → prefer newer   ││
│    │ self_novelty     │ 1 - max(cos(link, path)) → no backtrack││
│    │ sibling_diverge  │ 1 - max(cos(link, sibling.cryst))     ││
│    └──────────────────┴────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. BRANCHING: Fork on Moments                                   │
│                                                                  │
│    D5: Simple count threshold                                   │
│    if len(outgoing_links) >= 2 and node.type == "moment":       │
│        for link in top_candidates:                              │
│            child = se.spawn_child(target, link, context)        │
│        se.set_sibling_references()  # sibling_ids for diverge  │
│        await asyncio.gather(*[run(child) for child in children])│
│                                                                  │
│    Sibling divergence ensures children spread to different paths│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. RESONATING: Absorb Narrative                                 │
│                                                                  │
│    alignment = cos(query_embedding, narrative.embedding)        │
│    if alignment > 0:                                            │
│        # D3: dict with max(alignment)                           │
│        se.found_narratives[narrative_id] = max(current, align)  │
│        se.update_satisfaction(alignment)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. COLORING: Forward + Backward                                 │
│                                                                  │
│    Forward (during traversal):                                  │
│        blend_weight = flow / (flow + link.energy + 1)          │
│        color_weight = 1 - permanence  # newer = more colorable │
│        link.embedding = blend(link.emb, traverser.emb, bw×cw)  │
│                                                                  │
│    Backward (after finding):                                    │
│        for link in reversed(path):                              │
│            current_emb = attenuate(current_emb, polarity_ba)   │
│            link.embedding = blend(link.emb, current_emb, 0.3×cw)│
│            link.weight += permanence_boost  # memory trace     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. CRYSTALLIZING: Create New Narrative                          │
│                                                                  │
│    if satisfaction low but novel pattern found:                 │
│        if is_novel(crystallization_embedding, existing):        │
│            name, content = synthesize_from_crystallization(     │
│                intention_text, found_narratives                 │
│            )                                                    │
│            new_id = graph.create_narrative(name, content, emb)  │
│            se.crystallized = new_id                             │
│            se.found_narratives[new_id] = 1.0                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. MERGING: Aggregate Results                                   │
│                                                                  │
│    D3: max(alignment) merge                                     │
│    for child in children:                                       │
│        for narr_id, align in child.found_narratives.items():    │
│            parent.found_narratives[narr_id] = max(              │
│                parent.found_narratives.get(narr_id, 0), align   │
│            )                                                    │
│        if child.crystallized:                                   │
│            parent.found_narratives[child.crystallized] = 1.0    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. OUTPUT: ExplorationResult                                   │
│                                                                  │
│    ExplorationResult(                                           │
│        subentity_id="se_abc123",                                │
│        actor_id="actor_edmund",                                 │
│        found_narratives={                                       │
│            "narr_honor_code": 0.87,                             │
│            "narr_loyalty_oath": 0.72,                           │
│            "narr_new_insight": 1.0,  # crystallized            │
│        },                                                       │
│        crystallized="narr_new_insight",                         │
│        satisfaction=0.85,                                       │
│        depth=4,                                                 │
│        duration_s=1.2,                                          │
│    )                                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 11. POST-PROCESSING: Response Generation                        │
│                                                                  │
│    found_narratives (sorted by alignment)                       │
│         ↓                                                       │
│    Fetch narrative content from graph                           │
│         ↓                                                       │
│    Filter by intention_type:                                    │
│      - SUMMARIZE: top-N rich content                           │
│      - VERIFY: tensions/contradictions                          │
│      - FIND_NEXT: first match only                              │
│      - RETRIEVE: exact match                                    │
│         ↓                                                       │
│    Format response                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Intention Types (v1.8)

| Type | Intent Weight | Behavior |
|------|---------------|----------|
| `SUMMARIZE` | 0.3 | Privilege rich content, wide exploration |
| `VERIFY` | 0.5 | Look for tensions/contradictions |
| `FIND_NEXT` | 0.2 | Stop at first valid match |
| `EXPLORE` | 0.25 | Balanced exploration (default) |
| `RETRIEVE` | 0.1 | Exact match, minimal traversal |

### Crystallization Embedding Formula (v1.8)

Updated continuously at EACH step:

```
crystallization_embedding = weighted_sum([
    (0.4, query_embedding),           # What we searched for
    (intent_weight, intention_embedding),  # Why we searched
    (0.3, position.embedding),        # Where we are
    (0.2, mean(found.embedding × alignment)),  # What we found
    (0.1, mean(path.embedding))       # How we got here
])
```

### Key Implementation Files

| File | Responsibility |
|------|----------------|
| `runtime/physics/subentity.py` | SubEntity dataclass, ExplorationContext, state machine |
| `runtime/physics/exploration.py` | ExplorationRunner (async), ExplorationResult |
| `runtime/physics/link_scoring.py` | score_outgoing_links(), should_branch() |
| `runtime/physics/flow.py` | forward_color_link(), backward_color_path() |
| `runtime/physics/crystallization.py` | check_novelty(), crystallize() |
| `runtime/physics/synthesis.py` | synthesize_from_crystallization() |

### v1.7.2 Design Decisions

| ID | Decision |
|----|----------|
| D1 | sibling_ids are strings, resolved via ExplorationContext (lazy refs) |
| D3 | found_narratives is dict[str, float] with max(alignment) merge |
| D4 | Timeout errors loudly, crashes exploration, no partial merge |
| D5 | Branch threshold is simple count: len(outgoing) >= 2 |
| D6 | Link embedding = embed(synthesis) at creation |

### TraversalLogger (v1.0)

Agent-comprehensible logging of every SubEntity traversal step.

**Location:** `runtime/physics/traversal_logger.py`

**Features:**
- Natural language explanations for decisions
- "Why not" reasoning for rejected link candidates
- Counterfactual analysis
- Anomaly detection (backtracking, satisfaction plateau, deep exploration)
- Causal chain tracking
- Decision confidence scores
- State machine diagrams (ASCII)
- Learning signals

**Output formats:**
- JSONL: machine-readable, one JSON per line
- TXT: human/agent-readable formatted output

**Log levels:**
| Level | Content |
|-------|---------|
| TRACE | Everything including embeddings |
| STEP | Each step with decision details (default) |
| EVENT | State changes, branches, crystallizations only |
| SUMMARY | Start/end only |

**Usage:**
```python
from mind.physics.traversal_logger import get_traversal_logger

logger = get_traversal_logger()

# Start exploration
logger.exploration_start(exploration_id, actor_id, origin_moment, intention)

# Log each step (called by exploration runner)
logger.log_step(exploration_id, subentity_id, ...)

# End exploration
logger.exploration_end(exploration_id, found_narratives, crystallized, satisfaction)
```

**--debug mode proposal:**
```bash
# Normal mode: returns ExplorationResult only
mind explore "What does Edmund believe?" --actor edmund

# Debug mode: returns ExplorationResult + full traversal logs
mind explore "What does Edmund believe?" --actor edmund --debug

# Output includes:
# - ExplorationResult (found_narratives, crystallized, satisfaction)
# - Full JSONL log path
# - Summary of decisions, anomalies, learning signals
```

---

## GAPS / PROPOSITIONS

### v1.2 Gaps

- Handler runtime wiring still pending (captured in SYNC).
- Speed controller and canon holder integrations remain future work increments.
- Search: moments should search for similar moments (connect to each other).
- Search: activated cluster health as stopping condition (instead of fixed ticks).

### v1.6.1 → v1.7.2 → v1.8 Implemented

- ✅ SubEntity class with state machine (SEEKING → BRANCHING → RESONATING → REFLECTING → CRYSTALLIZING → MERGING).
- ✅ Link scoring with self_novelty and sibling_divergence (`runtime/physics/link_scoring.py`).
- ✅ Tree structure with lazy refs (parent_id, sibling_ids, children_ids) via ExplorationContext.
- ✅ found_narratives as dict[str, float] with max(alignment) merge (v1.7.2 D3).
- ✅ Branch threshold: simple count len(outgoing) >= 2 (v1.7.2 D5).
- ✅ Timeout errors loudly, crashes exploration (v1.7.2 D4).
- ✅ Forward/backward coloring in `runtime/physics/flow.py`.
- ✅ Crystallization and narrative creation (`runtime/physics/crystallization.py`).
- ✅ Link embedding field added to `runtime/models/links.py` with permanence property.
- ✅ Synthesis grammar (floats ↔ phrases) in `runtime/physics/synthesis.py`.
- ✅ Async exploration runner in `runtime/physics/exploration.py`.
- ✅ Query emotion computation (`compute_query_emotion`, `compute_path_emotion`).
- ✅ **v1.8:** Query vs Intention separation (query=WHAT, intention=WHY, intention_type=HOW).
- ✅ **v1.8:** IntentionType enum (SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE).
- ✅ **v1.8:** Crystallization embedding formula includes query + intention weights.

### v1.8 Remaining Gaps

- Integration with live graph (GraphInterface needs FalkorDB implementation).
- Embedding generation (requires external embed_fn, currently mocked in tests).
- SubEntity spawning from actual graph queries (tick integration).
- Post-processing: filter results by intention_type (not yet implemented).
