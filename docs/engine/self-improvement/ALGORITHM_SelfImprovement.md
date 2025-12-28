# Self-Improvement — Algorithm

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
THIS:           ./ALGORITHM_SelfImprovement.md
VALIDATION:     ./VALIDATION_SelfImprovement.md
IMPLEMENTATION: ./IMPLEMENTATION_SelfImprovement.md
HEALTH:         ./HEALTH_SelfImprovement.md
SYNC:           ./SYNC_SelfImprovement.md
```

---

## OVERVIEW

The self-improvement loop runs continuously, triggered by events:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         IMPROVEMENT LOOP                                 │
│                                                                          │
│   TRIGGER ──▶ OBSERVE ──▶ DIAGNOSE ──▶ PROPOSE ──▶ VALIDATE ──▶ DEPLOY  │
│      │                                                              │    │
│      │                      ┌───────────────────────────────────────┘    │
│      │                      ▼                                            │
│      └───────────────── LEARN ◀─────────────────────────────────────────┘
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: TRIGGER

### Event Types

```python
class TriggerType(Enum):
    THRESHOLD_BREACH = "threshold_breach"   # Health metric crosses threshold
    PATTERN_DETECTED = "pattern_detected"   # N occurrences of same anomaly
    PERIODIC = "periodic"                   # Time-based (daily, weekly)
    HUMAN_REQUEST = "human_request"         # Explicit improvement request
    META_CHECK = "meta_check"               # Self-improvement health check
```

### Algorithm: Trigger Handler

```python
async def handle_trigger(trigger: Trigger) -> Optional[ImprovementCycle]:
    # 1. Check if improvement loop is already running
    if improvement_loop.is_running and trigger.type != TriggerType.HUMAN_REQUEST:
        queue_trigger(trigger)
        return None

    # 2. Validate trigger
    if not validate_trigger(trigger):
        log_invalid_trigger(trigger)
        return None

    # 3. Compute urgency
    urgency = compute_urgency(trigger)

    # 4. Start improvement cycle
    cycle = ImprovementCycle(
        trigger=trigger,
        urgency=urgency,
        started_at=time.now(),
    )

    return await run_improvement_cycle(cycle)
```

### Urgency Computation

```python
def compute_urgency(trigger: Trigger) -> Urgency:
    if trigger.type == TriggerType.THRESHOLD_BREACH:
        # Severity based on how far past threshold
        severity = trigger.metric_value / trigger.threshold
        if severity > 2.0:
            return Urgency.CRITICAL
        elif severity > 1.5:
            return Urgency.HIGH
        else:
            return Urgency.MEDIUM

    elif trigger.type == TriggerType.PATTERN_DETECTED:
        # Based on pattern impact
        return trigger.pattern.impact_level

    elif trigger.type == TriggerType.HUMAN_REQUEST:
        return trigger.requested_urgency or Urgency.HIGH

    else:
        return Urgency.LOW
```

---

## PHASE 2: OBSERVE

### Signal Sources

```yaml
signal_sources:
  exploration_logs:
    path: mind/data/logs/traversal/*.jsonl
    signals:
      - state_transitions
      - link_scores
      - energy_injection
      - satisfaction
      - anomalies

  agent_traces:
    path: mind/data/logs/agents/*.jsonl
    signals:
      - skill_loaded
      - protocol_invoked
      - tool_calls
      - outcome

  health_metrics:
    source: doctor
    signals:
      - invariant_status
      - threshold_values
      - check_results

  graph_events:
    source: graph_ops
    signals:
      - node_created
      - link_created
      - energy_changed
      - weight_changed
```

### Algorithm: Signal Collection

```python
async def collect_signals(
    window: TimeWindow,
    sources: List[SignalSource],
) -> SignalSet:
    signals = SignalSet()

    for source in sources:
        # 1. Read from source
        raw = await source.read(window)

        # 2. Filter relevant signals
        filtered = source.filter(raw)

        # 3. Normalize to common schema
        normalized = source.normalize(filtered)

        # 4. Add to signal set
        signals.add_all(normalized)

    # 5. Compute aggregates
    signals.compute_aggregates()

    return signals
```

### Signal Aggregation

```python
def compute_aggregates(signals: SignalSet) -> Aggregates:
    return Aggregates(
        # Exploration aggregates
        exploration_count=len(signals.explorations),
        mean_satisfaction=mean(s.satisfaction for s in signals.explorations),
        mean_efficiency=mean(s.efficiency for s in signals.explorations),
        timeout_rate=count(s.timeout for s in signals.explorations) / len(signals.explorations),

        # Anomaly aggregates
        anomaly_count=len(signals.anomalies),
        anomaly_by_type=group_by(signals.anomalies, lambda a: a.type),
        anomaly_by_layer=group_by(signals.anomalies, lambda a: a.layer),

        # Agent aggregates
        agent_success_rate=mean(a.success for a in signals.agent_traces),
        protocol_usage=group_by(signals.agent_traces, lambda a: a.protocol),

        # Graph aggregates
        nodes_created=len(signals.graph_events.node_created),
        energy_injected=sum(e.amount for e in signals.graph_events.energy_changed),
    )
```

---

## PHASE 3: DIAGNOSE

### Pattern Detection

```python
async def detect_patterns(signals: SignalSet) -> List[Pattern]:
    patterns = []

    # 1. Recurring anomalies
    for anomaly_type, occurrences in signals.aggregates.anomaly_by_type.items():
        if len(occurrences) >= PATTERN_THRESHOLD:
            patterns.append(Pattern(
                type=PatternType.RECURRING_ANOMALY,
                anomaly_type=anomaly_type,
                occurrences=occurrences,
                impact=compute_impact(occurrences),
            ))

    # 2. Metric drift
    for metric, values in signals.metrics_over_time.items():
        trend = compute_trend(values)
        if abs(trend) > DRIFT_THRESHOLD:
            patterns.append(Pattern(
                type=PatternType.METRIC_DRIFT,
                metric=metric,
                trend=trend,
                impact=compute_drift_impact(metric, trend),
            ))

    # 3. Correlation patterns
    for (metric_a, metric_b), correlation in compute_correlations(signals).items():
        if abs(correlation) > CORRELATION_THRESHOLD:
            patterns.append(Pattern(
                type=PatternType.CORRELATION,
                metrics=(metric_a, metric_b),
                correlation=correlation,
            ))

    return patterns
```

### Layer Attribution

```python
async def diagnose_pattern(pattern: Pattern) -> Diagnosis:
    # 1. Start at symptom layer (Output)
    current_layer = Layer.OUTPUT

    # 2. Gather evidence for each layer
    evidence = {}
    for layer in Layer.from_top():
        evidence[layer] = await gather_layer_evidence(pattern, layer)

    # 3. Find root cause layer (first layer that explains pattern)
    root_layer = None
    root_evidence = None

    for layer in Layer.from_bottom():  # Start from deepest
        if explains_pattern(evidence[layer], pattern):
            root_layer = layer
            root_evidence = evidence[layer]
            break

    # 4. Check pattern library for known patterns
    known = await pattern_library.find_similar(pattern)

    return Diagnosis(
        pattern=pattern,
        root_layer=root_layer,
        evidence=root_evidence,
        confidence=compute_confidence(evidence, known),
        known_pattern=known,
    )
```

### Layer Evidence Gathering

```python
async def gather_layer_evidence(pattern: Pattern, layer: Layer) -> Evidence:
    if layer == Layer.OUTPUT:
        return Evidence(
            found_narratives=pattern.signals.found_narratives,
            satisfaction=pattern.signals.satisfaction,
            expected_vs_actual=compare_to_expected(pattern),
        )

    elif layer == Layer.BEHAVIOR:
        return Evidence(
            state_transitions=extract_transitions(pattern.signals),
            branching_decisions=extract_branching(pattern.signals),
            merge_results=extract_merges(pattern.signals),
        )

    elif layer == Layer.PHYSICS:
        return Evidence(
            link_scores=extract_scores(pattern.signals),
            energy_injection=extract_energy(pattern.signals),
            embedding_drift=compute_embedding_drift(pattern.signals),
        )

    elif layer == Layer.PROTOCOL:
        return Evidence(
            parameters=extract_parameters(pattern.signals),
            query_intention=extract_query_intention(pattern.signals),
            protocol_used=extract_protocol(pattern.signals),
        )

    elif layer == Layer.SKILL:
        return Evidence(
            skill_loaded=extract_skill(pattern.signals),
            context_available=extract_context(pattern.signals),
            tool_selection=extract_tools(pattern.signals),
        )
```

---

## PHASE 4: PROPOSE

### Proposal Generation

```python
async def generate_proposals(diagnosis: Diagnosis) -> List[Proposal]:
    proposals = []

    # 1. Check known fixes first
    if diagnosis.known_pattern:
        known_fix = await pattern_library.get_fix(diagnosis.known_pattern)
        if known_fix:
            proposals.append(adapt_known_fix(known_fix, diagnosis))

    # 2. Generate layer-specific proposals
    layer_proposals = generate_layer_proposals(diagnosis)
    proposals.extend(layer_proposals)

    # 3. Score and rank proposals
    for proposal in proposals:
        proposal.score = score_proposal(proposal, diagnosis)

    proposals.sort(key=lambda p: p.score, reverse=True)

    # 4. Add validation plans
    for proposal in proposals:
        proposal.validation_plan = create_validation_plan(proposal)

    return proposals
```

### Layer-Specific Proposal Generation

```python
def generate_layer_proposals(diagnosis: Diagnosis) -> List[Proposal]:
    layer = diagnosis.root_layer

    if layer == Layer.PHYSICS:
        return generate_physics_proposals(diagnosis)
    elif layer == Layer.BEHAVIOR:
        return generate_behavior_proposals(diagnosis)
    elif layer == Layer.PROTOCOL:
        return generate_protocol_proposals(diagnosis)
    elif layer == Layer.SKILL:
        return generate_skill_proposals(diagnosis)
    else:
        return []


def generate_physics_proposals(diagnosis: Diagnosis) -> List[Proposal]:
    proposals = []
    evidence = diagnosis.evidence

    # Constant tuning proposals
    if evidence.link_scores.mean_semantic < 0.5:
        proposals.append(Proposal(
            type=ProposalType.CONSTANT_TUNE,
            change=ConstantChange(
                name="INTENTION_WEIGHT",
                current=get_current("INTENTION_WEIGHT"),
                proposed=get_current("INTENTION_WEIGHT") * 1.2,
            ),
            rationale="Low semantic scores suggest intention weight too low",
            risk=Risk.LOW,
        ))

    if evidence.energy_injection.variance > THRESHOLD:
        proposals.append(Proposal(
            type=ProposalType.CONSTANT_TUNE,
            change=ConstantChange(
                name="STATE_MULTIPLIER",
                current=get_current("STATE_MULTIPLIER"),
                proposed=rebalance_multipliers(evidence),
            ),
            rationale="Energy injection variance too high",
            risk=Risk.MEDIUM,
        ))

    # Formula change proposals (higher risk)
    if evidence.embedding_drift.detected:
        proposals.append(Proposal(
            type=ProposalType.FORMULA_CHANGE,
            change=FormulaChange(
                function="update_crystallization_embedding",
                modification="Add decay factor for old path contributions",
            ),
            rationale="Crystallization embedding drifting from intent",
            risk=Risk.HIGH,
        ))

    return proposals
```

### Proposal Scoring

```python
def score_proposal(proposal: Proposal, diagnosis: Diagnosis) -> float:
    # Factors
    impact = estimate_impact(proposal, diagnosis)       # How much value gained
    confidence = diagnosis.confidence                   # How sure about root cause
    risk = proposal.risk.value                          # How risky is change
    complexity = estimate_complexity(proposal)          # How complex to implement

    # Scoring formula
    score = (impact * confidence) / (risk * complexity)

    # Bonus for known fixes
    if proposal.from_known_pattern:
        score *= 1.5

    return score
```

---

## PHASE 5: VALIDATE

### Validation Mode Selection

```python
def select_validation_mode(proposal: Proposal) -> ValidationMode:
    if proposal.type == ProposalType.CONSTANT_TUNE:
        if proposal.risk == Risk.LOW:
            return ValidationMode.UNIT_TEST
        else:
            return ValidationMode.AB_TEST

    elif proposal.type == ProposalType.FORMULA_CHANGE:
        return ValidationMode.SHADOW_MODE

    elif proposal.type == ProposalType.BEHAVIOR_FIX:
        return ValidationMode.CANARY

    elif proposal.type in [ProposalType.PROTOCOL_UPDATE, ProposalType.SKILL_IMPROVE]:
        return ValidationMode.SHADOW_MODE

    else:
        return ValidationMode.MANUAL


class ValidationMode(Enum):
    UNIT_TEST = "unit_test"       # Isolated test
    SHADOW_MODE = "shadow_mode"   # Run alongside production
    CANARY = "canary"             # Deploy to subset
    AB_TEST = "ab_test"           # Randomized comparison
    MANUAL = "manual"             # Human validation
```

### Validation Execution

```python
async def validate_proposal(proposal: Proposal) -> ValidationResult:
    mode = select_validation_mode(proposal)

    if mode == ValidationMode.UNIT_TEST:
        return await run_unit_tests(proposal)

    elif mode == ValidationMode.SHADOW_MODE:
        # Run new logic alongside old, compare outputs
        baseline = await collect_baseline_metrics()
        await deploy_shadow(proposal)
        shadow_metrics = await collect_shadow_metrics(duration=SHADOW_DURATION)
        return compare_metrics(baseline, shadow_metrics)

    elif mode == ValidationMode.CANARY:
        # Deploy to subset, monitor
        baseline = await collect_baseline_metrics()
        await deploy_canary(proposal, percentage=10)
        canary_metrics = await monitor_canary(duration=CANARY_DURATION)
        return compare_metrics(baseline, canary_metrics)

    elif mode == ValidationMode.AB_TEST:
        # Randomized comparison
        return await run_ab_test(proposal, duration=AB_DURATION)

    elif mode == ValidationMode.MANUAL:
        # Queue for human validation
        return ValidationResult(status=ValidationStatus.AWAITING_HUMAN)
```

### Validation Result

```python
@dataclass
class ValidationResult:
    status: ValidationStatus  # PASSED, FAILED, INCONCLUSIVE, AWAITING_HUMAN
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    improvement: Dict[str, float]  # Percentage change per metric
    statistical_significance: Optional[float]
    recommendation: str
```

---

## PHASE 6: APPROVE

### Approval Tier Selection

```python
def select_approval_tier(proposal: Proposal, validation: ValidationResult) -> ApprovalTier:
    # Auto-approve conditions
    if (proposal.type == ProposalType.CONSTANT_TUNE
        and proposal.risk == Risk.LOW
        and validation.status == ValidationStatus.PASSED
        and validation.improvement.get("target_metric", 0) > 0):
        return ApprovalTier.AUTO

    # Notify (auto but with notification)
    if (proposal.risk == Risk.LOW
        and validation.status == ValidationStatus.PASSED):
        return ApprovalTier.NOTIFY

    # Require human approval
    if (proposal.risk >= Risk.HIGH
        or proposal.type in [ProposalType.FORMULA_CHANGE, ProposalType.BEHAVIOR_FIX]
        or validation.status == ValidationStatus.INCONCLUSIVE):
        return ApprovalTier.REQUIRE

    # Default: queue for approval
    return ApprovalTier.APPROVE


class ApprovalTier(Enum):
    AUTO = "auto"         # Deploy immediately
    NOTIFY = "notify"     # Deploy and notify human
    APPROVE = "approve"   # Queue for human approval
    REQUIRE = "require"   # Block until human approves
```

### Human Approval Interface

```python
@dataclass
class ApprovalRequest:
    proposal: Proposal
    diagnosis: Diagnosis
    validation: ValidationResult

    # Human-readable summary
    summary: str
    rationale: str
    risk_assessment: str
    rollback_plan: str

    # Actions
    approve: Callable  # Human approves
    reject: Callable   # Human rejects
    modify: Callable   # Human modifies proposal
```

---

## PHASE 7: DEPLOY

### Deployment Execution

```python
async def deploy_proposal(proposal: Proposal, approval: Approval) -> DeploymentResult:
    # 1. Create backup
    backup = await create_backup(proposal.affected_files)

    # 2. Apply change
    try:
        await apply_change(proposal)
    except Exception as e:
        await restore_backup(backup)
        return DeploymentResult(status=DeploymentStatus.FAILED, error=e)

    # 3. Run verification tests
    verification = await run_verification_tests(proposal)
    if not verification.passed:
        await restore_backup(backup)
        return DeploymentResult(status=DeploymentStatus.FAILED, error=verification.error)

    # 4. Start monitoring
    monitor = await start_monitoring(proposal, duration=MONITOR_DURATION)

    # 5. Record deployment
    await record_deployment(proposal, approval, backup)

    return DeploymentResult(
        status=DeploymentStatus.SUCCESS,
        backup=backup,
        monitor=monitor,
    )
```

### Post-Deploy Monitoring

```python
async def monitor_deployment(deployment: Deployment, duration: Duration):
    baseline = deployment.baseline_metrics
    threshold = DEGRADATION_THRESHOLD

    start = time.now()
    while time.now() - start < duration:
        current = await collect_current_metrics()

        for metric, value in current.items():
            baseline_value = baseline.get(metric, value)
            degradation = (baseline_value - value) / baseline_value

            if degradation > threshold:
                await trigger_rollback(deployment, metric, degradation)
                return MonitorResult(status=MonitorStatus.ROLLED_BACK)

        await asyncio.sleep(MONITOR_INTERVAL)

    return MonitorResult(status=MonitorStatus.STABLE)
```

### Automatic Rollback

```python
async def trigger_rollback(deployment: Deployment, reason: str, severity: float):
    # 1. Restore backup
    await restore_backup(deployment.backup)

    # 2. Verify restoration
    verification = await run_verification_tests(deployment.proposal)

    # 3. Notify humans
    await notify_rollback(deployment, reason, severity)

    # 4. Mark proposal as failed
    await mark_proposal_failed(deployment.proposal, reason)

    # 5. Record for learning
    await record_failed_improvement(deployment, reason)
```

---

## PHASE 8: LEARN

### Learning Extraction

```python
async def learn_from_cycle(cycle: ImprovementCycle) -> LearningRecord:
    # 1. Record pattern → diagnosis mapping
    if cycle.diagnosis:
        await pattern_library.record_diagnosis(
            pattern=cycle.pattern,
            diagnosis=cycle.diagnosis,
        )

    # 2. Record successful fixes
    if cycle.deployment and cycle.deployment.status == DeploymentStatus.SUCCESS:
        await pattern_library.record_fix(
            pattern=cycle.pattern,
            proposal=cycle.proposal,
            outcome="success",
        )

    # 3. Record failed fixes (to avoid repeating)
    if cycle.deployment and cycle.deployment.status == DeploymentStatus.ROLLED_BACK:
        await pattern_library.record_fix(
            pattern=cycle.pattern,
            proposal=cycle.proposal,
            outcome="failed",
            reason=cycle.deployment.rollback_reason,
        )

    # 4. Update pattern recognition
    await pattern_library.update_recognition(cycle)

    return LearningRecord(
        cycle_id=cycle.id,
        pattern_recorded=bool(cycle.pattern),
        diagnosis_recorded=bool(cycle.diagnosis),
        fix_recorded=bool(cycle.deployment),
    )
```

### Pattern Library Operations

```python
class PatternLibrary:
    async def find_similar(self, pattern: Pattern) -> Optional[KnownPattern]:
        """Find known pattern similar to this one."""
        candidates = await self.search(pattern.embedding, top_k=5)
        for candidate in candidates:
            if similarity(pattern, candidate) > SIMILARITY_THRESHOLD:
                return candidate
        return None

    async def get_fix(self, known: KnownPattern) -> Optional[ProvenFix]:
        """Get proven fix for known pattern."""
        fixes = await self.get_fixes(known.id)
        successful = [f for f in fixes if f.outcome == "success"]
        if successful:
            return max(successful, key=lambda f: f.success_rate)
        return None

    async def record_diagnosis(self, pattern: Pattern, diagnosis: Diagnosis):
        """Record pattern → diagnosis mapping."""
        await self.store(PatternDiagnosis(
            pattern_embedding=pattern.embedding,
            pattern_type=pattern.type,
            root_layer=diagnosis.root_layer,
            evidence_summary=summarize(diagnosis.evidence),
        ))

    async def record_fix(self, pattern: Pattern, proposal: Proposal, outcome: str):
        """Record fix attempt and outcome."""
        await self.store(FixRecord(
            pattern_id=pattern.id,
            proposal_type=proposal.type,
            proposal_summary=summarize(proposal),
            outcome=outcome,
            timestamp=time.now(),
        ))
```

---

## KEY FORMULAS

| Formula | Purpose |
|---------|---------|
| `urgency = severity × recency × impact` | Prioritize improvement cycles |
| `pattern_score = occurrences × impact / noise` | Identify real patterns |
| `proposal_score = (impact × confidence) / (risk × complexity)` | Rank proposals |
| `improvement = (after - before) / before` | Measure change effect |
| `confidence = evidence_strength × known_pattern_bonus` | Diagnosis confidence |

---

## CONFIGURATION

| Config | Default | Purpose |
|--------|---------|---------|
| PATTERN_THRESHOLD | 3 | Min occurrences for pattern |
| DRIFT_THRESHOLD | 0.05 | Min trend for drift detection |
| CORRELATION_THRESHOLD | 0.7 | Min for correlation pattern |
| SHADOW_DURATION | 1h | Shadow mode test duration |
| CANARY_DURATION | 4h | Canary test duration |
| AB_DURATION | 24h | A/B test duration |
| MONITOR_DURATION | 24h | Post-deploy monitoring |
| DEGRADATION_THRESHOLD | 0.1 | Rollback trigger (10% degradation) |
| SIMILARITY_THRESHOLD | 0.8 | Pattern library matching |

---

## COMPLEXITY

| Operation | Time | Notes |
|-----------|------|-------|
| Signal collection | O(S × W) | S=sources, W=window size |
| Pattern detection | O(A²) | A=anomalies (clustering) |
| Layer attribution | O(L × E) | L=layers, E=evidence gathering |
| Proposal generation | O(P × D) | P=proposals, D=diagnosis depth |
| Validation | O(V × T) | V=validation ops, T=test duration |

**Bounded by:** Resource quotas, time limits per phase, concurrent cycle limits.
