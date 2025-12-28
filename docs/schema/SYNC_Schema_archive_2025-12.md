# Archived: SYNC_Schema.md

Archived on: 2025-12-23
Original file: SYNC_Schema.md

---

## MATURITY

**STATUS: CANONICAL v1.2**

What's canonical:
- 5 node types: actor, space, thing, narrative, moment
- 9 link types:
  - Energy carriers: `expresses`, `about`, `relates`, `attached_to`
  - Structural: `contains`, `leads_to`, `sequence`, `primes`, `can_become`
- Link physics: conductivity, weight, energy, strength, emotions
- Semantic properties: name, role, direction (replaces old type differentiation)
- Unified flow formula: `flow = source.energy × rate × conductivity × weight × emotion_factor`
- Link cooling: 30% drain + 10% strength conversion (NO DECAY)
- Hot/cold filtering via heat_score
- Schema loading with project overlay
- Health check CLI and pytest suite

What's in progress:
- World runner integration
- Canon holder validation functions

What's proposed (v2):
- Full V2/V3/V7 coverage in check_health.py
- Schema versioning in nodes
- Auto-fix capabilities

---


## v1.2 CHANGES SUMMARY

### Link Types (7 → 9)

| Type | Category | From → To | Phase |
|------|----------|-----------|-------|
| `expresses` | Energy | Actor → Moment | Draw |
| `about` | Energy | Moment → Any | Flow |
| `relates` | Energy | Any → Any | Flow, Backflow |
| `attached_to` | Energy | Thing → Actor/Space | Flow |
| `contains` | Structural | Space → Actor/Thing/Space | — |
| `leads_to` | Structural | Space → Space | — |
| `sequence` | Structural | Moment → Moment | — |
| `primes` | Structural | Moment → Moment | — |
| `can_become` | Structural | Thing → Thing | — |

### Semantic Properties (NEW)

Instead of 14+ link types, use 9 types + semantic properties (`name`, `role`, `direction`):

```yaml
# Old: Actor -[BELIEVES]-> Narrative
# New:
relates:
  node_a: actor_aldric
  node_b: narrative_oath
  name: believes
  role: believer            # originator, believer, witness, subject, creditor, debtor

# Old: Actor -[OWES]-> Actor
# New:
relates:
  node_a: actor_aldric
  node_b: actor_baron
  name: owes debt to
  role: debtor

# Old: Narrative -[SUPPORTS]-> Narrative
# New:
relates:
  node_a: narrative_loyalty
  node_b: narrative_oath
  direction: support        # support, oppose, elaborate, subsume, supersede
  emotions: [[alignment, 0.8]]
```

### Physics Changes (NO DECAY)

| v1.1 | v1.2 |
|------|------|
| Decay 40%/tick | **NO DECAY** — link cooling |
| All links processed | Hot links only (top-N filter) |
| — | heat_score = energy × weight |
| — | Link drain: 30% to nodes |
| — | Strength growth: 10% converts |

### Migration from Legacy Types

```
BELIEVES       → relates (role: believer)
ORIGINATED     → relates (role: originator, higher weight)
SUPPORTS       → relates (direction: support, emotions: [[alignment, X]])
CONTRADICTS    → relates (direction: oppose, emotions: [[opposition, X]])
ELABORATES     → relates (direction: elaborate)
CAN_SPEAK/SAID → expresses
AT             → contains (INVERTED: space contains actor)
CARRIES        → attached_to (INVERTED: thing attached_to actor)
ATTACHED_TO    → about (for Moment → Any)
THEN           → sequence
CAN_LEAD_TO    → primes
```

---


## v1.1 CHANGES SUMMARY

### Node Fields

| Field | v1.0 | v1.1 | Why |
|-------|------|------|-----|
| weight | 0-1 | 0-∞ | Importance needs range (protagonist 10x villager) |
| energy | 0-1 | 0-∞ | Accumulates from moments, decay prevents explosion |

Weight does double duty: importance (ranking) + inertia (physics stability).

### Link Fields

| Field | v1.0 | v1.1 | Why |
|-------|------|------|-----|
| from_id/to_id | string | RENAMED | → node_a/node_b (bidirectional clarity) |
| conductivity | — | 0-1 | NEW. Percentage of energy that passes through |
| weight | 0-1 | 0-∞ | Link importance (used in flow formula) |
| energy | 0-1 | 0-∞ | Current attention (decays 40%/tick) |
| strength | 0-1 | 0-∞ | Accumulated depth (decays slower) |
| polarity | -1 to +1 | REMOVED | Replaced by emotions list |
| emotions | — | List | NEW. [[name, intensity], ...] — single list |

### Link Type Collapse (10 → 7)

| Old | New | Why |
|-----|-----|-----|
| at | REMOVED | Same as `contains` reversed |
| said | **expresses** | Abstracts to thought/action/question |
| then | **sequence** | Clearer naming |
| can_lead_to | **can_become** | Clearer naming |
| attached_to | REMOVED | Use `relates` |
| about | REMOVED | Use `relates` |

**Taxonomy:**
- Organizational: contains, leads_to, expresses
- Chronological: sequence, primes, can_become
- Semantic: relates

### Emotion Model

```yaml
# All links have emotions (unified list, colored by energy flow)
link:
  emotions: [["fear", 0.7], ["respect", 0.4]]  # Hebbian: colored by what flows through
  conductivity: 0.7                             # percentage of energy flow
  weight: 1.0                                   # link importance
  energy: 0.5                                   # current attention (decays 40%/tick)
  strength: 2.3                                 # accumulated depth
```

**Hebbian coloring:** When energy flows through a link, the link's emotions blend with the flowing moment's emotions. Links "learn" what passes through them.

---


## ESCALATIONS

<!-- @mind:escalation
title: "DECAY_RATE: What's the right global decay rate?"
priority: 5
response:
  status: resolved
  choice: "Split decay rates"
  behavior: "Link energy: 40%/tick (attention fades fast). Node energy: BASE_NODE_DECAY (0.1) × 1/(1+weight). High-weight nodes decay slower."
  notes: "2025-12-23: Specified in Schema v1.1. Decided by Nicolas."
-->

<!-- @mind:escalation
title: "INERTIA_FORMULA: How does node weight affect energy change?"
priority: 5
response:
  status: resolved
  choice: "Weight in unified formula"
  behavior: "flow = source.energy × rate × conductivity × link.weight × emotion_factor. Weight affects flow rate directly. Decay uses 1/(1+weight) for inertia."
  notes: "2025-12-23: Specified in Schema v1.1. No separate inertia field. Decided by Nicolas."
-->


## TODOS

### Immediate

@mind:todo — **DB_MIGRATION_V1.1:** Write and run migration for link field changes
- Rename from_id→node_a, to_id→node_b
- Add energy, strength fields to links (default 0)
- Remove polarity, add emotions list

### Physics Implementation (See SYNC_Project_State.md for full TODO)

@mind:todo — **UNIFIED_FLOW:** Implement `flow = source.energy × rate × conductivity × weight × emotion_factor`
@mind:todo — **HEBBIAN_COLORING:** Implement link emotion blending from energy flow
@mind:todo — **PATH_RESISTANCE:** Implement Dijkstra with conductivity-based resistance
@mind:todo — **LINK_CRYSTALLIZATION:** Create relates links from shared moments
@mind:todo — **MOMENT_LIFECYCLE:** Implement possible→active→completed state machine

### Coverage

- [ ] **IMPL_V7_ENDPOINTS:** Add `validate_link_endpoints()` to check_health.py
- [ ] **MIND_DOCTOR_INTEGRATION:** Integrate check_health.py into mind doctor

### Lower Priority

- [ ] **SPLIT_TEST_SCHEMA:** test_schema.py exceeds size threshold
- [ ] **E2_E3_TESTS:** Test missing schema / malformed YAML

---



---

# Archived: SYNC_Schema.md

Archived on: 2025-12-26
Original file: SYNC_Schema.md

---

## KEY CONCEPTS (v1.6.1)

### SubEntity Structure (v1.6.1)

SubEntities are temporary consciousness fragments spawned by actors:

```python
SubEntity:
    # Identity
    id: string
    actor_id: string          # Who spawned this exploration
    origin_moment: string     # Moment that triggered exploration

    # Tree structure
    parent: SubEntity | null  # null for root
    siblings: [SubEntity]     # Other children of same parent
    children: [SubEntity]     # Spawned from branching

    # Traversal state
    state: seeking | branching | resonating | reflecting | crystallizing | merging
    position: node_id
    path: [(link_id, direction)]
    depth: int

    # Intention
    intention: string
    intention_embedding: vector

    # Accumulated findings
    found_narratives: dict[str, float]  # {narrative_id: max_alignment}
    crystallization_embedding: vector   # Computed at EACH step
    satisfaction: float [0,1]
    crystallized: narrative_id | null   # If created one
```

### State Machine

```
SEEKING → BRANCHING → RESONATING → REFLECTING → CRYSTALLIZING → MERGING
```

| State | Trigger | Action |
|-------|---------|--------|
| SEEKING | Aligned link found | Traverse, update crystallization_embedding |
| SEEKING | Moment with paths | → BRANCHING (spawn children with sibling refs) |
| SEEKING | Narrative found | → RESONATING |
| SEEKING | No aligned links | → REFLECTING |
| BRANCHING | Children spawned | Wait for all → REFLECTING |
| RESONATING | Absorbed narrative | Add to found_narratives with alignment → SEEKING/REFLECTING |
| REFLECTING | Satisfaction high | → MERGING |
| REFLECTING | Still unsatisfied | → CRYSTALLIZING |
| CRYSTALLIZING | Novel pattern | Create Narrative, set crystallized → MERGING |
| MERGING | — | Pass found_narratives + crystallized to parent, die |

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

### Crystallization Embedding (Computed Each Step)

```python
# Updated EVERY traversal step, not just at crystallization
crystallization_embedding = weighted_sum([
    (0.4, intention_embedding),
    (0.3, position.embedding),
    (0.2, mean(n.embedding for n, _ in found_narratives)),
    (0.1, mean(link.embedding for link, _ in path))
])
```

This enables sibling divergence — siblings can compare their crystallization_embeddings to avoid duplicate exploration.

### Criticality Formula

```python
criticality = (1 - satisfaction) × (depth / (depth + 1))
```

High criticality = desperate, branches more, accepts weaker alignments

### Derived Rates (No Arbitrary Constants)

| Rate | Formula | Meaning |
|------|---------|---------|
| permanence_rate | `1 / (graph.avg_degree + 1)` | Sparse graphs solidify faster |
| blend_weight | `flow / (flow + link.energy + 1)` | High-energy links resist change |
| branch_threshold | 2:1 outgoing/incoming | Only branch at decision points |
| crystallization_threshold | 0.85 cosine | Create only if truly novel |

---


## v1.6.1 DESIGN DECISIONS

### D1: Sibling Init — Lazy Refs via IDs

```python
sibling_ids: list[str]  # IDs, not objects
_context: ExplorationContext  # shared registry

@property
def siblings(self) -> list[SubEntity]:
    return [self._context.get(sid) for sid in self.sibling_ids
            if self._context.exists(sid)]
```

### D2: Embedding Consistency — Eventual OK

No locks on crystallization_embedding. Stale reads acceptable for divergence.

### D3: found_narratives Merge — Max Alignment

```python
found_narratives: dict[str, float]  # {narrative_id: max_alignment}
```

Not list of tuples. On merge, take max alignment per narrative.

### D4: Timeout — Error Loud

Crash exploration on timeout. Log full state. No partial merge.

### D5: Branch Threshold — >= 2 Outgoing

```python
def should_branch(moment: Node) -> bool:
    return len(get_outgoing_links(moment)) >= 2
```

### D6: Link Embedding — embed(synthesis)

```python
link.embedding = embed(link.synthesis)  # at creation
link.embedding = blend(link.embedding, intention, 1 - permanence)  # on traverse
```

### D7: Search Only Mode

v1.6.1 = search system. v1.2 physics tick disabled during development.

---


## v1.6.1 IMPLEMENTATION TODOS

@mind:todo — **SUBENTITY_CLASS:** Implement SubEntity dataclass in mind/physics/
- Identity: id, actor_id, origin_moment
- Tree structure: parent, siblings, children (references)
- Traversal: state, position, path, depth
- Intention: intention, intention_embedding
- Accumulated: found_narratives as [(id, alignment)], crystallization_embedding, satisfaction
- Output: crystallized (narrative_id if created)
- Computed: criticality

@mind:todo — **SUBENTITY_STATE_MACHINE:** Implement state transitions
- SEEKING: traverse, update crystallization_embedding each step
- BRANCHING: spawn children with sibling references
- RESONATING: absorb narrative with alignment score
- REFLECTING: backprop colors along path
- CRYSTALLIZING: check novelty, create Narrative, set crystallized field
- MERGING: pass found_narratives + crystallized to parent

@mind:todo — **LINK_SCORE_FORMULA:** Implement link scoring
- semantic_alignment × polarity[direction] × (1 - permanence)
- self_novelty: avoid links similar to path
- sibling_divergence: avoid siblings' crystallization_embeddings

@mind:todo — **CRYSTALLIZATION_EMBEDDING:** Update at each step
- Weighted sum: 0.4 intention + 0.3 position + 0.2 found_narratives + 0.1 path
- Enables sibling divergence comparison

@mind:todo — **FORWARD_COLORING:** Implement in traverse()
- weight = 1 - permanence
- blend embedding with intention
- energy accumulation

@mind:todo — **BACKWARD_COLORING:** Implement in reflect()
- Walk path in reverse
- Attenuation via polarity[reverse]
- Permanence boost on positive alignment

@mind:todo — **CRYSTALLIZATION:** Implement narrative creation
- Use crystallization_embedding (already computed)
- Check existing narratives (cosine > 0.85 = match)
- Create new Narrative with links
- Set crystallized field with new narrative_id

---


## v1.5 IMPLEMENTATION TODOS (Still Pending)

@mind:todo — **LINK_EMBEDDING_FIELD:** Add embedding vector field to links.py
- Requires vector storage strategy (inline vs external)
- Blend function for vector interpolation

@mind:todo — **SYNTHESIS_GENERATION:** Implement generate_link_synthesis()
- Grammar from floats to French phrases
- Bidirectional: parsing agent input to floats

@mind:todo — **TRAVERSE_FUNCTION:** Implement traverse() in tick
- Blend emotions, permanence, polarity, embedding
- Drift detection and synthesis regeneration

@mind:todo — **COMPUTE_QUERY_EMOTION:** Implement emotion emergence
- Weighted sum of aligned link emotions
- Used when actor creates/activates moments

@mind:todo — **CLUSTER_DYNAMICS:** Implement tension/convergence detection
- Tension: opposing trust on same target
- Convergence: 3+ incoming links

---


## OPEN QUESTIONS (v1.6 Escalations)

1. **CONTAINER_REDISTRIBUTION:** How do Spaces avoid becoming infinite sinks?
   - Current thinking: Asymmetric flow rates (absorb slow, diffuse fast)
   - Pending: Validate with purpose-driven traversal tests

2. **INTENTION_PROPAGATION_SCOPE:** How far does an intention propagate?
   - Options: fixed hops, energy threshold, alignment threshold
   - Pending: Empirical testing

3. **ACTOR_RECHARGE:** Actor recharge rate
   - Fixed per tick? Proportional to weight?

4. **SUBENTITY_LIFESPAN:** How long should sub-entities persist?
   - Options: satisfaction threshold, max depth, energy depleted
   - Current thinking: Combination — stop when any limit hit

5. **NARRATIVE_CREATION:** Under what conditions should crystallization create?
   - Proposed: satisfaction < 0.5, cosine < 0.85, path permanence > 0.6
   - Pending: Validate with gameplay tests

---

