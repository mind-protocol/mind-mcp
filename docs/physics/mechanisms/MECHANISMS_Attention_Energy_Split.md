# MECHANISMS — Attention Energy Split (v0)

```
STATUS: DRAFT
CREATED: 2025-12-21
```
---

## CHAIN

- PATTERNS_Attention_Energy_Split.md
- PATTERNS_Interrupt_By_Focus_Reconfiguration.md
- BEHAVIORS_Attention_Split_And_Interrupts.md
- VALIDATION_Attention_Split_And_Interrupts.md

---

## PURPOSE

Provide a deterministic, local, mechanically-honest mechanism that:
- redistributes a player-local attention/energy budget across eligible sinks (Moments + Narratives),
- causes *focus reconfiguration* (dominant change / deactivation) as an emergent interrupt trigger,
- avoids heuristic interrupts and avoids query side-effects.

---

## INPUTS (REQUIRED)

### Nodes
- ACTOR: `attention_budget` (player)
- NARRATIVE: `focus` (0.1–3.0 recommended)
- MOMENT: `energy`, `status`, `tick_created`, `history.appends`

### Links
- AT: `present`, `visible`, `recency_s` (as available)
- RELATES: `strength`, `role`, `mode`, `confidence`, `polarity` (optional), `emotions` (optional)
- PRIMES (optional contribution): `strength`, `lag_ticks`, `decay_half_life_ticks`, `intent_tags`

### Context (Ctx)
All “constants” are functions; store tunables as Space-scoped narratives (runner_tuning):
- `attention_scale(actor, place)` → float
- `attention_temp(place)` → float (softmax temperature)
- `energy_inertia(actor, place)` → float in [0,1]
- `role_weight(role, place)` → float
- `mode_weight(mode, place)` → float
- `status_weight(moment_status, place)` → float

---

## STEP 1 — Build Player Neighborhood

Define a neighborhood function (already constrained by your DMZ + view logic):

```
N = player_neighborhood(player_id, place_id)
```

**Invariant:** Only nodes in `N` may receive attention allocations.

---

## STEP 2 — Enumerate Eligible Sinks

```
S = { n in N | type(n) in {MOMENT, NARRATIVE} }
```

Optionally filter by visibility:
- if a sink has AT.visible = 0, it contributes 0 mass.

---

## STEP 3 — Compute Sink Mass (Node↔Link Jointure)

For each sink `s`:

### 3.1 focus_term(s)
- If NARRATIVE: `focus_term = focus(s)`
- If MOMENT: `focus_term = 1.0 + status_weight(status(s), place)`

### 3.2 link_term(s)
Aggregate incoming neighborhood links (design choice: include those originating from player and/or from neighborhood actors):

```
link_term(s) = Σ over incoming RELATES/PRIMES:
    strength(link) * role_weight(role(link)) * mode_weight(mode(link)) * conf(link)
```
- For PRIMES edges, use `prime_effect` from MECHANISMS_Primes_Lag_Decay.md.

### 3.3 visibility_term(s)
If AT.visible exists along the local path, use it as a multiplier (else 1.0).

### 3.4 mass(s)
```
mass(s) = clamp( focus_term(s) * link_term(s) * visibility_term(s), lo, hi )
```

**No magic constants:** `lo/hi` come from context functions (or are global invariants in patterns).

---

## STEP 4 — Allocate Attention

Budget:
```
E = attention_budget(player) * attention_scale(player, place)
```

Distribution:
```
share(s) = softmax( mass(s) / attention_temp(place) )
alloc(s) = E * share(s)
```

**Invariant:** Σ alloc(s) ≈ E (floating error allowed).

---

## STEP 5 — Update Moment Energies (and only moment energies)

For each MOMENT m in S:

```
m.energy_next = blend(m.energy_prev, alloc(m), energy_inertia(player, place))
```

Where:
- `blend(a,b,α) = α*a + (1-α)*b`
- `α = energy_inertia(...)` in [0,1]

**Rule:** Narratives do not need persistent energy; compute their “salience” on demand, or store as diagnostic only.

---

## OUTPUTS

- Updated `energy` for moments in neighborhood.
- Diagnostics (optional, debug-only):
  - sink_set_size
  - top_k sinks by mass + alloc
  - dominant active moment id before/after

---

## INTERRUPT COUPLING (uses separate pattern)

Interrupt = YES iff:
- dominant active moment changes, OR
- dominant active moment deactivates below threshold, OR
- any player-neighborhood moment becomes completed.

(See PATTERNS_Interrupt_By_Focus_Reconfiguration.md)

---

## FAILURE MODES

- Over-sensitivity: small arrivals churn focus constantly
- Under-sensitivity: nothing ever reconfigures; plateau
- Neighborhood explosion: too many sinks dilute allocations; nothing surfaces

---

## VALIDATION HOOKS

- V2 deterministic replay (same snapshot → same alloc)
- V3 sink set exactly neighborhood-defined
- V4 interrupt iff focus reconfiguration / spoken
