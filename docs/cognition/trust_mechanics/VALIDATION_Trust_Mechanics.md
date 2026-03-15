# VALIDATION: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: Invariants that must hold — what must be true
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: ALGORITHM_Trust_Mechanics.md
```

---

## V1: Trust Bounded [0, 1]

**Invariant:** `∀ link: 0.0 ≤ link.trust ≤ 1.0`

**Why:** Trust is a normalized confidence measure. Values outside [0, 1] have no semantic meaning and would break downstream formulas (friction calculation, pricing discount).

**Verification:**
```python
def verify_trust_bounds():
    for link in all_links():
        assert 0.0 <= link.trust <= 1.0, f"link {link.id}: trust={link.trust} out of bounds"
```

**When could break:** Floating point accumulation without clamping. Fix: `min(1.0, ...)` in all trust update formulas.

---

## V2: Trust Never Stored on Nodes

**Invariant:** No node in the graph has a `trust_score` property. Trust Score is always computed from link topology.

**Why:** A stored Trust Score would become stale, could be manipulated independently of links, and would violate the "trust is relational" principle.

**Verification:**
```python
def verify_no_stored_trust_score():
    for node in all_nodes():
        assert not hasattr(node, 'trust_score'), f"node {node.id} has stored trust_score"
        # Also check the database directly
        assert 'trust_score' not in node.properties, f"node {node.id} has trust_score property in DB"
```

**When could break:** Performance optimization that caches Trust Score as a node property. Fix: Use TTL-cached computation, never persist.

---

## V3: Asymptotic Convergence

**Invariant:** `ΔTrust` monotonically decreases as `trust` increases, for constant limbic_delta.

```
∀ limbic_delta > 0:
  ΔTrust(trust=a, LD) > ΔTrust(trust=b, LD)  when a < b
```

**Why:** This is the anti-gaming core. Without asymptotic convergence, linear trust growth would allow rapid trust farming.

**Verification:**
```python
def verify_asymptotic():
    for ld in [0.05, 0.1, 0.2, 0.5]:
        prev_delta = float('inf')
        for trust in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            delta = 0.05 * ld * (1.0 - trust)
            assert delta < prev_delta, f"Non-monotonic at trust={trust}, LD={ld}"
            prev_delta = delta
```

---

## V4: Energy Conservation During Propagation

**Invariant:** When energy propagates from thing→creator (Law 2), the source depletes exactly the amount transferred.

```
∀ propagation event:
  Σ(energy_transferred_to_neighbors) = energy_depleted_from_source
```

**Why:** Energy conservation prevents trust inflation. If propagation creates energy, the system inflates unboundedly.

**Verification:**
```python
def verify_energy_conservation(node, pre_energy, post_energy, transfers):
    total_transferred = sum(transfers.values())
    depleted = pre_energy - post_energy
    assert abs(total_transferred - depleted) < 1e-6, "Energy conservation violated"
```

---

## V5: No Self-Loop Trust

**Invariant:** No actor has a link to itself. Trust cannot be self-referential.

```
∀ link: link.node_a ≠ link.node_b  (when both are the same actor)
```

**Why:** Self-loops would allow an actor to inflate their own Trust Score.

**Verification:**
```python
def verify_no_self_loops():
    for link in all_links():
        if get_node(link.node_a).node_type == 'actor' and get_node(link.node_b).node_type == 'actor':
            assert link.node_a != link.node_b, f"Self-loop on actor {link.node_a}"
```

---

## V6: Friction Bounded [0, 1]

**Invariant:** `∀ link: 0.0 ≤ link.friction ≤ 1.0`

**Why:** Friction is a damping coefficient. Values > 1 would invert the formula (negative friction = earning). Values < 0 are undefined.

Note: Transaction friction (the economic formula) CAN go negative (Pattern 5 in Economy). But `link.friction` (the graph property) is bounded [0, 1]. The economic formula combines link.friction with trust_score to produce a value that can be negative.

**Verification:**
```python
def verify_friction_bounds():
    for link in all_links():
        assert 0.0 <= link.friction <= 1.0, f"link {link.id}: friction={link.friction} out of bounds"
```

---

## V7: Affinity-Aversion Anti-Correlation

**Invariant:** `affinity + aversion ≤ 1.5` — a link cannot be maximally attractive and maximally repulsive simultaneously.

**Why:** While ambivalence exists (documented as `ambivalence` field on links), extreme simultaneous affinity and aversion is physically nonsensical. The soft cap at 1.5 (not 1.0) allows for moderate ambivalence.

**Verification:**
```python
def verify_affinity_aversion():
    for link in all_links():
        assert link.affinity + link.aversion <= 1.5 + 1e-6, \
            f"link {link.id}: affinity({link.affinity}) + aversion({link.aversion}) > 1.5"
```

---

## V8: Temporal Decay Monotonicity

**Invariant:** A link that receives no activation strictly decreases in weight over time (given stability < 1.0).

```
∀ link where activation_count unchanged between tick T and T+N:
  link.weight(T+N) < link.weight(T)  when link.stability < 1.0
```

**Why:** Without this, abandoned relationships persist indefinitely, inflating Trust Scores.

**Verification:**
```python
def verify_temporal_decay(link, snapshots):
    """
    snapshots = [(tick, weight, activation_count), ...]
    """
    for i in range(1, len(snapshots)):
        prev_tick, prev_weight, prev_ac = snapshots[i-1]
        curr_tick, curr_weight, curr_ac = snapshots[i]
        if curr_ac == prev_ac and link.stability < 1.0:
            assert curr_weight < prev_weight, \
                f"link {link.id}: weight not decaying between ticks {prev_tick} and {curr_tick}"
```

---

## V9: Limbic Delta Bounds

**Invariant:** `limbic_delta ∈ [-2.0, +2.0]`

**Why:** Derived from the bounded ranges of individual drives (each [0, 1]). The formula `satisfaction_Δ - frustration_Δ - 0.5 × anxiety_Δ` has theoretical max of +2.0 and min of -2.0.

**Verification:**
```python
def verify_limbic_delta_bounds(delta):
    assert -2.0 <= delta <= 2.0, f"limbic_delta={delta} out of bounds"
```

---

## V10: Creator Attribution Topology

**Invariant:** Every thing node that has users must have at least one creation link (thing→creator or creator→thing).

**Why:** Without a creation link, the attribution cascade has nowhere to propagate. Trust generated by tool usage stays at the tool and never reaches a creator.

**Verification:**
```python
def verify_creator_attribution():
    for thing in all_nodes_of_type('thing'):
        user_links = [l for l in thing.inbound_links() if get_node(l.node_a).node_type == 'actor']
        if user_links:  # Thing has users
            creator_links = [l for l in thing.all_links()
                           if get_node(l.other_node(thing)).node_type == 'actor'
                           and l.hierarchy < 0]  # Contains/created relationship
            assert len(creator_links) > 0, \
                f"thing {thing.id} has {len(user_links)} users but no creator link"
```

---

## V11: Trust Score Non-Negative

**Invariant:** `∀ actor: trust_score(actor) ≥ 0.0`

**Why:** Trust on links is [0, 1], link weights are [0, infinity). Weighted mean of non-negative values is non-negative.

**Verification:**
```python
def verify_trust_score_non_negative():
    for actor in all_actors():
        score = trust_score(actor)
        assert score >= 0.0, f"actor {actor.id}: trust_score={score} is negative"
```

---

## V12: Negative Interactions Increase Friction, Not Decrease Trust

**Invariant:** A negative limbic_delta on a single interaction never directly decreases link.trust. It only increases link.friction.

**Why:** Trust reduction happens through temporal decay (Law 7), not through punitive mechanics. This prevents revenge attacks and trust volatility.

**Verification:**
```python
def verify_negative_delta_behavior(link, limbic_delta, trust_before, trust_after, friction_before, friction_after):
    if limbic_delta < 0:
        assert trust_after >= trust_before - 1e-6, \
            f"Trust decreased from negative delta: {trust_before} → {trust_after}"
        assert friction_after >= friction_before - 1e-6, \
            f"Friction should increase on negative delta"
```

---

## V13: Sub-Threshold Link Dissolution

**Invariant:** Links with both `weight < 0.01` and `trust < 0.01` are dissolved (removed from graph).

**Why:** Prevents unbounded graph growth from dead links. These links carry no meaningful signal.

**Verification:**
```python
def verify_sub_threshold_dissolution():
    for link in all_links():
        assert not (link.weight < 0.01 and link.trust < 0.01), \
            f"link {link.id} should have been dissolved: weight={link.weight}, trust={link.trust}"
```

**Note:** Structural links (hierarchy=-1, contains relationship) are protected from dissolution regardless of weight/trust.

---

## V14: Sybil Resistance

**Invariant:** A cluster of N actors that only interact with each other cannot achieve aggregate Trust Score > `0.1 × N / total_actors`.

**Why:** Self-referential trust loops must not produce meaningful Trust Score. The aggregate score of an isolated cluster should approach zero as total_actors grows.

**Verification:**
```python
def verify_sybil_resistance():
    clusters = find_isolated_clusters()  # Clusters with zero external links
    for cluster in clusters:
        avg_score = mean(trust_score(actor) for actor in cluster)
        bound = 0.1 * len(cluster) / total_actor_count()
        assert avg_score <= bound + 1e-6, \
            f"Sybil cluster of {len(cluster)} has avg trust {avg_score} > bound {bound}"
```

---

## Validation Schedule

| Invariant | Frequency | Trigger |
|-----------|-----------|---------|
| V1, V6 | Every tick | After trust/friction update |
| V2 | Every 1000 ticks | Schema audit |
| V3 | On formula change | Unit test |
| V4 | Every propagation | In propagation code |
| V5 | On link creation | Guard in create_link() |
| V7 | Every tick | After affinity/aversion update |
| V8 | Every 100 ticks | Decay audit |
| V9 | Every tick | After limbic delta computation |
| V10 | Every 1000 ticks | Topology audit |
| V11 | On demand | When Trust Score computed |
| V12 | Every tick | After negative interaction |
| V13 | Every 100 ticks | During Law 7 forgetting cycle |
| V14 | Daily | Cluster analysis |

---

## Related

- `ALGORITHM_Trust_Mechanics.md` — Formulas these invariants verify
- `BEHAVIORS_Trust_Mechanics.md` — Scenarios where invariants are tested
- `docs/schema/schema.yaml` — Schema-level invariants
