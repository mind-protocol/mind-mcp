# SubEntity — Algorithm

```
STATUS: CANONICAL
VERSION: v2.0
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
THIS:           ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## OVERVIEW

SubEntity exploration is an async state machine that traverses the graph
with query + intention, scoring links, branching at decision points,
absorbing narratives, and crystallizing new knowledge when gaps exist.

---

## STATE MACHINE

```
┌─────────────────────────────────────────────────────────────────────────┐
│   SEEKING ─────────────────────────────────────────────────────┐        │
│      │                                                          │        │
│      ├──▶ BRANCHING ──▶ (await children) ──────────────────────┤        │
│      │                                                          │        │
│      ├──▶ ABSORBING ──▶ CRYSTALLIZING ──┬──▶ SEEKING ──────────┤        │
│      │                                  │                       │        │
│      └──▶ RESONATING ──▶ REFLECTING ───┬┴──▶ MERGING ◀─────────┘        │
│                                        │                                 │
│                                        └──▶ CRYSTALLIZING ──▶ MERGING   │
└─────────────────────────────────────────────────────────────────────────┘
```

| State | Multiplier | Trigger | Action |
|-------|------------|---------|--------|
| SEEKING | 0.5 | Start / continue | Score links, traverse best |
| BRANCHING | 0.5 | Moment with ≥2 links | Spawn children, await all |
| ABSORBING | 1.0 | Content to process | Check alignment + novelty |
| RESONATING | 2.0 | At Narrative node | Absorb, boost satisfaction |
| REFLECTING | 0.5 | Dead end / after branch | Backpropagate colors |
| CRYSTALLIZING | 1.5 | Low satisfaction + high novelty | Create new Narrative |
| MERGING | 0.0 | Done | Return to parent/actor |

---

## ALGORITHM: Exploration Runner

### Step 1: Create Root SubEntity

```python
root = create_subentity(
    actor_id=actor_id,
    origin_moment=origin_moment,
    query=query,
    query_embedding=query_embedding,
    intention=intention,
    intention_embedding=intention_embedding,
    intention_type=intention_type,
    start_position=actor_id,
    context=exploration_context,
)
```

**Initializes:**
- position = actor_id (start at actor)
- state = SEEKING
- path = []
- found_narratives = {}
- crystallization_embedding = query_embedding
- satisfaction = 0.0

### Step 2: Run State Machine Loop

```python
while subentity.is_active:
    if state == SEEKING:
        await step_seeking(subentity)
    elif state == BRANCHING:
        await step_branching(subentity)
    elif state == ABSORBING:
        await step_absorbing(subentity)
    elif state == RESONATING:
        await step_resonating(subentity)
    elif state == REFLECTING:
        await step_reflecting(subentity)
    elif state == CRYSTALLIZING:
        await step_crystallizing(subentity)
    elif state == MERGING:
        await step_merging(subentity)

    if depth >= max_depth:
        transition to REFLECTING
```

---

## ALGORITHM: SEEKING

### Step 1: Get Outgoing Links

```python
links = await graph.get_outgoing_links(position)
if not links:
    transition to REFLECTING
    return
```

### Step 2: Gather Embeddings for Scoring

```python
path_embeddings = [graph.get_link_embedding(lid) for lid, _ in path]
sibling_embeddings = [s.crystallization_embedding for s in siblings if s.is_active]
```

### Step 3: Score Links

For each link, compute:

```python
# Query alignment (WHAT we're searching for)
query_alignment = cosine(query_embedding, link.embedding)

# Intention alignment (WHY we're searching)
intention_alignment = cosine(intention_embedding, link.embedding)

# Combined alignment (weighted by intention_type)
intent_weight = INTENTION_WEIGHTS[intention_type]
#   SUMMARIZE: 0.3, VERIFY: 0.5, FIND_NEXT: 0.2, EXPLORE: 0.25, RETRIEVE: 0.1
alignment = (1 - intent_weight) * query_alignment + intent_weight * intention_alignment

# Self-novelty (avoid backtracking)
self_novelty = 1 - max(cosine(link.embedding, p) for p in path_embeddings)

# Sibling divergence (spread exploration)
sibling_divergence = 1 - max(cosine(link.embedding, s) for s in sibling_embeddings)

# Permanence factor (prefer explorable links)
permanence_factor = 1 - link.permanence

# Final score
link_score = alignment * link.polarity * permanence_factor * self_novelty * sibling_divergence
```

### Step 4: Select Best Link

```python
scored = [(link, score, components) for link in links]
scored.sort(key=lambda x: x[1], reverse=True)

if scored[0][1] < min_link_score:
    transition to REFLECTING
    return

best_link, score, components = scored[0]
target_id = get_target_node_id(best_link, position)
```

### Step 5: Check for Branching

```python
if await graph.is_moment(position) and len(scored) >= min_branch_links:
    transition to BRANCHING
    return
```

### Step 6: Forward Color Link

```python
color_weight = 1 - best_link.permanence
best_link.embedding = blend(best_link.embedding, intention_embedding, color_weight)
best_link.energy += flow * 0.3
best_link.polarity[direction] reinforced
```

### Step 7: Traverse

```python
path.append((best_link.id, target_id))
position = target_id
depth += 1
```

### Step 8: Inject Energy (v1.9)

```python
injection = criticality * STATE_MULTIPLIER[SEEKING]  # 0.5
target_node.energy += injection
target_node.weight += injection * target_node.permanence
```

### Step 9: Update Crystallization Embedding

```python
crystallization_embedding = weighted_sum([
    (0.4, query_embedding),
    (intent_weight, intention_embedding),
    (0.3, position.embedding),
    (0.2, mean(found_narratives.embeddings)),
    (0.1, mean(path.embeddings))
])
```

### Step 10: Check Target Type

```python
if await graph.is_narrative(target_id):
    transition to RESONATING
elif await graph.is_moment(target_id) and len(outgoing) >= min_branch_links:
    transition to BRANCHING
else:
    continue SEEKING
```

---

## ALGORITHM: BRANCHING

### Step 1: Score All Outgoing Links

Same as SEEKING Step 3.

### Step 2: Select Top N Candidates

```python
candidates = select_branch_candidates(scored, max_branches=3)

if len(candidates) <= 1:
    transition to SEEKING
    return
```

### Step 3: Spawn Children

```python
children = []
for link, score, components in candidates:
    child = parent.spawn_child(
        target_position=link.target,
        via_link=link.id,
        context=exploration_context,
    )
    children.append(child)
```

### Step 4: Set Sibling References

```python
parent.set_sibling_references()
# Each child now has sibling_ids pointing to its siblings
```

### Step 5: Run Children in Parallel

```python
await asyncio.gather(*[run_subentity(child) for child in children])
```

### Step 6: Merge Results

```python
for child in children:
    for narr_id, alignment in child.found_narratives.items():
        parent.found_narratives[narr_id] = max(
            parent.found_narratives.get(narr_id, 0),
            alignment
        )
    if child.crystallized:
        parent.found_narratives[child.crystallized] = 1.0

parent.satisfaction = max(parent.satisfaction, max(c.satisfaction for c in children))
```

### Step 7: Transition

```python
transition to REFLECTING
```

---

## ALGORITHM: ABSORBING (v1.9)

### Step 1: Compute Alignment

```python
node_embedding = await graph.get_node_embedding(position)
alignment = cosine(intention_embedding, node_embedding)
```

### Step 2: Compute Novelty

```python
novelty = 1 - max(cosine(node_embedding, p) for p in path_embeddings)
```

### Step 3: Inject Energy

```python
injection = criticality * STATE_MULTIPLIER[ABSORBING]  # 1.0
node.energy += injection
node.weight += injection * node.permanence
```

### Step 4: Decide Next State

```python
if alignment > 0.7 and novelty > 0.7:
    transition to CRYSTALLIZING
else:
    transition to SEEKING
```

---

## ALGORITHM: RESONATING

### Step 1: Get Narrative Embedding

```python
narrative_embedding = await graph.get_node_embedding(position)
```

### Step 2: Compute Alignment

```python
alignment = cosine(intention_embedding, narrative_embedding)
```

### Step 3: Store Finding

```python
current = found_narratives.get(position, 0.0)
found_narratives[position] = max(current, alignment)
```

### Step 4: Boost Satisfaction

```python
total_align = sum(found_narratives.values()) + 1.0
boost = alignment / total_align
satisfaction = min(1.0, satisfaction + boost)
```

### Step 5: Add Weight (v1.9)

```python
node.weight += criticality * STATE_MULTIPLIER[RESONATING]  # 2.0
```

### Step 6: Transition

```python
if satisfaction >= satisfaction_threshold:
    transition to MERGING
else:
    transition to SEEKING
```

---

## ALGORITHM: REFLECTING

### Step 1: Backward Color Path

```python
for link, node in reversed(path):
    attenuation = link.polarity[reverse_direction]
    if alignment > 0:
        link.permanence += attenuation * alignment * permanence_rate
```

### Step 2: Transition

```python
if satisfaction > 0.5:
    transition to MERGING
else:
    transition to CRYSTALLIZING
```

---

## ALGORITHM: CRYSTALLIZING

### Step 1: Create Narrative

```python
narrative = {
    'name': f"{intention}: {spawn_node.name}",
    'weight': criticality * STATE_MULTIPLIER[CRYSTALLIZING],  # 1.5
    'energy': criticality * STATE_MULTIPLIER[CRYSTALLIZING],
    'content': render_cluster(path, focus_node),
    'embedding': crystallization_embedding,
}
narr_id = await graph.create_narrative(narrative)
```

### Step 2: Create Links

```python
# spawn_node → new_narrative
await graph.create_link({
    'node_a': spawn_node.id,
    'node_b': narr_id,
    'polarity': [0.8, 0.2],
    'hierarchy': mean_path_hierarchy,
    'permanence': mean_path_permanence,
    **subentity_emotions,
})

# new_narrative → focus_node
await graph.create_link({
    'node_a': narr_id,
    'node_b': focus_node.id,
    'polarity': [0.8, 0.2],
    'permanence': criticality,
    **subentity_emotions,
})
```

### Step 3: Record

```python
crystallized = narr_id
found_narratives[narr_id] = 1.0
```

### Step 4: Transition

```python
if depth > 0:
    transition to SEEKING  # Continue exploring
else:
    transition to MERGING  # Done
```

---

## ALGORITHM: MERGING

Terminal state. Results collected by parent or returned to actor.

```python
state = MERGING
completed_at = time.time()
# Child crystallizes if needed (v2.0)
if should_child_crystallize(self):
    self.crystallize()
# NO propagation to parent — graph is source of truth
```

---

## ALGORITHM: Awareness Tracking (v2.0)

### Step 1: Update Depth After Traversal

Called after each link traversal in SEEKING:

```python
def update_depth(subentity, link_hierarchy: float):
    if link_hierarchy > 0.2:
        subentity.depth[0] += link_hierarchy      # UP
    elif link_hierarchy < -0.2:
        subentity.depth[1] += abs(link_hierarchy)  # DOWN
    # PEER links (|hierarchy| <= 0.2) don't affect depth
```

### Step 2: Track Progress Toward Intention

Called after updating crystallization_embedding:

```python
def update_progress(subentity):
    current = cosine(subentity.crystallization_embedding, subentity.intention_embedding)
    if subentity.progress_history:
        delta = current - subentity.progress_history[-1]
    else:
        delta = current
    subentity.progress_history.append(delta)
```

### Step 3: Check Fatigue (Stopping Condition)

Called before continuing SEEKING:

```python
def is_fatigued(subentity, window=5, threshold=0.05) -> bool:
    if len(subentity.progress_history) < window:
        return False
    recent = subentity.progress_history[-window:]
    return all(abs(d) < threshold for d in recent)

# In state loop:
if is_fatigued(subentity):
    transition to REFLECTING  # Then MERGING
```

### Step 4: Child Crystallization Rule

```python
def should_child_crystallize(child) -> bool:
    if child.found_narratives:
        best_match = max(child.found_narratives.values())
        if best_match >= 0.9:
            return False  # Found exact match, no need to crystallize
    return True  # Crystallize exploration as new knowledge
```

---

## KEY FORMULAS

| Formula | Purpose |
|---------|---------|
| `link_score = alignment × polarity × (1-permanence) × self_novelty × sibling_divergence` | Link selection |
| `alignment = (1-intent_weight) × query_align + intent_weight × intention_align` | Query + intention balance |
| `self_novelty = 1 - max(cos(link, path))` | Avoid backtracking |
| `sibling_divergence = 1 - max(cos(link, sibling.crystallization))` | Spread exploration |
| `criticality = (1-satisfaction) × (depth/(depth+1))` | Urgency measure |
| `injection = criticality × STATE_MULTIPLIER[state]` | Energy to inject |
| `weight_gain = injection × permanence` | Energy → weight conversion |
| `color_weight = 1 - permanence` | How much link absorbs intention |
| `depth[0] += hierarchy` (if > 0.2) | Accumulate UP traversals (v2.0) |
| `depth[1] += abs(hierarchy)` (if < -0.2) | Accumulate DOWN traversals (v2.0) |
| `progress = cos(crystallization, intention)` | Measure goal alignment (v2.0) |
| `fatigued = all(abs(delta) < 0.05 for last 5)` | Stagnation detection (v2.0) |

---

## COMPLEXITY

| Operation | Time | Notes |
|-----------|------|-------|
| Link scoring | O(L × E) | L=links, E=embedding dim |
| Cosine similarity | O(E) | E=embedding dim |
| Self-novelty | O(P × E) | P=path length |
| Sibling divergence | O(S × E) | S=siblings |
| Branching | O(C × depth) | C=children per branch |
| Full exploration | O(B^D × L × E) | B=branching, D=depth |

**Bounded by:** max_depth (10), max_children (3), timeout (30s)
