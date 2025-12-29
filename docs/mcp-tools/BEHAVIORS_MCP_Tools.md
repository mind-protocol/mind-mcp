# BEHAVIORS: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Observable effects of structured graph dialogues
```

---

## Doctor Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-DOC-1 | Doctor detects gap | Missing spec/coverage triggers skill load | G6 (dependency aware) |
| B-DOC-2 | Doctor queries graph | Calls graph API before deciding which protocol | G4 (context-rich) |
| B-DOC-3 | Doctor loads skill | Skill markdown loaded into agent context | G3 (workflow guided) |
| B-DOC-4 | Doctor selects protocol | Skill guides which protocol to run | G3 (workflow guided) |

---

## Skill Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-SKILL-1 | Skill provides domain knowledge | Agent understands context before answering | G4 (context-rich) |
| B-SKILL-2 | Skill maps situations to protocols | Clear guidance on which protocol when | G3 (workflow guided) |
| B-SKILL-3 | Skill shows patterns/anti-patterns | Agent avoids common mistakes | G5 (traceable) |
| B-SKILL-4 | Skill suggests queries | Agent knows what to look for | G4 (context-rich) |

---

## Protocol Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-PROT-1 | Protocol asks questions | Each `ask` step prompts agent | G2 (use-case oriented) |
| B-PROT-2 | Protocol queries graph | Each `query` step loads context | G4 (context-rich) |
| B-PROT-3 | Protocol branches | `branch` step routes based on condition | G6 (dependency aware) |
| B-PROT-4 | Protocol calls protocol | `call_protocol` step invokes sub-protocol | G6 (dependency aware) |
| B-PROT-5 | Protocol creates cluster | `create` step produces nodes + links | G1 (dense clusters) |

---

## Membrane Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-MEM-1 | Membrane loads protocol | YAML protocol loaded and parsed | G3 (workflow guided) |
| B-MEM-2 | Membrane validates input | Invalid input rejected with reason | G5 (traceable) |
| B-MEM-3 | Membrane allows enrichment | Agent can query graph mid-step | G4 (context-rich) |
| B-MEM-4 | Membrane manages call stack | Sub-protocols execute and return | G6 (dependency aware) |
| B-MEM-5 | Membrane commits cluster | All nodes/links created atomically | G1 (dense clusters) |
| B-MEM-6 | Membrane records moments | Every step creates moment with prose | G5 (traceable) |
| B-MEM-7 | Membrane reports summary | Completion returns structured output | G2 (use-case oriented) |

---

## Graph Output Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-GRAPH-1 | Cluster creation | Multiple nodes created in single operation | G1 (dense clusters) |
| B-GRAPH-2 | Cross-linking | Nodes linked to each other, not just container | G1 (dense clusters) |
| B-GRAPH-3 | Strength from answers | Link strength derived from agent input | G4 (context-rich) |
| B-GRAPH-4 | Moment trail | Every operation leaves moment with prose | G5 (traceable) |

---

## Session Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-SESS-1 | Session tracking | Session ID maintained across steps | G5 (traceable) |
| B-SESS-2 | Step sequencing | Steps execute in defined order | G3 (workflow guided) |
| B-SESS-3 | Context preservation | Earlier answers available in later steps | G4 (context-rich) |
| B-SESS-4 | Abort handling | Session can be aborted, no partial commits | G5 (traceable) |

---

## Error Behaviors

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-ERR-1 | Validation failure | Clear error message, step repeats | G5 (traceable) |
| B-ERR-2 | Spawn depth exceeded | Membrane fails with depth error | G6 (dependency aware) |
| B-ERR-3 | Query failure | Graph error surfaces to agent | G4 (context-rich) |
| B-ERR-4 | Session timeout | Stale session cleaned up | G5 (traceable) |

---

## Behavior Matrix: Membrane × Output

| Membrane | Nodes Created | Links Created | Moments |
|----------|---------------|---------------|---------|
| explore_space | 1 (exploration) | 2 (expresses, about) | 1 |
| add_objectives | 1 + N + M | contains × all, supports × N, bounds × M | 1 |
| add_invariant | 2 (validation + moment) | contains, ensures × behaviors | 1 |
| add_health_coverage | 4 (health + 2 docks + moment) | contains × 3, attached_to × 2, verifies × validations | 1 |
| record_work | 1 + N + M (progress + escalations + goals) | expresses, about × affected + new nodes | 1 |
| investigate | 1-2 (investigation + optional) | expresses, about | 1 |
| resolve_blocker | 2 (rationale + resolution) | about × (escalation + affected), expresses | 1 |

---

---

## MCP Tool Behaviors: doctor_check

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-DOC-CHK-1 | Doctor check runs health validation | Issues detected and returned with severity | G5 (traceable) |
| B-DOC-CHK-2 | Doctor check assigns agents | Each issue mapped to appropriate agent posture | G3 (workflow guided) |
| B-DOC-CHK-3 | Doctor check filters by depth | Only issues matching depth level returned | G2 (use-case oriented) |
| B-DOC-CHK-4 | Doctor check filters by path | Path filter narrows results to specific files | G4 (context-rich) |

### GIVEN/WHEN/THEN: doctor_check

**B-DOC-CHK-1: Basic Health Check**
```
GIVEN the MCP server is connected
WHEN doctor_check is called with no arguments
THEN it runs health checks at "docs" depth (default)
AND returns a list of issues with severity, type, path, and message
AND each issue includes assigned agent and agent status (ready/busy)
```

**B-DOC-CHK-2: Depth Filtering**
```
GIVEN issues exist at multiple depth levels
WHEN doctor_check is called with depth="links"
THEN only link-related issues are returned (fastest)

WHEN doctor_check is called with depth="docs"
THEN link and documentation issues are returned

WHEN doctor_check is called with depth="full"
THEN all issue types are returned (slowest, most comprehensive)
```

**B-DOC-CHK-3: Path Filtering**
```
GIVEN issues exist in multiple paths
WHEN doctor_check is called with path="docs/physics"
THEN only issues where path contains "docs/physics" are returned
AND other issues are excluded from results
```

**B-DOC-CHK-4: Agent Assignment**
```
GIVEN an issue of type STALE_SYNC is found
WHEN doctor_check formats the issue
THEN it assigns agent_herald (posture: herald)
AND shows whether agent_herald is ready or busy

GIVEN an issue of type UNDOCUMENTED is found
WHEN doctor_check formats the issue
THEN it assigns agent_voice (posture: voice)
```

**B-DOC-CHK-5: Edge Cases**
```
GIVEN no issues are found
WHEN doctor_check completes
THEN it returns "No issues found."

GIVEN the doctor check fails
WHEN an exception occurs
THEN it returns "Error running doctor: {error message}"
```

---

## MCP Tool Behaviors: agent_list

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-AGT-LST-1 | Agent list shows all agents | All work agents displayed with status | G3 (workflow guided) |
| B-AGT-LST-2 | Agent list shows posture mappings | Issue types mapped to postures shown | G4 (context-rich) |
| B-AGT-LST-3 | Agent list shows energy | Agent energy level visible for selection | G6 (dependency aware) |

### GIVEN/WHEN/THEN: agent_list

**B-AGT-LST-1: Basic Agent Listing**
```
GIVEN the agent graph is initialized
WHEN agent_list is called
THEN it returns all work agents
AND each agent shows: id, posture, status (ready/running), energy
AND ready agents show green indicator, running agents show red
```

**B-AGT-LST-2: Posture Mappings**
```
GIVEN agents exist for different postures
WHEN agent_list is called
THEN it shows the "Posture -> Issue Types" section
AND each posture lists the issue types it handles (truncated to 3 with "..." if more)
```

**B-AGT-LST-3: Edge Cases**
```
GIVEN the agent graph fails to initialize
WHEN agent_list is called
THEN it uses fallback mode and returns available agents (possibly empty)
```

---

## MCP Tool Behaviors: agent_spawn

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-AGT-SPN-1 | Agent spawn executes task | Agent actually runs and produces output | G3 (workflow guided) |
| B-AGT-SPN-2 | Agent spawn uses task context | Full task context with objectives and issues passed to agent | G4 (context-rich) |
| B-AGT-SPN-3 | Agent spawn tracks assignments | Assignment moment created linking agent to task | G5 (traceable) |
| B-AGT-SPN-4 | Agent spawn auto-selects posture | Agent posture derived from issue type | G6 (dependency aware) |

### GIVEN/WHEN/THEN: agent_spawn

**B-AGT-SPN-1: Spawn by Task ID**
```
GIVEN a task exists in the graph with id "task_fix_physics_sync"
WHEN agent_spawn is called with task_id="task_fix_physics_sync"
THEN the server queries the graph for full task context
AND retrieves linked objectives and issues
AND builds a rich prompt with task name, module, skill, objectives, and issues
AND spawns the appropriate agent to execute
AND returns execution results with success status and duration
```

**B-AGT-SPN-2: Spawn by Issue**
```
GIVEN no task_id is provided
WHEN agent_spawn is called with issue_type="STALE_SYNC" and path="docs/physics/SYNC.md"
THEN a task narrative is created for the fix
AND an issue narrative is upserted in the graph
AND the appropriate agent (agent_herald for STALE_SYNC) is selected
AND the agent executes with a prompt describing the issue
```

**B-AGT-SPN-3: Agent Selection**
```
GIVEN issue_type="UNDOCUMENTED" and no agent_id specified
WHEN agent_spawn is called
THEN it looks up the posture for UNDOCUMENTED (voice)
AND selects agent_voice automatically

GIVEN agent_id="agent_fixer" is explicitly provided
WHEN agent_spawn is called
THEN it uses agent_fixer regardless of issue type
```

**B-AGT-SPN-4: Provider Selection**
```
GIVEN provider="gemini" is specified
WHEN agent_spawn is called
THEN the agent uses Gemini as the LLM provider

GIVEN no provider is specified
WHEN agent_spawn is called
THEN the agent uses "claude" as the default provider
```

**B-AGT-SPN-5: Agent Availability**
```
GIVEN agent_witness is currently running
WHEN agent_spawn is called with agent_id="agent_witness"
THEN it returns error: "agent_witness is already running. Choose another agent or wait."
```

**B-AGT-SPN-6: Edge Cases**
```
GIVEN neither task_id nor (issue_type + path) is provided
WHEN agent_spawn is called
THEN it returns error: "Either task_id OR (issue_type + path) required"

GIVEN task_id="nonexistent_task" is provided
WHEN the graph query finds no matching task
THEN it returns error: "Task 'nonexistent_task' not found in graph"

GIVEN no graph connection is available
WHEN agent_spawn is called with task_id
THEN it returns error: "No graph connection for task lookup"
```

**B-AGT-SPN-7: Execution Result**
```
GIVEN agent execution completes
WHEN the spawn finishes
THEN the response includes:
  - Agent ID and posture
  - Task ID or issue type/path
  - Provider used
  - Success boolean
  - Duration in seconds
  - Assignment moment ID (if created)
  - Agent output (truncated to 1000 chars)
  - Any errors encountered
```

---

## MCP Tool Behaviors: agent_status

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-AGT-STS-1 | Agent status retrieval | Current agent state returned | G5 (traceable) |
| B-AGT-STS-2 | Agent status modification | Agent status can be set to ready/running | G3 (workflow guided) |
| B-AGT-STS-3 | Agent status shows full info | Energy, weight, posture all visible | G4 (context-rich) |

### GIVEN/WHEN/THEN: agent_status

**B-AGT-STS-1: Get Agent Status**
```
GIVEN agent_witness exists in the agent graph
WHEN agent_status is called with agent_id="agent_witness"
THEN it returns:
  - Agent ID
  - Posture (witness)
  - Status (ready/running)
  - Energy level (0.0-1.0)
  - Weight value
```

**B-AGT-STS-2: Set Agent Status**
```
GIVEN agent_fixer exists and is ready
WHEN agent_status is called with agent_id="agent_fixer" and set_status="running"
THEN agent_fixer's status is updated to "running"
AND confirmation message returned: "Agent agent_fixer status set to running"

GIVEN agent_fixer is running
WHEN agent_status is called with agent_id="agent_fixer" and set_status="ready"
THEN agent_fixer's status is updated to "ready"
```

**B-AGT-STS-3: Edge Cases**
```
GIVEN no agent_id is provided
WHEN agent_status is called
THEN it returns error: "agent_id is required"

GIVEN agent_id="agent_nonexistent" does not exist
WHEN agent_status is called (get mode)
THEN it returns error: "Agent agent_nonexistent not found"
```

---

## MCP Tool Behaviors: task_list

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-TSK-LST-1 | Task list shows pending tasks | Non-completed tasks displayed | G3 (workflow guided) |
| B-TSK-LST-2 | Task list shows objectives | Tasks linked to their objectives | G4 (context-rich) |
| B-TSK-LST-3 | Task list supports filtering | Filter by module or objective type | G2 (use-case oriented) |

### GIVEN/WHEN/THEN: task_list

**B-TSK-LST-1: Basic Task Listing**
```
GIVEN tasks exist in the graph as Narrative nodes with type='task'
WHEN task_list is called with no arguments
THEN it returns up to 20 tasks (default limit)
AND tasks are ordered by creation date (newest first)
AND completed tasks are excluded
AND each task shows: name, ID, module, skill, status icon, linked objectives
```

**B-TSK-LST-2: Module Filtering**
```
GIVEN tasks exist for modules "physics" and "auth"
WHEN task_list is called with module="physics"
THEN only tasks where module="physics" are returned
```

**B-TSK-LST-3: Objective Filtering**
```
GIVEN tasks are linked to objectives like "documented", "synced", "maintainable"
WHEN task_list is called with objective="documented"
THEN only tasks serving the "documented" objective are returned
```

**B-TSK-LST-4: Limit Control**
```
GIVEN 50 tasks exist
WHEN task_list is called with limit=10
THEN only 10 tasks are returned
```

**B-TSK-LST-5: Status Icons**
```
GIVEN tasks have different statuses
WHEN task_list formats results
THEN pending tasks show hourglass icon
AND in_progress tasks show cycle icon
AND other statuses show pause icon
```

**B-TSK-LST-6: Edge Cases**
```
GIVEN no graph connection is available
WHEN task_list is called
THEN it returns error: "No graph connection"

GIVEN no tasks exist in the graph
WHEN task_list is called
THEN it returns: "No tasks found. Run `doctor` first to create tasks."
```

---

## MCP Tool Behaviors: graph_query

| ID | Behavior | Observable Effect | Linked Goal |
|----|----------|-------------------|-------------|
| B-GRQ-1 | Graph query uses natural language | Semantic search across graph | G4 (context-rich) |
| B-GRQ-2 | Graph query creates moments | Each query creates traceable moment | G5 (traceable) |
| B-GRQ-3 | Graph query runs concurrently | Multiple queries execute in parallel | G2 (use-case oriented) |
| B-GRQ-4 | Graph query supports formats | Markdown or JSON output available | G4 (context-rich) |

### GIVEN/WHEN/THEN: graph_query

**B-GRQ-1: Basic Query**
```
GIVEN a graph with nodes exists
WHEN graph_query is called with queries=["Who is Edmund?"]
THEN it creates a query moment linked to the actor
AND runs SubEntity exploration from the moment
AND returns found narratives with alignment scores
AND shows exploration state and satisfaction level
```

**B-GRQ-2: Multiple Queries**
```
GIVEN multiple questions need answers
WHEN graph_query is called with queries=["Who is Edmund?", "What oaths exist?"]
THEN both queries run concurrently (async)
AND each query result is labeled with "## Query N: {question}"
AND results are formatted together in the response
```

**B-GRQ-3: Top-K Control**
```
GIVEN a query matches many nodes
WHEN graph_query is called with queries=["Find all characters"] and top_k=10
THEN up to 10 matching narratives are returned per query
```

**B-GRQ-4: Output Formats**
```
GIVEN format="md" (default)
WHEN graph_query returns results
THEN output is formatted as markdown with headers and bullet points

GIVEN format="json"
WHEN graph_query returns results
THEN output is structured JSON with query/result pairs
```

**B-GRQ-5: Actor Resolution**
```
GIVEN actor_id="actor_claude" is specified
WHEN the actor exists in the graph
THEN the query moment is linked to that actor

GIVEN actor_id="actor_nonexistent" is specified
WHEN the actor does not exist
THEN a random existing actor is selected from the graph
AND the query proceeds with that actor
```

**B-GRQ-6: Debug Mode**
```
GIVEN debug=true is specified
WHEN graph_query executes
THEN additional debug information is included:
  - Actor used
  - Timeout value
  - Top K value
  - Moment creation confirmation
  - Linked previous moments
  - Witnesses in same space
  - Exploration completion time
  - Exploration state and satisfaction
  - Log file path
```

**B-GRQ-7: Moment Linking**
```
GIVEN the actor has previous moments
WHEN a new query is made
THEN the new moment is linked via THEN to the previous moment
AND actors in the same space are linked via WITNESSED to the moment
```

**B-GRQ-8: Timeout Control**
```
GIVEN timeout=60 is specified
WHEN graph_query executes
THEN the SubEntity exploration times out after 60 seconds
```

**B-GRQ-9: Edge Cases**
```
GIVEN no queries array is provided
WHEN graph_query is called
THEN it returns error: "'queries' array is required"

GIVEN queries contains empty strings
WHEN graph_query filters queries
THEN empty/whitespace-only queries are skipped

GIVEN no graph connection is available
WHEN graph_query is called
THEN it returns error: "No graph connection available"

GIVEN exploration fails with exception
WHEN debug=true
THEN the full traceback is included in the error response
```

---

## CHAIN

- **Prev:** PATTERNS_MCP_Tools.md
- **Next:** ALGORITHM_MCP_Tools.md
- **Validates:** VALIDATION_MCP_Tools.md
