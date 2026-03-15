# Project — Sync: Current State

```
LAST_UPDATED: 2026-03-15
UPDATED_BY: Claude (agent)
```

---

## CURRENT STATE

Mind MCP is the **MCP server + cognitive runtime** for Mind Protocol. It implements the L1 citizen layer — the backend engine that gives AI citizens persistent memory, emotions, drives, relationships, and physics-based cognition through a FalkorDB graph.

**What it IS:**
- MCP server exposing 15 tools (THINK / ACT / SPEAK)
- Physics engine running 21 cognitive laws (zero-LLM tick loop)
- Orchestrator for multi-citizen dispatch (budget-driven)
- Bridges to Telegram, Discord, WhatsApp, Twitter/X, Email, SMS
- CLI (`mind init`, `mind status`, `mind explore`)
- Home server (FastAPI wrapper for cloud deployment on Render)

**What it is NOT:**
- Not a frontend (that's mind-platform)
- Not the registry (that's L4 / mind-protocol)
- Not the XR world (that's cities-of-light)

**Architecture position:**

| Layer | Role | Repo |
|-------|------|------|
| L1 | Citizen cognition | **mind-mcp** (this repo) |
| L2 | Organization | **mind-mcp** `runtime/organization/` |
| L3 | Ecosystem | mind-platform |
| L4 | Protocol | mind-protocol |

---

## KEY COMPONENTS

| Component | Path | Status |
|-----------|------|--------|
| MCP Server | `mcp/server.py` + `mcp/tools/` | Stable |
| Physics Engine | `runtime/physics/` + `runtime/cognition/` | Stable (Laws 1-18 implemented, 19-21 emerging) |
| Orchestrator | `runtime/orchestrator/` | Stable |
| Graph Ops | `runtime/physics/graph/` | Stable |
| Membrane | `runtime/membrane/` | Stable |
| Organization (L2) | `runtime/organization/` | New (2026-03-15) |
| Bridges | `runtime/bridges/` | Stable |
| CLI | `cli/` | Stable |
| Home Server | `home_server.py` | Stable |
| Embeddings | `runtime/infrastructure/embeddings/` | Stable (OpenAI in prod) |

### MCP Tools (15)

**THINK:** `graph_query`, `graph_write`, `procedure`, `think`
**ACT:** `task`, `alarm`, `place`, `call`, `subcall`, `spawn`, `profile`, `debug`
**SPEAK:** `send`, `read`, `media`

---

## ACTIVE WORK

### L2 Organizational Layer (Just Added)

- **Area:** `runtime/organization/`
- **Status:** Code added, integration ongoing
- **Owner:** agent
- **Context:** 16 new capabilities, 20 new skills. Includes access_manager, anti_sybil, bilateral_transfer, lifecycle_manager, settlement_engine.

### Schema v2.3

- **Area:** `.mind/schema.yaml`, `schema-l2.yaml`
- **Status:** v2.3 stable, schema-l2.yaml drafted but uncommitted
- **Owner:** agent
- **Context:** Structural link tags, visual assets at L3, renames. Split into schema-l1/l3 considered.

---

## RECENT CHANGES

### 2026-03-15: L2 Organizational Membrane Layer

- **What:** Added `runtime/organization/` with access_manager, anti_sybil, bilateral_transfer, lifecycle_manager, settlement_engine.
- **Why:** Enable multi-citizen coordination, permission models, and economic settlement at the org level.
- **Impact:** 16 capabilities + 20 skills added. Integration with existing membrane layer pending.

### 2026-03-15: Cleanup — Dead Physics + Broken CLI

- **What:** Deleted 11 dead physics files, 6 broken CLI commands, accidental .temp/ and duplicate schema.yaml.
- **Why:** Reducing entropy. Dead code was confusing agents.
- **Impact:** Cleaner codebase. `mind init` fixed (SameFileError resolved).

### 2026-03-14: Doc Reorganization

- **What:** Reorganized docs/ into 5 areas, deleted legacy docs, cleaned structure.
- **Why:** Docs were scattered and outdated.
- **Impact:** Clear doc chain navigation.

### 2026-03-13: Schema v2.3

- **What:** Structural link tags, visual assets at L3, renames.
- **Why:** Schema evolution for richer graph semantics.
- **Impact:** Graph ops updated accordingly.

---

## DEPLOYMENT

**Platform:** Render (Docker, Pro plan, Frankfurt region)
**Persistent disk:** 20GB
**Database:** FalkorDB (single graph: `blood_ledger`)
**Embeddings:** OpenAI `text-embedding-3-small` (1536 dimensions, API-based, no local model)
**Entry:** `home_server.py` via uvicorn

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| SYNC was wrong | Fixed | `.mind/state/` | Was describing mind-platform, now corrected |
| `.mind/CLAUDE.md` stale | Medium | `.mind/CLAUDE.md` | References `doctor_check`, `agent_run` — needs update |
| schema-l2.yaml uncommitted | Low | root | Drafted but not yet committed |
| Other repos need render.yaml update | Medium | External | cities-of-light, lumina-prime, contre-terre still use old startCommand |
| Laws 19-21 emerging | Low | `runtime/cognition/` | Budget mgmt, prospection, vertical membrane — partially implemented |

---

## HANDOFF: FOR AGENTS

**Current focus:** Stabilization — SYNC/docs accuracy, L2 integration, schema finalization.

**Key context:**
- 15 MCP tools, not the old `doctor_check`/`task_list`/`agent_run` — those were removed
- Physics runs zero-LLM in the tick loop — all 21 laws are pure graph math
- Production embeddings use OpenAI API, not local sentence-transformers
- FalkorDB graph name is `blood_ledger` (single universe graph)
- Citizens are pre-seeded from `citizens/` directory profiles

**Watch out for:**
- Don't import `sentence-transformers` — not in production deps
- `subentity.py` is ~38K lines — read carefully, don't modify lightly
- The orchestrator manages budget — don't bypass it

---

## HANDOFF: FOR HUMAN

**Executive summary:**
SYNC file was completely wrong — described mind-platform (Next.js frontend), not mind-mcp. Rewritten from scratch. The project is the MCP server + cognitive runtime, deployed on Render with OpenAI embeddings.

**Decisions made recently:**
- L2 org layer added to this repo (not a separate service)
- Schema v2.3 with structural link tags
- 11 dead physics files + 6 broken CLI commands removed

**Still needs your input:**
- Commit the uncommitted `schema-l2.yaml` and `shrine/state/message_queue.jsonl`?
- Update render.yaml in cities-of-light, lumina-prime, contre-terre?
- L2 integration testing plan?

---

## TODO

### Immediate

- [x] Rewrite SYNC (was describing wrong project)
- [ ] Fix `.mind/CLAUDE.md` stale tool references
- [ ] Commit `schema-l2.yaml`
- [ ] Update render.yaml in other repos (cities-of-light, lumina-prime, contre-terre)

### High Priority

- [ ] L2 organization layer integration testing
- [ ] Laws 19-21 completion (budget, prospection, vertical membrane)
- [ ] Per-citizen L1 graph isolation (currently shared `blood_ledger`)

### Backlog

- [ ] Subconscious mode (graceful degradation on budget exhaustion)
- [ ] Session parallelization (drive diversity -> micro-sessions)
- [ ] Full procedural dialogue system
- [ ] Browser-safe export entry point for mind-platform consumption

---

## MODULE COVERAGE

| Module | Code | Docs | Maturity |
|--------|------|------|----------|
| MCP Server | `mcp/` | `.mind/docs/` | STABLE |
| Physics Engine | `runtime/physics/`, `runtime/cognition/` | `docs/` | STABLE |
| Orchestrator | `runtime/orchestrator/` | - | STABLE |
| Membrane | `runtime/membrane/` | - | STABLE |
| Organization (L2) | `runtime/organization/` | - | NEW |
| Bridges | `runtime/bridges/` | - | STABLE |
| CLI | `cli/` | - | STABLE |
| Embeddings | `runtime/infrastructure/embeddings/` | - | STABLE |

---

## Init: 2025-12-29 → Last rewrite: 2026-03-15

| Setting | Value |
|---------|-------|
| Version | v0.3.0 |
| Database | FalkorDB |
| Graph | blood_ledger |
| Embedding | OpenAI text-embedding-3-small |
| Deploy | Render (Docker, Pro, Frankfurt) |
