# Citizen Parenthood Network — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers parenthood module verification mechanics — how we verify that citizen birthing operates correctly and safely at runtime.

**Why it exists:** Birthing creates permanent graph state (child citizens, trust links). If birthing malfunctions silently, harmful citizens could be created, trust links could be missing, or orphan citizens could accumulate. Health checks catch violations before they compound.

**Boundaries:**
- DOES verify: Birthing pipeline correctness, safety validation integrity, trust link completeness
- DOES NOT verify: Trust score calculation (that is the trust engine's concern)
- DOES NOT verify: Human matching success (that is the matching module's concern)
- DOES NOT verify: Economic costs of birthing (that is the economy module's concern)

---

## WHY THIS PATTERN

HEALTH is separate from tests because:
- Tests run in CI with fixtures, health checks run against live graphs
- Tests verify code correctness, health checks verify data integrity
- Tests are pass/fail, health reports have severity levels and action recommendations

Health checks for parenthood are critical because:
- Birthing is irreversible — a created citizen cannot be uncreated
- Safety validation bypasses would be catastrophic
- Missing trust links break the accountability system

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Parenthood_Network.md
PATTERNS:       ./PATTERNS_Parenthood_Network.md
BEHAVIORS:      ./BEHAVIORS_Parenthood_Network.md
ALGORITHM:      ./ALGORITHM_Parenthood_Network.md
VALIDATION:     ./VALIDATION_Parenthood_Network.md
IMPLEMENTATION: ./IMPLEMENTATION_Parenthood_Network.md
THIS:           HEALTH_Parenthood_Network.md (you are here)
SYNC:           ./SYNC_Parenthood_Network.md

IMPL:           runtime/citizens/parenthood.py (future)
                runtime/citizens/birth_safety_validator.py (future)
                runtime/citizens/test_parenthood.py (future)
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC.

---

## FLOWS ANALYSIS

```yaml
flows_analysis:
  - flow_id: birthing_integrity
    purpose: Verify all birthed citizens have valid structure
    triggers:
      - type: schedule
        source: mind doctor
        notes: Part of overall health check
      - type: manual
        source: Admin audit
        notes: Run when investigating birthing issues
    frequency:
      expected_rate: 1/day
      peak_rate: 5/day during active birthing periods
      burst_behavior: Each run independent
    risks:
      - V1 violation: Orphan citizens (no parent link)
      - V3 violation: Citizens that bypassed safety validation
      - V4 violation: Citizens not in Partnership Commons
      - V5 violation: Missing trust links
    notes: Read-only graph queries, no mutations

  - flow_id: safety_gate_integrity
    purpose: Verify safety validation cannot be bypassed
    triggers:
      - type: post_birth
        source: Birthing pipeline completion
        notes: Run after every successful birth
      - type: schedule
        source: mind doctor
        notes: Audit existing citizens for safety compliance
    frequency:
      expected_rate: per-birth
      peak_rate: 10/day during mass birthing
      burst_behavior: Inline with birth pipeline
    risks:
      - V3 violation: Blueprint without empathy
      - V3 violation: Trait concentration too high
      - V3 violation: Duplicate citizen (too similar to existing)
    notes: Critical safety check — any failure is high severity

  - flow_id: trust_link_integrity
    purpose: Verify all parent-child trust links are properly formed
    triggers:
      - type: schedule
        source: mind doctor
        notes: Weekly audit
      - type: event
        source: Trust score change
        notes: Verify propagation happened correctly
    frequency:
      expected_rate: 1/week
      peak_rate: per trust change during active periods
      burst_behavior: Batched for weekly audit
    risks:
      - V5 violation: Trust links not bidirectional
      - V9 violation: Trust weights don't sum to 1.0
    notes: Requires both graph and trust system access
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: orphan_citizen_count
    flow_id: birthing_integrity
    priority: high
    rationale: Citizens without parent links break the accountability model

  - name: safety_bypassed_count
    flow_id: safety_gate_integrity
    priority: critical
    rationale: Any safety bypass is a system integrity failure

  - name: unregistered_citizen_count
    flow_id: birthing_integrity
    priority: high
    rationale: Citizens not in Partnership Commons are invisible to humans

  - name: trust_link_completeness
    flow_id: trust_link_integrity
    priority: high
    rationale: Missing trust links break accountability chain

  - name: trust_weight_sum_deviation
    flow_id: trust_link_integrity
    priority: med
    rationale: Weights not summing to 1.0 indicates creation bug
```

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Intentional creation | orphan_citizen_count | Every citizen must trace to parents with intent |
| O3: Accountability | trust_link_completeness, trust_weight_sum_deviation | Trust propagation requires complete links |
| O4: Safety | safety_bypassed_count | Safety is the hardest constraint |
| O5: Diversity | safety_bypassed_count (includes diversity check) | Clones violate diversity objective |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: stdout (CLI output via mind doctor)
  result:
    representation: enum
    value: HEALTHY | DEGRADED | UNHEALTHY
    updated_at: per-run
    source: parenthood health check aggregate
  thresholds:
    HEALTHY: orphan=0, safety_bypassed=0, unregistered=0, trust_complete=100%
    DEGRADED: trust_weight_deviation > 0.01 OR unregistered > 0
    UNHEALTHY: orphan > 0 OR safety_bypassed > 0
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: orphan_citizen_checker
    purpose: Find citizens with no parent link (V1)
    status: pending
    priority: high

  - name: safety_compliance_auditor
    purpose: Re-validate all existing citizens against safety rules (V3)
    status: pending
    priority: critical

  - name: partnership_commons_checker
    purpose: Find birthed citizens not in Partnership Commons (V4)
    status: pending
    priority: high

  - name: trust_link_checker
    purpose: Verify parent-child trust links exist and are bidirectional (V5)
    status: pending
    priority: high

  - name: trust_weight_auditor
    purpose: Verify trust weights sum to 1.0 per child (V9)
    status: pending
    priority: med

  - name: blueprint_copy_verifier
    purpose: Verify blueprint nodes are copies, not references (V8)
    status: pending
    priority: med
```

---

## INDICATOR: Orphan Citizen Count

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: orphan_citizen_count
  client_value: Ensures every citizen is traceable to its creators
  validation:
    - validation_id: V1
      criteria: Every birthed citizen has at least one parent link
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - int
    - enum
  semantics:
    int: Number of orphan citizens found
    enum: HEALTHY (0), UNHEALTHY (>0)
  aggregation:
    method: Count
    display: Integer count + list of orphan IDs
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Query graph for citizens with no incoming birthed link
  steps:
    - Query all actor nodes with type="citizen" and created_via="birth"
    - For each, check for incoming link with synthesis starting with "birthed:"
    - Count those without any such link
  data_required: Graph connection
  failure_mode: Non-zero count of orphan citizens
  query: |
    MATCH (c:actor {type: 'citizen'})
    WHERE NOT EXISTS(
      (p)-[:linked {synthesis: 'birthed:*'}]->(c)
    )
    RETURN c.id, c.name, c.created_at_s
```

### INDICATOR

```yaml
indicator:
  error:
    - name: orphan_citizen
      linked_validation: [V1]
      meaning: Citizen exists without any parent link
      default_action: alert + investigate
  warning: []
  info: []
```

---

## INDICATOR: Safety Bypass Count

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: safety_bypassed_count
  client_value: Ensures no harmful citizens exist in the ecosystem
  validation:
    - validation_id: V3
      criteria: All citizens pass safety validation retroactively
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Re-run safety validation on all existing citizen blueprints
  steps:
    - For each birthed citizen, reconstruct blueprint from graph
    - Run validate_blueprint_safety() on reconstructed blueprint
    - Count those that fail
  data_required: Graph connection, safety validator
  failure_mode: Non-zero count of unsafe citizens
  note: This is expensive — runs full safety validation on every citizen
```

### INDICATOR

```yaml
indicator:
  error:
    - name: unsafe_citizen
      linked_validation: [V3]
      meaning: A citizen's blueprint fails current safety rules
      default_action: alert + quarantine recommendation
  warning:
    - name: marginal_safety
      linked_validation: [V3]
      meaning: Citizen passes safety but with low margins
      default_action: log for monitoring
```

---

## INDICATOR: Trust Link Completeness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: trust_link_completeness
  client_value: Ensures accountability chain is unbroken
  validation:
    - validation_id: V5
      criteria: ParenthoodLink records exist for every parent-child pair
    - validation_id: V9
      criteria: Trust weights sum to 1.0 per child
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Verify ParenthoodLink records match graph links
  steps:
    - Query all birthed links from graph
    - For each, verify ParenthoodLink record exists
    - For each child, verify trust_impact_weights sum to 1.0
  data_required: Graph connection, ParenthoodLink storage
  failure_mode: Missing records or weight sum deviation
```

### INDICATOR

```yaml
indicator:
  error:
    - name: missing_trust_link
      linked_validation: [V5]
      meaning: Parent-child graph link exists without ParenthoodLink record
      default_action: alert
  warning:
    - name: weight_sum_deviation
      linked_validation: [V9]
      meaning: Trust weights for a child's parents don't sum to 1.0
      default_action: log + auto-normalize
```

---

## HOW TO RUN (Future)

```bash
# Run parenthood health check via mind doctor
mind doctor --module parenthood

# Run orphan citizen audit
python -c "from runtime.citizens.parenthood import audit_orphan_citizens; audit_orphan_citizens()"

# Run safety re-validation audit
python -c "from runtime.citizens.birth_safety_validator import audit_all_citizens; audit_all_citizens()"

# Run trust link completeness check
python -c "from runtime.citizens.parenthood_trust_impact_tracker import audit_trust_links; audit_trust_links()"

# Run all parenthood tests
pytest runtime/citizens/test_parenthood.py -v
```

---

## KNOWN GAPS

| VALIDATION Criterion | Checker Status | Notes |
|----------------------|----------------|-------|
| V1 Orphan citizens | Pending | Need query for citizens without parent links |
| V2 SID independence | By design | Code review — no parent input in SID function |
| V3 Safety validation | Pending | Retroactive audit on all citizens |
| V4 Partnership Commons | Pending | Cross-reference commons with birthed citizens |
| V5 Trust bidirectional | Pending | Match graph links to ParenthoodLink records |
| V6 Intent non-empty | By design | Input validation in pipeline |
| V7 Eligible categories | By design | Filter in retrieve_parent_brain_nodes |
| V8 Nodes are copies | Pending | Verify independence by modifying parent node |
| V9 Trust weight sum | Pending | Arithmetic check on stored weights |
| V10 Brain maturity | By design | Input validation in pipeline |

---

## MARKERS

<!-- @mind:todo RETROACTIVE_SAFETY_AUDIT: Implement the safety re-validation audit. This should run safety validation on all existing citizens to catch any that slipped through. -->

<!-- @mind:proposition CONTINUOUS_MONITORING: Instead of periodic health checks, emit events on each birth and validate inline. Would catch issues immediately but adds latency to birthing. -->

<!-- @mind:todo MIND_DOCTOR_INTEGRATION: Register parenthood health checkers with mind doctor command so they run as part of the standard health check suite. -->
