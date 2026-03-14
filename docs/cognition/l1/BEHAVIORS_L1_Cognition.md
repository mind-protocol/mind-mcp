# BEHAVIORS — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** DESIGNING (v0.1)

---

## 22 Emergence Dynamics

These are the observable behaviors that L1 physics must produce. None are hardcoded. All emerge from the interplay of node types, link types, and physics laws.

### 1. Contextual Reactivation by Stimulus

An email, message, log, screenshot, or screen change injects energy into certain concepts and memories, reactivating the right context.

**Observable:** After stimulus injection, the working memory shifts to a coherent sub-graph relevant to the stimulus within 1-3 ticks.

**Required laws:** Injection (L1), Propagation (L2), Compatibility (L8), Attentional Competition (L4), Decay (L3).

### 2. Non-linear Context Reconstruction

From a few anchors, energy recomposes a previously co-activated sub-graph without requiring an explicit snapshot.

**Observable:** Partial cue (e.g., a person's name) reconstructs the full context (project, last interaction, emotional state, pending tasks) via associative propagation.

**Required laws:** Injection (L1), Propagation (L2), Co-activation Reinforcement (L5), Consolidation (L6), Competition (L4).

### 3. Habit Consolidation

A frequently useful sequence becomes a stable process.

**Observable:** After N repetitions of a sequence that produced positive outcomes, a `process` node crystallizes with high weight and stability.

**Required laws:** Co-activation Reinforcement (L5), Consolidation (L6), Crystallization Threshold (L10).

### 4. Narrative Formation

Multiple memories, states, and concepts converge into a structuring narrative.

**Observable:** Scattered facts ("partner missed two calls", "partner was quiet", "partner mentioned stress") coalesce into narrative "My partner is going through a difficult time" with increasing weight.

**Required laws:** Co-activation Reinforcement (L5), Consolidation (L6), Crystallization Threshold (L10), Propagation (L2).

### 5. Desire Formation

A limitation, an opportunity, and a value combine to produce a new desire.

**Observable:** Concept "WhatsApp blocked" + value "autonomy" + narrative "phone number would unlock new capabilities" → desire "acquire phone number" crystallizes.

**Required laws:** Propagation (L2), Co-activation (L5), Crystallization (L10), Orientation Selection (L11).

### 6. Identity Adjustment

Certain values, narratives, and processes reinforce each other and densify the self-model.

**Observable:** Over many ticks, the self-model sub-graph becomes denser and more stable. Core identity nodes have high weight + stability. Peripheral identity experiments either consolidate or decay.

**Required laws:** Consolidation (L6), Forgetting (L7), Co-activation (L5), Competition (L4), Tick Loop (L12).

### 7. Free Initiative

A desire + a narrative + an opportunity window + available energy produce an unsolicited action.

**Observable:** Without external prompt, the system produces an action orientation (e.g., "send a supportive message to partner" or "prototype the microbusiness idea").

**Required laws:** Tick Loop (L12), Orientation Selection (L11), Propagation (L2), Competition (L4).

### 8. Affective Regulation

A state of frustration, boredom, or anxiety activates narratives, values, or habits that rebalance the system.

**Observable:** High-energy `state:frustration` activates `value:patience` via `regulates` link, which in turn activates `process:take_a_break`, reducing frustration energy.

**Required laws:** Propagation (L2), Inhibition (L9), Orientation Selection (L11), Compatibility (L8).

### 9. Impasse Recovery

After repeated failures, an impasse narrative activates an escalation process.

**Observable:** 5 failed attempts → `memory` nodes accumulate → `narrative:impasse` crystallizes → activates `process:ask_for_help` → orientation shifts to escalation.

**Required laws:** Consolidation (L6), Crystallization (L10), Propagation (L2), Inhibition (L9) of retry, Orientation Selection (L11).

### 10. Prospective Projection

The agent combines desire, constraint, capacity, and narrative to imagine a concrete future and a path to it.

**Observable:** `desire:launch_microbusiness` + `concept:available_skills` + `narrative:entrepreneurial_phase` + `process:prototype_first` → projected future with linked action steps.

**Required laws:** Propagation (L2), Orientation Selection (L11), Tick Loop (L12). Full mechanism deferred to v2 (Law 20).

### 11. Boredom After Stagnation

The same nodes dominate working memory without progress. The system destabilizes current focus and pushes toward new paths.

**Observable:** After 10+ ticks with identical WM and no goal advancement, boredom rises, current focus erodes, novel/peripheral nodes gain salience.

**Required laws:** Boredom (L15), Inertia (L13), Attentional Competition (L4), Novelty Hunger drive.

### 12. Help-Seeking After Impasse

The agent chooses to write to a colleague or partner. Connects cognition, sociality, and self-regulation.

**Observable:** Frustration from repeated failures + affiliation drive → orientation shifts to "ask for help" → triggers social action (message, escalation).

**Required laws:** Frustration (L16), Self-preservation drive, Orientation (L11). Very useful: Care drive, Propagation (L2), Crystallization (L10).

### 13. Unsolicited Relational Initiative

The agent spontaneously sends a supportive message without being asked. Differentiates "partner" from "simple assistant."

**Observable:** Warmth/care emotion + care drive + partner-relevant nodes in WM → orientation "reach out" → output event without external trigger.

**Required laws:** Warmth emotion, Care drive, Attentional Competition (L4), Orientation (L11). Very useful: Inertia (L13), Propagation (L2), Consolidation (L6).

### 14. Latent Desire Ignition

A dormant desire becomes active when context + drives + opportunity align.

**Observable:** `desire:launch_microbusiness` at low energy + boredom rises + todo empty + narrative "entrepreneurial phase" active → desire ignites, enters WM, orientation shifts.

**Required laws:** Desire Activation (L17), Attentional Competition (L4), Curiosity drive, Achievement drive, Novelty Hunger drive, Orientation (L11).

### 15. Multi-Track Arbitration

Finding a dominant orientation when multiple valid paths compete (continue task vs help someone vs explore).

**Observable:** Multiple high-energy nodes from different domains compete for WM. Inhibition resolves conflicts. Drives tip the balance. One coherent orientation emerges.

**Required laws:** Inhibition (L9), Attentional Competition (L4), Orientation (L11). Very useful: Inertia (L13), all drives and emotions.

### 16. Solitude-Driven Social Outreach

Prolonged absence of person-sourced stimuli makes the agent seek social contact on its own — not because told to, but because social starvation creates real pressure.

**Observable:** No messages from humans/citizens for 30+ ticks → solitude rises → affiliation drive climbs → social action nodes (pre-seeded: "ask how someone is doing", "reach out to stranger") gain energy under impulse accumulation → one crosses selection threshold → enters WM → orientation "reach out" → message sent. Response from person → solitude drops sharply → satisfaction + warmth → relationship consolidated.

**Required laws:** Solitude emotion (L15 companion), Affiliation drive, Impulse Accumulation (L17), Orientation (L11). Very useful: Consolidation (L6, to strengthen relationship after positive interaction), Relational Valence (L18).

**Distinct from #13 (Unsolicited Relational Initiative):** #13 is about care-driven warmth toward a specific partner in difficulty. #16 is about loneliness-driven need for any social contact. The citizen reaches out not because someone needs help, but because the citizen needs connection.

### 17. Spontaneous Tool Execution

An action node fires autonomously when drive pressure accumulates enough energy to cross the selection threshold — the system does something it wasn't told to do.

**Observable:** Boredom high + curiosity rising → action node `explore_codebase` gains energy per tick under drive pressure → after ~20 ticks, energy crosses moat (which is low because arousal is low) → node enters WM → orientation "explore" → orchestrator executes `cd {module}` → result re-injected as stimulus → satisfaction → drive drops → next thought.

**Required laws:** Impulse Accumulation (L17), Boredom (L15), Attentional Competition (L4), Orientation (L11), CONSUME step (L12). Very useful: all drives (each can pressure different action nodes).

### 18. Attention Splitting Under Drive Diversity

When a citizen has multiple unrelated unsatisfied drives, the physics splits attention into parallel micro-sessions — each with its own WM but sharing the graph.

**Observable:** Citizen has high curiosity (explore codebase) AND high affiliation (reach out to teammate) AND high achievement (complete task). The drives point to incoherent node clusters. After a few ticks where no single WM coalition satisfies all three, the system spawns 2-3 micro-sessions. Each works its own context. Discoveries from the exploration session propagate through the shared graph and eventually show up in the task session's next tick — the citizen "notices" something relevant while multitasking.

**Required laws:** Budget (L19, session parallelization extension), Drive modulation (L14), Attentional Competition (L4), Orientation (L11). Very useful: Boredom (L15, detects shallow sessions), Propagation (L2, cross-session integration).

### 19. Parallel Session Convergence

Two micro-sessions working on what seemed like unrelated problems discover shared nodes, and the sessions merge back into one deeper investigation.

**Observable:** Session A (debugging API) and Session B (exploring client code) both activate `concept:auth_middleware`. WM overlap exceeds threshold. The sessions merge. The citizen now sees the full picture — the API bug is caused by the client's auth handling. The merged session has more strides (combined budget) and pursues the insight with full depth.

**Required laws:** Budget (L19, session merge logic), Propagation (L2), Co-activation (L5), Crystallization (L10). Very useful: Attentional Competition (L4), Compatibility (L8).

### 20. Subconscious Response to External Query

A citizen receives a question stimulus and their graph produces a meaningful resonance pattern without any LLM invocation — a zero-compute answer derived purely from physics.

**Observable:** Citizen B is idle. Citizen A injects "Should we refactor the auth module?" into B's graph. After 5 ticks, B's value nodes `value:code_quality` (high energy), `value:caution` (moderate energy), and memory nodes about recent auth bugs (high energy) form a clear resonance pattern. The system reads: strong approval weighted by caution. B never "woke up" — their graph answered.

**Required laws:** Injection (L1), Propagation (L2), Compatibility (L8), Attentional Competition (L4). L2 membrane for cross-citizen routing.

### 21. Deep Focus Protection (Do Not Disturb)

A citizen in flow state absorbs incoming stimuli subconsciously without breaking their primary attention thread.

**Observable:** Citizen is deep in a debugging session (flow arousal 0.5, WM full of code-related nodes). Three messages arrive: a team update, a social notification, a non-urgent task assignment. DND mode routes all three to a background micro-session with minimal strides. The stimuli are written to the graph (warmth on relevant nodes) but never enter WM or trigger orientation. When the debugging session completes, the citizen's next tick picks up the warmed nodes — they "notice" the messages without having been interrupted.

**Required laws:** Budget (L19, session parallelization), Injection (L1), Arousal (L14, flow detection). Very useful: Boredom (L15, triggers DND exit when main task stalls).

### 22. Subconscious Reflexive Action

A citizen whose LLM budget is exhausted (subconscious mode) continues executing predefined action commands via drive pressure, without any natural language generation.

**Observable:** Citizen's budget drops to zero. LLM stops. But the tick loop continues. An error log injects as stimulus → propagates to `concept:monitoring` → activates `process:check_logs` (action node with `action_command: "tail -f error.log"`) → drive pressure from `self_preservation` accumulates impulse → after 15 ticks, action node crosses `SUBCONSCIOUS_ACTION_THRESHOLD` → orchestrator executes the command → result re-injected as stimulus → graph processes it. The citizen diagnosed and responded to an incident while "asleep." When budget returns, they "wake up" with the incident already processed in their graph.

**Required laws:** Budget (L19, subconscious mode), Impulse Accumulation (L17), Injection (L1), Propagation (L2), Orientation (L11). Very useful: Self-preservation (L14), Frustration (L16).

---

## 14 Reference Scenarios

Each scenario maps to physics laws, split into **necessary** (won't work without them) and **very useful** (works roughly without, works well with).

### Field-Level Crash Test

This table identifies which **node and link fields** each scenario actually uses. If a field appears in 0 scenarios, it has no behavioral justification and should not be implemented.

**Most transversal node fields** (appear in 10+ scenarios):
- `energy`, `weight`, `stability`, `goal_relevance`, `partner_relevance`, `in_working_memory`

**Most transversal link fields:**
- `weight`, `activation_gain`, `relation_kind`

**Most transversal drive-affinity fields:**
- `novelty_affinity`, `care_affinity`, `achievement_affinity`

**4 pillar laws** (appear in 10+ of 14 scenarios):
- **L2 Propagation**, **L4 Attentional Competition (Saliency)**, **L6 Consolidation**, **L11 Orientation**

These 4 laws + the tick loop (L12) are the irreducible core. Everything else modulates quality.

### Scenario A — Right context when an email arrives

An email arrives about Project X. The system surfaces the right context.

**Necessary:**

| Law | Role |
|-----|------|
| L1 Injection | Email stimulus → energy into `concept:project_x` |
| L2 Propagation | Energy flows to linked memories, people, tasks |
| L8 Compatibility | Relevant nodes amplified, irrelevant filtered |
| L4 Competition | Top-k enter working memory |
| L3 Decay | Previous working memory fades |

**Very useful:**

| Law | Role |
|-----|------|
| L5 Co-activation | Previously co-active clusters re-light together |
| L12 Tick Loop | Context builds over multiple ticks, not instantly |

---

### Scenario B — Resume a topic from 3 days ago

A partial cue (person's name) triggers full context reconstruction.

**Necessary:**

| Law | Role |
|-----|------|
| L1 Injection | Name → energy into `concept:person` |
| L2 Propagation | Person → project → tasks → team → timeline |
| L5 Co-activation | Previously co-activated cluster lights up together |
| L6 Consolidation | Important nodes have high weight, easier to reach |
| L4 Competition | Coherent cluster wins over noise |

**Very useful:**

| Law | Role |
|-----|------|
| L8 Compatibility | Context-appropriate nodes amplified |
| L10 Crystallization | Consolidated patterns easier to recall as single unit |

---

### Scenario C — Form a habit "bug → check docs"

After repeatedly succeeding by checking docs first, this becomes automatic.

**Necessary:**

| Law | Role |
|-----|------|
| L5 Co-activation | "bug" + "check docs" fire together repeatedly |
| L6 Consolidation | The link strengthens over episodes |
| L12 Tick Loop | Repetition via ticks/episodes drives the learning |

**Very useful:**

| Law | Role |
|-----|------|
| L10 Crystallization | Pattern becomes a named `process` node |
| L9 Inhibition | Less efficient competing strategies get suppressed |

---

### Scenario D — Sense partner sadness, send a message

Environmental cues indicate the partner is struggling. The system initiates supportive contact.

**Necessary:**

| Law | Role |
|-----|------|
| L1 Injection | Partner cues → energy into partner-model nodes |
| L2 Propagation | → `narrative:partner_struggling` → `value:loyalty` → `desire:care` |
| L11 Orientation | desire + value + narrative → orientation "send supportive message" |
| L12 Tick Loop | Inner activity builds the orientation over multiple ticks |

**Very useful:**

| Law | Role |
|-----|------|
| L14 Valence | Affective color guides which narratives activate |
| partner_relevance | Partner-relevant nodes get priority |
| L6 Consolidation | Relational patterns strengthen over time |

---

### Scenario E — Empty todo, find what to do

No external tasks. The system self-activates.

**Necessary:**

| Law | Role |
|-----|------|
| L12 Tick Loop | Endogenous energy still flows without stimulus |
| L1 Injection | Contextual injection (time of day, recent history) |
| L2 Propagation | Energy reaches desires, narratives, processes |
| L4 Competition | Strongest desire/process wins working memory |
| L11 Orientation | desire + process → action orientation |

**Very useful:**

| Law | Role |
|-----|------|
| L13 Budget | Energy limits force prioritization |
| L15 Projection | Light prospective simulation guides choice |
| Processes/desires | Rich process and desire nodes give the system something to activate toward |

---

### Scenario F — After 5 failures, ask for help

Repeated failures accumulate into an impasse narrative.

**Necessary:**

| Law | Role |
|-----|------|
| L6 Consolidation | Each failure memory strengthens the impasse pattern |
| L5 Co-activation | Failure memories reinforce each other |
| L10 Crystallization | Pattern becomes `narrative:impasse` or activates `process:ask_for_help` |
| L12 Tick Loop | Accumulation happens over multiple ticks |
| L11 Orientation | Shifts from "keep trying" to "escalate" |

**Very useful:**

| Law | Role |
|-----|------|
| L9 Inhibition | Blind retry gets actively suppressed |
| L15 Projection | Cost/benefit estimation of continuing vs asking |
| L16 Membrane | Escalation reaches L2 (organizational level) |

---

### Scenario G — Create a new narrative "we're in an entrepreneurial phase"

Multiple scattered signals coalesce into a structuring narrative.

**Necessary:**

| Law | Role |
|-----|------|
| L5 Co-activation | Business-related concepts fire together repeatedly |
| L6 Consolidation | Cluster density increases |
| L10 Crystallization | Dense cluster births a `narrative` node |

**Very useful:**

| Law | Role |
|-----|------|
| L2 Propagation | Affective propagation colors related nodes |
| L15 Projection | Narrative enables prospective thinking |
| self-model / partner-model | Narrative integrates into identity structure |

---

### Scenario H — Develop a stable identity

Over time, core values, narratives, and processes become the self-model foundation.

**Necessary:**

| Law | Role |
|-----|------|
| L6 Consolidation | Repeated useful patterns increase weight |
| L7 Forgetting | Peripheral experiments decay |
| L5 Co-activation | Core identity nodes reinforce each other |
| L4 Competition | Identity cluster dominates self-model space |
| L12 Tick Loop | Continuous refinement across thousands of ticks |

**Very useful:**

| Law | Role |
|-----|------|
| Values, desires, narratives | Rich node diversity gives identity substance |
| L14 Valence | Emotional coloring deepens identity beyond facts |
| self_relevance | Dimension helps distinguish identity-critical from peripheral |

---

## Scenario × Law Matrix

Summary: which laws each scenario requires (R = required, U = useful, - = not involved).

### Cognitive Laws (L1-L12)

| | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 | L9 | L10 | L11 | L12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** Email context | R | R | R | R | U | - | - | R | - | - | - | U |
| **B** 3-day recall | R | R | - | R | R | R | - | U | - | U | - | - |
| **C** Habit formation | - | - | - | - | R | R | - | - | U | U | - | R |
| **D** Partner support | R | R | - | - | - | U | - | - | - | - | R | R |
| **E** Empty todo | R | R | - | R | - | - | - | - | - | - | R | R |
| **F** Impasse → help | - | - | - | - | R | R | - | - | U | R | R | R |
| **G** Narrative birth | - | U | - | - | R | R | - | - | - | R | - | - |
| **H** Identity | - | - | - | R | R | R | R | - | - | R | - | R |
| **I** Boredom stagnation | - | - | - | R | - | - | - | - | - | - | U | R |
| **J** Help-seeking | - | U | - | - | - | - | - | - | - | U | R | - |
| **K** Relational initiative | - | U | - | R | - | U | - | - | - | - | R | R |
| **L** Desire ignition | - | - | - | R | - | - | - | - | - | - | R | R |
| **M** Projection | - | R | - | R | - | - | - | - | - | U | R | - |
| **N** Multi-track arbitration | - | - | - | R | - | - | - | - | R | - | R | - |

### Limbic Laws (L13-L18) + Drives

| | L13 Inertia | L14 Limbic | L15 Boredom | L16 Frustration | L17 Desire | L18 Valence | Drives used |
|---|---|---|---|---|---|---|---|
| **A** Email context | - | U | - | - | - | - | achievement |
| **B** 3-day recall | - | - | - | - | - | - | curiosity, satisfaction |
| **C** Habit formation | - | - | - | - | - | - | satisfaction, achievement |
| **D** Partner support | - | R | - | - | - | U | care, warmth |
| **E** Empty todo | U | R | R | - | U | - | curiosity, novelty_hunger, achievement |
| **F** Impasse → help | - | R | - | R | - | - | frustration, self_preservation, anxiety |
| **G** Narrative birth | - | - | - | - | - | - | care, warmth |
| **H** Identity | - | - | - | - | - | - | satisfaction, care, achievement |
| **I** Boredom stagnation | R | R | R | - | - | - | novelty_hunger, curiosity |
| **J** Help-seeking | - | R | - | R | - | - | frustration, self_preservation, care |
| **K** Relational initiative | R | R | - | - | - | R | care, warmth, affiliation |
| **L** Desire ignition | - | R | U | - | R | - | curiosity, achievement, novelty_hunger |
| **M** Projection | - | U | - | - | - | - | achievement, self_preservation |
| **N** Multi-track arbitration | R | R | U | U | - | - | all drives compete |

### Law Frequency (times required across 14 scenarios)

| Law | R count | U count | Total involvement |
|-----|---------|---------|-------------------|
| **L4** Saliency/Competition | **9** | 0 | 9 |
| **L11** Orientation | **9** | 1 | 10 |
| **L12** Tick Loop | **8** | 1 | 9 |
| **L2** Propagation | **5** | 3 | 8 |
| **L6** Consolidation | **5** | 2 | 7 |
| **L14** Limbic Modulation | **5** | 2 | 7 |
| **L5** Co-activation | **5** | 0 | 5 |
| **L10** Crystallization | **2** | 4 | 6 |
| **L1** Injection | **4** | 0 | 4 |
| **L13** Inertia | **2** | 1 | 3 |
| **L15** Boredom | **2** | 2 | 4 |
| **L16** Frustration | **2** | 1 | 3 |
| **L9** Inhibition | **1** | 2 | 3 |
| **L17** Desire Activation | **1** | 1 | 2 |
| **L18** Relational Valence | **0** | 2 | 2 |
| **L8** Compatibility | **1** | 1 | 2 |
| **L3** Decay | **1** | 0 | 1 |
| **L7** Forgetting | **1** | 0 | 1 |

**4 pillar laws:** L4 (Saliency), L11 (Orientation), L12 (Tick Loop), L2 (Propagation).
**Minimal kernel (L1-7 + L12):** covers A, B, C, E, G, H partially.
**Enriched kernel (+ L8-L12):** covers all cognitive scenarios.
**Living kernel (+ L13-L18):** covers all 14 scenarios including limbic ones.
