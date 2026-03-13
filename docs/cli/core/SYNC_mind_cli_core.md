# mind_cli_core — SYNC: Project State and Recent Changes

```
STATUS: CANONICAL
UPDATED: 2026-03-13
```

---

## CHAIN

OBJECTIVES:      ./OBJECTIVES_mind_cli_core.md
BEHAVIORS:       ./BEHAVIORS_mind_cli_core.md
PATTERNS:        ./PATTERNS_mind_cli_core.md
ALGORITHM:       ./ALGORITHM_mind_cli_core.md
VALIDATION:      ./VALIDATION_mind_cli_core.md
IMPLEMENTATION:  ./IMPLEMENTATION_mind_cli_core.md
HEALTH:          ./HEALTH_mind_cli_core.md
THIS:            SYNC_mind_cli_core.md

---

## CURRENT STATUS

### Maturity

**STATUS: CANONICAL (6 commands) + PROPOSED (6 commands)**

**What's canonical (implemented in `cli/__main__.py`):**
- `mind init [--database falkordb|neo4j]` — Initialize .mind/ directory (15 steps)
- `mind status` — Show mind protocol status
- `mind upgrade` — Check for protocol upgrades
- `mind fix-embeddings [--dry-run]` — Fix missing/mismatched embeddings
- `mind export [--target notebooklm]` — Export project for external tools
- `mind swarm [--agents N] [--status] [--stop] [--stream] [--logs] [--background]` — Run multiple agents in parallel

**What's proposed (future):**
- `mind validate` — Protocol enforcement, CI integration
- `mind work` — AI-assisted repair (needs redesign)
- `mind context [node_id] [--question "..."] [--intent "..."]` — Node context
- `mind sync-files` — SYNC file management
- `mind human-review` — Marker resolution
- `mind talk` — Agent conversation

**Legacy CLI (`runtime/cli.py`):**
- Separate entry point with its own init via `runtime/init_cmd.py:init_protocol()`
- Contains additional commands: validate, prompt, context, solve-markers, map, overview, doctor, sync, work
- NOT the canonical `mind` command (that's `cli/__main__.py:main`)
- Some logic (system prompt building, permission enforcement) not yet ported to modular CLI

**What's removed (no longer documented):**
- `mind doctor` — Content dispatched to other commands
- `mind prompt` — Merged into context
- `mind overview` — Internal, called by other commands
- `mind refactor`, `mind protocol`, `mind trace` — Not needed

---

## RECENT CHANGES

### 2026-03-13: Documentation Alignment v0.2.1

**What Changed:**
Updated all 4 doc chain files (BEHAVIORS, ALGORITHM, IMPLEMENTATION, SYNC) to match actual code.

**Key corrections:**
- Init pipeline documented as 15 steps (was 13)
- Added missing steps: capabilities copy (step 2), capabilities graph injection (step 9), health checks (step 15)
- Removed stale reference to seed injection (no longer called from init since commit 493c37b)
- Updated helper file listing (26 helpers, grouped by: init pipeline, standalone, shared)
- Init data flow diagram restructured into 5 phases
- Noted standalone helpers (inject_seed, inject_agents) that exist but aren't called by init

### 2026-03-12: Actors Generation Removed (commit 493c37b)

**What Changed:**
Removed actors/ generation step from mind init.

**Impact:**
- `inject_agents_to_graph.py` no longer called from init (still exists as standalone)
- `inject_seed_yaml_to_graph.py` no longer called from init (still exists as standalone)
- Init pipeline simplified to 15 steps

### 2026-03-12: Brain Seeder and MCP Tools (commit 9b929ca)

**What Changed:**
Added brain seeder script, gemini_chat + telegram_notify MCP tools, schema v1.9.1.

**Files Added:**
- `runtime/seed_brain_from_source_docs_dynamic_generator.py` — Generates baseline cognitive nodes for AI citizens (3285 lines, standalone)
- `mcp/tools/gemini_chat.py` — Google Gemini integration
- `mcp/tools/telegram_notify.py` — Telegram notifications
- `.mind/manifesto/MIND_MANIFESTO.md` — $MIND vision declaration

**Note:** Brain seeder is NOT integrated into init. It's a standalone script for generating universal seed brain JSON.

### 2025-12-29: Init Command v0.2.0

**What Changed:**
Major update to `mind init`. Reordered and expanded pipeline.

**Key changes:**
- Seed injection runs AFTER file ingestion (spaces exist before actor linking)
- Git info injection: creates human actor from git config (user.name, user.email)
- Repo Thing: created from git remote URL + GitHub API metadata (if public)
- Overview generation: creates map.md files at end
- Embeddings step: all nodes embedded at end with progress bar

**Files Added:**
- `cli/helpers/generate_embeddings_for_graph_nodes.py` - Embeddings with progress bar

**Files Modified:**
- `cli/commands/init.py` - Reordered pipeline
- `cli/helpers/inject_seed_yaml_to_graph.py` - Git info + GitHub API
- `cli/helpers/ingest_repo_files_to_graph.py` - Removed embed parameter

---

### 2025-12-29: Documentation Chain Overhaul

**What Changed:**
All 8 documentation files in this chain were updated to accurately reflect the actual CLI implementation.

**Files Modified:**
- `OBJECTIVES_mind_cli_core.md` - Updated objectives for actual + future commands
- `PATTERNS_mind_cli_core.md` - Fixed: uses argparse not Click, actual cli/ structure
- `BEHAVIORS_mind_cli_core.md` - Added behaviors for all 10 commands (4 actual + 6 future)
- `ALGORITHM_mind_cli_core.md` - Updated dispatch for actual commands
- `VALIDATION_mind_cli_core.md` - Updated invariants for actual implementation
- `IMPLEMENTATION_mind_cli_core.md` - Fixed paths: cli/__main__.py, cli/commands/, cli/helpers/
- `HEALTH_mind_cli_core.md` - Updated health checks for actual commands
- `SYNC_mind_cli_core.md` - Updated current state, marked future commands as PROPOSED

**Why:**
Previous documentation referenced non-existent code structure (`runtime/` directory, Click framework, commands that don't exist). This update aligns documentation with actual implementation.

**Reasoning:**
The documentation chain must accurately reflect reality. Future commands are clearly marked as PROPOSED so agents and humans know what exists vs what's planned.

---

## CODE STRUCTURE

```
cli/
├── __init__.py              # Package marker
├── __main__.py              # Main entry point (argparse setup, dispatch)
├── config.py                # Configuration constants
├── commands/
│   ├── __init__.py
│   ├── init.py              # mind init command (15 steps)
│   ├── status.py            # mind status command
│   ├── upgrade.py           # mind upgrade command
│   └── fix_embeddings.py    # mind fix-embeddings command
└── helpers/                 # 26 helper functions
    ├── __init__.py
    ├── copy_ecosystem_templates_to_target.py     # Init step 1
    ├── copy_capabilities_to_target.py            # Init step 2
    ├── copy_runtime_package_to_target.py         # Init step 3
    ├── save_version_hash.py                      # Init step 3b
    ├── create_ai_config_files_for_claude_agents_gemini.py  # Init step 4
    ├── sync_skills_to_ai_tool_directories.py     # Init step 5
    ├── create_database_config_yaml.py            # Init step 6
    ├── setup_database_and_apply_schema.py        # Init step 7
    ├── ingest_repo_files_to_graph.py             # Init step 8
    ├── ingest_capabilities_to_graph.py           # Init step 9
    ├── create_env_example_file.py                # Init step 10
    ├── create_mcp_config_json.py                 # Init step 11
    ├── update_gitignore_with_runtime_entry.py    # Init step 12
    ├── generate_repo_overview_maps.py            # Init step 13
    ├── generate_embeddings_for_graph_nodes.py    # Init step 14
    ├── inject_seed_yaml_to_graph.py              # Standalone (not in init)
    ├── inject_agents_to_graph.py                 # Standalone (not in init)
    ├── export_project_to_notebooklm.py           # NotebookLM export
    ├── get_paths_for_templates_and_runtime.py
    ├── get_mcp_version_from_config.py
    ├── check_github_for_latest_version.py
    ├── show_upgrade_notice_if_available.py
    ├── validate_embedding_config_matches_stored.py
    ├── check_mind_status_in_directory.py
    └── fix_embeddings_for_nodes_and_links.py
```

---

## HANDOFFS

### For Agents Implementing Future Commands

When implementing a proposed command:

1. Create `cli/commands/{command}.py` following the pattern:
   ```python
   def run(directory: Path, **kwargs) -> bool:
       """Execute the command."""
       ...
   ```

2. Add subparser in `cli/__main__.py`

3. Add dispatch case in `cli/__main__.py`

4. Update BEHAVIORS_mind_cli_core.md to change status from PROPOSED to CANONICAL

5. Update SYNC_mind_cli_core.md to move command from proposed to canonical

### Priority Order for Future Commands

1. **mind validate** - Most valuable for CI integration
2. **mind context** - Needed for AI-assisted workflows
3. **mind human-review** - Needed for marker resolution
4. **mind sync-files** - Needed for state management
5. **mind work** - Needs redesign first
6. **mind talk** - Depends on agent infrastructure

---

## KNOWN ISSUES

None currently. Documentation now matches implementation.

---

## DEPENDENCIES

### External Packages Required

| Package | Purpose |
|---------|---------|
| `argparse` | CLI argument parsing (stdlib) |
| `pathlib` | Path handling (stdlib) |
| `pyyaml` | YAML config parsing |
| `falkordb` | Graph database client |
| `neo4j` | Graph database client (alternative) |

### Internal Dependencies

The CLI depends on:
- `mcp/` - For graph operations and embedding generation
- `runtime/` - For protocol logic (when implemented)

---

## METRICS

| Metric | Value | Notes |
|--------|-------|-------|
| Implemented Commands | 6 | init, status, upgrade, fix-embeddings, export, swarm |
| Proposed Commands | 6 | validate, work, context, sync-files, human-review, talk |
| Helper Functions | 26 | In cli/helpers/ (15 init + 3 standalone + 8 shared) |
| Init Steps | 15 | Full pipeline: copy → config → graph → env → finalize |
| Test Coverage | TBD | Tests not yet verified |
