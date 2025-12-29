# Project — Sync: Current State

```
LAST_UPDATED: 2025-12-29
UPDATED_BY: agent_claude
```

---

## CURRENT STATE

The mind-mcp project provides an MCP server for AI agents to interact with a knowledge graph. Core infrastructure is working:

- **Graph connection:** FalkorDB (`mind_mcp` graph)
- **Embedding service:** local (all-mpnet-base-v2), 768 dimensions
- **MCP server:** Full operational loop with capabilities, triggers, agents
- **Capability system:** Health checks, throttling, circuit breaker

### MCP Tools

| Tool | Purpose |
|------|---------|
| `graph_query` | Natural language queries via SubEntity traversal |
| `procedure_start/continue/abort/list` | Structured dialogue sessions |
| `doctor_check` | Health checks with assigned agents |
| `agent_list/spawn/status` | Work agent management |
| `task_list` | Pending tasks by module/objective |
| `capability_status` | System health: capabilities, throttler, controller |
| `capability_trigger` | Fire triggers manually for testing |
| `capability_list` | List loaded capabilities and checks |

### Startup Flow

```
MCP server start
    │
    ▼
Load capabilities from .mind/capabilities/
    │
    ▼
Register checks in TriggerRegistry
    │
    ▼
Start cron scheduler (background thread)
    │
    ▼
Fire init.startup trigger
    │
    ▼
Ready for tool calls
```

---

## ACTIVE WORK

None — system stable.

---

## RECENT CHANGES

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

## KNOWN ISSUES

None currently.

---

## HANDOFF: FOR AGENTS

**Current state:** Capability Runtime V2 implemented

### Architecture

```
Trigger (file, cron, git, etc.)
    │
    ▼
TriggerRegistry.get_checks()
    │
    ▼
dispatch_trigger() → runs checks
    │
    ▼
Signal (healthy/degraded/critical)
    │
    ▼
Throttler.can_create() — dedup, rate limit
    │
    ▼
create_task_runs() → graph nodes
    │
    ▼
Agent claims (pull model)
    │
    ▼
Agent executes (heartbeat 60s)
    │
    ▼
complete/fail
```

### Key Components

**Throttler** (`mind-platform/runtime/capability/throttler.py`):
```python
max_concurrent_agents = 5   # Max claimed by agents
max_pending_no_agent = 20   # Queue limit
max_per_module_hour = 10    # Rate limit
```

**Kill Switch** (`agents.py`, memory only):
- `pause()` — No new claims, running finish
- `stop()` — Stop after current step
- `kill(registry)` — Immediate stop, release all
- `enable()` — Resume (or MCP restart)

**Stuck Detection**:
- 5 min no heartbeat → STUCK
- 10 min no heartbeat → DEAD, auto-release task

### Trigger Types

| Category | Methods |
|----------|---------|
| `file` | on_create, on_modify, on_delete, on_move |
| `init` | after_scan, startup |
| `cron` | daily, weekly, hourly, every(min) |
| `git` | post_commit, pre_commit |
| `ci` | pull_request, push |
| `stream` | on_error, on_pattern |
| `graph` | on_node_create, on_link_create |
| `event` | on(name) |
| `hook` | on(name) |

### Graph Schema

**task_run node:**
```
status: pending|claimed|running|completed|failed|stuck
[executes] → task template
[concerns] → target node
[claimed_by] → actor
```

**actor node:**
```
status: idle|running|stuck|dead
last_heartbeat: timestamp
[works_on] → task_run
```

### Fail Loud

| Failure | Action |
|---------|--------|
| check.py crash | Log, disable capability |
| check timeout >30s | Log, mark failed |
| agent stuck 5min | Mark STUCK |
| agent dead 10min | Mark DEAD, release task |

### Visibility

**3 levels:**

1. **CLI status** (`mind status`):
   - Agents: running/stuck/dead counts
   - Tasks: pending/running/completed today
   - Throttle: current usage
   - Mode: active/paused/stopped

2. **Logs** (`.mind/logs/`):
   - `system.log` — Everything unified
   - `health.log` — Detections, signals
   - `tasks.log` — Create/claim/complete/fail
   - `agents.log` — Spawn/heartbeat/stuck/dead

3. **Graph queries** (`graph_query`):
   - "show me stuck tasks"
   - "what did witness_01 do today"
   - "which capabilities have failures"

**Log Events:**

| Event | Log | Level |
|-------|-----|-------|
| Problem detected | health | INFO |
| Task created/claimed/completed | tasks | INFO |
| Task failed | tasks | ERROR |
| Agent spawned | agents | INFO |
| Agent stuck | agents | WARN |
| Agent dead | agents | ERROR |
| Circuit breaker triggered | system | ERROR |
| Capability disabled | system | ERROR |

### Files

**mind-platform/runtime/capability/**
- decorators.py, context.py, loader.py
- registry.py, dispatch.py, throttler.py
- agents.py, graph_ops.py

**mind-mcp/cli/helpers/**
- copy_capabilities_to_target.py

**mind-platform/capabilities/system-health/**
- Self-monitoring capability (stuck agents, orphan tasks)

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Capabilities system implemented. Each capability is self-contained with full doc chain + tasks + skills + procedures.

**What was done:**
- Created `create-doc-chain` capability in `mind-platform/templates/capabilities/`
- Updated ingestion to handle capability structure
- On `mind init`, capabilities are copied to `.mind/capabilities/` and injected into graph

**No input needed** — system ready for more capabilities.

---

## ARCHIVE

Older init logs and content archived to: `SYNC_Project_State_archive_2025-12.md`

## Init: 2025-12-29 22:37

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 22:37

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 22:55

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings

---
