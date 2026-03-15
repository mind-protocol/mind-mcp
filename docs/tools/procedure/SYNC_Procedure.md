# Procedure — SYNC: Current State

```
STATUS: DRAFT
VERSION: v2.0
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
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
THIS:            SYNC_Procedure.md (you are here)

IMPL:            runtime/connectome/procedure_runner.py (planned)
```

---

## CURRENT STATE

### Documentation

| Doc | Status | Last Updated |
|-----|--------|--------------|
| OBJECTIVES | READY (v2.0) | 2025-12-29 |
| PATTERNS | READY (v2.0) | 2025-12-29 |
| BEHAVIORS | READY (v2.0) | 2025-12-29 |
| VOCABULARY | READY (v2.0) | 2025-12-29 |
| ALGORITHM | READY (v2.0) | 2025-12-29 |
| VALIDATION | READY (v2.0) | 2025-12-29 |
| IMPLEMENTATION | READY (v2.0) | 2025-12-29 |
| HEALTH | READY (v2.0) | 2025-12-29 |
| SYNC | READY (v2.0) | 2025-12-29 |

### Implementation

| Component | Status | Location |
|-----------|--------|----------|
| MCP procedure tools | STABLE | `mcp/server.py` |
| YAML loader | STABLE | `runtime/connectome/persistence.py` |
| Session management | STABLE | In-memory dict in server |
| Run Space creation | NOT STARTED | Planned: `runtime/connectome/procedure_runner.py` |
| Step transitions | NOT STARTED | Planned: `runtime/connectome/procedure_runner.py` |
| Validation | NOT STARTED | Planned: `runtime/connectome/validation.py` |
| Health checkers | NOT STARTED | Planned: `runtime/health/procedure_health.py` |

**V2 Note:** No `doc_chain.py` — steps are self-contained guides.

### Related Modules

| Module | Relationship | SYNC |
|--------|--------------|------|
| mcp-tools | API layer for procedure execution | `docs/mcp-tools/SYNC_MCP_Tools.md` |
| physics/subentity | Energy-based state tracking | `docs/physics/subentity/SYNC_SubEntity.md` |
| schema | Node/link types for Run Space | `docs/schema/SYNC_Schema.md` |

---

## HANDOFFS

### To Implementation Agent

**Context:** Docs are ready at V2.0. All escalations resolved. Implement V2.

**Priority tasks:**
1. Create `runtime/connectome/procedure_runner.py` with `start_procedure`, `continue_procedure`, `end_procedure`
2. Create `runtime/connectome/validation.py` with `check_validation`, `parse_validation_spec`
3. Add IMPLEMENTS to `runtime/connectome/schema.py`
4. Integrate with existing MCP tools

**Key decisions to follow:**
- **Steps are self-contained guides** — no doc chain loading at runtime
- Step content includes What/Why/How/Watch out sections
- IMPLEMENTS links are for audit trail only (not loaded at runtime)
- Use MERGE + SET for link updates (no new persistence methods)
- ISO-8601 timestamps
- WARNING on missing guide sections (don't block)

**Read first:**
- ALGORITHM_Procedure.md (execution logic, step content format)
- VOCABULARY_Procedure.md (executor types, terms)
- IMPLEMENTATION_Procedure.md (file structure, data flows)
- VALIDATION_Procedure.md (invariants to enforce)

---

## BLOCKED ON

None. Ready for implementation.

---

## MARKERS

<!-- @mind:handoff TO=agent_groundwork: Implement procedure_runner.py per V2.0 ALGORITHM spec (self-contained steps) -->
<!-- @mind:handoff TO=agent_keeper: Review doc chain for V2.0 consistency after implementation -->
<!-- @mind:resolved V2.0 documentation complete — runtime doc chain loading removed, steps are guides -->


---

## ARCHIVE

Older content archived to: `SYNC_Procedure_archive_2025-12.md`
