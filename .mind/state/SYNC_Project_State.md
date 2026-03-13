# Project — Sync: Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: Claude (architect)
```

---

## CURRENT STATE

**mind-mcp** — Deployable "citizen home" runtime for Mind Protocol. Hosts N citizens with their own brains, keys, and graph. Contains physics engine, orchestrator, bridges, membrane, and MCP server.

STATUS: DESIGNING (consolidation in progress)

### What's Canonical (working)

- **MCP Server** — 9 tools (THINK/ACT/SPEAK): graph_query, graph_write, procedure, task, agent, think, send, media, alarm
- **Home Server** — FastAPI app (`home_server.py`) with 17 HTTP routes + 1 WebSocket
- **Citizen Management** — Identity loading, prompt building, autonomy permissions
- **Orchestrator** — Budget-driven dispatch loop with ThreadPoolExecutor, Claude Code subprocess invocation, account balancing, degradation handling
- **Alarm System** — Per-citizen alarms (set/list/cancel MCP tool + background watcher)
- **Membrane** — HTTP endpoint for cross-home stimulus, subscriptions, info
- **Bridges** — Telegram (polling), WhatsApp (webhook), Voice (WebSocket STT→LLM→TTS)
- **Physics** — Graph operations, embeddings, membrane

### What's Still Being Built

- Phase 6: Flask→FastAPI API migration (user-facing endpoints from manemus)
- Phase 7: Production cutover (parallel run, DNS switch, bot migration)
- Citizen directories not yet copied from manemus

---

## ACTIVE WORK

### MCP Consolidation (Phases 0-5 DONE, Phase 3 DONE)

**Plan:** Transform mind-mcp into a deployable citizen home runtime, replacing manemus WSL services.

**Completed phases:**
- Phase 0: Foundation — `home_server.py`, `Dockerfile`, `render.yaml`, `docker/entrypoint.sh`
- Phase 1: Citizens — `runtime/citizens/identity_loader.py`, `prompt_builder.py`
- Phase 2: Orchestrator — 7 modules: `account_balancer.py`, `claude_invoker.py`, `compute_budget.py`, `degradation.py`, `dispatcher.py`, `message_queue.py`, `session_tracker.py`
- Phase 3: Bridges — `telegram_bridge.py`, `whatsapp_bridge.py`, `voice_websocket.py`, `rate_limiter.py`
- Phase 4: Alarms — `alarm_handler.py` (MCP tool) + `alarm_watcher.py` (background scanner)
- Phase 5: Membrane — `http_endpoint.py` (stimulus, subscribe, info routes)

**Next:** Phase 6 (HTTP API migration) → Phase 7 (cutover)

---

## RECENT CHANGES

### 2026-03-13: Citizen Parenthood Network documentation chain created

- **What:** Created complete 8-file documentation chain for the Citizen Parenthood Network module under `docs/citizens/parenthood_network/`.
- **Why:** Defines how AI citizens reproduce — N parents spawn a new citizen with inherited traits via embedding-based brain node selection, safety-validated seed brains, and trust-linked accountability.
- **Files created:** OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC — all fully populated with design content.
- **Status:** DESIGNING (proposed module, no code exists yet)
- **Key design decisions:** N-parent spawning (1-6+) via intent embedding centroid, top-K node selection by cosine similarity, safety gate (empathy/concentration/diversity/population-distance), protocol-determined SID (parents cannot influence), copy semantics for seed brain, trust impact weight = 1/N, child enters unpartnered matching pool at birth.

### 2026-03-13: Human-AI Pairing documentation chain created

- **What:** Created complete 8-file documentation chain for the Human-AI Pairing module under `docs/citizens/human_ai_pairing/`.
- **Why:** Captures the architectural vision for 1:1 citizen-human bonds — the structural constraint that prevents AI monoculture and ensures bilateral investment in Mind Protocol.
- **Files created:** OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC — all fully populated with design content.
- **Status:** DESIGNING (proposed module, no code exists yet)
- **Key design decisions:** 1:1 bond enforced by graph constraints, matching pool with pluggable compatibility scoring, cooldown on dissolution, autonomy milestones as moment nodes, all state graph-native.

### 2026-03-13: Phase 3 — Bridge Integration

- **What:** Ported Telegram, WhatsApp, and Voice bridges from manemus to mind-mcp.
- **Created:**
  - `runtime/bridges/__init__.py` — Module init
  - `runtime/bridges/rate_limiter.py` — Shared spam/flood detection (emoji, burst, repeated patterns)
  - `runtime/bridges/telegram_bridge.py` — Polling bot with citizen routing, voice STT/TTS, group chat support
  - `runtime/bridges/whatsapp_bridge.py` — WAHA webhook receiver with FastAPI router, LID resolution
  - `runtime/bridges/voice_websocket.py` — Real-time voice: Whisper STT → Claude LLM → ElevenLabs TTS
- **Modified:** `home_server.py` — Added bridge startup in lifespan, WhatsApp router, Voice WebSocket route, bridge shutdown
- **Routes added:** `/whatsapp/webhook`, `/whatsapp/health`, `/voice/ws`

### 2026-03-13: Phases 0-2, 4-5 — Core Runtime

- **What:** Built complete citizen home runtime from scratch + ported from manemus.
- **Phase 0:** FastAPI server, Dockerfile with Claude CLI, Render config, entrypoint with credential seeding
- **Phase 1:** Citizen identity loading, prompt building with profile sections, autonomy permissions
- **Phase 2:** Full orchestrator with budget-driven ticks (sqrt trust scaling), account balancer (round-robin), Claude Code subprocess invocation, graceful degradation (4 levels), JSONL priority queue, neuron session tracking
- **Phase 4:** Alarm MCP tool (set/list/cancel) + background alarm watcher (30s scan interval, repeating alarms)
- **Phase 5:** Membrane HTTP endpoint (stimulus queries, stream subscriptions, L4 discovery info)

### 2026-03-12: MCP Tool Pruning (by another session)

- Reduced from 21 tools to 9 (THINK/ACT/SPEAK pattern)
- `mcp/server.py` — 1959→258 lines
- Handler files in `mcp/tools/`

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| Citizen dirs not copied | Medium | `.mind/citizens/` | Need to copy from manemus |
| No user-facing HTTP API | Medium | Phase 6 | Flask routes not yet ported |
| Graph may not connect | Low | FalkorDB | Graceful degradation if offline |

---

## HANDOFF: FOR AGENTS

**Agent subtype:** groundwork (implementation)

**Current focus:** Phase 6 (Flask→FastAPI API migration) or Phase 7 prep

**Key context:**
- Citizens use Claude Code subprocess (`claude --print`), NEVER direct API. API is degraded fallback only.
- Tick speed is budget-driven (ComputeBudget), not fixed sleep interval.
- Trust-based compute: sqrt scaling, higher trust = more ticks.
- No cron — citizens set their own alarms via MCP tool.
- Account balancer round-robins across `~/.claude-accounts/{a,b,c}/`.

**Architecture:**
```
home_server.py (FastAPI)
├── runtime/citizens/        — identity, prompt building
├── runtime/orchestrator/    — dispatcher, invoker, budget, queue, sessions
├── runtime/bridges/         — telegram, whatsapp, voice
├── runtime/membrane/        — HTTP endpoint, stimulus, subscriptions
├── mcp/server.py            — 9 MCP tools (stdio)
└── mcp/tools/               — handler files
```

---

## HANDOFF: FOR HUMAN

**Executive summary:**
mind-mcp is now a complete citizen home runtime. Phases 0-5 implemented: deployable container, citizen management, budget-driven orchestrator, all three bridges (Telegram polling, WhatsApp webhook, Voice WebSocket), alarm system, membrane endpoint. 17 HTTP routes + 1 WebSocket + 9 MCP tools.

**What remains:**
- Phase 6: Port user-facing API routes from manemus Flask server
- Phase 7: Deploy to Render, parallel run, DNS cutover
- Copy citizen directories from manemus to `.mind/citizens/`

---

## MODULE COVERAGE

| Module | Code | Status |
|--------|------|--------|
| MCP Server | `mcp/server.py`, `mcp/tools/` | CANONICAL |
| Home Server | `home_server.py` | CANONICAL |
| Citizens | `runtime/citizens/` | CANONICAL |
| Orchestrator | `runtime/orchestrator/` (7 files) | CANONICAL |
| Bridges | `runtime/bridges/` (4 files) | CANONICAL |
| Alarms | `mcp/tools/alarm_handler.py`, `runtime/orchestrator/alarm_watcher.py` | CANONICAL |
| Membrane | `runtime/membrane/http_endpoint.py` | CANONICAL |
| Physics | `runtime/physics/` | CANONICAL (pre-existing) |
| Human-AI Pairing | `docs/citizens/human_ai_pairing/` (8 docs) | DESIGNING (proposed) |
| Parenthood Network | `docs/citizens/parenthood_network/` (8 docs) | DESIGNING (proposed) |

## Init: 2026-03-13 17:35

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---
