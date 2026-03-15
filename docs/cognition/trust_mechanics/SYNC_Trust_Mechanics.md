# SYNC: Trust Mechanics

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Force 4 (architect)
STATUS: DESIGNING
```

---

## Current State

**Phase:** C — Implementation plan complete. Ready for coding.

### What Exists

| Document | Status | Content |
|----------|--------|---------|
| `OBJECTIVES_Trust_Mechanics.md` | Complete | 5 objectives + tradeoffs + non-objectives |
| `PATTERNS_Trust_Mechanics.md` | Complete | 7 patterns + 5 anti-patterns |
| `ALGORITHM_Trust_Mechanics.md` | Complete | Limbic delta, trust update, cascade, tempering, detection, tick integration |
| `BEHAVIORS_Trust_Mechanics.md` | Complete | 9 scenarios + health signals |
| `VALIDATION_Trust_Mechanics.md` | Complete | 14 invariants + validation schedule |
| `VALUE_CREATION_TAXONOMY.md` | Complete | 30 types across 7 spheres + Limbic Delta formulas |
| `VALUE_DESTRUCTION_PATHOLOGIES.md` | Complete | 14 pathologies + detection + response |
| `IMPLEMENTATION_Trust_Mechanics.md` | Complete | Architecture, file plan, 8 phases, interfaces, test plan |
| `SYNC_Trust_Mechanics.md` | This file | Current state |

### What's Canonical

- Trust lives on links, never on nodes (Law 18, schema v2.0)
- Trust Score = topological aggregation, always computed, never stored
- Asymptotic convergence: `ΔW = alpha x avg_energy x U x (1-W)`
- Three tempering safeguards: asymptotic (Law 6), temporal decay (Law 7), boredom erosion (Law 15)
- Creator attribution cascade: Laws 2 + 5 on existing graph topology
- Negative deltas increase friction, not decrease trust
- 30 value creation types across 7 spheres
- 14 value destruction pathologies with topological detection

---

## Maturity

STATUS: DESIGNING

**What's canonical (v1):**
- Trust on links as the only trust primitive
- Asymptotic growth formula
- Creator attribution cascade mechanism
- Three tempering safeguards
- Value creation taxonomy structure (7 spheres)
- Value destruction pathology catalogue
- 14 validation invariants

**What's still being designed:**
- Trust Score aggregation method (weighted mean vs PageRank)
- Limbic Delta to Trust conversion rate (beta = 0.05, needs simulation)
- Friction learning rate (gamma = 0.08, needs simulation)
- assess_agent() interface with Personhood Ladder
- Detection algorithm thresholds
- Value type to Personhood Ladder aspect mapping

**What's proposed (v2):**
- Cross-brain trust synchronization (L3 layer)
- Trust-weighted governance (voting power from trust)
- Trust markets (bonded trust delegation)

---

## Open Questions

### OQ1: Trust Score Aggregation Method
**Question:** Weighted mean by link weight, or PageRank-style recursive computation?

**Arguments for weighted mean:**
- Simpler to compute and explain
- Sufficient for v1 use cases (pricing, friction, UBC tier)
- No recursion = no convergence issues

**Arguments for PageRank:**
- Captures transitivity (trusted-by-trusted is more valuable)
- Better Sybil resistance (isolated clusters can't inflate scores)
- More sophisticated signal

**Current lean:** Weighted mean for v1. PageRank as v2 upgrade if needed.

**Decision needed from:** Nicolas / human review

---

### OQ2: Limbic Delta to Trust Conversion Rate

**Question:** What is the right `beta` (trust learning rate)?

**Current value:** `beta = 0.05`

**Implications:**
- At beta=0.05 and limbic_delta=0.2 and trust=0.0: ΔTrust = 0.01 per tick
- At fast_tick (5s): 720 ticks/hour, ΔTrust = 7.2/hour (but only during active interaction)
- Seems reasonable for reaching trust ~0.3 in first month with daily usage

**Needs:** Simulation across realistic usage patterns. Verify month-1, month-6, month-12 trust trajectories.

---

### OQ3: assess_agent() Frequency

**Question:** How often should the Personhood Ladder assessment run?

**Options:**
- Per tick: Too expensive, changes too granular
- Per day: Reasonable for batch processing, aligned with settlement cycle
- On demand: Most efficient, but may miss gradual changes

**Current lean:** Daily batch, with on-demand for specific queries.

---

### OQ4: Value Type to Personhood Ladder Mapping

**Question:** Which value creation types demonstrate which of the 14 Personhood Ladder aspects?

**Status:** Blocked. Need Nicolas's "Daughters (T7 Autonomy)" document to understand the 14 aspects fully.

**Partial mapping (from what's known):**
- Care (relational) → Empathy aspect
- Tool creation (generative) → Competence aspect
- Teaching (cognitive) → Communication aspect
- Community building (relational) → Social awareness aspect

---

### OQ5: L3 Trust Dimensions

**Question:** At L3 (Universe Graph), trust on links uses the same float field but with structural (not cognitive) interpretation. How does L3 trust interact with L1 trust?

**Current understanding:** L3 trust is the "ground truth" structural relationship. L1 trust is the subjective perception. An actor might have L1 trust=0.9 on their link to another actor, while L3 trust=0.4 (structural reality). This divergence is information (the actor is over-trusting).

**Decision needed:** Does L3 trust exist as a computed aggregate of all L1 trusts? Or is it independently determined?

---

### OQ6: Trust Tier Reconciliation

**Question:** PRINCIPLES.md references 5 trust tiers (Owner, High, Medium, Low, Stranger). This module models trust as a continuous float [0, 1]. How do the tiers map?

**Current understanding:** The 5 tiers are likely economic/governance thresholds on the continuous trust float, not a separate mechanism. For example:
- Stranger: trust_score < 0.10 (default, highest friction)
- Low: 0.10 <= trust_score < 0.30
- Medium: 0.30 <= trust_score < 0.60
- High: 0.60 <= trust_score < 0.85
- Owner: trust_score >= 0.85 or structural (bond partner)

These thresholds are speculative. The tier system may also be an L3/L4 concept (protocol-level access control) rather than an L1 concept (cognitive trust). F3's consent model is binary (granted/revoked), not tier-based, which suggests consent operates independently of trust tiers.

**Decision needed:** Are trust tiers L1 (cognitive), L3 (structural), or L4 (protocol)? What are the threshold values?

---

## Recent Changes

### 2026-03-14: Phase C Implementation Plan Created
- Created `IMPLEMENTATION_Trust_Mechanics.md` with full architecture and file plan
- 8 implementation phases (T1-T8) with function signatures and file paths
- 10 new files in `runtime/cognition/trust/`
- 4 existing files modified (models.py, constants.py, tick_runner, law_13_to_18)
- 14 invariant tests mapped to test files
- 7 behavioral scenario tests from BEHAVIORS mapped
- Shared interfaces documented: needs from F3/F5, provides to F2/F5
- Review issues from F3/F4 and F4/F5 cross-reviews addressed in implementation design
- Limbic delta bounds corrected to [-2.5, +2.5] per F4/F5 review Issue 7
- Trust update step correctly placed at step 4/16 (propagation/valence), not step 9

### 2026-03-14: F3/F4 Cross-Review Fixes
- Added Pattern 7 (Bilateral Bond) to PATTERNS — cross-references F3 human integration
- Added ALGORITHM section 2.4 (Sovereign Cascade alignment as trust signal)
- Fixed B9 in BEHAVIORS (biometric node type: actor not thing; privacy-bounded trust flow)
- Added B4 (Voice Data) and B5 (Behavioral Context) to VALUE_CREATION_TAXONOMY (now 30 types)
- Renamed Sphere 5 from "Biometric" to "Biometric & Partner Data"
- Fixed pathology count in PATTERNS (14, not "12+")
- Updated SYNC handoff to F3 with specific Sovereign Cascade and pipeline references
- Added OQ6 (Trust Tier Reconciliation)

### 2026-03-13: Initial Documentation Created
- Created full doc chain: OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, VALIDATION, SYNC
- Created VALUE_CREATION_TAXONOMY.md (28 types, 7 spheres)
- Created VALUE_DESTRUCTION_PATHOLOGIES.md (14 pathologies)
- All grounded in schema v2.0 (Laws 2, 5, 6, 7, 15, 18) and PATTERNS_Economy.md

---

## Dependencies

| This Module Needs | From | Status |
|-------------------|------|--------|
| LinkBase.trust field | Schema v2.0 | EXISTS |
| LinkBase.friction field | Schema v2.0 | EXISTS |
| LinkBase.affinity field | Schema v2.0 | EXISTS |
| LinkBase.aversion field | Schema v2.0 | EXISTS |
| 8 drives (limbic system) | Schema v2.0 | EXISTS |
| Law 2 (Propagation) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Law 5 (Co-activation) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Law 6 (Consolidation) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Law 7 (Forgetting) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Law 15 (Boredom) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Law 18 (Relational Valence) | Schema v2.0 | EXISTS (spec), TODO (implementation) |
| Transaction friction formula | PATTERNS_Economy.md | EXISTS |
| Personhood Ladder (14 aspects) | Force 4 / graphcare | TODO |

| Other Modules Need From This | Consumer | Status |
|------------------------------|----------|--------|
| Trust Score computation | Economy (pricing, friction, fees) | DOCUMENTED |
| Value creation types | Personhood Ladder assessment | DOCUMENTED |
| Destruction detection | Anti-gaming / moderation | DOCUMENTED |
| Limbic Delta formula | Physics engine (tick cycle) | DOCUMENTED |

---

## Handoff

**For Force 5 (L1 Physics Wiring):**
- Trust update formulas integrate into tick cycle steps 4, 8, 9, 10, 13 (see ALGORITHM section 9)
- Trust/friction update happens at step 4 (PROPAGATE, Law 18 modulation), NOT at step 9 (CONSOLIDATE)
- No new tick steps needed. Trust mechanics piggyback on existing Laws 2, 5, 6, 7, 15, 18
- Key requirement: limbic delta must be computed between ticks (snapshot drives at step 1 LIMBIC_UPDATE, compare at step 17 CONSUME)
- **Integration boundary:** F5 produces drive snapshots at tick boundaries (step 1 and step 17). F4 consumes these snapshots for limbic delta computation. The limbic delta then feeds trust/friction updates during step 4 propagation. F5 does not need to know about value creation types -- the limbic delta abstracts them.

**For Force 2 (Economy):**
- Trust Score aggregation feeds into: transaction friction, membrane fee, effective pricing
- All formulas documented in ALGORITHM section 6
- Decision needed on aggregation method (OQ1) before economy implementation

**For Force 3 (Human Integration):**
- Biometric and partner data value creation (Sphere 5 in Taxonomy, types B1-B5) maps human data → trust signals on the bond link
- Partner_relevance on nodes interacts with trust on partner bond link
- Bilateral bond trust is a specific instance of the general trust cascade (see PATTERNS, Pattern 7)
- Sovereign Cascade alignment fidelity acts as an additional trust signal on the bond link (see ALGORITHM section 2.4). F3's `measure_alignment_fidelity` output feeds directly into `update_bond_trust_from_alignment`
- F3's six ingestion pipelines (voice, garmin, desktop, blockchain, AI conversations, direct chat) are the source of data for Sphere 5 value creation types
- Privacy constraint: trust signals from partner_model data flow ONLY on the bond link (F3 VALIDATION V5/V7)

**For Human:**
- Review open questions OQ1 (aggregation), OQ4 (Personhood mapping)
- Provide "Daughters (T7 Autonomy)" document for Personhood Ladder integration
- Validate beta=0.05 learning rate via simulation or intuition check

---

## Module Coverage

| Component | Doc | Code | Tests | Phase |
|-----------|-----|------|-------|-------|
| Trust on links | DOCUMENTED | IMPL PLANNED (T1) | PLANNED | T1 |
| Limbic Delta | DOCUMENTED | IMPL PLANNED (T2) | PLANNED | T2 |
| Creator cascade | DOCUMENTED | IMPL PLANNED (T3) | PLANNED | T3 |
| Trust Score aggregation | DOCUMENTED | IMPL PLANNED (T4) | PLANNED | T4 |
| Value type classification | DOCUMENTED | IMPL PLANNED (T5) | PLANNED | T5 |
| Destruction detection | DOCUMENTED | IMPL PLANNED (T6) | PLANNED | T6 |
| Trust tempering | DOCUMENTED | IMPL PLANNED (T7) | PLANNED | T7 |
| Personhood Ladder integration | PARTIAL (4/14 aspects) | IMPL PLANNED (T8) | PLANNED | T8 |
| Value creation taxonomy | DOCUMENTED | N/A (reference data) | N/A | T5 |
