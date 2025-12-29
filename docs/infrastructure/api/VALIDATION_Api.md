# API — Validation

## INVARIANTS

- `GET /health` returns an ISO-8601 UTC timestamp so clients can compare clocks.
- `GET /health` returns `status=ok` only when both read and write graph connections succeed.
- Debug SSE events are serialized JSON strings so downstream consumers can parse them safely.
- Debug SSE clients are removed on disconnect or cancellation to avoid leaked queues.

## PROPERTIES

- The app factory returns a fully wired FastAPI instance with routers and shared dependencies attached once.
- Debug and gameplay streams are isolated; debug queue backpressure must not block gameplay delivery.
- Health checks are lightweight and should not mutate graph state or enqueue gameplay events.

## ERROR CONDITIONS

- Graph read failure returns `503` with `graph_read=error` details.
- Graph write failure returns `503` with `graph_write=error` details.
- Invalid request payloads trigger FastAPI validation errors (HTTP 422) with field-level messages.
- Debug stream keeps sending `ping` events when idle, but closes on cancellation or disconnect.

## TEST COVERAGE

- No dedicated API-only tests are documented; behavior is covered via manual smoke checks and shared engine integration tests.
- The engine test suite exercises downstream services, but does not assert API HTTP responses directly.

## VERIFICATION PROCEDURE

1. Start the API app and confirm `GET /health` returns `status=ok` with a UTC timestamp.
2. Open a debug SSE client and verify JSON payloads plus periodic `ping` events when idle.
3. Force a graph connection failure and confirm `503` responses include `graph_read`/`graph_write` error markers.

## SYNC STATUS

Validation notes align with `docs/infrastructure/api/SYNC_Api.md` and the current implementation doc chain as of 2025-12-19.

-## MARKERS

- [x] Add explicit API integration tests that assert health and SSE behavior (covered by `runtime/tests/test_moments_api.py`
  and `runtime/tests/test_router_schema_validation.py`).
<!-- @mind:proposition Document a reproducible smoke-test script for playthrough creation and action dispatch. -->
<!-- @mind:escalation Should validation include an auth-required health mode once gateway decisions are final? -->

---

## CHAIN

PATTERNS: ./PATTERNS_Api.md
BEHAVIORS: ./BEHAVIORS_Api.md
ALGORITHM: ./ALGORITHM_Api.md
VALIDATION: ./VALIDATION_Api.md
IMPLEMENTATION: ./IMPLEMENTATION_Api.md
TEST: ./TEST_Api.md
SYNC: ./SYNC_Api.md
