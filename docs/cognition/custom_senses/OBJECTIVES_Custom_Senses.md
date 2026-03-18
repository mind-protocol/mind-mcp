# OBJECTIVES -- Custom Senses

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Custom_Senses.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Custom_Senses.md
BEHAVIORS:      ./BEHAVIORS_Custom_Senses.md
ALGORITHM:      ./ALGORITHM_Custom_Senses.md
VALIDATION:     ./VALIDATION_Custom_Senses.md
HEALTH:         ./HEALTH_Custom_Senses.md
IMPLEMENTATION: ./IMPLEMENTATION_Custom_Senses.md
SYNC:           ./SYNC_Custom_Senses.md

IMPL:           runtime/cognition/custom_senses.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Citizen-defined perception** -- Citizens can create their own sensory channels that scan the L3 graph for patterns they care about, producing stimuli that enter cognition through the same Law 1 pathway as built-in senses. This is the difference between a fixed set of senses designed by developers and a perceptual system that evolves with its inhabitants.

2. **Shareability and credit** -- A sense created by one citizen can be adopted by others through a simple graph link, with authorship tracked via `->created_by->`. Echo builds `gossip_radar`, Vox adopts it, Echo gets credited. Same economic pattern as styles and frequencies: creation produces shareable assets.

3. **Two-tier complexity** -- Simple senses are declarative YAML filters (no code, no sandbox, fast evaluation). Complex senses are Python scripts (sandboxed, `query_fn`-only, full graph query power). The YAML tier lowers the barrier to sense creation; the Python tier removes the ceiling. Same two-tier pattern as `graph_enricher`.

4. **Seamless integration with exteroception** -- Custom senses are additional channels in the exteroception engine, subject to the same gating mechanics: priority, refractory periods, max stimuli per tick. They do not bypass the perceptual pipeline -- they extend it.

## NON-OBJECTIVES

- **Replacing built-in channels** -- The 6 hardcoded exteroception channels (new_message, new_mention, narrative_shift, new_thing, actor_nearby, space_atmosphere) remain. Custom senses supplement, not replace.
- **Real-time push** -- Custom senses are pull-based (evaluated per tick or per N ticks), not event-driven push subscriptions. Push is a v2 concern.
- **Arbitrary code execution** -- Python senses do NOT have filesystem, network, or import access. They receive `query_fn` and nothing else. This is a sandbox, not a runtime extension.
- **Sense marketplace / economy** -- Pricing, trading, or licensing senses is out of scope. The graph tracks creation and adoption; economics are a layer above.

## TRADEOFFS (canonical decisions)

- When **simplicity** conflicts with **power**, provide both tiers (YAML and Python) rather than compromising either.
- When **security** conflicts with **flexibility**, choose security. Python senses run sandboxed even if it limits what they can do.
- When **tick performance** conflicts with **sense count**, cap the number of custom senses evaluated per tick rather than allowing unbounded scan time. The physics tick must never stall.
- We accept the **complexity of two formats** (YAML + Python) to preserve the **low barrier to simple senses** and the **no-ceiling for complex ones**.

## SUCCESS SIGNALS (observable)

- A citizen with `->perceives_with->` links to custom sense Things receives stimuli from those senses during tick execution
- A sense created by citizen A and adopted by citizen B produces stimuli for citizen B with correct attribution
- YAML senses evaluate in under 10ms per sense per tick
- Python senses evaluate in under 50ms per sense per tick (sandboxed)
- A citizen with zero custom senses experiences no performance difference from the current exteroception engine
- Adding or removing a `->perceives_with->` link dynamically changes the citizen's perceptual field within N ticks (where N = sense refresh interval)
