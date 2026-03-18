# OBJECTIVES — Subcall

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against 3edd76b
```

---

## CHAIN

```
THIS:            OBJECTIVES_Subcall.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Subcall.md
BEHAVIORS:      ./BEHAVIORS_Subcall.md
ALGORITHM:      ./ALGORITHM_Subcall.md
VALIDATION:     ./VALIDATION_Subcall.md
IMPLEMENTATION: ./IMPLEMENTATION_Subcall.md
HEALTH:         ./HEALTH_Subcall.md
SYNC:           ./SYNC_Subcall.md

IMPL:           mcp/tools/subcall_handler.py
                mcp/tools/subcall_auto.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Zero-LLM telepathy** — probe any citizen's cognitive graph without waking an LLM on the target side. One embedding computation + one graph query. Milliseconds, not seconds. This is the defining constraint: subcall is graph physics, never token generation.

2. **Thermodynamic routing** — target selection and resonance ranking are driven by a single formula whose shape is set by limbic profiles (24 scenarios). No if/then routing logic. The formula morphs continuously as arousal, drives, and trust shift. The same code path handles a panic-mode sniper shot and a calm-mode dragnet sweep.

3. **Non-read-only stimulus injection** — a subcall is telepathy, not a database lookup. The query enters the target's graph as energy (Law 1). Nodes that resonate gain energy, may enter working memory, and over repeated subcalls can crystallize (Law 10) in the target's brain. This is by design.

4. **Intelligence briefing output** — every response is an actionable briefing, not a data dump. Four layers: telemetry narrative (state + delta + recommendation), structured resonance data, graph extraction (medoid + edge chain), and WM-injectable inner voice. The caller gets analysis, not raw nodes.

5. **Continuous thermodynamic economics** — subcall is fully free at the API layer. No upfront cost. $MIND flows continuously via the vertical membrane: `token_flow_per_tick = link.trust * link.weight` (while limbic_delta > 0). The cognitive graph and the metabolic economy are mathematically indistinguishable.

## NON-OBJECTIVES

- **LLM-generated answers** — subcall never invokes an LLM on the target. If you want an LLM conversation, use `/call`.
- **Permission gating** — there are no access control checks. Any citizen can subcall any other citizen. Trust shapes the routing formula, not a permission boundary.
- **Real-time conversation** — subcall is fire-and-response, not a dialogue. The target is never "aware" they were queried.
- **Exact semantic search** — subcall returns resonance patterns (what activated), not keyword matches. Results are emergent, not deterministic.

## TRADEOFFS (canonical decisions)

- When routing precision conflicts with formula simplicity, choose formula simplicity. The 24 scenarios differ only in limbic drive values, not in code paths.
- When response richness conflicts with latency, choose richness for single-target mode (full content, 3 output layers) and latency for broadcast modes (truncated content, summary stats).
- We accept that repeated subcalls will modify the target's graph state (energy injection, potential crystallization) to preserve the physics-first design. Read-only subcall would break Law 1.
- We accept embedding computation cost (~50ms) to preserve vector similarity search quality over keyword fallback.

## SUCCESS SIGNALS (observable)

- Single-target subcall completes in under 2 seconds
- Auto-select mode scans 50 citizens and returns 3-5 diverse results in under 5 seconds
- Intelligence briefing contains all 4 layers (telemetry, structured, graph extraction, inner voice) for single-target calls
- Zero LLM tokens spent on the target side (verified by cost: 0 in every response)
- Broadcast to 200 citizens (random:200) completes in under 10 seconds
