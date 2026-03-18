# SubEntity Traversal Engine — Patterns: Temporary Consciousness Fragments as Graph Walkers

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against runtime/physics/subentity.py v2.1
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
THIS:            PATTERNS_SubEntity.md (you are here)
BEHAVIORS:       ./BEHAVIORS_SubEntity.md
ALGORITHM:       ./ALGORITHM_SubEntity.md
VALIDATION:      ./VALIDATION_SubEntity.md
HEALTH:          ./HEALTH_SubEntity.md
IMPLEMENTATION:  ./IMPLEMENTATION_SubEntity.md
SYNC:            ./SYNC_SubEntity.md

IMPL:            runtime/physics/subentity.py
                 runtime/physics/exploration.py
                 runtime/physics/link_scoring.py
                 runtime/physics/crystallization.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC_SubEntity.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_SubEntity.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

The knowledge graph contains actors, moments, narratives, spaces, and things connected by semantically embedded links. A citizen (or the system itself) needs to answer a question — "What do I know about X?" or "Find connections related to Y." This requires traversing the graph intelligently: following semantically aligned links, branching at decision points, recognizing when relevant narratives are found, and creating new knowledge when the traversal discovers patterns not yet captured.

Without SubEntity traversal:
- Graph queries become brute-force embedding searches with no awareness of graph structure
- The graph never grows from its own exploration (no crystallization)
- There are no heat trails — no way for one exploration to influence future ones
- Branch points are ignored; only the single "best" path is followed

---

## THE PATTERN

**SubEntity = temporary consciousness fragment with a state machine.**

A SubEntity is spawned with a query (what to find) and an intention (why finding it). It walks the graph node by node, scoring outgoing links at each position using a five-factor formula (semantic alignment, polarity, permanence, self-novelty, sibling divergence). At branch points on Moment nodes, it spawns children that explore different paths in parallel. When it finds a narrative, it resonates (measures alignment). When it runs out of aligned links, it reflects and potentially crystallizes a new narrative from its journey.

The key insight: **traversal is not read-only**. Every step injects energy into the visited node proportional to the SubEntity's criticality and current state. This creates "heat trails" — frequently explored paths become energetically hotter, making them more visible to future traversals and to the physics tick. The graph remembers where attention has flowed.

The second key insight: **the graph is the source of truth, not the SubEntity**. Children don't propagate results back to parents (v2.0 change). Instead, children crystallize new narratives directly into the graph. The parent doesn't need to remember what its children found — the graph holds it.

---

## BEHAVIORS SUPPORTED

- **B1** (Semantic graph traversal) — The link scoring formula ensures traversal follows semantically relevant paths
- **B2** (Parallel branching) — The branch/child/sibling architecture enables exploring multiple paths simultaneously
- **B3** (Knowledge crystallization) — The CRYSTALLIZING state creates new narrative nodes from exploration discoveries
- **B4** (Energy injection) — STATE_MULTIPLIER per-state weights create differentiated heat trails
- **B5** (Fatigue-based stopping) — Progress history tracking detects stagnation and terminates fruitless exploration

## BEHAVIORS PREVENTED

- **A1** (Infinite exploration) — State machine with terminal MERGING state, MAX_STEPS=1000, depth limits, timeout, and fatigue detection
- **A2** (Duplicate knowledge) — Novelty threshold (0.85) prevents crystallizing narratives too similar to existing ones
- **A3** (Backtracking) — Self-novelty scoring penalizes links similar to already-traversed path

---

## PRINCIPLES

### Principle 1: State Machine Rigor

Every SubEntity is in exactly one of 7 states. Transitions are validated against a whitelist (`VALID_TRANSITIONS`). Invalid transitions raise `SubEntityTransitionError`. There is no "unknown" state, no "pending" state, no ambiguity. The state machine is the contract between the SubEntity dataclass and the ExplorationRunner.

This matters because the ExplorationRunner dispatches to per-state handler methods. An invalid state would cause silent misbehavior. The transition validation catches bugs at the boundary, not deep inside handler logic.

### Principle 2: Lazy Reference Resolution

SubEntities reference parents, siblings, and children by ID strings, not by object references. Resolution happens at access time via `ExplorationContext`, which maintains a registry of all active SubEntities. This design (v1.7.2) eliminates circular references, simplifies serialization, and enables garbage collection of completed SubEntities.

This matters because branching creates tree structures where siblings need to read each other's crystallization embeddings (for divergence scoring). Direct object references would create reference cycles that complicate memory management and make serialization impossible.

### Principle 3: Query/Intention Separation

The query ("what to find") and intention ("why finding it") are separate embeddings that combine in link scoring with fixed weights (75% query, 25% intention). v2.1 removed the rigid IntentionType enum in favor of fully semantic intention via embedding — any intention string, embedded by the caller, no predefined categories.

This matters because the same query can serve different purposes. "Find narratives about Venice" with intention "summarize for a newcomer" should favor breadth; with intention "verify a historical claim" should favor depth. The embedding carries the semantic meaning without enum rigidity.

### Principle 4: Energy Injection is Physics

SubEntities don't just read the graph — they write energy into it at every step. The injection formula (`criticality x STATE_MULTIPLIER[state]`) means high-criticality SubEntities (unsatisfied, deep in exploration) inject more energy, and certain states (RESONATING = 2.0x) inject disproportionately. Permanence converts injected energy to weight: `weight_gain = injection x permanence`.

This matters because it ties the cognitive layer (SubEntity traversal) to the physics layer (energy/weight/decay). Explored paths warm up. Frequently explored patterns accumulate weight. The graph's structure literally records where attention has been paid.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `runtime/physics/subentity.py` | FILE | SubEntity dataclass, ExplorationContext, state machine, link scoring functions, energy injection |
| `runtime/physics/exploration.py` | FILE | ExplorationRunner: async state machine dispatcher, graph interface, per-state handlers |
| `runtime/physics/link_scoring.py` | FILE | Link score formula: cosine similarity, permanence, polarity, self-novelty, sibling divergence, branch detection |
| `runtime/physics/crystallization.py` | FILE | Crystallization embedding computation, novelty check, narrative creation, link generation |
| `runtime/physics/flow.py` | FILE | Energy flow primitives: inject_node_energy, backward_color_path, blend_embeddings |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/flow.py` | Energy injection (inject_node_energy), path backpropagation (backward_color_path), embedding blending |
| `runtime/physics/synthesis.py` | Narrative name generation during crystallization (synthesize_from_crystallization) |
| `runtime/physics/cluster_presentation.py` | Presenting exploration results as readable clusters (present_cluster) |
| `runtime/physics/constants.py` | COLD_THRESHOLD, TOP_N_LINKS constants |
| `runtime/physics/traversal_logger.py` | Optional step-by-step logging of exploration decisions |

---

## INSPIRATIONS

- **Random walk with restart** — SubEntity traversal resembles a biased random walk, but with semantic scoring instead of uniform edge selection, branching instead of single-path walking, and crystallization instead of simple convergence counting.
- **Spreading activation** — Energy injection at each step is a form of spreading activation. Unlike classic spreading activation (which decays from a source), SubEntity activation is directional and state-dependent.
- **Ant colony optimization** — Heat trails function like pheromone trails. Frequently explored useful paths accumulate weight, making them more attractive to future explorations.

---

## SCOPE

### In Scope

- SubEntity state machine (7 states, validated transitions)
- ExplorationContext (lazy reference registry)
- Link scoring formula (5 factors: semantic, polarity, permanence, self-novelty, sibling divergence)
- Energy injection during traversal (criticality x STATE_MULTIPLIER)
- Branching and merging (parent-child tree structure)
- Crystallization embedding computation (5-component weighted sum)
- Awareness depth tracking (up/down accumulator from link hierarchy)
- Fatigue detection (progress stagnation)
- ExplorationRunner (async state machine dispatcher with timeout)
- Novelty checking for crystallization (cosine threshold 0.85)
- Narrative creation and linking during crystallization

### Out of Scope

- **Physics tick loop** — SubEntity traversal is triggered by the tick but the tick itself lives in `tick_v1_2.py`
- **Embedding computation** — SubEntities receive pre-computed embeddings; embedding models are outside this module
- **Actor state management** — Actors spawn SubEntities but actor state (energy, relationships) is managed elsewhere
- **Graph storage** — SubEntities interact with the graph through `GraphInterface`; database adapters are not this module's concern
- **Presentation layer** — `cluster_presentation.py` handles formatting results; this module produces raw `ExplorationResult`

---

## MARKERS

<!-- @mind:proposition Consider adding exploration result caching keyed by (actor_id, query_embedding hash) for repeated identical queries -->
