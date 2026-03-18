# Vision — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Change detection effectiveness over real renders | CLIP cosine threshold needs real engine output, not synthetic images |
| Token budget adherence across 60+ citizens | Individual captures are cheap; aggregate cost emerges at scale |
| Flashbulb capture rate vs limbic delta distribution | Depends on real emotional dynamics, not fixtures |
| Engine render reliability over time | Transient failures only visible in production |

**Tests gate completion. Health monitors runtime.**

If behavior is deterministic with known inputs (FOV cone math, quaternion conversion) -- write a test.
If behavior emerges from real data over time (capture rate, change detection hit rate, token budget) -- write a health check.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the vision module's runtime behavior across 60+ citizens: capture rates, change detection effectiveness, flashbulb trigger fidelity, engine reliability, and token budget compliance. It exists to catch drift that unit tests cannot detect — a CLIP threshold that works in tests but produces too many false positives on real engine renders, or a capture rate that stays within budget per-citizen but exceeds it in aggregate.

Boundaries: this file does NOT verify FOV cone math (deterministic, tested), quaternion conversions (deterministic, tested), or CLIP model accuracy (external dependency, not our responsibility).

---

## WHY THIS PATTERN

Tests can verify that `vision_tick()` returns the correct output for a given input. But they cannot verify that change detection is actually saving tokens at scale, that flashbulb captures are firing at the right rate, or that the engine render API is reliable over hours of operation. These are emergent runtime properties that only health checks can monitor.

Docking-based checks are the right tradeoff because vision has clear input/output boundaries: each capture produces a VisionOutput and optionally a Moment node. Checking these outputs against VALIDATION invariants requires no changes to vision internals — just observing what comes out.

Throttling is critical because vision health checks themselves should not consume significant resources. A health check that renders screenshots to verify rendering would be self-defeating.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Vision.md
PATTERNS:        ./PATTERNS_Vision.md
BEHAVIORS:       ./BEHAVIORS_Vision.md
ALGORITHM:       ./ALGORITHM_Vision.md
VALIDATION:      ./VALIDATION_Vision.md
IMPLEMENTATION:  ./IMPLEMENTATION_Vision.md
THIS:            HEALTH_Vision.md
SYNC:            ./SYNC_Vision.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks/vision_health.py       # Python code implementing these checks (to be created)
  decorator: @check                               # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: vision_capture_pipeline
    purpose: "If this flow fails, citizens are blind — they cannot see their environment"
    triggers:
      - type: schedule
        source: runtime/cognition/vision.py:vision_tick()
        notes: "Called once per tick by the tick runner"
    frequency:
      expected_rate: "1 capture per 10 ticks per citizen (~6/hour at 60s/tick)"
      peak_rate: "1 capture per tick per citizen during high-activity periods (event triggers)"
      burst_behavior: "Multiple citizens may capture simultaneously; engine render queue handles backpressure"
    risks:
      - "V2: Change detection threshold too low → excessive captures → token waste"
      - "V2: Change detection threshold too high → missed significant changes → blind citizen"
      - "V7: Engine render timeout → stalled tick loop"
      - "V3: CLIP inference failure → visual Moments without embeddings"
    notes: "Cross-boundary: engine render (external API), CLIP model (external inference), object storage (file write)"

  - flow_id: flashbulb_capture
    purpose: "If flashbulb fails to fire, emotional peaks have no visual record"
    triggers:
      - type: event
        source: runtime/cognition/interoception.py:limbic_delta
        notes: "Triggered when |limbic_delta| > FLASHBULB_THRESHOLD (0.7)"
    frequency:
      expected_rate: "0-3 per citizen per day (depends on emotional dynamics)"
      peak_rate: "1 per 30 ticks per citizen (cooldown enforced)"
      burst_behavior: "Cooldown prevents rapid-fire; at most 1 flashbulb per 30 ticks"
    risks:
      - "V4: Flashbulb condition met but capture skipped"
      - "V4: Flashbulb Moment created with wrong weight (not 3.0)"
    notes: "Must coordinate with Law 6 triple consolidation"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Token efficiency (O2) | capture_rate, change_detection_hit_rate | If these degrade, token budget explodes |
| Visual memories (O3) | embedding_coverage | If embeddings are missing, visual memories are dead weight |
| Flashbulb vision (O5) | flashbulb_fidelity | If flashbulbs don't fire, emotional peaks have no visual record |
| System stability (O1) | render_reliability, tick_latency | If these degrade, citizens go blind or the system stalls |

```yaml
health_indicators:
  - name: capture_rate
    flow_id: vision_capture_pipeline
    priority: high
    rationale: "If capture rate exceeds budget, token costs become unsustainable at 60+ citizens"

  - name: change_detection_hit_rate
    flow_id: vision_capture_pipeline
    priority: high
    rationale: "If change detection suppresses too few frames, tokens are wasted; if too many, citizens miss changes"

  - name: embedding_coverage
    flow_id: vision_capture_pipeline
    priority: high
    rationale: "Visual Moments without CLIP embeddings cannot participate in physics (Sim_vis = 0)"

  - name: flashbulb_fidelity
    flow_id: flashbulb_capture
    priority: high
    rationale: "Flashbulb captures at emotional peaks are the vision module's highest-value output"

  - name: render_reliability
    flow_id: vision_capture_pipeline
    priority: med
    rationale: "If engine renders fail, citizens lose vision; intermittent failures are normal but sustained failure is critical"

  - name: tick_latency
    flow_id: vision_capture_pipeline
    priority: high
    rationale: "If vision_tick() exceeds 5000ms, it stalls the tick loop and blocks all other cognition"
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/checks/vision_health.py
  result:
    representation: enum
    value: UNKNOWN
    updated_at: "2026-03-18T00:00:00Z"
    source: vision_health_aggregate
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: vision_capture_rate_checker
    purpose: "Verify capture rate stays within budget (V2)"
    status: pending
    priority: high

  - name: vision_change_detection_checker
    purpose: "Verify change detection is suppressing static frames (V2)"
    status: pending
    priority: high

  - name: vision_embedding_coverage_checker
    purpose: "Verify all visual Moments have CLIP embeddings (V3)"
    status: pending
    priority: high

  - name: vision_flashbulb_fidelity_checker
    purpose: "Verify flashbulb captures fire at emotional peaks (V4)"
    status: pending
    priority: high

  - name: vision_render_reliability_checker
    purpose: "Verify engine render API is responding reliably (V7, V8)"
    status: pending
    priority: med

  - name: vision_tick_latency_checker
    purpose: "Verify vision_tick() stays under 5000ms (V7)"
    status: pending
    priority: high
```

---

## INDICATOR: capture_rate

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: capture_rate
  client_value: "If capture rate exceeds budget, the system burns through tokens and becomes economically unviable"
  validation:
    - validation_id: V2
      criteria: "No token waste on static scenes; captures gated by change detection and periodic timer"
    - validation_id: V5
      criteria: "At most one capture per tick per citizen"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: "Ratio of actual captures to maximum possible captures. Expected: 0.05-0.15 (5-15% of ticks produce captures). Above 0.3 = likely change detection failure."
  aggregation:
    method: "Average across all citizens"
    display: "float_0_1 surfaced as percentage"
```

### SIGNALS

```yaml
signals:
  healthy: "Capture rate per citizen is between 0.02 and 0.20 (2-20% of ticks)"
  degraded: "Capture rate per citizen exceeds 0.20 but below 0.50"
  critical: "Capture rate per citizen exceeds 0.50 (capturing more than half of all ticks)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "Every 100 ticks"
  max_frequency: "1 check per 100 ticks"
  burst_limit: 1
  backoff: "If critical, check every 50 ticks; if degraded, check every 100 ticks; if healthy, check every 200 ticks"
```

---

## INDICATOR: embedding_coverage

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: embedding_coverage
  client_value: "Visual Moments without embeddings are dead weight in the graph — they exist but contribute nothing to physics"
  validation:
    - validation_id: V3
      criteria: "Every stored visual has a CLIP embedding"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: "Ratio of visual Moments with media.image.embedding to total visual Moments. Expected: 1.0. Below 0.95 indicates CLIP inference issues."
  aggregation:
    method: "Count across all citizens"
    display: "float_0_1 surfaced as percentage"
```

### SIGNALS

```yaml
signals:
  healthy: "100% of visual Moments have CLIP embeddings"
  degraded: "95-99% of visual Moments have CLIP embeddings"
  critical: "Below 95% of visual Moments have CLIP embeddings"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "Every 500 ticks"
  max_frequency: "1 check per 500 ticks"
  burst_limit: 1
  backoff: "None — always check at cadence"
```

---

## INDICATOR: flashbulb_fidelity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: flashbulb_fidelity
  client_value: "Flashbulb captures are the highest-value visual memories — emotional peaks without visual records are lost experiences"
  validation:
    - validation_id: V4
      criteria: "When |limbic_delta| > 0.7, a screenshot is captured with triple weight and subtype vision"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: "Ratio of flashbulb captures to flashbulb-eligible ticks (ticks where limbic_delta > 0.7 and cooldown is not active). Expected: 1.0."
  aggregation:
    method: "Count across all citizens"
    display: "float_0_1 surfaced as percentage"
```

### SIGNALS

```yaml
signals:
  healthy: "100% of flashbulb-eligible ticks produce captures"
  degraded: "90-99% of flashbulb-eligible ticks produce captures"
  critical: "Below 90% of flashbulb-eligible ticks produce captures"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "Every 500 ticks"
  max_frequency: "1 check per 500 ticks"
  burst_limit: 1
  backoff: "None — always check at cadence"
```

---

## HOW TO RUN

```bash
# Run all health checks for the vision module
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks.vision_health --all

# Run a specific checker
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks.vision_health --checker vision_capture_rate_checker
```

---

## KNOWN GAPS

<!-- @mind:todo No checker yet for V1 (FOV derives from body state). This is deterministic and should be a unit test, not a health check. But worth confirming that the body model's head height offset matches the config value in production. -->

<!-- @mind:todo No checker yet for V6 (screenshot reaches the LLM). This requires observing the LLM prompt assembly, which is outside the vision module's boundary. May need a cross-module health check or a contract test with the prompt assembler. -->

<!-- @mind:todo No checker yet for V8 (render API failure is loud). Need to verify that engine errors surface in logs. Could be a log-scanning health check that looks for vision render error patterns. -->

---

## MARKERS

<!-- @mind:todo Implement all 6 checkers in runtime/checks/vision_health.py once the vision module itself is implemented. Checkers depend on VisionState statistics (total_captures, total_skipped, total_flashbulbs) being accessible. -->

<!-- @mind:proposition Consider a "visual diversity" health indicator that measures how varied a citizen's visual Moments are over time. A citizen who only ever sees the same scene (low CLIP embedding variance) may indicate a pathological state (stuck in one location, or change detection is too aggressive). -->

<!-- @mind:escalation The tick_latency checker needs access to timing data from vision_tick(). Should vision_tick() instrument itself with timing, or should the tick runner measure it externally? The former is simpler but adds overhead; the latter is cleaner but requires tick runner changes. -->
