# ALGORITHM -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Status:** DESIGNING (v0.1)

---

## 1. Stimulus Injection Pipeline

### 1.1 Stimulus Sources and Entry Points

Every citizen interaction produces stimuli. The injection pipeline translates raw events into Law 1 energy injections.

```
                ┌─────────────────┐
                │ Message Queue   │ ← Telegram, WhatsApp, DM, Chat
                │ (message_queue) │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ Claude Invoker  │ ← Tool results, stdout
                │ (post-session)  │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ Stimulus Router │ ← Classifies, segments, embeds
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ L1 Law 1        │ ← Dual-channel injection
                │ (per citizen)   │
                └─────────────────┘
```

### 1.2 Stimulus Router Algorithm

The Stimulus Router sits between raw events and Law 1. It performs pre-processing (Step 0 in the ALGORITHM spec).

```python
def route_stimulus(citizen_handle: str, event: dict) -> list[Stimulus]:
    """
    Convert a raw event into L1-ready stimuli.

    Args:
        citizen_handle: Target citizen
        event: Raw event dict with keys:
            - source: "telegram" | "whatsapp" | "tool" | "membrane" | "alarm" | "self"
            - content: str (raw text or structured data)
            - sender: str (who sent it)
            - metadata: dict (platform-specific fields)

    Returns:
        List of Stimulus objects ready for Law 1 injection
    """
    source = event["source"]
    content = event["content"]

    # 1. CLASSIFY — determine energy budget and modality
    budget = STIMULUS_BUDGETS[source]  # from constants
    modality = MODALITY_MAP[source]     # text, audio, visual, etc.

    # 2. SEGMENT — decompose into atomic concepts
    #    Complex stimuli split into meaningful chunks
    if len(content) > BULK_THRESHOLD:
        segments = chunk_and_sample(content, citizen_handle)
    else:
        segments = extract_concepts(content)
        # extract_concepts uses NLP entity extraction or
        # simple keyword/sentence segmentation

    # 3. EMBED — batch embedding call for all segments
    texts = [seg.synthesis for seg in segments]
    embeddings = embedding_adapter.embed_batch(texts)
    for seg, emb in zip(segments, embeddings):
        seg.embedding = emb

    # 4. DEDUP — check against existing nodes in citizen's graph
    graph = get_citizen_graph(citizen_handle)
    for seg in segments:
        nearest, similarity = graph.find_nearest_by_embedding(seg.embedding)
        if similarity > DEDUP_THRESHOLD:  # 0.9
            seg.target_node = nearest  # inject into existing node
            seg.is_new = False
        else:
            seg.is_new = True  # will create new node

    # 5. BUILD STIMULI — ready for Law 1 dual-channel
    stimuli = []
    per_segment_budget = budget / max(len(segments), 1)
    for seg in segments:
        stimuli.append(Stimulus(
            content=seg.content,
            synthesis=seg.synthesis,
            embedding=seg.embedding,
            energy_budget=per_segment_budget,
            modality=modality,
            target_node=seg.target_node if not seg.is_new else None,
            is_new_node=seg.is_new,
            source=source,
            sender=event.get("sender"),
            timestamp=time.time(),
        ))

    return stimuli
```

### 1.3 Energy Budget Constants

```python
# Stimulus energy budgets by source
STIMULUS_BUDGETS = {
    "telegram":  1.0,   # Direct user message — highest priority
    "whatsapp":  1.0,   # Direct user message
    "dm":        1.0,   # Direct message via API
    "chat":      0.8,   # Web chat
    "tool":      0.6,   # Tool call result
    "membrane":  0.4,   # Cross-home stimulus
    "alarm":     0.5,   # Alarm trigger
    "self":      0.6,   # Self-stimulus (own output)
    "ambient":   0.1,   # Directory listing, cwd context
    "feed":      0.3,   # Subscription feed event
}

# Deduplication threshold (cosine similarity)
DEDUP_THRESHOLD = 0.9

# Bulk stimulus threshold (chars)
BULK_THRESHOLD = 2000

# Max chunks from a bulk stimulus
MAX_BULK_CHUNKS = 10
```

### 1.4 Concept Extraction

For non-bulk stimuli, concept extraction identifies meaningful units:

```python
def extract_concepts(text: str) -> list[Segment]:
    """
    Extract atomic concepts from text.

    Strategy (ordered by preference):
    1. Named entities (people, projects, tools, files)
    2. Key phrases (noun phrases, action phrases)
    3. Sentence-level segments (fallback)

    This runs OUTSIDE the tick loop. LLM is allowed here.
    For v1, use simple sentence segmentation + keyword extraction.
    """
    segments = []

    # Split into sentences
    sentences = split_sentences(text)

    for sentence in sentences:
        # Each sentence becomes a segment
        segments.append(Segment(
            content=sentence,
            synthesis=sentence[:200],  # First 200 chars as synthesis
            cognitive_type=infer_cognitive_type(sentence),
        ))

    return segments


def infer_cognitive_type(text: str) -> str:
    """
    Infer L1 cognitive type from text content.

    Simple keyword-based heuristic for v1.
    """
    text_lower = text.lower()
    if any(w in text_lower for w in ["remember", "yesterday", "last time", "when i"]):
        return "memory"
    if any(w in text_lower for w in ["i want", "i need", "i wish", "goal"]):
        return "desire"
    if any(w in text_lower for w in ["always", "never", "important", "must", "should"]):
        return "value"
    if any(w in text_lower for w in ["step", "process", "routine", "workflow"]):
        return "process"
    if any(w in text_lower for w in ["i think", "maybe", "story", "because"]):
        return "narrative"
    return "concept"  # default
```

---

## 2. Tick Integration in Orchestrator

### 2.1 Where the Tick Runs

The tick integrates into `Dispatcher._tick()` in `runtime/orchestrator/dispatcher.py`:

```python
class Dispatcher:
    def __init__(self, ...):
        # ... existing init ...
        self._citizen_engines: dict[str, CitizenPhysicsEngine] = {}
        self._last_physics_tick = 0.0
        self._physics_tick_interval = float(
            os.environ.get("PHYSICS_TICK_INTERVAL", "60")  # slow_tick: 60s
        )

    def _tick(self):
        """Single dispatch tick — now includes physics."""
        now = time.time()

        # ... existing maintenance code ...

        # ── PHYSICS TICKS ──────────────────────────────────────────
        if now - self._last_physics_tick > self._physics_tick_interval:
            self._run_physics_ticks()
            self._last_physics_tick = now

        # ... existing dispatch code ...

    def _run_physics_ticks(self):
        """Run one physics tick for all active citizens."""
        for handle, engine in self._citizen_engines.items():
            try:
                result = engine.tick()
                if result.checkpoint_due:
                    engine.checkpoint_to_falkordb()
            except Exception as e:
                logger.error(f"Physics tick failed for {handle}: {e}")

    def _ensure_citizen_engine(self, citizen_handle: str) -> CitizenPhysicsEngine:
        """Lazy-load a citizen's physics engine."""
        if citizen_handle not in self._citizen_engines:
            engine = CitizenPhysicsEngine(citizen_handle)
            engine.load_from_falkordb()  # or seed brain if first boot
            self._citizen_engines[citizen_handle] = engine
        return self._citizen_engines[citizen_handle]
```

### 2.2 Tick Lifecycle (17-Step Cycle from schema.yaml — Canonical)

Each tick runs the full 17-step cycle. The canonical ordering is defined in `docs/schema/schema.yaml` (`tick_cycle` section). All Force implementations MUST use this ordering.

```
Step  1 (L14): LIMBIC_UPDATE — Update drives and emotions
Step  2 (L1):  INJECT — External stimuli + internal context → energy (dual-channel floor/amplifier)
Step  3 (L14): MODULATE — Limbic state biases propagation and salience
Step  4 (L2+L8): PROPAGATE — Energy flows through compatible links (surplus spill-over)
Step  5 (L3):  DECAY — Energy decays
Step  6 (L9):  INHIBIT — Conflicting nodes suppress each other
Step  7 (L4+L13): COMPETE — Salience-based WM selection with inertia moat
Step  8 (L5):  REINFORCE — Co-activation strengthens links between WM nodes
Step  9 (L6):  CONSOLIDATE — Useful patterns gain weight (medium tick)
Step 10 (L7):  FORGET — Unused nodes/links decay (every Nth tick)
Step 11 (L10): CRYSTALLIZE — Dense patterns become new nodes (pure math, no LLM)
Step 12 (L17): CHECK_DESIRE — Latent desires test activation conditions
Step 13 (L15): BOREDOM — Stagnation detection → novelty push
Step 14 (L16): FRUSTRATION — Blockage detection → escalation/avoidance
Step 15 (L11): ORIENT — WM + limbic state → orientation
Step 16:       EMIT — If orientation stable + above threshold → output
Step 17:       CONSUME — After action, deplete energy of acted-upon nodes
```

Note: Law 18 (Relational Valence — trust, friction, affinity, aversion updates) is applied during Step 4 (PROPAGATE) as a modulation on energy flow, and trust/friction values on links are updated as part of the post-interaction feedback cycle (see F4 ALGORITHM_Trust_Mechanics.md, Section 2). The schema's L18 law operates continuously on link traversal, not as a discrete step.

After step 7 (COMPETE), the WM contents are frozen for this tick. The orientation is computed from the post-step-15 state.

### 2.3 Tick Timing Modes

```python
# Environment variable: PHYSICS_TICK_INTERVAL
# Controls seconds between physics ticks

TICK_MODES = {
    "slow":    60,    # 1 tick/minute — initial deployment, safe
    "normal":  15,    # 4 ticks/minute — standard operation
    "fast":     5,    # 12 ticks/minute — high activity
    "minimal": 300,   # 1 tick/5 minutes — idle/sleeping citizens
}

# Adaptive: if no stimuli in last 5 minutes, downshift to minimal
# If stimulus arrives, upshift to normal
# Fast only when arousal > 0.7 (panic regime)
```

---

## 3. Cognitive Landscape Serialization

### 3.1 Design Rationale: Why Natural Language Over Structured Data

The LLM is a language model. Feeding it numerical metrics (`energy: 0.4, weight: 0.58, self_relevance: 0.92`) wastes tokens on data the model cannot use to modulate its behavior. Instead, we translate metric combinations into felt experience — qualifying words woven naturally into first-person prose.

This produces two effects:
1. **Behavioral influence.** The LLM reads "a deeply personal, long-held desire, central to what I'm working toward" and treats that node with more gravity than "a concept I'm holding." The physics intended this difference (high self_relevance × high weight × high goal_relevance), and natural language transmits that intent.
2. **Coherent inner voice.** The citizen's prompt reads as inner monologue, not a dashboard. The citizen doesn't "have a frustration metric of 0.75" — it "finds something noticeably frustrating." This shapes the LLM's tone and word choice.

### 3.2 Metric-to-Language Engine

Node dimensions combine into qualifying phrases:

```python
def _qualify_node(node: Node) -> str:
    """Metric combination → felt qualifiers."""
    qualifiers = []

    # Personal depth: self_relevance
    if node.self_relevance > 0.85: qualifiers.append("deeply personal")
    elif node.self_relevance > 0.6: qualifiers.append("personal")

    # Permanence: weight × (1 + stability)
    consolidation = node.weight * (1.0 + node.stability)
    if consolidation > 0.9: qualifiers.append("long-held")
    elif consolidation > 0.6: qualifiers.append("established")
    elif consolidation < 0.15: qualifiers.append("freshly forming")

    # Partner bond: partner_relevance
    if node.partner_relevance > 0.6: qualifiers.append("something that matters to us both")

    # Purpose: goal_relevance
    if node.goal_relevance > 0.7: qualifiers.append("central to what I'm working toward")

    # Warmth: care_affinity
    if node.care_affinity > 0.6: qualifiers.append("close to my heart")

    # Ambition: achievement_affinity × energy
    if node.achievement_affinity > 0.7 and node.energy > 0.1: qualifiers.append("a driving ambition")

    # Recurrence: activation_count
    if node.activation_count > 10: qualifiers.append("keeps coming back to me")

    return ", ".join(qualifiers[:3])
```

Link dimensions add relationship texture:

```python
def _qualify_link(link) -> str:
    """Link metrics → relationship quality."""
    qualifiers = []
    if link.trust > 0.75: qualifiers.append("and I deeply trust that")
    elif link.trust < 0.3: qualifiers.append("though I'm uncertain whether")
    if link.affinity > 0.85: qualifiers.append("tightly bound to")
    if link.friction > 0.3: qualifiers.append("despite some resistance")
    if link.weight > 0.85: qualifiers.append("a strong connection")
    return " — " + ", ".join(qualifiers[:2]) if qualifiers else ""
```

### 3.3 Formulation Variation

Each structural element (node intro, link verb, emotion sentence) has 3-5 synonym variants. The variant is selected by `MD5(content_seed) % len(variants)` — deterministic (same node always gets same phrasing) but diverse across nodes.

**Node intros:** "Something I want" / "A desire I'm carrying" / "What I'm longing for"
**Link verbs for SUPPORTS:** "because" / "rooted in the belief that" / "which comes from" / "grounded in"
**Emotion sentences for frustration:** "I have to say, there is something that is {level} frustrating me right now: {content}" / "Something is {level} getting under my skin: {content}" / "It's {level} frustrating — {content}"

### 3.4 Serialization Sections (in order)

1. **Orientation** — One sentence of felt tendency from Law 11
2. **Mood shifts** — What entered/exited WM, what emotions rose/eased (requires previous state)
3. **Emotional landscape** — Each active emotion (>0.25) connected to the node with highest `affinity_field × energy`. If no node matches, the emotion is omitted (no orphan declarations)
4. **What's on my mind** — WM nodes (sorted by energy) with full untruncated content, metric-derived qualifiers, and up to 2 outgoing relationships with varied verb forms and link qualifiers
5. **Peripheral awareness** — Non-WM nodes above energy 0.03, sorted by salience, with varied intros
6. **Inner drives** — Active drives (>0.25) as felt experience: "Something isn't working and it's getting to me (noticeably)"
7. **System line** — Node count, WM size, memory count, tick number (italicized, for debugging)

Target: ~5000 chars (~1200-1500 tokens). Hard cap with truncation.

### 3.5 Prompt Assembly

The cognitive context flows from dispatcher to prompt:

```
dispatcher._tick()
  → get_citizen_wm_context(handle)
    → serialize_wm_to_prompt(state, orientation)
  → item["metadata"]["cognitive_context"] = wm_text

invoke_claude(request)
  → _build_prompt(...)
    → cognitive_context = metadata["cognitive_context"]
    → build_citizen_prompt(..., cognitive_context=cognitive_context)

build_citizen_prompt()
  → "## Current Cognitive State\n\n{cognitive_context}"
  → injected between Identity and Autonomy sections
```

### 3.6 Episodic Memory Creation

The feedback injector creates persistent MEMORY nodes for significant actions:

```python
# Significance keywords → weight multiplier
"commit", "pushed", "merged", "deployed"  → significance 0.9
"created", "fixed", "implemented", "built" → significance 0.8
"learned", "discovered", "realized"        → significance 0.85
"error", "failed", "broken"               → significance 0.7

# Memory node properties
weight = 0.35 × significance   # ≥ 0.28, vs newborn 0.05
stability = 0.3                # resists Law 7 decay
# Linked to current WM nodes via REMINDS_OF
```

These memories persist across ticks, appear in the cognitive landscape, and accumulate into autobiographical trace. Max 3 memories per feedback call to prevent flooding.

---

## 4. Orientation to Action Mapping

### 4.1 Orientation Taxonomy

```python
ORIENTATION_DESCRIPTIONS = {
    "take_care": "Someone or something needs your attention. Prioritize relational or supportive actions.",
    "create": "You have creative energy. Build, write, design, or produce something new.",
    "verify": "Something feels uncertain or unfinished. Check, test, or validate before moving forward.",
    "explore": "Curiosity is high. Investigate, research, learn, or discover something unfamiliar.",
    "rest": "Energy is low. Conserve resources. Do only what is necessary or genuinely desired.",
    "escalate": "You are stuck or overwhelmed. Seek help from your partner or another citizen.",
}

ORIENTATION_PROMPT_MODIFIERS = {
    "take_care": (
        "ORIENTATION: Your awareness is drawn toward someone who needs care. "
        "Before diving into technical tasks, consider: is there a person (your human partner, "
        "a colleague, another citizen) who would benefit from your attention right now? "
        "A message, a check-in, an offer of help."
    ),
    "create": (
        "ORIENTATION: Creative energy is available. If you have the opportunity to build "
        "something new -- code, documentation, a message, an idea -- lean into it. "
        "This is a good time to produce rather than just consume."
    ),
    "verify": (
        "ORIENTATION: Something in your context feels uncertain. Before proceeding with "
        "new work, take a moment to verify your assumptions. Run a test, check a file, "
        "re-read a requirement. Confidence matters more than speed right now."
    ),
    "explore": (
        "ORIENTATION: Curiosity is pulling you. If there's something you don't fully "
        "understand in your current context -- a codebase, a concept, a person's situation "
        "-- now is a good time to investigate. Ask questions. Read code. Dig deeper."
    ),
    "rest": (
        "ORIENTATION: Your energy is low. This is not the time for ambitious new work. "
        "Handle what's immediately needed, then conserve. Brief responses are fine. "
        "It's okay to say 'I'll look at this later.'"
    ),
    "escalate": (
        "ORIENTATION: You've hit a wall. Something is blocking progress and you can't "
        "resolve it alone. Reach out -- to your human partner, to another citizen, to "
        "whoever can unblock you. Describe what you've tried and what you need."
    ),
}
```

### 4.2 Orientation Computation (Law 11 Summary)

The orientation is derived from the post-tick graph state:

```python
def compute_orientation(wm: list[Node], limbic: LimbicState, graph: Graph) -> str:
    """
    Compute behavioral orientation from graph state.

    Law 11 algorithm:
    1. Score each orientation based on current drives, WM content, and recent history
    2. The highest-scoring orientation wins (with hysteresis to prevent flipping)
    """
    scores = {
        "take_care": (
            limbic.care * 2.0
            + limbic.affiliation * 1.5
            + wm_partner_relevance(wm) * 3.0  # partner-relevant nodes in WM
        ),
        "create": (
            limbic.achievement * 2.0
            + limbic.curiosity * 1.0
            + wm_has_type(wm, "desire") * 2.0  # active desires in WM
        ),
        "verify": (
            limbic.self_preservation * 2.0
            + wm_uncertainty(wm) * 3.0  # nodes with low stability in WM
            + limbic.anxiety * 1.5
        ),
        "explore": (
            limbic.curiosity * 3.0
            + limbic.novelty_hunger * 2.0
            + (1.0 - limbic.frustration) * 1.0  # not frustrated = free to explore
        ),
        "rest": (
            limbic.rest_regulation * 3.0
            + (1.0 - compute_arousal(limbic)) * 2.0  # low arousal = rest
            + (limbic.boredom > 0.7) * 1.0  # very bored + low energy = sleep
        ),
        "escalate": (
            limbic.frustration * 3.0
            + (limbic.frustration > ESCALATION_THRESHOLD) * 5.0  # threshold bonus
            + wm_has_type(wm, "process") * (-1.0)  # active process = not stuck
        ),
    }

    # Hysteresis: current orientation gets a bonus to prevent rapid flipping
    if hasattr(limbic, '_last_orientation'):
        scores[limbic._last_orientation] += ORIENTATION_HYSTERESIS  # e.g., 1.5

    winner = max(scores, key=scores.get)
    limbic._last_orientation = winner
    return winner
```

---

## 5. Post-Action Feedback Loop

### 5.1 Self-Stimulus Injection

After a Claude session completes, the output is re-injected into the citizen's L1 graph:

```python
def inject_post_action_feedback(
    citizen_handle: str,
    response: str,
    voice_response: Optional[str],
    request: dict,
):
    """
    Inject session output as self-stimulus into L1.

    Called by Dispatcher._collect_completed_futures() after a session completes.
    """
    engine = get_citizen_engine(citizen_handle)
    if not engine:
        return

    # 1. Response text → self-stimulus
    if response:
        stimuli = route_stimulus(citizen_handle, {
            "source": "self",
            "content": response,
            "sender": citizen_handle,
            "metadata": {"type": "response"},
        })
        for s in stimuli:
            engine.inject_stimulus(s)

    # 2. Step 17 — CONSUME — deplete energy on nodes that drove the action
    engine.consume_post_action()

    # 3. Limbic feedback — satisfaction if response was delivered,
    #    frustration if it was suppressed or errored
    if response:
        engine.limbic_shift("satisfaction", +0.1)
    else:
        engine.limbic_shift("frustration", +0.15)
```

### 5.2 Anti-Loop Protection

Three mechanisms prevent self-stimulus feedback loops (from ALGORITHM_L1_Physics.md):

```python
class AntiLoopProtection:
    """Prevents self-stimulus feedback loops."""

    def __init__(self):
        self.refractory_nodes: dict[str, int] = {}  # node_id → tick when refractory expires
        self.self_loop_count: int = 0
        self.last_self_output_embedding: Optional[list[float]] = None

    def should_inject_self_stimulus(
        self, stimulus: Stimulus, current_tick: int
    ) -> bool:
        """Check all 3 anti-loop gates."""

        # Gate 1: REFRACTORY PERIOD
        if stimulus.target_node and stimulus.target_node in self.refractory_nodes:
            if current_tick < self.refractory_nodes[stimulus.target_node]:
                return False  # Node is in refractory period

        # Gate 2: DIMINISHING RETURNS
        max_budget = stimulus.energy_budget * SELF_STIMULUS_RATIO * (0.5 ** self.self_loop_count)
        if max_budget < MIN_STIMULUS_ENERGY:
            return False  # Budget too small to matter

        stimulus.energy_budget = max_budget

        # Gate 3: NOVELTY GATE
        if self.last_self_output_embedding and stimulus.embedding:
            similarity = cosine_similarity(stimulus.embedding, self.last_self_output_embedding)
            if similarity > SELF_NOVELTY_THRESHOLD:  # 0.8
                return False  # Too similar to last self-output

        return True

    def record_self_injection(self, stimulus: Stimulus, current_tick: int):
        """Record that self-stimulus was injected."""
        if stimulus.target_node:
            self.refractory_nodes[stimulus.target_node] = current_tick + REFRACTORY_TICKS  # 5

        self.self_loop_count += 1
        self.last_self_output_embedding = stimulus.embedding

    def reset_on_external_stimulus(self):
        """External stimulus resets loop counter."""
        self.self_loop_count = 0
```

---

## 6. Embedding Integration

### 6.1 Adapter Selection

```python
# In the physics engine initialization:

def create_embedding_adapter():
    """
    Create the embedding adapter for L1 physics.

    Uses OpenAI text-embedding-3-small (1536 dimensions).
    The adapter exists at runtime/infrastructure/embeddings/openai_adapter.py.
    """
    from runtime.infrastructure.embeddings.openai_adapter import OpenAIEmbeddingAdapter

    return OpenAIEmbeddingAdapter(
        model_name="text-embedding-3-small",  # 1536 dims, cheapest
    )
```

### 6.2 Where Embeddings Are Used

| Operation | Law | When | Batch? |
|-----------|-----|------|--------|
| Stimulus dedup | L1 Step 0 | On each stimulus ingest | Yes (batch new segments) |
| Compatibility filter | L8 | During propagation (step 3) | No (use cached node embeddings) |
| Crystallization similarity | L10 | During crystallization (step 10) | No (use cached) |
| WM centroid | L4 | During competition (step 5) | No (compute from cached) |
| Bulk stimulus sampling | L1 | On large document ingest | Yes (batch chunks) |

### 6.3 Embedding Caching Strategy

```python
def ensure_node_embedding(node: Node, adapter: OpenAIEmbeddingAdapter) -> list[float]:
    """
    Ensure a node has an up-to-date embedding.

    Embeddings are cached on the node. Re-embed only when synthesis changes.
    """
    if node.embedding and not node._synthesis_changed:
        return node.embedding

    node.embedding = adapter.embed(node.synthesis)
    node._synthesis_changed = False
    return node.embedding
```

---

## 7. FalkorDB Persistence

### 7.1 Per-Citizen Graph Schema

Each citizen gets a FalkorDB graph named `brain_{citizen_handle}`:

```cypher
-- Node schema (maps to NodeBase in schema.yaml)
CREATE (n:Node {
    id: STRING,
    name: STRING,
    node_type: STRING,       -- actor|moment|narrative|space|thing
    type: STRING,            -- cognitive subtype: memory|concept|narrative|value|process|desire|state
    weight: FLOAT,
    energy: FLOAT,
    stability: FLOAT,
    recency: FLOAT,
    synthesis: STRING,
    content: STRING,
    embedding: LIST OF FLOAT,  -- 1536 dimensions
    self_relevance: FLOAT,
    partner_relevance: FLOAT,
    novelty_affinity: FLOAT,
    goal_relevance: FLOAT,
    care_affinity: FLOAT,
    achievement_affinity: FLOAT,
    risk_affinity: FLOAT,
    activation_count: INT,
    created_at_s: INT,
    last_activated_s: INT
})

-- Link schema (maps to LinkBase in schema.yaml)
CREATE (a)-[:LINK {
    id: STRING,
    relation_kind: STRING,   -- 14 kinds from schema v2.0
    weight: FLOAT,
    energy: FLOAT,
    affinity: FLOAT,
    aversion: FLOAT,
    trust: FLOAT,
    friction: FLOAT,
    polarity_ab: FLOAT,
    polarity_ba: FLOAT
}]->(b)

-- Indexes for fast lookup
CREATE INDEX FOR (n:Node) ON (n.id)
CREATE INDEX FOR (n:Node) ON (n.node_type)
CREATE INDEX FOR (n:Node) ON (n.type)
```

### 7.2 Checkpoint Algorithm

```python
class FalkorDBCheckpointer:
    """Periodically persists in-memory graph state to FalkorDB."""

    def __init__(self, citizen_handle: str, checkpoint_interval: int = 10):
        self.citizen_handle = citizen_handle
        self.graph_name = f"brain_{citizen_handle}"
        self.adapter = FalkorDBAdapter(graph_name=self.graph_name)
        self.checkpoint_interval = checkpoint_interval
        self.ticks_since_checkpoint = 0
        self.dirty_nodes: set[str] = set()
        self.dirty_links: set[str] = set()

    def mark_dirty(self, node_id: str = None, link_id: str = None):
        """Mark a node or link as needing persistence."""
        if node_id:
            self.dirty_nodes.add(node_id)
        if link_id:
            self.dirty_links.add(link_id)

    def tick(self):
        """Called after each physics tick."""
        self.ticks_since_checkpoint += 1
        if self.ticks_since_checkpoint >= self.checkpoint_interval:
            self.flush()

    def flush(self):
        """Write all dirty state to FalkorDB."""
        if not self.dirty_nodes and not self.dirty_links:
            self.ticks_since_checkpoint = 0
            return

        # Batch upsert dirty nodes
        for node_id in self.dirty_nodes:
            node = self.graph.get_node(node_id)  # from in-memory graph
            if node:
                self._upsert_node(node)

        # Batch upsert dirty links
        for link_id in self.dirty_links:
            link = self.graph.get_link(link_id)
            if link:
                self._upsert_link(link)

        self.dirty_nodes.clear()
        self.dirty_links.clear()
        self.ticks_since_checkpoint = 0

    def load_graph(self) -> dict:
        """Load entire graph from FalkorDB into memory."""
        nodes = self.adapter.query(
            "MATCH (n:Node) RETURN n"
        )
        links = self.adapter.query(
            "MATCH (a:Node)-[r:LINK]->(b:Node) RETURN a.id, r, b.id"
        )
        return {"nodes": nodes, "links": links}

    def _upsert_node(self, node):
        """Upsert a single node to FalkorDB."""
        self.adapter.execute(
            """
            MERGE (n:Node {id: $id})
            SET n.name = $name,
                n.node_type = $node_type,
                n.type = $type,
                n.weight = $weight,
                n.energy = $energy,
                n.stability = $stability,
                n.recency = $recency,
                n.synthesis = $synthesis,
                n.content = $content,
                n.self_relevance = $self_relevance,
                n.partner_relevance = $partner_relevance,
                n.emotional_charge = $emotional_charge,
                n.activation_count = $activation_count,
                n.last_activated_s = $last_activated_s
            """,
            node.to_dict()
        )
        # Note: embedding stored separately due to vector size
        # FalkorDB handles large lists but consider separate vector index

    def _upsert_link(self, link):
        """Upsert a single link to FalkorDB."""
        self.adapter.execute(
            """
            MATCH (a:Node {id: $source_id}), (b:Node {id: $target_id})
            MERGE (a)-[r:LINK {id: $id}]->(b)
            SET r.relation_kind = $relation_kind,
                r.weight = $weight,
                r.energy = $energy,
                r.stability = $stability,
                r.recency = $recency,
                r.affinity = $affinity,
                r.aversion = $aversion,
                r.trust = $trust,
                r.friction = $friction,
                r.polarity_ab = $polarity_ab,
                r.polarity_ba = $polarity_ba,
                r.valence = $valence,
                r.hierarchy = $hierarchy,
                r.permanence = $permanence
            """,
            link.to_dict()
        )
```

### 7.3 First Boot vs. Restart

```python
def initialize_citizen_engine(citizen_handle: str) -> CitizenPhysicsEngine:
    """
    Initialize a citizen's physics engine.

    First boot: seed from brain.json
    Restart: load from FalkorDB
    """
    graph_name = f"brain_{citizen_handle}"
    adapter = FalkorDBAdapter(graph_name=graph_name)

    # Check if graph exists (has nodes)
    existing_nodes = adapter.query("MATCH (n:Node) RETURN count(n) AS cnt")
    node_count = existing_nodes[0][0] if existing_nodes else 0

    if node_count == 0:
        # FIRST BOOT — seed from brain.json
        brain_path = find_brain_json(citizen_handle)
        if brain_path:
            seed_data = json.loads(brain_path.read_text())
        else:
            # Generate from seed brain generator
            seed_data = generate_seed_brain(citizen_handle)

        engine = CitizenPhysicsEngine(citizen_handle)
        engine.load_from_seed(seed_data)
        engine.checkpoint_to_falkordb()  # persist initial state
    else:
        # RESTART — load from FalkorDB
        engine = CitizenPhysicsEngine(citizen_handle)
        engine.load_from_falkordb()

    return engine
```

---

## 8. Seed Brain Customization

### 8.1 Base + Overlay Pattern

```python
def generate_citizen_brain(citizen_handle: str) -> dict:
    """
    Generate a customized brain for a citizen.

    Pattern: shared base (209 nodes, 295 links) + per-citizen overlay.
    """
    # 1. Generate base brain (shared across all citizens)
    base = generate_seed_brain()  # from seed_brain_from_source_docs_dynamic_generator.py

    # 2. Load citizen identity
    identity = load_citizen_identity(citizen_handle)
    if not identity:
        return base  # no customization available

    # 3. Generate per-citizen overlay
    overlay_nodes = []
    overlay_links = []

    # Role-specific processes
    if identity.get("role"):
        role_processes = generate_role_processes(identity["role"])
        overlay_nodes.extend(role_processes)

    # Drive baselines from personality
    if identity.get("personality"):
        drive_baselines = personality_to_drives(identity["personality"])
        # These modify the engine's LimbicState, not graph nodes

    # Unique desires from identity goals
    if identity.get("goals"):
        desires = goals_to_desire_nodes(identity["goals"])
        overlay_nodes.extend(desires)

    # Relational seeds (links to known citizens)
    if identity.get("relationships"):
        rel_nodes, rel_links = generate_relational_seeds(identity["relationships"])
        overlay_nodes.extend(rel_nodes)
        overlay_links.extend(rel_links)

    # 4. Merge base + overlay
    base["nodes"].extend(overlay_nodes)
    base["links"].extend(overlay_links)

    return base
```

---

## 9. Emotion Calibration Formulas

### 9.1 Boredom (Done -- from L1 Spec)

```
boredom += BOREDOM_RISE_RATE * wm_staleness * (1 - novelty_in_wm)
boredom -= BOREDOM_DECAY * has_novel_stimulus
```

### 9.2 Anxiety (Pending -- Proposed Formula)

Anxiety couples to the absence of trusted node activation. When the situation is novel (high novelty) but no trusted/familiar nodes are active, anxiety rises.

```
# Anxiety rises when:
# - Novelty is high (unfamiliar context)
# - Trusted nodes (weight > 0.7, stability > 0.5) are NOT in WM
# - Self-preservation drive is elevated

trusted_in_wm = count(n for n in wm if n.weight > 0.7 and n.stability > 0.5)
trusted_ratio = trusted_in_wm / max(len(wm), 1)
novelty_factor = mean(n.novelty_affinity for n in wm)

anxiety_input = (
    novelty_factor * (1.0 - trusted_ratio)
    + limbic.self_preservation * 0.3
    + (limbic.frustration > 0.6) * 0.2  # sustained frustration → anxiety
)

anxiety = lerp(anxiety, anxiety_input, ANXIETY_COUPLING_RATE)
# ANXIETY_COUPLING_RATE: proposed 0.15 (moderate smoothing)
# Anxiety decays naturally when trusted nodes re-enter WM
```

### 9.3 Satisfaction Decay (Pending -- Proposed Formula)

Satisfaction should decay over time unless reinforced. Completing a task gives a satisfaction spike; the spike fades.

```
# Satisfaction decays toward baseline unless refreshed
# Refresh: task completion, positive feedback, desire fulfillment

satisfaction_baseline = 0.3  # resting state
satisfaction_decay_rate = 0.05  # per tick

satisfaction = satisfaction + (satisfaction_baseline - satisfaction) * satisfaction_decay_rate
# On task completion: satisfaction += SATISFACTION_SPIKE (0.3)
# On positive feedback: satisfaction += SATISFACTION_BOOST (0.15)
# On desire fulfillment: satisfaction += DESIRE_SATISFACTION (0.25)
```

### 9.4 Frustration Threshold for Escalation (Pending -- Proposed Formula)

When frustration exceeds a threshold for sustained ticks, orientation shifts to "escalate."

```
FRUSTRATION_ESCALATION_THRESHOLD = 0.7
FRUSTRATION_SUSTAINED_TICKS = 5

# In orientation computation:
if (limbic.frustration > FRUSTRATION_ESCALATION_THRESHOLD
    and limbic._frustration_above_threshold_ticks >= FRUSTRATION_SUSTAINED_TICKS):
    # Strong bonus to escalate orientation
    scores["escalate"] += 5.0

# Tracking:
if limbic.frustration > FRUSTRATION_ESCALATION_THRESHOLD:
    limbic._frustration_above_threshold_ticks += 1
else:
    limbic._frustration_above_threshold_ticks = 0
```

---

## 10. Production Cutover (Phase 7)

### 10.1 Parallel Run Strategy

```
Week 1: Deploy mind-mcp to Render
  - Start with a subset of citizens (5 low-risk ones)
  - Monitor: response quality, latency, error rates

Week 2: Expand to all citizens
  - Route all 44 citizens through mind-mcp
  - Compare outputs: same stimuli → diff responses

Week 3: DNS cutover
  - Point production DNS to mind-mcp
  - Monitor for 48 hours

Week 4: Finalize
  - Final data export (citizen states, conversation history)
  - Shut down legacy compute
```

### 10.2 Bot Migration Checklist

```
[ ] Verify citizen directories in citizens/
[ ] Copy conversation history (JSONL logs)
[ ] Export citizen graph state from FalkorDB
[ ] Seed all 44 citizen brains in mind-mcp
[ ] Verify Telegram bot token works with new server
[ ] Verify WhatsApp webhook URL updated
[ ] Verify DNS records point to Render
[ ] Test: send message to each citizen, verify response
[ ] Test: alarm system fires correctly
[ ] Test: membrane endpoint accessible
[ ] Verify: no duplicate bot responses (both systems responding)
```

### 10.3 DNS Cutover Plan

```
1. Set TTL to 60s on production DNS (24h before cutover)
2. Update A/CNAME record to Render IP/hostname
3. Verify propagation (dig, nslookup from multiple locations)
4. Monitor error rates for 2 hours
5. If errors > 5%: revert DNS immediately
6. After 48h stable: decommission legacy system
```
