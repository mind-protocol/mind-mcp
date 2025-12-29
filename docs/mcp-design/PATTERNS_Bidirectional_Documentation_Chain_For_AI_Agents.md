# mind Framework — Patterns: Bidirectional Documentation Chain for AI Agent Workflows

```
STATUS: STABLE
CREATED: 2024-12-15
```

---

## CHAIN

```
THIS:            PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
BEHAVIORS:       ./BEHAVIORS_Observable_Protocol_Effects.md
ALGORITHM:       ./ALGORITHM_Protocol_Core_Mechanics.md
VALIDATION:      ./VALIDATION_Protocol_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Protocol_System_Architecture.md
TEST:            ./TEST_Protocol_Test_Cases.md
SYNC:            ./SYNC_Protocol_Current_State.md
```

---

## THE PROBLEM

AI agents have limited context windows. They can't load everything.

Current failure modes:
1. **Context overload** — Loading too much, missing what matters
2. **Context starvation** — Loading too little, hallucinating the rest
3. **State loss** — Each session starts fresh, work is repeated
4. **Navigation failure** — Not knowing where things are, inventing structure
5. **Update neglect** — Making changes without updating docs, drift accumulates

**Root cause:** No protocol telling agents what to load, when, and what to update.

---

## THE PATTERN

**A mind Framework for AI Agents Working on Code**

The protocol specifies:
1. **What to load** for each task type (VIEWS)
2. **What must exist** for each module (documentation chain)
3. **What to update** after changes (SYNC files)
4. **Where to find things** (consistent structure)

**Key insight:** Agents shouldn't understand the whole system. They should receive:
- A tiny bootstrap (.mind/CLAUDE.md + root AGENTS.md with Codex guidance, including protocol-first reading, no self-run TUI, verbose outputs, and parallel-work awareness)
- One VIEW for their current task
- Tools to navigate when needed

The VIEW tells them everything. Load this. Focus on this. Update this when done.

---

## PRINCIPLES

### 1. Agents Load Views, Not Everything

An agent working on implementation loads VIEW_Implement.md.
That view tells them exactly what files to read.
They don't need to understand the whole protocol.

```
Task → View → Specific files → Work → Update SYNC
```

### 2. Documentation Is Navigation, Not Archive

Docs exist so agents can find what they need.
File names are long and descriptive — agents read them.
Structure is consistent — agents can predict where things are.

```
# Descriptive names
PATTERNS_Narrative_Pressure_As_Structural_Force.md

# Not
patterns.md
```

### 3. State Is Explicit

Every change updates SYNC files.
Next session reads SYNC to understand current state.
Handoffs are documented, not lost.

```
SYNC answers:
- What exists?
- What's in progress?
- What needs to happen next?
```

### 4. Chain Links Code and Docs

Every module has a documentation chain:
- PATTERNS (why this shape, plus **DATA** sources)
- BEHAVIORS (what it does)
- ALGORITHM (how it works)
- VALIDATION (how to verify)
- SYNC (current state)

Implementation files reference their docs.
Docs reference their implementation.
Navigation works both directions.

### 5. Concepts Span Modules

Cross-cutting ideas get their own documentation:
- CONCEPT (what it means)
- TOUCHES (where it appears)

Agents working on any module can understand the concept.

### 6. Human-Agent Feedback Loop

The protocol provides explicit markers for agents to communicate with humans:
- **Escalations** (`@mind&#58;escalation`): When an agent is blocked and needs a human decision.
- **Propositions** (`@mind&#58;proposition`): When an agent suggests improvements or new ideas that require human approval.
- **Todos** (`@mind&#58;todo`): When an agent or manager captures a task that should be tracked and executed.

This ensures that human intuition and agent productivity remain aligned.

---

## DEPENDENCIES

None. The protocol is self-contained markdown files.

---

## INSPIRATIONS

**Literate Programming (Knuth)**
Code and docs woven together. We adapt: docs and code in separate files, but tightly linked.

**Design by Contract (Meyer)**
Preconditions, postconditions, invariants. We capture these in VALIDATION files.

**Zettlekasten**
Atomic notes with links. We use: modules as atoms, chains as links, TOUCHES as indexes.

**Context Window Management (practical LLM work)**
The hard constraint that forces all of this. Can't load everything. Must choose wisely.

---

## WHAT THIS DOES NOT SOLVE

- **Doesn't prevent bad design** — but makes design visible
- **Doesn't write tests** — but tells you what to test
- **Doesn't guarantee sync** — but makes drift detectable
- **Doesn't replace thinking** — but structures it
- **Doesn't work magic** — agents must actually follow the protocol

---

## MARKERS

<!-- @mind:todo MCP tools for navigation (load_view, find_docs, update_sync) -->
<!-- @mind:todo Automated SYNC verification -->
<!-- @mind:todo Integration with different agent frameworks -->
<!-- @mind:proposition Generate module index from doc structure -->
<!-- @mind:proposition Lint for missing chain links -->
<!-- @mind:escalation How to handle very large projects with many areas? -->

<!-- @mind:escalation
title: "This PATTERNS doc is redundant with .mind/FRAMEWORK.md"
priority: 2
context: |
  This file describes "A mind Framework for AI Agents Working on Code".
  The same content now exists canonically in .mind/FRAMEWORK.md.

  Key differences:
  - This doc references VIEWs (VIEW_Implement.md etc.) that don't exist
  - This doc references .mind/ but actual path is .mind/
  - .mind/FRAMEWORK.md is the authoritative bootstrap
question: |
  This doc predates the current .mind/ structure. Should it be:
  a) Deleted (framework is now in .mind/FRAMEWORK.md)
  b) Kept as "original design rationale" with deprecation notice
  c) Updated to describe only protocol MODULE (not framework meta-docs)
-->

<!-- @mind:proposition
title: "Convert to protocol-as-module documentation"
suggestion: |
  If docs/mcp-design/ is kept, it should document the protocol MODULE
  (the code that implements mind init, mind validate, etc.) rather than
  the framework META-DOCS (which belong in .mind/).

  Current state: docs about how to document
  Proposed state: docs about the protocol implementation code
-->
