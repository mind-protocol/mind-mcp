# REVIEW: Force 4 (Trust Mechanics) x Force 5 (L1 Wiring) Coherence

```
REVIEWED: 2026-03-14
REVIEWER: Force cross-review (architect)
STATUS: Issues found and fixed
SCHEMA_VERSION: 2.0
```

---

## Summary

Cross-reviewed all 14 documents across Force 4 (Trust & Value Taxonomy, 8 docs) and Force 5 (L1 Wiring / Physics Engine, 6 docs) plus schema.yaml for consistency of formulas, step numbering, field references, and cross-module integration points.

**Result:** 7 issues found. 5 fixed in-place. 2 flagged as design decisions needing confirmation.

---

## Issues Found

### ISSUE 1: Tick Cycle Step Numbering Mismatch (CRITICAL — FIXED)

**Location:** F5 `ALGORITHM_L1_Wiring.md` Section 2.2

**Problem:** F5 defines a 17-step tick cycle with different step numbering than the authoritative source (schema.yaml `tick_cycle`). Key differences:

| Step # | schema.yaml (authoritative) | F5 ALGORITHM_L1_Wiring.md |
|--------|---------------------------|--------------------------|
| 1 | L14 LIMBIC_UPDATE | L1 INJECT |
| 2 | L1 INJECT | L2 PROPAGATE |
| 3 | L14 MODULATE | L8 COMPATIBILITY |
| 4 | L2+L8 PROPAGATE | L3 DECAY |
| 5 | L3 DECAY | L4 COMPETE |
| 6 | L9 INHIBIT | L5 COACTIVATE |
| 7 | L4+L13 COMPETE | L9 INHIBIT |
| 8 | L5 REINFORCE | L6 CONSOLIDATE |
| 9 | L6 CONSOLIDATE | L7 FORGET |
| 10 | L7 FORGET | L10 CRYSTALLIZE |
| 11 | L10 CRYSTALLIZE | L13 INERTIA |
| 12 | L17 CHECK_DESIRE | L14 DRIVES |
| 13 | L15 BOREDOM | L15 BOREDOM |
| 14 | L16 FRUSTRATION | L16 FRUSTRATION |
| 15 | L11 ORIENT | L17 DESIRE |
| 16 | EMIT | L18 VALENCE |
| 17 | CONSUME | CONSUME |

F5 omits the initial LIMBIC_UPDATE (step 1) and MODULATE (step 3) entirely. It reorders most steps. The schema is the canonical source.

**Fix applied:** Replaced F5's tick cycle in Section 2.2 with the schema-canonical ordering, preserving F5's additional context notes.

---

### ISSUE 2: F4 Tick Integration Uses a Third Numbering (FIXED)

**Location:** F4 `ALGORITHM_Trust_Mechanics.md` Section 9

**Problem:** F4 defines its own tick cycle numbering that partially matches schema but diverges on several steps. F4's step 4 combines L2+L8, but puts INHIBIT at step 6 (schema has it there too) while COMPETE is at step 7 in schema but at step 7 in F4 too -- F4 is closer to schema but still diverges on a few steps. Most critically, F4 also starts step 1 with LIMBIC_UPDATE, matching schema.

However, F4 has Law 18 VALENCE missing from its tick cycle entirely, while schema puts it at step 16 between ORIENT and EMIT. F4 claims trust updates happen in step 9 (CONSOLIDATE), but trust is a Law 18 operation, not a Law 6 operation.

**Fix applied:** Corrected F4's tick cycle in Section 9 to exactly match schema.yaml, and explicitly noted where trust update actually occurs (step 16, VALENCE / Law 18, not step 9).

---

### ISSUE 3: Trust Update Step Misattributed in F4 (FIXED)

**Location:** F4 `ALGORITHM_Trust_Mechanics.md` Section 9

**Problem:** F4's tick integration claims trust update (the cascade step 2) happens at step 9 alongside CONSOLIDATE (Law 6). But trust update is a Law 18 operation (Relational Valence), which in the schema occurs at step 16 (VALENCE). Law 6 handles weight consolidation, not trust updates.

This conflation is understandable -- both involve the `(1-W)` asymptotic pattern -- but they are distinct physics laws operating at different tick steps.

**Fix applied:** Moved trust update reference from step 9 to the correct position. Added clarifying comment.

---

### ISSUE 4: `emotional_charge` in F5 FalkorDB Schema Not in schema.yaml (FIXED)

**Location:** F5 `ALGORITHM_L1_Wiring.md` Section 7.1 (FalkorDB Per-Citizen Graph Schema)

**Problem:** F5's Cypher schema includes `emotional_charge: FLOAT` as a node property. This field does not exist in schema.yaml's NodeBase. The schema has drive-affinity dimensions (`goal_relevance`, `novelty_affinity`, `care_affinity`, `achievement_affinity`, `risk_affinity`) but no `emotional_charge`.

**Fix applied:** Removed `emotional_charge` from F5's FalkorDB node schema. It was likely a v1.x holdover. The limbic state is tracked via drives, not a single emotional_charge float.

---

### ISSUE 5: F5 FalkorDB Link Upsert Missing Fields (FIXED)

**Location:** F5 `ALGORITHM_L1_Wiring.md` Section 7.2 (`_upsert_link` method)

**Problem:** The `_upsert_link` Cypher template persists only `relation_kind, weight, energy, affinity, aversion, trust, friction`. But F5's own link schema (Section 7.1) also defines `polarity_ab, polarity_ba`, and schema.yaml defines additional fields on LinkBase including `stability, recency, valence, ambivalence, hierarchy, permanence`.

F4 relies on `trust` and `friction` being persisted (which they are), but `stability` is critical for F4's temporal decay formula (`effective_decay = base_decay_rate * (1.0 - stability_protection)`). If stability isn't persisted, trust decay calculations break after restart.

**Fix applied:** Added `stability, recency, polarity_ab, polarity_ba, valence, hierarchy, permanence` to the `_upsert_link` Cypher template.

---

### ISSUE 6: F4 Value Creation Not Referenced by F5 (DESIGN — NO FIX)

**Location:** F5 Scope section, F4 `VALUE_CREATION_TAXONOMY.md`

**Problem:** F4 defines 28 value creation types with specific limbic delta signatures. F5 does not reference or detect these types. F5's scope explicitly excludes "Trust mechanics / value taxonomy (Force 4)."

This is an intentional design separation, not a bug. However, there is no documented integration point explaining HOW F4's value type detection will eventually plug into F5's stimulus injection or tick cycle. The limbic delta computation (F4 Section 1) requires drive snapshots that F5's tick cycle produces, but F5 doesn't export or surface these snapshots.

**Recommendation:** Add a cross-reference note in both F4 SYNC and F5 SYNC documenting the integration boundary: F5 produces drive snapshots at tick boundaries; F4 consumes them for limbic delta computation; the integration point is the post-stimulus drive comparison.

---

### ISSUE 7: F4 Limbic Delta Bounds vs Drive Count (MINOR — NO FIX)

**Location:** F4 `ALGORITHM_Trust_Mechanics.md` Section 1.3, F4 `VALIDATION_Trust_Mechanics.md` V9

**Problem:** F4 states limbic delta bounds as [-2.0, +2.0], derived from: "satisfaction goes 0->1 (+1) AND frustration goes 1->0 (-(-1)=+1) AND anxiety goes 1->0 (-0.5x(-1)=+0.5)". The math yields max = 1 + 1 + 0.5 = 2.5, not 2.0. Similarly, min should be -2.5.

However, since all drives are bounded [0, 1] and the formula is `satisfaction_delta - frustration_delta - 0.5 * anxiety_delta`, the theoretical extremes are:
- Max: (+1) - (-1) - 0.5*(-1) = +2.5
- Min: (-1) - (+1) - 0.5*(+1) = -2.5

The stated bound of [-2.0, +2.0] is too tight, but the "practical range" of [-0.3, +0.3] is more operationally relevant.

**Recommendation:** Correct the theoretical bounds to [-2.5, +2.5] or document why [-2.0, +2.0] is chosen as a practical clamp.

---

## Coherence Assessment

### Consistent Across F4 and F5

| Aspect | F4 | F5 | Schema | Verdict |
|--------|----|----|--------|---------|
| Trust on links [0,1] | Yes | Yes | Yes | CONSISTENT |
| Friction on links [0,1] | Yes | Yes | Yes | CONSISTENT |
| Affinity on links [0,1] | Yes | Yes | Yes | CONSISTENT |
| Aversion on links [0,1] | Yes | Yes | Yes | CONSISTENT |
| 8 drives in limbic system | Yes | Yes | Yes | CONSISTENT |
| Boredom coefficient -3.0 | Yes | N/A (defers to schema) | Yes (L13) | CONSISTENT |
| Asymptotic (1-W) pattern | Yes | Yes (via schema) | Yes (Law 6) | CONSISTENT |
| Trust Score computed, never stored | Yes | N/A | Yes (L3 section) | CONSISTENT |
| WM capacity 5-7 | Indirect ref | Yes | Yes | CONSISTENT |
| FalkorDB stores link trust/friction | N/A | Yes | N/A | ALIGNED |
| Law 7 sub-threshold dissolution | Yes (V13: <0.01) | N/A | Yes | CONSISTENT |

### Cross-References Added

- F4 SYNC: Added handoff note about F5 integration boundary (drive snapshot timing)
- F5 SYNC: Added note about F4 dependency for trust mechanics

---

## Related Documents

- `docs/trust_mechanics/` -- Force 4 doc chain (8 files)
- `docs/l1_wiring/` -- Force 5 doc chain (6 files)
- `docs/schema/schema.yaml` -- Canonical schema v2.0
