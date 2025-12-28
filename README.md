# mind-mcp

Mind Protocol MCP server and runtime for AI agents. Graph physics, traversal, structured dialogues.

## Quick Start

```bash
# Clone and install
git clone https://github.com/mind-protocol/mind-mcp.git
cd mind-mcp
pip install -e .

# Initialize a project (defaults to FalkorDB)
mind init
```

This creates `.mind/` with:
- Protocol docs (PRINCIPLES.md, FRAMEWORK.md)
- Agent definitions, skills, procedures
- Python runtime for physics, graph, traversal
- Database config (graph name defaults to repo name)

## Local Runtime

After `mind init`, projects can run mind locally without pip install:

```bash
PYTHONPATH=".mind:$PYTHONPATH" python3 my_script.py
```

```python
# my_script.py
from mind.physics.constants import DECAY_RATE
from mind.connectome import ConnectomeRunner
from mind.infrastructure.database.factory import get_database_adapter

adapter = get_database_adapter()
```

## CLI Commands

```bash
mind init [--database falkordb|neo4j]  # Initialize .mind/ with runtime
mind status                             # Show status and modules
mind upgrade                            # Check for updates
```

## Database Backends

Graph name defaults to repo name (e.g., `my-project` → `my_project`).

### FalkorDB (default, local)

```bash
mind init

# Start FalkorDB
docker run -p 6379:6379 falkordb/falkordb
```

Override graph name in `.env`:
```bash
FALKORDB_GRAPH=custom_name
```

### Neo4j (cloud or local)

```bash
mind init --database neo4j
```

Configure in `.env`:
```bash
DATABASE_BACKEND=neo4j
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

See `.env.mind.example` for all options.

## MCP Server

### Claude Code

Add to `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "mind": {
      "command": "python3",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/mind-mcp"
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `graph_query` | Semantic search across the graph |
| `membrane_start` | Start a structured dialogue |
| `membrane_continue` | Continue dialogue with answer |
| `membrane_list` | List available dialogues |
| `doctor_check` | Run health checks |
| `agent_list` | List work agents |
| `agent_spawn` | Spawn a work agent |
| `task_list` | List pending tasks |

## Project Structure

```
.mind/
├── PRINCIPLES.md          # How to work
├── FRAMEWORK.md           # Navigation guide
├── config.yaml            # Mind config
├── database_config.yaml   # Database settings
├── agents/                # Agent postures
├── skills/                # Executable capabilities
├── procedures/            # Structured dialogues
├── state/                 # SYNC files
└── mind/                  # Python runtime
    ├── physics/           # Graph physics
    ├── graph/             # Graph operations
    ├── connectome/        # Dialogue runner
    ├── infrastructure/    # DB adapters
    └── traversal/         # Traversal logic
```

## Requirements

- Python 3.10+
- Neo4j or FalkorDB
- Optional: OpenAI API key (for embeddings)

## License

MIT
