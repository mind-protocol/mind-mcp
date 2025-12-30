# Agent System — Implementation

```
STATUS: CANONICAL
UPDATED: 2025-12-30
```

---

## Module Structure

```
runtime/agents/
├── __init__.py          # Public exports
├── run.py               # run_work_agent, conversation capture
├── spawn.py             # spawn_work_agent, spawn_for_task
├── graph.py             # AgentGraph class
├── cli.py               # build_agent_command
├── postures.py          # PROBLEM_TO_POSTURE mapping
├── verification.py      # verify_completion
├── prompts.py           # System prompts, learnings
├── liveness.py          # Session detection
└── mapping.py           # Name normalization
```

---

## Key Classes

### RunResult (run.py)

```python
@dataclass
class RunResult:
    success: bool
    actor_id: str
    output: str
    error: Optional[str] = None
    duration_seconds: float = 0.0
    retried_without_continue: bool = False
    assignment_moment_id: Optional[str] = None
    completion_moment_id: Optional[str] = None
```

### _ConversationTurn (run.py)

```python
@dataclass
class _ConversationTurn:
    type: str  # "thinking", "text", "tool_use", "tool_result"
    content: str
    tool_name: Optional[str] = None
    tool_id: Optional[str] = None
```

### _ConversationBatch (run.py)

```python
@dataclass
class _ConversationBatch:
    summary: str      # Formatted turn summaries
    turn_count: int   # Number of turns in batch
    tools_used: List[str]  # Tool names used
```

### AgentGraph (graph.py)

```python
class AgentGraph:
    def __init__(self, graph_name: str = None)
    def set_agent_running(self, actor_id: str) -> bool
    def set_agent_ready(self, actor_id: str) -> bool
    def create_moment(self, actor_id, moment_type, prose, ...) -> str
    def link_moments(self, from_id, to_id, nature="precedes") -> bool
    def update_agent_cwd(self, actor_id, new_cwd) -> bool
    def boost_agent_energy(self, actor_id, amount) -> bool
```

---

## Key Functions

### run_work_agent (run.py)

Main entry point for running an agent.

```python
async def run_work_agent(
    actor_id: str,           # "AGENT_Witness"
    prompt: str,             # Task prompt
    target_dir: Path,        # Project root
    agent_provider: str = "claude",
    on_output: Optional[Callable] = None,
    timeout: float = 300.0,
    use_continue: bool = True,
    task_id: Optional[str] = None,
    problem_ids: Optional[List[str]] = None,
) -> RunResult
```

### get_active_agent_from_session (liveness.py)

Detect running agent from session file.

```python
def get_active_agent_from_session(target_dir: Path) -> Optional[str]:
    """Returns agent name if one is running, None otherwise."""
    actors_dir = target_dir / ".mind" / "actors"
    for agent_dir in actors_dir.iterdir():
        if (agent_dir / ".sessionId").exists():
            return agent_dir.name
    return None
```

### _detect_cd_commands (run.py)

Parse cd commands from Bash tool calls.

```python
def _detect_cd_commands(turns: List[_ConversationTurn]) -> List[str]:
    """Returns list of directories agent cd'd into."""
```

### _group_turns_into_batches (run.py)

Group conversation turns for moment creation.

```python
def _group_turns_into_batches(
    turns: List[_ConversationTurn],
    batch_size: int = 5,
    tool_output_max_len: int = 200,
) -> List[_ConversationBatch]
```

---

## Session File Location

```
.mind/actors/{agent_name}/.sessionId
```

- Written when agent starts (contains Claude session UUID)
- Deleted when agent finishes (in finally block)
- Checked by `get_active_agent_from_session()` for detection

---

## Graph Nodes Created

### Actor Node (updated)

```cypher
(:Actor {
    id: "AGENT_Witness",
    status: "running" | "ready",
    cwd: "/path/to/current/dir",
    updated_at_s: timestamp
})
```

### Moment Nodes (created per run)

```cypher
(:Moment {
    id: "moment:conversation:witness_abc0",
    type: "CONVERSATION",
    synthesis: "💭 thinking... 📝 output...",
    batch_index: 0,
    turn_count: 5,
    tools_used: ["Read", "Glob"],
    timestamp: 1234567890
})

(:Moment {
    id: "moment:completion:witness_abc1",
    type: "COMPLETION",
    synthesis: "Agent witness completed after 2 batches",
    status: "completed",
    duration_seconds: 15.2,
    total_turns: 8
})
```

### Links Created

```cypher
(actor)-[:LINK {verb: "creates"}]->(moment)
(moment1)-[:LINK {verb: "precedes"}]->(moment2)
(moment)-[:LINK {verb: "about"}]->(task)
```

---

## Dependencies

- `runtime/inject.py` — Moment creation uses inject()
- `runtime/infrastructure/database/` — Graph adapter
- `runtime/agents/cli.py` — Command building
- `runtime/agents/prompts.py` — System prompt loading
