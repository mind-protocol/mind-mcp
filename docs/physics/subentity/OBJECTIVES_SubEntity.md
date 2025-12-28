# SubEntity — Objectives

```
STATUS: CANONICAL
VERSION: v1.9
UPDATED: 2025-12-26
```

---

## CHAIN

```
THIS:           ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## PURPOSE

SubEntity exploration enables actors to query the graph with intention,
find relevant narratives, and create new understanding when gaps exist.

---

## PRIMARY OBJECTIVES (Ranked)

### O1: Actors Get Useful Answers

**Priority: CRITICAL**

When an actor needs information, they get it. The exploration returns
relevant narratives ranked by alignment with query and intention.

**Success signals:**
- found_narratives is non-empty for valid queries
- Alignment scores correlate with actual relevance
- Actor can use findings in subsequent decisions

**Tradeoffs:** Prioritize relevance over speed. A slow correct answer
beats a fast wrong one.

---

### O2: Gaps Become Knowledge

**Priority: HIGH**

When exploration finds no existing narrative that satisfies the intention,
it crystallizes a new narrative from the exploration path.

**Success signals:**
- Crystallization occurs when satisfaction remains low
- New narratives have high novelty (< 0.85 similarity to existing)
- Future explorations find what was previously missing

**Tradeoffs:** Crystallize conservatively. Better to return nothing than
pollute the graph with redundant narratives.

---

### O3: Graph Learns From Use

**Priority: HIGH**

Exploration shapes the graph. Frequently-traversed paths become more
salient. Links absorb intention embeddings. Energy creates heat trails.

**Success signals:**
- Link embeddings drift toward common intentions
- Frequently-explored paths have higher weight
- Future explorations on similar queries are faster

**Tradeoffs:** Learning should be gradual. High-permanence links resist
change to preserve established knowledge.

---

### O4: Parallel Exploration Spreads

**Priority: MEDIUM**

When branching occurs, siblings explore different paths. No redundant work.

**Success signals:**
- Sibling divergence ≥ 0.7 on average
- Children find different narratives
- Path overlap between siblings < 30%

**Tradeoffs:** Some overlap is acceptable if paths converge on important
narratives. Divergence shouldn't prevent finding the same truth.

---

### O5: Urgency Deepens Search

**Priority: MEDIUM**

Critical needs (high criticality) get deeper exploration, accept weaker
alignments, and are more likely to crystallize.

**Success signals:**
- High-criticality explorations go deeper
- Weak-but-relevant findings are accepted when desperate
- Crystallization rate higher for critical explorations

**Tradeoffs:** Depth costs time. Very deep exploration may timeout.

---

### O6: Context Accompanies Findings

**Priority: MEDIUM**

Findings include not just what was found but alignment scores, emotional
context, and the path taken.

**Success signals:**
- ExplorationResult includes alignment per narrative
- Emotional state (Plutchik axes) tracked
- Path available for debugging/understanding

**Tradeoffs:** Context adds overhead. Keep what's useful, not everything.

---

## NON-OBJECTIVES

### NOT: Real-Time Response

SubEntity exploration is async and may take seconds. It's not designed
for real-time UI responsiveness. Use caching or pre-exploration for
time-sensitive queries.

### NOT: Exhaustive Search

We don't explore every path. We follow aligned links and stop when
satisfied. Completeness is not a goal; relevance is.

### NOT: Deterministic Paths

Same query may take different paths on different runs (depending on
graph state, link weights). Determinism is not guaranteed or needed.

---

## TRADEOFFS

| When | Prefer | Over |
|------|--------|------|
| Relevance vs Speed | Relevance | Speed |
| Depth vs Breadth | Breadth (via branching) | Single deep path |
| Crystallization vs Nothing | Nothing | Redundant crystallization |
| Divergence vs Convergence | Divergence | Duplicate paths |
| Context vs Overhead | Essential context | Full trace |

---

## SUCCESS METRICS

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Answer rate | ≥ 80% explorations find ≥1 narrative | < 50% |
| Efficiency | ≥ 0.2 narratives per step | < 0.05 |
| Satisfaction velocity | ≥ 0.1 per step | ≤ 0.02 |
| Sibling divergence | ≥ 0.7 mean | < 0.5 |
| Crystallization novelty | ≥ 0.85 | < 0.7 |
| Timeout rate | < 5% | ≥ 20% |
