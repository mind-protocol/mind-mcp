# L3 Link Synthesis Grammar
# Universe Graph — Physics → Language Mapping

```
VERSION: 1.0
DATE: 2026-03-13
SCHEMA: v2.0
LAYER: L3 (Ecosystem / Universe)
```

## RELATIONSHIP TO L1 GRAMMAR

The L1 grammar (`GRAMMAR_Link_Synthesis.md`) maps physics floats to human-readable
synthesis for **brain links** — subjective, emotionally colored, cognitively typed.

This L3 grammar maps the **same physics floats** to human-readable synthesis for
**universe links** — objective, structural, emotionless.

**Key differences:**
- L1 uses `relation_kind` (14 types) — L3 has `relation_kind = null` always
- L1 uses Plutchik axes for post-modifiers — L3 ignores them (always 0.0)
- L1 uses verb overrides by node-type pairs — L3 uses verb overrides by node-type pairs too, but with structural (not cognitive) vocabulary
- L1 verbs are colored by affect — L3 verbs are colored by structural properties only

**Same mechanism:** `[PRE-MODIFIERS] + [BASE VERB] + [POST-MODIFIERS]`

The verb is **never stored**. It is always **computed from dimensions**.

---

## CORE PRINCIPLE: NO STORED VERBS

At L3, there is no `relation_kind`, no stored verb, no prescribed label.
The relationship between two nodes is fully described by its 13 active dimensions:

| Dimension | Range | Structural Meaning at L3 |
|-----------|-------|--------------------------|
| weight | [0, +inf] | How established this relationship is |
| energy | [0, +inf] | How active right now (trending) |
| stability | [0, 1] | How resistant to dissolution |
| recency | [0, 1] | How fresh the last interaction was |
| polarity | [0,1] x [0,1] | Directional flow: [a→b strength, b→a strength] |
| hierarchy | [-1, +1] | -1 = contains/owns, +1 = elaborates/extends |
| permanence | [0, 1] | 0 = temporary/speculative, 1 = permanent/definitive |
| valence | [-1, +1] | Positive or negative structural charge |
| ambivalence | [0, 1] | Conflicting signals in the relationship |
| trust | [0, 1] | Reliability/credibility of this connection |
| friction | [0, 1] | Resistance/cost in this relationship |
| affinity | [0, 1] | Structural attraction (co-activation tendency) |
| aversion | [0, 1] | Structural repulsion (anti-correlation tendency) |

From these 13 numbers, the grammar computes a human-readable label on demand.

---

## BASE VERBS (from hierarchy + polarity)

### Hierarchy-Dominant (|hierarchy| > 0.5)

| hierarchy | Verb | L3 Meaning |
|-----------|------|------------|
| < -0.7 | "encompasses" | Full containment (world contains zone, org contains team) |
| -0.7 to -0.5 | "contains" | Partial containment (repo contains file, space holds actor) |
| +0.5 to +0.7 | "extends" | Elaboration (PR extends issue, reply extends thread) |
| > +0.7 | "specializes" | Deep elaboration (implementation specializes design) |

### Polarity-Dominant (|hierarchy| <= 0.5)

| polarity[0] | polarity[1] | Verb | L3 Meaning |
|-------------|-------------|------|------------|
| > 0.7 | < 0.3 | "acts on" | Unidirectional effect (author → commit, service → endpoint) |
| > 0.7 | 0.3-0.7 | "influences" | Strong a→b, moderate return (maintainer → project) |
| > 0.7 | > 0.7 | "interacts with" | Bilateral exchange (two collaborators, two services) |
| 0.3-0.7 | > 0.7 | "responds to" | Stronger b→a (reply to message, reaction to event) |
| < 0.3 | > 0.7 | "receives from" | Passive recipient (consumer ← producer) |
| 0.3-0.7 | 0.3-0.7 | "is linked to" | Weak bidirectional (co-occurrence, co-mention) |
| < 0.3 | < 0.3 | "coexists with" | Minimal interaction (same space, no real exchange) |

### Special Combinations

| hierarchy | polarity | Verb | L3 Meaning |
|-----------|----------|------|------------|
| < -0.5 | [>0.7, <0.3] | "absorbs" | Containment with consumption (space absorbs activity) |
| < -0.5 | [<0.3, >0.7] | "emits" | Containment with output (source emits artifacts) |
| > +0.5 | [>0.7, <0.3] | "refines" | Elaboration with strong direction (review refines PR) |
| > +0.5 | [>0.7, >0.7] | "co-develops" | Mutual elaboration (two projects evolving together) |

---

## PRE-MODIFIERS

### From Permanence

| permanence | Modifier | L3 Meaning |
|------------|----------|------------|
| < 0.2 | "temporarily" | Ephemeral (active session, draft PR) |
| 0.2 - 0.4 | "provisionally" | Uncertain (proposed change, pending review) |
| 0.4 - 0.6 | -- | Neutral |
| 0.6 - 0.8 | "established" | Confirmed (merged PR, verified transaction) |
| > 0.8 | "permanently" | Structural fact (org membership, physical location) |

### From Energy

| energy | Modifier | L3 Meaning |
|--------|----------|------------|
| > 8.0 | "intensely" | Very hot right now (viral event, active incident) |
| 5.0 - 8.0 | "actively" | Significant current activity |
| 2.0 - 5.0 | -- | Normal activity |
| 0.5 - 2.0 | "quietly" | Low activity |
| < 0.5 | "dormantly" | Nearly inactive (archived, stale) |

### From Trust (at L3: structural reliability, not emotional)

| trust | Modifier | L3 Meaning |
|-------|----------|------------|
| > 0.8 | "reliably" | High-confidence relationship (verified identity, long history) |
| 0.6 - 0.8 | "confidently" | Established reliability |
| 0.2 - 0.4 | "tentatively" | Low confidence (new relationship, unverified) |
| < 0.2 | "uncertainly" | Unknown reliability (stranger, first interaction) |

---

## POST-MODIFIERS

### From Friction

| friction | Modifier | L3 Meaning |
|----------|----------|------------|
| > 0.7 | "(high friction)" | Costly, contested, bureaucratic |
| 0.4 - 0.7 | "(some friction)" | Notable resistance |
| < 0.4 | -- | Low or no friction |

### From Affinity + Aversion

| affinity | aversion | Modifier | L3 Meaning |
|----------|----------|----------|------------|
| > 0.7 | < 0.3 | "(strong affinity)" | Natural co-activation, structural attraction |
| < 0.3 | > 0.7 | "(structural tension)" | Anti-correlated, tend to suppress each other |
| > 0.5 | > 0.5 | "(ambiguous)" | Both attracted and repulsed (complex relationship) |

### From Weight (accumulated importance)

| weight | Modifier | L3 Meaning |
|--------|----------|------------|
| > 5.0 | "[foundational]" | Core structural relationship |
| 3.0 - 5.0 | "[significant]" | Important relationship |
| 1.0 - 3.0 | -- | Normal |
| < 1.0 | "[minor]" | Weak, possibly dissolving |

### From Valence (structural, NOT emotional)

| valence | Modifier | L3 Meaning |
|---------|----------|------------|
| > 0.5 | "(constructive)" | Relationship adds value, builds structure |
| < -0.5 | "(destructive)" | Relationship degrades value, breaks structure |
| -0.5 to 0.5 | -- | Neutral structural impact |

### From Ambivalence

| ambivalence | Modifier | L3 Meaning |
|-------------|----------|------------|
| > 0.7 | "(contested)" | Strong conflicting signals about this relationship |
| 0.4 - 0.7 | "(disputed)" | Some disagreement |
| < 0.4 | -- | Clear signal |

---

## COMBINATION RULES

### Priority Order

1. **Pre-modifiers** (left to right, max 2):
   - Energy (if extreme)
   - Permanence
   - Trust (if extreme)

2. **Base verb** (always present)

3. **Post-modifiers** (max 2 + weight annotation):
   - Friction (if notable)
   - Affinity/Aversion
   - Valence (if extreme)
   - Ambivalence (if notable)
   - Weight (in brackets, optional)

### Neutral Suppression

If a dimension falls in its neutral range, it produces no modifier.
A link with all neutral values produces only the base verb.

### Template

```
{pre1} {pre2} {BASE_VERB} {post1}, {post2} [weight_annotation]
```

---

## SEMANTIC VERB OVERRIDES (by Node-Type Pair)

When the source and target node types are known, more specific verbs replace the
generic base verb. These are **structural** overrides, not cognitive ones.

### Actor -> Moment

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| polarity[0] > 0.7 | "performed" | Actor did the action |
| polarity[0] > 0.7 + hierarchy < -0.3 | "initiated" | Actor started/caused the event |
| polarity[0] < 0.3 + polarity[1] > 0.7 | "was affected by" | Event impacted actor |
| polarity ~= [0.5, 0.5] | "participated in" | Actor was involved bidirectionally |

### Actor -> Space

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy > 0.3 | "created" | Actor founded/built the space |
| hierarchy < -0.3 + permanence > 0.7 | "inhabits" | Actor resides in the space |
| hierarchy < -0.3 + permanence < 0.5 | "visits" | Actor is temporarily in the space |
| polarity[0] > 0.7 + trust > 0.5 | "administers" | Actor manages the space |
| polarity[0] < 0.3 | "left" | Actor departed the space |

### Actor -> Actor

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| trust > 0.7 + affinity > 0.7 | "trusted collaborator of" | High-trust bilateral relationship |
| trust > 0.5 + polarity[0] > 0.7 | "mentors" | Trust + directional influence |
| friction > 0.7 + aversion > 0.5 | "in conflict with" | High friction and structural aversion |
| affinity > 0.7 + polarity ~= [0.5, 0.5] | "partner of" | Strong mutual affinity |
| hierarchy < -0.5 + permanence > 0.7 | "employs" | Containment + permanence |
| hierarchy > 0.5 + permanence > 0.7 | "works for" | Subordination + permanence |

### Actor -> Thing

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy < -0.3 + permanence > 0.7 | "owns" | Permanent containment |
| hierarchy < -0.3 + permanence < 0.5 | "uses" | Temporary containment |
| polarity[0] > 0.7 | "created" | Actor produced the thing |
| polarity[0] < 0.3 + polarity[1] > 0.7 | "depends on" | Actor relies on the thing |

### Space -> Space

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy < -0.5 | "contains" | Parent-child spaces (world contains zone) |
| hierarchy > 0.5 | "is nested in" | Child to parent |
| polarity ~= [0.5, 0.5] + affinity > 0.5 | "is connected to" | Peer spaces with passage |
| friction > 0.5 | "borders" | Adjacent with boundary friction |

### Moment -> Moment

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| polarity[0] > 0.7 + recency(b) > recency(a) | "caused" | Temporal causation (a preceded b) |
| polarity ~= [0.5, 0.5] + recency ~= same | "co-occurred with" | Simultaneous events |
| hierarchy < -0.5 | "is the context of" | Larger event containing smaller |
| hierarchy > 0.5 | "is a detail of" | Smaller event within larger |
| valence < -0.5 | "cancelled" | Negation (refund cancels purchase) |

### Moment -> Thing

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| polarity[0] > 0.7 + valence > 0.3 | "produced" | Event created the artifact |
| polarity[0] > 0.7 + valence < -0.3 | "consumed" | Event destroyed/used up the thing |
| polarity[0] > 0.7 | "involved" | Event concerned the thing |
| hierarchy < -0.5 | "is about" | The event's subject |

### Thing -> Thing

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy < -0.5 + permanence > 0.7 | "contains" | Structural nesting (package contains module) |
| hierarchy > 0.5 | "is a component of" | Part-whole |
| polarity ~= [0.5, 0.5] + affinity > 0.5 | "accompanies" | Natural pairing |
| permanence > 0.8 + hierarchy ~= 0 | "is equivalent to" | Alias, same entity |
| valence < -0.5 + friction > 0.5 | "competes with" | Alternatives in tension |

### Narrative -> Moment

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy < -0.5 | "is evidenced by" | Narrative supported by events |
| hierarchy > 0.5 | "interprets" | Narrative gives meaning to event |
| valence < -0.5 | "is contradicted by" | Event undermines narrative |

### Narrative -> Narrative

| Condition | Verb | L3 Meaning |
|-----------|------|------------|
| hierarchy < -0.5 | "subsumes" | Broader narrative contains narrower |
| hierarchy > 0.5 | "elaborates" | Narrower narrative extends broader |
| valence < -0.5 + friction > 0.5 | "contradicts" | Incompatible narratives |
| trust > 0.5 + affinity > 0.5 | "corroborates" | Mutually reinforcing narratives |

---

## COMPOSITE PATTERN SIGNATURES

These are common link "fingerprints" — clusters of dimension values that map to
recognizable real-world relationships. They are not categories; they are regions
in the 13-dimensional link space.

### Ownership / Containment

```yaml
signature:
  hierarchy: [-1.0, -0.5]
  permanence: [0.7, 1.0]
  polarity: [[0.6, 1.0], [0.0, 0.4]]  # Strong a→b, weak b→a
  friction: [0.0, 0.3]
reads_as: "owns / contains / holds"
examples:
  - "GitHub org contains repo"
  - "Actor owns $MIND tokens"
  - "VR world contains zone"
```

### Trusted Collaboration

```yaml
signature:
  trust: [0.6, 1.0]
  affinity: [0.6, 1.0]
  friction: [0.0, 0.3]
  polarity: [[0.4, 0.7], [0.4, 0.7]]  # Roughly balanced
  stability: [0.5, 1.0]
reads_as: "trusted collaborator / reliable partner"
examples:
  - "Two citizens with long collaboration history"
  - "Service A reliably calls Service B"
  - "Author and long-term editor"
```

### Tension / Conflict

```yaml
signature:
  friction: [0.6, 1.0]
  aversion: [0.5, 1.0]
  energy: [3.0, +inf]  # Active tension
  valence: [-1.0, -0.3]
  ambivalence: [0.0, 0.5]  # Clear negative, not confused
reads_as: "in conflict / competing / contested"
examples:
  - "Two competing proposals for the same feature"
  - "Actor A and Actor B in a dispute"
  - "Rival services targeting same market"
```

### Response / Causation

```yaml
signature:
  polarity: [[0.6, 1.0], [0.0, 0.4]]  # Directional
  hierarchy: [0.3, 0.8]  # b elaborates a
  recency: [0.5, 1.0]  # Recent
reads_as: "response to / caused by / triggered by"
examples:
  - "PR is a response to issue"
  - "Refund triggered by complaint"
  - "Reply extends message"
```

### Economic Transfer

```yaml
signature:
  polarity: [[0.8, 1.0], [0.0, 0.2]]  # Strongly directional
  permanence: [0.8, 1.0]  # Irrevocable
  hierarchy: [-0.2, 0.2]  # Flat
  valence: [0.0, 1.0]  # Constructive or neutral
reads_as: "transferred to / paid / funded"
examples:
  - "$MIND transfer from citizen A to citizen B"
  - "Employer pays contractor"
  - "Donor funds project"
```

### Temporal Proximity (Co-occurrence)

```yaml
signature:
  polarity: [[0.3, 0.7], [0.3, 0.7]]  # Balanced
  hierarchy: [-0.3, 0.3]  # Flat
  recency: [0.7, 1.0]  # Very recent
  energy: [2.0, +inf]  # Active
reads_as: "co-occurred with / happened alongside"
examples:
  - "Two commits pushed in same session"
  - "Meeting and document creation at same time"
  - "Two events in same game round"
```

### Speculative / Proposed

```yaml
signature:
  permanence: [0.0, 0.3]
  stability: [0.0, 0.3]
  weight: [0.0, 1.5]
reads_as: "might relate to / proposed connection / speculative link"
examples:
  - "Draft PR linked to potential issue"
  - "Proposed partnership between orgs"
  - "Tentative categorization"
```

---

## FULL SYNTHESIS ALGORITHM

```python
def synthesize_l3_link(link, node_a, node_b):
    """
    Generate human-readable synthesis for an L3 universe link.

    No relation_kind. No emotions. Pure structural math.
    """

    # 1. Compute base verb
    verb = compute_base_verb(link.hierarchy, link.polarity)

    # 2. Check for node-type-pair override
    pair = (node_a.node_type, node_b.node_type)
    override = get_l3_override(pair, link)
    if override:
        verb = override

    # 3. Build pre-modifiers (max 2)
    pre = []

    # Energy
    if link.energy > 8.0:
        pre.append("intensely")
    elif link.energy > 5.0:
        pre.append("actively")
    elif link.energy < 0.5:
        pre.append("dormantly")

    # Permanence
    if link.permanence < 0.2:
        pre.append("temporarily")
    elif link.permanence > 0.8:
        pre.append("permanently")

    # Trust (only if extreme)
    if len(pre) < 2:
        if link.trust > 0.8:
            pre.append("reliably")
        elif link.trust < 0.2:
            pre.append("uncertainly")

    pre = pre[:2]  # Max 2

    # 4. Build post-modifiers (max 2 + weight)
    post = []

    # Friction
    if link.friction > 0.7:
        post.append("(high friction)")
    elif link.friction > 0.4:
        post.append("(some friction)")

    # Affinity / Aversion
    if link.affinity > 0.7 and link.aversion < 0.3:
        post.append("(strong affinity)")
    elif link.aversion > 0.7 and link.affinity < 0.3:
        post.append("(structural tension)")
    elif link.affinity > 0.5 and link.aversion > 0.5:
        post.append("(ambiguous)")

    # Valence
    if len(post) < 2:
        if link.valence > 0.5:
            post.append("(constructive)")
        elif link.valence < -0.5:
            post.append("(destructive)")

    # Ambivalence
    if len(post) < 2:
        if link.ambivalence > 0.7:
            post.append("(contested)")

    post = post[:2]  # Max 2

    # Weight annotation
    weight_annotation = ""
    if link.weight > 5.0:
        weight_annotation = "[foundational]"
    elif link.weight > 3.0:
        weight_annotation = "[significant]"
    elif link.weight < 1.0:
        weight_annotation = "[minor]"

    # 5. Assemble
    parts = pre + [verb] + post
    synthesis = " ".join(parts)
    if weight_annotation:
        synthesis += f" {weight_annotation}"

    return synthesis
```

---

## EXAMPLES

### Example 1: Citizen owns a token collection

```yaml
# Actor -> Thing
polarity: [0.9, 0.1]
hierarchy: -0.6
permanence: 0.95
trust: 0.9
affinity: 0.8
friction: 0.0
valence: 0.3
energy: 1.5
weight: 4.2
```

**Synthesis:** `"permanently owns [significant]"`

---

### Example 2: Two actors in active collaboration

```yaml
# Actor -> Actor
polarity: [0.65, 0.60]
hierarchy: 0.0
permanence: 0.7
trust: 0.85
affinity: 0.75
friction: 0.1
valence: 0.4
energy: 6.0
weight: 3.5
stability: 0.7
```

**Synthesis:** `"actively reliably trusted collaborator of (strong affinity) [significant]"`

---

### Example 3: Commit moment to repository space

```yaml
# Moment -> Space (via Thing/Space pattern)
polarity: [0.8, 0.2]
hierarchy: 0.6
permanence: 0.95
trust: 0.5
affinity: 0.3
friction: 0.0
valence: 0.3
energy: 2.0
weight: 0.8
```

**Synthesis:** `"permanently extends [minor]"`

---

### Example 4: Competing proposals (tension)

```yaml
# Narrative -> Narrative
polarity: [0.5, 0.5]
hierarchy: 0.0
permanence: 0.4
trust: 0.2
affinity: 0.1
aversion: 0.8
friction: 0.75
valence: -0.6
energy: 7.0
weight: 2.0
ambivalence: 0.3
```

**Synthesis:** `"actively uncertainly contradicts (high friction) (structural tension)"`

---

### Example 5: Crystallized project hub containing commits

```yaml
# Narrative (hub) -> Moment (commit)
polarity: [0.8, 0.2]
hierarchy: -0.9
permanence: 1.0
trust: 0.7
affinity: 0.6
friction: 0.0
valence: 0.4
energy: 0.3
weight: 6.0
```

**Synthesis:** `"dormantly permanently encompasses [foundational]"`

---

### Example 6: $MIND economic transfer

```yaml
# Actor -> Actor (via Moment intermediary, but direct link also valid)
polarity: [0.95, 0.05]
hierarchy: 0.0
permanence: 1.0
trust: 0.4
affinity: 0.2
friction: 0.1
valence: 0.6
energy: 3.0
weight: 1.2
```

**Synthesis:** `"permanently acts on (constructive)"`

With Actor->Actor override: `"permanently transferred to (constructive)"`

---

## WHAT THIS GRAMMAR REPLACES

At L3, there is no need for:
- `relation_kind` — the verb is computed, not stored
- Plutchik emotion axes — the universe has no feelings
- Limbic-coupled modifiers (fear, rage, joy) — those are L1 only
- Cognitive verb categories (remembers, cares_about, wants) — those are L1 only

The same 13 dimensional numbers that describe a link at L1 describe it at L3.
The grammar is different because the interpretation is different.
The math is the same because the physics is the same.

---

## POINTERS

- L1 Link Grammar: `docs/schema/GRAMMAR_Link_Synthesis.md`
- Schema v2.0: `docs/schema/schema.yaml` (L3 section)
- L3 Invariants: `docs/schema/schema.yaml` (l3_invariants)
- Physics Laws: `docs/cognition/l1/ALGORITHM_L1_Physics.md`
