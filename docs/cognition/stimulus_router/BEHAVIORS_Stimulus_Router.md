# Stimulus Router — Behaviors: Observable Routing Effects

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
THIS:            BEHAVIORS_Stimulus_Router.md (you are here)
PATTERNS:        ./PATTERNS_Stimulus_Router.md
ALGORITHM:       ./ALGORITHM_Stimulus_Router.md
VALIDATION:      ./VALIDATION_Stimulus_Router.md
HEALTH:          ./HEALTH_Stimulus_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stimulus_Router.md
SYNC:            ./SYNC_Stimulus_Router.md

IMPL:            runtime/cognition/stimulus_router.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: External Events Produce Full-Energy Stimuli

**Why:** External events are the citizen's primary sensory input. Every message from the outside world must reach the cognitive engine with its full energy budget intact. Dropping or attenuating external events makes the citizen unresponsive.

```
GIVEN:  An IncomingEvent with source in ("telegram", "whatsapp", "discord", "mcp", "system")
WHEN:   StimulusRouter.route() is called with this event
THEN:   A Stimulus object is returned with energy_budget >= 1.0
AND:    The anti-loop self_stimulus_count is reset to 0 (external events break the self-loop counter)
```

### B2: Self-Stimuli Attenuate Geometrically

**Why:** When a citizen produces output, that output re-enters the graph as self-stimulus via the feedback injector. Without attenuation, the citizen would amplify its own signal indefinitely. The geometric decay (half-life of 3 self-stimuli) ensures self-reflection diminishes naturally.

```
GIVEN:  An IncomingEvent with source="self"
WHEN:   The citizen has already produced N self-stimuli since the last external event
THEN:   Energy is multiplied by 0.5^(N/3)
AND:    At N=3: energy is 50% of base
AND:    At N=6: energy is 25% of base
AND:    At N=9: energy is 12.5% of base
```

### B3: Refractory Period Blocks Immediate Self-Stimuli

**Why:** Immediately after a citizen takes an action, its own output should not immediately re-stimulate it. The 5-second refractory period creates a temporal gap that prevents tight action-perception loops.

```
GIVEN:  An IncomingEvent with source="self"
WHEN:   Less than 5.0 seconds have elapsed since the last recorded action
THEN:   The event is rejected (route() returns None)
AND:    No energy enters the graph
```

### B4: Duplicate Content Is Silently Dropped

**Why:** The same message can arrive through multiple paths (bridge relay, MCP echo, retry). Injecting it twice would double its energy impact and distort working memory competition. Hash-based dedup catches exact content matches within a sliding window.

```
GIVEN:  An IncomingEvent whose MD5 content hash (first 12 chars) matches a hash in the recent history
WHEN:   StimulusRouter.route() is called
THEN:   The event is rejected (route() returns None)
AND:    The dedup window holds the last 50 stimulus hashes
```

### B5: Social Sources Get Energy Boost

**Why:** Social stimuli (messages from humans, conversations) carry higher attentional weight than system events. The 1.2x energy multiplier ensures social signals compete more effectively for working memory slots, reflecting the biological priority of social cognition.

```
GIVEN:  An IncomingEvent where is_social=True OR source in ("telegram", "whatsapp", "discord")
WHEN:   StimulusRouter.route() processes the event
THEN:   The base energy is 1.2 (instead of 1.0)
AND:    The Stimulus.is_social flag is set to True
```

### B6: Failure Events Get Reduced Energy but Signal Status

**Why:** Failures should not dominate attention (low energy) but must be noticed (is_failure flag). The limbic system uses the failure flag to increment frustration, which in turn affects drive intensity and orientation. Energy 0.8 prevents failures from overwhelming working memory while the flag ensures emotional registration.

```
GIVEN:  An IncomingEvent with is_failure=True
WHEN:   StimulusRouter.route() processes the event
THEN:   The base energy is 0.8 (reduced from 1.0)
AND:    The Stimulus.is_failure flag is True
AND:    The tick runner's limbic update will increment frustration based on this flag
```

### B7: Concept Extraction Produces Node Targeting Hints

**Why:** Before embeddings are available, the router extracts keyword concepts from the event content. These concepts are attached to the Stimulus as `_concepts` for downstream node matching. This is a transitional mechanism — when per-citizen embedding functions are available, cosine similarity will replace keyword matching.

```
GIVEN:  An IncomingEvent with textual content
WHEN:   StimulusRouter.route() processes the event
THEN:   Up to 15 unique concepts are extracted (words > 3 chars, excluding stop words)
AND:    Concepts are stored on the Stimulus as stimulus._concepts
AND:    Concepts are deduplicated while preserving order
```

### B8: Feedback Injector Closes the Perception-Action Loop

**Why:** The feedback injector converts a citizen's LLM output into a self-stimulus that re-enters the graph. This closes the loop: message -> stimulus -> tick -> WM -> prompt -> LLM -> action -> feedback -> stimulus. The injector also creates episodic memory nodes and updates limbic state based on success/failure.

```
GIVEN:  A citizen has produced LLM output (action_output) with a success/failure flag
WHEN:   inject_post_action_feedback() is called
THEN:   router.record_action() is called (setting the refractory timestamp)
AND:    Episodic memory nodes are created for significant outputs (>= 30 chars)
AND:    The output is truncated to 500 chars and routed as source="self"
AND:    Limbic state is updated: success -> satisfaction +0.1, failure -> frustration +0.15
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Faithful signal transduction | External events must reach the engine with full energy |
| B2, B3 | O2: Anti-loop integrity | Self-stimuli are geometrically attenuated and refractory-gated |
| B5, B6 | O3: Source-aware energy budgeting | Social and failure events get differentiated energy levels |
| B4 | O4: Deduplication fidelity | Hash-based dedup prevents double injection |
| B5, B6 | O5: Metabolism readiness | Energy multipliers are isolated values that metabolism can modulate |

---

## INPUTS / OUTPUTS

### Primary Function: `StimulusRouter.route()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| event | IncomingEvent | Raw event from any source with content, source, citizen_handle, and classification flags |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stimulus | Optional[Stimulus] | Well-formed Stimulus for injection into the tick loop, or None if filtered |

**Side Effects:**

- Anti-loop gate state is updated (self_stimulus_count, recent_hashes)
- Dedup history is updated (content hash appended, oldest evicted if > 50)

### Feedback Function: `inject_post_action_feedback()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| state | CitizenCognitiveState | Citizen's cognitive state (mutated for memory creation and limbic updates) |
| router | StimulusRouter | Citizen's router instance (for anti-loop checking) |
| action_output | str | The text the citizen produced |
| success | bool | Whether the action succeeded |
| response_time_ms | Optional[float] | How long the action took (>30s triggers mild anxiety) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stimulus | Optional[Stimulus] | Self-stimulus if anti-loop allows it, None if filtered |

**Side Effects:**

- Episodic memory nodes created in state (up to 3 per session)
- Limbic drives/emotions updated (satisfaction, frustration, anxiety, achievement)
- router.record_action() called (sets refractory timestamp)

---

## EDGE CASES

### E1: Empty Content

```
GIVEN:  An IncomingEvent with content="" (empty string)
THEN:   The event still passes through the pipeline
AND:    Its MD5 hash is computed on the empty string (d41d8cd98f00)
AND:    extract_concepts() returns an empty list
AND:    The Stimulus is created with energy_budget based on source, but with no targeting concepts
```

### E2: Rapid-Fire External Events

```
GIVEN:  50+ external events arrive within 1 second
THEN:   All pass the anti-loop gate (source != "self" always passes)
AND:    Dedup catches any with identical content
AND:    Each unique event produces a Stimulus
AND:    The dedup window evicts oldest entries when exceeding 50
```

### E3: Self-Stimulus After Long External Silence

```
GIVEN:  A citizen has been producing self-stimuli for 20+ cycles with no external input
THEN:   The diminishing returns multiplier is 0.5^(20/3) = ~0.01 (nearly zero energy)
AND:    At this level, self-stimuli effectively stop entering working memory
AND:    The next external event resets self_stimulus_count to 0, restoring full sensitivity
```

### E4: Feedback Injector With Very Long Output

```
GIVEN:  A citizen produces action_output of 5000+ characters
THEN:   The feedback injector truncates to first 250 chars + " [...] " + last 200 chars
AND:    The truncated content (500 chars max) is routed as self-stimulus
AND:    Episodic memories are created from significant lines in the FULL output
```

---

## ANTI-BEHAVIORS

### A1: Feedback Amplification Loop

```
GIVEN:   A citizen produces output that re-enters as self-stimulus
WHEN:    The self-stimulus triggers another LLM call that produces similar output
MUST NOT: The cycle continue indefinitely with constant or increasing energy
INSTEAD:  Energy decreases geometrically (0.5^(n/3)) and the novelty gate rejects repeated content hashes
```

### A2: Duplicate Energy Stacking

```
GIVEN:   The same message content arrives twice (e.g., Telegram retry + MCP echo)
WHEN:    Both events reach the router within the dedup window (50 items)
MUST NOT: Both events inject energy into the graph
INSTEAD:  The second event is silently dropped by hash-based dedup
```

### A3: Self-Stimulus Bypassing Refractory Period

```
GIVEN:   A citizen just completed an action (record_action() called)
WHEN:    A self-stimulus arrives within 5 seconds
MUST NOT: The self-stimulus pass through the anti-loop gate
INSTEAD:  The gate rejects it (returns allowed=False, energy_mult=0.0)
```

### A4: System Events Overwhelming Social Signals

```
GIVEN:   Multiple system events and one social message arrive in the same tick window
WHEN:    The router processes all events
MUST NOT: System events (energy 1.0) systematically outcompete social events
INSTEAD:  Social events get 1.2x energy boost, giving them a competitive advantage for working memory
```
