# Self-Improvement — Patterns

```
STATUS: DESIGNING
VERSION: v0.1
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SelfImprovement.md
THIS:           ./PATTERNS_SelfImprovement.md
BEHAVIORS:      ./BEHAVIORS_SelfImprovement.md
ALGORITHM:      ./ALGORITHM_SelfImprovement.md
VALIDATION:     ./VALIDATION_SelfImprovement.md
IMPLEMENTATION: ./IMPLEMENTATION_SelfImprovement.md
HEALTH:         ./HEALTH_SelfImprovement.md
SYNC:           ./SYNC_SelfImprovement.md
```

---

## DESIGN PHILOSOPHY

### The System Explores Itself

The self-improvement loop is structurally identical to SubEntity exploration:

```
SubEntity explores graph          │  Self-Improvement explores system
─────────────────────────────────┼────────────────────────────────────
Actor spawns exploration          │  Trigger spawns improvement cycle
Query = what to find              │  Signal = what went wrong
Intention = why finding           │  Objective = what value to improve
Traversal = following links       │  Observation = collecting signals
Scoring = evaluating paths        │  Diagnosis = evaluating patterns
Branching = parallel exploration  │  Proposal = multiple improvement options
Crystallization = new knowledge   │  Deployment = new system behavior
Energy injection = reinforcement  │  Learning = pattern memory
```

This is not metaphor — the improvement loop IS consciousness exploring its
own behavior space.

---

## CORE PRINCIPLES

### P1: Signal Over Noise

**Pattern:** Only collect signals that could lead to actionable improvements.

**Why:** Observation has overhead. Collecting everything creates noise that
obscures patterns and wastes resources.

**Application:**
- Define signal sources explicitly
- Filter at collection, not analysis
- Prioritize signals tied to objectives
- Drop signals that never lead to improvements

**Anti-pattern:** Logging everything "in case it's useful later."

---

### P2: Pattern Over Instance

**Pattern:** Diagnose recurring patterns, not individual failures.

**Why:** Individual failures may be noise. Patterns indicate systemic issues
worth fixing. Fixing patterns has compound value.

**Application:**
- Aggregate signals over time windows
- Require N occurrences before pattern status
- Track pattern recurrence after fixes
- Weight patterns by impact, not frequency

**Anti-pattern:** Creating improvement proposals for every anomaly.

---

### P3: Layer Attribution

**Pattern:** Every diagnosis must attribute the root cause to a specific layer.

**Why:** Treating symptoms at the wrong layer wastes effort and creates
false confidence. A physics problem fixed by skill changes will recur.

**Layers (top to bottom):**
```
5. Skill       — Agent context and guidance
4. Protocol    — Procedure and parameters
3. Physics     — Scoring, energy, embeddings
2. Behavior    — State machine, decisions
1. Output      — What actor receives
0. Data        — Graph content
```

**Application:**
- Diagnose from symptom layer downward
- Stop at first layer that explains the pattern
- Fix at root layer, not symptom layer
- Verify fix by checking symptom disappears

**Anti-pattern:** Fixing output when physics is broken.

---

### P4: Typed Proposals

**Pattern:** Every improvement proposal is a specific, typed change.

**Why:** Vague proposals ("make it better") can't be validated, deployed,
or rolled back. Typed proposals are tractable.

**Types:**
```yaml
constant_tune:    # Adjust thresholds, weights, multipliers
formula_change:   # Modify computation logic
behavior_fix:     # Change state machine
protocol_update:  # Modify procedure steps
skill_improve:    # Add context or guidance
graph_content:    # Add/fix nodes, links, narratives
```

**Application:**
- Every proposal has exactly one type
- Type determines validation approach
- Type determines approval requirements
- Type determines rollback mechanism

**Anti-pattern:** "General improvement to exploration quality."

---

### P5: Validation Before Deployment

**Pattern:** Every change is validated before production deployment.

**Why:** A bad improvement is worse than no improvement. Production stability
is non-negotiable.

**Validation modes:**
```
Unit test     — Isolated logic verification
Shadow mode   — Run alongside production, compare outputs
Canary        — Deploy to subset, monitor for degradation
A/B test      — Randomized comparison with statistical significance
```

**Application:**
- Type determines minimum validation mode
- Higher risk requires more validation
- Validation failure blocks deployment
- Validation results are recorded

**Anti-pattern:** "It works in testing" without production validation.

---

### P6: Tiered Autonomy

**Pattern:** Autonomy level matches risk level.

**Why:** Low-risk changes shouldn't wait for humans. High-risk changes
shouldn't deploy without human oversight.

**Tiers:**
```
AUTO:         constant_tune with low impact, validation passed
NOTIFY:       auto-deploy but notify human after
APPROVE:      queue for human approval before deploy
REQUIRE:      block until explicit human approval
```

**Application:**
- Type + risk + impact determines tier
- Auto tier has strict bounds
- Humans can always override
- Audit trail for all tiers

**Anti-pattern:** Same approval process for all changes.

---

### P7: Compound Learning

**Pattern:** Each improvement creates knowledge that accelerates future improvements.

**Why:** Improvement velocity should increase over time, not stay constant.
The system should recognize patterns it has seen before.

**Learning surfaces:**
```
Pattern library   — Known patterns with proven fixes
Diagnosis cache   — Layer attribution for pattern types
Proposal templates — Typed proposals for common patterns
Validation history — What validation approaches worked
```

**Application:**
- Record pattern → diagnosis → fix → outcome
- Reuse successful fixes for similar patterns
- Build pattern recognition from history
- Surface confidence based on prior success

**Anti-pattern:** Diagnosing from scratch every time.

---

### P8: Graceful Degradation

**Pattern:** Improvement failures degrade gracefully, never catastrophically.

**Why:** The improvement system itself can fail. Failures must not cascade
into production failures.

**Application:**
- Observation failure → continue without signals (degrade detection)
- Diagnosis failure → surface uncertainty (degrade proposals)
- Validation failure → block deployment (protect production)
- Deployment failure → automatic rollback (restore prior state)

**Anti-pattern:** Improvement system failure takes down production.

---

### P9: Observable Improvement

**Pattern:** Every improvement must be observable in metrics.

**Why:** Unobservable improvements can't be verified. They might not work.
They definitely can't compound.

**Application:**
- Define success metric before deployment
- Measure baseline before change
- Compare to baseline after change
- Record outcome for learning

**Anti-pattern:** "It should help" without measurement.

---

### P10: Bounded Meta-Recursion

**Pattern:** Self-improvement can improve itself, but with strict bounds.

**Why:** Unbounded meta-improvement leads to infinite loops and resource
exhaustion. But meta-improvement is valuable.

**Bounds:**
```
- Meta-improvement cycles limited to 1 per day
- Meta-changes require REQUIRE tier approval
- Meta-observation is sampled, not complete
- Meta-diagnosis uses simpler heuristics
```

**Application:**
- Self-improvement module has its own health checks
- Improvements to self-improvement are high-risk
- Meta-learning is slower and more conservative
- Humans approve all meta-changes

**Anti-pattern:** Self-improvement infinitely tuning itself.

---

## SCOPE

### In Scope

| Component | Improvable Aspects |
|-----------|-------------------|
| Physics | Constants, formulas, thresholds |
| SubEntity | State machine, scoring, energy |
| Protocols | Steps, parameters, gates |
| Skills | Context, guidance, gates |
| Agents | Tool selection, skill loading |
| Graph ops | Query optimization, caching |

### Out of Scope

| Component | Why |
|-----------|-----|
| Core architecture | Too fundamental, requires human design |
| External APIs | Not under system control |
| User interface | Requires human judgment |
| Security policies | Requires explicit human approval |
| Data retention | Legal/compliance, not algorithmic |

---

## ARCHITECTURE PRINCIPLES

### Single Loop, Multiple Layers

One improvement loop operates across all layers:

```
┌─────────────────────────────────────────────────────────┐
│                  IMPROVEMENT LOOP                        │
│                                                          │
│  OBSERVE ──▶ DIAGNOSE ──▶ PROPOSE ──▶ VALIDATE ──▶ DEPLOY│
│                                                          │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐    │
│  │ Skill   │Protocol │ Physics │Behavior │ Output  │    │
│  │ signals │ signals │ signals │ signals │ signals │    │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘    │
└─────────────────────────────────────────────────────────┘
```

Not separate loops per layer — unified observation with layer-attributed diagnosis.

### Event-Driven Triggers

Improvement cycles are triggered by events, not schedules:

```yaml
triggers:
  threshold_breach:
    signal: Health metric crosses threshold
    urgency: high

  pattern_detected:
    signal: N occurrences of same anomaly
    urgency: medium

  periodic:
    signal: Time-based (daily, weekly)
    urgency: low

  human_request:
    signal: Explicit improvement request
    urgency: varies
```

### Proposal Queue

Proposals queue for validation and approval:

```
High urgency ──▶ Front of queue
Low risk ──▶ Auto-validate, auto-deploy
High risk ──▶ Wait for human approval
Conflicting ──▶ Merge or prioritize
```

---

## RELATIONSHIPS TO OTHER MODULES

| Module | Relationship |
|--------|--------------|
| SubEntity | Provides exploration signals; receives physics improvements |
| Physics | Provides scoring/energy signals; receives constant/formula changes |
| Protocols | Provides execution signals; receives step/parameter updates |
| Skills | Provides guidance signals; receives context improvements |
| Doctor | Provides health signals; may receive check improvements |
| Graph | Provides content signals; receives content fixes |

---

## DESIGN DECISIONS

### D1: Why unified loop, not per-layer loops?

Per-layer loops create coordination problems. A physics problem might be
masked by a skill workaround. Unified observation sees cross-layer patterns.

### D2: Why event-driven, not scheduled?

Scheduled improvement wastes resources when nothing is wrong and reacts
slowly when something is. Event-driven responds to actual need.

### D3: Why typed proposals?

Untyped proposals ("improve exploration") can't be validated, deployed,
or rolled back. Types make improvement tractable.

### D4: Why tiered autonomy?

Full autonomy is dangerous (no human oversight). No autonomy is slow
(humans bottleneck everything). Tiered matches autonomy to risk.

### D5: Why pattern over instance?

Individual failures are often noise. Patterns indicate systemic issues.
Fixing patterns has compound value; fixing instances is whack-a-mole.
