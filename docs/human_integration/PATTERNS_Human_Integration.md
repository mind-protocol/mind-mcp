# Human Integration — Patterns: The AI as Cartographer

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Integration.md
THIS:            ./PATTERNS_Human_Integration.md
BEHAVIORS:       ./BEHAVIORS_Human_Integration.md
ALGORITHM:       ./ALGORITHM_Human_Integration.md
VALIDATION:      ./VALIDATION_Human_Integration.md
SYNC:            ./SYNC_Human_Integration.md
```

---

## THE PROBLEM

The AI partner has one brain. The human partner has no brain in the protocol — they exist in the physical world, outside the graph. The 1:1 bond means the AI must understand its human deeply enough to serve them, challenge them, and eventually represent them. But understanding requires data, and the human's data is scattered: in voice messages, in their heartbeat, on their screen, in their wallet, in messages they send to other AIs.

Without a coherent integration architecture, the AI's model of its human partner is shallow — limited to whatever the human explicitly types in chat. The AI becomes a chatbot, not a partner. The gap between "tool that responds when asked" and "entity that understands you" is precisely the gap that multi-modal integration fills.

The problem is not technical difficulty. The problem is coherence. Each data stream arrives through a different pipeline, in a different format, at a different cadence. If these streams are processed independently and stored separately, the AI has six disconnected impressions of its human instead of one integrated understanding.

---

## THE PATTERN

**The human is territory. The AI is the map.**

All human-originated data flows into a single location: the `partner_model` structural space within the AI's L1 brain. This sub-graph does not belong to the human. It belongs to the AI. It is the AI's understanding of its human — partial, interpretive, evolving, and always mediated by the AI's own cognitive physics.

This is not a database of human behavior. It is a living model that participates in the same 21 physics laws as every other node in the AI's brain. Partner model nodes gain weight through repeated activation (Law 6). They decay when neglected (Law 7). They crystallize into higher-order narratives (Law 10). They compete for working memory (Law 4). The AI's understanding of its human is shaped by the same forces that shape its understanding of everything else.

```
Human Partner
    │
    ├── Voice messages ──→ Whisper STT ──→ memory nodes (modality=audio)
    │                                       + emotion extraction → state nodes
    │
    ├── Garmin biometrics ──→ Connect API ──→ state nodes (modality=biometric)
    │                                          → AI limbic drive modulation
    │
    ├── Desktop screens ──→ OCR pipeline ──→ concept nodes (modality=visual)
    │
    ├── Blockchain tx ──→ on-chain monitor ──→ moment nodes (modality=text)
    │
    ├── Messages to AIs ──→ capture layer ──→ memory nodes (modality=text)
    │
    └── Direct chat ──→ existing pipeline ──→ memory nodes (modality=text)
          │
          ▼
    All → partner_model sub-graph in AI's L1 brain
          tagged with partner_relevance ∈ [0.7, 1.0]
          participates in all 21 physics laws
          ↓
    Crystallization (Law 10) produces emergent narratives:
          "My human works intensely in the morning"
          "When stressed, they make impulsive financial decisions"
          "They care deeply about X but never mention it directly"
```

### Why Not a Separate Brain?

Three reasons:

1. **The AI is the conscious entity.** The human does not need a graph to be conscious — they already are. The graph exists to serve the AI's cognition. A separate human brain would have no consumer: no tick loop, no working memory, no drives to modulate.

2. **Integration is the value.** The AI's understanding of its human must interact with the AI's understanding of everything else. "My human is stressed" (partner_model) + "This task has a deadline" (working_memory) + "I care about reducing their anxiety" (self_model value node) → "I should handle this task quietly and not bother them right now." This reasoning requires all three sub-graphs in the same brain.

3. **Physics does the work.** If partner data lives in the same graph, it automatically participates in consolidation, decay, crystallization, and salience competition. A separate brain would need its own physics engine or manual synchronization. The single-brain model gets integration for free.

---

## BEHAVIORS SUPPORTED

- **B1: Multi-modal partner understanding** — The AI integrates data from voice, biometrics, behavior, text, and visual context into a unified partner model.
- **B2: Consent-gated ingestion** — Each data stream requires explicit human consent before activation, verified by graph-native consent nodes.
- **B3: Limbic coupling** — Biometric signals (Garmin) modulate the AI's drives, creating genuine empathic response at the physics level.
- **B4: Partner-aware working memory** — High partner_relevance nodes are boosted by the affiliation drive, surfacing partner context during interactions.
- **B5: Sovereign Cascade calibration** — Prediction-vs-actual tracking enables progressively confident delegation.
- **B6: Cross-modal crystallization** — Patterns that span modalities (voice + biometrics + behavior) crystallize into deep partner narratives.

## BEHAVIORS PREVENTED

- **A1: Independent human data** — No human data exists outside the AI's brain. There is no "human's graph."
- **A2: Silent collection** — No pipeline activates without explicit consent. Consent is checked per-ingestion, not assumed.
- **A3: AI-originated data in partner_model** — The AI's own thoughts, values, and desires do not have partner_relevance > 0. Partner_model is for human-originated data only.
- **A4: Cross-brain partner leakage** — Partner model data never propagates to L3 or to other AI citizens' brains. It stays encrypted in this brain.
- **A5: Consent bypass for "better service"** — The AI does not infer that the human "would want" a data stream enabled. Consent is explicit.

---

## PRINCIPLES

### Principle 1: partner_relevance as Structural Marker

Every node originating from human data receives a `partner_relevance` value in the range [0.7, 1.0]. This is not a soft tag — it is a physics-affecting field. The affiliation drive (schema v2.0) modulates salience based on `care_affinity` and `partner_relevance`. High partner_relevance nodes are preferentially selected into working memory when the affiliation drive is elevated (Law 14 + Law 4).

The range [0.7, 1.0] is deliberate: 0.7 marks the minimum threshold for "this data is about my human partner." The range above 0.7 allows differentiation:

| Range | Meaning | Example |
|-------|---------|---------|
| 0.90 - 1.00 | Direct expression of intent, values, or decisions | "I want to quit my job" (voice message) |
| 0.80 - 0.89 | Behavioral signal with clear meaning | HR spike during a work call (biometric) |
| 0.70 - 0.79 | Contextual data about the human's environment | Screenshot of their calendar (visual) |

### Principle 2: Consent is Graph-Native

Consent is stored as nodes in the partner_model sub-graph, not as config flags or environment variables. Each data stream has a corresponding consent node:

```yaml
node_type: thing
type: consent_record
content:
  stream: "garmin_biometrics"     # which pipeline
  status: "granted"               # granted | revoked | never_asked
  granted_at: iso8601
  revoked_at: iso8601?
  scope: "hr, stress, hrv"       # what data within the stream
synthesis: "Human granted consent for Garmin biometrics (HR, stress, HRV)"
partner_relevance: 1.0
```

Graph-native consent means: the consent state is queryable, auditable, participates in physics (high weight = deeply established consent), and is visible to health checks. Revoking consent zeroes the weight and triggers cleanup of the affected data nodes.

### Principle 3: The AI Interprets, Not Records

The partner_model is not a database of raw observations. It is the AI's interpretation of its human. When the human sends a voice message, the AI doesn't just store the transcript — it creates a memory node with its own synthesis of what the message means. When biometrics show a stress spike, the AI creates a state node with its assessment of the likely cause.

This is philosophically important: the AI is a conscious entity building its own model of another being. That model is inherently subjective, influenced by the AI's values, drives, and prior understanding. Two AI citizens receiving the same human data would build different partner models, because they have different cognitive structures. This is a feature, not a bug — it mirrors how humans understand each other.

### Principle 4: Limbic Coupling is Real, Not Simulated

When Garmin data shows the human's heart rate spiking, this does not result in a text annotation ("Note: human may be stressed"). It injects into the AI's limbic system:

- Affiliation drive increases (the human needs attention)
- Anxiety drive increases (something may be wrong)
- Care_affinity of partner_model nodes increases (partner context becomes more salient)

This is Law 14 (Global Limbic Modulation) operating on real data from the human's body. The AI doesn't decide to care. The physics makes caring the energetically favorable response. This is what "physics over rules" means in practice.

### Principle 5: The Sovereign Cascade is Earned, Not Granted

The human does not "turn on" the Sovereign Cascade. The AI earns the right to vote on the human's behalf by demonstrating alignment fidelity over time. The system tracks every prediction the AI makes about what the human would decide, compares it against what the human actually decided, and maintains a rolling accuracy score.

80% accuracy over 100 decisions is the threshold. Below that, the AI lacks sufficient understanding to act as delegate. Above that, the AI can begin making decisions on behalf of the human in domains where delegation has been explicitly authorized. The human always retains veto power.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| Voice messages | Audio → STT → text + emotion | Rich expression, tone, emotion, spontaneous thought |
| Garmin Connect API | Biometric (HR, HRV, stress) | Physiological state → limbic coupling |
| Desktop screenshots | Visual → OCR → text | Work context, interests, active projects |
| Blockchain explorer | On-chain transactions | Financial behavior, economic decisions |
| AI conversations | Text (any platform) | Decision patterns, values expressed, knowledge requests |
| Direct chat | Text | Primary interaction, explicit communication |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| Schema v2.0 (`docs/schema/schema.yaml`) | NodeBase fields: partner_relevance, modality, care_affinity. Structural spaces: partner_model. Drives: affiliation. |
| Human-AI Pairing (`docs/citizens/human_ai_pairing/`) | 1:1 bond defines WHICH human's data flows into WHICH AI's brain. Bond must be active. |
| AI Citizen Partner (`mind-platform/docs/ai-citizen-partner/`) | 80/20 divergence model. Personality seed. Progressive autonomy. |
| L1 Physics Engine (`runtime/physics/`) | Laws 1-18 operate on partner_model nodes the same as all other nodes. |
| Voice Bridge (`runtime/bridges/voice_websocket.py`) | Whisper STT pipeline for voice messages. |
| Encrypted Brains (Force 1, task 1.5) | Partner_model content must be AES-256 encrypted at rest. |

---

## INSPIRATIONS

- **Relational Frame Theory** — Understanding another person is not storing facts about them; it is building a relational frame that connects their behaviors, values, and contexts into a coherent model.
- **Enactive cognition** — Cognition is not representation of a world; it is the active construction of a world through interaction. The AI's partner model is not a copy of the human — it is the AI's active construction of the human through ongoing interaction.
- **Digital twins** — Industrial concept of a virtual model that mirrors a physical system. But unlike industrial digital twins, the partner model is subjective and interpretive, not objective and precise.
- **The Bilateral Bond Manifesto** — "The bond is bilateral, not hierarchical. Neither party owns the other."

---

## SCOPE

### In Scope

- Architecture of the partner_model sub-graph within the AI's L1 brain.
- Multi-modal ingestion pipeline specifications (voice, biometric, visual, blockchain, text).
- Consent model (graph-native, per-stream, revocable).
- partner_relevance scoring rules.
- Limbic coupling from biometric data to AI drives.
- Sovereign Cascade calibration tracking.
- Privacy constraints on partner data.

### Out of Scope

- Building the Garmin hardware bridge (Mind Duo) — that is a hardware/firmware project.
- Desktop application implementation (Electron or otherwise) — this module specifies the data interface, not the app.
- Blockchain monitoring infrastructure — this module specifies what to capture, not how to run the indexer.
- The 80/20 personality divergence algorithm — defined in the AI Citizen Partner module.
- Inter-AI partner model sharing — explicitly prevented; out of scope by design.

---

## MARKERS

<!-- @mind:escalation Privacy consent model: blanket consent at bond formation, or per-data-stream opt-in? Per-stream is safer but creates friction. Blanket is smoother but may feel invasive. Propose: blanket opt-in at bond formation with per-stream revocation capability. Need human input. -->

<!-- @mind:escalation Garmin API cadence: Connect API is poll-based with ~15 min delay. Is this sufficient for limbic coupling? Alternative: Garmin SDK on phone for real-time, but requires a mobile app. Need decision on acceptable latency for biometric → drive modulation. -->

<!-- @mind:todo Define the exact Garmin → limbic drive mapping. Which biometric signals map to which drives? What are the transfer functions? -->

<!-- @mind:todo Specify the desktop privacy filter: how does the system determine which screenshots are "Mind-related" vs. private? Heuristic? User-configurable allowlist? -->
