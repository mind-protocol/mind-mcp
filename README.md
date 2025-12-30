# mind-mcp

Mind Protocol MCP server and runtime for AI agents. Graph physics, traversal, structured dialogues.

[![PyPI](https://img.shields.io/pypi/v/mind-mcp)](https://pypi.org/project/mind-mcp/)

## Install

```bash
pip install mind-mcp
```

Or from source:
```bash
git clone https://github.com/mind-protocol/mind-mcp.git
cd mind-mcp
pip install -e .
```

## Quick Start

```bash
# Initialize a project
mind init

# Start FalkorDB (default backend)
docker run -p 6379:6379 falkordb/falkordb
```

Creates `.mind/` with:
- Protocol docs (PRINCIPLES.md, FRAMEWORK.md)
- Agent definitions in `.mind/actors/{name}/CLAUDE.md`
- Skills, procedures, state tracking
- Python runtime for physics, graph, traversal

## Agents

Agents are discovered dynamically from `.mind/actors/{name}/CLAUDE.md`.

Selection uses graph physics: `score = similarity * weight * energy`

## ID Convention

All IDs follow `{TYPE}_{Name}` pattern:
- `AGENT_Witness`, `AGENT_Fixer`
- `TASK_FixAuth_a7b3`
- `MOMENT_Assignment_witness_c4d2`

## MCP Server

Add to `.mcp.json`:

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

### Tools

| Tool | Description |
|------|-------------|
| `graph_query` | Semantic search across the graph |
| `procedure_start` | Start a structured dialogue |
| `procedure_continue` | Continue dialogue with answer |
| `procedure_list` | List available dialogues |
| `doctor_check` | Run health checks |
| `agent_list` | List work agents |
| `agent_spawn` | Spawn agent for task |
| `agent_status` | Get/set agent status |
| `task_list` | List pending tasks |
| `task_claim` | Claim a task for an agent |
| `task_complete` | Mark task completed |
| `task_fail` | Mark task failed |

## CLI

```bash
mind init [--database falkordb|neo4j]  # Initialize .mind/
mind status                             # Show status
mind doctor                             # Health checks
mind work [path]                        # AI-assisted work
```

## Database Backends

### FalkorDB (default)

```bash
docker run -p 6379:6379 falkordb/falkordb
```

### Neo4j

```bash
mind init --database neo4j
```

Configure in `.env`:
```bash
DATABASE_BACKEND=neo4j
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Project Structure

```
.mind/
├── PRINCIPLES.md          # How to work
├── FRAMEWORK.md           # Navigation guide
├── actors/                # Agent prompts
│   ├── witness/CLAUDE.md
│   ├── fixer/CLAUDE.md
│   └── ...
├── skills/                # Executable capabilities
├── procedures/            # Structured dialogues
└── state/                 # SYNC files
```

## Requirements

- Python 3.10+
- FalkorDB or Neo4j
- Optional: OpenAI API key (embeddings)

## License

MIT
