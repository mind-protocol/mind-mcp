# Physics — Algorithm: Attention Energy Split

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
THIS:            ALGORITHM_Attention_Energy_Split.md (you are here)
VALIDATION:      ./VALIDATION_Attention_Split_And_Interrupts.md
IMPLEMENTATION:  ./IMPLEMENTATION_Attention_Energy_Split.md
HEALTH:          ./HEALTH_Attention_Energy_Split.md
SYNC:            ./SYNC_Attention_Energy_Split.md

MECHANISM:       ../mechanisms/MECHANISMS_Attention_Energy_Split.md
IMPL:            mind/physics/attention_split_sink_mass_distribution_mechanism.py
```

---

## OVERVIEW

Attention is a conserved budget distributed across sinks in the player
neighborhood. Mass is computed from focus, link axes, and visibility, then
softmaxed to produce allocations.

---

## PROCEDURE (ABRIDGED)

```
N = player_neighborhood(player, place)
S = { n in N | type(n) in {MOMENT, NARRATIVE} }
mass(s) = clamp(focus_term * link_term * vis_term)
share(s) = softmax(mass(s) / ctx.attention_temp)
alloc(s) = E * share(s)
moment.energy_next = blend(moment.energy_prev, alloc, ctx.energy_inertia)
```

Refer to `MECHANISMS_Attention_Energy_Split.md` for full detail.

