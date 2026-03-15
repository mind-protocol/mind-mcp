# Task Routing — Sync: Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: @dragon_slayer
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- `select_best_agent()` with `actor_type` parameter for citizen filtering
- `seed_citizen_actors()` for idempotent graph seeding
- `record_task_outcome()` for energy feedback
- `normalize_citizen_id()` and `extract_citizen_handle()` in mapping.py
- Orchestrator integration: `_select_citizen_for_task()`, `pick_autonomous_task()` citizen path
- Brain seed: `narrative:escalation_reflex` and `action:escalate_when_stuck`
- Full doc chain

**What's still being designed:**
- Health checkers (specified but not implemented — see HEALTH doc)

**What's proposed (v2+):**
- Task type affinity tracking per citizen (which task categories they succeed at)
- Cross-project citizen routing (routing tasks from mind-ops to mind-mcp citizens)

---

## CURRENT STATE

All code is implemented and syntax-verified. The system is ready for production testing.

Key changes across two repos:
- **mind-mcp**: Generalized `select_best_agent()` with `actor_type` param, added citizen seed module, added `record_task_outcome()`, added escalation reflex to brain seed, added CITIZEN_ prefix handling to mapping.py
- **orchestrator**: Modified `pick_autonomous_task()` to route through citizens, added citizen seeding on startup, added energy feedback on session completion

The JSONL backlog remains the source of truth for task creation. The graph is the routing layer. The orchestrator bridges them.

---

## RECENT CHANGES

### 2026-03-13: Initial Implementation

- **What:** Complete citizen-based task routing system
- **Why:** Anonymous sessions retry tasks 300+ times. Citizens have identity, memories, and can escalate.
- **Files:**
  - `mind-mcp/runtime/task_assignment.py` — added `actor_type` param, `record_task_outcome()`
  - `mind-mcp/runtime/agents/mapping.py` — added CITIZEN_ prefix handling
  - `mind-mcp/runtime/citizens/seed.py` — new file
  - `mind-mcp/runtime/citizens/__init__.py` — export seed_citizen_actors
  - `mind-mcp/runtime/seed_brain_from_source_docs_dynamic_generator.py` — escalation nodes
  - `runtime/orchestrator/dispatcher.py` — citizen routing in pick_autonomous_task

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Extend or VIEW_Debug

**Where I stopped:** Code complete, syntax verified, docs complete. Health checkers are specified but not implemented.

**What you need to understand:**
The orchestrator seeds citizen actors on startup in a background thread. This means the first task dispatch after startup might not find citizens yet (race window ~5-10s while embeddings compute). The fallback to anonymous dispatch handles this.

**Watch out for:**
- `get_database_adapter(target_dir=...)` needs the project root, not the scripts dir

**Open questions I had:**
- Should we also route incident-triggered tasks through citizens? Currently only backlog tasks go through this path.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Task routing via citizen graph physics is implemented. Every backlog task will be routed to the best-matching citizen (by skills/role embedding similarity), with attempt history and escalation awareness built in. Anonymous dispatch is now a fallback, not the default.

**Decisions made:**
- Bridge architecture (JSONL stays, graph routes) — minimal disruption to existing backlog workflow
- Energy feedback replaces max_attempts — physics-driven, self-correcting
- Background thread for citizen seeding — doesn't block startup

**Needs your input:**
- Should the seeding run on every startup, or only when citizens.json changes?
- Should incident tasks also route through citizens?

---

## TODO

### Immediate

- [ ] Test with live orchestrator (restart orchestrator, verify citizen seeding, trigger a backlog task)
- [ ] Verify zombie tasks (db01ade3, scan-004) get routed to a citizen on next cycle

### Later

- [ ] Implement health checkers (check_anonymous_dispatch_rate, check_orphaned_tasks, check_avg_attempts)
- [ ] Track task type affinity per citizen (which categories they succeed at)

---

## POINTERS

| What | Where |
|------|-------|
| Task scoring | `mind-mcp/runtime/task_assignment.py:select_best_agent()` |
| Citizen seeding | `mind-mcp/runtime/citizens/seed.py:seed_citizen_actors()` |
| Orchestrator bridge | `runtime/orchestrator/dispatcher.py:_select_citizen_for_task()` |
| Energy feedback | `runtime/orchestrator/dispatcher.py:_record_citizen_task_outcome()` |
| Brain escalation | `runtime/seed_brain_from_source_docs_dynamic_generator.py:narrative:escalation_reflex` |
| Citizens config | `config/citizens.json` |
| Backlog source | `shrine/state/backlog.jsonl` |
