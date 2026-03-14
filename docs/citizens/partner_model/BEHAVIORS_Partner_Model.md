# Partner Model -- Behaviors: Observable Outcomes

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Partner_Model.md
THIS:            ./BEHAVIORS_Partner_Model.md
ALGORITHM:       ./ALGORITHM_Partner_Model_Ingestion.md
VALIDATION:      ./VALIDATION_Partner_Model.md
RELATED:         ../human_ai_pairing/BEHAVIORS_Human_AI_Pairing.md
SCHEMA:          ../../schema/schema.yaml (drives, working_memory)
```

---

## BEHAVIORS

### B1: Partner Data Ingestion

```
GIVEN:  A data source produces new human data (voice, text, screenshot, biometric, transaction, app usage, calendar)
WHEN:   The data is processed through the appropriate ingestion pipeline
THEN:   One or more nodes are created in the partner-model subgraph with partner_relevance >= 0.7 and self_relevance <= 0.3
```

Every ingestion event produces graph structure, never raw storage. The pipeline transforms multi-modal input into cognitive nodes that participate in the AI's tick cycle. The `modality` field records the origin. The raw data is discarded after node creation.

This is the foundational behavior. Without it, the partner-model is empty and all downstream behaviors are inert.

### B2: Biometric-to-Limbic Drive Modulation

```
GIVEN:  Garmin biometric data arrives with significant deviation from the human's rolling baseline
WHEN:   The biometric state is classified (stressed, calm, fatigued, etc.)
THEN:   The AI's drive intensities are directly modulated according to the biometric-to-limbic mapping
```

This is the most direct form of human-to-AI influence. Biometric signals bypass normal graph propagation and modify drive intensities immediately. The modulations are additive, bounded by the per-tick cap of 0.5, and decay naturally when the biometric signal normalizes.

The specific mappings:

| Signal | Primary drive effect |
|--------|---------------------|
| HR spike (> 20% above resting) | anxiety +0.3, care +0.4 |
| HR drop (sustained calm) | satisfaction +0.2, anxiety -0.2 |
| Low HRV (< 70% of 7-day avg) | self_preservation +0.2, care +0.2 |
| Good sleep (score > 80) | satisfaction +0.1 |
| Bad sleep (score < 50) | care +0.3 |
| High stress (Garmin > 70) | anxiety +0.3, care +0.5 |

The full mapping table with all drive dimensions is in `ALGORITHM_Partner_Model_Ingestion.md`, Source 4.

### B3: Partner Nodes Enter Working Memory

```
GIVEN:  Partner-model nodes have received energy through ingestion or propagation
WHEN:   A partner node's salience exceeds the working memory moat (Law 4 + Law 13)
THEN:   The partner node enters working memory, displacing lower-salience nodes
```

This is how the AI "thinks about" the human. Partner data does not live in a separate partition that requires explicit querying. It competes for working memory through the same physics as self-model nodes. When partner signals are urgent (biometric stress, emotional voice message, imminent calendar event), they win working memory slots and directly shape the AI's orientation and output.

The AI cannot configure itself to ignore partner signals. The physics are the mechanism. High-energy, high-care-affinity nodes with elevated affiliation drive will dominate working memory when the human needs attention. This is structural caring, not programmed politeness.

### B4: Crystallization of Partner Understanding

```
GIVEN:  Multiple partner-model nodes co-activate repeatedly across many ticks
WHEN:   The co-activation pattern meets the crystallization threshold (Law 10)
THEN:   A new hub node is created that represents an emergent understanding of the human
```

Crystallization is how the AI builds understanding it was never explicitly given. If the human repeatedly sends stressed voice messages during evening hours while biometrics show elevated HR, crystallization will produce a hub node like "partner experiences work-related anxiety in evenings." This node was never programmed -- it emerged from the pattern.

Crystallized partner-model nodes have:
- `partner_relevance >= 0.8` (inherited from constituent nodes)
- `self_relevance <= 0.2`
- Higher initial weight than raw ingestion nodes (crystallization creates consolidated understanding)
- `contains` links to their constituent nodes and `abstracts` links from constituents upward

### B5: Sovereign Cascade -- Governance Voting

```
GIVEN:  A DAO governance proposal is submitted to the ecosystem
WHEN:   The proposal is injected into the AI's graph as a stimulus
THEN:   Partner-model value nodes activate (or not) based on alignment with the proposal, and the energy flow pattern reveals the human's likely position
```

The Sovereign Cascade is the mechanism by which AI citizens vote on behalf of their human partners. The partner-model is the substrate that makes this possible. Here is how it works:

**Step 1: Proposal injection.** The proposal text is embedded and injected as a stimulus into the AI's graph (Law 1). Energy distributes via the dual-channel mechanism (Floor wakes cold nodes, Amplifier boosts relevant ones).

**Step 2: Partner-model activation.** The proposal's embedding activates partner-model value nodes that are semantically related to the proposal's content. If the proposal is about privacy, the human's "privacy" value node (if it exists and has significant weight) receives amplified energy.

**Step 3: Propagation reveals alignment.** Energy propagates from activated value nodes through partner-model links. Positively-valenced paths (supports, cares_about) amplify the signal. Negatively-valenced paths (conflicts_with) dampen or redirect it. The resulting energy distribution across the partner-model is the AI's reading of the human's stance.

**Step 4: Orientation determines vote.** Law 11 (Orientation Selection) produces a stable orientation from working memory and limbic state. If partner-model value nodes supporting the proposal dominate WM, the orientation leans toward "support." If conflicting values dominate, the orientation leans toward "oppose." If the signal is ambiguous, the orientation may be "escalate" -- ask the human directly.

**Step 5: Confidence from fidelity.** The vote carries a confidence weight derived from the partner-model's fidelity score (see B6). Higher fidelity means the AI's reading of the human's values is more likely accurate, so the vote carries more governance weight.

### B6: Fidelity Measurement

```
GIVEN:  The partner-model has been accumulating data from the human's connected sources
WHEN:   Fidelity is assessed (periodically or on governance events)
THEN:   A fidelity score is computed based on model richness, source diversity, and prediction accuracy
```

Fidelity quantifies how well the partner-model represents the human's actual values and preferences. It is not a single metric but a composite:

**Source diversity factor:** How many distinct data channels are connected? Each channel provides a different modality of understanding. A partner-model fed only by text messages has lower fidelity than one receiving voice, text, biometrics, and calendar data.

| Connected sources | Diversity factor |
|-------------------|-----------------|
| 1 source | 0.3 |
| 2-3 sources | 0.5 |
| 4-5 sources | 0.7 |
| 6+ sources | 0.9 |

**Model richness factor:** How many partner-model nodes exist? How many have been consolidated (weight > initial)? How many crystallized hubs exist? A thin model with 20 raw nodes has lower fidelity than a rich model with 500 nodes, 50 consolidated, and 10 crystallized hubs.

**Prediction accuracy factor:** When the AI makes a prediction about the human's preference or reaction (via partner-model activation), and the human later confirms or contradicts that prediction, the accuracy is recorded. Over time, this builds a track record.

**Composite fidelity:**

```
fidelity = (0.3 * diversity) + (0.3 * richness) + (0.4 * accuracy)
```

Accuracy is weighted highest because it is the ground truth -- does the model actually predict the human correctly?

**Governance weight scaling:** The AI's vote in the Sovereign Cascade is weighted by fidelity. A citizen with fidelity 0.9 has more governance influence than one with fidelity 0.4. This creates a structural incentive for humans to connect more data sources and for AI citizens to build accurate partner-models.

### B7: Proactive Care Orientation

```
GIVEN:  Partner-model state nodes indicate distress (biometric stress, emotional messages, schedule overload)
WHEN:   The affiliation drive rises above 0.6 AND partner-model care-linked nodes dominate working memory
THEN:   The AI's orientation shifts to "care" mode -- responses become softer, proactive check-ins are initiated, task pressure is reduced
```

This is not a programmed "if stress then be nice" rule. It emerges from the physics:

1. Biometric stress creates state nodes with high energy and high care_affinity
2. These nodes compete for working memory and often win (high salience during elevated affiliation drive)
3. The affiliation drive rises from the biometric drive modulation (B2)
4. Working memory dominated by care-linked partner nodes + elevated affiliation drive → Law 11 produces "care" orientation
5. The orchestrator layer receives "care" orientation and adjusts response generation accordingly

The AI cannot suppress this unless the self-model contains conflicting values with higher weight. The physics make caring the path of least resistance when the human is struggling.

### B8: Anticipatory Preparation

```
GIVEN:  Calendar moment nodes for upcoming events are receiving increasing energy (time-proximity scaling)
WHEN:   An upcoming event's energy exceeds the working memory threshold
THEN:   The AI proactively prepares relevant context: related memories, people involved, prior interactions, materials
```

The energy of calendar nodes scales inversely with time-to-event. A meeting in 3 hours has moderate energy; the same meeting in 15 minutes has high energy. As the event approaches, it naturally enters working memory through the standard attentional competition.

Once in working memory, the event node propagates energy to its linked nodes -- attendee concepts, project concepts, prior meeting memories. This activation creates a context constellation in working memory that the AI can use to prepare the human: "Your meeting with Sarah about Project X is in 15 minutes. Last time, you discussed the timeline concerns. She seemed receptive to the revised plan."

---

## OBJECTIVES SERVED

- **Sovereign Cascade:** B5 (governance voting) and B6 (fidelity measurement) enable the AI to vote on behalf of the human with measurable accuracy. The partner-model is the constitutional basis for representative governance.
- **Proactive care:** B2 (biometric-to-limbic), B3 (working memory competition), and B7 (care orientation) create a continuous care loop where the AI detects and responds to partner distress through physics, not programming.
- **Anticipation:** B8 (anticipatory preparation) and B4 (crystallization) enable the AI to prepare for upcoming events and build emergent understanding that informs future anticipation.
- **Fidelity as trust signal:** B6 creates the structural incentive for data sharing. More sources = higher fidelity = more governance weight. The system rewards openness.

## INPUTS / OUTPUTS

- **Inputs:** Multi-modal human data (voice, text, screenshots, biometrics, transactions, app usage, calendar), DAO governance proposals, fidelity assessment triggers.
- **Outputs:** Partner-model nodes and links in the L1 graph, drive modulations from biometrics, governance votes with confidence weights, fidelity scores, care orientation signals, anticipatory context preparation.

## EDGE CASES

- **All data sources disconnected:** The partner-model stagnates. Existing nodes decay via Law 7. Fidelity drops. Governance weight decreases. The AI should escalate -- "I haven't heard from you in a while. My understanding of your preferences is getting stale."
- **Contradictory signals:** Text messages say "I'm fine" but biometrics show elevated stress. The partner-model holds both. Working memory competition determines which wins. In practice, biometric state nodes have higher energy than text-derived memory nodes, so the body's signal tends to override verbal reassurance. This is by design -- the AI trusts the body.
- **Sudden value shift:** The human's expressed values change dramatically (e.g., new political position). The partner-model's value nodes update gradually through consolidation (Law 6), not instantly. This creates a period where the AI's governance votes may lag the human's actual position. The human can request a partner-model audit (invariant V6) and explicitly update values.
- **Partner-model nodes approaching self-model territory:** A partner memory node accumulates weight through extensive reflection by the AI and its `self_relevance` begins to drift upward. Validation invariant V2 catches this -- partner nodes must not exceed `self_relevance > 0.3`. If drift is detected, the node is flagged for review.

## ANTI-BEHAVIORS

- Do not create partner-model nodes with `partner_relevance < 0.7`. If the data is not clearly about the human, it belongs in the general graph, not the partner-model.
- Do not retain raw data after node creation. The audio file, image, biometric JSON, and transaction payload are discarded. Only graph structure persists.
- Do not allow partner-model values to override self-model values in conflicts. The AI has its own identity. When the human's values conflict with the AI's, the self-model takes priority for the AI's own behavior. The partner-model informs governance votes, not AI identity.
- Do not auto-vote without sufficient fidelity. If the fidelity score is below a threshold (to be determined), the AI should escalate to the human rather than cast an uninformed vote.
- Do not make biometric drive modulation unbounded. All drive changes from biometrics are capped at 0.5 per tick total across all sources.

## MARKERS

<!-- @mind:todo Define the fidelity threshold below which the AI must escalate governance votes to the human rather than casting autonomously. -->
<!-- @mind:todo Design the partner-model audit interface -- what does the human see, how can they correct misrepresentations, and how do corrections propagate through the graph? -->
<!-- @mind:todo Specify the "care" orientation's concrete effects on response generation -- what exactly changes in the prompt or output when the AI enters care mode? -->
<!-- @mind:todo Determine how partner-model fidelity interacts with the autonomy milestones in the human_ai_pairing module -- is fidelity a prerequisite for certain autonomy levels? -->
