# SubEntity Traversal Engine — Behaviors: Observable Effects of Graph Exploration

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against runtime/physics/subentity.py v2.1
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
THIS:            BEHAVIORS_SubEntity.md (you are here)
PATTERNS:        ./PATTERNS_SubEntity.md
ALGORITHM:       ./ALGORITHM_SubEntity.md
VALIDATION:      ./VALIDATION_SubEntity.md
HEALTH:          ./HEALTH_SubEntity.md
IMPLEMENTATION:  ./IMPLEMENTATION_SubEntity.md
SYNC:            ./SYNC_SubEntity.md

IMPL:            runtime/physics/subentity.py
                 runtime/physics/exploration.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Traversal Follows Semantic Alignment

**Why:** Without semantic scoring, traversal would follow random or structural paths. Semantic alignment ensures the SubEntity moves toward nodes related to what it is searching for, producing relevant results for graph_query and subcall.

```
GIVEN:  A SubEntity in SEEKING state at a node with multiple outgoing links
WHEN:   The SubEntity evaluates outgoing links
THEN:   Links are scored using: alignment x polarity x (1-permanence) x self_novelty x sibling_divergence
AND:    alignment = 0.75 x cosine(query_embedding, link_embedding) + 0.25 x cosine(intention_embedding, link_embedding)
AND:    The SubEntity traverses the highest-scoring link
```

### B2: Branching Spawns Divergent Children at Moment Nodes

**Why:** Single-path traversal misses alternative connections. Branching at Moment nodes (which represent decision points or events) enables parallel exploration of multiple promising paths, increasing recall.

```
GIVEN:  A SubEntity in SEEKING state arrives at a Moment node
WHEN:   2 or more outgoing links have positive scores
THEN:   The SubEntity transitions to BRANCHING
AND:    Up to 3 child SubEntities are spawned (one per candidate link)
AND:    Children run concurrently as async coroutines
AND:    Each child inherits query, intention, and query_embedding from parent
AND:    Sibling IDs are set so children can compute sibling divergence
```

### B3: Resonating Measures Narrative Alignment

**Why:** Finding a narrative node is the primary goal of exploration. Resonating measures how well the found narrative matches the search intent, updating satisfaction and determining whether exploration should continue.

```
GIVEN:  A SubEntity arrives at a narrative node
WHEN:   The SubEntity transitions to RESONATING
THEN:   alignment = cosine(intention_embedding, narrative_embedding)
AND:    found_narratives[narrative_id] = max(existing_alignment, new_alignment)
AND:    satisfaction increases by: alignment / (sum_found_alignments + 1)
AND:    If satisfaction >= 0.8, transition to MERGING (done)
AND:    If satisfaction < 0.8, transition to SEEKING (continue)
```

### B4: Energy Injection Creates Heat Trails

**Why:** Traversal is not read-only. Energy injection ties the cognitive layer to the physics layer, making explored paths more visible to the decay/propagation tick and to future explorations. Without this, exploration would leave no trace.

```
GIVEN:  A SubEntity at any active state (SEEKING, ABSORBING, RESONATING, CRYSTALLIZING)
WHEN:   The SubEntity processes a traversal step
THEN:   injection = criticality x STATE_MULTIPLIER[state]
AND:    node.energy += injection
AND:    node.weight += injection x node.permanence
AND:    STATE_MULTIPLIER values: SEEKING=0.5, ABSORBING=1.0, RESONATING=2.0, CRYSTALLIZING=1.5, MERGING=0.0
```

### B5: Crystallization Produces Novel Narratives

**Why:** The graph grows through exploration. When a SubEntity discovers a pattern not captured by existing narratives, it crystallizes a new narrative node, linking it to the run node and focus node. Without crystallization, the graph is static.

```
GIVEN:  A SubEntity in REFLECTING state with satisfaction <= 0.5
WHEN:   The SubEntity transitions to CRYSTALLIZING
THEN:   A crystallization embedding is computed from query (0.4), intention (0.25), position (0.3), found narratives (0.2), path (0.1)
AND:    Novelty is checked: max cosine similarity to existing narratives must be < 0.85
AND:    If novel: a narrative node is created with the crystallization embedding
AND:    Links are created: run_node -> narrative and narrative -> focus_node
AND:    The SubEntity's crystallized field is set to the new narrative ID
AND:    Path links are backpropagated with crystallization embedding
```

### B6: Fatigue Stops Stagnant Exploration

**Why:** Some explorations enter regions of the graph with no useful connections. Without fatigue detection, these explorations waste computation until hitting the hard timeout. Fatigue provides an earlier, softer stopping condition based on lack of progress.

```
GIVEN:  A SubEntity with 5 or more progress history entries
WHEN:   All of the last 5 progress deltas are below 0.05 in absolute value
THEN:   is_fatigued() returns True
AND:    The exploration runner should terminate this SubEntity
```

### B7: Awareness Depth Tracks Hierarchy Direction

**Why:** As a SubEntity traverses links, it may move up (toward abstraction, hierarchy > 0.2) or down (toward detail, hierarchy < -0.2). Tracking this as an unbounded accumulator enables the system to understand whether an exploration went broad or deep.

```
GIVEN:  A SubEntity traverses a link with hierarchy value h
WHEN:   h > 0.2
THEN:   awareness_depth[0] (UP) += h
WHEN:   h < -0.2
THEN:   awareness_depth[1] (DOWN) += |h|
WHEN:   |h| <= 0.2
THEN:   No depth change (peer link)
```

### B8: Reflecting Backpropagates Color Along Useful Paths

**Why:** Not all explored paths are useful. Backpropagation during REFLECTING colors only paths that led to discoveries (satisfaction > 0.5), using the intention embedding. This creates semantic trails in the graph — links that led to relevant findings become "colored" with what was found along them.

```
GIVEN:  A SubEntity in REFLECTING state with satisfaction > 0.5
WHEN:   The SubEntity has a non-empty path
THEN:   Path links are colored with the intention embedding
AND:    Color attenuates at 0.8 per hop (nearest links get strongest color)
AND:    Permanence is boosted by 0.05 x satisfaction
AND:    Colored links are persisted back to the graph
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Semantic graph traversal | Link scoring is the mechanism that makes traversal intelligent |
| B2 | Parallel branching with sibling divergence | Branching increases coverage; divergence prevents duplication |
| B3 | Semantic graph traversal | Resonating is how the SubEntity evaluates found results |
| B4 | Energy injection as traversal side-effect | Heat trails connect cognitive traversal to physics tick |
| B5 | Knowledge crystallization | New narratives grow the graph from exploration |
| B6 | Bounded exploration with fatigue | Soft stopping prevents wasted computation |
| B7 | Semantic graph traversal | Hierarchy tracking informs traversal depth decisions |
| B8 | Energy injection as traversal side-effect | Backpropagation reinforces useful graph paths |

---

## INPUTS / OUTPUTS

### Primary Function: `ExplorationRunner.explore()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| actor_id | str | ID of the actor spawning the exploration |
| query | str | Text of what to search for |
| query_embedding | List[float] | Vector embedding of the query |
| intention | str | Text of why searching (defaults to query) |
| intention_embedding | List[float] | Vector embedding of intention (defaults to query_embedding) |
| origin_moment | str (optional) | Moment node that triggered the exploration |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| result | ExplorationResult | Contains: found_narratives dict, crystallized narrative ID, satisfaction score, depth reached, duration, children results |

**Side Effects:**

- Node energy and weight modified at every traversal step (energy injection)
- Link energy and weight modified during path backpropagation (REFLECTING, CRYSTALLIZING)
- New narrative nodes created in the graph (CRYSTALLIZING)
- New links created connecting crystallized narratives to run/focus nodes
- Node synthesis may be regenerated if embedding drift detected

---

## EDGE CASES

### E1: No Outgoing Links

```
GIVEN:  A SubEntity in SEEKING at a node with no outgoing links
THEN:   Transition to REFLECTING (then CRYSTALLIZING or MERGING)
```

### E2: All Links Score Below Minimum

```
GIVEN:  A SubEntity in SEEKING at a node where all outgoing links score below min_link_score (0.1)
THEN:   Transition to REFLECTING (treated as dead end)
```

### E3: Only One Branch Candidate

```
GIVEN:  A SubEntity in BRANCHING but only 1 link passes the relative score threshold (0.5)
THEN:   Fall back to SEEKING (not worth branching for a single path)
```

### E4: Depth Limit Reached

```
GIVEN:  A SubEntity at depth >= max_depth (10) in SEEKING, BRANCHING, or ABSORBING
THEN:   Force transition to REFLECTING
AND:    This does NOT apply to CRYSTALLIZING or MERGING (to avoid infinite loops)
```

### E5: Timeout

```
GIVEN:  Exploration runs longer than timeout_s (30.0)
THEN:   ExplorationTimeoutError is raised (v1.7.2 D4: crash loud, no partial merge)
```

### E6: 90%+ Match Found by Child

```
GIVEN:  A child SubEntity found a narrative with alignment >= 0.9
THEN:   should_child_crystallize() returns False (the knowledge already exists)
```

---

## ANTI-BEHAVIORS

### A1: Infinite Exploration Loop

```
GIVEN:   A SubEntity in any state
WHEN:    State transitions occur
MUST NOT: Loop indefinitely between SEEKING/REFLECTING/CRYSTALLIZING
INSTEAD:  MAX_STEPS=1000 hard limit, fatigue detection (5-step stagnation), depth limit, timeout
```

### A2: Child Results Overwrite Parent Findings

```
GIVEN:   A parent SubEntity after children complete (v2.0)
WHEN:    merge_child_results() is called
MUST NOT: Propagate child found_narratives or satisfaction to parent
INSTEAD:  Children crystallize directly to graph; parent keeps only its own findings
```

### A3: Crystallizing Duplicates

```
GIVEN:   A SubEntity in CRYSTALLIZING state
WHEN:    The crystallization embedding is >= 0.85 similar to an existing narrative
MUST NOT: Create a new narrative (it would be a near-duplicate)
INSTEAD:  Return CrystallizedNarrative with is_novel=False
```

### A4: Invalid State Transitions

```
GIVEN:   A SubEntity in state X
WHEN:    Attempting transition to state Y not in VALID_TRANSITIONS[X]
MUST NOT: Silently change state
INSTEAD:  Raise SubEntityTransitionError with details of invalid transition
```

---

## MARKERS

<!-- @mind:proposition Consider B9: "Absorbing triggers crystallization" — ABSORBING can transition directly to CRYSTALLIZING when alignment > 0.7 AND novelty > 0.7, but this path is rarely exercised and may need validation -->
