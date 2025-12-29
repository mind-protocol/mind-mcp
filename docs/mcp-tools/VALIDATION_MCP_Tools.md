# VALIDATION: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Invariants that must hold for structured graph dialogues
```

---

## Protocol Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-PROT-1 | Protocol steps execute in defined order | Workflow corrupted | HIGH |
| V-PROT-2 | Conditional steps only run when condition true | Wrong work done | MED |
| V-PROT-3 | Protocol completes all non-conditional steps | Incomplete work | HIGH |
| V-PROT-4 | Success criteria evaluated at end | Quality unknown | MED |

---

## Membrane Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-MEM-1 | Every `ask` step gets valid answer before proceeding | Invalid data in graph | HIGH |
| V-MEM-2 | Dependencies resolved before membrane body | Missing prerequisites | HIGH |
| V-MEM-3 | Spawn depth never exceeds max_spawn_depth | Infinite recursion | HIGH |
| V-MEM-4 | All step transitions lead to valid next step or $complete | Membrane hangs | HIGH |
| V-MEM-5 | Create step produces ≥1 node | Empty output | MED |
| V-MEM-6 | Create step produces ≥1 link per node (avg) | Sparse graph | MED |

---

## Session Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-SESS-1 | Session ID is unique | Session collision | HIGH |
| V-SESS-2 | Session maintains answer history | Context lost | HIGH |
| V-SESS-3 | Aborted session creates no nodes | Partial commits | HIGH |
| V-SESS-4 | Completed session returns summary | Status unknown | MED |
| V-SESS-5 | Session has single active step at any time | State confusion | HIGH |

---

## Cluster Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-CLUST-1 | All nodes in cluster have valid node_type | Schema violation | HIGH |
| V-CLUST-2 | All links reference existing nodes | Dangling links | HIGH |
| V-CLUST-3 | Moment node created for traceable membranes | Audit trail broken | MED |
| V-CLUST-4 | Links have correct direction (from/to) | Semantics wrong | MED |
| V-CLUST-5 | for_each creates correct count | Missing nodes/links | MED |

---

## Moment Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-MOM-1 | Every moment has `expresses` link from actor | Unattributed | HIGH |
| V-MOM-2 | Every moment has prose (non-empty) | Meaningless moment | MED |
| V-MOM-3 | Moment type matches step type | Wrong categorization | LOW |
| V-MOM-4 | Moment timestamp is accurate | Audit incorrect | LOW |

---

## Query Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-QUERY-1 | Query returns valid nodes or empty list | Crash on null | HIGH |
| V-QUERY-2 | Query respects depth limits | Performance issue | MED |
| V-QUERY-3 | Query filters applied correctly | Wrong results | MED |

---

## Doctor Invariants

| ID | Invariant | Failure Mode | Severity |
|----|-----------|--------------|----------|
| V-DOC-1 | Doctor calls graph before selecting protocol | Blind decisions | MED |
| V-DOC-2 | Doctor selects appropriate protocol for gap | Wrong workflow | MED |
| V-DOC-3 | Doctor completes protocol before moving to next gap | Incomplete resolution | HIGH |

---

## v1 Test Cases

### Protocol Integration

| Test | Description | Validates |
|------|-------------|-----------|
| T-1 | Doctor loads protocol → correct protocol selected | V-DOC-2 |
| T-2 | Protocol workflow → steps execute in order | V-PROT-1 |
| T-3 | Protocol calls membrane → membrane completes | V-MEM-4 |

### Cluster Creation

| Test | Description | Validates |
|------|-------------|-----------|
| T-4 | Membrane output → multiple nodes + rich links | V-MEM-5, V-MEM-6 |
| T-5 | Cross-linking → nodes linked to each other | V-CLUST-2 |
| T-6 | Strength values → derived from answers | V-CLUST-4 |

### Context & Moments

| Test | Description | Validates |
|------|-------------|-----------|
| T-7 | Context enrichment → agent queries, uses results | V-QUERY-1 |
| T-8 | All ask steps → moments with descriptions | V-MOM-1, V-MOM-2 |
| T-9 | Link structure → expresses, about correct | V-MOM-1 |

### Dependencies

| Test | Description | Validates |
|------|-------------|-----------|
| T-10 | Spawn → sub-membrane runs and completes | V-MEM-2 |
| T-11 | Dependency chain → health → validation → behavior | V-MEM-2 |
| T-12 | Cycle detection → detected and blocked | V-MEM-3 |

---

## Error Conditions

| Condition | Detection | Response |
|-----------|-----------|----------|
| Invalid answer | validate_answer returns false | Return error, repeat step |
| Missing node reference | graph_exists returns false | Return error with node ID |
| Spawn depth exceeded | depth > max_spawn_depth | Fail membrane with error |
| Query timeout | graph query exceeds timeout | Return partial or error |
| Session not found | load_session returns null | Return session expired error |

---

## CHAIN

- **Prev:** ALGORITHM_MCP_Tools.md
- **Next:** IMPLEMENTATION_MCP_Tools.md
- **Behaviors:** BEHAVIORS_MCP_Tools.md
