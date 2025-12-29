# Physics — Sync: Attention Energy Split

```
LAST_UPDATED: 2025-12-21
UPDATED_BY: codex
STATUS: DESIGNING
```

---

## CURRENT STATE

Attention split mechanics implemented as a pure function module that computes
sink mass, softmax shares, and energy blending. Doc chain for attention split
is now complete and references mechanism spec + implementation.

---

## RECENT CHANGES

### 2025-12-21: Implemented attention split mechanism

- **What:** Added `apply_attention_split` and related helpers.
- **Why:** Enable deterministic attention redistribution per v0 spec.
- **Files:** `runtime/physics/attention_split_sink_mass_distribution_mechanism.py`.

### 2025-12-21: Added attention split doc chain

- **What:** Added ALGORITHM/IMPLEMENTATION/HEALTH/SYNC docs for attention split.
- **Why:** Complete the attention chain referenced by patterns/behaviors.

---

## TODO

<!-- @mind:todo Define player_neighborhood() boundary (links + depth) -->
<!-- @mind:todo Wire attention split into runtime tick/runner -->

