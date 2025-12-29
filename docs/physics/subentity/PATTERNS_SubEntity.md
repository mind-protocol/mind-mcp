# SubEntity — Patterns

```
STATUS: CANONICAL
VERSION: v2.0
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
THIS:           ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md

IMPL:           runtime/physics/subentity.py
                runtime/physics/exploration.py
                runtime/physics/traversal_logger.py
```

---

## THE PROBLEM

Actors need to query the graph with purpose. A simple graph search
returns nodes matching keywords. But actors need:

- **Semantic relevance:** Not just keyword match, but meaning alignment
- **Intentional traversal:** WHY you search affects WHERE you look
- **Gap filling:** When knowledge doesn't exist, create it
- **Parallel perspectives:** Complex queries need multiple angles
- **Graph learning:** Repeated queries should improve future search

Traditional graph queries are passive lookups. Actors need active exploration.

---

## THE PATTERN

**SubEntities are temporary consciousness fragments.**

When an actor needs something, they spawn a SubEntity — a coroutine that
traverses the graph with query (WHAT to find) and intention (WHY finding).

The SubEntity:
1. Scores links by semantic alignment with query + intention
2. Traverses highest-scoring links, avoiding backtracking
3. Branches at decision points (Moments) for parallel exploration
4. Absorbs found narratives, tracking alignment
5. Crystallizes new narratives when gaps exist
6. Returns findings to actor with context

**Key insight:** Exploration is not passive. It shapes the graph.

Links absorb intention embeddings. Energy creates heat trails. The graph
learns from repeated exploration — common queries become faster to answer.

---

## DESIGN PRINCIPLES

### P1: Query vs Intention (v1.8)

**Query** = WHAT you're searching for (semantic matching target)
**Intention** = WHY you're searching (traversal coloring)

Same query with different intentions explores differently:
- "events at crossing" + SUMMARIZE → wide exploration
- "events at crossing" + VERIFY → seek tensions/contradictions

Intention type affects weight balance and stopping conditions.

---

### P2: Lazy Sibling References (v1.7.2)

Siblings reference each other by ID, not object. ExplorationContext
maintains the registry. This enables:
- Safe parallel spawning (no race conditions)
- Memory efficiency (no circular object refs)
- Clean serialization

```python
sibling_ids: List[str]  # Not List[SubEntity]
```

---

### P3: Tree Structure for Parallel Exploration

SubEntities form a tree:
```
Root (actor query)
├── Child A (branch 1)
│   └── Grandchild A1
└── Child B (branch 2)
```

Children explore in parallel (asyncio.gather). Results merge upward.
Siblings see each other's crystallization embeddings to diverge.

---

### P4: Crystallization Embedding = Evolving Understanding

Updated EACH step, not just at crystallization:
```
crystallization_embedding = weighted_sum([
    (0.4, query_embedding),
    (intent_weight, intention_embedding),
    (0.3, position_embedding),
    (0.2, found_narratives_embedding),
    (0.1, path_embedding)
])
```

This enables sibling divergence — siblings compare embeddings to spread.

---

### P5: Energy Injection Creates Heat Trails (v1.9)

SubEntity injects energy at EACH step:
```
injection = criticality × STATE_MULTIPLIER[state]
weight_gain = injection × permanence
```

No decay during traversal. Creates persistent heat trails that make
frequently-explored paths more salient for future explorations.

---

### P6: Satisfaction-Driven Stopping

Exploration stops when satisfied, not when exhausted:
```
if satisfaction >= threshold:
    transition to MERGING
```

This prevents over-exploration. Find enough, stop.

---

### P7: Crystallization Is Conservative

Only crystallize when:
1. Satisfaction remains low (didn't find what we need)
2. Novelty is high (new narrative wouldn't duplicate existing)

```
if max(cos(embedding, existing)) < 0.85:
    crystallize
```

Better to return empty than pollute graph.

---

### P8: State Machine Enforces Flow

Valid transitions are explicit:
```
SEEKING → BRANCHING, ABSORBING, RESONATING, REFLECTING, SEEKING
BRANCHING → MERGING, REFLECTING
ABSORBING → SEEKING, RESONATING, REFLECTING, CRYSTALLIZING
RESONATING → REFLECTING, SEEKING
REFLECTING → SEEKING, CRYSTALLIZING, MERGING
CRYSTALLIZING → SEEKING, MERGING
MERGING → (terminal)
```

Invalid transitions throw SubEntityTransitionError.

---

### P9: Branching Only at Moments

Moments are decision points — forks in narrative. Other node types
(Space, Thing, Actor, Narrative) continue SEEKING without branching.

```
if node.type == "Moment" and len(outgoing) >= 2:
    BRANCHING
```

---

### P10: Forward + Backward Coloring

**Forward (SEEKING):** Links absorb intention as traversed
```
link.embedding = blend(link.embedding, intention, 1 - permanence)
```

**Backward (REFLECTING):** Successful paths get reinforced
```
link.permanence += attenuation × alignment × permanence_rate
```

---

### P11: Awareness Depth + Breadth (v2.0)

Understanding a narrative cluster requires structural coverage, not just semantic match.

**Depth** = vertical traversal via hierarchy links `[up, down]`
- `depth[0]`: accumulated UP (toward abstraction)
- `depth[1]`: accumulated DOWN (toward details)
- Unbounded accumulator, not compressed to [0,1]

**Breadth** = horizontal traversal via peer links (hierarchy ≈ 0)
- Physics handles peer traversal naturally
- No explicit cluster size estimation needed

**Stopping = Fatigue**, not arbitrary threshold:
```
progress = cos(crystallization_embedding, intention_embedding)
delta = progress[t] - progress[t-1]
fatigued = all(|delta| < 0.05 for last 5 steps)
```

**Child crystallization is systematic:**
- Child explores → crystallizes to graph (unless 90%+ match found)
- No propagation to parent — graph is source of truth

See: `docs/physics/mechanisms/MECHANISMS_Awareness_Depth_Breadth.md`

---

## SCOPE

### In Scope

- Semantic graph traversal with query + intention
- Parallel exploration via branching
- Narrative discovery and crystallization
- Graph coloring (link embedding, energy, weight)
- Comprehensive logging for agent comprehension

### Out of Scope

- Real-time response (async, may take seconds)
- Exhaustive search (relevance-first, not complete)
- Deterministic paths (graph state affects traversal)
- UI/display concerns (returns data, not presentation)

---

## INSPIRATIONS

- **Spreading activation:** Energy flows through associative networks
- **A* search:** Heuristic-guided pathfinding with semantic alignment
- **Monte Carlo Tree Search:** Parallel exploration with backpropagation
- **Attention mechanisms:** Query-key-value scoring for relevance

---

## DEPENDENCIES

| Module | Purpose |
|--------|---------|
| `runtime/physics/flow.py` | Forward/backward coloring, energy injection |
| `runtime/physics/link_scoring.py` | Link score computation |
| `runtime/physics/crystallization.py` | Embedding computation |
| `runtime/physics/cluster_presentation.py` | Rendering crystallized content |
| `runtime/physics/traversal_logger.py` | Agent-comprehensible logging |
