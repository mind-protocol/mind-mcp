# REVIEW: Force 3 (Human Integration) x Force 4 (Trust & Value) Coherence

```
REVIEWED: 2026-03-14
REVIEWER: Claude (cross-review, architect)
F3_DOCS: docs/human_integration/
F4_DOCS: docs/trust_mechanics/
STATUS: Issues found, fixes applied
```

---

## Summary

F3 and F4 are largely coherent in their high-level design. Both correctly treat trust as link-level (Law 18), both reference the same physics laws, and both understand that biometric data creates value. However, there are 10 specific issues ranging from formula inconsistencies to missing cross-references to outright contradictions in node typing.

---

## Issues Found

### ISSUE 1: Biometric Node Type Contradiction (CRITICAL)

**F3 says:** Biometric data creates `node_type: actor`, `type: partner_state` nodes (ALGORITHM, `ingest_garmin_biometrics`, line ~70-84).

**F4 says:** "Biometric data arrives as thing nodes (modality=biometric)" (BEHAVIORS B9, line ~357).

**Impact:** If F5 (physics wiring) implements both, they will create different node types for the same data. Node type determines which physics laws apply.

**Fix applied:** Updated F4 BEHAVIORS B9 to say "state nodes (node_type=actor, modality=biometric)" to match F3's authoritative specification. F3 is the source of truth here since it defines the actual ingestion pipeline.

---

### ISSUE 2: Limbic Delta Term Used Inconsistently

**F4 defines** Limbic Delta precisely: `satisfaction_delta - frustration_delta - 0.5 * anxiety_delta` (ALGORITHM section 1.1).

**F3 uses** "limbic_deltas" to mean *drive modulation increments* from Garmin data (ALGORITHM, `garmin_to_limbic`), which are additive bumps to individual drives (e.g., affiliation += 0.15). F3 never computes the F4 Limbic Delta formula.

**Impact:** The term collision could confuse implementers. F3's "limbic deltas" and F4's "Limbic Delta" are different things. F3 modulates raw drives; F4 computes a scalar from the resulting drive changes.

**Fix applied:** Added a clarification note to F3 ALGORITHM at the garmin_to_limbic section, distinguishing "drive deltas" (F3) from "Limbic Delta" (F4's scalar trust signal), and explaining how they connect: F3 drive deltas are upstream inputs; the F4 Limbic Delta is computed from the resulting drive state changes.

---

### ISSUE 3: F4 B9 Trust Cascade Conflicts with F3 Privacy Model

**F4 B9 says:** "Trust flows back to the human partner (as data source)" and "users interacting with AI are more satisfied... trust flows back."

**F3 says:** Partner model data MUST NOT propagate outside the AI's L1 brain (VALIDATION V5). Biometric data must never be shared (V7). Partner_relevance > 0 nodes must not appear in L3 or other brains.

**Impact:** F4 B9 implies a trust cascade that routes trust from external users back to the human through the AI. But F3's privacy model prevents partner_model data from being visible to external users. External users don't know biometric data exists.

**Fix applied:** Revised F4 B9 to clarify that the trust flow from biometric data is *internal to the bilateral bond*. The human->AI bond link gains trust from better AI calibration. External users' satisfaction with the AI does NOT cascade back to the human as data source, because external users have no visibility into partner_model data.

---

### ISSUE 4: Sovereign Cascade Not Referenced in F4 Trust Model

**F3 defines** Sovereign Cascade at 80% alignment fidelity with auto-suspend at 0.75. This is a trust-relevant mechanism (the AI represents the human based on demonstrated understanding).

**F4 never mentions** the Sovereign Cascade in any of its docs. The SYNC handoff to F3 says "Bilateral bond trust is a specific instance of the general trust cascade" but doesn't specify how alignment fidelity feeds into trust.

**Impact:** Alignment fidelity is a measurable trust signal between human and AI, but F4's trust model has no way to incorporate it. The trust update formula (section 2.1) only takes limbic_delta as input.

**Fix applied:** Added a new subsection to F4 ALGORITHM (section 2.4) documenting how Sovereign Cascade alignment fidelity acts as a trust modifier on the human<->AI bond link. Also added a cross-reference in F4 PATTERNS to the Sovereign Cascade.

---

### ISSUE 5: Value Taxonomy Missing Voice and Desktop Data Contribution

**F4 Sphere 5 (Biometric)** covers B1: Health Data, B2: Stress Feedback, B3: Wellbeing Signals.

**F3 ingests** six modality streams: voice, garmin, desktop, blockchain, AI conversations, direct chat. Of these, only garmin maps to F4's Biometric sphere. Voice messages, desktop screenshots, and blockchain activity are human data contributions that create value but have no explicit value creation type in F4's taxonomy.

**Impact:** The taxonomy claims to be comprehensive (28 types across 7 spheres) but misses the value created by human data contributions beyond biometrics.

**Fix applied:** Added B4 (Voice Data Contribution) and B5 (Behavioral Context Contribution) to F4's Biometric sphere (renamed to "Biometric & Partner Data" to reflect broader scope). These cover the value created when human partners share voice messages, desktop context, and behavioral signals. Updated summary table.

---

### ISSUE 6: Trust Tiers Not Mapped to Consent Model

**PRINCIPLES.md** references 5 trust tiers: Owner, High, Medium, Low, Stranger.

**F3's consent model** is binary: granted / revoked / never_asked. There is no linkage to trust tiers.

**F4's trust model** is continuous: trust is a float [0, 1] on links. No tier mapping exists.

**Impact:** The 5-tier model from PRINCIPLES is disconnected from both F3 and F4. This is not necessarily a bug -- the tiers may be an L3/L4 concept not applicable at L1 -- but the disconnect is worth noting.

**Fix applied:** No code fix. Added a note in F4 SYNC open questions documenting that the 5-tier model from PRINCIPLES needs to be reconciled with the continuous trust model. The tiers are likely economic/governance thresholds on the continuous float, not separate mechanisms.

---

### ISSUE 7: Bilateral Bond Trust Not Explicitly Modeled in F4

**F3 extensively references** the bilateral bond (the 1:1 human-AI pairing). Partner_relevance, limbic coupling, and the Sovereign Cascade all operate within this bond.

**F4's trust mechanics** are generic. Trust lives on links, any link. There is no special treatment of the bond link.

**Impact:** Low. F4's generic model naturally covers bonds (a bond IS a link). But the lack of explicit mention means implementers may not realize that F3's partner_model interactions generate trust signals on the bond link.

**Fix applied:** Added a cross-reference in F4 PATTERNS (after Pattern 6) noting that the bilateral bond is the primary trust relationship in the human-AI pairing, and that F3's alignment fidelity, limbic coupling, and consent model all generate trust/friction signals on this specific link.

---

### ISSUE 8: Pathology Count Inconsistency in F4

**F4 PATTERNS** says "12+ pathology catalogue" (line ~228).
**F4 VALUE_DESTRUCTION_PATHOLOGIES** defines 14 pathologies.
**F4 SYNC** says 14 pathologies.

**Fix applied:** Updated F4 PATTERNS to say "14 pathology catalogue" to match the actual count.

---

### ISSUE 9: Missing Cross-References (Multiple)

**F3 ALGORITHM INTERACTIONS** references "Trust Mechanics (Force 4)" but F4 has no corresponding back-reference to F3's Sovereign Cascade or ingestion pipelines.

**F3 SYNC HANDOFF** explicitly says "Sovereign Cascade alignment fidelity score is a measurable trust signal" but F4 SYNC HANDOFF to F3 does not mention how to incorporate it.

**Fix applied:** Updated F4 SYNC handoff section for Force 3 to explicitly reference the Sovereign Cascade alignment fidelity as a trust input and to reference F3's ingestion pipelines as the source of biometric value creation signals.

---

### ISSUE 10: Human-Only Value Types Applicable to Partner Model

**F4 Sphere 6 (Human-Only)** defines H1: Judgment, H2: Taste, H3: Cultural Context, H4: Emotional Intelligence. These are value types that only humans can produce.

**F3's partner model** ingests human data that could demonstrate these value types (e.g., voice messages expressing judgment, AI conversations revealing taste preferences). But neither force connects human-only value types to partner model ingestion.

**Impact:** Low for v1. This is a future integration point: as the partner model thickens, the AI could recognize when human data demonstrates H1-H4 type value creation and track it.

**Fix applied:** No code fix. Noted as a future integration point in F4 VALUE_CREATION_TAXONOMY, Sphere 6 header.

---

## Coherence Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Terminology consistency | 7/10 | "Limbic delta" used differently; fixed with clarification |
| Cross-references | 5/10 | Many missing; fixed with additions |
| Formula consistency | 8/10 | F4 formulas are authoritative; F3 extends them correctly |
| Architectural alignment | 9/10 | Both follow single-brain, link-trust, physics-over-rules |
| Privacy model coverage | 6/10 | F4 B9 contradicted F3 privacy invariants; fixed |
| Completeness | 7/10 | Value taxonomy missing voice/desktop data; fixed |

---

## Remaining Open Items

1. **Trust tier reconciliation** -- The 5-tier model (Owner/High/Medium/Low/Stranger) from PRINCIPLES needs explicit thresholds on the continuous trust float. Neither F3 nor F4 owns this; it may be an L3/L4 concern.

2. **Alignment fidelity as trust input** -- The integration is now documented but the exact formula (how alignment_score modifies bond link trust) needs simulation to calibrate.

3. **Human-only value detection** -- Future work: detect when partner model data demonstrates H1-H4 value types and track them as trust signals.
