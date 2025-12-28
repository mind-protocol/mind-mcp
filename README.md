# mind-mcp

MIND Engine — Graph physics, traversal, membrane client for AI agents.

## Installation

```bash
pip install mind-mcp
```

Or from source:

```bash
git clone https://github.com/mind-protocol/mind-mcp.git
cd mind-mcp
pip install -e .
```

## MCP Server Setup

### Claude Code

Add to `~/.claude/settings.json`:

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

Or per-project in `.mcp.json`:

```json
{
  "mcpServers": {
    "mind": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "."
    }
  }
}
```

### Cursor / VS Code

Add to settings:

```json
{
  "mcp.servers": {
    "mind": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/mind-mcp"
    }
  }
}
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `graph_query` | Query the graph in natural language |
| `membrane_start` | Start a structured dialogue session |
| `membrane_continue` | Continue with an answer |
| `membrane_list` | List available membranes |
| `doctor_check` | Run health checks |
| `agent_list` | List work agents |
| `agent_spawn` | Spawn a work agent |
| `task_list` | List available tasks |

### Example: Query the Graph

```
graph_query(queries: ["What characters exist?"], top_k: 5)
```

### Example: Start a Membrane

```
membrane_start(membrane: "create_doc_chain")
membrane_continue(session_id: "...", answer: "physics")
```

## CLI

```bash
python -m cli init          # Initialize .mind/ in current directory
python -m cli status        # Show status
```

## Python API

```python
from mind import get_graph_ops, get_graph_queries

# Connect to graph
ops = get_graph_ops("my_graph")
queries = get_graph_queries("my_graph")

# Query nodes
results = queries.search_by_embedding("consciousness", top_k=5)
```

## Requirements

- Python 3.10+
- Neo4j (local or Aura)
- OpenAI API key (for embeddings)

## Environment Variables

```bash
# Neo4j connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Or Neo4j Aura
NEO4J_AURA_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_AURA_USER=neo4j
NEO4J_AURA_PASSWORD=xxx

# Embeddings
OPENAI_API_KEY=sk-xxx
```

## License

MIT
