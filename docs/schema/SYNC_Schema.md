# Schema — Sync: Current State

```
LAST_UPDATED: 2025-12-26
UPDATED_BY: Claude (v1.8.1 node subtype field)
```

---

## CURRENT STATE

Schema module is **DRAFT v1.8.1** — added node subtype field.

**v1.8.1 changes (NEW):**
- **NodeBase.type** (string, nullable) — Subtype within node_type:
  - actor: null, "player", "npc", "system"
  - moment: "event", "decision", "action"
  - narrative: "issue", "objective", "task", "belief", "pattern", "documentation"
  - space: "area", "module", "directory"
  - thing: "file", "uri", "artifact"
- Used by doctor system for issues/objectives/tasks
- Already implemented in `mind/doctor_graph.py`

**v1.8 changes:**
- Query vs Intention separation (query=WHAT, intention=WHY)
- IntentionType enum: SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE
- Combined link scoring with query + intention alignment

**v1.7 changes:
- **NodeBase temporal fields:**
  - `created_at_s` (int, required) — Unix timestamp of node creation
  - `updated_at_s` (int, required) — Unix timestamp of last modification
  - `last_traversed_at_s` (int, nullable) — Unix timestamp of last traversal by a sub-entity
- **MomentBase temporal fields** (extends NodeBase):
  - `started_at_s` (int, nullable) — Unix timestamp when moment became active
  - `completed_at_s` (int, nullable) — Unix timestamp when moment was resolved
  - `duration_s` (int, nullable) — Duration in seconds (if known/estimated)
- **LinkBase temporal fields:**
  - `created_at_s` (int, required) — Unix timestamp of link creation
  - `updated_at_s` (int, required) — Unix timestamp of last modification
  - `last_traversed_at_s` (int, nullable) — Unix timestamp of last traversal by a sub-entity

**v1.6.1 refinements (NEW):**
- **SubEntity structure** — origin_moment, siblings, children fields for tree tracking
- **found_narratives** — now `[(narrative_id, alignment), ...]` tuples with alignment scores
- **crystallization_embedding** — computed at EACH step, not just at crystallization
- **Sibling divergence** — SubEntities avoid paths their siblings are exploring
- **Bidirectional vocabulary** — same grammar for agent input AND synthesis output
- **Link score formula**: `semantic × polarity × (1 - permanence) × self_novelty × sibling_divergence`

**v1.6 changes APPLIED:**
- **SubEntities** — temporary consciousness fragments that traverse graph
- **State machine**: SEEKING → BRANCHING → RESONATING → REFLECTING → CRYSTALLIZING → MERGING
- **Criticality** drives exploration: `(1 - satisfaction) × (depth / (depth + 1))`
- **Forward coloring**: links absorb intention (weight = 1 - permanence)
- **Backward coloring**: permanence increases on positive alignment during REFLECTING
- **Branching only on Moments** (threshold: outgoing/incoming < 2:1)
- **Narratives created by crystallization** (not directly)
- **No arbitrary constants** — all rates derived from graph properties

**v1.5 changes APPLIED:**
- Traversals **color** links (emotions, permanence, polarity, embedding)
- **Emotions emerge** from actor→narrative links, not declared
- **Synthesis regenerates** from floats on drift
- **Intention drives flow**: alignment boosts/dampens energy
- Node + Link both have `synthesis` and `embedding` fields
- Complete formulas for: `compute_query_emotion`, `traverse`, `compute_flow`
- Cluster dynamics: tension, convergence, divergence detection

**v1.4.1 changes APPLIED:**
- Single `linked` type
- `polarity [a→b, b→a]` bidirectional flow
- `permanence` for energy vs weight solidification

**v1.3 changes APPLIED:**
- Plutchik 4 bipolar emotion axes
- Node energy roles (pump, router, accumulator, context, passthrough)

---

## FILES

| File | Purpose | Status |
|------|---------|--------|
| `docs/schema/schema.yaml` | Authoritative base schema | **v1.8.1** |
| `docs/schema/GRAMMAR_Link_Synthesis.md` | Synthesis generation grammar | **v2.0** |
| `mind/models/links.py` | Pydantic link models | **v1.3** |
| `mind/models/nodes.py` | Pydantic node models | **v1.7.1** |
| `mind/doctor_graph.py` | Doctor node types with type field | **v1.8.1** |
| `mind/physics/cluster_presentation.py` | Cluster presentation (uses type) | **v1.9.1** |
| `docs/schema/PATTERNS_Schema.md` | Design philosophy | CANONICAL |
| `docs/schema/SYNC_Schema.md` | This file | **v1.8.1** |

---

## HANDOFF: FOR AGENTS

**Current focus:**
1. Implement SubEntity class with v1.6.1 structure (origin_moment, siblings, children)
2. Implement link_score formula with self_novelty and sibling_divergence
3. Update crystallization_embedding at each step (not just at crystallization)
4. Implement forward/backward coloring in traverse/reflect
5. Implement crystallization with narrative creation + crystallized field

**Key context (v1.6.1):**
- Full spec: `docs/schema/schema.yaml`
- SubEntities track tree structure: origin_moment, siblings, children
- found_narratives stores (narrative_id, alignment) tuples
- crystallization_embedding updated EVERY step for sibling comparison
- Link score includes self_novelty and sibling_divergence factors
- Bidirectional vocabulary: same grammar for input and output

**Watch out for:**
- Sibling references must be maintained as SubEntities spawn
- crystallization_embedding recomputed after each traversal
- found_narratives alignment scores needed for weighted embedding
- Crystallization threshold: 0.85 cosine similarity
- self_novelty: avoid backtracking (compare to own path)
- sibling_divergence: avoid siblings' exploration space

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Schema v1.6.1 refines **SubEntity traversal** with sibling awareness and continuous crystallization tracking.

**Key v1.6.1 refinements over v1.6:**
- SubEntities now track tree structure (origin_moment, siblings, children)
- found_narratives stores alignment scores with each narrative
- crystallization_embedding computed at EACH step (enables sibling divergence)
- Link scoring includes self_novelty (avoid backtrack) + sibling_divergence (spread exploration)
- Bidirectional vocabulary — same grammar for agent input and synthesis output

**What this enables:**
- Siblings naturally spread out rather than exploring same paths
- Parent can see children's crystallization_embeddings to understand what each found
- Alignment scores in found_narratives enable weighted aggregation
- More efficient exploration of graph space

**Open questions (reduced from v1.6):**
1. Container redistribution (Space sinks)
2. Actor recharge rate
3. SubEntity lifespan limits

---

## ARCHIVE

Older content archived to: `SYNC_Schema_archive_2025-12.md`


---

## ARCHIVE

Older content archived to: `SYNC_Schema_archive_2025-12.md`
