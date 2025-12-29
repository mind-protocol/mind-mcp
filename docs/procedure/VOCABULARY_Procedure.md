# Procedure — Vocabulary: Terms and Imports

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Procedure.md
PATTERNS:        ./PATTERNS_Procedure.md
BEHAVIORS:       ./BEHAVIORS_Procedure.md
THIS:            VOCABULARY_Procedure.md (you are here)
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md
```

---

## PURPOSE

VOCABULARY defines terms, imports skills/procedures, and maps to ngram schema.

---

## TERMS

### Core Concepts

| Term | Definition |
|------|------------|
| **Procedure** | A space node (subtype: procedure) that contains ordered Steps. Read-only template. |
| **Step** | A narrative node (subtype: step) with guide content. What/Why/How/Watch out format. |
| **Run Space** | A space node (subtype: run) created when executing a procedure. Agent writes here. |
| **Guide** | The step content that tells the agent what to do. Self-contained, no external doc loading. |

### Execution States

| Term | Definition |
|------|------------|
| **Active Step** | Step linked from Run Space with `acts on`, energy > 5, polarity [0.9, 0.1] |
| **Completed Step** | Step linked from Run Space with `receives from`, energy < 2, polarity [0.2, 0.8] |
| **Active Run** | Run Space with status "active" and actor linked via "occupies" |
| **Completed Run** | Run Space with status "completed" and actor linked via "inhabits" |

### Link Types

| Term | Definition |
|------|------------|
| **IMPLEMENTS** | Links doc chain nodes bottom→top. Health implements Implementation, etc. |
| **acts on** | Run Space → Active Step. High energy, forward polarity. |
| **receives from** | Run Space → Completed Step. Low energy, backward polarity. |
| **elaborates** | Run Space → Procedure. Instance-of relationship. |
| **occupies** | Actor → Active Run Space. |
| **inhabits** | Actor → Completed Run Space. |

---

## EXECUTORS

Steps can be executed by different actors. The `executor` field in step content specifies who/what runs the step.

### Executor Types

| Executor | Code | Description | Example |
|----------|------|-------------|---------|
| **Agent LLM** | `agent` | Claude or other LLM executes via reasoning | "Analyze code and suggest improvements" |
| **Pure Code** | `code` | Python/system executes deterministically | "Run pytest, check exit code" |
| **Actor Mechanical** | `actor` | External system, events, logs | "Log audit event", "Send notification" |
| **Hybrid** | `hybrid` | Code prepares, agent decides | "Fetch data, agent interprets" |

### Step Content by Executor

```yaml
# Agent executor - needs guide
step:
  executor: agent
  guide:
    what: "Review the validation implementation"
    why: "Ensure invariants are enforced"
    how: |
      1. Read check_validation function
      2. Verify node_exists and link_exists handling
      3. Check error messages are actionable
    watch_out:
      - "Don't modify, just review"

# Code executor - needs command
step:
  executor: code
  command: "pytest tests/test_validation.py -v"
  success_criteria: "exit_code == 0"
  on_failure: "Return validation_failed with stderr"

# Actor executor - needs event
step:
  executor: actor
  event: "procedure_step_completed"
  payload:
    step_id: "$current_step"
    run_id: "$run_id"
    timestamp: "$now"

# Hybrid executor - needs both
step:
  executor: hybrid
  code_phase:
    command: "git diff --stat"
    output_var: "diff_output"
  agent_phase:
    guide:
      what: "Interpret the diff output"
      context: "$diff_output"
```

### Executor Selection

| Use Case | Executor | Why |
|----------|----------|-----|
| Judgment, creativity needed | `agent` | LLM reasons about ambiguity |
| Deterministic, repeatable | `code` | No variability, faster |
| Side effects, notifications | `actor` | External integration |
| Data prep + interpretation | `hybrid` | Best of both |

---

## NARRATIVE SUBTYPES

### For Doc Chain Nodes

| Subtype | Role | Content |
|---------|------|---------|
| `objective` | Why | Priorities, success signals, tradeoffs |
| `pattern` | Philosophy | Problem, insight, principles, scope |
| `behavior` | Observable | GIVEN/WHEN/THEN, anti-behaviors |
| `vocabulary` | Terms | Definitions + skill/procedure imports |
| `algorithm` | Logic | Steps, decisions, who executes |
| `validation` | Rules | Invariants, MUST/NEVER |
| `implementation` | Code/Exec | Files, entry points, flows, docking |
| `health` | Monitoring | Indicators, thresholds, recovery |

### For Execution

| Subtype | Role | Content |
|---------|------|---------|
| `procedure` | Executable template | Purpose, steps (via CONTAINS) |
| `step` | Guide for agent | What/Why/How/Watch out, validation spec |
| `run` | Execution instance | Status, timestamps, actor link |

---

## SKILL IMPORTS

Skills that use procedures:

| Skill | Procedures Used | Notes |
|-------|-----------------|-------|
| `mind.module_define_boundaries` | `protocol:define_space`, `protocol:add_objectives` | Creates module structure |
| `mind.create_module_documentation` | `protocol:create_doc_chain` | Creates full doc chain |
| `mind.add_cluster` | `protocol:add_cluster` | Creates graph clusters |

---

## PROCEDURE IMPORTS

Standard procedures available:

| Procedure | Purpose | Steps |
|-----------|---------|-------|
| `protocol:define_space` | Create module space | 3 steps |
| `protocol:add_objectives` | Add objectives to space | 4 steps |
| `protocol:add_patterns` | Add patterns to space | 3 steps |
| `protocol:add_behaviors` | Add behaviors to space | 3 steps |
| `protocol:create_doc_chain` | Full chain from templates | 8 steps |
| `protocol:update_sync` | Update SYNC state | 2 steps |

---

## SCHEMA MAPPING

### Node Types

| Concept | node_type | subtype | content |
|---------|-----------|---------|---------|
| Doc chain node | narrative | objective/pattern/behavior/etc. | Full markdown text |
| Procedure template | space | procedure | Purpose, metadata |
| Step | narrative | step | Guide (What/Why/How) |
| Run instance | space | run | Status, timestamps |

### Link Physics

| Link | hierarchy | polarity | permanence | energy |
|------|-----------|----------|------------|--------|
| IMPLEMENTS | -1 | [1, 0] | 1 | 1 |
| acts on | 0 | [0.9, 0.1] | 0.5 | 8 |
| receives from | 0 | [0.2, 0.8] | 0.5 | 1 |
| elaborates | +0.6 | [0.5, 0.5] | 0.5 | 1 |
| occupies | 0 | [0.8, 0.2] | 0.5 | 8 |
| inhabits | 0 | [0.3, 0.7] | 0.5 | 1 |

---

## MARKERS

<!-- @mind:proposition Add custom procedure import mechanism -->
