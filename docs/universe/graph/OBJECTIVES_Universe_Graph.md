# OBJECTIVES -- Universe Graph

```
STATUS: DESIGNING
CREATED: 2026-03-13
UPDATED_BY: Force 1 (architect)
```

---

## CHAIN

```
THIS:            ./OBJECTIVES_Universe_Graph.md
PATTERNS:        ./PATTERNS_Universe_Graph.md
BEHAVIORS:       ./BEHAVIORS_Universe_Graph.md
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md
```

---

## PRIMARY OBJECTIVES (ranked)

1. **O1: Single source of truth per universe** -- One graph holds all Spaces, Actors, Moments, Narratives, and Things for a given universe. No separate L2 layer, no per-organization graphs, no per-channel databases. The universe graph IS the universe. Everything that happens in `venezia` lives in the `venezia` graph. This eliminates cross-graph joins, data duplication, and split-brain problems that plagued the 4-layer model.

2. **O2: Link-based access control** -- Access is a relationship, not a property. An Actor can see and act within a Space if and only if a `HAS_ACCESS` link exists from that Actor to that Space (or to an ancestor Space in the hierarchy). Roles (owner, admin, member) are properties on the link, not on the Actor. This makes access auditable, revocable, and graph-native -- no ACL tables, no permission matrices, no external auth systems.

3. **O3: Encrypted content with visible topology** -- Brain Spaces (an Actor's private cognitive graph) live inside the universe graph but their node content and link synthesis are AES-256 encrypted at rest. Topology -- which nodes exist, which links connect them, node types, physics floats -- remains visible. This enables physics (propagation, decay, crystallization) to operate on the full graph while keeping private thoughts private. The encryption key is a per-Space symmetric key, stored encrypted with each authorized Actor's public key on the `HAS_ACCESS` link.

4. **O4: Physics continuity across layers** -- The same 5 node types, the same LinkBase dimensions (weight, energy, stability, recency, polarity, hierarchy, permanence, valence, ambivalence, trust, friction, affinity, aversion), and the same physics laws (L2, L3, L5, L6, L7, L10) operate at universe scale. L1 (brain) and L3 (universe) are not separate systems with separate schemas -- they are the same schema operating at different scopes. L1 adds cognitive extensions (relation_kind, drives, working memory). L3 strips them off.

5. **O5: Scalability without taxonomy** -- No `space_type` enum. No `relation_kind` at L3. No filtering on labels. The universe graph must scale to millions of nodes and links without relying on categorical indexes that become maintenance burdens. Topology -- the shape of the graph itself -- determines context. A discord channel and a medieval tavern are both Spaces; the difference is in their links, not their labels.

6. **O6: Macro-crystallization for self-management** -- The universe graph manages its own growth via Law 10 (crystallization) at universe scale and Law 7 (forgetting) for link pruning. 300 commits crystallize into 1 project-phase narrative. Stale links dissolve. The graph never grows without bound.

## NON-OBJECTIVES

- **Creating a new schema for L3.** L3 uses the existing universal schema (5 types, LinkBase). No new node types. No new link types.
- **Building a permission system outside the graph.** If access requires external lookup (RBAC tables, IAM policies), the architecture has failed.
- **Full homomorphic encryption.** Only content and synthesis are encrypted. Physics floats, node types, and topology remain in plaintext for graph operations.
- **Replacing L1 brains.** Brains remain the cognitive substrate. The universe graph is the structural substrate. They share schema, not identity.
- **Eliminating all categorization.** Free-form `type` fields and `space_type` hints are allowed. The constraint is that no algorithm, formula, or physics law may branch on these values.

## TRADEOFFS (canonical decisions)

- **One graph over many graphs:** A single universe graph means larger graph size but eliminates cross-graph queries, data synchronization, and the entire L2 coordination layer. The complexity moves from inter-graph coordination to intra-graph access control (HAS_ACCESS links), which is simpler.
- **Topology visible over fully encrypted:** Exposing topology means an observer can see that Actor A has 500 links while Actor B has 50. This leaks structural information. We accept this because physics must operate on topology -- encrypted topology would require homomorphic computation that doesn't exist at scale.
- **No taxonomy over taxonomized Spaces:** Without `space_type` filters, queries that want "all discord channels" must use topological signals (e.g., Spaces linked to a discord bot Actor). This is harder to query but prevents taxonomy rot and enforcement costs.
- **Same physics laws over L3-specific laws:** Using the same laws at L3 means some parameters need re-tuning (crystallization threshold = 300 at L3 vs 50-250 at L1). We prefer this over designing new laws because one physics engine serves both layers.
- **Symmetric encryption per Space over per-node encryption:** Per-Space keys mean all nodes within a Space share one key. An Actor with access to a Space can read all its nodes. This is coarser than per-node encryption but dramatically simpler for key management.

## SUCCESS SIGNALS (observable)

- All data for a universe lives in exactly one FalkorDB graph (or namespace). No join queries across graphs.
- Removing an Actor's `HAS_ACCESS` link to a Space immediately revokes read and write access. No cache invalidation, no eventual consistency.
- Physics (decay, crystallization, propagation) runs across the entire universe graph without needing to decrypt content.
- Brain content is unreadable without the per-Space symmetric key, even with full database access.
- The universe graph prunes itself: total link count stabilizes despite continuous moment creation, because Law 7 dissolves stale links and Law 10 compresses dense clusters.
- Organizations function as Narrative nodes with associated hall Spaces -- no special "organization" type, no organization-specific code paths.
