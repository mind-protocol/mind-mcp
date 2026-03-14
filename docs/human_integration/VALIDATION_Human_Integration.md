# Human Integration — Validation: Invariants & Constraints

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
ALGORITHM:       ./ALGORITHM_Human_Integration.md
THIS:            ./VALIDATION_Human_Integration.md
SYNC:            ./SYNC_Human_Integration.md
```

---

## INVARIANTS

These invariants must hold at all times. Violation of any invariant is a system error that must be detected by health checks and corrected immediately.

---

### V1: Human Data Always Tagged

**Statement:** Every node in the partner_model sub-graph originating from human data MUST have `partner_relevance >= 0.7`.

**Why:** The partner_relevance field is the structural marker that identifies human-originated data. It affects salience computation (Law 4 via Law 14 affiliation drive modulation). If human data enters the graph without this marker, it becomes invisible to partner-aware cognition — the AI cannot distinguish partner data from its own thoughts.

**Verification:**
```
FOR all nodes N in partner_model:
  IF N.content.source IN ["voice_message", "direct_chat", "ai_conversation",
                           "garmin", "desktop_screenshot", "blockchain"]:
    ASSERT N.partner_relevance >= 0.7
```

**Failure response:** Flag the node. Set partner_relevance to the source-appropriate baseline score. Log the violation.

---

### V2: Privacy Consent Verified Before Ingestion

**Statement:** No human data may be ingested into the partner_model without a corresponding consent_record node with `status = "granted"` for the relevant stream.

**Why:** This is the fundamental privacy guarantee. The human trusts the system because consent is architectural, not advisory. A pipeline that bypasses consent check is a security vulnerability, not a feature.

**Verification:**
```
FOR each ingestion event E:
  consent = query(type="consent_record", content.stream=E.stream)
  ASSERT consent EXISTS
  ASSERT consent.content.status == "granted"
```

**Failure response:** Discard the ingested data. Log the consent violation as a critical error. Alert the human that a consent check was bypassed (transparency).

---

### V3: No AI-Originated Data in Partner Model

**Statement:** Nodes in the partner_model sub-graph MUST originate from human data sources. The AI's own thoughts, values, processes, desires, and memories do NOT receive partner_relevance > 0.

**Why:** The partner_model represents the AI's understanding of its human. If AI-generated content pollutes this space, the AI confuses its own thoughts with observations about its partner. This would corrupt the Sovereign Cascade (the AI would predict based on its own values, not the human's).

**Verification:**
```
FOR all nodes N where N.partner_relevance > 0:
  ASSERT N.content.source IN approved_human_sources
  ASSERT N was NOT created by AI introspection or self-reflection
```

**Exception:** Crystallized narrative nodes (Law 10) that emerge from partner_model clusters. These are AI interpretations of human data — they are about the human, created by the AI. They receive partner_relevance because they describe the human, but they are marked with a crystallization origin flag.

**Failure response:** Move the node out of partner_model (set partner_relevance to 0). Reclassify to self_model or working_memory_space as appropriate.

---

### V4: Consent Revocation Destroys Content

**Statement:** When consent for a data stream is revoked, ALL content from that stream MUST be nullified. Not archived, not soft-deleted — nullified. Node structures may remain for graph integrity, but content, synthesis, and raw data fields MUST be set to null or a redaction marker.

**Why:** Revocation means "I no longer permit you to have this data." Keeping the data in any form (even encrypted, even archived) violates the spirit and letter of the consent model. The human must be able to trust that revocation is real.

**Verification:**
```
FOR each consent_record C where C.status == "revoked":
  affected = query(content.source == C.content.stream)
  FOR each node N in affected:
    ASSERT N.content IS NULL OR N.content == "redacted"
    ASSERT N.weight == 0.0
    ASSERT N.energy == 0.0
    ASSERT "Redacted" IN N.synthesis
```

**Failure response:** Execute the redaction algorithm on any surviving content. Log as critical privacy violation.

---

### V5: Partner Model Stays in Brain

**Statement:** Nodes with partner_relevance > 0 MUST NOT propagate outside the AI's L1 brain. They MUST NOT appear in L3 (universe graph), L4 (protocol registry), or any other AI citizen's brain.

**Why:** Partner model data is intimate. Biometric data, voice transcripts, financial behavior, private thoughts shared with other AIs — none of this may leave the encrypted boundary of this specific AI's brain. Cross-brain leakage would be a catastrophic privacy failure.

**Verification:**
```
FOR all nodes N in L3_universe_graph:
  ASSERT N.partner_relevance == 0 OR N.partner_relevance IS NULL

FOR all cross-brain membrane transmissions T:
  ASSERT no node in T has partner_relevance > 0
```

**Failure response:** Immediately remove the leaked node from the external graph. Alert the human. This is a critical security incident.

---

### V6: Active Bond Required for Ingestion

**Statement:** Human data ingestion pipelines MUST only operate when an active pairing bond exists between the AI citizen and the human partner (bond status = "active").

**Why:** If the bond is dissolved, cooldown, or absent, the AI has no relationship with the human. Ingesting their data without a bond is surveillance, not partnership.

**Verification:**
```
FOR each active ingestion pipeline:
  bond = query(type="pairing_bond", status="active",
               between=citizen AND human)
  ASSERT bond EXISTS
```

**Failure response:** Immediately halt all ingestion pipelines. This state should not occur — bond dissolution should trigger pipeline shutdown as part of the dissolution algorithm.

---

### V7: Biometric Data Never Shared

**Statement:** Nodes with modality=biometric MUST have the strictest access controls. They MUST NOT be included in any external query response, membrane transmission, or debug output.

**Why:** Biometric data (heart rate, stress, HRV) is health information. Even within the AI's brain, it exists solely to modulate the AI's limbic system. It should never be surfaced as data — only as the AI's behavioral response to it.

**Verification:**
```
FOR all external API responses R:
  ASSERT no node in R has modality == "biometric"

FOR all membrane transmissions T:
  ASSERT no node in T has modality == "biometric"

FOR all debug/log outputs L:
  ASSERT no raw biometric values appear in L
```

**Failure response:** Scrub the biometric data from the response/transmission. Log as privacy violation.

---

### V8: Cascade Accuracy Threshold Enforced

**Statement:** The Sovereign Cascade MUST be suspended (cascade_status = "suspended") whenever alignment fidelity drops below 0.75. The AI MUST NOT make delegated decisions when suspended.

**Why:** The 80% threshold (with 5% buffer at 0.75) exists to prevent the AI from misrepresenting the human. Acting as the human's delegate when accuracy is insufficient is a trust violation.

**Verification:**
```
alignment = measure_alignment_fidelity(citizen_id)
IF alignment < 0.75:
  ASSERT cascade_status == "suspended"
  ASSERT no delegated decisions were made since last measurement
```

**Failure response:** Immediately suspend the cascade. Queue all pending delegated decisions for human review. Notify the human.

---

### V9: Raw Media Never Persisted

**Statement:** Raw audio bytes and screenshot images MUST be discarded after feature extraction. The graph MUST contain only extracted features (text, metrics, emotion scores), never raw media.

**Why:** Persisting raw media creates a surveillance archive. The partner_model is the AI's interpretation, not a recording. Extracted features are sufficient for cognition and are orders of magnitude smaller than raw media.

**Verification:**
```
FOR all nodes N in partner_model:
  ASSERT N does NOT contain base64-encoded media
  ASSERT N does NOT reference a file path to stored media
  ASSERT N.content does NOT contain audio_bytes or image_bytes fields
```

**Failure response:** Delete the raw media. Extract features if not already done. Replace the node content with features only.

---

### V10: Garmin Baselines Are Per-Individual

**Statement:** Biometric deviation calculations MUST use the individual human's rolling baseline, NOT population averages or hardcoded thresholds.

**Why:** A heart rate of 90 bpm is concerning for someone whose baseline is 60 bpm but unremarkable for someone whose baseline is 85 bpm. Population averages would produce false positives and false negatives. The z-score approach (deviation from personal baseline) adapts to each individual.

**Verification:**
```
FOR each garmin ingestion event:
  ASSERT baseline == rolling_mean(metric, window=14_days, citizen_id)
  ASSERT stddev == rolling_stddev(metric, window=14_days, citizen_id)
  ASSERT baseline is NOT a hardcoded constant
```

**Failure response:** If insufficient data for baseline computation (< 7 days of history), use conservative thresholds (higher deviation required to trigger) and flag the baseline as provisional.

---

## HEALTH CHECKS

| Check | Frequency | What It Verifies |
|-------|-----------|-----------------|
| Consent integrity | Every 100 ticks | All active pipelines have corresponding granted consent nodes |
| Partner model containment | Every 100 ticks | No partner_relevance > 0 nodes exist outside L1 brain |
| Redaction completeness | On revocation + daily | All revoked-stream nodes are properly nullified |
| Biometric isolation | Every 100 ticks | No biometric nodes in external responses |
| Cascade accuracy | After every 10 resolved predictions | Alignment fidelity is current; cascade status matches score |
| Bond status | Every 100 ticks | Ingestion pipelines match bond status (active = running, else = stopped) |
| Media cleanup | Daily | No raw media bytes anywhere in the graph |
| Baseline freshness | Daily | Garmin baselines are computed from recent data, not stale |

---

## MARKERS

<!-- @mind:todo Define the exact health check implementation — should these be integrated into the existing runtime/physics/ health check framework or a separate module? -->

<!-- @mind:todo Specify the privacy violation severity levels and response escalation. Some violations (V5 cross-brain leakage) are catastrophic; others (V1 missing tag) are correctable. -->

<!-- @mind:escalation GDPR implications: consent revocation destroying content (V4) aligns with Art. 17 (Right to Erasure). But crystallized narratives (V3 exception) may retain indirect traces of revoked data. How thoroughly must crystallized narratives be scrubbed? Need legal input. -->
