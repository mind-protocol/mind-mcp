# Physics — Implementation: Attention Energy Split

```
STATUS: DRAFT
CREATED: 2025-12-21
VERIFIED: 2025-12-21 against local tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Attention_Energy_Split.md
BEHAVIORS:       ./BEHAVIORS_Attention_Split_And_Interrupts.md
ALGORITHM:       ./ALGORITHM_Attention_Energy_Split.md
VALIDATION:      ./VALIDATION_Attention_Split_And_Interrupts.md
THIS:            IMPLEMENTATION_Attention_Energy_Split.md (you are here)
HEALTH:          ./HEALTH_Attention_Energy_Split.md
SYNC:            ./SYNC_Attention_Energy_Split.md

IMPL:            mind/physics/attention_split_sink_mass_distribution_mechanism.py
```

---

## CODE MAP

| File | Responsibility | Key Functions |
|------|----------------|---------------|
| `mind/physics/attention_split_sink_mass_distribution_mechanism.py` | Compute sink mass, softmax split, energy blend | `apply_attention_split`, `compute_sink_mass` |

---

## NOTES

- This module is pure computation and does not touch the DB.
- Neighborhood assembly is upstream (view/DMZ).
- Interrupt evaluation remains in runtime orchestration.

