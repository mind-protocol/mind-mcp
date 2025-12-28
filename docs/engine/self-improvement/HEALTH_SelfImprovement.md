# Self-Improvement — Health

```
STATUS: DESIGNING
VERSION: v0.1
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SelfImprovement.md
PATTERNS:       ./PATTERNS_SelfImprovement.md
BEHAVIORS:      ./BEHAVIORS_SelfImprovement.md
ALGORITHM:      ./ALGORITHM_SelfImprovement.md
VALIDATION:     ./VALIDATION_SelfImprovement.md
IMPLEMENTATION: ./IMPLEMENTATION_SelfImprovement.md
THIS:           ./HEALTH_SelfImprovement.md
SYNC:           ./SYNC_SelfImprovement.md
```

---

## PURPOSE

Health checks verify the self-improvement module is working correctly and
delivering value. This includes both the module's internal health AND the
meta-question: is improvement actually happening?

---

## WHEN TO USE HEALTH VS TESTS

| Use HEALTH for | Use TESTS for |
|----------------|---------------|
| Is improvement velocity increasing? | Does pattern detection work? |
| Are deployments succeeding? | Does rollback execute correctly? |
| Is learning compounding? | Does pattern library store records? |
| Is overhead bounded? | Do resource limits trigger? |
| Are humans satisfied with proposals? | Does approval queue work? |

---

## HEALTH INDICATORS

### H1: Improvement Velocity

**Value:** System is getting better at getting better.

**Objective:** O6 (Compound Learning)

**Metric:** `improvements_deployed / time_window`

| Value | Status | Interpretation |
|-------|--------|----------------|
| Increasing | HEALTHY | Learning is compounding |
| Stable | WARNING | Not accelerating yet |
| Decreasing | ERROR | Something blocking improvement |

**Mechanism:**
```python
def check_improvement_velocity(window: Duration = 30d) -> HealthResult:
    # Get weekly improvement counts
    weeks = split_into_weeks(window)
    counts = [count_improvements(week) for week in weeks]

    # Compute trend
    trend = compute_trend(counts)

    if trend > 0.1:  # Increasing by 10%+ per week
        return HealthResult("HEALTHY", f"Velocity trending up: {trend:.1%}")
    elif trend > -0.1:  # Roughly stable
        return HealthResult("WARNING", f"Velocity stable: {trend:.1%}")
    else:
        return HealthResult("ERROR", f"Velocity declining: {trend:.1%}")
```

---

### H2: Deployment Success Rate

**Value:** Deployments don't break things.

**Objective:** O4 (Safe Deploy)

**Metric:** `successful_deployments / total_deployments`

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 95% | HEALTHY | Deployments reliable |
| 90-94% | WARNING | Some failures |
| < 90% | ERROR | Too many failures |

**Mechanism:**
```python
def check_deployment_success(window: Duration = 30d) -> HealthResult:
    deployments = get_deployments(window)
    if not deployments:
        return HealthResult("HEALTHY", "No deployments")

    successful = sum(1 for d in deployments if d.status == "success")
    rate = successful / len(deployments)

    if rate >= 0.95:
        return HealthResult("HEALTHY", f"Success rate: {rate:.1%}")
    elif rate >= 0.90:
        return HealthResult("WARNING", f"Success rate: {rate:.1%}")
    else:
        return HealthResult("ERROR", f"Success rate: {rate:.1%}")
```

---

### H3: Rollback Rate

**Value:** Few deployments need to be reversed.

**Objective:** O4 (Safe Deploy)

**Metric:** `rollbacks / deployments`

| Value | Status | Interpretation |
|-------|--------|----------------|
| < 5% | HEALTHY | Validation catching problems |
| 5-10% | WARNING | Some slip through |
| > 10% | ERROR | Validation not effective |

**Mechanism:**
```python
def check_rollback_rate(window: Duration = 30d) -> HealthResult:
    deployments = get_deployments(window)
    if not deployments:
        return HealthResult("HEALTHY", "No deployments")

    rollbacks = sum(1 for d in deployments if d.status == "rolled_back")
    rate = rollbacks / len(deployments)

    if rate < 0.05:
        return HealthResult("HEALTHY", f"Rollback rate: {rate:.1%}")
    elif rate <= 0.10:
        return HealthResult("WARNING", f"Rollback rate: {rate:.1%}")
    else:
        return HealthResult("ERROR", f"Rollback rate: {rate:.1%}")
```

---

### H4: Detection Lead Time

**Value:** Problems found before users notice.

**Objective:** O2 (Early Detection)

**Metric:** `patterns_detected_before_complaint / total_patterns`

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 80% | HEALTHY | Proactive detection |
| 50-79% | WARNING | Often reactive |
| < 50% | ERROR | Mostly reactive |

**Mechanism:**
```python
def check_detection_lead_time(window: Duration = 30d) -> HealthResult:
    patterns = get_patterns(window)
    if not patterns:
        return HealthResult("HEALTHY", "No patterns")

    proactive = sum(1 for p in patterns if p.detected_before_complaint)
    rate = proactive / len(patterns)

    if rate >= 0.80:
        return HealthResult("HEALTHY", f"Proactive rate: {rate:.1%}")
    elif rate >= 0.50:
        return HealthResult("WARNING", f"Proactive rate: {rate:.1%}")
    else:
        return HealthResult("ERROR", f"Proactive rate: {rate:.1%}")
```

---

### H5: Fix Recurrence Rate

**Value:** Fixes actually work.

**Objective:** O3 (Root Causes)

**Metric:** `recurring_patterns / fixed_patterns`

| Value | Status | Interpretation |
|-------|--------|----------------|
| < 10% | HEALTHY | Fixes are lasting |
| 10-20% | WARNING | Some recurrence |
| > 20% | ERROR | Treating symptoms not causes |

**Mechanism:**
```python
def check_fix_recurrence(window: Duration = 90d) -> HealthResult:
    fixed = get_fixed_patterns(window)
    if not fixed:
        return HealthResult("HEALTHY", "No fixed patterns")

    recurring = sum(1 for p in fixed if p.recurred_after_fix)
    rate = recurring / len(fixed)

    if rate < 0.10:
        return HealthResult("HEALTHY", f"Recurrence rate: {rate:.1%}")
    elif rate <= 0.20:
        return HealthResult("WARNING", f"Recurrence rate: {rate:.1%}")
    else:
        return HealthResult("ERROR", f"Recurrence rate: {rate:.1%}")
```

---

### H6: Resource Overhead

**Value:** Improvement doesn't degrade production.

**Objective:** O7 (Efficiency)

**Metric:** `improvement_cpu_time / total_cpu_time`

| Value | Status | Interpretation |
|-------|--------|----------------|
| < 3% | HEALTHY | Minimal overhead |
| 3-5% | WARNING | Approaching limit |
| > 5% | ERROR | Exceeds budget |

**Mechanism:**
```python
def check_resource_overhead() -> HealthResult:
    improvement_cpu = measure_improvement_cpu()
    total_cpu = measure_total_cpu()

    overhead = improvement_cpu / total_cpu

    if overhead < 0.03:
        return HealthResult("HEALTHY", f"Overhead: {overhead:.1%}")
    elif overhead <= 0.05:
        return HealthResult("WARNING", f"Overhead: {overhead:.1%}")
    else:
        return HealthResult("ERROR", f"Overhead: {overhead:.1%}")
```

---

### H7: Human Approval Rate

**Value:** Proposals are sensible.

**Objective:** O5 (Human Control)

**Metric:** `approved_proposals / submitted_proposals`

| Value | Status | Interpretation |
|-------|--------|----------------|
| ≥ 80% | HEALTHY | Proposals are sensible |
| 60-79% | WARNING | Some misalignment |
| < 60% | ERROR | Proposals not useful |

**Mechanism:**
```python
def check_approval_rate(window: Duration = 30d) -> HealthResult:
    submitted = get_proposals_needing_approval(window)
    if not submitted:
        return HealthResult("HEALTHY", "No proposals")

    approved = sum(1 for p in submitted if p.approved)
    rate = approved / len(submitted)

    if rate >= 0.80:
        return HealthResult("HEALTHY", f"Approval rate: {rate:.1%}")
    elif rate >= 0.60:
        return HealthResult("WARNING", f"Approval rate: {rate:.1%}")
    else:
        return HealthResult("ERROR", f"Approval rate: {rate:.1%}")
```

---

### H8: Learning Library Growth

**Value:** Knowledge is accumulating.

**Objective:** O6 (Compound Learning)

**Metric:** `new_patterns_recorded / time_window`

| Value | Status | Interpretation |
|-------|--------|----------------|
| Growing | HEALTHY | Learning new patterns |
| Stable | WARNING | Not finding new patterns |
| Empty | ERROR | Learning not working |

**Mechanism:**
```python
def check_learning_growth(window: Duration = 30d) -> HealthResult:
    library_size_start = get_library_size(window.start)
    library_size_end = get_library_size(window.end)

    growth = library_size_end - library_size_start
    growth_rate = growth / library_size_start if library_size_start > 0 else float('inf')

    if growth > 0:
        return HealthResult("HEALTHY", f"Library grew by {growth} patterns")
    elif library_size_end > 0:
        return HealthResult("WARNING", f"Library stable at {library_size_end}")
    else:
        return HealthResult("ERROR", "Library is empty")
```

---

### H9: Value Metric Trend

**Value:** Core metrics actually improving.

**Objective:** O1 (Value Delivery)

**Metric:** Trend of target value metrics (satisfaction, completion, etc.)

| Value | Status | Interpretation |
|-------|--------|----------------|
| Improving | HEALTHY | System getting better |
| Stable | WARNING | Not improving |
| Declining | ERROR | Something wrong |

**Mechanism:**
```python
def check_value_trend(window: Duration = 90d) -> HealthResult:
    metrics = [
        ("satisfaction", get_satisfaction_trend(window)),
        ("completion_rate", get_completion_trend(window)),
        ("error_rate", get_error_trend(window)),  # Inverted: declining is good
    ]

    improving = 0
    for name, trend in metrics:
        if name == "error_rate":
            if trend < -0.05:
                improving += 1
        else:
            if trend > 0.05:
                improving += 1

    if improving >= 2:
        return HealthResult("HEALTHY", f"{improving}/3 metrics improving")
    elif improving >= 1:
        return HealthResult("WARNING", f"{improving}/3 metrics improving")
    else:
        return HealthResult("ERROR", "No metrics improving")
```

---

### H10: Invariant Violations

**Value:** Core guarantees maintained.

**Objective:** All (system integrity)

**Metric:** Count of invariant violations

| Value | Status | Interpretation |
|-------|--------|----------------|
| 0 | HEALTHY | All invariants respected |
| 1-2 | WARNING | Minor violations |
| ≥ 3 | ERROR | Systemic issues |

**Mechanism:**
```python
def check_invariant_violations(window: Duration = 7d) -> HealthResult:
    violations = get_invariant_violations(window)

    critical = sum(1 for v in violations if v.priority == "CRITICAL")
    high = sum(1 for v in violations if v.priority == "HIGH")
    total = len(violations)

    if critical > 0:
        return HealthResult("ERROR", f"{critical} CRITICAL violations")
    elif total == 0:
        return HealthResult("HEALTHY", "No violations")
    elif total <= 2:
        return HealthResult("WARNING", f"{total} violations")
    else:
        return HealthResult("ERROR", f"{total} violations")
```

---

## META-HEALTH

The self-improvement module must monitor its own health:

### M1: Loop Liveness

**Check:** Is the improvement loop running?

```python
def check_loop_liveness() -> HealthResult:
    last_cycle = get_last_cycle_timestamp()
    if not last_cycle:
        return HealthResult("ERROR", "No cycles ever run")

    age = time.now() - last_cycle
    max_age = timedelta(hours=24)

    if age < max_age:
        return HealthResult("HEALTHY", f"Last cycle: {age} ago")
    else:
        return HealthResult("ERROR", f"No cycle in {age}")
```

### M2: Trigger Queue Depth

**Check:** Is the trigger queue backing up?

```python
def check_trigger_queue() -> HealthResult:
    depth = get_trigger_queue_depth()

    if depth < 10:
        return HealthResult("HEALTHY", f"Queue depth: {depth}")
    elif depth < 50:
        return HealthResult("WARNING", f"Queue depth: {depth}")
    else:
        return HealthResult("ERROR", f"Queue backed up: {depth}")
```

### M3: Cycle Duration

**Check:** Are cycles completing in reasonable time?

```python
def check_cycle_duration(window: Duration = 7d) -> HealthResult:
    cycles = get_cycles(window)
    if not cycles:
        return HealthResult("HEALTHY", "No cycles")

    durations = [c.duration for c in cycles]
    p95 = percentile(durations, 95)

    max_duration = timedelta(hours=1)

    if p95 < max_duration:
        return HealthResult("HEALTHY", f"p95 duration: {p95}")
    else:
        return HealthResult("WARNING", f"Slow cycles: p95 = {p95}")
```

---

## HEALTH CHECK FLOW

```
1. Periodic timer (every hour)
   │
   ▼
2. Run all health checks
   │
   ├─▶ H1: Improvement velocity
   ├─▶ H2: Deployment success rate
   ├─▶ H3: Rollback rate
   ├─▶ H4: Detection lead time
   ├─▶ H5: Fix recurrence rate
   ├─▶ H6: Resource overhead
   ├─▶ H7: Human approval rate
   ├─▶ H8: Learning library growth
   ├─▶ H9: Value metric trend
   ├─▶ H10: Invariant violations
   ├─▶ M1: Loop liveness
   ├─▶ M2: Trigger queue depth
   └─▶ M3: Cycle duration
   │
   ▼
3. Aggregate results → HealthReport
   │
   ▼
4. If any ERROR: Alert immediately
   If any WARNING: Log and include in daily digest
   If all HEALTHY: Log summary
```

---

## HEALTH CHECKER INDEX

| ID | Metric | HEALTHY | WARNING | ERROR |
|----|--------|---------|---------|-------|
| H1 | Improvement velocity | Increasing | Stable | Decreasing |
| H2 | Deployment success rate | ≥ 95% | 90-94% | < 90% |
| H3 | Rollback rate | < 5% | 5-10% | > 10% |
| H4 | Detection lead time | ≥ 80% proactive | 50-79% | < 50% |
| H5 | Fix recurrence rate | < 10% | 10-20% | > 20% |
| H6 | Resource overhead | < 3% | 3-5% | > 5% |
| H7 | Human approval rate | ≥ 80% | 60-79% | < 60% |
| H8 | Learning library growth | Growing | Stable | Empty |
| H9 | Value metric trend | 2+ improving | 1 improving | 0 improving |
| H10 | Invariant violations | 0 | 1-2 | ≥ 3 or CRITICAL |
| M1 | Loop liveness | < 24h | — | ≥ 24h |
| M2 | Trigger queue depth | < 10 | 10-50 | > 50 |
| M3 | Cycle duration (p95) | < 1h | — | ≥ 1h |

---

## MANUAL REVIEW CHECKLIST

When reviewing self-improvement health manually:

```markdown
## Self-Improvement Health Review: {date}

### Improvement Quality
- [ ] Value metrics trending positive
- [ ] Deployment success rate ≥ 95%
- [ ] Rollback rate < 5%
- [ ] No recurring patterns (< 10%)

### Detection Quality
- [ ] Detection mostly proactive (≥ 80%)
- [ ] Patterns have sufficient evidence
- [ ] Layer attribution accurate

### Efficiency
- [ ] Resource overhead < 5%
- [ ] Cycles completing in < 1h
- [ ] Trigger queue not backed up

### Learning
- [ ] Pattern library growing
- [ ] Improvement velocity increasing
- [ ] Known fixes being reused

### Human Oversight
- [ ] Approval rate ≥ 80%
- [ ] Proposals understandable
- [ ] Rollback always available

### Invariants
- [ ] No CRITICAL violations
- [ ] No HIGH violations
- [ ] Audit trail complete

### Overall
- [ ] System actually getting better
- [ ] Trust in automation appropriate
- [ ] No concerning trends
```

---

## EXAMPLE HEALTH REPORT

```
═══════════════════════════════════════════════════════════════════════════════
SELF-IMPROVEMENT HEALTH REPORT: 2025-12-26
═══════════════════════════════════════════════════════════════════════════════

OVERALL: HEALTHY ✅

Improvement Metrics:
  H1 Improvement velocity:    HEALTHY (trending up 15%/week)
  H2 Deployment success rate: HEALTHY (97%)
  H3 Rollback rate:           HEALTHY (2%)
  H9 Value metric trend:      HEALTHY (2/3 metrics improving)

Detection & Diagnosis:
  H4 Detection lead time:     HEALTHY (85% proactive)
  H5 Fix recurrence rate:     HEALTHY (8%)

Efficiency:
  H6 Resource overhead:       HEALTHY (2.1%)

Human Oversight:
  H7 Human approval rate:     HEALTHY (88%)

Learning:
  H8 Learning library growth: HEALTHY (+12 patterns this month)

Integrity:
  H10 Invariant violations:   HEALTHY (0 violations)

Meta-Health:
  M1 Loop liveness:           HEALTHY (last cycle 2h ago)
  M2 Trigger queue depth:     HEALTHY (3 pending)
  M3 Cycle duration:          HEALTHY (p95 = 18m)

Summary:
  - 15 improvements deployed this month
  - 97% success rate, 2% rollback rate
  - Value metrics improving
  - Learning library growing

Verdict: Self-improvement module functioning well.
═══════════════════════════════════════════════════════════════════════════════
```

---

## DOCKING POINTS

Health checks dock into these locations:

| Dock ID | Location | Type | Purpose |
|---------|----------|------|---------|
| DOCK_CYCLE_START | loop.py:run_cycle | input | Capture cycle start |
| DOCK_CYCLE_END | loop.py:run_cycle | output | Capture cycle result |
| DOCK_DEPLOY | deployer.py:deploy | output | Deployment result |
| DOCK_ROLLBACK | rollback.py:rollback | output | Rollback event |
| DOCK_APPROVE | queue.py:approve | output | Approval decision |
| DOCK_LEARN | extractor.py:extract | output | Learning record |

---

## HOW TO RUN

### CLI

```bash
# Run all health checks
python -m engine.improvement.health.check_all

# Run specific check
python -m engine.improvement.health.check H1

# Run meta-health only
python -m engine.improvement.health.check_meta

# Generate report
python -m engine.improvement.health.report --format markdown
```

### Programmatic

```python
from mind.improvement.health import run_health_checks

report = run_health_checks()
print(report.overall_status)  # HEALTHY, WARNING, or ERROR

for name, result in report.checks.items():
    print(f"  {name}: {result.status} - {result.message}")
```
