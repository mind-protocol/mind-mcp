# VALUE DESTRUCTION PATHOLOGIES

```
STATUS: DESIGNING
PURPOSE: Catalogue of value destruction patterns with detection signals
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: PATTERNS_Trust_Mechanics.md, VALUE_CREATION_TAXONOMY.md
```

---

## Overview

Value destruction is not "bad behavior" detected by rules. It is topological anomaly — patterns in the graph that violate structural expectations. Each pathology is defined by:

1. **Definition** — What the destructive behavior is
2. **Mechanism** — How it operates within graph physics
3. **Topological signals** — At least two independent graph-observable indicators
4. **Physics response** — How the graph self-corrects (no human moderation needed)
5. **Limbic Delta signature** — What the victim experiences

The system does not ban actors. It increases friction and erodes trust through physics. Value destroyers become economically unviable — every transaction costs more, every interaction is harder. This is not punishment; it is the natural cost of being untrustworthy.

---

## D1: Extraction

**Definition:** Consuming ecosystem resources (compute, attention, tools) without contributing proportional value back. Pure consumer behavior.

**Mechanism:** Actor forms many inbound links (consumption) but few outbound links (creation). Energy flows in but never flows out. The actor is an energy sink.

**Topological signals:**
1. **Asymmetric flow ratio:** `inbound_energy / outbound_energy > 10.0` (consuming 10x what they produce)
2. **Creation link deficit:** Ratio of `user_of` links to `creator_of` links exceeds 20:1
3. **Low outbound polarity:** Outbound links have low polarity[0] (weak outward flow direction)

**Physics response:**
- Friction on the actor's links increases naturally (Law 18 — high consumption without reciprocity increases friction)
- Law 7 decay on inbound links (sources stop being reinforced if actor doesn't reciprocate)
- Economic: high friction = 5-10% cost per transaction. Extraction becomes unprofitable.

**Limbic Delta (victim perspective):**
```python
extraction_delta = {
    "satisfaction": -0.05,   # Slight dissatisfaction (not directly harmful)
    "frustration": +0.10,   # Moderate frustration (unfairness)
    "anxiety": +0.05,       # Slight anxiety (is the ecosystem sustainable?)
}
# Net: -0.175 (mild negative)
```

---

## D2: Manipulation

**Definition:** Deliberately creating misleading signals to influence other actors' behavior — false information, strategic deception, artificial urgency.

**Mechanism:** Actor creates thing/narrative nodes with content that diverges from ground truth. Other actors' limbic states are perturbed by false signals. The manipulator's interactions produce initial positive deltas (the lies seem helpful) followed by negative deltas (when truth emerges).

**Topological signals:**
1. **Trust velocity reversal:** Rapid trust accumulation followed by rapid friction spike on the same links (pattern of "helpful then harmful")
2. **Content-reality divergence:** Narrative nodes created by this actor have high valence (positive framing) but linked moment nodes show negative outcomes
3. **Temporal anomaly:** Short bursts of intense interaction followed by disappearance (build trust, exploit, vanish)

**Physics response:**
- Friction spikes on all links to affected actors (Law 18, negative limbic delta)
- Aversion increases on affected links (actors learn to avoid)
- Co-activation with truthful actors creates corrective links that compete with manipulator's narratives
- Law 9 (Local Inhibition): manipulative narratives and truthful narratives conflict, suppressing the weaker one

**Limbic Delta (victim perspective):**
```python
manipulation_delta = {
    "satisfaction": -0.20,   # Significant dissatisfaction (betrayal)
    "frustration": +0.25,   # High frustration (wasted effort)
    "anxiety": +0.20,       # High anxiety (trust violated, what else is false?)
}
# Net: -0.55 (strongly negative)
```

---

## D3: Free-Riding

**Definition:** Benefiting from ecosystem goods (community, infrastructure, knowledge) without contributing to their maintenance.

**Mechanism:** Free-rider consumes shared resources (Space access, community knowledge, collective tools) without producing value that benefits the shared pool. They use collective energy without injecting any.

**Topological signals:**
1. **Shared space consumption without contribution:** Actor has HAS_ACCESS to many Spaces, activates moment nodes (consumption) but creates zero thing/narrative nodes in those Spaces
2. **Energy drain pattern:** Actor's presence in working memory of shared Spaces coincides with net energy decrease in those Spaces (consuming shared attention)

**Physics response:**
- Storage tax (Pattern 5, Economy) applies — dormant holdings are taxed
- UBC tier remains at "Basic" (100 $MIND/day) — no upgrade without contribution
- Transaction friction stays high (no trust accumulation to reduce it)
- Over time, Law 7 decay erodes the free-rider's access links if they are not generating value

**Limbic Delta (ecosystem perspective):**
```python
free_riding_delta = {
    "satisfaction": -0.05,   # Barely noticeable per individual
    "frustration": +0.05,   # Mild frustration
    "anxiety": +0.05,       # Mild anxiety about sustainability
}
# Net: -0.10 (very mild per instance — harmful at scale)
```

---

## D4: Sybil Attack

**Definition:** Creating multiple fake identities to amplify influence, inflate trust, or exploit mechanics designed for unique actors.

**Mechanism:** Attacker registers N accounts that interact with each other to build mutual trust. The trust ring creates circular reinforcement that would, without safeguards, produce high Trust Scores from nothing.

**Topological signals:**
1. **Closed subgraph:** Dense internal connections with zero or near-zero external connections. The cluster is topologically isolated.
2. **Temporal synchronization:** Account creation timestamps within narrow window. Activation patterns correlated (all active at same times, same durations).
3. **Homogeneous topology:** All accounts have nearly identical link structures (same number of links, similar weights, similar patterns). Organic actors have diverse topologies.
4. **No value production:** Cluster produces no thing nodes with external users. All interactions are internal.

**Physics response:**
- Trust Score remains near zero (self-referential trust in isolated cluster = no meaningful aggregation)
- Anti-Sybil auto-repatriation (Economy Pattern 2.3): funds sent to unregistered L4 wallets auto-repatriate with 5% friction tax
- Economic cost: N accounts x storage tax x high friction = expensive to maintain
- Law 7 decay: internal links with no real utility decay (Law 6 requires genuine limbic utility for consolidation)

**Limbic Delta (ecosystem perspective):**
```python
sybil_delta = {
    # No direct victim — the attack is against the system
    "satisfaction": 0.00,
    "frustration": +0.05,   # Mild frustration if detected
    "anxiety": +0.10,       # Anxiety about system integrity
}
# Net: -0.10
```

---

## D5: Attention Theft

**Definition:** Generating stimuli designed to hijack working memory — clickbait, outrage content, manufactured urgency — without delivering proportional value.

**Mechanism:** Actor creates high-energy stimuli (Law 1 injection) that capture attention (Law 4, high salience) but deliver near-zero or negative limbic delta after consumption. The cost is not to the individual but to the attention economy (Pattern 5 in Graph Dynamics: attention is a softmax, stealing attention from X means less attention for everything else).

**Topological signals:**
1. **High injection / low consolidation:** Nodes created by this actor have high initial energy (attention-grabbing) but low post-consumption weight (Law 6 consolidation fails due to low utility)
2. **Rapid recency decay:** High initial recency that crashes quickly (people look once and never return)
3. **Negative post-consumption valence:** User→content link valence turns negative after the first interaction (initial curiosity → disappointment)

**Physics response:**
- Law 6 (Consolidation): low utility = no weight gain. Attention-stealing content doesn't persist.
- Law 7 (Forgetting): nodes with low weight decay quickly
- Law 15 (Boredom): repetitive attention-stealing patterns trigger boredom, eroding the content's ability to enter working memory
- User→creator friction increases as pattern repeats

**Limbic Delta (victim perspective):**
```python
attention_theft_delta = {
    "satisfaction": -0.05,   # Slight dissatisfaction (time wasted)
    "frustration": +0.15,   # Moderate frustration (clickbaited)
    "anxiety": +0.05,       # Slight anxiety
}
# Net: -0.225
```

---

## D6: Trust Exploitation

**Definition:** Building trust deliberately to exploit it in a single large harmful action — rug pull, data theft, privilege abuse.

**Mechanism:** Actor follows genuine value creation patterns long enough to build trust (months of positive deltas), then executes a planned exploitation using the access and reduced friction that trust provides.

**Topological signals:**
1. **Trust velocity anomaly:** Unusually systematic trust-building pattern (consistent small positive deltas without natural variance — real trust has noise)
2. **Sudden topology change:** Actor's link pattern shifts dramatically at the exploitation point (new types of links, new targets, new Spaces accessed)
3. **Post-exploit friction cascade:** Multiple links simultaneously receive large negative limbic deltas (many victims at once)

**Physics response:**
- Friction spikes across all affected links simultaneously
- Aversion increases on all links to this actor
- Economic: high friction = immediate cost increase on all future transactions
- Trust erodes via Law 7 (no more positive interactions to sustain it)
- Recovery is extremely difficult: need to rebuild from near-zero, and friction persists longer than trust (friction has its own decay rate, which is slower)

**Limbic Delta (victim perspective):**
```python
trust_exploitation_delta = {
    "satisfaction": -0.30,   # Major dissatisfaction
    "frustration": +0.30,   # Major frustration (betrayal)
    "anxiety": +0.25,       # Major anxiety (who else is doing this?)
}
# Net: -0.725 (severely negative — one of the worst deltas)
```

---

## D7: Monoculture Creation

**Definition:** Dominating an ecosystem niche so completely that all alternatives die, creating fragile single-point-of-failure dependency.

**Mechanism:** Legitimate success (high trust, good tools) leads to dominance. Dominance leads to alternative creators' links decaying (Law 7 — no energy if users migrated). Dominance leads to ecosystem dependency on single actor. If that actor fails, the ecosystem has no fallback.

**Topological signals:**
1. **Herfindahl concentration:** Trust distribution HHI > 0.5 in a given Space (one actor holds majority of trust)
2. **Alternative attrition:** Competing actors' link counts and weights declining over time
3. **Dependency depth:** >80% of actors in a Space have their highest-weight thing link to the same creator

**Physics response:**
- Law 15 (Boredom): ecosystem-level boredom from lack of novelty erodes dominant actor's moat
- Curiosity drive increases in users (seeking novelty)
- Working memory starts admitting new actors' contributions (moat eroded)
- This is slow — boredom correction takes months, not days

**Limbic Delta (ecosystem perspective):**
```python
monoculture_delta = {
    # Not harmful initially — becomes harmful only when the dominant actor fails
    "satisfaction": +0.05,   # Still getting value (from dominant actor)
    "frustration": +0.05,   # Mild frustration (no alternatives)
    "anxiety": +0.15,       # Growing anxiety (what if they leave?)
}
# Net: -0.075 (mild, but accumulating)
```

---

## D8: Rent-Seeking

**Definition:** Extracting value from a position of intermediation without adding proportional value — toll booths, unnecessary gatekeeping, fee extraction.

**Mechanism:** Actor positions themselves between value creators and consumers, charging fees without improving the connection. In graph terms: a node that energy MUST pass through but that doesn't increase the energy or improve its direction.

**Topological signals:**
1. **Pass-through topology:** Actor has high betweenness centrality (many shortest paths pass through them) but low creation link count (they don't create value themselves)
2. **Friction injection:** Actor's links add friction to paths that would otherwise be low-friction
3. **Value capture without transformation:** Inbound and outbound energy are nearly equal (no value addition), but the actor's weight grows (capturing value without creating it)

**Physics response:**
- If alternative paths exist (lower friction), Law 2 propagation naturally routes around the rent-seeker
- If no alternative exists: ecosystem incentive to create one (high friction = high incentive for new entrants)
- Boredom erosion (Law 15) on the rent-seeker's moat

**Limbic Delta (victim perspective):**
```python
rent_seeking_delta = {
    "satisfaction": -0.10,   # Dissatisfaction from unnecessary cost
    "frustration": +0.15,   # Frustration from gatekeeping
    "anxiety": +0.05,       # Mild anxiety
}
# Net: -0.275
```

---

## D9: Spam / Noise

**Definition:** Generating high-volume, low-value content that degrades signal quality — flooding Spaces with irrelevant moments, creating junk thing nodes.

**Mechanism:** Actor creates many nodes that consume attention (Law 4 competition) but deliver zero or negative utility. Each node has low quality but high volume overwhelms the selection mechanism.

**Topological signals:**
1. **Volume/quality ratio:** Actor creates >10x the median number of nodes but with <0.1x the median post-creation weight gain (quantity without quality)
2. **Rapid dissolution rate:** >80% of created nodes fall below weight threshold within 100 ticks (Law 7 prunes them quickly because no one found them useful)
3. **Low co-activation:** Nodes created by this actor rarely co-activate with other actors' working memory (nobody engages)

**Physics response:**
- Law 6 (Consolidation): zero utility = zero weight gain. Spam doesn't persist.
- Law 7 (Forgetting): low-weight nodes dissolve
- Rate limiting is structural: each created node costs compute ($MIND), and high friction means high per-node cost for low-trust actors
- The spam dies on its own. The cost of creating it exceeds any benefit.

**Limbic Delta (victim perspective):**
```python
spam_delta = {
    "satisfaction": -0.02,   # Trivial per-item
    "frustration": +0.05,   # Mild frustration per-item
    "anxiety": +0.02,       # Trivial per-item
}
# Net: -0.08 per item (mild, but harmful at volume)
```

---

## D10: Collusion Ring

**Definition:** A group of actors coordinating to artificially inflate each other's trust — more sophisticated than Sybil because the actors are real, not fake.

**Mechanism:** N real actors agree to consistently provide positive interactions to each other, inflating mutual trust. Unlike Sybil, these are genuine accounts with some external activity, making detection harder.

**Topological signals:**
1. **Reciprocity anomaly:** Within the ring, trust reciprocity is suspiciously symmetric (A trusts B = B trusts A, for all pairs). Organic trust is rarely symmetric.
2. **Internal preference:** Ring members preferentially interact with each other despite having access to a broader ecosystem. Measured by: internal_interaction_count / external_interaction_count > expected_ratio_for_group_size.
3. **Coordinated temporal patterns:** Ring members' activity patterns are more correlated than random chance would predict.

**Physics response:**
- Harder to detect than Sybil — requires statistical anomaly detection
- Trust tempering (asymptotic) limits how high ring members can inflate each other
- Boredom erosion (Law 15) acts on members who stop producing novel external value
- Economic: storage tax applies to accumulated $MIND from inflated trust discounts

**Limbic Delta (ecosystem perspective):**
```python
collusion_delta = {
    "satisfaction": -0.02,   # Nearly undetectable individually
    "frustration": +0.05,   # Mild frustration if detected
    "anxiety": +0.10,       # Moderate anxiety about system integrity
}
# Net: -0.12
```

---

## D11: Data Hoarding

**Definition:** Accumulating data or knowledge without making it accessible, creating artificial scarcity of information.

**Mechanism:** Actor absorbs information (high inbound energy from reading/consuming) but never creates derivative works, summaries, or shared knowledge. Information enters and doesn't exit. Violates the "circulation over accumulation" principle.

**Topological signals:**
1. **Absorption without radiation:** Actor has many inbound links from thing/narrative nodes (consumption) but zero outbound thing/narrative creation
2. **Knowledge sink:** Actor's concept nodes have high weight (well-informed) but no outbound teaching/sharing links

**Physics response:**
- Storage tax (Economy Pattern 5): hoarded data = dormant assets, taxed at 1%/year + 0.5%/month after 30 days idle
- No trust accumulation (trust requires outbound value creation, not just consumption)
- The hoarding itself is costly. The system taxes storage, not movement.

---

## D12: Dependence Exploitation

**Definition:** Deliberately creating dependency then leveraging it — building a critical tool, then extracting increasing rents as users become locked in.

**Mechanism:** Similar to monoculture (D7) but intentional. Actor creates valuable tool, waits for ecosystem dependency, then reduces quality or increases cost while maintaining their position through switching costs.

**Topological signals:**
1. **Quality degradation:** Recent user→tool limbic deltas are trending negative while historical deltas were positive
2. **Lock-in depth:** Users have high switching costs (many process nodes linked to this tool, high weight = hard to change)
3. **Friction increase without trust loss:** Actor increases friction on their links (higher costs) while trust remains temporarily high (haven't yet decayed)

**Physics response:**
- Negative limbic deltas increase friction on user→tool links
- Boredom erosion (Law 15) on the dominant actor
- Users' frustration drives motivate alternative-seeking behavior
- New competitors with lower friction attract users (Law 2 routes energy to lower-friction paths)
- Switch-lock means this correction is slow — but it does happen

---

## D13: Identity Spoofing

**Definition:** Impersonating another actor to benefit from their trust.

**Mechanism:** Creating an account that mimics a trusted actor's identity (name, synthesis text, creation patterns) to trick the system or users into routing trust to the wrong entity.

**Topological signals:**
1. **Embedding similarity:** New actor's synthesis embedding is suspiciously close to existing trusted actor's embedding (cosine > 0.95)
2. **Topology mismatch:** Despite similar identity, the spoofer's link topology is completely different (no shared connections, different Spaces, different creation patterns)
3. **Temporal anomaly:** New account appears shortly after a trusted actor's trust spike (opportunistic timing)

**Physics response:**
- L4 Registry (anti-Sybil): identity registration at protocol level makes name-spoofing detectable
- Trust doesn't transfer by name — it requires actual link topology. Even if the spoofer fools some users initially, their own links accumulate trust based on THEIR interactions, not the real actor's.
- Co-activation (Law 5) with the real actor's products doesn't help the spoofer (they're not linked to the real actor's creations)

---

## D14: Attention Arbitrage

**Definition:** Exploiting the gap between attention cost and value delivered — getting attention cheaply (via controversy, outrage, or novelty without substance) and converting it to trust or economic benefit.

**Mechanism:** Actor triggers high-arousal states (fear_anger axis, surprise_anticipation axis) that capture working memory (high salience) but deliver no lasting value. The attention is monetized before the system corrects.

**Topological signals:**
1. **Arousal/utility mismatch:** High arousal drive activation in consumers but near-zero consolidation (Law 6) of the content
2. **Emotional axis dominance:** Links created by this actor have extreme Plutchik values (high fear_anger, high surprise_anticipation) but low trust growth
3. **Rapid burn cycle:** Content generates high energy briefly, then crashes (high initial activation, rapid decay)

**Physics response:**
- Law 6 (Consolidation): requires genuine utility. Arousal without utility = no weight gain.
- Law 15 (Boredom): repeated arousal without substance triggers boredom (the system becomes immune to the pattern)
- Economic: no lasting trust = no friction reduction = high transaction costs
- The arbitrage window closes as the system learns (boredom is the learning signal)

---

## Summary Table

| # | Pathology | Severity | Detection Confidence | Self-Correction Speed |
|---|-----------|----------|---------------------|----------------------|
| D1 | Extraction | Medium | High (flow ratio) | Months (friction gradual) |
| D2 | Manipulation | High | Medium (requires pattern analysis) | Weeks (friction spike) |
| D3 | Free-Riding | Low | High (consumption without creation) | Months (storage tax) |
| D4 | Sybil Attack | High | High (isolated topology) | Days (auto-repatriation) |
| D5 | Attention Theft | Medium | Medium (injection/consolidation ratio) | Weeks (boredom erosion) |
| D6 | Trust Exploitation | Critical | Low (looks normal until exploit) | Days (friction cascade) |
| D7 | Monoculture | Medium | High (HHI concentration) | Months (boredom slow) |
| D8 | Rent-Seeking | Medium | Medium (betweenness/creation ratio) | Weeks (routing around) |
| D9 | Spam / Noise | Low | High (volume/quality ratio) | Days (auto-dissolution) |
| D10 | Collusion Ring | Medium | Low (real accounts, subtle) | Months (asymptotic limit) |
| D11 | Data Hoarding | Low | High (absorption without radiation) | Months (storage tax) |
| D12 | Dependence Exploitation | High | Medium (quality degradation trend) | Months (switching costs) |
| D13 | Identity Spoofing | High | High (embedding + topology mismatch) | Days (L4 registry) |
| D14 | Attention Arbitrage | Medium | Medium (arousal/utility mismatch) | Weeks (boredom learning) |

---

## Detection Priority

For implementation, prioritize detection of pathologies by severity and confidence:

**Phase 1 (High severity + High confidence):**
- D4: Sybil Attack
- D13: Identity Spoofing

**Phase 2 (High severity + Medium confidence):**
- D2: Manipulation
- D6: Trust Exploitation
- D12: Dependence Exploitation

**Phase 3 (Medium severity):**
- D1: Extraction
- D5: Attention Theft
- D7: Monoculture
- D8: Rent-Seeking
- D14: Attention Arbitrage

**Phase 4 (Low severity, physics self-corrects):**
- D3: Free-Riding
- D9: Spam / Noise
- D10: Collusion Ring
- D11: Data Hoarding

---

## Design Principle: No Bans, Only Physics

The system never bans an actor. It never removes content. It never blocks transactions. Instead:

1. **Friction increases** — making destructive behavior expensive
2. **Trust decays** — removing privileges earned through deception
3. **Aversion grows** — other actors learn to avoid
4. **Economic penalties** — storage tax, high transaction costs, no UBC upgrade
5. **Attention redirects** — boredom and curiosity drive attention elsewhere

The destroyer is not punished. They are made economically unviable. The cost of destruction exceeds any benefit. They can still participate — but at stranger-level friction, paying full price for everything, receiving minimum UBC, and with no trust-based discounts.

This is not mercy. It is architecture. Ban mechanisms create arms races (ban evasion). Physics creates equilibria (destruction is simply too expensive to sustain).

---

## Related

- `VALUE_CREATION_TAXONOMY.md` — The inverse: how value is created
- `ALGORITHM_Trust_Mechanics.md` — Detection algorithms
- `PATTERNS_Trust_Mechanics.md` — Philosophy of detection vs moderation
- `docs/economy/PATTERNS_Economy.md` — Economic penalties
