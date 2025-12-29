# SYNC: MCP Tools

```
LAST_UPDATED: 2025-12-29
UPDATED_BY: Claude (documentation review and correction)
STATUS: DESIGNING
```

<!-- Updated 2025-12-29: procedures/ directory now exists with 24 protocol YAML files.
     Skills in templates/mind/skills/ still need verification. -->

---

## Terminology

| Term | Format | Purpose |
|------|--------|---------|
| **Skill** | Markdown | Domain knowledge, which protocols when |
| **Protocol** | YAML | Procedure: ask → query → branch → call_protocol → create |
| **Membrane** | Tool | Executor that runs protocols |

---

## Current State

### Coverage

```
Protocols: 20/20 implemented (100%)
├── Phase 0: add_cluster ✅
├── Phase 1: explore_space, record_work, investigate ✅
├── Phase 2: add_objectives, add_patterns, update_sync, add_behaviors, add_algorithm ✅
├── Phase 3: add_invariant, add_health_coverage, add_implementation ✅
├── Phase 4: raise_escalation, resolve_blocker, capture_decision ✅
├── Phase 5: define_space, create_doc_chain, add_goals, add_todo ✅
└── Meta: completion_handoff ✅ (called by all protocols)
```

### Implemented

| Component | Status | Location |
|-----------|--------|----------|
| MCP Server | Working | `mcp/server.py` |
| ConnectomeRunner | Working | `runtime/connectome/runner.py` |
| Session + call stack | Working | `runtime/connectome/session.py` |
| Step execution | Working | `runtime/connectome/steps.py` |
| **Graph Schema** | Working | `runtime/connectome/schema.py` |
| **Graph Persistence** | Working | `runtime/connectome/persistence.py` |
| Coverage validator | @mind:escalation | `tools/coverage/validate.py` (may not exist) |
| Health checker | Working | `runtime/doctor_checks_membrane.py` |
| **Verification System** | @mind:escalation | `runtime/repair_verification.py` (needs verification) |
| Protocols | Working | `procedures/*.yaml` (24 protocols) |
| Skills | N/A | Located in mind-platform repo, not mind-mcp |
| Health doc | Complete | `docs/mcp-tools/HEALTH_MCP_Tools.md` |
| Verification doc | Complete | `docs/mcp-tools/VALIDATION_Completion_Verification.md` |
| Issue→Verification map | Complete | `docs/mcp-tools/MAPPING_Issue_Type_Verification.md` |

### Skills (15 total)

| Skill ID | File | Status |
|----------|------|--------|
| mind.add_cluster | SKILL_Add_Cluster_Dynamic_Creation.md | ✅ |
| mind.author_skills | SKILL_Author_Skills_Structure_And_Quality.md | ✅ |
| mind.author_protocols | SKILL_Author_Protocols_Structure_And_Quality.md | ✅ |
| mind.create_module_docs | SKILL_Create_Module_Documentation_Chain... | ✅ |
| mind.module_define_boundaries | SKILL_Define_Module_Boundaries... | ✅ |
| mind.implement_with_docs | SKILL_Implement_Write_Or_Modify_Code... | ✅ |
| mind.health_define_and_verify | SKILL_Define_And_Verify_Health_Signals... | ✅ |
| mind.debug_investigate | SKILL_Debug_Investigate_And_Fix_Issues... | ✅ |
| mind.update_sync | SKILL_Update_Module_Sync_State... | ✅ |
| mind.onboard | SKILL_Onboard_Understand_Existing_Module... | ✅ |
| mind.extend | SKILL_Extend_Add_Features_To_Existing... | ✅ |
| mind.ingest | SKILL_Ingest_Raw_Data_Sources... | ✅ |
| mind.orchestrate | SKILL_Orchestrate_Feature_Integration... | ✅ |
| mind.review | SKILL_Review_Evaluate_Changes... | ✅ |

### Protocols (20 total)

| Phase | Protocol | Status | Notes |
|-------|----------|--------|-------|
| 0 | add_cluster | ✅ | |
| 1 | explore_space | ✅ | |
| 1 | record_work | ✅ | |
| 1 | investigate | ✅ | |
| 2 | add_objectives | ✅ | |
| 2 | add_patterns | ✅ | |
| 2 | update_sync | ✅ | |
| 2 | add_behaviors | ✅ | |
| 2 | add_algorithm | ✅ | |
| 3 | add_invariant | ✅ | |
| 3 | add_health_coverage | ✅ | |
| 3 | add_implementation | ✅ | |
| 4 | raise_escalation | ✅ | For blocked work |
| 4 | resolve_blocker | ✅ | |
| 4 | capture_decision | ✅ | |
| 5 | define_space | ✅ | v1.1 with explanations |
| 5 | create_doc_chain | ✅ | |
| 5 | add_goals | ✅ | |
| 5 | add_todo | ✅ | For deferred work |
| Meta | completion_handoff | ✅ | Called by all protocols |

---

## Handoff

**For agents:**
- MCP server: `mcp/server.py` - exposes membrane_* tools and agent tools
- ConnectomeRunner: `runtime/connectome/` - session management and protocol execution
- Membrane integration: `runtime/membrane/` - membrane-graph integration layer
- Procedure runner: `runtime/procedure_runner.py` - alternative protocol runner
- Doctor→Protocol mapping in `docs/mcp-tools/MAPPING_Doctor_Issues_To_Protocols.md`
- Issue→Verification mapping in `docs/mcp-tools/MAPPING_Issue_Type_Verification.md`
- Graph schema in `runtime/connectome/schema.py`
- Graph persistence in `runtime/connectome/persistence.py`

**For human review:**
- Test imports: `python3 -c "from mind.connectome import ConnectomeRunner; print('OK')"`
- Test MCP server: `python3 mcp/server.py` (stdio mode)


---

## CHAIN

- **Prev:** IMPLEMENTATION_MCP_Tools.md
- **Doc root:** OBJECTIVES_MCP_Tools.md


---

## ARCHIVE

Older content archived to: `SYNC_MCP_Tools_archive_2025-12.md`
