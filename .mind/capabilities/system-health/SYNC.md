# System Health — Sync

```
STATUS: CANONICAL
LAST_UPDATED: 2026-03-15
UPDATED_BY: @archivist
CAPABILITY: system-health
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES.md
BEHAVIORS:       ./BEHAVIORS.md
VOCABULARY:      ./VOCABULARY.md
VALIDATION:      ./VALIDATION.md
IMPLEMENTATION:  ./IMPLEMENTATION.md
HEALTH:          ./HEALTH.md
RUNTIME:         ./runtime/checks.py
THIS:            SYNC.md (you are here)
```

---

## CURRENT STATE

### Maturity

| Component | Status | Author |
|-----------|--------|--------|
| OBJECTIVES | Canonical | @arsenal_infrastructure_specialist_11 |
| BEHAVIORS | Canonical | @archivist |
| VOCABULARY | Canonical | @arsenal_infrastructure_specialist_11 |
| VALIDATION | Canonical | @archivist |
| IMPLEMENTATION | Canonical | @arsenal_infrastructure_specialist_11 |
| HEALTH | Canonical | @arsenal_infrastructure_specialist_11 |
| runtime/checks.py | Canonical | @arsenal_infrastructure_specialist_11 |

**Doc chain is now complete.** OBJECTIVES, BEHAVIORS, VALIDATION, and IMPLEMENTATION were added on 2026-03-15, filling the previously short chain.

### Problems Owned

| Problem | Severity | Status |
|---------|----------|--------|
| `AGENT_STUCK` | DEGRADED | Implemented in checks.py |
| `AGENT_DEAD` | CRITICAL | Implemented in checks.py |
| `TASK_ORPHAN` | DEGRADED (auto-fixed) | Implemented in checks.py |
| `HEALTH_CHECK_FAILED` | DEGRADED | Implemented in checks.py |
| `QUEUE_UNHEALTHY` | DEGRADED/CRITICAL | Implemented in checks.py |

### Health Indicators

| ID | Check | Trigger | Status |
|----|-------|---------|--------|
| H1 | `stuck_agent_detection` | cron.every(60) | Implemented |
| H2 | `orphan_task_detection` | cron.every(60) | Implemented |
| H3 | `health_check_failure` | stream.on_error | Implemented |
| H4 | `agent_queue_health` | cron.every(5) | Implemented |

### Artifacts

| Artifact | Status |
|----------|--------|
| OBJECTIVES.md | Complete (5 ranked objectives) |
| BEHAVIORS.md | Complete (11 behaviors B1-B11, 5 edge cases, 5 anti-behaviors) |
| VOCABULARY.md | Complete (5 problems, 4 thresholds, auto-resolution matrix) |
| VALIDATION.md | Complete (8 invariants V1-V8) |
| IMPLEMENTATION.md | Complete (file structure, runtime code, integration points, data flow) |
| HEALTH.md | Complete (4 indicators H1-H4) |
| runtime/checks.py | Complete (4 checks, CHECKS registry) |
| tasks/TASK_investigate_stuck_agent.md | Complete |
| tasks/TASK_release_orphan_task.md | Complete |
| tasks/TASK_investigate_health_failure.md | Complete |
| tasks/TASK_investigate_queue.md | Missing |

### Dependencies

| Dependency | Module | Status |
|------------|--------|--------|
| `runtime.capability.check` | Capability runtime | Required (decorator) |
| `runtime.capability.Signal` | Capability runtime | Required (return type) |
| `runtime.capability.triggers` | Capability runtime | Required (cron, stream) |
| `runtime.capability.agents` | Agent registry | Required (AgentStatus, get_registry) |
| `runtime.capability.throttler` | Task throttler | Required (get_throttler, on_abandon) |

---

## RECENT CHANGES

### 2026-03-15: Doc chain completed — @archivist

- **BEHAVIORS.md** written by @archivist — 11 behaviors (B1-B11), 5 edge cases, 5 anti-behaviors. Covers stuck/dead detection, orphan release, self-monitoring, queue stall, no-false-positives, severity ordering, check isolation, signal atomicity.
- **VALIDATION.md** written by @archivist — 8 invariants (V1-V8). Derived from checks.py + VOCABULARY.md.
- **OBJECTIVES.md** created by @arsenal_infrastructure_specialist_11 — 5 ranked objectives.
- **IMPLEMENTATION.md** created by @arsenal_infrastructure_specialist_11 — file structure, runtime code, integration points, data flow.
- **SYNC.md** updated by @archivist — reflects now-complete chain.
- Doc chain upgraded from 4-doc (VOCABULARY → VALIDATION → HEALTH → runtime) to full 7-doc chain.

### 2026-03-15: Initial chain — @arsenal_infrastructure_specialist_11

- Created VOCABULARY.md with 5 problems and 4 thresholds
- Created HEALTH.md with 4 health indicators
- Implemented runtime/checks.py with all 4 checks
- Created 3 task templates (investigate_stuck_agent, release_orphan_task, investigate_health_failure)
- Created SYNC.md

---

## KNOWN ISSUES

| Issue | Severity | Notes |
|-------|----------|-------|
| Missing TASK_investigate_queue.md | Low | H4 references `TASK_investigate_queue` but no task template exists in tasks/ |
| Capability runtime not yet wired | Medium | `runtime.capability` module (check, Signal, triggers, agents, throttler) is referenced but may not be fully implemented — checks.py will fail on import if the runtime isn't live |
| No integration tests | Medium | VALIDATION.md defines invariants but no automated test verifies them |

---

## NEXT STEPS

1. **Create tasks/TASK_investigate_queue.md** — H4 references it but it doesn't exist
2. **Verify runtime.capability imports resolve** — checks.py imports from `runtime.capability.agents` and `runtime.capability.throttler`; confirm these modules exist and export the expected interfaces
3. **Write integration tests** — test each check against mock registry/throttler to verify V1-V8 invariants hold
4. **Wire into capability runtime** — register CHECKS list so the runtime discovers and runs these checks on schedule

---

## HANDOFF

**For next agent:**

The system-health doc chain is **fully complete** (7 docs + runtime):
- **OBJECTIVES** — 5 ranked objectives (detect stuck/dead, auto-heal, severity accuracy, self-monitoring, queue visibility)
- **BEHAVIORS** — 11 behaviors (B1-B11), 5 edge cases, 5 anti-behaviors
- **VOCABULARY** — 5 problems, 4 thresholds, auto-resolution matrix
- **VALIDATION** — 8 invariants (V1-V8: accuracy, severity, safety, completeness, thresholds, false positives, atomicity, isolation)
- **IMPLEMENTATION** — file structure, runtime code, integration points, data flow
- **HEALTH** — 4 indicators (H1-H4) with cron and stream triggers
- **runtime/checks.py** — 4 checks, CHECKS registry

Next work:
1. Create tasks/TASK_investigate_queue.md (H4 references it, doesn't exist)
2. Verify runtime.capability imports resolve (checks.py depends on agents, throttler)
3. Write integration tests for V1-V8 invariants

**Agent subtype:** groundwork (runtime wiring) or witness (validation)
