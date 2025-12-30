# Doctor Issues to Protocols Mapping

Maps health check issues to remediation protocols and skills.

<!-- @mind:escalation This mapping references protocols that should exist in `procedures/` directory,
     but that directory does not currently exist in the codebase. The `DoctorIssue.protocol` field
     integration depends on these protocol definitions being available. -->

---

## How It Works

```
Doctor detects issue → Issue has protocol field → Membrane can auto-trigger protocol
```

When `mind doctor` finds an issue, the issue includes:
- `type`: Issue category
- `severity`: critical/warning/info
- `protocol`: Which protocol remediates this
- `suggestion`: Human-readable fix

The membrane system can:
1. Read doctor output
2. Extract issues with protocols
3. Auto-run protocols to fix issues

---

## Issue → Protocol → Skill Mapping

### Critical Issues (Score -10 each)

| Issue | Protocol | Skill | What It Does |
|-------|----------|-------|--------------|
| `UNDOCUMENTED` | `protocol_define_space` → `protocol_create_doc_chain` | `mind.create_module_documentation` | Creates space + full doc chain |
| `MISSING_DOCS` | `protocol_create_doc_chain` | `mind.create_module_documentation` | Creates missing doc chain |
| `PLACEHOLDER` | (manual) | `mind.create_module_documentation` | Fill template content |
| `MONOLITH` | (manual refactor) | `mind.implement_write_or_modify_code` | Split large files |

### Warning Issues (Score -3 each)

| Issue | Protocol | Skill | What It Does |
|-------|----------|-------|--------------|
| `INCOMPLETE_CHAIN` | `protocol_create_doc_chain` | `mind.create_module_documentation` | Adds missing doc types |
| `DOC_TEMPLATE_DRIFT` | `protocol_create_doc_chain` | `mind.create_module_documentation` | Fills missing sections |
| `STALE_SYNC` | `protocol_update_sync` | `mind.sync_update_module_state` | Updates SYNC with current state |
| `ACTIVITY_GAP` | `protocol_record_work` → `protocol_update_sync` | `mind.sync_update_module_state` | Records work, updates SYNC |
| `NO_DOCS_REF` | `protocol_add_implementation` | `mind.implement_write_or_modify_code` | Adds code→doc references |
| `MISSING_VALIDATION` | `protocol_add_invariant` | `mind.health_define_and_verify` | Creates validation narratives |
| `UNCOVERED_HEALTH` | `protocol_add_health_coverage` | `mind.health_define_and_verify` | Creates health indicators + docks |
| `ABANDONED` | `protocol_explore_space` | `mind.orchestrate_feature_integration` | Explores, decides: complete or remove |
| `NON_STANDARD_DOC_TYPE` | (manual rename) | `mind.create_module_documentation` | Rename to standard prefix |
| `NAMING_CONVENTION` | (manual rename) | `mind.onboard_understand_module_codebase` | Fix naming |

### Info Issues (Score -1 each)

| Issue | Protocol | Skill | What It Does |
|-------|----------|-------|--------------|
| `MISSING_OBJECTIVES` | `protocol_add_objectives` | `mind.define_module_boundaries` | Adds ranked objectives |
| `MISSING_PATTERNS` | `protocol_add_patterns` | `mind.define_module_boundaries` | Documents design decisions |
| `NO_EXPLORATION` | `protocol_explore_space` | `mind.onboard_understand_module_codebase` | Explores before work |
| `VAGUE_NAME` | (manual rename) | `mind.onboard_understand_module_codebase` | Improve naming |

---

## Protocol Dependency Graph

```
protocol_define_space
    └── protocol_create_doc_chain
            └── protocol_add_objectives
            └── protocol_add_patterns

protocol_explore_space
    └── protocol_add_invariant
            └── protocol_add_health_coverage

protocol_explore_space
    └── protocol_add_implementation

protocol_record_work
    └── protocol_update_sync
```

---

## Auto-Fix Flow

When running `mind work` to auto-fix issues:

```python
def auto_fix_issue(issue: Issue) -> bool:
    if not issue.protocol:
        return False  # Manual fix required

    # Load skill for context
    skill = load_skill_for_issue(issue.type)

    # Run protocol via membrane
    result = membrane.run_protocol(
        protocol=issue.protocol,
        context={
            "space": extract_space(issue.path),
            "actor_id": "agent_doctor",
            "issue": issue
        }
    )

    return result.success
```

---

## Issue Detection → Protocol Trigger Examples

### UNDOCUMENTED → protocol_define_space + protocol_create_doc_chain

```yaml
issue:
  type: UNDOCUMENTED
  path: "src/physics/tick"
  protocol: protocol_define_space

trigger:
  space_id: "space_physics_tick"
  parent_space: "space_physics"
  then: protocol_create_doc_chain
```

### MISSING_VALIDATION → protocol_add_invariant

```yaml
issue:
  type: MISSING_VALIDATION
  path: "docs/physics/tick"
  protocol: protocol_add_invariant

trigger:
  space: "space_physics_tick"
  context:
    existing_behaviors: [from BEHAVIORS doc]
```

### STALE_SYNC → protocol_update_sync

```yaml
issue:
  type: STALE_SYNC
  path: "docs/physics/tick/SYNC_Tick_Runner.md"
  protocol: protocol_update_sync

trigger:
  space: "space_physics_tick"
  context:
    days_stale: 21
    commits_since: 5
```

---

## Adding New Issue Types

When adding a new doctor check:

1. Define the check in `ALGORITHM_Project_Health_Doctor.md`
2. Include `protocol` field in Issue with remediation protocol
3. Add mapping to this document
4. Create protocol if it doesn't exist
5. Link to appropriate skill

```python
Issue(
    type="NEW_TASK_TYPE",
    severity="warning",
    path=str(path),
    message="Description",
    details={...},
    suggestion="Human-readable fix",
    protocol="protocol_that_fixes_this"  # <-- Required for auto-fix
)
```
