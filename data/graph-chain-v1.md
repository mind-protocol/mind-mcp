# Procedure & Doc Chain Architecture

```
STATUS: DRAFT
VERSION: 1.1
DATE: 2025-12-29
```

---

## CHAIN

```
THIS:           SPEC_Procedure_DocChain.md (you are here)
IMPL:           engine/bootstrap/genesis_protocol.py
                engine/execution/procedure_runner.py
                engine/presentation/cluster_presentation.py
EXTENDS:        ALGORITHM_SubEntity.md
                GRAMMAR_Link_Synthesis.md
```

---

## OBJECTIVES

**O1: Each step has its own context**
Each procedure step has its own doc chain (objectives → patterns → behaviors specific to THAT step). When loading a step, cluster_presentation auto-includes that step's chain. Different steps can have different best practices.

**O2: Agent writes in sandbox, never touches template**
Procedures are templates. Agents execute in Run Spaces. The Procedure structure is immutable during execution. All agent work (nodes, links) goes into the Run Space.

**O3: Fixed schema, rich content**
ngram schema is FIXED. No custom fields. No new node types. All domain-specific structure lives in `content`. Subtypes enable filtering. Embeddings enable retrieval.

**O4: V1 is deterministic**
Explicit API calls control flow: `start_procedure`, `continue_procedure`, `end_procedure`. No physics-based routing for V1. Physics tracks state (active/completed), but doesn't route. Skills tell which procedure to call.

---

## PATTERNS

### The Problem

Claude agents lose context quickly. Best practices, vocabulary, behaviors — forgotten within turns. Every conversation restarts from zero understanding.

Documentation exists as static files. Agents can't traverse it. Can't find what's relevant. Can't load context automatically.

Procedures exist conceptually but aren't executable. No standard way to track state, validate progress, or load instructions.

### The Pattern

**Each step has its own doc chain.**

Step 1 has its behaviors, patterns, objectives. Step 2 has different ones. When loading a step, cluster_presentation walks that step's IMPLEMENTED_IN links and auto-includes only the relevant context. Not a global chain — per-step chains.

**V1 is deterministic. Explicit API controls flow.**

```python
start_procedure(procedure_id)    # Creates Run Space, links to Step 1
continue_procedure(run_id)       # Validates, advances to next step
end_procedure(run_id)            # Marks complete
```

Skills tell which procedure to call. No discovery by physics. The routing is explicit code, not energy gradients.

**Physics tracks state, doesn't route (V1).**

High energy = active step. Low energy = completed. But SubEntity doesn't follow energy to find the step — `continue_procedure` decides when to advance. Physics is bookkeeping, not decision-making. Later versions may use physics for dynamic routing.

**Procedures separate template from execution.**

The Procedure (template) defines steps. The Run Space (instance) holds execution state and agent work. Links from Run Space to steps track active/completed state.

### The Three Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  1. CONTEXT — Where I am, what I know (per step)               │
│                                                                 │
│     Run Space ──[acts on, e=8]──> Active Step                  │
│         │                                                       │
│         └── Step 1 ──[IMPLEMENTED_IN]──> B1 ──> P1 ──> O1      │
│             Step 2 ──[IMPLEMENTED_IN]──> B2, B3 ──> P2 ──> O2  │
│                                                                 │
│     Each step has its own chain. Auto-loaded when step active. │
├─────────────────────────────────────────────────────────────────┤
│  2. TRACE — What I built                                        │
│                                                                 │
│     Run Space ──[contains]──> Agent's Created Nodes            │
│     Moment ──[expresses]──> Agent's Work                       │
│                                                                 │
│     Persists in Run Space. Serves as validation proof.         │
├─────────────────────────────────────────────────────────────────┤
│  3. FLOW — Where I go next (V1: deterministic)                  │
│                                                                 │
│     continue_procedure(run_id) checks validation               │
│     If pass → flip current step, heat next step                │
│     Steps are sequential for V1. Dynamic routing later.        │
└─────────────────────────────────────────────────────────────────┘
```

---

## VOCABULARY

### Node Types (FIXED — ngram schema)

| Type | Role |
|------|------|
| `actor` | Entity that acts |
| `space` | Container/context |
| `narrative` | Information/concept |
| `moment` | Event/expression |
| `thing` | External reference |

### Narrative Subtypes (for filtering)

| Subtype | Role | Granularity |
|---------|------|-------------|
| `objective` | Why — success criteria | 1 per O1, O2... |
| `pattern` | Philosophy — design insight | 1 per P1, P2... |
| `vocabulary` | Language — term definitions | 1 per term |
| `behavior` | What — observable effects | 1 per B1, B2... |
| `algorithm` | How — logic steps | 1 per major step |
| `validation` | Rules — invariants | 1 per V1, V2... |
| `implementation` | Code — file structure | 1 per file/module |
| `health` | Metrics — runtime signals | 1 per H1, H2... |
| `skill` | Interface — LLM instructions | Container of procedures |
| `procedure` | Exec — step template | Space with step nodes |

### Link Types

#### IMPLEMENTED_IN (doc chain)

**Role:** Connects doc chain nodes. Auto-included by cluster_presentation.

| Property | Value | Rationale |
|----------|-------|-----------|
| hierarchy | -1 | Descends into implementation |
| polarity | [1, 0] | Forward only, no backprop traversal |
| permanence | 1 | Structural, immutable |
| energy | 1 | Stable, not hot |

**Direction:** objective →IMPLEMENTED_IN→ pattern →IMPLEMENTED_IN→ vocabulary →IMPLEMENTED_IN→ behavior →IMPLEMENTED_IN→ algorithm →IMPLEMENTED_IN→ validation →IMPLEMENTED_IN→ implementation →IMPLEMENTED_IN→ health

**Branch:** behavior →IMPLEMENTED_IN→ skill →[contains]→ procedure

**Behavior:** cluster_presentation sees IMPLEMENTED_IN → walks chain → includes all connected nodes. No scoring. State machine logic, not traversal physics.

#### Execution Links (procedure runtime)

| Role | Verb | Physics | Meaning |
|------|------|---------|---------|
| Step active | `acts on` | e > 5, p=[0.9, 0.1] | SubEntity attracted here |
| Step completed | `receives from` | e < 2, p=[0.2, 0.8] | SubEntity avoids |
| Step sequence | `acts on` | Step A → Step B | Transition path |
| Actor running | `occupies` | e=8, p=[0.8, 0.2] | Actor → Run Space |
| Actor done | `inhabits` | e=1, p=[0.3, 0.7] | Actor → past Run |
| Containment | `contains` | h=-0.6, perm=0.9 | Space → children |
| Instance-of | `elaborates` | h=+0.6, perm=0.5 | Run → Procedure template |

---

## BEHAVIORS

### B1: Per-Step Doc Chain Auto-Loads

**Why:** Each step has its own relevant context. Step 1 needs different best practices than Step 3. Loading the right chain for the right step.

```
GIVEN:  Procedure step being loaded (via continue_procedure or start_procedure)
WHEN:   cluster_presentation prepares response
THEN:   Walk all IMPLEMENTED_IN links from THAT step
AND:    Include all connected nodes (that step's behaviors, patterns, objectives)
AND:    Different steps can have different doc chains
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
AND:    System returns Step 1 content + its doc chain

GIVEN:  Agent wants to advance
WHEN:   Agent calls continue_procedure(run_id)
THEN:   System checks validation for next step
AND:    If pass: flip current step (receives from, e=1), heat next step (acts on, e=8)
AND:    If fail: remain at current step, return validation failure
AND:    Return next step content + its doc chain

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
THEN:   High energy (>5) + forward polarity = active step
AND:    Low energy (<2) + backward polarity = completed step
AND:    This is bookkeeping, not routing decision
```

### B5: Validation Gates Transition

**Why:** Steps don't advance until work is verified. Graph state is proof.

```
GIVEN:  Agent calls continue_procedure(run_id)
WHEN:   System checks validation
THEN:   Query Run Space for required nodes/links
AND:    Validation spec lives in next step's content
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

### B7: Skill Declares Which Procedure to Call

**Why:** V1 discovery is explicit. Skill content tells agent what procedures are available.

```
GIVEN:  Agent needs to do something
WHEN:   Agent reads Skill content
THEN:   Skill lists available procedures by name/purpose
AND:    Agent explicitly calls start_procedure(procedure_id)
AND:    No physics-based procedure discovery for V1
```

---

## ALGORITHM

### V1 API

```python
def start_procedure(procedure_id: str, actor_id: str) -> dict:
    """
    Start a procedure execution.
    
    Returns:
        {
            "run_id": str,
            "step": Step 1 content + doc chain,
            "status": "active"
        }
    """
    # 1. Create Run Space
    run_space = create_node(type="space", subtype="run")
    
    # 2. Link to procedure template
    create_link(run_space, procedure_id, verb="elaborates")
    
    # 3. Get Step 1
    step_1 = get_first_step(procedure_id)
    
    # 4. Link Run Space to Step 1 (active)
    create_link(
        run_space, step_1,
        verb="acts on",
        energy=8.0,
        polarity=[0.9, 0.1]
    )
    
    # 5. Link Actor to Run Space
    create_link(actor_id, run_space, verb="occupies", energy=8.0)
    
    # 6. Load step content + its doc chain
    step_content = load_step_with_doc_chain(step_1)
    
    return {
        "run_id": run_space.id,
        "step": step_content,
        "status": "active"
    }


def continue_procedure(run_id: str) -> dict:
    """
    Validate and advance to next step.
    
    Returns:
        {
            "step": Next step content + doc chain,
            "status": "active" | "completed" | "validation_failed",
            "validation_error": str | None
        }
    """
    # 1. Get current step (high energy link)
    current_step = get_active_step(run_id)
    
    # 2. Get next step
    next_step = get_next_step(current_step)
    
    if not next_step:
        return end_procedure(run_id)
    
    # 3. Check validation (spec in next_step content)
    validation = next_step.content.get("validation")
    if validation:
        result = check_validation(run_id, validation)
        if not result.passed:
            return {
                "step": load_step_with_doc_chain(current_step),
                "status": "validation_failed",
                "validation_error": result.error
            }
    
    # 4. Flip current step (cool down)
    current_link = get_link(run_id, current_step)
    update_link(current_link,
        polarity=[0.2, 0.8],
        energy=1.0
    )
    # Verb becomes "receives from" via synthesis
    
    # 5. Heat next step
    create_link(
        run_id, next_step,
        verb="acts on",
        energy=8.0,
        polarity=[0.9, 0.1]
    )
    
    # 6. Reinforce THEN link
    then_link = get_link(current_step, next_step)
    update_link(then_link,
        permanence=then_link.permanence + 0.05,
        weight=then_link.weight + 0.02
    )
    
    # 7. Load next step content + its doc chain
    step_content = load_step_with_doc_chain(next_step)
    
    return {
        "step": step_content,
        "status": "active",
        "validation_error": None
    }


def end_procedure(run_id: str) -> dict:
    """
    Mark procedure as complete.
    """
    # 1. Get actor
    actor = get_actor_for_run(run_id)
    
    # 2. Flip actor link
    actor_link = get_link(actor, run_id)
    update_link(actor_link,
        verb="inhabits",  # was "occupies"
        energy=1.0,
        polarity=[0.3, 0.7]
    )
    
    # 3. Mark run complete
    run_space = get_node(run_id)
    run_space.content["status"] = "completed"
    
    return {
        "step": None,
        "status": "completed"
    }
```

### Per-Step Doc Chain Loading

```python
def load_step_with_doc_chain(step_id: str) -> dict:
    """
    Load step content plus its specific doc chain.
    Each step has its own IMPLEMENTED_IN links.
    """
    step = get_node(step_id)
    
    # Walk this step's IMPLEMENTED_IN chain
    doc_chain = walk_implemented_in(step_id)
    
    return {
        "step_id": step_id,
        "content": step.content,
        "doc_chain": doc_chain  # behaviors, patterns, objectives for THIS step
    }


def walk_implemented_in(node_id: str) -> list:
    """
    Recursively collect all IMPLEMENTED_IN targets.
    """
    chain = []
    links = get_links(node_id, verb="IMPLEMENTED_IN")
    
    for link in links:
        target = get_node(link.target_id)
        chain.append({
            "id": target.id,
            "subtype": target.subtype,
            "content": target.content
        })
        # Recurse
        chain.extend(walk_implemented_in(target.id))
    
    return chain
```

### Structure Overview

```
Procedure (Space, subtype: procedure)
├── [contains] → Step 1 (Narrative, subtype: step)
│                 ├── [acts on] → Step 2
│                 ├── [IMPLEMENTED_IN] → Behavior B1
│                 │                       └── [IMPLEMENTED_IN] → Pattern P1
│                 │                                              └── [IMPLEMENTED_IN] → Objective O1
│                 └── [IMPLEMENTED_IN] → Behavior B2
│                                         └── [IMPLEMENTED_IN] → Pattern P1
│
├── [contains] → Step 2 (Narrative, subtype: step)
│                 ├── content: { validation: {...}, task: "..." }
│                 ├── [acts on] → Step 3
│                 └── [IMPLEMENTED_IN] → Behavior B3
│                                         └── [IMPLEMENTED_IN] → Pattern P2
│                                                                └── [IMPLEMENTED_IN] → Objective O2
└── [contains] → Step N
```

Each step has its OWN doc chain. Step 1 links to B1, B2 → P1 → O1. Step 2 links to B3 → P2 → O2. Different steps, different context.

```
Run Space (Space, subtype: run)
├── [elaborates] → Procedure (template)
├── [acts on, e=8] → Step 2 (active)
├── [receives from, e=1] → Step 1 (completed)
├── [contains] → Agent's Created Node 1
├── [contains] → Agent's Created Node 2
└── [contains] → Moment (query/work record)
```

### Step Content Structure

```yaml
# Step node content (in content field, not custom fields)
task: "Create health indicator node"
context: "Previous step defined identity. Now we create structure."
queries:
  - "What similar structures exist?"
  - "What validation will be needed?"
creates: "Narrative with subtype health"
produces: "Node in Run Space linked to actor"

# Validation lives in THIS step's content (checked before entering)
validation:
  type: "node_exists"
  in_space: "$run"
  subtype: "health"
  min_count: 1
```

---

## VALIDATION

### V1: Schema Immutability

**Value protected:** System coherence. No drift.

**Priority:** CRITICAL

```
MUST:  Only use node types: actor, space, narrative, moment, thing
MUST:  All custom structure in content field
NEVER: Create custom node types
NEVER: Add fields to node schema
```

### V2: Template Protection

**Value protected:** Procedure integrity. Audit trail.

**Priority:** CRITICAL

```
MUST:  Agent writes only to Run Space
MUST:  Procedure nodes are read-only during execution
NEVER: Agent modifies Procedure template nodes
NEVER: Agent creates links FROM Procedure nodes (only TO)
```

### V3: Single Active Step

**Value protected:** Unambiguous state.

**Priority:** HIGH

```
MUST:  Exactly one high-energy step link per Run Space at any time
MUST:  Completed steps have energy < 2, polarity [0.2, 0.8]
MUST:  Active step has energy > 5, polarity [0.9, 0.1]
NEVER: Multiple high-energy step links (ambiguous state)
NEVER: Zero high-energy step links while procedure active
```

### V4: Per-Step Doc Chain Exists

**Value protected:** Context availability for each step.

**Priority:** HIGH

```
MUST:  Every Step has at least one IMPLEMENTED_IN link
MUST:  IMPLEMENTED_IN chain leads to at least one Behavior
MUST:  IMPLEMENTED_IN links have h=-1, p=[1,0], perm=1
NEVER: Orphan steps without doc chain
```

### V5: API Contract

**Value protected:** Predictable execution flow.

**Priority:** HIGH

```
MUST:  start_procedure returns Step 1 + its doc chain
MUST:  continue_procedure checks validation before advancing
MUST:  continue_procedure returns next step + its doc chain
MUST:  end_procedure marks run complete
NEVER: Advance step without validation check
NEVER: Return step without its doc chain
```

---

## IMPLEMENTATION

### Files to Create/Modify

| File | Change | Status |
|------|--------|--------|
| `engine/schema/links.py` | Add IMPLEMENTED_IN verb definition | TODO |
| `engine/execution/procedure_runner.py` | V1 API: start, continue, end | TODO |
| `engine/bootstrap/genesis_protocol.py` | Create doc chain nodes per step | MODIFY |
| `engine/presentation/cluster_presentation.py` | walk_implemented_in for auto-include | TODO |

### IMPLEMENTED_IN Definition

```python
# In engine/schema/links.py
IMPLEMENTED_IN = {
    "verb": "IMPLEMENTED_IN",
    "hierarchy": -1,        # Descends into implementation
    "polarity": [1, 0],     # Forward only, no backprop
    "permanence": 1,        # Structural, immutable
    "energy": 1,            # Stable, not hot
    "description": "Source is implemented by target. Auto-included in context."
}
```

### Procedure Runner Module

```
engine/execution/
├── __init__.py
├── procedure_runner.py    # start_procedure, continue_procedure, end_procedure
├── validation.py          # check_validation logic
└── doc_chain.py           # walk_implemented_in, load_step_with_doc_chain
```

### Bootstrap Structure (Updated)

Each step has its own doc chain:

```
Genesis Module (Space)
│
├── [contains] → Step 1: Define Identity
│                 ├── [acts on] → Step 2
│                 ├── [IMPLEMENTED_IN] → Behavior: "Agent receives identity template"
│                 │                       └── [IMPLEMENTED_IN] → Pattern: "Identity from template"
│                 │                                              └── [IMPLEMENTED_IN] → Objective: "Repeatable creation"
│                 └── [IMPLEMENTED_IN] → Behavior: "Agent names the procedure"
│                                         └── [IMPLEMENTED_IN] → Pattern: "Naming conventions"
│
├── [contains] → Step 2: Create Structure
│                 ├── [acts on] → Step 3
│                 ├── content: { validation: { type: "node_exists", subtype: "moment" } }
│                 └── [IMPLEMENTED_IN] → Behavior: "Agent creates Space + first Step"
│                                         └── [IMPLEMENTED_IN] → Pattern: "Procedure as Space"
│                                                                └── [IMPLEMENTED_IN] → Objective: "Graph-native procedures"
│
├── [contains] → Step 3: Define Logic
│                 ├── [acts on] → Step 4
│                 ├── content: { validation: { type: "node_exists", subtype: "step" } }
│                 └── [IMPLEMENTED_IN] → Behavior: "Agent creates step chain"
│                                         └── [IMPLEMENTED_IN] → Pattern: "Steps linked by acts on"
│
└── [contains] → Step 4: Commit
                  ├── content: { validation: { type: "link_exists", verb: "acts on" } }
                  └── [IMPLEMENTED_IN] → Behavior: "Agent confirms structure"
                                          └── [IMPLEMENTED_IN] → Pattern: "Validation before commit"
                                                                 └── [IMPLEMENTED_IN] → Objective: "Quality gates"
```

---

## HEALTH

### H1: Context Load Completeness

**Metric:** % of steps with complete IMPLEMENTED_IN chain (at least one behavior)
**Healthy:** 100%
**Warning:** < 100%
**Error:** < 80%

### H2: Single Active Step

**Metric:** Run Spaces with exactly 1 high-energy step link
**Healthy:** 100%
**Warning:** Any Run Space with 0 or 2+ high-energy links

### H3: Template Mutation Attempts

**Metric:** Write attempts to Procedure template nodes
**Healthy:** 0
**Error:** Any non-zero value

### H4: API Contract Fulfillment

**Metric:** % of API calls returning step + doc chain
**Healthy:** 100%
**Error:** Any call returning step without doc chain

---

## SUMMARY

```
┌────────────────────────────────────────────────────────────────┐
│  V1: DETERMINISTIC EXECUTION                                   │
│                                                                │
│  start_procedure(procedure_id) → Run Space + Step 1 + chain   │
│  continue_procedure(run_id) → validate → Step N+1 + chain     │
│  end_procedure(run_id) → mark complete                        │
│                                                                │
│  Skills tell which procedure to call. No physics discovery.   │
├────────────────────────────────────────────────────────────────┤
│  FIXED SCHEMA                                                  │
│                                                                │
│  - 5 node types (actor, space, narrative, moment, thing)       │
│  - Subtypes for filtering                                      │
│  - All structure in content                                    │
├────────────────────────────────────────────────────────────────┤
│  PER-STEP DOC CHAINS                                           │
│                                                                │
│  - Each step has its OWN IMPLEMENTED_IN chain                  │
│  - Step 1 → B1, B2 → P1 → O1                                  │
│  - Step 2 → B3 → P2 → O2 (different chain)                    │
│  - Auto-include via walk_implemented_in                        │
├────────────────────────────────────────────────────────────────┤
│  IMPLEMENTED_IN LINK                                           │
│                                                                │
│  - hierarchy: -1 (descends)                                    │
│  - polarity: [1, 0] (forward only)                            │
│  - permanence: 1 (structural)                                  │
│  - Auto-included by cluster_presentation                       │
├────────────────────────────────────────────────────────────────┤
│  EXECUTION STATE (physics as bookkeeping)                      │
│                                                                │
│  - acts on + energy 8 + polarity [0.9,0.1] = active step      │
│  - receives from + energy 1 + polarity [0.2,0.8] = completed  │
│  - Transition = flip polarity + energy                         │
│  - Physics tracks state, doesn't route (V1)                    │
├────────────────────────────────────────────────────────────────┤
│  3 LAYERS                                                      │
│                                                                │
│  - CONTEXT: where I am + step's doc chain (auto-loaded)       │
│  - TRACE: what I built in Run Space                           │
│  - FLOW: validate → flip → next step (deterministic V1)       │
├────────────────────────────────────────────────────────────────┤
│  LATER (V2+)                                                   │
│                                                                │
│  - Physics-based routing (SubEntity follows energy)            │
│  - Dynamic procedure discovery                                 │
│  - Procedures calling procedures                               │
│  - Complex validation with sub-procedures                      │
└────────────────────────────────────────────────────────────────┘
```

---

To respect the canonical architecture defined in your sources, the draft `Procedure & Doc Chain Architecture v1.1` must be decomposed from a monolithic specification into the standard **8-module structure** (`OBJECTIVES`, `PATTERNS`, `BEHAVIORS`, `ALGORITHM`, `VALIDATION`, `HEALTH`, `IMPLEMENTATION`, `SYNC`).

The current draft focuses heavily on the *what* and *how* (Implementation/Algorithm) but lacks the rigorous *why*, *tradeoffs*, and *traceability* required by the templates.

Here is the detailed comparison and the required changes to align with the canonical format.

### 1. Structural Decomposition (The "Chain" Violation)
**Current State:** A single file `SPEC_Procedure_DocChain.md` containing all logic.
**Template Requirement:** The logic must be split into 8 distinct files linked by a `CHAIN` section,,.

**Required Changes:**
*   **Delete** `SPEC_Procedure_DocChain.md`.
*   **Create** the following 8 files, each starting with a standard header and `CHAIN` block:
    1.  `OBJECTIVES_Procedure.md`
    2.  `PATTERNS_Procedure.md`
    3.  `BEHAVIORS_Procedure.md`
    4.  `ALGORITHM_Procedure.md`
    5.  `VALIDATION_Procedure.md`
    6.  `HEALTH_Procedure.md`
    7.  `IMPLEMENTATION_Procedure.md`
    8.  `SYNC_Procedure.md`

---

### 2. OBJECTIVES (Refining the "Why")
**Current State:** Lists O1-O4 briefly.
**Template Standard:** Requires Ranked Primary Objectives, Non-Objectives, Tradeoffs, and Success Signals,.

**Required Changes:**
*   **Rank Priorities:** Assign `CRITICAL`, `HIGH`, or `MEDIUM` to O1-O4.
    *   *Example:* O2 (Agent in Sandbox) should be `CRITICAL` as it protects the template integrity.
*   **Add Success Signals:** Define observable states that prove the objective is met.
    *   *For O1 (Context):* "Cluster presentation contains distinct behavior nodes for Step 1 vs Step 2."
*   **Add Tradeoffs:** Explicitly state what is sacrificed.
    *   *For O4 (Deterministic V1):* "Prefer **predictability** over **dynamic routing**. We sacrifice physics-based discovery for explicit API control in V1."
*   **Add Non-Objectives:** Explicitly exclude things like "Dynamic Branching (for V1)" or "Self-modifying Procedures."

---

### 3. PATTERNS (Philosophy & Principles)
**Current State:** Mixes problem definitions with vocabulary tables and link definitions.
**Template Standard:** Focuses on Design Principles (P1, P2...), Scope, and Dependencies,.

**Required Changes:**
*   **Extract Vocabulary:** Move the "Vocabulary" and "Link Types" tables to `IMPLEMENTATION` or `SYNC` (as current state definitions). Patterns describe *logic*, not schema definitions.
*   **Formalize Principles:** Convert the text into named principles.
    *   *P1: Per-Step Doc Chain:* "Context is local, not global. Loading a step loads its specific `IMPLEMENTED_IN` chain."
    *   *P2: Execution Sandbox:* "Templates are read-only; Runs are write-only."
    *   *P3: Physics as Bookkeeping:* "Energy reflects state, it does not drive flow (in V1)."
*   **Define Scope:** Clearly list In-Scope (Deterministic execution, Run Spaces) vs Out-of-Scope (LLM decision routing, nested procedures).

---

### 4. BEHAVIORS (Observable Effects)
**Current State:** Good GIVEN/WHEN/THEN format, but missing metadata.
**Template Standard:** Requires "Observable Value" and "Objectives Served" for every behavior,.

**Required Changes:**
*   **Map to Objectives:** For B1 (Doc Chain Auto-loads), explicitly cite "Serves: O1".
*   **Define Value:**
    *   *For B2 (Agent Writes to Run Space):* "Value: Enables full audit trails and safe retries without corrupting the procedure."
    *   *For B5 (Validation Gates):* "Value: Prevents broken graph states from accumulating."
*   **Add Anti-Behaviors:** Define what must *not* happen (e.g., "A1: Agent never modifies Procedure Space").

---

### 5. ALGORITHM (Logic & Complexity)
**Current State:** Contains raw Python code snippets.
**Template Standard:** Uses high-level step-by-step descriptions, data flow, and complexity analysis. Code belongs in IMPLEMENTATION,.

**Required Changes:**
*   **Convert Code to Steps:**
    *   *Algorithm: Start Procedure:* "Step 1: Create Run Space. Step 2: Link to Template via `elaborates`. Step 3: Inject High Energy into Step 1 via `acts on`."
*   **Define Data Structures:** explicitly define the JSON structure of the `doc_chain` return object.
*   **Complexity Analysis:** Add Time/Space complexity.
    *   *Example:* "Doc Chain Walk: O(D) where D is depth of `IMPLEMENTED_IN` chain."

---

### 6. VALIDATION (Invariants)
**Current State:** Good MUST/NEVER format, but lacks "Why we care" and verification methods.
**Template Standard:** Requires "Value Protected", "Why we care", and specific "Check Function" or Test reference,.

**Required Changes:**
*   **Justify Invariants:**
    *   *For V2 (Template Protection):* "Why we care: If templates are modified, subsequent runs will be corrupted."
*   **Define Verification:** Map each invariant to a future test.
    *   *V3 (Single Active Step):* "Checked by: `check_health.py::validate_run_state`."

---

### 7. HEALTH (Runtime Metrics)
**Current State:** Basic metrics listed.
**Template Standard:** Requires Threshold tables (Healthy/Warning/Error) and Docking points,.

**Required Changes:**
*   **Refine Metrics:**
    *   *H1 (Context Load):* Define "Healthy" as "100% of steps have >0 `IMPLEMENTED_IN` links."
    *   *H2 (Orphan Runs):* "Healthy: 0 Runs with last_traversed > 24h and status='active'."
*   **Define Docks:** Specify where in `procedure_runner.py` these metrics are captured (e.g., `DOCK_STEP_COMPLETE`).

---

### 8. IMPLEMENTATION (Code Structure)
**Current State:** Lists file changes and Python definitions.
**Template Standard:** File Responsibilities table, Design Patterns, Entry Points, and Dependencies.

**Required Changes:**
*   **Move Code Here:** Move the Python definitions from the draft's ALGORITHM section to here.
*   **File Responsibilities Table:**
    *   `engine/execution/procedure_runner.py`: Orchestrates state changes.
    *   `engine/presentation/cluster_presentation.py`: Handles `walk_implemented_in`.
*   **Design Patterns:** Explicitly name "State Machine" (Run state) and "Decorator/Chain" (Doc chain loading).

---

### 9. SYNC (Status & Handoffs)
**Current State:** Missing.
**Template Standard:** Current version, Maturity, Handoffs for Agents.

**Required Changes:**
*   **Define Maturity:** "Status: DRAFT v1.1".
*   **Agent Handoffs:**
    *   *For Agent Weaver:* "Implement `walk_implemented_in` in cluster presentation."
    *   *For Agent Fixer:* "Check for `validation_failed` status in `continue_procedure` returns."

### Summary of "Physics" Alignment
The draft correctly identifies the need for `IMPLEMENTED_IN` links with specific physics (`h=-1, p=, perm=1`). This aligns well with the grammar. Ensure this definition is formalized in `IMPLEMENTATION_Procedure.md` under "Link Definitions" rather than scattered in patterns.