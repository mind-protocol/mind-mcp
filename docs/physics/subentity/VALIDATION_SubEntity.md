# SubEntity — Validation

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
ALGORITHM:      ./ALGORITHM_SubEntity.md
THIS:           ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## PURPOSE

Validation invariants define WHAT MUST BE TRUE for SubEntity exploration
to be correct. If any invariant is violated, it's a bug — not a variance
in interpretation or configuration.

---

## INVARIANTS

### V1: State Machine Integrity

**Value protected:** Exploration follows defined flow.

**Why we care:** Invalid transitions indicate bugs that could cause
undefined behavior, infinite loops, or lost results.

**MUST:** All state transitions follow VALID_TRANSITIONS map
**MUST:** Terminal state (MERGING) cannot transition further
**NEVER:** Skip states (e.g., SEEKING → MERGING without REFLECTING)

```python
def check_state_transitions(log: List[StepRecord]) -> bool:
    VALID_TRANSITIONS = {
        "seeking": {"branching", "absorbing", "resonating", "reflecting", "seeking"},
        "branching": {"merging", "reflecting"},
        "absorbing": {"seeking", "resonating", "reflecting", "crystallizing"},
        "resonating": {"reflecting", "seeking"},
        "reflecting": {"seeking", "crystallizing", "merging"},
        "crystallizing": {"seeking", "merging"},
        "merging": set(),  # terminal
    }

    for i in range(1, len(log)):
        prev = log[i-1].state_after.lower()
        curr = log[i].state_after.lower()
        if curr not in VALID_TRANSITIONS.get(prev, set()):
            return False  # Invalid transition
    return True
```

**Priority:** CRITICAL

---

### V2: Tree Structure Consistency

**Value protected:** Parent-child-sibling relationships are valid.

**Why we care:** Corrupt tree structure breaks merging, loses findings,
and causes reference errors.

**MUST:** Every child.parent_id == parent.id
**MUST:** parent.children_ids contains all child.id values
**MUST:** sibling_ids excludes self.id
**NEVER:** Circular parent references

```python
def check_tree_consistency(context: ExplorationContext) -> bool:
    for se in context.all_active():
        # Parent-child consistency
        if se.parent_id:
            parent = context.get(se.parent_id)
            if not parent or se.id not in parent.children_ids:
                return False

        # Sibling consistency
        if se.id in se.sibling_ids:
            return False  # Can't be own sibling

        # No circular refs (parent chain should terminate)
        visited = set()
        current = se
        while current.parent_id:
            if current.parent_id in visited:
                return False  # Circular!
            visited.add(current.parent_id)
            current = context.get(current.parent_id)
            if not current:
                break

    return True
```

**Priority:** CRITICAL

---

### V3: Path Monotonicity

**Value protected:** Exploration history is preserved.

**Why we care:** Path is used for self-novelty, backward coloring, and
crystallization. Lost path entries corrupt these.

**MUST:** len(path) increases or stays same each step
**MUST:** Path entries are valid (link_id, node_id) tuples
**NEVER:** Path entries removed or modified after addition

```python
def check_path_monotonicity(log: List[StepRecord]) -> bool:
    prev_len = 0
    for step in log:
        path_len = step.depth  # depth tracks path length
        if path_len < prev_len:
            return False  # Path shrunk
        prev_len = path_len
    return True
```

**Priority:** HIGH

---

### V4: Satisfaction Monotonicity

**Value protected:** Progress is never lost.

**Why we care:** Finding things should increase satisfaction. Decreasing
satisfaction indicates lost findings or corrupted state.

**MUST:** satisfaction >= previous satisfaction (within same exploration)
**MUST:** satisfaction ∈ [0, 1]
**NEVER:** satisfaction decreases during SEEKING/RESONATING

```python
def check_satisfaction_monotonicity(log: List[StepRecord]) -> bool:
    prev_satisfaction = 0.0
    for step in log:
        if step.satisfaction < prev_satisfaction - 0.001:  # tolerance for float
            return False  # Satisfaction decreased
        if step.satisfaction < 0 or step.satisfaction > 1:
            return False  # Out of bounds
        prev_satisfaction = step.satisfaction
    return True
```

**Priority:** HIGH

---

### V5: Energy Conservation

**Value protected:** Energy injection is accountable.

**Why we care:** Energy injection creates heat trails. Incorrect injection
distorts graph learning.

**MUST:** injection = criticality × STATE_MULTIPLIER[state]
**MUST:** weight_gain = injection × permanence
**MUST:** No negative energy or weight values

```python
def check_energy_injection(step: StepRecord, node: Dict) -> bool:
    STATE_MULTIPLIER = {
        "seeking": 0.5, "branching": 0.5, "absorbing": 1.0,
        "resonating": 2.0, "reflecting": 0.5, "crystallizing": 1.5,
        "merging": 0.0
    }

    expected = step.criticality * STATE_MULTIPLIER.get(step.state_after.lower(), 0)

    if node.get('energy', 0) < 0 or node.get('weight', 0) < 0:
        return False  # Negative values

    # Energy should have increased by approximately expected amount
    # (tolerance for concurrent updates)
    return True
```

**Priority:** MEDIUM

---

### V6: Crystallization Novelty Gate

**Value protected:** No duplicate narratives created.

**Why we care:** Duplicate narratives pollute the graph, cause confusion,
and waste storage.

**MUST:** Only crystallize if max(cos(embedding, existing)) < 0.85
**MUST:** Crystallized narrative has unique ID
**NEVER:** Crystallize if highly similar narrative exists

```python
def check_crystallization_novelty(
    crystallized_embedding: List[float],
    existing_narratives: List[Tuple[str, List[float]]]
) -> bool:
    NOVELTY_THRESHOLD = 0.85

    for narr_id, narr_embedding in existing_narratives:
        similarity = cosine(crystallized_embedding, narr_embedding)
        if similarity >= NOVELTY_THRESHOLD:
            return False  # Too similar, shouldn't crystallize

    return True
```

**Priority:** HIGH

---

### V7: Child Crystallization (v2.0)

**Value protected:** Knowledge persists to graph, not lost in memory.

**Why we care:** Children's discoveries must be persisted. Graph is
source of truth, not parent aggregation.

**MUST:** Child crystallizes to graph unless found 90%+ match
**MUST:** Parent.found_narratives unchanged after child merge (no propagation)
**MUST:** Crystallized narrative exists in graph after merge
**NEVER:** Propagate findings from child to parent (v2.0 change)

```python
def check_child_crystallization(child: SubEntity, graph) -> bool:
    # Check crystallization rule
    if child.found_narratives:
        best_match = max(child.found_narratives.values())
        if best_match >= 0.9:
            # Should NOT crystallize
            return child.crystallized is None
        else:
            # Should crystallize
            if child.crystallized is None:
                return False
            # Verify it's in graph
            return graph.node_exists(child.crystallized)
    else:
        # No findings = should crystallize
        if child.crystallized is None:
            return False
        return graph.node_exists(child.crystallized)

def check_no_parent_propagation(parent: SubEntity, children: List[SubEntity]) -> bool:
    # Parent should NOT have inherited child findings (v2.0)
    for child in children:
        for narr_id in child.found_narratives:
            if narr_id in parent.found_narratives:
                # Could be coincidence (parent found same thing)
                # But if alignment is identical, it's propagation
                if parent.found_narratives[narr_id] == child.found_narratives[narr_id]:
                    return False  # Suspicious - likely propagated
    return True
```

**Priority:** CRITICAL

---

### V8: Timeout Behavior

**Value protected:** Runaway exploration fails loudly.

**Why we care:** Silent timeouts could leave actor waiting forever or
return corrupted partial results.

**MUST:** Exploration times out after config.timeout_s
**MUST:** ExplorationTimeoutError raised (not silent return)
**MUST:** Partial results NOT merged on timeout (v1.7.2 D4)

```python
def check_timeout_behavior(result: ExplorationResult, duration_s: float, config: ExplorationConfig) -> bool:
    if duration_s > config.timeout_s:
        # Should have raised ExplorationTimeoutError
        # If we got a result, timeout wasn't enforced
        return False
    return True
```

**Priority:** HIGH

---

### V9: Link Score Bounds

**Value protected:** Link selection is well-defined.

**Why we care:** Unbounded scores could cause selection errors or
division issues.

**MUST:** All score components ∈ [0, 1]
**MUST:** Final link_score ∈ [0, 1]
**NEVER:** Negative scores or scores > 1

```python
def check_link_score_bounds(score: float, components: Dict[str, float]) -> bool:
    for name, value in components.items():
        if value < 0 or value > 1:
            return False
    if score < 0 or score > 1:
        return False
    return True
```

**Priority:** MEDIUM

---

### V10: Embedding Dimension Consistency

**Value protected:** Vector operations are valid.

**Why we care:** Mismatched embedding dimensions cause runtime errors
or incorrect cosine similarities.

**MUST:** All embeddings have same dimension
**MUST:** Embeddings are non-empty lists
**NEVER:** None or empty list where embedding expected

```python
def check_embedding_consistency(subentity: SubEntity) -> bool:
    embeddings = [
        subentity.query_embedding,
        subentity.intention_embedding,
        subentity.crystallization_embedding
    ]

    dims = set()
    for emb in embeddings:
        if emb is None or len(emb) == 0:
            return False
        dims.add(len(emb))

    if len(dims) > 1:
        return False  # Inconsistent dimensions

    return True
```

**Priority:** HIGH

---

### V11: Depth Accumulation (v2.0)

**Value protected:** Structural exploration is tracked accurately.

**Why we care:** Depth informs stopping decisions and exploration quality.
Incorrect depth breaks fatigue detection.

**MUST:** `depth[0]` increases only when traversing UP links (hierarchy > 0.2)
**MUST:** `depth[1]` increases only when traversing DOWN links (hierarchy < -0.2)
**MUST:** Depth values are unbounded accumulators (not clamped)
**NEVER:** Depth decreases

```python
def check_depth_accumulation(log: List[StepRecord]) -> bool:
    prev_depth = [0.0, 0.0]
    for step in log:
        # Monotonicity
        if step.depth[0] < prev_depth[0] or step.depth[1] < prev_depth[1]:
            return False

        # Check increment matches link hierarchy
        if step.link_hierarchy is not None:
            if step.link_hierarchy > 0.2:
                # Should have increased depth[0]
                expected_delta = step.link_hierarchy
                actual_delta = step.depth[0] - prev_depth[0]
                if abs(actual_delta - expected_delta) > 0.01:
                    return False
            elif step.link_hierarchy < -0.2:
                # Should have increased depth[1]
                expected_delta = abs(step.link_hierarchy)
                actual_delta = step.depth[1] - prev_depth[1]
                if abs(actual_delta - expected_delta) > 0.01:
                    return False

        prev_depth = list(step.depth)
    return True
```

**Priority:** HIGH

---

### V12: Progress History Consistency (v2.0)

**Value protected:** Fatigue detection has accurate data.

**Why we care:** Progress history drives stopping. Corrupted history
causes premature or late stopping.

**MUST:** `len(progress_history)` equals step count
**MUST:** Each entry is delta (current - previous), not absolute
**MUST:** First entry equals initial progress (not delta)

```python
def check_progress_history(log: List[StepRecord], subentity: SubEntity) -> bool:
    if len(subentity.progress_history) != len(log):
        return False  # Length mismatch

    for i, (step, delta) in enumerate(zip(log, subentity.progress_history)):
        current_progress = cosine(step.crystallization_embedding, step.intention_embedding)
        if i == 0:
            if abs(delta - current_progress) > 0.01:
                return False  # First should be absolute
        else:
            prev_progress = cosine(log[i-1].crystallization_embedding, step.intention_embedding)
            expected_delta = current_progress - prev_progress
            if abs(delta - expected_delta) > 0.01:
                return False

    return True
```

**Priority:** HIGH

---

### V13: Fatigue Stopping Correctness (v2.0)

**Value protected:** Stopping is intention-appropriate.

**Why we care:** Stopping too early loses findings. Stopping too late
wastes resources.

**MUST:** Fatigue only triggers after `window` consecutive low-delta steps
**MUST:** All deltas in window < threshold (0.05 default)
**NEVER:** Stop before minimum steps (window size)

```python
def check_fatigue_stopping(subentity: SubEntity, stopped_by_fatigue: bool) -> bool:
    WINDOW = 5
    THRESHOLD = 0.05

    if len(subentity.progress_history) < WINDOW:
        # Can't be fatigued yet
        if stopped_by_fatigue:
            return False

    recent = subentity.progress_history[-WINDOW:]
    is_fatigued = all(abs(d) < THRESHOLD for d in recent)

    if stopped_by_fatigue and not is_fatigued:
        return False  # Stopped but shouldn't have

    return True
```

**Priority:** HIGH

---

## PRIORITY TABLE

| Priority | Meaning | Invariants |
|----------|---------|------------|
| CRITICAL | System fails if violated | V1, V2, V7 |
| HIGH | Major value lost | V3, V4, V6, V8, V10, V11, V12, V13 |
| MEDIUM | Partial value lost | V5, V9 |

---

## INVARIANT INDEX

| ID | Value Protected | Priority | Check Function |
|----|-----------------|----------|----------------|
| V1 | State machine flow | CRITICAL | `check_state_transitions` |
| V2 | Tree structure | CRITICAL | `check_tree_consistency` |
| V3 | Path history | HIGH | `check_path_monotonicity` |
| V4 | Satisfaction progress | HIGH | `check_satisfaction_monotonicity` |
| V5 | Energy accounting | MEDIUM | `check_energy_injection` |
| V6 | Narrative uniqueness | HIGH | `check_crystallization_novelty` |
| V7 | Child crystallization (v2.0) | CRITICAL | `check_child_crystallization` |
| V8 | Timeout enforcement | HIGH | `check_timeout_behavior` |
| V9 | Score bounds | MEDIUM | `check_link_score_bounds` |
| V10 | Embedding dimensions | HIGH | `check_embedding_consistency` |
| V11 | Depth accumulation (v2.0) | HIGH | `check_depth_accumulation` |
| V12 | Progress history (v2.0) | HIGH | `check_progress_history` |
| V13 | Fatigue stopping (v2.0) | HIGH | `check_fatigue_stopping` |

---

## VERIFICATION PROCEDURE

1. Run unit tests in `mind/tests/test_subentity.py`
2. Run traversal logger tests in `mind/tests/test_traversal_logger.py`
3. Execute exploration on test graph, verify all invariants
4. Check logs for anomaly warnings (see HEALTH_SubEntity.md)
5. Record results in SYNC_SubEntity.md
