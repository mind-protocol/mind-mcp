# Subcall — Validation: What Must Be True

```
STATUS: STABLE
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
PATTERNS:        ./PATTERNS_Subcall.md
BEHAVIORS:       ./BEHAVIORS_Subcall.md
THIS:            VALIDATION_Subcall.md (you are here)
ALGORITHM:       ./ALGORITHM_Subcall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Subcall.md
HEALTH:          ./HEALTH_Subcall.md
SYNC:            ./SYNC_Subcall.md
```

---

## PURPOSE

These invariants define what properties, if violated, would mean subcall has failed its purpose as zero-LLM telepathy. They protect the defining constraints: no LLM on the target, physics-driven routing, actionable intelligence output, and economic anchoring via persistent moments.

---

## INVARIANTS

### V1: Zero LLM Tokens on Target Side

**Why we care:** The entire economic and architectural premise of subcall is that probing another citizen's knowledge costs one embedding + graph queries, not an LLM invocation. If this invariant breaks, subcall becomes a slow, expensive duplicate of `/call`.

```
MUST:   All target-side processing uses only graph queries (Cypher) and vector similarity (KNN)
MUST:   Every response footer reports "Cost: 0 LLM tokens"
NEVER:  Invoke an LLM, language model, or token-generating service to produce target-side responses
NEVER:  Import or call any LLM client (OpenAI, Anthropic, Ollama, etc.) within subcall_handler.py
```

### V2: Formula Morphs Without Conditional Branches

**Why we care:** If scenario handling uses if/then branches, adding scenarios becomes a code change. The thermodynamic design requires that all 24 scenarios flow through the same formula, differing only in drive values. Conditional routing would fragment the physics into 24 separate algorithms.

```
MUST:   All 24 scenarios exist as entries in SCENARIO_PROFILES dict (limbic drive values only)
MUST:   score_citizens() reads drives from the limbic_state dict, not from scenario names
NEVER:  Add if/elif/else blocks that check scenario name to change routing behavior
NEVER:  Create scenario-specific code paths in target selection or resonance scoring
```

### V3: Subcall Moments Are Persisted with Full Topology

**Why we care:** The moment node is the economic anchor for the vertical membrane. Without it, $MIND cannot flow from consumer to creator. Without CREATED/CONTRIBUTED links, the settlement system cannot trace who asked and who answered.

```
MUST:   Every single-target subcall creates a Moment node (type="subcall", status="completed")
MUST:   Moment has CREATED link from caller and CONTRIBUTED links from each responder
MUST:   Moment carries: direction, creating_drive, trigger, intention, resonance_count, origin_citizen
MUST:   Moment's settlement_status is set to "tracking"
NEVER:  Skip moment creation to save latency — the graph mutation is the settlement anchor
```

### V4: Auto-Selection Produces Diverse Results

**Why we care:** If auto-select returns the top 5 by score, it will return citizens who are similar to each other (same knowledge cluster). This creates an echo chamber. The diverse selection algorithm must actively maximize viewpoint spread.

```
MUST:   Auto-select mode (no target) always applies select_diverse() with method="diverse"
MUST:   Selection uses farthest-point greedy algorithm, not simple top-N ranking
MUST:   The top-1 scorer is always included (strongest signal guaranteed)
NEVER:  Return only the top-N citizens by raw score in auto-select mode
```

### V5: Single-Target Returns Three Output Layers

**Why we care:** A single briefing layer is insufficient for different consumption contexts. The telemetry layer is for quick scanning, the structured layer is for detailed reading, and the inner voice layer is for WM injection. Missing any layer degrades the intelligence product.

```
MUST:   Single @handle target response contains:
          Layer 1: Telemetry briefing (header + because + recommendation + graph extraction)
          Layer 2: Structured resonance (method, node list, responder profile)
          Layer 3: Inner voice (first-person whisper for WM injection)
MUST:   Layers are separated by "---" markdown dividers
NEVER:  Return only raw node data without the telemetry narrative for single-target calls
```

### V6: Stimulus Cluster Carries Caller Context

**Why we care:** A bare query like "how do I fix that" has no semantic gravity. Without the caller's context nodes (active working memory, current moment, self reference), the target's graph cannot resonate meaningfully. Quality of resonance depends directly on stimulus cluster richness.

```
MUST:   Stimulus cluster includes at minimum: self actor node + query text node
MUST:   If graph_ops is available, cluster includes activated nodes from caller's brain
MUST:   All cluster segments carry origin_citizen and origin_date provenance stamps
NEVER:  Send a bare query string without wrapping it in a cluster
```

### V7: Graph Operations Are Restored After Universe Switch

**Why we care:** When a subcall specifies a different universe, a new GraphOps instance is created for that universe. If the original graph_ops is not restored after the call, all subsequent MCP tools would operate on the wrong graph.

```
MUST:   ctx.graph_ops is saved before universe switch and restored in finally block
MUST:   Universe-specific GraphOps is used only within the try block
NEVER:  Leave ctx.graph_ops pointing to a non-default graph after handle_subcall() returns
```

### V8: Keyword Fallback Activates When Vector Search Fails

**Why we care:** If the embedding service is down or the graph lacks vector indexes, subcall must still function. Returning "no resonance" when the citizen actually has relevant keyword-matching content would be a false negative that breaks trust in the tool.

```
MUST:   If vector similarity search returns empty results, attempt keyword text matching
MUST:   Keyword search uses top 5 words (>3 chars) from query against content + synthesis fields
NEVER:  Return "no resonance" without attempting keyword fallback when vector search yields nothing
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
| V1 | Zero-LLM economics | CRITICAL |
| V2 | Physics-driven routing (no conditional branches) | CRITICAL |
| V3 | Economic settlement anchor (moments + links) | HIGH |
| V4 | Anti-echo-chamber (diverse selection) | HIGH |
| V5 | Intelligence product completeness (3 layers) | HIGH |
| V6 | Stimulus quality (caller context in cluster) | MEDIUM |
| V7 | Graph operations safety (universe restore) | CRITICAL |
| V8 | Graceful degradation (keyword fallback) | MEDIUM |
