# HEALTH: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
      BEHAVIORS_{Module_Name}.md
        ALGORITHM_{Module_Name}.md
          VALIDATION_{Module_Name}.md
            IMPLEMENTATION_{Module_Name}.md
→             HEALTH (you are here)
                → SYNC_{Module_Name}.md

IMPL: {path/to/health_checks.py}
```

---

## WHEN TO USE HEALTH vs TESTS

- **Tests** = deterministic assertions, run on code changes, pass/fail.
- **Health** = runtime verification, detects drift, uses real graph data, reports state.

Health checks answer: "Is this module behaving correctly RIGHT NOW with real data?"

## PURPOSE

{What this health file covers. Which flows, which objectives, which risks it reduces.}

## IMPLEMENTS

```
Runtime path: {runtime/checks.py or equivalent}
Registration: @health_check decorator or equivalent
```

## FLOWS ANALYSIS

Which flows through this module are critical and need monitoring.

| Flow | Trigger | Frequency (expected) | Frequency (peak) | Risk | Priority |
|------|---------|---------------------|-------------------|------|----------|
| {flow name} | {event/schedule/manual} | {N/tick, N/hour} | {N/tick, N/hour} | {what goes wrong} | CRITICAL / HIGH / MEDIUM |

## PATHOLOGIES

Abnormal states this module can enter. Inspired by the cognitive pathology model (ref: HEALTH_L1_Cognition.md).

### P1: {Pathology name}

**Symptom:** {what you observe — graph state, metric anomaly, behavioral change}
**Root cause:** {which invariant is violated, which physics law is miscalibrated}
**Detection:** {specific metric or graph query}
**Schema signals:** {which NodeBase/LinkBase/drive fields indicate this}
**Severity:** CRITICAL | WARNING | INFO
**Response:** {what to do — auto-correct, alert, escalate}

### P2: {Pathology name}

{Same format.}

## HEALTH INDICATORS

Metrics derived from graph state that signal module health.

### H1: {Indicator name}

**Client value:** {why someone cares about this indicator}
**Validation mapping:** {which invariant (V{N}) this monitors}
**Schema fields:** {which NodeBase/LinkBase/drive fields are measured}
**Physics laws:** {which laws this indicator reflects — L{N}}

**Representation:**
- Allowed: {gauge / counter / histogram / boolean / ratio}
- Selected: {chosen representation}
- Semantics: {what the number means — e.g., "ratio of nodes with energy > 0.1"}

**Thresholds:**
- Healthy: {range or condition}
- Warning: {range or condition}
- Critical: {range or condition}

**Dock:**
- Type: {graph_ops / file / api / event / stream / scheduler / process}
- Read: {Cypher query or function call to get the data}
- Frequency: {how often to check}

### H2: {Indicator name}

{Same format.}

## CHECKER INDEX

| Checker | Purpose | Status | Priority | Indicator | Validation |
|---------|---------|--------|----------|-----------|------------|
| {check_name} | {what it verifies} | ACTIVE / PENDING | CRITICAL / HIGH / MEDIUM | H{N} | V{N} |

## INTERVENTION TIERS

Graduated responses to health degradation. Inspired by T0–T4 model.

| Tier | Trigger | Action | Automated? |
|------|---------|--------|------------|
| T0: Observe | {metric crosses warning threshold} | Log, track trend | Yes |
| T1: Nudge | {metric persists at warning for N ticks} | {light correction — adjust constant, reset counter} | Yes |
| T2: Intervene | {metric crosses critical threshold} | {stronger correction — prune, rebalance, force law execution} | Yes |
| T3: Escalate | {T2 failed to correct} | {create task, alert human, pause module} | Partial |
| T4: Override | {module causing system-wide degradation} | {disable module, fallback to safe state} | Manual |

## HOW TO RUN

```bash
# All health checks for this module
{command to run all checks}

# Specific checker
{command to run one check}

# Health report
{command to generate health report}
```

## KNOWN GAPS

Validation invariants not yet covered by health checks.

| Invariant | Why not covered | Plan |
|-----------|----------------|------|
| V{N} | {reason} | {when/how to add} |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
