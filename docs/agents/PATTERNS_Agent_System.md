# Agent System — Design Patterns

```
STATUS: CANONICAL
UPDATED: 2025-12-30
```

---

## Purpose

The agent system enables AI agents (Claude, Gemini, Codex) to autonomously fix project issues detected by health checks. This document explains the architecture and how the components connect.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DETECTION LAYER                              │
│  Capabilities with @check decorators detect issues                  │
│  .mind/capabilities/{name}/runtime/checks.py                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Signal (healthy/degraded/critical)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        TASK LAYER                                   │
│  Issues become task_run nodes in graph                              │
│  Throttler controls concurrency and rate limits                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ task_run node
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                                  │
│  Agents claim tasks and execute fixes                               │
│  runtime/agents/ — spawn, verify, track                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ subprocess (claude/gemini/codex CLI)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        EXECUTION LAYER                              │
│  External LLM runs with tools: Bash, Read, Edit, Write, etc.        │
│  Makes changes, commits, updates SYNC                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Capabilities (Detection)

Each capability has health checks that detect issues:

```python
# .mind/capabilities/create-doc-chain/runtime/checks.py

@check(
    id="chain_completeness",
    triggers=[triggers.cron.daily(), triggers.init.after_scan()],
    on_problem="INCOMPLETE_CHAIN",
    task="TASK_create_doc",
)
def chain_completeness(ctx) -> dict:
    # Detect missing docs
    if missing:
        return Signal.degraded(missing=list(missing))
    return Signal.healthy()
```

**Location:** `.mind/capabilities/{name}/runtime/checks.py`
**Registry:** `CHECKS = [check1, check2, ...]` list at bottom

### 2. Triggers

Triggers fire checks at specific moments:

| Category | Examples |
|----------|----------|
| `cron` | `daily()`, `hourly()`, `every(60)` |
| `file` | `on_create()`, `on_modify()`, `on_delete()` |
| `init` | `after_scan()`, `startup()` |
| `git` | `post_commit()`, `pre_commit()` |
| `event` | `on(name)` |

### 3. Throttler

Controls task creation and agent concurrency:

```python
max_concurrent_agents = 5   # Max tasks claimed by agents
max_pending_no_agent = 20   # Queue limit before blocking
max_per_module_hour = 10    # Rate limit per module
```

**Deduplication:** Same issue won't create duplicate tasks within 1 hour.

### 4. Agent Selection

Agents are selected by posture based on issue type:

| Posture | Issue Types |
|---------|-------------|
| `witness` | STALE_SYNC, STALE_IMPL, DOC_DELTA |
| `groundwork` | UNDOCUMENTED, INCOMPLETE_CHAIN, MISSING_TESTS |
| `fixer` | STUB_IMPL, INCOMPLETE_IMPL, NO_DOCS_REF |
| `weaver` | BROKEN_IMPL_LINK, DOC_LINK_INTEGRITY |
| `scout` | MONOLITH, LARGE_DOC_MODULE |
| `steward` | ESCALATION, SUGGESTION |

**Location:** `runtime/agents/postures.py`

### 5. Agent Execution

Agents run as subprocesses:

```python
# Build command
cmd = build_agent_command(
    agent="claude",
    prompt=prompt,
    system_prompt=system_prompt,
    stream_json=True,
)

# Execute
process = subprocess.Popen(cmd, ...)
```

**Tools available:** Bash, Read, Edit, Write, Glob, Grep, WebFetch, TodoWrite

### 6. Verification

After agent completes, verify the fix:

```python
verification_results = verify_completion(
    issue=issue,
    target_dir=target_dir,
    head_before=head_before,
    head_after=head_after,
)

if all_passed(verification_results):
    # Success
else:
    # Retry with feedback (up to 3 times)
```

### 7. Session Tracking

Agents track their sessions via files for status detection:

```
.mind/actors/{name}/.sessionId    # Written on start, deleted on finish
```

**Detection:**
```python
from runtime.agents import get_active_agent_from_session

# Check if any agent is currently running
active = get_active_agent_from_session(Path("."))  # Returns agent name or None
```

**Use cases:**
- MCP auto-fills actor_id from active session
- Status dashboard shows running agents
- Prevents duplicate agent spawns

### 8. Conversation Capture

Agent conversations are captured as graph moments:

```
Agent Run
    │
    ▼
Parse stream-json output
    │
    ▼
Capture turns: thinking, text, tool_use, tool_result
    │
    ▼
Group into batches of 5
    │
    ▼
Create CONVERSATION moment per batch
    │
    ▼
Chain moments with --precedes-->
    │
    ▼
Create final COMPLETION moment
```

**Moment structure:**
```
moment:conversation:witness_abc0
  synthesis: "💭 thinking... 📝 output... 🔧 Read(...) → result..."
  batch_index: 0
  turn_count: 5
  tools_used: ["Read", "Glob"]

moment:completion:witness_abc1
  synthesis: "Agent witness completed after 2 batches"
  status: completed
  duration_seconds: 15.2
  total_turns: 8
```

### 9. CWD Tracking

Agent's current working directory is tracked from `cd` commands:

```python
# Detected from Bash tool calls
if turn.tool_name == "Bash" and "cd" in command:
    # Extract path, update agent's cwd property
    agent_graph.update_agent_cwd(actor_id, new_path)
```

**Graph state:**
```
(:Actor {
  id: "AGENT_Witness",
  cwd: "/home/user/project/docs",  # Updated after cd
  status: "ready"
})
```

---

## Data Flow

### 1. Detection → Task Creation

```
Trigger fires (cron, file change, etc.)
    │
    ▼
TriggerRegistry.get_checks(trigger)
    │
    ▼
dispatch_trigger() runs each check
    │
    ▼
Check returns Signal.degraded/critical
    │
    ▼
Throttler.can_create() — dedup, rate limit
    │
    ▼
create_task_run() — graph node created
    │
    ▼
task_run status: "pending"
```

### 2. Task → Agent Assignment

```
agent_spawn(task_type="X", path="...")
    │
    ▼
Select agent by posture mapping
    │
    ▼
Throttler.can_claim() — concurrency check
    │
    ▼
Graph: set actor status = "running"
    │
    ▼
Graph: link actor → task_run
    │
    ▼
task_run status: "claimed"
```

### 3. Agent Execution

```
Build prompt with:
  - Issue details
  - Instructions (from work_instructions.py)
  - Docs to read
  - System prompt (posture + learnings)
    │
    ▼
Spawn subprocess: claude/gemini/codex
    │
    ▼
Agent works (with heartbeat every 60s)
    │
    ▼
Agent commits changes
    │
    ▼
Verify completion
    │
    ▼
task_run status: "completed" or "failed"
```

---

## Graph Schema

### Actor Node (Agent)

```
(:Actor {
  id: "agent_witness",
  name: "witness",
  type: "agent",
  status: "ready" | "running" | "stuck" | "dead",
  posture: "witness",
  last_heartbeat: timestamp,
  energy: 0.0-1.0
})
```

### Task Run Node

```
(:Narrative {
  id: "task_run_abc123",
  type: "task_run",
  status: "pending" | "claimed" | "running" | "completed" | "failed",
  task_type: "STALE_SYNC",
  path: "docs/physics/SYNC.md",
  created: timestamp,
  claimed_at: timestamp,
  completed_at: timestamp
})
```

### Links

```
(actor)-[:WORKS_ON]->(task_run)
(task_run)-[:EXECUTES]->(task_template)
(task_run)-[:CONCERNS]->(target_node)
```

---

## Entry Points

### CLI

```bash
# Run work on all detected issues
mind work --depth docs --max 10

# Filter by issue type
mind work --type UNDOCUMENTED --max 5
```

### MCP Tools

```
# List tasks
task_list(limit=10)

# Spawn agent for specific issue
agent_spawn(task_type="STALE_SYNC", path="docs/physics/SYNC.md")

# Spawn agent for task node
agent_spawn(task_id="narrative:task:TASK_create_doc")
```

### Python

```python
from runtime.agents import spawn_work_agent

result = await spawn_work_agent(
    task_type="UNDOCUMENTED",
    path="runtime/schema",
    target_dir=Path("."),
    agent_provider="claude",
)
```

---

## File Structure

```
runtime/
├── agents/
│   ├── __init__.py          # Public API
│   ├── run.py               # run_work_agent, conversation capture
│   ├── spawn.py             # spawn_work_agent, spawn_for_task
│   ├── graph.py             # AgentGraph, status, moments, cwd
│   ├── cli.py               # build_agent_command
│   ├── postures.py          # PROBLEM_TO_POSTURE, posture configs
│   ├── verification.py      # verify_completion
│   ├── prompts.py           # AGENT_SYSTEM_PROMPT, build_agent_prompt
│   ├── liveness.py          # Session detection, get_active_agent_from_session
│   └── mapping.py           # Agent name normalization
│
├── capability/
│   ├── decorators.py        # @check, Signal, triggers
│   ├── registry.py          # TriggerRegistry
│   ├── dispatch.py          # dispatch_trigger
│   ├── throttler.py         # Throttler
│   └── loader.py            # discover_capabilities
│
.mind/capabilities/
├── create-doc-chain/
│   └── runtime/checks.py    # Health checks for this capability
├── sync-state/
│   └── runtime/checks.py
└── ...
```

---

## Adding New Detection

1. **Create capability** (if new category):
   ```
   .mind/capabilities/my-capability/
   ├── PATTERNS.md
   ├── ALGORITHM.md
   └── runtime/
       ├── __init__.py
       └── checks.py
   ```

2. **Add check**:
   ```python
   @check(
       id="my_check",
       triggers=[triggers.cron.daily()],
       on_problem="MY_TASK_TYPE",
       task="TASK_fix_my_issue",
   )
   def my_check(ctx) -> dict:
       # Detection logic
       if problem:
           return Signal.degraded(details=...)
       return Signal.healthy()

   CHECKS = [my_check]
   ```

3. **Add posture mapping** (if new issue type):
   ```python
   # runtime/agents/postures.py
   PROBLEM_TO_POSTURE["MY_TASK_TYPE"] = "fixer"
   ```

4. **Add instructions** (for work prompt):
   ```python
   # runtime/agents/instructions.py
   ISSUE_INSTRUCTIONS["MY_TASK_TYPE"] = {
       "view": "VIEW_Fix_My_Issue.md",
       "docs_to_read": ["docs/relevant/PATTERNS.md"],
       "prompt": "Fix the issue at {path}...",
   }
   ```

---

## Deprecation: Doctor Module

The `doctor` module is being replaced by capability health checks:

| Old (doctor) | New (capabilities) |
|--------------|-------------------|
| `runtime/doctor_checks_*.py` | `.mind/capabilities/*/runtime/checks.py` |
| `run_doctor()` | `fire_trigger("init.after_scan")` |
| `DoctorIssue` | `Signal.degraded/critical` |
| `mind doctor` | `mind status` + capability checks |

**Migration:** Detection logic moves to capability checks. The capability system provides:
- Declarative triggers (cron, file, git)
- Automatic task creation
- Circuit breaker for failing checks
- Better organization (one capability = one concern)
