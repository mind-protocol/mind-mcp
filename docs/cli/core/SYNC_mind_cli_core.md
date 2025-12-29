# mind_cli_core — SYNC: Project State and Recent Changes

```
STATUS: CANONICAL
UPDATED: 2025-12-29
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

**STATUS: CANONICAL (4 commands) + PROPOSED (6 commands)**

**What's canonical (implemented):**
- `mind init [--database falkordb|neo4j]` - Initialize .mind/ directory
- `mind status` - Show mind protocol status
- `mind upgrade` - Check for protocol upgrades
- `mind fix-embeddings [--dry-run]` - Fix missing/mismatched embeddings

**What's proposed (future):**
- `mind validate` - Protocol enforcement, CI integration
- `mind work` - AI-assisted repair (needs redesign)
- `mind context [node_id] [--question "..."] [--intent "..."]` - Node context
- `mind sync-files` - SYNC file management
- `mind human-review` - Marker resolution
- `mind talk` - Agent conversation

**What's removed (no longer documented):**
- `mind doctor` - Content dispatched to other commands
- `mind prompt` - Merged into context
- `mind overview` - Internal, called by other commands
- `mind refactor`, `mind protocol`, `mind trace` - Not needed

---

## RECENT CHANGES

### 2025-12-29: Init Command v0.2.0

**What Changed:**
Major update to `mind init`. Now has 13 steps with proper ordering and embeddings.

**Key changes:**
- Seed injection runs AFTER file ingestion (spaces exist before actor linking)
- Git info injection: creates human actor from git config (user.name, user.email)
- Repo Thing: created from git remote URL + GitHub API metadata (if public)
- Overview generation: creates map.md files at end
- Embeddings step: all nodes embedded at end with progress bar

**Files Added:**
- `cli/helpers/generate_embeddings_for_graph_nodes.py` - Embeddings with progress bar

**Files Modified:**
- `cli/commands/init.py` - 13 steps, reordered
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
│   ├── init.py              # mind init command (13 steps)
│   ├── status.py            # mind status command
│   ├── upgrade.py           # mind upgrade command
│   └── fix_embeddings.py    # mind fix-embeddings command
└── helpers/
    ├── __init__.py
    ├── copy_ecosystem_templates_to_target.py
    ├── copy_runtime_package_to_target.py
    ├── create_ai_config_files_for_claude_agents_gemini.py
    ├── create_database_config_yaml.py
    ├── create_env_example_file.py
    ├── create_mcp_config_json.py
    ├── generate_embeddings_for_graph_nodes.py  # NEW: progress bar
    ├── generate_repo_overview_maps.py
    ├── ingest_repo_files_to_graph.py
    ├── inject_seed_yaml_to_graph.py            # git info + GitHub API
    ├── setup_database_and_apply_schema.py
    ├── sync_skills_to_ai_tool_directories.py
    ├── update_gitignore_with_runtime_entry.py
    └── *.py                 # 21 helper functions total
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
| Implemented Commands | 4 | init, status, upgrade, fix-embeddings |
| Proposed Commands | 6 | validate, work, context, sync-files, human-review, talk |
| Helper Functions | 21 | In cli/helpers/ |
| Init Steps | 13 | Full pipeline with embeddings |
| Test Coverage | TBD | Tests not yet verified |
