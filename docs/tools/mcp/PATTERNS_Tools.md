# Tools — Patterns: Utility Scripts

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
THIS:            docs/tools/PATTERNS_Tools.md
BEHAVIORS:       ./BEHAVIORS_Tools.md
ALGORITHM:       ./ALGORITHM_Tools.md
VALIDATION:      ./VALIDATION_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tools.md
HEALTH:          ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

---

## THE PROBLEM

Utility scripts are easy to lose track of without documentation, which makes it harder to reuse them and keep them aligned with the rest of the protocol.

## THE PATTERN

Treat `tools/` as a small, documented module. Each script stays lightweight, but the module captures intent, ownership, and guardrails.

## BEHAVIORS SUPPORTED

- Utility documentation splitting safely extracts bundled exports into repo-aligned Markdown fragments and rewrites `$$$` fences so downstream modules treat the derived files as source-worthy artifacts.
- Dialogue streaming keeps narrated playthroughs reproducible by emitting JSONL events, tagging each entry with GraphOps metadata, and supplying a shareable feed the SSE player and log archives can tail.

## BEHAVIORS PREVENTED

- Prevent accidental corruption of the canonical docs tree by blocking any splitter path that would escape `docs/connectome/` or overwrite non-derived files without explicit approval.
- Prevent inconsistent moment streams by requiring GraphOps connectivity and metadata consistency before the streamer appends entries, so the SSE endpoint always references valid clickables.

## PRINCIPLES

- Document every helper so the scripts cannot drift into undocumented improvisations; the PATTERN keeps their guardrails visible and auditable.
- Keep scripts script-like: small, composable, and focused on one transformation or startup task so ownership remains obvious.
- Treat any environment or service wiring (ngrok hosts, frontend commands, systemd units) as configuration metadata that must be surfaced in the protocol rather than hidden in shell helpers.
- Maintain deterministic outputs by sanitizing inputs (paths, CLI args, playthrough identifiers) before any mutation occurs.

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `data/connectome/*.md` bundles | FILE | Primary input for the splitter; each bundle is parsed by header lines such as `### path.md` to derive modular doc fragments. |
| `docs/connectome/` targets | DIRECTORY | Destination for the rewritten fragments so the rest of the chain consumes canonical module docs rather than the original export. |
| Streamed playthrough logs | JSONL | Input for `stream_dialogue.py`; each event includes `dialogue`, `scene`, `time`, and `complete` flags plus FalkorDB identifiers. |
| GraphOps metadata | GRAPH | Retrieved during dialogue streaming to attach clickables, character references, and moment IDs so downstream consumers can replay interactions. |
| Environment variables (`NGROK_*`, `FE_CMD`, `FALKORDB_HOST`) | CONFIG | Supply service endpoints to the helpers, keeping runtime wiring flexible and machine-specific without hard-coding secrets.

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `docs/connectome/*` | The splitter writes into this directory and the rest of the doc chain (behaviors, algorithm, validation, health, sync) reads from there. |
| `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py` | Implements the splitter pattern and enforces path sanitization, so it is the runtime embodiment of the documented behavior. |
| `tools/stream_dialogue.py` | Implements the narrative streamer, updating GraphOps moments and JSONL logs aligned with the PATTERN. |
| `tools/run_stack.sh` | Coordinates service restarts, logs commands, and uses the documented env vars so that the module can restart its dependencies without surprises. |
| `tools/ngrok.yml` & systemd user units | Provide auxiliary wiring for tunneling and service orchestration mentioned in the PATTERN scope.

## INSPIRATIONS

- Documentation build systems that treat exported blobs as inputs to safe, deterministic preprocessors.
- Streaming pipelines where each log entry is tagged with enough metadata to replay or audit the exact user intent.
- Dev tooling ecosystems that keep runtime wiring in config files so scripts remain portable and easy to reason about.
- Systems that prefer small, single-responsibility utilities over monolithic `make` targets, because each tool can be documented and verified in isolation.

## SCOPE

### In Scope

- Documenting every helper under `tools/` that operates as part of the stack runner, stream utilities, or documentation bundler.
- Ensuring environment wiring (`NGROK_*`, `FE_CMD`, GraphOps hosts) is surfaced in docs so future agents can reproduce the runtime behavior.
- Guarding doc bundle outputs, streamer metadata, and log directories with sanitization and path checks.
- Keeping the module scoped to tooling, not migrating into business logic or application runtime features.

### Out of Scope

- Rewriting the frontend or backend runtime code; the tools module should orchestrate, not replace, the application stacks.
- Embedding secret credentials inside scripts instead of describing them via configs and env templates.
- Introducing new distributed service orchestration outside the documented stack runner and systemd wiring until those helpers stabilize.

## MARKERS

<!-- @mind:todo Decide if the splitter should capture a manifest mapping bundle names to derived docs for traceability in audit logs. -->
<!-- @mind:todo Determine whether `stream_dialogue.py` needs a dry-run mode to validate JSON/GraphOps payloads without mutating the production store. -->
<!-- @mind:todo Ask whether the canonical frontend command for `mind-fe.service` can be documented here so `tools/run_stack.sh` can rely on a single source of truth. -->
