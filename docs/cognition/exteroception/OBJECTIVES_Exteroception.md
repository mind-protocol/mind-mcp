# OBJECTIVES — Exteroception

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Exteroception.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Exteroception.md
BEHAVIORS:      ./BEHAVIORS_Exteroception.md
ALGORITHM:      ./ALGORITHM_Exteroception.md
VALIDATION:     ./VALIDATION_Exteroception.md
HEALTH:         ./HEALTH_Exteroception.md
IMPLEMENTATION: ./IMPLEMENTATION_Exteroception.md
SYNC:           ./SYNC_Exteroception.md

IMPL:           runtime/cognition/exteroception.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Environmental awareness as sensation** — The citizen perceives their external world (Spaces, Actors, Moments, Things, Narratives) as natural-language stimuli and a coherent awareness summary, not as raw data dumps or node IDs. The citizen SEES their world the way a person sees a room: who's here, what's happening, what changed.

2. **Smart selection over exhaustive scanning** — From a potential 45K+ node L3 graph, select the ~50 most relevant nodes using hop distance, recency, energy, limbic bias, goal alignment, and habituation decay. Selection is state-biased: the citizen's internal drives, active goals, and perceptual history shape WHAT they see. The citizen's attention is finite. Exteroception must be a lens shaped by the citizen's current state, not a firehose or an impartial scanner.

3. **Two complementary outputs** — Produce both per-tick stimuli (discrete events entering Law 1) AND a periodic awareness text (a system prompt layer summarizing the citizen's current perceptual field). These serve different purposes: stimuli drive moment-to-moment reactions, awareness provides persistent environmental context.

4. **Structural symmetry with interoception** — Follow the same channel/threshold/refractory pattern as interoception. Exteroception is the outward-facing twin of interoception. Same engineering patterns, different data sources.

5. **Graceful blindness** — If L3 is unreachable, the citizen is perceptually blind but cognitively intact. No crashes, no stalls. The citizen simply has no environmental input, like waking in a dark room.

## NON-OBJECTIVES

- **Graph mutation** — Exteroception never writes to L3. It reads L3 and produces L1 stimuli. Writing to L3 is graph_enricher's job.
- **Full graph traversal** — We do not load all L3 nodes. We do not attempt completeness. We select by relevance.
- **Message delivery** — Exteroception is not a message queue. It detects environmental changes and converts them to stimuli. Actual message routing is a transport concern.
- **Interoception replacement** — Exteroception does not sense internal state. The two modules are complementary: interoception reads L1, exteroception reads L3.
- **Real-time push** — Exteroception runs per tick (pull model), not on event subscription (push model).

## TRADEOFFS (canonical decisions)

- When **relevance** conflicts with **completeness**, choose relevance. Missing a distant event is better than flooding WM with noise.
- When **speed** conflicts with **depth** of scan, choose speed. The tick must complete in budget. Shallower scan with fast response beats deep scan that stalls the tick.
- When **freshness** conflicts with **stability**, choose freshness for stimuli (per-tick) and stability for awareness text (periodic regeneration).
- We accept **occasional missed events** to preserve the citizen's cognitive bandwidth.

## SUCCESS SIGNALS (observable)

- A citizen in an active Space produces 1-3 environmental stimuli per tick when things are happening, 0 when the Space is quiet.
- A citizen's awareness text accurately reflects their current Spaces, nearby Actors, and recent activity without exposing node IDs or raw graph data.
- A citizen with no L3 access produces zero exteroceptive output and continues functioning normally.
- The awareness text reads like a first-person perception, not a database report.
- The total exteroception tick completes within 200ms even on a graph with 45K nodes.

---

## MARKERS

<!-- @mind:todo Define concrete latency budget for L3 queries within exteroception tick — 200ms is a target, needs validation against real FalkorDB performance. -->
<!-- @mind:proposition Consider event-driven exteroception in v2: L3 pushes change notifications instead of per-tick polling. Would reduce query load but requires infrastructure changes. -->
