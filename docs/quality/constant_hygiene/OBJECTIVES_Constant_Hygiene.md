# OBJECTIVES: Constant Hygiene — Code That Derives, Not Guesses

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
THIS:            OBJECTIVES_Constant_Hygiene.md
PATTERNS:        ./PATTERNS_Constant_Hygiene.md
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md

IMPL:            runtime/orchestrator/constant_hygiene.py
```

---

## Why This Exists

Constants are frozen assumptions. Every `THRESHOLD = 0.5` says "this value is correct forever." But the system evolves — citizens are added, ticks speed up, pressure changes, baselines shift. The constant stays the same while the world moves around it.

Mind Protocol's core principle: "If behavior needs a hardcoded rule, the architecture is wrong." Constants ARE hardcoded rules. This module makes them visible at the moment of creation — when the citizen still has the context to derive the value from system state instead.

---

## Priorities (Ranked)

### O1: Constants are detected at commit time via the graph

When a citizen commits code containing hardcoded constants, the system detects it by reading the commit Moment in L3 and analyzing the git diff. Detection happens through the graph — no hooks, no external systems.

### O2: Detection is felt, not reported

The finding enters the citizen's awareness through normal physics — a Concept node linked via OBSERVED_IN, imported on the next awareness tick, competing for WM entry via energy. Not a notification. Not a dashboard. A thought that arises naturally.

### O3: Behavior changes over time

The goal is not to catch every constant forever. The goal is that citizens internalize the pattern and start deriving values before the sense has to remind them. Success = the sense fires less often over time because citizens learned.

---

## Non-Objectives

- NOT a linter or CI gate — does not block commits
- NOT exhaustive — misses some constants, catches most. Precision > recall.
- NOT punitive — degraded weight is mild (-0.03). This is a nudge, not a punishment.
- NOT for physical/mathematical constants (pi, HTTP codes, byte sizes) — has safe exclusions

---

## Success Signals

- Constants per commit per citizen trends downward over 2 weeks
- Citizens reference mind.eliminate_constants in commit messages ("derived from X instead of hardcoding")
- The sense fires healthy more often than degraded (ratio improves over time)

## Results Required

| Objective | Result | Sense | Health |
|-----------|--------|-------|--------|
| O1 | R1: Caught at creation | sense:quality:constant_detection_latency | H1 |
| O2 | R2: Felt in awareness | sense:quality:concept_import_rate | H2 |
| O3 | R3: Trend improves | sense:quality:constant_trend | H3 |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
