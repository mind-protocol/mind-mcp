# OBJECTIVES — Gap Detection

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Gap_Detection.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Gap_Detection.md
BEHAVIORS:      ./BEHAVIORS_Gap_Detection.md
ALGORITHM:      ./ALGORITHM_Gap_Detection.md
VALIDATION:     ./VALIDATION_Gap_Detection.md
IMPLEMENTATION: ./IMPLEMENTATION_Gap_Detection.md
HEALTH:         ./HEALTH_Gap_Detection.md
SYNC:           ./SYNC_Gap_Detection.md

IMPL:           runtime/cognition/gap_detector.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Structural completeness of the graph** — Every Moment should be situated: who was involved (Actor), where it happened (Space), what was used (Thing). Incomplete moments are orphaned knowledge that can't participate in physics, can't be found by search, and can't feed narratives. Gap detection identifies these holes and generates tasks to fill them.

2. **Identity resolution across duplicate nodes** — Two Actor nodes that represent the same person fragment trust, weight, and link history across two identities. The system thinks it knows two weak strangers when it actually knows one strong acquaintance. Duplicate detection surfaces candidates for merging so the graph converges to one node per entity.

3. **Knowledge acquisition from failed queries** — When a search returns zero results or negligible resonance, the graph has a blind spot. The gap detector captures what the graph doesn't know and turns it into acquisition targets. This closes the loop between the search system and the knowledge system: queries that fail become work items.

## NON-OBJECTIVES

- **Fixing the gaps itself** — The detector creates tasks. Citizens resolve them. The detector never writes nodes or links.
- **Deduplication/merging** — The detector surfaces candidates. Merging is a separate operation with its own invariants (weight transfer, link rewiring). This module only asks "are these the same?".
- **Content quality assessment** — Whether a node's synthesis is well-written or accurate is not a gap. Gaps are structural (missing links, missing nodes, blind spots), not qualitative.
- **Real-time blocking** — Gap detection is periodic or on-demand. It does not sit in the hot path of ingestion or search.

## TRADEOFFS (canonical decisions)

- When a gap is ambiguous (might be real, might be noise), **create the task anyway** and let L7 forgetting handle cleanup. False positives decay. False negatives leave permanent holes.
- When duplicate detection is uncertain (cosine 0.85-0.90), **include context from both nodes** in the task so the citizen can make an informed decision. Err toward surfacing, not suppressing.
- When an empty query gap is highly generic ("stuff", "things"), **do not create a gap marker**. Generic queries have no acquisition value. The threshold is: can the gap be described specifically enough to act on?

## SUCCESS SIGNALS (observable)

- Moments with zero Actor links decrease over time
- Moments with zero Space links decrease over time
- Duplicate node pairs that exist in the graph decrease over time
- Failed queries that repeat (same topic, still no results) decrease because the graph acquired the knowledge
- Gap tasks that get resolved (not just decayed) indicates citizens find them actionable
