# Gap Detection — Behaviors: Observable Effects of Graph Gap Scanning

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
THIS:            BEHAVIORS_Gap_Detection.md (you are here)
PATTERNS:        ./PATTERNS_Gap_Detection.md
ALGORITHM:       ./ALGORITHM_Gap_Detection.md
VALIDATION:      ./VALIDATION_Gap_Detection.md
HEALTH:          ./HEALTH_Gap_Detection.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gap_Detection.md
SYNC:            ./SYNC_Gap_Detection.md

IMPL:            runtime/cognition/gap_detector.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Unlinked Moments Produce Actionable Tasks

**Why:** A Moment without an Actor link is contextless knowledge — it happened but nobody was involved. A Moment without a Space link is unlocated — it happened but nowhere. These orphans degrade search quality (no propagation paths) and context assembly (citizen can't recall where/with whom something happened). The gap detector surfaces them as tasks so citizens can reconnect the graph.

```
GIVEN:  A Moment node exists in an L1 brain graph
WHEN:   The gap detector scans and finds zero Actor links on that Moment
THEN:   A task is created with type='task', category='gap_detection', sub_type='missing_actor_link'
AND:    The task synthesis includes the Moment's content, its existing links, and the question "Who was involved?"
AND:    The task is linked CONTRIBUTES_TO the 'citizen_operational' meta-objective
```

```
GIVEN:  A Moment node exists in an L1 brain graph
WHEN:   The gap detector scans and finds zero Space links on that Moment
THEN:   A task is created with type='task', category='gap_detection', sub_type='missing_space_link'
AND:    The task synthesis includes the Moment's content, its existing links, and the question "Where did this happen?"
```

```
GIVEN:  A Moment node's content mentions concrete objects, tools, or artifacts
WHEN:   The gap detector scans and finds zero Thing links on that Moment
THEN:   A task is created with type='task', category='gap_detection', sub_type='missing_thing_link'
AND:    The task synthesis includes the Moment's content and the question "What was used or discussed?"
```

### B2: Similar Nodes Surface As Merge Candidates

**Why:** Two Actor nodes for the same person fragment trust, weight, and link history. The system sees two weak strangers instead of one strong acquaintance. Two Space nodes for the same place mean memories get split across locations. Duplicate detection identifies these pairs so citizens can merge them and unify the graph.

```
GIVEN:  Two Actor nodes exist in the same graph scope
WHEN:   Their embedding cosine similarity exceeds 0.85
THEN:   A task is created with category='gap_detection', sub_type='potential_duplicate_actor'
AND:    The task synthesis includes both nodes' names, content, link counts, platform handles, and the question "Are these the same person? Merge?"
```

```
GIVEN:  Two Space nodes exist in the same graph scope
WHEN:   Their embedding cosine similarity exceeds 0.85
THEN:   A task is created with category='gap_detection', sub_type='potential_duplicate_space'
AND:    The task synthesis includes both nodes' names, content, link counts, and the question "Same place?"
```

### B3: Failed Queries Become Acquisition Targets

**Why:** When a citizen asks the graph a question and gets nothing back, the graph has a blind spot. If nobody records this, the blind spot persists indefinitely. By capturing the failed query as a gap marker, the system turns invisible ignorance into visible work. Repeated failures on the same topic escalate priority: the more the graph is asked about something it doesn't know, the more urgent it becomes to learn it.

```
GIVEN:  A graph_query call completes
WHEN:   The result set is empty OR all results have resonance below the gap threshold
THEN:   A gap marker node is created (or the energy on an existing marker for the same topic is incremented)
AND:    The gap marker captures the query text, the actor who asked, and the timestamp
```

```
GIVEN:  A gap marker already exists for a topic
WHEN:   Another query on the same topic fails
THEN:   The existing marker's energy is incremented (not a new marker)
AND:    The energy increase follows urgency accumulation: each repeat adds diminishing energy (logarithmic)
```

### B4: Existing Gap Tasks Are Not Duplicated

**Why:** Running gap detection twice should not create two tasks for the same missing link or the same duplicate pair. The detector checks for existing open tasks before creating new ones. This is deduplication of gap tasks, not deduplication of graph nodes.

```
GIVEN:  A gap (missing link or duplicate pair) was already detected in a previous scan
WHEN:   The same gap is detected again
THEN:   No new task is created
AND:    The existing task's energy may be refreshed (preventing L7 decay if the gap persists)
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Structural completeness | Fills the graph's missing connections so moments participate in physics and search |
| B2 | Identity resolution | Prevents identity fragmentation that degrades trust, weight, and context assembly |
| B3 | Knowledge acquisition | Closes the loop between search and knowledge: what the graph can't answer becomes what it learns next |
| B4 | All objectives | Prevents task spam that would bury real gaps in noise |

---

## INPUTS / OUTPUTS

### Primary Function: `scan_gaps()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `actor_id` | str | The citizen whose L1 brain graph to scan (for missing links and duplicates) |
| `adapter` | DatabaseAdapter | Graph database adapter for queries |
| `embed_fn` | callable | Embedding function for cosine similarity |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `gaps_found` | list[dict] | List of gap descriptors with type, node IDs, context, and whether a task was created |
| `tasks_created` | int | Count of new tasks created in this scan |
| `tasks_refreshed` | int | Count of existing tasks whose energy was refreshed |

**Side Effects:**

- Creates Narrative(type='task') nodes in the graph via `create_task()`
- Refreshes energy on existing gap tasks that persist

### Hook Function: `on_query_result()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query_text` | str | The original query string |
| `actor_id` | str | Who asked |
| `results` | list | The search results (clusters or nodes) |
| `resonance_threshold` | float | Below this, results are considered non-resonant (default: 0.3) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `gap_created` | bool | Whether a gap marker was created or an existing one was energized |

**Side Effects:**

- Creates or energizes gap marker nodes in the graph

---

## EDGE CASES

### E1: Moment With Only Weak Links

```
GIVEN:  A Moment has Actor links but all with weight < 0.1 (barely connected)
THEN:   The gap detector does NOT flag this as missing — a link exists. Link quality is not this module's concern.
```

### E2: All Nodes Are Potential Duplicates Of Each Other

```
GIVEN:  A citizen with many Actor nodes about similar people (e.g., all "software engineers")
THEN:   Only pairs above the 0.85 cosine threshold are flagged. If this produces too many candidates, the citizen resolves the most energetic ones first and the rest decay via L7.
```

### E3: Empty Query On Brand New Graph

```
GIVEN:  A newly seeded brain graph with < 10 nodes
THEN:   Empty queries are expected — the graph is young. Gap markers should still be created but with low initial energy (0.2 instead of 0.5) to avoid flooding a new citizen with acquisition tasks.
```

### E4: Thing Link Detection Requires Content Analysis

```
GIVEN:  A Moment's content mentions "the document" or "the API key"
WHEN:   Detecting whether a Thing link is missing requires understanding the content
THEN:   Use simple heuristics (entity-like noun phrases in content) rather than LLM analysis. False negatives are acceptable — better to miss some than to invoke an LLM on every moment.
```

---

## ANTI-BEHAVIORS

### A1: Gap Detector Writes Links

```
GIVEN:   A missing Actor link is detected on a Moment
WHEN:    The detector runs
MUST NOT: Create the link itself or guess which Actor to connect
INSTEAD:  Create a task asking the citizen to create the link
```

### A2: Duplicate Detector Merges Nodes

```
GIVEN:   Two Actors with 0.92 cosine similarity
WHEN:    The detector runs
MUST NOT: Merge the nodes, transfer weights, or rewire links
INSTEAD:  Create a task with both nodes' context asking "Are these the same?"
```

### A3: Every Failed Query Creates A Gap

```
GIVEN:   A query like "asdfghjkl" returns zero results
WHEN:    The on_query_result hook fires
MUST NOT: Create a gap marker for gibberish or overly generic queries
INSTEAD:  Apply minimum query quality checks: length > 3 words, not all stop words, embedding norm within expected range
```

### A4: Gap Tasks Accumulate Without Bound

```
GIVEN:   Gap detection has been running for months
WHEN:    Thousands of gap tasks exist
MUST NOT: Let gap tasks persist forever, consuming graph space
INSTEAD:  Rely on L7 forgetting. Gap tasks are normal Narrative nodes — if nobody resolves them and no energy flows in, they decay and get pruned. The detector does not need its own cleanup.
```

---

## MARKERS

<!-- @mind:todo Define exact heuristic for "content mentions objects" in Thing link detection (E4) -->
<!-- @mind:escalation Should empty query gap detection be opt-in per citizen, or always-on? If a citizen never uses graph_query, they'll never generate empty query gaps. Is that a problem? -->
