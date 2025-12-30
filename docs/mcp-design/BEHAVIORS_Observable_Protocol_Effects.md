# mind Framework — Behaviors: Observable Protocol Effects

```
STATUS: STABLE
CREATED: 2024-12-15
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
THIS:            BEHAVIORS_Observable_Protocol_Effects.md
ALGORITHM:       ./ALGORITHM_Protocol_Core_Mechanics.md
VALIDATION:      ./VALIDATION_Protocol_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Protocol_System_Architecture.md
TEST:            ./TEST_Protocol_Test_Cases.md
SYNC:            ./SYNC_Protocol_Current_State.md
```

---

## BEHAVIORS

### B1: Agent Receives Task and Loads Appropriate View

```
GIVEN:  An AI agent is assigned a task (implement, debug, review, extend)
WHEN:   The agent starts working
THEN:   The agent loads .mind/PROTOCOL.md first
AND:    The agent identifies the task type
AND:    The agent loads the appropriate VIEW file
AND:    The agent follows the VIEW instructions
```

### B2: Agent Reads Docs Before Modifying Code

```
GIVEN:  An agent needs to modify a module
WHEN:   The agent prepares to write code
THEN:   The agent first loads the module's PATTERNS_*.md
AND:    The agent loads the module's SYNC_*.md
AND:    Only then does the agent modify code
```

### B3: Agent Updates SYNC After Any Change

```
GIVEN:  An agent has made changes to code or docs
WHEN:   The agent completes their work
THEN:   The agent updates ...mind/state/SYNC_Project_State.md
AND:    The agent updates relevant module SYNC files
AND:    The SYNC includes: what changed, why, what's next
```

### B4: Agent Creates Docs for New Modules

```
GIVEN:  An agent needs to create a new module
WHEN:   The module doesn't have documentation
THEN:   The agent creates docs BEFORE implementation
AND:    At minimum: PATTERNS_*.md and SYNC_*.md
AND:    Templates are used from .mind/templates/
```

### B5: Navigation Works Bidirectionally

```
GIVEN:  An agent is looking at code
WHEN:   The agent needs to understand the design
THEN:   The implementation file contains path to docs
AND:    Following the path leads to existing PATTERNS_*.md
AND:    The PATTERNS file explains the design

GIVEN:  An agent is looking at docs
WHEN:   The agent needs to see implementation
THEN:   The doc file contains path to implementation
AND:    Following the path leads to existing code
```

### B6: State Persists Across Sessions

```
GIVEN:  A session ends with work in progress
WHEN:   A new session begins
THEN:   The new agent reads SYNC files
AND:    The new agent understands current state
AND:    The new agent can continue work without re-discovering context
```

### B7: File Names Describe Contents

```
GIVEN:  An agent is scanning a directory
WHEN:   The agent sees file names
THEN:   The names indicate content without opening
AND:    PATTERNS_*.md contains design philosophy
AND:    BEHAVIORS_*.md contains observable effects
AND:    The description part of the name is specific
```

### B8: Cross-Cutting Concepts Are Discoverable

GIVEN:  An agent encounters a concept that spans modules
WHEN:   The agent needs to understand the concept
THEN:   docs/concepts/{concept}/ exists
AND:    CONCEPT_*.md explains what it means
AND:    TOUCHES_*.md shows where it appears in code

### B9: Agents Communicate Blockers and Ideas

GIVEN:  An agent is blocked by a vague requirement
WHEN:   The agent cannot proceed safely
THEN:   The agent adds an `@mind&#58;escalation` marker
AND:    The agent describes the conflict/question in YAML format

GIVEN:  An agent identifies a potential improvement or new feature
WHEN:   The agent wants to suggest it without implementing it yet
THEN:   The agent adds an `@mind&#58;proposition` marker
AND:    The agent describes the idea and its implications in YAML format

GIVEN:  An agent or manager identifies a concrete follow-up task
WHEN:   The task should be tracked for later execution
THEN:   The agent or manager adds an `@mind&#58;todo` marker
AND:    The agent describes the task details in YAML format

---

## INPUTS / OUTPUTS

### Protocol Installation

**Input:** A project without context protocol

**Output:** Project with:
- `.mind/PROTOCOL.md`
- `.mind/views/VIEW_*.md`
- `.mind/templates/*.md`
- `...mind/state/SYNC_Project_State.md`
- Updated .mind/CLAUDE.md with protocol bootstrap
- Updated AGENTS.md with the bootstrap plus Codex guidance (protocol-first reading, verbose outputs, parallel-work awareness)

### Agent Task Execution

**Input:** Task + VIEW + relevant docs

**Output:** 
- Code changes (if applicable)
- Updated SYNC files
- Updated docs (if behavior changed)

---

## EDGE CASES

### E1: No Documentation Exists

```
GIVEN:  Agent needs to work on module with no docs
THEN:   Agent creates docs before implementing
AND:    Agent uses templates
AND:    Agent notes in SYNC that docs were created
```

### E2: Docs Conflict With Code

```
GIVEN:  Agent finds docs that don't match implementation
THEN:   Agent determines which is correct
AND:    Agent updates the incorrect one
AND:    Agent notes the conflict resolution in SYNC
```

### E3: No Appropriate VIEW Exists

```
GIVEN:  Agent's task doesn't match existing VIEWs
THEN:   Agent uses closest VIEW as starting point
AND:    Agent notes in SYNC what was done
AND:    Consider creating new VIEW for this task type
```

### E4: Very Large Module

```
GIVEN:  Module is too large for single doc set
THEN:   Split into sub-modules
AND:    Each sub-module gets own docs
AND:    Parent module docs reference sub-modules
```

---

## ANTI-BEHAVIORS

### A1: Skipping Docs

```
GIVEN:   Agent needs to modify code
WHEN:    Agent modifies without reading PATTERNS
MUST NOT: Change code without understanding design
INSTEAD:  Always read PATTERNS first, then decide if change fits
```

### A2: Forgetting SYNC Update

```
GIVEN:   Agent has completed changes
WHEN:    Agent considers work done
MUST NOT: Leave SYNC files unchanged
INSTEAD:  Always update SYNC, even for small changes
```

### A3: Hallucinating File Existence

```
GIVEN:   Agent needs a file that might not exist
WHEN:    Agent references the file
MUST NOT: Assume file exists without checking
INSTEAD:  Check first, create if needed, never reference non-existent files
```

### A4: Loading Everything

```
GIVEN:   Agent starts a task
WHEN:    Agent loads context
MUST NOT: Load all docs in the project
INSTEAD:  Load VIEW, follow VIEW instructions, load only what's specified
```

---

## MARKERS

<!-- @mind:todo Behavior for handling merge conflicts in SYNC files -->
<!-- @mind:todo Behavior for multi-agent concurrent work -->
<!-- @mind:proposition VIEW for onboarding new agents to a project -->
<!-- @mind:escalation
title: "How detailed should SYNC updates be?"
priority: 5
response:
  status: resolved
  choice: "Summary + pointers"
  behavior: "What changed, why, and pointers to paths (with section/function names when possible). Not exhaustive trace — git has that. Stays scannable."
  pattern: |
    ### 2025-12-23 — tick → tick_created migration
    Changed Moment.tick to tick_created. Migration script created.
    Why: Remove backwards compat per schema evolution policy.
    Pointers: engine/models/nodes.py:Moment, engine/physics/graph/graph_ops.py:add_moment
  notes: "2025-12-23: Decided by Nicolas."
-->
