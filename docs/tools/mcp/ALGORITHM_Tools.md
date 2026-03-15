# Tools — Algorithm: Script Flow

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tools.md
BEHAVIORS:       ./BEHAVIORS_Tools.md
THIS:            ./ALGORITHM_Tools.md
VALIDATION:      ./VALIDATION_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tools.md
HEALTH:          ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

---

## OVERVIEW

The tools module keeps the auxiliary scripts that process documentation bundles,
stream playthrough dialogue, and restart developer services explicit within the
protocol so every helper has a known owner and observable output.

## OBJECTIVES AND BEHAVIORS

These utilities satisfy the behavior ledger: B1 ensures bundled markdown exports
are split into module-friendly docs and B2 keeps narrator streams reproducible for
the graph-backed frontend. Recording the narrative here prevents DOC_TEMPLATE_DRIFT
and keeps the mission visible to future agents.

## DATA STRUCTURES

- The bundle splitter works with a list of `(relative_path, section_text)` tuples
  plus string buffers that capture each Markdown chunk before it is rewritten.
- `stream_dialogue` builds newline-delimited JSON events with `type`, ISO
  `timestamp`, and `data` payloads; the `data` field carries speaker, tone,
  clickable metadata, and moment identifiers that the GraphOps helpers consume.
- Clickable metadata collects `speaks`, `intent`, and the generated
  `target_moment_id`, enabling the narrator to spawn placeholder moments when the
  player clicks inline `[word](response)` links.
- `run_stack.sh` keeps a record of service `pattern`, `cmd`, and `log` files so
  the script can restart FalkorDB, the backend, the optional frontend, MCP server,
  and ngrok in a predictable order.

## ALGORITHM: stream_dialogue.main

1. Parse CLI arguments, resolve `--playthrough`, and determine the event `--type`.
2. For `dialogue` or `narration`, call `create_moment_with_clickables` to add the
   active moment, clickable targets, and CAN_LEAD_TO links via
   `engine.physics.graph.graph_ops.GraphOps` before formatting the clean text for
   streaming.
3. `create_moment_with_clickables` reads tick/place context through
   `GraphQueries`, normalizes `[word](speaks)` clickables, and writes moments and
   links with the required weights so future clicks trigger narratives.
4. For `scene` or `mutation`, ingest JSON from `--file` or inline text, persist
   the payload under `playthroughs/<id>/scene.json`, and hand the dictionary to
   `stream_event`.
5. `time`, `complete`, and `error` events simply append minimal payloads to
   `playthroughs/<id>/stream.jsonl` via `stream_event` without touching the graph;
   `stream_event` returns the record so the CLI prints confirmation.
6. Every path writes to the shared JSONL feed so the SSE consumer can tail the
   same stream that the CLI produced, keeping the frontend, streaming API, and log
   archives synchronized.

## KEY DECISIONS

- Keep these scripts in `tools/` so each helper can stay small, documented, and
  easily invoked by maintainers without being buried under larger modules.
- Call out newline-delimited JSON for streaming so the playthrough logs remain
  human-readable and the SSE endpoint can tail them without a database.
- Sanitize every extracted bundle path via `_is_safe_relative_path` before writing
  to disk to stop directory traversal bugs from leaking into docs.
- Combine service orchestration (FalkorDB, backend, frontend, MCP server, ngrok)
  into a single `run_stack.sh` helper so developers get a deterministic restart
  experience.
- Favor setsid-based backgrounding and log file redirection inside `run_stack.sh`
  so each process leaves a traceable log while stderr is appended to
  `.mind/error.log`.

## DATA FLOW

Bundles move from `data/connectome/*.md` through `_split_sections`, get their
`$$$` fences rewritten, and land under `docs/connectome/`, while narrator text
travels through `stream_dialogue`, mutates the FalkorDB graph, and creates JSONL
events that the SSE reader and log archives replay. `run_stack.sh` interacts with
these scripts indirectly by keeping the backend, ngrok, and frontend alive so the
events can flow uninterrupted.

## COMPLEXITY

- Splitting scales linearly with the bundle text size: each line is inspected once
  and each section writes once, so runtime is proportional to the total
  characters processed.
- Streaming scales with the sum of text length and clickable count because graph
  lookups, JSON encoding, and GraphOps writes are bounded by those values.
- Restarting the stack takes O(S) time, where `S` is the number of configured
  services, because `run_stack.sh` serializes `pgrep`, `pkill`, and `setsid` calls
  for each helper.

## HELPER FUNCTIONS

- `_is_safe_relative_path`: rejects absolute locations and `..` segments to keep
  bundle writes inside the repo.
- `_split_sections`: extracts `(relative_path, section_text)` pairs from `### path.md`
  headers and strips leading blank lines.
- `create_moment_with_clickables`: calls `GraphOps.add_moment` and `add_can_lead_to` to
  register the active moment, clickable targets, and their weight transfers.
- `parse_inline_clickables`: strips `[word](response)` decorators, returns the
  cleaned text, and assembles metadata for clickables so GraphOps can link them.
- `stream_event`: appends the structured payload to `playthroughs/<id>/stream.jsonl`,
  creating the file if necessary.
- `start_service` / `stop_service`: orchestrate `run_stack.sh` by checking patterns,
  killing existing processes, and launching commands via `setsid` with logs routed
  to `./logs/run_stack`.

## INTERACTIONS

This module touches `docs/connectome/` (bundle outputs), `playthroughs/` (stream
JSONL), the `engine.physics.graph` helpers (GraphOps/GraphQueries), and the
frontend SSE feed. `tools/run_stack.sh` keeps the runtime stack humming so these
helpers have backend services to talk to, and `tools/ngrok.yml` plus
`.mind/systemd.env` set the environment that the scripts and services assume.

## MARKERS

<!-- @mind:todo Introduce smoke tests that rerun the splitter on a synthetic bundle to -->
  ensure the rewritten fences and directory structure match expectations.
<!-- @mind:todo Consider adding a `--dry-run` flag to `stream_dialogue` so agents can -->
  validate payloads without modifying the graph.
<!-- @mind:todo Document `run_stack.sh` requirements (ngrok URL, frontend command) near -->
  these docs so the helper’s contract is easier to discover.

## FLOWS

1. Read input files or streams.
2. Transform content into protocol-friendly outputs.
3. Emit outputs into the docs or logs required by the pipeline.
