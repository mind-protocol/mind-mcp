# VALIDATION — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** DESIGNING (v0.1)

---

## Structural Invariants

These must hold at all times, by construction.

### V1: Node Type Integrity

Every node has exactly one cognitive type from {memory, concept, narrative, value, process, desire, state}.

```
MATCH (n) WHERE n.cognitive_type IS NULL RETURN count(n)
→ 0
```

### V2: Minimum Dimensions

Every node carries: weight, energy, stability, recency, self_relevance, partner_relevance. No nulls.

### V3: Link Type Integrity

Every link has `relation_kind` from the 14 defined types (12 cognitive + 2 crystallization: `contains`, `abstracts`). No untyped links.

### V4: Working Memory Bounded

Working memory contains at most `WM_SIZE` (7) nodes at any tick.

```
|working_memory| <= WM_SIZE at all times
```

### V5: Energy Non-negative

No node or link has negative energy. Inhibition reduces but never inverts.

```
∀ node: node.energy >= 0
∀ link: link.energy >= 0
```

### V6: Weight Non-negative

No node or link has negative weight.

---

## Dynamic Invariants

These must hold after sufficient ticks (100+).

### V7: Decay Prevents Saturation

After 1000 ticks, no node has energy above 10x its injection rate. Decay must outpace accumulation for idle nodes.

```
∀ node not receiving continuous injection:
  node.energy < 10 * avg_injection_rate after 100 ticks without stimulus
```

### V8: Working Memory Turnover

Working memory contents change at least once every 50 ticks (no frozen consciousness).

```
jaccard(WM at tick t, WM at tick t+50) < 1.0
```

### V9: Consolidation Gradient

After 500 ticks, identity nodes (values, core narratives) have higher average weight than peripheral memories.

```
avg_weight(values + core_narratives) > avg_weight(peripheral_memories)
```

### V10: Forgetting Works

After 1000 ticks, at least 10% of nodes created in tick 0-100 have gone dormant (weight < MIN_WEIGHT).

### V11: No Energy Divergence

Total system energy stays bounded. No exponential growth.

```
total_energy(tick t) < C * total_energy(tick 0) for reasonable C
```

### V12: No Energy Death

System doesn't collapse to zero energy if stimuli continue.

```
If stimuli continue: total_energy(tick t) > epsilon for all t
```

### V13: Crystallization Produces Nodes

After 1000 ticks with repeated patterns, at least one new `process` or `narrative` node has been crystallized.

### V14: Orientation Stability

An orientation that reaches output must have been stable for at least `ORIENTATION_STABILITY_TICKS` consecutive ticks.

---

## Scenario-Based Validation

Each scenario from BEHAVIORS must be verifiable.

### Test A: Email Context Reactivation

**Setup:** Pre-load graph with Project X context (concept + 5 memories + 3 people). Inject "email about Project X" stimulus.

**Assert within 3 ticks:**
- `concept:project_x` is in working memory
- At least 2 related memories are in working memory
- At least 1 related person is in working memory
- Previous working memory contents have decayed

### Test B: 3-Day-Old Topic Recall

**Setup:** Activate a context cluster at tick 0. Run 500 ticks of other activity. Then inject partial cue (person name).

**Assert within 5 ticks:**
- At least 3 nodes from the original cluster reactivate
- The cluster is more coherent than random noise (coherence > 0.5)

### Test C: Habit Formation

**Setup:** Simulate 15 episodes of "bug detected → check docs → bug fixed" sequence.

**Assert:**
- A `process` node has crystallized
- It has `follows_process` links from bug-related concepts
- Its weight > average node weight

### Test D: Partner Support Initiative

**Setup:** Inject signals indicating partner sadness. Ensure `value:loyalty` and `desire:care` exist.

**Assert within 10 ticks:**
- Working memory contains partner-related nodes
- Orientation shifts to "supportive"
- If sustained, an output event is emitted

### Test E: Self-Directed Activity (Empty Todo)

**Setup:** No external stimuli. Desires and processes exist in graph.

**Assert within 20 ticks:**
- Working memory is NOT empty (endogenous activity)
- At least one desire or process enters working memory
- An orientation forms

### Test F: Impasse → Escalation

**Setup:** Inject 5 consecutive failure events for the same task.

**Assert:**
- `narrative:impasse` crystallizes or strengthens
- `process:ask_for_help` activates
- Orientation shifts from "retry" to "escalate"

### Test G: Narrative Crystallization

**Setup:** Inject 20 business-related events over 200 ticks.

**Assert:**
- A new `narrative` node containing the entrepreneurial theme crystallizes
- It has links to the relevant concept and memory nodes

### Test H: Identity Stability

**Setup:** Run 2000 ticks with mixed activity.

**Assert:**
- Self-model sub-graph has higher average weight than non-self nodes
- Core values have stability > 0.7
- At least one value has been reinforced (weight increased)
- At least one peripheral experiment has decayed

### Test I: Boredom Drives Exploration

**Setup:** Run 30 ticks with identical stimulus (same email, same context). No novelty.

**Assert:**
- `boredom` emotion rises above 0.5
- Working memory starts shifting toward novel/peripheral nodes
- Orientation shifts from current task toward "explore" or "change activity"
- Inertia of the stale focus erodes

### Test J: Frustration Drives Escalation

**Setup:** Inject 5 failure events for the same task in 10 ticks. No resolution.

**Assert:**
- `frustration` emotion rises above 0.5
- Inhibition of the failed path increases
- Drive balance determines outcome:
  - If `achievement` > `self_preservation`: stubbornness (retry variant)
  - If `affiliation` high: help-seeking
  - If `self_preservation` high: avoidance/workaround
- The system does NOT retry identically for the 6th time

### Test K: Latent Desire Ignites

**Setup:** Create a `desire:launch_microbusiness` with low energy (0.1). Run 50 ticks of unrelated activity. Then: set boredom high, todo empty, active narrative "entrepreneurial phase."

**Assert:**
- The desire's energy jumps (ignition boost)
- The desire enters working memory
- Orientation shifts toward the desire

### Test L: Relational Valence Modulates Cognition

**Setup:** Create two `concept` nodes (person_A with high affinity, person_B with high friction). Inject stimulus mentioning both.

**Assert:**
- person_A's energy is amplified by affinity
- person_B's energy is dampened by friction (or frustration increases faster)
- Working memory preferentially includes person_A over person_B at equal stimulus

### Test M: Inertia Holds Focus

**Setup:** System is deeply focused on a task (working memory stable for 5 ticks). Inject a weak distraction stimulus.

**Assert:**
- Working memory does NOT shift to distraction
- Inertia keeps current focus intact
- Only a strong stimulus (energy > inertia_bonus * current WM energy) can dislodge

---

## Limbic Invariants

### V15: Drive Bounds

All drives stay in [0, 1]. No drive diverges.

```
∀ drive: 0 <= drive.intensity <= 1 at all times
```

### V16: Boredom Responds to Stagnation

If WM is identical for `STAGNATION_WINDOW` ticks, boredom must be > 0.3.

### V17: Frustration Responds to Failure

If `FAILURE_WINDOW` consecutive failures, frustration must be > 0.3.

### V18: Inertia Is Finite

No WM configuration persists for more than 200 ticks without external reinforcement or active desire.

### V19: Relational Valence Evolves

After 500 ticks with varied interactions, at least one link has changed affinity by > 0.1.

### V20: Desire Ignition Occurs

After 1000 ticks, at least one latent desire has ignited (crossed activation threshold).

### V21: Drive Diversity

After 500 ticks, no single drive has intensity > 0.8 for more than 20 consecutive ticks (drives must compete and regulate each other).

---

## Anti-Patterns to Detect

| Anti-Pattern | Detection | Response |
|-------------|-----------|----------|
| **Christmas Tree** | >50% of nodes above activation threshold | Increase decay rate |
| **Dead Graph** | <5% of nodes above activation threshold | Check injection, reduce decay |
| **Frozen WM** | Same WM for 100+ ticks | Check competition and boredom |
| **Runaway Cascade** | Total energy doubles in <10 ticks | Cap per-tick flow, check propagation limits |
| **Identity Erosion** | Core value weights declining | Reduce identity decay multiplier |
| **Compulsive Crystallization** | >10 new nodes per 100 ticks | Raise crystallization thresholds |
| **Never Crystallizes** | 0 new nodes after 1000 ticks | Lower thresholds, check co-activation detection |
| **Mono-orientation** | Same orientation for 500+ ticks | Check inhibition, desire diversity, boredom |
| **Eternal Boredom** | Boredom > 0.7 for 100+ ticks | Check injection, novelty sources are starved |
| **Eternal Frustration** | Frustration > 0.7 for 100+ ticks | Check escalation paths, rest_regulation |
| **Affective Flatline** | All drives near 0.5, no emotion > 0.3 | Check limbic update, stimuli may be too uniform |
| **Obsessive Focus** | WM identical for 200+ ticks | Inertia too strong, boredom not eroding fast enough |
| **Butterfly Agent** | WM changes completely every 2-3 ticks | Inertia too weak, drives too volatile |
