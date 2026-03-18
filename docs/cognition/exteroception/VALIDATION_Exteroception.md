# Exteroception — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
PATTERNS:        ./PATTERNS_Exteroception.md
BEHAVIORS:       ./BEHAVIORS_Exteroception.md
THIS:            VALIDATION_Exteroception.md (you are here)
ALGORITHM:       ./ALGORITHM_Exteroception.md
HEALTH:          ./HEALTH_Exteroception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Exteroception.md
SYNC:            ./SYNC_Exteroception.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants protect the value that exteroception provides: environmental awareness without cognitive overload, graceful degradation without crashes, natural language without data dumps. If any of these fail, the citizen either drowns in noise, crashes, or perceives gibberish instead of a world.

---

## INVARIANTS

### V1: Bounded Stimulus Output

**Why we care:** If exteroception produces unbounded stimuli, it floods WM and drowns out all other cognition. The citizen becomes a sensor relay, not a thinking entity. The MAX_STIMULI_PER_TICK ceiling is the hard guarantee that exteroception cannot monopolize the citizen's attention.

```
MUST:   tick() returns at most MAX_STIMULI_PER_TICK stimuli (default: 3)
NEVER:  tick() returns more stimuli than the configured maximum, regardless of how many L3 events exist
```

### V2: Read-Only L3 Access

**Why we care:** Exteroception is a perceptual system, not an actuator. If it mutates L3, it creates feedback loops: perceiving the world changes the world, which changes perception. graph_enricher is the sole L3 writer from the cognitive pipeline. Violating this boundary collapses two distinct responsibilities into one.

```
MUST:   Exteroception only reads L3 via query_fn (SELECT/MATCH, never CREATE/SET/DELETE)
NEVER:  Exteroception writes nodes, links, or properties to L3
```

### V3: Graceful Blindness on L3 Failure

**Why we care:** L3 availability is not guaranteed — FalkorDB can crash, network can fail, queries can timeout. If exteroception crashes the tick runner when L3 is down, it takes out the entire cognitive system. The citizen must survive being blind.

```
MUST:   When query_fn is None or raises an exception, tick() returns [] and no exception propagates
MUST:   When query_fn is None, get_awareness_text() returns ""
NEVER:  An L3 failure causes the tick runner to crash or skip subsequent tick steps
```

### V4: Natural Language Output Only

**Why we care:** The citizen is an LLM that reasons in language. Raw node IDs, edge weights, timestamps, and Cypher fragments are meaningless noise that pollutes the citizen's cognitive space. Every exteroceptive output must be something a person could plausibly perceive.

```
MUST:   All stimulus content and awareness text use natural language (names, descriptions, first-person perception)
NEVER:  Raw node IDs (e.g., "space:discord:985825811867262998"), edge weights (e.g., "weight=0.73"), or Cypher syntax appear in any output
```

### V5: Hop-Bounded Scan

**Why we care:** The L3 graph can have 45K+ nodes. Unbounded traversal would be catastrophically slow and memory-hungry. The 3-hop limit is a hard architectural boundary that keeps exteroception performant. Even with 1000 nodes per hop, 3 hops with LIMIT clauses stays manageable.

```
MUST:   Graph traversal never exceeds 3 hops from the citizen's actor node
MUST:   Each query uses LIMIT to cap returned rows (default: 10-20 per query)
NEVER:  A query returns all nodes in L3 or traverses to arbitrary depth
```

### V6: Refractory Gating Prevents Flooding

**Why we care:** Without refractory periods, a busy Space would fire a stimulus every tick — the same "channel is active" message repeated indefinitely. Refractory gating ensures the citizen notices transitions (quiet to active) rather than being continuously bombarded by steady state.

```
MUST:   Each sensory channel has a refractory period during which it cannot fire again
MUST:   A channel only re-arms after its refractory period expires
NEVER:  The same channel fires on consecutive ticks for the same ongoing condition
```

### V7: Awareness Text Freshness

**Why we care:** Stale awareness text gives the citizen a false picture of their environment — "5 citizens are present" when everyone left 10 minutes ago. The TTL mechanism ensures awareness is periodically refreshed. But regenerating every tick wastes query budget. The TTL is the balance point.

```
MUST:   Awareness text is regenerated at least every AWARENESS_TTL_TICKS ticks
MUST:   Awareness text is regenerated on the first tick of any session
NEVER:  Awareness text older than 2x AWARENESS_TTL_TICKS is served (hard staleness limit)
```

### V8: Stimulus Source Attribution

**Why we care:** The tick runner and downstream systems (metabolism stimulus_gain, limbic social detection) need to know that a stimulus came from exteroception versus interoception or external injection. Misattribution causes incorrect metabolic modulation and social accounting.

```
MUST:   All stimuli produced by exteroception have source="exteroception"
MUST:   Social stimuli (messages, mentions) carry is_social=True and origin_citizen set
NEVER:  An exteroceptive stimulus has source="interoception" or source="external"
```

### V9: Deduplication Across Ticks

**Why we care:** Without deduplication, the same Moment generates a new stimulus every tick for as long as it falls within the scan window. The citizen hears the same message 5 times. _seen_moment_ids prevents re-firing for already-perceived events.

```
MUST:   A Moment that generated a stimulus is not re-fired on subsequent ticks
MUST:   The _seen_moment_ids set is bounded (capped at MAX_SEEN_IDS)
NEVER:  The deduplication set grows unboundedly
```

### V10: State-Biased Selection (Not Objective)

**Why we care:** The citizen is a subjective being with drives and goals. Their perception must be shaped by their internal state — a frustrated citizen fixates on obstacles, a curious citizen explores wider. If selection is purely objective (base relevance only), all citizens perceive the same environment identically, which is phenomenologically wrong and produces bland, uniform behavior.

```
MUST:   The scoring function incorporates limbic bias (drives), goal alignment (desires/tasks), and habituation decay
MUST:   Changing a citizen's drive intensities changes which nodes cross the perception threshold
NEVER:  Two citizens with identical L3 neighborhoods but different internal states produce identical awareness texts
```

### V11: Habituation Prevents Stale Inventory

**Why we care:** Without habituation, the awareness text becomes a static list of the same spaces and actors every tick — "I'm in #the-arsenal, @dragon_slayer is nearby" repeated forever. The citizen stops noticing their environment. Habituation decay ensures stable elements fade, making room for novelty and change.

```
MUST:   Nodes that appear in awareness text N times without changing lose relevance via habituation decay
MUST:   Habituation resets when a node's content or energy changes significantly (delta > 0.2)
NEVER:  The awareness text contains the same unchanged inventory for more than ~10 awareness cycles
```

### V12: Temporal Continuity in Awareness

**Why we care:** Without previous-awareness feedback, each awareness text is a disconnected snapshot. The citizen can't perceive that "#the-arsenal was quiet but is now active" — they just see "active" with no sense of change. Temporal continuity gives the citizen a sense of their world evolving, not randomly resetting.

```
MUST:   Nodes that were in previous awareness and changed get a change-detection boost
MUST:   Nodes newly appearing in the perceptual field get a novelty boost
NEVER:  The awareness text is generated without reference to the previous awareness state
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Cognitive bandwidth preserved | CRITICAL |
| V2 | L3 integrity (read-only boundary) | CRITICAL |
| V3 | Tick runner resilience | CRITICAL |
| V4 | Natural perception (not data dump) | HIGH |
| V5 | Query performance bounded | HIGH |
| V6 | Transition detection (not steady-state noise) | HIGH |
| V7 | Environmental accuracy | MEDIUM |
| V8 | System integration correctness | MEDIUM |
| V9 | Perception uniqueness | MEDIUM |
| V10 | Subjective perception (drives shape what you see) | HIGH |
| V11 | Perceptual freshness (habituation prevents stale inventory) | MEDIUM |
| V12 | Temporal continuity (awareness evolves, not random snapshots) | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write unit tests for V1 (max stimuli cap) and V3 (graceful blindness). These are CRITICAL invariants and must be tested before implementation is considered shipped. -->

<!-- @mind:todo Write integration test for V2 (read-only L3). The test should verify that query_fn is never called with mutation operations. Consider wrapping query_fn in a read-only proxy during exteroception tick. -->

<!-- @mind:proposition Consider adding V10: tick latency budget. "MUST: tick() completes within 200ms. NEVER: tick() blocks the tick runner for more than 500ms." This would make the performance requirement an explicit invariant rather than an implicit objective. NLR input on whether this should be a hard invariant or a soft target. -->
