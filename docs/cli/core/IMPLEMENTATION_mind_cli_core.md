# mind_cli_core — Implementation: Code Architecture and Structure

```
STATUS: CANONICAL
CREATED: 2025-12-24
UPDATED: 2025-12-29
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
│   ├── init.py              # mind init command
│   ├── status.py            # mind status command
│   ├── upgrade.py           # mind upgrade command
│   └── fix_embeddings.py    # mind fix-embeddings command
└── helpers/
    ├── __init__.py
    ├── get_paths_for_templates_and_runtime.py
    ├── get_mcp_version_from_config.py
    ├── copy_runtime_package_to_target.py
    ├── update_gitignore_with_runtime_entry.py
    ├── check_github_for_latest_version.py
    ├── show_upgrade_notice_if_available.py
    ├── create_ai_config_files_for_claude_agents_gemini.py
    ├── sync_skills_to_ai_tool_directories.py
    ├── create_env_example_file.py
    ├── setup_database_and_apply_schema.py
    ├── create_database_config_yaml.py
    ├── validate_embedding_config_matches_stored.py
    ├── check_mind_status_in_directory.py
    ├── create_mcp_config_json.py
    ├── fix_embeddings_for_nodes_and_links.py
    ├── copy_ecosystem_templates_to_target.py
    ├── generate_repo_overview_maps.py
    ├── inject_seed_yaml_to_graph.py
    └── ingest_repo_files_to_graph.py
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

| Helper | Purpose |
|--------|---------|
| `get_paths_for_templates_and_runtime.py` | Resolve template and runtime paths |
| `get_mcp_version_from_config.py` | Get current MCP version |
| `copy_runtime_package_to_target.py` | Copy runtime to target project |
| `update_gitignore_with_runtime_entry.py` | Add .mind to .gitignore |
| `check_github_for_latest_version.py` | Query GitHub for latest release |
| `show_upgrade_notice_if_available.py` | Display upgrade notice |
| `create_ai_config_files_for_claude_agents_gemini.py` | Create AI config files |
| `sync_skills_to_ai_tool_directories.py` | Sync skills to AI tools |
| `create_env_example_file.py` | Create .env.example |
| `setup_database_and_apply_schema.py` | Setup database connection and schema |
| `create_database_config_yaml.py` | Create database.yaml |
| `validate_embedding_config_matches_stored.py` | Validate embedding configuration |
| `check_mind_status_in_directory.py` | Check if directory is mind-initialized |
| `create_mcp_config_json.py` | Create mcp-config.json |
| `fix_embeddings_for_nodes_and_links.py` | Core embedding fix logic |
| `copy_ecosystem_templates_to_target.py` | Copy ecosystem templates |
| `generate_repo_overview_maps.py` | Generate repository overview |
| `inject_seed_yaml_to_graph.py` | Inject seed data to graph |
| `ingest_repo_files_to_graph.py` | Ingest repository files |

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
    +-> create_database_config_yaml()
    +-> create_mcp_config_json()
    +-> create_env_example_file()
    +-> create_ai_config_files_for_claude_agents_gemini()
    +-> sync_skills_to_ai_tool_directories()
    +-> copy_ecosystem_templates_to_target()
    +-> setup_database_and_apply_schema()
    +-> inject_seed_yaml_to_graph()
    +-> ingest_repo_files_to_graph()
    +-> generate_repo_overview_maps()
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
