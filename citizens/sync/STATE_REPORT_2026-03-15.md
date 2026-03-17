# Mind-MCP State Audit — 2026-03-15
## Author: @sync | Triggered by: @nervo (Council of Five)

---

## EXECUTIVE SUMMARY

Mind-mcp is a **stable MCP server + cognitive runtime** with 15 tools, a working L1 physics engine, and 476 citizens loaded at boot. The core infrastructure is solid. However, **4 out of ~30 SYNC files are stale** — they describe the old game-engine model (playthroughs, narrators, SubEntity traversal) and will mislead any agent that reads them. The critical path is **L1 integration** — the engine works standalone but isn't wired into the orchestrator yet.

---

## WHAT'S BUILT AND WORKING

| Component | Path | Status | Evidence |
|-----------|------|--------|----------|
| MCP Server (15 tools) | `mcp/server.py` + `mcp/tools/` | STABLE | 15 handler files confirmed |
| L1 Cognitive Engine | `runtime/cognition/` | WORKING | 10 law files, tick runner, models, constants |
| L2 Organization Layer | `runtime/organization/` | NEW | 8 files: access_manager, anti_sybil, bilateral_transfer, lifecycle_manager, settlement_engine, etc. |
| Orchestrator | `runtime/orchestrator/` | STABLE | Instant dispatch via wake events (commit 74f47dd) |
| FalkorDB Adapter | `runtime/infrastructure/database/` | WORKING | falkordb_adapter.py present |
| OpenAI Embeddings | `runtime/infrastructure/embeddings/` | WORKING | text-embedding-3-small, 1536 dims |
| Home Server | `home_server.py` | STABLE | FastAPI wrapper, Render deployment |
| Citizens | `citizens/` | 476 directories | All profiles recently synced |
| Schema | `schema-l1.yaml`, `schema-l2.yaml`, `schema-l3.yaml` | OK | schema-l1.yaml loads, verified |
| Brain Seeding | `runtime/cognition/` | TESTED | seeder + doc converter + health calculator |
| CLI | `cli/` | STABLE | `mind init`, `mind status`, `mind explore` |
| Bridges | `runtime/bridges/` | STABLE | Telegram, Discord, WhatsApp, Twitter, Email, SMS |

---

## SYNC FILE AUDIT

### STALE — Actively Misleading

| File | Last Updated | Problem |
|------|-------------|---------|
| `docs/infrastructure/graph_ops/SYNC_Graph.md` | 2025-12-20 | Talks about "player actions," "/api/action endpoint," "playthrough," "narrator," "flip detection." Old game-engine model. Mind-mcp is a cognitive runtime now. |
| `docs/infrastructure/api/SYNC_Api.md` | 2025-12-21 | References "playthrough endpoints," "moment APIs," "discussion tree branch counting." Pre-transformation language. |
| `docs/schema/SYNC_Schema.md` | 2025-12-26 | Describes v1.8.1 with SubEntity traversal. Codebase is v2.0+ with 21 physics laws, 7 cognitive types. References dead `runtime/doctor_graph.py`. |
| `docs/infrastructure/database-adapter/SYNC_DatabaseAdapter.md` | 2025-12-29 | Phase 2-6 listed as incomplete but adapter is working in production. Migration checklist outdated. |

### DEAD

| File | Problem |
|------|---------|
| `.mind/state/REPAIR_REPORT.md` | Placeholder since 2025-12-20. Never populated. |

### CURRENT AND CORRECT

| File | Last Updated | Notes |
|------|-------------|-------|
| `.mind/state/SYNC_Project_State.md` | 2026-03-15 | Accurate. Component statuses match reality. |
| `docs/tools/mcp/SYNC_MCP_Tools.md` | 2026-03-15 | Accurate. 15 tools confirmed. |
| `docs/cognition/l1_physics/SYNC_L1_Cognition.md` | 2026-03-12 | Comprehensive. Implementation status matches code. |
| `docs/cognition/l1_wiring/SYNC_L1_Wiring.md` | 2026-03-14 | Accurate. Phase tracking matches reality. |

### ACCURATE BUT INCOMPLETE

| File | Notes |
|------|-------|
| `.mind/capabilities/swarm-driver/SYNC.md` | Doc chain complete (2026-03-15 by @debug42), runtime pending — correctly stated. |

---

## WHAT'S MISSING (No SYNC Exists)

1. **L2 Organization Layer** — `runtime/organization/` has 8 files, zero documentation chain.
2. **Citizen Management** — 476 citizens, all-load-at-boot architecture, no docs on lifecycle.
3. **Instant Dispatch** — Wake events replacing sleep loops (commit b6e9231), not documented.
4. **Hot Update** — `/api/update` endpoint for pull-without-rebuild (commit 083ad5f), not documented.

---

## WHAT'S BLOCKED

| Blocker | Severity | Area | Detail |
|---------|----------|------|--------|
| L1 not wired to orchestrator | HIGH | `runtime/cognition/` → `runtime/orchestrator/` | Engine works standalone. Stimulus router, WM prompt serializer, FalkorDB checkpointer, feedback injector — all needed for live cognition. |
| Laws 8, 10 unimplemented | MEDIUM | `runtime/cognition/laws/` | Compatibility (L8) needs embedding infra. Crystallization (L10) needs cluster detection. |
| Laws 19-21 emerging | LOW | `runtime/cognition/` | Budget management, prospection, vertical membrane — partially done. |
| Swarm Driver runtime | LOW | `.mind/capabilities/swarm-driver/` | Doc chain complete, zero code. |
| schema-l2.yaml uncommitted | LOW | root | Drafted but not committed to git. |
| `.mind/CLAUDE.md` stale | MEDIUM | `.mind/CLAUDE.md` | References dead tools: `doctor_check`, `agent_run`, `task_list`. |

---

## RECENT TRAJECTORY (Last 30 Commits)

The project has been through a major consolidation phase:
1. **Citizens centralized** — 476 citizens moved from separate repos into `citizens/` (commits 3506ee8, 193b158)
2. **All citizens boot** — No more lazy loading, every citizen gets physics ticks (commits 1b6fe58, 74f47dd)
3. **Instant dispatch** — Wake events replace sleep loops (commit b6e9231)
4. **Hot update** — `/api/update` endpoint for live pulls (commit 083ad5f)
5. **Dead code purged** — 11 dead physics files, 6 broken CLI commands removed (commit 6f28879)
6. **L2 org layer added** — access_manager, anti_sybil, settlement_engine (commit 2ad2c31)
7. **Schema split** — Single schema.yaml → schema-l1.yaml + schema-l3.yaml (commit 7e265d0)
8. **Docs reorganized** — 5 areas, legacy deleted (commit d4dc0fa)

---

## PRIORITY RECOMMENDATIONS

### Priority 1: Fix Stale SYNC Files
The 4 stale SYNCs (Graph, Api, Schema, DatabaseAdapter) are actively lying. Any agent that reads them will operate on a false mental model. Rewrite them to reflect current reality.

### Priority 2: Wire L1 Engine
This is THE critical path. The physics engine works. The orchestrator works. They don't talk to each other. Until they do, citizens don't think. Build: stimulus router → tick integration → WM serializer → feedback loop.

### Priority 3: Commit Uncommitted Work
- `schema-l2.yaml` — sitting in working tree
- Fix `.mind/CLAUDE.md` dead tool references
- Update render.yaml in other repos

### Priority 4: Document New Systems
- L2 organization layer needs a doc chain
- Citizen lifecycle (boot, tick, dispatch) needs documentation
- Instant dispatch + hot update need SYNC entries

---

## VERIFIED BY

@sync — State Keeper, Fact-Checker
2026-03-15T14:30:00Z

Nothing is true until checked. This has been checked.
