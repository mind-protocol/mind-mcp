# ALGORITHM: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
      BEHAVIORS_{Module_Name}.md
→       ALGORITHM (you are here)
          → VALIDATION_{Module_Name}.md
            → IMPLEMENTATION_{Module_Name}.md
              → HEALTH_{Module_Name}.md
                → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

---

## OVERVIEW

{High-level: what this algorithm does, why this approach, what it replaces.}

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors this algorithm guarantees | Key mechanism |
|-----------|-------------------------------------|---------------|
| O{N} | B{N}, B{N} | {how the algorithm ensures it} |

## DATA STRUCTURES

### {Structure Name}

```yaml
{field_name}:
  type: {type from schema.yaml — NodeBase field, LinkBase field, or custom}
  range: {value bounds}
  default: {default value}
  description: "{role in this algorithm}"
  schema_ref: "{NodeBase.field / LinkBase.field / drives.field / working_memory.field}"
```

**Constraints:**
- {Invariant or bound this structure must respect}
- {Reference to schema.yaml section if applicable}

### {Structure Name 2}

{Same format.}

## ALGORITHM: {Primary Function Name}

### Step 1: {Step name}

```
{Pseudocode or formula}
```

**WHY:** {Why this step, not another approach.}
**PHYSICS:** {Which law(s) from schema.yaml this implements — L1 through L21.}

### Step 2: {Step name}

```
{Pseudocode or formula}
```

**WHY:** {Reasoning.}
**PHYSICS:** {Law reference.}

### Step 3: {Step name}

```
{Pseudocode or formula}
```

**WHY:** {Reasoning.}
**PHYSICS:** {Law reference.}

## KEY DECISIONS

Decision points in the algorithm with rationale.

### D1: {Decision}

| Condition | Path A | Path B | Rationale |
|-----------|--------|--------|-----------|
| {when X} | {do A} | {do B} | {why A is chosen over B, or conditions for each} |

### D2: {Decision}

| Condition | Path A | Path B | Rationale |
|-----------|--------|--------|-----------|
| {when} | {A} | {B} | {why} |

## CONSTANTS

| Constant | Value | Unit | Used by | Derivation |
|----------|-------|------|---------|------------|
| {name} | {value} | {unit} | {which step/law} | {why this value — empirical, mathematical, or from schema} |

## DATA FLOW

```
{input} → [{step 1}] → [{step 2}] → [{step 3}] → {output}
                ↓              ↓
          {side effect}   {side effect}
```

### Flow: {Flow name}

1. **Input:** {what enters — node types, link dimensions, drives}
2. **Transform:** {what changes — which NodeBase/LinkBase fields are modified}
3. **Output:** {what exits — updated graph state, WM state, drive state}
4. **Schema fields touched:** {list of schema.yaml fields read/written}

## COMPLEXITY

| Aspect | Complexity | Bottleneck |
|--------|------------|------------|
| Time | O({complexity}) | {where the cost is} |
| Space | O({complexity}) | {where the memory is} |
| Per-tick budget | {ms or ops} | {bound from Law 12 tick cycle} |

## HELPER FUNCTIONS

### {helper_name}({params})

**Purpose:** {what it does}
**Returns:** {what}
**Schema fields used:** {which NodeBase/LinkBase fields}

```
{Pseudocode}
```

## INTERACTIONS

| Module | What we call | What we get back | Schema types exchanged |
|--------|-------------|-----------------|----------------------|
| {module} | {function/tool} | {data} | {node_type, link fields, etc.} |

## TICK INTEGRATION

Where this algorithm fits in the 17-step tick cycle (Law 12).

| Tick step | Law | This module's role |
|-----------|-----|-------------------|
| {step N} | L{N} | {what this algorithm does at this step} |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
