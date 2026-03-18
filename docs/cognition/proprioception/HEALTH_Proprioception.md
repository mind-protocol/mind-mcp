# Proprioception — Health: Runtime Verification

```
STATUS: DESIGNING
CREATED: 2026-03-18
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
THIS:            HEALTH_Proprioception.md (you are here)
SYNC:            ./SYNC_Proprioception.md

IMPL:            runtime/cognition/proprioception.py (to be created)
```

---

## HEALTH CHECKS

### H1: Stimulus Quality Check

**What:** Verify that all emitted stimuli contain qualitative natural-language content with no raw numeric leakage.

**How:** After each tick, scan stimulus content strings for patterns indicating numeric leakage: bare floats (regex `\b\d+\.\d+\b`), coordinate tuples, internal tool names (`mcp__`), node IDs.

**Frequency:** Every tick (cheap string scan).

**Signal:**
- HEALTHY: Zero matches across all stimuli in the tick
- DEGRADED: Any match found — log the offending stimulus, continue
- FAILED: Persistent matches across 10+ consecutive ticks — proprioception is broken

### H2: Hysteresis Effectiveness

**What:** Verify that hysteresis is preventing stimulus spam without causing stimulus starvation.

**How:** Track per-channel emission counts over a rolling window of 100 ticks. Healthy range: 0-10 emissions per channel per window. Above 10 = hysteresis too loose. Zero emissions for 200+ ticks while BodyState has non-neutral values = hysteresis too tight (starvation).

**Frequency:** Every 100 ticks.

**Signal:**
- HEALTHY: All channels within expected emission range
- DEGRADED: One or more channels emitting > 10 per window (spam) or 0 per 200 ticks with active BodyState (starvation)
- FAILED: A channel emitting on every tick (hysteresis completely broken)

### H3: Tick Performance

**What:** Verify that the proprioception tick completes within the performance budget (< 1ms).

**How:** Time the `proprioception_tick()` call. Track P50, P95, P99 latencies over a rolling window.

**Frequency:** Every tick (cheap timer).

**Signal:**
- HEALTHY: P99 < 1ms
- DEGRADED: P99 > 1ms but P50 < 0.5ms (occasional slowdowns, likely texture cache miss)
- FAILED: P50 > 1ms (proprioception is consistently slow, degrading tick loop)

### H4: Channel Coverage

**What:** Verify that all eight channels are active and producing stimuli when conditions warrant.

**How:** Track which channels have emitted at least once in the last 1000 ticks. If a channel has never emitted and BodyState contains values that should trigger it (e.g., wind_intensity=0.8 but vent channel never fires), that channel is broken.

**Frequency:** Every 1000 ticks.

**Signal:**
- HEALTHY: All channels that have non-neutral BodyState values have emitted at least once
- DEGRADED: One channel has not emitted despite triggering conditions
- FAILED: Multiple channels silent despite triggering conditions

### H5: Immersion Attenuation

**What:** Verify that water immersion correctly attenuates non-water stimuli.

**How:** When water_level > 0.3, check that non-eau stimuli have reduced energy_budget compared to their baseline. Compare emitted energy against expected attenuated energy.

**Frequency:** Whenever water_level > 0.3 (event-driven).

**Signal:**
- HEALTHY: Non-water stimuli properly attenuated
- DEGRADED: Some stimuli not attenuated (attenuation code path bypassed)
- FAILED: Immersion has no effect on other channels

### H6: Texture Cache Freshness

**What:** Verify that the texture familiarity cache is being refreshed and not serving stale data.

**How:** Track cache age. The cache should refresh every 50 ticks. If it goes 200+ ticks without refresh, it may be stuck.

**Frequency:** Every 50 ticks.

**Signal:**
- HEALTHY: Cache refreshed within expected interval
- DEGRADED: Cache older than 100 ticks (graph may be slow)
- FAILED: Cache older than 500 ticks (cache refresh is broken, texture grounding is using stale data)

### H7: Comfort Composite Range

**What:** Verify that the comfort composite value stays within [-1.0, +1.0] and is not stuck at a constant value.

**How:** Track comfort_composite over a rolling window. If it stays at exactly 0.0 for 500+ ticks while stimuli are being emitted, the computation is likely broken.

**Frequency:** Every 100 ticks.

**Signal:**
- HEALTHY: Comfort composite varies and stays in range
- DEGRADED: Comfort composite stuck at one value for 500+ ticks
- FAILED: Comfort composite outside [-1.0, +1.0] range

---

## HEALTH DASHBOARD SUMMARY

| Check | What | Threshold | Priority |
|-------|------|-----------|----------|
| H1 | Stimulus quality (no numerics) | Zero leaks per tick | CRITICAL |
| H2 | Hysteresis effectiveness | 0-10 per channel per 100 ticks | HIGH |
| H3 | Tick performance | P99 < 1ms | HIGH |
| H4 | Channel coverage | All active channels emit | MEDIUM |
| H5 | Immersion attenuation | Non-water energy reduced when submerged | MEDIUM |
| H6 | Texture cache freshness | Refresh every 50 ticks | LOW |
| H7 | Comfort composite range | In [-1.0, +1.0], not stuck | LOW |

---

## MARKERS

<!-- @mind:todo Implement H1-H7 as runtime health checks in proprioception.py, callable via mind doctor -->

<!-- @mind:todo Add H3 latency tracking to the tick runner's performance metrics -->
