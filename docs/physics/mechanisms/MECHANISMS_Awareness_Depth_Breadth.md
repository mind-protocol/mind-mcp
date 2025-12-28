# MECHANISMS — Awareness Depth + Breadth (v1)

```
STATUS: CANONICAL
CREATED: 2025-12-26
UPDATED: 2025-12-26
IMPL: mind/physics/subentity.py
TESTS: mind/tests/test_subentity.py
```
---

## CHAIN

- PATTERNS_SubEntity.md (P11: Awareness Depth + Breadth)
- ALGORITHM_SubEntity.md (link score v2, fatigue stopping)
- VALIDATION_SubEntity.md (awareness invariants)

---

## PURPOSE

Track SubEntity exploration progress using two orthogonal dimensions:

- **Depth**: Vertical exploration via hierarchy links `[up, down]`
- **Breadth**: Horizontal exploration via peer links (hierarchy ≈ 0)

Stopping is **fatigue-based**: when progress toward intention stagnates.

---

## THE INSIGHT

A single narrative is incomplete. Understanding requires a **cluster**:

```
                    ┌─────────────────┐
                    │  Testing (abs)  │  ← UP (hierarchy > 0)
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Unit Test│──│ Int Test │──│ E2E Test │  ← PEERS (hierarchy ≈ 0)
        └────┬─────┘  └──────────┘  └──────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌───────┐┌───────┐┌───────┐
│ Input ││Output ││Assert │  ← DOWN (hierarchy < 0)
└───────┘└───────┘└───────┘
```

The SubEntity needs to know:
1. How deep it has gone (up into abstraction, down into details)
2. Whether it's making progress toward its intention
3. When to stop (fatigue, not arbitrary threshold)

---

## INPUTS (REQUIRED)

### SubEntity State
```python
depth: List[float] = [0.0, 0.0]  # [up, down] - unbounded accumulator
progress_history: List[float] = []  # delta toward intention per step
crystallization_embedding: List[float]  # evolves each step
intention_embedding: List[float]  # fixed goal
```

### Link Properties
- `hierarchy`: float [-1, 1] — link direction in abstraction hierarchy

### Computed
- `current_progress`: cosine(crystallization_embedding, intention_embedding)

---

## STEP 1 — Classify Link and Update Depth

After traversing a link:

```python
def update_depth(subentity, link_hierarchy: float):
    if link_hierarchy > 0.2:
        # UP: toward abstraction
        subentity.depth[0] += link_hierarchy
    elif link_hierarchy < -0.2:
        # DOWN: toward details
        subentity.depth[1] += abs(link_hierarchy)
    # else: PEER link, no depth change
```

**Key decision:** Depth is **unbounded** `[-∞, +∞]`. We accumulate, not compress.

- After 3 DOWN links with hierarchy=-0.5: `depth[1] = 1.5`
- After 10 DOWN links: `depth[1] = 5.0`
- No arbitrary ceiling

---

## STEP 2 — Track Progress Toward Intention

Each step, measure how close crystallization is to intention:

```python
def update_progress(subentity):
    current = cosine(subentity.crystallization_embedding, subentity.intention_embedding)

    if subentity.progress_history:
        previous = subentity.progress_history[-1]
        delta = current - previous
    else:
        delta = current  # First step

    subentity.progress_history.append(delta)
```

**Progress interpretation:**
- `delta > 0`: Getting closer to intention
- `delta < 0`: Moving away from intention
- `delta ≈ 0`: Stagnating

---

## STEP 3 — Detect Fatigue (Stopping Condition)

```python
def is_fatigued(subentity, window: int = 5, threshold: float = 0.05) -> bool:
    """Stop when progress stagnates over N steps."""
    if len(subentity.progress_history) < window:
        return False

    recent_deltas = subentity.progress_history[-window:]
    return all(abs(d) < threshold for d in recent_deltas)
```

**Fatigue = no meaningful progress for 5 consecutive steps.**

Alternative triggers:
- Novelty drops below 0.1
- No new narratives found for N steps

---

## STEP 4 — Child Crystallization Rule

Children crystallize systematically, EXCEPT when finding a high-match narrative:

```python
def should_child_crystallize(child) -> bool:
    # Don't crystallize if we found exactly what we were looking for
    if child.found_narratives:
        best_match = max(child.found_narratives.values())
        if best_match >= 0.9:
            return False  # Found it, no need to create new

    return True  # Crystallize our journey
```

**Rationale:**
- If child found the answer (90%+ match), just return it
- If child explored but didn't find exact match, crystallize the exploration as new knowledge

---

## STEP 5 — No Parent Propagation

Children do NOT propagate found_narratives/satisfaction to parent.

Instead:
- Child crystallizes → creates Narrative in graph
- Graph persists the knowledge
- Parent (or future explorations) find it via graph traversal

```python
# OLD (removed):
# parent.found_narratives.update(child.found_narratives)
# parent.satisfaction = max(parent.satisfaction, child.satisfaction)

# NEW:
if should_child_crystallize(child):
    child.crystallize()  # Persists to graph
# Parent continues its own exploration
```

---

## OUTPUTS

### Updated SubEntity Fields
```python
depth: List[float]  # [up_accumulated, down_accumulated]
progress_history: List[float]  # delta sequence toward intention
```

### Modified Behaviors
- Stopping is fatigue-based, not threshold-based
- Children crystallize systematically (unless 90%+ match found)
- No upward propagation of findings

---

## KEY FORMULAS

| Formula | Purpose |
|---------|---------|
| `depth[0] += hierarchy` (if > 0.2) | Accumulate UP traversals |
| `depth[1] += abs(hierarchy)` (if < -0.2) | Accumulate DOWN traversals |
| `progress = cos(crystallization, intention)` | Measure goal alignment |
| `delta = progress[t] - progress[t-1]` | Measure progress rate |
| `fatigued = all(abs(delta) < 0.05 for last 5)` | Stagnation detection |

---

## FAILURE MODES

| Mode | Symptom | Mitigation |
|------|---------|------------|
| Premature fatigue | Stops too early, threshold too sensitive | Increase window or decrease threshold |
| Never fatigues | Explores forever, threshold too loose | Add max_depth / timeout as backup |
| Over-crystallization | Too many narratives created | Increase match threshold (90% → 95%) |
| Under-crystallization | Knowledge lost | Decrease match threshold |

---

## ANTI-PATTERNS (What Doesn't Work)

| Anti-pattern | Why it fails |
|--------------|--------------|
| Bounded depth `[0, 1]` | Arbitrary compression loses information |
| Cluster size estimation | Adds complexity, physics already handles peer traversal |
| Parent aggregation | Creates memory bloat, graph is the source of truth |
| Fixed stopping thresholds | Different intentions need different exploration depth |

---

## VALIDATION HOOKS

- V1: `depth[0]` increases only on UP links (hierarchy > 0.2)
- V2: `depth[1]` increases only on DOWN links (hierarchy < -0.2)
- V3: `progress_history` length = step count
- V4: Fatigue triggers only after `window` steps of stagnation
- V5: Child crystallizes unless found_narrative alignment >= 0.9
- V6: Parent.found_narratives unchanged after child merge

---

## IMPLEMENTATION STATUS

All steps completed:

1. ✓ Added P11 to PATTERNS_SubEntity.md
2. ✓ Updated ALGORITHM_SubEntity.md with fatigue-based stopping
3. ✓ Updated VALIDATION_SubEntity.md with V7, V11-V13 invariants
4. ✓ Implemented in mind/physics/subentity.py (70 tests passing)
