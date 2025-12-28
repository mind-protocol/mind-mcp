# SubEntity — Behaviors

```
STATUS: CANONICAL
VERSION: v1.9
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
THIS:           ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
IMPLEMENTATION: ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## PURPOSE

Behaviors define WHAT VALUE SubEntity exploration produces — observable
effects that matter to actors and the system. Not HOW it works (that's
ALGORITHM), but WHAT you get.

---

## BEHAVIORS

### B1: Actor Gets Answers

**Why it matters:** Actors need information to act.

**GIVEN:** Actor spawns exploration with query "What happened at the crossing?"
**WHEN:** Exploration completes
**THEN:** Actor receives ranked list of relevant narratives with alignment scores

**Observable value:** Actor can reference found narratives in subsequent
decisions and dialogue. The actor knows more than before.

**Objectives served:** O1 (Actors Get Useful Answers)

---

### B2: Gaps Get Filled

**Why it matters:** Missing understanding should crystallize into new knowledge.

**GIVEN:** Actor searches for something that doesn't exist as a narrative
**WHEN:** Exploration finds no satisfying matches AND novelty is high
**THEN:** New narrative crystallizes from the exploration path

**Observable value:** The graph grows richer. Future explorations find
what was missing. Knowledge compounds.

**Objectives served:** O2 (Gaps Become Knowledge)

---

### B3: Graph Learns From Attention

**Why it matters:** Frequently-explored paths should become easier to find.

**GIVEN:** Multiple explorations traverse similar paths
**WHEN:** Links are repeatedly colored by intention
**THEN:** Those paths become more prominent (higher weight, shaped embeddings)

**Observable value:** Common knowledge becomes faster to retrieve. The
graph reflects what actors care about. Hot paths stay hot.

**Objectives served:** O3 (Graph Learns From Use)

---

### B4: Parallel Perspectives Emerge

**Why it matters:** Complex queries deserve multiple angles.

**GIVEN:** Exploration branches at a decision point (Moment)
**WHEN:** Children explore in parallel
**THEN:** Actor receives findings from multiple perspectives

**Observable value:** Richer, more complete answers. "I found betrayal
AND denial" not just whichever came first.

**Objectives served:** O4 (Parallel Exploration Spreads)

---

### B5: Desperation Deepens Search

**Why it matters:** Critical needs should try harder.

**GIVEN:** Actor has high criticality (urgent need, nothing found yet)
**WHEN:** Exploration continues
**THEN:** Deeper paths explored, weaker alignments accepted

**Observable value:** Important searches don't give up easily. System
tries harder when it matters.

**Objectives served:** O5 (Urgency Deepens Search)

---

### B6: Exploration Respects Intent

**Why it matters:** Different goals need different strategies.

**GIVEN:** Actor asks to VERIFY (check for contradictions) vs SUMMARIZE
**WHEN:** Exploration traverses
**THEN:** VERIFY finds tensions; SUMMARIZE finds breadth

**Observable value:** Same query with different intent produces
appropriately different results. Intent shapes exploration.

**Objectives served:** O1, O6 (Answers, Context)

---

### B7: Found Knowledge Has Context

**Why it matters:** Bare facts aren't enough; emotional/relational context matters.

**GIVEN:** Exploration finds a narrative
**WHEN:** Narrative returned to actor
**THEN:** Alignment score + emotional state + path context included

**Observable value:** Actor knows not just WHAT but HOW MUCH it aligns
and the emotional tenor. Rich understanding, not bare data.

**Objectives served:** O6 (Context Accompanies Findings)

---

## ANTI-BEHAVIORS

### A1: Exploration Never Runs Forever

**MUST NOT:** Exploration that never terminates

**Observable harm:** System hangs, actor waits indefinitely, resources
exhausted.

**Prevention:** Timeout (default 30s), max steps (1000), max depth (10).

---

### A2: Parallel Work Never Duplicates

**MUST NOT:** Two siblings exploring the same path

**Observable harm:** Wasted computation, redundant results, inefficiency.

**Prevention:** Sibling divergence factor in link scoring penalizes
paths similar to sibling crystallization embeddings.

---

### A3: Crystallization Never Pollutes

**MUST NOT:** Creating narratives that duplicate existing knowledge

**Observable harm:** Graph bloat, confusing duplicate answers, noise.

**Prevention:** Novelty check (< 0.85 similarity) gates crystallization.

---

### A4: Exploration Never Loses Findings

**MUST NOT:** Child finds narrative but parent doesn't receive it

**Observable harm:** Actor misses relevant information. Silent data loss.

**Prevention:** Merge uses max(alignment) per narrative, crystallized
narratives get alignment 1.0.

---

### A5: Deep Search Never Ignores Shallow Wins

**MUST NOT:** Going to depth 10 when answer was at depth 2

**Observable harm:** Inefficient, slow responses, wasted exploration.

**Prevention:** Satisfaction-driven stopping. Find enough, stop.

---

## EDGE CASES

### E1: No Outgoing Links

**GIVEN:** SubEntity at node with no outgoing links
**WHEN:** SEEKING step executes
**THEN:** Transition to REFLECTING (backpropagate and potentially crystallize)

---

### E2: All Links Below Threshold

**GIVEN:** SubEntity at node where all links score below min_link_score
**WHEN:** Scoring completes
**THEN:** Transition to REFLECTING (treat as dead end)

---

### E3: Timeout During Branching

**GIVEN:** Parent waiting for children, timeout occurs
**WHEN:** asyncio.TimeoutError raised
**THEN:** ExplorationTimeoutError raised (no partial merge, fail loud)

---

### E4: Circular Path Detected

**GIVEN:** SubEntity about to traverse link to already-visited node
**WHEN:** Link scoring includes self_novelty
**THEN:** Self-novelty heavily penalizes (near zero score), avoided

---

### E5: Sibling Dies Early

**GIVEN:** Sibling SubEntity completes or errors before others
**WHEN:** Remaining siblings continue
**THEN:** Dead sibling's embedding still used for divergence (cached)

---

## INPUTS

| Input | Type | Source | Purpose |
|-------|------|--------|---------|
| actor_id | str | Caller | Who is exploring |
| query | str | Caller | WHAT to search for |
| query_embedding | List[float] | Caller (embed) | Semantic vector of query |
| intention | str | Caller | WHY searching |
| intention_embedding | List[float] | Caller (embed) | Semantic vector of intention |
| intention_type | enum | Caller | SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE |
| origin_moment | str | Caller | What triggered exploration |

---

## OUTPUTS

| Output | Type | Recipient | Purpose |
|--------|------|-----------|---------|
| found_narratives | Dict[str, float] | Actor | {narrative_id: alignment} |
| crystallized | Optional[str] | Actor | New narrative if created |
| satisfaction | float | Actor | How fulfilled [0,1] |
| depth | int | Logging | How deep we went |
| duration_s | float | Logging | How long it took |
| children_results | List[Result] | Logging | Child exploration results |

---

## OBJECTIVES COVERAGE

| Objective | Behaviors |
|-----------|-----------|
| O1: Actors Get Useful Answers | B1, B6, B7 |
| O2: Gaps Become Knowledge | B2 |
| O3: Graph Learns From Use | B3 |
| O4: Parallel Exploration Spreads | B4 |
| O5: Urgency Deepens Search | B5 |
| O6: Context Accompanies Findings | B6, B7 |
