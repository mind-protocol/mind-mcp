# API — Behaviors

## BEHAVIORS

The API exposes a thin FastAPI surface that brokers playthrough creation,
moment streaming, and debug mutation visibility while delegating heavy work to
orchestration and graph layers. It guarantees consistent response shapes for
health and debug endpoints and preserves a stable SSE connection contract.

## INPUTS / OUTPUTS

- Inputs include HTTP requests to playthrough, moment, action, and health
  routes plus SSE client connections for gameplay and debug streams.
- Outputs include JSON payloads for health/action responses and SSE event
  frames with named events, timestamps, and JSON data payloads.

## EDGE CASES

- If the graph client is unreachable, health checks downgrade to a 503 response
  with a degraded status and explicit error detail.
- Debug stream queues can become idle; the server emits keepalive pings to
  avoid idle timeouts and to confirm stream liveness.

## Health Check

- `GET /health` returns `status=ok` with timestamp and connection details when the graph is reachable.
- If graph connectivity fails, the endpoint responds with `503` and a `status=degraded` payload describing the failure.

## Debug Mutation Stream

- `GET /api/debug/stream` opens a server-sent events stream for mutation events.
- The stream sends:
  - `connected` event on connect
  - `mutation` events with JSON payloads
  - `ping` keepalives when idle

## ANTI-BEHAVIORS

- The API should not mutate graph state inside health checks or debug streams.
- The debug SSE channel should not leak gameplay events or block on slow
  consumers; each client must keep an isolated queue.

## MARKERS

<!-- @mind:todo Document the expected payload shapes for `/api/action` once the frontend -->
  contract stabilizes.
<!-- @mind:proposition Add explicit backpressure guidance for debug streams in the API docs. -->
<!-- @mind:escalation Should health checks validate scenario assets or remain pure -->
  connectivity probes?

---

## CHAIN

PATTERNS: ./PATTERNS_Api.md
BEHAVIORS: ./BEHAVIORS_Api.md
ALGORITHM: ./ALGORITHM_Api.md
VALIDATION: ./VALIDATION_Api.md
IMPLEMENTATION: ./IMPLEMENTATION_Api.md
TEST: ./TEST_Api.md
SYNC: ./SYNC_Api.md
