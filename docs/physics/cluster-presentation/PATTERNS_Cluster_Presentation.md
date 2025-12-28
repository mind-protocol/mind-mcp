# Cluster Presentation Patterns

```
STATUS: STABLE (v1.9.1)
UPDATED: 2025-12-26
```

## Overview

When an MIND agent queries the graph, it receives a **cluster** — a subgraph activated by exploration. This document describes how to present that cluster in a readable and actionable format.

**v1.9.1**: Each node in paths and branching now includes its content in a ``` block.

---

## P1: Query vs Intention Drives Presentation

The same cluster looks different depending on WHY you're looking.

**Query**: What we're searching for in the graph.
```
"Recent events in the Great Hall"
"Auth module documentation"
"Current physics SYNC state"
```

**Intention**: Why the agent makes this query. What they'll do with the result.
```
"Write scene summary for narrator"
"Determine next possible moment for Edmund"
"Implement login feature"
"Decide which task to prioritize"
```

### Impact of Intention

| Intention | Privileges | Stops When | Returns |
|-----------|------------|------------|---------|
| "Write summary" | Rich content, narratives | Sufficient coverage | Full traversal + syntheses |
| "Next moment" | Moments with status=possible | Moment found | Moment + minimal context |
| "Verify coherence" | Tensions, contradictions | Tension detected | Tensions + sources |
| "Implement feature" | IMPLEMENTATION, code | Docs found | Docs + file paths |

---

## P2: Cluster Has Structure

A presented cluster has these sections:

1. **Header** — Query + Intention
2. **Response** — What directly answers the intention
3. **Path** — How we found the response (tree format)
4. **Dynamics** — Branching, convergence, tensions
5. **Gaps** — What's missing
6. **Temporal Chain** — Event order (if Moments)
7. **Stats** — What was traversed vs presented

---

## P3: Markers Signal Structure

| Marker | Meaning |
|--------|---------|
| ◆ | Point of interest (response, branching, tension) |
| ⚡ | Tension (contradictions) |
| → | Convergence |
| ○ | Gap (missing) |
| ✓ | Chosen path (when alternatives shown) |

---

## P4: Synthesis Unfolds From Floats

### Stored (compact)

Node: `surprising reliable the Servant's Revelation, incandescent (ongoing)`
Link: `suddenly definitively establishes, with admiration`

### Presented (prose)

The narrative **Servant's Revelation**, surprisingly reliable, is incandescent and ongoing. It suddenly, definitively established, with admiration, the **Hidden Truth**.

### Unfolding Rules

**Node template:**
```
{The} {node_type} **{name}**, {prefixes as adverbs}, is {energy} {and status}.
```

**Link template:**
```
{Pronoun} {pre-modifiers as adverbs}, {verb participle}, {post-modifiers}, {the} **{target.name}**.
```

---

## P5: Filtering Reduces 200 Nodes to 30

The traversal explores extensively. The presentation filters.

### What Gets Kept

1. **Direct Response** (1-5 nodes) — Match the intention
2. **Convergences** — 3+ incoming links
3. **Tensions** — Contradictory trust_disgust values
4. **Divergences** — 3+ outgoing links followed
5. **Main Path** — From start to response
6. **Relevant Gaps** — Pertinent to intention

### Scoring

```
score(node) =
  + 10  if direct_response
  + 5   if on main_path
  + 3   if convergence
  + 3   if tension
  + 2   if divergence
  + node.weight × 0.5
  + node.energy × 0.3
  + alignment(node, intention) × 2
```

---

## P6: Stats Show What's Hidden

Always include metadata so the agent knows what wasn't shown:

```yaml
cluster_stats:
  traversed_nodes: 200
  traversed_links: 300
  presented_nodes: 28
  presented_links: 35

available_details:
  - "Detail the Father's Betrayal"
  - "Detail the Falsification Mechanism"
```

---

## Related Documents

- ALGORITHM_Cluster_Presentation.md — Selection and formatting algorithms
- IMPLEMENTATION_Cluster_Presentation.md — Code locations
- docs/physics/PATTERNS_Physics.md (P11) — SubEntity exploration
- docs/schema/schema.yaml (v1.8) — Query/intention fields
