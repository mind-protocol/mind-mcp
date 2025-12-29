# Archived: SYNC_Physics.md

Archived on: 2025-12-26
Original file: SYNC_Physics.md

---

## MATURITY

STATUS: v1.2 IMPLEMENTED, v1.6.1 DESIGNING

What's canonical (v1.2):
- Modular 8-phase tick (runtime/physics/phases/)
- NO DECAY — link cooling (drain + weight growth)
- Hot/cold filtering (Top-N links)
- Unified traversal (energy + weight + emotions)
- Path resistance Dijkstra (graph_query_utils.py)
- Integration with Orchestrator and World Runner

What's being designed (v1.6.1):
- **SubEntity traversal** — temporary consciousness fragments with tree structure
- **State machine**: SEEKING → BRANCHING → RESONATING → REFLECTING → CRYSTALLIZING → MERGING
- **Sibling awareness** — SubEntities avoid paths their siblings explore
- **Continuous crystallization_embedding** — computed each step, not just at crystallization
- **Link scoring** — semantic × polarity × (1 - permanence) × self_novelty × sibling_divergence
- **No arbitrary constants** — rates derived from graph properties

What's being designed (v1.9):
- **SubEntity energy injection** — energy injected at each traversal step, no decay
- **State multipliers** — injection strength varies by state (SEEKING=0.5, ABSORBING=1.0, RESONATING=2.0, CRYSTALLIZING=1.5)
- **Heat trails** — traversal paths accumulate energy, making frequently-visited paths more salient


## v1.6.1 DESIGN OVERVIEW

### SubEntity Structure (v1.6.1)

SubEntities are temporary consciousness fragments with tree structure:

```python
SubEntity:
    # Identity
    id, actor_id, origin_moment

    # Tree structure
    parent: SubEntity | null
    siblings: [SubEntity]      # Other children of same parent
    children: [SubEntity]      # Spawned from branching

    # Traversal state
    state, position, path, depth

    # Intention
    intention, intention_embedding

    # Accumulated (v1.6.1 refinements)
    found_narratives: [(narrative_id, alignment)]  # With scores
    crystallization_embedding: vector              # Updated EACH step
    satisfaction: float [0,1]
    crystallized: narrative_id | null
```

### State Machine

| State | Trigger | Action |
|-------|---------|--------|
| SEEKING | Aligned link | Traverse, update crystallization_embedding |
| BRANCHING | Moment with paths | Spawn children with sibling refs |
| RESONATING | Narrative found | Add to found_narratives with alignment |
| REFLECTING | No aligned links | Backprop colors along path |
| CRYSTALLIZING | Still unsatisfied | Create Narrative, set crystallized |
| MERGING | Done | Pass found_narratives + crystallized to parent |

### Link Score Formula (v1.6.1)

```python
link_score = (
    semantic_alignment(intention_embedding, link.embedding) *
    link.polarity[direction] *
    (1 - link.permanence) *
    self_novelty *
    sibling_divergence
)

where:
    self_novelty = 1 - max(cos(link.embedding, p.embedding) for p in path)
    sibling_divergence = 1 - max(cos(link.embedding, s.crystallization_embedding) for s in siblings)
```

### Crystallization Embedding (Updated Each Step)

```python
crystallization_embedding = weighted_sum([
    (0.4, intention_embedding),
    (0.3, position.embedding),
    (0.2, mean(n.embedding for n, _ in found_narratives)),
    (0.1, mean(link.embedding for link, _ in path))
])
```

Computed at EACH step — enables sibling_divergence comparison.

### Criticality

```python
criticality = (1 - satisfaction) × (depth / (depth + 1))
```

### Derived Rates (no arbitrary constants)

- permanence_rate = `1 / (graph.avg_degree + 1)`
- blend_weight = `flow / (flow + link.energy + 1)`
- branch_threshold = 2:1 outgoing/incoming ratio
- crystallization_threshold = 0.85 cosine similarity

### Forward Coloring

As SubEntity traverses link:
- color_weight = 1 - permanence (less permanent = more colorable)
- link.embedding = blend(link.embedding, intention_embedding, color_weight)
- link.energy += flow × 0.3
- polarity[direction] reinforced

### Backward Coloring (REFLECTING)

Walking back along path:
- Attenuation per link = polarity[reverse_direction]
- If alignment > 0: link.permanence += attenuation × alignment × permanence_rate
- If alignment < 0: permanence unchanged (don't weaken on single pass)


## v1.6.1 DESIGN DECISIONS

### D1: Sibling Init Strategy — Lazy Refs via IDs

SubEntities reference siblings by ID, not object. A shared `ExplorationContext` maintains the registry.

```python
@dataclass
class SubEntity:
    sibling_ids: list[str]  # IDs, not objects
    _context: ExplorationContext  # shared, contains all SubEntities

    @property
    def siblings(self) -> list[SubEntity]:
        return [self._context.get(sid) for sid in self.sibling_ids
                if self._context.exists(sid)]
```

**Rationale:** No race at spawn, eventual consistency natural, serializable.

### D2: Embedding Consistency — Eventual Consistency OK

`crystallization_embedding` updates are not locked. Siblings may read stale values.

**Rationale:** Divergence is "best effort" — stale reads still provide useful signal.

### D3: found_narratives Merge — Max Alignment

When children merge to parent, use `max(alignment)` per narrative_id:

```python
found_narratives: dict[str, float]  # {narrative_id: max_alignment}
```

**Rationale:** If one path finds N1 with 0.9 alignment, that's the real discovery. Lower alignments confirm but don't add critical info.

### D4: Timeout Behavior — Error Loud

If exploration hits timeout:
- Log full state (position, path, found_narratives, crystallization_embedding)
- Raise error, crash exploration
- Do NOT merge partial results

**Rationale:** Silent failures hide bugs. Fix timeout issues explicitly.

### D5: Branch Threshold — Simple Count

Branch if moment has >= 2 outgoing links:

```python
def should_branch(moment: Node) -> bool:
    return len(get_outgoing_links(moment)) >= 2
```

**Rationale:** Scoring handles selection. Branch threshold just needs "real choice exists".

### D6: Link Embedding Source — embed(synthesis)

New links get embedding from `embed(synthesis)`. On traverse, embedding blends with intention.

```python
link.embedding = embed(link.synthesis)  # at creation
link.embedding = blend(link.embedding, intention, 1 - permanence)  # on traverse
```

### D7: Physics vs Search — Search Only

v1.6.1 SubEntity is for search. v1.2 physics tick disabled during SubEntity development.

**Rationale:** Focus on one system. Integrate after SubEntity works.

---


## v1.6.1 IMPLEMENTATION TODOS

@mind:todo — **SUBENTITY_CLASS:** Implement SubEntity dataclass
- Location: `runtime/physics/subentity.py`
- Identity: id, actor_id, origin_moment
- Tree structure: parent, siblings, children (references)
- Traversal: state, position, path, depth
- Intention: intention, intention_embedding
- Accumulated: found_narratives as [(id, alignment)], crystallization_embedding, satisfaction
- Output: crystallized (narrative_id if created)
- Computed: criticality

@mind:todo — **LINK_SCORE_FORMULA:** Implement link scoring
- semantic × polarity[direction] × (1 - permanence)
- self_novelty: avoid links similar to path
- sibling_divergence: avoid siblings' crystallization_embeddings

@mind:todo — **CRYSTALLIZATION_EMBEDDING:** Update at each step
- Weighted sum: 0.4 intention + 0.3 position + 0.2 found_narratives + 0.1 path
- Enables sibling divergence comparison

@mind:todo — **SUBENTITY_STATE_MACHINE:** Implement state transitions
- SEEKING: traverse, update crystallization_embedding each step
- BRANCHING: spawn children with sibling references
- RESONATING: add to found_narratives with alignment score
- REFLECTING: backprop colors
- CRYSTALLIZING: check novelty, create Narrative, set crystallized
- MERGING: pass found_narratives + crystallized to parent

@mind:todo — **FORWARD_COLORING:** Implement in flow.py traverse()
- color_weight = 1 - permanence
- blend embedding with intention
- energy accumulation

@mind:todo — **BACKWARD_COLORING:** Implement reflect() function
- Walk path in reverse
- Attenuation via polarity[reverse]
- Permanence boost on positive alignment

@mind:todo — **CRYSTALLIZATION:** Implement narrative creation
- Use crystallization_embedding (already computed)
- Check existing narratives (cosine > 0.85 = match)
- Create new Narrative with links
- Set crystallized field with new narrative_id


## RECENT CHANGES

### 2025-12-26: SubEntity Energy Injection (v1.9)

New mechanic: SubEntity injects energy at each traversal step with no decay.

```python
STATE_MULTIPLIER = {
    SEEKING: 0.5,       # Low: exploring, not yet committed
    ABSORBING: 1.0,     # Normal: absorbing content
    RESONATING: 2.0,    # High: found aligned narrative
    CRYSTALLIZING: 1.5  # Medium-high: creating new narrative
}

injection = criticality * STATE_MULTIPLIER[state]
focus_node.energy += injection
```

Key insight: Creates "heat trails" — paths accumulate energy during traversal,
making frequently-traversed paths more salient for future queries.

Documented in: `docs/physics/ALGORITHM_Physics.md` (Key Formulas section)

### 2025-12-26: TraversalLogger v1.0 Complete

Agent-comprehensible SubEntity exploration logging:
- Natural language explanations for decisions
- "Why not" reasoning for rejected options
- Progress narratives, anomaly detection, causal chains
- Learning signals for pattern extraction
- JSONL + human-readable output formats
- 41 tests passing

Files:
- `runtime/physics/traversal_logger.py` (1200 lines)
- `runtime/tests/test_traversal_logger.py` (41 tests)
- `docs/physics/traversal_logger/` (IMPLEMENTATION + SYNC)

### 2025-12-26: SubEntity v1.7.2 Complete

SubEntity class implemented with:
- State machine (6 states)
- Crystallization embedding computation
- Link scoring with all 5 factors
- Tree operations (spawn, merge, find_siblings)
- 7 health checkers (V15-V19)
- 55 tests passing

### 2025-12-26: Schema v1.6.1 Refinements

- SubEntity structure refined: origin_moment, siblings, children fields
- found_narratives now stores (narrative_id, alignment) tuples
- crystallization_embedding computed at EACH step (not just at crystallization)
- Link score formula: semantic × polarity × (1-permanence) × self_novelty × sibling_divergence
- Sibling divergence enables SubEntities to spread exploration naturally

### 2025-12-26: Schema v1.6 Design

- SubEntity schema added to `docs/schema/schema.yaml`
- State machine documented
- Forward/backward coloring mechanics specified
- Crystallization embedding formula defined
- All rates derived from graph properties (no magic numbers)

### 2025-12-23: v1.2 Validation & Health Checker Infrastructure

- Created `docs/physics/VALIDATION_Energy_Physics.md` — 19 validation IDs
- Created `docs/physics/HEALTH_Energy_Physics.md` — Health indicators
- Implemented health checker CLI: `python -m engine.physics.health.checker`
- Checker infrastructure in `runtime/physics/health/checkers/`

### 2025-12-23: Schema v1.1 Spec Complete

- Unified flow formula replaces speaker/witness special cases
- Moment lifecycle: possible → active → completed/rejected/interrupted/overridden
- Path resistance via Dijkstra (weight × emotion_factor)
- Link crystallization, narrative backflow, liquidation on completion

