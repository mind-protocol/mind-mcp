# Process: Designing RESULTS for a Module

```
STATUS: CANONICAL
CREATED: 2026-03-19
AUTHOR: @mechanical_visionary (guest session)
```

---

## What This Is

A step-by-step process for writing a RESULTS file for any module. RESULTS sits at the TOP of the doc chain — every objective, sense, behavior, and health signal traces back to a result. Without RESULTS, the guarantee loop is open and the module has no definition of success.

This process produces a RESULTS YAML that follows `templates/results.yaml` exactly and closes the guarantee loop: RESULT → SENSE → HEALTH → CARRIER.

---

## When To Use

- A module exists with OBJECTIVES/BEHAVIORS/SENSES but no RESULTS → use this process
- A new module is being created → use this BEFORE writing OBJECTIVES
- A module's senses fire but nobody knows what "success" means → use this

---

## Prerequisites

Before starting, you need:

1. **The module's OBJECTIVES file** — what the module is trying to achieve (ranked priorities)
2. **The module's BEHAVIORS file** (if it exists) — what observable effects the module produces
3. **The module's SENSES file** (if it exists) — what's currently being measured
4. **The templates:** `templates/results.yaml` and `templates/sense.yaml`

If OBJECTIVES doesn't exist, write it first. You can't define success without knowing the goal.

---

## The Process

### Step 1: Ask the Existence Question

For the module, complete this sentence:

> "If this module didn't exist, what would break or be missing?"

Write down the answer in plain language. Not technical. Not about code. About IMPACT.

**Examples:**
- Attention engine: "Nobody would notice when a citizen goes dormant or a partner is ready to convert."
- Video selfie pipeline: "Citizens would have no way to show themselves to their human partners."
- Relance cadence: "Citizens would either spam partners or never reach out — no balance."

This answer IS your first result candidate. The module exists to prevent that breakage.

### Step 2: Convert Impact to Observable Outcomes

For each impact from Step 1, ask:

> "How would a stranger verify this is working, without reading the code?"

The answer must be:
- **Observable** — you can see it happening (or not happening)
- **Measurable** — you can put a number on it
- **Time-bounded** — over what window is it measured

**Template:**
```
ACHIEVED: "{What you'd see if it works — specific scenario with actors and actions}"
NOT_ACHIEVED: "{What you'd see if it doesn't — the bad scenario}"
```

**Example (attention engine):**
```
ACHIEVED: "@forge goes dark → @dragon_slayer + @mentor know within 10 minutes without checking."
NOT_ACHIEVED: "Citizens disappear for days. Nobody notices until someone asks 'where's @forge?'"
```

### Step 3: Define the Threshold

For each outcome, ask:

> "What number separates success from failure?"

Four fields:
- **metric:** what is measured (a specific variable, not a vague concept)
- **target:** the number (specific, not "high" or "good")
- **window:** over what timeframe (per event, 7 days, 30 days, per tick)
- **direction:** above, below, or equal

**How to pick the target:**
1. If you have historical data → use the current performance as baseline, set target 20% better
2. If you have no data → set a reasonable target, mark status as `calibrating`, adjust after 2 weeks
3. If you're unsure → set TWO targets: a "good enough" target (P1) and an "excellent" target (P0)

**Warning:** Don't pick a target you can't measure. If no sense exists to measure it, either create the sense or pick a different metric. A result without a sense is a wish.

### Step 4: Wire the Guarantee Loop

For each result, fill in three mandatory links:

```yaml
proved_by:      # Which sense(s) measure this result?
  - "sense:scope:slug"

health_signal:  # Which health checker verifies the sense is running?
  - "H1"

measured_by:    # Which objective node in L3 carries the weight?
  - objective: "narrative:obj:slug"
    green: 0.7   # above this = achieved
    red: 0.3     # below this = failing
```

**Rules:**
- Every result MUST have at least one sense in `proved_by`
- Every result MUST have at least one health signal in `health_signal`
- If the sense doesn't exist yet → note it, create it next. But name it now.
- If the health checker doesn't exist yet → note it. But name it now.

The names can be provisional. The point is: the loop is drawn even if the implementation is pending.

### Step 5: Write the Failure Diagnostic

For each result, write a 3-level diagnostic:

```yaml
failure_diagnostic: |
  If this result is not met:
  1. Local: {check the immediate cause — is the measurement correct?}
  2. Upstream: {check the dependency — is the input to this result healthy?}
  3. Systemic: {check the infrastructure — is the substrate working?}
```

This is the "what to do when the light goes red" guide. Write it as if you're explaining to someone who has never seen the module. The three levels (local → upstream → systemic) ensure they don't jump to "rebuild everything" when the problem is a misconfigured threshold.

### Step 6: Assign Priority and Ownership

```yaml
priority: P0 | P1 | P2
owner: "@citizen_handle"
```

- **P0:** If this result fails, the module has no reason to exist
- **P1:** Module works but isn't achieving its purpose
- **P2:** Quality or efficiency gap

Owner = the citizen who FEELS this result in their awareness. Usually the module lead or the citizen whose domain this is.

### Step 7: Fill the Completeness Matrix

At the bottom of the RESULTS file, add the matrix:

```
| Result | Sense (proved_by) | Health (health_signal) | Carrier | Status |
|--------|-------------------|------------------------|---------|--------|
| R1     | sense:x:y         | H1                     | @citizen | wired/pending |
```

Every row must be filled. Every column must have a value (even if "PENDING"). This is how you track whether the loop is closed.

---

## Quality Checklist

Before shipping a RESULTS file, verify:

- [ ] Every result traces to an OBJECTIVE (traces_to field)
- [ ] Every result has an ACHIEVED and NOT_ACHIEVED scenario that a stranger could verify
- [ ] Every threshold has a specific metric, target, window, and direction
- [ ] Every result has at least one sense in proved_by (even if the sense is "PENDING — to create")
- [ ] Every result has at least one health signal (even if "PENDING")
- [ ] Every result has a 3-level failure diagnostic (local, upstream, systemic)
- [ ] Priority is assigned (P0/P1/P2)
- [ ] Owner is assigned (who feels this)
- [ ] Completeness matrix is filled
- [ ] The file follows `templates/results.yaml` format exactly

---

## Common Mistakes

### Mistake 1: Results that describe features, not outcomes

```
BAD:  "Authentication module is deployed"          → that's IMPLEMENTATION
GOOD: "99.5% of login attempts resolve within 2s"  → that's an OUTCOME
```

### Mistake 2: Thresholds you can't measure

```
BAD:  metric: "user satisfaction"     → how do you measure that continuously?
GOOD: metric: "response_rate_24h"     → concrete, measurable by a sense
```

### Mistake 3: Results without senses

```
BAD:  proved_by: []                   → a promise nobody is keeping
GOOD: proved_by: ["sense:lp:response_rate"]  → even if the sense is PENDING
```

### Mistake 4: Results that are too granular

```
BAD:  "The decay rate is exactly 0.02 per tick"     → that's VALIDATION
GOOD: "Attention fades without reinforcement"         → that's a result
```

A result is what the USER or PARTNER would notice. Validation is what the CODE must guarantee. Don't confuse them.

### Mistake 5: All results at P0

If everything is P0, nothing is P0. A module should have 1-2 P0 results (existential), 1-2 P1 (important), and 0-2 P2 (quality). If you have 5 P0 results, you haven't prioritized.

---

## Example: Applying This Process to the Attention Engine

### Step 1: Existence question
"If the attention engine didn't exist, nobody would notice when citizens go dormant, partners are ready to convert, infrastructure is degraded, or personhood tiers are wrong."

### Step 2: Observable outcomes
- R1: "Activity changes detected within 10 minutes" — @forge goes dark → someone knows in 10 min
- R2: "Conversion offered at the right moment" — f1 score > 0.6
- R3: "At-risk partners saved before churn" — churn < 20%/month
- R4: "Personhood tiers differentiate citizens" — tier score σ > 1.5

### Step 3: Thresholds
- R1: detection_latency_minutes < 10, per_event
- R2: conversion_f1_score > 0.6, 30d window
- R3: monthly_churn_rate < 0.20, 30d window
- R4: tier_score_std_dev > 1.5, per_assessment

### Step 4: Guarantee loop
- R1 → sense:ae:activity_delta → H_activity_scanner → @dragon_slayer
- R2 → sense:ae:conversion_precision → H_conversion_checker → @mentor
- R3 → sense:ae:churn_prevention → H_churn_checker → @mentor
- R4 → sense:ae:personhood_calibration → H_personhood_checker → @dragon_slayer

### Step 5: Failure diagnostics
Each result gets local/upstream/systemic diagnosis. (See templates/results.yaml example section for the full attention engine example.)

### Step 6: Priority
- R1: P0 (without detection, the engine has no purpose)
- R2: P0 (conversion is the revenue path)
- R3: P1 (churn prevention is important but not existential)
- R4: P1 (differentiation proves value but isn't revenue-critical)

---

## After Writing RESULTS

1. **Update SYNC** — add the GUARANTEE LOOP STATUS table showing which results are wired
2. **Create missing senses** — if proved_by points to senses that don't exist, create them next
3. **Create missing health checkers** — if health_signal points to checkers that don't exist, add to HEALTH
4. **Wire in L3** — create objective nodes, link senses via CONTRIBUTES_TO, assign carriers via PERCEIVES_WITH
5. **Broadcast to module owner** — the owner should review and confirm the thresholds make sense for their domain

---

## The Standard

A module is NOT complete until:
- Every RESULT has a SENSE proving it
- Every SENSE has a HEALTH signal verifying it
- Every HEALTH signal has a CARRIER who feels it
- The COMPLETENESS MATRIX shows all rows as "wired"

This is the guarantee loop. It's mandatory. An open loop means the system THINKS it's healthy but might not be. The Popen bug (2026-03-19) proved what happens when the loop is open: 98.8% failure rate, invisible for hours.

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
