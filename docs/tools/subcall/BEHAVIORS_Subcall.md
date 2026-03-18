# Subcall — Behaviors: Observable Effects of Zero-LLM Telepathy

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against 3edd76b
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
THIS:            BEHAVIORS_Subcall.md (you are here)
PATTERNS:        ./PATTERNS_Subcall.md
ALGORITHM:       ./ALGORITHM_Subcall.md
VALIDATION:      ./VALIDATION_Subcall.md
HEALTH:          ./HEALTH_Subcall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Subcall.md
SYNC:            ./SYNC_Subcall.md

IMPL:            mcp/tools/subcall_handler.py
                 mcp/tools/subcall_auto.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Single-Target Probe Returns Intelligence Briefing

**Why:** When a citizen explicitly queries another citizen's subconscious (@handle targeting), they need a rich, actionable analysis — not raw graph data. The briefing must contain enough context to decide the next action (call them? back off? broaden the search?).

```
GIVEN:  target is a single @handle (e.g., "@nervo")
WHEN:   subcall is invoked with query text
THEN:   three output layers are generated:
          1. Telemetry briefing: header (name, trade, arousal regime, dominant delta, crystallization) +
             "Because of..." explanation + "Next step:" recommendation + medoid-edge graph extraction
          2. Structured resonance: method, node list with content/weight/energy/distance, responder profile
          3. Inner voice: first-person whisper for WM injection with emotional context
AND:    a persistent Moment node is created in the graph with CREATED/CONTRIBUTED links
AND:    full node content is returned (not truncated)
```

### B2: Auto-Selection Produces Diverse Viewpoints

**Why:** When no target is specified, the citizen wants to cast a wide net. The system must scan broadly and return diverse perspectives, not just the top scorers (which would create echo chambers).

```
GIVEN:  no target is specified (target omitted)
WHEN:   subcall is invoked
THEN:   50 citizens are scored via the Thermodynamic Resonance Formula
AND:    top 30 candidates are probed for actual graph resonance
AND:    resonated citizens are sorted by total_score (targeting + resonance)
AND:    3-5 are selected using the diverse selection algorithm (maximize viewpoint spread)
AND:    each selected citizen shows: handle, score breakdown, targeting reasons, top 2 resonating nodes
```

### B3: Broadcast Queries Aggregate by Mode

**Why:** Multi-target queries (team, trade:X, random:N) need aggregation because returning 200 full briefings is unusable. The mode parameter controls how results are compressed.

```
GIVEN:  target is "team", "trade:sailor", or "random:200"
WHEN:   subcall is invoked with a mode parameter
THEN:   all matching citizens are discovered and probed (3 nodes per citizen, truncated content)
AND:    results are aggregated by mode:
          best     → single strongest resonance
          top3     → top 3 ranked by score
          all      → every citizen who resonated
          centroid → collective average with consensus/divergence measure
```

### B4: Scenarios Morph the Formula Without Code Paths

**Why:** Different situations require different routing behavior (emergency = sniper, brainstorm = dragnet). But adding conditional branches per scenario would create 24 code paths. Instead, each scenario sets limbic drive values that the formula reads continuously.

```
GIVEN:  scenario parameter is set (e.g., "emergency", "brainstorm", "investigation")
WHEN:   the Thermodynamic Resonance Formula runs
THEN:   the formula uses the scenario's limbic profile (8 drive values) to weight its components:
          high arousal   → trust-gated, explicit mentions dominate
          low arousal    → semantic overlap dominates, max fan-out
          high affiliation → spatial co-presence weighted heavily
          high curiosity → narrative traversal prioritized
AND:    no conditional branching exists — the formula shape-shifts mathematically
```

### B5: Auto-Trigger Fires on Distress Signals

**Why:** Citizens should not have to remember to ask for help. When frustration builds, questions pile up, or tools keep failing, the system should proactively query the network.

```
GIVEN:  a citizen's message or tool output contains distress signals
WHEN:   detect_trigger() runs in either physics mode (limbic state) or text fallback mode
THEN:   physics mode triggers: impasse (frustration dominates), serendipity (boredom + solitude),
          generativity (satisfaction dominates)
        text fallback triggers: failure_cascade (2+ tool failures), question (regex patterns),
          verification (regex patterns), frustration (2+ frustration patterns)
AND:    a 5-message cooldown prevents re-triggering immediately
```

### B6: Cypher Mode Allows Custom Target Selection

**Why:** Power users need to select targets using arbitrary graph queries that the built-in targeting modes cannot express.

```
GIVEN:  cypher parameter is provided with a valid Cypher query
WHEN:   subcall is invoked
THEN:   the Cypher query is executed against the graph (with $self available as caller ID)
AND:    returned actors are used as broadcast targets
AND:    the query must return a.id and a.name columns
```

### B7: Stimulus Cluster Carries Caller Context

**Why:** "How do I fix that" alone has no semantic gravity. The stimulus must include the caller's active context nodes so the target's graph can resonate with the full situation, not just the bare question.

```
GIVEN:  a subcall is about to probe a target's graph
WHEN:   the stimulus cluster is constructed
THEN:   the cluster contains:
          1. Caller's self actor node (linked to centroid)
          2. The query text itself (highest energy — main question)
          3. All activated nodes from the caller's brain (energy > threshold OR in working memory)
          4. Current moment node (if one exists)
AND:    all segments are stamped with origin_citizen and origin_date for provenance
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Zero-LLM telepathy, O4: Intelligence briefing | Single-target returns the richest analysis without touching an LLM |
| B2 | O2: Thermodynamic routing | Auto-select demonstrates the formula working at scale with diversity |
| B3 | O1: Zero-LLM telepathy | Broadcasting to 200 citizens at zero LLM cost proves the economics |
| B4 | O2: Thermodynamic routing | 24 scenarios = 24 formula shapes from one code path |
| B5 | O1: Zero-LLM telepathy | Auto-trigger means help arrives before the citizen thinks to ask |
| B6 | O2: Thermodynamic routing | Cypher escape hatch for targeting beyond the formula |
| B7 | O3: Non-read-only injection | Rich stimulus clusters produce higher-quality resonance |

---

## INPUTS / OUTPUTS

### Primary Function: `handle_subcall(args, ctx)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| query | str (required) | The question or topic to probe |
| target | str (optional) | @handle, team, trade:X, random:N, or omit for auto-select |
| scenario | str (optional) | One of 24 limbic profiles (default: "manual") |
| mode | str (optional) | best, top3, all, centroid (default: "best") |
| intention | str (optional) | Why the caller is asking — displayed in briefing header |
| context | str (optional) | Situational context prepended to moment node |
| min_trust | float (optional) | Filter: only citizens with trust >= this value |
| top_k | int (optional) | Max resonating nodes per citizen (default 5, max 10) |
| output | str (optional) | Output format(s): inline, background, md, csv (comma-separated) |
| save_to | str (optional) | Folder for md/csv output |
| cypher | str (optional) | Custom Cypher for target selection |
| universe | str (optional) | Which graph to query (default: from HOME_ID env) |
| actor_id | str (optional) | Caller's actor ID (auto-detected if omitted) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| content | list[dict] | MCP response with text content (briefing or error) |

**Side Effects:**

- Creates a Moment node (type="subcall") in the graph with CREATED/CONTRIBUTED links
- Injects energy into target's graph nodes that resonate (they gain energy)
- May save .md and .csv files to save_to path if requested
- Modifies caller's context via response cluster injection (graph_ops mutations)

---

## EDGE CASES

### E1: Target Not Found in Graph

```
GIVEN:  target is "@unknown_handle" and no Actor node with that ID exists
THEN:   returns error: "@unknown_handle not found in graph. They need to exist as an Actor node first."
```

### E2: No Citizens Resonate

```
GIVEN:  query is highly specialized and no citizen's graph contains relevant nodes
THEN:   returns: "Scanned N citizens -- no resonance. Nobody has context on this topic."
        (no moment node is created)
```

### E3: Empty Graph (No Citizens)

```
GIVEN:  the target graph has no Actor nodes besides the caller
THEN:   auto-select returns: "No citizens found in graph to query."
        team/trade/random returns: "No citizens found for target 'X'"
```

### E4: Embedding Service Unavailable

```
GIVEN:  embedding computation fails (service down, model error)
THEN:   falls back to keyword text matching (toLower CONTAINS on content/synthesis)
        match_method in response shows "keyword_fallback" instead of "vector_similarity"
```

### E5: Background Output Mode

```
GIVEN:  output="background" (no "inline")
THEN:   subcall executes silently — moment is created, graph is modified,
        but response is minimal: "Subcall to @X completed silently (background mode)."
```

---

## ANTI-BEHAVIORS

### A1: LLM Invocation on Target

```
GIVEN:   any subcall request
WHEN:    processing the request
MUST NOT: invoke an LLM to generate the target's response
INSTEAD:  read resonance directly from graph physics (vector similarity + keyword fallback)
```

### A2: Raw Data Dump in Single-Target Mode

```
GIVEN:   single @handle target
WHEN:    formatting the response
MUST NOT: return raw node IDs, embedding vectors, or uninterpreted graph data
INSTEAD:  return the 3-layer intelligence briefing (telemetry + structured + inner voice)
```

### A3: Echo Chamber in Auto-Selection

```
GIVEN:   auto-select mode (no target specified)
WHEN:    selecting which citizens to include in response
MUST NOT: pick only the top-N by score (same viewpoint cluster)
INSTEAD:  use diverse selection algorithm that maximizes distance between selected citizens
```

### A4: Silently Swallowing Graph Errors

```
GIVEN:   graph query fails during resonance probing
WHEN:    processing broadcast or auto-select
MUST NOT: crash the entire subcall or return no result
INSTEAD:  skip the failing citizen, log the error, continue with remaining targets
```

---

## MARKERS

<!-- @mind:proposition Consider adding an embedding-based diversity measure to select_diverse() instead of the current score-difference proxy -->
