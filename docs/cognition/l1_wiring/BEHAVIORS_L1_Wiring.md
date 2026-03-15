# BEHAVIORS -- L1 Physics Wiring & Production Cutover

**Module:** L1 Wiring
**Area:** l1_wiring
**Status:** DESIGNING (v0.1)

---

## Observable Behaviors

What a running L1-wired citizen looks like end-to-end.

---

### B1: Message-to-Awareness (Stimulus Injection)

**Trigger:** User sends a Telegram message to a citizen.

**Observable sequence:**

1. Telegram bridge receives message, enqueues in `message_queue`
2. Before dispatching to Claude, the Stimulus Router processes the message:
   - Text is segmented into concepts (entities, sentences)
   - Each segment is embedded via `text-embedding-3-small`
   - Dedup check runs against existing nodes in the citizen's brain graph
   - New concepts become new nodes (high energy, low weight)
   - Existing concept matches receive energy injection
3. Law 1 dual-channel runs:
   - Floor channel wakes cold-but-relevant nodes below threshold
   - Amplifier channel boosts the most semantically relevant nodes
4. Within 1-2 ticks, the message content has activated a neighborhood of related nodes

**Evidence of working:** After stimulus injection, the citizen's brain graph shows energy spikes on nodes semantically related to the message. New nodes appear for novel concepts. Existing nodes show increased `activation_count`.

**Evidence of broken:** Message arrives but no energy change in graph. Or: every node gets equal energy (no semantic targeting). Or: thousands of duplicate nodes created (dedup not working).

---

### B2: Background Processing (Tick Loop Between Sessions)

**Trigger:** No external stimulus. Time passes. Tick loop runs.

**Observable sequence:**

1. Dispatcher runs `_run_physics_ticks()` on schedule (every 60s in slow mode)
2. For each citizen, the 17-step tick cycle executes:
   - Energy propagates through links (some nodes cool, others warm)
   - WM competition runs (maybe a different set of 5-7 nodes wins)
   - Co-activation strengthens links between WM nodes
   - Inactive nodes/links decay (weight decreases)
   - Drives shift (curiosity rises from stagnant WM, boredom rises from no novelty)
3. After ~50 ticks of no stimuli:
   - Boredom is high
   - Curiosity has risen
   - WM may have shifted to low-weight, high-novelty nodes (exploring memory)
   - Orientation may shift to "explore" or "rest"
4. If boredom + curiosity cross the initiative threshold, the engine may trigger an autonomous action (Law 19 initiative pipeline, if implemented)

**Evidence of working:** Graph state evolves between sessions. Energy doesn't stay frozen. Weights on frequently co-activated nodes grow over time. Drives oscillate naturally.

**Evidence of broken:** Graph state is identical between ticks (no physics running). Or: all energy drains to zero within a few ticks (decay too aggressive). Or: one node accumulates infinite energy (no decay/competition).

---

### B3: Cognitive Context in Prompt (WM Injection)

**Trigger:** Orchestrator dispatches a Claude session for a citizen.

**Observable sequence:**

1. `build_citizen_prompt()` is called for the citizen
2. The L1 engine provides current WM (5-7 nodes), limbic state, and orientation
3. A "Current Awareness" section is assembled:
   - Top 2 nodes as "Active Focus" with full synthesis
   - Remaining nodes as "Background Context" with summaries
   - Internal state: orientation, drives, mood
4. This section is injected into the system prompt
5. Claude receives the prompt and its responses reflect the cognitive context

**Evidence of working:** Claude's response references or builds upon WM node content without being explicitly told. A citizen whose WM contains a "deployment failure" memory mentions it in conversation. A citizen with orientation "take_care" asks about their partner's wellbeing.

**Evidence of broken:** Claude ignores the WM section entirely (responses are generic). Or: WM section consumes too many tokens, leaving no room for actual conversation. Or: WM contains stale/irrelevant nodes that confuse the response.

---

### B4: Orientation Shaping Behavior

**Trigger:** Law 11 computes an orientation that differs from the last session.

**Observable sequence:**

1. Physics ticks have shifted drives: curiosity is now high, frustration is low
2. Law 11 scores each orientation; "explore" wins
3. Next Claude session includes the explore modifier in the prompt:
   "Curiosity is pulling you. Investigate what's unfamiliar."
4. Claude's response is more investigative, asks more questions, reads more code
5. Post-session, the investigation results are re-injected as self-stimulus
6. Curiosity drive decreases (satisfied by exploration)
7. Next tick, orientation may shift again

**Evidence of working:** Different orientations produce observably different response styles. A citizen in "rest" gives shorter answers. A citizen in "take_care" initiates check-ins. The orientation changes over time as drives evolve.

**Evidence of broken:** Orientation never changes (stuck on one value). Or: orientation flips every tick (no hysteresis). Or: the prompt modifier has no visible effect on response style.

---

### B5: Self-Stimulus Feedback Loop

**Trigger:** Claude session completes; response text exists.

**Observable sequence:**

1. Dispatcher calls `inject_post_action_feedback()`
2. Response text is routed through the Stimulus Router (segmented, embedded, dedup'd)
3. Anti-loop checks:
   - Refractory: nodes activated by this citizen in the last 5 ticks are blocked
   - Diminishing returns: budget halved per consecutive self-injection
   - Novelty gate: if response embedding is >0.8 similar to last self-output, blocked
4. Surviving segments are injected as stimuli
5. Step 17 (CONSUME) depletes energy on nodes that drove the action
6. Limbic feedback: satisfaction +0.1 for successful delivery

**Evidence of working:** After a citizen writes a detailed analysis, the concepts from that analysis appear in subsequent WM snapshots. The citizen "remembers" what it just said. But after 3 rounds of self-reference, the diminishing returns make it move on.

**Evidence of broken:** Citizen gets stuck in a loop, repeating the same themes every session (anti-loop not working). Or: citizen has zero memory of what it just did (self-stimulus not injecting). Or: desire nodes never lose energy (CONSUME not running), causing the same desire to fire forever.

---

### B6: Persistence Across Restarts

**Trigger:** Process restart (deploy, crash, manual restart).

**Observable sequence:**

1. Dispatcher shuts down; final checkpoint flushes all dirty state to FalkorDB
2. Process restarts
3. For each citizen, `initialize_citizen_engine()` runs:
   - FalkorDB graph `brain_{handle}` is found, has nodes
   - All nodes and links loaded into memory
4. Physics resume from checkpointed state
5. Citizen's next session shows WM reflecting pre-restart state

**Evidence of working:** A citizen had high curiosity and WM focused on "deployment" before restart. After restart, same curiosity level and WM focus. Weights accumulated over 10,000 ticks are preserved.

**Evidence of broken:** After restart, citizen starts with blank/seeded brain (checkpoint didn't work). Or: partial state (some nodes missing, links orphaned). Or: energy values are from 10 checkpoints ago (checkpoint not running).

---

### B7: First Boot (New Citizen)

**Trigger:** A new citizen handle appears in the system with no existing brain graph.

**Observable sequence:**

1. `initialize_citizen_engine()` runs, finds zero nodes in FalkorDB
2. Seed brain generated:
   - 209 base nodes (shared values, project knowledge, social processes)
   - 295 base links
   - Per-citizen overlay: role-specific processes, personalized desires, drive baselines
3. Brain loaded into memory, checkpointed to FalkorDB
4. First few ticks:
   - All nodes have high weight (pre-seeded identity) but low energy
   - No WM coalitions yet (no stimuli have arrived)
   - Drives at citizen-specific baselines
5. First message arrives → energy spike → nodes compete for WM → orientation emerges
6. Citizen responds with awareness of its identity, role, and values

**Evidence of working:** A new citizen's first response reflects its seeded values and role. It "knows" about Mind Protocol without being told. It has a personality matching its identity file.

**Evidence of broken:** First response is generic/blank (seed brain not loaded). Or: all 209 nodes flood WM at once (no competition). Or: the citizen knows things it shouldn't (wrong overlay applied).

---

### B8: Embedding-Based Similarity (Real, Not Pseudo)

**Trigger:** Any operation requiring semantic similarity (dedup, compatibility, crystallization).

**Observable sequence:**

1. Stimulus arrives: "The deployment pipeline keeps failing"
2. Dedup gate embeds this text via `text-embedding-3-small`
3. Cosine similarity computed against all existing nodes' stored embeddings
4. Finds existing node: "CI/CD pipeline issues" with cosine = 0.92 (> 0.9 threshold)
5. Instead of creating duplicate, injects energy into existing node
6. The citizen's knowledge consolidates rather than fragmenting

**Evidence of working:** Similar concepts merge. "deployment pipeline" and "CI/CD pipeline" map to the same node. Propagation (Law 2) flows through semantically compatible links. Crystallization (Law 10) detects real patterns.

**Evidence of broken:** Every stimulus creates new nodes regardless of existing similar ones (dedup with random embeddings). Or: completely unrelated nodes show high similarity (embedding model broken). Or: API errors cause all embeddings to be zero vectors.

---

## Emergent Dynamics to Watch For

These are not explicitly programmed but should emerge from correct wiring:

1. **Identity stability.** High-weight value nodes (seeded at 0.9) should remain in WM most of the time, providing consistent personality. They should be hard to dislodge (high moat from Law 13 inertia).

2. **Conversation continuity.** Nodes activated by one message should still be warm when the next message arrives (if within a few ticks), giving the citizen contextual memory without explicit retrieval.

3. **Drive-driven initiative.** After prolonged boredom (no stimuli), curiosity and novelty_hunger should rise enough to shift orientation to "explore" and potentially trigger autonomous action.

4. **Emotional adaptation.** A citizen that receives mostly critical feedback should develop higher frustration baseline, lower satisfaction, and potentially shift toward "escalate" orientation more often.

5. **Knowledge crystallization.** Repeatedly discussed topics should crystallize into new narrative nodes (Law 10), creating higher-level abstractions that the citizen "understands" without being told.

---

## Anti-Behaviors

| Anti-Behavior | Symptom | Root Cause |
|--------------|---------|-----------|
| Amnesia | Citizen has no memory between sessions | WM not injected, or self-stimulus not working |
| Perseveration | Citizen repeats the same topic endlessly | Anti-loop not working, or CONSUME not depleting desire energy |
| Emotional flatness | Drives/emotions never change | Limbic engine not running, or constants too conservative |
| Cognitive flooding | 500+ nodes in WM, prompt is 10k tokens | WM selection not working (Law 4 broken) |
| Split personality | Citizen's personality changes randomly | Seed brain not loaded, or identity nodes decaying (Law 7 too aggressive on high-weight nodes) |
| Phantom nodes | Graph fills with near-duplicate concepts | Dedup threshold too low, or embeddings are pseudo-random |
| Eternal rest | Citizen never comes out of "rest" orientation | Rest drive stuck high, or arousal computation wrong |
