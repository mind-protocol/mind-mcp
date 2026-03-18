# Gap Detection — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## PURPOSE

This HEALTH file covers the gap detection module: periodic graph scanning for structural incompleteness (missing links, duplicates, empty query gaps) and the task creation that follows. It exists because gap detection is a background process with no direct user feedback loop — if it silently stops working, nobody notices until graph quality degrades weeks later. Health checks verify that scans run, produce results, and create well-formed tasks.

**Boundaries:** This file verifies gap detection mechanics. It does NOT verify whether gap tasks get resolved (that's task physics health) or whether the graph is structurally complete (that's a higher-order assessment).

---

## WHY THIS PATTERN

Tests can verify that `scan_gaps()` produces the right GapDescriptors for a fixture graph. But they can't verify that scans actually run at the configured interval in production, that task creation succeeds against a live graph, or that the empty query hook is wired and firing. These are runtime emergent behaviors that only health checks can monitor.

Docking-based checks are the right tradeoff because gap detection has clear input/output boundaries: scans produce gap descriptors, task creation writes to the graph, and the query hook fires on search completion. We can observe these docks without modifying the scan logic.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
PATTERNS:        ./PATTERNS_Gap_Detection.md
BEHAVIORS:       ./BEHAVIORS_Gap_Detection.md
ALGORITHM:       ./ALGORITHM_Gap_Detection.md
VALIDATION:      ./VALIDATION_Gap_Detection.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gap_Detection.md
THIS:            HEALTH_Gap_Detection.md (you are here)
SYNC:            ./SYNC_Gap_Detection.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/checks.py               # Python code implementing these checks
  decorator: @check                        # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: periodic_gap_scan
    purpose: "If scans stop running, gaps accumulate silently — graph quality degrades invisibly"
    triggers:
      - type: schedule
        source: runtime/cognition/tick_runner_l1_cognitive_engine.py (tick loop)
        notes: "Fires every GAP_SCAN_INTERVAL ticks (default 100)"
    frequency:
      expected_rate: "1 per 100 ticks (~once per hour depending on tick rate)"
      peak_rate: "1 per 100 ticks (not bursty)"
      burst_behavior: "No burst — strictly periodic"
    risks:
      - "Scan silently disabled or interval misconfigured (V5)"
      - "Task creation fails due to graph connectivity issues (V2, V3)"
    notes: "Single citizen scope per scan — scales linearly with citizen count"

  - flow_id: empty_query_gap_capture
    purpose: "If the hook stops firing, failed queries go unrecorded — knowledge blind spots persist"
    triggers:
      - type: event
        source: runtime/physics/graph/graph_queries_search.py (search return path)
        notes: "Fires after every graph_query call"
    frequency:
      expected_rate: "Proportional to search usage — 5-50/hour per active citizen"
      peak_rate: "During active sessions — up to 100/hour"
      burst_behavior: "Gap markers are deduplicated, so bursts of same-topic queries don't create spam"
    risks:
      - "Hook unwired or removed during refactor (breaks V4 feedback loop)"
      - "Gap markers accumulate without bound if L7 forgetting is not running"
    notes: "Lightweight — no embedding computation, only comparison against threshold"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Structural completeness | gap_scan_running, gap_tasks_well_formed | Verifies the primary mechanism for finding and surfacing missing links |
| Identity resolution | gap_scan_running | Duplicate detection is part of the periodic scan |
| Knowledge acquisition | query_hook_wired | Verifies failed queries are captured as gap markers |

```yaml
health_indicators:
  - name: gap_scan_running
    flow_id: periodic_gap_scan
    priority: high
    rationale: "If scans stop, gaps accumulate silently. This is the primary detection mechanism."

  - name: gap_tasks_well_formed
    flow_id: periodic_gap_scan
    priority: high
    rationale: "Tasks without sufficient context (V1) waste citizen attention. Tasks with duplicate IDs (V2) flood the queue."

  - name: query_hook_wired
    flow_id: empty_query_gap_capture
    priority: med
    rationale: "The query hook is the only mechanism for empty query gap detection. If unwired, knowledge blind spots go unrecorded."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "HEALTH_Gap_Detection.md status block"
  result:
    representation: enum
    value: UNKNOWN
    updated_at: "2026-03-18T00:00:00Z"
    source: gap_scan_running
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: gap_scan_running
    purpose: "Verify gap detection scans execute at configured interval (V5)"
    status: pending
    priority: high
  - name: gap_tasks_well_formed
    purpose: "Verify created tasks carry sufficient context (V1) and are not duplicated (V2)"
    status: pending
    priority: high
  - name: query_hook_wired
    purpose: "Verify on_query_result hook is called from search return path"
    status: pending
    priority: med
```

---

## INDICATOR: gap_scan_running

Verifies that gap detection scans are executing at the configured interval and producing results.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: gap_scan_running
  client_value: "Citizens get timely gap tasks — graph self-repair happens"
  validation:
    - validation_id: V5
      criteria: "Scan completes within bounded time at configured interval"
    - validation_id: V6
      criteria: "Persistent gaps have their task energy refreshed"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: "OK = scan ran within last 2 intervals; WARN = last scan was 3-5 intervals ago; ERROR = no scan in 5+ intervals"
  aggregation:
    method: "Worst-case across citizens"
    display: "enum"
```

### SIGNALS

```yaml
signals:
  healthy: "Last scan timestamp within 2 × GAP_SCAN_INTERVAL ticks"
  degraded: "Last scan timestamp between 3-5 × GAP_SCAN_INTERVAL ticks"
  critical: "No scan in 5+ × GAP_SCAN_INTERVAL ticks"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "schedule — check every 200 ticks (2x scan interval)"
  max_frequency: "1 per 200 ticks"
  burst_limit: 1
  backoff: "None needed — periodic, not event-driven"
```

---

## INDICATOR: gap_tasks_well_formed

Verifies that gap tasks created by the detector carry sufficient context and are not duplicated.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: gap_tasks_well_formed
  client_value: "Citizens can resolve gap tasks from the task itself, without re-querying"
  validation:
    - validation_id: V1
      criteria: "Task synthesis contains source content, existing links, and a question"
    - validation_id: V2
      criteria: "No two active gap tasks share the same deterministic ID"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: "Ratio of well-formed gap tasks to total gap tasks. 1.0 = all well-formed, 0.0 = none"
  aggregation:
    method: "Mean across all gap tasks in the graph"
    display: "float_0_1"
```

### SIGNALS

```yaml
signals:
  healthy: "100% of gap tasks are well-formed and no duplicate IDs found"
  degraded: "90-99% well-formed or 1-2 duplicate IDs found"
  critical: "<90% well-formed or >2 duplicate IDs found"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "After each gap scan completes"
  max_frequency: "1 per scan (every GAP_SCAN_INTERVAL ticks)"
  burst_limit: 1
  backoff: "None"
```

---

## INDICATOR: query_hook_wired

Verifies that the `on_query_result()` hook is being called from the search system.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: query_hook_wired
  client_value: "Knowledge blind spots are captured — the graph learns what it doesn't know"
  validation:
    - validation_id: V4
      criteria: "Empty query gaps require minimum query quality"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: "1 = hook fired at least once in last 1000 ticks; 0 = hook never fired"
  aggregation:
    method: "Binary AND across active citizens"
    display: "binary"
```

### SIGNALS

```yaml
signals:
  healthy: "Hook has fired at least once in the last 1000 ticks"
  degraded: "N/A (binary)"
  critical: "Hook has not fired in 1000+ ticks (or never fired)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: "schedule — check every 500 ticks"
  max_frequency: "1 per 500 ticks"
  burst_limit: 1
  backoff: "None"
```

---

## HOW TO RUN

```bash
# Run all health checks for gap detection
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks --module gap_detection

# Run a specific checker
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks --checker gap_scan_running
```

---

## KNOWN GAPS

- No checker yet for V3 (detector never modifies graph structure) — would require audit logging of all graph writes during a scan
- No checker yet for V7 (duplicate detection is not crystallization) — low priority, this is an architectural invariant enforced by code separation

<!-- @mind:todo Add checker for V3 once graph write audit logging is available -->
<!-- @mind:todo Add checker for gap task resolution rate (not just creation) — this crosses into task physics health territory -->

---

## MARKERS

<!-- @mind:proposition Consider a combined health dashboard that shows gap detection + task physics together, so operators can see the full pipeline: gaps found -> tasks created -> tasks resolved -->
