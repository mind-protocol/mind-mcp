# Graph Enricher — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers the graph enricher module (graph_enricher.py + planned extractor/resolver/merger files) and its runtime verification. It reduces the risk of silent failures in entity extraction: messages passing through without extracting entities, ghost nodes proliferating, false merges corrupting identity, or LLM extraction stalling the write path.

The graph enricher is verified at runtime because its critical properties (extraction completeness, dedup effectiveness, merge correctness) depend on real text patterns, entity distributions, and timing that unit tests with fixture data cannot replicate.

This file will NOT verify: physics engine behavior (covered by l1_physics HEALTH), trust propagation correctness, stimulus injection, or LLM response quality (beyond extraction parsing).

---

## WHY THIS PATTERN

Tests verify that extract_urls() finds URLs in known strings and that auto_merge() transfers links correctly. But the enricher's critical failure modes are emergent:
- Gemini extraction quality drifting as prompt patterns change
- Embedding match thresholds being too aggressive or too lenient for real-world name distributions
- Platform ID collision detection failing under concurrent message processing
- Graph connection silently dropping, causing all enrichment to no-op

Docking-based runtime checks catch these without modifying the enricher code. Throttling keeps verification cheap (the enricher processes hundreds of messages per day; health checks sample at 1/5min).

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Graph_Enricher.md
PATTERNS:        ./PATTERNS_Graph_Enricher.md
BEHAVIORS:       ./BEHAVIORS_Graph_Enricher.md
ALGORITHM:       ./ALGORITHM_Graph_Enricher.md
VALIDATION:      ./VALIDATION_Graph_Enricher.md
IMPLEMENTATION:  ./IMPLEMENTATION_Graph_Enricher.md
THIS:            HEALTH_Graph_Enricher.md (you are here)
SYNC:            ./SYNC_Graph_Enricher.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code will live in runtime:

```yaml
implements:
  runtime: runtime/checks.py       # Python code implementing these checks
  decorator: @check                # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: message_enrichment
    purpose: Verify messages produce structural records AND entity nodes — if this fails, the graph is blind to what citizens discuss
    triggers:
      - type: event
        source: scripts/graph_enricher.py:on_message
        notes: Called by discord_bridge, telegram_bridge, whatsapp_bridge on every message
    frequency:
      expected_rate: 50-200/day across all citizens
      peak_rate: 50/hour during active conversation
      burst_behavior: Sequential processing. No backpressure. Graph connection may fail under extreme load (FalkorDB crash known issue with 278+ citizens).
    risks:
      - V1 violation: message passes through without creating structural record (graph connection lost)
      - V6 violation: tier 2 extraction blocks structural write path (Gemini timeout)
      - V7 violation: low-confidence extraction creates garbage nodes
    notes: Primary flow. Tier 1 extraction is inline; tier 2 may be async.

  - flow_id: entity_resolution
    purpose: Verify extracted entities are correctly matched or created — if this fails, the graph fills with duplicates or false merges
    triggers:
      - type: event
        source: scripts/graph_enricher_entity_resolver.py:resolve_entity (planned)
        notes: Called per extracted entity from tier 2
    frequency:
      expected_rate: 1-5 entities per message, 50-1000/day
      peak_rate: 20 entities/message for long detailed messages
      burst_behavior: Sequential per message. Embedding computation adds ~10ms per entity.
    risks:
      - V8 violation: false merge due to embedding threshold too low
      - V4 violation: platform_id collision not detected
    notes: Depends on tier 2 being implemented. Health checks initially monitor existing structural enrichment.

  - flow_id: auto_merge
    purpose: Verify merges preserve all links and enforce platform_id uniqueness — if this fails, identity data is lost
    triggers:
      - type: event
        source: scripts/graph_enricher_node_merger.py:auto_merge (planned)
        notes: Triggered when platform_id collision detected during handle update
    frequency:
      expected_rate: 1-5/day (most users have stable platform IDs)
      peak_rate: 10/hour (bulk import or new platform integration)
      burst_behavior: Each merge is atomic within a FalkorDB transaction.
    risks:
      - V5 violation: links lost during merge
      - V4 violation: duplicate platform_id persists after merge
    notes: Low frequency but high impact. Every merge must be logged and verifiable.
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Entity extraction | structural_record_rate, extraction_yield | Confirms messages produce graph state and entities are extracted |
| O2: Dedup and merge | merge_correctness, ghost_node_count | Confirms entities are deduplicated without data loss |
| O3: Confidence-aware | unconfirmed_node_ratio | Confirms LLM extractions are properly flagged |
| O5: Minimal latency | enrichment_latency | Confirms tier 2 doesn't block the write path |

```yaml
health_indicators:
  - name: structural_record_rate
    flow_id: message_enrichment
    priority: high
    rationale: If messages pass through without creating Moment/Actor/Space nodes, the graph loses all memory of events. This is the most critical indicator — the existing v1 functionality must keep working.

  - name: extraction_yield
    flow_id: message_enrichment
    priority: med
    rationale: Tracks how many entities tier 1 and tier 2 extract per message. Too low suggests extraction is broken. Too high suggests over-extraction (noise). Baseline needed before tuning.

  - name: ghost_node_count
    flow_id: entity_resolution
    priority: med
    rationale: Counts Actor nodes with status="unconfirmed" that have no inbound LINK(mentions) beyond their creation Moment. These are orphaned extractions that were never referenced again — potential garbage.

  - name: merge_correctness
    flow_id: auto_merge
    priority: high
    rationale: After a merge, verify the surviving node has all links from both original nodes. Missing links means identity data was lost.

  - name: enrichment_latency
    flow_id: message_enrichment
    priority: med
    rationale: Tracks time from on_message() call to completion. If tier 2 is inline, this measures Gemini API impact on the write path.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/checks.py
  result:
    representation: enum
    value: PENDING
    updated_at: 2026-03-18T00:00:00Z
    source: graph_enricher_health
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_structural_record_rate
    purpose: Verify V1 — every message event produces Moment/Actor/Space nodes
    status: pending
    priority: high

  - name: check_extraction_yield
    purpose: Monitor entity extraction volume per message (baseline for tuning)
    status: pending
    priority: med

  - name: check_ghost_nodes
    purpose: Count unconfirmed nodes never referenced again (dedup quality signal)
    status: pending
    priority: med

  - name: check_merge_link_preservation
    purpose: Verify V5 — auto-merge preserves all links from both nodes
    status: pending
    priority: high

  - name: check_enrichment_latency
    purpose: Verify V6 — enrichment completes without blocking write path
    status: pending
    priority: med
```

---

## INDICATOR: structural_record_rate

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: structural_record_rate
  client_value: Citizens must have graph memory of every conversation. If structural records are missing, context assembly is incomplete and citizens appear to have amnesia.
  validation:
    - validation_id: V1
      criteria: Every call to on_message() creates at minimum 1 Moment, 1 Actor (MERGE), 1 Space (MERGE), and 3 structural LINKs
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Ratio of on_message() calls that successfully created all structural nodes to total calls. 1.0 = all succeeded. Below 0.95 = degraded (graph connection issues). Below 0.80 = critical.
  aggregation:
    method: Rolling count over 1-hour window
    display: float_0_1 surfaced in health dashboard
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_structural_complete
    type: graph_ops
    payload: on_message() success/failure flag + moment_id
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="structural_record_rate",
    triggers=[
        triggers.cron.every("5m"),
    ],
    on_problem="ENRICHER_STRUCTURAL_FAILURE",
    task="investigate_enrichment_failures",
)
def check_structural_record_rate(ctx) -> dict:
    """Verify on_message() creates structural graph records."""
    total_calls = ctx.get_counter("graph_enricher.on_message.calls")
    total_success = ctx.get_counter("graph_enricher.on_message.success")
    if total_calls == 0:
        return Signal.healthy(details="No messages in window")
    rate = total_success / total_calls
    if rate >= 0.95:
        return Signal.healthy(details=f"Record rate: {rate:.2%}")
    if rate >= 0.80:
        return Signal.degraded(details=f"Record rate dropped: {rate:.2%}")
    return Signal.critical(details=f"Record rate critical: {rate:.2%}")
```

### SIGNALS

```yaml
signals:
  healthy: Record rate >= 95% of messages produce structural graph state
  degraded: Record rate between 80-95% (graph connection intermittent)
  critical: Record rate below 80% (enricher is failing, citizens have no memory)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron every 5 minutes
  max_frequency: 1/5min
  burst_limit: 1
  backoff: Suppress repeated critical alerts for 15 minutes after first alert
```

---

## INDICATOR: merge_correctness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: merge_correctness
  client_value: When two Actor nodes are merged, all relationship history must survive. Lost links mean lost trust scores, interaction counts, and narrative connections.
  validation:
    - validation_id: V5
      criteria: After auto-merge, every LINK from the discarded node exists on the surviving node
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all recent merges preserved all links. 0 = at least one merge lost links.
  aggregation:
    method: AND across all merges in the check window
    display: binary surfaced as OK/FAIL in health dashboard
```

### DOCKS SELECTED

```yaml
docks:
  - point: dock_merge_executed
    type: graph_ops
    payload: keep_id, discard_id, pre-merge link count, post-merge link count
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="merge_correctness",
    triggers=[
        triggers.event.on("graph_enricher.merge_executed"),
    ],
    on_problem="ENRICHER_MERGE_DATA_LOSS",
    task="investigate_merge_data_loss",
)
def check_merge_correctness(ctx) -> dict:
    """Verify auto-merge preserved all links."""
    merge_event = ctx.get_event()
    keep_id = merge_event["keep_id"]
    pre_count = merge_event["pre_merge_link_count"]
    post_count = merge_event["post_merge_link_count"]
    if post_count >= pre_count:
        return Signal.healthy(details=f"Merge {keep_id}: {pre_count} -> {post_count} links")
    return Signal.critical(details=f"Merge {keep_id}: LOST {pre_count - post_count} links")
```

### SIGNALS

```yaml
signals:
  healthy: All merges preserved all links
  critical: A merge lost links (identity data corruption)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: On each merge_executed event
  max_frequency: 1/min (merges are rare)
  burst_limit: 10
  backoff: No suppression — every merge failure is critical
```

---

## HOW TO RUN

```bash
# Run all health checks for graph enricher
python -m runtime.checks --module graph_enricher

# Run a specific checker
python -m runtime.checks --check check_structural_record_rate
```

---

## KNOWN GAPS

- No instrumentation counters exist on graph_enricher.on_message() — the structural_record_rate checker needs counter hooks added.
- No merge logging or event emission exists — merge_correctness checker needs merge events to be emitted.
- extraction_yield and ghost_node_count checkers depend on tier 2 implementation (not yet built).
- enrichment_latency checker needs timing instrumentation added to on_message().
- FalkorDB is known to crash under heavy load (278+ citizens). Health checks cannot prevent this but should detect it via structural_record_rate dropping.

<!-- @mind:todo Add counter instrumentation to graph_enricher.on_message() for health check support -->
<!-- @mind:todo Add merge event emission for merge_correctness checker -->
<!-- @mind:todo Add timing instrumentation for enrichment_latency checker -->
<!-- @mind:proposition Consider graph connection health check (ping FalkorDB before each on_message) — but adds latency -->

---

## MARKERS

<!-- @mind:todo Implement check_structural_record_rate with counter hooks -->
<!-- @mind:todo Implement check_merge_link_preservation with merge event emission -->
<!-- @mind:todo Implement check_extraction_yield after tier 2 is built -->
