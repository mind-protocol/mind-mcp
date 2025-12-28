# MECHANISMS — Contradiction Pressure (v0)

```
STATUS: DRAFT
CREATED: 2025-12-21
```
---

## CHAIN

- PATTERNS_Simultaneity_And_Contradiction.md
- PATTERNS_Attention_Energy_Split.md
- BEHAVIORS_Attention_Split_And_Interrupts.md
- VALIDATION_Attention_Split_And_Interrupts.md

---

## PURPOSE

Represent "alternatives remain alive" as a physical local force:
- contradictions (RELATES.polarity < 0) create pressure,
- pressure influences surfacing indirectly (via membrane / thresholds / pressure boost),
- without deleting alternatives and without fiat narration.

---

## INPUTS

### Links (RELATES / narrative_link)
- `polarity` in [-1,+1] (negative = contradiction)
- `strength` in [0,1]
- `confidence` in [0,1]
- `role` in {descriptive, evidential, normative, procedural}
- `mode` typically semantic/structural

### Context
- `contradiction_gain(place)` → float in [0,1] (as function)
- `pressure_decay(place)` → float in [0,1] (as function)

### Neighborhood
- contradictions are computed **only within player neighborhood** (or within a place scope for per-place mood)

---

## EDGE PRESSURE

For each contradiction edge e where polarity < 0:

```
edge_pressure(e) = (-polarity) * strength * confidence
```

Total pressure (raw):
```
raw = Σ edge_pressure(e)
```

Scaled + bounded:
```
pressure_instant = clamp( contradiction_gain(place) * raw, 0, 1 )
```

With temporal accumulation:
```
pressure_next = clamp( pressure_prev * pressure_decay(place) + pressure_instant, 0, 1 )
```

---

## EFFECT (INDIRECT ONLY)

Pressure MUST NOT create nodes or set statuses directly.

It may:
- scale `dramatic_pressure` input to `apply_dramatic_boost`
- offset activation threshold via membrane (dynamic function)
- adjust decay scale via membrane

---

## BEHAVIORAL EXPECTATIONS

- After canonizing one moment among alternatives, CONTRADICTS links remain.
- If contradictions become visible in neighborhood, pressure rises.
- Pressure makes “clarify / crisis / reconcile” moments more likely to surface mechanically (through parameter modulation), not through direct narration.

---

## FAILURE MODES

- pressure too high → constant drama, no calm
- pressure too low → alternatives die silently (plateau)
- non-local pressure → contamination across places (violates scoping)

---

## VALIDATION HOOKS

- V6 contradiction visibility interrupting (if you keep that behavior)
- Health: top contradiction contributors + pressure value per place/player
