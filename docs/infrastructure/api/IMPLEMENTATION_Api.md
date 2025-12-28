# API — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2024-12-18
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Api.md
BEHAVIORS:       ./BEHAVIORS_Api.md
ALGORITHM:       ./ALGORITHM_Api.md
VALIDATION:      ./VALIDATION_Api.md
THIS:            IMPLEMENTATION_Api.md
HEALTH:          ./HEALTH_Api.md
SYNC:            ./SYNC_Api.md

IMPL:            Pending import from external repo (PROPOSED)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind/infrastructure/api/
├── __init__.py         # Package export surface
├── app.py              # FastAPI app factory + legacy endpoints
├── moments.py          # Moment graph router + SSE stream
├── playthroughs.py     # Playthrough creation + moment ingestion
├── tempo.py            # Tempo controller endpoints
└── sse_broadcast.py    # Shared SSE client registry and broadcast
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `mind/infrastructure/api/app` | App factory, core endpoints, debug SSE | `create_app`, `player_action` | ~735 | SPLIT |
| `mind/infrastructure/api/moments` | Moment graph endpoints + SSE stream | `create_moments_router` | ~489 | WATCH |
| `mind/infrastructure/api/playthroughs` | Playthrough creation | `create_playthrough` | ~579 | WATCH |
| `mind/infrastructure/api/tempo` | Tempo endpoints | `create_tempo_router` | ~234 | OK |
| `mind/infrastructure/api/sse_broadcast` | Shared SSE fan-out registry | `register_sse_client` | ~81 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** App-factory + router-factory FastAPI layout with event fan-out for SSE.

**Why this pattern:** Centralized setup keeps shared dependencies consistent, while router factories isolate endpoint groups and keep hot-path code obvious.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Factory | `app.py:create_app` | Single entry for wiring routers + shared helpers. |
| Observer/Fan-out | `sse_broadcast` | Broadcast click/moment events to SSE clients. |
| Cache | per-playthrough maps | Reuse GraphQueries + orchestrators per playthrough. |

### Anti-Patterns to Avoid

- **God Router**: avoid adding new API endpoints directly into `app`.
- **Hidden Globals**: keep caches explicit and scoped to modules.

---

## SCHEMA

### ActionRequest

```yaml
ActionRequest:
  required:
    - playthrough_id: str
    - action: str
  optional:
    - player_id: str            # default "char_player"
    - location: str | null
    - stream: bool              # return SSE when true
```

### PlaythroughCreateRequest

```yaml
PlaythroughCreateRequest:
  required:
    - scenario_id: str
    - player_name: str
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `create_app()` | `mind/infrastructure/api/app:110` | Import-time wiring or tests |
| `app = create_app()` | `mind/infrastructure/api/app:731` | Uvicorn import path |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Action Loop: Player Action → Orchestrator

This flow handles the primary gameplay interaction loop where a player's intent is processed by the narrator and physics engine.

```yaml
flow:
  name: action_loop
  purpose: Process player actions through the simulation.
  scope: HTTP Request -> Orchestrator -> Result Response
  steps:
    - id: step_1_receive
      description: POST /api/action receives ActionRequest.
      file: mind/infrastructure/api/app
      function: player_action
      input: ActionRequest
      output: Response payload
      trigger: HTTP Post
      side_effects: none
    - id: step_2_process
      description: Orchestrator coordinates narrator and physics tick.
      file: mind/infrastructure/orchestration/orchestrator.py
      function: process_action
      input: action_text, playthrough_id
      output: ActionResult
      trigger: player_action call
      side_effects: graph mutations, history updates
  docking_points:
    guidance:
      include_when: action results are transformed or events are emitted
    available:
      - id: action_input
        type: api
        direction: input
        file: mind/infrastructure/api/app
        function: player_action
        trigger: POST /api/action
        payload: ActionRequest
        async_hook: not_applicable
        needs: none
        notes: Primary entry point for player intent
      - id: action_output
        type: api
        direction: output
        file: mind/infrastructure/api/app
        function: player_action
        trigger: return payload
        payload: object
        async_hook: optional
        needs: none
        notes: Response sent back to UI
    health_recommended:
      - dock_id: action_input
        reason: Verification of player intent ingestion.
      - dock_id: action_output
        reason: Verification of simulation response quality.
```

---

## LOGIC CHAINS

### LC1: Health Check

**Purpose:** Validate graph connectivity without heavy scans.

```
GET /health
  → get_graph_queries().query("RETURN 1 AS ok")
    → get_graph_ops() to validate write path
      → return status JSON
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind/infrastructure/api
    ├── imports → mind/infrastructure/orchestration
    ├── imports → mind/physics/graph
    ├── imports → mind/moment_graph
    └── imports → mind/infrastructure/tempo
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| fastapi | HTTP server | `app`, `moments`, etc. |
| PyYAML | Config parsing | `playthroughs` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Orchestrator Cache | `app.py:_orchestrators` | process | per-playthrough cache |
| SSE Clients | `sse_broadcast.py:_sse_clients` | process | per-connection |

---

## RUNTIME BEHAVIOR

### Initialization

1. create_app() wires routers.
2. Shared graph helpers initialized lazily.

### Request Cycle

1. FastAPI routes to handler.
2. Handler resolves playthrough-specific state.
3. Response returned (JSON or SSE).

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| FastAPI | async | Concurrent request handling on event loop |
| SSE Streams | async queues | Dedicated per-client buffers |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `graph_name` | `create_app` | `blood_ledger` | Default FalkorDB graph |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `mind/infrastructure/api/app` | 13 | `DOCS: docs/infrastructure/api/` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| App factory | `mind/infrastructure/api/app:create_app` |
| Health check | `mind/infrastructure/api/app:health_check` |

---

## MARKERS

### Extraction Candidates

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `app` | ~735L | <400L | views module (planned) | view/ledger endpoints |

### Missing Implementation

<!-- @mind:todo Authentication and rate limiting. -->
