# PATTERNS: MCP Tools

```
STATUS: V1 SPEC
PURPOSE: Design philosophy for structured graph dialogues
```

---

## Core Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| P1 | **Skill = knowledge** | Markdown document with domain expertise, when to use which protocols. |
| P2 | **Protocol = procedure** | YAML steps: ask → query → branch → call_protocol → create. |
| P3 | **Membrane = executor** | Tool that runs protocols, manages sessions, commits clusters. |
| P4 | **Cluster output** | Protocols create multiple nodes + dense links, never single isolated nodes. |
| P5 | **Context enrichment** | Agent can query graph before answering any step. Understanding before deciding. |
| P6 | **Agent descriptions** | Every step creates moment with agent-written prose. The graph captures reasoning. |
| P7 | **Protocol composition** | Protocols call protocols. Missing prerequisite → `call_protocol` step. |
| P8 | **Doctor drives** | Doctor loads skill → skill guides which protocols → membrane executes. |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                   DOCTOR                     │
│  Detects gaps, loads skill for guidance      │
│  Calls graph to understand current state     │
└─────────────────────────────────────────────┘
                    │
                    │ loads
                    ▼
┌─────────────────────────────────────────────┐
│               SKILL (Markdown)               │
│  Domain knowledge, which protocol when       │
│  Patterns, anti-patterns, examples           │
└─────────────────────────────────────────────┘
                    │
                    │ guides
                    ▼
┌─────────────────────────────────────────────┐
│              PROTOCOL (YAML)                 │
│  Steps: ask, query, branch, call_protocol    │
│  Can call other protocols                    │
└─────────────────────────────────────────────┘
                    │
                    │ runs via
                    ▼
┌─────────────────────────────────────────────┐
│              MEMBRANE (Tool)                 │
│  Executes protocol steps                     │
│  Manages sessions, validates, commits        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│                   GRAPH                      │
│  Nodes + dense links (the output)            │
└─────────────────────────────────────────────┘
```

---

## Skill Format (Markdown)

```markdown
# {Skill Name} Skill

## Domain

{Domain knowledge — what this skill covers, key concepts}

## When to Use Which Protocol

| Situation | Protocol |
|-----------|----------|
| {situation} | `protocol:{name}` → `protocol:{name}` |

## Process

1. {Step description}
2. {Step description}

## Patterns

- {Good pattern}
- {Good pattern}

## Anti-Patterns

- {Bad pattern to avoid}

## Queries to Run

When exploring:
- {Query description}

## Examples

{Examples of applying this skill}
```

---

## Protocol Format (YAML)

```yaml
protocol: {name}
version: "1.0"
description: {what this creates}

steps:
  # ASK - get input from agent
  {step_id}:
    type: ask
    question: "{question text}"
    expects:
      type: string | id | id_list | string_list | enum
      # type-specific constraints
    context_enrichment:
      prompt: "{enrichment prompt}"
      allows: [exploration, relationship, verification, clarification]
    moment:
      agent_provides: [description, reasoning]
    next: {step_id | $complete}

  # QUERY - load data from graph
  {step_id}:
    type: query
    store_as: {variable_name}
    query:
      find: {node_type}
      where: {...}
      in_space: "{space_id}"
    moment:
      agent_provides: [description]
    next: {step_id}

  # BRANCH - conditional routing
  {step_id}:
    type: branch
    condition: "{expression}"
    then: {step_id}
    else: {step_id}
    # OR for multi-case:
    cases:
      {value}: {step_id}
      {value}: {step_id}

  # CALL_PROTOCOL - invoke sub-protocol
  {step_id}:
    type: call_protocol
    protocol: {protocol_name}
    context:
      {key}: "{value}"
    on_complete: {step_id}

  # CREATE - build cluster
  {step_id}:
    type: create
    nodes:
      - id: "{node_id}"
        node_type: {type}
        # fields...
      - for_each: {list_variable}
        id: "{template}"
        # fields...
    links:
      - type: {link_type}
        from: "{node_id}"
        to: "{node_id}"
      - for_each: {list_variable}
        type: {link_type}
        from: "{template}"
        to: "{template}"
    next: $complete

output:
  cluster:
    nodes: [...]
    links: [...]
  summary: "{template}"
```

---

## Anti-Patterns

| Don't | Instead |
|-------|---------|
| Create single nodes | Create clusters with links |
| Skip context queries | Enrich understanding first |
| Let agent decide workflow | Skill guides → protocol executes |
| Silent operations | Every step creates moment with prose |
| Ignore missing prerequisites | Use `call_protocol` step |
| Put procedure in skills | Skills = knowledge, protocols = procedure |
| Put knowledge in protocols | Protocols = steps only, skills = guidance |

---

## Skills (v1)

| Skill | Domain | Status |
|-------|--------|--------|
| `health_coverage` | Runtime verification, docking points | Spec complete |
| `module_design` | Starting new areas, boundaries | Spec complete |
| `feature_implementation` | Building within existing module | Spec complete |
| `escalation_handling` | Blockers, decisions needed | Spec complete |
| `decision_capture` | Recording rationale | Spec complete |
| `progress_tracking` | Session handoffs | Spec complete |

*Skills live in `skills/` as Markdown files.*

---

## Protocols (v1)

| Protocol | Purpose | Output |
|----------|---------|--------|
| `explore_space` | Understand what exists | exploration moment |
| `add_objectives` | Define module goals | primary + N secondary + M non-objectives + moment |
| `add_invariant` | Add validation constraint | validation + moment + ensures links |
| `add_health_coverage` | Add runtime verification | health + 2 docks + moment + verifies links |
| `add_implementation` | Document code structure | implementation + N docks + moment |
| `record_work` | Document progress | progress moment + N escalations + M goals |
| `investigate` | Deep dive into node/issue | investigation moment + optional goal/escalation |
| `resolve_blocker` | Handle escalation | rationale + resolution moment |

*Protocols live in `protocols/` as YAML files.*

---

## Query Language

### Find Nodes
```yaml
query:
  find: {node_type}
  where:
    {field}: {value}
  in_space: {space_id}
  limit: {int}
```

### Find Links
```yaml
query:
  links_from: {node_id}
  type: {link_type}

query:
  links_to: {node_id}
  type: {link_type}
```

### Find Related
```yaml
query:
  related_to: {node_id}
  via: {link_type}
  direction: from | to | both
  depth: {int}
```

### Find Contents
```yaml
query:
  contents_of: {space_id}
  node_type: {type}
  depth: {int}
```

### Presets

| Preset | Query |
|--------|-------|
| `all_spaces` | `{find: space}` |
| `all_validations` | `{find: narrative, where: {type: validation}}` |
| `all_behaviors` | `{find: narrative, where: {type: behavior}}` |
| `all_goals` | `{find: narrative, where: {type: goal}}` |
| `all_escalations` | `{find: narrative, where: {type: escalation}}` |

---

## CHAIN

- **Prev:** OBJECTIVES_MCP_Tools.md
- **Next:** BEHAVIORS_MCP_Tools.md
- **Implements:** IMPLEMENTATION_MCP_Tools.md
