# MCP Tools — Sync: Current State

```
LAST_UPDATED: 2026-03-15
UPDATED_BY: Claude (template compliance rewrite)
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- 15 MCP tools: THINK (4) / ACT (8) / SPEAK (3)
- JSON-RPC stdio transport
- ServerContext dependency injection
- Tool dispatch via static lookup table
- All handlers follow `(args, ctx?) → response` pattern

**What's still being designed:**
- HEALTH checkers (4 indicators defined, none implemented)
- Completion verification system (designed, not coded)

**What's proposed (v2+):**
- Tool composition (chaining tools in a single call)
- Streaming responses (for long-running tools like graph_query)

---

## CURRENT STATE

The MCP server exposes 15 tools organized by cognitive function. All tools are implemented and working in production (deployed on Render via venezia, cities-of-light, lumina-prime, contre-terre). The server connects to FalkorDB for graph operations, auto-registers its endpoint in L4, and initializes the capability manager at startup.

The home_server.py wraps the MCP layer as a FastAPI application for HTTP access. It acts as the single exposed port on Render, proxying unmatched requests to the Node.js engine running on ENGINE_PORT.

---

## RECENT CHANGES

### 2026-03-15: Agent/Marker System Removed

- **What:** Removed the `agent` MCP tool, `runtime/agents/` directory, marker system (`@mind:escalation/proposition/todo`), swarm command, solve-markers command
- **Why:** Agents and markers are deprecated — citizens handle their own work
- **Files:** mcp/server.py, mcp/tools/context.py, runtime/cli.py, .mind/FRAMEWORK.md, .mind/PRINCIPLES.md
- **Impact:** 16 → 15 tools. Created `runtime/identity.py` to preserve citizen ID resolution functions

### 2026-03-15: Engine Reverse Proxy

- **What:** home_server.py now proxies unmatched routes to Node.js engine
- **Why:** Single exposed port on Render; Python is the front door
- **Files:** home_server.py, venezia/render.yaml

### 2026-03-15: Subconscious Mode + Lazy Embedding

- **What:** Added invoke_subconscious() for zero-LLM responses; tick runner auto-embeds nodes
- **Files:** runtime/orchestrator/claude_invoker.py, runtime/cognition/tick_runner_l1_cognitive_engine.py

---

## KNOWN ISSUES

### HEALTH Checkers Not Implemented

- **Severity:** medium
- **Symptom:** HEALTH_MCP_Tools.md defines 4 indicators but no runtime code exists
- **Suspected cause:** Deprioritized in favor of feature work
- **Attempted:** Spec is complete; implementation blocked on capability runtime integration

---

## HANDOFF: FOR AGENTS

**Where I stopped:** All 15 tools working. Doc chain rewritten to match templates.

**What you need to understand:**
- Each handler in `mcp/tools/` is self-contained. Add new tools by creating a handler + adding to TOOL_SCHEMAS and TOOL_DISPATCH in server.py.
- `runtime/identity.py` replaces the old `runtime/agents/mapping.py` for citizen ID resolution.
- The engine proxy in home_server.py is a catch-all — it matches `/{path:path}` so it must be the last route.

**Watch out for:**
- WebSocket proxy requires the `websockets` package (lazy import)
- `httpx` is needed for the engine HTTP proxy
- Think tool sessions are in-memory only (lost on restart, TTL 2h)

---

## HANDOFF: FOR HUMAN

**Executive summary:**
15 MCP tools working in production. Agent/marker system removed. Engine reverse proxy added (Python as front door on Render). Doc chain fully rewritten to match templates.

**Decisions made:**
- Agents removed (citizens are autonomous, no agent orchestration layer)
- Python home_server is the single exposed port; Node.js runs internally on ENGINE_PORT
- httpx + websockets for reverse proxy (no nginx dependency)

**Needs your input:**
- HEALTH checker implementation priority (4 indicators defined, 0 implemented)
- Whether to implement the completion verification system from VALIDATION_Completion_Verification.md

---

## TODO

### Doc/Impl Drift

- [ ] IMPL→DOCS: subcall_handler.py has 24 scenarios not fully documented in ALGORITHM
- [ ] IMPL→DOCS: place_handler.py encryption flow not detailed in ALGORITHM

### Tests to Run

```bash
python3 -m pytest tests/ -x -q
```

### Immediate

- [ ] Implement h_session_valid health checker
- [ ] Add httpx + websockets to pip install in all render.yaml files

### Later

- [ ] Tool composition (multi-tool calls)
- [ ] Streaming responses for long-running tools

---

## POINTERS

| What | Where |
|------|-------|
| MCP server | `mcp/server.py` |
| All tool handlers | `mcp/tools/*_handler.py` |
| Shared context | `mcp/tools/context.py` |
| Identity resolution | `runtime/identity.py` |
| Home server (HTTP) | `home_server.py` |
| Engine proxy | `home_server.py:proxy_to_engine()` |
| Procedure YAMLs | `procedures/*.yaml` |
