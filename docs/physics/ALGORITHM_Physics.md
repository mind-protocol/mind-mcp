# Physics — Algorithm: System Overview

```
CREATED: 2024-12-18
UPDATED: 2025-12-26
STATUS: Canonical (v1.2 implemented, v1.6.1 designed)
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Physics.md
BEHAVIORS:      ./BEHAVIORS_Physics.md
THIS:           ALGORITHM_Physics.md (you are here)
SCHEMA:         ../schema/SCHEMA_Moments.md
VALIDATION:     ./VALIDATION_Physics.md
IMPLEMENTATION: ./IMPLEMENTATION_Physics.md
HEALTH:         ./HEALTH_Physics.md
SYNC:           ./SYNC_Physics.md
```

---

## Consolidation Note

This algorithm is now split into focused documents to reduce size and make
review more targeted. The overview stays here; deep dives live in the
linked algorithm docs below.

## OVERVIEW

This algorithm describes the physics engine that moves energy through the
graph, detects flips, and hands off work to handlers, canon, and display
control. The intent is to keep all authoritative state in the graph while
the tick cycle applies deterministic propagation rules.

---

## DETAILED ALGORITHMS

### v1.2 (Implemented)

- `algorithms/ALGORITHM_Physics_Energy_Mechanics_And_Link_Semantics.md`
  — canonical physics algorithm covering energy mechanics, flow sources/sinks, tick cycle, handler/input processing, and speed control behaviors.
- `algorithms/ALGORITHM_Physics_Mechanisms.md` (function-level mapping to code)

### v1.6.1 (Designed)

- SubEntity traversal state machine (see below)
- Sibling awareness via crystallization_embedding comparison
- Link scoring with self_novelty and sibling_divergence
- Forward/backward coloring mechanics
- Crystallization and narrative creation

## LEGACY ALGORITHM REDIRECTS

- `algorithms/ALGORITHM_Physics_Energy_Flow_Sources_Sinks_And_Moment_Dynamics.md`
- `algorithms/ALGORITHM_Physics_Tick_Cycle_Gating_Flips_And_Dispatch.md`
- `algorithms/ALGORITHM_Physics_Handler_And_Input_Processing_Flows.md`
- `algorithms/ALGORITHM_Physics_Speed_Control_And_Display_Filtering.md`
  — stubs that point readers to the canonical algorithm above.

## DATA STRUCTURES

- Graph nodes for Characters, Narratives, Moments with `weight` and `energy`.
- Graph links for BELIEVES/ABOUT/SUPPORTS/etc. with `strength` and optional
  routing attributes like `presence_required` and `require_words`.
- Tick context: current tick index, decay constants, and pending flip results.
- Queues: handler outputs (potential moments) and canon records (actualized).

---

## ALGORITHM: Physics Tick Cycle

Primary function: `run_physics_tick()` (conceptual name for the per-tick loop).

1. Load active characters and their BELIEVES/ORIGINATED links.
2. Pump character energy into narratives using link strengths.
3. Route narrative energy across narrative-to-narrative links (zero-sum).
4. Push energy to moments via ATTACHED_TO and CAN_SPEAK links.
5. Apply decay and clamp weights/energy to minimum thresholds.
6. Compute salience and detect flips for moments and narratives.
7. Emit flip results to handlers and canon recording pipeline.
8. Persist updated weights/energy to the graph and return tick summary.

---

## KEY DECISIONS

- Energy is the proximity signal; no separate proximity layer exists.
- Links only route energy; creation happens via character pumps or input.
- The graph is the only source of truth; ticks never cache authoritative state.
- Zero-sum transfers preserve energy while decay and actualization drain it.

---

## DATA FLOW

Graph queries load current node/link state → tick computes injections and
transfers → updates are written back to the graph → flip events are surfaced
to handlers and canon holder → display layer filters by speed settings.

---

## COMPLEXITY

Per tick cost is proportional to the number of active characters, their
adjacent BELIEVES/ABOUT links, and reachable narrative edges. Worst case is
O(V+E) over the active subgraph; practical runs are bounded by salience
filters and query limits in graph ops.

---

## HELPER FUNCTIONS

- `salience(node)` multiplies weight and energy to rank surfacing.
- `reinforce_link()` and `challenge_link()` adjust strengths with clamps.
- `apply_decay()` reduces energy/weight based on real-time elapsed.
- `is_interrupt()` classifies moments for 3x snap-to-1x transitions.

---

## INTERACTIONS

- Handlers read flip outputs to generate new potential moments.
- Canon holder records actualized moments and THEN links.
- Speed controller adjusts tick interval and display filtering rules.
- GraphOps/GraphQueries provide the mutation and read API used by ticks.

---

## ALGORITHM: SubEntity Traversal (v1.8)

Primary function: `run_exploration()` in `runtime/physics/exploration.py`.

### v1.8 Key Change: Query vs Intention

- **Query**: WHAT we're searching for (semantic matching)
- **Intention**: WHY we're searching (traversal coloring)
- **IntentionType**: HOW to traverse (affects weights, stopping, filtering)

### State Machine

```
SEEKING → BRANCHING → RESONATING → REFLECTING → CRYSTALLIZING → MERGING
```

### Step 1: Create SubEntity

```python
def create_subentity(
    actor_id: str,
    origin_moment: str,
    query: str,
    query_embedding: List[float],
    intention: str = "",
    intention_embedding: Optional[List[float]] = None,
    intention_type: IntentionType = IntentionType.EXPLORE,
    context: Optional[ExplorationContext] = None,
):
    """v1.8: Separate query (WHAT) from intention (WHY)."""
    se = SubEntity(
        id=generate_id(),
        actor_id=actor_id,
        origin_moment=origin_moment,
        parent_id=None,
        sibling_ids=[],
        child_ids=[],
        state=SubEntityState.SEEKING,
        position=actor_id,
        path=[],
        depth=0,
        query=query,
        query_embedding=query_embedding,
        intention=intention or query,
        intention_embedding=intention_embedding or query_embedding,
        intention_type=intention_type,
        found_narratives={},  # v1.7.2: dict[str, float] with max alignment
        crystallization_embedding=query_embedding.copy(),
        satisfaction=0.0,
        crystallized=None
    )
    if context:
        context.register(se)
    return se

# Intention types and their weights
INTENTION_WEIGHTS = {
    IntentionType.SUMMARIZE: 0.3,   # Privilege rich content
    IntentionType.VERIFY: 0.5,      # Look for contradictions
    IntentionType.FIND_NEXT: 0.2,   # Stop at first match
    IntentionType.EXPLORE: 0.25,    # Balanced
    IntentionType.RETRIEVE: 0.1,    # Exact match
}
```

### Step 2: SEEKING — Traverse Aligned Links

```python
def compute_link_score(se, link, direction):
    """v1.8 link score formula with query + intention alignment."""
    intent_weight = INTENTION_WEIGHTS[se.intention_type]

    # v1.8: Combine query and intention alignment
    query_align = cosine(se.query_embedding, link.embedding)
    intention_align = cosine(se.intention_embedding, link.embedding)
    alignment = (1 - intent_weight) * query_align + intent_weight * intention_align

    # Self-novelty: avoid backtracking (links similar to path)
    if se.path:
        self_novelty = 1 - max(cosine(link.embedding, get_link(p).embedding) for p, _ in se.path)
    else:
        self_novelty = 1.0

    # Sibling divergence: avoid siblings' exploration space
    if se.siblings:
        sibling_divergence = 1 - max(cosine(link.embedding, s.crystallization_embedding) for s in se.siblings)
    else:
        sibling_divergence = 1.0

    return alignment * link.polarity[direction] * (1 - link.permanence) * self_novelty * sibling_divergence


def update_crystallization_embedding(se):
    """v1.8: includes both query and intention with type-based weighting."""
    intent_weight = INTENTION_WEIGHTS[se.intention_type]
    se.crystallization_embedding = weighted_sum([
        (0.4, se.query_embedding),
        (intent_weight, se.intention_embedding),
        (0.3, get_node(se.position).embedding),
        (0.2, mean([get_node(n).embedding for n, _ in se.found_narratives.items()]) if se.found_narratives else zero_vector()),
        (0.1, mean([get_link(l).embedding for l, _ in se.path]) if se.path else zero_vector())
    ])


def step_seeking(se):
    links = get_outgoing_links(se.position)

    # v1.8: Score links with query+intention alignment, self_novelty, sibling_divergence
    scored = [(link, compute_link_score(se, link, FORWARD)) for link in links]

    for link, score in sorted(scored, key=lambda x: -x[1]):
        if is_moment(link.target) and count_outgoing(link.target) > 2:
            return transition(se, BRANCHING, link.target)

        if is_narrative(link.target):
            return transition(se, RESONATING, link.target)

        if score > se.criticality * 0.5:  # more critical = lower threshold
            forward_color(se, link)
            se.position = link.target
            se.path.append((link.id, FORWARD))
            se.depth += 1
            update_crystallization_embedding(se)  # v1.8: update each step
            return se  # stay SEEKING

    return transition(se, REFLECTING)  # no aligned links found
```

### Step 3: BRANCHING — Spawn Children

```python
def step_branching(se):
    # Only branch on Moments (not other types)
    if not is_moment(se.position):
        return transition(se, SEEKING)

    outgoing = get_outgoing_links(se.position)
    incoming = get_incoming_links(se.position)

    # Threshold: 2:1 ratio
    if len(outgoing) / max(len(incoming), 1) < 2:
        return transition(se, SEEKING)

    # Spawn children with sibling references
    children = []
    max_children = int(se.criticality * len(outgoing))
    for link in outgoing[:max_children]:
        child = spawn_child(se, link.target)
        child.sibling_ids = [c.id for c in children]  # each child knows its siblings
        children.append(child)
    # Update sibling_ids for all children
    for child in children:
        child.sibling_ids = [c.id for c in children if c.id != child.id]

    se.child_ids = [c.id for c in children]  # track children

    # Wait for children, then reflect
    results = run_all(children)

    # v1.7.2+: Merge found_narratives dict (max alignment per narrative)
    for child in children:
        for narr_id, align in child.found_narratives.items():
            se.found_narratives[narr_id] = max(se.found_narratives.get(narr_id, 0), align)
        if child.crystallized:
            se.found_narratives[child.crystallized] = 1.0  # crystallized = fully aligned

    se.satisfaction = aggregate_satisfaction(results)
    update_crystallization_embedding(se)  # v1.8: update after merging children

    return transition(se, REFLECTING)
```

### Step 4: RESONATING — Absorb Narrative

```python
def step_resonating(se, narrative):
    # v1.8: Compute alignment using both query and intention
    intent_weight = INTENTION_WEIGHTS[se.intention_type]
    query_align = cosine(se.query_embedding, narrative.embedding)
    intention_align = cosine(se.intention_embedding, narrative.embedding)
    align = (1 - intent_weight) * query_align + intent_weight * intention_align

    if align > 0:
        # v1.7.2: found_narratives is dict with max alignment
        se.found_narratives[narrative.id] = max(se.found_narratives.get(narrative.id, 0), align)
        # Satisfaction boost weighted by narrative importance
        boost = align * narrative.weight / (sum(se.found_narratives.values()) + 1)
        se.satisfaction = min(1.0, se.satisfaction + boost)
        update_crystallization_embedding(se)  # v1.8: update after absorbing

    if se.satisfaction > 0.8:
        return transition(se, MERGING)
    else:
        return transition(se, SEEKING)
```

### Step 5: REFLECTING — Backpropagate Colors

```python
def step_reflecting(se):
    intent_weight = INTENTION_WEIGHTS[se.intention_type]

    # Walk path in reverse
    for link_id in reversed(se.path):
        link = get_link(link_id)

        # Attenuation via reverse polarity
        direction = get_direction(se, link)
        attenuation = link.polarity[1 - direction]

        # v1.8: Permanence boost on positive combined alignment
        query_align = cosine(se.query_embedding, link.embedding)
        intention_align = cosine(se.intention_embedding, link.embedding)
        align = (1 - intent_weight) * query_align + intent_weight * intention_align
        if align > 0:
            rate = 1 / (graph.avg_degree + 1)  # derived, not arbitrary
            link.permanence += attenuation * align * rate
            link.permanence = min(1.0, link.permanence)

    if se.satisfaction > 0.5:
        return transition(se, MERGING)
    else:
        return transition(se, CRYSTALLIZING)
```

### Step 6: CRYSTALLIZING — Create Narrative

```python
def step_crystallizing(se):
    # v1.8: crystallization_embedding computed at each step with query+intention
    update_crystallization_embedding(se)

    # Check if novel (no similar narrative exists)
    similar = find_similar_narratives(se.crystallization_embedding, threshold=0.85)

    if not similar:
        # Create new Narrative
        narrative = create_narrative(
            embedding=se.crystallization_embedding,
            synthesis=generate_synthesis(se.crystallization_embedding)
        )

        # Link to found narratives with their alignment scores (v1.7.2: dict)
        for n_id, alignment in se.found_narratives.items():
            create_link(narrative.id, n_id, type='relates', polarity=[alignment, alignment])

        # Link to origin Moment
        if se.origin_moment:
            create_link(se.origin_moment, narrative.id, type='about')

        se.crystallized = narrative.id
        se.found_narratives[narrative.id] = 1.0  # add to found with full alignment

    return transition(se, MERGING)
```

### Step 7: MERGING — Return Findings

```python
def step_merging(se):
    if se.parent_id:
        parent = context.get(se.parent_id)
        # v1.7.2: Merge found_narratives dict (max alignment per narrative)
        for n_id, align in se.found_narratives.items():
            parent.found_narratives[n_id] = max(parent.found_narratives.get(n_id, 0), align)
        # Also pass crystallized if we created one
        if se.crystallized:
            parent.found_narratives[se.crystallized] = 1.0
    else:
        # Pass to actor
        actor = get_node(se.actor_id)
        for n_id, alignment in se.found_narratives.items():
            reinforce_link(actor.id, n_id, strength=alignment)

    # Die
    context.unregister(se.id)
```

### Key Formulas (v1.8)

**Link Score**:
```python
intent_weight = INTENTION_WEIGHTS[intention_type]  # 0.1-0.5 based on type

alignment = (1 - intent_weight) * query_align + intent_weight * intention_align

link_score = (
    alignment *
    link.polarity[direction] *
    (1 - link.permanence) *
    self_novelty *
    sibling_divergence
)

where:
    query_align = cos(query_embedding, link.embedding)
    intention_align = cos(intention_embedding, link.embedding)
    self_novelty = 1 - max(cos(link.embedding, p.embedding) for p in path)
    sibling_divergence = 1 - max(cos(link.embedding, s.crystallization_embedding) for s in siblings)
```

**Crystallization Embedding (v1.8)** — computed at EACH step:
```python
intent_weight = INTENTION_WEIGHTS[intention_type]

crystallization_embedding = weighted_sum([
    (0.4, query_embedding),
    (intent_weight, intention_embedding),
    (0.3, position.embedding),
    (0.2, mean(n.embedding for n in found_narratives.keys())),
    (0.1, mean(link.embedding for link, _ in path))
])
```

**Criticality** (drives exploration aggressiveness):
```python
criticality = (1 - satisfaction) * (depth / (depth + 1))
```

**Forward Coloring** (as SubEntity traverses):
```python
color_weight = 1 - link.permanence  # less permanent = more colorable
link.embedding = blend(link.embedding, intention_embedding, color_weight)
link.energy += flow * 0.3
```

**Derived Rates** (no arbitrary constants):
```python
permanence_rate = 1 / (graph.avg_degree + 1)
blend_weight = flow / (flow + link.energy + 1)
```

**Energy & Weight Flows (v1.9)**

**Link: Energy Flow (traversal)**
```python
# Energy PASSES THROUGH the link (not stored here)
if source.id == link.node_a:
    flow = source.energy * link.polarity[0] * link.weight
else:
    flow = source.energy * link.polarity[1] * link.weight

# Modified by alignment with intention
flow *= (1 + alignment)

# Modified by hierarchy (containers amplify inward)
if link.hierarchy < 0 and going_inward:
    flow *= (1 + abs(link.hierarchy))
```

**Link: Weight Gain (solidification)**
```python
# Link gains weight proportional to flow AND permanence
link.weight += flow * link.permanence
# High permanence = solidifies fast
# Low permanence = stays light
```

**Link: Energy Storage**
```python
# Link stores energy proportional to flow AND inverse of permanence
link.energy += flow * (1 - link.permanence)
# High permanence = little energy stored (stable, not reactive)
# Low permanence = lots of energy stored (volatile, reactive)
```

**Node: Energy Injection (every step)**
```python
STATE_MULTIPLIER = {
    SubEntityState.SEEKING: 0.5,       # Low: exploring
    SubEntityState.ABSORBING: 1.0,     # Normal: absorbing
    SubEntityState.RESONATING: 2.0,    # High: aligned
    SubEntityState.CRYSTALLIZING: 1.5  # Medium-high: creating
}

# Energy scales with node weight — heavier nodes get more
base = criticality * STATE_MULTIPLIER[state]
injection = base * node.weight
node.energy += injection
```

**Node: Weight Gain (RESONATING only)**
```python
# Only at RESONATING state — no permanence, no convergence bonus
gain = criticality * STATE_MULTIPLIER[RESONATING]
node.weight += gain
```

**Effect:**
- Node with weight 5.0 → receives 5× more energy
- Node that resonates often → gains weight → receives even more energy
- Positive feedback loop (bounded by criticality ∈ [0, 1])

| Event | Formula |
|-------|---------|
| Energy injection (every step) | `+= criticality × state_mult × node.weight` |
| Weight gain (RESONATING only) | `+= criticality × state_mult` |

| State | Multiplier | Rationale |
|-------|------------|-----------|
| SEEKING | 0.5 | Exploring cautiously, low commitment |
| ABSORBING | 1.0 | Baseline energy for content absorption |
| RESONATING | 2.0 | Strong alignment found, amplify signal |
| CRYSTALLIZING | 1.5 | Creating narrative, elevated but focused |

---

## MARKERS

- Handler runtime and canon holder code are planned but not fully implemented.
- Energy constants (pump rates, thresholds) still need playtesting.
- Question Answerer async integration depends on infrastructure readiness.
- v1.6.1 SubEntity implementation pending (design complete).

---
