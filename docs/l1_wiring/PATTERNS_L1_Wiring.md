# PATTERNS -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Status:** DESIGNING (v0.1)

---

## Design Philosophy

### The Graph Computes Between LLM Calls

The fundamental insight: the LLM is expensive and slow. The graph is cheap and fast. Between each Claude invocation, the graph runs physics -- energy flows, weights consolidate, working memory shifts, drives update, boredom rises, desires activate. When the LLM finally fires, it receives a curated cognitive context (WM) that reflects all this background processing.

This means the tick loop is NOT synchronized with Claude calls. Ticks run continuously (or on a timer). Claude calls happen when the orchestrator dispatches work. The WM snapshot at dispatch time is what the citizen "knows" for that session.

```
EXTERNAL EVENT ─────┐
                     ▼
              ┌──────────────┐
              │ Law 1: Inject │ ← Stimulus pre-processing (segment, dedup, embed)
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Laws 2-18:   │ ← N ticks of pure graph physics (no LLM)
              │ Tick Loop    │   energy flows, WM shifts, drives update
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Law 11:      │ ← Orientation emerges from graph state
              │ Orientation  │   (take_care/create/verify/explore/rest/escalate)
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ WM → Prompt  │ ← 5-7 nodes serialized into system prompt
              │ Assembly     │   weight-proportional token budget
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Claude Code  │ ← LLM session with cognitive context
              │ Subprocess   │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ Self-Stimulus │ ← LLM output re-injected as new stimuli
              │ Feedback     │   (anti-loop protected)
              └──────────────┘
```

### The Cognitive Landscape Is Natural Language, Not Data

WM is the bottleneck. The graph may have 500+ nodes. The prompt has ~1500 tokens of cognitive budget. WM selection (Law 4) is the gatekeeper: it picks the 5-7 most salient nodes. But the serialized output extends beyond WM to include peripheral awareness, emotional connections, active links, and metric-derived qualifiers.

**Why natural language?** The LLM is a language model. `energy: 0.4, weight: 0.58` is data it cannot internalize. But "a deeply personal, long-held desire — this is at the edge of awareness" is meaning it can use to shape its tone and priorities. The prompt reads like inner monologue, not a dashboard.

**The Metric-to-Language Engine.** Rather than showing numerical dimensions, the serializer translates metric combinations into qualifying words woven into sentences:

| Metric Combination | What It Means Subjectively | Words Produced |
|---|---|---|
| `self_relevance > 0.85` | This is core to who I am | "deeply personal" |
| `weight × (1+stability) > 0.9` | I've held this a long time | "long-held" |
| `weight × (1+stability) < 0.15` | This just appeared | "freshly forming" |
| `partner_relevance > 0.6` | This matters to my human too | "something that matters to us both" |
| `goal_relevance > 0.7` | This is tied to my purpose | "central to what I'm working toward" |
| `care_affinity > 0.6` | I feel warmth about this | "close to my heart" |
| `achievement_affinity > 0.7 + energy > 0.1` | I'm actively striving for this | "a driving ambition" |
| `activation_count > 10` | This thought is recurrent | "keeps coming back to me" |
| Link `trust > 0.75` | The connection is reliable | "and I deeply trust that" |
| Link `affinity > 0.85` | The bond is strong | "tightly bound to" |
| Link `friction > 0.3` | Something resists | "despite some resistance" |

**Why this helps:** These qualifiers are computed from the physics, not hallucinated. When the LLM reads "a deeply personal, established desire, central to what I'm working toward" it treats that node differently than "a concept I'm holding" — which is exactly what the physics intended. The dimensions that were invisible as numbers become behavioral influence as language.

**Link verbs vary.** Instead of a single `supports` → `"is supported by"`, each link type maps to 3-5 synonym variants (`"because"`, `"rooted in the belief that"`, `"grounded in"`). The variant is selected deterministically by content hash, so the same node always gets the same phrasing but different nodes get different formulations. This prevents the monotone "is supported by... is supported by..." pattern.

**Emotions connect to nodes.** Instead of listing `Frustration: 0.60`, the serializer finds which node has the highest `achievement_affinity × energy` and says: "It's noticeably frustrating — Always have projects on the fire..." The emotion is grounded in a specific thought, not floating abstractly. If no node matches, the emotion line is omitted entirely (no orphan declarations).

**Episodic memories persist.** Significant actions (commits, fixes, discoveries) create memory nodes with weight ≥ 0.28 (vs. Law 1 newborn weight of 0.05). These survive forgetting cycles and appear in the cognitive context as "Something I remember: Committed: fix membrane subscription timeout cleanup." The citizen accumulates autobiographical trace.

The output structure:

```
I feel driven toward action — I want to make concrete progress, fix things, ship.

It's noticeably frustrating — Always have projects on the fire...

**What's on my mind:**

A desire I'm carrying (personal, established, central to what I'm working toward):
  Participate in the governance of my city...
  Which comes from: I am a citizen of Mind Protocol... — tightly bound to
  Rooted in the belief that: Autonomy is earned, not granted...

**At the edge of my awareness:**
- A value I hold deeply: Governance resolves through graph physics...

**What I feel inside:**
- I want to make progress and accomplish things (mildly)
- Something isn't working and it's getting to me (noticeably)

_[215 nodes in graph, 7 in focus, 3 memories, tick #10]_
```

This is how the citizen "remembers" without explicit memory retrieval. The physics did the retrieval, and the language did the translation.

### Orientation Is Behavioral Gravity, Not a Command

Law 11 produces one of 6 qualitative orientations. These are tendencies, not instructions:

| Orientation | Behavioral Effect | Prompt Modifier |
|------------|-------------------|----------------|
| `take_care` | Prioritize partner/relational tasks | "Your partner needs attention. Consider their state before acting on other tasks." |
| `create` | Produce something new | "You have creative energy. Build, write, or make something." |
| `verify` | Check, test, validate | "Something feels uncertain. Verify before proceeding." |
| `explore` | Investigate, learn | "Curiosity is high. Explore what's unfamiliar." |
| `rest` | Reduce activity, conserve | "Energy is low. Do only what's necessary." |
| `escalate` | Seek help, report blockers | "You're stuck. Escalate to your human partner or another citizen." |

Orientation maps to a soft modifier in the prompt, not a hard constraint. The citizen can override it -- but the tendency is real.

### Stimulus Categories: What Counts as Input

Everything that happens to a citizen is a stimulus. The wiring must handle all categories:

| Category | Source | Law 1 Treatment | Energy Budget |
|----------|--------|-----------------|--------------|
| User message | Telegram, WhatsApp, DM, chat | Full injection, high priority | HIGH (1.0) |
| Tool result | Claude Code subprocess output | Inject as process activation | MEDIUM (0.6) |
| Bridge event | Group chat mention, reaction | Inject with social amplification | MEDIUM (0.5) |
| Membrane stimulus | Cross-home, subscription feed | Inject with membrane attenuation | LOW-MEDIUM (0.3-0.5) |
| Alarm firing | alarm_watcher.py trigger | Inject as temporal trigger boost | MEDIUM (0.5) |
| Self-stimulus | Own LLM output re-injected | Anti-loop protected, diminishing | VARIABLE (0.1-0.6) |
| Ambient | Directory listing, cwd context | Sub-threshold warmth | LOW (0.1) |
| Biometric | Garmin data (future) | Limbic injection, not graph nodes | LOW (0.2) |
| Economic | $MIND tx (future) | Satisfaction/frustration shift | LOW (0.2) |

### Persistence Is Hybrid: In-Memory Physics, Periodic FalkorDB Checkpoint

Running physics directly against FalkorDB would be too slow (each tick touches hundreds of nodes). The pattern:

1. **On boot:** Load citizen graph from FalkorDB into in-memory structures
2. **Per tick:** Run all 17 steps in-memory (fast, ~5ms/tick)
3. **Every N ticks:** Checkpoint dirty nodes/links to FalkorDB (batched Cypher)
4. **On shutdown:** Final checkpoint, flush all state
5. **On crash:** Lose at most N ticks of physics. Acceptable for non-critical state.

The checkpoint interval N should be tunable via env var. Start with N=10 (every 10 ticks). At 1 tick/min slow mode, that's every 10 minutes. At 12 ticks/min fast mode, that's every ~50 seconds.

### One Graph Per Citizen, Not Shared

Each citizen gets their own FalkorDB graph: `brain_{citizen_handle}`. Reasons:

1. **Isolation:** One citizen's physics cannot corrupt another's state
2. **Performance:** Queries are scoped to one brain (~200-500 nodes), not a shared pool of 44 x 500 = 22,000 nodes
3. **Backup/restore:** Can snapshot individual brains independently
4. **Migration:** Can move a citizen's brain between instances

The L3 universe graph (Force 1) is separate -- shared across all citizens. Brain graphs are private.

### The Tick Loop Lives in the Orchestrator, Not in Physics

The current orchestrator (`dispatcher.py`) has a `_tick()` method that runs periodically. The physics tick should integrate here, not as a separate process:

```
Dispatcher._tick():
    1. Periodic maintenance (cleanup, relaunch, health)
    2. Collect completed futures
    3. >>> FOR EACH CITIZEN: run_physics_tick(citizen_handle) <<<
    4. Check capacity, backoff
    5. Pop queue item, dispatch Claude
```

The physics tick for each citizen runs synchronously within the dispatcher tick. Since each tick is ~5ms in-memory, running 44 citizens = ~220ms total, well within the 1-second dispatch interval.

### Embedding Strategy: Batch on Ingest, Cache in Graph

Embeddings are expensive in API calls, not in computation. Strategy:

1. **On stimulus ingest:** Embed all new segments in a single batch call (OpenAI supports batch embedding)
2. **Store on nodes:** Each node's `embedding` field persists in FalkorDB. No re-embedding unless synthesis changes.
3. **Similarity operations:** Use stored embeddings. Law 8 compatibility, Law 1 dedup, Law 10 crystallization -- all use pre-computed vectors.
4. **Cache miss:** If a node has no embedding (legacy data), embed on first access, store result.

This means embedding costs are proportional to new node creation, not to tick frequency.

---

## Scope

### In Scope
- Stimulus injection pipeline (all sources to Law 1)
- Tick loop integration in orchestrator
- WM-to-prompt serialization
- Orientation-to-prompt mapping
- Self-stimulus feedback loop
- OpenAI embedding integration for Law 8 compatibility
- FalkorDB persistence (per-citizen graphs)
- Seed brain generation for 44 citizens
- Production deployment (Render, DNS cutover)
- Emotion calibration (remaining formulas)

### Out of Scope
- L3 universe graph (Force 1)
- $MIND economy (Force 2)
- Human partner model / biometric ingestion (Force 3)
- Trust mechanics / value taxonomy (Force 4)
- Laws 19-21 (deferred in the spec itself)
- Session parallelization (Law 19 extension -- v2 feature)
- Cross-citizen mechanisms (L2 scope)

---

## Key Design Decisions

1. **Tick loop in orchestrator, not standalone.** The orchestrator already has a periodic tick. Physics piggybacks on it. No separate process, no IPC.

2. **Hybrid persistence.** In-memory for speed, FalkorDB for durability. Checkpoint every N ticks.

3. **One graph per citizen.** Isolation, performance, backup. Graph name: `brain_{citizen_handle}`.

4. **WM serialization is structured, not raw.** The prompt receives a formatted "Current Awareness" section, not a JSON dump.

5. **Orientation is soft.** Prompt modifiers, not hard constraints. The citizen feels a pull, not a wall.

6. **Embeddings are batched and cached.** Embed on ingest, store on nodes, reuse for physics. No per-tick embedding calls.

7. **Start with slow_tick (60s).** During initial deployment, 1 tick/minute is safe. Fast tick (5s) for when the system is validated.

8. **Same base brain, per-citizen overlay.** All citizens share the 209 base nodes (values, project knowledge). Each gets additional nodes from their identity file (role-specific processes, drive baselines, unique desires).
