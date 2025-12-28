# World Runner — Implementation: Service Architecture and Boundaries

```
STATUS: STABLE
CREATED: 2025-12-19
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_World_Runner.md
BEHAVIORS:      ./BEHAVIORS_World_Runner.md
ALGORITHM:      ./ALGORITHM_World_Runner.md
VALIDATION:     ./VALIDATION_World_Runner_Invariants.md
THIS:           IMPLEMENTATION_World_Runner_Service_Architecture.md
HEALTH:         ./HEALTH_World_Runner.md
SYNC:           ./SYNC_World_Runner.md

IMPL:           mind/infrastructure/orchestration/world_runner.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
agents/
└── world_runner/
    └── CLAUDE.md                       # World Runner agent prompt/instructions

mind/
└── infrastructure/
    └── orchestration/
        ├── __init__.py                 # Exports WorldRunnerService
        └── world_runner.py             # CLI adapter for World Runner agent
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `agents/world_runner/CLAUDE.md` | Agent instructions and output contract | — | ~650 | WATCH |
| `mind/infrastructure/orchestration/world_runner.py` | Build prompt, call agent CLI, parse JSON | `WorldRunnerService` | ~156 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Adapter + Service Wrapper.

**Why this pattern:** Isolates agent CLI interaction behind a stable interface, allowing the LLM boundary to be replaced or mocked without impacting the orchestrator.

---

## SCHEMA

### WorldRunnerOutput (JSON)

```yaml
WorldRunnerOutput:
  required:
    - thinking: string          # Agent's chain-of-thought
    - graph_mutations: object   # Updates for FalkorDB
    - world_injection: object   # Narrative events for the Narrator
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| process_flips | `world_runner.py:34` | Orchestrator._process_flips |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### World Evolution: Ticks → Flips → Agent Resolution

This flow handles the transition from detected pressure flips in the graph to structured world changes and narrative injections.

```yaml
flow:
  name: world_evolution
  purpose: Resolve off-screen pressure flips into concrete world changes.
  scope: Tick Result -> World Runner Agent -> Mutations & Injections
  steps:
    - id: step_1_prompt
      description: Assemble prompt from flips and graph context.
      file: mind/infrastructure/orchestration/world_runner.py
      function: _build_prompt
      input: flips (List), graph_context (Dict)
      output: prompt_string
      trigger: process_flips call
      side_effects: none
    - id: step_2_call
      description: Invoke agent CLI and capture stdout.
      file: mind/infrastructure/orchestration/world_runner.py
      function: _call_claude
      input: prompt_string
      output: json_response_string
      trigger: process_flips workflow
      side_effects: none
    - id: step_3_resolve
      description: Return structured output to Orchestrator.
      file: mind/infrastructure/orchestration/world_runner.py
      function: process_flips
      input: json_response_string
      output: WorldRunnerOutput (Dict)
      trigger: return value
      side_effects: none
  docking_points:
    guidance:
      include_when: world state is being transformed or agents are triggered
    available:
      - id: runner_input
        type: custom
        direction: input
        file: mind/infrastructure/orchestration/world_runner.py
        function: process_flips
        trigger: Orchestrator
        payload: PromptContext
        async_hook: optional
        needs: none
        notes: Context for world-state resolution
      - id: runner_output
        type: event
        direction: output
        file: mind/infrastructure/orchestration/world_runner.py
        function: _call_claude
        trigger: json.loads
        payload: WorldRunnerOutput
        async_hook: required
        needs: none
        notes: Results applied to graph and narrator queue
    health_recommended:
      - dock_id: runner_output
        reason: Verification of background story consistency and schema.
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind/infrastructure/orchestration/orchestrator.py
    └── imports → WorldRunnerService
```

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| CLI Config | `WorldRunnerService` | instance | persistent for service life |

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Agent Call | Sync/Subprocess | Blocks worker until agent returns or times out |

## LOGIC CHAINS

The `WorldRunnerService` chain starts inside `Orchestrator._process_flips` whenever `GraphTick.run` reports flips and hands the pressure flip list, player context, and time span to the service. `process_flips` then orchestrates `_build_prompt`, pulls the detailed flip and character data through `GraphQueries`, and funnels the assembled prompt into `_call_claude`. After `parse_claude_json_output` yields the `WorldRunnerOutput`, `GraphOps.apply` persists the mutations, `_apply_wr_mutations` consolidates them with the orchestrator state, and any returned `world_injection` is queued for the next narrator invocation.

## RUNTIME BEHAVIOR

At runtime the service behaves as a stateless adapter: each `process_flips` invocation begins by querying the graph for pressure metadata, character locations, and strained beliefs, then emits a YAML prompt that includes the flips, the enriched graph context, and the provided player snapshot. `_call_claude` runs the CLI via `run_agent` with `output_format="json"`, guards against timeouts, parse failures, and missing binaries, and only then lets `_fallback_response` surface a minimal injection if anything goes wrong. When the agent returns cleanly, `process_flips` applies `graph_mutations` with `GraphOps`, logs how many narratives or beliefs changed, and hands the parsed output back to the orchestrator along with any saved `world_injection`.

## CONFIGURATION

`WorldRunnerService` is instantiated by the orchestrator with the writer `GraphOps` and reader `GraphQueries` so it can mutate and inspect the same FalkorDB context that triggered the flips. The service uses the optional `working_dir` (defaulting to `Path.cwd()`) so tests or container setups can isolate the CLI invocation, and its `timeout` defaults to 600 seconds but can be shortened to keep agent calls from stalling the main loop. The CLI wrapper relies on `run_agent`, which in turn honours the agent prompt stored in `agents/world_runner/CLAUDE.md`, so adjusting agent expectations or the CLI entry point also propagates to how this service is configured at boot time.

## BIDIRECTIONAL LINKS

- `mind/infrastructure/orchestration/world_runner.py` declares `# DOCS: docs/agents/world-runner/PATTERNS_World_Runner.md`, keeping the code-to-docs link explicit so any code refactor knows to revisit the documented pattern.
- This implementation doc points to `HEALTH_World_Runner.md` and `SYNC_World_Runner.md`, while the SYNC references it under `CHAIN`, ensuring future agents can jump back into the runtime contract from the service state summary.
- The CLI instructions in `agents/world_runner/CLAUDE.md` are effectively linked bidirectionally because this doc captures how the prompt ducks into `_build_prompt`, and the CLAUDE doc can cite this implementation file to ground expectations for the JSON schema and fallback behavior.

## MARKERS

- Instrument `process_flips` to emit a structured trace (flip IDs, prompt length, timestep) so long-running ticks can be profiled without replaying the full narrative cycle.
- Introduce resilience around `GraphQueries.query` calls (circuit breaker, caching, or retry) so a slow or missing context query does not cascade into a fallback world injection.
- Define a small schema validator in this module for `world_injection` so the fallback payload and real injections share explicit optional fields before the narrator processes them.
