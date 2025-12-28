# Tempo Controller — Patterns: Pacing the Main Loop

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
THIS:            PATTERNS_Tempo.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Tempo.md
ALGORITHM:       ./ALGORITHM_Tempo_Controller.md
VALIDATION:      ./VALIDATION_Tempo.md
HEALTH:          ./HEALTH_Tempo.md
SYNC:            ./SYNC_Tempo.md

IMPL:            mind/infrastructure/tempo/tempo_controller.py (planned)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: tempo controller"
3. Run tests: `mind validate`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_*.md: "Implementation changed, docs need: tempo docs update"
3. Run tests: `mind validate`

---

## THE PROBLEM

The system needs a stable pacing layer that advances time, runs physics, and
surfaces canon without blocking on LLM output or conflating user input with
world simulation. Without an explicit tempo loop, ticks become ad hoc, latency
spikes leak into gameplay, and canon surfacing loses determinism.

---

## THE PATTERN

Introduce a **Tempo Controller**: a dedicated runtime loop that owns time
progression and surfacing cadence. It ticks at a speed-controlled interval,
invokes physics, and triggers canon surfacing independently of narrator
execution.

---

## PRINCIPLES

### Principle 1: Deterministic Cadence

Ticks are governed by speed mode, not user input. This keeps pacing stable and
predictable.

### Principle 2: Non-Blocking Loop

Tempo must never wait for narrator output. It advances physics and canonization
based on time, not generation latency.

### Principle 3: Separation of Concerns

Tempo controls *when* the world advances; physics and narrators control *what*
changes. The loop never generates content.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Tempo state | OTHER | speed, running flag, tick counters |
| Physics output | OTHER | flip results for downstream handlers |
| Canon queue | OTHER | surfaced moments ready to broadcast |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind/physics/tick.py` | Runs physics updates per tick |
| `mind/infrastructure/canon/` | Records surfaced moments |
| `mind/infrastructure/api/tempo.py` | Speed/stop/start controls |

---

## INSPIRATIONS

- Game loops that decouple simulation ticks from input events.
- Event-driven schedulers with explicit pacing authority.

---

## SCOPE

### In Scope

- Tick cadence and speed modes.
- Triggering physics and canon scans per tick.
- Backpressure handling to avoid overload.

### Out of Scope

- Content generation (Narrator, World Runner).
- Graph mutations beyond invoking physics and canon.
- UI rendering or SSE transport details.

---

## MARKERS

<!-- @mind:todo Define exact speed to interval mapping for v1. -->
<!-- @mind:todo Decide whether tempo state persists across restarts. -->
<!-- @mind:proposition Adaptive pacing based on graph load or queue size. -->
<!-- @mind:escalation
title: "Should pauses flush pending surfacing or freeze it?"
priority: 5
response:
  status: resolved
  choice: "Freeze"
  behavior: "Pause = 0 ticks. No graph time passes, queue frozen as-is, resumes exactly where left off."
  notes: "2025-12-23: Decided by Nicolas."
-->
