# World Runner — Validation: Service Invariants and Failure Behavior

```
STATUS: STABLE
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against working tree (manual review only)
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_World_Runner.md
BEHAVIORS:       ./BEHAVIORS_World_Runner.md
ALGORITHM:       ./ALGORITHM_World_Runner.md
THIS:            VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_World_Runner_Service_Architecture.md
TEST:            ./TEST_World_Runner_Coverage.md
SYNC:            ./SYNC_World_Runner.md

IMPL:            runtime/infrastructure/orchestration/world_runner.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## INVARIANTS

### V1: Output Schema Is Always Returned

```
WorldRunnerService.process_flips() returns a dict containing:
  - thinking: string
  - graph_mutations: dict
  - world_injection: dict
```

**Checked by:** Manual review of `_call_claude()` and `_fallback_response()` in `runtime/infrastructure/orchestration/world_runner.py`.

### V2: Runner Calls Are Stateless

```
Agent CLI is invoked without --continue, and calls do not depend on
prior state outside the graph/context passed in the prompt.
```

**Checked by:** Manual review of `_call_claude()` CLI arguments.

### V3: Failures Degrade Safely

```
On non-zero exit, timeout, JSON parse error, or missing CLI,
the service returns a safe fallback response with empty mutations.
```

**Checked by:** Manual review of `_call_claude()` error handlers.

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | Every invocation of `WorldRunnerService.process_flips()` delivers `thinking`, `graph_mutations`, and `world_injection`, even when `_fallback_response()` is triggered. | Guarantees that narrators and downstream tooling never see partial payloads, giving the doctor an anchor to assert schema compliance while fallback runs finish safely. |
| B2 | Each run reloads the latest graph snapshot, applies mutations, and returns without relying on retained state. | Stateless calls keep every tick deterministic and let `background_consistency` monitors confirm the injection always reflects the freshest world before narrating. |
| B3 | CLI errors, timeouts, or parse failures always produce the documented fallback response plus a log entry. | `adapter_resilience` can surface every degradation immediately instead of letting the orchestrator hang, so operators know when the runner tripped over the agent boundary. |

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| Deliver deterministic narrator-ready injections before control returns. | V1, V2 | Binding schema and statelessness together ensures the Narrator sees a complete, consistent graph snapshot plus the intended mutations every run. |
| Surface every CLI failure via safe fallbacks so the orchestrator can react. | V3, P1 | Connecting fallback guarantees to the documented error conditions lets the health tooling flag degraded runs before they block the narrator. |
| Keep validation documentation aligned with the error modes operators will triage. | E1, E2, E3 | Explicitly naming the symptoms prevents ad-hoc investigations and lets tooling look for the right log keys when replaying incidents. |

## HEALTH COVERAGE

- `background_consistency` in `docs/agents/world-runner/HEALTH_World_Runner.md` checks that every mutation batch and injection remains schema-compliant before the Narrator consumes it.
- `adapter_resilience` reuses the validation error modes to alert whenever `_call_claude()` returns non-zero, times out, or emits invalid JSON, so the orchestrator always knows which guardrail tripped.
- `fallback_validator` and `mutation_safety_checker` are the scripted checks that tie these invariants back to automation so `mind doctor` can prove the service never drifts from the documented safe states.

---

## PROPERTIES

### P1: Error Paths Always Return Valid Output

```
FORALL error in {timeout, parse_error, cli_missing, nonzero_exit}:
    process_flips(...) returns V1-compliant output
```

**Tested by:** NOT YET TESTED — no automated tests present.

---

## ERROR CONDITIONS

### E1: Agent CLI Returns Non-Zero

```
WHEN:    subprocess.run() returns returncode != 0
THEN:    fallback response is returned
SYMPTOM: logged error "[WorldRunnerService] Agent CLI failed"
```

**Tested by:** NOT YET TESTED — manual review only.

### E2: Invalid JSON Response

```
WHEN:    response_text cannot be parsed as JSON
THEN:    fallback response is returned
SYMPTOM: logged error "[WorldRunnerService] Failed to parse response"
```

**Tested by:** NOT YET TESTED — manual review only.

### E3: CLI Timeout or Missing Binary

```
WHEN:    subprocess.TimeoutExpired OR FileNotFoundError
THEN:    fallback response is returned
SYMPTOM: logged timeout or "Agent CLI not found"
```

**Tested by:** NOT YET TESTED — manual review only.

---

## TEST COVERAGE

| Requirement | Test(s) | Status |
|-------------|---------|--------|
| V1: Output schema | — | ⚠ NOT YET TESTED |
| V2: Stateless calls | — | ⚠ NOT YET TESTED |
| V3: Safe fallback | — | ⚠ NOT YET TESTED |
| P1: Error path output | — | ⚠ NOT YET TESTED |
| E1: Non-zero exit | — | ⚠ NOT YET TESTED |
| E2: Invalid JSON | — | ⚠ NOT YET TESTED |
| E3: Timeout/CLI missing | — | ⚠ NOT YET TESTED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — inspect _call_claude() and _fallback_response()
[ ] V2 holds — verify no --continue in CLI invocation
[ ] V3 holds — inspect exception handlers and fallback path
[ ] Error logging present for E1/E2/E3
```

### Automated

```bash
# No automated tests for World Runner service yet.
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-19
VERIFIED_AGAINST:
    impl: runtime/infrastructure/orchestration/world_runner.py (working tree)
    test: none
VERIFIED_BY: manual review
RESULT:
    V1: PASS (manual)
    V2: PASS (manual)
    V3: PASS (manual)
```

---

## MARKERS

<!-- @mind:todo Add unit tests for error handling and schema compliance. -->
<!-- @mind:todo Add a contract test that validates WorldRunnerOutput against TOOL_REFERENCE schema. -->
