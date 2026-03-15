# SKILL: mind.{verb}_{object}

<!-- @mind:id — SKILL_{Verb}_{Object} -->

## MAPS TO VIEW

{agent subtype path, e.g., `.mind/agents/groundwork/CLAUDE.md`, or "(meta-skill)"}

## CONTEXT

{Project-specific knowledge ONLY. What the agent needs to know that isn't in FRAMEWORK.md.
Show system integration, local term definitions. NO generic LLM knowledge.}

### Schema context

{Which node types, link dimensions, and physics laws this skill operates on.
Reference schema.yaml v2.2 sections.}

## PURPOSE

{One sentence, verb-first. What this skill produces.}

## INPUTS

```yaml
{input_name}:
  type: {type — NodeBase field, file path, string, etc.}
  required: {true/false}
  description: "{what it is}"
  schema_ref: "{NodeBase.field / LinkBase.field / drives.field / N/A}"
```

## OUTPUTS

```yaml
{output_name}:
  type: {type — node, file, report, etc.}
  description: "{what it produces}"
  schema_ref: "{what schema element is created/modified}"
```

## GATES

Verifiable conditions that MUST pass before this skill executes.
State as "must X" — never "should be good" or "ideally".

| # | Gate | Reason | Verification |
|---|------|--------|-------------|
| G1 | {must X} | {why this matters} | {how to check} |
| G2 | {must Y} | {why} | {how to check} |

## PROCESS

### Step 1: {Step name}

{What to do.}

**Reasoning:** {Why this step, not another.}
**Schema interaction:** {Which graph operations — create node, modify link, query, etc.}

### Step 2: {Step name}

{What to do.}

**Reasoning:** {Why.}
**Schema interaction:** {What.}

### Step 3: {Step name}

{What to do.}

## PROCEDURES REFERENCED

| Procedure | When | Creates |
|-----------|------|---------|
| {procedure_name} | {condition to invoke} | {what it produces} |

## MEMBRANE INTEGRATION

Optional auto-triggering and context fetching via MCP tools.

| Aspect | Value |
|--------|-------|
| Auto-trigger | {condition, or "manual only"} |
| Auto-fetch | {graph_query or procedure to run before skill, or "none"} |
| Output destination | {where results go — graph, file, message, etc.} |

## EVIDENCE

### Docs

| ID | File | Section |
|----|------|---------|
| {doc_id} | {file path} | {heading} |

### Code

| File | Symbol |
|------|--------|
| {file path} | {function/class name} |

## GRAPH OPERATIONS SUMMARY

| Operation | Node type | Fields | Cypher pattern |
|-----------|-----------|--------|----------------|
| {create/read/update/delete} | {type} | {fields} | {pattern} |

<!-- @mind:TODO — -->
<!-- @mind:escalation — -->
<!-- @mind:proposition — -->

## NEVER-STOP

If blocked: add `@mind:escalation` with context, then `@mind:proposition` with your best guess, then proceed with the proposition. Do not halt.
