# Silence Sentinel — Implementation: Code Architecture

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
ALGORITHM:       ./ALGORITHM_Silence_Sentinel.md
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
THIS:            IMPLEMENTATION_Silence_Sentinel.md (you are here)
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md

IMPL:            runtime/orchestrator/silence_counter.py
```

---

## CODE STRUCTURE

```
runtime/orchestrator/
├── silence_counter.py          # Counter module + sense evaluation + routing
├── dispatcher.py               # Instrumented: record_attempt/record_success for invoke flow
├── claude_invoker.py           # Instrumented: substantive response classification
└── (bridges — instrument when bridges are tested)
```

### File Responsibilities

| File | Purpose | Key Functions | Lines | Status |
|------|---------|---------------|-------|--------|
| `runtime/orchestrator/silence_counter.py` | Counter recording, sense evaluation, stimulus routing | `record_attempt`, `record_success`, `evaluate_all`, `_compute_ratio`, `_compute_baseline` | ~200 | NEW |
| `runtime/orchestrator/dispatcher.py` | Instrumented: calls record_attempt in dispatch(), record_success in _collect_completed_futures() | `dispatch()`, `_collect_completed_futures()` | ~870 | MODIFY (2 lines added) |
| `runtime/orchestrator/claude_invoker.py` | Instrumented: classifies substantive responses | `invoke_claude()` | ~700 | MODIFY (3 lines added) |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Observer — counter module observes flow outcomes without modifying flow logic.

**Why:** The counter MUST be invisible to the instrumented code. One-line calls, fire-and-forget, exception-swallowing. The observer pattern keeps the sentinel decoupled from the flows it monitors.

### Anti-Patterns to Avoid

- **Middleware/decorator wrapping:** Don't wrap invoke_claude in a silence_counter decorator. Too magical, hides the instrumentation, breaks when signatures change. Explicit 1-line calls are better.
- **Shared mutable state:** The counter module uses module-level dicts, accessed only from the dispatcher thread (GIL-safe). No locks needed. Don't add threading complexity.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `record_attempt("invoke_claude")` | `dispatcher.py:dispatch()` | Every conscious action dispatch |
| `record_success("invoke_claude")` | `dispatcher.py:_collect_completed_futures()` | When a future completes with substantive output |
| `evaluate_all()` | `dispatcher.py:_run_loop()` | Every tick (called in _maintenance or after _collect) |

---

## DATA FLOW

### Flow: Counter Recording

```yaml
flow:
  name: counter_recording
  purpose: Record attempt/success events from instrumented flows
  steps:
    - id: step_1
      description: Flow calls record_attempt(flow_name)
      file: runtime/orchestrator/silence_counter.py
      function: record_attempt
      input: flow_name (str)
      output: None
      side_effects: increments bucket.attempted
    - id: step_2
      description: Flow completes, calls record_success(flow_name) if substantive
      file: runtime/orchestrator/silence_counter.py
      function: record_success
      input: flow_name (str)
      output: None
      side_effects: increments bucket.substantive
```

### Flow: Silence Evaluation

```yaml
flow:
  name: silence_evaluation
  purpose: Evaluate all tracked flows and route stimuli for degraded ones
  steps:
    - id: step_1
      description: Compute 5min ratio per flow
      file: runtime/orchestrator/silence_counter.py
      function: _compute_ratio
      input: flow_name, window_seconds
      output: (ratio, sample_size)
    - id: step_2
      description: Compute rolling baseline adjusted for pressure + circadian
      file: runtime/orchestrator/silence_counter.py
      function: _compute_baseline
      input: flow_name, pressure, circadian_factor
      output: adjusted_baseline
    - id: step_3
      description: Compare ratio to baseline, determine status
      file: runtime/orchestrator/silence_counter.py
      function: evaluate
      input: flow_name, pressure, circadian_factor
      output: status (GREEN/YELLOW/RED/CALIBRATING)
    - id: step_4
      description: If RED/YELLOW, route stimulus to infra actor
      file: runtime/orchestrator/silence_counter.py
      function: _route_stimulus
      input: flow_name, status, ratio, baseline
      output: None
      side_effects: inject_stimulus into best available infra actor
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `SILENCE_WINDOW_SECONDS` | env | 300 | Window for ratio computation (5 min) |
| `SILENCE_CALIBRATION_MIN` | env | 5 | Evaluations before rules activate |
| `SILENCE_BASELINE_MINUTES` | env | 60 | Rolling baseline window (1 hour) |
| `SILENCE_RED_THRESHOLD` | env | 0.5 | Ratio < baseline × this = RED |
| `SILENCE_YELLOW_THRESHOLD` | env | 0.8 | Ratio < baseline × this = YELLOW |

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Counter recording | Sync, in-thread | Called from dispatcher thread, GIL-safe |
| Sense evaluation | Sync, in-thread | Called from _run_loop, same thread as counters |
| Stimulus routing | Sync → async inject | inject_stimulus may spawn work, but the call itself is sync |

No locks needed. All counter access is from the single dispatcher thread.

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM 1: Counter Recording | `silence_counter.py:record_attempt()`, `record_success()` |
| ALGORITHM 2: Silence Evaluation | `silence_counter.py:evaluate()`, `_compute_ratio()`, `_compute_baseline()` |
| BEHAVIOR B1: Detection | `silence_counter.py:evaluate()` → status RED |
| BEHAVIOR B4: Fire-and-forget | `silence_counter.py:record_attempt()` try/except |
| BEHAVIOR B5: Auto-routing | `silence_counter.py:_route_stimulus()` → inject_stimulus(target="infra") |
| VALIDATION V2: No failures | `silence_counter.py:record_attempt()` exception swallowing |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
