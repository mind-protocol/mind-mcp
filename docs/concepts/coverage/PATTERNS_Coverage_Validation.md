# PATTERNS: Coverage Validation System
@mind:id: PATTERNS.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Design decisions for the coverage validation system
```

---

## Core Pattern: Layered Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCTOR LAYER                            │
│  Detections: gaps, events, triggers                             │
│  D-001, D-002, D-003...                                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ requires_skill
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SKILL LAYER                             │
│  Domain knowledge: when to use which protocols                  │
│  mind.create_module_docs, mind.debug_investigate...           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ calls_protocols
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PROTOCOL LAYER                           │
│  Executable procedures: ask → query → branch → create           │
│  explore_space, record_work, investigate...                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ produces
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT LAYER                             │
│  Graph mutations: nodes + links                                 │
│  moment, narrative, escalation, thing...                        │
└─────────────────────────────────────────────────────────────────┘
```

**Why this shape**: Each layer has single responsibility. Validation traces paths layer by layer.

---

## Pattern: YAML as Single Source

```yaml
# specs/coverage.yaml - THE source of truth

doctor_workflow:
  detections:
    - id: "D-UNDOC-CODE"
      trigger: "Undocumented code directory"
      skill: "mind.create_module_docs"

skills:
  mind.create_module_docs:
    file: "SKILL_Create_Module_Documentation_Chain..."
    protocols:
      - explore_space
      - create_doc_chain

protocols:
  explore_space:
    file: "protocols/explore_space.yaml"
    required_steps: [ask, query, create]
    output_nodes: [moment]
    output_links: [about, expresses]
```

**Why YAML**: Machine-parseable, human-readable, diffable, versionable.

**Anti-pattern**: Separate markdown docs that must be manually kept in sync.

---

## Pattern: Validator as Gate

```
coverage.yaml → validate_coverage.py → COVERAGE_REPORT.md
                        │
                        ├── Exit 0: All paths complete
                        └── Exit 1: Gaps found (blocks CI)
```

**Why gate**: Coverage regressions are bugs. Catch before merge.

---

## Pattern: Detection Categories

Doctor detections grouped by domain:

| Category | Detection Pattern | Example |
|----------|-------------------|---------|
| `doc_health` | Missing/stale/orphaned docs | D-UNDOC-CODE |
| `module_def` | Missing boundaries/objectives | D-NO-OBJECTIVES |
| `code_struct` | Monoliths, complexity | D-MONOLITH |
| `health_ver` | Missing health coverage | D-NO-HEALTH |
| `escalation` | Stuck modules, blockers | D-STUCK-MODULE |
| `progress` | Stale SYNC, missing handoffs | D-STALE-SYNC |

**Why categorize**: Maps 1:1 to skills. Each category = one skill domain.

---

## Pattern: Protocol Completeness Check

A protocol is complete when it has:

```yaml
required:
  - triggers          # What starts it
  - requires_skills   # Domain knowledge
  - steps:
      - type: ask     # At least one input gathering
      - type: create  # At least one graph mutation
  - output:
      - nodes: [...]  # What gets created
      - links: [...]  # How it connects
```

**Why these requirements**: Protocols without input are hardcoded. Protocols without output are no-ops.

---

## Pattern: Incremental Coverage

```
Phase 1: Core protocols (explore_space, record_work, investigate)
         → Covers: orientation, progress, debugging

Phase 2: Doc chain protocols (add_objectives, add_patterns, update_sync)
         → Covers: module definition, documentation

Phase 3: Verification protocols (add_invariant, add_health_coverage)
         → Covers: health verification

Phase 4: Issue handling (raise_escalation, resolve_blocker, capture_decision)
         → Covers: escalation management

Phase 5: Full coverage (remaining protocols)
         → Covers: all doctor detections
```

**Why phased**: Validate incrementally. Each phase adds coverage.

---

## Anti-Patterns

### A1: Orphan Detection

Detection exists but no skill handles it.
```yaml
# BAD
detections:
  - id: "D-ORPHAN"
    trigger: "Something happens"
    skill: null  # No handler!
```

### A2: Skill Without Protocols

Skill claims to handle detection but references no protocols.
```yaml
# BAD
skills:
  mind.empty_skill:
    protocols: []  # What does it do?
```

### A3: Protocol Without Output

Protocol has steps but creates nothing.
```yaml
# BAD
steps:
  ask_stuff:
    type: ask
    next: $complete  # No create step!
```

### A4: Circular Protocol Calls

Protocol A calls B, B calls A.
```yaml
# BAD - infinite loop
protocol_a:
  steps:
    call_b:
      type: call_protocol
      protocol: protocol_b

protocol_b:
  steps:
    call_a:
      type: call_protocol
      protocol: protocol_a
```

---

## CHAIN

- **Prev:** OBJECTIVES_Coverage_Validation.md
- **Next:** BEHAVIORS_Coverage_Validation.md
