# Proprioception — SYNC: Current State

```
STATUS: DESIGNING
UPDATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
PATTERNS:        ./PATTERNS_Proprioception.md
BEHAVIORS:       ./BEHAVIORS_Proprioception.md
ALGORITHM:       ./ALGORITHM_Proprioception.md
VALIDATION:      ./VALIDATION_Proprioception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Proprioception.md
HEALTH:          ./HEALTH_Proprioception.md
THIS:            SYNC_Proprioception.md (you are here)

IMPL:            runtime/cognition/proprioception.py (to be created)
```

---

## Maturity

STATUS: DESIGNING

**What is canonical (designed, documented):**
- Full doc chain: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC
- Eight sense channels defined: 4 somatic (limb, force, accelerometer, thermoception) + 4 environmental (vent/wind, eau/water, pression/pressure, texture)
- BodyState dataclass with all fields including environmental: wind_intensity, wind_direction, water_level, pressure, surface_texture
- Hysteresis mechanism for all channels
- Immersion attenuation (water muffles other senses)
- Comfort composite (weighted blend across all channels)
- Texture grounding (familiarity-based stability modifier from graph history)
- Pressure cognitive rhythm modifier (breathing metaphor)
- 8 validation invariants (V1-V8)
- 7 health checks (H1-H7)

**What is NOT yet built:**
- `runtime/cognition/proprioception.py` — the actual implementation
- `tests/test_proprioception.py` — unit tests
- Integration with tick_runner_l1_cognitive_engine.py
- Integration with metabolism.py (record_light_input, set_rhythm_factor)
- BodyState WebSocket protocol with engine team

---

## Recent Changes

### 2026-03-18: Full doc chain created with environmental senses

NLR specified four environmental sense channels to add to the proprioception module:

1. **Vent (Wind)** — wind_intensity (0=calm, 1=gale) + wind_direction (unit vector). Affects comfort, movement resistance, exposure feeling. Suppressed when submerged.
2. **Eau (Water)** — water_level (0=dry, 0.5=wading, 1.0=submerged). Near water changes acoustics. Submersion muffles all other senses (immersion attenuation).
3. **Pression (Pressure)** — pressure (0=vacuum, 0.5=normal, 1.0=crushing). Affects cognitive rhythm — high pressure = faster/shallower processing, low pressure = slower/deeper. The "breathing metaphor."
4. **Texture** — surface_texture ("stone"|"wood"|"grass"|"metal"|"water"|"sand"). Familiar texture boosts stability (grounding). Unfamiliar texture produces subtle unease. Requires graph history lookup.

These were integrated across all eight doc chain files.

---

## Handoffs

### For @nervo (implementation):
- Full doc chain is ready. ALGORITHM has pseudocode for all 8 channels + immersion attenuation + comfort composite.
- BodyState dataclass is specified with exact field names, types, and ranges.
- Start with `runtime/cognition/proprioception.py`, implement the BodyState and ProprioceptionModule classes.
- The texture channel requires graph access for familiarity lookup — use caching (every 50 ticks).
- Integration with tick runner: call `proprioception.tick()` pre-Law-1, inject returned stimuli.

### For engine team:
- Need to define the BodyState WebSocket protocol. What JSON format does the engine send? What frequency?
- Environmental fields (wind, water, pressure, texture) must be populated by the engine's weather/world simulation.
- If the engine does not support a field, it should send neutral defaults (wind_intensity=0.0, water_level=0.0, pressure=0.5, surface_texture="stone").

---

## Open Questions

1. Should proprioception run every tick or at a slower cadence (e.g., every 5 ticks)?
2. B12 cross-feed: should luminosity directly modify circadian_phase on metabolism, or inject a separate stimulus?
3. V8 texture familiarity: when FalkorDB is down, return neutral (0.5) or skip texture channel entirely?
4. Should the pressure rhythm_factor directly modify metabolism tick pacing, or be advisory only?

---

## MARKERS

<!-- @mind:todo Create runtime/cognition/proprioception.py — implementation is the next step -->
<!-- @mind:todo Define BodyState WebSocket protocol with engine team -->
<!-- @mind:todo Resolve open questions 1-4 with NLR -->
