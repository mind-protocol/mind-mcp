# Self-Improvement — Validation

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
THIS:           ./VALIDATION_SelfImprovement.md
IMPLEMENTATION: ./IMPLEMENTATION_SelfImprovement.md
HEALTH:         ./HEALTH_SelfImprovement.md
SYNC:           ./SYNC_SelfImprovement.md
```

---

## PURPOSE

Validation invariants define WHAT MUST BE TRUE for the self-improvement
module to operate correctly. If any invariant is violated, it's a bug —
not a variance in interpretation or configuration.

---

## INVARIANTS

### V1: No Deployment Without Validation

**Value protected:** Production stability.

**Why we care:** Unvalidated changes could degrade production. Validation
exists specifically to catch problems before they reach users.

**MUST:** Every deployment preceded by validation with PASSED or MANUAL_APPROVED status
**MUST:** Validation result recorded in audit log
**NEVER:** Deployment with FAILED or INCONCLUSIVE validation (unless human override with REQUIRE tier)

```python
def check_validation_before_deploy(deployment: Deployment) -> bool:
    validation = deployment.validation_result

    if validation.status == ValidationStatus.PASSED:
        return True

    if validation.status == ValidationStatus.AWAITING_HUMAN:
        return deployment.approval.tier == ApprovalTier.REQUIRE

    return False  # FAILED or INCONCLUSIVE without human override
```

**Priority:** CRITICAL

---

### V2: No Deployment Without Audit

**Value protected:** Traceability and accountability.

**Why we care:** Without audit trail, we can't understand what changed,
rollback precisely, or learn from failures.

**MUST:** Every deployment creates audit record with: proposal, validation, approval, timestamp, actor
**MUST:** Audit records are immutable after creation
**NEVER:** Deployment without corresponding audit record

```python
def check_audit_exists(deployment: Deployment) -> bool:
    audit = get_audit_record(deployment.id)

    if not audit:
        return False

    required_fields = ['proposal', 'validation', 'approval', 'timestamp', 'actor']
    for field in required_fields:
        if not hasattr(audit, field) or getattr(audit, field) is None:
            return False

    return True
```

**Priority:** CRITICAL

---

### V3: Rollback Always Possible

**Value protected:** Recovery capability.

**Why we care:** If we can't rollback, a bad deployment becomes permanent.
Recovery must be guaranteed.

**MUST:** Every deployment creates backup before applying changes
**MUST:** Backup sufficient to restore previous state
**MUST:** Rollback tested (at least for deployment type)
**NEVER:** Deployment without backup

```python
def check_rollback_possible(deployment: Deployment) -> bool:
    # Backup exists
    if not deployment.backup:
        return False

    # Backup is valid
    if not deployment.backup.is_valid():
        return False

    # Rollback mechanism tested for this type
    if not rollback_tested_for_type(deployment.proposal.type):
        return False

    return True
```

**Priority:** CRITICAL

---

### V4: Approval Tier Respected

**Value protected:** Human oversight.

**Why we care:** Bypassing approval tiers removes human control from
high-risk changes. Trust depends on this.

**MUST:** AUTO tier only for low-risk, validated constant tunes
**MUST:** REQUIRE tier for high-risk or formula changes
**MUST:** Human approval recorded when required
**NEVER:** High-risk deployment without human approval

```python
def check_approval_tier_respected(deployment: Deployment) -> bool:
    tier = deployment.approval.tier
    proposal = deployment.proposal

    if tier == ApprovalTier.AUTO:
        # Must be low risk constant tune
        if proposal.type != ProposalType.CONSTANT_TUNE:
            return False
        if proposal.risk != Risk.LOW:
            return False
        if deployment.validation.status != ValidationStatus.PASSED:
            return False

    elif tier in [ApprovalTier.APPROVE, ApprovalTier.REQUIRE]:
        # Must have human approval
        if not deployment.approval.human_approved:
            return False
        if not deployment.approval.approver_id:
            return False

    return True
```

**Priority:** CRITICAL

---

### V5: Pattern Requires Evidence

**Value protected:** Diagnosis quality.

**Why we care:** Diagnosing without evidence leads to wrong fixes.
Evidence makes diagnosis verifiable.

**MUST:** Every pattern has N >= PATTERN_THRESHOLD occurrences
**MUST:** Every diagnosis has evidence from root layer
**MUST:** Evidence traceable to logs or metrics
**NEVER:** Pattern from single occurrence

```python
def check_pattern_has_evidence(pattern: Pattern) -> bool:
    # Minimum occurrences
    if len(pattern.occurrences) < PATTERN_THRESHOLD:
        return False

    # Evidence exists
    if not pattern.evidence:
        return False

    # Evidence is traceable
    for e in pattern.evidence:
        if not e.source or not e.timestamp:
            return False

    return True


def check_diagnosis_has_evidence(diagnosis: Diagnosis) -> bool:
    # Root layer identified
    if not diagnosis.root_layer:
        return False

    # Evidence for root layer
    if diagnosis.root_layer not in diagnosis.evidence:
        return False

    # Evidence is non-empty
    if not diagnosis.evidence[diagnosis.root_layer]:
        return False

    return True
```

**Priority:** HIGH

---

### V6: Proposal Is Typed and Complete

**Value protected:** Tractability.

**Why we care:** Untyped proposals can't be validated, deployed, or
rolled back. Incomplete proposals create undefined behavior.

**MUST:** Every proposal has exactly one type
**MUST:** Every proposal has change specification
**MUST:** Every proposal has rationale
**MUST:** Every proposal has risk assessment
**NEVER:** Proposal with missing required fields

```python
def check_proposal_complete(proposal: Proposal) -> bool:
    required_fields = ['type', 'change', 'rationale', 'risk']

    for field in required_fields:
        if not hasattr(proposal, field) or getattr(proposal, field) is None:
            return False

    # Type-specific checks
    if proposal.type == ProposalType.CONSTANT_TUNE:
        if not proposal.change.name or proposal.change.proposed is None:
            return False

    elif proposal.type == ProposalType.FORMULA_CHANGE:
        if not proposal.change.function or not proposal.change.modification:
            return False

    return True
```

**Priority:** HIGH

---

### V7: Resource Bounds Respected

**Value protected:** System stability.

**Why we care:** Unbounded improvement overhead degrades production.
Resources must stay within limits.

**MUST:** Observation overhead < 5% of operation cost
**MUST:** Concurrent improvement cycles <= MAX_CONCURRENT
**MUST:** Single cycle duration <= MAX_CYCLE_DURATION
**NEVER:** Improvement loop starves production

```python
def check_resource_bounds() -> bool:
    # Observation overhead
    obs_overhead = measure_observation_overhead()
    if obs_overhead > 0.05:
        return False

    # Concurrent cycles
    active_cycles = count_active_cycles()
    if active_cycles > MAX_CONCURRENT_CYCLES:
        return False

    # Check oldest cycle duration
    oldest = get_oldest_active_cycle()
    if oldest and oldest.duration > MAX_CYCLE_DURATION:
        return False

    return True
```

**Priority:** HIGH

---

### V8: Learning Is Recorded

**Value protected:** Compound improvement.

**Why we care:** Without learning records, we can't accelerate future
improvements. Knowledge must accumulate.

**MUST:** Every completed cycle creates learning record
**MUST:** Successful fixes recorded in pattern library
**MUST:** Failed fixes recorded (to avoid repetition)
**NEVER:** Cycle completes without learning extraction

```python
def check_learning_recorded(cycle: ImprovementCycle) -> bool:
    if cycle.status != CycleStatus.COMPLETED:
        return True  # Not yet complete

    learning = get_learning_record(cycle.id)
    if not learning:
        return False

    # If there was a deployment, fix should be recorded
    if cycle.deployment:
        fix_record = get_fix_record(cycle.id)
        if not fix_record:
            return False

    return True
```

**Priority:** MEDIUM

---

### V9: Degradation Triggers Rollback

**Value protected:** Automatic recovery.

**Why we care:** Humans can't watch every deployment. Automatic rollback
on degradation is essential for safety.

**MUST:** Post-deploy monitoring detects degradation > threshold
**MUST:** Degradation automatically triggers rollback
**MUST:** Rollback completes within timeout
**NEVER:** Sustained degradation without rollback attempt

```python
def check_degradation_rollback(deployment: Deployment) -> bool:
    if deployment.status != DeploymentStatus.SUCCESS:
        return True  # Deployment didn't succeed

    monitoring = deployment.monitoring
    if not monitoring:
        return False  # No monitoring

    for metric, values in monitoring.metrics.items():
        degradation = compute_degradation(values, deployment.baseline)
        if degradation > DEGRADATION_THRESHOLD:
            # Should have triggered rollback
            if deployment.status != DeploymentStatus.ROLLED_BACK:
                return False

    return True
```

**Priority:** HIGH

---

### V10: Meta-Improvement Is Bounded

**Value protected:** System sanity.

**Why we care:** Self-improvement improving itself without bounds leads
to infinite loops and unpredictable behavior.

**MUST:** Meta-improvement cycles limited to 1 per day
**MUST:** Meta-changes require REQUIRE tier
**MUST:** Meta-learning uses conservative thresholds
**NEVER:** Meta-improvement triggers itself

```python
def check_meta_bounds() -> bool:
    # Check meta-cycle frequency
    meta_cycles_today = count_meta_cycles(window=timedelta(days=1))
    if meta_cycles_today > 1:
        return False

    # Check recent meta-changes had REQUIRE tier
    recent_meta = get_recent_meta_changes(window=timedelta(days=7))
    for change in recent_meta:
        if change.approval.tier != ApprovalTier.REQUIRE:
            return False

    return True
```

**Priority:** HIGH

---

## PRIORITY TABLE

| Priority | Meaning | Invariants |
|----------|---------|------------|
| CRITICAL | System fails if violated | V1, V2, V3, V4 |
| HIGH | Major safety/value compromised | V5, V6, V7, V9, V10 |
| MEDIUM | Functionality degraded | V8 |

---

## INVARIANT INDEX

| ID | Value Protected | Priority | Check Function |
|----|-----------------|----------|----------------|
| V1 | Production stability | CRITICAL | `check_validation_before_deploy` |
| V2 | Traceability | CRITICAL | `check_audit_exists` |
| V3 | Recovery capability | CRITICAL | `check_rollback_possible` |
| V4 | Human oversight | CRITICAL | `check_approval_tier_respected` |
| V5 | Diagnosis quality | HIGH | `check_pattern_has_evidence` |
| V6 | Tractability | HIGH | `check_proposal_complete` |
| V7 | System stability | HIGH | `check_resource_bounds` |
| V8 | Compound learning | MEDIUM | `check_learning_recorded` |
| V9 | Automatic recovery | HIGH | `check_degradation_rollback` |
| V10 | System sanity | HIGH | `check_meta_bounds` |

---

## VERIFICATION PROCEDURE

1. Run invariant checks after each improvement cycle phase
2. Block phase transition if CRITICAL invariant violated
3. Alert and log if HIGH invariant violated
4. Log warning if MEDIUM invariant violated
5. Record all violations in health metrics
6. Daily report on invariant health

```python
async def verify_invariants(phase: Phase) -> InvariantReport:
    checks = get_checks_for_phase(phase)
    results = {}

    for check in checks:
        try:
            passed = await check.function()
            results[check.id] = InvariantResult(
                passed=passed,
                priority=check.priority,
            )
        except Exception as e:
            results[check.id] = InvariantResult(
                passed=False,
                priority=check.priority,
                error=str(e),
            )

    # Block on CRITICAL failures
    critical_failures = [r for r in results.values()
                        if not r.passed and r.priority == Priority.CRITICAL]
    if critical_failures:
        raise InvariantViolationError(critical_failures)

    return InvariantReport(results=results)
```

---

## TESTING REQUIREMENTS

| Invariant | Test Type | Coverage |
|-----------|-----------|----------|
| V1 | Unit + Integration | Attempt deploy without validation |
| V2 | Integration | Verify audit record creation |
| V3 | Integration | Test rollback for each proposal type |
| V4 | Unit + Integration | Verify tier assignment and enforcement |
| V5 | Unit | Pattern creation with varying occurrences |
| V6 | Unit | Proposal validation with missing fields |
| V7 | Integration | Resource consumption under load |
| V8 | Integration | Learning record creation after cycles |
| V9 | Integration | Rollback trigger on metric degradation |
| V10 | Integration | Meta-cycle bounds enforcement |
