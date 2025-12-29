# mind Framework — Implementation: Overview

```
STATUS: STABLE
CREATED: 2025-12-18
```

---

## CHAIN

```
PATTERNS:        ../PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
BEHAVIORS:       ../BEHAVIORS_Observable_Protocol_Effects.md
ALGORITHM:       ../ALGORITHM_Protocol_Core_Mechanics.md
VALIDATION:      ../VALIDATION_Protocol_Invariants.md
HEALTH:          ../HEALTH_Protocol_Verification.md
SYNC:            ../SYNC_Protocol_Current_State.md
THIS:            ./IMPLEMENTATION_Protocol_File_Structure.md
```

---

## OVERVIEW

The protocol is implemented as markdown structure and templates. The "implementation" is the file layout, how agents navigate it, and how the CLI installs and validates it.

This document consolidates the protocol implementation details that were previously split across multiple files.

---

## FILE STRUCTURE

### Template Directory (Source of Truth)

```
../../../templates/mind/
├── PROTOCOL.md
├── PRINCIPLES.md
├── views/                 # 11 VIEW files
├── templates/             # 10 doc templates
└── state/
    └── <!-- ../../../templates/..mind/state/SYNC_Project_State.md -->
```

### Installed Directory (Target Project)

```
../../../.mind/
├── PROTOCOL.md
├── PRINCIPLES.md
├── views/
├── templates/
├── modules.yaml
├── state/
│   ├── <!-- ...mind/state/SYNC_Project_State.md -->
│   └── <!-- ...mind/state/SYNC_Project_Health.md -->
└── traces/                # Optional agent logs
```

### File Responsibilities

| File Pattern | Purpose | When Loaded |
|--------------|---------|-------------|
| PROTOCOL.md | Navigation rules | Session start |
| PRINCIPLES.md | Working stance | Session start |
| VIEW_*.md | Task instructions | Based on task |
| *_TEMPLATE.md | Doc scaffolding | When creating docs |
| ...mind/state/SYNC_Project_State.md | Project state and handoff | Session start |
| ...mind/state/SYNC_Project_Health.md | Doctor output | After `doctor` |
| modules.yaml | Code ↔ docs mapping | CLI and tooling |

### Bootstrap Files

The protocol is surfaced through:
- ../../../.mind/CLAUDE.md (includes templates/CLAUDE_ADDITION.md, PRINCIPLES.md, PROTOCOL.md)
- Root `AGENTS.md` mirroring ../../../.mind/CLAUDE.md plus `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`
- ../../../.mind/agents/manager/AGENTS.md for manager role

---

## SCHEMAS AND CONFIG

### modules.yaml Schema

```yaml
modules:
  {module_name}:
    code: str           # Glob pattern for source files
    docs: str           # Path to documentation directory
    tests: str          # Optional test path
    maturity: enum      # DESIGNING | CANONICAL | PROPOSED | DEPRECATED
    owner: str          # agent | human | team-name
    entry_points: list  # Main files to start reading
    internal: list      # Implementation details, not public API
    depends_on: list    # Other modules this requires
    patterns: list      # Design patterns used
    notes: str          # Quick context
```

### SYNC File Structure

```yaml
SYNC:
  required:
    - LAST_UPDATED: date
    - STATUS: enum          # CANONICAL | DESIGNING | PROPOSED | DEPRECATED
  sections:
    - MATURITY
    - CURRENT STATE
    - HANDOFF: FOR AGENTS
    - HANDOFF: FOR HUMAN
  optional:
    - CONSCIOUSNESS TRACE
    - STRUCTURE
    - POINTERS
```

### VIEW File Structure

```yaml
VIEW:
  required:
    - WHY THIS VIEW EXISTS
    - CONTEXT TO LOAD
    - THE WORK
    - AFTER
  optional:
    - VERIFICATION
```

### Configuration Defaults

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| Ignore patterns | ../../../.mind/config.yaml | Common patterns | Paths to skip in doctor |
| Monolith threshold | ../../../.mind/config.yaml | 500 lines | SYNC archive trigger |
| Stale days | ../../../.mind/config.yaml | 14 days | When SYNC is stale |
| Disabled checks | ../../../.mind/config.yaml | [] | Doctor checks to skip |

---

## FLOWS AND LINKS

### Entry Points

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| Bootstrap | ../../../.mind/CLAUDE.md + AGENTS.md | Agent session start |
| Navigation | ../../../.mind/PROTOCOL.md | After bootstrap |
| Task selection | ../../../.mind/views/VIEW_*.md | Based on task type |
| State check | ...mind/state/SYNC_Project_State.md | Before any work |
| Module context | docs/{area}/{module}/PATTERNS_*.md | When modifying code |

### Agent Session Flow

```
Agent starts
  → read ../../../.mind/CLAUDE.md / AGENTS.md
  → read PROTOCOL + PRINCIPLES
  → load ...mind/state/SYNC_Project_State.md
  → select VIEW_{Task}
  → load module docs
  → do work
  → update SYNC files
```

### Documentation Chain Flow

```
PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → HEALTH → SYNC
```

### Bidirectional Links

#### Code → Docs

```python
# DOCS: docs/{area}/{module}/PATTERNS_*.md
```

#### Docs → Code

| Doc Section | Points To |
|-------------|-----------|
| PATTERNS: Dependencies | Module imports |
| IMPLEMENTATION: Code structure | File paths |
| VALIDATION: Invariants | Test files |
| SYNC: Pointers | Key file locations |

### Dependencies (Internal)

```
../../../.mind/CLAUDE.md
  → PROTOCOL.md
  → PRINCIPLES.md
PROTOCOL.md
  → views/VIEW_*.md
  → templates/*_TEMPLATE.md
VIEW_*.md
  → ...mind/state/SYNC_Project_State.md
  → docs/{area}/{module}/*.md
modules.yaml
  → code paths
  → docs paths
```
