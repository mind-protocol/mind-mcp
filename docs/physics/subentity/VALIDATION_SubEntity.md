# SubEntity Traversal Engine — Validation: What Must Be True

```
STATUS: STABLE
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_SubEntity.md
PATTERNS:        ./PATTERNS_SubEntity.md
BEHAVIORS:       ./BEHAVIORS_SubEntity.md
THIS:            VALIDATION_SubEntity.md (you are here)
ALGORITHM:       ./ALGORITHM_SubEntity.md
IMPLEMENTATION:  ./IMPLEMENTATION_SubEntity.md
HEALTH:          ./HEALTH_SubEntity.md
SYNC:            ./SYNC_SubEntity.md
```

---

## PURPOSE

These invariants protect the correctness and safety of the SubEntity traversal engine. If any invariant is violated, exploration either produces wrong results (bad graph_query answers), corrupts the graph (invalid energy/weight values), or fails to terminate (infinite loops, resource exhaustion).

---

## INVARIANTS

### V1: State Transitions Are Valid

**Why we care:** An invalid state transition means the state machine contract is broken. The ExplorationRunner dispatches to handlers based on state — an unexpected state causes either a silent no-op (lost exploration) or a crash. Every transition in the VALID_TRANSITIONS whitelist was explicitly designed; anything else is a bug.

```
MUST:   Every call to transition_to(new_state) succeeds only if new_state is in VALID_TRANSITIONS[current_state]
NEVER:  A SubEntity silently changes state without going through transition_to()
NEVER:  A SubEntity reaches a state not in the SubEntityState enum
```

### V2: Exploration Always Terminates

**Why we care:** A non-terminating exploration blocks the async event loop, starving all other SubEntities and the physics tick. The system becomes unresponsive. Four independent termination guarantees exist: MAX_STEPS, max_depth, timeout, and fatigue. All four must hold.

```
MUST:   Every exploration completes (reaches MERGING) or raises ExplorationTimeoutError
MUST:   Step count never exceeds MAX_STEPS (1000)
MUST:   Depth-limited SubEntities in SEEKING/BRANCHING/ABSORBING are forced to REFLECTING at max_depth
NEVER:  A SubEntity loops between REFLECTING and CRYSTALLIZING without eventually reaching MERGING
```

### V3: Energy Injection Is Non-Negative

**Why we care:** Negative energy injection would drain nodes during exploration, violating the physics model where exploration is an energy source. Energy can only decay via the physics tick, not via traversal.

```
MUST:   compute_energy_injection() returns >= 0 for all states
MUST:   STATE_MULTIPLIER values are >= 0 for all states
MUST:   Node energy after injection >= node energy before injection
NEVER:  A SubEntity decreases node.energy or node.weight during traversal
```

### V4: Crystallization Respects Novelty Threshold

**Why we care:** Creating duplicate narratives pollutes the graph. Near-identical narratives fragment knowledge and confuse future traversals. The 0.85 cosine threshold is the boundary between "genuinely new knowledge" and "a slightly different phrasing of existing knowledge."

```
MUST:   Crystallization only creates a narrative when max cosine similarity to ALL existing narratives < 0.85
MUST:   CrystallizedNarrative.is_novel == False when similarity >= 0.85 (no graph mutation)
NEVER:  A narrative is created with embedding cosine >= 0.85 to an existing narrative
```

### V5: Found Narratives Use Max-Alignment Merge

**Why we care:** found_narratives is a dict[str, float] where the value is the maximum alignment ever observed for that narrative. If alignment were summed or averaged instead, the semantic meaning would change — a narrative found twice with mediocre alignment would look better than one found once with perfect alignment.

```
MUST:   found_narratives[id] = max(old_value, new_alignment) on every update
NEVER:  found_narratives[id] is set to a value lower than its current value
NEVER:  found_narratives accumulates alignment (sum/average instead of max)
```

### V6: Children Inherit Query and Intention

**Why we care:** A child SubEntity exploring a different query than its parent would search for unrelated content. Children must explore the SAME question via different paths, not different questions.

```
MUST:   child.query == parent.query
MUST:   child.query_embedding == copy(parent.query_embedding)
MUST:   child.intention == parent.intention
MUST:   child.intention_embedding == copy(parent.intention_embedding)
NEVER:  A child SubEntity is created with different query/intention than its parent
```

### V7: ExplorationContext Is Single Source of Truth

**Why we care:** If SubEntities bypass the context and resolve references directly, lazy resolution breaks. Siblings can't compute divergence against each other, parents can't find children, and unregistered SubEntities become invisible to the system.

```
MUST:   Every SubEntity is registered with ExplorationContext before executing
MUST:   parent_id, sibling_ids, children_ids are string references resolved via context
NEVER:  A SubEntity holds direct object references to parent/siblings/children
NEVER:  A SubEntity executes without being registered in a context
```

### V8: Satisfaction Is Bounded [0, 1]

**Why we care:** Satisfaction drives the stopping condition (>= 0.8 stops exploration) and the criticality formula ((1 - satisfaction) x depth_factor). Unbounded satisfaction breaks both formulas.

```
MUST:   satisfaction is always in [0.0, 1.0]
MUST:   update_satisfaction() clamps to min(1.0, ...)
NEVER:  satisfaction exceeds 1.0 or goes below 0.0
```

### V9: Crystallization Embedding Evolves Monotonically

**Why we care:** The crystallization embedding represents "what this SubEntity would become if crystallized." It must incorporate ALL information encountered (query, intention, position, found narratives, path). Losing information means the crystallized narrative doesn't represent the full exploration.

```
MUST:   crystallization_embedding is updated at every traversal step via update_crystallization_embedding()
MUST:   The embedding incorporates query (0.4), intention (0.25), position (0.3), found narratives (0.2), path (0.1)
MUST:   The embedding is L2-normalized after computation
NEVER:  crystallization_embedding is reset to None during active exploration
```

### V10: Timeout Crashes Loud

**Why we care:** Silent timeout would return partial, potentially misleading results. The caller must know exploration was incomplete so it can decide how to handle the partial data. v1.7.2 D4 made this explicit: timeout is an error, not a graceful degradation.

```
MUST:   asyncio.TimeoutError is caught and re-raised as ExplorationTimeoutError
MUST:   ExplorationTimeoutError includes: timeout duration, SubEntity ID, depth, position, count of found narratives
NEVER:  Timeout returns a partial ExplorationResult without signaling the timeout condition
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | State machine integrity | CRITICAL |
| V2 | Exploration termination | CRITICAL |
| V3 | Energy physics correctness | HIGH |
| V4 | Graph knowledge quality (no duplicates) | HIGH |
| V5 | Found narratives accuracy | HIGH |
| V6 | Child exploration correctness | HIGH |
| V7 | Reference resolution integrity | HIGH |
| V8 | Satisfaction bounds | MEDIUM |
| V9 | Crystallization embedding completeness | MEDIUM |
| V10 | Timeout signaling | HIGH |

---

## MARKERS

<!-- @mind:proposition V11: Link score components should all be in [0, 1] range — currently polarity can be negative, which inverts the score. Consider whether negative scores are intentional or a bug -->
<!-- @mind:todo Verify V2 with a stress test: create a graph with cycles and confirm exploration terminates within MAX_STEPS -->
