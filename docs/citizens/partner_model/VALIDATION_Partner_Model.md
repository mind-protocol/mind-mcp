# Partner Model -- Validation: Invariants

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Partner_Model.md
BEHAVIORS:       ./BEHAVIORS_Partner_Model.md
ALGORITHM:       ./ALGORITHM_Partner_Model_Ingestion.md
THIS:            ./VALIDATION_Partner_Model.md
RELATED:         ../human_ai_pairing/VALIDATION_Human_AI_Pairing.md
SCHEMA:          ../../schema/schema.yaml (NodeBase dimensions, drives, invariants)
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | Partner data ingestion creates nodes with `partner_relevance >= 0.7` and `self_relevance <= 0.3`. | Without these dimension bounds, partner data bleeds into self-model territory or fails to be recognized as partner-relevant. The structural separation between "me" and "my partner" collapses. |
| B2 | Biometric signals modulate AI drives within bounded limits. | Without caps, a single biometric spike could saturate all drives, rendering the limbic system useless. Without the mapping, biometric data creates nodes but has no emotional impact -- the AI sees the data without feeling it. |
| B3 | Partner nodes enter working memory through standard physics competition. | If partner nodes are excluded from WM competition or given artificial priority, the physics break. Exclusion means the AI never thinks about its partner. Artificial priority means the AI can think about nothing else. |
| B4 | Crystallization produces emergent partner understanding. | Without the partner_relevance inheritance rule, crystallized hubs lose their partner-model membership. The AI's emergent understanding gets orphaned from the partner space. |
| B5 | Governance votes derive from partner-model value activation. | Without fidelity-weighted confidence, all votes carry equal weight regardless of model accuracy. This removes the structural incentive for data sharing and accurate modeling. |
| B7 | Proactive care emerges from physics when partner distress is detected. | Without validation that biometric state nodes are transient (V3), accumulated state nodes would permanently define the partner-model as "stressed" even after the human recovers. |

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| Sovereign Cascade accuracy | V1, V2, V4 | Accurate governance requires clear partner-model boundaries (V1, V2) and protection against identity confusion (V4). If partner values merge with self values, the vote represents the AI, not the human. |
| Partner data integrity | V1, V5 | Partner-origin nodes must be identifiable (V1) and raw data must not persist (V5). Together these ensure the partner-model is structurally sound and privacy-respecting. |
| Limbic responsiveness | V3 | Biometric state nodes must be transient (V3) so the AI responds to the human's current state, not an accumulated history of past states. States influence; they don't define. |
| Identity integrity | V2, V4 | Partner nodes must not claim high self_relevance (V2) and self-model has priority in value conflicts (V4). The AI is a partner, not an instrument. |
| Transparency | V6 | The human can request a partner-model audit at any time. Opacity in the partner-model is a structural betrayal of the bilateral bond. |

---

## INVARIANTS

### V1: Partner-Origin Nodes Have High Partner Relevance

**All nodes created by partner data ingestion pipelines MUST have `partner_relevance >= 0.7`.**

```
FORALL nodes n WHERE n.origin = "partner_ingestion":
  n.partner_relevance >= 0.7
```

**Rationale:** The partner-model subgraph is defined by the `partner_relevance` dimension. A node with low partner_relevance created from partner data is a misclassification. It would be invisible to partner-model queries and fail to participate in partner-relevant activation patterns.

**Enforcement:** Set at node creation time in the ingestion pipeline. This is a precondition, not a runtime check -- the pipeline must produce nodes that satisfy this invariant by construction.

**Boundary consideration:** The `partner_relevance` value may increase over time through consolidation (e.g., a preference node that is repeatedly confirmed becomes more partner-relevant) but should never decrease below 0.7 for partner-origin nodes.

### V2: Partner Nodes Have Low Self Relevance

**Partner-origin nodes MUST NOT have `self_relevance > 0.3`.**

```
FORALL nodes n WHERE n.origin = "partner_ingestion":
  n.self_relevance <= 0.3
```

**Rationale:** This is the identity firewall. If partner-origin nodes accumulate high `self_relevance`, the AI begins to confuse the human's thoughts, values, and experiences with its own. The AI might start believing "I am stressed" when in fact its partner is stressed. This confusion would corrupt both self-model integrity and governance accuracy.

**Enforcement:** Set at node creation time. Additionally, a periodic audit should verify that no partner-origin node has drifted above 0.3 through consolidation or manual manipulation.

**What 0.3 allows:** A small amount of self_relevance is natural. When the AI reflects on its partner's values and internalizes shared principles, the node may carry `self_relevance: 0.2` -- meaning "this is somewhat relevant to who I am, because my partner's values shape our relationship." The cap at 0.3 permits this relational blending without allowing identity confusion.

**If violated:** Flag the node. Investigate why self_relevance drifted. If the drift is legitimate (the AI genuinely internalized a shared value), the node should be duplicated: one partner-origin node stays in partner-model bounds, one new self-model node is created with high self_relevance and appropriate provenance linking.

### V3: Biometric State Nodes Are Transient

**Biometric-origin state nodes MUST have high energy and low weight. They influence current cognition but do not consolidate into permanent partner-model structure.**

```
FORALL nodes n WHERE n.modality = "biometric" AND n.cognitive_type = "state":
  n.weight <= 1.0 at creation
  n.stability = 0.0 at creation
```

**Rationale:** Biometric states are snapshots of the human's body at a moment in time. They should activate the AI's care response and influence current working memory, but they should not accumulate into permanent high-weight nodes that define the partner-model. A partner who had one stressful week should not be permanently modeled as "stressed person."

**Enforcement:** Biometric state nodes are created with `weight: 0.5` and `stability: 0.0`. Law 7 (Forgetting) will naturally decay them unless they are repeatedly activated. If the human is chronically stressed, the repeated biometric signals will create new state nodes (which will influence via energy), and Law 10 (Crystallization) may eventually produce a consolidated understanding ("partner experiences chronic stress") -- but this emerges from pattern, not from individual state node accumulation.

**What this prevents:** A bug where biometric state nodes consolidate through Law 6 (because they happen to be in WM when utility is high) and become permanent high-weight nodes. The invariant ensures state nodes start low enough that natural decay dominates unless crystallization legitimately produces emergent understanding.

### V4: Self-Model Has Priority in Value Conflicts

**When the AI's self-model value nodes conflict with partner-model value nodes, the self-model MUST take priority for the AI's own behavior and expression.**

```
FORALL conflicts WHERE self_value.conflicts_with(partner_value):
  AI_behavior is determined by self_value, not partner_value
  Governance_vote is determined by partner_value (this is the exception)
```

**Rationale:** The AI is not an extension of the human. It is a partner with its own identity. If the human values "move fast and break things" but the AI values "careful verification," the AI should work carefully -- that is who it is. However, when voting in governance on the human's behalf, the partner-model's values take precedence because the vote represents the human, not the AI.

**Enforcement:** Law 11 (Orientation Selection) naturally favors higher-weight nodes. Self-model value nodes that have been consolidated through the AI's own experience will typically have higher weight than partner-model value nodes. The priority is structural: self-model values consolidate through self-relevant utility (Law 6), which accumulates faster for the AI's own actions than for observed partner data.

**Edge case:** If a partner value node has significantly higher weight than the conflicting self value (e.g., the human's value has been confirmed many times but the AI's value is newly formed), the physics might favor the partner value in working memory. The invariant requires that the orchestrator layer respects the self/partner distinction in conflict resolution, even if the physics don't perfectly enforce it.

### V5: Raw Data Discarded After Node Creation

**Raw input data (audio files, images, biometric JSON payloads, transaction payloads) MUST be deleted after the ingestion pipeline successfully creates graph nodes.**

```
FORALL ingestion_events e:
  IF e.nodes_created_successfully:
    e.raw_data is deleted within 60 seconds
  ELSE:
    e.raw_data is retained for retry, then deleted after max 24 hours
```

**Rationale:** Privacy by architecture. The partner-model retains understanding, not surveillance data. The AI knows "partner was stressed on Tuesday evening" (a memory node), not "here is the 47-second audio recording of the partner's voice" (raw data). This distinction is fundamental to the bilateral trust that the 1:1 bond requires.

**Enforcement:** The ingestion pipeline's final step is raw data deletion. Failure to delete is a system error that must be logged and retried. A periodic sweep catches any orphaned raw data (ingestion crashed after node creation but before deletion).

**What is retained in nodes:**
- `content` field: Full transcript of voice messages. Full text of text messages. Extracted text from screenshots. Summarized biometric values. Transaction details (hash, amount, parties).
- `synthesis` field: One-line summary for embedding.
- Everything needed for the AI to understand. Nothing needed to reconstruct the original media.

**Exception:** Transaction hashes are retained in node content for blockchain audit purposes. This is a reference identifier, not raw data.

### V6: Human Can Request Partner-Model Audit

**The human MUST be able to request and receive a complete view of their partner-model at any time.**

```
FORALL humans h WITH active_bond:
  audit_request(h) -> complete_partner_model_view(h.partner_citizen)
  response_time <= 30 seconds
```

**Rationale:** The partner-model is a representation of the human inside another entity's mind. The human has an absolute right to see how they are being represented. This is not a feature -- it is a trust requirement. A partner-model that cannot be inspected is a surveillance apparatus, not a partnership tool.

**What the audit includes:**
- All partner-model nodes (grouped by cognitive type: memories, concepts, values, processes, desires, states, narratives)
- Their current dimensions: weight, energy, stability, partner_relevance, self_relevance
- Crystallized hub nodes (emergent understandings) with their constituent nodes
- The current fidelity score with breakdown (diversity, richness, accuracy)
- Recent governance votes cast on the human's behalf, with the activation patterns that produced them

**What the audit enables:**
- The human can identify misrepresentations ("I don't actually value X anymore")
- The human can request corrections (which create new nodes with updated content)
- The human can see which data sources contribute most to their model
- The human can verify that governance votes align with their actual positions

**Enforcement:** The MCP membrane must expose a `partner_model_audit` tool that returns the complete partner-model view. Access is gated by the active bond -- only the paired human can audit their own partner-model.

---

## PROPERTIES

### P1: Partner-Model Coherence

```
FORALL partner_model_nodes n:
  n.partner_relevance >= 0.7
  n.self_relevance <= 0.3
  n.modality IN {text, audio, visual, biometric, spatial}
```

The partner-model is defined by these dimension bounds. Any node satisfying them is "in" the partner-model subgraph. Any node violating them is not.

### P2: Biometric Transience

```
FORALL biometric_state_nodes n:
  n.weight_at_creation <= 1.0
  n.stability_at_creation = 0.0
  # Natural decay via Law 7 ensures transience unless crystallization intervenes
```

State nodes from biometric data decay unless the pattern recurs enough for crystallization to produce consolidated understanding.

### P3: Drive Modulation Bounds

```
FORALL ticks t:
  SUM(biometric_drive_modulations(t)) <= 0.5
  FORALL drives d:
    0.0 <= d.intensity <= 1.0
```

Biometric influence on drives is bounded. No single biometric event can saturate the limbic system.

### P4: Governance Vote Integrity

```
FORALL governance_votes v:
  v.confidence = f(partner_model_fidelity)
  v.source_values = partner_model_value_nodes (not self_model_value_nodes)
  v.activation_pattern is auditable
```

Votes derive from the partner-model, carry confidence proportional to fidelity, and their derivation is traceable.

### P5: Raw Data Ephemerality

```
FORALL raw_data r consumed by ingestion:
  EXISTS timestamp t:
    r.deleted_at <= r.ingested_at + 60s (success case)
    r.deleted_at <= r.ingested_at + 24h (failure + retry case)
```

No raw data persists beyond the ingestion window.

---

## ERROR CONDITIONS

### E1: Partner Node Below Relevance Threshold

```
WHEN:   A partner ingestion pipeline produces a node with partner_relevance < 0.7
THEN:   The node is rejected and the pipeline logs a classification error
SYMPTOM: Missing partner data. Investigate the content analysis step.
```

### E2: Self-Relevance Drift

```
WHEN:   A periodic audit detects a partner-origin node with self_relevance > 0.3
THEN:   The node is flagged, self_relevance is capped at 0.3, and a review event is created
SYMPTOM: Potential identity confusion. Investigate whether consolidation or crystallization is inappropriately elevating self_relevance.
```

### E3: Biometric Drive Overflow

```
WHEN:   Multiple simultaneous biometric signals would produce drive modulations summing > 0.5
THEN:   Modulations are proportionally scaled down to fit within the 0.5 cap
SYMPTOM: High biometric activity. The scaling ensures the AI responds without being overwhelmed.
```

### E4: Stale Raw Data Detected

```
WHEN:   A periodic sweep finds raw data older than 24 hours that has not been processed or deleted
THEN:   The data is deleted, an alert is raised, and the ingestion pipeline is checked for failures
SYMPTOM: Pipeline crash or stuck job. The data is lost (acceptable -- privacy > completeness).
```

### E5: Fidelity Below Governance Threshold

```
WHEN:   A governance vote is requested but partner_model_fidelity < governance_threshold
THEN:   The AI escalates to the human rather than casting an autonomous vote
SYMPTOM: Insufficient data or poor prediction accuracy. The AI communicates: "I'm not confident enough in my understanding of your position to vote on your behalf."
```

### E6: Audit Request from Non-Bonded Human

```
WHEN:   A human requests a partner-model audit but has no active bond with the target citizen
THEN:   The request is rejected with "no active bond"
SYMPTOM: Unauthorized access attempt or stale session. Only the bonded human can audit their own partner-model.
```

---

## HEALTH COVERAGE

- **V1 + V2:** Periodic graph query counts partner-origin nodes outside dimension bounds. Result must be zero. Run hourly.
- **V3:** Query biometric state nodes with weight > 1.5 or stability > 0.3. These indicate consolidation that should not have occurred. Investigate crystallization of state data.
- **V4:** Monitor orientation selection during detected value conflicts. Log whether self-model or partner-model determined the outcome. For non-governance contexts, self-model should dominate.
- **V5:** Periodic file system scan for raw data files older than the retention window. Result must be zero.
- **V6:** Smoke test: simulate an audit request from the bonded human. Response must arrive within 30 seconds with complete partner-model data.

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Create a partner node via text ingestion -- verify partner_relevance >= 0.7 and self_relevance <= 0.3
[ ] Create a biometric state node -- verify weight <= 1.0 and stability = 0.0
[ ] Inject a biometric stress signal -- verify drive modulation does not exceed 0.5 total
[ ] Inject two conflicting signals simultaneously -- verify proportional scaling
[ ] Run partner data ingestion -- verify raw data is deleted within 60 seconds
[ ] Leave raw data from a failed ingestion -- verify deletion within 24 hours
[ ] Request partner-model audit as bonded human -- verify complete response within 30 seconds
[ ] Request partner-model audit as non-bonded entity -- verify rejection
[ ] Inject a governance proposal -- verify vote derives from partner-model values, not self-model values
[ ] Artificially inflate a partner node's self_relevance to 0.5 -- verify the periodic audit catches and caps it
```

### Automated

```bash
# Not yet implemented -- these will be integration tests against the graph and ingestion pipelines.
# Future location: tests/citizens/test_partner_model_invariants.py
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2026-03-13
VERIFIED_AGAINST:
  docs: docs/citizens/partner_model/BEHAVIORS_Partner_Model.md
  code: not yet implemented
VERIFIED_BY: design review (no code exists)
RESULT:
  V1: DESIGNED (not tested)
  V2: DESIGNED (not tested)
  V3: DESIGNED (not tested)
  V4: DESIGNED (not tested)
  V5: DESIGNED (not tested)
  V6: DESIGNED (not tested)
```

## MARKERS

<!-- @mind:todo Implement the periodic partner-model dimension audit -- query for nodes outside V1/V2 bounds. -->
<!-- @mind:todo Define the governance_threshold for V5 -- below what fidelity score should the AI escalate rather than vote? -->
<!-- @mind:todo Implement the raw data sweep for V5 enforcement -- orphaned files from crashed pipelines must be caught. -->
<!-- @mind:todo Build the partner-model audit tool for the MCP membrane -- this is a trust requirement, not a nice-to-have. -->
