# MCP Tools — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2025-12-24
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
BEHAVIORS:       ./BEHAVIORS_MCP_Tools.md
PATTERNS:        ./PATTERNS_MCP_Tools.md
ALGORITHM:       ./ALGORITHM_MCP_Tools.md
VALIDATION:      ./VALIDATION_MCP_Tools.md
THIS:            IMPLEMENTATION_MCP_Tools.md (you are here)
HEALTH:          ./HEALTH_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            mcp/server.py, mcp/tools/*_handler.py, home_server.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mcp/
├── server.py                         # MindServer — JSON-RPC dispatch, startup
└── tools/
    ├── context.py                    # ServerContext dataclass (shared deps)
    ├── graph_query_handler.py        # [THINK] Semantic search via SubEntity
    ├── graph_write_handler.py        # [THINK] Create nodes and links
    ├── procedure_handler.py          # [THINK] Structured dialogues
    ├── think_handler.py              # [THINK] Gemini consultation
    ├── task_handler.py               # [ACT]   Task lifecycle
    ├── alarm_handler.py              # [ACT]   Wake scheduling
    ├── place_handler.py              # [ACT]   Living places + encryption
    ├── call_handler.py               # [ACT]   Citizen-to-citizen calls
    ├── subcall_handler.py            # [ACT]   Zero-LLM telepathy
    ├── spawn_handler.py              # [ACT]   Citizen birth
    ├── profile_handler.py            # [ACT]   Profile management
    ├── debug_handler.py              # [ACT]   Trace sessions
    ├── send_handler.py               # [SPEAK] Send to platforms
    ├── read_handler.py               # [SPEAK] Read from platforms
    └── media_handler.py              # [SPEAK] Image gen, TTS, file send
```

### File Responsibilities

| File | Purpose | Key Functions | Lines | Status |
|------|---------|---------------|-------|--------|
| `mcp/server.py` | JSON-RPC server, tool dispatch | `MindServer`, `main()` | ~200 | OK |
| `mcp/tools/context.py` | Shared context | `ServerContext` | ~22 | OK |
| `mcp/tools/graph_query_handler.py` | Semantic search | `handle_graph_query` | ~362 | OK |
| `mcp/tools/place_handler.py` | Living places | `handle_place` | ~600 | WATCH |
| `mcp/tools/spawn_handler.py` | Citizen birth | `handle_spawn` | ~574 | WATCH |
| `mcp/tools/call_handler.py` | Calls | `handle_call` | ~470 | WATCH |
| `mcp/tools/subcall_handler.py` | Telepathy | `handle_subcall` | ~200+ | OK |
| `mcp/tools/send_handler.py` | Platform send | `handle_send` | ~396 | OK |
| `mcp/tools/read_handler.py` | Platform read | `handle_read` | ~422 | WATCH |
| `mcp/tools/media_handler.py` | Media gen | `handle_media` | ~403 | WATCH |
| `mcp/tools/think_handler.py` | Gemini | `handle_think` | ~308 | OK |
| `mcp/tools/profile_handler.py` | Profile | `handle_profile` | ~407 | WATCH |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Dispatcher with shared context injection.

**Why:** Each tool is independent but needs optional access to graph, runner, and capabilities. The `needs_ctx` flag in TOOL_DISPATCH controls whether ServerContext is injected — stateless tools (send, read, think, alarm, media) don't need it.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Lazy Import | All bridge modules in send/read/media | Keep startup fast, optional deps truly optional |
| Shared Singleton | `_httpx_client` in home_server.py | Avoid per-request connection overhead |
| MERGE Semantics | graph_write, spawn, call | Idempotent creation — safe to retry |
| Fire-and-forget | Place Server notifications | Non-blocking, best-effort real-time updates |

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `MindServer.handle_request()` | `mcp/server.py:214` | JSON-RPC on stdin |
| `main()` | `mcp/server.py:260` | `python mcp/server.py` |
| Each `handle_{name}()` | `mcp/tools/{name}_handler.py` | Tool dispatch |

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load .env
2. Check for runtime upgrades
3. Connect to FalkorDB (GraphOps + GraphQueries)
4. Connect to membrane graph
5. Initialize CapabilityManager (fire init.startup)
6. Auto-assign pending tasks
7. Initialize ConnectomeRunner
8. Build ServerContext
```

### Main Loop

```
1. Read line from stdin
2. Parse as JSON-RPC
3. Route: initialize | tools/list | tools/call
4. Dispatch to handler via TOOL_DISPATCH
5. Return JSON-RPC response on stdout
```

### Shutdown

```
1. stdin closes (parent process exits)
2. Python interpreter exits
3. No explicit cleanup needed (graph connections are stateless)
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `MIND_FALKORDB_HOST` | env | localhost | FalkorDB host |
| `MIND_FALKORDB_PORT` | env | 6379 | FalkorDB port |
| `GEMINI_API_KEY` | env | (none) | Required for think tool |
| `TELEGRAM_BOT_TOKEN` | env | (none) | Required for Telegram send |
| `ELEVENLABS_API_KEY` | env | (none) | Required for TTS in media tool |
| `ENGINE_PORT` | env | 10001 | Node.js engine port (for home_server proxy) |

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mcp/server.py
    └── mcp/tools/context.py (ServerContext)
    └── mcp/tools/*_handler.py (15 handlers)
        └── runtime/identity.py (actor resolution)
        └── runtime/physics/graph/ (GraphOps, GraphQueries)
        └── runtime/connectome/ (ConnectomeRunner)
        └── runtime/infrastructure/embeddings/ (embedding service)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `falkordb` | Graph database | runtime/physics/graph |
| `google.genai` | Gemini API | think_handler |
| `requests` | Telegram Bot API, ElevenLabs | send_handler, media_handler |
| `httpx` | Engine reverse proxy | home_server.py |
| `websockets` | Engine WS proxy | home_server.py |
