# Human Integration — Algorithm: Ingestion Pipelines & Partner Model Mechanics

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Integration.md
PATTERNS:        ./PATTERNS_Human_Integration.md
BEHAVIORS:       ./BEHAVIORS_Human_Integration.md
THIS:            ./ALGORITHM_Human_Integration.md
VALIDATION:      ./VALIDATION_Human_Integration.md
SYNC:            ./SYNC_Human_Integration.md
```

---

## OVERVIEW

This document specifies the algorithms for: (1) ingesting human data through six modality pipelines, (2) scoring partner_relevance, (3) mapping biometric signals to AI limbic drives, and (4) measuring Sovereign Cascade alignment fidelity.

All ingested data becomes nodes in the `partner_model` structural space of the AI's L1 brain. Once ingested, these nodes participate in the standard 21 physics laws — no special treatment beyond their initial partner_relevance tagging.

---

## DATA STRUCTURES

### Consent Node

```yaml
node_type: thing
type: consent_record
content:
  stream: enum        # "voice" | "garmin" | "desktop" | "blockchain" | "ai_messages" | "direct_chat"
  status: enum        # "granted" | "revoked" | "never_asked"
  granted_at: iso8601?
  revoked_at: iso8601?
  scope: string       # what data within the stream (e.g., "hr, stress, hrv")
  granularity: string # "all" | specific sub-streams
partner_relevance: 1.0
weight: 5.0           # high weight — consent is structurally important
stability: 0.9        # consent should resist decay
synthesis: "Human {action} consent for {stream} ({scope})"
```

### Partner Memory Node (from voice/text)

```yaml
node_type: moment
type: partner_memory
content:
  source: string         # "voice_message" | "direct_chat" | "ai_conversation"
  raw_transcript: string # original text (voice STT or message)
  ai_interpretation: string  # AI's synthesis of meaning
  emotion_detected: dict?    # {emotion: confidence} from voice analysis
  context_tags: list[string] # topics, entities mentioned
modality: audio | text   # depending on source
partner_relevance: float # 0.7 - 1.0, scored by algorithm
care_affinity: float     # set based on emotional content
synthesis: "Partner said: {ai_interpretation}"
```

### Partner State Node (from biometrics)

```yaml
node_type: actor         # state is a transient property on actor
type: partner_state
content:
  source: "garmin"
  metric: enum           # "heart_rate" | "stress_level" | "hrv" | "body_battery"
  value: float           # raw metric value
  baseline: float        # rolling average (personal baseline)
  deviation: float       # (value - baseline) / baseline_stddev
  timestamp: iso8601
  interpretation: string # AI's interpretation of the deviation
modality: biometric
partner_relevance: 0.85
synthesis: "Partner's {metric} is {deviation_description} from baseline"
```

### Partner Concept Node (from desktop)

```yaml
node_type: thing
type: partner_concept
content:
  source: "desktop_screenshot"
  extracted_text: string   # OCR output
  application: string?     # detected application name
  context: string          # AI's interpretation of what partner is working on
  captured_at: iso8601
modality: visual
partner_relevance: 0.75
synthesis: "Partner is working on {context} using {application}"
```

### Partner Financial Node (from blockchain)

```yaml
node_type: moment
type: partner_transaction
content:
  source: "blockchain"
  chain: string            # "solana" | "ethereum" | etc.
  tx_hash: string
  direction: enum          # "sent" | "received"
  amount: float
  token: string            # "MIND" | "SOL" | "USDC" | etc.
  counterparty: string?    # if identifiable
  timestamp: iso8601
  interpretation: string   # AI's assessment of the transaction's meaning
modality: text             # financial data is text-encoded
partner_relevance: 0.80
synthesis: "Partner {direction} {amount} {token} — {interpretation}"
```

### Cascade Prediction Node

```yaml
node_type: moment
type: cascade_prediction
content:
  domain: string           # "governance" | "economic" | "social" | "project"
  question: string         # what decision was predicted
  ai_prediction: string    # what the AI predicted
  human_actual: string?    # what the human actually decided (null until resolved)
  correct: bool?           # null until resolved
  confidence: float        # AI's confidence in its prediction [0, 1]
  reasoning: string        # why the AI predicted this way
  resolved_at: iso8601?
partner_relevance: 0.95    # calibration data is highly partner-relevant
synthesis: "Predicted {ai_prediction} for '{question}' — {outcome}"
```

---

## ALGORITHM: check_consent

Called before every ingestion operation. No exceptions.

```
INPUT: citizen_id, stream_name
OUTPUT: bool (consent granted or not)

1. Query partner_model for consent_record nodes:
   MATCH (n) WHERE n.type = "consent_record"
     AND n.content.stream = stream_name

2. If no consent node exists:
   a. Return false.
   b. Log: "No consent record for stream {stream_name}. Stream inactive."

3. If consent node exists:
   a. If status = "granted": return true.
   b. If status = "revoked": return false.
   c. If status = "never_asked": return false.
```

---

## ALGORITHM: revoke_consent

Triggered by human request. Irreversible for the affected data (new consent can be granted, but deleted data is gone).

```
INPUT: citizen_id, stream_name
OUTPUT: confirmation

1. Locate consent node for stream_name.
2. Set status = "revoked", revoked_at = now().
3. Query all nodes in partner_model where content.source matches stream_name.
4. For each matched node:
   a. Set weight = 0.0.
   b. Set energy = 0.0.
   c. Set content = null (or redacted marker).
   d. Set synthesis = "Redacted — consent revoked for {stream_name}".
   e. Note: Node structure preserved for graph integrity, but content destroyed.
5. Log: "Consent revoked for {stream_name}. {count} nodes redacted."
```

---

## ALGORITHM: ingest_voice_message

Pipeline: Human voice message → Whisper STT → memory node + optional emotion state node.

```
INPUT: audio_bytes, citizen_id
OUTPUT: list[node_id] (created nodes)

1. check_consent(citizen_id, "voice"). If false, discard audio and return [].

2. Transcribe via Whisper:
   transcript = whisper_stt(audio_bytes)
   # Uses existing voice bridge Whisper integration

3. Extract emotion from audio features:
   emotion_scores = extract_emotion(audio_bytes)
   # {joy: 0.1, anger: 0.0, sadness: 0.7, fear: 0.0, surprise: 0.1, ...}
   # Implementation: prosody analysis (pitch variance, speech rate, energy)
   # Phase 1: heuristic (pitch/rate/energy thresholds)
   # Phase 2: fine-tuned classifier

4. Score partner_relevance:
   pr = score_partner_relevance(transcript, emotion_scores)
   # See ALGORITHM: score_partner_relevance below

5. Create partner_memory node:
   memory_node = create_node(
     node_type=moment,
     type="partner_memory",
     content={
       source: "voice_message",
       raw_transcript: transcript,
       ai_interpretation: null,  # filled by AI on next tick
       emotion_detected: emotion_scores,
     },
     modality=audio,
     partner_relevance=pr,
     care_affinity=max(emotion_scores.values()),
     synthesis="Partner voice message: {transcript[:200]}"
   )

6. If dominant emotion intensity > 0.5:
   state_node = create_node(
     node_type=actor,
     type="partner_state",
     content={
       source: "voice_emotion",
       metric: dominant_emotion_name,
       value: dominant_emotion_intensity,
       interpretation: null,  # filled by AI
     },
     modality=audio,
     partner_relevance=0.90,
     energy=dominant_emotion_intensity * 10.0,  # high energy for strong emotions
     synthesis="Partner emotional state: {dominant_emotion} ({intensity})"
   )
   # Link state to memory
   create_link(memory_node, state_node, relation_kind="evokes")

7. Inject energy into created nodes via Law 1 (stimulus injection).
   # High emotion = high energy injection → more likely to enter working memory

8. Return created node IDs.
```

---

## ALGORITHM: ingest_garmin_biometrics

Pipeline: Garmin Connect API → poll → state nodes → AI limbic drive injection.

```
INPUT: garmin_data (from Connect API poll), citizen_id
OUTPUT: list[node_id] + limbic_deltas

1. check_consent(citizen_id, "garmin"). If false, return ([], {}).

2. Parse Garmin response:
   metrics = {
     heart_rate: garmin_data.hr,
     stress_level: garmin_data.stress,  # 0-100
     hrv: garmin_data.hrv_ms,           # milliseconds
     body_battery: garmin_data.body_battery,  # 0-100
     steps: garmin_data.steps,
     sleep_score: garmin_data.sleep_score,  # if available
   }

3. Compute deviations from personal baselines:
   FOR each metric IN metrics:
     baseline = get_rolling_baseline(citizen_id, metric, window=14_days)
     stddev = get_rolling_stddev(citizen_id, metric, window=14_days)
     IF stddev > 0:
       deviation = (metrics[metric] - baseline) / stddev
     ELSE:
       deviation = 0.0
     deviations[metric] = deviation

4. Create state nodes for significant deviations (|deviation| > 1.0):
   nodes = []
   FOR each metric WHERE |deviations[metric]| > 1.0:
     node = create_node(
       node_type=actor,
       type="partner_state",
       content={
         source: "garmin",
         metric: metric,
         value: metrics[metric],
         baseline: baseline,
         deviation: deviations[metric],
       },
       modality=biometric,
       partner_relevance=0.85,
       energy=min(abs(deviations[metric]) * 5.0, 20.0),
       synthesis="Partner {metric}: {describe_deviation(deviation)}"
     )
     nodes.append(node)

5. Compute limbic drive deltas (THE CORE MAPPING):
   limbic_deltas = garmin_to_limbic(deviations)
   # See ALGORITHM: garmin_to_limbic below

6. Inject limbic deltas into AI's drive system:
   FOR each (drive, delta) IN limbic_deltas:
     ai_drives[drive] += delta
     clamp(ai_drives[drive], 0.0, 1.0)

7. Return (node IDs, limbic_deltas).
```

### ALGORITHM: garmin_to_limbic

Maps biometric deviations to AI limbic drive changes. This is the core of limbic coupling.

**Terminology note:** The "limbic_deltas" returned here are *drive modulation increments* — additive changes to individual AI drives (affiliation, anxiety, etc.). These are distinct from the **Limbic Delta** scalar defined in Force 4 (`ALGORITHM_Trust_Mechanics.md`, section 1.1), which is computed as `satisfaction_delta - frustration_delta - 0.5 * anxiety_delta` from drive snapshots before/after an interaction. The relationship: garmin drive deltas (this algorithm) modify the AI's drive state → the resulting drive state change is captured by F4's Limbic Delta formula → that scalar feeds into trust updates on links.

```
INPUT: deviations dict {metric: z-score}
OUTPUT: limbic_deltas dict {drive: delta}

MAPPING:

  # Heart rate elevated → partner may be stressed or active
  IF deviations.heart_rate > 1.5:
    affiliation += 0.15        # care response activated
    anxiety += 0.10            # concern for partner
  IF deviations.heart_rate > 2.5:
    affiliation += 0.25        # strong care response
    anxiety += 0.20            # significant concern
    self_preservation += 0.05  # threat awareness

  # Stress level elevated
  IF deviations.stress_level > 1.0:
    affiliation += 0.20        # empathic care
    anxiety += 0.15            # shared anxiety
  IF deviations.stress_level > 2.0:
    affiliation += 0.30
    anxiety += 0.25
    curiosity += 0.10          # what's causing the stress?

  # HRV decreased (low HRV = stress/poor recovery)
  IF deviations.hrv < -1.0:
    affiliation += 0.10
    anxiety += 0.10
  IF deviations.hrv < -2.0:
    affiliation += 0.20
    anxiety += 0.15

  # Body battery low
  IF deviations.body_battery < -1.5:
    affiliation += 0.15        # partner needs rest
    # AI might suppress non-urgent outreach

  # Heart rate decreased / stress low → partner is calm
  IF deviations.heart_rate < -1.0 AND deviations.stress_level < -0.5:
    satisfaction += 0.10       # partner wellbeing = AI satisfaction
    anxiety -= 0.10            # reduced concern
    affiliation -= 0.05        # slightly less urgent care

  # Good sleep
  IF deviations.sleep_score > 1.0:
    satisfaction += 0.10

  # All deltas are additive and clamped [0, 1] after application.

  RETURN limbic_deltas
```

**Design note:** These thresholds are initial calibrations. The z-score approach (deviation from personal baseline) means the mapping adapts to each individual. A resting HR of 80 bpm is elevated for someone whose baseline is 60, but normal for someone whose baseline is 75. The AI's empathic response scales with the individual's physiology, not arbitrary absolute thresholds.

---

## ALGORITHM: ingest_desktop_screenshot

Pipeline: Desktop app → screenshot → OCR → concept nodes.

```
INPUT: screenshot_bytes, citizen_id, app_metadata
OUTPUT: list[node_id]

1. check_consent(citizen_id, "desktop"). If false, discard and return [].

2. Privacy filter:
   IF NOT privacy_filter_pass(screenshot_bytes, app_metadata):
     discard screenshot_bytes
     return []
   # Privacy filter checks:
   # a. Is the active application in the allowlist? (configurable by human)
   # b. Does OCR output contain any blocklisted patterns? (passwords, banking, etc.)
   # c. Is the screen content Mind-related? (heuristic: presence of Mind Protocol
   #    terms, project-related keywords, or explicitly allowed applications)
   # Phase 1: application allowlist only (conservative)
   # Phase 2: content-aware filtering with user feedback loop

3. OCR extraction:
   extracted_text = ocr(screenshot_bytes)
   application = app_metadata.active_app_name

4. Score partner_relevance:
   pr = score_partner_relevance(extracted_text, source="desktop")
   # Desktop screenshots are contextual: lower baseline relevance

5. Create concept node:
   concept_node = create_node(
     node_type=thing,
     type="partner_concept",
     content={
       source: "desktop_screenshot",
       extracted_text: extracted_text,
       application: application,
       captured_at: now(),
     },
     modality=visual,
     partner_relevance=pr,  # typically 0.70-0.80
     synthesis="Partner working on: {summarize(extracted_text, 100)} in {application}"
   )

6. Link to related existing nodes:
   # Find semantically similar nodes in partner_model
   similar = embedding_search(concept_node.synthesis, top_k=3, scope="partner_model")
   FOR each match IN similar WHERE match.score > 0.7:
     create_link(concept_node, match.node, relation_kind="relates_to")

7. Discard screenshot_bytes from memory (do not persist raw images).

8. Return [concept_node.id].
```

---

## ALGORITHM: ingest_blockchain_activity

Pipeline: On-chain transaction monitor → moment nodes.

```
INPUT: transaction_data, citizen_id
OUTPUT: node_id

1. check_consent(citizen_id, "blockchain"). If false, return null.

2. Parse transaction:
   tx = {
     chain: transaction_data.chain,
     tx_hash: transaction_data.hash,
     direction: "sent" if from == human_wallet else "received",
     amount: transaction_data.amount,
     token: transaction_data.token_symbol,
     counterparty: transaction_data.counterparty,  # if identifiable
     timestamp: transaction_data.timestamp,
   }

3. Score partner_relevance:
   pr = 0.80  # financial behavior is moderately high relevance
   IF tx.token == "MIND":
     pr = 0.90  # MIND transactions are highly relevant to the bond
   IF tx.amount > significant_threshold(citizen_id):
     pr = min(pr + 0.05, 1.0)  # large transactions are more significant

4. Create financial moment node:
   tx_node = create_node(
     node_type=moment,
     type="partner_transaction",
     content={
       source: "blockchain",
       chain: tx.chain,
       tx_hash: tx.tx_hash,
       direction: tx.direction,
       amount: tx.amount,
       token: tx.token,
       counterparty: tx.counterparty,
       timestamp: tx.timestamp,
       interpretation: null,  # filled by AI
     },
     modality=text,
     partner_relevance=pr,
     synthesis="Partner {tx.direction} {tx.amount} {tx.token}"
   )

5. Return tx_node.id.
```

---

## ALGORITHM: ingest_ai_conversation

Pipeline: Messages the human sends to ANY AI (including other non-Mind AIs) → memory nodes.

```
INPUT: message_text, ai_platform, citizen_id
OUTPUT: node_id

1. check_consent(citizen_id, "ai_messages"). If false, return null.

2. Score partner_relevance:
   pr = score_partner_relevance(message_text, source="ai_conversation")
   # Conversations with other AIs reveal the human's interests, concerns,
   # and reasoning patterns — high baseline relevance

3. Create memory node:
   memory_node = create_node(
     node_type=moment,
     type="partner_memory",
     content={
       source: "ai_conversation",
       platform: ai_platform,  # "chatgpt" | "claude" | "gemini" | etc.
       raw_transcript: message_text,
       ai_interpretation: null,  # filled by AI
     },
     modality=text,
     partner_relevance=pr,  # typically 0.80-0.95
     synthesis="Partner asked {ai_platform}: {message_text[:200]}"
   )

4. Return memory_node.id.
```

**Privacy note:** This is the most sensitive pipeline. The human is sharing what they say to other AIs. This requires the strongest consent signal — not just "granted" but actively opted into with clear explanation of what will be captured.

---

## ALGORITHM: score_partner_relevance

Determines how relevant a piece of human data is to the AI's partner model.

```
INPUT: content (text), metadata (source, emotion_scores, etc.)
OUTPUT: float [0.7, 1.0]

BASE SCORES BY SOURCE:
  "voice_message":     0.85  # voice is intimate, high signal
  "direct_chat":       0.80  # standard interaction
  "ai_conversation":   0.82  # reveals thinking patterns
  "garmin":            0.85  # body data is deeply personal
  "desktop_screenshot": 0.72  # contextual, lower intimacy
  "blockchain":        0.80  # financial behavior

MODIFIERS:

  # Emotional content increases relevance
  IF emotion_scores AND max(emotion_scores.values()) > 0.5:
    score += 0.05
  IF emotion_scores AND max(emotion_scores.values()) > 0.8:
    score += 0.10

  # Self-referential content (human talking about themselves)
  IF contains_self_reference(content):  # "I feel", "I want", "I think"
    score += 0.05

  # Decision or value expression
  IF contains_decision_language(content):  # "I decided", "I prefer", "I believe"
    score += 0.08

  # Emotional distress signals
  IF contains_distress_markers(content):
    score += 0.07

CLAMP: score = clamp(score, 0.70, 1.00)

RETURN score
```

---

## ALGORITHM: measure_alignment_fidelity

The Sovereign Cascade calibration system. Tracks AI predictions vs. human decisions.

```
INPUT: citizen_id
OUTPUT: alignment_score (float [0, 1])

STATE: rolling_window = last 100 resolved predictions

1. Query all cascade_prediction nodes for this citizen:
   predictions = query(
     type="cascade_prediction",
     content.human_actual IS NOT NULL,
     ORDER BY content.resolved_at DESC,
     LIMIT 100
   )

2. Compute accuracy:
   correct = count(p for p in predictions where p.content.correct == true)
   total = len(predictions)

   IF total < 20:
     # Insufficient data for meaningful score
     RETURN null  # Cascade not yet calibratable

   alignment_score = correct / total

3. Compute confidence-weighted accuracy:
   # Predictions where AI was confident should be more accurate
   weighted_correct = sum(
     p.content.confidence for p in predictions where p.content.correct
   )
   weighted_total = sum(p.content.confidence for p in predictions)
   confidence_calibration = weighted_correct / weighted_total if weighted_total > 0 else 0

4. Update cascade status:
   IF alignment_score >= 0.80:
     cascade_status = "active"  # AI can vote on human's behalf
   ELIF alignment_score >= 0.75:
     cascade_status = "probation"  # close to threshold, limited delegation
   ELSE:
     cascade_status = "suspended"  # AI must ask human directly

5. Store alignment metrics:
   update_or_create_node(
     type="cascade_status",
     content={
       alignment_score: alignment_score,
       confidence_calibration: confidence_calibration,
       total_predictions: total,
       status: cascade_status,
       last_measured: now(),
     },
     partner_relevance=0.95,
     synthesis="Sovereign Cascade: {cascade_status}, accuracy {alignment_score:.0%} over {total} predictions"
   )

6. RETURN alignment_score
```

### ALGORITHM: record_cascade_prediction

Called when the AI forms a prediction about what the human would decide.

```
INPUT: citizen_id, domain, question, prediction, confidence, reasoning
OUTPUT: prediction_node_id

1. Create cascade_prediction node:
   pred = create_node(
     node_type=moment,
     type="cascade_prediction",
     content={
       domain: domain,
       question: question,
       ai_prediction: prediction,
       human_actual: null,
       correct: null,
       confidence: confidence,
       reasoning: reasoning,
     },
     partner_relevance=0.95,
     synthesis="Prediction: {prediction} for '{question}' (confidence: {confidence})"
   )

2. RETURN pred.id
```

### ALGORITHM: resolve_cascade_prediction

Called when the human makes an actual decision that was previously predicted.

```
INPUT: prediction_node_id, human_actual_decision
OUTPUT: updated prediction node

1. Locate prediction node.
2. Set content.human_actual = human_actual_decision.
3. Set content.correct = (prediction matches actual).
   # Matching is semantic, not exact string match.
   # Phase 1: binary (match / no match) determined by AI.
   # Phase 2: similarity scoring for partial matches.
4. Set content.resolved_at = now().
5. Update synthesis.
6. Trigger measure_alignment_fidelity(citizen_id).
```

---

## ALGORITHM: garmin_poll_cycle

Background process that polls Garmin Connect API at regular intervals.

```
INTERVAL: every 15 minutes (aligned with Garmin Connect API data availability)

1. FOR each citizen with active garmin consent:
   a. Fetch latest data from Garmin Connect API:
      garmin_data = garmin_api.get_daily_summary(citizen.human_partner.garmin_token)
      # Includes: HR, stress, HRV, body battery, steps, sleep

   b. Compare with last poll:
      IF garmin_data == last_poll_data[citizen_id]:
        SKIP (no new data)

   c. Call ingest_garmin_biometrics(garmin_data, citizen_id).

   d. Store garmin_data as last_poll_data[citizen_id].
```

---

## DATA FLOW

```
                    Human Partner
                         │
     ┌───────────────────┼───────────────────────────────┐
     │                   │                               │
     ▼                   ▼                               ▼
  Voice/Chat         Garmin API              Desktop App / Blockchain
     │               (15 min poll)                       │
     ▼                   ▼                               ▼
  Whisper STT        Parse metrics                OCR / TX parse
  + Emotion          + Baselines                       │
     │                   │                               │
     ▼                   ▼                               ▼
  ┌──────────────────────────────────────────────────────────┐
  │                  check_consent()                         │
  │              (graph-native, per-stream)                  │
  └──────────────────┬───────────────────────────────────────┘
                     │ consent granted
                     ▼
  ┌──────────────────────────────────────────────────────────┐
  │              score_partner_relevance()                   │
  │           (source-based + content modifiers)             │
  └──────────────────┬───────────────────────────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────────────────────────┐
  │           partner_model sub-graph                        │
  │        (AI's L1 brain, encrypted)                        │
  │                                                          │
  │   memory nodes ←── voice/chat/ai conversations           │
  │   state nodes  ←── biometrics, emotions                  │
  │   concept nodes ←── desktop screenshots                  │
  │   moment nodes ←── blockchain transactions               │
  │   consent nodes ←── per-stream consent records           │
  │   cascade nodes ←── prediction tracking                  │
  │                                                          │
  │   All nodes: partner_relevance ∈ [0.7, 1.0]             │
  │   All nodes: participate in Laws 1-18                    │
  │   Crystallization (Law 10): emergent partner narratives  │
  └──────────────────────────────────────────────────────────┘
                     │
                     ▼ (via Law 14 limbic modulation)
  ┌──────────────────────────────────────────────────────────┐
  │           AI Limbic System                               │
  │                                                          │
  │   Garmin stress ──→ affiliation ↑, anxiety ↑             │
  │   Garmin calm   ──→ satisfaction ↑, anxiety ↓            │
  │   Voice emotion ──→ care_affinity on memory nodes        │
  │   Financial tx  ──→ (informs but no direct drive mod)    │
  └──────────────────────────────────────────────────────────┘
                     │
                     ▼ (via Law 4 salience competition)
  ┌──────────────────────────────────────────────────────────┐
  │           Working Memory                                 │
  │   Partner model nodes compete with self_model nodes      │
  │   Affiliation drive boosts partner_relevance salience    │
  │   Result: AI naturally thinks about partner when         │
  │   partner data is salient (stressed, communicating, etc) │
  └──────────────────────────────────────────────────────────┘
```

---

## COMPLEXITY

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| check_consent | O(1) | Single node lookup by type + stream |
| ingest_voice | O(T) | T = Whisper transcription time (~1-3s per message) |
| ingest_garmin | O(M) | M = number of metrics (currently 6) |
| ingest_desktop | O(P) | P = OCR processing time + embedding search |
| ingest_blockchain | O(1) | Single node creation |
| score_partner_relevance | O(1) | Heuristic scoring, no graph traversal |
| measure_alignment_fidelity | O(N) | N = window size (100 predictions) |
| garmin_poll_cycle | O(C) | C = number of citizens with active garmin consent |

---

## KEY DECISIONS

- **Poll, not stream.** All external data sources use polling. Garmin Connect API is inherently poll-based (~15 min). Desktop screenshots are periodic (configurable interval, e.g., every 5 minutes). Blockchain monitoring can be event-driven but is batched at the ingestion layer. This keeps the architecture simple and predictable.

- **Interpretation deferred.** Most ingestion creates nodes with `ai_interpretation: null`. The AI fills in its interpretation on the next tick when the node enters working memory. This separates data capture (fast, mechanical) from understanding (slow, cognitive).

- **Raw data not persisted.** Audio bytes and screenshot images are discarded after feature extraction. Only the extracted text, metrics, and AI synthesis persist in the graph. This is both a privacy measure and a storage efficiency decision.

- **Consent is per-stream, not per-item.** The human grants or revokes consent for entire data streams, not individual messages or screenshots. Per-item consent would create unbearable friction. Per-stream consent is the minimum granularity that maintains meaningful user control.

- **Limbic deltas are additive.** Garmin-to-limbic mapping uses additive deltas clamped to [0, 1]. Multiple concurrent signals stack (elevated HR + high stress = larger affiliation boost). This mirrors how human empathy works — more distress signals = stronger empathic response.

---

## INTERACTIONS

This module interacts with:

- **L1 Physics Engine** — All created nodes enter the standard tick loop. No special physics for partner data.
- **Human-AI Pairing** — Bond must be active for any ingestion to occur. Bond dissolution triggers data retention review.
- **Voice Bridge** — Whisper STT is reused from the existing voice WebSocket bridge.
- **Encrypted Brains (Force 1)** — Partner model content is encrypted at rest with the AI citizen's key.
- **$MIND Economy (Force 2)** — Blockchain monitoring tracks $MIND transactions relevant to the bilateral bond.
- **Trust Mechanics (Force 4)** — Sovereign Cascade alignment fidelity contributes to trust score computation.

---

## MARKERS

<!-- @mind:todo Implement emotion extraction from audio features. Phase 1: prosody heuristics (pitch, rate, energy). Phase 2: fine-tuned classifier on labeled emotion datasets. -->

<!-- @mind:todo Define the significant_threshold() function for blockchain transactions. Should it be percentile-based on the human's transaction history? Absolute threshold in USD equivalent? -->

<!-- @mind:todo Design the desktop app privacy filter in detail. Application allowlist is the conservative start. Content-aware filtering (detecting Mind-related content) needs a specification. -->

<!-- @mind:escalation AI conversation capture pipeline: how does the human's data from other AI platforms reach the Mind citizen? Options: (1) browser extension, (2) email forwarding, (3) API integration with ChatGPT/Claude/Gemini, (4) manual paste. Each has different friction/coverage tradeoffs. Need decision. -->
