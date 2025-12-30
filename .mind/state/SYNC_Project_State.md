# Project — Sync: Current State

```
LAST_UPDATED: 2025-12-30
UPDATED_BY: agent_claude
```

## Recent Changes

### 2025-12-30: Agent Session Tracking and Conversation Capture

**What:** Agents now track their sessions and capture full conversations as graph moments.

**Session-based agent tracking:**
- Agent writes `session_id` to `.mind/actors/{name}/.sessionId` on start
- File deleted when agent finishes
- `get_active_agent_from_session(target_dir)` detects running agent for MCP auto-fill
- Replaces jsonl-based detection (simpler, more reliable)

**Conversation capture:**
- Full conversation parsed from Claude's `--output-format stream-json --verbose`
- Captures: thinking blocks, text output, tool_use calls, tool_result responses
- Turns grouped into batches of 5 for manageable moment sizes
- Tool output truncated to 200 chars; thinking/text kept full
- Creates CONVERSATION moment per batch, chained with `--precedes-->`
- Final COMPLETION moment summarizes the run

**CD command detection:**
- Parses Bash tool calls for `cd` commands
- Updates agent's `cwd` property on actor node
- Links to existing folder Space nodes if found

**Files modified:**
- `runtime/agents/run.py` — Session file write, conversation parsing, batching, cd detection
- `runtime/agents/graph.py` — `create_moment()` uses inject(), added `link_moments()`, `update_agent_cwd()`
- `runtime/agents/liveness.py` — Added `get_active_agent_from_session()`, `get_all_active_agents_from_sessions()`
- `runtime/agents/__init__.py` — Exports new functions

**Usage:**
```python
from runtime.agents import run_work_agent, get_active_agent_from_session

# Check if any agent is currently running
active = get_active_agent_from_session(Path("."))  # Returns agent name or None

# Run agent - session tracked automatically
result = await run_work_agent(
    actor_id="AGENT_Witness",
    prompt="Read README.md and cd into docs/",
    target_dir=Path("."),
)

# Result includes moment IDs
print(result.completion_moment_id)  # moment:completion:witness_abc1
```

**Graph state after run:**
```
AGENT_Witness:
  cwd: /home/user/project/docs
  status: ready

Moments created:
  moment:conversation:witness_abc0 (batch 0)
  moment:conversation:witness_abc1 (batch 1)
  moment:completion:witness_abc2 (final)
```

---

### 2025-12-30: Canonical Unified Injection Function

**What:** Created `runtime/inject.py` as the single entry point for all graph injection operations.

**Why:** Consolidate duplicate injection code scattered across modules. Previously, `procedure_runner.py`, `symbol_extractor.py`, and ingest modules each had their own `_upsert_node`/`_upsert_link` functions with inconsistent embedding and synthesis handling.

**Key features of inject():**
- Single function handles both nodes and links (detects by `from`/`to` vs `id`)
- Automatic synthesis generation from physics state (via `runtime/physics/synthesis.py`)
- Embedding generation from synthesis
- Nature string → physics floats conversion
- Context linking (actor, space, moment) with `with_context` flag
- Moment chaining per actor (temporal chain)
- Fail loud (no silent failures)

**with_context flag:**
- `with_context=True` (default): Query-driven injection — creates moment, chains to previous, links to actor/space
- `with_context=False`: Init-time bulk load — no moments, no context linking (used during `mind init`)

**Files created/modified:**
- `runtime/inject.py` — NEW: Canonical injection module
- `runtime/physics/synthesis.py` — Added `synthesize_node()`, `synthesize_link_full()`
- `runtime/procedure_runner.py` — `_upsert_node`, `_upsert_link` now delegate to `inject()`
- `runtime/symbol_extractor.py` — `_upsert_symbol`, `_upsert_link` now delegate to `inject()`
- `runtime/ingest/actors.py` — NEW: Actor ingestion using `inject()`
- `runtime/ingest/capabilities.py` — Now uses `inject()`

**Usage pattern:**
```python
from runtime.inject import inject, set_actor

# Set active actor (task is auto-detected from graph)
set_actor("actor:agent_witness")

# Inject node - automatically creates moment and links
inject(adapter, {
    "id": "narrative:finding_123",
    "content": "Found the bug in line 42",
})

# Inject link
inject(adapter, {
    "from": "space:root",
    "to": "space:actors",
    "nature": "contains",
})

# Bulk init (no context)
inject(adapter, {...}, with_context=False)
```

---

### 2025-12-29: MCP Task Lifecycle Tools Implemented

**What:** Implemented and tested MCP tools for task lifecycle management.

**Tools added:**
- `task_claim` — Atomically claim a pending task for an agent
- `task_complete` — Mark a claimed task as completed
- `task_fail` — Mark a task as failed with reason
- `agent_heartbeat` — Update actor heartbeat timestamp

**Key fixes:**
- FalkorDB doesn't have `datetime()` function — use ISO timestamp strings instead
- Throttler only knows tasks from current session — skip throttler check for older tasks
- Use direct graph queries instead of mind-platform's graph_ops (interface mismatch)

**Files modified:**
- `mcp/server.py` — Task lifecycle tool implementations
- `runtime/capability_graph_adapter.py` — Sets `status='pending'` on task_run creation
- `runtime/capability_integration.py` — Exports graph_ops functions

**Tested flows:**
```
task_claim(task_id, actor_id) → "Task claimed"
task_complete(task_id) → "Task completed"
task_fail(task_id, reason) → "Task failed: reason"
agent_heartbeat(actor_id, step) → "Heartbeat: actor_id (step N)"
```

---

### 2025-12-29: Agent Prompts Module Extraction

**What:** Created `runtime/agents/prompts.py` by extracting prompt-related code from `runtime/work_core.py`

**Why:** Consolidating agent-related code into the `runtime/agents/` package for better module organization. The `__init__.py` already expects this module.

**Changes:**
- Created `/home/mind-protocol/mind-mcp/runtime/agents/prompts.py` with:
  - `AGENT_SYSTEM_PROMPT` constant (2842 chars)
  - `get_learnings_content(target_dir: Path) -> str` function
  - `build_agent_prompt(issue, instructions, target_dir, github_issue_number)` function
  - `split_docs_to_read(docs_to_read, target_dir)` helper function
  - `_detect_recent_issue_number(target_dir, max_commits)` helper function
- Added docstring referencing `docs/agents/PATTERNS_Agent_System.md`
- Proper imports: `Path`, `Any`, `Dict`, `List`, `Optional` from typing, `re`, `subprocess`

**Note:** The `runtime/agents/__init__.py` has a pre-existing import error related to `spawn.py` (missing `spawn_for_task`), unrelated to this change.

---

### 2025-12-29: Agent CLI Module Reorganization

**What:** Copied `runtime/agent_cli.py` to `runtime/agents/cli.py`

**Why:** Reorganizing agent-related code into the `runtime/agents/` package for better module organization.

**Changes:**
- Created `/home/mind-protocol/mind-mcp/runtime/agents/cli.py`
- Updated docs reference from `docs/mind_cli_core/OBJECTIVES_mind_cli_core.md` to `docs/agents/PATTERNS_Agent_System.md`
- Code logic unchanged

---

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
| `task_claim` | Atomic: claim task, update graph, register throttler |
| `task_complete` | Mark done, update graph, release throttler slot |
| `task_fail` | Mark failed, record reason, release slot |
| `agent_heartbeat` | Update last_heartbeat on actor node (60s interval) |
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


---

## ARCHIVE

Older content archived to: `SYNC_Project_State_archive_2025-12.md`

## Init: 2025-12-30 02:49

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 03:43

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 03:51

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---
