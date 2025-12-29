# ARCHITECTURE — Cybernetic Studio — Implementation: Code Structure

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Cybernetic_Studio_Architecture.md
BEHAVIORS:      ./BEHAVIORS_Cybernetic_Studio_System_Behaviors.md
ALGORITHM:      ./ALGORITHM_Cybernetic_Studio_Process_Flow.md
VALIDATION:     ./VALIDATION_Cybernetic_Studio_Architectural_Invariants.md
THIS:           IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
HEALTH:         ./HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:           ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:           N/A (Conceptual Architecture Document)
SOURCE:         ../../../data/ARCHITECTURE — Cybernetic Studio.md
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

This architecture spans two repos plus an external graph service. The structure below is conceptual and names the current repo boundaries, not exhaustive file listings.

```
mind/                      # Studio Platform (graph physics, ingestion, orchestration)
├── mind/                  # CLI, orchestration, health/validation tooling
├── docs/                   # Protocol + module docs
└── data/                   # Architecture sources (conceptual)

blood-ledger/               # Game Cartridge (world content + player experience)
├── mind/                 # Runtime orchestration, physics integration
├── frontend/               # Player UI
├── data/                   # Seeds, narratives, world content
└── docs/                   # Cartridge design + system docs

(graph service)             # External graph physics and storage
```

### File Responsibilities (Conceptual)

| Area | Purpose | Key Artifacts | Status |
|------|---------|---------------|--------|
| `mind` | Graph physics + stimuli ingestion + Places + agent orchestration | `runtime/`, `docs/` | DESIGNING |
| `blood-ledger` | Game content + UI + cartridge orchestration | `runtime/`, `frontend/`, `data/` | DESIGNING |
| graph service | Graph storage + traversal + pressure computation (owned by `mind`) | external service | DESIGNING |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Dual-repo architecture with shared physics service

**Why this pattern:** Keeps the Studio Platform stable and reusable while the Game Cartridge iterates on content and player experience. The graph service is a shared physics layer, not an artifact store.

### Anti-Patterns to Avoid

- **Graph-as-filesystem:** Never store file content in the graph.
- **Overmind daemon:** Avoid privileged always-on controllers; use stimuli + physics.
- **Magic constants:** Use adaptive gates for thresholds.

---

## BOUNDARIES

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Repo artifacts | Code, tests, assets, SYNC docs | Graph state | EvidenceRef (repo/path/sha) |
| Graph physics | Weight, energy, pressure, salience | Repo content | Graph ops API |
| Places | SYNC/UI/VIEW context surfaces | Raw files | Place registry + surfaces |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `mind` CLI | `runtime/` | Dev workflows (validation, sync, repair) |
| `blood-ledger` runtime | run script (external) | Game orchestration in dev |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Stimulus Ingestion → Graph Tick

```yaml
flow:
  name: stimulus_ingestion_and_tick
  purpose: Convert repo/system events into graph energy, then surface candidates.
  scope: Repo events, EvidenceRefs, graph ops
  steps:
    - id: capture_l1
      description: Capture L1 stimuli from repo events
      file: mind (watchers, future)
      function: watcher hooks (planned)
      input: repo events
      output: L1 stimulus
      trigger: file read/write/commit/exec
      side_effects: stimulus creation
    - id: derive_l2
      description: Derive intent/incident stimuli
      file: mind (stimulus derivation, planned)
      function: derive_stimuli
      input: L1 stimulus
      output: L2 stimulus
      trigger: L1 capture
      side_effects: none
    - id: inject_energy
      description: Inject energy into graph nodes/links/places
      file: graph service
      function: graph_ops.inject
      input: L2 stimulus + EvidenceRefs
      output: updated graph state
      trigger: L2 derivation
      side_effects: weight/energy updates
    - id: tick
      description: Route, compute pressure, decay, surface, flip
      file: graph service
      function: physics_tick
      input: graph state
      output: surfaced candidates + canonized moments
      trigger: scheduled tick or stimulus
      side_effects: THEN chains, narratives
  docking_points:
    guidance:
      include_when: significant, cross-boundary, or risky
      omit_when: trivial pass-through
      selection_notes: Focus on boundaries between repo and graph.
    available:
      - id: dock_repo_event
        type: file
        direction: input
        file: repo watchers (planned)
        function: watcher hook
        trigger: file_read/write/commit/exec
        payload: event metadata + EvidenceRef
        async_hook: optional
        needs: add watcher
        notes: boundary from repo to graph
      - id: dock_graph_inject
        type: graph_ops
        direction: output
        file: graph service
        function: inject
        trigger: stimulus ingestion
        payload: EvidenceRefs + energy
        async_hook: not_applicable
        needs: none
        notes: core physics entry
    health_recommended:
      - dock_id: dock_repo_event
        reason: validates stimulus coverage (VALIDATION V3)
      - dock_id: dock_graph_inject
        reason: validates graph-only meaning storage (VALIDATION V1)
```

### Place Updates via SYNC

```yaml
flow:
  name: sync_place_updates
  purpose: Treat SYNC files as Places and generate Moments on updates.
  scope: SYNC edits, Place registry, Moments
  steps:
    - id: sync_edit
      description: Edit SYNC file in repo
      file: ...mind/state/SYNC_*.md
      function: manual edit
      input: markdown update
      output: updated file
      trigger: user/agent edit
      side_effects: repo change
    - id: place_moment
      description: Emit Moment attached to Place
      file: graph service (planned)
      function: attach_to_place
      input: sync diff + EvidenceRef
      output: new Moment
      trigger: sync_edit
      side_effects: moment graph updates
  docking_points:
    guidance:
      include_when: user-visible state or canonicalization
      omit_when: doc-only edits with no runtime integration
      selection_notes: SYNC is the canonical human handoff surface.
    available:
      - id: dock_sync_edit
        type: file
        direction: input
        file: ...mind/state/SYNC_Project_State.md
        function: manual edit
        trigger: edit
        payload: markdown diff
        async_hook: optional
        needs: watcher
        notes: Place boundary
      - id: dock_place_attach
        type: graph_ops
        direction: output
        file: graph service
        function: attach_to_place
        trigger: sync_edit
        payload: EvidenceRef + moment
        async_hook: not_applicable
        needs: none
        notes: Place moment creation
    health_recommended:
      - dock_id: dock_sync_edit
        reason: validates Place-first behavior (VALIDATION V5)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind → graph service
blood-ledger → mind
blood-ledger → graph service
```

### External Dependencies

| Package/Service | Used For | Imported By |
|-----------------|----------|-------------|
| graph service (owned by `mind`) | storage + physics | `mind`, `blood-ledger` |

---

## BIDIRECTIONAL LINKS

### Code → Docs

No direct code references yet (conceptual architecture).

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| Stimulus ingestion flow | planned watchers + graph ops |
| SYNC as Place flow | planned SYNC watcher + graph attach |

---

## MARKERS

<!-- @mind:todo Specify exact watcher locations in `mind` once stimulus ingestion code lands. -->
<!-- @mind:todo Confirm graph ops API boundaries and versioning strategy. -->
<!-- @mind:escalation Where should Place registry live: `mind` or the graph service? -->
