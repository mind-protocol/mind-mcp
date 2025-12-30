# VALIDATION: MCP Tools

```
STATUS: V2
PURPOSE: Invariants that must hold for MCP tools
```

---

## Query Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-Q-1 | `queries` array required and non-empty | Tool fails to execute | HIGH |
| V-Q-2 | Each query produces embedding search | No semantic matching | HIGH |
| V-Q-3 | Results include similarity scores | Quality unknown | MED |
| V-Q-4 | Intent affects traversal weights | Wrong exploration path | MED |
| V-Q-5 | Exploration terminates (satisfaction or max steps) | Infinite loop | HIGH |

### Validation Tests

```
GIVEN graph_query(queries=[])
WHEN executed
THEN error: "queries array required"

GIVEN graph_query(queries=["Find X"], intent="verify")
WHEN SubEntity explores
THEN VERIFY intention weights applied
AND exploration terminates

GIVEN graph_query returns
THEN each result has alignment score 0.0-1.0
```

---

## Procedure Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-PROC-1 | Session ID unique per start | Session collision | HIGH |
| V-PROC-2 | Steps execute in defined order | Workflow corrupted | HIGH |
| V-PROC-3 | Answers validated before advancing | Invalid data | HIGH |
| V-PROC-4 | Abort commits nothing | Partial changes | HIGH |
| V-PROC-5 | Complete commits atomically | Incomplete changes | HIGH |

### Validation Tests

```
GIVEN procedure_start(procedure="X")
WHEN procedure exists
THEN session_id is unique UUID
AND first step returned

GIVEN procedure_continue with invalid answer
WHEN validation fails
THEN error returned
AND step NOT advanced

GIVEN procedure_abort(session_id)
WHEN session active
THEN no nodes created
AND no links created
```

---

## Graph Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-G-1 | All nodes have valid `node_type` | Schema violation | HIGH |
| V-G-2 | All links reference existing nodes | Dangling links | HIGH |
| V-G-3 | All links are type `:link` | Schema violation | HIGH |
| V-G-4 | Moments have actor link | Unattributed | HIGH |
| V-G-5 | Narratives have synthesis | Not searchable | MED |

### Validation Tests

```
GIVEN node creation
THEN node_type IN ['actor', 'moment', 'narrative', 'space', 'thing']

GIVEN link creation
THEN link type = ':link'
AND from_id exists in graph
AND to_id exists in graph

GIVEN narrative creation
THEN synthesis field populated
AND synthesis is embeddable text
```

---

## Agent Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-A-1 | Only one agent running at a time | Resource conflict | MED |
| V-A-2 | Agent status transitions: ready → running → ready | State corruption | HIGH |
| V-A-3 | Spawn requires task_id OR (task_type + path) | Incomplete context | HIGH |
| V-A-4 | Running agent returns result | Orphaned process | MED |

### Validation Tests

```
GIVEN agent_spawn when agent running
THEN error: "Agent X is already running"

GIVEN agent_spawn(task_id=None, task_type=None)
THEN error: "Either task_id or (task_type + path) required"

GIVEN agent completes
THEN status = "ready"
AND result returned
```

---

## Doctor Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-D-1 | Check returns issues with assigned agents | No actionability | MED |
| V-D-2 | Depth respected: links < docs < full | Wrong scope | LOW |
| V-D-3 | Path filter applied correctly | Wrong scope | LOW |
| V-D-4 | Auto-fix only for ≤10 schema issues | Uncontrolled changes | MED |

### Validation Tests

```
GIVEN doctor_check(depth="links")
THEN only link checks run
AND doc checks NOT run

GIVEN doctor_check finds 5 schema issues
THEN issues auto-fixed
AND no issues in result

GIVEN doctor_check finds 15 schema issues
THEN issues NOT auto-fixed
AND issues returned with agents
```

---

## SubEntity Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-SE-1 | Exploration starts from actor moment | No origin | HIGH |
| V-SE-2 | Movement follows highest-scored link | Wrong path | MED |
| V-SE-3 | Visited nodes tracked (no infinite loops) | Stuck | HIGH |
| V-SE-4 | Satisfaction increases on narrative finds | No progress signal | MED |
| V-SE-5 | Crystallization when satisfaction < 0.5 AND novelty > 0.85 | Lost discoveries | MED |

### Validation Tests

```
GIVEN exploration starts
THEN origin = moment linked to actor

GIVEN multiple link candidates
THEN selected = max(alignment × polarity × (1-permanence) × novelty × divergence)

GIVEN node visited twice
THEN backtrack logged
AND depth still increases

GIVEN exploration finds narrative
THEN satisfaction += alignment score
```

---

## Error Conditions

| Condition | Detection | Response |
|-----------|-----------|----------|
| Empty queries | len(queries) == 0 | Error: "queries array required" |
| No graph connection | adapter.ping() fails | Error: "No graph connection" |
| Procedure not found | file not exists | Error: "Procedure X not found" |
| Session expired | session not in cache | Error: "Session expired or invalid" |
| Agent busy | status == "running" | Error: "Agent X is already running" |
| Exploration stuck | satisfaction plateau 5+ steps | Warning logged, continue |

---

## CHAIN

- **Prev:** ALGORITHM_MCP_Tools.md
- **Next:** IMPLEMENTATION_MCP_Tools.md
- **Behaviors:** BEHAVIORS_MCP_Tools.md
