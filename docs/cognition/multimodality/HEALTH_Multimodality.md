# Multimodality — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Coherence score distribution drift | Needs real graph data across many ticks, not fixtures |
| Weight redistribution balance | Emergent from actual modality coverage across citizen graphs |
| Embedding dimension consistency | Real nodes may have stale embeddings from old model versions |
| Media dict serialization integrity | FalkorDB serialization behavior under real data volumes |

**Tests gate completion. Health monitors runtime.**

If behavior is deterministic with known inputs -> write a test.
If behavior emerges from real data over time -> write a health check.

See `VALIDATION_Multimodality.md` for the full distinction.

---

## PURPOSE OF THIS FILE

This HEALTH file covers the multimodal system's runtime verification: ensuring that media attachments, coherence computation, weight distribution, and backward compatibility remain correct as citizens accumulate real media data over time.

It exists because multimodal coherence behavior depends on the actual distribution of modalities across a citizen's graph — something tests with fixtures cannot fully predict. A citizen with 200 text-only nodes and 3 image nodes will have very different weight redistribution patterns than a citizen with balanced media coverage.

**Boundaries:** This file verifies multimodal-specific invariants (V1-V8 from VALIDATION). It does NOT verify general coherence quality (that belongs to Law 8 health), FalkorDB storage health (that belongs to infrastructure health), or embedding model quality (that belongs to the model adapter's health).

---

## WHY THIS PATTERN

Tests verify that `compute_multimodal_coherence()` returns correct values for known inputs. But they cannot verify that, across a real citizen's graph with thousands of nodes and heterogeneous modality coverage, the coherence formula produces reasonable distributions. Docking-based health checks can sample real nodes, compute real coherence, and verify that the output stays within expected bounds — without modifying any implementation files.

Throttling protects against health checks themselves becoming a performance burden. The coherence function is called many times per tick. A health check that re-computes coherence for sampling purposes must be infrequent enough to not impact tick performance.

---

## HOW TO USE THIS TEMPLATE

Confirmation: the full chain was read (OBJECTIVES through IMPLEMENTATION). The flows covered are:

1. **multimodal_coherence** — the coherence computation flow, because invalid coherence corrupts WM selection
2. **media_write** — the attachment validation flow, because bad data entering the graph is hard to fix later

Indicators maintained:
- `coherence_validity` — V2 (always valid float)
- `weight_balance` — V5 (weights sum correctly)
- `no_binary_blobs` — V1 (URI only, no inline data)
- `legacy_shim_accuracy` — V6 (v2.2 fields read correctly)

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Multimodality.md
PATTERNS:        ./PATTERNS_Multimodality.md
BEHAVIORS:       ./BEHAVIORS_Multimodality.md
ALGORITHM:       ./ALGORITHM_Multimodality.md
VALIDATION:      ./VALIDATION_Multimodality.md
IMPLEMENTATION:  ./IMPLEMENTATION_Multimodality.md
THIS:            HEALTH_Multimodality.md (you are here)
SYNC:            ./SYNC_Multimodality.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks/multimodal_health_checks.py   # To be created
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: multimodal_coherence
    purpose: "Coherence score drives WM selection. Invalid scores corrupt consciousness state for the citizen."
    triggers:
      - type: event
        source: runtime/physics/exploration.py:compute_coherence()
        notes: "Triggered every time Law 8 evaluates coherence between two nodes during tick"
    frequency:
      expected_rate: "50-200/tick (depends on graph size and WM candidates)"
      peak_rate: "500/tick (large graph with many active nodes)"
      burst_behavior: "No retries. Each coherence computation is independent. Burst = large tick."
    risks:
      - "V2: NaN or infinity from zero-norm vectors"
      - "V3: Dimension mismatch from stale embeddings"
      - "V5: Weight redistribution error causing sum != 1.0"
    notes: "Hot path. Health checks must sample, never instrument every call."

  - flow_id: media_write
    purpose: "Media attachments entering the graph with invalid data (binary blobs, wrong dims) are hard to fix retroactively."
    triggers:
      - type: event
        source: mcp/tools/graph_write_handler.py:handle_graph_write()
        notes: "Triggered on node creation/update with media payload via MCP"
    frequency:
      expected_rate: "1-5/min (media attachments are less frequent than text-only writes)"
      peak_rate: "20/min (batch media import)"
      burst_behavior: "Each write is independent. No queuing or backpressure."
    risks:
      - "V1: Binary blob smuggled past validation"
      - "V3: Embedding dimensions not matching registry"
      - "V8: Embedding dispatch blocking the caller too long"
    notes: "Write-time validation is the primary defense. Health checks verify post-write integrity."
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Multimodal physics (O2) | `coherence_validity`, `weight_balance` | Invalid coherence or unbalanced weights silently corrupt WM selection |
| URI-based storage (O3) | `no_binary_blobs` | Binary in graph would bloat storage and break serialization |
| Graceful degradation (O4) | `weight_balance` | Verifies redistribution works correctly for real modality distributions |
| Backward compat (O5) | `legacy_shim_accuracy` | Ensures v2.2 image data is not lost during transition |

```yaml
health_indicators:
  - name: coherence_validity
    flow_id: multimodal_coherence
    priority: high
    rationale: "Invalid coherence (NaN, inf, negative, >1) would corrupt WM selection for the citizen. Every citizen is affected."

  - name: weight_balance
    flow_id: multimodal_coherence
    priority: high
    rationale: "If weights don't sum to ~1.0, coherence scores are systematically biased. Citizens with fewer modalities would be penalized."

  - name: no_binary_blobs
    flow_id: media_write
    priority: high
    rationale: "Binary content in graph would cause storage bloat, slow queries, and break serialization. V1 invariant."

  - name: legacy_shim_accuracy
    flow_id: multimodal_coherence
    priority: med
    rationale: "v2.2 citizens have image data in legacy fields. If the shim breaks, their visual memory vanishes from coherence."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "runtime/checks/multimodal_health_checks.py -> SYNC_Multimodality.md"
  result:
    representation: enum
    value: PENDING
    updated_at: "2026-03-18T00:00:00Z"
    source: "multimodal_health_composite"
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_coherence_validity
    purpose: "Sample coherence computations and verify all return valid floats in [0, 1]"
    status: pending
    priority: high
  - name: check_weight_balance
    purpose: "For a random subset of node pairs, verify that resolved weights sum to 1.0 within tolerance"
    status: pending
    priority: high
  - name: check_no_binary_blobs
    purpose: "Scan recently written nodes for media URIs that look like base64 or contain binary markers"
    status: pending
    priority: high
  - name: check_legacy_shim_accuracy
    purpose: "For nodes with image_uri but no media dict, verify get_node_media() returns correct data"
    status: pending
    priority: med
```

---

## INDICATOR: coherence_validity

Verifies that multimodal coherence computations always return valid floats, protecting WM selection from corruption.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: coherence_validity
  client_value: "Citizens' working memory selection remains correct — the right memories surface at the right time"
  validation:
    - validation_id: V2
      criteria: "compute_multimodal_coherence() returns float in [0.0, 1.0] for any input combination"
    - validation_id: V3
      criteria: "Dimension mismatches detected and raised, not silently ignored"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: "OK = all sampled coherence values valid | WARN = >0 edge cases hit fallback | ERROR = invalid values detected"
  aggregation:
    method: "worst-of across all sampled pairs"
    display: "enum"
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_coherence_output
    type: graph_ops
    payload: "float coherence score from compute_multimodal_coherence()"
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="coherence_validity",
    triggers=[
        triggers.cron.every("100 ticks"),
    ],
    on_problem="MULTIMODAL_COHERENCE_INVALID",
    task="fix_multimodal_coherence",
)
def check_coherence_validity(ctx) -> dict:
    """Sample 20 random node pairs, compute coherence, verify all in [0, 1]."""
    pairs = ctx.graph.sample_node_pairs(n=20)
    for a, b in pairs:
        coh = compute_multimodal_coherence(...)
        if not (0.0 <= coh <= 1.0) or math.isnan(coh) or math.isinf(coh):
            return Signal.critical(details={"node_a": a.id, "node_b": b.id, "coherence": coh})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: "All sampled coherence values are valid floats in [0, 1]"
  degraded: "Some edge cases produced fallback behavior (logged warnings)"
  critical: "At least one coherence computation returned NaN, inf, negative, or >1"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "every 100 ticks"
  max_frequency: "1/100 ticks"
  burst_limit: 1
  backoff: "double interval on repeated critical signals"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: "SYNC_Multimodality.md status section"
      transport: file
      notes: "Agent-readable health status"
display:
  locations:
    - surface: Log
      location: "runtime/checks/multimodal_health_checks.log"
      signal: "OK/WARN/ERROR"
      notes: "Standard health check log format"
```

### MANUAL RUN

```yaml
manual_run:
  command: "PYTHONPATH='.mind:.' python3 -m runtime.checks.multimodal_health_checks --check coherence_validity"
  notes: "Run when suspecting coherence corruption after model changes"
```

---

## INDICATOR: weight_balance

Verifies that the weight redistribution algorithm always produces weights summing to 1.0.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: weight_balance
  client_value: "Coherence scores are calibrated — nodes with fewer modalities are not systematically penalized or inflated"
  validation:
    - validation_id: V5
      criteria: "Effective weights sum to 1.0 (within float tolerance of 1e-6)"
    - validation_id: V4
      criteria: "Text weight >= any single modality weight"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = all weight sums within tolerance | 0 = at least one weight sum out of bounds"
  aggregation:
    method: "AND across all sampled configurations"
    display: "binary"
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_weight_resolution
    type: graph_ops
    payload: "dict of modality -> weight from resolve_weights()"
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="weight_balance",
    triggers=[
        triggers.cron.every("100 ticks"),
    ],
    on_problem="MULTIMODAL_WEIGHT_IMBALANCE",
    task="fix_multimodal_weights",
)
def check_weight_balance(ctx) -> dict:
    """Test resolve_weights() with all possible modality subsets."""
    from itertools import combinations
    all_modalities = list(MODALITY_REGISTRY.keys())
    all_modalities = [k for k in all_modalities if k != "text"]
    for r in range(len(all_modalities) + 1):
        for subset in combinations(all_modalities, r):
            weights = resolve_weights(list(subset), MODALITY_REGISTRY)
            total = weights["w_text"] + sum(weights.get(k, 0) for k in subset) + weights["w_lex"]
            # w_affect is subtracted, not added, so total should = 1.0 + w_affect
            expected = 1.0 + weights["w_affect"]
            if abs(total - expected) > 1e-6:
                return Signal.critical(details={"subset": subset, "total": total, "expected": expected})
            if weights["w_text"] < max(weights.get(k, 0) for k in subset) if subset else 0:
                return Signal.critical(details={"text_weight": weights["w_text"], "subset": subset})
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: "All modality subsets produce balanced weights summing to expected total"
  critical: "At least one modality subset produces unbalanced weights"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "every 100 ticks"
  max_frequency: "1/100 ticks"
  burst_limit: 1
  backoff: "none — this is a pure computation check, always cheap"
```

### MANUAL RUN

```yaml
manual_run:
  command: "PYTHONPATH='.mind:.' python3 -m runtime.checks.multimodal_health_checks --check weight_balance"
  notes: "Run after changing modality weights in constants.py"
```

---

## HOW TO RUN

```bash
# Run all health checks for multimodality module
PYTHONPATH='.mind:.' python3 -m runtime.checks.multimodal_health_checks

# Run a specific checker
PYTHONPATH='.mind:.' python3 -m runtime.checks.multimodal_health_checks --check coherence_validity
```

---

## KNOWN GAPS

- V1 (no binary blobs): `check_no_binary_blobs` is pending — needs heuristic for detecting base64 in URI fields
- V6 (legacy shim): `check_legacy_shim_accuracy` is pending — needs access to real v2.2 nodes in test graph
- V8 (embedding never blocks tick): not yet covered by health — would need tick timing instrumentation

<!-- @mind:todo Implement check_no_binary_blobs — scan media URIs for base64 patterns (data:, long alphanumeric strings without scheme prefix) -->
<!-- @mind:todo Implement check_legacy_shim_accuracy — find nodes with image_uri but no media dict, verify shim output -->
<!-- @mind:todo Add tick-timing check for V8 — verify that coherence computation adds < 1ms to tick duration -->

---

## MARKERS

<!-- @mind:todo Create runtime/checks/multimodal_health_checks.py implementing the 4 checkers defined above -->
<!-- @mind:proposition Consider a health indicator for "modality coverage distribution" — tracking what percentage of nodes have each modality. Not a correctness check, but useful for understanding how multimodal the graph actually is. -->
<!-- @mind:escalation The weight_balance check tests all modality subsets combinatorially. With 5+ modalities, this becomes 2^5 = 32 subsets. Still cheap, but the approach doesn't scale to 20 modalities. Acceptable for v1? -->
