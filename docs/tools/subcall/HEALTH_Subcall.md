# Subcall — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

| Use Health For | Why |
|----------------|-----|
| Resonance quality over time | Requires real citizen graphs with real embeddings, not fixtures |
| Formula behavior across 24 scenarios | Emergent from limbic drive combinations, not deterministic per scenario |
| Moment creation reliability | Depends on live FalkorDB state and concurrent writes |
| Auto-trigger accuracy in production | Requires real message patterns, not synthetic test strings |

---

## PURPOSE OF THIS FILE

This HEALTH file covers the subcall module (subcall_handler.py + subcall_auto.py) — the flagship MCP tool for zero-LLM telepathy across citizen graphs.

It exists because subcall's value depends on emergent properties that unit tests cannot verify: resonance quality (do the right nodes activate?), formula behavior (do scenarios actually produce different routing?), moment persistence (do settlement anchors survive in production?), and auto-trigger precision (does it fire when it should, not when it shouldn't?).

Boundaries: This file does NOT verify graph_ops correctness (that belongs to runtime/physics/graph health), embedding quality (that belongs to runtime/infrastructure/embeddings health), or MCP transport (that belongs to mcp/server health).

---

## WHY THIS PATTERN

Subcall tests can verify that `_format_as_telemetry()` produces the right structure given mock resonance data. But they cannot verify that the KNN search actually returns relevant nodes from a real citizen's brain, or that the thermodynamic formula routes to the right citizens under production limbic conditions. Those are runtime health properties that emerge from real data.

Docking-based checks are the right tradeoff because they observe the pipeline at its natural output points (resonance result, moment creation) without modifying the handler code.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
PATTERNS:        ./PATTERNS_Subcall.md
BEHAVIORS:       ./BEHAVIORS_Subcall.md
ALGORITHM:       ./ALGORITHM_Subcall.md
VALIDATION:      ./VALIDATION_Subcall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Subcall.md
THIS:            HEALTH_Subcall.md (you are here)
SYNC:            ./SYNC_Subcall.md
```

---

## IMPLEMENTS

```yaml
implements:
  runtime: runtime/checks.py
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: single_target_subcall
    purpose: Intelligence briefing production and economic moment creation for explicit @handle queries
    triggers:
      - type: event
        source: mcp/server.py tool dispatch
        notes: citizen invokes subcall(target="@handle", query="...")
    frequency:
      expected_rate: 10-50/day per active citizen
      peak_rate: 200/day during collaborative sprints
      burst_behavior: sequential processing, no backpressure; graph queries may queue under load
    risks:
      - V1 violation: LLM import introduced during refactor
      - V3 violation: moment creation skipped on graph error
      - V5 violation: formatter regression drops an output layer
      - V7 violation: universe switch not restored on exception
    notes: this is the highest-value flow — produces the richest output and anchors economics

  - flow_id: auto_select_subcall
    purpose: Broad citizen scan for diverse viewpoints when no target specified
    triggers:
      - type: event
        source: mcp/server.py tool dispatch (target omitted)
        notes: citizen invokes subcall(query="...") without target
    frequency:
      expected_rate: 5-20/day per active citizen
      peak_rate: 100/day during exploration phases
      burst_behavior: scans 50 citizens sequentially; 200+ citizen graphs queried in total
    risks:
      - V4 violation: diverse selection bypassed, echo chamber results
      - V8 violation: keyword fallback not triggered when embeddings are missing
    notes: most expensive flow computationally; probe of 50 * 5 labels = 250 KNN searches

  - flow_id: auto_trigger_subcall
    purpose: Proactive help when distress signals detected
    triggers:
      - type: event
        source: L1 tick runner or MCP middleware
        notes: fires after each message/tool output via detect_trigger()
    frequency:
      expected_rate: 1-5/day per citizen (cooldown prevents more)
      peak_rate: 10/day during debugging sessions
      burst_behavior: 5-message cooldown prevents cascading triggers
    risks:
      - false positive: trigger on benign text patterns (e.g., "?" in code comments)
      - false negative: limbic_state not provided, falling back to text-only detection
    notes: cooldown mechanism is critical — without it, every question mark would trigger
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Zero-LLM | zero_llm_guarantee | if this fails, subcall's economic premise is broken |
| O2: Thermodynamic routing | formula_scenario_diversity | if scenarios produce identical routing, the physics is dead |
| O3: Non-read-only injection | moment_persistence_rate | if moments aren't created, the economy has no settlement anchors |
| O4: Intelligence briefing | briefing_completeness | if output layers are missing, the intelligence product is degraded |

```yaml
health_indicators:
  - name: zero_llm_guarantee
    flow_id: single_target_subcall
    priority: high
    rationale: any LLM import in subcall_handler.py would violate the core architectural promise

  - name: moment_persistence_rate
    flow_id: single_target_subcall
    priority: high
    rationale: unpersisted moments mean $MIND cannot flow from consumer to creator

  - name: briefing_completeness
    flow_id: single_target_subcall
    priority: med
    rationale: missing output layers degrade the intelligence product citizens rely on

  - name: formula_scenario_diversity
    flow_id: auto_select_subcall
    priority: med
    rationale: if 24 scenarios produce identical routing, the thermodynamic design is not working

  - name: auto_trigger_precision
    flow_id: auto_trigger_subcall
    priority: med
    rationale: false positives waste graph queries; false negatives leave citizens struggling alone
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: docs/tools/subcall/HEALTH_Subcall.md
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-18T00:00:00Z
    source: zero_llm_guarantee
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_zero_llm_imports
    purpose: verify no LLM client libraries are imported in subcall_handler.py (V1)
    status: pending
    priority: high
  - name: check_moment_creation
    purpose: verify subcall moments are being created with correct topology (V3)
    status: pending
    priority: high
  - name: check_briefing_layers
    purpose: verify single-target response contains all 3 output layers (V5)
    status: pending
    priority: med
  - name: check_scenario_profile_count
    purpose: verify SCENARIO_PROFILES has exactly 24 entries + manual default (V2)
    status: pending
    priority: med
  - name: check_universe_restore
    purpose: verify ctx.graph_ops is restored after universe switch (V7)
    status: pending
    priority: high
```

---

## INDICATOR: zero_llm_guarantee

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: zero_llm_guarantee
  client_value: citizens trust that subcall costs 0 LLM tokens — any violation breaks trust and economics
  validation:
    - validation_id: V1
      criteria: no LLM client imports in subcall_handler.py or subcall_auto.py
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = no LLM imports found, 0 = LLM import detected
  aggregation:
    method: single check, no aggregation
    display: binary pass/fail
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="zero_llm_guarantee",
    triggers=[
        triggers.file.on_change("mcp/tools/subcall_handler.py"),
        triggers.file.on_change("mcp/tools/subcall_auto.py"),
    ],
    on_problem="SUBCALL_LLM_VIOLATION",
    task="TASK_fix_llm_import",
)
def zero_llm_guarantee(ctx) -> dict:
    """Verify subcall never imports LLM clients."""
    import ast
    forbidden = {"openai", "anthropic", "ollama", "litellm", "langchain", "transformers"}
    for path in ["mcp/tools/subcall_handler.py", "mcp/tools/subcall_auto.py"]:
        tree = ast.parse(open(path).read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                names = [a.name for a in node.names]
                all_names = ([module] if module else []) + names
                for name in all_names:
                    if name and any(f in name.lower() for f in forbidden):
                        return Signal.critical(details=f"LLM import found: {name} in {path}")
    return Signal.healthy()
```

### SIGNALS

```yaml
signals:
  healthy: no LLM client libraries imported in subcall files
  critical: LLM client import detected — subcall's zero-LLM promise is broken
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: file change on subcall_handler.py or subcall_auto.py
  max_frequency: 1/commit
  burst_limit: 5
  backoff: none needed — static analysis, near-instant
```

---

## INDICATOR: moment_persistence_rate

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: moment_persistence_rate
  client_value: economic settlement depends on moments being created — unpersisted moments mean creators are not compensated
  validation:
    - validation_id: V3
      criteria: every single-target subcall creates a Moment node with CREATED + CONTRIBUTED links
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: ratio of subcall invocations that successfully created moment nodes (1.0 = all persisted)
  aggregation:
    method: rolling average over last 100 subcalls
    display: float with threshold at 0.95
```

### SIGNALS

```yaml
signals:
  healthy: moment creation rate >= 0.95
  degraded: moment creation rate 0.8-0.95
  critical: moment creation rate < 0.8
```

---

## HOW TO RUN

```bash
# Run all health checks for subcall module
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks --module subcall

# Run a specific checker
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.checks --check zero_llm_guarantee
```

---

## KNOWN GAPS

- V2 (formula morphs without branches): no automated checker yet — requires running the formula with all 24 profiles and verifying output diversity
- V4 (diverse selection): no checker — would require running select_diverse() with known inputs and verifying spread
- V6 (stimulus cluster richness): no checker — would require a live graph with activated nodes
- V8 (keyword fallback activation): no checker — would require deliberately failing embedding service

<!-- @mind:todo Create checker for V2: run score_citizens() with each of 24 scenario profiles on same graph, verify output rankings differ -->
<!-- @mind:todo Create checker for V4: verify select_diverse() output has higher pairwise distance than naive top-N -->

---

## MARKERS

<!-- @mind:todo Implement check_moment_creation as a runtime health check querying recent subcall moments -->
<!-- @mind:proposition Add a telemetry counter in handle_subcall() that tracks moment creation success/failure rate for the health indicator -->
