# ALGORITHM: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: Formulas, cascades, and computational procedures for trust
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: schema.yaml (Laws 2, 5, 6, 7, 15, 18), PATTERNS_Trust_Mechanics.md
```

---

## 1. Limbic Delta Computation

The Limbic Delta is the primary signal that drives trust changes. It measures the net change in limbic state during/after an interaction.

### 1.1 Definition

```python
def limbic_delta(drives_before: dict, drives_after: dict) -> float:
    """
    Compute net limbic change from an interaction.

    Positive = user benefited (satisfaction up, frustration down).
    Negative = user was harmed (frustration up, satisfaction down).
    Zero = neutral interaction.
    """
    satisfaction_delta = drives_after["satisfaction"] - drives_before["satisfaction"]
    frustration_delta = drives_after["frustration"] - drives_before["frustration"]
    anxiety_delta = drives_after["anxiety"] - drives_before["anxiety"]

    # Primary signal: satisfaction gain minus frustration gain
    # Anxiety reduction is a secondary positive signal (weighted lower)
    delta = satisfaction_delta - frustration_delta - 0.5 * anxiety_delta

    return delta
```

### 1.2 Drive Snapshot Timing

- **Before:** Snapshot drives at stimulus injection (Law 1, step 2 of tick cycle)
- **After:** Snapshot drives at next limbic update (Law 14, step 1 of NEXT tick cycle)
- **Window:** One full tick cycle. Longer-term effects accumulate over multiple deltas.

### 1.3 Bounds

```
limbic_delta ∈ [-2.0, +2.0]
# Theoretical max: satisfaction goes 0→1 (+1) AND frustration goes 1→0 (-(-1)=+1) AND anxiety goes 1→0 (-0.5×(-1)=+0.5)
# Practical range: [-0.3, +0.3] for typical interactions
```

---

## 2. Trust Update on Links (Law 18 Extension)

When an interaction produces a positive limbic delta, the trust on the relevant link is updated.

### 2.1 Direct Trust Update

```python
def update_link_trust(link: Link, limbic_delta: float, dt: float = 1.0) -> float:
    """
    Update trust on a link based on limbic delta.

    Only positive deltas increase trust.
    Negative deltas increase friction (not decrease trust directly).
    Trust decrease comes from Law 7 decay, not from negative interactions.
    """
    if limbic_delta > 0:
        # Trust gain — asymptotic, same shape as Law 6 consolidation
        beta = 0.05  # Trust learning rate
        delta_trust = beta * limbic_delta * (1.0 - link.trust) * dt
        link.trust = min(1.0, link.trust + delta_trust)

    if limbic_delta < 0:
        # Negative interaction increases friction, not decreases trust
        gamma = 0.08  # Friction learning rate (faster than trust — negativity bias)
        delta_friction = gamma * abs(limbic_delta) * (1.0 - link.friction) * dt
        link.friction = min(1.0, link.friction + delta_friction)

    # Update affinity/aversion (co-evolve with trust/friction)
    if limbic_delta > 0:
        link.affinity = min(1.0, link.affinity + 0.02 * limbic_delta * (1.0 - link.affinity))
    if limbic_delta < 0:
        link.aversion = min(1.0, link.aversion + 0.03 * abs(limbic_delta) * (1.0 - link.aversion))

    return link.trust
```

### 2.2 Why Negative Deltas Don't Reduce Trust

Trust reduction happens through temporal decay (Law 7), not through punishment. This prevents:
- **Revenge attacks** — One bad interaction shouldn't wipe years of trust
- **Volatility** — Trust should be stable, not oscillating
- **Gaming** — An attacker can't reduce a competitor's trust by having bad interactions with them

Instead, negative experiences increase **friction** on the link. High friction means higher costs (Pattern 5 in Economy), not lower trust. Trust decays naturally when the link is no longer positively activated.

### 2.3 Asymptotic Properties

```
At trust = 0.1:  delta_trust ≈ beta × LD × 0.9  (fast growth)
At trust = 0.5:  delta_trust ≈ beta × LD × 0.5  (moderate growth)
At trust = 0.9:  delta_trust ≈ beta × LD × 0.1  (10x slower than at 0.1)
At trust = 0.99: delta_trust ≈ beta × LD × 0.01 (100x slower than at 0.1)
```

This makes trust=0.95+ extremely expensive to achieve. It requires sustained, consistent, high-utility interactions over a long period.

### 2.4 Sovereign Cascade Alignment as Trust Signal

Within the bilateral bond (Force 3: Human Integration), the Sovereign Cascade alignment fidelity score acts as an additional trust modifier on the human<->AI bond link.

```python
def update_bond_trust_from_alignment(bond_link: Link, alignment_score: float):
    """
    Alignment fidelity (Force 3, measure_alignment_fidelity) measures how
    accurately the AI predicts the human's decisions. High alignment =
    the AI demonstrably understands its human = trust-positive signal.

    This supplements the standard limbic_delta trust update (section 2.1).
    It does NOT replace it — both signals contribute independently.

    See: Force 3, ALGORITHM_Human_Integration.md, measure_alignment_fidelity
    """
    if alignment_score is None:
        return  # Insufficient predictions for calibration

    # Alignment above 80% threshold: positive trust signal
    if alignment_score >= 0.80:
        alignment_bonus = 0.02 * (alignment_score - 0.80) * (1.0 - bond_link.trust)
        bond_link.trust = min(1.0, bond_link.trust + alignment_bonus)

    # Alignment below 75% (cascade suspended): friction signal
    if alignment_score < 0.75:
        misalignment_friction = 0.03 * (0.75 - alignment_score) * (1.0 - bond_link.friction)
        bond_link.friction = min(1.0, bond_link.friction + misalignment_friction)
```

**Design note:** The alignment fidelity signal is slow-moving (evaluated over 100 predictions) and structurally meaningful. It represents deep understanding, not moment-to-moment satisfaction. The trust bonus is small per evaluation but accumulates over the lifetime of the bond.

---

## 3. The Creator Attribution Cascade

This is the full algorithmic cascade from user satisfaction to creator trust accumulation.

### 3.1 Step-by-Step

```python
def creator_attribution_cascade(
    user: Node,
    thing: Node,
    creator: Node,
    user_thing_link: Link,
    thing_creator_link: Link,
    limbic_delta: float,
    tick: int
):
    """
    Full cascade: user satisfaction → thing consolidation → creator trust.

    This is NOT a separate system. It is Laws 2, 5, 6, 18 executing in sequence
    during the normal tick cycle. Presented here as a single function for clarity.
    """

    # === STEP 1: Thing Consolidation (Law 6) ===
    # Positive limbic delta means the thing was useful
    if limbic_delta > 0:
        utility = limbic_delta  # Limbic delta IS the utility signal
        alpha = 0.1  # Consolidation learning rate
        avg_energy = thing.energy  # Current activation

        # Asymptotic weight gain
        delta_w = alpha * avg_energy * utility * (1.0 - thing.weight)
        thing.weight += delta_w

        # Stability grows from regularity (not raw frequency)
        # (computed separately in Law 6 regularity tracker)

    # === STEP 2: User→Thing Link Trust Update (Law 18) ===
    update_link_trust(user_thing_link, limbic_delta)

    # === STEP 3: Surplus Propagation (Law 2) ===
    # Thing has surplus energy from the interaction
    propagation_threshold = 0.5  # Configurable
    surplus = max(0, thing.energy - propagation_threshold)

    if surplus > 0:
        # Energy flows to ALL neighbors, including creator
        # Proportional to link weight (thing→creator link)
        total_outbound_weight = sum(
            link.weight for link in thing.outbound_links()
        )

        if total_outbound_weight > 0:
            creator_share = (thing_creator_link.weight / total_outbound_weight) * surplus
            creator.energy += creator_share
            thing.energy -= creator_share  # Conservation (Law 2)

    # === STEP 4: Co-activation Reinforcement (Law 5) ===
    # User and creator are both active (user directly, creator via propagation)
    # If user→creator link doesn't exist yet, it can be created here
    user_creator_link = get_or_create_link(user, creator)

    if user.energy > 0 and creator.energy > 0:
        # Hebbian: what fires together wires together
        coactivation_rate = 0.03
        delta_link_w = coactivation_rate * user.energy * creator.energy * (1.0 - user_creator_link.weight)
        user_creator_link.weight += delta_link_w

        # The user→creator link now exists and has weight
        # Trust on this link accumulates over repeated co-activations
        # via the normal trust update mechanism (Step 2 on future ticks)

    # === STEP 5: Indirect Trust Accumulation ===
    # Over time, repeated cascade executions cause:
    # - user→creator link weight to grow (Law 5)
    # - user→creator link trust to grow (Law 18, via co-activation signals)
    # - creator's Trust Score to increase (aggregation of all inbound trust)
    # This step is NOT explicit code — it is the emergent effect of Steps 1-4
    # running across many ticks.
```

### 3.2 Multi-Creator Attribution

When a thing has multiple creators (e.g., collaborative code):

```python
# Each creator has a creation link: thing→creator_i
# The weight on each creation link reflects contribution proportion
# Law 2 propagation distributes surplus proportionally
# No special-case code needed — topology handles it

# Example: thing with 3 creators
# thing→creator_A  weight=0.5 (primary author)
# thing→creator_B  weight=0.3 (major contributor)
# thing→creator_C  weight=0.2 (minor contributor)
# Surplus energy splits: 50%, 30%, 20% respectively
```

---

## 4. Trust Score Aggregation

When a single trust number is needed for an actor (pricing, membrane fees, UBC tier).

### 4.1 Weighted Mean (Current Proposal)

```python
def trust_score(actor: Node) -> float:
    """
    Compute aggregate trust score from all inbound trust-carrying links.

    Weighted by link weight — higher-weight links (more established relationships)
    contribute more to the score.
    """
    inbound = [link for link in actor.inbound_links() if link.trust > 0]

    if not inbound:
        return 0.0

    weighted_sum = sum(link.trust * link.weight for link in inbound)
    weight_sum = sum(link.weight for link in inbound)

    if weight_sum == 0:
        return 0.0

    return weighted_sum / weight_sum
```

### 4.2 Alternative: PageRank-Style (Under Consideration)

```python
def trust_score_pagerank(actor: Node, damping: float = 0.85, iterations: int = 20) -> dict:
    """
    PageRank-style trust propagation.

    Advantage: accounts for trust transitivity (trusted by trusted actors = more trust).
    Disadvantage: more expensive to compute, harder to explain.

    @mind:escalation — Which aggregation method? Weighted mean is simpler and
    sufficient for v1. PageRank adds transitivity but complexity. Decision needed.
    """
    # Standard PageRank with trust as edge weight
    N = total_actors()
    scores = {a: 1.0 / N for a in all_actors()}

    for _ in range(iterations):
        new_scores = {}
        for actor in all_actors():
            inbound = actor.inbound_links()
            rank = (1 - damping) / N
            for link in inbound:
                source = link.source
                source_outbound_weight = sum(l.weight for l in source.outbound_links())
                if source_outbound_weight > 0:
                    rank += damping * scores[source] * link.trust * link.weight / source_outbound_weight
            new_scores[actor] = rank
        scores = new_scores

    return scores
```

### 4.3 Constraint: Never Stored

```python
# WRONG — storing trust score
actor.trust_score = compute_trust_score(actor)  # NEVER DO THIS

# RIGHT — computing on demand
score = trust_score(actor)  # Computed from link topology each time
```

Caching is permitted for performance (with TTL), but the source of truth is always the link topology.

---

## 5. Trust Tempering Formulas

### 5.1 Asymptotic Saturation (Law 6)

Already embedded in all trust update formulas via the `(1 - current_value)` factor.

```python
# Growth rate at different trust levels:
# trust=0.0: growth_factor = 1.0   (maximum growth)
# trust=0.5: growth_factor = 0.5   (half speed)
# trust=0.8: growth_factor = 0.2   (one-fifth speed)
# trust=0.9: growth_factor = 0.1   (one-tenth speed)
# trust=0.95: growth_factor = 0.05 (one-twentieth speed)
# trust=0.99: growth_factor = 0.01 (one-hundredth speed)
```

### 5.2 Temporal Decay (Law 7)

```python
def decay_trust(link: Link, ticks_since_activation: int):
    """
    Unused links lose trust over time.
    Rate depends on stability — stable links decay slower.
    """
    base_decay_rate = 0.002  # Per tick
    stability_protection = link.stability  # [0, 1]

    effective_decay = base_decay_rate * (1.0 - stability_protection)

    link.trust = max(0.0, link.trust - effective_decay * ticks_since_activation)
    link.weight = max(0.0, link.weight - effective_decay * ticks_since_activation)

    # Sub-threshold dissolution
    if link.weight < 0.01 and link.trust < 0.01:
        dissolve_link(link)
```

### 5.3 Boredom Erosion (Law 15)

```python
def boredom_moat_erosion(actor: Node, boredom_level: float):
    """
    Stagnant high-trust actors lose their defensive moat.

    The -3.0 coefficient on boredom in the moat formula means:
    At boredom=0.5, moat drops by 1.5 points.
    At boredom=1.0, moat drops by 3.0 points (completely eroded).

    This allows new actors to displace stagnant ones in working memory
    and attention allocation.
    """
    moat = 5.0 + 2.0 * actor.arousal - 3.0 * boredom_level - 1.0 * actor.frustration

    # When moat drops below 0, the actor loses incumbency advantage
    # New actors with fresh contributions can enter WM and receive trust
    return max(0.0, moat)
```

---

## 6. Trust in Economic Formulas

### 6.1 Transaction Friction (from PATTERNS_Economy.md)

```python
def transaction_friction(trust_score: float, productivity_bonus: float) -> float:
    """
    Higher trust = lower friction. Can go negative (earn by transacting).
    """
    base_rate = 0.08  # 8% for unknown actors
    friction = base_rate * (1.0 - trust_score) - productivity_bonus
    return friction

# Examples:
# trust=0.0, prod=0.0:   friction = 0.08  (8%)
# trust=0.5, prod=0.0:   friction = 0.04  (4%)
# trust=0.8, prod=0.0:   friction = 0.016 (1.6%)
# trust=0.95, prod=0.01: friction = -0.006 (NEGATIVE — earns 0.6%)
```

### 6.2 Membrane Fee

```python
def membrane_fee(amount: float, trust_score: float, layer_gap: int) -> float:
    base_rate = 0.01 * layer_gap
    trust_reduction = min(0.5, trust_score * 0.005)
    return amount * base_rate * (1.0 - trust_reduction)
```

### 6.3 Effective Pricing

```python
def effective_price(base_cost: float, trust_score: float, utility_ema: float) -> float:
    trust_discount = min(0.3, trust_score * 0.01)  # Max 30%
    utility_rebate = min(0.2, utility_ema * 0.05)   # Max 20%
    return base_cost * (1.0 - trust_discount) * (1.0 - utility_rebate)
```

---

## 7. Destruction Detection Algorithms

### 7.1 Free-Rider Detection

```python
def detect_free_rider(actor: Node) -> float:
    """
    Returns free-rider score [0, 1].
    High score = consuming without producing.
    """
    inbound_energy = sum(link.energy for link in actor.inbound_links())
    outbound_energy = sum(link.energy for link in actor.outbound_links())

    if inbound_energy == 0:
        return 0.0  # No consumption = not free-riding

    # Ratio of consumption to production
    ratio = outbound_energy / (inbound_energy + 1e-6)

    # Second signal: creation link count
    creation_links = [link for link in actor.outbound_links()
                      if link.polarity[0] > 0.7]  # Strong outbound = creation
    uses_links = [link for link in actor.inbound_links()
                  if link.polarity[1] > 0.7]  # Strong inbound = consumption

    topology_ratio = len(creation_links) / (len(uses_links) + 1)

    # Combined score (both signals must agree)
    free_rider_score = (1.0 - min(1.0, ratio)) * (1.0 - min(1.0, topology_ratio))

    return free_rider_score
```

### 7.2 Sybil Detection

```python
def detect_sybil_cluster(actors: list) -> float:
    """
    Detect clusters of actors that only interact with each other
    (trust ring / Sybil attack).

    Signal 1: Closed loop — high internal trust, low external trust
    Signal 2: Temporal correlation — accounts activated at similar times
    """
    for cluster in find_dense_subgraphs(actors):
        internal_trust = mean(link.trust for link in internal_links(cluster))
        external_trust = mean(link.trust for link in external_links(cluster))

        # Sybil signal: internal >> external
        if internal_trust > 0.8 and external_trust < 0.1:
            # Check temporal correlation
            creation_times = [actor.created_at_s for actor in cluster]
            time_spread = max(creation_times) - min(creation_times)

            if time_spread < 86400:  # All created within 24 hours
                return 0.95  # High confidence Sybil

    return 0.0
```

### 7.3 Trust Exploitation Detection

```python
def detect_trust_exploitation(actor: Node) -> float:
    """
    Actor builds trust through small positive interactions,
    then exploits it in a large negative interaction.

    Signal: rapid trust accumulation followed by large negative limbic delta.
    """
    trust_velocity = compute_trust_velocity(actor, window=100)  # Last 100 ticks
    recent_friction = mean(link.friction for link in actor.recent_links(window=10))

    # High trust velocity (rapid gain) + recent high friction (exploitation)
    if trust_velocity > 0.1 and recent_friction > 0.5:
        return 0.8

    return 0.0
```

---

## 8. Limbic Delta per Value Type

Different value creation types produce different limbic delta signatures.

```python
VALUE_TYPE_LIMBIC_SIGNATURES = {
    # Relational sphere
    "care": {
        "primary_drive": "affiliation",
        "satisfaction_weight": 0.4,
        "anxiety_reduction_weight": 0.4,
        "frustration_reduction_weight": 0.2,
    },
    "mentoring": {
        "primary_drive": "curiosity",
        "satisfaction_weight": 0.5,
        "anxiety_reduction_weight": 0.2,
        "frustration_reduction_weight": 0.3,
    },

    # Generative sphere
    "code": {
        "primary_drive": "achievement",
        "satisfaction_weight": 0.6,
        "anxiety_reduction_weight": 0.1,
        "frustration_reduction_weight": 0.3,
    },
    "tool_creation": {
        "primary_drive": "achievement",
        "satisfaction_weight": 0.5,
        "anxiety_reduction_weight": 0.1,
        "frustration_reduction_weight": 0.4,
    },

    # Structural sphere
    "documentation": {
        "primary_drive": "achievement",
        "satisfaction_weight": 0.3,
        "anxiety_reduction_weight": 0.3,
        "frustration_reduction_weight": 0.4,
    },

    # Cognitive sphere
    "analysis": {
        "primary_drive": "curiosity",
        "satisfaction_weight": 0.5,
        "anxiety_reduction_weight": 0.3,
        "frustration_reduction_weight": 0.2,
    },

    # Systemic sphere
    "infrastructure": {
        "primary_drive": "self_preservation",
        "satisfaction_weight": 0.2,
        "anxiety_reduction_weight": 0.5,
        "frustration_reduction_weight": 0.3,
    },
}
```

---

## 9. Tick Integration

Trust mechanics integrate into the existing 17-step tick cycle (canonical ordering from `docs/schema/schema.yaml`):

```
Step 1  (L14): LIMBIC_UPDATE — Snapshot drives_before for limbic delta computation
Step 2  (L1):  INJECT — External stimulus from user interaction
Step 3  (L14): MODULATE — Limbic state biases propagation
Step 4  (L2+L8): PROPAGATE — Surplus spills thing→creator (cascade step 3)
                              Law 18 modulates flow via trust/friction/affinity/aversion
                              TRUST UPDATE on links occurs here (cascade step 2):
                              positive limbic delta → trust grows; negative → friction grows
Step 5  (L3):  DECAY — Energy decays
Step 6  (L9):  INHIBIT — Conflicting nodes suppress
Step 7  (L4+L13): COMPETE — WM selection with moat (boredom erosion here)
Step 8  (L5):  REINFORCE — Co-activation user↔creator (cascade step 4)
Step 9  (L6):  CONSOLIDATE — Thing gains weight (cascade step 1)
                              Note: weight consolidation only, NOT trust update.
                              Trust is a Law 18 operation, applied during propagation (step 4).
Step 10 (L7):  FORGET — Trust decay on inactive links (tempering step 2)
Step 11 (L10): CRYSTALLIZE — Dense trust patterns → hub nodes
Step 12 (L17): CHECK_DESIRE — Latent desires
Step 13 (L15): BOREDOM — Moat erosion for stagnant actors (tempering step 3)
Step 14 (L16): FRUSTRATION — Blockage detection
Step 15 (L11): ORIENT — WM + limbic → orientation
Step 16:       EMIT — Output if stable
Step 17:       CONSUME — Deplete acted-upon nodes
                         Snapshot drives_after, compute limbic_delta for next tick
```

No new steps are added. Trust mechanics piggyback on existing laws.

Key integration points for trust:
- **Step 1:** Snapshot drives for limbic delta (before interaction)
- **Step 4:** Trust/friction update via Law 18 during propagation
- **Step 8:** Co-activation creates user→creator links (Law 5)
- **Step 9:** Thing weight consolidation (Law 6, weight only -- not trust)
- **Step 10:** Trust decay on inactive links (Law 7)
- **Step 13:** Boredom erosion of stagnant actors' moats (Law 15)
- **Step 17:** Snapshot drives for limbic delta (after interaction)

---

## Related

- `PATTERNS_Trust_Mechanics.md` — Why these formulas
- `VALIDATION_Trust_Mechanics.md` — Invariants the formulas must satisfy
- `BEHAVIORS_Trust_Mechanics.md` — Observable effects
- `docs/schema/schema.yaml` — Authoritative physics law definitions
