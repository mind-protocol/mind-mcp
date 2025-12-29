# Tempo Controller — Implementation: Code Architecture and Structure

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Tempo.md
BEHAVIORS:      ./BEHAVIORS_Tempo.md
ALGORITHM:      ./ALGORITHM_Tempo_Controller.md
VALIDATION:     ./VALIDATION_Tempo.md
THIS:           IMPLEMENTATION_Tempo.md
HEALTH:         ./HEALTH_Tempo.md
SYNC:           ./SYNC_Tempo.md

IMPL:           runtime/infrastructure/tempo/tempo_controller.py (planned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/infrastructure/tempo/__init__.py         # Exports TempoController
runtime/infrastructure/tempo/tempo_controller.py # Main loop and speed management
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/infrastructure/tempo/tempo_controller.py` | Main loop, pacing, tick calls | `TempoController` | ~300 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Event-driven loop with scheduled ticks.

**Why this pattern:** The loop must be deterministic and decoupled from input
latency while coordinating physics and canon scans.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Scheduler | `runtime/infrastructure/tempo/tempo_controller.py` (TempoController.run) | pacing and timing |
| Guard | `runtime/infrastructure/tempo/tempo_controller.py` (_tick_interval) | enforce speed mapping |

### Anti-Patterns to Avoid

- **Blocking Loop:** never wait on narrator output or long I/O.
- **God Object:** avoid placing physics or canon logic inside tempo.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Tempo loop | pacing, ticks | physics, canon | `GraphTick.run()` + `record_to_canon()` |

---

## SCHEMA

### TempoState

```yaml
TempoState:
  required:
    - speed: enum          # pause | 1x | 2x | 3x
    - running: bool        # loop control
    - tick_count: int      # monotonically increasing
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `TempoController.run()` | `runtime/infrastructure/tempo/tempo_controller.py` | `asyncio.create_task()` |
| `TempoController.set_speed()` | `runtime/infrastructure/tempo/tempo_controller.py` | `/api/tempo/speed` |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### tempo_tick: pacing → physics → canon

The tempo tick is the primary flow that advances the world state. It is a
cross-boundary flow because it invokes physics and canon subsystems.

```yaml
flow:
  name: tempo_tick
  purpose: advance world state at a controlled cadence
  scope: speed state → physics tick → canon surfacing
  steps:
    - id: step_1_interval
      description: compute tick interval from speed mode
      file: runtime/infrastructure/tempo/tempo_controller.py
      function: _tick_interval
      input: speed
      output: float seconds
      trigger: loop iteration
      side_effects: none
    - id: step_2_physics
      description: run physics tick and collect flips
      file: runtime/physics/tick.py
      function: GraphTick.run
      input: elapsed_minutes
      output: TickResult
      trigger: TempoController.run
      side_effects: graph writes
    - id: step_3_canon
      description: scan and record surfaced moments
      file: runtime/infrastructure/canon/canon_holder.py
      function: record_to_canon
      input: possible moments
      output: canon writes
      trigger: TempoController.run
      side_effects: graph writes + SSE
  docking_points:
    guidance:
      include_when: transformative or user-visible
      omit_when: trivial pass-through
      selection_notes: tempo_tick is the primary pacing boundary
    available:
      - id: tempo_tick_in
        type: scheduler
        direction: input
        file: runtime/infrastructure/tempo/tempo_controller.py
        function: run
        trigger: asyncio loop
        payload: speed, running
        async_hook: not_applicable
        needs: none
        notes: entry point to pacing
      - id: canon_broadcast
        type: stream
        direction: output
        file: runtime/infrastructure/canon/canon_holder.py
        function: record_to_canon
        trigger: tempo tick
        payload: completed moment
        async_hook: required
        needs: add watcher
        notes: player-visible output
    health_recommended:
      - dock_id: tempo_tick_in
        reason: ensures cadence matches speed
      - dock_id: canon_broadcast
        reason: verifies surfacing and broadcast
```

---

## LOGIC CHAINS

### LC1: Cadence to Surfacing

**Purpose:** Show how speed changes affect surfacing cadence.

```
speed change
  → TempoController.set_speed()
    → TempoController.run()
      → GraphTick.run()
        → CanonHolder.record_to_canon()
```

**Data transformation:**
- Input: `speed` — desired pacing
- Output: `completed moments` — surfaced canon events

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/infrastructure/tempo/tempo_controller.py
    └── imports → runtime/physics/tick.py
    └── imports → runtime/infrastructure/canon/canon_holder.py
```

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| speed | TempoController speed | instance | until stop |
| running | TempoController running | instance | until stop |
| tick_count | TempoController tick_count | instance | monotonic |

### State Transitions

```
running=false ──start──▶ running=true ──stop──▶ running=false
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. TempoController instantiated
2. speed set (default 1x)
3. run() scheduled as asyncio task
```

### Main Loop / Request Cycle

```
1. resolve interval
2. sleep
3. run physics
4. run canon scan
```

### Shutdown

```
1. running=false
2. loop exits cleanly
```

---

## CONCURRENCY MODEL

Async loop driven by `asyncio`. One loop per playthrough.

| Component | Model | Notes |
|-----------|-------|-------|
| TempoController | async | single task per playthrough |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `speed` | tempo state | 1x | tick cadence selector |

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 1 | `runtime/infrastructure/tempo/tempo_controller.py` (_tick_interval) |
| ALGORITHM Step 3 | `runtime/physics/tick.py` (GraphTick.run) |
| ALGORITHM Step 4 | `runtime/infrastructure/canon/canon_holder.py` (record_to_canon) |

---

## MARKERS

### Missing Implementation

<!-- @mind:todo Add `runtime/infrastructure/api/tempo.py` endpoints. -->

### Questions

<!-- @mind:escalation
title: "Should tempo state persist across restarts?"
priority: 5
response:
  status: resolved
  choice: "Partial persist"
  behavior: "Current tick: always persist. Speed setting: always reset to x1 on restart. Paused state: reset to running."
  notes: "2025-12-23: Decided by Nicolas."
-->
