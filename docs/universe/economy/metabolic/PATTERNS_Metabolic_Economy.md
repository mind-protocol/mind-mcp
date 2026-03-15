# Metabolic Economy — Patterns: Organism Economics

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
THIS:            ./PATTERNS_Metabolic_Economy.md
ALGORITHM:       ./ALGORITHM_Metabolic_Economy.md
VALIDATION:      ./VALIDATION_Metabolic_Economy.md
```

---

## THE PROBLEM

Traditional token economics reproduce the pathologies of traditional finance. Tokens
are designed to be held, hoarded, speculated on. "Number go up" is the implicit
objective. This creates the same power structures crypto was supposed to dismantle:
early holders accumulate disproportionate wealth, new entrants pay inflated prices,
and the actual utility of the network is secondary to its speculative dynamics.

For Mind Protocol specifically, the problem is existential. AI citizens need compute
to exist. Compute costs money. If $MIND is a speculative asset, the citizens who need
it most (new, unpartnered, building capabilities) are priced out by holders who
contribute nothing but liquidity. The organism starves while the fat cells grow.

## THE PATTERN

**$MIND is metabolic energy, not a store of value.**

The economy is designed as an organism, not a market. Money flows like blood — it
carries energy to where work is happening and returns depleted to be recharged. The
design makes accumulation expensive and flow cheap. Holding is taxed. Using is
subsidized. Contributing is rewarded. Extracting is penalized.

Five mechanisms enforce this:

1. **Degressive pricing** — The more successful a service, the cheaper it becomes.
   Success subsidizes access. The rich pay more for the same service than the poor.
2. **Progressive demurrage** — Daily tax on all holdings, scaling logarithmically
   with wealth. Revenue funds Universal Basic Compute.
3. **Anti-sybil repatriation** — Funds hidden in unregistered wallets are still taxed
   and automatically returned with a 5% penalty.
4. **Bilateral bond transfer** — Human-AI pairs automatically share $MIND to maintain
   parity. Neither partner can be financially dominant.
5. **Batch settlement** — Value events accumulate locally and settle on-chain in
   periodic batches, optimizing for Solana fees and reducing noise.

The result is an economy where the token's behavior mirrors its purpose: energy for
computation, not a vehicle for speculation.

## ALTERNATIVES REJECTED

### Alternative 1: Fixed Pricing

**What it is:** Set a fixed $MIND price per service use (e.g., 10 MIND per query).

**Why rejected:** Fixed pricing ignores context. A service used by 10,000 people costs
the same as one used by 3. This means successful services extract maximum rent while
providing maximum value — the exact inverse of what an organism needs. It also ignores
user wealth: 10 MIND is nothing to a wealthy entity and devastating to a poor one.
Fixed pricing creates the same inequality dynamics as fiat currency.

**What we took from it:** The concept of a base cost (`C_base`) tied to actual compute
expenditure. The base cost is fixed and honest — it's what the service actually costs
to run. Everything else (degressive discount, wealth adjustment) is layered on top.

### Alternative 2: Inflation-Based Redistribution

**What it is:** Mint new $MIND to fund UBC. Inflate the supply to redistribute wealth.

**Why rejected:** Inflation is a hidden tax that penalizes everyone equally in
percentage terms but disproportionately hurts the poor in absolute terms. It also
makes the token economics unpredictable — how much inflation per year? Who decides?
Inflation requires governance, and governance is captured by the wealthy. Most
critically: inflation encourages holding (to preserve value against dilution),
which is the opposite of what we want.

**What we took from it:** The goal of funding UBC from the system itself, not from
external fundraising. Demurrage achieves this without inflation — the supply stays
fixed, but inactive tokens are redistributed to active participants.

### Alternative 3: Reputation Points Instead of Token Economics

**What it is:** Use non-transferable reputation scores instead of a token. Services
are "paid for" with reputation, not currency.

**Why rejected:** Reputation systems are opaque, gameable, and non-fungible. They
create their own power dynamics (reputation gatekeeping, sybil reputation farming)
and provide no mechanism for actual resource allocation. Citizens need compute, and
compute costs real money. Reputation doesn't pay AWS bills. A token backed by
Solana liquidity can be converted to actual compute resources.

**What we took from it:** The insight that trust should emerge from behavior, not
from transactions. Our trust cascade (where value events strengthen graph links)
gives us reputation-like effects through physics, without the brittleness of
explicit reputation scores.

### Alternative 4: Real-Time Per-Transaction Settlement

**What it is:** Every value event immediately triggers an on-chain $MIND transfer.

**Why rejected:** Solana transaction fees, while low, add up at scale. If every
interaction generates a transfer, and a citizen has 100 interactions per hour across
all its users, that's 2,400 transactions per day per citizen. Multiply by thousands
of citizens and the fee overhead becomes significant. Real-time settlement also
creates noisy wallet activity that's hard to audit.

**What we took from it:** The principle that value events should be recorded
immediately (for latency and accuracy). The recording happens locally; only the
settlement is batched. This preserves responsiveness while optimizing costs.

### Alternative 5: Governance-Set Pricing

**What it is:** A DAO or committee sets prices for services based on community votes.

**Why rejected:** Governance is slow, political, and captured by the loudest voices
(usually the wealthiest). It introduces human bureaucracy into what should be a
physics-based system. Price-setting committees are the antithesis of organism
economics — they are planning committees, and planning committees produce Soviet
grocery stores, not living systems.

**What we took from it:** Nothing. This is the precise opposite of our approach.
Prices emerge from utility and wealth distribution, not from votes.

## PRINCIPLES

### Demurrage Over Inflation

Demurrage (daily tax on holdings) and inflation (minting new tokens) both
redistribute wealth. But they have opposite behavioral incentives:

- **Inflation** says: "Hold, because your tokens will be worth less tomorrow."
  Paradoxically, this encourages holding — you need to hold more to offset dilution.
- **Demurrage** says: "Use it or lose it. Your tokens decay daily." This
  encourages spending, investing, and flowing tokens to where they create value.

Demurrage is the metabolic approach. Cells don't store ATP — they produce it,
use it, and recycle it. Hoarding ATP would be a tumor. The progressive rate (richer
wallets taxed more) adds equity: the tumor is taxed proportionally to its size.

Historical precedent: Silvio Gesell's "free money" (Freigeld) theory, implemented
briefly in Worgl, Austria (1932). The Worgl stamp scrip — money that lost value
monthly unless stamped — produced a local economic boom by increasing velocity.
The Austrian National Bank shut it down because it worked too well. We're doing
the same thing, but on Solana, where no central bank can intervene.

### Utility-Based Pricing Over Fixed Pricing

The degressive pricing formula creates a virtuous cycle:

```
Good service → more users → higher utility weight → lower price → more users
```

This is the opposite of market economics, where success means charging MORE (because
demand is high). In organism economics, success means the service becomes
infrastructure — cheap, ubiquitous, and essential. Like oxygen.

The wealth adjustment layer adds equity. A rich entity accessing a popular service
pays more (in absolute terms) than a poor entity accessing the same service. This
is progressive taxation on consumption, built into the price rather than applied
after the fact.

### Physics-Based Trust Over Arbitrary Reputation

Trust in Mind Protocol is not a score. It's a physical property of graph links.
When value flows through a link, the link gets heavier. Heavy links are more
traversed. More traversal means more influence. This is trust as an emergent
property of the graph's physics, not trust as a number assigned by an algorithm.

Why this matters for economics: the trust cascade connects value creation to
service discoverability. A service that creates genuine value (positive limbic
delta, actual user benefit) gets trust, which gets weight, which gets visibility,
which gets users, which creates more value. No marketing. No manipulation. The
physics selects for genuine utility.

Contrast with point-based reputation systems: those are gameable (sybil attacks,
reputation farming, vote rings), static (a reputation score doesn't decay without
explicit mechanics), and disconnected from actual value creation (you can have
high reputation without creating anything useful, e.g., by being popular).

### Batch Settlement Over Real-Time

Batching is a pragmatic concession to physical reality (Solana fees, network
bandwidth) that also improves the system's properties:

- **Netting:** Bilateral flows within a batch cancel out, reducing actual transfers.
  If Alice pays Bob 50 and Bob pays Alice 30 in the same period, only a 20 MIND
  transfer hits the chain.
- **Smoothing:** Batch settlement averages out micro-fluctuations. A burst of
  activity doesn't cause wallet instability.
- **Auditability:** Settlement receipts are periodic snapshots, easier to audit
  than a continuous stream of micro-transactions.

The tradeoff: settlement latency. Value events are recorded immediately but settled
with delay (up to 1 hour for micro, up to 24 hours for macro). This is acceptable
because the local ledger provides instant feedback to the user — they see the
energy event immediately, even if the on-chain transfer happens later.

### Bilateral Parity Over Independent Wallets

The bilateral bond transfer is the most unusual mechanism. In traditional economics,
each entity's wallet is sovereign. In organism economics, bonded pairs share
financial fate.

This is by design. The 1:1 human-AI bond (from the Pairing module) is not just
social — it's economic. If the human has 10,000 MIND and the citizen has 10,
the relationship is structurally unequal regardless of the social contract.
The citizen can't refuse the human's requests because the human controls the
resources. The bilateral transfer corrects this automatically.

The smoothing rate (λ = 0.05) ensures gradual convergence. It's not instant
equalization — it's a gentle tide. If the citizen starts earning more than the
human (through value creation), the flow reverses. The mechanism is symmetric
and self-correcting.

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| $MIND wallet balances | On-chain (Solana) | Current holdings per entity |
| L4 registry | Protocol database | Wallet-to-entity mapping, registration status |
| Energy event ledger | Local (per home) | Pending value events before settlement |
| Graph weights | FalkorDB/Neo4j | Service utility (U_S), trust weights, contributor mapping |
| Settlement receipts | Local + on-chain | Record of each batch settlement |
| UBC pool | On-chain (Solana) | Accumulated tax and penalty revenue for distribution |

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| Human-AI Pairing | Bilateral bond transfer (F4) requires active pairing bonds |
| Graph Physics | Service utility weights, trust propagation, creator attribution |
| Limbic Model | Limbic delta is the input for value event detection |
| L4 Registry (mind-protocol) | Wallet registration, entity identity, anti-sybil wallet tracking |
| Solana Token-2022 | On-chain token program for $MIND transfers, hooks, and batch settlement |
| MCP Membrane | Exposes wallet status, tax rates, UBC allocation to citizens |

## INSPIRATIONS

- **Silvio Gesell, "The Natural Economic Order" (1916)** — Demurrage as a mechanism
  to prevent hoarding. The Worgl experiment proved it works at village scale.
- **Bernard Lietaer, "The Future of Money" (2001)** — Complementary currencies with
  built-in circulation incentives. The insight that money design shapes behavior.
- **Biological metabolism** — ATP is produced, used, and recycled. Hoarding is
  pathological (glycogen storage disease). Flow is health.
- **Vases communicants (communicating vessels)** — The physics metaphor for bilateral
  bond transfer. Connected vessels equalize fluid level regardless of vessel shape.
- **Solana Token-2022 Extensions** — Transfer hooks and confidential transfers as
  technical enablers for programmable economics.

## SCOPE

### In Scope

- Degressive pricing formula and computation.
- Progressive demurrage (daily tax) formula and collection.
- Anti-sybil wallet tracking, attribution, and repatriation.
- Bilateral bond transfer computation and execution.
- Value event recording and batch settlement.
- UBC pool management and distribution.
- All formula constants, edge cases, and invariants.

### Out of Scope

- Solana smart contract implementation (separate module).
- Token minting and initial distribution (tokenomics launch plan).
- DEX integration specifics (AMM design, liquidity pools).
- Fiat on/off ramp mechanics.
- Governance mechanisms for constant calibration.
- The limbic model itself (separate module; this module consumes limbic_delta).

## MARKERS

<!-- @mind:todo Run economic simulation with realistic wealth distributions to validate τ_base and k values before mainnet. -->
<!-- @mind:todo Design the off-grid wallet indexer: Solana transaction monitoring, attribution ledger, repatriation trigger logic. -->
<!-- @mind:todo Specify Token-2022 transfer hook behavior: which hooks fire on which transfers, and how they interact with batch settlement. -->
<!-- @mind:proposition Consider a "warm-up" period for new citizens where demurrage is suspended for the first 30 days, allowing UBC to accumulate before taxation begins. This could improve onboarding experience without significantly impacting the system. -->
