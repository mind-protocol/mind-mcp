# Tools — Implementation: Code Mapping

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tools.md
BEHAVIORS:       ./BEHAVIORS_Tools.md
ALGORITHM:       ./ALGORITHM_Tools.md
VALIDATION:      ./VALIDATION_Tools.md
THIS:            ./IMPLEMENTATION_Tools.md
HEALTH:          ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

---

## CODE STRUCTURE

Tools sits under the repo root `tools/` directory and keeps each helper as a focused, script-level module so the rest of the pipeline can invoke them directly without importing a layered package. `connectome_doc_bundle_splitter_and_fence_rewriter.py` owns the markdown slicing, rewriting, and file writes, while `stream_dialogue.py` handles narrator CLI wiring, GraphOps mutations, and JSONL output; the two files remain distinct so their responsibilities are discoverable and measurable.

## DESIGN PATTERNS

We follow the Utility Scripts pattern described in `PATTERNS_Tools.md`, meaning each helper is documented, guarded by a single-purpose entry point, and restrained to predictable behaviors so nothing in `tools/` gets lost when the larger repo evolves. This keeps each script from draping itself over unrelated services while still being treated as part of an explicit module.

## SCHEMA

The bundle splitter expects an input that repeats `### relative/path/to/doc.md` headers, rewrites the bodies to replace `$$$` fences with ``` before writing, and emits clean markdown files; the dialogue streamer appends JSON lines with fields such as `type`, `text`, `speaker`, `tone`, `tick`, `timestamp`, and a `clickables` map so downstream SSE consumers can hydrate narrations deterministically. The `clickables` map also carries `requires` metadata so downstream handlers know which word drives each clickable moment.

## ENTRY POINTS

- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py` exposes a `main()` invoked via the shebang or a CLI alias, parses the bundle path plus an optional `--root`, and orchestrates the rewrite loop before printing `Wrote N files.` to stdout.
- `tools/stream_dialogue.py` exposes a rich CLI with the `-p/--playthrough`, `-t/--type`, `--tone`, and `-s/--speaker` flags plus plain text arguments; every invocation ends in either `SystemExit` or an explicit `return` after writing to the playthrough stream and echoing its console signal so telemetry and playwrights know what happened.

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

1. The bundle splitter flow docks at `data/connectome/*.md`, normalizes line endings, splits sections via `_split_sections`, rewrites fences, and writes into `docs/connectome/` paths while printing a summary for operators.
2. The dialogue streamer flow docks at `playthroughs/{id}/stream.jsonl`, resolves the target FalkorDB graph via `player.yaml`, creates GraphOps moments (primary plus clickable targets), appends a timestamped JSON line, and lets SSE listeners tail the log for frontend delivery.
3. The stack runner `tools/run_stack.sh` orchestrates stopping and starting backend, frontend, and infrastructure helpers, logs each command under `./logs/run_stack/`, and ensures the helper scripts run against a warmed-up environment whenever the doc team reboots the stack.

Each flow announces its work (`Wrote N files.` for the splitter, stream traces for `tools/stream_dialogue.py`, and logged restart checkpoints for `run_stack.sh`) so the doctor and humans can quickly verify that the transformations occurred before approvals.

## LOGIC CHAINS

- Splitting: parse CLI args → load bundle text → `_split_sections` → check `_is_safe_relative_path` → rewrite `$$$` → ensure parent directories exist → write files with normalized gutters → count successes → print completion message.
- Streaming: parse CLI args → resolve `playthrough` and GraphOps/Queries → consult the current tick/place → `parse_inline_clickables` → `add_moment` for the main node → add target moments plus CAN_LEAD_TO links → append JSON line to `stream.jsonl` with `toned` metadata → print a trace line when done.

## MODULE DEPENDENCIES

- Standard library: `argparse`, `pathlib`, `sys`, `re`, `json`, `datetime`, `typing`, `yaml` (transitively used for `player.yaml`), and `PurePosixPath` for path sanitization.
- Engine surfaces: `engine.physics.graph.graph_ops.GraphOps` and `engine.physics.graph.graph_queries.GraphQueries` power the moment creation, place lookup, and tick reads that the dialogue streamer relies on.
- Filesystem targets: `data/connectome/`, `docs/connectome/`, and `playthroughs/{id}/stream.jsonl` plus `player.yaml` under each playthrough, forming the storage dependencies.

## STATE MANAGEMENT

The splitter manages no long-lived state beyond the files it writes, but the dialogue streamer relies on FalkorDB world ticks/places plus the append-only `stream.jsonl` log; `GraphOps` handles distributed tick updates, while the script merely reads the current tick/place, writes new moments, and appends JSON lines so operator-visible state lives entirely in those persisted artifacts.

## RUNTIME BEHAVIOR

Calling either script from the CLI prints concise status feedback, exits with zero when every documented transformation succeeds, and writes diagnostics to stderr when it cannot locate its input, encounters an unsafe path, or cannot make a GraphOps mutation, keeping runtime behavior aligned with the documented validation invariants.

## CONCURRENCY MODEL

Both scripts execute in a single thread per invocation and complete their work before returning, leaving concurrency and transactionality to the underlying FalkorDB graph layer and the filesystem; the JSONL append is atomic per line, and repeated invocations serialize through the shell rather than through explicit threading logic.

## CONFIGURATION

`connectome_doc_bundle_splitter_and_fence_rewriter.py` accepts `input` (default `data/connectome/1.md`) and `--root` (default repo root) arguments, while `stream_dialogue.py` requires `-p/--playthrough`, `-t/--type`, optional `--tone`, `-s/--speaker`, and message text; the streamer sets `PROJECT_ROOT` to the repo root so `GraphOps`/`GraphQueries` imports resolve, while each playthrough can override its FalkorDB graph name via `playthroughs/{id}/player.yaml`.

## BIDIRECTIONAL LINKS

This Implementation doc points back to the Tools chain (PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, HEALTH, SYNC), while the stream helper itself ships a `# DOCS:` header pointing at `docs/infrastructure/cli-tools/PATTERNS_CLI_Agent_Utilities.md`, and each script explicitly references these docs so code and documentation stay linked in both directions.

## CODE LOCATIONS

- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/stream_dialogue.py`

## MARKERS

<!-- @mind:todo Add fixture-driven regression checks that run the splitter on a saved bundle so we know `$$$` transforms keep producing the documented documents. -->
<!-- @mind:todo Build a controlled dialogue streamer fixture that asserts the appended JSON line matches the schema described above, including clickable metadata and FalkorDB graph selection. -->
<!-- @mind:todo Explain how `tools/run_stack.sh` fits this implementation ledger so operators can trace its restarts back to this documentation chain when diagnosing drift. -->
## CODE LOCATIONS

- `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py`
- `tools/stream_dialogue.py`
