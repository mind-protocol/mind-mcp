# Mind CLI Core — Algorithm: Command Parsing and Execution Logic

```
STATUS: CANONICAL
CREATED: 2023-12-19
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
SYNC:            ./SYNC_mind_cli_core.md
THIS:            ALGORITHM_mind_cli_core.md

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This algorithm describes how the `mind` CLI receives a command, parses it using argparse, dispatches to the appropriate handler, and returns an exit code. The implementation lives in `cli/__main__.py`.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1-O3 | B1-B4 | Enables execution of all implemented commands |
| O4-O7 | B5-B10 | Future extension points for proposed commands |

---

## DATA STRUCTURES

### `Namespace` (argparse)

```
Represents the parsed command-line arguments.
Fields:
  - command: str (subparser name: init, status, upgrade, fix-embeddings)
  - dir: Path (working directory, default: cwd)
  - database: str (for init: falkordb or neo4j)
  - dry_run: bool (for fix-embeddings)
```

---

## ALGORITHM: `main()` in cli/__main__.py

### Step 1: Configure Argument Parser

```python
parser = argparse.ArgumentParser(prog="mind", description="Mind Protocol CLI")
subs = parser.add_subparsers(dest="command")

# Register subcommands
p = subs.add_parser("init", help="Initialize .mind/")
p.add_argument("--dir", "-d", type=Path, default=Path.cwd())
p.add_argument("--database", "-db", choices=["falkordb", "neo4j"], default="falkordb")

p = subs.add_parser("status", help="Show status")
p.add_argument("--dir", "-d", type=Path, default=Path.cwd())

p = subs.add_parser("upgrade", help="Check for updates")
p.add_argument("--dir", "-d", type=Path, default=Path.cwd())

p = subs.add_parser("fix-embeddings", help="Fix missing/mismatched embeddings")
p.add_argument("--dir", "-d", type=Path, default=Path.cwd())
p.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
```

### Step 2: Parse Arguments

```python
args = parser.parse_args()
```

### Step 3: Dispatch Command

```python
if args.command == "init":
    ok = init.run(args.dir, database=args.database)
    show_upgrade_notice()
    sys.exit(0 if ok else 1)

elif args.command == "status":
    code = status.run(args.dir)
    show_upgrade_notice()
    sys.exit(code)

elif args.command == "upgrade":
    ok = upgrade.run(args.dir)
    sys.exit(0 if ok else 1)

elif args.command == "fix-embeddings":
    ok = fix_embeddings.run(args.dir, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)

else:
    parser.print_help()
    show_upgrade_notice()
    sys.exit(1)
```

---

## COMMAND HANDLER ALGORITHMS

### init.run(directory, database)

```pseudocode
1. Check if .mind/ already exists
   - If yes, warn user and decide whether to update or abort
2. Create .mind/ directory structure
3. Create database.yaml with selected backend
4. Create mcp-config.json
5. Create .env.example
6. Create AI config files (CLAUDE.md, etc.)
7. Sync skills to AI tool directories
8. Copy ecosystem templates
9. Setup database and apply schema
10. Inject seed YAML to graph
11. Ingest repository files to graph
12. Generate repository overview maps
13. Return True on success, False on failure
```

### status.run(directory)

```pseudocode
1. Check if .mind/ exists
   - If not, print "Not a mind project" and return non-zero
2. Load database.yaml configuration
3. Connect to database
4. Query graph health metrics
5. Check embedding configuration
6. Print status report
7. Return 0 if healthy, non-zero if issues detected
```

### upgrade.run(directory)

```pseudocode
1. Get current version from config
2. Check GitHub for latest version
3. Compare versions
4. If newer available:
   - Print upgrade instructions
5. Else:
   - Print "Already up to date"
6. Return True
```

### fix_embeddings.run(directory, dry_run)

```pseudocode
1. Load database configuration
2. Validate embedding config matches stored
3. Query for nodes/links with missing or mismatched embeddings
4. If dry_run:
   - Print what would be fixed
   - Return True
5. Else:
   - Regenerate embeddings for affected entities
   - Update graph
   - Print summary
6. Return True on success, False on failure
```

---

## DATA FLOW

```
sys.argv (raw CLI input)
    |
    v
argparse.parse_args() -> Namespace
    |
    v
if/elif dispatch (selects handler)
    |
    v
command_handler.run(args) -> bool/int
    |
    v
sys.exit(code)
```

---

## FUTURE COMMAND DISPATCH (PROPOSED)

When implementing future commands, add to the dispatch:

```python
elif args.command == "validate":
    ok = validate.run(args.dir)
    sys.exit(0 if ok else 1)

elif args.command == "work":
    ok = work.run(args.dir, path=args.path, objective=args.objective)
    sys.exit(0 if ok else 1)

elif args.command == "context":
    context_cmd.run(args.dir, node_id=args.node_id,
                    question=args.question, intent=args.intent)
    sys.exit(0)

elif args.command == "sync-files":
    ok = sync_files.run(args.dir)
    sys.exit(0 if ok else 1)

elif args.command == "human-review":
    ok = human_review.run(args.dir)
    sys.exit(0 if ok else 1)

elif args.command == "talk":
    ok = talk.run(args.dir)
    sys.exit(0 if ok else 1)
```

---

## COMPLEXITY

**Time:** O(1) for argument parsing and dispatch. Handler execution time varies by command.

**Space:** O(1) for CLI scaffolding. Handlers may use more for graph operations.

**Bottlenecks:**
- Database connection latency
- Embedding generation for fix-embeddings
- Repository ingestion for init

---

## HELPER FUNCTIONS

### show_upgrade_notice()

**Purpose:** Display upgrade notice if newer version available.
**Location:** `cli/helpers/show_upgrade_notice_if_available.py`
**Logic:** Checks cached version info and displays notice if update available.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `cli.commands.init` | `run(dir, database)` | `bool` (success) |
| `cli.commands.status` | `run(dir)` | `int` (exit code) |
| `cli.commands.upgrade` | `run(dir)` | `bool` (success) |
| `cli.commands.fix_embeddings` | `run(dir, dry_run)` | `bool` (success) |
| `cli.helpers.*` | Various helpers | Various return types |
