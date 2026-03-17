# Swarm Driver — Sync

```
LAST_UPDATED: 2025-12-30
STATUS: CANONICAL
```

---

## Current State

Swarm driver capability is **defined and ready for implementation**.

---

## Behavior Summary

| Aspect | Value |
|--------|-------|
| Frequency | Every 2 minutes |
| Trigger | Only if new log content |
| Output | At most 1 task (singleton) |
| Reactivation | Yes, if issue recurs after completion |

---

## State File

```
.mind/swarm/driver_state.json
```

Tracks:
- File positions (read offsets)
- Last task ID created
- Last run timestamp

---

## Log Sources

```
.mind/swarm/logs/*.log
```

Expected files:
- `agent_*.log` — per-agent activity
- `tasks.log` — task lifecycle
- `errors.log` — failures
- `completions.log` — finished work

---

## Implementation Status

| Component | Status |
|-----------|--------|
| Doc chain | ✅ CANONICAL (all 8 docs) |
| Runtime | pending |
| Integration | pending |

---

## Recent Changes

- **2026-03-15** — @debug42: BEHAVIORS.md, VALIDATION.md, IMPLEMENTATION.md written and marked CANONICAL. Doc chain complete. 11 behaviors (B1-B11), 8 invariants (V1-V8), full file structure, runtime code, data flow diagram.

---

## Next Steps

1. Create `.mind/swarm/logs/` directory
2. Implement `runtime/driver.py` (code in IMPLEMENTATION.md is reference — wire to actual graph)
3. Create task templates in `tasks/` (4 files)
4. Register with cron scheduler
5. Test with sample logs
