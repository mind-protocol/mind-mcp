# Agent Trace Logging — Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2024-12-16
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Agent_Trace_Logging.md
BEHAVIORS:       THIS
ALGORITHM:       (not yet created)
VALIDATION:      (not yet created)
IMPLEMENTATION:  (not yet created)
TEST:            (not yet created)
SYNC:            ./SYNC_Agent_Trace_Logging.md
```

---

## COMMANDS

### `mind trace`

Show trace summary for current project.

```bash
$ mind trace

Trace Summary (last 7 days)
===========================

Docs loaded: 47 times across 12 sessions

Most loaded:
  1. SYNC_Project_State.md          (12 loads, 100% of sessions)
  2. PATTERNS_*.md                  (34 loads, 92% of sessions)
  3. VIEW_Implement_*.md            (8 loads, 67% of sessions)
  4. BEHAVIORS_*.md                 (5 loads, 42% of sessions)
  5. ALGORITHM_*.md                 (2 loads, 17% of sessions)

Least loaded:
  1. VALIDATION_*.md                (0 loads)
  2. HEALTH_*.md                    (1 load, 8% of sessions)

Navigation patterns:
  VIEW → SYNC → PATTERNS           (8 times)
  PATTERNS → SYNC                  (4 times)
  context command → full chain     (3 times)

Potentially stale:
  - docs/engine/ALGORITHM_*.md: loaded 2x, never updated, code changed 5x
```

### `mind trace --detail`

Show individual trace entries.

```bash
$ mind trace --detail --limit 10

2024-12-16 14:32:01 | READ    | ...mind/state/SYNC_Project_State.md
2024-12-16 14:32:05 | READ    | .mind/views/VIEW_Implement_*.md
2024-12-16 14:32:15 | READ    | docs/engine/graph/PATTERNS_*.md
2024-12-16 14:33:01 | CONTEXT | src/engine/graph.py → docs/engine/graph/ (4 docs)
...
```

### `mind trace clear`

Clear trace history.

```bash
$ mind trace clear --before 30d
Cleared 156 trace entries older than 30 days.
```

---

## AUTOMATIC TRACING

### From CLI commands

When `mind context <file>` is run, it logs:
- The file requested
- All docs returned in the chain
- Timestamp

### From file reads (if watching)

When `mind watch` is running:
- Detects reads of `.mind/` and `docs/` files
- Logs each read with timestamp and file path

---

## TRACE FILE FORMAT

Location: `.mind/traces/YYYY-MM-DD.jsonl`

Each line is a JSON object:

```json
{"ts": "2024-12-16T14:32:01Z", "action": "read", "file": "docs/engine/graph/PATTERNS_Graph.md", "via": "context-cmd", "session": "abc123"}
{"ts": "2024-12-16T14:32:05Z", "action": "read", "file": ".mind/views/VIEW_Implement.md", "via": "direct", "session": "abc123"}
```

Fields:
- `ts`: ISO timestamp
- `action`: read, context, view-load
- `file`: relative path from project root
- `via`: how it was accessed (context-cmd, direct, validate, etc.)
- `session`: optional session identifier for grouping

---

## INTEGRATION POINTS

### With validate

`mind validate` can use traces to enhance warnings:

```
✗ [DR] Drift detected
    - docs/engine/ALGORITHM_*.md
      Loaded 5 times in last 7 days, but not updated since code changed
```

### With SYNC

SYNC files can show trace-based insights:

```markdown
## Usage (auto-generated)

This doc was loaded 12 times in the last 30 days.
Last loaded: 2024-12-16 by session xyz
```

---

## WHAT GETS TRACED

| Action | Traced? | Notes |
|--------|---------|-------|
| `mind context` | Yes | Logs file + all chain docs |
| `mind validate` | Yes | Logs which checks ran |
| `mind prompt` | Yes | Logs prompt generation |
| Direct file read by agent | Only if watching | Requires `trace watch` |
| Agent self-report | Yes | Via `trace log` command |

---

## WHAT DOESN'T GET TRACED

- File reads outside the protocol (no way to intercept)
- Reads by other tools (IDE, grep, etc.)
- Content of files (only paths)
