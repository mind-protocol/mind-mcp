# Archived: SYNC_Project_State.md

Archived on: 2025-12-29
Original file: SYNC_Project_State.md

---

## RECENT CHANGES

### 2025-12-29: Doc Ingestion — Fail Loud on Missing Templates

- **What:** Changed `_load_required_sections()` to raise `FileNotFoundError` instead of using hardcoded fallback
- **Why:** Follows "fail LOUD" principle from PRINCIPLES.md — silent fallbacks hide problems
- **Files:** `runtime/ingest/docs.py`

### 2025-12-29: Doc Ingestion at Init and Sync

- **What:** Added automatic doc ingestion to both `mind init` and `mind sync` commands
- **Why:** Docs should be in graph for semantic querying
- **Flow:**
  1. Scans `docs/` directory for modules
  2. Creates space hierarchy (root → area → module)
  3. For each doc chain file (OBJECTIVES → HEALTH):
     - Doc exists + valid → Create narrative:{subtype}
     - Doc exists + invalid → Create narrative:{subtype} + task:fix_template
     - Doc missing → Create stub narrative:{subtype} + task:create_doc
  4. Validates docs against `.mind/templates/{PREFIX}_TEMPLATE.md`
- **Files:**
  - `runtime/ingest/docs.py` (new) — main ingestion logic
  - `runtime/init_cmd.py` — calls doc ingestion after seed injection
  - `runtime/sync.py` — calls doc ingestion before showing status

### 2025-12-29: Schema v1.9.0 — Granularity Field

- **What:** Updated schema.yaml to v1.9.0 with NarrativeBase.granularity field
- **Why:** Formalize doc ingestion granularity that was already in use (runtime/ingest/docs.py)
- **Changes:**
  - Added NarrativeBase section extending NodeBase
  - `granularity: int (nullable, values: 1, 2, 3)` — 1=full doc, 2=per-section, 3=per-item
  - Updated version to 1.9.0
- **Files:** `docs/schema/schema.yaml`
- **Note:** Schema.py NOT changed — YAML is source of truth, runtime validation doesn't need explicit entry for nullable fields

### 2025-12-29: Procedure Docs V2.0 Complete

- **What:** Updated all 9 procedure doc chain files to V2.0
- **Why:** V1 had runtime doc chain loading which was complex; V2 simplifies to self-contained steps
- **Key V2.0 changes:**
  - Steps are self-contained guides (What/Why/How/Watch out sections)
  - No runtime doc chain loading
  - IMPLEMENTS direction: bottom → top (Health → Implementation → ... → Objectives)
  - Executor types: agent, code, actor, hybrid
  - guide_completeness replaces doc_chain_completeness health indicator
- **Files:** All `docs/procedure/*.md` files (9 total including new VOCABULARY)

### 2025-12-29: Procedure Module Doc Chain Created

- **What:** Created full 8-file documentation chain for Procedure module
- **Why:** Crystallize V1.1 spec (`data/graph-chain-v1.md`) into canonical mind protocol format
- **Files created:**
  - `docs/procedure/OBJECTIVES_Procedure.md` — Ranked goals (O1-O4), tradeoffs, success signals
  - `docs/procedure/PATTERNS_Procedure.md` — Three layers (Context/Trace/Flow), template vs execution
  - `docs/procedure/BEHAVIORS_Procedure.md` — 7 behaviors (B1-B7) with GIVEN/WHEN/THEN
  - `docs/procedure/ALGORITHM_Procedure.md` — Logic steps for start/continue/end (no code)
  - `docs/procedure/VALIDATION_Procedure.md` — 7 invariants (V1-V7) with priorities
  - `docs/procedure/IMPLEMENTATION_Procedure.md` — Code structure, flows, schemas (no code)
  - `docs/procedure/HEALTH_Procedure.md` — 4 health indicators, checker specs
  - `docs/procedure/SYNC_Procedure.md` — Current state, handoffs, open questions
- **Key decisions:**
  - Per-step doc chains via IMPLEMENTED_IN links (not global context)
  - Deterministic V1 API (physics tracks state, doesn't route)
  - Template protection (agent writes to Run Space only)
- **Open escalations (12 total):**
  - IMPLEMENTED_IN direction unclear
  - Validation spec schema not finalized
  - File location convention (engine/ vs runtime/)
- **Impact:** Ready for implementation once escalations resolved

### 2025-12-29: Backprop coloring (v2.1)

- **What:** Changed link coloring from forward to backward propagation
- **Why:** Forward coloring colored links before knowing if the path was useful
- **Changes:**
  1. Removed `forward_color_link` from `_step_seeking`
  2. Implemented `backward_color_path` in `_step_reflecting` (when satisfaction > 0.5)
  3. Added backprop after `_step_crystallizing` (when narrative created)
- **Result:** Links are only colored when we know the path led to something valuable
- **Files:** `runtime/physics/exploration.py`

### 2025-12-29: Semantic intention (v2.1)

- **What:** Removed IntentionType enum from SubEntity — intention is now fully semantic via embedding
- **Why:** The enum (SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE) was rigid and keyword-based
- **Changes:**
  1. Removed `IntentionType` enum from `subentity.py`
  2. Removed `INTENTION_WEIGHTS` dict (0.1-0.5 per type)
  3. Added fixed `INTENTION_WEIGHT = 0.25` constant
  4. Removed `intention_type` field from `SubEntity` dataclass
  5. Updated `create_subentity()` to not take `intention_type` param
  6. Moved `IntentionType` to `cluster_presentation.py` (used for presentation filtering only)
- **Result:** Simpler, more flexible system. Any intention string can be used, embedded semantically.
- **Files:**
  - `runtime/physics/subentity.py` (removed enum, added constant)
  - `runtime/physics/cluster_presentation.py` (now defines IntentionType)
  - `runtime/physics/__init__.py` (updated exports)
  - `runtime/physics/exploration.py` (removed type parsing)
  - `mcp/server.py` (updated import)
  - `runtime/explore_cmd.py` (removed unused import)

### 2025-12-29: Crystallization fixes

- **What:** Fixed narrative crystallization to produce clean content
- **Why:** Multiple bugs causing garbage output
- **Bugs fixed:**
  1. `synthesis` field not saved → Added to `create_narrative()` query
  2. Path duplicates from backtracking → Deduplicate before rendering
  3. `unfold_*` producing garbage on non-grammar nodes → Direct prose generation
  4. `render_cluster(mode='response')` instead of `'crystallize'` → Fixed mode
- **Result:** Clean narratives with name, content, synthesis all populated
- **Files:**
  - `runtime/physics/exploration.py:777-808` (content generation)
  - `runtime/explore_cmd.py:234-246` (create_narrative with synthesis)

### 2025-12-29: MCP graph_query uses cluster presentation

- **What:** Wired `present_cluster()` into MCP `_ask_single()` response
- **Why:** Was doing ad-hoc formatting instead of using proper cluster presentation
- **Changes:**
  - Fetches actual content for each found narrative
  - Builds ClusterNodes with real synthesis
  - Calls `present_cluster()` to generate markdown
  - Returns `PresentedCluster.markdown` with markers (◆ RESPONSE, etc.)
- **Files:** `mcp/server.py:974-1078`

### 2025-12-29: MCP Tools documentation chain V2

- **What:** Updated entire docs/mcp-tools/ chain to V2:
  - OBJECTIVES: Simplified query interface goals
  - PATTERNS: Two tools (graph_query + procedures), no Cypher
  - BEHAVIORS: Observable effects with GIVEN/WHEN/THEN
  - ALGORITHM: SubEntity exploration + procedure flow
  - VALIDATION: Invariants for queries, procedures, graph, agents
  - IMPLEMENTATION: Code structure and data flow
  - SYNC: Current V2 state
- **Why:** Docs were V1, describing old membrane interface
- **Key changes:**
  - Removed: top_k, expand, format, include_membrane parameters
  - Added: intent parameter (affects SubEntity traversal weights)
  - Link type: all `:link`, no EXPRESSES/THEN/WITNESSED
  - Response: returns best narrative content, cleaned
- **Files:** `docs/mcp-tools/*.md` (7 files)

### 2025-12-29: Integrated schema cleanup into CLI and MCP

- **What:**
  1. Added graph health check to `mind status` CLI command
  2. Added graph schema check to MCP `doctor_check` tool (auto-fixes ≤10 invalid nodes)
- **Why:** Schema violations need to be visible and fixable
- **Files:** `cli/helpers/check_mind_status_in_directory.py`, `mcp/server.py`
- **Impact:** Both CLI and MCP now show graph health status

### 2025-12-29: Schema cleanup and validation

- **What:**
  1. Created `runtime/physics/graph/graph_schema_cleanup.py` with cleanup/fix/health functions
  2. Fixed ingestion to set `node_type` property on new nodes
  3. Migrated existing 732 nodes to have `node_type` property
- **Why:** Nodes without `node_type` cause exploration to fail
- **Impact:** Graph is 100% schema-compliant, future nodes will have correct properties

### 2025-12-29: Migrated node_type property

- **What:** Set `node_type` property from labels on 732 nodes
- **Why:** Exploration code checks property, not labels
- **Impact:** All nodes now have proper node_type (thing: 683, space: 43, actor: 16)

### 2025-12-29: Fixed crystallization loops in SubEntity exploration

- **What:** Two bugs fixed:
  1. Depth check overwrote CRYSTALLIZING→MERGING transitions
  2. CRYSTALLIZING→SEEKING created secondary loop (satisfaction not updated)
- **Why:** Exploration got stuck in infinite loops when trying to crystallize
- **Impact:** Crystallization now works — narratives are created and stored in graph
- **Files:** `runtime/physics/exploration.py:384-389, 816-832`
- **Verified:** Test shows State=merging, Satisfaction=0.50, Crystallized=narrative_cryst_xxx

### 2025-12-29: Documentation review

- **What:** Identified doc-code drift in SSE, CLI, MCP tools docs
- **Why:** Imported docs described non-existent implementations
- **Impact:** Rewrote CLI docs, renamed membrane_* to procedure_*

---


## TODO

### High Priority

- [x] Test that crystallization now works after bug fix — DONE
- [x] Run migration to set `node_type` property from labels — DONE (732 nodes)
- [x] Update ingestion to set `node_type` property on new nodes — DONE
- [x] Create schema cleanup function — DONE (`runtime/physics/graph/graph_schema_cleanup.py`)
- [x] Integrate schema cleanup into CLI status — DONE
- [x] Integrate schema cleanup into MCP doctor_check — DONE

### Medium Priority

- [ ] Make init dynamic (detect env, show what will be created, confirm)
- [ ] Test ConnectomeRunner dialogue flows end-to-end

### Low Priority

- [ ] Create narratives from docs content
- [ ] Add health checks for SubEntity exploration



---

# Archived: SYNC_Project_State.md

Archived on: 2025-12-29
Original file: SYNC_Project_State.md

---

## ACTIVE WORK

### Agent 1: CLI Commands

Build operational CLI for monitoring and control.

**Files:** `cli/commands/status.py`, `cli/commands/agents.py`, `cli/commands/tasks.py`, `cli/commands/events.py`

| Command | Purpose |
|---------|---------|
| `mind status` | Dashboard: agents, tasks, throttle, recent events, alerts |
| `mind agents list` | Who's running, what task, how long |
| `mind agents pause/stop/kill/enable` | Control agent lifecycle |
| `mind tasks list [--module X] [--capability Y]` | Pending, running, stuck, failed |
| `mind events [--last 30m] [filter]` | Timeline from all sources |
| `mind errors [--unresolved] [--type X]` | Error moments |

**Data sources:**
- Graph: task_run nodes, actor nodes
- Throttler: `get_throttler().active`
- Controller: `get_controller().mode`

---

### Agent 2: MCP Task Lifecycle ✅ COMPLETED

Built atomic task operations for agent workflow.

**Files:** `mcp/server.py` (tools added), `runtime/capability/graph_ops.py` (existing functions)

| Tool | Status |
|------|--------|
| `task_claim` | ✅ Implemented |
| `task_complete` | ✅ Implemented |
| `task_fail` | ✅ Implemented |
| `agent_heartbeat` | ✅ Implemented |

**Flow:**
```
agent_spawn → task_list → task_claim → procedure_start
→ [work + heartbeat] → procedure_continue → ...
→ task_complete/fail
```

**Wiring:**
- MCP tools in server.py (lines 402-469, 504-511, 1336-1473)
- Graph ops from mind-platform/runtime/capability/graph_ops.py
- Throttler integration via runtime/capability/throttler.py
- Agent registry integration via runtime/capability/agents.py

---


## RECENT CHANGES

### 2025-12-29: MCP Task Lifecycle Tools (Agent 2)

Added 4 MCP tools for atomic task lifecycle operations:

| Tool | Purpose |
|------|---------|
| `task_claim` | Claim task atomically with throttler check |
| `task_complete` | Mark done, release throttler slot |
| `task_fail` | Mark failed with reason, release slot |
| `agent_heartbeat` | Update heartbeat timestamp (60s interval) |

**Implementation:**
- Tool definitions: server.py lines 402-469
- Handler routing: server.py lines 504-511
- Implementation methods: server.py lines 1336-1473

**Wires to:**
- `runtime.capability.graph_ops`: claim_task, complete_task, fail_task, update_actor_heartbeat
- `runtime.capability.throttler`: can_claim, register_claim, on_complete, on_abandon
- `runtime.capability.agents`: get_registry().heartbeat()

### 2025-12-29: MCP Capability Integration

Wired capability runtime to MCP server with full operational loop.

**Files created in mind-mcp/:**
- `runtime/capability_integration.py` — CapabilityManager, CronScheduler wrapper

**MCP Server Updates (`mcp/server.py`):**
- Capability manager initialization on startup
- `init.startup` trigger fired on server start
- Cron scheduler runs in background thread
- New tools: `capability_status`, `capability_trigger`, `capability_list`

**Two-Level Loop Protection (`dispatch.py`):**

| Level | Problems | Mechanism |
|-------|----------|-----------|
| L1 | AGENT_DEAD, TASK_ORPHAN, TASK_STUCK, AGENT_STUCK | Atomic graph ops, no task_run |
| L2 | All others | Task_run with circuit breaker (3 fails = disable) |

**Circuit Breaker:**
- 3 failures in 24h → capability disabled
- Manual re-enable via `enable_capability()`
- Prevents infinite loops from failing checks

### 2025-12-29: Capability Runtime V2

Full operational system for capabilities with health checks, agents, throttling.

**Files created in mind-platform/runtime/capability/:**
- `decorators.py` — @check decorator, Signal, triggers.*
- `context.py` — CheckContext (read-only for checks)
- `loader.py` — discover_capabilities from .mind/capabilities/
- `registry.py` — TriggerRegistry (maps triggers to checks)
- `dispatch.py` — dispatch_trigger, create_task_runs
- `throttler.py` — Dedup, rate limit, queue limit
- `agents.py` — AgentRegistry, AgentController (kill switch)
- `graph_ops.py` — Task/agent state in graph

**Files created in mind-mcp/:**
- `cli/helpers/copy_capabilities_to_target.py`
- `runtime/core_utils.py` — get_capabilities_path()

**System capabilities:**
- `system-health` — Self-monitoring (stuck agents, orphan tasks)

### Earlier: Capabilities system

- Structure: `capabilities/{name}/` in mind-platform
- Copied to `.mind/capabilities/` on `mind init`
- Graph ingestion creates capability space

---

