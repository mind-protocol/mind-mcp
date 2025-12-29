# Schema — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2025-12-23
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Schema.md
BEHAVIORS:      ./BEHAVIORS_Schema.md
PATTERNS:       ./PATTERNS_Schema.md
ALGORITHM:      ./ALGORITHM_Schema.md
VALIDATION:     ./VALIDATION_Schema.md
THIS:           IMPLEMENTATION_Schema.md (you are here)
HEALTH:         ./HEALTH_Schema.md
SYNC:           ./SYNC_Schema.md

IMPL:           docs/schema/schema.yaml
                mind/graph/health/check_health.py
                mind/graph/health/test_schema.py
                mind/graph/health/schema.yaml
                mind/models/base.py
                mind/models/nodes.py
                mind/models/links.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
docs/schema/
├── schema.yaml                 # Authoritative base schema (project-agnostic)
├── PATTERNS_Schema.md          # Design philosophy
├── OBJECTIVES_Schema.md         # Goals and tradeoffs
├── BEHAVIORS_Schema.md         # Observable effects
├── ALGORITHM_Schema.md         # Validation procedures
├── VALIDATION_Schema.md        # Invariants
├── IMPLEMENTATION_Schema.md    # This file
├── HEALTH_Schema.md            # Health checks
└── SYNC_Schema.md              # Current state

mind/graph/health/
├── check_health.py             # CLI health checker
├── test_schema.py              # Pytest validation suite
└── schema.yaml                 # Blood Ledger project schema overlay

mind/models/
├── base.py                     # Enums, shared types (game-specific)
├── nodes.py                    # Pydantic node models (game-specific)
└── links.py                    # Pydantic link models (game-specific)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `docs/schema/schema.yaml` | Authoritative base schema | NodeBase, LinkBase, nodes, links, invariants | ~240 | OK |
| `runtime/graph/health/check_health.py` | CLI health check | `check_graph_health()`, `validate_node()`, `HealthReport` | ~430 | WATCH |
| `runtime/graph/health/test_schema.py` | Pytest suite | `SchemaValidator`, 20+ test methods | ~880 | SPLIT |
| `runtime/graph/health/schema.yaml` | Blood Ledger overlay | Character, Place, Thing, Narrative enums | ~320 | OK |
| `runtime/models/base.py` | Pydantic enums | `CharacterType`, `PlaceType`, `ThingType`, etc. | ~460 | WATCH |
| `runtime/models/nodes.py` | Pydantic nodes | `Character`, `Place`, `Thing`, `Narrative`, `Moment` | ~320 | OK |
| `runtime/models/links.py` | Pydantic links | `CharacterNarrative`, `PlacePlace`, etc. | ~225 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size
- **WATCH** (400-700 lines): Getting large
- **SPLIT** (>700 lines): Must split before adding

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Layered Schema with Overlay

**Why this pattern:** Base schema provides project-agnostic structure. Project schemas overlay constraints. Separation enables reuse across mind/Blood Ledger.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Dataclass | `Issue`, `HealthReport` in check_health.py | Clean data containers |
| Strategy | Schema overlay loading | Project-specific validation rules |
| Builder | `HealthReport.add_issue()` | Accumulate issues during validation |

### Anti-Patterns to Avoid

- **Hardcoded enums in base schema**: Don't add game-specific values to docs/schema/schema.yaml
- **LLM in validation**: Never invoke LLM during health checks
- **Mutation during query**: All validation is read-only

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Base schema | 5 node_types, link types, invariants | Game-specific enums | `schema.yaml` |
| Project schema | Blood Ledger enums | Base structure | Overlay merge |
| Pydantic models | Game classes | Graph validation | Separate concern |

---

## SCHEMA

### NodeBase (from schema.yaml)

```yaml
NodeBase:
  required:
    - id: string
    - name: string
    - node_type: enum [actor, space, thing, narrative, moment]
    - type: string
  optional:
    - description: string
    - weight: float [0,1]
    - energy: float [0,1]
    - created_at_s: int
    - updated_at_s: int
```

### LinkBase (from schema.yaml)

```yaml
LinkBase:
  required:
    - id: string
    - from_id: string
    - to_id: string
    - type: enum [at, contains, leads_to, relates, primes, then, said, can_lead_to, attached_to, about]
  optional:
    - strength: float [0,1]
    - polarity: float [-1,1]
    - weight: float [0,1]
    - energy: float [0,1]
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| CLI health check | `check_health.py:381` (`main()`) | `python check_health.py` |
| Pytest runner | `test_schema.py:865` (`main()`) | `pytest test_schema.py` |
| mind init | — | Copies schema.yaml to .mind/ |

---

## DATA FLOW AND DOCKING

### Flow 1: Schema Loading

```yaml
flow:
  name: schema_loading
  purpose: Merge base + project schemas for validation
  steps:
    - id: load_base
      description: Load docs/schema/schema.yaml
      file: mind/graph/health/check_health.py
      function: load_schema()
      input: BASE_SCHEMA_PATH
      output: base dict
    - id: load_project
      description: Load mind/graph/health/schema.yaml
      file: mind/graph/health/check_health.py
      function: load_schema()
      input: PROJECT_SCHEMA_PATH
      output: project dict
    - id: merge
      description: Deep merge, project wins
      function: load_schema()
      output: merged schema dict
  docking_points:
    available:
      - id: dock_base_loaded
        type: file
        direction: input
        file: docs/schema/schema.yaml
      - id: dock_project_loaded
        type: file
        direction: input
        file: mind/graph/health/schema.yaml
      - id: dock_merged_schema
        type: custom
        direction: output
        payload: dict
    health_recommended:
      - dock_id: dock_merged_schema
        reason: Verify merge produces valid combined schema
```

### Flow 2: Graph Validation

```yaml
flow:
  name: graph_validation
  purpose: Check all nodes/links against schema
  steps:
    - id: connect
      description: Connect to FalkorDB
      file: mind/graph/health/check_health.py
      function: main()
      input: host, port, graph_name
    - id: query_nodes
      description: Query all nodes by type
      function: check_graph_health()
      input: GraphOps instance
    - id: validate
      description: Check each node against schema
      function: validate_node()
      input: node dict, node_type, schema
      output: issues added to report
    - id: report
      description: Generate HealthReport
      output: HealthReport
  docking_points:
    available:
      - id: dock_graph_connection
        type: db
        direction: input
      - id: dock_node_query
        type: graph_ops
        direction: input
      - id: dock_validation_result
        type: custom
        direction: output
        payload: HealthReport
    health_recommended:
      - dock_id: dock_validation_result
        reason: Primary health signal for schema compliance
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
docs/schema/schema.yaml (authoritative)
    └── loaded by → mind/graph/health/check_health.py
    └── loaded by → mind/graph/health/test_schema.py
    └── copied to → .mind/schema.yaml (at init)

mind/graph/health/schema.yaml (Blood Ledger)
    └── overlays → base schema at load time
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `pyyaml` | Schema parsing | check_health.py, test_schema.py |
| `pydantic` | Model validation | mind/models/*.py |
| `falkordb` | Graph queries | check_health.py, test_schema.py |
| `pytest` | Test framework | test_schema.py |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Merged schema | `load_schema()` return | Function call | Per invocation |
| HealthReport | `check_graph_health()` return | Function call | Per invocation |
| Graph connection | `GraphOps` instance | Script execution | Per run |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `check_health.py` | 8 | `# DOCS: docs/schema/graph-health/...` (obsolete path) |
| `nodes.py` | 8 | `# DOCS: docs/schema/` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM load_schema | `check_health.py:146` |
| ALGORITHM validate_node | `check_health.py:197` |
| VALIDATION V1 | `test_schema.py::test_*_link_structure` |
| VALIDATION V6 | `test_schema.py::test_*_required_fields` |

---

## EXTRACTION CANDIDATES

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `test_schema.py` | ~880L | <400L | `test_schema_nodes.py`, `test_schema_links.py` | Split node tests from link tests |
| `base.py` | ~460L | <400L | — | OK for now, mostly enums |

---

## MARKERS

<!-- @mind:resolved PYDANTIC_VS_SCHEMA: RESOLVED 2025-12-23 — Pydantic models now use generic schema types (Actor, Space, Thing). Character→Actor, Place→Space migration complete. No game-specific models. -->

<!-- @mind:todo DOCS_REFERENCE_UPDATE: check_health.py:8 references obsolete docs path "docs/schema/graph-health/...". Update to current location. -->

<!-- @mind:todo SPLIT_TEST_SCHEMA: test_schema.py at 880 lines exceeds SPLIT threshold. Should extract node tests and link tests into separate files. -->

<!-- @mind:proposition SCHEMA_TYPING: Add Python type stubs for schema.yaml structure so IDE can provide completion when accessing loaded schema dict. -->
