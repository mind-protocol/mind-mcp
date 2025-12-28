# mind Graph System — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2024-12-23
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Mind_Graph_System.md
PATTERNS:        ./PATTERNS_Mind_Graph_System.md
BEHAVIORS:       ./BEHAVIORS_Mind_Graph_System.md
ALGORITHM:       ./ALGORITHM_Mind_Graph_System.md
VALIDATION:      ./VALIDATION_Mind_Graph_System.md
THIS:            IMPLEMENTATION_Mind_Graph_System.md (you are here)
HEALTH:          ./HEALTH_Mind_Graph_System.md
SYNC:            ./SYNC_Mind_Graph_System.md

IMPL:            building/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC.

---

## BOUNDARY REMINDER

**We are a client of the mind engine.**

```
┌─────────────────────────────────────────┐
│              ENGINE                      │
│  physics, tick, activation, graph_ops   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │     engine.* API                  │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
                    ▲
                    │ calls
                    │
┌─────────────────────────────────────────┐
│            BUILDING/ (us)                │
│  ingest, agents, formatting, config     │
└─────────────────────────────────────────┘
```

---

## CODE STRUCTURE

```
building/
├── __init__.py              # exports public API
├── ingest/
│   ├── __init__.py
│   ├── discover.py          # file discovery + pattern matching
│   ├── parse.py             # doc parsing, section extraction
│   ├── markers.py           # @mind: marker extraction
│   └── create.py            # calls engine.create_* APIs
├── agents/
│   ├── __init__.py
│   ├── handler.py           # on_agent_trigger entry point
│   ├── prompts.py           # system prompt building
│   ├── response.py          # response parsing
│   └── config.py            # agent definitions from agents.yaml
├── context/
│   ├── __init__.py
│   ├── query.py             # calls engine.get_context
│   └── format.py            # formats context for prompts
├── content/
│   ├── __init__.py
│   ├── moment.py            # moment creation helpers
│   ├── narrative.py         # narrative creation helpers
│   └── inference.py         # type inference from content
├── config/
│   ├── __init__.py
│   ├── mapping.py           # loads repo_to_graph_mapping.yaml
│   └── agents.py            # loads agents.yaml
└── health/
    ├── __init__.py
    └── checks.py            # client-side health checks
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Status |
|------|---------|----------------------|--------|
| `ingest/discover.py` | Find files matching patterns | `discover_files()`, `match_pattern()` | PLANNED |
| `ingest/parse.py` | Parse doc content | `parse_doc()`, `extract_sections()` | PLANNED |
| `ingest/markers.py` | Extract @mind markers | `extract_markers()` | PLANNED |
| `ingest/create.py` | Create graph nodes | `create_spaces()`, `create_narratives()` | PLANNED |
| `agents/handler.py` | Handle agent triggers | `on_agent_trigger()` | PLANNED |
| `agents/prompts.py` | Build system prompts | `build_system_prompt()` | PLANNED |
| `agents/response.py` | Parse LLM responses | `parse_response()`, `extract_moments()` | PLANNED |
| `context/query.py` | Query engine for context | `get_context()` | PLANNED |
| `context/format.py` | Format context for prompt | `format_narratives()`, `format_moments()` | PLANNED |
| `content/moment.py` | Create moments | `create_moment()` | PLANNED |
| `content/narrative.py` | Create narratives | `create_narrative()` | PLANNED |
| `content/inference.py` | Infer types | `infer_moment_type()`, `infer_narrative_type()` | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Layered + Adapter

**Why:**
- We're a thin layer over engine APIs
- Ingest/Agents/Content are independent concerns
- Each module adapts our domain (docs, agents) to engine's domain (nodes, links)

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | `ingest/create.py` | Adapts parsed docs to engine.create_* calls |
| Strategy | `content/inference.py` | Different inference strategies per content type |
| Template Method | `agents/handler.py` | Common trigger flow with customizable steps |

### Anti-Patterns to Avoid

- **Leaking Engine Details**: Don't expose engine internals through our API
- **Fat Ingest**: Don't put parsing + creation + linking in one function
- **Magic Inference**: Type inference should be explicit and testable

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Ingest | File parsing, pattern matching | Engine graph ops | `ingest.run(repo_path)` |
| Agents | Prompt building, response parsing | Engine triggers, LLM | `on_agent_trigger()` |
| Content | Type inference, formatting | Engine node creation | `create_moment()`, `create_narrative()` |

---

## SCHEMA

### IngestConfig (from repo_to_graph_mapping.yaml)

```yaml
IngestConfig:
  required:
    - version: string
    - spaces: SpacePatterns
    - narratives: NarrativePatterns
    - things: ThingPatterns
    - actors: ActorConfig
    - links: LinkPatterns
    - physics: PhysicsDefaults
```

### AgentConfig (from agents.yaml)

```yaml
AgentConfig:
  required:
    - id: string
    - name: string
    - initial_space: string
  optional:
    - base_prompt_path: string
    - weight: float (default 0.8)
```

### ParsedDoc

```yaml
ParsedDoc:
  required:
    - path: string
    - type: string (objectives|pattern|behavior|...)
    - content: string
  optional:
    - sections: List[Section]
    - markers: List[Marker]
    - chain_refs: List[string]
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `ingest.run()` | `ingest/__init__.py` | CLI / bootstrap |
| `on_agent_trigger()` | `agents/handler.py` | Engine callback |
| `create_moment()` | `content/moment.py` | Actor thinking |
| `create_narrative()` | `content/narrative.py` | Actor documenting |

---

## DATA FLOW AND DOCKING

### Flow 1: Ingest

Transforms repo files into graph nodes. Run at bootstrap.

```yaml
flow:
  name: ingest
  purpose: Transform docs/code into graph nodes
  scope:
    input: repo directory
    output: populated graph
  steps:
    - id: discover
      description: Find files matching patterns
      file: ingest/discover.py
      function: discover_files()
      input: repo_path, patterns
      output: List[FilePath]

    - id: parse
      description: Parse doc content and structure
      file: ingest/parse.py
      function: parse_doc()
      input: FilePath
      output: ParsedDoc

    - id: extract_markers
      description: Find @mind markers
      file: ingest/markers.py
      function: extract_markers()
      input: ParsedDoc
      output: List[Marker]

    - id: create_spaces
      description: Create Space nodes
      file: ingest/create.py
      function: create_spaces()
      input: List[DirectoryPattern]
      output: List[space_id]
      side_effects: engine.create_space() calls

    - id: create_narratives
      description: Create Narrative nodes
      file: ingest/create.py
      function: create_narratives()
      input: List[ParsedDoc]
      output: List[narrative_id]
      side_effects: engine.create_narrative(), engine.create_link() calls

    - id: create_things
      description: Create Thing nodes for files
      file: ingest/create.py
      function: create_things()
      input: List[FilePath]
      output: List[thing_id]
      side_effects: engine.create_thing() calls

    - id: create_actors
      description: Create Actor nodes
      file: ingest/create.py
      function: create_actors()
      input: AgentConfig
      output: List[actor_id]
      side_effects: engine.create_actor() calls

  docking_points:
    available:
      - id: dock_ingest_start
        type: event
        direction: input
        payload: {repo_path, config}

      - id: dock_files_discovered
        type: event
        direction: output
        payload: List[FilePath]
        notes: Count of files found

      - id: dock_narratives_created
        type: event
        direction: output
        payload: {count, types}
        notes: Summary of what was created

      - id: dock_ingest_complete
        type: event
        direction: output
        payload: {spaces, narratives, things, actors, links}
        notes: Full ingest summary

    health_recommended:
      - dock_id: dock_ingest_complete
        reason: Verify ingest created expected nodes
```

---

### Flow 2: Agent Trigger

Engine triggers us when agent should work.

```yaml
flow:
  name: agent_trigger
  purpose: Handle agent activation, produce work
  scope:
    input: trigger from engine
    output: moments/narratives created
  steps:
    - id: receive_trigger
      description: Engine calls our handler
      file: agents/handler.py
      function: on_agent_trigger()
      input: agent_id, moment, context
      output: None (processing starts)

    - id: build_prompt
      description: Assemble system prompt from context
      file: agents/prompts.py
      function: build_system_prompt()
      input: context, agent_config
      output: system_prompt string

    - id: format_opening
      description: Format the triggering moment
      file: agents/prompts.py
      function: format_opening()
      input: moment
      output: opening string

    - id: call_llm
      description: Get agent response
      file: agents/handler.py
      function: call_llm()
      input: system_prompt, opening
      output: response string
      side_effects: LLM API call

    - id: parse_response
      description: Extract moments/narratives from response
      file: agents/response.py
      function: parse_response()
      input: response string
      output: {moments, narratives}

    - id: create_content
      description: Create nodes via engine
      file: agents/handler.py
      function: create_content()
      input: {moments, narratives}
      output: {moment_ids, narrative_ids}
      side_effects: engine.create_moment(), engine.create_narrative()

    - id: complete
      description: Signal completion to engine
      file: agents/handler.py
      function: complete()
      input: moment_id
      output: None
      side_effects: engine.complete_moment()

  docking_points:
    available:
      - id: dock_trigger_received
        type: event
        direction: input
        payload: {agent_id, moment, context}

      - id: dock_prompt_built
        type: event
        direction: output
        payload: {prompt_length, context_size}

      - id: dock_llm_response
        type: event
        direction: output
        payload: {response_length, latency_ms}

      - id: dock_content_created
        type: event
        direction: output
        payload: {moments_count, narratives_count}

    health_recommended:
      - dock_id: dock_llm_response
        reason: Track LLM latency and response quality
      - dock_id: dock_content_created
        reason: Verify agents produce output
```

---

### Flow 3: Content Creation

Actor (human or agent) creates moment/narrative.

```yaml
flow:
  name: content_creation
  purpose: Record actor thinking as graph nodes
  scope:
    input: actor action
    output: node in graph
  steps:
    - id: infer_type
      description: Determine moment/narrative type
      file: content/inference.py
      function: infer_moment_type() or infer_narrative_type()
      input: content string
      output: type string

    - id: call_engine
      description: Create node via engine API
      file: content/moment.py or content/narrative.py
      function: create_moment() or create_narrative()
      input: actor_id, content, type, touched_ids
      output: node_id
      side_effects: engine.create_*()

  docking_points:
    available:
      - id: dock_content_inferred
        type: event
        direction: output
        payload: {content_preview, inferred_type}

      - id: dock_node_created
        type: event
        direction: output
        payload: {node_id, node_type}
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
building/
├── ingest/
│   └── imports → config/mapping
├── agents/
│   ├── imports → config/agents
│   ├── imports → context/
│   └── imports → content/
├── content/
│   └── imports → (none internal)
└── context/
    └── imports → (none internal)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `engine` | Graph operations | `ingest/create.py`, `content/*.py` |
| `pyyaml` | Config loading | `config/*.py` |
| `anthropic` or `openai` | LLM calls | `agents/handler.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Ingest config | `config/mapping.py` | Module | Loaded once at startup |
| Agent configs | `config/agents.py` | Module | Loaded once at startup |
| Current context | Function local | Request | Per trigger |

No persistent state in our code. Engine owns all graph state.

---

## RUNTIME BEHAVIOR

### Initialization (Bootstrap)

```
1. Load configs (mapping.yaml, agents.yaml)
2. Run ingest on repo
3. Register on_agent_trigger with engine
4. Ready
```

### Main Loop

We don't have a main loop. Engine runs the world.

```
Engine ticks
  → Engine detects activation
    → Engine calls on_agent_trigger()
      → We handle, create content
        → Engine records, flows energy
```

### Shutdown

```
1. Unregister trigger handler
2. Done (no cleanup needed, engine owns state)
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `mapping_path` | env/cli | `repo_to_graph_mapping.yaml` | Ingest patterns |
| `agents_path` | env/cli | `agents.yaml` | Agent definitions |
| `llm_model` | env | `claude-3-sonnet` | Model for agents |
| `max_context_narratives` | mapping.yaml | 20 | Context size limit |

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM 1: Ingest | `ingest/*.py` |
| ALGORITHM 2: Context Query | `context/query.py` |
| ALGORITHM 3: Agent Handler | `agents/handler.py` |
| ALGORITHM 4: Content Creation | `content/*.py` |
| VALIDATION V-MIND-INGEST-* | `tests/building/test_ingest.py` |
| VALIDATION V-MIND-AGENT-* | `tests/building/test_agents.py` |

---

## OPEN QUESTIONS

<!-- @mind:escalation How do we register on_agent_trigger with engine? Callback registration API? -->

<!-- @mind:escalation What's the engine.get_context() signature? Do we pass thresholds or engine owns them? -->

<!-- @mind:escalation How do we handle agent failure? Retry? Mark moment as failed? -->

<!-- @mind:escalation Response parsing: structured output from LLM? Or parse freeform text? -->

<!-- @mind:proposition Consider making ingest incremental (watch for file changes) -->

<!-- @mind:proposition Consider caching parsed configs to avoid reload -->

<!-- @mind:escalation [D6] Module Naming Dispatcher — how do we map file paths to module Spaces?
  Options:
    A) Explicit mapping.yaml with glob patterns per Space
    B) Directory conventions (each dir = Space)
    C) LLM inference from file content
    D) Filename patterns (PATTERNS_*.md → patterns Space)
  Opinion: (A) mapping.yaml with globs. Explicit is debuggable. (B) creates too many Spaces. (C) is expensive and unpredictable. (D) is too rigid. Glob patterns give control: "docs/building/**" → building Space. Fallback: files not matching any pattern go to root Space. Config over convention here.
  Phase: 1 -->

<!-- @mind:escalation [Q7] Incremental Ingest — how to handle docs created/modified after bootstrap?
  Options:
    A) Manual re-ingest command (mind ingest --incremental)
    B) File watcher daemon
    C) Git hook on commit
    D) Periodic cron job
  Opinion: (A) Manual first. File watchers are complex (debouncing, ignore patterns, daemon management). Git hooks miss non-committed changes. Cron is wasteful. Start with explicit command. Add file watcher in Phase 4 when we understand ingest patterns better. Manual ingest also forces intentionality.
  Phase: 4 -->

---

## MARKERS

<!-- @mind:todo Implement ingest/discover.py -->
<!-- @mind:todo Implement ingest/parse.py -->
<!-- @mind:todo Implement agents/handler.py -->
<!-- @mind:todo Define agents.yaml schema -->
<!-- @mind:todo Write tests for type inference -->
