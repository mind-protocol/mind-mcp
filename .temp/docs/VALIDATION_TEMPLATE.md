# VALIDATION: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
      BEHAVIORS_{Module_Name}.md
        ALGORITHM_{Module_Name}.md
→         VALIDATION (you are here)
            → IMPLEMENTATION_{Module_Name}.md
              → HEALTH_{Module_Name}.md
                → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

---

## PURPOSE

Validation defines WHAT MUST BE TRUE for this module to function correctly.
Not how to test — what to protect. Each invariant names a VALUE, not a mechanism.

Invariants are grounded in the schema (schema.yaml v2.2) and physics laws.

## STRUCTURAL INVARIANTS

Properties of the graph that must hold at all times.

### V1: {Value protected}

**Priority:** CRITICAL | HIGH | MEDIUM
**Schema grounding:** {NodeBase.field / LinkBase.field / invariant from schema.yaml}

**MUST:** {what must be true — stated as a property, not an action}
**NEVER:** {what must never happen}
**WHY:** {what breaks if violated — which behaviors degrade, which objectives fail}

### V2: {Value protected}

**Priority:** {level}
**Schema grounding:** {field or invariant}

**MUST:** {condition}
**NEVER:** {anti-condition}
**WHY:** {consequence}

### V3: {Value protected}

{Same format.}

## DYNAMIC INVARIANTS

Properties that must hold over time (across ticks, across sessions).

### VD1: {Convergence/divergence property}

**Over:** {time window — N ticks, N sessions, infinite horizon}
**Schema fields:** {which fields must converge/diverge/remain bounded}
**Physics laws:** {which laws enforce this — L6, L7, L10, etc.}

**MUST:** {temporal property — "weight must converge", "energy must decay", etc.}
**BOUND:** {numerical bound if applicable}
**WHY:** {consequence of violation}

### VD2: {Property}

{Same format.}

## LIMBIC INVARIANTS

For modules touching the drive system (Law 14) or emotional state.

### VL1: {Drive bound}

**Drive:** {curiosity / achievement / affiliation / self_preservation / anxiety / satisfaction / frustration / boredom}
**Range:** [0, 1]
**Schema ref:** drives.{drive_name}

**MUST:** {bound or behavior}
**WHY:** {consequence — which pathology emerges if violated, ref HEALTH doc}

### VL2: {Drive interaction}

{Same format.}

## SCENARIO-BASED VALIDATION

Concrete scenarios that exercise multiple invariants simultaneously.

### S1: {Scenario name}

**Setup:** {initial graph state — node types, link dimensions, drive levels}
**Action:** {what happens — stimulus, tick sequence, user action}
**Expected:** {what must be true after — which invariants hold}
**Invariants tested:** V{N}, V{N}, VD{N}
**Laws exercised:** L{N}, L{N}

### S2: {Scenario name}

{Same format.}

## ANTI-PATTERNS

Known failure modes and their detection.

### AP1: {Anti-pattern name}

**Symptom:** {what you observe when this happens}
**Root cause:** {which invariant is violated}
**Detection:** {how to detect — which HEALTH check catches it}
**Response:** {what to do — which law or mechanism corrects it}

### AP2: {Anti-pattern name}

{Same format.}

## INVARIANT INDEX

| ID | Value protected | Priority | Schema ref | Laws | Type |
|----|----------------|----------|------------|------|------|
| V1 | {value} | {CRITICAL/HIGH/MEDIUM} | {field} | L{N} | structural |
| V2 | {value} | {level} | {field} | L{N} | structural |
| VD1 | {value} | {level} | {field} | L{N} | dynamic |
| VL1 | {value} | {level} | {field} | L{N} | limbic |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
