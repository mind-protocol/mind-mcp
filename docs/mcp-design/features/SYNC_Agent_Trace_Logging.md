# Agent Trace Logging — Sync: Current State

```
LAST_UPDATED: 2025-12-16
UPDATED_BY: Claude (Opus 4.5)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — feature is being designed

**What's still being designed:**
- Trace file format
- CLI commands (trace, trace --detail, trace clear)
- Integration with context command
- Analysis/summary output

**What's proposed (v2+):**
- File watcher for automatic tracing
- SYNC injection of usage stats
- Cross-session analysis

---

## CURRENT STATE

Documentation complete. Ready for implementation.

Docs created:
- PATTERNS: Design decisions and rationale
- BEHAVIORS: Observable effects and command interface

---

## IMPLEMENTATION PLAN

### Phase 1: Basic tracing (MVP)

1. Add trace logging to `mind context` command
2. Create `.mind/traces/` directory on first trace
3. Write JSONL trace entries
4. Add `mind trace` command for basic summary

### Phase 2: Analysis

5. Add `--detail` flag for raw trace output
6. Add summary statistics (most loaded, least loaded)
7. Add `--clear` command for cleanup

### Phase 3: Integration

8. Integrate with validate (stale doc detection)
9. Add `trace log <file>` for agent self-reporting
10. Optional: file watcher mode

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Start here:**
1. Read BEHAVIORS to understand the interface
2. Implement Phase 1 in cli.py
3. Test with `mind context` on a file
4. Verify trace file created

**Key files:**
- `runtime/cli.py` — add trace functions
- `.mind/traces/` — output location

---

## TODO

### Immediate

<!-- @mind:todo Implement `log_trace()` function -->
<!-- @mind:todo Add tracing to `context` command -->
<!-- @mind:todo Implement `trace` command (basic summary) -->

### Later

<!-- @mind:todo `trace --detail` flag -->
<!-- @mind:todo `trace clear` command -->
<!-- @mind:todo Navigation pattern detection -->
<!-- @mind:todo Stale doc detection integration -->

---

## OPEN QUESTIONS

- Should we trace validate runs? (might be noisy)
- Session ID: auto-generate or let agent provide?
- Retention policy: auto-delete after N days?

---

## MARKERS

<!-- @mind:escalation
title: "Agent Trace Logging feature is documented but NOT implemented"
priority: 3
context: |
  The entire Agent Trace Logging feature (mind trace command, .mind/traces/,
  JSONL logging, etc.) is fully documented in PATTERNS, BEHAVIORS, and SYNC files
  but has ZERO implementation. No code exists in mind/*.py for this feature.
  This documentation describes vaporware.
question: |
  Should this feature be:
  a) Implemented as documented
  b) Removed from docs (design cancelled)
  c) Kept as future design spec (mark as PROPOSED v2+)
-->

<!-- @mind:proposition
title: "Move Agent Trace Logging docs to PROPOSED/future"
suggestion: |
  Since Agent Trace Logging has no implementation and STATUS is DESIGNING,
  these docs should either:
  1. Be moved to a dedicated "proposed-features/" directory
  2. Have their STATUS changed to PROPOSED with clear "NOT IMPLEMENTED" warnings
  3. Be linked from .mind/FRAMEWORK.md as "future capabilities"
  This prevents agents from expecting `mind trace` to work.
-->
