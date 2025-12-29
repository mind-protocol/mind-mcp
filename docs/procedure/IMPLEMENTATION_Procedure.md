# Procedure — Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
THIS:            IMPLEMENTATION_Procedure.md (you are here)
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/connectome/procedure_runner.py (planned)
                 runtime/connectome/validation.py (planned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/connectome/
├── __init__.py              # exports: start_procedure, continue_procedure, end_procedure
├── persistence.py           # (existing) graph ops, MERGE for link updates
├── procedure_runner.py      # (planned) main API: orchestrates state changes
├── validation.py            # (planned) check_validation, parse_validation_spec
└── schema.py                # (existing) add IMPLEMENTS verb definition
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/connectome/procedure_runner.py` | Main API orchestration | `start_procedure`, `continue_procedure`, `end_procedure` | ~150 | PLANNED |
| `runtime/connectome/validation.py` | Step validation | `check_validation`, `parse_validation_spec` | ~100 | PLANNED |
| `runtime/connectome/persistence.py` | Graph operations | `_persist_link` (MERGE), `_persist_node` | ~300 | EXISTS |
| `runtime/connectome/schema.py` | Link type definitions | Add `IMPLEMENTS` constant | ~150 | EXISTS (modify) |

**V2 Simplification:** No `doc_chain.py` — steps are self-contained guides. The creator transforms docs into step content at procedure authoring time, not runtime.

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** State Machine + Repository

**Why this pattern:** Run Spaces are finite state machines (active → completed). The graph is the repository — no external state store. State transitions are explicit API calls.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| State Machine | Run Space lifecycle | Clear transitions: start → active → completed |
| Repository | Graph operations | Graph IS the data store, no ORM |
| Guard Clause | Validation | Check before transition, fail fast |
| Self-Contained | Step guides | Each step has complete context embedded |

### Anti-Patterns to Avoid

- **Runtime Doc Loading**: V1 tried walking IMPLEMENTS at runtime. V2 embeds context in step content.
- **Silent Failure**: Never swallow validation errors. Always return actionable messages.
- **Premature Optimization**: Simple runtime, complex authoring.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Execution | Run Space lifecycle, step transitions | Graph operations | `procedure_runner.py` public API |
| Validation | Spec parsing, requirement checking | Graph queries | `check_validation()` |

---

## SCHEMA

### IMPLEMENTS Link (Bottom → Top)

**Direction:** Lower layers implement higher layers.

```
Health → Implementation → Validation → Algorithm → Behaviors → Vocabulary → Patterns → Objectives
```

Each layer IMPLEMENTS the layer above it.

```yaml
IMPLEMENTS:
  required:
    - verb: "IMPLEMENTS"
    - hierarchy: -1              # descends into implementation
    - polarity: [1, 0]           # forward only, no backprop
    - permanence: 1              # structural, immutable
    - energy: 1                  # stable, not hot
  constraints:
    - source: doc chain node (lower layer)
    - target: doc chain node (higher layer)
    - chain terminates at Objectives (no further IMPLEMENTS)
  purpose: Audit trail only — not loaded at runtime in V2
```

### Execution Links

```yaml
acts_on:
  context: Run Space → Active Step
  required:
    - energy: 8.0
    - polarity: [0.9, 0.1]
    - hierarchy: 0               # peer level
  semantics: "Run Space is currently focused on this step"

receives_from:
  context: Run Space → Completed Step
  required:
    - energy: 1.0
    - polarity: [0.2, 0.8]
    - hierarchy: 0
  semantics: "Run Space has completed this step"

occupies:
  context: Actor → Active Run Space
  required:
    - energy: 8.0
    - polarity: [0.8, 0.2]
  semantics: "Actor is currently executing this run"

inhabits:
  context: Actor → Completed Run Space
  required:
    - energy: 1.0
    - polarity: [0.3, 0.7]
  semantics: "Actor has completed this run"

elaborates:
  context: Run Space → Procedure Template
  required:
    - hierarchy: +0.6            # upward to template
    - permanence: 0.5            # semi-permanent
  semantics: "Run Space is an instance of this procedure"
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| start_procedure | `runtime/connectome/procedure_runner.py:start_procedure` | MCP tool call |
| continue_procedure | `runtime/connectome/procedure_runner.py:continue_procedure` | MCP tool call |
| end_procedure | `runtime/connectome/procedure_runner.py:end_procedure` | MCP tool call or continue_procedure (last step) |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow: Start Procedure

Explain: Creates a new Run Space, links it to a Procedure template, activates the first step, and returns step content with its doc chain.

```yaml
flow:
  name: start_procedure
  purpose: Initialize procedure execution context
  scope: procedure_id, actor_id → run_id, step, status
  steps:
    - id: create_run
      description: Create Run Space node
      file: runtime/connectome/procedure_runner.py
      function: start_procedure
      input: procedure_id, actor_id
      output: run_space node
      trigger: MCP procedure_start tool
      side_effects: graph node created

    - id: link_template
      description: Link Run to Procedure template
      file: runtime/connectome/procedure_runner.py
      function: start_procedure
      input: run_space, procedure_id
      output: elaborates link
      trigger: after create_run
      side_effects: graph link created

    - id: activate_step
      description: Link Run to Step 1 with high energy
      file: runtime/connectome/procedure_runner.py
      function: start_procedure
      input: run_space, step_1
      output: acts_on link (e=8)
      trigger: after link_template
      side_effects: graph link created

    - id: return_step
      description: Return Step 1 content (self-contained guide)
      file: runtime/connectome/procedure_runner.py
      function: start_procedure
      input: step_1
      output: step_content (guide with What/Why/How)
      trigger: after activate_step
      side_effects: none

  docking_points:
    available:
      - id: dock_run_created
        type: graph_ops
        direction: output
        file: runtime/connectome/procedure_runner.py
        function: start_procedure
        trigger: after create_node
        payload: run_space node
        async_hook: optional
        needs: none
        notes: Health can verify run creation rate

      - id: dock_step_activated
        type: graph_ops
        direction: output
        file: runtime/connectome/procedure_runner.py
        function: start_procedure
        trigger: after create_link (acts_on)
        payload: step link with energy
        async_hook: optional
        needs: none
        notes: Health can verify single active step

    health_recommended:
      - dock_id: dock_run_created
        reason: Track run creation rate for capacity planning
      - dock_id: dock_step_activated
        reason: Verify invariant V3 (single active step)
```

### Flow: Continue Procedure

Explain: Validates current state, transitions to next step, returns new step content with doc chain.

```yaml
flow:
  name: continue_procedure
  purpose: Validate and advance to next step
  scope: run_id → step, status, validation_error
  steps:
    - id: get_active
      description: Find current active step
      file: runtime/connectome/procedure_runner.py
      function: continue_procedure
      input: run_id
      output: current_step node
      trigger: MCP procedure_continue tool
      side_effects: none

    - id: check_validation
      description: Verify next step requirements
      file: runtime/connectome/validation.py
      function: check_validation
      input: run_id, validation_spec
      output: pass/fail + error
      trigger: after get_active
      side_effects: none

    - id: cool_current
      description: Lower energy on current step link
      file: runtime/connectome/procedure_runner.py
      function: continue_procedure
      input: current_link
      output: updated link (e=1)
      trigger: after check_validation (if pass)
      side_effects: graph link updated

    - id: heat_next
      description: Create high-energy link to next step
      file: runtime/connectome/procedure_runner.py
      function: continue_procedure
      input: run_space, next_step
      output: acts_on link (e=8)
      trigger: after cool_current
      side_effects: graph link created

    - id: return_step
      description: Return next step content (self-contained guide)
      file: runtime/connectome/procedure_runner.py
      function: continue_procedure
      input: next_step
      output: step_content (guide with What/Why/How)
      trigger: after heat_next
      side_effects: none

  docking_points:
    available:
      - id: dock_validation_result
        type: graph_ops
        direction: output
        file: runtime/connectome/validation.py
        function: check_validation
        trigger: after validation query
        payload: {passed: bool, error: str}
        async_hook: optional
        needs: none
        notes: Track validation failure rate

      - id: dock_transition_complete
        type: graph_ops
        direction: output
        file: runtime/connectome/procedure_runner.py
        function: continue_procedure
        trigger: after heat_next
        payload: {from_step, to_step, run_id}
        async_hook: optional
        needs: none
        notes: Verify transition atomicity

    health_recommended:
      - dock_id: dock_validation_result
        reason: Track validation failure patterns
      - dock_id: dock_transition_complete
        reason: Verify invariant V3 maintained after transition
```

---

## LOGIC CHAINS

### LC1: Start to First Step

**Purpose:** Initialize procedure and return first step guide

```
start_procedure(procedure_id, actor_id)
  → persistence.create_node(type=space, subtype=run)
    → persistence.create_link(run → procedure, verb=elaborates)
      → get_first_step(procedure_id)
        → persistence.create_link(run → step1, verb=acts_on, e=8)
          → return step1.content
            → {run_id, step_content, status}
```

**Data transformation:**
- Input: `procedure_id: str, actor_id: str`
- After create_node: `run_space: Node`
- Output: `{run_id: str, step_content: str (guide), status: "active"}`

**V2 Simplification:** Step content IS the guide. No doc chain loading.

### LC2: Continue with Validation

**Purpose:** Gate transition on validation, then advance

```
continue_procedure(run_id)
  → get_active_step(run_id)
    → get_next_step(current_step)
      → validation.check_validation(run_id, next.validation_spec)
        → [if pass] persistence.update_link(current, e=1, p=[0.2,0.8])
          → persistence.create_link(run → next, verb=acts_on, e=8)
            → return next_step.content
              → {step_content, status: "active"}
        → [if fail] → {step_content: current.content, status: "validation_failed", error}
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/connectome/procedure_runner.py
    └── imports → runtime/connectome/validation.py
    └── imports → runtime/connectome/persistence.py

runtime/connectome/validation.py
    └── imports → runtime/connectome/persistence.py
```

**V2 Simplification:** No doc_chain.py — steps are self-contained.

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `datetime` | Timestamps | `procedure_runner.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Run Space status | Graph node content | Per-run | Created at start, updated at end |
| Active step | Graph link (high energy) | Per-run | Changes on continue |
| Step guide | Step node content | Per-step | Static, authored at procedure creation |

### State Transitions

```
(none) ──start──▶ active ──continue──▶ active ──continue──▶ completed
                    │                     │
                    └──validation_fail────┘ (stays active)
```

---

## BIDIRECTIONAL LINKS

### Code → Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/connectome/procedure_runner.py` | TBD | `# DOCS: docs/procedure/IMPLEMENTATION_Procedure.md` |
| `runtime/connectome/validation.py` | TBD | `# DOCS: docs/procedure/VALIDATION_Procedure.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM start_procedure | `runtime/connectome/procedure_runner.py:start_procedure` |
| ALGORITHM continue_procedure | `runtime/connectome/procedure_runner.py:continue_procedure` |
| ALGORITHM end_procedure | `runtime/connectome/procedure_runner.py:end_procedure` |
| VALIDATION V3 check | `tests/test_procedure_invariants.py:test_single_active_step` |

---

## RESOLVED DECISIONS

### RD1: File Location

**Decision:** `runtime/connectome/`

Procedures are structured dialogues. `persistence.py` already handles graph operations. Follow existing convention — no new top-level directory.

### RD2: Persistence API

**Decision:** Use existing MERGE pattern.

`persistence._persist_link()` uses `MERGE (a)-[r]->(b) SET r += $props`. This updates properties if link exists, creates if not. No new `update_link()` method needed.

**Verified:** persistence.py lines 287-297 show MERGE + SET pattern.

---

## MARKERS

<!-- @mind:proposition Consider adding runtime/connectome/recovery.py for crash recovery logic (find orphan runs, repair state) -->
