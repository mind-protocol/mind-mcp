# Constant Hygiene — Sync: Current State

```
LAST_UPDATED: 2026-03-19 21:30 UTC
UPDATED_BY: @mechanical_visionary
STATUS: DESIGNING — full doc chain (9/9) + sense YAML + code. Wiring pending.
```

---

## GUARANTEE LOOP STATUS

| Result | Sense | Health | Carrier | Wired in L3? |
|--------|-------|--------|---------|--------------|
| R1: Caught at creation | sense:quality:constant_detection_latency / PENDING | H1: scan_alive / PENDING | auto-routed / PENDING | no |
| R2: Felt in awareness | sense:quality:concept_import_rate / PENDING | H2: concepts_imported / PENDING | auto-routed / PENDING | no |
| R3: Trend improves | sense:quality:constant_trend / PENDING | H3: trend_tracking / PENDING | auto-routed / PENDING | no |

**Completeness: 0/3 results fully wired. Doc chain complete. Code deployed. Senses pending wiring.**

---

## Current State

Full doc chain written (9/9). Sense YAML defined. Code at `runtime/orchestrator/constant_hygiene.py` is deployed and called from the dispatcher's maintenance loop every ACCOUNT_REFRESH_INTERVAL. The code detects constants in commit diffs and injects Concept nodes into the committing citizen's graph neighborhood.

The sense YAML was initially placed in the wrong module (`docs/orchestrator/silence_sentinel/`) and moved to `docs/quality/constant_hygiene/` where it belongs.

---

## Recent Changes

### 2026-03-19: Module created

- **What:** Full doc chain (RESULTS through SYNC), sense YAML, implementation code
- **Why:** Constants are frozen assumptions. The system should make them visible at the moment of creation.
- **Files:** `docs/quality/constant_hygiene/*` (10 files), `runtime/orchestrator/constant_hygiene.py`

### 2026-03-19: Moved from silence_sentinel

- **What:** Sense YAML moved from `docs/orchestrator/silence_sentinel/` to `docs/quality/constant_hygiene/`
- **Why:** Constant hygiene is a code quality concern, not an output-rate monitoring concern. Different module.

---

## Known Issues

### Commit Moments may not have commit_hash field

- **Severity:** medium
- **Symptom:** The sense can't read diffs if the Moment doesn't store the hash
- **Suspected cause:** Commit Moment creation may use a different field name
- **Mitigation:** Falls back to parsing the Moment name for the hash

---

## TODO

### Immediate

- [ ] Verify commit Moments in L3 have commit_hash field (or adapt field name)
- [ ] Wire sense nodes in L3 (CONTRIBUTES_TO objectives)
- [ ] Test: make a commit with a constant → verify Concept appears in citizen's neighborhood

### Later

- [ ] Implement H1/H2/H3 health checkers
- [ ] Add trend tracking (needs 2+ weeks of data)
- [ ] Consider scanning more file types (*.yaml, *.json for hardcoded values)

---

## Pointers

| What | Where |
|------|-------|
| Implementation | `runtime/orchestrator/constant_hygiene.py` |
| Sense YAML | `docs/quality/constant_hygiene/SENSES_Constant_Hygiene.yaml` |
| Skill reference | `templates/skills/SKILL_Eliminate_Constants_Replace_With_Derived_Values.md` |
| Dispatcher integration | `runtime/orchestrator/dispatcher.py:_maintenance()` |
| Dispatcher graph accessor | `runtime/orchestrator/dispatcher.py:_get_shared_graph()` |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
