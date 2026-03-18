# Stimulus Router — Algorithm: Event-to-Stimulus Pipeline

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
BEHAVIORS:       ./BEHAVIORS_Stimulus_Router.md
PATTERNS:        ./PATTERNS_Stimulus_Router.md
THIS:            ALGORITHM_Stimulus_Router.md (you are here)
VALIDATION:      ./VALIDATION_Stimulus_Router.md
HEALTH:          ./HEALTH_Stimulus_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stimulus_Router.md
SYNC:            ./SYNC_Stimulus_Router.md

IMPL:            runtime/cognition/stimulus_router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The stimulus router converts raw `IncomingEvent` objects into `Stimulus` objects that the L1 cognitive engine can process via Law 1 energy injection. The pipeline is a linear filter chain: each stage can either reject the event (returning None) or pass it forward with computed values. The pipeline is synchronous, performs no I/O, and completes in microseconds.

A parallel subsystem, the feedback injector, closes the perception-action loop by converting LLM output back into self-stimulus events that re-enter the router.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Faithful signal transduction | B1, B5, B6, B7 | External events are classified, energy-budgeted, and concept-extracted |
| O2: Anti-loop integrity | B2, B3 | Three-layer anti-loop gate prevents self-stimulus runaway |
| O3: Source-aware energy | B5, B6 | Classification stage sets energy based on source and flags |
| O4: Dedup fidelity | B4 | Hash-based dedup rejects duplicates within sliding window |

---

## DATA STRUCTURES

### IncomingEvent

```
Raw event from any source. Immutable input to the router.

Fields:
  content: str              # The event text
  source: str               # "telegram", "whatsapp", "discord", "mcp", "system", "self"
  citizen_handle: str       # Which citizen this event targets
  is_social: bool           # Explicit social flag (default False)
  is_failure: bool          # Event represents a failure/error
  is_progress: bool         # Event represents progress/success
  metadata: dict            # Source-specific metadata (default {})
  timestamp: float          # Unix timestamp (default time.time())
```

### AntiLoopGate

```
Per-citizen gate that prevents self-stimulus feedback loops.
Mutable state that tracks recent self-stimuli.

Fields:
  refractory_seconds: float      # Minimum seconds after action before self-stimulus allowed (default 5.0)
  diminishing_half_life: int     # N self-stimuli for energy to halve (default 3)
  novelty_threshold: float       # Cosine sim threshold for duplicate rejection (default 0.85, currently unused)
  history_size: int              # Max recent hashes to track (default 20)
  _last_action_time: float       # Timestamp of last recorded action
  _self_stimulus_count: int      # Running count of self-stimuli since last external event
  _recent_hashes: list[str]      # MD5 hashes of recent self-stimulus content (8-char prefix)
```

### Stimulus (output)

```
Structured carrier for the L1 cognitive engine. Defined in tick_runner.

Fields:
  content: str                   # Event content text
  energy_budget: float           # Computed energy for injection (default 1.0)
  embedding: list[float]         # Embedding vector (empty until embed_fn available)
  target_node_ids: list[str]     # Node IDs for targeted injection (empty until node matching)
  is_social: bool                # Social stimulus flag
  is_failure: bool               # Failure stimulus flag
  is_novelty: bool               # Novel content flag
  is_progress: bool              # Progress stimulus flag
  source: str                    # Origin source string
  timestamp: float               # Event timestamp
  origin_citizen: str            # Actor ID of sender (v2.2 provenance)
  origin_citizen_name: str       # Display name of sender
  origin_citizen_image: str      # Sender's profile pic URI
  image_uri: str                 # Stimulus-specific image
  _concepts: list[str]           # (runtime attr) Extracted concept keywords for node targeting
```

---

## ALGORITHM: StimulusRouter.route()

### Step 1: Anti-Loop Gate Check

The first gate checks whether the event is self-generated and whether it should be allowed through.

For external events (source != "self"):
- Always allowed (returns True, 1.0)
- Resets the self_stimulus_count to 0 (breaks the diminishing returns chain)

For self events (source == "self"):
- **Layer 1 — Refractory period:** If elapsed time since last action < refractory_seconds (5.0s), reject immediately.
- **Layer 2 — Diminishing returns:** Compute energy multiplier as `0.5 ^ (count / half_life)`. At count=0: 1.0, count=3: 0.5, count=6: 0.25. Increment count.
- **Layer 3 — Novelty gate:** Compute MD5 hash of content (8-char prefix). If hash exists in recent_hashes, reject. Otherwise append to history (evict oldest if > 20).

```
IF event.source != "self":
    reset self_stimulus_count to 0
    RETURN (allowed=True, energy_mult=1.0)

elapsed = now - last_action_time
IF elapsed < refractory_seconds:
    RETURN (allowed=False, energy_mult=0.0)

count += 1
energy_mult = 0.5 ^ (count / diminishing_half_life)

hash = MD5(content)[:8]
IF hash IN recent_hashes:
    RETURN (allowed=False, energy_mult=0.0)

recent_hashes.append(hash)
trim_to(history_size)
RETURN (allowed=True, energy_mult)
```

### Step 2: Content Dedup Check

Independent of anti-loop, the router maintains a separate dedup history for ALL events (not just self-stimuli). This catches the same content arriving through multiple bridges.

```
hash = MD5(content)[:12]
IF hash IN recent_stimulus_hashes:
    RETURN None

recent_stimulus_hashes.append(hash)
trim_to(dedup_window=50)
```

Note the different hash lengths: anti-loop uses 8-char prefix (coarser), dedup uses 12-char prefix (finer). This is intentional — anti-loop catches approximate self-repeats while dedup catches exact duplicates.

### Step 3: Classification

Classify the event for downstream processing. Two independent classifications:

**Social detection:**
```
is_social = event.is_social OR event.source IN ("telegram", "whatsapp", "discord")
```

**Novelty detection:**
```
is_novelty = (content_hash NOT IN recent_stimulus_hashes)
```

Since the hash was just added in Step 2 and was not already present (or we would have returned None), novelty is currently always True for events that pass dedup. This will change when embedding-based similarity is available.

### Step 4: Concept Extraction

Extract keyword concepts from content for node targeting. This is a bridge mechanism until per-citizen embedding functions are available.

```
Split content into sentences (by '. ' or '! ' or '? ' or '\n')
Take first 5 sentences
For each sentence:
    Split into words
    For each word:
        Strip punctuation
        IF len > 3 AND word NOT IN stop_words:
            Add to concepts list
Deduplicate preserving order
Return first 15 concepts
```

Stop words include common English and French words (the, and, for, dans, pour, avec, etc.).

### Step 5: Energy Budget Computation

Compute the energy budget based on source classification and anti-loop multiplier.

```
base_energy = 1.0
IF is_social:
    base_energy = 1.2
IF event.is_failure:
    base_energy = 0.8

energy = base_energy * energy_mult_from_antiloop
```

Note: if both is_social and is_failure are true, is_failure wins (base_energy is set to 0.8 because it's the later conditional). This is the current behavior — social failures get reduced energy.

### Step 6: Build Stimulus

Assemble the Stimulus object from computed values.

```
stimulus = Stimulus(
    content       = event.content,
    energy_budget = energy,
    embedding     = [],          # filled by embed_fn when available
    target_node_ids = [],        # filled by node matching
    is_social     = is_social,
    is_failure    = event.is_failure,
    is_novelty    = is_novelty,
    is_progress   = event.is_progress,
    source        = event.source,
    timestamp     = event.timestamp,
)
stimulus._concepts = concepts    # runtime attribute for node matching
```

---

## ALGORITHM: inject_post_action_feedback()

The feedback injector converts LLM output back into a self-stimulus. It performs three operations:

### Step 1: Record Action

Call `router.record_action()` to set the refractory timestamp. This prevents the self-stimulus from immediately re-entering the graph.

### Step 2: Create Episodic Memories

If the action output is >= 30 characters, extract memory-worthy segments:

```
For each line in output:
    IF line contains commit/deploy keywords: significance = 0.9
    ELIF line contains create/fix/implement keywords: significance = 0.8
    ELIF line contains error/failed/broken keywords: significance = 0.7
    ELIF line contains learned/discovered keywords: significance = 0.85
    ELSE: skip line

Create up to 3 memory nodes per session
Each memory node:
    weight = 0.35 * significance (heavier than Law 1 newborns at 0.05)
    stability = 0.3 (resists some forgetting)
    self_relevance = 0.6 (autobiographical)
    linked to top 3 WM nodes via REMINDS_OF links
```

### Step 3: Route Self-Stimulus

Truncate long outputs (>500 chars: first 250 + " [...] " + last 200) and create an IncomingEvent with source="self", is_failure=!success, is_progress=success. Route through the standard pipeline.

### Step 4: Update Limbic State

```
IF success:
    satisfaction += 0.1
    frustration -= 0.05
    achievement -= 0.03 (partial fulfillment)
IF failure:
    frustration += 0.15
    achievement += 0.05 (want to try harder)
IF response_time > 30s:
    anxiety += 0.05
```

---

## KEY DECISIONS

### D1: Separate Anti-Loop and Dedup

```
IF event is self-stimulus:
    Anti-loop gate checks refractory + diminishing + novelty (8-char hash)
    THEN dedup checks content hash (12-char hash)
    Why: Anti-loop is about preventing loops. Dedup is about preventing duplicates.
    These are orthogonal concerns with different hash granularities.
ELSE:
    Anti-loop passes immediately
    Dedup still checks content hash
    Why: External duplicates still need dedup even though anti-loop doesn't apply.
```

### D2: Social vs Failure Energy Priority

```
IF event.is_social AND event.is_failure:
    base_energy = 0.8 (failure wins)
    Why: A social failure (e.g., partner reports an error) should get reduced
         energy for attention, but the is_social flag is still set True, so
         limbic updates (ticks_since_social reset) still fire. The energy
         reduction is intentional — failures shouldn't dominate attention
         even when social.
```

### D3: Concept Extraction Over Embedding

```
Currently: keyword extraction (no LLM, no embedding model)
Future:    cosine similarity against node embeddings
Why: The router must remain zero-latency. Embedding generation requires an
     API call or a local model. The embed_fn parameter on StimulusRouter
     is the hook for this future upgrade. Meanwhile, keyword concepts
     provide coarse but immediate targeting.
```

---

## DATA FLOW

```
IncomingEvent (from bridge/MCP/system/feedback_injector)
    |
    v
AntiLoopGate.check()
    |-- rejected (source="self" + refractory/duplicate/diminished) --> None
    |-- allowed (external or novel self) + energy_multiplier
    v
Dedup check (MD5 content hash, 12-char, window=50)
    |-- duplicate --> None
    |-- unique
    v
Classify (is_social, is_novelty)
    v
extract_concepts() --> list[str] (max 15 keywords)
    v
Energy budget (base * energy_mult)
    v
Build Stimulus --> Stimulus object
    v
L1CognitiveTickRunner.run_tick(stimulus=...)
    |
    v
Law 1: inject_energy() --> distributes energy across graph nodes
```

---

## COMPLEXITY

**Time:** O(S + D) per route() call, where S is content length (for hashing and concept extraction) and D is dedup window size (for hash lookup). In practice, content is typically < 2000 chars and D=50, so this is effectively O(1).

**Space:** O(D + H) per citizen, where D is the dedup window (50 hashes) and H is the anti-loop history (20 hashes). Total ~70 string entries per citizen. Negligible.

**Bottlenecks:**
- The `extract_concepts()` function splits text and filters stop words. For very long texts this could be noticeable, but the function caps at 5 sentences and 15 concepts.
- MD5 computation is the most expensive operation per call. Still sub-microsecond for typical message lengths.

---

## HELPER FUNCTIONS

### `extract_concepts(text: str) -> list[str]`

**Purpose:** Extract keyword concepts from text for node targeting.

**Logic:** Split into sentences (max 5), tokenize, filter by length (>3 chars) and stop word list, deduplicate preserving order, cap at 15 concepts.

### `AntiLoopGate.record_action()`

**Purpose:** Record that the citizen took an action. Called by the feedback injector after LLM output.

**Logic:** Sets `_last_action_time = time.time()`. This starts the refractory period for subsequent self-stimuli.

### `AntiLoopGate.check(event) -> (bool, float)`

**Purpose:** Three-layer gate check for self-stimulus anti-loop protection.

**Logic:** External events pass immediately. Self events check refractory period, then compute diminishing returns, then check novelty hash.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `tick_runner_l1_cognitive_engine` | Import `Stimulus` class | Dataclass for building output |
| `feedback_injector` | `inject_post_action_feedback()` | Routes self-stimulus back through us |
| `dispatcher` | Creates `StimulusRouter(handle)`, calls `route(event)` | Gets `Optional[Stimulus]` for tick injection |
| `l1_stimulus_injector_for_partner_data` | (Parallel interface) | Produces `PartnerStimulus` objects that bypass this router |
