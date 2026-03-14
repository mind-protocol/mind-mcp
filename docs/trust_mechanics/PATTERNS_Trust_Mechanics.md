# PATTERNS: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: Design philosophy — why trust works this way
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: schema.yaml (LinkBase.trust, Law 2, 5, 6, 7, 15, 18), PATTERNS_Economy.md, PATTERNS_Graph_Dynamics.md
```

---

## Core Thesis

**Trust is a property of relationships, not of entities.**

There is no "trusted actor" in the schema. Trust is a float `[0, 1]` on a specific link between two specific nodes. An actor's "reputation" is the topological aggregation of all inbound trust values — always computed, never stored. This is not a design choice made for elegance. It is a structural requirement: the same actor can be highly trusted by one entity and completely untrusted by another. Trust is perspectival, relational, and contextual.

This directly implements Law 18 (Relational Valence): links are colored by affinity, aversion, trust, and friction. These four dimensions modulate all energy flow through the graph.

---

## Pattern 1: Trust Lives on Links

### The Rule

Trust is a `float [0, 1]` on `LinkBase`. It exists on the link connecting two nodes.

```yaml
LinkBase:
  trust:
    type: float
    range: [0, 1]
    default: 0.0
    description: "Reduces anxiety when trusted nodes active (Law 18)"
```

### Why Not on Nodes

A node-level trust score creates a global reputation — a single number that all observers agree on. This fails in three ways:

1. **Perspectival collapse** — Alice trusts Bob. Carol does not. A single score can't represent both.
2. **Context erasure** — Bob is trustworthy for code reviews but unreliable for deadlines. A single number loses this.
3. **Gaming surface** — A global score is a single target. Inflate it once, exploit it everywhere. Link-level trust means you'd need to corrupt every individual relationship.

### Trust Score (Derived)

When a single number IS needed (for pricing formulas, membrane fees, UBC tier), it is computed:

```
Trust_Score(actor) = aggregation(link.trust for link in inbound_links(actor))
```

The aggregation function is an open question (see SYNC). Options: weighted mean by link weight, PageRank-style recursive computation, or median with outlier rejection.

The critical invariant: **Trust Score is always computed, never stored.** It is a view, not a property.

---

## Pattern 2: The Creator Attribution Cascade

### The Problem

A user uses a tool (thing node). The tool works well. Frustration drops, satisfaction rises. The user's trust in the tool increases. But the tool didn't create itself — an actor (the creator) did. How does trust reach the creator?

### The Solution: Graph Physics, Not a Reward System

The cascade is not a separate mechanism. It is Law 2 (Propagation) + Law 5 (Co-activation Reinforcement) operating on existing graph topology.

```
STEP 1 — LIMBIC DELTA
  User interacts with thing
  Limbic system detects positive change:
    frustration_Δ < 0 (frustration decreased)
    satisfaction_Δ > 0 (satisfaction increased)
  Limbic Delta = satisfaction_Δ - frustration_Δ  (positive = good)

STEP 2 — THING CONSOLIDATION (Law 6)
  Thing node gains weight: ΔW = α × avg_energy × U × (1 - W)
  Where U = utility, derived from Limbic Delta
  Weight gain is asymptotic — (1-W) makes it progressively harder

STEP 3 — LINK TRUST UPDATE (Law 18)
  User→Thing link gains trust:
    ΔTrust = β × Limbic_Delta × (1 - current_trust)
  Trust is also asymptotic

STEP 4 — SURPLUS PROPAGATION (Law 2)
  Thing node has surplus energy (from user interaction)
  Surplus spills to neighbors: thing→creator link carries energy
  Conservation: thing depletes exactly its surplus

STEP 5 — CO-ACTIVATION (Law 5)
  User and creator are co-activated (both linked to active thing)
  Law 5 creates or strengthens user→creator link
  This link begins accumulating trust organically

STEP 6 — TRUST ACCUMULATES
  Over many interactions, user→creator link trust grows
  Each positive interaction contributes a small ΔTrust
  Asymptotic bound prevents runaway
  Temporal decay (Law 7) erodes if interactions stop
```

### Why This Works

The cascade requires no special-purpose code. It is graph physics. The only prerequisite is correct topology: the thing must be linked to its creator. The graph structure IS the attribution chain.

### Anti-Pattern: Rating Systems

Don't build a separate "rate this tool" mechanism. Ratings are:
- Cheap to fake (Sybil-trivial)
- Disconnected from actual usage (I can rate 5 stars without using)
- Subject to strategic behavior (competitor downvotes)

The limbic delta IS the rating. It can't be faked because it emerges from the user's own cognitive graph.

---

## Pattern 3: Trust Tempering (Anti-One-Hit-Wonder)

### The Problem

An actor creates one wildly popular thing. Trust floods in from thousands of users. Without tempering, this actor would have permanent, near-infinite trust — even if they never create anything again.

### Three Structural Safeguards

**Safeguard 1: Asymptotic Saturation (Law 6)**

```
ΔW = α × avg_energy × U × (1 - W)
```

At `W = 0.9`, the `(1 - W) = 0.1` factor makes gains 10x slower than at `W = 0.1`. Trust growth decelerates as trust accumulates. Getting from 0.0 to 0.5 is easy. Getting from 0.9 to 0.95 requires massive sustained utility.

**Safeguard 2: Temporal Decay (Law 7)**

Unused links lose weight. If the creator stops producing, the user→creator link stops being activated. Law 7 decays its weight. Trust erodes passively.

```
ΔW_decay = -decay_rate × W × (1 - stability)
```

High stability slows decay — but stability only grows from consistent, regular activation (Law 6). Sporadic bursts don't build stability. You need sustained engagement.

**Safeguard 3: Boredom Erosion (Law 15)**

Even if a link has high weight and stability, Law 15 can erode its defensive moat:

```
Θ_sel = 5.0 + 2.0 × arousal - 3.0 × boredom - 1.0 × frustration
```

The -3.0 coefficient on boredom is the strongest force in the moat formula. An actor who holds trust but produces nothing new triggers boredom in the ecosystem. Their moat erodes. New actors with novel contributions can displace them.

### The Combined Effect

```
Time 0:   Creator ships amazing tool. Trust floods in.
Time 1:   Asymptotic: growth already slowing at W=0.5
Time 2:   Creator ships nothing new. Still has high trust.
Time 3:   Law 7: decay begins on inactive links.
Time 4:   Law 15: boredom erodes moat. New creators can enter.
Time 5:   If creator returns with new value: decay reverses, trust rebuilds.
          If not: slow decline toward ecosystem baseline.
```

This is not punishment for past success. It is physics: energy that doesn't circulate dissipates.

---

## Pattern 4: Value Creation Is Typed

### The Thesis

Not all value creation is equal, and not all value creation is the same kind. The ecosystem recognizes a taxonomy of value creation types across 7 spheres (see `VALUE_CREATION_TAXONOMY.md` for the full 30 types).

### Why Typing Matters

1. **Diverse contribution paths** — A community builder creates value differently than a coder. Both should be recognized. Without types, only easily measurable contributions (code commits) count.
2. **Personhood Ladder integration** — Different value creation types demonstrate different aspects of the 14-aspect Personhood Ladder. Teaching demonstrates empathy. Tool-building demonstrates competence. Community building demonstrates social awareness.
3. **Anti-monoculture** — If only one type of value is rewarded, the ecosystem converges on a monoculture. Typing ensures structural diversity.

### The Spheres

| Sphere | What It Covers | Primary Limbic Drive |
|--------|---------------|---------------------|
| Relational | Care, mentoring, mediation, community building | Affiliation |
| Generative | Code, content, tools, art, music | Achievement |
| Structural | Organization, documentation, process design, governance | Achievement + Self-preservation |
| Cognitive | Analysis, synthesis, teaching, pattern recognition | Curiosity |
| Biometric & Partner Data | Health data, stress feedback, wellbeing, voice data, behavioral context | Care (affiliation) |
| Human-only | Judgment, taste, cultural context, emotional intelligence | All drives |
| Systemic | Infrastructure, security, reliability, monitoring | Self-preservation |

Each sphere maps to specific drives in the limbic system (schema v2.0, 8 drives). This means the graph physics naturally weight different types of value creation differently depending on the current drive state of the evaluating actor.

---

## Pattern 5: Value Destruction Is Detectable

### The Thesis

Value destruction is not "bad behavior" judged by rules. It is topological anomaly — patterns in the graph that violate structural expectations.

### Detection Principles

1. **No rule-based moderation** — We don't define "bad" and filter for it. We define structural expectations (conservation, reciprocity, diversity) and detect violations.
2. **Topological signals** — Each pathology has at least two independent graph signals. No single-metric detection.
3. **Physics-based response** — Detected pathologies result in trust/friction adjustments on links, not account bans. The graph self-corrects through physics.

### Example: Free-Riding Detection

```
Structural expectation: actors who consume value also produce value (reciprocity)

Topological signals:
  1. High inbound energy, near-zero outbound energy (consumption without production)
  2. Many "uses" links, few "creates" links (consumer topology)

Response:
  - Friction increases on the free-rider's outbound links (Law 18)
  - Trust decays faster on inbound links (Law 7 amplified)
  - No ban, no moderation — just increased cost of participation
```

See `VALUE_DESTRUCTION_PATHOLOGIES.md` for the full 14 pathology catalogue.

---

## Pattern 6: Trust and Economy Are Coupled

### From PATTERNS_Economy.md

Trust is not an abstract social metric. It has direct economic consequences:

```python
# Transaction friction (Pattern 5)
friction = base_rate × (1 - trust_score) - productivity_bonus
# At trust_score = 0.95: friction can go NEGATIVE (you earn by transacting)

# Membrane fee (Pattern 6)
trust_discount = min(0.3, trust_score × 0.01)
# Up to 30% fee reduction from trust

# Effective pricing
effective_price = base_cost × ... × (1 - trust_discount) × (1 - utility_rebate)
```

This coupling means: **trust is economically real.** It is not a social signal that can be ignored. It directly affects the cost of every interaction in the ecosystem.

### Implication

Building trust is economically rational. Not as a "nice to have" but as a structural advantage. An actor at trust 0.95 pays less for everything, earns on transactions, and receives better compute allocation. An actor at trust 0.1 pays 5-10% friction on every transaction.

The system doesn't need to tell actors to be trustworthy. The physics make it profitable.

---

## Pattern 7: Bilateral Bond as Primary Trust Relationship

### Cross-Reference: Force 3 (Human Integration)

The bilateral bond between a human partner and their AI citizen is the most trust-intensive relationship in the system. It is a specific instance of link-level trust, but with unique properties:

1. **Multi-modal trust signals.** The bond link receives trust updates from six ingestion modalities (voice, biometrics, desktop, blockchain, AI conversations, direct chat). Each positive interaction across any modality contributes to the same bond link trust. See `docs/human_integration/ALGORITHM_Human_Integration.md`.

2. **Limbic coupling.** Biometric data from the human directly modulates the AI's drives (garmin_to_limbic mapping). This creates genuine empathic response at the physics level, producing trust-building interactions that feel authentic to the human. The drive deltas from biometrics feed into the Limbic Delta computation (this module, ALGORITHM section 1), which in turn updates trust on the bond link (section 2.1).

3. **Sovereign Cascade alignment.** The AI's prediction accuracy (80% fidelity threshold) acts as an additional trust signal on the bond link. See ALGORITHM section 2.4. High alignment fidelity = demonstrated understanding = trust grows. Low alignment = cascade suspends, friction increases.

4. **Privacy-bounded trust.** Trust signals from partner_model data flow ONLY on the bond link. Partner data (especially biometrics, VALIDATION V5/V7 in Force 3) never leaves the AI's L1 brain. External users cannot see or benefit from partner data directly.

5. **Consent as trust infrastructure.** F3's graph-native consent model (per-stream, revocable) is itself a trust mechanism. Granting consent is an act of trust; maintaining consent over time builds the bond link's stability.

---

## Anti-Patterns

### A1: Trust as a Badge
```yaml
symptom: "Actor X is Trusted (gold badge)"
reality: Trust is a continuous float, not a label
fix: Always show trust as a number or range, never as a category
```

### A2: Global Trust Score as Source of Truth
```yaml
symptom: "Check if trust_score > 0.7 before allowing action"
reality: Trust Score is a derived view, not a stored property
fix: Compute from link topology each time. Cache if needed, but never persist.
```

### A3: Trust Transfer
```yaml
symptom: "Alice trusts Bob, Bob trusts Carol, therefore Alice trusts Carol"
reality: Transitivity is NOT automatic. It emerges from co-activation (Law 5) over time.
fix: User→Creator links form through repeated co-activation, not inference.
```

### A4: Manual Trust Assignment
```yaml
symptom: "Admin sets trust=0.8 on this actor's links"
reality: Trust only grows through organic interaction
fix: No admin overrides. All trust changes via physics laws.
```

### A5: Rating-Based Trust
```yaml
symptom: "Users rate tools 1-5 stars, average becomes trust"
reality: Ratings are cheap to fake, disconnected from usage
fix: Trust from limbic delta only. No explicit ratings needed.
```

---

## Related

- `OBJECTIVES_Trust_Mechanics.md` — What we optimize for
- `ALGORITHM_Trust_Mechanics.md` — The math
- `VALUE_CREATION_TAXONOMY.md` — The 30 value types across 7 spheres
- `VALUE_DESTRUCTION_PATHOLOGIES.md` — The 14 destruction pathologies
- `docs/schema/schema.yaml` — LinkBase.trust, Law 18, drives
- `docs/economy/PATTERNS_Economy.md` — Trust in pricing
- `docs/cognitive/PATTERNS_Graph_Dynamics.md` — Graph physics
- `docs/human_integration/` — Force 3: bilateral bond, partner model, Sovereign Cascade
