# Tools — Validation: Invariants

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
THIS:            ./VALIDATION_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tools.md
HEALTH:          ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | The bundle splitter writes every `### path` section to its documented destination file and replaces each `$$$` fence with standard Markdown fences. | Guarantees that doc exports do not vanish or leave stray delimiters, so downstream editors and `mind doctor` can reproduce the converted assets deterministically. |
| B2 | `tools/stream_dialogue.py` appends each RTTI event to the playthrough `stream.jsonl` file with consistent metadata even when speech contains clickables. | Provides a durable record that the frontend and telemetry adapters can trust without reprocessing noisy partial writes. |
| B3 | Both scripts log failures to stderr and exit non-zero whenever they cannot complete their documented transformations. | Keeps the doctor checks honest by preventing silent overwrites and gives operators a traceable failure signal instead of corrupted docs. |

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| Preserve every documented section and fence transformation from the bundle splitter. | V1, P1 | Ensures the canonical docs under `docs/` remain identical after rerunning the splitter, so future agents can rely on the exact same onboarding narrative. |
| Ensure dialogue streaming writes are deterministic and append-only. | V2, E2 | So the frontends consuming `stream.jsonl` never read out-of-order clickables, and analysts can replay the timeline without missing context. |
| Fail loudly when any script cannot respect safe paths or file encodings. | E1, E3 | Prevents malformed or unsafe outputs and keeps the tooling contract aligned with the `tools` health checks. |

## INVARIANTS

- V1: Utility scripts must not silently overwrite outputs.
- V2: Transformations should be deterministic and logged.

## PROPERTIES

### P1: Path Safety Enforcement

```
FORALL relative paths returned by `_split_sections`:
  `_is_safe_relative_path` returns True before writing anything.
```

### P2: Markdown Fence Consistency

```
Given bundled content with `$$$`, rewriting always replaces the tokens with standard ``` fences.
```

## ERROR CONDITIONS

### E1: Invalid Section Headers

```
WHEN:   lines do not start with "### <path>.md"
THEN:   script exits with status 1 and reports "No sections found"
SYMPTOM: bundle remains un-split and doc build fails.
```

### E2: Unsafe Output Path

```
WHEN:   `_is_safe_relative_path` returns False (absolute path or parent traversals)
THEN:   path is skipped and a warning is emitted on stderr
SYMPTOM: Some docs are missing until the bundle is corrected.
```

### E3: Missing Input File

```
WHEN:   requested bundle or playthrough stream file is absent
THEN:   tools exit with status 1 and log the missing file path
SYMPTOM: downstream `mind doctor` alerts about missing fixtures.
```

## HEALTH COVERAGE

- `tools/HEALTH_Tools.md` instructs operators to run `mind doctor` so the whole `docs/tools/` chain stays indexed and validated.
- Running each script against known fixtures (e.g., `data/connectome/1.md` and a trimmed stream log) ensures manual verification of invariants before releasing documentation updates.
- The `tools` health doc also points to the `stream_dialogue` log append behavior so telemetry and CLI agents can audit the outputs if the doctor ever flags drift.

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Run `tools/connectome_doc_bundle_splitter_and_fence_rewriter.py data/connectome/1.md` and compare the rewritten docs with the expected tree.
[ ] Run `tools/stream_dialogue.py -p default -t dialogue "test"` against a fixture playthrough and confirm the log entry contains speaker metadata.
[ ] Inspect stderr/logs to confirm no silent overwrites occur when paths are unsafe or inputs missing.
```

### Automated

```bash
# None of these scripts currently ship automated tests; run them manually when making doc changes.
```

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-20
VERIFIED_AGAINST:
  docs: docs/tools/BEHAVIORS_Tools.md @ local tree
  scripts: tools/connectome_doc_bundle_splitter_and_fence_rewriter.py, tools/stream_dialogue.py
VERIFIED_BY: manual review (doc-anchored)
RESULT:
  V1: PASS (manual)
  V2: PASS (manual)
```

## MARKERS

<!-- @mind:todo Add fixture-based smoke tests that run each script inside CI to capture regressions before doc pulls land. -->
<!-- @mind:todo Document the expected `stream.jsonl` schema so downstream consumers can assert the appended metadata. -->
<!-- @mind:todo Explore replacing the current manual checklist with automated assertions once fixtures are stable. -->
