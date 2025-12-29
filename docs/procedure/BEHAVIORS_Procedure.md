# Procedure — Behaviors: Observable Execution Effects

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
UPDATED: 2025-12-29
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Procedure.md
PATTERNS:        ./PATTERNS_Procedure.md
THIS:            BEHAVIORS_Procedure.md (you are here)
VOCABULARY:      ./VOCABULARY_Procedure.md
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/connectome/procedure_runner.py (planned)
```

---

## BEHAVIORS

### B1: Step Is Self-Contained Guide

**Why:** Agent gets what it needs without loading external docs. Creator did the transformation work.

```
GIVEN:  Agent receives a step via start_procedure or continue_procedure
WHEN:   Agent reads step content
THEN:   Content contains complete guide (What/Why/How/Watch out)
AND:    No additional doc loading needed
AND:    Validation spec included if applicable
```

### B2: Agent Writes to Run Space Only

**Why:** Procedure template is protected. Agent work is isolated. Enables audit, reprise, rollback.

```
GIVEN:  Agent executing a Procedure
WHEN:   Agent creates nodes or links
THEN:   All creations go into Run Space (via CONTAINS)
AND:    Procedure template nodes are read-only
AND:    Moment tracks what was created (via EXPRESSES)
```

### B3: Explicit API Controls Flow (V1)

**Why:** V1 is deterministic. No physics-based routing. Clear, testable, debuggable.

```
GIVEN:  Agent wants to start a procedure
WHEN:   Agent calls start_procedure(procedure_id)
THEN:   System creates Run Space
AND:    System links Run Space to Step 1 (acts on, e=8)
AND:    System returns Step 1 content

GIVEN:  Agent wants to advance
WHEN:   Agent calls continue_procedure(run_id)
THEN:   System checks validation for next step
AND:    If pass: flip current step (receives from, e=1), heat next step (acts on, e=8)
AND:    If fail: remain at current step, return validation failure
AND:    Return next step content

GIVEN:  Agent wants to finish
WHEN:   Agent calls end_procedure(run_id)
THEN:   System marks Run Space complete
AND:    System flips Actor link to inhabits (from occupies)
```

### B4: Physics Tracks State (V1)

**Why:** Graph state reflects execution state. Enables crash recovery, audit, visualization. But doesn't drive routing in V1.

```
GIVEN:  Run Space with step links
WHEN:   Inspecting state
THEN:   High energy (>5) + forward polarity [0.9, 0.1] = active step
AND:    Low energy (<2) + backward polarity [0.2, 0.8] = completed step
AND:    This is bookkeeping, not routing decision
```

### B5: Validation Gates Transition

**Why:** Steps don't advance until work is verified. Graph state is proof.

```
GIVEN:  Agent calls continue_procedure(run_id)
WHEN:   System checks validation
THEN:   Validation spec from next step's content
AND:    Query Run Space for required nodes/links
AND:    If validation passes → execute transition
AND:    If validation fails → return failure, remain at current step
```

### B6: Crash Recovery from Graph State

**Why:** Graph IS state. No external state to sync. Reload = resume.

```
GIVEN:  Agent crashed mid-procedure
WHEN:   New agent loads Run Space
THEN:   Find high-energy "acts on" link → active step
AND:    Find CONTAINS links → work already done
AND:    Resume from active step with existing trace
```

### B7: Procedure Links to Doc Space (Later)

**Why:** Audit trail. If docs change, can flag procedure steps for review.

```
GIVEN:  Procedure linked to doc space via IMPLEMENTS
WHEN:   Checking traceability
THEN:   Can follow IMPLEMENTS chain to Objectives
AND:    (V2) If doc node modified → flag procedure for review
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (Steps Self-Contained) | Agent has everything in step content |
| B2 | O2 (Sandbox Only) | Protects procedure definitions |
| B3 | O4 (Deterministic Flow) | Makes execution predictable and testable |
| B4 | O4 (Deterministic Flow) | State is readable, doesn't drive routing |
| B5 | O2 (Sandbox Only) | Validation proves work without modifying template |
| B6 | O1, O2 | Recovery relies on self-contained state |
| B7 | O5 (Multi-Granularity) | Links support later refinement |

---

## INPUTS / OUTPUTS

### Primary Function: `start_procedure()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| procedure_id | str | ID of the procedure template to execute |
| actor_id | str | ID of the actor running the procedure |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| run_id | str | ID of the created Run Space |
| step_content | str | Step 1 content (the guide) |
| status | str | "active" |

**Side Effects:**
- Creates Run Space node (space, subtype: run)
- Creates link: Run Space → Procedure (elaborates)
- Creates link: Run Space → Step 1 (acts on, e=8)
- Creates link: Actor → Run Space (occupies, e=8)

### Primary Function: `continue_procedure()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| run_id | str | ID of the Run Space |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| step_content | str | Next step content (or current if failed) |
| status | str | "active" / "completed" / "validation_failed" |
| validation_error | str/None | Error message if validation failed |

**Side Effects:**
- Updates current step link: polarity flip, energy drop
- Creates next step link: acts on, e=8

---

## EDGE CASES

### E1: Last Step Continue

```
GIVEN:  Agent at final step, calls continue_procedure
THEN:   System calls end_procedure internally
AND:    Returns status: "completed", step_content: None
```

### E2: Validation Failure

```
GIVEN:  Validation check fails
THEN:   Current step link unchanged (still high energy)
AND:    Return current step content
AND:    Return validation_error with specific failure reason
```

### E3: Orphan Run Space

```
GIVEN:  Run Space exists with no high-energy step link
THEN:   This is an error state (invariant V3 violated)
AND:    Recovery: find last completed step, heat next step
```

---

## ANTI-BEHAVIORS

### A1: Template Mutation

```
GIVEN:   Agent executing procedure
WHEN:    Agent attempts to create node in Procedure space
MUST NOT: Allow write to Procedure template
INSTEAD:  Reject write, return error, log attempt
```

### A2: Multiple Active Steps

```
GIVEN:   Run Space with step links
WHEN:    Transition occurs
MUST NOT: Leave two high-energy step links
INSTEAD:  Atomic flip: cool current THEN heat next
```

### A3: Step Without Guide

```
GIVEN:   Step being loaded
WHEN:    Content missing What/Why/How
MUST NOT: Accept incomplete step
INSTEAD:  Fail at procedure creation time, not runtime
```

---

## MARKERS

<!-- @mind:proposition Add B8: "Run Space Expires After N Days" — garbage collection -->
