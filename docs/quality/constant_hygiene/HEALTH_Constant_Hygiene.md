# Constant Hygiene — Health

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## THE GUARANTEE: HEALTH ↔ RESULTS ↔ SENSES (1-1 MANDATORY)

| Result ID | Result Name | Sense (proved_by) | Health Indicator | Status |
|-----------|-------------|-------------------|------------------|--------|
| R1 | Caught at creation | sense:quality:constant_detection_latency | H1: scan_alive | pending |
| R2 | Felt in awareness | sense:quality:concept_import_rate | H2: concepts_imported | pending |
| R3 | Trend improves | sense:quality:constant_trend | H3: trend_tracking | pending |

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
OBJECTIVES:      ./OBJECTIVES_Constant_Hygiene.md
PATTERNS:        ./PATTERNS_Constant_Hygiene.md
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
THIS:            HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: scan_alive
    purpose: Verify evaluate() is running in the maintenance loop (V4)
    status: pending
    priority: high
  - name: concepts_imported
    purpose: Verify injected Concepts are reaching citizens' L1 (V3, R2)
    status: pending
    priority: med
  - name: trend_tracking
    purpose: Verify constant-per-commit trend is being measured (R3)
    status: pending
    priority: low
```

---

## H1: Scan Alive

**What:** evaluate() is being called and processing commits.
**Validates:** V4 (can't break the dispatcher) + R1 (caught at creation)
**Carrier:** Auto-routed (infra domain)

```yaml
signals:
  healthy: "evaluate() ran within the last maintenance cycle AND processed ≥0 commits"
  degraded: "evaluate() ran but threw warnings or couldn't read diffs"
  critical: "evaluate() has not run in 2+ maintenance cycles"
```

## H2: Concepts Imported

**What:** Concept nodes created by the sense are actually being imported into citizens' L1.
**Validates:** V3 (routes to committing citizen) + R2 (felt in awareness)
**Carrier:** Auto-routed

```yaml
signals:
  healthy: ">80% of injected Concepts appear in the target citizen's L1 within 3 awareness ticks"
  degraded: "50-80% imported — some citizens' awareness ticks may not reach the Concept"
  critical: "<50% — Concepts are being created but not reaching citizens"
```

## H3: Trend Tracking

**What:** The per-citizen constant count trend is being measured and is improving.
**Validates:** R3 (trend downward)
**Carrier:** Auto-routed

```yaml
signals:
  healthy: "After 2+ weeks of data, average constants per commit is trending down"
  degraded: "Flat trend — citizens see the Concepts but don't change behavior"
  critical: "Upward trend — constants per commit increasing despite the sense running"
```

---

## HOW TO RUN

```bash
# Check if the sense is running
python3 -c "from runtime.orchestrator.constant_hygiene import _recent_constant_counts; print(_recent_constant_counts)"

# Manual scan
python3 -c "
from falkordb import FalkorDB
db = FalkorDB(host='localhost', port=6379)
g = db.select_graph('lumina-prime')
from runtime.orchestrator.constant_hygiene import evaluate
print(evaluate(g, '/home/mind-protocol/mind-mcp'))
"
```

---

## KNOWN GAPS

<!-- @mind:todo H1 checker not yet coded — needs timestamp tracking in evaluate() -->
<!-- @mind:todo H2 checker needs L1 import verification — requires querying citizen brains -->
<!-- @mind:todo H3 trend tracking needs at least 2 weeks of data to be meaningful -->

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
