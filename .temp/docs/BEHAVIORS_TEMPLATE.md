# BEHAVIORS: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
→   BEHAVIORS (you are here)
      → ALGORITHM_{Module_Name}.md
        → VALIDATION_{Module_Name}.md
          → IMPLEMENTATION_{Module_Name}.md
            → HEALTH_{Module_Name}.md
              → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

---

## BEHAVIORS

Name behaviors by their OBSERVABLE RESULT, not by the concept.
Use GIVEN/WHEN/THEN format. Each behavior must be testable.

### B1: {Observable result name}

**Why:** {Which objective this serves (O1, O2, ...) and why this behavior matters.}

**GIVEN** {precondition — graph state, node types, link dimensions}
**WHEN** {trigger — stimulus, tick event, threshold crossed, physics law fires}
**THEN** {observable result — what changes in graph, WM, or output}
**AND** {secondary effect, if any}

**Schema grounding:**
- Node types: {which node_type / cognitive type involved}
- Link dimensions: {which dimensions change — weight, energy, trust, etc.}
- Physics laws: {which laws produce this behavior — L1, L4, L6, etc.}

### B2: {Observable result name}

**Why:** {Objective served.}

**GIVEN** {precondition}
**WHEN** {trigger}
**THEN** {observable result}

**Schema grounding:**
- Node types: {...}
- Link dimensions: {...}
- Physics laws: {...}

### B3: {Observable result name}

{Same format.}

## OBJECTIVES SERVED

| Behavior | Objective | How |
|----------|-----------|-----|
| B1 | O{N} | {mechanism} |
| B2 | O{N} | {mechanism} |

## INPUTS / OUTPUTS

### Inputs

| Parameter | Type (schema) | Source | Description |
|-----------|--------------|--------|-------------|
| {name} | {NodeBase field / LinkBase field / drive / custom} | {where it comes from} | {what it represents} |

### Outputs

| Output | Type (schema) | Destination | Description |
|--------|--------------|-------------|-------------|
| {name} | {NodeBase field / LinkBase field / drive / custom} | {where it goes} | {what changes} |

### Side effects

- {Effect on graph state}
- {Effect on working memory}
- {Effect on drives / limbic state}

## EDGE CASES

### E1: {Scenario}

**Condition:** {what unusual state or input}
**Expected behavior:** {what should happen}
**Schema concern:** {which field bounds, invariants, or laws are stressed}

### E2: {Scenario}

**Condition:** {what}
**Expected behavior:** {what}

## ANTI-BEHAVIORS

What this module should NEVER do. Name by the bad outcome.

### A1: {Bad outcome name}

**Should NEVER:** {what must not happen}
**Instead:** {correct behavior}
**Schema violation if triggered:** {which invariant from schema.yaml would break}

### A2: {Bad outcome name}

**Should NEVER:** {what}
**Instead:** {correct}

## REFERENCE SCENARIOS

Concrete scenarios grounding behaviors to real use. Each scenario maps to specific laws and node types.

| ID | Scenario | Primary behaviors | Laws involved | Node types |
|----|----------|-------------------|---------------|------------|
| S1 | {description} | B1, B3 | L1, L4, L6 | moment, narrative |
| S2 | {description} | B2 | L2, L8 | actor, thing |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
