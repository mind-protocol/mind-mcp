# Procedure — Algorithm: Deterministic Execution Flow

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
BEHAVIORS:       ./BEHAVIORS_Procedure.md
VOCABULARY:      ./VOCABULARY_Procedure.md
THIS:            ALGORITHM_Procedure.md (you are here)
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/connectome/procedure_runner.py (planned)
```

---

## OVERVIEW

The Procedure execution system provides deterministic step-by-step execution. Three APIs control flow: `start_procedure` creates execution context, `continue_procedure` validates and advances, `end_procedure` marks completion.

**V2 simplification:** Steps are self-contained guides. No runtime doc chain loading. The step content IS the context.

Physics (energy/polarity) tracks state but does not drive routing in V1.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1 (Steps Self-Contained) | B1 | Step content has everything agent needs |
| O2 (Sandbox Only) | B2, B5 | Run Space isolation, validation without mutation |
| O4 (Deterministic Flow) | B3, B4 | Explicit API, physics as bookkeeping only |

---

## DATA STRUCTURES

### Run Space

```
node_type: space
subtype: run
content:
  status: "active" | "completed" | "failed"
  started_at: ISO-8601 timestamp
  completed_at: ISO-8601 timestamp (if completed)
```

### Step (Self-Contained Guide)

```
node_type: narrative
subtype: step
synthesis: "Step N: brief description"
content: |
  executor: agent | code | actor | hybrid

  ## What you're doing
  Brief description of the task.

  ## Why
  Context from OBJECTIVES/PATTERNS.

  ## How
  1. Step-by-step instructions
  2. Code examples if applicable

  ## Watch out
  - Common pitfalls
  - Edge cases

  ## Validation to pass this step
  type: node_exists
  in_space: $run
  subtype: validation_result
  min_count: 1
```

### Executor Types

| Executor | Runner | Description |
|----------|--------|-------------|
| `agent` | LLM | Claude/LLM executes via reasoning |
| `code` | Python | Deterministic code execution |
| `actor` | External | Events, logs, notifications |
| `hybrid` | Both | Code prepares, agent decides |

### Step Link (Run → Step)

```
Active step:
  verb: "acts on"
  energy: 8.0
  polarity: [0.9, 0.1]

Completed step:
  verb: "receives from"
  energy: 1.0
  polarity: [0.2, 0.8]
```

---

## ALGORITHM: start_procedure

### Step 1: Create Run Space

Create a new space node with subtype "run". Set status to "active", record started_at timestamp.

### Step 2: Link to Template

Create link from Run Space to Procedure template with verb "elaborates". Physics: h=+0.6, perm=0.5.

### Step 3: Get First Step

Query the Procedure template for its first step (via CONTAINS links, ordered by sequence).

### Step 4: Activate First Step

Create link from Run Space to Step 1:
- verb: "acts on"
- energy: 8.0
- polarity: [0.9, 0.1]

### Step 5: Link Actor

Create link from Actor to Run Space:
- verb: "occupies"
- energy: 8.0
- polarity: [0.8, 0.2]

### Step 6: Return

Return run_id, step_content (the guide), status "active".

**No doc chain loading.** Step content IS the context.

---

## ALGORITHM: continue_procedure

### Step 1: Get Active Step

Query Run Space for links with energy > 5 and verb "acts on". Returns current step.

### Step 2: Get Next Step

Query Procedure's CONTAINS links to find step sequence. Get next after current. If no next step, call end_procedure.

### Step 3: Check Validation

Parse validation spec from next step's content (YAML block after "## Validation"). If validation exists:
- Query Run Space for matching nodes/links
- If requirements not met: return current step content, status "validation_failed", error

### Step 4: Cool Current Step

Update the link from Run Space to current step:
- energy: 1.0 (was 8.0)
- polarity: [0.2, 0.8] (was [0.9, 0.1])

### Step 5: Heat Next Step

Create link from Run Space to next step:
- verb: "acts on"
- energy: 8.0
- polarity: [0.9, 0.1]

### Step 6: Return

Return next step content (the guide), status "active".

---

## ALGORITHM: end_procedure

### Step 1: Get Actor

Query for the actor linked to this Run Space via "occupies".

### Step 2: Flip Actor Link

Update the actor's link:
- verb: "inhabits" (was "occupies")
- energy: 1.0 (was 8.0)
- polarity: [0.3, 0.7] (was [0.8, 0.2])

### Step 3: Mark Run Complete

Update Run Space content:
- status: "completed"
- completed_at: current timestamp

### Step 4: Return

Return step_content: None, status: "completed".

---

## V1 API (Python)

```python
def start_procedure(procedure_id: str, actor_id: str) -> dict:
    """Start a procedure execution."""
    # 1. Create Run Space
    run_space = create_node(type="space", subtype="run", content={
        "status": "active",
        "started_at": datetime.now().isoformat()
    })

    # 2. Link to procedure template
    create_link(run_space, procedure_id, verb="elaborates")

    # 3. Get Step 1
    step_1 = get_first_step(procedure_id)

    # 4. Link Run Space to Step 1 (active)
    create_link(run_space, step_1, verb="acts on", energy=8.0, polarity=[0.9, 0.1])

    # 5. Link Actor to Run Space
    create_link(actor_id, run_space, verb="occupies", energy=8.0)

    return {
        "run_id": run_space.id,
        "step_content": step_1.content,  # The guide
        "status": "active"
    }


def continue_procedure(run_id: str) -> dict:
    """Validate and advance to next step."""
    current_step = get_active_step(run_id)
    next_step = get_next_step(current_step)

    if not next_step:
        return end_procedure(run_id)

    # Check validation
    validation = parse_validation_from_content(next_step.content)
    if validation:
        result = check_validation(run_id, validation)
        if not result.passed:
            return {
                "step_content": current_step.content,
                "status": "validation_failed",
                "validation_error": result.error
            }

    # Flip current step (cool down)
    update_link(run_id, current_step, energy=1.0, polarity=[0.2, 0.8])

    # Heat next step
    create_link(run_id, next_step, verb="acts on", energy=8.0, polarity=[0.9, 0.1])

    return {
        "step_content": next_step.content,  # The guide
        "status": "active",
        "validation_error": None
    }


def end_procedure(run_id: str) -> dict:
    """Mark procedure as complete."""
    actor = get_actor_for_run(run_id)
    update_link(actor, run_id, verb="inhabits", energy=1.0, polarity=[0.3, 0.7])

    update_node(run_id, content={
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    })

    return {"step_content": None, "status": "completed"}
```

---

## VALIDATION TYPES (V1)

```python
def check_validation(run_id: str, validation: dict) -> ValidationResult:
    match validation["type"]:
        case "node_exists":
            nodes = query_nodes(in_space=run_id, subtype=validation.get("subtype"))
            passed = len(nodes) >= validation.get("min_count", 1)

        case "link_exists":
            links = query_links(from_node=run_id, verb=validation["verb"])
            passed = len(links) >= validation.get("min_count", 1)

        case _:
            passed = True  # Unknown type = auto-pass

    return ValidationResult(passed=passed, error=None if passed else f"Validation failed: {validation}")
```

---

## DATA FLOW

```
start_procedure(procedure_id, actor_id)
  │
  ├─► Create Run Space (space, subtype: run)
  ├─► Link: Run → Procedure (elaborates)
  ├─► Get Step 1 from Procedure
  ├─► Link: Run → Step 1 (acts on, e=8)
  ├─► Link: Actor → Run (occupies, e=8)
  └─► Return {run_id, step_content, status: "active"}
```

```
continue_procedure(run_id)
  │
  ├─► Find active step (energy > 5)
  ├─► Get next step
  ├─► Check validation
  │     ├─► [fail] Return {step_content: current, status: "validation_failed"}
  │     └─► [pass] Continue...
  ├─► Cool current step (e=1)
  ├─► Heat next step (e=8)
  └─► Return {step_content: next, status: "active"}
```

---

## COMPLEXITY

**Time:** O(S) per API call
- S = number of steps (for finding active step, getting next)

**Space:** O(1) — no doc chain collection

**Simplified from V1:** Removed O(D) doc chain traversal.

---

## HELPER FUNCTIONS

### `get_active_step(run_id)`

Query links from run_id with energy > 5 and verb "acts on". Return target node.

### `get_next_step(step_id)`

Query Procedure's CONTAINS links for step ordering. Return step after current, or None.

### `check_validation(run_id, validation_spec)`

Parse validation type, query Run Space, return pass/fail with error.

### `parse_validation_from_content(content)`

Look for "## Validation" section in step content. Parse YAML block. Return dict or None.

---

## KEY DECISIONS

### D1: No Runtime Doc Chain Loading (V2)

**V1 approach:** `walk_implemented_in()` traversed links at runtime.

**V2 approach:** Step content includes everything. Creator transforms docs into guide.

**Why:** Simpler runtime. Creator has time to think; runtime shouldn't.

### D2: Validation in Next Step

Validation spec lives in NEXT step's content. Check BEFORE entering.

**Why:** Gate prevents broken state.

---

## MARKERS

<!-- @mind:resolved walk_implemented_in removed — steps are self-contained -->
