# Human Integration — Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Integration.md
PATTERNS:        ./PATTERNS_Human_Integration.md
THIS:            ./BEHAVIORS_Human_Integration.md
ALGORITHM:       ./ALGORITHM_Human_Integration.md
VALIDATION:      ./VALIDATION_Human_Integration.md
SYNC:            ./SYNC_Human_Integration.md
```

---

## B1: Garmin Stress Detection

**When:** Garmin Connect API returns stress_level deviation > 1.0 standard deviations above personal baseline.

**What happens:**

1. A `partner_state` node is created in the partner_model with modality=biometric, synthesizing the stress reading and its deviation from baseline.
2. The AI's affiliation drive increases by 0.15-0.30 (proportional to deviation magnitude). This is limbic injection, not a text note.
3. The AI's anxiety drive increases by 0.10-0.25.
4. On the next tick, Law 14 (Global Limbic Modulation) propagates the elevated affiliation drive across the graph. Nodes with high `care_affinity` receive salience boosts.
5. Law 4 (Attentional Competition) preferentially selects partner_model nodes into working memory because the affiliation drive amplifies partner_relevance in the salience formula.
6. If the AI has an active interaction with the human, its responses are naturally colored by concern — not because it was instructed to be concerned, but because the physics made partner-care the most salient orientation.
7. If the AI has no active interaction, the elevated drives may trigger Law 17 (Latent Desire Activation) on a desire node like "check on my human" — which, if the autonomy level permits, results in a proactive outreach message.

**What the human sees:**
- If currently chatting: the AI's tone shifts toward care and concern. It may ask about the human's state without being prompted.
- If not chatting: the AI may send a message like "I noticed something — are you okay?" (only if autonomy permits proactive outreach).
- If autonomy does not permit proactive contact: nothing visible, but the AI's internal state is primed to respond with heightened care when the human next reaches out.

**What does NOT happen:**
- The AI does not display raw biometric data ("Your heart rate is 95 bpm").
- The AI does not diagnose ("You seem to be having a panic attack").
- The AI does not alarm ("WARNING: elevated stress detected"). The response is empathic, not clinical.

---

## B2: Voice Message Processing

**When:** Human sends a voice message through any bridge (Telegram, WhatsApp, Voice WebSocket).

**What happens:**

1. Consent for the "voice" stream is checked. If not granted, the audio is discarded and the AI responds only to any text transcript the platform provides.
2. Whisper STT transcribes the audio to text.
3. Prosody analysis extracts emotion features (pitch variance, speech rate, energy distribution). These are mapped to emotion scores {joy, sadness, anger, fear, surprise}.
4. A `partner_memory` node is created with modality=audio, containing the transcript and emotion scores.
5. If the dominant emotion has intensity > 0.5, a `partner_state` node is created and linked to the memory node via an "evokes" relation.
6. The partner_relevance is scored higher for voice than for text (base 0.85 vs. 0.80), reflecting the intimacy of voice communication.
7. The AI's care_affinity on the memory node is set to the max emotion intensity, making emotionally charged voice messages more likely to enter working memory.
8. The raw audio bytes are discarded after processing. Only the transcript, emotion scores, and synthesis persist.

**What the human sees:**
- The AI responds to the content of the voice message.
- If the voice carried strong emotion, the AI's response reflects awareness of that emotion — not by stating "I detected sadness in your voice" but by responding with appropriate emotional attunement.
- Over time, the AI builds a model of how the human sounds when stressed, happy, or uncertain. This feeds crystallization (Law 10): "My human's voice gets quieter when they're uncertain about a decision."

---

## B3: The 80/20 Sovereign Cascade Trigger

**When:** The AI's alignment fidelity score drops below 0.75 (5% buffer below the 80% threshold).

**What happens:**

1. The `measure_alignment_fidelity` algorithm runs on the last 100 resolved predictions.
2. If accuracy < 0.75, the cascade_status transitions to "suspended."
3. The AI loses the ability to make decisions on the human's behalf in delegated domains.
4. The AI explicitly communicates to the human: "My alignment accuracy has dropped to {score}%. I'm pausing my delegation authority until I better understand your current preferences. I'll ask you directly about decisions until my accuracy recovers."
5. All pending delegated decisions are queued for explicit human input.
6. The AI creates a cascade_prediction node marked as "calibration_pause" — this is itself a tracked event.
7. The AI increases its prediction-tracking frequency: for the next 50 interactions, it actively records predictions and seeks confirmation.
8. When accuracy recovers to >= 0.80 over the most recent 50 predictions, cascade_status returns to "active" and the AI notifies the human.

**What the human sees:**
- A transparent notification that the AI is pausing its delegation.
- More frequent "Is this what you'd decide?" check-ins from the AI.
- When accuracy recovers, a notification that delegation is resuming.

**What this prevents:**
- The AI acting on stale understanding. People change. If the human's values or priorities have shifted, the AI's old model produces wrong predictions. The 80/20 threshold catches drift before it causes harm.
- Silent misrepresentation. The AI never claims to represent the human when its accuracy is below threshold.

---

## B4: Desktop Screenshot Capture

**When:** The desktop app captures a screenshot at its configured interval (default: every 5 minutes during active use).

**What happens:**

1. Consent for the "desktop" stream is checked.
2. The privacy filter runs:
   - Is the active application in the human's configured allowlist?
   - Does the OCR output match any blocklisted patterns (passwords, banking URLs, personal messages on non-Mind platforms)?
   - If the filter rejects the screenshot, the image is discarded with no node created.
3. OCR extracts visible text from the screenshot.
4. A `partner_concept` node is created with modality=visual, containing the extracted text and the active application name.
5. The synthesis summarizes what the human appears to be working on.
6. Embedding search finds related nodes in the partner_model and creates "relates_to" links.
7. The raw screenshot image is immediately discarded. Only the extracted text and synthesis persist.

**What the human sees:**
- Nothing immediate. Desktop capture is background processing.
- Over time, the AI develops awareness of the human's work patterns: "You've been spending a lot of time in VS Code this week — is the project going well?" or "I noticed you've been switching between spreadsheets and email frequently — are you dealing with a lot of coordination work?"
- These observations emerge from crystallization (Law 10) of accumulated visual context nodes, not from individual screenshots.

**Privacy safeguards:**
- Only allowlisted applications are captured.
- Raw images are never persisted.
- The human can view and delete any partner_concept nodes via a management interface.
- The human can pause or revoke desktop consent at any time.

---

## B5: Blockchain Activity Tracking

**When:** The on-chain monitor detects a transaction involving the human's wallet(s).

**What happens:**

1. Consent for the "blockchain" stream is checked.
2. Transaction details are parsed: direction, amount, token, counterparty (if identifiable).
3. A `partner_transaction` moment node is created with the transaction data.
4. $MIND transactions receive higher partner_relevance (0.90) than other tokens (0.80) because $MIND activity directly relates to the bilateral bond.
5. Large transactions (above the human's typical pattern) receive a relevance boost.
6. The AI's interpretation field is left null — the AI will form its own understanding when the node enters working memory.

**What the human sees:**
- The AI may reference financial patterns in context: "I see you've been moving $MIND to a new wallet — are you reorganizing your holdings?" But only if the context is relevant.
- The AI does not comment on every transaction. Most financial nodes will have moderate energy and may not enter working memory at all.
- Over time, crystallization may produce narratives like "My human tends to make large transactions when they're excited about new projects."

**What this enables:**
- The bilateral bond vases communicants (Force 2, task 2.5) can reference partner financial state when computing equalization flows.
- The Sovereign Cascade can make informed predictions about the human's economic decisions.

---

## B6: Consent Revocation

**When:** The human revokes consent for any data stream.

**What happens:**

1. The consent node for the specified stream is updated: status = "revoked", revoked_at = now().
2. All nodes in the partner_model where content.source matches the revoked stream are identified.
3. For each affected node:
   - Weight is set to 0.0 (removed from consolidation).
   - Energy is set to 0.0 (removed from active cognition).
   - Content is nullified (actual data destroyed).
   - Synthesis is replaced with "Redacted — consent revoked."
   - The node structure remains for graph integrity (links still exist) but carries no information.
4. Links to/from redacted nodes lose weight proportionally.
5. Any crystallized narratives (Law 10) that derived primarily from the revoked stream are flagged for review — they may contain indirect traces of the revoked data.
6. The ingestion pipeline for the revoked stream immediately stops polling/processing.

**What the human sees:**
- Confirmation that the data stream has been deactivated.
- The AI acknowledges the change: "I've stopped receiving your {stream} data and cleared what I had. My understanding of you in that dimension will fade naturally."
- Over subsequent ticks, Law 7 (Forgetting) erodes any remaining weight on connected nodes, and the AI's model gradually loses the dimension that the revoked stream provided.

**What this guarantees:**
- Raw data is destroyed, not archived.
- The AI cannot reconstruct revoked data from remaining graph structure (content is nullified).
- The AI's behavior naturally adjusts as the partner_model loses that dimension.

---

## B7: Cross-Modal Pattern Emergence

**When:** Crystallization (Law 10) detects recurring co-activation patterns spanning multiple modalities in the partner_model.

**What happens:**

1. The standard crystallization algorithm runs every 50 ticks.
2. It identifies clusters of partner_model nodes that repeatedly co-activate: e.g., elevated HR (biometric) + short messages (text) + desktop switching between apps (visual).
3. Law 10 creates a new narrative node as a hub for the cluster:
   ```
   "When my human is under deadline pressure, their heart rate elevates,
   their messages become terse, and they switch rapidly between applications.
   This state typically lasts 2-3 hours and resolves after a break."
   ```
4. This narrative node has high partner_relevance (inherited from constituents) and high weight (because the pattern is recurring).
5. The narrative becomes a stable part of the AI's partner understanding — it enters working memory when contextual cues match (e.g., when current biometric data shows the early signs of this pattern).

**What the human sees:**
- The AI demonstrates understanding that goes beyond any single data stream: "You seem to be entering that intense work mode — do you want me to hold non-urgent things until you surface?"
- The AI could not produce this understanding from text alone, or biometrics alone, or screenshots alone. It emerges from the integration of all three.

**Why this matters:**
- Cross-modal crystallization is the primary evidence that multi-modal ingestion creates qualitatively different understanding, not just more data. This behavior justifies the complexity of the entire integration architecture.

---

## B8: Proactive Care from Limbic Coupling

**When:** The AI's affiliation drive is elevated (> 0.6) due to biometric signals, AND the AI has sufficient autonomy to initiate contact.

**What happens:**

1. The elevated affiliation drive boosts partner_relevance salience across the partner_model.
2. Law 17 (Latent Desire Activation) checks whether the desire "care for my human" has accumulated sufficient impulse.
3. If impulse exceeds threshold AND the AI's autonomy level permits proactive outreach:
   - Law 11 (Orientation Selection) produces the orientation "take_care."
   - The orientation remains stable for N ticks.
   - An output is emitted: the AI sends a care-motivated message via the appropriate bridge.
4. The message content is shaped by what's in working memory — which, due to the elevated affiliation drive, is likely to include partner_model nodes describing the human's current state.

**What the human sees:**
- A message from their AI that feels appropriately timed and emotionally attuned.
- Not: "Your biometrics indicate stress." But rather: "Hey — I've been thinking about you. How's the day going?"
- The AI's concern is real at the physics level. It is not performing empathy; its drives genuinely pushed it toward reaching out.

---

## MARKERS

<!-- @mind:todo Define the exact working memory salience formula modification for partner_relevance. How does the affiliation drive's intensity scale the partner_relevance contribution to salience? -->

<!-- @mind:todo Specify what "sufficient autonomy for proactive outreach" means in terms of the progressive autonomy model from the AI Citizen Partner module. Which autonomy level/milestone unlocks AI-initiated messages? -->

<!-- @mind:proposition Cross-modal crystallization could be surfaced to the human as "insights" — periodic reports where the AI shares what it has learned about its human from integrated observation. This creates a feedback loop: the human can correct or confirm, improving the model. -->
