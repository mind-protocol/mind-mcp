# MECHANISMS — PRIMES Lag + Half-Life (v0)

```
STATUS: DRAFT
CREATED: 2025-12-21
```
---

## CHAIN

- PATTERNS_Attention_Energy_Split.md
- BEHAVIORS_Attention_Split_And_Interrupts.md
- VALIDATION_Attention_Split_And_Interrupts.md

---

## PURPOSE

Implement soft causality that:
- **does not** create facts,
- introduces **delay** (lag) to avoid “commentator immediacy”,
- decays with a half-life to avoid long-term pollution.

PRIMES contributes to attention mass and/or triggers possibility generation by actors (Fox), but never forces spoken.

---

## PRIMES LINK FIELDS (REQUIRED)

- `strength` in [0,1]
- `lag_ticks` (int ≥ 0)
- `decay_half_life_ticks` (float > 0)
- `intent_tags` (array of strings; e.g., ["generate_possibles", "increase_salience"])

Optional:
- `budget_cost` in [0,1] (compute/attention cost)
- `history` (count, last_tick)

---

## INPUTS

- `tick_now`
- source node `a.tick_created` (or “last reinforced tick”)
- link parameters above

---

## PRIME EFFECT FUNCTION

Let `age = tick_now - tick_created(a)`.

Lag gate:
```
lag_gate = 1 if age >= lag_ticks else 0
```

Decay after lag:
```
effective_age = max(0, age - lag_ticks)
decay = 2 ** ( - effective_age / decay_half_life_ticks )
```

Prime effect:
```
prime(a,b,t) = strength * lag_gate * decay
```

**Properties:**
- Before lag: effect = 0
- At lag boundary: effect = strength
- After: monotone decay to 0

---

## HOW PRIMES IS USED (v0)

### Option A — contributes to link_term(s) in Attention Split
Treat `prime(a→s)` as an additional incoming influence:
```
link_term(s) += prime(a,s,t) * role_weight("procedural") * mode_weight("causal")
```

### Option B — triggers Fox possibility generation (still not facts)
If `intent_tags` contains `"generate_possibles"` and `prime` exceeds a context threshold:
- enqueue a Fox job to create *possible* moments related to `b`
- apply DMZ constraints if relevant

---

## FAILURE MODES

- lag too small → narrator/fox feels instantaneous
- half-life too long → stale primes never die (plateau)
- primes used as facts → violates canon boundaries

---

## VALIDATION HOOKS

- V2 deterministic replay
- Test: prime=0 before lag, equals strength at lag, decays after
