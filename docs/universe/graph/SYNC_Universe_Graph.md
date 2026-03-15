# SYNC -- Universe Graph

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Force 1 (architect)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Graph.md
PATTERNS:        ./PATTERNS_Universe_Graph.md
BEHAVIORS:       ./BEHAVIORS_Universe_Graph.md
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
IMPLEMENTATION:  ./IMPLEMENTATION_Universe_Graph.md
THIS:            ./SYNC_Universe_Graph.md
```

---

## MATURITY

STATUS: DESIGNING

### What is canonical (decided)

- **Single graph per universe.** One FalkorDB graph holds all data for a universe (e.g., `venezia`). No separate L2 layer. This is confirmed.
- **5 universal node types.** Actor, Moment, Narrative, Space, Thing. No new types at L3. Schema v2.0 is the authority.
- **Space as universal context container.** Every "place where things happen" (channel, repo, world, brain, address) is a Space node. No parallel container types.
- **HAS_ACCESS link-based access.** Access is a graph link from Actor to Space, with role (owner/admin/member) and optionally an encrypted symmetric key. No ACL tables.
- **Hierarchical access.** Parent Space access implies child Space access via containment traversal.
- **Organizations as Narratives.** Orgs are Narrative nodes with associated hall Spaces. Members BELIEVE in the Narrative and have HAS_ACCESS to the hall.
- **Encrypted brains.** Brain Spaces live inside the universe graph with visible topology and AES-256 encrypted content. Per-Space symmetric key on HAS_ACCESS link.
- **L3 link dimensions.** Same LinkBase as L1 (trust, affinity, aversion, friction, polarity, hierarchy, permanence, etc.). No relation_kind. Plutchik axes frozen at 0.0.
- **L3 physics subset.** Laws L2, L3, L5, L6, L7, L10 apply. No limbic laws (L13-L18). No working memory (L4). No compatibility filtering (L8).
- **Macro-crystallization.** Law 10 at universe scale with higher thresholds (50+ nodes, density 0.15+). Creates hub Narratives. Law 7 prunes stale links.
- **Trust on links only.** No node-level trust. Reputation computed on demand from inbound link trust values.
- **space_type is free text.** No taxonomy. No algorithmic branching on space_type.
- **Key management split.** AI keys in `.keys/` dir. Human keys via wallet (Chrome ext / app). Same key for $MIND + Space decryption.

### What is being designed (open)

- **Graph isolation strategy.** See Open Questions below.
- **Migration path.** How to move from the current `mind_mcp` graph (single flat graph) to the universe model.
- **Brain Space implementation details.** Exact structure of brain sub-Spaces (self_model, partner_model, working_memory_space) within the universe graph.
- **Key rotation UX.** How key rotation after adversarial revocation is surfaced to remaining members.
- **L3 tick timing.** The universe graph needs its own tick rhythm for decay and crystallization, independent of L1 tick cycles. The Metabolic Economy (Force 2) defines a daily epoch at 00:00 UTC for demurrage, bond equilibrium, and UBC redistribution, plus 6-hour settlement epochs (00:00, 06:00, 12:00, 18:00 UTC). The L3 tick rhythm must be reconciled with this schedule -- e.g., how many L3 ticks per day, and does the crystallization check interval (500 ticks) align with the daily epoch?
- **Moment perception routing.** The exact mechanism by which L3 moments become L1 stimuli (Law 21 membrane).

### What is proposed (future)

- **Multi-universe federation.** A single FalkorDB instance hosting multiple universe namespaces. Actors can have HAS_ACCESS links across universes.
- **Universe-to-universe portals.** Spaces that bridge two universes (e.g., a "trade route" Space).
- **Historical compaction.** Beyond crystallization: aggressive pruning of ancient data into archival format.
- **Zero-knowledge proofs.** Proving membership or reputation without revealing identity.

---

## OPEN QUESTIONS

### Q1: Graph Isolation Strategy

**Question:** One FalkorDB instance with namespace per universe, or separate FalkorDB instances?

**Tradeoffs:**
- **Single instance, multiple namespaces:** Simpler ops (one process, one backup). But FalkorDB doesn't natively support namespaces -- would need separate named graphs within one instance. Performance isolation is weak.
- **Separate instances:** Stronger isolation. Each universe is independently scalable, deployable, backupable. But more operational overhead (N instances for N universes).
- **Proposed direction:** Start with separate named graphs within one FalkorDB instance (FalkorDB supports multiple named graphs via `GRAPH.QUERY graphname "..."`). If performance isolation becomes an issue, migrate to separate instances.

**Needs:** Performance benchmarks with 2-3 named graphs on a single FalkorDB instance. Measure cross-graph interference under load.

### Q2: Migration from mind_mcp Graph

**Question:** The current codebase uses a single flat graph called `mind_mcp` (set during `mind init`). How do we migrate to the universe model?

**Considerations:**
- Current graph has no Spaces, no HAS_ACCESS links, no encryption.
- Migration must be non-destructive (don't lose existing data).
- Proposed path:
  1. Create a default "root" Space in the existing graph.
  2. Link all existing nodes to the root Space.
  3. Create HAS_ACCESS link from the primary Actor to the root Space.
  4. Rename graph from `mind_mcp` to universe name.
  5. Gradually reorganize nodes into proper sub-Spaces.

**Needs:** Migration script. Validation that existing queries still work after Space introduction.

### Q3: Brains as Encrypted Private Spaces

**Question:** How exactly do L1 brains map onto the universe graph?

**Current thinking:**
- Each Actor has a "brain" Space (encrypted, HAS_ACCESS only to self).
- The brain Space contains sub-Spaces matching the L1 structural model: `self_model`, `partner_model`, `working_memory_space`.
- L1 cognitive types (memory, concept, narrative, value, process, desire, state) are nodes within these brain sub-Spaces, using the universal `type` field.
- L1 `relation_kind` values exist on links within the brain (encrypted, so L3 invariant INV-5 is not violated -- the L3-visible link has null relation_kind; the decrypted link has the cognitive relation_kind).

**Unresolved:**
- Does each brain sub-Space get its own encryption key, or do they all share the brain Space key?
  - Separate keys would allow sharing `partner_model` with the human partner without exposing `self_model`.
  - Single key is simpler.
- How does the L1 tick engine interact with the universe graph? Does it read-decrypt-process-encrypt-write on every tick, or maintain a decrypted in-memory copy?

### Q4: Topological Signals for Context Distinction

**Question:** Without space_type filtering, how do algorithms distinguish between a discord channel and a medieval tavern?

**Proposed topological signals:**
- **Bot presence:** A Space linked to a discord bot Actor is a discord channel. A Space linked to a VR engine Actor is a VR room.
- **Moment patterns:** Spaces with high-frequency short-text moments are likely chat channels. Spaces with low-frequency high-content moments are likely repos.
- **Actor density:** Spaces with many actors and shallow links are likely public forums. Spaces with few actors and deep links are likely private groups.
- **Containment structure:** Sub-Spaces of a "github" parent Space are repos. Sub-Spaces of a "discord_server" Space are channels.

**Needs:** Validate that these signals are sufficient for all current use cases. Identify any case where topology alone is ambiguous and space_type would be required.

---

## CURRENT STATE

### Code

- **Phases U1, U2, U4, U6 (partial) are implemented and tested.** 84 tests, all passing.
- **runtime/universe/** contains 6 files:
  - `__init__.py` -- Package exports (SpaceManager, AccessResolver, OrgManager, MomentPerceptionRouter, UniverseBootstrap)
  - `constants_l3_physics.py` -- L3 physics parameters (99 lines)
  - `space_and_hierarchy_manager.py` -- Space CRUD, containment hierarchy, moment placement (606 lines)
  - `access_resolution_and_link_manager.py` -- HAS_ACCESS resolution, grant/revoke, membership queries (455 lines)
  - `organization_lifecycle_manager.py` -- Org creation (Narrative + hall Space), membership, dissolution, reputation (310 lines)
  - `moment_perception_router.py` -- ALG-5 moment routing to accessing actors (140 lines)
  - `universe_bootstrap_and_metadata.py` -- Universe init, metadata node, flat graph migration (250 lines)
- **tests/universe/** contains 7 files:
  - `conftest.py` -- FakeAdapter (in-memory graph mock supporting Cypher patterns)
  - `test_space_crud_and_hierarchy.py` -- 18 tests (B1, INV-1, ALG-4, INV-9)
  - `test_access_resolution_and_inheritance.py` -- 19 tests (ALG-1, B2, B3, INV-2, INV-8)
  - `test_organization_lifecycle.py` -- 13 tests (ALG-7, ALG-8, B5, B6, dissolution)
  - `test_moment_perception_routing.py` -- 7 tests (ALG-5, B4)
  - `test_universe_bootstrap.py` -- 11 tests (INV-4, migration)
  - `test_integration_universe_lifecycle.py` -- 7 tests (full lifecycle, org membership, nested access, isolation)
- **Not yet implemented:**
  - U3: Encrypted brains (runtime/crypto/) -- AES-256-GCM, RSA-OAEP, key rotation
  - U5: L3 physics (runtime/physics/l3_*) -- energy propagation, consolidation, crystallization
  - U6 (MCP tools): space_manage and universe_admin MCP tool handlers
  - U6 (stimulus integration): inject_stimulus placeholder needs wiring to membrane when F5 is ready
- **Schema v2.0** (`docs/schema/schema.yaml`) already contains the full L3 section documenting the design.
- **Schema v1.9.1** (`mind-protocol/l4/schema/schema.yaml`) is the L4 canonical reference.
- **Physics engine** (`runtime/physics/`) implements the v1.x SubEntity model, not the 21-law model.

### Documentation

- **This doc chain** (6 files) captures the full design for the universe graph module.
- **Schema L3 section** in schema.yaml provides the authoritative type/link/law specifications.
- **L3 Link Synthesis Grammar** at `docs/schema/GRAMMAR_L3_Link_Synthesis.md` (referenced but may not exist yet).

### Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| FalkorDB multi-graph support | Available | Named graphs via `GRAPH.QUERY name "..."` |
| AES-256 encryption library | Available (Python `cryptography`) | For content encryption |
| RSA key management | Needs implementation | For per-actor key pairs |
| L1 physics engine (Force 5) | Not yet wired | Needed for brain Space tick execution |
| $MIND economy (Force 2) | Designed, not implemented | Key management shares wallet infrastructure |
| Trust mechanics (Force 4) | Designed, not implemented | Trust on links feeds reputation computation |

---

## HANDOFF

**For next agent (groundwork):**

Phases U1, U2, U4, and U6 (moment perception routing) are implemented with 84 passing tests. Remaining work:

1. **U3: Encrypted brains** -- `runtime/crypto/` with AES-256-GCM, RSA-OAEP, key rotation. This is the next priority for brain Space isolation.
2. **U5: L3 physics** -- `runtime/physics/l3_*.py` with energy propagation, consolidation, macro-crystallization. Depends on F5 tick engine.
3. **U6 (MCP tools)** -- `mcp/tools/space_management_handler.py` and `mcp/tools/universe_admin_handler.py`. Wire SpaceManager/AccessResolver to MCP tool registry in `home_server.py`.
4. **U6 (stimulus wiring)** -- `MomentPerceptionRouter.inject_stimulus()` is a placeholder. Wire to `runtime/membrane/stimulus.py` when F5 cognitive engine is ready.

**Key architecture patterns established:**
- Service layer: SpaceManager, AccessResolver, OrgManager, MomentPerceptionRouter, UniverseBootstrap all depend on DatabaseAdapter
- FakeAdapter in tests/universe/conftest.py supports the Cypher patterns used in production code
- All access control via HAS_ACCESS links (INV-2), no property-based ACL
- Hierarchical access inheritance with role downgrade (ALG-1)
- Organizations are Narrative + hall Space (ALG-7)
- Reputation computed on demand from inbound link trust (ALG-8)

**Agent subtype for next work:** groundwork (act, ship, iterate).

**Start with:** Phase U3 (crypto layer) if brain encryption is the priority, or Phase U6 (MCP tools) if agent-facing tools are needed first.

---

## RECENT CHANGES

### 2026-03-14: Phases U1, U2, U4, U6-routing Implementation (Force 1, groundwork)

- Implemented `runtime/universe/__init__.py` with package exports.
- Implemented `runtime/universe/universe_bootstrap_and_metadata.py`: UniverseBootstrap with initialize(), validate_metadata(), migrate_flat_graph(), get_root_space_id().
- Implemented `runtime/universe/organization_lifecycle_manager.py`: OrgManager with create_organization(), join_organization(), compute_org_reputation(), check_dissolution().
- Implemented `runtime/universe/moment_perception_router.py`: MomentPerceptionRouter with route(), inject_stimulus(), route_and_inject().
- Created `tests/universe/conftest.py` with FakeAdapter (in-memory graph mock supporting Cypher patterns used by universe module).
- Created 6 test files with 84 tests total, all passing:
  - test_space_crud_and_hierarchy.py (18 tests)
  - test_access_resolution_and_inheritance.py (19 tests)
  - test_organization_lifecycle.py (13 tests)
  - test_moment_perception_routing.py (7 tests)
  - test_universe_bootstrap.py (11 tests)
  - test_integration_universe_lifecycle.py (7 tests)
- Refactored universe_bootstrap_and_metadata.py migrate_flat_graph() to use Python-side orphan filtering instead of complex NOT-pattern Cypher (more portable across graph backends).

### 2026-03-14: Phase C Implementation Plan (Force 1, architect)

- Created IMPLEMENTATION_Universe_Graph.md with full Phase C plan.
- Defined 6 implementation phases (U1-U6), each independently testable.
- Specified 15 new files across `runtime/universe/`, `runtime/crypto/`, `runtime/physics/`, `mcp/tools/`, `tests/universe/`.
- Documented all function signatures and class interfaces.
- Mapped shared interfaces: what F2/F4/F5 need from F1, and what F1 needs from them.
- Identified 6 risks (FalkorDB community detection, encryption at scale, cross-force timing, migration, L3 tick timing, hierarchy depth).
- L3 tick timing proposal: 1 minute/tick, crystallization every 500 ticks (~8.3 hours).
- Updated CHAIN block to include IMPLEMENTATION link.

### 2026-03-14: Phase B Cross-Review Complete

- Cross-review with F2 found 7 issues, all fixed. See `docs/reviews/REVIEW_F1_F2_Coherence.md`.
- Key fixes: F2 cross-references to F1 Space model, MAPPING.md corrected (org = narrative, not actor), L6 consolidation at L3 documented for structural_utility.

### 2026-03-13: Initial Documentation (Force 1, Phase A)

- Created 6-file doc chain for Universe Graph module under `docs/universe/`.
- Captured all canonical decisions from MASTER TODO Force 1 (tasks 1.1 through 1.11).
- Documented 8 algorithms (HAS_ACCESS resolution, encryption key distribution, macro-crystallization, Space hierarchy traversal, moment perception routing, L3 energy model, organization lifecycle, reputation computation).
- Documented 12 structural invariants with verification pseudocode.
- Documented 12 observable behaviors and 6 anti-behaviors.
- Identified 4 open questions requiring further design work or benchmarking.
