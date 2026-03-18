# Style System -- Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Dangling style references | Only detectable with real graph data, not fixtures |
| Material completeness at render time | Emergent from cascade logic with real zone/style data |
| Artist attribution coverage | Requires scanning all Thing(type=style) nodes in production |
| Effects independence from styles | Must verify with real citizen energy + style combinations |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file covers the style system module: style resolution, style creation, and style adoption flows. It exists to detect data integrity failures (dangling references, missing attribution links, incomplete materials) that only surface with real graph data and cannot be caught by unit tests with mocked nodes.

Boundaries: This file does NOT verify Three.js rendering correctness, asset file validity (glTF integrity), or physics tick behavior. Those belong to the renderer and physics modules respectively.

---

## WHY THIS PATTERN

Tests can verify that `resolveStyle()` returns correct output for a hand-crafted mock node. But tests cannot detect that 12 of 464 citizens have style_id pointing to deleted style nodes, or that an artist created 5 styles but one is missing its ->created_by-> link. These are runtime data integrity signals that need periodic health checks against real graph state.

Docking-based checks are the right tradeoff because they observe graph state without modifying it, and they can run at throttled rates without impacting render performance.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
PATTERNS:        ./PATTERNS_Style_System.md
BEHAVIORS:       ./BEHAVIORS_Style_System.md
ALGORITHM:       ./ALGORITHM_Style_System.md
VALIDATION:      ./VALIDATION_Style_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Style_System.md
THIS:            HEALTH_Style_System.md (you are here)
SYNC:            ./SYNC_Style_System.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: (not yet created -- DESIGNING phase)
  decorator: @check
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: style_resolution
    purpose: "If resolution fails, citizens are invisible (V1) or render with wrong appearance"
    triggers:
      - type: schedule
        source: "health scheduler (periodic)"
        notes: "Scan all nodes with non-null style_id, verify reference validity"
    frequency:
      expected_rate: "1/hour"
      peak_rate: "1/hour"
      burst_behavior: "Single scan, no burst possible"
    risks:
      - "Dangling style_id references (V5)"
      - "Incomplete material after resolution (V4)"
    notes: "Read-only graph scan. No mutations."

  - flow_id: style_creation
    purpose: "If ->created_by-> link is missing, artist has no credit (V2)"
    triggers:
      - type: event
        source: "style_graph_operations.js:createStyle() (planned)"
        notes: "After each style creation, verify attribution link"
    frequency:
      expected_rate: "<1/day"
      peak_rate: "10/day"
      burst_behavior: "Burst during onboarding events; each check is lightweight"
    risks:
      - "Missing ->created_by-> link (V2)"
    notes: "Can also run as periodic scan of all Thing(type=style) nodes"
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Sovereign visual identity | `style_reference_integrity`, `material_completeness` | If references dangle or materials are incomplete, citizens are invisible or visually broken |
| O2: Artist attribution | `artist_attribution_coverage` | Missing links mean artists are uncredited -- structural betrayal of the creator economy |
| O5: Physics-driven effects | `effects_independence` | If effects leak into style config, the visual language of energy becomes unreliable |

```yaml
health_indicators:
  - name: style_reference_integrity
    flow_id: style_resolution
    priority: high
    rationale: "Dangling style_id means citizens may fail to render or silently fall back. Operators need to know how many references are broken."

  - name: artist_attribution_coverage
    flow_id: style_creation
    priority: high
    rationale: "Styles without ->created_by-> links are orphans. Artists lose credit. Future $MIND flow has no destination."

  - name: material_completeness
    flow_id: style_resolution
    priority: med
    rationale: "Incomplete material properties cause rendering artifacts. The cascade should prevent this, but real data may expose gaps."

  - name: effects_independence
    flow_id: style_resolution
    priority: high
    rationale: "If any style_variant contains effect-related keys that are not ignored, the visual language is compromised."
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: "docs/engine/style_system/HEALTH_Style_System.md (manual update during DESIGNING)"
  result:
    representation: enum
    value: UNKNOWN
    updated_at: "2026-03-18T00:00:00Z"
    source: "pending implementation"
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: style_reference_integrity_checker
    purpose: "Verify all non-null style_id fields reference existing Thing(type=style) nodes (V1, V5)"
    status: pending
    priority: high
  - name: artist_attribution_checker
    purpose: "Verify all Thing(type=style) nodes have exactly one ->created_by-> link to an Actor (V2)"
    status: pending
    priority: high
  - name: material_completeness_checker
    purpose: "Verify resolved materials have all required properties non-null (V4)"
    status: pending
    priority: med
  - name: effects_independence_checker
    purpose: "Verify no style_variant in the graph contains effect-related keys (V3)"
    status: pending
    priority: high
```

---

## INDICATOR: style_reference_integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: style_reference_integrity
  client_value: "Citizens with dangling style_id render as protocol default instead of their chosen style. Operators see how many references are broken."
  validation:
    - validation_id: V1
      criteria: "Every node with a position renders with a visible mesh"
    - validation_id: V5
      criteria: "Non-null style_id references an existing Thing(type=style) node"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - tuple
  semantics:
    tuple: "{ state: OK|WARN|ERROR, score: float (ratio of valid references) }"
  aggregation:
    method: "score = valid_references / total_references. WARN if score < 1.0. ERROR if score < 0.9."
    display: "tuple surfaced as 'N/M style references valid'"
```

### DOCKS SELECTED

```yaml
docks:
  - point: "graph scan of all nodes with non-null style_id"
    type: graph_ops
    payload: "{ node_id, style_id, style_node_exists: bool, style_node_type: string }"
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="style_reference_integrity",
    triggers=[
        triggers.cron.hourly(),
    ],
    on_problem="STYLE_DANGLING_REFERENCE",
    task="fix_dangling_style_references",
)
def style_reference_integrity(ctx) -> dict:
    """Check all non-null style_id references point to valid Thing(type=style) nodes."""
    nodes_with_style = ctx.graph.query("MATCH (n) WHERE n.style_id IS NOT NULL RETURN n.id, n.style_id")
    total = len(nodes_with_style)
    valid = 0
    dangling = []
    for node_id, style_id in nodes_with_style:
        style_node = ctx.graph.get(style_id)
        if style_node and style_node.node_type == "thing" and style_node.subtype == "style":
            valid += 1
        else:
            dangling.append({"node_id": node_id, "style_id": style_id})
    score = valid / total if total > 0 else 1.0
    if score == 1.0:
        return Signal.healthy(details={"total": total, "valid": valid})
    if score >= 0.9:
        return Signal.degraded(details={"total": total, "valid": valid, "dangling": dangling})
    return Signal.critical(details={"total": total, "valid": valid, "dangling": dangling})
```

### SIGNALS

```yaml
signals:
  healthy: "All non-null style_id references resolve to valid Thing(type=style) nodes"
  degraded: "Some style_id references are dangling (< 10% broken)"
  critical: "Many style_id references are dangling (>= 10% broken)"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.hourly
  max_frequency: "1/hour"
  burst_limit: 1
  backoff: "Skip next check if previous check took > 30s"
```

---

## INDICATOR: artist_attribution_coverage

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: artist_attribution_coverage
  client_value: "Every style in the catalog credits its creator. Uncredited styles mean broken attribution and future broken $MIND flow."
  validation:
    - validation_id: V2
      criteria: "Every Thing(type=style) has exactly one ->created_by-> link to an Actor"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - tuple
  semantics:
    tuple: "{ state: OK|ERROR, score: float (ratio of attributed styles) }"
  aggregation:
    method: "score = styles_with_link / total_styles. ERROR if score < 1.0 (any unattributed style is a violation)."
    display: "tuple surfaced as 'N/M styles have creator attribution'"
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="artist_attribution_coverage",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="STYLE_MISSING_ATTRIBUTION",
    task="fix_missing_style_attribution",
)
def artist_attribution_coverage(ctx) -> dict:
    """Check all Thing(type=style) nodes have a ->created_by-> link."""
    styles = ctx.graph.query("MATCH (s:thing {subtype: 'style'}) RETURN s.id")
    total = len(styles)
    orphans = []
    for (style_id,) in styles:
        links = ctx.graph.query(f"MATCH (s)-[:link {{relation_kind: 'created_by'}}]->(a:actor) WHERE s.id = '{style_id}' RETURN a.id")
        if not links:
            orphans.append(style_id)
    if not orphans:
        return Signal.healthy(details={"total": total})
    return Signal.critical(details={"total": total, "orphans": orphans})
```

### SIGNALS

```yaml
signals:
  healthy: "All Thing(type=style) nodes have a ->created_by-> link"
  critical: "One or more Thing(type=style) nodes lack a ->created_by-> link"
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: cron.daily
  max_frequency: "1/day"
  burst_limit: 1
  backoff: "None -- daily is already infrequent"
```

---

## HOW TO RUN

```bash
# Run all health checks for this module (when implemented)
mind doctor --module style_system

# Run a specific checker
mind doctor --check style_reference_integrity
```

---

## KNOWN GAPS

- No checker yet for material_completeness (V4) -- requires the resolution pipeline to exist first
- No checker yet for effects_independence (V3) -- requires scanning style_variant fields for effect keys
- No checker for skeleton universality (V6) -- requires validating style content does not contain joint modifications

<!-- @mind:todo Implement material_completeness_checker once style_resolver.js exists -->
<!-- @mind:todo Implement effects_independence_checker: scan all style_variant dicts for glow/particles/trail/pulse keys -->
<!-- @mind:todo Implement skeleton_universality_checker: validate style content does not modify joint definitions -->

---

## MARKERS

<!-- @mind:todo Create runtime check implementations when style system code is built -->
<!-- @mind:todo Wire checkers to Doctor framework once health runtime exists in this repo -->
<!-- @mind:proposition Add a "style popularity" health metric: track adoption count per style over time -->
<!-- @mind:escalation Do we need a real-time alert when ->created_by-> link is missing, or is daily scan sufficient? -->
