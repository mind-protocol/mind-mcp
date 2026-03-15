# TASK: {Task_Name}

## NODE

```yaml
node_type: narrative
type: "task"
status: active
```

## DEFINITION

{The OUTCOME this task produces — not the process. What is true after this task completes.}

## EXECUTION

| Aspect | Value |
|--------|-------|
| Executor | {agent / automated / mechanical} |
| SKILL | {SKILL_name, if agent-executed} |
| Procedure | {procedure_name, if applicable} |

## INPUTS

| Input | Type | Source | Schema ref |
|-------|------|--------|------------|
| {name} | {type} | {where it comes from} | {NodeBase/LinkBase field or N/A} |

## OUTPUTS

| Output | Type | Destination | Schema ref |
|--------|------|-------------|------------|
| {name} | {type} | {where it goes} | {NodeBase/LinkBase field or N/A} |

## INSTANCE SCHEMA

When this task runs, a task instance node is created:

```yaml
node_type: narrative
type: "task_run"
status: pending → running → completed | failed
synthesis: "{task_name}: {brief outcome description}"
```

### Links

| Direction | Target | relation_kind | Key dimensions |
|-----------|--------|---------------|----------------|
| [OF] | {task template node} | abstracts | hierarchy: +1.0 |
| [TARGET] | {node being created/modified} | relates_to | hierarchy: 0.0 |
| [CLAIMED_BY] | {executor actor node} | cares_about | trust: {level} |

## TRIGGERS

| Condition | Source | Frequency |
|-----------|--------|-----------|
| {what spawns this task} | {event / cron / manual / health check} | {how often} |

## PHYSICS INTERACTION

| Law | How this task interacts with it |
|-----|-------------------------------|
| L1 | {task completion injects energy into related nodes} |
| L6 | {successful task consolidates weight on executor link} |
