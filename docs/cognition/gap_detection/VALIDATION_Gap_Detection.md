# Gap Detection — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
PATTERNS:        ./PATTERNS_Gap_Detection.md
BEHAVIORS:       ./BEHAVIORS_Gap_Detection.md
THIS:            VALIDATION_Gap_Detection.md (you are here)
ALGORITHM:       ./ALGORITHM_Gap_Detection.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gap_Detection.md
HEALTH:          ./HEALTH_Gap_Detection.md
SYNC:            ./SYNC_Gap_Detection.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants define when the gap detector is working correctly versus when it has failed its purpose. A gap detector that creates bad tasks is worse than no detector at all, because bad tasks waste citizen attention and erode trust in the task system.

---

## INVARIANTS

### V1: Gap Tasks Carry Sufficient Context

**Why we care:** A gap task that says "Moment X needs an Actor link" but doesn't include the Moment's content forces the citizen to re-query the graph, defeating the purpose of gap detection. If tasks don't carry enough context to resolve, citizens will ignore them, and gaps will persist.

```
MUST:   Every gap task's synthesis field contains: (1) the source node's content (truncated to 300 chars),
        (2) a description of existing links on the source node, (3) a specific question to answer
NEVER:  Create a task with only a node ID and gap type — no bare references
```

### V2: No Duplicate Gap Tasks

**Why we care:** Running gap detection twice on the same graph should not produce two tasks for the same gap. Duplicate tasks dilute citizen attention, inflate the task queue, and make the gap detection system appear noisy and unreliable.

```
MUST:   Task IDs are deterministic: same gap = same task ID every time
MUST:   Before creating a task, check whether a non-completed task with that ID exists
NEVER:  Create two active tasks for the same missing link or the same duplicate pair
```

### V3: Detector Never Modifies Graph Structure

**Why we care:** The gap detector is a diagnostic tool, not a surgeon. If it starts creating links or merging nodes, it bypasses citizen judgment and introduces a new source of graph mutations that's hard to audit and easy to get wrong. The separation between detection and resolution is what makes the system safe to run aggressively.

```
MUST:   The detector's only write operations are: create_task() and energy refresh on existing tasks
NEVER:  Create links between nodes, merge nodes, delete nodes, or modify node content
NEVER:  Call graph_write or any link/node mutation outside of task creation
```

### V4: Empty Query Gaps Require Minimum Query Quality

**Why we care:** Creating gap markers for gibberish queries ("aaa", "test test test"), single-word queries, or all-stop-word queries pollutes the knowledge acquisition queue with noise. The gap system should only capture genuinely useful blind spots.

```
MUST:   Empty query gap creation requires: query length >= 3 words, not all stop words,
        embedding vector has reasonable norm (not zero, not outlier)
NEVER:  Create a gap marker for queries that cannot be meaningfully acted upon
```

### V5: Scan Completes Within Bounded Time

**Why we care:** Gap detection runs inside the physics tick loop (every N ticks). If it takes longer than the tick interval, it stalls the entire physics engine. The detector must be bounded and interruptible.

```
MUST:   Each scan pass has a configurable timeout
MUST:   Duplicate scan is capped at MAX_CANDIDATES_PER_SCAN (default 50)
MUST:   Missing link scan uses batch Cypher queries, not per-node queries
NEVER:  Let gap detection stall the physics tick beyond the allowed budget
```

### V6: Persistent Gaps Stay Visible

**Why we care:** A gap that persists across multiple scans (nobody has resolved it) should not silently decay away via L7 forgetting if the structural problem still exists. The energy refresh mechanism on re-detected gaps prevents this. However, gaps where the original node has been deleted should not be refreshed.

```
MUST:   When a gap is re-detected, the existing task's energy is refreshed to at least the base energy for that gap type
MUST:   Before refreshing, verify the source node still exists (the gap is still real)
NEVER:  Refresh energy on a gap task whose source node has been deleted — let it decay
```

### V7: Duplicate Detection Threshold Is Not Crystallization

**Why we care:** Crystallization (L10) is about merging dense clusters into hub narratives — it's a physics operation. Duplicate detection is about identity resolution: "are these two nodes the same real-world entity?" They look similar (both involve merging) but serve different purposes and use different thresholds. Confusing them would either make crystallization too aggressive or duplicate detection too timid.

```
MUST:   Duplicate detection uses cosine similarity threshold (0.85 default) independently of crystallization parameters
MUST:   Duplicate tasks are clearly labeled as identity resolution, not crystallization
NEVER:  Route duplicate detection through the crystallization engine
NEVER:  Use crystallization thresholds for duplicate detection or vice versa
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
| V1 | Tasks are actionable without re-querying | CRITICAL |
| V2 | No task spam from duplicate detection runs | CRITICAL |
| V3 | Detection-resolution separation (detector is read-only) | CRITICAL |
| V4 | Knowledge acquisition queue is signal, not noise | HIGH |
| V5 | Physics tick not stalled by gap detection | HIGH |
| V6 | Persistent gaps don't silently disappear | MEDIUM |
| V7 | Identity resolution is not crystallization | MEDIUM |

---

## MARKERS

<!-- @mind:todo V5 needs concrete timeout values once we benchmark scan performance on real graphs -->
<!-- @mind:proposition V4 could be extended with a learned stop-word list from the citizen's own vocabulary, not just generic English stop words -->
