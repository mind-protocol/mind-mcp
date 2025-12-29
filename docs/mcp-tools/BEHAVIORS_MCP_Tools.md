# BEHAVIORS: MCP Tools

```
STATUS: V2
PURPOSE: Observable effects of MCP tools
```

---

## Query Tool Behaviors

### graph_query (local)

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-GQ-1 | Queries use embedding search | No Cypher, semantic similarity only |
| B-GQ-2 | Multiple queries in parallel | Array processed concurrently |
| B-GQ-3 | Context is automatic | Actor derived from conversation |
| B-GQ-4 | Results include similarity | Each match has alignment score |
| B-GQ-5 | Expansion follows links | Connected nodes returned with matches |

#### GIVEN/WHEN/THEN

```
GIVEN graph_query is called with queries=["Who is Edmund?"]
WHEN the query executes
THEN embedding search runs on local graph
AND top-k similar nodes are returned
AND each result shows similarity score
```

```
GIVEN queries=["What is physics?", "Find actors"]
WHEN graph_query executes
THEN both queries run in parallel
AND results are labeled by query index
```

```
GIVEN expand=true (default)
WHEN matches are found
THEN linked nodes are included in results
AND connection types are shown
```

---

### membrane_query (cross-org)

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-MQ-1 | Searches membrane graph | Only public nodes from other orgs |
| B-MQ-2 | Same query format | Array of natural language questions |
| B-MQ-3 | Results include org_id | Source organization visible |
| B-MQ-4 | Independent of local | Membrane slow doesn't affect local |

#### GIVEN/WHEN/THEN

```
GIVEN membrane_query is called with queries=["Find ML experts"]
WHEN the query executes
THEN embedding search runs on membrane graph
AND only public=true nodes are searched
AND org_id is included in each result
```

```
GIVEN membrane graph is unavailable
WHEN membrane_query fails
THEN error returned with reason
AND local graph unaffected
```

---

## Procedure Tool Behaviors

### procedure_start / procedure_continue

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-PROC-1 | Start creates session | Session ID returned for continuation |
| B-PROC-2 | Steps execute in order | Each answer advances to next step |
| B-PROC-3 | Context preserved | Earlier answers available in later steps |
| B-PROC-4 | Abort cleans up | No partial commits on abort |
| B-PROC-5 | Completion commits | All changes atomic on final step |

#### GIVEN/WHEN/THEN

```
GIVEN procedure_start(procedure="create_doc_chain")
WHEN procedure exists
THEN session_id returned
AND first step question shown
```

```
GIVEN valid session_id and answer
WHEN procedure_continue is called
THEN answer validated
AND next step shown (or completion)
```

```
GIVEN procedure_abort(session_id)
WHEN session is active
THEN session terminated
AND no changes committed
```

---

## Agent Tool Behaviors

### agent_list

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-AL-1 | Shows all agents | ID, posture, status, energy |
| B-AL-2 | Status indicators | Ready (green) / Running (red) |
| B-AL-3 | Posture mappings | Which issues each posture handles |

### agent_spawn

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-AS-1 | Spawns by task_id | Full task context from graph |
| B-AS-2 | Spawns by issue | Creates task narrative for fix |
| B-AS-3 | Auto-selects posture | Derived from issue type |
| B-AS-4 | Returns execution result | Success, duration, output |

### agent_status

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-AST-1 | Gets agent state | Posture, status, energy |
| B-AST-2 | Sets agent state | ready or running |

---

## Task Tool Behaviors

### task_list

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-TL-1 | Shows pending tasks | Excludes completed |
| B-TL-2 | Groups by objective | documented, synced, maintainable |
| B-TL-3 | Filters by module | Optional path narrowing |
| B-TL-4 | Shows linked objectives | Task purpose visible |

---

## Doctor Tool Behaviors

### doctor_check

| ID | Behavior | Observable Effect |
|----|----------|-------------------|
| B-DC-1 | Runs health checks | Issues with severity returned |
| B-DC-2 | Assigns agents | Each issue mapped to posture |
| B-DC-3 | Filters by depth | links < docs < full |
| B-DC-4 | Filters by path | Optional path narrowing |
| B-DC-5 | Auto-fixes small issues | ≤10 invalid nodes fixed automatically |

---

## What Agents Cannot Do

| Blocked | Observable Effect |
|---------|-------------------|
| Call GraphOps | Error: mutations via procedures only |
| Pass Cypher | Error: use natural language |
| Provide context | Ignored: system derives automatically |
| Merge local + membrane | Error: use one tool or the other |

---

## Error Behaviors

| ID | Error | Observable Effect |
|----|-------|-------------------|
| B-ERR-1 | No queries array | "queries array required" |
| B-ERR-2 | Empty queries | Skipped silently |
| B-ERR-3 | No graph connection | "No graph connection available" |
| B-ERR-4 | Procedure not found | "Procedure X not found" |
| B-ERR-5 | Invalid session | "Session expired or invalid" |
| B-ERR-6 | Agent busy | "Agent X is already running" |

---

## CHAIN

- **Prev:** PATTERNS_MCP_Tools.md
- **Next:** ALGORITHM_MCP_Tools.md
- **Validates:** VALIDATION_MCP_Tools.md
