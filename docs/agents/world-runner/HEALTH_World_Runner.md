# World Runner — Health: Verification Checklist and Coverage

```
STATUS: DESIGNING
CREATED: 2025-12-20
UPDATED: 2025-12-31
```

---

## PURPOSE OF THIS FILE

This file captures the health flows, indicators, and checkers that prove the World Runner keeps background time consistent while the Narrator writes scenes. It lists the triggers, docks, objectives, and representations the doctor needs to map into the logs so no invisible evolution can corrupt the canonical graph.

What it protects:
- **Off-screen continuity**: Every background tick keeps the pressure flips coherent so interrupted scenes resume pointing at the same facts.
- **Service orchestration reliability**: The CLI agent and fallback machinery must stay responsive across timeouts, crashes, and special-purpose prompts.
- **Injection sanity**: Narrator-facing payloads stay schema-compliant even when the runner returns during multi-turn resumptions.

---

## WHY THIS PATTERN

Documenting health flows outside the code keeps the runner’s contract visible without touching runtime logic. World Runner touches the graph, CLI, and narrator in a single call, so this pattern names the docks, timing, and guardrails that operators can verify before the next deployment.

- Prevents drifting into noisy telemetry by explicitly tying each indicator to validation IDs instead of leaving that reasoning buried in `_call_claude()`.
- Keeps CLI resiliency visible so fallback errors do not become silent time freezes that block the narrator.
- Makes cadence and risk explicit for future agents checking DOC_TEMPLATE_DRIFT, allowing them to approve health coverage without playing through the entire loop.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_World_Runner.md
BEHAVIORS:       ./BEHAVIORS_World_Runner.md
ALGORITHM:       ./ALGORITHM_World_Runner.md
VALIDATION:      ./VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_World_Runner_Service_Architecture.md
HEALTH:          ./HEALTH_World_Runner.md
SYNC:            ./SYNC_World_Runner.md
```

> **Contract:** Health checks verify background continuity and fallback safety without changing CLI prompts or graph logic.

---

## CHECKS

Run the World Runner health checklist before significant orchestration changes and after CLI agent updates. These checks map the `fallback_validator` and `mutation_safety_checker` to the indicator table below so operators always know which failure mode triggered the health alert.

---

## HOW TO USE THIS TEMPLATE

- Start with the `FLOWS ANALYSIS` block so you understand the triggers, expected cadence, and risks before tracing any dock.
- Use the `OBJECTIVES COVERAGE` table to see which indicator protects which goal and where the doctor should focus when the health banner drifts.
- Take the named indicators into the `CHECKER INDEX`, link them to validation IDs, and describe the representation and aggregation to keep metrics consistent between docs and dashboards.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: world_evolution
    purpose: Advance pressure-driven story bits while the narrator hands control to the runner.
    triggers:
      - type: event
        source: Orchestrator long-action scheduling
        notes: Fired when the player action lasts longer than a single narration tick and the CLI must emit background mutations.
    frequency:
      expected_rate: 0.5/min (when idle travel workflows run)
      peak_rate: 5/min (during rapid traversal skips)
      burst_behavior: Limited by CLI timeouts and queued flips when the graph backlog grows.
    risks:
  - Graph mutations reflect stale facts because the CLI completed after the narrator already resumed.
  - CLI failures cause the orchestrator to stall and leave the world state frozen while waiting for a fallback.
```

This flow runs at roughly 0.5/min with 5/min bursts, and it feeds the `background_consistency` and `adapter_resilience` indicators so the manual `mind validate` check described later always samples the same cadence.

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: background_consistency
    flow_id: world_evolution
    priority: high
    rationale: Ensures world mutations never contradict the canon despite the delays between ticks.
  - name: adapter_resilience
    flow_id: world_evolution
    priority: high
    rationale: Keeps CLI failure paths safe so the orchestrator never stalls waiting for a response that will never arrive.
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|---------------------------|
| Keep off-screen evolution consistent so the narrator never observes contradictory pressure dynamics or stale flips. | background_consistency | A dropped mutation or inconsistent injection breaks the story, so this indicator gates scene resumption before it reaches the narrator. |
| Guarantee CLI adapter resiliency such that agent timeouts, parse errors, or missing binaries degrade to safe fallback responses. | adapter_resilience | Failure to fall back leaves the orchestrator waiting forever, so this indicator confirms the fallback validator and error logging continue to work. |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: doctor_logs
  result:
    representation: float_0_1
    value: 0.97
    updated_at: 2025-12-31T12:00:00Z
    source: world_runner_integration_pulse
    notes: Weighted average of background consistency passes and adapter resilience success stories captured in the logs.
```

---

## DOCK TYPES (COMPLETE LIST)

- `cli_context` (input) — Prompt bundles assembled by `engine.infrastructure.orchestration.orchestrator.Orchestrator` before `_call_claude()` starts the CLI run.
- `graph_mutations` (output) — The mutation map returned by `WorldRunnerService.process_flips()` and applied through `engine.physics.graph.graph_ops` so the world state stays canonical.
- `injection_payload` (output) — The narrator-facing `world_injection` dict that the orchestrator commits after every event loop so interruptions surface as structured moments.
- `fallback_response` (output) — The safe dict assembled when `_call_claude()` fails, ensuring the orchestrator always receives a V1-compliant result even on parser errors or timeouts.

---

## CHECKER INDEX

```yaml
checkers:
  - name: fallback_validator
    purpose: Validates that `_fallback_response()` always returns the V1 schema after CLI errors, keeping CLI failures visible instead of letting the orchestrator hang without feedback.
    status: active
    priority: high
  - name: mutation_safety_checker
    purpose: Verifies background mutation batches parsed from the agent response always apply via `graph_ops` without dangling references or schema violations.
    status: active
    priority: high
  - name: injection_schema_guard
    purpose: Plans to ensure the narrator-facing injection payload matches `TOOL_REFERENCE.md` so downstream renderers never reject the runner’s output.
    status: pending
    priority: medium
```

---

## INDICATOR: background_consistency

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: background_consistency
  client_value: Brings consistency to the world evolution logic so interruptions never leave contradictions for the narrator.
  validation:
    - validation_id: V1 (Runner)
      criteria: Output schema always contains `thinking`, `graph_mutations`, and `world_injection` before handing control back to the orchestrator.
    - validation_id: V2 (Runner)
      criteria: Runner calls stay stateless so each tick sees the latest graph when deciding whether to interrupt or finish.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: runner_input
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService.process_flips
    location: mind/infrastructure/orchestration/world_runner.py:34-88
  output:
    id: graph_mutations
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService.process_flips
    location: mind/infrastructure/orchestration/world_runner.py:110-145
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
semantics:
  float_0_1: Ratio of consistent mutation batches versus total background runs in the latest integration pulse.
  aggregation:
    method: Minimum of weighted indicators so a single contradictory mutation drags the score.
    display: Surface via the doctor log and the CLI health banner whenever the score dips below 0.90.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Track every mutation batch returned from the CLI and compare it with the prior graph snapshot before sending the injection downstream.
  steps:
    - Capture `graph_mutations` and `world_injection` from `WorldRunnerService.process_flips()` and note the last interrupts processed.
    - Run those payloads through the schema validator referenced in `docs/agents/world-runner/TEST_World_Runner_Coverage.md` while logging discrepancies.
    - Flag background_consistency as failed if any mutation references an edge that the prior graph snapshot did not permit, preventing the narrator from consuming contradictory facts.
  data_required: CLI response text, parsed mutation dict, canon graph snapshot, and the previous injection metadata.
  failure_mode: The crawler returns facts that the graph has already moved past, making the narrator appear to change the world mid-sentence.
```

---

## INDICATOR: adapter_resilience

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: adapter_resilience
  client_value: Keeps orchestrator routing alive by degrading gracefully whenever `_call_claude()` fails to return usable JSON.
  validation:
    - validation_id: V3 (Runner)
      criteria: Errors from the CLI yield `_fallback_response()` with empty mutations and clear logging instead of stalling.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: runner_invocation
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService._call_claude
    location: mind/infrastructure/orchestration/world_runner.py:62-99
  output:
    id: fallback_response
    method: engine.infrastructure.orchestration.world_runner.WorldRunnerService._fallback_response
    location: mind/infrastructure/orchestration/world_runner.py:120-150
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - binary
    - float_0_1
  selected:
    - binary
semantics:
  binary: 1 when `_fallback_response()` is triggered and 0 when the CLI delivers valid data, providing a deterministic alert whenever the adapter trips.
  aggregation:
    method: Logical AND of CLI success and fallback gating so any single crash is surfaced immediately.
    display: Doctor logs emit a RED event when adapter_resilience equals 0, and the orchestrator banner flips to PENDING.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Monitor `_call_claude()` for non-zero exits, timeouts, or parse failures and confirm `_fallback_response()` hands a safe payload back.
  steps:
    - Invoke `_call_claude()` inside the orchestrator shim and catch `TimeoutExpired`, `FileNotFoundError`, or JSON parse errors.
    - Route the stack into `_fallback_response()` so logs record the failure and the CLI still returns a V1-compliant structure.
    - Mark adapter_resilience as failed whenever this guard path executes and emit telemetry so operators can triage the CLI binary state.
  data_required: CLI stderr/stdout, fallback dict contents, runtime exception metadata.
  failure_mode: A crash leaves the orchestrator waiting forever and no fallback object ever propagates, breaking the moment loop.
```

---

## HOW TO RUN

1. Run the integration suite that drives the orchestrator by executing `pytest mind/tests/test_moment_lifecycle.py` so World Runner receives realistic `process_flips()` calls and logs health events.
2. For manual verification, instantiate `WorldRunnerService` in a Python shell, feed it a curated `Orchestrator` context, and inspect the `graph_mutations` and `world_injection` dictionaries for consistency before letting the Narrator resume.
3. If you need to reproduce adapter failures, temporarily point `_call_claude()` at a stub CLI that returns invalid JSON so the fallback paths, logs, and health indicators become visible in the doctor trace.

---

## KNOWN GAPS

<!-- @mind:todo No automated regression exists specifically for CLI timeout handling even though the fallback validator depends on that guard. -->
<!-- @mind:todo The injection payload returned to the Narrator is not yet schema-validated before it is forwarded, leaving room for untracked drift. -->

---

## MARKERS

<!-- @mind:todo Automate a quick CLI failure test by mocking `_call_claude()` so adapter_resilience can be asserted on every commit. -->
<!-- @mind:todo Add a background mutation diff that highlights graph edges touched by each run to surface unexpected changes before the narrator is notified. -->
<!-- @mind:escalation Should the runner health banner share the same scoring cadence as the Narrator health indicator so the doctor dashboard has a unified view of streaming consistency? -->
