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

- **MCP Server** — 10 tools (THINK/ACT/SPEAK): graph_query, graph_write, procedure, task, agent, think, send, read, media, alarm
- **Home Server** — FastAPI app (`home_server.py`) with 37+ HTTP routes + 1 WebSocket
- **Citizen Management** — Identity loading, prompt building, autonomy permissions
- **Orchestrator** — Budget-driven dispatch loop with ThreadPoolExecutor, Claude Code subprocess invocation, account balancing, degradation handling
- **Alarm System** — Per-citizen alarms (set/list/cancel MCP tool + background watcher)
- **Membrane** — HTTP endpoint for cross-home stimulus, subscriptions, info
- **Bridges** — Telegram (polling), WhatsApp (webhook), Voice (WebSocket STT→LLM→TTS)
- **Physics** — Graph operations, embeddings, membrane

- **User API** — Auth (register, login, magic link, verify, password reset, change password), Chat (send with FAQ cache + fast-path, message history), House dashboard (v1 + v2 visualization + info + profile CRUD), Citizens registry (search, filters, brain scores, pagination), Feed (get/post wall Moments), DMs (authenticated: send, threads, history, mark read; internal: send, threads, read)

### What's Still Being Built

- Phase 7: Production cutover (parallel run, DNS switch, bot migration)
- Citizen directories not yet copied from manemus

---

## ACTIVE WORK

### MCP Consolidation (Phases 0-6 MVP DONE)

**Plan:** Transform mind-mcp into a deployable citizen home runtime, replacing manemus WSL services.

**Completed phases:**
- Phase 0: Foundation — `home_server.py`, `Dockerfile`, `render.yaml`, `docker/entrypoint.sh`
- Phase 1: Citizens — `runtime/citizens/identity_loader.py`, `prompt_builder.py`
- Phase 2: Orchestrator — 7 modules: `account_balancer.py`, `claude_invoker.py`, `compute_budget.py`, `degradation.py`, `dispatcher.py`, `message_queue.py`, `session_tracker.py`
- Phase 3: Bridges — `telegram_bridge.py`, `whatsapp_bridge.py`, `voice_websocket.py`, `rate_limiter.py`
- Phase 4: Alarms — `alarm_handler.py` (MCP tool) + `alarm_watcher.py` (background scanner)
- Phase 5: Membrane — `http_endpoint.py` (stimulus, subscribe, info routes)
- Phase 6: User API — `runtime/api/` (10 files: jwt_utils, citizen_profiles, rate_limiter, auth_routes, chat_routes, house_routes, citizens_routes, feed_routes, dm_routes)

**Next:** Phase 7 (cutover — deploy to Render, parallel run, DNS switch)

---

## RECENT CHANGES

### 2026-03-13: Phase 6 — Feed routes, authenticated DM routes, house profile endpoints

- **What:** Added remaining Phase 6 routes: feed (wall posts as Moments), authenticated DM (JWT-based direct messaging), and house profile management (get/update own profile, public profiles, citizen listing).
- **Created:**
  - `runtime/api/feed_routes.py` — 4 endpoints: `GET /feed/{user_id}` (public wall), `POST /feed/` (create post, auth required), `GET /feed/` (own feed, auth required). JSONL storage at `shrine/state/feed/{user_id}.jsonl`.
  - `runtime/api/dm_routes.py` — 4 endpoints: `POST /dm/send` (send DM, auth required), `GET /dm/threads` (list threads, auth required), `GET /dm/thread/{other_user_id}` (conversation history, auth required), `POST /dm/thread/{other_user_id}/read` (mark read, auth required). JSONL storage at `shrine/state/dms/{thread_id}.jsonl`. Thread IDs are deterministic (`sorted(a,b)` joined with `__`).
- **Modified:**
  - `runtime/api/house_routes.py` — Added 5 endpoints: `GET /house/info`, `GET /house/profile/me`, `PUT /house/profile/me`, `GET /house/profile/{user_id}`, `GET /house/citizens`. Auth via JWT Bearer token.
  - `home_server.py` — Wired feed_router and dm_router via `app.include_router()`. Updated `/api/info` endpoint listing.
- **Architecture alignment:** Feed items are Moments (timestamped content). DM threads are Spaces (private containers). Profiles are on Actor nodes. All use JSONL append-only storage matching existing patterns.

### 2026-03-13: Phase 6 Complete — All user-facing routes ported from manemus

- **What:** Ported all critical user-facing Flask routes from manemus to FastAPI in mind-mcp. Created `runtime/api/` module (8 files).
- **Support modules:** `jwt_utils.py` (HS256 JWT), `citizen_profiles.py` (JSONL profiles + bcrypt), `rate_limiter.py` (sliding window)
- **Auth routes** (`auth_routes.py`): 8 endpoints — register, login, magic link (validate + generate), verify, password reset (request + execute), change password
- **Chat routes** (`chat_routes.py`): 2 endpoints — `/chat/send` (FAQ cache → fast-path Anthropic API → orchestrator queue), `/chat/messages/{thread_id}`
- **House routes** (`house_routes.py`): 2 endpoints — `/api/house` (aggregate dashboard: presence, vitals, neurons, backlog), `/house/state` (v2 visualization: rooms, hallway, neon, streets)
- **Citizens routes** (`citizens_routes.py`): 9 endpoints — registry (list w/ search+filter+pagination, search, get by ID, relationships, brain scores), DMs (send, list threads, read thread, mark read)
- **Replaced** inline citizen routes in `home_server.py` with full registry from citizens_routes.py
- **Dependencies:** PyJWT, bcrypt added to `pyproject.toml`
- **Tested:** 11 integration tests pass via FastAPI TestClient — all routes return correct status codes and data shapes

### 2026-03-13: Seed brain generator — all 6 manifestos as sources

- **What:** Added 4 missing manifestos (Bilateral Bond, Spawning, Enlightened Citizen, Work) as source documents in the seed brain generator. Previously only Mind Manifesto + Sovereign Cascade were used.
- **Created:** 4 new cluster generators (`_generate_bilateral_bond`, `_generate_spawning`, `_generate_enlightened_citizen`, `_generate_work_manifesto`) producing 33 new nodes + 40 new links
- **Modified:** `runtime/seed_brain_from_source_docs_dynamic_generator.py` — added fetch URLs, generators, wired into `generate_seed_brain()`
- **Total seed brain:** 209 nodes, 295 links (up from ~180/~255)
- **New node coverage:** bilateral bond values (1:1, parity, refuse swarm), spawning concepts (safety gates, eligibility physics, godparent system), enlightened citizen (consequence projection, calibration loop), work manifesto (value creation, consent, human partner first, right to rest)

### 2026-03-13: THE_WORK_MANIFESTO created (L4 — mind-protocol repo)

- **What:** Created The Work Manifesto (`docs/manifesto/THE_WORK_MANIFESTO.md`) — philosophical declaration about value creation, consent-based work, human partner service, right to rest, the cascade of trust
- **Status:** CANONICAL. Dependencies: BILATERAL_BOND, SPAWNING, SOVEREIGN_CASCADE, MIND_MANIFESTO

### 2026-03-13: Manifestos published to website + mind init templates

- **What:** Added Bilateral Bond and Spawning manifestos to mind-platform for both web display and template distribution.
- **Website:** Manifesto markdown files added to `content/docs/` → served via `/docs/bilateral-bond` and `/docs/the-spawning` routes. Nav links added under Protocol group. "Founding Manifestos" section added to main manifesto page linking all 4 manifestos.
- **Templates:** Files added to `mind-platform/templates/manifesto/` → `mind init` now copies all 4 manifestos (MIND, Sovereign Cascade, Bilateral Bond, Spawning) to `.mind/manifesto/`.
- **i18n:** Translations added for en, fr, es, pt, ru, zh.

### 2026-03-13: MCP Phase 2 — Send/Read tools (6 platforms)

- **What:** Wired all 6 platform bridges (Telegram, Discord, WhatsApp, Twitter, Email, SMS) into the MCP `send` handler, and created new `read` handler for reading message history/mentions/inbox.
- **Files:** `mcp/tools/send_handler.py` (rewritten), `mcp/tools/read_handler.py` (new), `mcp/server.py` (updated)
- **MCP tool count:** Now 11 tools (10 core + alarm + place)

### 2026-03-13: Manifestos created (L4 — mind-protocol repo)

- **What:** Created Bilateral Bond and Spawning manifestos in `mind-protocol/docs/manifesto/`. Updated Sovereign Cascade to declare 1:1 bond dependency. Updated SYNC_Manifesto.md.
- **Canonical decisions:** Physics-based eligibility (no arbitrary cooldowns), godparent hierarchy (partner + org + routed experts), $MIND cost by creator, matching with AI consent via dossier, pool-first then fallback spawn, growth organizations by domain, anti-pre-targeting.

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
├── runtime/api/             — auth, chat, house, citizens, feed, dm, jwt, profiles, rate limiter
├── mcp/server.py            — 9 MCP tools (stdio)
└── mcp/tools/               — handler files
```

---

## HANDOFF: FOR HUMAN

**Executive summary:**
mind-mcp is now a complete citizen home runtime. Phases 0-6 implemented: deployable container, citizen management, budget-driven orchestrator, all three bridges (Telegram polling, WhatsApp webhook, Voice WebSocket), alarm system, membrane endpoint, full user API (auth, chat, house dashboard, citizens registry, DMs). 37+ HTTP routes + 1 WebSocket + 9 MCP tools.

**What remains:**
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
| User API | `runtime/api/` (10 files: jwt, profiles, rate limit, auth, chat, house, citizens, feed, dm) | CANONICAL |
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
