# Tools — Behaviors: Utility Outcomes

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tools.md
THIS:            ./BEHAVIORS_Tools.md
ALGORITHM:       ./ALGORITHM_Tools.md
VALIDATION:      ./VALIDATION_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tools.md
HEALTH:          ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

---

## BEHAVIORS

### B1: Documentation Bundle Splitter

```
GIVEN:  A bundled markdown export
WHEN:   The splitter script runs
THEN:   The bundle is converted into module-friendly docs
```

Each rewritten file is sanitized via `_is_safe_relative_path` and placed under
`docs/connectome/`, so repeated runs remain idempotent and the canonical module
chain stays traceable from the bundle source.

### B2: Dialogue Streaming

```
GIVEN:  Streamed dialogue logs
WHEN:   The stream helper runs
THEN:   Output is formatted for review or ingestion
```

The stream emits newline-delimited JSON events and updates GraphOps moments so
the SSE reader, CLI log, and replay archives all observe the same sequence of
`dialogue`, `scene`, `time`, `complete`, and `error` payloads.

## OBJECTIVES SERVED

- Keep documentation bundles split cleanly so the connectome frontend and any
  downstream doc producers can import individual chapters without stitching the
  original export back together.
- Make narrated playthroughs reproducible for debugging and visualization while
  anchoring each streamed event to the FalkorDB graph via consistent metadata,
  clickable annotations, and the shared JSONL feed.
- Translate the stack runner outputs into documented objectives so operators and
  auditors can match every `tools/run_stack.sh` restart log to the behavior ledger
  that lists its goals, expected services, and log destinations.

## INPUTS / OUTPUTS

- **Inputs:** The splitter consumes `data/connectome/*.md` bundles with
  `### path.md` headers, while the stream helper accepts CLI arguments that
  reference playthrough IDs, event types, and optionally JSON files or inline
  text. Both helpers rely on sanitized environment data (ngrok host/port, CLI
  flags) so their outputs remain predictable.
- **Outputs:** The splitter writes module-friendly docs under `docs/connectome/`,
  rewrites `$$$` fences to Markdown ``` fences, and logs rewritten paths for the
  doc chain. The streamer updates `playthroughs/<id>/stream.jsonl`, creates
  GraphOps moments/clickables, and echoes a service-friendly JSON feed that the
  SSE endpoint, log archivist, and reviewers can tail in real time.
- **Outputs (stack runner):** `tools/run_stack.sh` records each service restart
  (FalkorDB, backend, optional frontend, MCP server, ngrok) into `./logs/run_stack`
  and appends stderr to `./.mind-mcp/error.log` so operators know what commands were
  issued and how the helper behaved during emergent restarts.

## EDGE CASES

- Splitting must never overwrite files outside `docs/connectome/`; `_is_safe_*`
  guards and path normalization enforce this because bundles sometimes contain
  trailing `../` fragments that would otherwise escape the repo root.
- Empty sections or headers without accompanying text fall back to placeholder
  stubs so the rebuild process never leaves dangling docs; the splitter still
  logs the missing sections in case the bundle publisher needs to fill them.
- Streaming events with missing playthrough IDs, malformed JSON, or GraphOps
  downtime are surfaced through the `error` event and the CLI exit code rather
  than crashing the helper, keeping the log archives consistent.

## ANTI-BEHAVIORS

- Do not treat the outputs of `tools/_split_sections` as canonical source
  documents; every run rewrites those files, so the original bundle must stay in
  version control if it is still needed.
- Avoid running `stream_dialogue` without GraphOps connectivity because the
  helper would still append JSONL lines but those entries would never resolve to
  moments, leaving the SSE feed with orphaned clickables.
- Never bypass the `run_stack.sh` log redirection or `setsid` wrapping because
  the stack helper documents every restart via `./logs/run_stack`; skipping the
  tracer makes it harder to audit what commands ran after the last crash.

## MARKERS

<!-- @mind:todo Should the splitter log a manifest (bundle name → output files) so revisions -->
  can be traced even after the target docs rotate during refactors?
<!-- @mind:todo Could `stream_dialogue` expose a `--dry-run` mode to validate JSON/GraphOps -->
  payloads without mutating FalkorDB, which would help scripted regression tests?
<!-- @mind:todo What is the canonical frontend command for `mind-fe.service`, and should -->
  `tools/run_stack.sh` expose it via a documented `FE_CMD` expectation for
  `ngrok` integration?
