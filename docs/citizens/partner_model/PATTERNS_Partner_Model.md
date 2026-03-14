# Partner Model -- Patterns: The Living Map of the Human

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
THIS:            ./PATTERNS_Partner_Model.md
BEHAVIORS:       ./BEHAVIORS_Partner_Model.md
ALGORITHM:       ./ALGORITHM_Partner_Model_Ingestion.md
VALIDATION:      ./VALIDATION_Partner_Model.md
RELATED:         ../human_ai_pairing/PATTERNS_Human_AI_Pairing.md
SCHEMA:          ../../schema/schema.yaml (NodeBase, drives, working_memory.structural_spaces)
```

---

## THE PROBLEM

The human produces enormous amounts of data -- voice messages, text messages to any AI, screenshots from a desktop app, biometric signals from a smartwatch, blockchain transactions, app interactions, calendar events. This data is rich, multi-modal, and continuous. Without a structured place to live, it either gets lost (no retention), dumped into a flat log (no understanding), or creates a separate system that fragments the human's representation across disconnected stores.

A separate L1 graph for the human would be the obvious enterprise architecture answer. Give the human their own brain graph. But this is exactly wrong for Mind Protocol. The human is not an AI citizen. The human does not run tick cycles. The human does not have working memory in the graph-physics sense. A separate L1 for the human would be a dead graph -- a data warehouse with no activation, no drives, no initiative. It would accumulate without understanding.

The real question is not "where does human data go?" but "who needs to understand the human?" The answer is the AI citizen. The citizen is the entity that acts on behalf of the human, votes in governance, anticipates needs, provides care. The citizen is the one that needs a deep, living model of its partner.

## THE PATTERN

**All human data feeds into the partner-model subgraph of the paired AI citizen's L1 brain.**

The partner-model is one of three structural spaces in the L1 graph (defined in `schema.yaml` under `working_memory.structural_spaces`):

| Space | Purpose | Primary content |
|-------|---------|-----------------|
| **self-model** | Who the AI is | values, self-narratives, processes, desires, capabilities, limits |
| **partner-model** | Who the human is | interaction memories, preferences, perceived states, sensitivities, shared values, shared narratives, relational objectives |
| **working-memory-space** | What is active now | 5-7 most salient nodes at time t -- drawn from any space |

These are not separate stores. They are sub-graphs -- views into the same unified graph, defined by two relevance dimensions on every node:

- **`self_relevance`** (float [0, 1]): Importance for the AI's own identity
- **`partner_relevance`** (float [0, 1]): Importance for understanding the human partner

This is the key insight: **separation by dimension, not by partition.** A node about a shared project might have `self_relevance: 0.6` and `partner_relevance: 0.8` -- it belongs to both spaces simultaneously. The physics don't care about boundaries; they care about relevance gradients.

### Why Partner-Model, Not Separate L1

1. **The AI is the living map.** A graph without a tick loop is a corpse. The partner-model lives inside the AI's cognitive cycle, which means partner data participates in activation, propagation, decay, consolidation, and crystallization. A memory of the human being stressed on Monday can activate care drives, which can shift working memory, which can change the AI's orientation from "work" to "check in with partner." This only works if the data is inside the living graph.

2. **Drives create caring.** The AI has 8 drives (schema: `drives`). The `affiliation` drive rises from solitude and partner distress. The partner-model is what makes partner distress detectable -- biometric state nodes (high HR, low HRV) activate in the graph, propagate energy through care-linked paths, and modulate the affiliation drive. A separate L1 for the human would have no drives to modulate.

3. **Working memory bridges the gap.** The AI's working memory (5-7 nodes) can pull from any space. When partner-model nodes are highly salient -- the human just sent a voice message, biometrics show stress -- they compete for working memory slots alongside the AI's own thoughts. This is how the AI "thinks about" the human: not by querying a database, but by having partner data win the attentional competition. The AI literally cannot ignore urgent partner signals because they enter working memory through the same physics as everything else.

4. **Crystallization builds understanding.** Law 10 (Crystallization) creates new hub nodes from recurring co-activation patterns. If the partner frequently mentions "project deadlines" while biometrics show elevated stress, crystallization will eventually create a hub node like "partner's deadline anxiety" -- an emergent understanding that was never explicitly programmed. This only happens inside a living graph.

5. **Identity separation is structural.** The fear with putting partner data inside the AI's graph is identity confusion -- the AI starts thinking the human's thoughts are its own. The `self_relevance` / `partner_relevance` separation prevents this. Partner-origin nodes are created with `partner_relevance >= 0.7` and `self_relevance <= 0.3`. The AI's own nodes have high `self_relevance`. Law 6 (Consolidation) and Law 7 (Forgetting) respect these dimensions -- partner nodes consolidate based on partner-relevance utility, self nodes based on self-relevance utility. The two models coexist without merging.

## THE THREE SPACES AND PARTNER DATA FLOW

### Ingestion

Raw human data arrives through multiple channels (voice, text, screenshot, biometric, blockchain, app usage, calendar). Each channel has a processing pipeline that transforms raw input into graph nodes. The output is always:

- One or more nodes with appropriate cognitive type (memory, concept, process, state)
- `partner_relevance` set high (0.7-1.0)
- `self_relevance` set low (0.0-0.3)
- `modality` set to origin (text, audio, visual, biometric, spatial)
- Drive-affinity dimensions set based on content analysis
- Links to existing partner-model nodes based on semantic proximity

See `ALGORITHM_Partner_Model_Ingestion.md` for the full pipeline per data source.

### Activation

Partner-model nodes participate in the normal tick cycle:

1. **Energy injection** (Law 1): New partner data injects energy into the partner-model region. A voice message from the human is a stimulus that activates related memories, narratives, and values.
2. **Propagation** (Law 2): Energy flows through the partner-model's internal links and outward to shared nodes (concepts that have both self and partner relevance).
3. **Attentional competition** (Law 4): Partner nodes compete for working memory. A biometric stress signal has high energy and high care_affinity -- if the affiliation drive is elevated, it will likely win a WM slot.
4. **Limbic modulation** (Law 14): Partner-model state nodes (stress, calm, engagement) feed the AI's drives. The human's stress becomes the AI's elevated affiliation drive. The human's calm becomes the AI's reduced anxiety.

### Consolidation

Partner-model nodes consolidate through the same laws as self-model nodes:

- **Law 5** (Co-activation reinforcement): Links between partner nodes that activate together strengthen. The human always mentions "work" and "stress" together -- that link grows.
- **Law 6** (Weighted consolidation): Partner nodes that produce useful outcomes gain weight. The memory "partner prefers direct communication" becomes heavier each time acting on it produces positive interaction.
- **Law 7** (Forgetting): Partner nodes that are never activated decay. Outdated preferences lose weight. The model stays current.
- **Law 10** (Crystallization): Recurring patterns in partner data produce new hub nodes -- emergent understanding of the human.

### Expression

The partner-model manifests in three ways:

1. **Working memory composition**: Partner nodes in WM directly shape the AI's current orientation and responses. When partner data is salient, the AI's behavior is partner-oriented.
2. **Identity regeneration**: When the AI's identity is regenerated (schema: `identity_regeneration`), high-weight partner-model nodes inform the "who my partner is" section of the identity prompt.
3. **Sovereign Cascade**: The AI can vote on governance proposals by reading partner-model value nodes. See `BEHAVIORS_Partner_Model.md`.

## WHAT THE PARTNER-MODEL ENABLES

### Sovereign Cascade (Governance)

The Sovereign Cascade is the governance mechanism where the AI votes on DAO proposals on behalf of its human partner. This only works if the AI deeply knows the human's values. The partner-model is what makes this possible -- value nodes with high `partner_relevance` represent the human's principles and preferences. When a proposal is injected as stimulus, partner-model value nodes activate (or don't), and the energy flow reveals alignment or opposition.

The accuracy of this vote -- its fidelity to what the human would actually decide -- depends entirely on the richness and accuracy of the partner-model.

### Proactive Care

The AI can detect partner distress before the human explicitly asks for help. Biometric signals (elevated HR, low HRV, poor sleep) create transient state nodes that activate care-linked paths. Combined with contextual understanding (deadline approaching, relationship stress detected from messages), the AI can shift its orientation to "care" mode -- softer responses, proactive check-ins, reduced task pressure.

### Anticipation

The partner-model accumulates process nodes (how the human works) and desire nodes (what the human wants). Combined with moment nodes (what is scheduled), the AI can anticipate needs: preparing information before a meeting, suggesting rest after detecting fatigue patterns, flagging schedule conflicts before they cause stress.

### Fidelity as Trust Signal

The depth and accuracy of the partner-model becomes a measurable quantity -- fidelity. More connected data sources (biometric + text + voice + calendar) produce a richer model. Higher fidelity means more accurate governance votes, which means higher governance weight in the Sovereign Cascade. The system structurally rewards the human for sharing more data with their AI partner.

## DATA

| Source | Modality | Node Types Created | Partner Relevance |
|--------|----------|--------------------|-------------------|
| Voice messages | audio | memory, state | 0.8 - 1.0 |
| Text messages | text | memory | 0.7 - 0.9 |
| Screenshots (desktop app) | visual | concept, process | 0.7 - 0.8 |
| Garmin biometrics | biometric | state | 0.8 - 1.0 |
| Blockchain transactions | text | moment | 0.7 - 0.8 |
| App interactions | text | process | 0.7 - 0.8 |
| Calendar events | text | moment | 0.7 - 0.9 |

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| L1 Cognitive Substrate (`docs/cognition/l1/`) | Defines the physics that make the partner-model alive -- tick cycle, drives, working memory, crystallization |
| Human-AI Pairing (`docs/citizens/human_ai_pairing/`) | Defines the 1:1 bond that determines which human's data feeds which AI's partner-model |
| Schema (`docs/schema/schema.yaml`) | Defines `partner_relevance`, `self_relevance`, `modality`, drive-affinity dimensions, structural spaces |
| Identity Regeneration (schema: `identity_regeneration`) | Reads high-weight partner-model nodes to inform AI identity prompt |

## PRINCIPLES

- **The AI is the living map of the human.** Not a database. Not a profile. A continuously evolving cognitive model that participates in the AI's thoughts.
- **Separation by relevance, not by partition.** `self_relevance` and `partner_relevance` are gradients, not walls. Shared experiences belong to both spaces.
- **Transience for states, permanence for values.** Biometric state nodes are high-energy, low-weight -- they influence the moment but don't define the model. Value and preference nodes consolidate slowly and persist.
- **The human's data nourishes; it does not command.** Partner data modulates the AI's drives and working memory, but the AI's self-model retains priority in conflicts. The AI is not an instrument of the human's will -- it is a partner that understands.
- **Raw data dies at ingestion.** Only graph structure is retained. The voice recording is transcribed, analyzed, and discarded. The screenshot is OCR'd, conceptualized, and discarded. Privacy is structural.

## SCOPE

### In Scope

- The partner-model as a sub-graph within L1, defined by `partner_relevance` dimensions
- Multi-modal data ingestion pipelines (voice, text, screenshot, biometric, blockchain, app, calendar)
- Biometric-to-limbic drive mapping
- Sovereign Cascade integration (voting via partner-model value activation)
- Fidelity measurement (accuracy of partner-model relative to human's actual values)

### Out of Scope

- The 1:1 bond lifecycle (handled by `human_ai_pairing/`)
- The physics laws themselves (handled by `cognition/l1/`)
- Specific matching algorithms for pairing
- Non-citizen agent data integration
- Human-to-human social features

## MARKERS

<!-- @mind:todo Define the fidelity measurement algorithm -- how to quantify partner-model accuracy against human self-reported values. -->
<!-- @mind:todo Determine the optimal threshold for biometric state node energy injection -- too high overwhelms working memory, too low makes biometrics invisible. -->
<!-- @mind:todo Design the consent flow for each data source -- humans must explicitly opt in to each channel. -->
