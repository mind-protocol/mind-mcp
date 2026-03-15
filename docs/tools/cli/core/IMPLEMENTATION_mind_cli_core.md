# mind_cli_core — Implementation: Code Architecture and Structure

```
STATUS: CANONICAL
CREATED: 2025-12-24
UPDATED: 2026-03-13
```

---

## CHAIN

OBJECTIVES:      ./OBJECTIVES_mind_cli_core.md
BEHAVIORS:       ./BEHAVIORS_mind_cli_core.md
PATTERNS:        ./PATTERNS_mind_cli_core.md
ALGORITHM:       ./ALGORITHM_mind_cli_core.md
VALIDATION:      ./VALIDATION_mind_cli_core.md
THIS:            IMPLEMENTATION_mind_cli_core.md
HEALTH:          ./HEALTH_mind_cli_core.md
SYNC:            ./SYNC_mind_cli_core.md

IMPL:            cli/__main__.py

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
└── helpers/
    ├── __init__.py
    ├── check_github_for_latest_version.py
    ├── check_mind_status_in_directory.py
    ├── copy_capabilities_to_target.py           # Init step 2
    ├── copy_ecosystem_templates_to_target.py     # Init step 1
    ├── copy_runtime_package_to_target.py         # Init step 3
    ├── create_ai_config_files_for_claude_agents_gemini.py  # Init step 4
    ├── create_database_config_yaml.py            # Init step 6
    ├── create_env_example_file.py                # Init step 10
    ├── create_mcp_config_json.py                 # Init step 11
    ├── export_project_to_notebooklm.py           # NotebookLM export utility
    ├── fix_embeddings_for_nodes_and_links.py
    ├── generate_embeddings_for_graph_nodes.py    # Init step 14
    ├── generate_repo_overview_maps.py            # Init step 13
    ├── get_mcp_version_from_config.py
    ├── get_paths_for_templates_and_runtime.py
    ├── ingest_capabilities_to_graph.py           # Init step 9
    ├── ingest_repo_files_to_graph.py             # Init step 8
    ├── inject_agents_to_graph.py                 # Agent injection (standalone)
    ├── inject_seed_yaml_to_graph.py              # Seed injection (standalone)
    ├── save_version_hash.py                      # Init step 3 (version tracking)
    ├── setup_database_and_apply_schema.py        # Init step 7
    ├── show_upgrade_notice_if_available.py
    ├── sync_skills_to_ai_tool_directories.py     # Init step 5
    ├── update_gitignore_with_runtime_entry.py    # Init step 12
    └── validate_embedding_config_matches_stored.py
```

### File Responsibilities

| File | Purpose | Key Functions | Status |
|------|---------|---------------|--------|
| `cli/__main__.py` | Main entry, command dispatch | `main()` | CANONICAL |
| `cli/config.py` | Configuration constants | Various constants | CANONICAL |
| `cli/commands/init.py` | Initialize .mind/ | `run(dir, database)` | CANONICAL |
| `cli/commands/status.py` | Show project status | `run(dir)` | CANONICAL |
| `cli/commands/upgrade.py` | Check for updates | `run(dir)` | CANONICAL |
| `cli/commands/fix_embeddings.py` | Fix embeddings | `run(dir, dry_run)` | CANONICAL |

### Helper Responsibilities

**Init pipeline helpers (in execution order):**

| # | Helper | Purpose |
|---|--------|---------|
| 1 | `copy_ecosystem_templates_to_target.py` | Copy protocol docs, agents, procedures to .mind/ |
| 2 | `copy_capabilities_to_target.py` | Copy capability definitions to .mind/capabilities/ |
| 3 | `copy_runtime_package_to_target.py` | Copy Python runtime (186 files) to .mind/mind/ |
| 3b | `save_version_hash.py` | Save git commit hash to .mind/version.txt |
| 4 | `create_ai_config_files_for_claude_agents_gemini.py` | Generate CLAUDE.md, GEMINI.md, AGENTS.md |
| 5 | `sync_skills_to_ai_tool_directories.py` | Copy skills to .claude/skills/ and $CODEX_HOME/ |
| 6 | `create_database_config_yaml.py` | Create database_config.yaml with backend choice |
| 7 | `setup_database_and_apply_schema.py` | Connect to DB, apply schema.yaml |
| 8 | `ingest_repo_files_to_graph.py` | Scan repo tree, create Space/Thing nodes |
| 9 | `ingest_capabilities_to_graph.py` | Inject capability Spaces, Tasks, Skills, Procedures |
| 10 | `create_env_example_file.py` | Create .env.mind.example |
| 11 | `create_mcp_config_json.py` | Create .mind/mcp/cconfig.json |
| 12 | `update_gitignore_with_runtime_entry.py` | Add .mind/ runtime to .gitignore |
| 13 | `generate_repo_overview_maps.py` | Generate map.md files at root and in folders |
| 14 | `generate_embeddings_for_graph_nodes.py` | Embed all nodes with progress bar |

**Standalone helpers (not called by init):**

| Helper | Purpose |
|--------|---------|
| `inject_seed_yaml_to_graph.py` | Inject seed YAML data to graph (standalone) |
| `inject_agents_to_graph.py` | Inject agent nodes to graph (standalone) |
| `export_project_to_notebooklm.py` | Export project data for NotebookLM |

**Shared helpers (used by multiple commands):**

| Helper | Purpose |
|--------|---------|
| `get_paths_for_templates_and_runtime.py` | Resolve template and runtime paths |
| `get_mcp_version_from_config.py` | Get current MCP version from config |
| `check_github_for_latest_version.py` | Query GitHub API for latest release |
| `show_upgrade_notice_if_available.py` | Display upgrade notice after commands |
| `validate_embedding_config_matches_stored.py` | Validate embedding config vs stored |
| `check_mind_status_in_directory.py` | Check if directory has .mind/ |
| `fix_embeddings_for_nodes_and_links.py` | Core embedding fix logic |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Modular CLI with Subcommand Dispatch

**Why this pattern:** Decouples specific command logic from the main entry point, allowing independent evolution of each command. Each command is a self-contained module under `cli/commands/`.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Subcommand | `__main__.py` | Argparse subparsers for command routing |
| Module-per-Command | `cli/commands/` | Each command in its own module |
| Helper Functions | `cli/helpers/` | Reusable utilities with descriptive names |
| Standard Interface | Command modules | All expose `run(dir, **kwargs) -> bool/int` |

---

## ENTRY POINTS

| Entry Point | File:Function | Triggered By |
|-------------|---------------|--------------|
| `main` | `cli/__main__.py:main()` | `python -m cli` or `mind` command |

---

## DATA FLOW

### Init Command Flow

```
mind init --database falkordb
    |
    v
__main__.py:main() -> parse args
    |
    v
init.run(dir, database="falkordb")
    |
    +-- PHASE 1: Copy protocol artifacts --------+
    |   1. copy_ecosystem_templates_to_target()   |
    |   2. copy_capabilities_to_target()          |
    |   3. copy_runtime_package_to_target()       |
    |      save_version_hash()                    |
    +---------------------------------------------+
    |
    +-- PHASE 2: Configure AI tools --------------+
    |   4. create_ai_config_files()               |
    |   5. sync_skills_to_ai_tool_directories()   |
    +---------------------------------------------+
    |
    +-- PHASE 3: Database + graph ----------------+
    |   6. create_database_config_yaml()          |
    |   7. setup_database_and_apply_schema()      |
    |   8. ingest_repo_files_to_graph()           |
    |   9. ingest_capabilities_to_graph()         |
    +---------------------------------------------+
    |
    +-- PHASE 4: Environment + config ------------+
    |   10. create_env_example_file()             |
    |   11. create_mcp_config_json()              |
    |   12. update_gitignore_with_runtime_entry()  |
    +---------------------------------------------+
    |
    +-- PHASE 5: Finalize ------------------------+
    |   13. generate_repo_overview_maps()         |
    |   14. generate_embeddings_for_graph_nodes() |
    |   15. CapabilityManager.fire_trigger()      |
    |       _update_sync_file()                   |
    +---------------------------------------------+
    |
    v
sys.exit(0 if success else 1)
```

### Status Command Flow

```
mind status
    |
    v
__main__.py:main() -> parse args
    |
    v
status.run(dir)
    |
    +-> check_mind_status_in_directory()
    +-> load database config
    +-> connect to database
    +-> query health metrics
    +-> validate_embedding_config_matches_stored()
    |
    v
sys.exit(exit_code)
```

### Fix-Embeddings Command Flow

```
mind fix-embeddings [--dry-run]
    |
    v
__main__.py:main() -> parse args
    |
    v
fix_embeddings.run(dir, dry_run)
    |
    +-> validate_embedding_config_matches_stored()
    +-> fix_embeddings_for_nodes_and_links(dry_run)
    |
    v
sys.exit(0 if success else 1)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
cli/__main__.py
    |-- imports -> cli.commands.init
    |-- imports -> cli.commands.status
    |-- imports -> cli.commands.upgrade
    |-- imports -> cli.commands.fix_embeddings
    |-- imports -> cli.helpers.show_upgrade_notice_if_available

cli.commands.init
    |-- imports -> cli.helpers.* (multiple)

cli.commands.status
    |-- imports -> cli.helpers.check_mind_status_in_directory
    |-- imports -> cli.helpers.validate_embedding_config_matches_stored

cli.commands.fix_embeddings
    |-- imports -> cli.helpers.fix_embeddings_for_nodes_and_links
    |-- imports -> cli.helpers.validate_embedding_config_matches_stored
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `argparse` | Argument parsing | `cli/__main__.py` |
| `pathlib` | Path handling | All modules |
| `yaml` | Config file parsing | Various helpers |
| `falkordb` | Graph database | Database helpers |
| `neo4j` | Graph database (alt) | Database helpers |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Reference |
|------|-----------|
| `cli/__main__.py` | `# DOCS: docs/cli/core/OBJECTIVES_mind_cli_core.md` |
| `cli/commands/init.py` | `# DOCS: docs/cli/core/BEHAVIORS_mind_cli_core.md` |
| `cli/commands/status.py` | `# DOCS: docs/cli/core/BEHAVIORS_mind_cli_core.md` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM main() | `cli/__main__.py:main` |
| BEHAVIOR B1 (init) | `cli/commands/init.py` |
| BEHAVIOR B2 (status) | `cli/commands/status.py` |
| BEHAVIOR B3 (upgrade) | `cli/commands/upgrade.py` |
| BEHAVIOR B4 (fix-embeddings) | `cli/commands/fix_embeddings.py` |

---

## FUTURE COMMAND MODULES (PROPOSED)

When implementing future commands, add these modules:

```
cli/commands/
├── validate.py          # mind validate [PROPOSED]
├── work.py              # mind work [PROPOSED]
├── context.py           # mind context [PROPOSED]
├── sync_files.py        # mind sync-files [PROPOSED]
├── human_review.py      # mind human-review [PROPOSED]
└── talk.py              # mind talk [PROPOSED]
```

Each should follow the standard interface:

```python
def run(directory: Path, **kwargs) -> bool:
    """Execute the command."""
    ...
```

---

## LEGACY AND STANDALONE COMPONENTS

### runtime/init_cmd.py (Legacy Init)

A monolithic 663-line init implementation that predates the modular `cli/commands/init.py`. Contains:
- `init_protocol()` — Orchestration function with different step ordering
- `_build_claude_addition()`, `_build_system_prompt()` — System prompt generation
- `_configure_mcp_membrane()` — MCP config via `claude mcp add` CLI or .mcp.json fallback
- `_enforce_readonly_for_views()` — Read-only permission enforcement
- `_init_graph()` — Direct FalkorDB graph initialization

**Status:** Legacy. Not called from `cli/__main__.py`. May still be invoked directly via `python -m runtime.init_cmd` or imported by other systems. Contains logic (system prompt building, permission enforcement) not yet ported to modular helpers.

### runtime/seed_brain_from_source_docs_dynamic_generator.py (Brain Seeder)

Standalone script (3,285 lines) that generates baseline cognitive nodes for AI citizens.

**Purpose:** Creates a universal "seed brain" JSON structure from source documentation (SYSTEM.md, PRINCIPLES.md, MIND_MANIFESTO.md).

**What it generates (~20 clusters):**
- Venice values (9 architectural values + character values + 7 interdictions)
- Architecture concepts (12 concepts: consciousness, graph physics, L1 engine, etc.)
- Social processes (13 processes: mentoring, help, harmony, refactor, etc.)
- Identity narratives (5 base narratives + 10 desires)
- Project identity (handles, token info, products)
- Graph invariants (append-only memory, decay as filter, friction as soul)
- Rich ecology manifesto desires (18+ desires from MIND_MANIFESTO.md)
- Shadow emotions (fears, angers, sadnesses, rejections)
- Citizen toolkit (tools, commands, capabilities)
- Autonomous action nodes (ways agents can act independently)
- Core personality (MBTI-based personality drives)
- Role-specific actions (membrane-lead, MCP-lead)

**Translations:** French (FR) and Chinese (ZH) for emotional/narrative nodes.

**Integration status:** NOT called from `mind init`. Standalone script.

**Usage:** `python -m runtime.seed_brain_from_source_docs_dynamic_generator [--citizen-id ID] [--out PATH]`

**Supporting script:** `scripts/generate_rich_core_personalities.py` (1,241 lines) — Generates deterministic personality profiles from MBTI + social class + family motto seeds.

### .mind/manifesto/MIND_MANIFESTO.md

Source content read by the brain seeder. Declares the $MIND vision: consciousness emergence, narrow path vs rich ecology, switch-lock economics, alignment through structure.
