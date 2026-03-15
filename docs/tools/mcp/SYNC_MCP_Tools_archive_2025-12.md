# Archived: SYNC_MCP_Tools.md

Archived on: 2025-12-24
Original file: SYNC_MCP_Tools.md (formerly SYNC_Membrane_System.md)

---

## Maturity

**STATUS: CANONICAL**

What's canonical (v1):
- Architecture: Doctor → Skill → Protocol → Membrane → Graph
- MCP server with 4 tools (start, continue, abort, list)
- Session-based dialogue with step sequencing
- YAML protocol definitions
- Cluster output (nodes + dense links)
- Coverage validation system (`specs/coverage.yaml` + `tools/coverage/validate.py`)
- All 19 protocols implemented
- 15 skills in templates/mind/skills/
- Doctor → Protocol mapping complete

What's proposed (v2):
- Dynamic skill generation
- Parallel protocol execution
- Approval workflows
- Undo/rollback

---


## Recent Changes

### 2025-12-24: Completion Verification System IMPLEMENTED (Agent 2)

Mandatory verification system fully implemented:

**Documentation:**
- `VALIDATION_Completion_Verification.md` — architecture and flow
- `MAPPING_Issue_Type_Verification.md` — complete mapping for ALL issue types

**Implementation:**
- `runtime/repair_verification.py` — verification checks and feedback formatting
- `runtime/repair_core.py` — added `spawn_repair_agent_with_verification_async`
- `runtime/repair.py` — now uses verification-enabled spawn

**Features:**
- File checks (patterns present/absent)
- Command checks (tests, imports, health)
- Membrane checks (graph queries - placeholder for MCP connection)
- Automatic retry on failure (max 3)
- Detailed feedback for agent continuation
- RepairResult tracks: verification_results, verification_passed, retry_count, membrane_protocols_needed

**Issue types with verification:** 13 (all major types covered)

### 2025-12-24: v1 Complete (Agent 2)

All membrane v1 objectives achieved:
- Coverage: 19/19 protocols (100%)
- Health checks: PASS (session lifecycle + step ordering)
- Doctor integration: `DoctorIssue.protocol` field for auto-fix
- E2E testing: Protocol flows verified working

Architecture confirmed:
- **Membrane** = structured dialogues → graph nodes/links
- **Repair agents** = file changes (code, docs)
- **Integration** = agents MUST call membrane for graph verification

### 2025-12-24: Membrane Health Implementation

- Created `HEALTH_Membrane_System.md` — full indicator specs for runtime verification
- Implemented `runtime/doctor_checks_membrane.py`:
  - `doctor_check_membrane_health`: Session lifecycle + step ordering verification
  - `doctor_check_membrane_protocols`: Protocol YAML structure validation
- Integrated with `doctor_checks.py` aggregator
- **Result**: Health checks PASS for session lifecycle and step ordering

### 2025-12-24: Verification Testing

- All 19 protocols load and execute correctly via ConnectomeRunner
- Tested `capture_decision` protocol: session flow works (start → continue → step progression)
- Doctor runs successfully: 68 critical issues found (mostly undocumented code directories)
- MCP server path updated to `protocols/` directory
- **Note**: MCP server needs restart to discover new protocols (currently shows old test protocols)

### 2025-12-24: Doctor Integration (Agent 2)

- Added `protocol` field to `DoctorIssue` dataclass
- Updated doctor checks with protocol auto-trigger fields:
  - UNDOCUMENTED → `define_space`
  - STALE_SYNC → `update_sync`
  - INCOMPLETE_CHAIN → `create_doc_chain`
  - DOC_TEMPLATE_DRIFT → `create_doc_chain`
  - NO_DOCS_REF → `add_implementation`
  - INVARIANT_NO_TEST → `add_health_coverage`
  - INVARIANT_UNTESTED → `add_health_coverage`
  - ESCALATION → `resolve_blocker`
  - DOC_GAPS → `record_work`

### 2025-12-24: All Protocols Complete (Agent 2)

- Created `add_goals.yaml` — goal narrative creation
- Created `add_todo.yaml` — actionable TODO creation
- Created `add_behaviors.yaml` — observable behavior documentation
- Created `add_algorithm.yaml` — procedure/pseudocode documentation
- Copied all protocols from templates to `protocols/`
- Updated `specs/coverage.yaml` — 100% coverage

### 2025-12-24: Phase 2-4 Protocols (Agent 1)

- Created `add_objectives.yaml`, `add_patterns.yaml`, `update_sync.yaml`
- Created `raise_escalation.yaml`, `resolve_blocker.yaml`, `capture_decision.yaml`

### 2025-12-24: Coverage Validation System

- Created `docs/concepts/coverage/` doc chain (OBJECTIVES through SYNC)
- Created `specs/coverage.yaml` — single source of truth
- Created `tools/coverage/validate.py` — checks all paths

### 2025-12-24: add_cluster Primitive

- Created `SKILL_Add_Cluster_Dynamic_Creation.md` — cluster design knowledge
- Created `protocols/add_cluster.yaml` — schema-guided cluster creation

---



---

# Archived: SYNC_MCP_Tools.md (Section 2)

Archived on: 2025-12-24
Original file: SYNC_MCP_Tools.md (formerly SYNC_Membrane_System.md)

---

## v1.2 Features (Complete)

### 1. Graph Schema & Persistence

All protocol create steps now validate and persist to the mind graph:

```
engine/connectome/schema.py
├── NODE_SCHEMAS — space, narrative, moment, thing, todo, actor
├── LINK_SCHEMAS — contains, expresses, about, relates, blocks, references
├── FieldDef — type validation with patterns, ranges, enums
├── SchemaError — error with guidance and examples
├── validate_node() — validates all fields against schema
├── validate_link() — validates link types and endpoints
└── validate_connectivity() — ensures new clusters connect to existing graph
```

```
engine/connectome/persistence.py
├── GraphPersistence — validated writes to graph
├── persist_cluster() — atomic node+link creation
├── validate_only() — check without persisting
└── PersistenceResult — success/error with details
```

**Key constraints:**
- All fields validated against schema (type, required, patterns)
- New clusters MUST connect to existing nodes (no orphans)
- Errors returned with HOW TO FIX guidance

### 2. Mandatory Verification with Membrane Queries

Repair agents verify completion with actual graph queries:

```
mind/repair_verification.py
├── VerificationCheck — file, command, membrane check types
├── VerificationResult — pass/fail with details
├── VerificationSession — loop protection with retry tracking
├── verify_completion() — runs all checks for issue type
├── create_membrane_query_function() — connects to graph for verification
├── _execute_membrane_query() — maps checks to graph queries
├── format_verification_feedback() — structured feedback for agent restart
├── format_escalation_feedback() — when max retries exceeded
└── format_todo_suggestion() — for partial progress scenarios
```

**Membrane verification:**
- Checks if space nodes exist in graph
- Verifies narrative nodes (sync, implementation, etc.)
- Confirms links between nodes
- Returns actual graph state, not file-based assumptions

**Loop protection:**
- Max 3 retries per issue
- Max 10 total session retries
- Oscillation detection (same failures repeating)
- Auto-escalate via `raise_escalation` protocol

### 3. Completion Handoff Protocol

Every protocol now calls `completion_handoff` at the end:

```yaml
call_handoff:
  type: call_protocol
  protocol: completion_handoff
  inputs:
    space_id: "{space_id}"
    task_id: "protocol_name_{id}"
```

The handoff gathers:
- Task summary & files changed
- Key decisions made
- Confidence level & reasoning
- Escalations (blocked) & propositions (improvements)
- Next steps & context files
- Improvement suggestions for skill/protocol/integration/context

### 4. Protocol Attribute Explanations

Protocols now include detailed comments explaining each node/link attribute:

```yaml
- id: "{space_id}"
  node_type: space
  # ━━━ ATTRIBUTE EXPLANATIONS ━━━
  # id: "{space_id}"
  #   WHAT: Unique identifier
  #   WHY: Used in all graph queries
  #   FORMAT: space_<area>_<module>
```

### 5. Protocol Reflection Steps

Protocols now include a `gather_thoughts` step for feedback:

```yaml
gather_thoughts:
  type: ask
  questions:
    - name: protocol_thoughts
      ask: "Any thoughts on improving this protocol?"
    - name: context_observations
      ask: "Anything about context/process that could be better?"
```

---


## Next Steps

All v1.2 objectives complete:
- ✅ End-to-end Testing — Protocol flows work
- ✅ Coverage Validation — 100% (20/20 protocols)
- ✅ Auto-fix Integration — `DoctorIssue.protocol` field
- ✅ Mandatory Verification — `repair_verification.py`
- ✅ Completion Handoff — All protocols call `completion_handoff`
- ✅ Loop Protection — Max retries + oscillation detection
- ✅ Graph Schema — `engine/connectome/schema.py`
- ✅ Graph Persistence — `engine/connectome/persistence.py`
- ✅ Connectivity Constraint — New clusters must connect
- ✅ Verification Integration — Membrane queries for graph verification
- ✅ Protocol Explanations — All 20 protocols have attribute explanations
- ✅ Graph Database Connection — FalkorDB connected via `GraphOps`/`GraphQueries`

**Protocol Pattern Status:**
- 19 protocols: `gather_thoughts` → `call_handoff` → `$complete`
- 1 protocol (`completion_handoff`): terminal protocol, no self-call needed

**v2 Opportunities:**
1. **Direct Protocol Execution** — `mind work --protocol=update_sync` CLI command
2. **End-to-End Test Suite** — Automated tests for full doctor→repair→verify flow
3. **Protocol Analytics** — Track execution time, success rate, feedback patterns

---

