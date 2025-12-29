# Skills and Protocols Mapping

```
STATUS: V1 SPEC
PURPOSE: Complete inventory of skills and protocols for doctor-driven graph work
```

---

## Doctor → Skill → Protocol Flow

```
Doctor detects gap → Loads skill → Skill guides protocol selection → Membrane executes
```

---

## Skills Inventory

### 1. documentation_health

**Skill File:** `SKILL_Create_Module_Documentation_Chain_From_Templates_And_Seed_Todos.md`
**Skill ID:** `mind.create_module_docs`

**Domain:** Doc chains, coverage, staleness, coherence

**Triggers (from doctor):**
- Undocumented code directory
- Placeholder docs (`{template}`)
- Orphaned docs (point to deleted code)
- Stale SYNC (not updated recently)
- Incomplete doc chains

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| No docs for code directory | `explore_space` → `create_doc_chain` |
| Placeholder docs | `explore_space` → `complete_doc` |
| Orphaned docs | `investigate` → `archive_or_delete` |
| Stale SYNC | `explore_space` → `update_sync` |
| Missing doc in chain | `create_doc` (specific type) |

---

### 2. module_definition

**Skill File:** `SKILL_Define_Module_Boundaries_Objectives_And_Scope.md`
**Skill ID:** `mind.module_define_boundaries`

**Domain:** Module boundaries, objectives, patterns, behaviors

**Triggers (from doctor):**
- Missing modules.yaml entry
- Missing OBJECTIVES
- Missing PATTERNS
- Missing BEHAVIORS
- Module scope unclear

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| New module needed | `explore_space` → `define_space` → `add_objectives` |
| Missing objectives | `explore_space` → `add_objectives` |
| Missing patterns | `explore_space` → `add_patterns` |
| Missing behaviors | `explore_space` → `add_behaviors` |
| Refactoring needed | `explore_space` → `add_patterns` → `record_work` |

---

### 3. code_structure

**Skill File:** `SKILL_Implement_Write_Or_Modify_Code_With_Doc_Chain_Coupling.md`
**Skill ID:** `mind.implement_with_docs`

**Domain:** Code health, monoliths, complexity, implementation docs

**Triggers (from doctor):**
- Monolith file (>500 lines)
- God function (>100 lines)
- Deep nesting (>4 levels)
- Missing DOCS: reference in code
- No IMPLEMENTATION doc

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| Missing implementation docs | `explore_space` → `add_implementation` |
| No docking points | `add_implementation` |
| Code without docs reference | `add_implementation` → `update_code_reference` |
| Refactor needed (info only) | `record_work` (note the issue) |

---

### 4. health_verification

**Skill File:** `SKILL_Define_And_Verify_Health_Signals_Mapped_To_Validation_Invariants.md`
**Skill ID:** `mind.health_define_and_verify`

**Domain:** Runtime verification, health indicators, invariants

**Triggers (from doctor):**
- Module has validations without health checks
- Runtime failures not caught
- New critical invariant needs verification
- No health indicators for module

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| No health coverage | `explore_space` → `add_health_coverage` |
| Validation missing | `add_invariant` first, then `add_health_coverage` |
| No docking points | `add_implementation` first |
| Health check outdated | `investigate` → `update_health` |

---

### 5. escalation_management

**Skill File:** `SKILL_Debug_Investigate_And_Fix_Issues_With_Evidence_First.md`
**Skill ID:** `mind.debug_investigate`

**Domain:** Blockers, stuck work, decisions needed

**Triggers (from doctor):**
- Stuck module (DESIGNING with no activity)
- Unresolved escalation
- Decision blocking progress
- TODO rot (aging backlog)

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| Stuck module | `investigate` → `raise_escalation` or `resolve_blocker` |
| Unresolved escalation | `investigate` → `resolve_blocker` |
| Decision needed | `investigate` → `capture_decision` |
| TODO aging | `investigate` → `record_work` (triage) |

---

### 6. progress_tracking

**Skill File:** `SKILL_Update_Module_Sync_State_And_Record_Markers.md`
**Skill ID:** `mind.update_sync`

**Domain:** Session handoffs, progress recording, goal management

**Triggers (from doctor):**
- Work session completed
- Handoff needed
- Goals need updating
- SYNC needs update

**Protocol mapping:**

| Situation | Protocols |
|-----------|-----------|
| Session complete | `record_work` |
| Goals completed | `record_work` → `update_goals` |
| New goals discovered | `add_goals` |
| Before context switch | `record_work` |

---

## Protocols Inventory

### Core Protocols (Always Needed)

| Protocol | Purpose | Output Cluster |
|----------|---------|----------------|
| `explore_space` | Understand what exists | exploration moment |
| `record_work` | Document progress | progress moment + escalations + goals |
| `investigate` | Deep dive into issue | investigation moment + optional goal/escalation |

### Doc Chain Protocols

| Protocol | Purpose | Output Cluster |
|----------|---------|----------------|
| `create_doc_chain` | Full doc chain for module | objectives + patterns + behaviors + sync |
| `add_objectives` | Define goals | primary + secondary + non-objectives + moment |
| `add_patterns` | Define design decisions | patterns + anti-patterns + moment |
| `add_behaviors` | Define observable effects | behaviors linked to objectives + moment |
| `add_algorithm` | Define procedures | algorithm + moment |
| `add_implementation` | Document code structure | implementation + docks + moment |
| `update_sync` | Update current state | updated SYNC node + moment |

### Verification Protocols

| Protocol | Purpose | Output Cluster |
|----------|---------|----------------|
| `add_invariant` | Add validation constraint | validation + ensures links + moment |
| `add_health_coverage` | Add runtime verification | health + 2 docks + verifies links + moment |

### Issue Handling Protocols

| Protocol | Purpose | Output Cluster |
|----------|---------|----------------|
| `raise_escalation` | Flag blocker | escalation + about links + moment |
| `resolve_blocker` | Resolve escalation | rationale + resolution moment |
| `capture_decision` | Record decision | decision + alternatives + affects links + moment |

### Goal Management Protocols

| Protocol | Purpose | Output Cluster |
|----------|---------|----------------|
| `add_goals` | Create new goals | goals + moment |
| `update_goals` | Update goal status | updated goals + moment |
| `add_todo` | Create actionable TODO | todo + about links + moment |

---

## Protocol Dependencies

```
add_health_coverage
├── requires: validation exists
│   └── if missing: call_protocol add_invariant
└── requires: docking points exist
    └── if missing: call_protocol add_implementation

add_invariant
└── requires: space exists
    └── if missing: call_protocol define_space

add_implementation
└── requires: space exists
    └── if missing: call_protocol define_space

add_behaviors
└── requires: objectives exist
    └── if missing: call_protocol add_objectives

add_objectives
└── requires: space exists
    └── if missing: call_protocol define_space
```

---

## Doctor → Protocol Mapping Summary

| Doctor Finding | Skill | Primary Protocol |
|----------------|-------|------------------|
| Undocumented code | documentation_health | create_doc_chain |
| Placeholder docs | documentation_health | complete_doc |
| Orphaned docs | documentation_health | archive_or_delete |
| Stale SYNC | documentation_health | update_sync |
| Incomplete chain | documentation_health | create_doc (specific) |
| Missing mapping | module_definition | define_space |
| Stuck module | escalation_management | investigate |
| TODO rot | escalation_management | investigate |
| Test gaps | health_verification | add_health_coverage |
| Monolith file | code_structure | (info - record for refactor) |
| No health coverage | health_verification | add_health_coverage |

---

## Implementation Priority

### Phase 1: Core (Minimum Viable)

1. `explore_space` — Foundation for all other work
2. `record_work` — Track what happened
3. `investigate` — Understand issues

### Phase 2: Doc Chain

4. `add_objectives` — Define goals
5. `add_patterns` — Define design
6. `update_sync` — Update state

### Phase 3: Verification

7. `add_invariant` — Define constraints
8. `add_health_coverage` — Runtime verification
9. `add_implementation` — Code structure

### Phase 4: Issue Handling

10. `raise_escalation` — Flag blockers
11. `resolve_blocker` — Handle escalations
12. `capture_decision` — Record decisions

### Phase 5: Goal Management

13. `add_goals` — Create goals
14. `update_goals` — Update status
15. `add_todo` — Create actionable TODOs
16. `create_doc_chain` — Full chain creation

---

## Files to Create

### Skills (Markdown)

```
skills/
├── documentation_health.md
├── module_definition.md
├── code_structure.md
├── health_verification.md
├── escalation_management.md
└── progress_tracking.md
```

### Protocols (YAML)

```
protocols/
├── explore_space.yaml
├── record_work.yaml
├── investigate.yaml
├── add_objectives.yaml
├── add_patterns.yaml
├── add_behaviors.yaml
├── add_algorithm.yaml
├── add_implementation.yaml
├── update_sync.yaml
├── add_invariant.yaml
├── add_health_coverage.yaml
├── raise_escalation.yaml
├── resolve_blocker.yaml
├── capture_decision.yaml
├── add_goals.yaml
├── update_goals.yaml
├── add_todo.yaml
└── create_doc_chain.yaml
```

---

## CHAIN

- **Parent:** SYNC_MCP_Tools.md
- **Implements:** PATTERNS_MCP_Tools.md (Skills and Protocols sections)

<!-- @mind:escalation The skills and protocols listed in this mapping document reference files that
     may not exist in the current codebase. The `procedures/` directory is missing and skill files
     in `templates/mind/skills/` need verification. -->
