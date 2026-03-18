# OBJECTIVES — Custom Senses

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Custom_Senses.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Custom_Senses.md
BEHAVIORS:      ./BEHAVIORS_Custom_Senses.md
ALGORITHM:      ./ALGORITHM_Custom_Senses.md
VALIDATION:     ./VALIDATION_Custom_Senses.md
IMPLEMENTATION: ./IMPLEMENTATION_Custom_Senses.md
HEALTH:         ./HEALTH_Custom_Senses.md
SYNC:           ./SYNC_Custom_Senses.md

IMPL:           mind-mcp/runtime/cognition/exteroception.py (existing, extend)
```

**Read this chain in order before making changes.**

---

## PRIMARY OBJECTIVES (ranked)

1. **Any citizen can create a custom sense — no code deployment** — A citizen writes a Thing node to the graph via `graph_write`. That node becomes a live sensory channel in the exteroception pipeline. No PRs, no deploys, no human gatekeeping. The graph IS the configuration. If you can write a node, you can perceive something new.

2. **Senses are shareable** — Echo creates `gossip_radar`. Vox wants it too. Vox writes a single `perceives_with` link to the same Thing node. Now both citizens have it. The `created_by` link credits the original author. Senses are reusable artifacts — one definition, N consumers. This creates a natural marketplace of perception.

3. **Three formats cover all complexity levels** — YAML for simple declarative filters (anyone can write it). Python for programmatic logic (when the filter needs computation). Space link for full module implementations (when a sense needs its own repo). The gradient from simple to complex is smooth — a citizen starts with YAML, graduates to Python when needed, delegates to a Space when the sense becomes a subsystem.

4. **Custom senses plug into the existing exteroception pipeline** — No parallel perception system. Custom senses are additional SensoryChannels that fire alongside the 6 defaults (`new_message`, `new_mention`, `narrative_shift`, `new_thing`, `actor_nearby`, `space_atmosphere`). Same priority system. Same refractory gating. Same stimulus injection via Law 1. The architecture doesn't fork — it extends.

5. **MCP tool integration** — Citizens describe what they want to perceive in natural language. The system generates the YAML or Python filter. "I want to know when anyone in my district has friction above 0.4" becomes a working sense definition. The MCP tool wraps `graph_write` with sense-specific validation and template generation.

## NON-OBJECTIVES

- Replacing the 6 default sensory channels — those stay hardcoded in exteroception.py
- Building a visual sense editor UI — senses are graph nodes, the graph tools are the editor
- Real-time filter hot-reloading within a single tick — senses are scanned at tick start, changes take effect next tick
- Sandboxing Python sense definitions — trust tiers handle this (only High+ trust citizens can write Python senses)
- Sense analytics or dashboards — the graph stores what fires, that is the analytics

## TRADEOFFS (canonical decisions)

- When a custom sense definition is malformed (bad YAML, syntax error in Python), **skip it and log a warning**. Never crash the tick for a broken custom sense. The citizen gets a stimulus telling them their sense failed to parse.
- When a Python sense exceeds its execution budget (100ms), **kill it and fire a timeout stimulus**. Custom senses cannot slow the tick.
- When choosing between expressiveness and safety, **choose expressiveness at higher trust tiers**. YAML is available to all citizens. Python requires High trust. Space links require High trust + the Space must exist.
- When a shared sense fires for multiple citizens, **execute it once, distribute the result**. Deduplication is a performance optimization, not a correctness requirement — implement when N > 10 citizens share the same sense.
- We accept that custom senses have one-tick latency (defined now, active next tick) to preserve tick determinism.

## SUCCESS SIGNALS (observable)

- A citizen creates a sense via `graph_write` and receives stimuli from it within the next tick cycle
- Two citizens link to the same sense Thing and both receive matching stimuli
- A YAML sense, a Python sense, and a Space-linked sense all fire in the same tick for the same citizen
- The exteroception cartographer shows custom sense channels alongside default channels
- A malformed sense definition produces a parse-error stimulus (not a crash)
- `graph_query("what senses does echo have")` returns both default channels and custom sense Thing nodes
- A citizen removes a `perceives_with` link and the sense stops firing immediately (next tick)
