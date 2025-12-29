# Narrator — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2024-12-19
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Narrator.md
BEHAVIORS:       ./BEHAVIORS_Narrator.md
ALGORITHM:       ./ALGORITHM_Scene_Generation.md
VALIDATION:      ./VALIDATION_Narrator.md
THIS:            IMPLEMENTATION_Narrator.md (you are here)
HEALTH:          ./HEALTH_Narrator.md
SYNC:            ./SYNC_Narrator.md

IMPL:            runtime/infrastructure/orchestration/narrator.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
agents/narrator/
├── CLAUDE.md             # Core agent instructions (System Prompt)
├── .claude/              # Agent CLI state
└── ...
runtime/infrastructure/orchestration/narrator.py  # Python entry point and prompt builder
runtime/infrastructure/orchestration/agent_cli.py # CLI wrapper for agent invocation
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `agents/narrator/CLAUDE.md` | Authorial intelligence rules | N/A | ~400 | OK |
| `runtime/infrastructure/orchestration/narrator.py` | Prompt construction and IO | `run_narrator` | ~300 | OK |
| `runtime/infrastructure/orchestration/agent_cli.py` | Subprocess management | `run_agent` | ~200 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Agent-as-a-Service with CLI integration.

**Why this pattern:** Decouples the authorial logic (prompt-driven) from the game engine (Python-driven). The CLI interface allows for thread persistence and easy testing.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Prompt Builder | `runtime/infrastructure/orchestration/narrator.py` | Dynamically assembles context for the LLM. |
| Streaming | `tools/stream_dialogue.py` | Delivers incremental output to the frontend via SSE. |

---

## SCHEMA

### Narrator Output (JSON)

```yaml
NarratorOutput:
  required:
    - scene: object            # New scene tree or updates
    - time_elapsed: int        # Game minutes passed
  optional:
    - mutations: list          # Graph updates to apply
    - voice_lines: list        # Audio assets to trigger
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| Narrator Call | `runtime/infrastructure/orchestration/narrator.py:50` | Orchestrator.process_action |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Scene Generation: Action → Narrator → Graph

This flow handles the transition from a player action to a newly authored scene, including any world-state changes (mutations).

```yaml
flow:
  name: scene_generation
  purpose: Author new story beats based on current graph state.
  scope: Action -> LLM -> Graph Mutations -> Scene Response
  steps:
    - id: step_1_context
      description: Orchestrator gathers graph context and world state.
      file: runtime/infrastructure/orchestration/narrator.py
      function: build_prompt
      input: playthrough_id, player_action
      output: full_prompt_string
      trigger: run_narrator call
      side_effects: none
    - id: step_2_author
      description: Agent authors response using CLAUDE.md rules.
      file: agents/narrator/CLAUDE.md
      function: N/A (Agent Intelligence)
      input: prompt
      output: JSON payload
      trigger: subprocess call
      side_effects: none
    - id: step_3_apply
      description: Extract and apply graph mutations from output.
      file: runtime/physics/graph/graph_ops.py
      function: apply_mutation
      input: mutation_list
      output: success_boolean
      trigger: runtime/infrastructure/orchestration/narrator.py parsing
      side_effects: graph state changed
  docking_points:
    guidance:
      include_when: narrative intent becomes concrete data
    available:
      - id: narrator_input
        type: custom
        direction: input
        file: runtime/infrastructure/orchestration/narrator.py
        function: run_narrator
        trigger: Orchestrator
        payload: PromptContext
        async_hook: optional
        needs: none
        notes: Context fed to the authorial intelligence
      - id: narrator_output
        type: custom
        direction: output
        file: runtime/infrastructure/orchestration/narrator.py
        function: run_narrator
        trigger: return response
        payload: NarratorOutput
        async_hook: required
        needs: none
        notes: Raw output before filtering
    health_recommended:
      - dock_id: narrator_output
        reason: Verification of authorial coherence and schema adherence.
```

---

## LOGIC CHAINS

### LC1: Invention to Canon

**Purpose:** Ensure LLM inventions are persisted correctly.

```
Agent authored "fact"
  → runtime/infrastructure/orchestration/narrator.py extracts mutations
    → graph_ops.py applies to FalkorDB
      → fact is now queryable by physics/other agents
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/infrastructure/orchestration/narrator.py
    ├── imports → runtime/physics/graph
    └── imports → runtime/moment_graph
```

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Thread History | `.claude/` | thread | per-playthrough session |

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Narrator CLI | Sync/Subprocess | Blocks worker thread during generation |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `AGENTS_MODEL` | env | `claude` | Model provider for narrator |

---

## RUNTIME BEHAVIOR

### Initialization

```
1. When the orchestrator instantiates `NarratorService` it scans for the `agents/narrator` working directory, configures timeouts, and logs the startup handshake so the health tooling knows the narrator is warming up.
2. The CLI imports `CLAUDE.md`, ensures `session_started` is false, and preloads rolling-window context so the first scene begins with canonical facts instead of improvising.
3. Once those checks succeed, the orchestrator broadcasts readiness and the front end can immediately begin feeding player actions without waiting for extra initialization chatter.
```

### Main Loop / Request Cycle

```
1. The engine calls `NarratorService.generate` with player actions, scene context, and optional world injections so the prompt builder can bake precise canonical state into the request.
2. The service runs `agent_cli.run_agent`, passing the continuation flag, streaming hooks, and `CLAUDE.md` instructions so the LLM can respond via SSE/JSON while the CLI awaits completion.
3. Parsed `NarratorOutput` flows through `runtime/physics/graph/graph_ops.py:apply_mutations` before the orchestrator streams the updated scene, elapsed time, and clickables back to the UI and logs success.
```

The output is streamed back through `tools/stream_dialogue.py`'s SSE wiring, which buffers narrator packets, annotates clickables, and records the final JSON payload in the health logs before the UI consumes it; thinking of the stream as two layers (chunk emitter + health logger) helps keep the CLI steady when applying backpressure.

### Shutdown

```
1. When playthrough teardown begins, `reset_session` clears `session_started`, allowing the next run to rebuild fresh prompts without accidental carryover of prior continuity.
2. Shutdown logs capture narrator availability changes while any active SSE buffers flush so the UI stops waiting on the narrator stream.
3. If the orchestrator closes the CLI, the platform ensures subprocesses exit cleanly and health monitors mark the narrator offline until the next restart.
```

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `runtime/infrastructure/orchestration/narrator.py` | 7 | `# DOCS: docs/agents/narrator/` (includes this implementation doc) |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| RUNTIME BEHAVIOR (Main Loop / Request Cycle) | `runtime/infrastructure/orchestration/narrator.py:45-165` (`generate`, `_build_prompt`, `_call_claude`) |
| DATA FLOW AND DOCKING (Scene Generation: Action → Narrator → Graph) | `runtime/physics/graph/graph_ops.py:704-742` (`apply_mutations`, logging) |
| LOGIC CHAINS (LC1: Invention to Canon) | `runtime/physics/graph/graph_ops.py:704-742` (`apply_mutations`, graph logging) |
| STATE MANAGEMENT (Thread History resets) | `runtime/infrastructure/orchestration/narrator.py:197-200` (`reset_session`) |

--- 

## MARKERS

### Extraction Candidates

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `runtime/infrastructure/orchestration/narrator.py` | ~200L (OK) | <400L | `narrator/prompt_builder.py` | Split prompt serialization and fallback plumbing once rolling-window logic grows to keep CLI wiring lean. |

### Missing Implementation

<!-- @mind:todo Add SSE health instrumentation that emits schema versions and streaming latency metadata so monitoring tooling can validate narrator output without manual CLI invocation. -->
<!-- @mind:todo Harden the fallback response metadata to surface narrator voice hints and mutation summaries before the engine applies defaults, reducing hallucination risk when generation fails. -->

### Ideas

<!-- @mind:proposition Log narrator prompt contexts and outcomes to a dedicated audit trail so debugging continuity breaks does not require parsing raw CLAUDE output. -->
<!-- @mind:proposition Surface narrator mutation summaries in the health dashboard with toggles for scene drift, SSE lag, and graph updates to speed up telemetric checks. -->
<!-- @mind:proposition Publish narrator SSE progress summaries (scene hash, click count, and latency) into the health log so the doctor can spot streaming stalls without replaying the full conversation. -->

### Questions

<!-- @mind:escalation Should the narrator CLI pre-cache heavy graph snapshots before each run when world size grows so repeated queries do not stall scene generation? -->
<!-- @mind:escalation How strict should the free-input guardrail be when deciding whether to hand a proposal back to physics versus issuing a canned fallback response? -->
