# IMPLEMENTATION: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Code architecture for structured graph dialogues
```

<!-- @mind:escalation Skills referenced in `templates/mind/skills/` may not exist - needs verification. -->

---

## Code Structure

```
mcp/
├── __init__.py
├── server.py                   # MCP server exposing tools (MindServer class)
├── sync_wrapper.py             # Sync wrapper utilities
└── tools/
    └── __init__.py

runtime/connectome/                # ConnectomeRunner (membrane executor)
├── __init__.py                 # Exports ConnectomeRunner
├── runner.py                   # ConnectomeRunner - protocol execution
├── session.py                  # Session state management + call stack
├── loader.py                   # YAML protocol loading
├── steps.py                    # Step execution (ask, query, branch, call_protocol, create)
├── validation.py               # Answer validation
├── templates.py                # Interpolation and templating
├── schema.py                   # Node/link schema validation
└── persistence.py              # Graph persistence layer

runtime/membrane/                  # Membrane integration layer
├── __init__.py
├── integrator.py               # Membrane-graph integrator
├── client.py                   # Membrane client
├── stimulus.py                 # Stimulus handling
└── broadcast.py                # Broadcast utilities

mind/
├── procedure_runner.py         # ProtocolRunner for procedure execution
└── doctor_checks_membrane.py   # Membrane health checks

procedures/                     # Protocol YAML files (24 protocols)
├── add_algorithm.yaml
├── add_behaviors.yaml
├── add_cluster.yaml
├── add_goals.yaml
├── add_health_coverage.yaml
├── add_implementation.yaml
├── add_invariant.yaml
├── add_objectives.yaml
├── add_patterns.yaml
├── add_todo.yaml
├── assess_exploration.yaml
├── capture_decision.yaml
├── completion_handoff.yaml
├── create_doc_chain.yaml
├── define_space.yaml
├── explore_space.yaml
├── ingest_docs.yaml
├── investigate.yaml
├── link_nature_vocab.yaml
├── raise_escalation.yaml
├── record_work.yaml
├── resolve_blocker.yaml
└── update_sync.yaml

templates/mind/skills/          # Skill markdown files (domain knowledge)
└── @mind:escalation - Skills referenced but may not exist
```

---

## Key Components

### MCP Server (`mcp/server.py`)

| Class | Purpose | Dock |
|-------|---------|------|
| `MindServer` | JSON-RPC handler for MCP protocol | Line 68 |
| `_handle_call_tool` | Routes tool calls to implementations | Line 337 |
| `_format_response` | Formats runner response for MCP | Line 990 |

**Tools exposed:**
- `procedure_start` -> `runner.start(protocol_name)` - Start dialogue session
- `procedure_continue` -> `runner.continue_session()` - Continue with answer
- `procedure_abort` -> `runner.abort()` - Abort session
- `procedure_list` -> lists protocol YAML files
- `doctor_check` -> Run health checks (integrated with agent system)
- `agent_list` -> List work agents and their status
- `agent_spawn` -> Spawn a work agent for issue/task
- `agent_status` -> Get/set agent status
- `task_list` -> List available tasks from graph
- `graph_query` -> Query graph using natural language (SubEntity exploration)

<!-- @mind:proposition The following tools exist in code but are not fully documented in behaviors:
     - doctor_check, agent_list, agent_spawn, agent_status, task_list, graph_query
     These represent agent orchestration capabilities that extend beyond the core membrane/protocol pattern. -->

### Skill Loading (Doctor responsibility)

Skills are markdown files loaded into agent context before protocol execution:

```python
def load_skill(domain: str) -> str:
    """Load skill markdown for domain knowledge."""
    path = skills_dir / f"{domain}.md"
    return path.read_text()

# Doctor loads skill, provides to agent
skill_content = load_skill("health_coverage")
# Agent has skill knowledge when answering protocol questions
```

### Runner (`runtime/connectome/runner.py`)

| Class | Purpose | Dock |
|-------|---------|------|
| `ConnectomeRunner` | Protocol executor (the membrane) | Class definition |
| `start()` | Creates session, loads protocol, returns first step | Method |
| `continue_session()` | Validates answer, advances step, handles branching | Method |
| `abort()` | Cleans up session | Method |

### Session (`runtime/connectome/session.py`)

| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | str | Unique identifier |
| `protocol_name` | str | Which protocol is running |
| `current_step` | str | Current step ID |
| `answers` | Dict | Step ID → answer mapping |
| `context` | Dict | Interpolation context |
| `call_stack` | List | Stack for sub-protocol calls |
| `created_nodes` | List | Nodes to commit |
| `created_links` | List | Links to commit |

### Steps (`runtime/connectome/steps.py`)

| Step Type | Handler | Output |
|-----------|---------|--------|
| `ask` | Returns question + expects to agent | `{status: 'active', step: {...}}` |
| `query` | Executes graph query, stores result | Advances to next step |
| `branch` | Evaluates condition, routes to then/else/cases | Advances to selected step |
| `call_protocol` | Pushes stack, starts sub-protocol | Executes sub-protocol |
| `create` | Instantiates nodes/links from spec | `{status: 'complete', created: {...}}` |
| `update` | Modifies existing node | Advances to next step |

### Validation (`runtime/connectome/validation.py`)

| Validator | Checks |
|-----------|--------|
| `validate_string` | min_length, pattern |
| `validate_id` | node exists, type matches |
| `validate_id_list` | each ID valid, min/max count |
| `validate_string_list` | list format, min/max count |
| `validate_enum` | value in options |

### Templates (`runtime/connectome/templates.py`)

| Function | Purpose |
|----------|---------|
| `interpolate()` | `{variable}` → value from context |
| `slugify()` | text → url-safe-slug |
| `truncate()` | text → max N chars |
| `timestamp()` | → current ISO timestamp |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP CLIENT                                │
│  (Claude Code, agent)                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ JSON-RPC over stdio
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     mcp/server.py                                │
│  MindServer.handle_request() → routes to tool handlers          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ runner.start() / runner.continue_session()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  runtime/connectome/runner.py                       │
│  ConnectomeRunner manages session lifecycle                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│ runtime/connectome/         │     │  runtime/connectome/loader.py       │
│ session.py               │     │  Load YAML → membrane dict       │
└─────────────────────────┘     └─────────────────────────────────┘
                              │
                              │ execute step
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  runtime/connectome/steps.py                        │
│  ask → return question                                          │
│  query → call graph, store result                               │
│  create → instantiate nodes/links                               │
│  update → modify existing node                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│ runtime/connectome/         │     │ runtime/connectome/templates.py     │
│ validation.py            │     │  Interpolate {vars} in specs    │
└─────────────────────────┘     └─────────────────────────────────┘
                              │
                              │ graph operations
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     runtime/physics/graph/                          │
│  GraphOps.create_node(), create_link()                          │
│  GraphQueries.find(), related_to()                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### MCP Server Config (`.mcp.json`)

```json
{
  "mcpServers": {
    "mind": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "/path/to/mind-mcp"
    }
  }
}
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MIND_FALKORDB_HOST` | Graph database host | localhost |
| `MIND_FALKORDB_PORT` | Graph database port | 6379 |

---

## Membrane YAML Location

<!-- @mind:escalation The procedures/ directory does not currently exist in the codebase.
     The documented protocols (20 protocols) are not present. This is a significant gap. -->

Membrane definitions should live in:
```
procedures/
├── explore_space.yaml
├── add_objectives.yaml
├── add_invariant.yaml
└── ...
```

**Current status:** The `procedures/` directory does not exist. The ConnectomeRunner looks for
YAML files in `procedures/` but this directory needs to be created with protocol definitions.

---

## Protocol YAML

<!-- @mind:escalation Protocol YAML definitions are referenced throughout docs but don't exist.
     This represents the gap between spec and implementation. -->

Protocols should live in `procedures/`:
```
procedures/
├── explore_space.yaml
├── record_work.yaml
├── investigate.yaml
├── add_objectives.yaml
├── add_patterns.yaml
├── add_behaviors.yaml
├── add_algorithm.yaml
├── add_implementation.yaml
├── update_sync.yaml
├── add_invariant.yaml
├── add_health_coverage.yaml
├── raise_escalation.yaml
├── resolve_blocker.yaml
├── capture_decision.yaml
├── add_goals.yaml
├── add_todo.yaml
├── define_space.yaml
├── create_doc_chain.yaml
├── add_cluster.yaml
└── completion_handoff.yaml
```

Doctor integration expects `DoctorIssue.protocol` field to trigger auto-fix via membrane.

---

## Extension Points

| Extension | Where | How |
|-----------|-------|-----|
| Add new membrane | `procedures/` | Create YAML file |
| Add new step type | `runtime/connectome/steps.py` | Add handler function |
| Add new validator | `runtime/connectome/validation.py` | Add validation function |
| Add new template filter | `runtime/connectome/templates.py` | Add filter function |
| Add graph operations | `runtime/physics/graph/` | Add to GraphOps/GraphQueries |
| Add new MCP tool | `mcp/server.py` | Add handler in MindServer._handle_call_tool |

---

## Tests

<!-- @mind:escalation Test files referenced may not exist. Need to verify tests/connectome_v0/ location. -->

```bash
# Run connectome tests (if they exist)
pytest tests/ -v -k connectome

# Run MCP server tests
pytest tests/ -v -k mcp
```

| Test File | Coverage |
|-----------|----------|
| `test_loader.py` | YAML loading, schema validation |
| `test_session.py` | Session lifecycle |
| `test_validation.py` | All answer types |
| `test_steps.py` | Step execution |
| `test_runner.py` | End-to-end flows |

---

## CHAIN

- **Prev:** VALIDATION_MCP_Tools.md
- **Next:** SYNC_MCP_Tools.md
- **Patterns:** PATTERNS_MCP_Tools.md
- **Algorithm:** ALGORITHM_MCP_Tools.md
