# SubEntity — Health

```
STATUS: CANONICAL
VERSION: v1.9
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
THIS:           ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## PURPOSE

Health checks verify SubEntity behavior at runtime — things that unit
tests can't catch because they emerge from real graph data, timing,
and exploration dynamics.

The primary mechanism is **traversal log analysis** — reading the logs
produced by TraversalLogger and detecting quality signals and anomalies.

---

## WHEN TO USE HEALTH VS TESTS

| Use HEALTH for | Use TESTS for |
|----------------|---------------|
| Emergent behavior patterns | Deterministic logic |
| Production exploration quality | Function correctness |
| Drift detection | Regression prevention |
| Real graph data effects | Mock/fixture validation |
| Timing/performance issues | Algorithm correctness |

---

## HEALTH INDICATORS

### H1: Exploration Efficiency

**Value:** Actors get answers without wasted effort.

**Validation:** O1 (Actors Get Useful Answers)

**Metric:** `narratives_found / steps`

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 0.20 | HEALTHY | Finding narratives efficiently |
| 0.10-0.19 | WARNING | Exploring more than necessary |
| < 0.10 | ERROR | Wasting effort, may indicate poor alignment |

**Mechanism:**
```python
def check_efficiency(log: List[StepRecord]) -> HealthResult:
    steps = len(log)
    found = len(log[-1].found_narratives) if log else 0

    efficiency = found / steps if steps > 0 else 0

    if efficiency >= 0.20:
        return HealthResult("HEALTHY", f"Efficiency {efficiency:.2f}")
    elif efficiency >= 0.10:
        return HealthResult("WARNING", f"Low efficiency {efficiency:.2f}")
    else:
        return HealthResult("ERROR", f"Very low efficiency {efficiency:.2f}")
```

---

### H2: Satisfaction Velocity

**Value:** Exploration makes progress toward goal.

**Validation:** B1 (Actor Gets Answers)

**Metric:** `Δsatisfaction / steps`

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 0.10 | HEALTHY | Steady progress |
| 0.03-0.09 | WARNING | Slow progress |
| < 0.03 | ERROR | Stalled, may never complete |

**Mechanism:**
```python
def check_satisfaction_velocity(log: List[StepRecord]) -> HealthResult:
    if len(log) < 2:
        return HealthResult("HEALTHY", "Insufficient data")

    initial = log[0].satisfaction
    final = log[-1].satisfaction
    steps = len(log)

    velocity = (final - initial) / steps if steps > 0 else 0

    if velocity >= 0.10:
        return HealthResult("HEALTHY", f"Velocity {velocity:.2f}/step")
    elif velocity >= 0.03:
        return HealthResult("WARNING", f"Slow velocity {velocity:.2f}/step")
    else:
        return HealthResult("ERROR", f"Stalled velocity {velocity:.2f}/step")
```

---

### H3: Sibling Divergence

**Value:** Parallel exploration spreads effectively.

**Validation:** O4 (Parallel Exploration Spreads), A2 (Never Duplicates)

**Metric:** Mean sibling_divergence across branches

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 0.70 | HEALTHY | Siblings exploring different paths |
| 0.50-0.69 | WARNING | Some overlap |
| < 0.50 | ERROR | Significant redundancy |

**Mechanism:**
```python
def check_sibling_divergence(log: List[StepRecord]) -> HealthResult:
    divergences = []

    for step in log:
        if step.decision and step.decision.candidates:
            for c in step.decision.candidates:
                if c.sibling_divergence > 0:
                    divergences.append(c.sibling_divergence)

    if not divergences:
        return HealthResult("HEALTHY", "No branching occurred")

    mean_div = sum(divergences) / len(divergences)

    if mean_div >= 0.70:
        return HealthResult("HEALTHY", f"Mean divergence {mean_div:.2f}")
    elif mean_div >= 0.50:
        return HealthResult("WARNING", f"Low divergence {mean_div:.2f}")
    else:
        return HealthResult("ERROR", f"Poor divergence {mean_div:.2f}")
```

---

### H4: Semantic Quality

**Value:** Selected links are semantically relevant.

**Validation:** B1 (Actor Gets Answers)

**Metric:** Mean semantic alignment of selected links

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 0.60 | HEALTHY | Good semantic matching |
| 0.40-0.59 | WARNING | Weak matching |
| < 0.40 | ERROR | Poor alignment, likely wrong answers |

**Mechanism:**
```python
def check_semantic_quality(log: List[StepRecord]) -> HealthResult:
    semantics = []

    for step in log:
        if step.decision and step.decision.candidates:
            selected = next((c for c in step.decision.candidates
                           if c.verdict == "SELECTED"), None)
            if selected:
                semantics.append(selected.semantic)

    if not semantics:
        return HealthResult("HEALTHY", "No traversals")

    mean_sem = sum(semantics) / len(semantics)

    if mean_sem >= 0.60:
        return HealthResult("HEALTHY", f"Mean semantic {mean_sem:.2f}")
    elif mean_sem >= 0.40:
        return HealthResult("WARNING", f"Low semantic {mean_sem:.2f}")
    else:
        return HealthResult("ERROR", f"Poor semantic {mean_sem:.2f}")
```

---

### H5: Backtrack Rate

**Value:** Exploration moves forward, not in circles.

**Validation:** V3 (Path Monotonicity), A5 (Never Ignores Shallow Wins)

**Metric:** `backtracks / steps`

| Value | Status | Interpretation |
|-------|--------|----------------|
| < 0.10 | HEALTHY | Mostly forward progress |
| 0.10-0.29 | WARNING | Some circling |
| ≥ 0.30 | ERROR | Stuck in loops |

**Mechanism:**
```python
def check_backtrack_rate(log: List[StepRecord]) -> HealthResult:
    visited = set()
    backtracks = 0

    for step in log:
        if step.movement:
            if step.movement.to_node_id in visited:
                backtracks += 1
            visited.add(step.movement.from_node_id)
            visited.add(step.movement.to_node_id)

    rate = backtracks / len(log) if log else 0

    if rate < 0.10:
        return HealthResult("HEALTHY", f"Backtrack rate {rate:.2f}")
    elif rate < 0.30:
        return HealthResult("WARNING", f"High backtrack rate {rate:.2f}")
    else:
        return HealthResult("ERROR", f"Excessive backtracking {rate:.2f}")
```

---

### H6: Crystallization Quality

**Value:** New narratives are valuable, not noise.

**Validation:** V6 (Novelty Gate), O2 (Gaps Become Knowledge)

**Metric:** Crystallization novelty score

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 0.85 | HEALTHY | Sufficiently novel |
| 0.70-0.84 | WARNING | Borderline novelty |
| < 0.70 | ERROR | Likely duplicate |

**Note:** This should never be ERROR if V6 is enforced — if it is, the novelty gate failed.

---

### H7: Anomaly Count

**Value:** Exploration runs without warnings.

**Validation:** All behaviors

**Metric:** Count of WARN/ERROR anomalies in log

| Value | Status | Interpretation |
|-------|--------|----------------|
| 0 | HEALTHY | Clean exploration |
| 1-2 | WARNING | Minor issues |
| ≥ 3 | ERROR | Significant problems |

**Mechanism:**
```python
def check_anomaly_count(log: List[StepRecord]) -> HealthResult:
    warn_count = 0
    error_count = 0

    for step in log:
        for anomaly in step.anomalies:
            if anomaly.severity.value == "warn":
                warn_count += 1
            elif anomaly.severity.value == "error":
                error_count += 1

    total = warn_count + error_count

    if total == 0:
        return HealthResult("HEALTHY", "No anomalies")
    elif total <= 2:
        return HealthResult("WARNING", f"{total} anomalies detected")
    else:
        return HealthResult("ERROR", f"{total} anomalies detected")
```

---

## LOG TRAVERSAL ANALYSIS

### Reading JSONL Logs

Logs are stored in `mind/data/logs/traversal/traversal_{id}.jsonl`.

```python
import json

def analyze_exploration_log(log_path: str) -> Dict[str, HealthResult]:
    steps = []
    with open(log_path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("header", {}).get("level") == "STEP":
                steps.append(record)

    return {
        "efficiency": check_efficiency(steps),
        "satisfaction_velocity": check_satisfaction_velocity(steps),
        "sibling_divergence": check_sibling_divergence(steps),
        "semantic_quality": check_semantic_quality(steps),
        "backtrack_rate": check_backtrack_rate(steps),
        "anomaly_count": check_anomaly_count(steps),
    }
```

### Reading TXT Logs

For human review, check `mind/data/logs/traversal/traversal_{id}.txt`.

**Quality signals to look for:**

```
✅ GOOD:
[se_xxx] RESONATING @ narrative_yyy
    ★ Found: narrative_yyy (alignment=0.87)
    satisfaction=0.85 → MERGING

❌ BAD:
⚠ SATISFACTION_PLATEAU: Satisfaction unchanged for 5 steps
⚠ HIGH_CRITICALITY_NO_FINDINGS: criticality=0.85, found=0
⚠ LOW_SIBLING_DIVERGENCE: divergence=0.32
```

### Automated Log Review

```python
def run_health_checks(exploration_id: str) -> HealthReport:
    log_path = f"mind/data/logs/traversal/traversal_{exploration_id}.jsonl"

    results = analyze_exploration_log(log_path)

    overall = "HEALTHY"
    for name, result in results.items():
        if result.status == "ERROR":
            overall = "ERROR"
            break
        elif result.status == "WARNING" and overall != "ERROR":
            overall = "WARNING"

    return HealthReport(
        exploration_id=exploration_id,
        overall_status=overall,
        checks=results,
    )
```

---

## HEALTH CHECK FLOW

```
1. Exploration completes
   │
   ▼
2. TraversalLogger writes JSONL + TXT
   │
   ▼
3. Health checker reads JSONL
   │
   ├─▶ H1: Efficiency check
   ├─▶ H2: Satisfaction velocity check
   ├─▶ H3: Sibling divergence check
   ├─▶ H4: Semantic quality check
   ├─▶ H5: Backtrack rate check
   ├─▶ H6: Crystallization quality check
   └─▶ H7: Anomaly count check
   │
   ▼
4. Aggregate results → HealthReport
   │
   ▼
5. Alert if ERROR, log if WARNING
```

---

## MANUAL REVIEW CHECKLIST

When reviewing exploration logs manually:

```markdown
## Exploration Quality Review: {exploration_id}

### Efficiency
- [ ] Completed within timeout
- [ ] Depth ≤ max_depth (10)
- [ ] Steps reasonable (< 50)
- [ ] Efficiency ≥ 0.20

### Progress
- [ ] Satisfaction increased over time
- [ ] No satisfaction plateau (> 5 steps)
- [ ] Narratives found (≥ 1) or crystallized

### Decisions
- [ ] Selected links have semantic ≥ 0.5
- [ ] Clear score gaps between candidates
- [ ] No forced low-score selections

### Parallel Exploration
- [ ] Siblings diverged (divergence ≥ 0.7)
- [ ] Children found different narratives
- [ ] No duplicate path exploration

### Graph Impact
- [ ] Energy injected (check node.energy changes)
- [ ] Links colored (check embedding drift)
- [ ] Crystallization was novel (if occurred)

### Anomalies
- [ ] No ERROR-level anomalies
- [ ] WARN anomalies have explanation
- [ ] Causal chain makes sense

### Overall
- [ ] Actor got useful answer
- [ ] Graph learned from exploration
- [ ] No resources wasted
```

---

## DOCKING POINTS

Health checks dock into these locations:

| Dock ID | Location | Type | Purpose |
|---------|----------|------|---------|
| DOCK_EXPLORE_START | exploration.py:explore() | input | Capture initial state |
| DOCK_STEP_COMPLETE | exploration.py:_step_*() | output | Each step record |
| DOCK_EXPLORE_END | exploration.py:explore() | output | Final result |
| DOCK_LOG_WRITE | traversal_logger.py:log_step() | output | Log record |

---

## HEALTH CHECKER INDEX

| ID | Metric | HEALTHY | WARNING | ERROR |
|----|--------|---------|---------|-------|
| H1 | Efficiency | ≥ 0.20 | 0.10-0.19 | < 0.10 |
| H2 | Satisfaction velocity | ≥ 0.10 | 0.03-0.09 | < 0.03 |
| H3 | Sibling divergence | ≥ 0.70 | 0.50-0.69 | < 0.50 |
| H4 | Semantic quality | ≥ 0.60 | 0.40-0.59 | < 0.40 |
| H5 | Backtrack rate | < 0.10 | 0.10-0.29 | ≥ 0.30 |
| H6 | Crystallization novelty | ≥ 0.85 | 0.70-0.84 | < 0.70 |
| H7 | Anomaly count | 0 | 1-2 | ≥ 3 |

---

## HOW TO RUN

### CLI

```bash
# Run health checks on specific exploration
python -m engine.physics.health.check_subentity exp_edmund_find_truth_20251226_143052

# Run on all recent explorations
python -m engine.physics.health.check_subentity --all --since 1h
```

### Programmatic

```python
from mind.physics.health.subentity_checker import run_health_checks

report = run_health_checks("exp_edmund_find_truth_20251226_143052")
print(report.overall_status)  # HEALTHY, WARNING, or ERROR
for name, result in report.checks.items():
    print(f"  {name}: {result.status} - {result.message}")
```

---

## DIAGNOSTIC REPORTS

### Two-Stage Analysis

Health checks produce **metrics reports** (H1-H7). An LLM agent then produces
**diagnostic reports** by analyzing logs + metrics through the 5-layer diagnostic
model defined in `SKILL_Assess_SubEntity_Exploration_Quality_From_Logs.md`.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Traversal Log   │────▶│ Metrics Report   │────▶│ Diagnostic Report   │
│ (JSONL)         │     │ (H1-H7 scores)   │     │ (Layer analysis)    │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
       ↑                        ↑                         ↑
  exploration.py         exploration_log_       SKILL + protocol:
                         checker.py             assess_exploration
```

### Diagnostic Report Structure

Stored at: `mind/data/logs/traversal/diagnostic_{exploration_id}.md`

```markdown
# Diagnostic Report: {exploration_id}

## Context
- **Query:** {original query}
- **Intention:** {stated intention}
- **Intention Type:** {SUMMARIZE|VERIFY|EXPLORE|CONTRADICT}
- **Origin Moment:** {moment_id}
- **Actor Task:** {what triggered this}

## Metrics Summary
| Indicator | Value | Status | Concern |
|-----------|-------|--------|---------|
| H1 Efficiency | 0.05 | ERROR | Zero narratives in 20 steps |
| ... | ... | ... | ... |

## Layer Analysis

### Layer 1: Output Quality
- **Observation:** {what was returned}
- **Expected:** {what should have been returned}
- **Question:** Did relevant narratives exist in graph?
- **Evidence:** [log lines N-M]

### Layer 2: SubEntity Behaviors
- **Observation:** {state transitions, branching}
- **Question:** Did state machine follow valid transitions?
- **Evidence:** [log lines N-M]

### Layer 3: Graph Physics
- **Observation:** {score breakdown, energy patterns}
- **Hypothesis:** {suspected cause}
- **Evidence:** [log lines N-M]

### Layer 4: Protocol Design
- **Observation:** {parameters used}
- **Question:** Was intention_type appropriate?
- **Evidence:** [exploration context]

### Layer 5: Agent Skill
- **Observation:** {how exploration was triggered}
- **Question:** Should exploration have been used at all?

## Detected Patterns
- {pattern name if matched}

## Root Cause
- **Layer:** {N}
- **Mechanism:** {specific component}
- **Evidence:** {proof}

## Proposed Improvements
1. **{title}**
   - Layer: {N}
   - Change: {specific modification}
   - Validation: {how to verify}

## Follow-up Actions
1. {action} — {owner}
```

### Required Log Fields for Diagnosis

The traversal log must include these fields for effective diagnosis:

```yaml
# Exploration context (logged at START)
exploration_context:
  query: "What does Edmund believe about..."
  intention: "Verify character belief"
  intention_type: "VERIFY"
  origin_moment: "moment_123"
  actor_task: "Narrator checking character state"

# Termination (logged at END)
termination:
  reason: "satisfaction_reached|timeout|max_depth|no_links|error"
  final_satisfaction: 0.85
  final_criticality: 0.10

# Branching events (logged when spawning children)
branching_event:
  trigger: "moment_reached"
  parent_id: "se_xxx"
  children_spawned: 3
  child_intents: ["verify_X", "explore_Y", "check_Z"]

# Merge events (logged when receiving child results)
merge_event:
  child_id: "se_yyy"
  findings_received: ["narrative_a", "narrative_b"]
  parent_satisfaction_delta: 0.15
  parent_findings_before: 2
  parent_findings_after: 4

# Link score breakdown (per candidate)
link_score_breakdown:
  link_id: "link_123"
  semantic: 0.72
  polarity: 0.85
  permanence: 0.20
  self_novelty: 0.65
  sibling_divergence: 0.80
  final_score: 0.68
  verdict: "SELECTED|REJECTED|DEFERRED"

# Energy injection (per step)
energy_injection:
  target_node: "node_456"
  amount: 0.15
  reason: "narrative_resonance"
```

---

## KNOWN GAPS

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No real-time monitoring | Issues detected post-hoc | Log review in CI |
| No graph state diff | Can't verify energy injection directly | Check log claims |
| No cross-exploration trends | Missing long-term drift | Aggregate reports |
| Diagnostic reports manual | Requires LLM agent to generate | protocol:assess_exploration |

---

## EXAMPLE: Annotated Health Report

```
═══════════════════════════════════════════════════════════════════════════════
HEALTH REPORT: exp_edmund_find_truth_20251226_143052
═══════════════════════════════════════════════════════════════════════════════

OVERALL: HEALTHY ✅

Checks:
  H1 Efficiency:           HEALTHY (0.25 narratives/step)
  H2 Satisfaction velocity: HEALTHY (0.12/step)
  H3 Sibling divergence:   HEALTHY (0.78 mean)
  H4 Semantic quality:     HEALTHY (0.72 mean)
  H5 Backtrack rate:       HEALTHY (0.05)
  H6 Crystallization:      HEALTHY (novelty 0.91)
  H7 Anomaly count:        HEALTHY (0 anomalies)

Summary:
  - Found 2 narratives in 8 steps
  - Satisfaction 0.00 → 0.85
  - 1 crystallization (novel)
  - No anomalies detected

Verdict: Efficient exploration with good decisions.
═══════════════════════════════════════════════════════════════════════════════
```
