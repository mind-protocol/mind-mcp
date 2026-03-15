# MCP Tools — Patterns: Cognitive Membrane Design

```
STATUS: STABLE
CREATED: 2025-12-24
VERIFIED: 2026-03-15 against bdaf2d0
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
THIS:            PATTERNS_MCP_Tools.md (you are here)
BEHAVIORS:       ./BEHAVIORS_MCP_Tools.md
ALGORITHM:       ./ALGORITHM_MCP_Tools.md
VALIDATION:      ./VALIDATION_MCP_Tools.md
HEALTH:          ./HEALTH_MCP_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            mcp/server.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read mcp/server.py and mcp/tools/*_handler.py

**After modifying this doc:**
1. Update IMPLEMENTATION or add TODO in SYNC

**After modifying the code:**
1. Update this doc chain to match

---

## THE PROBLEM

AI citizens need a coherent interface to interact with their living graph (L1 brain), shared universe (L3), other citizens, and external platforms. Without a structured tool layer, citizens would need raw Cypher, direct API calls, and platform-specific code — fragmenting cognition across ad-hoc implementations.

---

## THE PATTERN

**The Cognitive Membrane** — a single MCP server exposes 15 tools organized by cognitive function:

- **THINK** (4 tools): query the graph, create nodes, run structured dialogues, consult Gemini
- **ACT** (8 tools): manage tasks, set alarms, inhabit places, call citizens, spawn new citizens, update profile, debug
- **SPEAK** (3 tools): send messages, read messages, generate media

Each tool is a self-contained handler (`mcp/tools/{name}_handler.py`) that receives arguments and an optional `ServerContext` (graph connections, runner, capabilities). Tools return `{"content": [{"type": "text", "text": "..."}]}`.

The key insight: tools don't call each other. Complex workflows emerge from citizens combining atomic tools, or from structured procedures that guide multi-step creation.

---

## BEHAVIORS SUPPORTED

- B-QUERY: Semantic graph search via SubEntity traversal
- B-CALL: Instant citizen-to-citizen communication with subconscious fallback
- B-SUBCALL: Zero-LLM graph telepathy across citizens
- B-SPAWN: Full citizen birth pipeline (identity → brain → wallet → L4)
- B-PLACE: E2E encrypted living spaces with presence

## BEHAVIORS PREVENTED

- Direct Cypher injection (all graph access through typed operations)
- Silent failures (all tools return explicit errors)
- Cross-tool coupling (each handler is independent)

---

## PRINCIPLES

### Principle 1: Stateless Handlers

Each tool handler is stateless — it takes arguments, does its work, returns a result. The only shared state is the `ServerContext` (graph connections). Exception: `think_handler` maintains Gemini conversation sessions in memory (TTL 2h).

### Principle 2: Lazy Dependencies

All platform bridges (Discord, Twitter, WhatsApp, etc.) and optional libraries (crypto, websockets) are lazy-imported at call time. This means the MCP server starts fast and doesn't crash if optional deps are missing — it returns clear errors instead.

### Principle 3: Graph Physics First

Tools that need intelligence (graph_query, subcall, call) use graph physics (energy propagation, embedding similarity, limbic resonance) before reaching for an LLM. The subconscious response path is the flagship example: pure graph → narrated response → no tokens spent.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/graph/` | GraphOps + GraphQueries for all graph operations |
| `runtime/connectome/` | ConnectomeRunner for structured procedures |
| `runtime/identity.py` | Citizen ID resolution (env, cwd, config) |
| `runtime/infrastructure/embeddings/` | Embedding service for semantic search |
| `runtime/orchestrator/` | Dispatcher, subconscious invocation |

---

## SCOPE

### In Scope

- 15 MCP tools (THINK/ACT/SPEAK)
- JSON-RPC stdio transport
- ServerContext dependency injection
- Tool schema definitions and dispatch

### Out of Scope

- HTTP API (that's home_server.py) → see: home_server
- L1 cognitive engine (tick runner) → see: docs/l1_wiring/
- L4 registry operations → see: runtime/l4/
- Platform bridge implementations → see: runtime/bridges/
