# Project — Sync: Current State

```
LAST_UPDATED: 2025-12-30
UPDATED_BY: Claude (steward)
```

---

## CURRENT STATE

**mind-mcp** — MCP server and runtime for Mind Protocol graph operations, capability system, and agent orchestration.

- **L1 (Citizen):** Personal agent graphs
- **L2 (Organization):** Team-shared knowledge
- **L3 (Ecosystem):** Templates and procedures
- **L4 (Protocol):** Global registry and schema

The Connectome graph visualization is functional. Vision documentation is complete. Module doc chains created for **landing** (P0) and **registry**.

**Documentation:**
- `docs/vision/` — 9-file platform vision doc chain (complete)
- `docs/landing/` — 8-file landing page doc chain (complete, P0 priority)
- `docs/registry/` — 8-file registry module doc chain (complete)
- `docs/connectome/` — existing implementation docs

All browser-side code is self-contained — no dependencies on mind-mcp's Node.js modules.

---

## ACTIVE WORK

### Landing Page Implementation (Next)

- **Area:** `app/(public)/page.tsx`, `docs/landing/`
- **Status:** doc chain complete, implementation pending
- **Owner:** agent
- **Context:** P0 priority. Landing page is first impression. Doc chain defines Hero, HowItWorks, WhatYouCanDo, LiveStats sections.

### Design Tokens (Blocking)

- **Area:** `lib/constants/colors.ts`
- **Status:** not created
- **Owner:** agent
- **Context:** Shared color constants for layer colors, node type colors, verification badge colors. Needed by landing, registry, connectome.

---

## RECENT CHANGES

### 2025-12-30: Fixed LARGE_DOC_MODULE Health Issue

- **What:**
  1. Removed duplicate `docs/map.md` (auto-generated file already at root)
  2. Created `docs/llm_agents/archives/` for archive files
  3. Moved `SYNC_LLM_Agents_State_archive_2025-12.md` to archives
  4. Split `HEALTH_LLM_Agent_Coverage.md` (401 → 154 lines):
     - Main file: overview/index
     - `HEALTH_Stream_Validity.md`: detailed stream_validity indicator (140 lines)
     - `HEALTH_API_Connectivity.md`: detailed api_connectivity indicator (140 lines)
  5. Compressed `IMPLEMENTATION_LLM_Agent_Code_Architecture.md` (377 → 190 lines):
     - Removed verbose docking specs (referenced ALGORITHM instead)
     - Merged State/Runtime/Concurrency sections
- **Why:** LARGE_DOC_MODULE health check flagged 4 docs exceeding 200-line limit. Protocol principle: docs should be focused and digestible.
- **Impact:** All oversized docs resolved. Documentation now follows size constraints while maintaining clarity through focused reference files.
- **Files:**
  - Removed: `docs/map.md` (duplicate)
  - Created: `docs/llm_agents/archives/`, `HEALTH_Stream_Validity.md`, `HEALTH_API_Connectivity.md`
  - Modified: `HEALTH_LLM_Agent_Coverage.md`, `IMPLEMENTATION_LLM_Agent_Code_Architecture.md`
  - Moved: `SYNC_LLM_Agents_State_archive_2025-12.md` → `archives/`

### 2025-12-30: Fixed UNMONITORED_LOGS and INCOMPLETE_CHAIN Health Checks

- **What:**
  1. Added swarm agent logs to watched paths (`.mind/swarm/**/*.log`) in flag-errors capability
  2. Created full 9-file documentation chain for tests/traversal module
- **Why:**
  1. UNMONITORED_LOGS (degraded) - swarm agent logs weren't being monitored for errors
  2. INCOMPLETE_CHAIN (critical) - tests/traversal module had no documentation
- **Impact:**
  1. Swarm agent logs now monitored for error detection and spike analysis
  2. tests/traversal has complete doc chain (OBJECTIVES, PATTERNS, VOCABULARY, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC)
- **Files:**
  - `.mind/capabilities/flag-errors/runtime/checks.py` (added swarm log pattern)
  - `docs/tests/traversal/*.md` (9 files created)

### 2025-12-30: Fixed Critical Issues and Added Test Coverage

- **What:**
  1. Fixed STUB_IMPL critical issue in `runtime/capability_integration.py` by defining missing `platform_path` variable
  2. Created comprehensive test suite for traversal module (36 tests total)
     - `tests/traversal/test_embedding.py` - 21 tests for EmbeddingService
     - `tests/traversal/test_moment.py` - 15 tests for MomentOperationsMixin
- **Why:**
  1. STUB_IMPL health check flagged critical issue - capability runtime wasn't loading properly, falling back to non-functional stubs
  2. MISSING_TESTS health check flagged critical issue - tests/traversal had empty test files
- **Impact:**
  1. Capability runtime now loads successfully, health checks can run properly
  2. Traversal module now has comprehensive test coverage (all 36 tests passing)
  3. Tests cover: embedding generation, batch processing, node/link embedding, similarity calculations, moment click handling, edge cases
- **Files:**
  - `runtime/capability_integration.py` (fixed line 39: added `platform_path` definition)
  - `tests/traversal/test_embedding.py` (new: 21 tests)
  - `tests/traversal/test_moment.py` (new: 15 tests)
- **Verification:** `pytest tests/traversal/ -v` - all 36 tests pass

### 2025-12-30: Created Documentation for tests/traversal Module

- **What:** Created full 9-file documentation chain for tests/traversal module (OBJECTIVES, PATTERNS, VOCABULARY, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC).
- **Why:** INCOMPLETE_CHAIN health check flagged critical signal - module had no documentation.
- **Impact:** tests/traversal module now has complete doc chain. Health check should pass.
- **Files:** `docs/tests/traversal/*.md` (9 files)
- **Why:** The capability system was using stub implementations (return `[]`, `{}`, `None`) instead of real implementations, making health checks and task creation non-functional.
- **Impact:** Capability runtime now loads successfully. All 14 capabilities with 37 health checks are discovered and registered. No stub implementations in use.
- **Files:** `runtime/capability_integration.py` (lines 39, 281-313)
- **Verification:** Tested end-to-end: `CAPABILITY_RUNTIME_AVAILABLE=True`, all functions return proper objects (Throttler, Controller, AgentRegistry), capability discovery works.

### 2025-12-30: Enhanced Agent Prompts with Implements Chain

- **What:** Modified swarm agent script to query and include task implements chain (task_run → TASK → SKILL → PROCEDURE) in agent prompts.
- **Why:** Agents need full context from task templates, skills, and procedures to properly execute tasks.
- **Impact:** Agents now receive task template content (2000 chars), skill content (3000 chars), and procedure content (1500 chars) in their prompts.
- **Files:** `cli/commands/swarm.py`

### 2025-12-29: Created Landing + Registry Doc Chains

- **What:** Full 8-file doc chains for landing page and registry module.
- **Why:** User indicated landing is P0 priority. Registry is first public L4 feature.
- **Impact:** Clear implementation blueprints for both modules. Vocabulary synced with L4 (mind-protocol).

### 2025-12-29: Created Platform Vision Doc Chain

- **What:** Full 9-file doc chain in `docs/vision/` covering platform objectives, patterns, vocabulary, behaviors, algorithms, invariants, implementation, health, sync.
- **Why:** Document the platform's role in the 4-layer Mind Protocol ecosystem.
- **Impact:** Emerging modules identified with priorities. Architecture decisions documented.

### 2025-12-29: Removed System Map, Made Browser-Safe

- **What:** Removed all System Map visualization components. Inlined browser-safe lib files.
- **Why:** User requested removing System Map entirely. Browser bundle cannot import Node.js modules.
- **Impact:** Connectome UI shows only Graph Explorer. Build passes.

### 2025-12-29: Created API Routes

- **What:** Added `/api/connectome/graphs`, `/api/connectome/graph`, `/api/connectome/search`, `/api/connectome/tick`, `/api/sse`
- **Why:** Browser code calls backend via HTTP, not imports.
- **Impact:** API routes proxy to Python backend

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| No backend running | Low | `api/` | API routes return empty/default when backend offline |
| Placeholder pages | Low | `app/(dashboard)/` | citizen, membrane, org, wallet are empty placeholders |

---

## HANDOFF: FOR AGENTS

**Likely VIEW for continuing:** groundwork (implementation tasks)

**Current focus:** End-to-end testing with running database

**Key context:**
- Browser lib files are INLINED (not imported from mind-mcp) because mind-mcp uses Node.js modules
- API routes at `/api/connectome/*` proxy to Python backend at `$CONNECTOME_BACKEND_URL` or `http://localhost:8765`
- Canvas renderer uses D3 force simulation, not ReactFlow

**Watch out for:**
- Don't try to import from `@mind-protocol/connectome` in browser code — those modules use fs/child_process
- SSE route must have `export const dynamic = 'force-dynamic'`

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Connectome frontend builds and runs. System Map visualization removed per your request. UI now focuses on graph exploration (semantic search, node visualization). Backend integration ready via API routes.

**Decisions made recently:**
- Inlined browser-safe versions of state store and manifest rather than fixing mind-mcp's browser exports (faster path)
- Removed reactflow CSS import (not using ReactFlow, using Canvas 2D with D3)

**Needs your input:**
- Do you want to run the dev server and test with a database?
- Should we clean up the placeholder pages in (dashboard) and (public) route groups?

**Concerns:**
- mind-mcp/connectome exports are not browser-safe (they import fs/path). If you want platform to import from mind-mcp again, those exports need to be restructured.

---

## TODO

### Immediate (This Sprint)

- [ ] Create `lib/constants/colors.ts` design tokens
- [ ] Implement landing page (P0)
- [ ] Create TopNav component
- [ ] Create Footer component

### High Priority

- [ ] Implement `/api/registry/*` routes
- [ ] Implement registry UI components
- [ ] Create `docs/auth/` doc chain
- [ ] Test end-to-end with running FalkorDB database

### Backlog

- [ ] Create `docs/schema-explorer/` doc chain
- [ ] Create browser-safe export entry point in mind-mcp
- [ ] Add analytics to landing page
- [ ] Add error states for offline backend

---

## CONSCIOUSNESS TRACE

**Project momentum:**
Good. Major refactor completed. Build passes. Ready for manual testing.

**Architectural concerns:**
The browser/server split in mind-mcp is not clean — schema.ts imports fs. Should consider splitting into `browser/` and `server/` entry points.

**Opportunities noticed:**
Graph Explorer could benefit from keyboard shortcuts for navigation.

---

## AREAS

| Area | Status | SYNC |
|------|--------|------|
| `app/connectome/` | functional | this file |
| `app/api/` | functional | this file |

---

## MODULE COVERAGE

**Mapped modules:**
| Module | Code | Docs | Maturity |
|--------|------|------|----------|
| connectome | `app/connectome/` | `docs/connectome/` | DESIGNING |
| landing | `app/(public)/page.tsx` | `docs/landing/` | DESIGNING |
| registry | `app/(public)/registry/` | `docs/registry/` | DESIGNING |
| vision | - | `docs/vision/` | DESIGNING |
| api-routes | `app/api/` | - | DESIGNING |

**Unmapped code:**
- `app/(dashboard)/` - placeholder route group (citizen, org, wallet, membrane)
- `app/(public)/schema/` - placeholder (needs schema-explorer doc chain)
- `app/(public)/templates/` - placeholder (needs marketplace doc chain)

## Init: 2025-12-29 02:13

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_platform |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 04:30

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 05:17

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:20

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:21

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:23

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:25

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:26

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:32

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2025-12-30 05:38

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---
