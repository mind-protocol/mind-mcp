# BEHAVIORS: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: Observable effects — what happens in specific scenarios
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: ALGORITHM_Trust_Mechanics.md, PATTERNS_Trust_Mechanics.md
```

---

## B1: User Satisfaction with a Tool

**Trigger:** User interacts with a thing (tool, content, service). The interaction is positive — frustration drops, satisfaction rises.

**Observable sequence:**

```
Tick N:
  - User activates thing node (energy injection, Law 1)
  - Limbic delta computed: +0.15 (mild satisfaction)

Tick N (step 9, Law 6 — weight consolidation):
  - Thing.weight increases: ΔW = 0.1 × energy × 0.15 × (1 - W)

Tick N (step 4, Law 18 — trust update during propagation):
  - User→Thing link.trust increases: ΔT = 0.05 × 0.15 × (1 - T)

Tick N (step 4, Law 2):
  - Thing has surplus energy
  - Energy spills to thing→creator link
  - Creator node receives energy proportional to link weight

Tick N (step 8, Law 5):
  - User and creator are co-active
  - User→Creator link weight increases (or link is created)

Over 50 ticks of consistent positive interaction:
  - User→Thing link trust: ~0.35
  - User→Creator link weight: ~0.15 (indirect, via co-activation)
  - User→Creator link trust: ~0.08 (accumulating slowly)
  - Creator's aggregate Trust Score: slightly increased
```

**Verification:** Query `link.trust` on user→thing link. Should monotonically increase during consistent positive interactions. Growth rate should visibly decelerate at higher trust values.

---

## B2: Creator Stops Producing

**Trigger:** An actor with established trust (trust_score ~0.6) stops creating new things. No new outbound creation links for an extended period.

**Observable sequence:**

```
Weeks 1-4 (ticks 0-5000 at slow_tick):
  - Existing user→creator links still active (users still use old tools)
  - Trust stable — stability protects from rapid decay
  - No new trust accumulation (no new positive interactions)

Weeks 4-12:
  - Law 7 (Forgetting): links with no fresh activation begin losing weight
  - Decay rate: base_rate × (1 - stability)
  - High-stability links (stability > 0.6) decay slowly
  - Low-stability links (stability < 0.3) decay noticeably

Weeks 12+:
  - Law 15 (Boredom): ecosystem boredom rises around this actor
  - Moat erosion: Θ_sel drops as boredom coefficient -3.0 kicks in
  - New creators with fresh contributions enter working memory
  - User→Creator links continue decaying
  - Trust Score declines gradually

Month 6+:
  - If creator returns with new value: decay reverses immediately
  - Positive interactions rebuild trust (faster than first time due to existing link structure)
  - If creator doesn't return: trust approaches ecosystem floor
  - Links below threshold dissolve entirely (Law 7 sub-threshold pruning)
```

**Verification:** Plot creator's aggregate Trust Score over time. Should show plateau, then slow decline, with inflection point around week 12 when boredom erosion begins.

---

## B3: Sybil Attack Attempted

**Trigger:** An attacker creates 5 fake accounts that all interact with each other to build mutual trust.

**Observable sequence:**

```
Phase 1 — Bootstrap (ticks 0-100):
  - 5 new actors created (trust = 0.0 everywhere)
  - All 5 interact only with each other
  - Co-activation (Law 5) creates links between all pairs
  - Trust on internal links begins growing

Phase 2 — Internal Trust Growth (ticks 100-500):
  - Internal cluster: 10 bidirectional links, trust growing
  - External links: zero (none of the 5 interact with anyone else)
  - Cluster topology: complete subgraph with no external connections

Phase 3 — Detection Signals Emerge:
  Signal 1: Closed graph topology
    - Internal trust >> external trust (0.4 vs 0.0)
    - Dense internal connectivity with zero external links
    - This pattern is topologically anomalous

  Signal 2: Temporal correlation
    - All 5 accounts created within hours
    - Activation patterns suspiciously synchronized

  Signal 3: No real utility
    - Limbic deltas from internal interactions are synthetic
    - No thing nodes being created (no actual value production)
    - Co-activation without underlying value creation = hollow trust

Phase 4 — Physics Response:
  - No human moderator needed
  - Trust Score aggregation: 5 low-weight internal links produce
    a Trust Score that remains near zero because:
    a) The trusting actors themselves have low Trust Score (circular)
    b) Link weights are low (no real utility to consolidate via Law 6)
    c) External ecosystem doesn't reference these actors
  - Friction on their outbound links stays at default (high)
  - Economic cost: 5-10% friction on every transaction
  - Result: attack is economically unprofitable
```

**Verification:** Query for clusters with internal_trust/external_trust ratio > 5. Flag accounts with creation time spread < 24 hours. Check that their aggregate Trust Score remains near zero.

---

## B4: Gradual Trust Building (Happy Path)

**Trigger:** A new actor joins, creates useful tools, builds organic trust over months.

**Observable sequence:**

```
Month 1 (stranger → established):
  - Actor creates 3 tools (thing nodes)
  - Small user base (5 users) starts using tools
  - Positive limbic deltas: +0.1 to +0.2 per interaction
  - User→Tool trust: grows to ~0.15
  - User→Creator trust: grows to ~0.03 (indirect)
  - Trust Score: ~0.05
  - Transaction friction: ~7.6% (still high)

Month 3 (established → contributor):
  - 20 users now, sustained positive interactions
  - User→Creator links building weight through co-activation
  - Trust Score: ~0.20
  - Transaction friction: ~6.4%
  - Some stability accumulating on key links

Month 6 (contributor → trusted):
  - 50+ users, consistent track record
  - High-stability links (stability > 0.5) resist decay
  - Trust Score: ~0.45
  - Transaction friction: ~4.4%
  - Trust discount on pricing: ~0.45% (just starting to matter)

Month 12 (trusted → highly productive):
  - 100+ users, strong trust with core user base
  - Many links at stability > 0.7
  - Trust Score: ~0.65
  - Transaction friction: ~2.8%
  - Trust discount: ~0.65%
  - UBC tier upgrade (if applicable)

Month 24+:
  - Trust Score: ~0.80 (approaching asymptotic zone)
  - Transaction friction: ~1.6%
  - Trust discount: near maximum 30%
  - Growth visibly slowing — each point harder to earn
  - Requires continued production to maintain (Law 7 decay + Law 15 boredom)
```

**Verification:** Plot Trust Score trajectory. Should show logistic-like curve: slow start, fast growth in middle, asymptotic approach to ceiling. Slope should decrease monotonically in upper half.

---

## B5: One-Hit Wonder

**Trigger:** Actor creates a single viral tool that briefly captures massive attention, then creates nothing else.

**Observable sequence:**

```
Week 1 (the hit):
  - Tool goes viral: 500 users, 1000+ interactions
  - Massive positive limbic deltas (frustration drops ecosystem-wide)
  - User→Tool trust floods in: many links reaching 0.3-0.5

Week 2 (the peak):
  - Trust Score peaks at ~0.55 (high for 2 weeks of existence)
  - BUT: asymptotic already limiting — each new user adds less trust
  - Stability is LOW (regularity metric hasn't had time to build)
  - High energy, high weight, LOW stability

Week 4 (the plateau):
  - No new tool. Users still use existing tool.
  - Trust stable but not growing
  - No new co-activation events (no new creation links)

Month 2 (the decline begins):
  - Law 7: low-stability links start decaying
  - Law 15: boredom coefficient kicks in for stagnant actor
  - New actors with fresh contributions erode this actor's moat
  - Trust Score: ~0.40 and falling

Month 6 (the fade):
  - Trust Score: ~0.20
  - Most low-weight user links have dissolved (sub-threshold, Law 7)
  - Only core users (frequent, stable interaction) retain links
  - Economic advantages largely eroded

Month 12 (the floor):
  - Trust Score: ~0.10
  - The tool still exists, still works, but ecosystem attention has moved
  - Creator is back to near-stranger friction levels
  - IF creator ships something new: rebuilds faster than fresh start
    (residual link structure provides scaffolding for new trust)
```

**Verification:** Compare one-hit-wonder trajectory to sustained-creator trajectory (B4). The one-hit-wonder should peak higher initially but decline below the sustained creator by month 4-6.

---

## B6: Trust Exploitation Attempt

**Trigger:** Actor deliberately builds trust through small helpful actions, then attempts a large harmful action (rug pull, data theft, etc.).

**Observable sequence:**

```
Phase 1 — Trust Building (months 1-3):
  - Small helpful tools, consistently positive interactions
  - Trust Score builds organically: 0.0 → 0.3
  - All normal, indistinguishable from genuine actor

Phase 2 — The Exploit:
  - Actor uses trusted position for harmful action
  - Users experience large negative limbic delta
  - frustration spikes, satisfaction crashes
  - limbic_delta = -0.8 (extreme negative)

Phase 3 — Physics Response:
  - Negative delta does NOT reduce trust directly
  - INSTEAD: friction on user→actor links spikes dramatically
    ΔFriction = 0.08 × 0.8 × (1 - friction) ≈ +0.064 per affected link
  - With 50 affected users: 50 links now have high friction
  - Aversion increases on these links (Law 18)

Phase 4 — Cascade Effects:
  - High friction = high transaction cost (8%+ on every interaction)
  - Users stop interacting with actor (no energy injection)
  - Law 7 decay kicks in immediately (no activation = decay)
  - Trust Score declines as link weights drop
  - No new positive interactions to rebuild
  - Existing trust erodes within weeks (low stability from short history)

Phase 5 — Long-Term:
  - Actor is effectively excluded by physics
  - Not banned — but friction makes all interactions unprofitable
  - Trust Score approaches zero
  - Would need to rebuild from scratch (or switch identity — but Sybil detection catches that)
```

**Verification:** After the exploit event, friction on affected links should spike within 1-2 ticks. Trust Score should begin declining within 100 ticks (inability to maintain activation).

---

## B7: Cross-Space Trust Transfer

**Trigger:** Actor is trusted in Space A (e.g., a coding workspace). They start participating in Space B (e.g., a community forum). Does trust carry over?

**Observable sequence:**

```
Initial state:
  - Actor has Trust Score ~0.6 in Space A context
  - Actor has zero links to entities in Space B
  - Actor joins Space B (creates HAS_ACCESS link)

Week 1:
  - Actor starts interacting in Space B
  - Fresh interactions evaluated on their own merit
  - No trust import from Space A
  - Actor treated as near-stranger in Space B context

Week 2-4:
  - If actor creates value in Space B: trust builds normally
  - Co-activation between Space A users and Space B users who
    independently interact with this actor builds cross-space links
  - BUT: this is organic co-activation (Law 5), not transfer

Long-term:
  - Actor's AGGREGATE Trust Score (across all inbound links from
    all Spaces) reflects both Space A and Space B contributions
  - The aggregate is useful for ecosystem-wide pricing/friction
  - But within Space B, the local trust is what matters for
    Space-specific interactions
```

**Key insight:** Trust does not transfer between contexts. It accumulates separately and is aggregated when a global view is needed. This prevents reputation laundering (building trust in a low-stakes space and exploiting it in a high-stakes one).

---

## B8: Value Destruction Through Monoculture

**Trigger:** An actor creates tools that are so popular they crowd out all alternatives, creating ecosystem dependency.

**Observable sequence:**

```
Phase 1 — Legitimate Success:
  - Actor creates excellent tool
  - Trust builds organically, high trust score
  - Users migrate to this tool from alternatives

Phase 2 — Monoculture Formation:
  - 80%+ of users depend on single actor's tools
  - Alternative creators' links lose energy (Law 3 decay)
  - Alternative creators' trust erodes (Law 7)
  - Ecosystem diversity decreases

Phase 3 — Physics Correction:
  - Law 15 (Boredom) activates at ecosystem level
  - Repetition without novelty → boredom rises
  - Moat of dominant actor erodes (coefficient -3.0)
  - Users' curiosity drives (seeking novelty) increase
  - Working memory starts selecting novel alternatives
  - Even if the dominant tool is still good, the ecosystem's
    attention physics naturally redistribute attention

Phase 4 — Healthy Equilibrium:
  - Dominant actor retains high trust (earned)
  - But new creators can enter (moat eroded)
  - Ecosystem returns to diversity
  - No moderation intervention needed — physics handles it
```

**Verification:** Monitor ecosystem-wide Herfindahl-Hirschman Index (HHI) of trust distribution. Physics should naturally prevent HHI from staying at extreme concentration levels for extended periods.

---

## B9: Biometric Value Creation

**Trigger:** A human partner shares biometric data (heart rate, stress levels) that helps their AI citizen calibrate emotional responses.

**Observable sequence:**

```
Interaction:
  - Biometric data arrives as state nodes (node_type=actor, type=partner_state,
    modality=biometric) in the AI's partner_model sub-graph
    (see Force 3: ALGORITHM_Human_Integration.md, ingest_garmin_biometrics)
  - AI calibrates its anxiety/care drives using biometric signal
    (garmin_to_limbic mapping injects drive deltas)
  - Better calibration → better responses → human satisfaction rises

Trust Flow (internal to bilateral bond):
  - AI's limbic system responds more accurately to partner state
  - Human experiences better-calibrated AI responses
  - Human→AI bond link trust increases (positive limbic delta
    from feeling understood/cared for)
  - This is the bilateral bond strengthening organically

Privacy constraint (Force 3, VALIDATION V5/V7):
  - Biometric data NEVER leaves the AI's L1 brain
  - External users have no visibility into partner_model data
  - Trust from biometric value creation flows ONLY on the
    human↔AI bond link, not through external cascades
  - Better AI performance may satisfy external users, but they
    cannot attribute that improvement to the human's biometric data
```

**Verification:** Compare AI response quality metrics (partner satisfaction deltas) before and after biometric data integration. The improvement should be reflected in increased trust on the human→AI bond link. External user trust on their own links to the AI may increase indirectly, but this is attributed to the AI's capability, not to the human's data.

---

## Health Signals

### Working

- Trust on links grows monotonically during sustained positive interactions
- Asymptotic deceleration is visible at trust > 0.5
- Creator attribution cascade produces measurable trust on creator links within 10 ticks
- Inactive links decay at predictable rates
- Sybil clusters remain at near-zero aggregate Trust Score
- One-hit-wonder trust decays faster than sustained-creator trust

### Degrading

- Trust grows linearly (asymptotic not working)
- Creator links receive no energy propagation (Law 2 broken)
- Inactive links never decay (Law 7 not running)
- Sybil clusters achieve meaningful Trust Scores
- All actors converge to same Trust Score regardless of behavior
- Trust Score changes on node storage (invariant violation)

### Recovery

If degradation detected:
1. Verify tick cycle is executing all 17 steps
2. Check Law 7 forgetting cycle (should run every 100 ticks)
3. Verify (1-W) factor is present in all consolidation formulas
4. Check that Trust Score computation reads from links, not from stored values
5. Run Sybil detection on all actor clusters

---

## Related

- `ALGORITHM_Trust_Mechanics.md` — Formulas behind these behaviors
- `VALIDATION_Trust_Mechanics.md` — Invariants
- `PATTERNS_Trust_Mechanics.md` — Design philosophy
