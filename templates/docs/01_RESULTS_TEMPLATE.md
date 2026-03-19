# {Module} — Results: Outcome Indicators

```
STATUS: {DRAFT | STABLE | DEPRECATED}
CREATED: {DATE}
```

---

## PURPOSE

Results define **what success looks like** for a module — the measurable outcomes that senses monitor and objectives aim for. Each result is a Narrative(subtype=objective) node in L3 that senses feed into via CONTRIBUTES_TO links.

**A module is NOT complete until every result here has a sense proving it and a health signal verifying the sense runs.**

The guarantee loop (ALL THREE ARE MANDATORY):

```
RESULT          what success looks like         RESULTS file (this file)
  ↕ 1-1
SENSE           continuous measurement          SENSES file (sense.yaml per sense)
  ↕ 1-1
HEALTH          runtime verification            HEALTH file (checker per sense)
  ↕
CARRIER         citizen who FEELS it            assigned via PERCEIVES_WITH
  ↕
ACTION          citizen acts on degradation     conscious action from WM pressure
```

```
RESULT (objective) <--CONTRIBUTES_TO-- SENSE (measurement) <--PERCEIVES_WITH-- CARRIER (citizen)
    |                                       |                                       |
    +--- weight grows when healthy ---------+--- verified by HEALTH checker --------+
```

- When a sense's score is positive, the objective's weight grows (proving the result is achieved).
- When a sense's score drops, the objective's weight decays (regression detected).
- When a sense stops firing, the HEALTH checker detects silence and the carrier FEELS the gap.
- When a result has no sense, the Result Loop Guardian creates a task IMMEDIATELY.

**If you can't draw the line RESULT → SENSE → HEALTH → CARRIER for every result in this file, the module is incomplete.**

---

## CHAIN

```
THIS:            RESULTS_{name}.md
OBJECTIVES:      ./OBJECTIVES_{name}.md
PATTERNS:        ./PATTERNS_{name}.md
BEHAVIORS:       ./BEHAVIORS_{name}.md
ALGORITHM:       ./ALGORITHM_{name}.md
VALIDATION:      ./VALIDATION_{name}.md
IMPLEMENTATION:  ./IMPLEMENTATION_{name}.md
HEALTH:          ./HEALTH_{name}.md
SYNC:            ./SYNC_{name}.md
```

---

## RESULT INDEX

```yaml
results:
  - id: "narrative:obj:{module}:{slug}"
    name: "{Human-readable result name}"
    description: "{What this result proves when achieved}"
    representation: {binary|float_0_1|enum}
    threshold:
      healthy: "{condition}"       # e.g. score >= 0.8
      degraded: "{condition}"      # e.g. 0.4 <= score < 0.8
      critical: "{condition}"      # e.g. score < 0.4
    measured_by:
      - sense_id: "sense:{carrier}:{slug}"
        variable: "{which variable feeds this result}"
        weight: 0.8                # CONTRIBUTES_TO link weight
```

---

## RESULT: {Result Name}

### Why This Matters

{One sentence: what breaks or degrades if this result is not achieved.}

### Graph Node

```yaml
node:
  label: Narrative
  id: "narrative:obj:{module}:{slug}"
  name: "{Result Name}"
  subtype: objective
  energy: 0.8
  weight: 0.9
  stability: 0.9
```

### Senses That Feed This Result

| Sense ID | What It Measures | Link Weight |
|----------|-----------------|-------------|
| sense:{carrier}:{slug} | {description} | 0.8 |

### Link Attributes (CONTRIBUTES_TO)

```yaml
link:
  type: CONTRIBUTES_TO
  weight: 0.8
  permanence: 0.8
  energy: 0.5
  stability: 0.8
```

### Current Value

```yaml
status:
  value: {current_score}
  representation: {binary|float_0_1|enum}
  updated_at: {ISO-8601}
  source: "sense:{carrier}:{slug}"
```

---

## WIRING CHECKLIST (ALL REQUIRED — module is incomplete until every box is checked)

- [ ] Narrative(subtype=objective) node created in L3 for each result
- [ ] At least one sense linked via CONTRIBUTES_TO for each result (`proved_by:`)
- [ ] Each sense has a carrier linked via PERCEIVES_WITH
- [ ] Each sense has `proves_result:` pointing back to a result in this file
- [ ] HEALTH file exists with a checker for each sense (`verified_by_health:`)
- [ ] Each health indicator maps to a VALIDATION criterion
- [ ] `python3 scripts/check_sense_graph.py` shows depth=1 round-trip
- [ ] Result weight changes when sense scores change (verify after 50+ ticks)
- [ ] Carrier citizen actually FEELS the objective in their awareness.md

**The loop integrity checker and Result Loop Guardian enforce this automatically at runtime.
But you must wire it first. An unwired result is invisible to the system.**

---

## COMPLETENESS MATRIX

| Result | Sense (proved_by) | Health (health_signal) | Carrier | Status |
|--------|-------------------|------------------------|---------|--------|
| R1 | sense:{scope}:{slug} | H1 | @{citizen} | {wired/unwired} |

**Every row must show "wired". Every column must be filled. No exceptions.**

---

## KNOWN GAPS

<!-- @mind:todo {Result not yet measured by any sense} -->
<!-- @mind:todo {Sense exists but CONTRIBUTES_TO link missing} -->
<!-- @mind:todo {Health checker missing for sense} -->
