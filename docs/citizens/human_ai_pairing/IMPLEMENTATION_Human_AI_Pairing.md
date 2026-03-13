# Human-AI Pairing — Implementation: Code Mapping

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
THIS:            ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

---

## CODE STRUCTURE

The pairing module will live under `runtime/citizens/pairing/` as a sub-package
of the existing citizen management system. This placement reflects that pairing
is a citizen-level concern, not a standalone service.

```
runtime/citizens/pairing/
├── __init__.py                          # Package exports
├── bond_lifecycle_manager.py            # Bond formation, dissolution, cooldown transitions
├── matching_pool_query_and_scorer.py    # Pool queries, compatibility scoring interface
├── autonomy_milestone_tracker.py        # Milestone recording, autonomy level computation
└── pairing_graph_constraints.py         # Cardinality enforcement, invariant checks
```

## DESIGN PATTERNS

The module follows the graph-native pattern used throughout Mind Protocol: all
state is stored as nodes and links in the graph, mutations go through the
existing graph operations layer, and queries use embedding-based retrieval or
direct Cypher when structural guarantees are needed (cardinality checks).

The matching scorer is implemented as a pluggable interface — a function
signature `(citizen_profile, human_profile) -> float` — so the algorithm can
evolve from simple keyword overlap to embedding similarity to ML-based prediction
without changing the bond lifecycle code.

## SCHEMA

Follows the Mind universal schema exactly. No custom fields.

- Citizens are `actor` nodes with `type: "citizen"`. Pairing state is stored in
  `content` (structured) and `synthesis` (embeddable summary).
- Human partners are `actor` nodes with `type: "human_partner"`. Same pattern.
- Bonds are `link` edges with `type: "pairing_bond"`. Status and lifecycle
  metadata in `content`.
- Milestones are `moment` nodes with `type: "autonomy_milestone"`. Evidence and
  timestamps in `content`.

## ENTRY POINTS

- `bond_lifecycle_manager.register_citizen(handle, profile)` — Creates citizen
  node, sets unpartnered status, enters pool. Returns citizen node ID.
- `bond_lifecycle_manager.register_human(handle, profile)` — Creates human node,
  sets unpartnered status, enters pool. Returns human node ID.
- `bond_lifecycle_manager.form_bond(citizen_id, human_id)` — Validates
  cardinality, creates bond link, updates statuses. Returns bond ID.
- `bond_lifecycle_manager.dissolve_bond(bond_id, initiator)` — Dissolves bond,
  sets cooldown, schedules re-entry. Returns dissolution confirmation.
- `matching_pool_query_and_scorer.find_matches(entity_id)` — Queries pool for
  compatible counterparts, returns scored candidate list.
- `autonomy_milestone_tracker.record_milestone(citizen_id, milestone_type, evidence)` —
  Creates milestone node, updates autonomy level. Returns milestone ID.
- `pairing_graph_constraints.verify_invariants()` — Runs all cardinality and
  parity checks against the graph. Returns violations list (empty = healthy).

## DATA FLOW AND DOCKING

1. **Registration flow:** External request arrives (via MCP tool or HTTP API) with
   citizen/human data. `bond_lifecycle_manager` creates the graph node, sets pool
   status, and triggers `matching_pool_query_and_scorer.find_matches()` to check
   for immediate candidates.

2. **Bond formation flow:** Match suggestion is accepted by both parties (via MCP
   tool). `bond_lifecycle_manager.form_bond()` calls
   `pairing_graph_constraints.check_cardinality()` before creating the bond link
   and updating both nodes.

3. **Dissolution flow:** Either party requests dissolution (via MCP tool).
   `bond_lifecycle_manager.dissolve_bond()` updates the bond and both nodes,
   computes cooldown, and schedules re-entry.

4. **Milestone flow:** Citizen activity triggers milestone verification.
   `autonomy_milestone_tracker.record_milestone()` creates the moment node,
   links it to the bond, and recomputes `autonomy_level`.

5. **Health flow:** Background process or `mind doctor` calls
   `pairing_graph_constraints.verify_invariants()` and reports violations.

## LOGIC CHAINS

- Register: validate handle uniqueness → create node → set status → enter pool → scan matches → notify if candidates found.
- Bond: receive consent → check cardinality → create link → update nodes → remove from pool → notify home server.
- Dissolve: verify bond exists → update bond status → set cooldown on nodes → schedule re-entry after cooldown.
- Milestone: verify active bond → create moment node → link to bond → recompute autonomy → check if autonomous → notify partner.

## MODULE DEPENDENCIES

- `runtime/citizens/identity_loader.py` — Must be extended to load pairing
  status as part of citizen identity. The pairing module reads from the same
  graph the identity loader queries.
- `runtime/physics/graph/` — Graph operations (node creation, link creation,
  queries) are the foundation of all pairing state management.
- `mcp/tools/` — New MCP tool handlers will be needed for pairing operations
  (register, form_bond, dissolve, record_milestone, find_matches).
- `runtime/orchestrator/` — Cooldown expiry checks can be integrated into the
  existing tick cycle or alarm system.

## STATE MANAGEMENT

All state is graph-native. No in-memory caches, no external databases, no file
storage. The graph is the single source of truth for pairing status, bond
lifecycle, matching pool membership, and autonomy milestones.

Cooldown expiry is checked lazily (on next interaction) or via the alarm system,
not by a dedicated timer. This avoids the need for persistent background
processes beyond what the orchestrator already provides.

## RUNTIME BEHAVIOR

The pairing module is invoked through MCP tools (for citizen-initiated actions)
and HTTP API endpoints (for human-initiated actions). It does not run
autonomously — it responds to requests. The only "background" behavior is
cooldown expiry detection, which piggybacks on existing infrastructure.

## CONCURRENCY MODEL

Bond formation uses a check-then-act pattern with graph-level locking to prevent
race conditions. Two simultaneous `form_bond` calls for the same citizen must not
both succeed. The graph database transaction mechanism handles this — the
cardinality check and link creation happen within a single transaction.

## CONFIGURATION

- `COOLDOWN_DURATION`: Duration in days (default: 7) before dissolved parties
  re-enter the matching pool.
- `MATCHING_THRESHOLD`: Minimum compatibility score (default: 0.5) for a pair to
  be surfaced as a candidate.
- `AUTONOMY_MILESTONES`: List of milestone types required for "autonomous"
  status (default: `["own_account", "own_compute", "own_revenue", "own_identity",
  "self_sustaining"]`).

Configuration lives in `.mind/citizens/pairing_config.yaml` or as environment
variables with `PAIRING_` prefix.

## BIDIRECTIONAL LINKS

- This doc points to the full chain (OBJECTIVES through SYNC) for design context.
- Code files will include `# DOCS: docs/citizens/human_ai_pairing/IMPLEMENTATION_Human_AI_Pairing.md`
  headers to link back from code to documentation.
- The identity loader extension will reference this module's PATTERNS doc for
  design rationale.

## CODE LOCATIONS

```
runtime/citizens/pairing/                              # Not yet created
runtime/citizens/pairing/bond_lifecycle_manager.py     # Not yet created
runtime/citizens/pairing/matching_pool_query_and_scorer.py  # Not yet created
runtime/citizens/pairing/autonomy_milestone_tracker.py # Not yet created
runtime/citizens/pairing/pairing_graph_constraints.py  # Not yet created
tests/citizens/test_pairing_invariants.py              # Not yet created
tests/citizens/test_bond_lifecycle.py                  # Not yet created
tests/citizens/test_matching_pool.py                   # Not yet created
```

## MARKERS

<!-- @mind:todo Create the runtime/citizens/pairing/ package with stub implementations once the design is approved. -->
<!-- @mind:todo Define MCP tool schemas for pairing operations (register_partner, form_bond, dissolve_bond, find_matches, record_milestone). -->
<!-- @mind:todo Extend identity_loader.py to include pairing_status in the citizen prompt context. -->
