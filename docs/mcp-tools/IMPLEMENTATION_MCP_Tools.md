# IMPLEMENTATION: MCP Tools

```
STATUS: V2
PURPOSE: Code architecture for MCP tools
```

---

## Code Structure

```
mcp/
├── server.py                  # MindServer - MCP JSON-RPC handler

runtime/
├── physics/
│   ├── exploration.py         # run_exploration() - SubEntity orchestration
│   ├── subentity.py           # SubEntity class - graph cursor
│   ├── cluster_presentation.py # render_cluster() - format results
│   └── graph/
│       ├── graph_ops.py       # GraphOps - node/link mutations
│       └── graph_queries.py   # GraphQueries - embedding search
│
├── connectome/
│   ├── runner.py              # ConnectomeRunner - procedure execution
│   ├── session.py             # Session state management
│   ├── loader.py              # YAML procedure loading
│   ├── steps.py               # Step handlers (ask, create, branch)
│   └── validation.py          # Answer validation
│
└── infrastructure/
    └── database/
        ├── factory.py         # get_database_adapter()
        └── falkordb_adapter.py # FalkorDB implementation

.mind/procedures/              # Procedure YAML files
├── create_doc_chain.yaml
├── add_patterns.yaml
├── add_behaviors.yaml
├── investigate.yaml
└── ...
```

---

## Key Components

### MCP Server (`mcp/server.py`)

| Component | Purpose |
|-----------|---------|
| `MindServer` | JSON-RPC handler, routes tool calls |
| `_tool_graph_query()` | Handles graph_query → SubEntity exploration |
| `_tool_procedure_*()` | Procedure start/continue/abort handlers |
| `_tool_agent_*()` | Agent list/spawn/status handlers |
| `_tool_doctor_check()` | Health check handler |

**Tool Schema:**

```python
"graph_query": {
    "queries": ["string array"],   # WHAT to search
    "intent": "string"             # WHY searching (optional)
}
```

### SubEntity Exploration (`runtime/physics/exploration.py`)

| Function | Purpose |
|----------|---------|
| `run_exploration()` | Entry point - creates SubEntities, runs traversal |
| `ExplorationResult` | Container for found narratives, crystallized ID |

**Flow:**
```
run_exploration(queries, intent, actor_id)
  → create origin moment
  → create SubEntity per query
  → subentity.seek() until satisfied or max steps
  → crystallize if novelty high + satisfaction low
  → return ExplorationResult
```

### SubEntity (`runtime/physics/subentity.py`)

| Method | Purpose |
|--------|---------|
| `seek()` | Move to best adjacent node |
| `_score_link()` | Calculate link attractiveness |
| `_update_satisfaction()` | Track progress toward query |

**Link Scoring:**
```
score = alignment × polarity × (1-permanence) × novelty × divergence
```

### Procedure Runner (`runtime/connectome/runner.py`)

| Method | Purpose |
|--------|---------|
| `start(procedure)` | Load YAML, create session, return first step |
| `continue_session(answer)` | Validate, advance, return next step |
| `abort()` | Clean up session, commit nothing |

### Graph Operations (`runtime/physics/graph/`)

| Class | Purpose |
|-------|---------|
| `GraphOps` | Mutations: create_node, create_link, update_node |
| `GraphQueries` | Reads: embedding_search, find_by_id |

---

## Data Flow

### graph_query

```
MCP Client
    │
    │ graph_query(queries=["..."], intent="...")
    ▼
mcp/server.py
    │
    │ _tool_graph_query()
    │   → get actor_id from session
    │   → create query moment
    ▼
runtime/physics/exploration.py
    │
    │ run_exploration(queries, intent, actor_id)
    │   → spawn SubEntity per query
    ▼
runtime/physics/subentity.py
    │
    │ subentity.seek()
    │   → score adjacent links
    │   → move to best candidate
    │   → update satisfaction
    │   → repeat until done
    ▼
runtime/physics/exploration.py
    │
    │ crystallize if needed
    │   → create narrative node
    ▼
mcp/server.py
    │
    │ format response
    │   → fetch narrative content
    │   → return best match
    ▼
MCP Client
```

### procedure_start/continue

```
MCP Client
    │
    │ procedure_start(procedure="create_doc_chain")
    ▼
mcp/server.py
    │
    │ _tool_procedure_start()
    ▼
runtime/connectome/runner.py
    │
    │ runner.start(procedure_name)
    │   → load YAML from .mind/procedures/
    │   → create session with unique ID
    │   → return first step
    ▼
MCP Client
    │
    │ procedure_continue(session_id, answer)
    ▼
runtime/connectome/runner.py
    │
    │ runner.continue_session(session_id, answer)
    │   → validate answer
    │   → store in session
    │   → advance to next step
    │   → on final step: commit nodes/links
    ▼
MCP Client
```

---

## Configuration

### MCP Server (`.mcp.json`)

```json
{
  "mcpServers": {
    "mind": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/mind-mcp"
    }
  }
}
```

### Database (`.mind/database_config.yaml`)

```yaml
adapter: falkordb
host: localhost
port: 6379
graph_name: mind
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MIND_FALKORDB_HOST` | Database host | localhost |
| `MIND_FALKORDB_PORT` | Database port | 6379 |
| `MIND_GRAPH_NAME` | Graph name | mind |

---

## Extension Points

| Extension | Location | How |
|-----------|----------|-----|
| New MCP tool | `mcp/server.py` | Add `_tool_X()` method + schema |
| New procedure | `.mind/procedures/` | Create YAML file |
| New step type | `runtime/connectome/steps.py` | Add handler |
| New validator | `runtime/connectome/validation.py` | Add function |
| New exploration behavior | `runtime/physics/subentity.py` | Modify seek() |

---

## Tests

```bash
# Run exploration tests
pytest tests/ -v -k exploration

# Run MCP server tests
pytest tests/ -v -k server

# Run procedure tests
pytest tests/ -v -k procedure
```

---

## CHAIN

- **Prev:** VALIDATION_MCP_Tools.md
- **Next:** SYNC_MCP_Tools.md
- **Patterns:** PATTERNS_MCP_Tools.md
- **Algorithm:** ALGORITHM_MCP_Tools.md
