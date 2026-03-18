# OBJECTIVES — SubEntity Traversal Engine

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against runtime/physics/subentity.py v2.1
```

---

## CHAIN

```
THIS:            OBJECTIVES_SubEntity.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md

IMPL:           runtime/physics/subentity.py
                runtime/physics/exploration.py
                runtime/physics/link_scoring.py
                runtime/physics/crystallization.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Semantic graph traversal** — Given a query (what to find) and an intention (why finding it), traverse the graph to locate relevant narratives. This is the backbone of `graph_query`, `subcall`, and the cognitive tick loop. Everything downstream depends on this producing high-quality results.

2. **Knowledge crystallization** — When exploration discovers novel patterns not captured by existing narratives, create new narrative nodes in the graph. The graph grows through exploration, not manual insertion. Without crystallization, the system never learns.

3. **Energy injection as traversal side-effect** — Every step of exploration injects energy into traversed nodes and links, creating "heat trails" that persist after exploration. This ties traversal to the physics tick: explored paths become more visible, reinforcing the attention economy of the graph.

4. **Bounded exploration with fatigue** — Exploration must terminate. Depth limits, step limits, timeout, and fatigue detection (stagnation over N steps) ensure SubEntities converge. Unbounded exploration would starve the system.

5. **Parallel branching with sibling divergence** — At branch points (Moment nodes with multiple outgoing links), spawn child SubEntities that explore different paths simultaneously. Sibling divergence scoring ensures children spread apart rather than duplicating effort.

## NON-OBJECTIVES

- **Persistent identity** — SubEntities are temporary consciousness fragments. They exist only during exploration and are garbage collected after. They are not actors, not citizens, not persistent graph nodes.
- **Emotional modeling** — SubEntities carry no emotions. `get_emotions()` returns an empty list. Emotional weight belongs to actors and links, not to traversal fragments.
- **Direct graph mutation outside crystallization** — SubEntities inject energy and create narratives, but they do not delete nodes, restructure relationships, or modify node content (except energy/weight fields).
- **Caching or memoization** — Each exploration is independent. SubEntities do not remember previous explorations or share state between runs.

## TRADEOFFS (canonical decisions)

- When **traversal speed** conflicts with **exploration thoroughness**, choose thoroughness. The timeout (default 30s) is the safety valve, not premature termination.
- When **novelty** conflicts with **relevance**, choose relevance. Link scoring weights semantic alignment (75% query, 25% intention) above novelty factors. A highly relevant but familiar path beats a novel but irrelevant one.
- When **parent memory** conflicts with **graph truth**, choose graph truth. v2.0 removed child-to-parent result propagation. Children crystallize to graph; parent does not aggregate child findings into its own memory. The graph is the source of truth.
- We accept **O(depth x links) embedding computations** to preserve **accurate semantic scoring** at every step.

## SUCCESS SIGNALS (observable)

- `graph_query` returns semantically relevant narratives for arbitrary natural-language queries
- Crystallized narratives are novel (cosine similarity < 0.85 to all existing narratives)
- Energy injection creates measurable heat trails along explored paths (node.energy increases)
- Exploration completes within timeout for graphs up to 10,000 nodes
- Branching children explore divergent paths (sibling divergence score > 0.5 on average)
- Fatigue detection stops stagnant explorations within 5 steps of plateau
