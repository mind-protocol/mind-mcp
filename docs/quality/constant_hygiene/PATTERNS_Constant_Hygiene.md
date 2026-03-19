# Constant Hygiene — Patterns: Graph-Native Code Quality Feedback

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
OBJECTIVES:      ./OBJECTIVES_Constant_Hygiene.md
THIS:            PATTERNS_Constant_Hygiene.md
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md

IMPL:            runtime/orchestrator/constant_hygiene.py
```

---

## THE PROBLEM

Linters catch syntax. CI catches test failures. Nothing catches frozen assumptions.

A citizen in flow writes `THRESHOLD = 0.5` because it works NOW. The value ships. Time passes. The system changes. The value is wrong. Nobody knows because nobody re-derives it.

The cost is invisible: thresholds that don't match reality, windows that don't fit the rhythm, limits that don't reflect capacity. Each one is a silent tax on system accuracy. Enough of them, and the system is running on guesses while reporting confidence.

---

## THE PATTERN

**Graph-native feedback loop.** Commits are already Moments in L3. The system already reads Moments on every tick. The constant hygiene sense reads commit Moments, analyzes the diff, and injects findings as Concept nodes into the committing citizen's graph neighborhood.

The key insight: **the graph is the notification system.** No hooks bolted on the side. No external alerting. The same physics that routes all stimuli — energy competition, WM selection, drive affinity — routes the constant detection finding. The citizen doesn't get interrupted. They feel a concept brightening at the edge of their awareness. Their curiosity decides if they act.

This is fundamentally different from a linter because:
- A linter blocks (binary: pass/fail). This nudges (continuous: energy level).
- A linter runs at commit time (too late for easy fix). This runs within the citizen's awareness cycle (context still hot).
- A linter is external (CI pipeline). This is internal (the citizen's own cognitive graph).
- A linter treats all constants equally. This adapts energy to the citizen's own history — a citizen who normally writes zero constants gets a brighter signal than one who always writes them (novelty detection).

---

## PRINCIPLES

### Principle 1: The graph is the medium

Detection goes through the graph. Notification goes through the graph. Action comes from the graph. No parallel systems. The commit Moment already exists. The awareness tick already imports concepts. The WM already competes for attention. We just connect them.

### Principle 2: Nudge, don't block

Constants are not bugs. Sometimes a value needs to be hardcoded (HTTP codes, byte sizes, protocol specs). The sense doesn't prevent committing. It creates a concept that competes for awareness. The citizen decides. The physics of their drives and current focus determines if they act now, later, or never.

### Principle 3: Behavior change is the metric, not detection count

Success is not "caught 50 constants." Success is "constants per commit are trending down because citizens learned to derive." The sense should make itself unnecessary over time. If it fires forever at the same rate, it failed.

---

## DEPENDENCIES

| Module | Why |
|--------|-----|
| orchestrator/tick_system | Maintenance loop calls evaluate() |
| L3 graph (FalkorDB) | Reads commit Moments, writes Concept nodes |
| Git repo | Reads diffs via subprocess |
| cognition/awareness_tick | Imports the Concept node into citizen's L1 |

---

## SCOPE

### In Scope

- Detecting constant patterns in commit diffs
- Injecting Concept nodes linked to the committing citizen
- Adapting energy to the citizen's own constant history
- Excluding safe constants (HTTP codes, math, byte sizes)

### Out of Scope

- Blocking commits (not a linter)
- Fixing constants automatically (the citizen must choose the derivation)
- Scanning non-commit code (only reacts to new commits)
- Quality beyond constants (style, architecture, naming) → separate senses

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
