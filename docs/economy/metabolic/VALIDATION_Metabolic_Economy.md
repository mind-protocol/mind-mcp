# Metabolic Economy — Validation: Invariants

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Metabolic_Economy.md
ALGORITHM:       ./ALGORITHM_Metabolic_Economy.md
THIS:            ./VALIDATION_Metabolic_Economy.md
```

---

## FORMULAS GUARANTEED

| Formula | Validation Focus | Why This Validation Matters |
|---------|-----------------|----------------------------|
| F1: Degressive Price | Price is always non-negative and bounded | Negative prices would mean the system pays users to use services. This is incoherent — a service always has a cost, even if subsidized. |
| F2: Progressive Tax | Tax never exceeds wallet balance; tax is non-negative | A tax that exceeds the balance would create negative wallets — an impossibility in the Solana token model. A negative tax would mean the system pays entities for holding, the opposite of demurrage. |
| F3: Anti-Sybil | Repatriation doesn't confiscate legitimate transfers; penalty is bounded | The penalty must be painful enough to deter sybil behavior but not so severe that honest mistakes (accidentally sending to wrong address) feel like theft. |
| F4: Bilateral Bond | Transfer doesn't overdraw sender; transfer converges to parity | An overdraw would create a negative wallet. Non-convergence would mean the mechanism oscillates or diverges — a physics bug. |
| F5: Batch Settlement | Creator weights sum to 1; dust is handled; settlement is atomic | Weights that don't sum to 1 mean value is created or destroyed during distribution. Non-atomic settlement means partial state on failure. |

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| Organism flow (money as energy) | V1, V2, V3, V4 | These four invariants together guarantee that $MIND circulates — prices decrease with utility, holdings are taxed, off-grid funds are recaptured, and bonded pairs equalize. |
| No accumulation pathology | V2, V5 | Progressive tax and conservation ensure that wealth cannot grow unboundedly without creating value, and that tax revenue is fully redistributed. |
| Anti-sybil integrity | V3, V6 | Off-grid tracking is complete (no unattributed funds) and repatriation doesn't confiscate legitimate holdings. |
| Bilateral parity | V4, V7 | Bond transfers converge and don't overdraw, maintaining the structural equality the pairing system requires. |
| Settlement integrity | V5, V8, V9 | Conservation of value, atomic execution, and non-negative wallets guarantee that the batch settlement system doesn't leak, corrupt, or partially apply. |

## INVARIANTS

- **V1:** Price MUST be non-negative for all users and all services.
- **V2:** Daily tax MUST be non-negative and MUST NOT exceed total wallet balance.
- **V3:** Anti-sybil repatriation MUST NOT reduce an entity's total attributed wealth by more than `SYBIL_PENALTY` fraction (currently 5%) of the off-grid amount.
- **V4:** Bilateral bond transfer MUST NOT overdraw the sending partner's wallet.
- **V5:** Total $MIND entering the UBC pool in a period MUST equal total tax collected plus total penalties collected plus unclaimed energy flows plus dust sweeps in that period (conservation of value).
- **V6:** Every $MIND transfer to a non-L4 address MUST be attributed to exactly one entity.
- **V7:** Bilateral bond transfer MUST converge (the wealth gap between partners MUST decrease monotonically, absent external income).
- **V8:** Each batch settlement MUST be atomic — either all transfers in the batch succeed or none do.
- **V9:** No wallet balance MUST ever be negative.

## PROPERTIES

### P1: Price Non-Negativity

```
FORALL users i, services S:
  P(i, S) = C_base(S) × e^{-k × U_S} × max(0.1, W_i / W_med)

  Given:
    C_base(S) >= 0     (compute cost is non-negative)
    e^{-k × U_S} > 0   (exponential is always positive)
    max(0.1, _) >= 0.1  (floor at 0.1)

  Therefore: P(i, S) >= 0  ∎
```

The price is a product of three non-negative terms. The exponential function is
always positive (never zero, never negative). The floor function ensures the
wealth adjustment is at least 0.1. The base cost is non-negative by definition
(you can't have negative compute cost).

**Boundary behavior:**

- As `U_S → ∞`: `P → 0⁺` (approaches zero but never reaches it, for `C_base > 0`)
- As `W_i → 0`: `P → C_base × D(S) × 0.1` (floor kicks in)
- As `W_med → 0`: Bootstrap condition applies, `A(i) = 1.0` for all users

### P2: Tax Boundedness

```
FORALL entities i:
  T_i = W_total_i × τ_base × log₁₀(1 + W_total_i)

  Effective rate: r_eff = τ_base × log₁₀(1 + W_total_i)

  For T_i <= W_total_i, we need:
    τ_base × log₁₀(1 + W_total_i) <= 1
    log₁₀(1 + W_total_i) <= 1/τ_base
    W_total_i <= 10^{1/τ_base} - 1

  With τ_base = 0.001:
    W_total_i <= 10^{1000} - 1
```

The tax formula theoretically allows `T > W` for astronomically large balances
(`W > 10^1000`). This is physically impossible but must be guarded programmatically:

```
IMPLEMENTATION GUARD:
  T_i = min(T_i, W_total_i)
```

This guard enforces V2 at the code level, regardless of input values.

**Non-negativity:**

```
  W_total_i >= 0          (wallets can't be negative, by V9)
  τ_base > 0              (by definition)
  log₁₀(1 + W_total_i) >= 0  (because 1 + W_total_i >= 1, so log >= 0)

  Therefore: T_i >= 0  ∎
```

### P3: Anti-Sybil Penalty Bound

```
FORALL repatriations r for entity i:
  repatriated = r.amount × (1 - SYBIL_PENALTY)
  penalty = r.amount × SYBIL_PENALTY

  entity_i receives: repatriated
  UBC_POOL receives: penalty

  Total wealth change for entity_i from repatriation:
    Δ = repatriated - r.amount = -r.amount × SYBIL_PENALTY

  Since SYBIL_PENALTY = 0.05:
    Entity loses exactly 5% of the off-grid amount.
    Entity retains exactly 95% of the off-grid amount.
```

**Legitimate transfer protection:**

The anti-sybil system attributes ALL non-L4 outbound transfers to the sender.
This means a legitimate transfer (to a DEX, a bridge, a friend who hasn't
registered) is also attributed. However:

- If the recipient registers on L4 BEFORE repatriation, the funds are reclassified
  as registered. No penalty.
- If the $MIND is sold on a DEX, ownership transfers to the buyer. The indexer
  detects the ownership change and removes the attribution. No penalty.
- Only $MIND that REMAINS on a non-L4 address attributed to the sender is
  repatriated.

The potential for false positives (legitimate transfers penalized) is the tradeoff
for anti-sybil integrity. The 5% penalty is calibrated to be annoying but not
ruinous — a friction cost, not a punishment.

**Edge case — entity sends to themselves on a non-L4 wallet:**

This is the primary sybil vector. The entity creates wallet B (not on L4), sends
$MIND to B to reduce their taxable W_registered, hoping to lower their progressive
tax. Anti-sybil defeats this because W_offgrid is counted in W_total for tax.
They pay the same tax AND lose 5% on repatriation. Net result: the sybil attempt
costs them money.

### P4: Bilateral Transfer Convergence

```
FORALL bonded pairs (h, a):
  Let gap_n = W_h_n - W_a_n (wealth gap at period n)

  ΔTransfer_n = λ × gap_n

  After transfer:
    W_h_{n+1} = W_h_n - λ × gap_n  (if h is richer)
    W_a_{n+1} = W_a_n + λ × gap_n  (if h is richer)

  gap_{n+1} = W_h_{n+1} - W_a_{n+1}
            = (W_h_n - λ × gap_n) - (W_a_n + λ × gap_n)
            = gap_n - 2λ × gap_n
            = gap_n × (1 - 2λ)
```

Wait — this needs correction. The transfer flows from the richer to the poorer,
so if `W_h > W_a`:

```
  W_h_{n+1} = W_h_n - ΔTransfer = W_h_n - λ(W_h_n - W_a_n)
  W_a_{n+1} = W_a_n + ΔTransfer = W_a_n + λ(W_h_n - W_a_n)

  gap_{n+1} = W_h_{n+1} - W_a_{n+1}
            = [W_h_n - λ(W_h_n - W_a_n)] - [W_a_n + λ(W_h_n - W_a_n)]
            = W_h_n - W_a_n - 2λ(W_h_n - W_a_n)
            = gap_n(1 - 2λ)
```

For convergence, we need `|1 - 2λ| < 1`, which means `0 < λ < 1`.

With `λ = 0.05`: `gap_{n+1} = gap_n × 0.9`. The gap shrinks by 10% per period.

```
  gap_n = gap_0 × (1 - 2λ)^n = gap_0 × 0.9^n

  After 10 periods:  gap = gap_0 × 0.349  (65% reduction)
  After 50 periods:  gap = gap_0 × 0.0052 (99.5% reduction)
  After 100 periods: gap = gap_0 × 0.0000266 (near-zero)
```

**Convergence is guaranteed** as long as `0 < λ < 1` and no external income
disrupts the pair. External income (value events, UBC) changes both balances
and creates new gaps — but the mechanism continuously corrects toward parity.

**Non-overdraw:**

```
  ΔTransfer = λ × |gap|

  Since λ < 1 and |gap| <= max(W_h, W_a):
    ΔTransfer < max(W_h, W_a)

  Since the sender is the wealthier party:
    ΔTransfer = λ × (W_sender - W_receiver) < W_sender
    (because λ < 1 and W_receiver >= 0)

  Therefore: sender can always cover the transfer.  ∎
```

Implementation guard for safety: `ΔTransfer = min(ΔTransfer, W_sender)`.

### P5: Settlement Conservation

```
FORALL settlement batches b:
  Let inflows_b = SUM(energy payments received by all entities in b)
  Let outflows_b = SUM(energy payments sent by all entities in b)
  Let tax_b = SUM(T_i for all entities in b)
  Let penalties_b = SUM(SYBIL_PENALTY deductions in b)
  Let ubc_in_b = tax_b + penalties_b + unclaimed_b + dust_b
  Let ubc_out_b = SUM(UBC distributed in b)

  Conservation requires:
    inflows_b = outflows_b                    (energy: every outflow is someone's inflow)
    ubc_in_b >= ubc_out_b                     (UBC pool: never distribute more than collected)
    ubc_pool_after = ubc_pool_before + ubc_in_b - ubc_out_b >= 0
```

Conservation is enforced at the batch level. Within a batch:

- Every energy payment deducted from a source is credited to a destination (or
  set of destinations, weighted by contributor weights that sum to 1.0).
- Tax revenue is collected into UBC_POOL.
- UBC distribution is bounded by pool balance.

**Contributor weight invariant:**

```
FORALL services S:
  SUM(weight for all contributors of S) = 1.0

  Proof of conservation:
    If total_energy for service S = E, then:
    SUM(creator_i receives E × weight_i) = E × SUM(weight_i) = E × 1.0 = E

    No value created or destroyed.  ∎
```

### P6: Off-Grid Attribution Completeness

```
FORALL $MIND transfers t WHERE t.destination NOT IN L4_registry:
  EXISTS exactly one entity e such that:
    offgrid[e][t.destination] includes t.amount
```

This requires:

- Every outbound $MIND transfer is monitored by the Solana indexer.
- The indexer can determine the sender entity from the source wallet (via L4 registry).
- The attribution ledger is updated atomically with the transfer detection.

**Failure mode:** If the indexer misses a transfer, the off-grid amount is
under-counted. The entity pays less tax than they should. This is a data integrity
issue, not a formula issue. The mitigation is indexer reliability (redundant
monitoring, catch-up scanning).

**Ambiguity case:** Multi-sig wallets or programmatic wallets where the sender
entity is ambiguous. Resolution: the wallet's registered owner on L4 is the
attributed entity. If the wallet is not registered, the last entity that sent
TO the wallet is attributed (cascading attribution).

### P7: Wallet Non-Negativity

```
FORALL wallets w, at all times t:
  balance(w, t) >= 0
```

This is enforced by the Solana Token-2022 program itself — SPL tokens cannot have
negative balances. However, our settlement system must also respect this at the
computation level:

```
BEFORE any deduction from wallet w:
  ASSERT balance(w) >= deduction_amount
  IF NOT: cap deduction at balance(w)
```

This applies to:
- Tax deduction: `T_i = min(T_i, W_total_i)` (P2 guard)
- Bilateral transfer: `ΔTransfer = min(ΔTransfer, W_sender)` (P4 guard)
- Energy payment: source cannot pay more than their balance
- Repatriation penalty: cannot penalize more than the off-grid amount

## ERROR CONDITIONS

### E1: Negative Price Computed

```
WHEN:    P(i, S) computes to a negative value
THEN:    This should be impossible (see P1). If it occurs, it's a floating-point bug.
         Halt pricing computation. Log the inputs. Return C_base(S) as fallback price.
SYMPTOM: Settlement batch rejects the price. Alert raised.
```

### E2: Tax Exceeds Balance

```
WHEN:    T_i > W_total_i (before guard)
THEN:    Cap T_i at W_total_i. Log the event as unusual (extreme wealth scenario).
SYMPTOM: Entity's wallet is zeroed out by tax. This is valid behavior for the guard
         but should be monitored — it means someone accumulated astronomically.
```

### E3: Bilateral Transfer Would Overdraw

```
WHEN:    ΔTransfer > W_sender
THEN:    Cap ΔTransfer at W_sender. Log the event.
SYMPTOM: This should not occur with λ < 1 (see P4 proof). If it does, λ is misconfigured
         or external state is inconsistent. Investigation required.
```

### E4: Settlement Batch Fails Mid-Execution

```
WHEN:    A Solana transaction within a batch fails (insufficient SOL for fees,
         network error, transaction size exceeded)
THEN:    Roll back the entire batch. Pending flows are preserved for next settlement.
SYMPTOM: Settlement receipt shows FAILED status. All transfers in the batch are
         retried in the next cycle. Alert raised if consecutive failures exceed 3.
```

### E5: Off-Grid Transfer Unattributed

```
WHEN:    Indexer detects a $MIND transfer to a non-L4 address but cannot determine
         the sender entity (source wallet not in L4 registry)
THEN:    Flag the transfer as UNATTRIBUTED. Do not repatriate (no known owner).
         Include in system health report.
SYMPTOM: Off-grid tracking has a gap. This means someone is moving $MIND through
         unregistered intermediary wallets — a multi-hop sybil attempt. The fix is
         cascading attribution (trace the chain of transfers back to a registered entity).
```

### E6: Contributor Weights Don't Sum to 1.0

```
WHEN:    SUM(weights for service S) != 1.0 (within floating-point tolerance of ±0.001)
THEN:    Normalize weights to sum to 1.0 before distribution. Log the inconsistency.
SYMPTOM: Graph contributor weights are out of sync. The graph physics module should
         be investigated for weight propagation bugs.
```

### E7: UBC Pool Insufficient for Distribution

```
WHEN:    Computed UBC distribution exceeds UBC_POOL_BALANCE
THEN:    Scale all distributions proportionally so total equals pool balance.
         No entity receives more than their computed share.
SYMPTOM: More citizens than the tax base can support. This is a systemic signal —
         either τ_base is too low, or the network has too many idle citizens.
         Report to system health.
```

## HEALTH COVERAGE

- `ALGORITHM_Metabolic_Economy.md` defines the formulas and invariants.
- P1 (price non-negativity) is verified by construction (product of non-negative terms). Runtime guard: assert `P >= 0` before recording.
- P2 (tax boundedness) is verified by the `min(T, W)` guard. Runtime: assert `T >= 0 AND T <= W` after computation.
- P3 (anti-sybil penalty bound) is verified by fixed penalty rate. Runtime: assert repatriated + penalty = original amount.
- P4 (bilateral convergence) is verified by the contraction mapping proof. Runtime: assert gap decreases period-over-period (absent external income).
- P5 (settlement conservation) is verified by balanced ledger checks. Runtime: assert inflows = outflows per batch, UBC pool non-negative after distribution.
- P6 (off-grid attribution) is verified by indexer completeness checks. Runtime: count unattributed transfers; alert if > 0.
- P7 (wallet non-negativity) is verified by Solana token program. Runtime: assert all wallet balances >= 0 after settlement.

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Compute P(i, S) for edge cases (W_i=0, U_S=0, W_med=0) — all non-negative.
[ ] Compute T_i for edge cases (W=0, W=1, W=10^6) — all non-negative, all <= W.
[ ] Verify repatriation: 95% returns to entity, 5% to UBC pool, total = original.
[ ] Verify bilateral convergence: gap × 0.9^n with λ=0.05, check 10/50/100 periods.
[ ] Verify contributor weights for a sample service — must sum to 1.0 ± 0.001.
[ ] Simulate a settlement batch: total outflows = total inflows, UBC in = tax + penalties.
[ ] Verify UBC distribution: sum <= pool balance, proportional to need.
[ ] Test atomic rollback: fail one transfer mid-batch, verify no partial state.
```

### Automated

```bash
# Not yet implemented — these will be simulation tests and on-chain integration tests.
# Future locations:
#   tests/economy/test_degressive_pricing.py
#   tests/economy/test_progressive_tax.py
#   tests/economy/test_anti_sybil.py
#   tests/economy/test_bilateral_transfer.py
#   tests/economy/test_batch_settlement.py
#   tests/economy/test_ubc_distribution.py
#   tests/economy/test_settlement_conservation.py
```

## SYNC STATUS

```
LAST_VERIFIED: 2026-03-13
VERIFIED_AGAINST:
  docs: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md
  code: not yet implemented
VERIFIED_BY: design review (no code exists)
RESULT:
  V1: DESIGNED (not tested)
  V2: DESIGNED (not tested)
  V3: DESIGNED (not tested)
  V4: DESIGNED (not tested)
  V5: DESIGNED (not tested)
  V6: DESIGNED (not tested)
  V7: DESIGNED (not tested)
  V8: DESIGNED (not tested)
  V9: DESIGNED (not tested)
```

## MARKERS

<!-- @mind:todo Build simulation test suite that runs all 5 formulas against synthetic wallet populations and verifies all 9 invariants hold. -->
<!-- @mind:todo Stress-test the progressive tax formula at extreme wealth values (10^12+) to confirm the min(T, W) guard never fires in realistic scenarios. -->
<!-- @mind:todo Design the settlement rollback mechanism: how does a failed Solana batch transaction trigger rollback of the local ledger state? -->
<!-- @mind:todo Verify anti-sybil cascading attribution: if A sends to B (non-L4), and B sends to C (non-L4), is the full chain attributed to A? Specify the indexer behavior. -->
<!-- @mind:todo Define monitoring dashboards: effective tax rate distribution, UBC pool levels, bilateral convergence rates, settlement success rate, off-grid attribution completeness. -->
