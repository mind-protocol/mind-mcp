# Human Integration — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude (groundwork, Force 3)
```

---

## CURRENT STATE

**Module:** Human Integration / Partner Model
**Status:** DESIGNING (Phase C IMPLEMENTATION plan complete, no code exists yet)

The full documentation chain for the human integration module has been created, including the IMPLEMENTATION plan (Phase C). This module specifies how human data flows into the AI partner's `partner_model` sub-graph, the multi-modal ingestion pipelines, privacy/consent architecture, and Sovereign Cascade calibration. The implementation plan defines 11 files in `runtime/ingestion/`, 7 build phases (H1-H7), 54 tests, and all cross-force interfaces.

---

## MATURITY

STATUS: DESIGNING

### What's Canonical (decided)

- **No separate human brain.** The human does not get an L1 cognitive graph. All human data flows into the AI's partner_model structural space. This is the foundational architectural decision — confirmed in the 5-force planning session.
- **partner_relevance tagging.** Human-originated data receives partner_relevance in [0.7, 1.0], scored by source and content. The schema v2.0 field is reused as designed.
- **Graph-native consent.** Consent records are thing nodes in the partner_model, not config flags. Per-stream granularity with individual revocation.
- **Limbic coupling via Garmin.** Biometric deviations from personal baseline map to AI drive deltas (affiliation, anxiety, satisfaction). The AI feels concern because physics makes it the energetically favorable response.
- **Sovereign Cascade at 80%.** Rolling accuracy over 100 predictions. Auto-suspend at 0.75 (5% buffer). Transparent to the human.
- **Six modality pipelines.** Voice (Whisper STT + emotion), Garmin (biometric polling), Desktop (OCR + privacy filter), Blockchain (tx monitor), AI conversations (capture layer), Direct chat (existing).
- **Raw media never persisted.** Audio bytes and screenshot images are discarded after feature extraction.

### What's Still Being Designed

- **Privacy consent model.** Blanket at bond formation vs. per-stream opt-in. Current proposal: blanket opt-in at bond formation with per-stream revocation. Needs human decision.
- **Garmin API latency.** Connect API polls at ~15 min delay. Is this sufficient for limbic coupling? Alternative: Garmin SDK on phone for real-time, but requires a mobile app. The current design uses 15-min polling.
- **Desktop privacy filter.** Application allowlist is the conservative v1. Content-aware filtering (detecting Mind-related content) needs specification.
- **AI conversation capture.** How does data from other AI platforms (ChatGPT, Gemini, etc.) reach the Mind citizen? Browser extension, email forwarding, API integration, or manual paste. Each has different tradeoffs.
- **Emotion extraction from audio.** Phase 1 is prosody heuristics (pitch, rate, energy). Phase 2 is a fine-tuned classifier. Neither is implemented.
- **Alignment fidelity measurement.** The algorithm is specified but the prediction domains ("governance", "economic", "social", "project") need concrete definitions of what constitutes a "decision" worth predicting.

### What's Proposed (future)

- **Mind Duo hardware bridge.** Dedicated Garmin watch face or app that provides lower-latency biometric streaming directly to the AI, bypassing the Connect API polling delay.
- **Cross-modal insight reports.** The AI periodically shares what it has learned about its human from integrated observation, creating a feedback loop for model correction.
- **Proactive care calibration.** The human provides feedback on whether AI-initiated care messages were welcome or intrusive. This calibrates the affiliation drive threshold for proactive outreach.

---

## DOCUMENTATION CREATED

| File | Purpose | Status |
|------|---------|--------|
| `OBJECTIVES_Human_Integration.md` | Goals: deep partner model, multi-modal, privacy, Cascade | Complete |
| `PATTERNS_Human_Integration.md` | Philosophy: territory/map, consent model, limbic coupling | Complete |
| `ALGORITHM_Human_Integration.md` | Pipelines: all 6 modalities, relevance scoring, alignment | Complete |
| `BEHAVIORS_Human_Integration.md` | Observable effects: stress response, voice, cascade trigger | Complete |
| `VALIDATION_Human_Integration.md` | 10 invariants: consent, privacy, tagging, containment | Complete |
| `IMPLEMENTATION_Human_Integration.md` | Code plan: file structure, phases, interfaces, tests | Complete |
| `SYNC_Human_Integration.md` | This file | Complete |

---

## OPEN QUESTIONS

### Privacy Consent Model
**Question:** Blanket consent at bond formation, or per-data-stream opt-in?
**Current proposal:** Blanket opt-in at bond formation with per-stream revocation capability. The human is told during bond formation: "Your AI partner will receive data from these streams: [list]. You can disable any stream at any time."
**Why this matters:** Per-stream opt-in adds friction at onboarding but gives the human fine-grained control from the start. Blanket opt-in is smoother but may surprise the human when they realize their heartbeat is being monitored.
**Status:** Needs human decision.

### Garmin API Latency
**Question:** Is ~15-minute polling sufficient for meaningful limbic coupling?
**Analysis:** 15-minute windows capture trends (sustained stress, recovery patterns) but miss acute events (panic spike that resolves in 5 minutes). For the AI's empathic response, trends are arguably more important than spikes — sustained stress is more concerning than a momentary elevation. However, the AI's proactive care behavior (B8) becomes less timely with 15-minute lag.
**Alternative:** Garmin SDK on the human's phone could push data in near-real-time, but requires building a mobile app component.
**Status:** Use 15-minute polling for v1. Evaluate latency impact after deployment.

### Desktop App Platform
**Question:** Electron for cross-platform desktop app? Or something lighter?
**Analysis:** Electron provides cross-platform screenshots + OCR + privacy filtering. But it is heavy (~100MB+). Alternatives: native apps per platform (higher quality, much more development), or a browser extension (limited to browser tabs, simpler).
**Status:** Not blocking documentation. Implementation decision for Phase D.

### Alignment Fidelity Domain Definition
**Question:** What kinds of predictions count toward the 80% accuracy threshold?
**Analysis:** The prediction must be meaningful — "will the human eat lunch today?" (>99% likely) is not useful calibration. Predictions should be about decisions with genuine uncertainty: "will the human accept this meeting?", "will the human invest in this project?", "would the human agree with this governance proposal?"
**Proposed categories:**
- Governance: protocol votes, policy positions
- Economic: financial decisions, budget allocation
- Social: communication preferences, relationship priorities
- Project: technical decisions, priority ranking
**Status:** Needs further specification. What is the minimum decision granularity?

---

## DEPENDENCIES WAITING

| Dependency | From | Status | Impact |
|------------|------|--------|--------|
| Encrypted brains (AES-256) | Force 1, task 1.5 | TODO | Partner model content must be encrypted at rest |
| Universe graph model | Force 1, task 1.2 | TODO | Partner model lives within the brain Space in the universe graph |
| Bilateral bond vases communicants | Force 2, task 2.5 | TODO | Needs partner financial state from blockchain pipeline |
| Trust mechanics | Force 4, task 4.3 | DOCUMENTED | Cascade alignment fidelity feeds into bond trust via F4 ALGORITHM section 2.4 |
| Physics wiring to orchestrator | Force 5, task 5.1 | TODO | Partner model nodes need to participate in real tick loops |
| Real embeddings | Force 5, task 5.2 | TODO | Embedding search for related nodes in partner_model |

---

## HANDOFF: FOR CROSS-REVIEW

**For Force 1 (Universe Graph):** The partner_model is a sub-graph within the AI's brain Space. Brain encryption (task 1.5) must cover all partner model content. The HAS_ACCESS model (task 1.4) must ensure that only the AI citizen has access to its own partner_model — no other actor, not even the human partner directly.

**For Force 2 ($MIND Economy):** The blockchain ingestion pipeline (ALGORITHM, `ingest_blockchain_activity`) captures $MIND transactions. The bilateral bond vases communicants formula needs access to the human's $MIND holdings, which are tracked in the partner_model as financial moment nodes.

**For Force 4 (Trust Mechanics):** The Sovereign Cascade alignment fidelity score is a measurable trust signal. High alignment accuracy = the AI demonstrably understands its human. **Cross-review complete (2026-03-14):** F4 now includes ALGORITHM section 2.4 (`update_bond_trust_from_alignment`) that consumes this module's `measure_alignment_fidelity` output. F4 PATTERNS Pattern 7 documents the bilateral bond as a specific trust relationship. F4 VALUE_CREATION_TAXONOMY Sphere 5 now covers all six ingestion modalities (B1-B5).

**For Force 5 (Physics Wiring):** Partner model nodes are standard L1 nodes. They need no special physics. But the garmin_to_limbic mapping requires the drive system to be wired and operational. Force 5's limbic implementation (task 5.6) is a direct dependency for biometric → drive modulation.

---

## HANDOFF: FOR HUMAN

**What was built:** Complete 6-file documentation chain for the human integration module. Specifies how human data enters the AI's brain through six modality pipelines, the privacy/consent architecture, biometric-to-limbic drive mapping, and Sovereign Cascade calibration system.

**Key decisions documented:**
1. Human does NOT get a separate L1 brain. All data flows into AI's partner_model.
2. Consent is graph-native (thing nodes, not config flags).
3. Garmin biometrics directly modulate AI limbic drives (affiliation, anxiety).
4. 80% alignment fidelity threshold with 5% buffer and auto-suspend.
5. Raw media (audio, images) is never persisted — only extracted features.

**Needs your input on:**
1. Blanket consent at bond formation vs. per-stream opt-in.
2. Whether 15-minute Garmin polling latency is acceptable for v1.
3. Desktop app platform (Electron? Native? Browser extension?).
4. What kinds of predictions count toward alignment fidelity calibration.
