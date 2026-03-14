# Cross-Review: F1 (Universe Graph) / F2 (Metabolic Economy) Coherence

```
STATUS: COMPLETE
DATE: 2026-03-14
REVIEWER: Force cross-review agent
```

---

## Summary

F1 and F2 are well-designed independently but have **7 coherence gaps** where they make assumptions about each other without explicit alignment. The most critical issues are: (1) F2 references Spaces extensively for redistribution but never references F1's access model or Space hierarchy; (2) F1 explicitly scopes out $MIND economics but F2 assumes graph structures F1 defines without citing them; (3) the daily epoch timing in F2 and the tick-based timing in F1 are never reconciled.

---

## Issues Found

### ISSUE-1: F2 Space references lack F1 cross-reference [MODERATE]

**Location:** F2 ALGORITHM Formula 6 (UBC Proximity Redistribution), F2 BEHAVIORS B7, F2 PATTERNS Pattern 7

**Problem:** F2 uses "Spaces" extensively for proximity redistribution (Formula 6) but never references the F1 doc chain where Spaces are actually defined. F2 treats Spaces as pre-existing concepts without acknowledging that F1 defines their creation (B1), hierarchy (ALG-4), access model (ALG-1), and invariants (INV-1 through INV-11).

**Consequence:** An implementer reading F2 alone would not know that:
- Spaces have hierarchical containment (should presence in a parent Space count for child Spaces?)
- Access to Spaces is governed by HAS_ACCESS links (does an actor need HAS_ACCESS to count as "present"?)
- Brain Spaces are encrypted and private (should brain Spaces be excluded from redistribution?)

**Fix:** Add cross-references in F2 to the F1 Space model. Clarify that brain Spaces and private Spaces are excluded from UBC redistribution.

**Applied:** Yes -- added cross-references in F2 ALGORITHM and F2 PATTERNS.

---

### ISSUE-2: Economic implications of Space creation undocumented in F1 [MODERATE]

**Location:** F1 BEHAVIORS B1 (Space Creation), F1 BEHAVIORS B5 (Organization Creation)

**Problem:** F1 describes Space creation and organization creation with no mention of any economic cost or consequence. Creating a Space is free. Creating an organization is free. There is no $MIND cost, no bond requirement, no deposit.

F2 never defines a cost for Space or organization creation either. This means the system currently allows unlimited free Space creation, which could be exploited for UBC redistribution gaming (create hundreds of Spaces, seed them with presence, harvest redistribution).

**Consequence:** Without an economic cost for Space creation, F2's proximity redistribution (Formula 6) is vulnerable to farming via cheap Space proliferation.

**Fix:** F1 should note that economic implications are delegated to F2. F2 should acknowledge that Space creation costs are an open question.

**Applied:** Yes -- added notes to F1 BEHAVIORS and F2 SYNC open questions.

---

### ISSUE-3: Trust model references diverge [LOW]

**Location:** F1 BEHAVIORS B11, F1 VALIDATION INV-7, F2 ALGORITHM Formula 4 (Settlement)

**Problem:** F1 defines trust as a link dimension at L3 with values in [0, 1], built through L5/L6 co-activation. F1 explicitly states no transitive trust at L3 (B11). F2 uses `trust(Y -> X)` in the settlement formula but references it as coming from "L1 Law 18 (Relational Valence)."

This is a subtle but important divergence:
- F1 says L3 trust is structural, built via L5+L6 co-activation reinforcement
- F2 says settlement trust comes from L1 Law 18 (relational valence)
- L1 Law 18 does NOT apply at L3 (listed in schema.yaml as `applies: false`)

So where does settlement trust actually come from? L1 (brain-internal) or L3 (universe graph)?

**Resolution:** Settlement trust should come from L1 (it is a brain's subjective evaluation of another actor), not from L3 (which is structural). This is actually correct in F2 -- the settlement formula operates on L1 outputs. But F2 should clarify that this is brain-level trust, not universe-level trust. The L3 trust dimension on links is a separate, structural concept.

**Fix:** Add clarifying note in F2 ALGORITHM Formula 4 distinguishing L1 subjective trust from L3 structural trust.

**Applied:** Yes -- added clarification in F2 ALGORITHM.

---

### ISSUE-4: Macro-crystallization timing vs daily settlement [LOW]

**Location:** F1 ALGORITHM ALG-3 (crystallization check every 500 ticks), F2 ALGORITHM Formula 4 (batch settlement every 6 hours)

**Problem:** F1 defines crystallization checks at 500-tick intervals. F2 defines settlement at 6-hour intervals. Neither defines the L3 tick duration, so the relationship between ticks and wall-clock time is undefined.

F2's crystallization example (B7 in F1) mentions "~500 transfers -> 1 economic partnership narrative" which would be collapsed by macro-crystallization. But the settlement system creates Moment nodes (transfer records) that are also candidates for crystallization. The interplay is never documented.

**Consequence:** An implementer does not know:
- How many ticks correspond to 6 hours (or 24 hours)
- Whether settlement batch moments are crystallization candidates
- Whether crystallization of transfer moments affects settlement history

**Fix:** Add a note in F1 SYNC about L3 tick timing as it relates to the daily epoch schedule. This was already flagged as an open question in F1 SYNC (L3 tick timing) but should explicitly reference the F2 daily schedule.

**Applied:** Yes -- updated F1 SYNC Q5 to reference F2 daily schedule.

---

### ISSUE-5: Weight tracking for progressive demurrage [LOW]

**Location:** F2 ALGORITHM Formula 2, F1 ALGORITHM ALG-6 (Energy Model)

**Problem:** F2's progressive demurrage taxes based on wallet balance (`W_total_i`), which is a Solana on-chain value. This does NOT require any L3 graph weight. The `weight` dimension in the graph (node weight, link weight) is entirely separate from wallet balance.

However, F2's pricing formula uses `U_S` (service utility weight from graph consolidation Law 6), and F2's settlement uses `weight(thing_used)` from graph weight. These DO depend on the L3 graph's weight tracking.

F1 defines how weight works at L3 via L6 (consolidation) but does not explicitly document how service nodes accumulate weight. F1's energy model (ALG-6) covers energy injection and propagation but not weight consolidation.

**Consequence:** F2 depends on graph weight for pricing and settlement, but F1 does not document how Thing/service nodes accumulate weight at L3. L6 consolidation is listed as applying at L3, but the utility gating mechanism (which requires limbic significance at L1) needs an L3 analog.

**Fix:** Add a note in F1 ALGORITHM about L6 consolidation at L3 and how utility is determined without limbic input.

**Applied:** Yes -- added note to F1 ALGORITHM ALG-6.

---

### ISSUE-6: Cross-Space transactions not addressed [MODERATE]

**Location:** Neither F1 nor F2

**Problem:** F2's settlement formula rewards actions across the ecosystem. F1's Space model creates boundaries between contexts. Neither force addresses what happens when:
- An actor in Space A performs an action that benefits an actor in Space B
- A $MIND transfer occurs between actors in different Spaces
- Settlement rewards an actor for cross-Space value creation

F1's energy model (B10) describes cross-Space energy propagation (a moment in Space A propagates to Spaces B and C via the actor). But F2's redistribution (Formula 6) only considers single-Space presence. An actor who bridges two Spaces creates value (network effect) but this bridging value is not captured by F2's redistribution formula.

**Consequence:** Cross-Space value creation is structurally under-rewarded by F2. The redistribution formula rewards presence within Spaces but not the bridging between them.

**Fix:** Add a note in F2 SYNC as a v2 consideration. Not a blocking issue for v1 since settlement (Formula 4) already rewards cross-Space actions via limbic_delta.

**Applied:** Yes -- added to F2 SYNC proposed v2 ideas.

---

### ISSUE-7: MAPPING.md anti-pattern table says organization maps to actor [LOW]

**Location:** `/home/mind-protocol/mind-mcp/docs/MAPPING.md`, Anti-Patterns table

**Problem:** The MAPPING.md anti-pattern table says: "Creating a new node_type 'organization' -- Why It's Wrong: Schema has 5 types, period -- Correct Approach: Map to `actor` (it can initiate action)."

But F1 explicitly defines organizations as **Narrative** nodes (not Actor). F1 PATTERNS section "Why Organizations Are Narratives" explains: "An organization does not think. It does not run inference." Organizations are Narrative nodes with associated hall Spaces.

MAPPING.md contradicts F1's canonical design decision.

**Fix:** Correct the MAPPING.md anti-pattern table to say organizations map to `narrative`, not `actor`.

**Applied:** Yes -- corrected MAPPING.md.

---

## Issues NOT Found (Confirmed Coherent)

- **Key management model**: F1 mentions "same key pair for $MIND transactions and Space decryption." F2 mentions Solana wallets for settlement. These are consistent -- one keypair for both.
- **Trust on links only**: Both F1 (INV-7, B11, A6) and F2 use trust exclusively as a link property. No contradiction.
- **5 node types**: Both forces use the same 5 universal types. F2 maps $MIND transfers to Moment nodes. F1 defines Moment creation (B4). Consistent.
- **Physics law subset**: F1 lists L2, L3, L5, L6, L7, L10 at L3. F2 references L6 (consolidation for utility weight) and L18 (relational valence for trust) -- but correctly notes L18 is L1-only. Consistent.
- **Encrypted brain exclusion**: F1's encryption model means brain Spaces are invisible to other actors. F2's redistribution naturally excludes brain Spaces because no other actor has "presence" in them. Structurally consistent, though should be made explicit (addressed in ISSUE-1 fix).

---

## Fixes Applied

| Issue | File Modified | Change |
|-------|--------------|--------|
| ISSUE-1 | F2 ALGORITHM Formula 6 | Added cross-reference to F1 Space model, brain Space exclusion note |
| ISSUE-1 | F2 PATTERNS Pattern 7 | Added cross-reference to F1 Space model |
| ISSUE-2 | F1 BEHAVIORS B1 | Added note about economic implications delegated to F2 |
| ISSUE-2 | F2 SYNC | Added open question Q6 about Space creation cost |
| ISSUE-3 | F2 ALGORITHM Formula 4 | Added clarification distinguishing L1 trust from L3 trust |
| ISSUE-4 | F1 SYNC Q5 | Updated to reference F2 daily epoch schedule |
| ISSUE-5 | F1 ALGORITHM ALG-6 | Added L6 consolidation note for service weight at L3 |
| ISSUE-6 | F2 SYNC | Added cross-Space bridging value to v2 proposals |
| ISSUE-7 | MAPPING.md | Corrected organization mapping from `actor` to `narrative` |
