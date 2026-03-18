# Gap Detection — Algorithm: Scan Patterns and Task Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
BEHAVIORS:       ./BEHAVIORS_Gap_Detection.md
PATTERNS:        ./PATTERNS_Gap_Detection.md
THIS:            ALGORITHM_Gap_Detection.md (you are here)
VALIDATION:      ./VALIDATION_Gap_Detection.md
HEALTH:          ./HEALTH_Gap_Detection.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gap_Detection.md
SYNC:            ./SYNC_Gap_Detection.md

IMPL:            runtime/cognition/gap_detector.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The gap detector performs three independent scan passes over the graph and one hook-based capture. Each pass identifies a class of structural incompleteness, packages context, checks for existing tasks, and creates new tasks via `create_task()`. The scans are designed to run periodically (every N physics ticks) or on-demand, and to complete within a bounded time (never stalling the tick loop).

The three passes are:
1. **Missing link scan** — Moments without required link types
2. **Duplicate candidate scan** — Nodes with high embedding similarity
3. **Empty query gap capture** — Hook on `graph_query` return path

Each pass is independent: they share no state and can run in any order or in parallel.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Structural completeness | B1, B4 | Traverses all Moments and detects missing Actor/Space/Thing links, creates tasks with enough context to resolve |
| Identity resolution | B2, B4 | Compares embedding vectors pairwise within node types, surfaces high-similarity pairs as merge candidates |
| Knowledge acquisition | B3, B4 | Captures failed queries as gap markers, accumulates energy on repeated failures |

---

## DATA STRUCTURES

### GapDescriptor

```
GapDescriptor:
    gap_type: str           # 'missing_actor_link' | 'missing_space_link' | 'missing_thing_link' | 'potential_duplicate' | 'empty_query'
    source_node_id: str     # The node where the gap was found (Moment ID for missing links, first node for duplicates)
    target_node_id: str?    # Second node for duplicates, null for missing links
    context: str            # Rich text context for the task synthesis
    task_id: str            # Deterministic task ID (for dedup checking)
    energy: float           # Initial task energy
    actor_id: str           # The citizen this gap belongs to
```

### Task ID Convention

Task IDs for gap detection are deterministic and based on the gap itself, ensuring the same gap always produces the same task ID:

```
Missing link:    "gap:{actor_id}:missing_{link_type}:{moment_id}"
Duplicate:       "gap:{actor_id}:dup_{node_type}:{sorted_id_pair_hash}"
Empty query:     "gap:{actor_id}:query:{query_embedding_hash[:12]}"
```

This deterministic ID is the mechanism for B4 (no duplicate tasks). Before creating a task, check if a task with this ID already exists.

---

## ALGORITHM: scan_gaps()

### Step 1: Missing Link Scan

Traverse all Moment nodes in the citizen's L1 brain graph. For each Moment, check whether required link types exist.

```
FOR each Moment node M in citizen's brain:
    actor_links = MATCH (M)-[:LINK]-(a) WHERE a is Actor
    space_links = MATCH (M)-[:LINK]-(s) WHERE s is Space
    thing_links = MATCH (M)-[:LINK]-(t) WHERE t is Thing

    IF actor_links is empty:
        gap = GapDescriptor(
            gap_type = 'missing_actor_link',
            source_node_id = M.id,
            context = f"Moment: {M.content[:300]}\nExisting links: {describe_links(M)}\nQuestion: Who was involved in this?",
            task_id = f"gap:{actor_id}:missing_actor:{M.id}",
            energy = 0.5
        )
        IF NOT task_exists(gap.task_id):
            create_task(gap)
        ELSE:
            refresh_energy(gap.task_id)

    IF space_links is empty:
        gap = GapDescriptor(
            gap_type = 'missing_space_link',
            source_node_id = M.id,
            context = f"Moment: {M.content[:300]}\nExisting links: {describe_links(M)}\nQuestion: Where did this happen?",
            task_id = f"gap:{actor_id}:missing_space:{M.id}",
            energy = 0.4
        )
        IF NOT task_exists(gap.task_id):
            create_task(gap)
        ELSE:
            refresh_energy(gap.task_id)

    IF thing_links is empty AND content_mentions_objects(M.content):
        gap = GapDescriptor(
            gap_type = 'missing_thing_link',
            source_node_id = M.id,
            context = f"Moment: {M.content[:300]}\nExisting links: {describe_links(M)}\nQuestion: What was used or discussed?",
            task_id = f"gap:{actor_id}:missing_thing:{M.id}",
            energy = 0.3
        )
        IF NOT task_exists(gap.task_id):
            create_task(gap)
        ELSE:
            refresh_energy(gap.task_id)
```

**Why these energy values:** Missing Actor links get the highest energy (0.5) because "who" is the most critical missing context. Space gets 0.4 because location matters but is often implicit. Thing gets 0.3 because Thing links are the most optional and the detection is heuristic-based.

### Step 2: Duplicate Candidate Scan

Compare embedding vectors within each scanned node type. Use batch cosine similarity to avoid O(n^2) full comparison when possible.

```
COSINE_THRESHOLD = 0.85
MAX_CANDIDATES_PER_SCAN = 50

FOR each node_type in [Actor, Space]:
    nodes = MATCH (n)-[:LINK]-(citizen_actor) WHERE n is {node_type} AND n.embedding IS NOT NULL

    # Sort by embedding norm to enable early termination in some cases
    # But fundamentally this is pairwise comparison within a type

    FOR each pair (A, B) in nodes WHERE A.id < B.id:
        sim = cosine_similarity(A.embedding, B.embedding)

        IF sim >= COSINE_THRESHOLD:
            pair_hash = sha256(sorted([A.id, B.id]))[:12]
            task_id = f"gap:{actor_id}:dup_{node_type}:{pair_hash}"

            IF NOT task_exists(task_id):
                context = build_duplicate_context(A, B, sim)
                # context includes: both names, both content snippets,
                # link counts for each, platform handles if Actor,
                # similarity score, and the question

                gap = GapDescriptor(
                    gap_type = f'potential_duplicate_{node_type}',
                    source_node_id = A.id,
                    target_node_id = B.id,
                    context = context,
                    task_id = task_id,
                    energy = 0.4 + (sim - 0.85) * 3.0  # higher similarity = higher urgency
                )
                create_task(gap)

                candidates_found += 1
                IF candidates_found >= MAX_CANDIDATES_PER_SCAN:
                    BREAK  # prevent flooding
```

**Why the energy formula:** `0.4 + (sim - 0.85) * 3.0` maps similarity [0.85, 1.0] to energy [0.4, 0.85]. Near-duplicates (0.99 cosine) get high urgency. Borderline cases (0.85) get moderate urgency.

**Why MAX_CANDIDATES_PER_SCAN:** A graph with many similar nodes (e.g., 50 software engineers) would produce O(n^2) pairs. Capping at 50 per scan keeps the task queue manageable. The highest-similarity pairs are found first because of the energy formula, and lower-priority ones will be caught in subsequent scans.

### Step 3: Empty Query Gap Capture

This is not part of `scan_gaps()` but a hook function called from the search system.

```
FUNCTION on_query_result(query_text, actor_id, results, resonance_threshold=0.3):

    # Filter: skip garbage queries
    IF len(query_text.split()) < 3:
        RETURN false
    IF query_text is all stop words:
        RETURN false

    # Check if results are empty or all below threshold
    max_resonance = max(result.energy for result in results) IF results ELSE 0.0

    IF max_resonance < resonance_threshold:
        query_hash = sha256(embed(query_text))[:12]
        marker_id = f"gap:{actor_id}:query:{query_hash}"

        IF gap_marker_exists(marker_id):
            # Increment energy logarithmically: each repeat adds less
            existing_energy = get_energy(marker_id)
            increment = 0.3 / (1 + log2(existing_energy / 0.3))
            set_energy(marker_id, existing_energy + increment)
            RETURN true
        ELSE:
            # Determine initial energy based on graph maturity
            node_count = count_brain_nodes(actor_id)
            initial_energy = 0.2 IF node_count < 20 ELSE 0.5

            create_gap_marker(
                id = marker_id,
                content = f"The graph has no knowledge about: {query_text}",
                synthesis = f"Knowledge gap: '{query_text}' — query returned no resonant results. The graph needs content about this topic.",
                actor_id = actor_id,
                energy = initial_energy
            )
            RETURN true

    RETURN false
```

**Why logarithmic increment:** The first few failed queries on a topic should escalate quickly (this is genuinely missing). But the 20th failed query shouldn't be 20x as urgent as the first. Logarithmic increment reflects diminishing marginal urgency.

**Why lower initial energy for small graphs:** A brain with < 20 nodes will fail on almost everything. Flooding it with gap markers is noise, not signal. Low initial energy means the markers exist but don't dominate the task queue.

---

## KEY DECISIONS

### D1: When to Create Thing-Link Gap Tasks

```
IF Moment.content mentions concrete objects (detected by heuristic):
    Create gap task with low energy (0.3)
    Heuristic: content contains noun phrases matching common Thing patterns
    (tools, documents, currencies, artifacts, APIs, files)
ELSE:
    Skip Thing-link gap detection for this Moment
    Not every Moment involves a Thing
```

### D2: Pairwise vs. Approximate Nearest Neighbor for Duplicates

```
IF node_count < 500:
    Use brute-force pairwise comparison (O(n^2) but n is small)
    Exact results, no false negatives
ELSE:
    Use approximate nearest neighbor search if available (HNSW/FAISS)
    Accept potential false negatives for performance
    Fall back to brute-force with random sampling if ANN not available
```

### D3: Task Routing

```
Gap tasks are routed by the existing task physics system.
The citizen who owns the brain graph is the primary candidate.
Task routing uses embedding similarity between task.synthesis and citizen.synthesis.
Gap tasks carry category='gap_detection' for filtering in task list.
```

### D4: Scan Frequency

```
IF triggered by tick loop:
    Run every GAP_SCAN_INTERVAL ticks (configurable, default 100)
    This avoids running on every tick while ensuring gaps are caught
IF triggered on-demand:
    Run immediately (citizen or operator requests a scan)
    No frequency throttling for manual scans
```

---

## DATA FLOW

```
L1 Brain Graph (Moments, Actors, Spaces, Things)
    |
    v
scan_gaps(actor_id, adapter, embed_fn)
    |
    +---> Missing Link Scan
    |         |
    |         v
    |     [GapDescriptors]
    |         |
    +---> Duplicate Candidate Scan
    |         |
    |         v
    |     [GapDescriptors]
    |
    +---> (independently)
    |
    v
For each GapDescriptor:
    task_exists(gap.task_id)?
        YES --> refresh_energy(existing_task)
        NO  --> create_task(gap) via task_physics.create_task()
    |
    v
Tasks enter task physics system
    |
    +---> Urgency accumulation (tick loop)
    +---> Citizen routing (embedding similarity)
    +---> Completion cascade (citizen resolves)
    +---> L7 forgetting (unresolved tasks decay)


graph_query() return path
    |
    v
on_query_result(query_text, actor_id, results)
    |
    v
Results empty or below threshold?
    NO  --> return (no gap)
    YES --> Query quality check passes?
        NO  --> return (garbage query)
        YES --> Gap marker exists for this topic?
            YES --> increment energy (logarithmic)
            NO  --> create gap marker node
```

---

## COMPLEXITY

**Time:** O(M + A^2 + S^2) per scan — where M = number of Moments, A = number of Actor nodes, S = number of Space nodes. The missing link scan is linear in Moments. The duplicate scan is quadratic in nodes per type but capped by MAX_CANDIDATES_PER_SCAN.

**Space:** O(M + A + S) — gap descriptors are created and passed to `create_task()`, not accumulated. The working set is proportional to the number of gaps found, which is bounded by graph size.

**Bottlenecks:**
- Duplicate scan on large graphs: a citizen with 1000 Actor nodes would require 500K pairwise comparisons. The ANN fallback (D2) mitigates this.
- Missing link scan on graphs with many unlinked Moments: linear but potentially thousands of Moments. Batch Cypher queries help.
- Embedding computation: if nodes lack embeddings, the duplicate scan skips them. No on-the-fly embedding generation in the scan.

---

## HELPER FUNCTIONS

### `content_mentions_objects(content: str) -> bool`

**Purpose:** Heuristic to detect whether a Moment's content references concrete objects (tools, documents, artifacts, APIs, etc.) that should be linked as Thing nodes.

**Logic:** Pattern matching against common Thing-indicating noun phrases. Not LLM-based. Uses a small vocabulary of object-indicating patterns: file names, URLs, tool names, currency amounts, document types. Returns true if any pattern matches. False negatives are acceptable; false positives produce low-energy tasks that decay.

### `build_duplicate_context(node_a, node_b, similarity: float) -> str`

**Purpose:** Assemble rich comparison context for a duplicate candidate task so the citizen can decide without re-querying.

**Logic:** Extracts from both nodes: name, content (first 200 chars), link count, platform handles (if Actor), space hints (if Space). Formats as a side-by-side comparison with the similarity score. Ends with the question: "Are these the same {type}? If yes, merge. If no, dismiss."

### `task_exists(task_id: str) -> bool`

**Purpose:** Check whether a gap task with this ID already exists and is not completed.

**Logic:** `MATCH (t:Narrative {id: $task_id, type: 'task'}) WHERE t.status <> 'completed' RETURN count(t) > 0`

### `refresh_energy(task_id: str) -> None`

**Purpose:** Bump energy on an existing gap task to prevent L7 decay when the gap persists across scans.

**Logic:** `MATCH (t:Narrative {id: $task_id}) SET t.energy = max(t.energy, $min_energy)` where `min_energy` is the gap type's base energy. This prevents a persistent gap from decaying away just because nobody has resolved it yet.

### `describe_links(moment_node) -> str`

**Purpose:** Human-readable summary of a Moment's existing links for task context.

**Logic:** Queries all links from the Moment, groups by target type (Actor, Space, Thing, other), and formats as "Actors: [name1, name2], Spaces: [name3], Things: none". This tells the citizen what's already connected so they know what's missing.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/organization/task_physics.py` | `create_task(task_id, synthesis, adapter, ...)` | True/False (task created) |
| `runtime/physics/graph/graph_queries.py` | Cypher queries for Moments, links, nodes | Result sets |
| `runtime/infrastructure/embeddings/` | `cosine_similarity(vec_a, vec_b)` | float [0, 1] |
| `runtime/physics/graph/graph_queries_search.py` | Hook: `on_query_result()` called from search return path | (we are the callee) |

---

## MARKERS

<!-- @mind:todo Design the exact Cypher queries for batch missing-link detection (Step 1). Single query per link type is more efficient than per-Moment queries. -->
<!-- @mind:proposition For duplicate detection, consider using the graph's existing embedding index (FalkorDB vector search) instead of brute-force pairwise. This would make the scan O(n * k) instead of O(n^2). -->
<!-- @mind:escalation The Thing-link heuristic (content_mentions_objects) needs design. What patterns count? Should this be a configurable vocabulary or hardcoded? -->
