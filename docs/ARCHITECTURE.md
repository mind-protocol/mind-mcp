# mind-mcp Architecture

## Layer Position: L1 (Citizen)

mind-mcp is the **L1 client layer** of the Mind Protocol. It runs locally on user devices and connects to L4 for synchronization.

```
┌─────────────────────────────────────────────────────────────┐
│ L4: Protocol (mind-protocol)                                │
│     Registry, Economy, Validation, Broadcast                │
│                         ▲                                   │
│                         │ WebSocket push                    │
│                         │ (no polling)                      │
├─────────────────────────┼───────────────────────────────────┤
│ L3: Ecosystem (mind-platform)                               │
│     Templates, Organizations, Public Graph                  │
├─────────────────────────┼───────────────────────────────────┤
│ L2: Organization        │                                   │
│     Multi-user coordination                                 │
├─────────────────────────┼───────────────────────────────────┤
│ L1: Citizen (mind-mcp) ◄┘                                   │
│     Local graph, Physics engine, MCP server                 │
└─────────────────────────────────────────────────────────────┘
```

## Core Responsibilities

### 1. Local Graph Database
- Stores user's personal knowledge graph
- Neo4j or FalkorDB backend
- Embeddings for semantic search

### 2. Physics Engine
- Energy-based traversal
- Stimulus cascade (no ticks)
- Membrane graph navigation

### 3. MCP Server
- Exposes tools to AI agents (Claude, etc.)
- graph_query, procedure_start, agent_spawn
- Structured dialogue via membranes

### 4. CLI
- `mind init` - Initialize .mind/ in any project
- `mind status` - Show connection status

## Key Design Decisions

### No Ticks - Pure Stimulus
The engine doesn't poll or tick. Stimuli cascade through the membrane graph. When a stimulus arrives, it propagates until energy dissipates.

### Membrane = Graph
The membrane is not a list of direct connections. It's a graph structure that enables broadcast patterns and weighted routing.

### L4 Push Only
L1 doesn't poll L4. L4 pushes updates via WebSocket. This means L1 needs network connectivity to stay in sync.

### No Offline Mode (v1)
Currently requires L4 connection. Offline queue is a future enhancement.

## Module Structure

```
mind/
├── physics/           # Energy mechanics, traversal
│   ├── graph/         # Neo4j operations
│   ├── tick_v1_2.py   # Stimulus processing
│   └── flow.py        # Energy flow
├── models/            # Node/Link pydantic models
├── infrastructure/    # DB adapters, embeddings, API
│   ├── database/      # DatabaseAdapter pattern
│   └── embeddings/    # OpenAI embedding service
└── connectome/        # Session management

cli/                   # CLI entry point
mcp/                   # MCP server for AI agents
templates/             # .mind/ initialization templates
```

## Data Flow

```
User/Agent Action
       │
       ▼
  MCP Server (mcp/server.py)
       │
       ▼
  Physics Engine (runtime/physics/)
       │
       ├──► Graph Queries (read)
       │
       └──► Graph Ops (write)
              │
              ▼
         Neo4j/FalkorDB
              │
              ▼
      Stimulus Cascade
              │
              ▼
     WebSocket to L4 (future)
```

## Related Repos

| Repo | Layer | Purpose |
|------|-------|---------|
| mind-mcp | L1 | This repo - client engine |
| mind-protocol | L4 | Protocol law, registry, economy |
| mind-platform | L3 | Frontend, templates, ecosystem |
| mind-ops | - | Private infrastructure, billing |
