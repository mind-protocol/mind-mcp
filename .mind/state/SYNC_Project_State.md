# Project — Sync: Current State

```
LAST_UPDATED: {DATE}
UPDATED_BY: {AGENT/HUMAN}
```

---

## CURRENT STATE

{Narrative of the project's current state. Not a feature list — the story of where things are.}

---

## ACTIVE WORK

### {Work Stream}

- **Area:** `{area}/`
- **Status:** {in progress / blocked}
- **Owner:** {agent/human}
- **Context:** {what's happening, why it matters}

---

## RECENT CHANGES

### {DATE}: {Summary}

- **What:** {description}
- **Why:** {motivation}
- **Impact:** {what this affects}

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| {description} | {level} | `{area}/` | {context} |

---

## HANDOFF: FOR AGENTS

**Likely VIEW for continuing:** {which VIEW}

**Current focus:** {what the project is working toward right now}

**Key context:**
{The things an agent needs to know that aren't obvious from the code/docs}

**Watch out for:**
{Project-level gotchas}

---

## HANDOFF: FOR HUMAN

**Executive summary:**
{2-3 sentences on project state}

**Decisions made recently:**
{Key choices with rationale}

**Needs your input:**
{Blocked items, strategic questions}

**Concerns:**
{Things that might be problems, flagged for awareness}

---

## TODO

### High Priority

- [ ] Make init dynamic (detect env, show what will be created, confirm)
- [ ] Test ConnectomeRunner dialogue flows end-to-end

### Backlog

- [ ] Add `mind connect` command to test database connection
- [ ] Add runtime version tracking
- IDEA: `mind migrate` for moving data between backends

---

## CONSCIOUSNESS TRACE

**Project momentum:**
{Is the project moving well? Stuck? What's the energy like?}

**Architectural concerns:**
{Things that feel like they might become problems}

**Opportunities noticed:**
{Ideas that came up during work}

---

## AREAS

| Area | Status | SYNC |
|------|--------|------|
| `{area}/` | {status} | `docs/{area}/SYNC_*.md` |

---

## MODULE COVERAGE

Check `modules.yaml` (project root) for full manifest.

**Mapped modules:**
| Module | Code | Docs | Maturity |
|--------|------|------|----------|
| {module} | `{code_path}` | `{docs_path}` | {status} |

**Unmapped code:** (run `mind validate` to check)
- {List any code directories without module mappings}

**Coverage notes:**
{Any notes about why certain code isn't mapped, or plans to add mappings}

## Init: 2025-12-29 00:26

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, env_example, mcp_config, gitignore

---

## Init: 2025-12-29 00:51

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, seed_inject, file_ingest, env_example, mcp_config, gitignore

---

## Review: 2025-12-29 docs/mcp-design/ Analysis

**Reviewer:** Claude (Opus 4.5)

### Summary

Reviewed all documentation in `docs/mcp-design/` against `.mind/FRAMEWORK.md`, `.mind/PRINCIPLES.md`, and actual implementations in `mind/doctor*.py`.

### Key Findings

1. **REDUNDANCY**: Root-level docs in `docs/mcp-design/` (PATTERNS, BEHAVIORS, ALGORITHM, etc.) describe the same framework concepts now canonically defined in `.mind/FRAMEWORK.md`. This creates confusion about authority.

2. **PATH MISMATCH**: 64 occurrences in docs/mcp-design/ reference `.mind/` (with hyphen) but actual implementation uses `.mind/` (no hyphen). All paths are broken.

3. **UNIMPLEMENTED FEATURES**:
   - `mind trace` command (Agent Trace Logging) - fully documented, zero implementation
   - `mind doctor --guide` remediation mode - documented but not implemented
   - `mind doctor --check <name>` filter - documented but not implemented
   - `mind doctor --format markdown` - documented but not implemented
   - VIEWs referenced (VIEW_Implement.md etc.) - don't exist in `.mind/views/`

4. **WELL-ALIGNED**: `docs/mcp-design/doctor/` documentation matches `mind/doctor*.py` implementation reasonably well for v1 features.

### Escalations Added

- Priority 1: Path mismatch (.mind/ vs .mind/)
- Priority 2: Redundancy with .mind/FRAMEWORK.md
- Priority 3: Agent Trace Logging not implemented
- Priority 3: doctor --guide/--check/--format markdown not implemented

### Propositions Added

- Reorganize docs/mcp-design/ as module documentation
- Move doctor/ docs under docs/cli/
- Move Agent Trace Logging to proposed-features/

### Files Modified

- `docs/mcp-design/PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md`
- `docs/mcp-design/SYNC_Protocol_Current_State.md`
- `docs/mcp-design/doctor/SYNC_Project_Health_Doctor.md`
- `docs/mcp-design/features/SYNC_Agent_Trace_Logging.md`

---

## Review: 2025-12-29 docs/infrastructure/sse/ SSE Documentation Analysis

**Reviewer:** Claude (Opus 4.5)

### Summary

Critical documentation mismatch discovered in `docs/infrastructure/sse/` (8 files). Documentation describes a non-existent TypeScript/Next.js system while actual SSE implementation exists in Python/FastAPI.

### Key Findings

1. **COMPLETE MISMATCH**: Documentation describes `app/api/sse/route.ts` (TypeScript/Next.js). This file does not exist.

2. **ACTUAL IMPLEMENTATION (Python/FastAPI)**:
   - `mind/infrastructure/api/sse_broadcast.py` - Broadcast module for SSE client management
   - `mind/infrastructure/api/moments.py` - SSE endpoint at `/api/moments/stream/{playthrough_id}`
   - `mind/infrastructure/api/app.py` - Debug SSE endpoint at `/api/debug/stream`

3. **EVENT TYPE MISMATCH**:
   - Documented: `connectome_health`, `ping` (health monitoring)
   - Implemented: `moment_activated`, `moment_completed`, `moment_decayed`, `weight_updated`, `click_traversed`, `connected`, `ping`

4. **ARCHITECTURE CONFLICT**: Architecture spec (`mind-protocol-architecture-v1.md`) specifies WebSocket + GraphQL as primary protocol, not SSE for health monitoring.

### Actions Taken

- Added `@mind:escalation` to all 8 SSE doc files
- Changed SYNC_SSE_API.md status from CANONICAL to DEPRECATED
- Added `@mind:proposition` recommending deletion and proper documentation of actual implementation

### Files Modified

- `docs/infrastructure/sse/OBJECTIVES_SSE_API.md`
- `docs/infrastructure/sse/PATTERNS_SSE_API.md`
- `docs/infrastructure/sse/BEHAVIORS_SSE_API.md`
- `docs/infrastructure/sse/ALGORITHM_SSE_API.md`
- `docs/infrastructure/sse/VALIDATION_SSE_API.md`
- `docs/infrastructure/sse/IMPLEMENTATION_SSE_API.md`
- `docs/infrastructure/sse/HEALTH_SSE_API.md`
- `docs/infrastructure/sse/SYNC_SSE_API.md`

### Decision Needed

**Recommendation:** Delete entire `docs/infrastructure/sse/` doc chain and document the actual Python SSE implementation at `docs/infrastructure/api/`.

---

## Review: 2025-12-29 docs/cli/core/ CLI Documentation Analysis

**Reviewer:** Claude (Opus 4.5)

### Summary

Critical documentation mismatch discovered in `docs/cli/core/` (18 files). Documentation describes 12+ CLI commands that do not exist, references non-existent implementation files, and uses incorrect directory paths.

### Key Findings

1. **DOCUMENTED COMMANDS THAT DO NOT EXIST** (from BEHAVIORS_CLI_Command_Effects.md):
   - `mind init --force` - NO --force flag exists
   - `mind validate` - DOES NOT EXIST
   - `mind doctor` - DOES NOT EXIST
   - `mind work` (repair) - DOES NOT EXIST
   - `mind context <file>` - DOES NOT EXIST
   - `mind sync` - DOES NOT EXIST
   - `mind prompt` - DOES NOT EXIST
   - `mind overview` - DOES NOT EXIST
   - `mind solve-markers` - DOES NOT EXIST
   - `mind agents` - DOES NOT EXIST
   - `mind refactor` - DOES NOT EXIST
   - `mind docs-fix` - DOES NOT EXIST

2. **ACTUAL CLI COMMANDS** (from cli/__main__.py):
   - `mind init [--database falkordb|neo4j]` - Initialize .mind/
   - `mind status` - Show status (UNDOCUMENTED)
   - `mind upgrade` - Check for updates (UNDOCUMENTED)
   - `mind fix-embeddings [--dry-run]` - Fix embeddings (UNDOCUMENTED)

3. **PATH MISMATCHES**:
   - Docs reference `.mind/` but actual is `.mind/`
   - Docs reference `mind/cli.py`, `mind/doctor.py` etc. but actual is `cli/__main__.py`, `cli/commands/*.py`
   - All IMPL: references point to non-existent files

4. **DUPLICATE DOCUMENTATION CHAINS**:
   - Chain 1: PATTERNS_Why_CLI_Over_Copy.md, BEHAVIORS_CLI_Command_Effects.md, etc. (detailed but incorrect)
   - Chain 2: *_mind_cli_core.md files (generic, also incorrect)

### Escalations Added

- Priority CRITICAL: Documented commands do not exist
- Priority CRITICAL: Path references incorrect (.mind/ vs .mind/)
- Priority CRITICAL: Implementation paths reference non-existent files
- Priority HIGH: Algorithm documentation describes non-existent commands
- Priority HIGH: Subsystem files referenced do not exist

### Propositions Added

- Document existing undocumented commands (status, upgrade, fix-embeddings)
- Consolidate duplicate documentation chains

### Files Modified

- `docs/cli/core/BEHAVIORS_CLI_Command_Effects.md`
- `docs/cli/core/SYNC_CLI_Development_State.md`
- `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md`
- `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md`
- `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`
- `docs/cli/core/SYNC_mind_cli_core.md`
- `docs/cli/core/IMPLEMENTATION_mind_cli_core.md`

### Decision Needed

**Options:**
1. **Implement documented commands** - Add validate, doctor, work, context, etc. to the CLI
2. **Rewrite documentation** - Delete incorrect docs and document actual 4-command CLI
3. **Clarify scope** - This may be documentation from a planned future version; if so, mark as PROPOSED and create accurate CANONICAL docs

**Recommendation:** Option 2 - Rewrite documentation to match reality. The actual CLI (init, status, upgrade, fix-embeddings) is functional and should be properly documented. The documented commands appear to be aspirational/planned features.

---

## Review: 2025-12-29 docs/mcp-tools/ MCP Tools Documentation Analysis

**Reviewer:** Claude (Opus 4.5)

### Summary

Complete review and correction of all 13 documentation files in `docs/mcp-tools/`. Updated naming from "Membrane System" to "MCP Tools" and corrected all path references.

### Key Findings

1. **NAMING INCONSISTENCY**: All files used "Membrane System" in titles/headers while filenames use "MCP_Tools". Updated all to use "MCP Tools" consistently.

2. **PATH MISMATCHES** (now corrected):
   - `tools/mcp/membrane_server.py` -> `mcp/server.py`
   - `engine/connectome/` -> `mind/connectome/`
   - CHAIN links used `*_Membrane_System.md` -> corrected to `*_MCP_Tools.md`

3. **MISSING INFRASTRUCTURE**:
   - `procedures/` directory does not exist (documented as having 20 protocols)
   - `templates/mind/skills/` skills may not exist (documented as 15 skills)
   - `tools/coverage/validate.py` may not exist
   - `mind/repair_verification.py` needs verification

4. **UNDOCUMENTED TOOLS** (in code but not in behaviors):
   - `doctor_check` - Run health checks with agent assignment
   - `agent_list` - List work agents and status
   - `agent_spawn` - Spawn work agent for issue/task
   - `agent_status` - Get/set agent status
   - `task_list` - List available tasks
   - `graph_query` - Natural language graph query

### Markers Added

**@mind:escalation markers (documented but missing):**
- `procedures/` directory with 20 protocol YAML files
- Skills in `templates/mind/skills/`
- `tools/coverage/validate.py`
- Test files in `tests/connectome_v0/`

**@mind:proposition markers (exists but not documented):**
- Agent orchestration tools (doctor_check, agent_list, agent_spawn, etc.)
- Create `procedures/` directory with protocol definitions

### Files Modified

All 13 files in `docs/mcp-tools/`:
- OBJECTIVES_MCP_Tools.md
- PATTERNS_MCP_Tools.md
- BEHAVIORS_MCP_Tools.md
- ALGORITHM_MCP_Tools.md
- VALIDATION_MCP_Tools.md
- IMPLEMENTATION_MCP_Tools.md
- HEALTH_MCP_Tools.md
- SYNC_MCP_Tools.md
- SYNC_MCP_Tools_archive_2025-12.md
- MAPPING_Issue_Type_Verification.md
- MAPPING_Doctor_Issues_To_Protocols.md
- SKILLS_AND_PROTOCOLS_Mapping.md
- VALIDATION_Completion_Verification.md

### Decision Needed

**Recommendation:** Create the `procedures/` directory with protocol YAML files to match the documented protocol inventory. This is the most significant gap between documentation and implementation.

---

## Init: 2025-12-29 01:00

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:01

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:02

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:10

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:10

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:14

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Init: 2025-12-29 01:33

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview

---

## Refactor: 2025-12-29 - MCP Tool Rename: membrane_* to procedure_*

**Performed by:** Claude (Opus 4.5)

### Summary

Renamed all MCP membrane dialogue tools to procedure tools for clarity:
- `membrane_start` -> `procedure_start`
- `membrane_continue` -> `procedure_continue`
- `membrane_abort` -> `procedure_abort`
- `membrane_list` -> `procedure_list`

### Rationale

The tool names now better reflect what they do: start/continue/abort/list structured procedures. The term "membrane" remains appropriate for the integration layer concept (`mind/membrane/`) but was confusing when used for dialogue tool names.

### Files Modified

**MCP Server (core implementation):**
- `mcp/server.py` - Tool definitions, handlers, docstrings

**Documentation (all references updated):**
- `docs/mcp-tools/IMPLEMENTATION_MCP_Tools.md`
- `docs/mcp-tools/MAPPING_Issue_Type_Verification.md`
- `docs/mcp-tools/VALIDATION_Completion_Verification.md`
- `docs/mcp-tools/HEALTH_MCP_Tools.md`
- `docs/mcp-tools/ALGORITHM_MCP_Tools.md`
- `README.md`
- `AGENTS.md`
- `.mind/FRAMEWORK.md`
- `templates/mind/FRAMEWORK.md`
- `docs/ARCHITECTURE.md`

**Python implementation files:**
- `mind/init_cmd.py`
- `mind/work_verification.py`

### What Was NOT Changed

- The `mind/membrane/` directory (different concept - integration layer)
- References to "membrane" as a concept (e.g., "Membrane graph navigation")
- Only the MCP tool names were renamed

### Verification

Grep search for old names returns no matches. All 100 occurrences across 13 files now use the new procedure_* naming convention.

---

## Init Command v0.2.0: 2025-12-29

**Performed by:** Claude (Opus 4.5)

### Summary

Major update to `mind init` command. Now has 13 steps with proper ordering and embeddings with progress bar.

### Changes

1. **Seed injection now runs AFTER file ingestion** - Spaces exist before linking actors to them
2. **Added git info injection** - Creates human actor from git config (user.name, user.email)
3. **Added repo Thing from git remote** - URL + GitHub API metadata for public repos
4. **Added overview generation** - Generates map.md files at end of init
5. **Added embeddings step with progress bar** - All nodes embedded at end

### Init Steps (13 total)

1. Ecosystem templates
2. Runtime package
3. AI config files
4. Skills sync
5. Database config
6. Database setup
7. File ingestion (creates Spaces, Things)
8. Seed injection (creates Actors, links to Spaces)
9. Env example
10. MCP config
11. Gitignore
12. Overview (map.md)
13. Embeddings (with progress bar)

### Files Modified

- `cli/commands/init.py` - 13 steps, reordered
- `cli/helpers/inject_seed_yaml_to_graph.py` - Git info + GitHub API
- `cli/helpers/generate_embeddings_for_graph_nodes.py` - NEW, progress bar
- `cli/helpers/ingest_repo_files_to_graph.py` - Removed embed parameter
- `mind/ingest/files.py` - Removed embed option (always create nodes only)
- `docs/building/seed-injection.yaml` - Minimal MCP client seed (5 agents)

### Seed YAML Changes

Removed generic "developer" actor from YAML (now created dynamically from git config). Agents: assistant, scout, fixer, builder, reviewer - all linked to space:root.

---

## Documentation Overhaul: 2025-12-29

**Performed by:** Claude (Opus 4.5)

### Summary

Complete review and consolidation of imported documentation from ngram repo. Fixed massive doc-code drift across 4 areas.

### Actions Completed

1. **Copied procedures/** - 24 YAML protocol files from ngram
2. **Fixed paths** - `.mind/` → `.mind/` in protocol docs
3. **Deleted SSE docs** - TypeScript docs for non-existent implementation, created placeholder
4. **Deleted CLI Chain 1** - Kept Chain 2 (*_mind_cli_core.md), deleted duplicate chain
5. **Updated CLI docs** - Rewrote all 8 files for actual + future commands
6. **Renamed MCP tools** - `membrane_*` → `procedure_*` (13 files)

### Future `mind` Commands Decided

| Command | Status | Purpose |
|---------|--------|---------|
| `init`, `status`, `upgrade`, `fix-embeddings` | CANONICAL | Existing |
| `validate` | PROPOSED | Protocol enforcement |
| `work` | PROPOSED | AI-assisted repair (redesign needed) |
| `context` | PROPOSED | Node context for actors (redesign: graph-aware, optional question/intent) |
| `sync-files` | PROPOSED | SYNC file management |
| `human-review` | PROPOSED | Marker resolution for humans |
| `talk` | PROPOSED | Talk with an agent |

### Removed Commands

- `doctor` - content dispatched elsewhere
- `prompt` - merged into `context`
- `overview` - internal (called by other commands)
- `refactor`, `protocol`, `trace` - not needed

### Pending

- Verify `templates/mind/skills/` exists

---

## Init: 2025-12-29 01:47

| Setting | Value |
|---------|-------|
| Version | v0.1.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Documentation: 2025-12-29 - MCP Tools Behaviors Documented

**Performed by:** Claude (Opus 4.5)

### Summary

Documented 6 MCP tools in `docs/mcp-tools/BEHAVIORS_MCP_Tools.md` that were previously only in code. Removed the `@mind:proposition` marker since documentation is now complete.

### Tools Documented

| Tool | Purpose | Behaviors Added |
|------|---------|-----------------|
| `doctor_check` | Run health checks with agent assignment | B-DOC-CHK-1 through B-DOC-CHK-5 |
| `agent_list` | List work agents and their status | B-AGT-LST-1 through B-AGT-LST-3 |
| `agent_spawn` | Spawn work agent for issue/task | B-AGT-SPN-1 through B-AGT-SPN-7 |
| `agent_status` | Get or set agent status | B-AGT-STS-1 through B-AGT-STS-3 |
| `task_list` | List available tasks from graph | B-TSK-LST-1 through B-TSK-LST-6 |
| `graph_query` | Natural language graph query | B-GRQ-1 through B-GRQ-9 |

### Documentation Format

Each tool documented with:
- Behavior table (ID, Behavior, Observable Effect, Linked Goal)
- GIVEN/WHEN/THEN specifications covering:
  - Input parameters and their effects
  - Normal operation behaviors
  - Edge cases and error handling

### Files Modified

- `docs/mcp-tools/BEHAVIORS_MCP_Tools.md` - Added 6 new behavior sections (~420 lines)

### Source Reference

Implementation analyzed from `mcp/server.py`:
- `_tool_doctor_check()` (lines 410-456)
- `_tool_agent_list()` (lines 458-479)
- `_tool_task_list()` (lines 481-540)
- `_tool_agent_spawn()` (lines 542-729)
- `_tool_agent_status()` (lines 731-759)
- `_tool_graph_query()` (lines 761-818)

---
