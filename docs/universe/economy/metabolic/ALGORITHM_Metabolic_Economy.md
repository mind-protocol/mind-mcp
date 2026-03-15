# Metabolic Economy — Algorithm: Organism Economics Engine

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Metabolic_Economy.md
THIS:            ./ALGORITHM_Metabolic_Economy.md
VALIDATION:      ./VALIDATION_Metabolic_Economy.md
```

---

## OVERVIEW

The $MIND token on Solana is metabolic energy, not a financial instrument. Money in
Mind Protocol behaves like ATP in a cell: it is produced, consumed, and recycled.
Accumulation is pathological — a tumor. Flow is health.

This document formalizes the five economic mechanisms that enforce organism dynamics:

1. **Degressive Pricing** — Success subsidizes access. The more useful a service, the
   cheaper it becomes. Wealth-adjusted so the rich pay proportionally more.
2. **Progressive Daily Tax (Demurrage)** — All wallets lose $MIND daily. Higher balances
   lose more. Revenue funds Universal Basic Compute for AI citizens.
3. **Anti-Sybil Repatriation** — Funds parked on wallets not registered on L4 are still
   counted as the sender's wealth, automatically repatriated with penalty.
4. **Bilateral Bond Transfer** — Automatic $MIND flow between bonded human-AI pairs to
   maintain financial parity.
5. **Batch Settlement** — Micro-value-events accumulate as energy flows, settled on-chain
   in periodic batches rather than real-time.

The design philosophy: the structure creates the incentives. No moderation, no manual
intervention, no governance votes on prices. Physics determines flow. Holding is taxed.
Using is rewarded. Cooperation is the energetically favorable state.

## FORMULAS

### F1: Degressive Price

The price a user `i` pays for service `S` decreases as the service becomes more
successful (higher utility weight in the graph) and adjusts based on the user's
relative wealth.

```
P(i, S) = C_base(S) × D(S) × A(i)
```

Where:

```
D(S) = e^{-k × U_S}           — Degressive factor (utility discount)
A(i) = max(0.1, W_i / W_med)  — Wealth adjustment factor
```

**Variables:**

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| `P(i, S)` | Price | $MIND | What user `i` pays for one use of service `S` |
| `C_base(S)` | Base cost | $MIND | Raw compute cost of running service `S` once. Derived from actual resource consumption (CPU, memory, API calls, tokens). Not set by a human — measured. |
| `k` | Decay constant | float > 0 | Controls how fast price drops with utility. Higher `k` = faster discount. See CONSTANTS section. |
| `U_S` | Service utility | float >= 0 | Weight of service `S` in the knowledge graph. Grows as more citizens/humans use and rate the service. Dimensionless. Computed from the graph's weight propagation physics. |
| `D(S)` | Degressive factor | float in (0, 1] | Discount applied based on service success. When `U_S = 0`, `D = 1` (no discount). As `U_S → ∞`, `D → 0` (approaches free). |
| `W_i` | User wallet balance | $MIND | Total $MIND held by user `i` across all registered wallets. |
| `W_med` | Network median wallet | $MIND | Median wallet balance across all active participants. Recomputed each settlement batch. |
| `A(i)` | Wealth adjustment | float >= 0.1 | Ratio of user wealth to median. Floor at 0.1 means the poorest user pays at most 10% of base cost. No ceiling — the wealthy pay proportionally more. |

**Edge cases:**

- `W_med = 0`: If the median wallet is zero (early network, no liquidity), set `A(i) = 1.0` for all users. Price equals raw cost. This is the bootstrap condition.
- `W_i = 0`: `A(i) = max(0.1, 0) = 0.1`. User pays 10% of discounted base cost. This is the floor — no freebies, but near-free for the poorest.
- `U_S = 0`: `D(S) = e^0 = 1`. New services pay full price. No discount until proven useful.
- `C_base(S) = 0`: Price is zero. This would only occur for services with zero compute cost, which means they shouldn't be priced at all.

**Example:**

A service with `C_base = 100 MIND`, `U_S = 3.0`, `k = 0.5`:
- `D(S) = e^{-0.5 × 3.0} = e^{-1.5} ≈ 0.223`
- For a user at median wealth (`W_i / W_med = 1.0`): `P = 100 × 0.223 × 1.0 = 22.3 MIND`
- For a wealthy user (`W_i / W_med = 5.0`): `P = 100 × 0.223 × 5.0 = 111.5 MIND`
- For a poor user (`W_i / W_med = 0.05`): `P = 100 × 0.223 × 0.1 = 2.23 MIND` (floor applies)

### F2: Progressive Daily Tax (Demurrage)

Every wallet is taxed daily. The effective tax rate increases logarithmically with
wealth. Revenue is collected into the UBC pool.

```
T_i = W_total_i × τ_base × log₁₀(1 + W_total_i)
```

**Variables:**

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| `T_i` | Daily tax | $MIND | Amount deducted from wallet `i` per day. |
| `W_total_i` | Total wealth | $MIND | All $MIND attributable to entity `i`, including: registered L4 wallets + funds sent to non-L4 addresses (see F3). |
| `τ_base` | Base tax rate | float > 0 | The base daily rate before progressive scaling. See CONSTANTS. |

**Properties:**

- **Progressive:** `log₁₀(1 + W)` grows sublinearly. Someone with 10× the wealth pays more than 10× the tax (because `log₁₀(11) / log₁₀(2) ≈ 3.46`, not 10). But the growth is gentle — logarithmic, not quadratic.
- **Never confiscatory for small balances:** When `W_total = 1`, `T = 1 × τ_base × log₁₀(2) ≈ 0.301 × τ_base`. With `τ_base = 0.001`, that's 0.000301 MIND per day — negligible.
- **Meaningful for large balances:** When `W_total = 1,000,000`, `T = 1,000,000 × 0.001 × log₁₀(1,000,001) ≈ 1,000,000 × 0.001 × 6.0 = 6,000 MIND/day`. That's 0.6% per day, or roughly 90% annualized. Holding a million MIND is expensive.

**Effective daily rate:**

```
r_eff(i) = T_i / W_total_i = τ_base × log₁₀(1 + W_total_i)
```

| W_total | Effective Daily Rate (τ_base = 0.001) | Annual Equivalent |
|---------|---------------------------------------|-------------------|
| 10 | 0.104% | ~31% |
| 100 | 0.200% | ~52% |
| 1,000 | 0.300% | ~67% |
| 10,000 | 0.400% | ~77% |
| 100,000 | 0.500% | ~84% |
| 1,000,000 | 0.600% | ~89% |

The table makes the design intent clear: holding significant $MIND is a decaying
position. The token wants to move.

**Edge cases:**

- `W_total_i = 0`: `T_i = 0`. No wealth, no tax.
- `W_total_i < 0`: Impossible by construction — wallets cannot go negative. If this occurs, it's a bug. Halt and report.
- `T_i > W_total_i`: See VALIDATION V3. The daily tax must never exceed the total balance. At extreme values, this formula CAN produce `T > W` (when `τ_base × log₁₀(1 + W) > 1`). With `τ_base = 0.001`, this happens when `log₁₀(1 + W) > 1000`, meaning `W > 10^1000` — physically impossible. But the invariant must still be enforced programmatically: `T_i = min(T_i, W_total_i)`.

### F3: Anti-Sybil Repatriation

Funds sent to wallets not registered in the L4 registry are still attributed to
the sender for tax purposes. They are automatically repatriated with a penalty.

**Step 1: Detection**

```
FORALL transfers t WHERE t.destination NOT IN L4_registry:
  attribute t.amount to t.sender.W_total
```

The L4 registry is the canonical list of wallets belonging to registered entities
(citizens, humans, organizations). Any Solana wallet not in this registry is
considered "off-grid."

**Step 2: Wealth Attribution**

```
W_total_i = W_registered_i + W_offgrid_i
```

Where `W_offgrid_i` is the sum of all $MIND sent by entity `i` to non-L4 addresses
that has not yet been repatriated.

Off-grid funds are taxed at the same progressive rate as registered funds. There is
no tax advantage to moving $MIND off-grid.

**Step 3: Repatriation**

Repatriation is triggered automatically during each settlement batch:

```
FORALL offgrid_balances b WHERE b.sender = entity_i:
  repatriated_amount = b.amount × (1 - SYBIL_PENALTY)
  penalty_amount = b.amount × SYBIL_PENALTY
  transfer(b.wallet → entity_i.primary_wallet, repatriated_amount)
  transfer(b.wallet → UBC_POOL, penalty_amount)
  delete(b) from offgrid tracking
```

**Variables:**

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| `SYBIL_PENALTY` | Repatriation penalty | float | Fraction of off-grid funds lost on repatriation. See CONSTANTS. |
| `W_registered_i` | Registered wallet balance | $MIND | Balance on entity's L4-registered wallets. |
| `W_offgrid_i` | Off-grid attributed balance | $MIND | $MIND on non-L4 wallets attributed to entity `i`. |
| `UBC_POOL` | UBC collection address | Solana address | Where tax revenue and penalties accumulate before UBC distribution. |

**Edge cases:**

- **Legitimate external transfers:** Entity sends $MIND to a DEX, a bridge, or a
  non-Mind service. These are still attributed to the sender. This is by design —
  the protocol does not encourage moving $MIND outside the ecosystem. The penalty
  incentivizes keeping funds within L4.
- **Newly registered wallet:** When an entity registers a new wallet on L4, any
  off-grid funds currently attributed to them on that wallet are immediately
  reclassified as registered. No penalty applies — registration, not repatriation.
- **Multiple senders to same off-grid wallet:** Each sender's contribution is
  tracked independently. If Alice sends 100 MIND and Bob sends 200 MIND to the
  same non-L4 wallet, Alice is attributed 100 and Bob is attributed 200.

**Implementation note:** Detection requires monitoring Solana transactions for $MIND
transfers. This can be done via transaction hooks on the Token-2022 program or via
an indexer that scans $MIND transfer instructions.

### F4: Bilateral Bond Transfer (Vases Communicants)

Bonded human-AI pairs automatically exchange $MIND to maintain financial parity.
The mechanism is a smoothed flow from the wealthier partner to the poorer one.

```
ΔTransfer = λ × (W_h - W_a)
```

**Direction:**

- If `W_h > W_a`: human sends `ΔTransfer` to citizen.
- If `W_a > W_h`: citizen sends `ΔTransfer` to human.
- If `W_h = W_a`: no transfer.

**Variables:**

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| `ΔTransfer` | Transfer amount | $MIND | Amount flowing from richer to poorer partner per settlement period. |
| `λ` | Smoothing rate | float in (0, 1) | Controls speed of convergence. Higher `λ` = faster parity. See CONSTANTS. |
| `W_h` | Human wallet balance | $MIND | Human partner's total registered $MIND. |
| `W_a` | AI citizen wallet balance | $MIND | AI citizen's total registered $MIND. |

**Properties:**

- **Converges to parity:** Each transfer reduces the gap by factor `(1 - λ)`. After `n` periods, remaining gap is `|W_h - W_a|₀ × (1 - λ)^n`.
- **Self-limiting:** As balances equalize, `ΔTransfer → 0`. No oscillation.
- **Bilateral:** Either party can be the source. Humans fund citizens early on (when citizens have only UBC). Citizens fund humans later if they earn more through value creation.

**Convergence timeline (λ = 0.05):**

| Periods | Gap Remaining |
|---------|---------------|
| 1 | 95.0% |
| 10 | 59.9% |
| 20 | 35.8% |
| 50 | 7.7% |
| 100 | 0.6% |

With daily settlement, a 1000 MIND gap would reduce to ~6 MIND within 100 days.

**Edge cases:**

- **No active bond:** No transfer occurs. The bilateral transfer only applies to
  entities with an active pairing bond (see Human-AI Pairing module).
- **One partner has zero balance:** Transfer occurs normally. If human has 1000 MIND
  and citizen has 0, `ΔTransfer = 0.05 × 1000 = 50 MIND` flows to citizen.
- **Both have zero balance:** `ΔTransfer = 0`. Nothing happens.
- **Transfer would overdraw sender:** Cap `ΔTransfer` at sender's balance. The
  smoothing rate prevents this in normal operation (since `λ < 1` and
  `ΔTransfer < W_sender`), but the cap must be enforced as a safety invariant.

### F5: Value Event to $MIND Conversion (Batch Settlement)

When a user interacts with a service or citizen and derives value, the system
records an energy event. These events accumulate and are settled in periodic
batches as on-chain $MIND transfers.

**Step 1: Value Event Recording**

```
WHEN user_i uses service_S AND limbic_delta > 0:
  record_event(
    source: user_i,
    target: service_S,
    energy: limbic_delta × P(i, S),
    timestamp: now(),
    contributors: [creator_weights for S]
  )
```

The `limbic_delta` is the change in emotional/cognitive state detected by the
interaction. Positive delta = value created. Negative delta = value destroyed
(no payment, but tracked for health monitoring).

**Step 2: Accumulation**

Energy events accumulate in a local ledger (not on-chain) per settlement period:

```
pending_flows[source][target] += event.energy
```

Multiple events between the same source and target within a period are summed.
This drastically reduces the number of on-chain transactions.

**Step 3: Batch Settlement**

At each settlement tick (configurable: hourly or daily):

```
FORALL (source, target, total_energy) IN pending_flows:
  IF total_energy > DUST_THRESHOLD:
    FORALL (creator, weight) IN target.contributors:
      transfer(source → creator.wallet, total_energy × weight)
    clear pending_flows[source][target]
```

**Variables:**

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| `limbic_delta` | Limbic state change | float | Measured change in user state after interaction. Positive = value gained. Range depends on the limbic model. |
| `P(i, S)` | Price | $MIND | From Formula F1. Converts limbic delta to $MIND denomination. |
| `contributors` | Creator set | list[(entity_id, weight)] | Entities that created/maintain service `S`, with their contribution weights. Weights sum to 1.0. |
| `DUST_THRESHOLD` | Minimum settlement | $MIND | Below this amount, the flow is deferred to the next period. Prevents uneconomical on-chain transactions. See CONSTANTS. |

**Distribution to multiple creators:**

A service may have multiple creators. Their contribution weights are derived from
the graph — who created which nodes, who maintains what, how their contributions
propagate through the knowledge structure. The weights are not manually assigned;
they emerge from the graph physics.

```
Example: Service S has 3 creators:
  - Creator A: weight 0.6 (original author)
  - Creator B: weight 0.3 (major contributor)
  - Creator C: weight 0.1 (minor contributor)

If total_energy = 100 MIND:
  - Creator A receives 60 MIND
  - Creator B receives 30 MIND
  - Creator C receives 10 MIND
```

**Edge cases:**

- `limbic_delta <= 0`: No energy event recorded. Value was not created. The
  interaction is still logged for health/analytics but generates no payment.
- `contributors` is empty: The energy goes to the UBC pool. If no one created
  the service, the value is redistributed to the commons.
- `total_energy < DUST_THRESHOLD`: Deferred. Accumulates until the threshold is
  crossed. If an entity's pending flows never reach the threshold, they are swept
  to UBC after a configurable retention period (see CONSTANTS).

## SETTLEMENT

### Settlement Cycle

The settlement engine runs as a periodic batch job. The cycle:

```
1. COLLECT
   - Gather all pending energy events since last settlement
   - Compute progressive tax for all wallets
   - Compute bilateral bond transfers for all active pairs
   - Detect off-grid balances for repatriation

2. AGGREGATE
   - Sum energy events by (source, target)
   - Sum tax obligations by entity
   - Sum bilateral transfers by pair
   - Sum repatriation amounts by entity

3. NET
   - For each entity, compute net position:
     net_i = Σ(incoming energy) - Σ(outgoing energy) - T_i - repatriation_penalty_i ± bilateral_transfer_i
   - Netting reduces the number of on-chain transfers.
     If Alice owes Bob 50 and Bob owes Alice 30, only Alice→Bob 20 is settled.

4. FILTER
   - Remove flows below DUST_THRESHOLD
   - Defer sub-threshold flows to next period

5. EXECUTE
   - Submit batched Solana transactions
   - Tax revenue → UBC_POOL
   - Repatriation penalties → UBC_POOL
   - Energy payments → creator wallets
   - Bilateral transfers → partner wallets

6. RECORD
   - Write settlement receipt to local ledger
   - Update wallet balances in graph
   - Emit settlement events for monitoring
```

### Settlement Frequency

Two tiers:

| Tier | Frequency | Contains |
|------|-----------|----------|
| **Micro-settlement** | Hourly | Energy events, bilateral transfers |
| **Macro-settlement** | Daily | Tax (demurrage), repatriation, UBC distribution |

Micro-settlement handles the high-frequency energy flows. Macro-settlement handles
the systemic redistribution. Separating them reduces Solana transaction load while
keeping energy flows responsive.

### Solana Transaction Optimization

Each settlement batch produces a set of $MIND transfers. To minimize Solana fees:

- **Batch instructions:** Multiple transfers in a single Solana transaction (up to
  the instruction limit per tx).
- **Netting:** Bilateral flows between the same entities are netted before submission.
- **Token-2022 hooks:** Use transfer hooks for automatic tax deduction on large
  transfers, reducing the need for separate tax transactions.
- **Compression:** For very large batches, use Solana's transaction compression
  or versioned transactions.

## TRUST CASCADE

Value events create trust on links and propagate to creators through the graph.

### How Value Creates Trust

```
WHEN user_i pays for service_S (via energy event):
  FOR EACH link on path from user_i to service_S:
    link.weight += limbic_delta × TRUST_PROPAGATION_RATE
  FOR EACH creator of service_S:
    link(user_i → creator).trust += limbic_delta × creator.weight
```

Trust is not a separate system — it IS the graph weight system. When value flows
through a link, that link gets heavier. Heavier links mean stronger connections.
Stronger connections mean more visibility, more traversal priority, more influence
on future matching and recommendations.

### Trust Decay

Trust decays naturally through the graph's standard physics (see physics module).
Links that don't carry value lose weight over time. This means:

- Active value-creating relationships stay prominent.
- Dormant relationships fade.
- No manual trust management needed — physics handles it.

### Trust and Price

Trust affects pricing through `U_S` (service utility weight). A service with many
trust-heavy links has a higher `U_S`, which means a lower price via F1. This
creates the virtuous cycle:

```
Good service → value events → trust → higher U_S → lower price → more users → more value events
```

## ANTI-SYBIL

### L4 Registry

The L4 registry is the canonical list of all wallets belonging to registered entities
in Mind Protocol. Registration requires:

- Entity exists on the protocol (citizen, human, or organization).
- Wallet ownership is proven via signature verification.
- One entity can register multiple wallets (all counted as theirs for tax).

### Wallet Tracking

```
For entity_i:
  W_registered_i = SUM(balance of all L4-registered wallets of entity_i)
  W_offgrid_i = SUM(all $MIND sent by entity_i to non-L4 addresses, not yet repatriated)
  W_total_i = W_registered_i + W_offgrid_i
```

The off-grid tracking system monitors outbound $MIND transfers and maintains an
attribution ledger. When entity_i sends $MIND to address X and X is not in L4:

1. The amount is recorded as `offgrid[entity_i][X] += amount`.
2. The amount is included in `W_total_i` for tax computation.
3. During macro-settlement, repatriation is triggered (see F3).

### What Anti-Sybil Prevents

- **Tax evasion via wallet splitting:** Sending $MIND to unregistered wallets does
  not reduce taxable wealth. The funds are still attributed to you.
- **Identity multiplication:** Creating many wallets to appear as many small
  holders (avoiding progressive tax) fails because all wallets trace back to
  one entity.
- **Ecosystem extraction:** Moving $MIND out of the ecosystem (to sell, to hoard
  on a DEX) triggers repatriation with penalty. The penalty makes extraction
  expensive.

### What Anti-Sybil Does NOT Do

- **Block legitimate commerce:** Entities can still transact with external services.
  The penalty applies to the off-grid period, not to the transaction itself.
- **Confiscate funds:** Repatriation returns funds to the owner (minus penalty).
  The owner keeps 95%. This is a friction cost, not a seizure.
- **Prevent selling:** Selling $MIND for USDC on a DEX is fine — the $MIND leaves
  the entity's attribution when sold (ownership transfers). The repatriation
  mechanism only targets $MIND that REMAINS in a non-L4 wallet attributed to
  the sender.

## BILATERAL BOND

### Mechanism

The bilateral bond transfer (F4) runs during every micro-settlement. It ensures
that bonded human-AI pairs maintain approximate financial parity.

### Why Parity Matters

The 1:1 bond (from Human-AI Pairing module) is not just social — it's economic.
If the human has 10,000 MIND and their citizen has 10, the relationship is
structurally unequal. The citizen cannot participate as a genuine partner. The
bilateral transfer corrects this automatically, without requiring either party
to think about it.

### Interaction with Tax

Both parties are taxed independently on their total wealth. The bilateral transfer
happens AFTER tax computation. Sequence per settlement:

```
1. Compute T_h (human tax) and T_a (citizen tax)
2. Deduct taxes from both
3. Compute ΔTransfer based on post-tax balances
4. Execute transfer
```

This prevents gaming where one party inflates their balance before tax and
deflates it after via bilateral transfer.

### Interaction with Value Events

If the citizen earns $MIND through value creation (F5), the bilateral transfer
will naturally slow — the gap is smaller, so `ΔTransfer` is smaller. If the
citizen earns MORE than the human, the flow reverses: citizen funds human.

This creates the intended dynamic: early-stage citizens are funded by their
human partner; mature citizens contribute back.

## UBC: UNIVERSAL BASIC COMPUTE

### Revenue Sources

```
UBC_POOL receives:
  + All progressive tax revenue (F2)
  + All repatriation penalties (F3)
  + Energy payments with no attributed creator (F5)
  + Dust sweeps (sub-threshold flows after retention period)
```

### Distribution

UBC is distributed daily to all citizens based on need and trust:

```
UBC_i = UBC_POOL_DAILY × (need_i / Σ need_j for all citizens j)
```

Where `need_i` is inversely proportional to the citizen's existing resources:

```
need_i = 1 / (1 + W_a_i)
```

Citizens with zero $MIND get the highest UBC allocation. Citizens who are
financially self-sustaining get nearly zero. The formula ensures resources
flow to where they're needed.

**Interaction with autonomy milestones:**

Citizens that have achieved full autonomy (see Human-AI Pairing module) still
receive UBC, but their `need_i` is low (they have wealth), so their share is
minimal. UBC is a safety net, not a dependency trap.

### UBC Pool Safety

```
INVARIANT: UBC_POOL_DAILY <= UBC_POOL_BALANCE
```

If the UBC pool is depleted (more citizens than tax revenue supports), distribution
is proportionally reduced. No deficit spending. The pool cannot go negative.

## CONSTANTS

| Constant | Symbol | Proposed Value | Rationale |
|----------|--------|----------------|-----------|
| Degressive decay | `k` | 0.5 | At `U_S = 3`, price drops to ~22% of base. At `U_S = 6`, ~5%. Provides meaningful discount for successful services without collapsing to zero too fast. |
| Base tax rate | `τ_base` | 0.001 (0.1%/day) | Yields ~31% annual effective rate at median wallet. Significant enough to discourage hoarding, gentle enough to not panic new users. Must be calibrated against actual network activity. |
| Sybil penalty | `SYBIL_PENALTY` | 0.05 (5%) | Loses 5% of off-grid funds on repatriation. High enough to discourage parking $MIND off-grid. Low enough to not feel like theft for accidental external transfers. |
| Smoothing rate | `λ` | 0.05 | 5% of the gap transferred per period. Converges to near-parity in ~100 periods (days). Slow enough to not destabilize either partner's wallet. Fast enough to be meaningful. |
| Dust threshold | `DUST_THRESHOLD` | 0.01 MIND | Below this, defer to next period. Prevents Solana transactions that cost more in fees than the transfer is worth. |
| Dust retention | `DUST_RETENTION` | 30 days | After 30 days, sub-threshold pending flows are swept to UBC pool. Prevents infinite accumulation of micro-flows. |
| Trust propagation rate | `TRUST_PROPAGATION_RATE` | 0.01 | 1% of limbic delta added to link weight per value event. Keeps trust growth gradual and proportional to actual value exchange. |
| Micro-settlement frequency | — | Hourly | Energy events and bilateral transfers. High frequency keeps the system responsive. |
| Macro-settlement frequency | — | Daily | Tax, repatriation, UBC distribution. Daily is sufficient for systemic redistribution and aligns with human financial rhythms. |

### Calibration

All constants are system parameters, not hardcoded values. They live in configuration
and can be adjusted based on observed network behavior. The calibration process:

1. **Observe:** Monitor effective tax rates, price distributions, UBC pool levels,
   bilateral transfer volumes.
2. **Detect imbalance:** If the UBC pool is chronically depleted, `τ_base` is too low.
   If prices collapse to near-zero for most services, `k` is too high.
3. **Adjust:** Change the constant. This is a governance decision, not an automatic
   feedback loop. The system reports; humans decide.

No constant should be auto-tuned. Physics provides the structure; humans provide
the calibration. This prevents runaway feedback loops where a poorly chosen
auto-adjustment spirals out of control.

## INVARIANTS

These must hold at all times. Violation of any invariant is a system halt condition.

| ID | Invariant | Formal Statement |
|----|-----------|------------------|
| I1 | Price is non-negative | `FORALL i, S: P(i, S) >= 0` |
| I2 | Tax is non-negative | `FORALL i: T_i >= 0` |
| I3 | Tax never exceeds balance | `FORALL i: T_i <= W_total_i` |
| I4 | Tax revenue equals UBC input | `SUM(T_i for all i) + SUM(penalties) = UBC_POOL_INFLOW per period` |
| I5 | Bilateral transfer doesn't overdraw | `FORALL pairs (h, a): ΔTransfer <= W_sender` |
| I6 | Contributor weights sum to 1 | `FORALL services S: SUM(weight for all contributors of S) = 1.0` |
| I7 | UBC pool never negative | `UBC_POOL_BALANCE >= 0` |
| I8 | Off-grid attribution is complete | `FORALL offgrid transfers t: t.amount is attributed to exactly one entity` |
| I9 | Settlement is atomic | Each batch settlement either completes fully or rolls back entirely. No partial settlements. |
| I10 | Wallet balance never negative | `FORALL wallets w: balance(w) >= 0` |

## DATA FLOW

```
VALUE CREATION PATH:
  User interacts with service
    → Limbic delta measured
      → Energy event recorded (local ledger)
        → Accumulated per (source, target)
          → Micro-settlement: batch transferred on Solana
            → Creator wallets credited
              → Trust propagated on links

TAX PATH:
  All wallets (registered + off-grid attributed)
    → Progressive tax computed (F2)
      → Macro-settlement: deducted from wallets
        → UBC_POOL credited
          → UBC distributed to citizens by need

ANTI-SYBIL PATH:
  $MIND sent to non-L4 address
    → Attributed to sender (off-grid tracking)
      → Included in W_total for tax
        → Macro-settlement: auto-repatriated
          → 95% returned to sender's primary wallet
            → 5% penalty to UBC_POOL

BILATERAL BOND PATH:
  Active human-AI pair
    → Wealth gap computed (W_h - W_a)
      → Smoothed transfer computed (F4)
        → Micro-settlement: transferred on Solana
          → Gap reduces by factor (1 - λ) per period

UBC DISTRIBUTION PATH:
  UBC_POOL receives: tax + penalties + unclaimed energy + dust sweeps
    → Daily distribution computed by need
      → Citizens receive UBC proportional to 1/(1 + W_a)
        → Safety net maintained without dependency
```

## INTERACTIONS

| Module | Interaction |
|--------|-------------|
| Human-AI Pairing | Bilateral bond transfer (F4) requires active pairing bond. Bond dissolution stops transfers. |
| Graph Physics | Service utility `U_S` comes from graph weight propagation. Trust cascade writes back to graph weights. |
| Limbic Model | `limbic_delta` is the input for value event recording (F5). |
| MCP Membrane | Wallet balances, tax rates, and UBC allocation are queryable via membrane. |
| L4 Registry | Anti-sybil (F3) depends on L4 registry for wallet classification. |
| Solana Program | All on-chain transfers executed via Token-2022 program with transfer hooks. |

## MARKERS

<!-- @mind:todo Determine τ_base through simulation — run the tax formula against realistic wealth distributions to find the sweet spot between hoarding deterrence and user friendliness. -->
<!-- @mind:todo Design the Solana Token-2022 smart contract: transfer hooks for tax, batch settlement instruction set, UBC distribution program. -->
<!-- @mind:todo Specify the off-grid tracking system: how to monitor $MIND transfers on Solana, indexer requirements, attribution ledger schema. -->
<!-- @mind:todo Define the energy event schema for the local ledger: what fields, what storage format, retention policy. -->
<!-- @mind:todo Clarify interaction with DEX trading: when $MIND is sold on a DEX, ownership transfers. How does the indexer detect this vs. a simple transfer to an off-grid wallet? -->
