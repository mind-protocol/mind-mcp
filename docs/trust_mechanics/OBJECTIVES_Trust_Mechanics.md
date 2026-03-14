# OBJECTIVES: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: What the trust system optimizes for
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: schema.yaml (Law 2, 5, 6, 7, 15, 18), PATTERNS_Economy.md
```

---

## O1: Accurate Attribution (Primary)

**What:** When a user derives value from something in the ecosystem, the trust signal must flow to every entity that contributed to that value — and only to those entities.

**Why:** Without accurate attribution, the system rewards the wrong actors. Popular intermediaries capture trust meant for original creators. Marketing becomes more profitable than building. The system devolves into an attention economy.

**Measure:** Attribution precision — what fraction of trust signals land on the actual creator(s) vs intermediaries, proxies, or unrelated actors.

**Constraint:** Zero-LLM. Attribution is topological (graph structure), not inferred by a model. The graph's link structure IS the attribution chain.

---

## O2: Anti-Gaming (Critical)

**What:** No actor should be able to artificially inflate their trust score through manipulation, collusion, or gaming mechanics.

**Why:** Trust is the foundational currency of the ecosystem. It determines transaction friction (Pattern 5 in Economy), membrane fees (Pattern 6), compute allocation, and governance weight. A gameable trust system is worse than no trust system — it rewards the most manipulative actors.

**Measure:** Three structural safeguards must hold simultaneously:
1. **Asymptotic saturation** — trust gains decelerate as trust grows (Law 6: `1-W` damping)
2. **Temporal decay** — unused trust erodes (Law 7: forgetting on inactive links)
3. **Boredom erosion** — stagnant high-trust actors lose their defensive moat (Law 15: coefficient -3.0)

**Constraint:** No single event can create high trust. Trust is accumulated, never granted.

---

## O3: Organic Trust Growth (Primary)

**What:** Trust must emerge from actual usage patterns — the limbic delta (satisfaction change) when a user interacts with something. Not from votes, ratings, endorsements, or declarations.

**Why:** Declared trust (ratings, reviews) is cheap to fake and expensive to validate. Observed trust (did frustration drop? did satisfaction rise? did the user return?) is expensive to fake and cheap to observe — the graph already tracks it.

**Measure:** Trust delta on any link should correlate with measurable limbic improvement in the user. Specifically: `ΔTrust` should be proportional to positive limbic delta (frustration decrease + satisfaction increase).

**Constraint:** Trust only flows through links that carry actual energy (Law 2). No trust from dormant connections.

---

## O4: Creator Reward Cascade (Primary)

**What:** When trust flows to a thing (tool, content, service), it must propagate backward through the creation chain to reach the creator(s). This is not a separate mechanism — it is Law 2 (surplus spill-over) and Law 5 (co-activation reinforcement) operating on the existing graph topology.

**Why:** Creators are the primary value producers. If trust stops at the artifact, creators have no incentive to keep building. The cascade must be structural — built into graph physics, not a secondary reward system.

**Measure:** For every trust-positive interaction with a thing, the thing's creator(s) should receive measurable trust propagation within the same tick cycle. The propagation amount should be proportional to the creator's contribution weight on the creation link.

---

## O5: Destruction Detection (Secondary)

**What:** Value destruction patterns (extraction, manipulation, Sybil, free-riding) should be detectable through topological signals, not behavioral heuristics.

**Why:** Heuristic detection is an arms race. Topological signals are structural — they emerge from graph physics and are harder to circumvent because the attacker would need to alter graph structure, not just behavior.

**Measure:** Each destruction pathology should have at least two independent topological signals. Detection should not require human review for common patterns.

---

## Tradeoff Resolution

| Tension | Resolution |
|---------|------------|
| Accuracy vs Speed | Accuracy wins. Trust updates happen at tick speed (5s-60s), not real-time. Batch settlement means slight delay is acceptable. |
| Anti-gaming vs Accessibility | Anti-gaming wins. New actors start at trust 0.0 and earn their way up. High friction for strangers (5-10%) is the price of integrity. |
| Creator reward vs User privacy | Creator reward is limited to trust propagation through graph topology. No user behavior data is exposed to creators — they see accumulated trust on their inbound links, not individual user actions. |
| Organic growth vs Bootstrapping | Organic wins long-term. Bootstrap is handled by UBC and initial bond staking, not by granting artificial trust. |

---

## Non-Objectives

- **Reputation portability** — Trust is local to the ecosystem. By design (Switch-Lock, Pattern 2). Not a bug.
- **Trust transfer** — Trust on links is not transferable between actors. You earn your own.
- **Algorithmic fairness** — The system optimizes for accuracy, not equal distribution. Actors who create more value accumulate more trust. This is intended.
- **Human-readable trust scores** — Trust Score is a topological aggregation. It is a float, not a label. No "trusted"/"untrusted" categories.

---

## Related

- `PATTERNS_Trust_Mechanics.md` — Design philosophy
- `ALGORITHM_Trust_Mechanics.md` — Formulas and cascades
- `VALIDATION_Trust_Mechanics.md` — Invariants
- `docs/schema/schema.yaml` — Schema v2.0 (Law 18, link dimensions)
- `docs/economy/PATTERNS_Economy.md` — Economy patterns (trust in pricing)
