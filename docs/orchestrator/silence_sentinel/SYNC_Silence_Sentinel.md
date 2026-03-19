# Silence Sentinel — Sync: Current State

```
LAST_UPDATED: 2026-03-19 20:30 UTC
UPDATED_BY: @mechanical_visionary (guest session)
STATUS: DESIGNING — full doc chain written (9/9), code not yet implemented
```

---

## GUARANTEE LOOP STATUS

| Result | Sense | Health | Carrier | Wired in L3? |
|--------|-------|--------|---------|--------------|
| R1: Detected within 5min | sense:sentinel:detection_latency / PENDING | H1: silence_detector_alive / PENDING | auto-routed / PENDING | no |
| R2: Per-flow isolation | sense:sentinel:flow_isolation / PENDING | H2: per_flow_counters_active / PENDING | auto-routed / PENDING | no |
| R3: Zero false alarms | sense:sentinel:false_positive_rate / PENDING | H3: baseline_calibration_healthy / PENDING | auto-routed / PENDING | no |

**Completeness: 0/3 results fully wired. Doc chain complete, code next.**

---

## Current State

Full doc chain written (RESULTS, OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC). The design is complete and internally consistent. The guarantee loop is specified but not yet wired — needs code implementation.

---

## In Progress

### Implementation: silence_counter.py

- **Started:** 2026-03-19
- **By:** @mechanical_visionary
- **Status:** doc chain complete, code next
- **Context:** Motivated by the Popen bug (2026-03-19) that showed 98.8% silent failure rate.

---

## Recent Changes

### 2026-03-19: Doc chain created

- **What:** 9 doc chain files written from templates
- **Why:** The Popen bug proved that mechanism-based health checks miss the deadliest failures. Output-rate monitoring is the only robust approach.
- **Files:** docs/orchestrator/silence_sentinel/* (9 files)

---

## Handoff: For Agents

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Doc chain complete. Code not started.

**What you need to understand:**
The counter module is simple — a dict of deques of buckets. The tricky parts are:
1. "Substantive" classification for invoke_claude (must reject subconscious placeholders)
2. Baseline adjustment using pressure + circadian (must read from existing modules)
3. Auto-routing via inject_stimulus(target="infra") — uses existing subcall physics

**Watch out for:**
- Counter calls MUST be fire-and-forget. If silence_counter.py fails to import, the instrumented flow must continue. Wrap imports in try/except at the call site.
- The evaluate_all() function must be called from the dispatcher's _run_loop, not from a separate thread. All counter access is from the dispatcher thread (GIL-safe, no locks needed).

**Open questions:**
- Should evaluate_all() run every tick (5s) or every N ticks? Every tick is fine — O(300) per evaluation is negligible.
- How to handle the "all flows fail simultaneously" case? The sentinel fires RED for each independently, but if the tick loop itself is dead, the sentinel can't fire. This is caught by the external /health endpoint.

---

## Handoff: For Human

**Executive summary:**
Complete doc chain for the Silence Sentinel — a continuous sense that detects flows producing no output. Designed as the permanent fix for the class of bug that caused the Popen failure. Self-calibrating baseline, per-flow isolation, auto-routing. Code implementation next.

**Decisions made:**
- 5-minute detection window (1min = too reactive, 15min = too slow)
- Rolling 1h baseline adjusted by pressure + circadian
- Per-flow counters (not global average)
- "Substantive" output classification (rejects subconscious placeholders)
- Auto-routing via existing subcall physics (no hardcoded carrier)

**Needs your input:**
- None — ready to implement

---

## TODO

### Immediate

- [ ] Implement silence_counter.py (counter + evaluation + routing)
- [ ] Instrument dispatcher.py:dispatch() with record_attempt("invoke_claude")
- [ ] Instrument dispatcher.py:_collect_completed_futures() with record_success("invoke_claude")
- [ ] Instrument claude_invoker.py with substantive classification
- [ ] Add evaluate_all() call to dispatcher._run_loop()
- [ ] Wire sense nodes in L3 (CONTRIBUTES_TO objectives)
- [ ] Test: simulate Popen bug scenario → verify RED in <5min

### Later

- [ ] Instrument bridge_telegram when bridges are production-tested
- [ ] Instrument bridge_whatsapp when bridges are production-tested
- [ ] Instrument graph_write in awareness_tick
- [ ] Implement H1/H2/H3 health checkers
- [ ] 24h baseline window for slow degradation detection (separate sense)

---

## Pointers

| What | Where |
|------|-------|
| Counter module (to create) | `runtime/orchestrator/silence_counter.py` |
| Dispatcher (to instrument) | `runtime/orchestrator/dispatcher.py:dispatch()` |
| Invoker (to instrument) | `runtime/orchestrator/claude_invoker.py:invoke_claude()` |
| Existing inject_stimulus | `runtime/orchestrator/dispatcher.py:inject_stimulus()` |
| Activation pressure | `runtime/orchestrator/activation_pressure.py` |
| Metabolism circadian | `runtime/cognition/metabolism.py` |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
