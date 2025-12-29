# API — Sync: Current State

```
STATUS: CANONICAL
UPDATED: 2025-12-21
```

## MATURITY

STATUS: CANONICAL

What's canonical (v1):
- API app factory, router wiring, and current playthrough/moment endpoints are live and documented.
- Debug and gameplay SSE streams are established with separate queues.

What's still being designed:
- Auth, rate limiting, and API gateway decisions.

## CURRENT STATE

**Implementation Location:** `runtime/infrastructure/api/app.py`

The API module hosts the FastAPI application, including playthrough endpoints, moment APIs, and debug streaming.

## RECENT CHANGES

### 2025-12-21: Guard SSE delivery and schema validation with tests

- **What:** Added a burst-load SSE regression test in `runtime/tests/test_moments_api.py` and introduced
  `runtime/tests/test_router_schema_validation.py` to exercise the playthrough and tempo router schemas.
- **Why:** Prevent regressions when SSE queues back up under sustained clicks and ensure router Pydantic
  models keep rejecting malformed payloads before expensive graph operations run.
- **Impact:** Automated coverage now documents both SSE reliability and router request validation, so the
  previous gaps no longer need manual verification.

### 2025-12-21: Consolidate playthrough algorithm docs

- **What:** Simplified `ALGORITHM_Playthrough_Creation.md` into a legacy alias that points to `ALGORITHM_Api.md` instead of re-documenting the same flow.
- **Why:** Remove duplication while keeping the old path alive for existing references, so there is one authoritative ALGORITHM doc for the API module.
- **Impact:** Agents should consult `ALGORITHM_Api.md` for playthrough creation logic; the alias now serves as a redirect.

### 2025-12-20: Pending external implementation references

- **What:** Replaced stub file paths with pending import notes in implementation docs.
- **Why:** Remove broken impl links until upstream code is imported.

### 2025-12-20: Broadcast player moments on SSE

- **What:** Emit `moment_completed` SSE events when `/api/moment` creates a player moment.
- **Why:** UI relies on SSE to refresh; player messages were not appearing.
- **Impact:** Frontend receives a refresh trigger after player input.

### 2025-12-20: Fix moment stream route collision

- **What:** Moved `/api/moments/stream/{playthrough_id}` above the generic
  `/{playthrough_id}/{moment_id}` route in `runtime/infrastructure/api/moments.py`.
- **Why:** The generic route was capturing `/stream/{id}` and returning 404.
- **Impact:** SSE stream endpoint responds with 200 as expected.

### 2025-12-20: Mind Framework Refactor

- **What:** Refactored `IMPLEMENTATION_Api.md` and updated `TEST_Api.md` to the Health format.
- **Why:** To align with the new mind documentation standards and emphasize DATA FLOW AND DOCKING.
- **Impact:** API module documentation is now compliant; Health checks are anchored to concrete docking points.

### 2025-12-20: Discussion Tree Branch Counting

- **What:** Count discussion tree branches by remaining leaf paths and document the helper behavior.
- **Why:** Ensure regeneration triggers reflect actual remaining branch paths.
- **Impact:** Branch count now aligns with discussion tree lifecycle expectations.

## HANDOFF: FOR AGENTS

Use VIEW_Implement_Write_Or_Modify_Code when touching API routers. Ensure new endpoints are extracted from `app.py` to keep it from growing further.

## TODO

<!-- @mind:todo Split remaining legacy endpoints from `app.py` into router modules. -->
<!-- @mind:todo Implement API versioning strategy. -->

## POINTERS

- `docs/infrastructure/api/PATTERNS_Api.md` for scope and design rationale.
- `docs/infrastructure/api/IMPLEMENTATION_Api.md` for endpoint-level data flow notes.

## CHAIN

```
THIS:            SYNC_Api.md (you are here)
PATTERNS:        ./PATTERNS_Api.md
BEHAVIORS:       ./BEHAVIORS_Api.md
ALGORITHM:       ./ALGORITHM_Api.md
VALIDATION:      ./VALIDATION_Api.md
IMPLEMENTATION:  ./IMPLEMENTATION_Api.md
HEALTH:          ./HEALTH_Api.md
```
