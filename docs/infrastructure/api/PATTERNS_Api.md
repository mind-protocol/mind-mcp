# API — Patterns

## THE PROBLEM

The API needs a consistent entrypoint for gameplay actions, streaming, and health
checks without leaking infrastructure concerns across endpoints. Without shared
patterns, initialization becomes fragile, dependencies sprawl, and behavior
drifts between routers.

## THE PATTERN

Centralize the FastAPI setup in a single app factory that wires shared
dependencies, exposes focused endpoints, and keeps debug streaming isolated from
gameplay events. Keep the API thin, delegating heavy work to orchestration and
graph layers.

## PRINCIPLES

### App Factory First

- Use a single `create_app()` factory to wire routes, shared state, and
  dependency helpers.
- Keep shared resources (graph clients, orchestrators) inside the factory
  closure.

### Lightweight Health Checks

- Health checks should validate connectivity without expensive graph scans.
- Prefer simple queries and connection instantiation.

### SSE Debug Streams

- Debug streaming is isolated from gameplay SSE to avoid accidental coupling.
- Each client receives a dedicated queue to prevent slow consumers from blocking
  others.

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| runtime/physics/graph | GraphOps/GraphQueries power mutations and health checks. |
| runtime/infrastructure/orchestration | Orchestrator processes actions and drives the loop. |
| runtime/infrastructure/embeddings | Optional embeddings used during playthrough creation. |
| scenarios/ | Scenario YAML and opening templates drive playthrough creation. |
| FastAPI | HTTP server and routing framework for the API surface. |

## INSPIRATIONS

App-factory FastAPI deployments, SSE queue fan-out patterns, and service
boundaries that separate orchestration from transport concerns.

## SCOPE

### In Scope

- FastAPI app factory wiring for API routers and shared dependencies.
- Playthrough creation, action dispatch, and health/debug endpoints.
- Debug stream isolation policies and queue lifecycle management.

### Out of Scope

- Frontend hooks and UI-specific state handling -> see: `docs/frontend/`.
- Graph mutation logic and physics tick behavior -> see: `docs/physics/`.
- Narrator prompt composition and agent behavior -> see: `docs/agents/narrator/`.

## MARKERS

<!-- @mind:todo Document the API versioning strategy once public clients exist. -->
<!-- @mind:todo Clarify whether debug SSE should be behind auth or dev-only config. -->
<!-- @mind:proposition Split the app factory into per-router factories when the surface grows. -->
<!-- @mind:escalation
title: "Should health checks include a read-only scenario asset check?"
priority: 5
response:
  status: resolved
  choice: "N/A — wrong scope"
  notes: "2025-12-23: Scenarios are Blood Ledger scope, not mind. Remove scenario references from mind repo; health checks stay simple (DB/graph connectivity only)."
-->

## CHAIN

PATTERNS: ./PATTERNS_Api.md
BEHAVIORS: ./BEHAVIORS_Api.md
ALGORITHM: ./ALGORITHM_Api.md
VALIDATION: ./VALIDATION_Api.md
IMPLEMENTATION: ./IMPLEMENTATION_Api.md
HEALTH: ./HEALTH_Api.md
SYNC: ./SYNC_Api.md
```
