# Link Synthesis Grammar
# Physics → Language Mapping

```
VERSION: 2.1
DATE: 2025-12-26
SCHEMA: v1.7.1
```

## CHANGELOG v2.1

- Added OWNERSHIP_VERBS (Thing ↔ Actor)
- Added EVIDENTIAL_VERBS (Thing/Moment → Narrative)
- Extended SPATIAL_VERBS (Space → Actor/Thing)
- Added VERB_INTENSIFIERS (attenuated/intensified forms)
- Added NODE_SYNTHESIS_GRAMMAR (formalized)
- Added BIDIRECTIONAL_SYNTHESIS (mutual relations)
- Added NARRATIVE_CONTEXT_MODIFIERS
- **v2.1**: Added TEMPORAL_MODIFIERS (recency, age, duration)

---

## STRUCTURE

```
[PRE-MODIFIERS] + [BASE VERB] + [POST-MODIFIERS]
```

Example: `"suddenly"` + `"contradicts"` + `"with rage"`

---

## BASE VERBS (from hierarchy + polarity)

### Hierarchy-Dominant (|hierarchy| > 0.5)

| hierarchy | polarity[0] | polarity[1] | Verb |
|-----------|-------------|-------------|------|
| < -0.7 | any | any | "encompasses" |
| -0.7 to -0.5 | any | any | "contains" |
| +0.5 to +0.7 | any | any | "elaborates" |
| > +0.7 | any | any | "exemplifies" |

### Polarity-Dominant (|hierarchy| ≤ 0.5)

| polarity[0] | polarity[1] | Verb |
|-------------|-------------|------|
| > 0.7 | < 0.3 | "acts on" |
| > 0.7 | 0.3 - 0.7 | "influences" |
| > 0.7 | > 0.7 | "interacts with" |
| 0.3 - 0.7 | > 0.7 | "receives from" |
| < 0.3 | > 0.7 | "undergoes" |
| 0.3 - 0.7 | 0.3 - 0.7 | "is linked to" |
| < 0.3 | < 0.3 | "coexists with" |

### Special Combinations

| hierarchy | polarity pattern | Verb |
|-----------|------------------|------|
| < -0.5 | [>0.7, <0.3] | "absorbs" |
| < -0.5 | [<0.3, >0.7] | "diffuses to" |
| > +0.5 | [>0.7, <0.3] | "reinforces" |
| > +0.5 | [>0.7, >0.7] | "co-elaborates" |

---

## PRE-MODIFIERS

### From Permanence

| permanence | Modifier | Meaning |
|------------|----------|---------|
| < 0.2 | "perhaps" | Highly speculative |
| 0.2 - 0.4 | "probably" | Uncertain |
| 0.4 - 0.6 | — | Neutral, no modifier |
| 0.6 - 0.8 | "clearly" | Confident |
| > 0.8 | "definitely" | Canon/fact |

### From Surprise-Anticipation

| surprise_anticipation | Modifier | Meaning |
|-----------------------|----------|---------|
| > +0.7 | "suddenly" | Shocking, unexpected |
| +0.4 to +0.7 | "unexpectedly" | Surprising |
| -0.4 to +0.4 | — | Neutral |
| -0.7 to -0.4 | "as expected" | Expected |
| < -0.7 | "inevitably" | Long anticipated |

### From Energy (link.energy)

| energy | Modifier | Meaning |
|--------|----------|---------|
| > 8.0 | "intensely" | Very hot right now |
| 5.0 - 8.0 | "actively" | Active |
| 2.0 - 5.0 | — | Neutral |
| 0.5 - 2.0 | "weakly" | Low activity |
| < 0.5 | "barely" | Nearly dormant |

---

## TEMPORAL MODIFIERS

Based on temporal fields from schema v1.7.1.

**All temporal fields are auto-managed:**
- `created_at_s` — auto-generated on creation
- `updated_at_s` — auto-updated on modification
- `last_traversed_at_s` — auto-updated on traversal
- `started_at_s` — auto-set when moment status → active
- `completed_at_s` — auto-set when moment status → completed
- `duration_s` — computed (completed_at_s - started_at_s)

### Recency (from last_traversed_at_s)

How recently was this link/node traversed? Uses `now - last_traversed_at_s`.

| Recency (seconds) | English | French | Meaning |
|-------------------|---------|--------|---------|
| < 60 | "just now" | "à l'instant" | Within last minute |
| 60 - 3600 | "recently" | "récemment" | Within last hour |
| 3600 - 86400 | "today" | "aujourd'hui" | Within last day |
| 86400 - 604800 | "this week" | "cette semaine" | Within last week |
| > 604800 | "long ago" | "depuis longtemps" | Over a week ago |
| null | — | — | Never traversed |

### Age (from created_at_s)

How old is this relationship? Uses `now - created_at_s`.

| Age (seconds) | English | French | Meaning |
|---------------|---------|--------|---------|
| < 3600 | "newly" | "nouvellement" | Just created |
| 3600 - 86400 | "freshly" | "fraîchement" | Created today |
| 86400 - 604800 | — | — | Normal age |
| > 2592000 | "anciently" | "anciennement" | Over a month old |
| > 31536000 | "timelessly" | "depuis toujours" | Over a year old |

### Duration (Moments only, from MomentBase)

For moments with temporal bounds.

| Condition | English | French | Meaning |
|-----------|---------|--------|---------|
| duration_s < 60 | "briefly" | "brièvement" | Under a minute |
| duration_s 60-3600 | — | — | Normal duration |
| duration_s > 3600 | "prolongedly" | "longuement" | Over an hour |
| duration_s > 86400 | "extensively" | "extensivement" | Over a day |
| started_at_s set, completed_at_s null | "ongoing" | "en cours" | Still active |
| started_at_s null | "pending" | "en attente" | Not yet started |

### Staleness (from updated_at_s vs last_traversed_at_s)

Detects stale links that haven't been traversed since they were modified.

| Condition | English | French | Meaning |
|-----------|---------|--------|---------|
| last_traversed < updated | "unvisited since update" | "non visité depuis mise à jour" | Stale |
| last_traversed > updated + 86400 | "well-trodden" | "bien parcouru" | Frequently traversed |

### Temporal Modifier Priority

Temporal modifiers are **optional post-modifiers** that add context:

1. Recency (if last_traversed_at_s is set and recent)
2. Age (if notably new or old)
3. Duration (for moments only)

Max 1 temporal modifier per synthesis to avoid verbosity.

### Examples

```yaml
# Recently traversed link
last_traversed_at_s: 1735200000  # 30 seconds ago
→ "influences, recently"
→ "influence, récemment"

# Ancient relationship
created_at_s: 1672531200  # Over a year ago
→ "timelessly encompasses"
→ "englobe depuis toujours"

# Ongoing moment
started_at_s: 1735190000
completed_at_s: null
→ "The Confrontation, burning (ongoing)"
→ "la Confrontation, brûlante (en cours)"

# Brief moment
duration_s: 45
→ "The Accusation, briefly (completed)"
→ "the Accusation, briefly (completed)"
```

---

## POST-MODIFIERS

### From Fear-Anger

| fear_anger | Modifier | Meaning |
|------------|----------|---------|
| < -0.7 | "with rage" | Intense anger |
| -0.7 to -0.4 | "with hostility" | Anger |
| -0.4 to +0.4 | — | Neutral |
| +0.4 to +0.7 | "with apprehension" | Fear |
| > +0.7 | "with terror" | Intense fear |

### From Trust-Disgust

| trust_disgust | Modifier | Meaning |
|---------------|----------|---------|
| < -0.7 | "with disgust" | Loathing |
| -0.7 to -0.4 | "with distrust" | Distrust |
| -0.4 to +0.4 | — | Neutral |
| +0.4 to +0.7 | "with confidence" | Trust |
| > +0.7 | "with admiration" | Deep trust |

### From Joy-Sadness

| joy_sadness | Modifier | Meaning |
|-------------|----------|---------|
| < -0.7 | "with despair" | Grief |
| -0.7 to -0.4 | "with sadness" | Sadness |
| -0.4 to +0.4 | — | Neutral |
| +0.4 to +0.7 | "with satisfaction" | Joy |
| > +0.7 | "with euphoria" | Ecstasy |

### From Weight (accumulated importance)

| weight | Modifier | Meaning |
|--------|----------|---------|
| > 5.0 | "(fundamental)" | Core relationship |
| 3.0 - 5.0 | "(important)" | Significant |
| 1.0 - 3.0 | — | Normal |
| < 1.0 | "(minor)" | Weak relationship |

---

## COMBINATION RULES

### Priority Order

1. **Pre-modifiers** (left to right):
   - Energy (if extreme)
   - Surprise-anticipation
   - Permanence

2. **Base verb** (always present)

3. **Post-modifiers** (combined with "et" if multiple):
   - Fear-anger
   - Trust-disgust
   - Joy-sadness
   - Weight (in parentheses, optional)

### Max Modifiers

- Max 2 pre-modifiers
- Max 2 post-modifiers (+ weight annotation)
- If more qualify, pick highest intensity

### Neutral Suppression

- If value in neutral range (typically -0.4 to +0.4), no modifier
- A link with all neutral values = just the base verb

---

## EXAMPLES

### Example 1: Belief with anger

```yaml
polarity: [0.9, 0.1]
hierarchy: 0.0
permanence: 0.8
fear_anger: -0.7
trust_disgust: -0.4
joy_sadness: 0.0
surprise_anticipation: 0.0
weight: 4.0
energy: 6.0
```

**Synthesis:** `"définitivement agit sur avec hostilité (important)"`

Or more natural: `"définitivement influence, avec hostilité"`

---

### Example 2: Sudden contradiction

```yaml
polarity: [0.9, 0.1]
hierarchy: 0.0
permanence: 1.0
fear_anger: 0.0
trust_disgust: 0.4
joy_sadness: 0.2
surprise_anticipation: 0.9
weight: 3.0
energy: 7.0
```

**Synthesis:** `"activement, soudain, définitivement agit sur avec confiance"`

Or: `"soudain et définitivement contredit, avec confiance retrouvée"`

---

### Example 3: Container relationship

```yaml
polarity: [0.7, 0.3]
hierarchy: -0.9
permanence: 1.0
fear_anger: 0.0
trust_disgust: 0.0
joy_sadness: 0.0
surprise_anticipation: 0.0
weight: 1.0
energy: 2.0
```

**Synthesis:** `"définitivement englobe"`

---

### Example 4: Weak speculation

```yaml
polarity: [0.5, 0.5]
hierarchy: 0.0
permanence: 0.1
fear_anger: 0.0
trust_disgust: -0.5
joy_sadness: 0.0
surprise_anticipation: 0.0
weight: 0.8
energy: 1.0
```

**Synthesis:** `"peut-être est lié à, avec méfiance (mineur)"`

---

### Example 5: Elaboration with joy

```yaml
polarity: [0.8, 0.4]
hierarchy: 0.8
permanence: 0.7
fear_anger: 0.0
trust_disgust: 0.6
joy_sadness: 0.6
surprise_anticipation: -0.3
weight: 2.5
energy: 4.0
```

**Synthesis:** `"clairement exemplifie, avec confiance et satisfaction"`

---

## SEMANTIC VERB OVERRIDES

When node types are known, more specific verbs can be used.

### Actor → Moment

| Base Verb | Override |
|-----------|----------|
| "acts on" | "expresses" |
| "influences" | "initiates" |

### Actor → Narrative

| Condition | Override |
|-----------|----------|
| polarity[0] > 0.7 + trust > 0.5 | "believes in" |
| polarity[0] > 0.7 + trust < -0.5 | "doubts" |
| hierarchy > 0.5 | "created" |
| hierarchy < -0.5 | "is defined by" |

### Actor → Thing (OWNERSHIP)

| Condition | Override |
|-----------|----------|
| hierarchy < -0.3 | "possesses" |
| hierarchy < -0.3 + permanence > 0.8 | "holds" |
| polarity[0] > 0.7 + polarity[1] < 0.3 | "uses" |
| polarity[0] < 0.3 + polarity[1] > 0.7 | "depends on" |

### Thing → Actor (OWNERSHIP inverse)

| Condition | Override |
|-----------|----------|
| hierarchy > 0.3 | "belongs to" |
| hierarchy > 0.3 + permanence > 0.8 | "is the property of" |
| polarity[0] > 0.7 | "serves" |
| polarity[0] < 0.3 + polarity[1] > 0.7 | "encumbers" |

### Thing → Thing

| Condition | Override |
|-----------|----------|
| hierarchy < -0.5 | "contains" |
| hierarchy > 0.5 | "compose" |
| polarity ≈ [0.5, 0.5] | "accompanies" |
| permanence > 0.8 | "is attached to" |

### Moment → Narrative (EVIDENTIAL)

| Condition | Override |
|-----------|----------|
| hierarchy > 0.5 | "illustrates" |
| permanence > 0.8 + trust > 0.5 | "confirms" |
| permanence > 0.8 + trust < -0.5 | "contradicts" |
| permanence 0.5-0.8 + trust > 0.3 | "supports" |
| permanence 0.5-0.8 + trust < -0.3 | "questions" |
| permanence < 0.5 | "evokes" |

### Moment → Thing

| Base Verb | Override |
|-----------|----------|
| "acts on" | "concerns" |
| "influences" | "affects" |
| hierarchy > 0.5 | "reveals" |
| hierarchy < -0.5 | "implicates" |

### Thing → Narrative (EVIDENTIAL)

| Condition | Override |
|-----------|----------|
| permanence > 0.8 + trust > 0.5 | "proves" |
| permanence > 0.8 + trust < -0.5 | "refutes" |
| permanence 0.5-0.8 + trust > 0.3 | "suggests" |
| permanence 0.5-0.8 + trust < -0.3 | "casts doubt on" |
| permanence < 0.5 | "evokes" |
| hierarchy > 0.5 | "symbolizes" |

### Space → Actor (SPATIAL extended)

| Condition | Override |
|-----------|----------|
| hierarchy < -0.7 | "shelters" |
| hierarchy -0.7 to -0.5 | "contains" |
| hierarchy < -0.5 + energy > 6.0 | "welcomes" |
| hierarchy < -0.5 + fear_anger > 0.4 | "imprisons" |
| hierarchy < -0.5 + joy_sadness > 0.4 | "protects" |
| hierarchy < -0.5 + joy_sadness < -0.4 | "isolates" |

### Space → Thing (SPATIAL extended)

| Condition | Override |
|-----------|----------|
| hierarchy < -0.5 + permanence > 0.8 | "encloses" |
| hierarchy < -0.5 + permanence < 0.5 | "exposes" |
| hierarchy < -0.7 | "shelters" |
| hierarchy -0.7 to -0.5 | "contains" |

### Actor → Space

| Condition | Override |
|-----------|----------|
| polarity[0] > 0.7 | "occupies" |
| polarity[0] > 0.7 + permanence > 0.8 | "inhabits" |
| polarity[0] < 0.3 | "flees" |
| polarity[0] < 0.3 + fear_anger > 0.4 | "fears" |
| hierarchy > 0.5 | "dominates" |
| hierarchy < -0.5 | "belongs to" |

### Narrative → Narrative

| Condition | Override |
|-----------|----------|
| trust < -0.7 + permanence > 0.8 | "radically contradicts" |
| trust < -0.5 + permanence > 0.8 | "contradicts" |
| trust < -0.5 + permanence < 0.5 | "is in tension with" |
| trust > 0.5 + hierarchy > 0.5 | "elaborates" |
| trust > 0.5 + hierarchy < -0.5 | "contextualizes" |
| hierarchy > 0.7 | "is the mechanism of" |
| hierarchy < -0.7 | "encompasses" |
| polarity ≈ [0.7+, 0.7+] | "interacts with" |

---

## VERB INTENSIFIERS

Based on `intensity = permanence + |polarity[0] - polarity[1]|`:

| Intensity | Form |
|-----------|------|
| < 0.4 | Attenuated |
| 0.4 - 0.8 | Base |
| > 0.8 | Intensified |

### Intensifier Table

| Base Verb | Attenuated | Intensified |
|-----------|------------|-------------|
| "believes in" | "tends to believe" | "firmly believes" |
| "doubts" | "hesitates about" | "rejects" |
| "contradicts" | "nuances" | "radically contradicts" |
| "confirms" | "supports" | "absolutely confirms" |
| "influences" | "touches" | "dominates" |
| "contains" | "touches" | "imprisons" |
| "shelters" | "welcomes" | "protects" |
| "belongs to" | "is associated with" | "is inseparable from" |
| "possesses" | "has access to" | "holds" |
| "proves" | "suggests" | "demonstrates" |
| "illustrates" | "evokes" | "embodies" |
| "expresses" | "sketches" | "proclaims" |

### Intensity Calculation

```python
def compute_intensity(link):
    polarity_strength = abs(link.polarity[0] - link.polarity[1])
    return (link.permanence + polarity_strength) / 2

def apply_intensifier(verb, intensity):
    if intensity < 0.4:
        return ATTENUATED.get(verb, verb)
    elif intensity > 0.8:
        return INTENSIFIED.get(verb, verb)
    return verb
```

---

## BIDIRECTIONAL SYNTHESIS

When `|polarity[0] - polarity[1]| < 0.2`, the relationship is mutual.

### Detection

```python
def is_bidirectional(link):
    return abs(link.polarity[0] - link.polarity[1]) < 0.2
```

### Mutual Verb Forms

| Base Verb | Mutual Form |
|-----------|-------------|
| "influences" | "mutually influence each other" |
| "acts on" | "interact" |
| "contradicts" | "contradict each other" |
| "supports" | "reinforce each other" |
| "is linked to" | "are linked" |
| "believes in" | "mutually validate each other" |

### Output Modes

For bidirectional links, generate three forms:

```python
def generate_bidirectional_synthesis(link, node_a, node_b):
    if not is_bidirectional(link):
        return {
            'forward': generate_synthesis(link, node_a, node_b),
            'reverse': None,
            'combined': None
        }

    base = generate_synthesis(link, node_a, node_b)
    mutual = MUTUAL_FORMS.get(extract_verb(base), base)

    return {
        'forward': base,
        'reverse': generate_synthesis(link, node_b, node_a),
        'combined': apply_modifiers(mutual, link)
    }
```

### Examples

```yaml
# Bidirectional link
polarity: [0.75, 0.72]

forward: "influence avec confiance"
reverse: "influence avec confiance"
combined: "s'influencent mutuellement avec confiance"
```

---

## NARRATIVE CONTEXT MODIFIERS

Narratives have a `type` field that adds contextual flavor.

### Narrative Types

| Type | Context Modifier |
|------|------------------|
| belief | "as a belief" |
| pattern | "as a pattern" |
| secret | "secretly" |
| mechanism | "mechanically" |
| memory | "in memory" |
| prophecy | "prophetically" |

### Application Rules

1. Context modifier is a **pre-modifier** (before verb)
2. Only applies when target node is a narrative with explicit type
3. Priority: after energy, before surprise

### Examples

```yaml
# Link to narrative with type: secret
Actor → Narrative (secret)
"secrètement croit en"

# Link to narrative with type: mechanism
Thing → Narrative (mechanism)
"mécaniquement prouve"

# Link between narratives
Narrative (belief) → Narrative (pattern)
"en tant que croyance élabore comme schéma"
# Simplified: "elaborates the pattern from the belief"
```

### Implementation

```python
def get_narrative_context_modifier(node, position):
    """
    position: 'source' or 'target'
    """
    if node.node_type != 'narrative':
        return None

    narrative_type = getattr(node, 'type', None)
    if not narrative_type:
        return None

    modifiers = {
        'belief': ('en tant que croyance', 'la croyance'),
        'pattern': ('comme schéma', 'le schéma'),
        'secret': ('secrètement', 'le secret'),
        'mechanism': ('mécaniquement', 'le mécanisme'),
        'memory': ('en souvenir', 'le souvenir'),
        'prophecy': ('prophétiquement', 'la prophétie'),
    }

    if position == 'source':
        return modifiers.get(narrative_type, (None, None))[0]
    else:
        return modifiers.get(narrative_type, (None, None))[1]
```

---

## NODE SYNTHESIS GRAMMAR

Nodes also have synthesis, computed from their properties.

### Structure

```
[ARTICLE] + [NAME] + [ENERGY-STATE] + [IMPORTANCE]
```

### Articles by Type

| Node Type | Article |
|-----------|---------|
| actor | — (proper noun) or "le/la" (role) |
| space | "le/la/les" |
| thing | "le/la/les" |
| narrative | "la" (feminine for beliefs/patterns) |
| moment | "le/la" (event) |

### Energy-State Modifiers

| Energy | Modifier | Meaning |
|--------|----------|---------|
| > 8.0 | ", incandescent" | Extremely active |
| 6.0 - 8.0 | ", burning" | Very active |
| 4.0 - 6.0 | ", active" | Active |
| 2.0 - 4.0 | — | Neutral |
| 1.0 - 2.0 | ", weak" | Low activity |
| < 1.0 | ", dormant" | Nearly inactive |

### Importance Modifiers (from weight)

| Weight | Modifier | Meaning |
|--------|----------|---------|
| > 5.0 | "(central)" | Core to the story |
| 3.0 - 5.0 | "(important)" | Significant |
| 1.0 - 3.0 | — | Normal |
| < 1.0 | "(minor)" | Background element |

### Status Modifiers (moments only)

| Status | Modifier |
|--------|----------|
| active | "(in progress)" |
| completed | "(completed)" |
| possible | "(possible)" |

### Node Type Specific Synthesis

#### Actors

```python
def synthesize_actor(node):
    parts = [node.name]

    # Energy state
    if node.energy > 8.0:
        parts.append("intensely present")
    elif node.energy > 6.0:
        parts.append("très actif")
    elif node.energy < 1.0:
        parts.append("en retrait")

    # Importance
    if node.weight > 5.0:
        parts.append("(central)")
    elif node.weight > 3.0:
        parts.append("(important)")

    return ", ".join(parts)
```

**Examples:**
- `"Edmund, intensely present (central)"`
- `"Gloucester (fundamental)"`
- `"the Servant, active"`

#### Spaces

```python
def synthesize_space(node):
    article = get_article(node.name, 'space')
    parts = [f"{article}{node.name}"]

    # Energy = atmosphere
    if node.energy > 6.0:
        parts.append("charged")
    elif node.energy < 2.0:
        parts.append("calme")

    # Weight
    if node.weight > 5.0:
        parts.append("(central)")
    elif node.weight > 3.0:
        parts.append("(important)")

    return ", ".join(parts)
```

**Examples:**
- `"the Great Hall, charged"`
- `"the Dungeons, dormant"`
- `"Castle Gloucester (important)"`

#### Things

```python
def synthesize_thing(node):
    article = get_article(node.name, 'thing')
    parts = [f"{article}{node.name}"]

    # Energy = salience
    if node.energy > 6.0:
        parts.append("brûlant(e)")
    elif node.energy < 2.0:
        parts.append("dormant(e)")

    # Weight
    if node.weight > 5.0:
        parts.append("(fundamental)")
    elif node.weight > 3.0:
        parts.append("(important)")
    elif node.weight < 1.0:
        parts.append("(minor)")

    return ", ".join(parts)
```

**Examples:**
- `"the Forged Letter, burning (important)"`
- `"the Father's Sword, dormant"`
- `"the Family Seal (important)"`

#### Narratives

```python
def synthesize_narrative(node):
    parts = [f"la {node.name}"]

    # Energy = how contested/active
    if node.energy > 8.0:
        parts.append("incandescente")
    elif node.energy > 6.0:
        parts.append("brûlante")
    elif node.energy > 4.0:
        parts.append("active")
    elif node.energy < 2.0:
        parts.append("latente")

    # Weight
    if node.weight > 5.0:
        parts.append("(centrale)")
    elif node.weight > 3.0:
        parts.append("(importante)")

    return ", ".join(parts)
```

**Examples:**
- `"the Father's Betrayal, incandescent (central)"`
- `"the Hidden Truth, burning (important)"`
- `"the Forgery Mechanism (important)"`

#### Moments

```python
def synthesize_moment(node):
    parts = [f"l'{node.name}" if starts_with_vowel(node.name) else f"le {node.name}"]

    # Energy = urgency
    if node.energy > 8.0:
        parts.append("incandescent")
    elif node.energy > 6.0:
        parts.append("brûlant")

    # Status
    status_map = {
        'active': "(in progress)",
        'completed': "(completed)",
        'possible': "(possible)"
    }
    if node.status in status_map:
        parts.append(status_map[node.status])

    return ", ".join(parts)
```

**Examples:**
- `"Edmund's Accusation (completed)"`
- `"the Servant's Revelation, incandescent (in progress)"`
- `"Edmund's Choice (possible)"`

---

## FULL LINK EXPRESSION

Combining node and link synthesis:

```
[Node A Synthesis] + [Link Synthesis] + [Node B Synthesis]
```

### Examples

```
Edmund, intensely present (central)
  └─ firmly believes with disgust and hostility ─→
     the Father's Betrayal, incandescent (central)

the Forged Letter, burning (important)
  └─ definitely belongs to ─→
     Edmund, intensely present (central)

the Great Hall, charged
  └─ welcomes ─→
     Edmund, intensely present
```

---

## IMPLEMENTATION

### Complete Implementation (v2.0)

```python
# =============================================================================
# VOCABULARY (Bilingual: English default, French available)
# =============================================================================

VOCAB = {
    'en': {
        # Base verbs
        'encompasses': 'encompasses',
        'contains': 'contains',
        'elaborates': 'elaborates',
        'exemplifies': 'exemplifies',
        'acts_on': 'acts on',
        'influences': 'influences',
        'interacts_with': 'interacts with',
        'receives_from': 'receives from',
        'undergoes': 'undergoes',
        'linked_to': 'is linked to',
        'coexists_with': 'coexists with',

        # Ownership verbs
        'belongs_to': 'belongs to',
        'owns': 'owns',
        'possesses': 'possesses',
        'holds': 'holds',
        'uses': 'uses',
        'depends_on': 'depends on',
        'serves': 'serves',
        'accompanies': 'accompanies',

        # Evidential verbs
        'proves': 'proves',
        'refutes': 'refutes',
        'suggests': 'suggests',
        'questions': 'questions',
        'evokes': 'evokes',
        'symbolizes': 'symbolizes',
        'confirms': 'confirms',
        'contradicts': 'contradicts',
        'supports': 'supports',
        'illustrates': 'illustrates',

        # Spatial verbs
        'shelters': 'shelters',
        'welcomes': 'welcomes',
        'imprisons': 'imprisons',
        'protects': 'protects',
        'isolates': 'isolates',
        'encloses': 'encloses',
        'exposes': 'exposes',
        'occupies': 'occupies',
        'inhabits': 'inhabits',
        'flees': 'flees',
        'fears': 'fears',
        'dominates': 'dominates',

        # Actor verbs
        'expresses': 'expresses',
        'initiates': 'initiates',
        'believes_in': 'believes in',
        'doubts': 'doubts',
        'created': 'created',
        'is_defined_by': 'is defined by',

        # Narrative verbs
        'radically_contradicts': 'radically contradicts',
        'is_in_tension_with': 'is in tension with',
        'is_mechanism_of': 'is the mechanism of',
        'contextualizes': 'contextualizes',

        # Pre-modifiers
        'intensely': 'intensely',
        'barely': 'barely',
        'suddenly': 'suddenly',
        'inevitably': 'inevitably',
        'definitely': 'definitely',
        'perhaps': 'perhaps',
        'probably': 'probably',
        'clearly': 'clearly',
        'actively': 'actively',
        'weakly': 'weakly',
        'unexpectedly': 'unexpectedly',
        'as_expected': 'as expected',

        # Post-modifiers
        'with_rage': 'with rage',
        'with_terror': 'with terror',
        'with_hostility': 'with hostility',
        'with_apprehension': 'with apprehension',
        'with_disgust': 'with disgust',
        'with_admiration': 'with admiration',
        'with_distrust': 'with distrust',
        'with_confidence': 'with confidence',
        'with_despair': 'with despair',
        'with_euphoria': 'with euphoria',
        'with_sadness': 'with sadness',
        'with_satisfaction': 'with satisfaction',

        # Weight annotations
        'fundamental': '(fundamental)',
        'important': '(important)',
        'minor': '(minor)',

        # Narrative context
        'as_belief': 'as a belief',
        'as_pattern': 'as a pattern',
        'secretly': 'secretly',
        'mechanically': 'mechanically',
        'in_memory': 'in memory',
        'prophetically': 'prophetically',

        # Node synthesis
        'intensely_present': 'intensely present',
        'very_active': 'very active',
        'withdrawn': 'withdrawn',
        'central': '(central)',
        'charged': 'charged',
        'calm': 'calm',
        'burning': 'burning',
        'dormant': 'dormant',
        'incandescent': 'incandescent',
        'active': 'active',
        'latent': 'latent',
        'in_progress': '(in progress)',
        'completed': '(completed)',
        'possible': '(possible)',

        # Connectors
        'and': 'and',
        'with': 'with',

        # Temporal modifiers
        'just_now': 'just now',
        'recently': 'recently',
        'today': 'today',
        'this_week': 'this week',
        'long_ago': 'long ago',
        'newly': 'newly',
        'freshly': 'freshly',
        'anciently': 'anciently',
        'timelessly': 'timelessly',
        'briefly': 'briefly',
        'prolongedly': 'prolongedly',
        'extensively': 'extensively',
        'ongoing': '(ongoing)',
        'pending': '(pending)',
        'stale': '(unvisited since update)',
        'well_trodden': '(well-trodden)',
    },
    'fr': {
        # Base verbs
        'encompasses': 'englobe',
        'contains': 'contient',
        'elaborates': 'détaille',
        'exemplifies': 'exemplifie',
        'acts_on': 'agit sur',
        'influences': 'influence',
        'interacts_with': 'interagit avec',
        'receives_from': 'reçoit de',
        'undergoes': 'subit',
        'linked_to': 'est lié à',
        'coexists_with': 'coexiste avec',

        # Ownership verbs
        'belongs_to': 'appartient à',
        'owns': 'possède',
        'possesses': 'possède',
        'holds': 'détient',
        'uses': 'utilise',
        'depends_on': 'dépend de',
        'serves': 'sert',
        'accompanies': 'accompagne',

        # Evidential verbs
        'proves': 'prouve',
        'refutes': 'réfute',
        'suggests': 'suggère',
        'questions': 'remet en question',
        'evokes': 'évoque',
        'symbolizes': 'symbolise',
        'confirms': 'confirme',
        'contradicts': 'contredit',
        'supports': 'soutient',
        'illustrates': 'illustre',

        # Spatial verbs
        'shelters': 'abrite',
        'welcomes': 'welcomes',
        'imprisons': 'emprisonne',
        'protects': 'protège',
        'isolates': 'isole',
        'encloses': 'renferme',
        'exposes': 'expose',
        'occupies': 'occupe',
        'inhabits': 'habite',
        'flees': 'fuit',
        'fears': 'craint',
        'dominates': 'domine',

        # Actor verbs
        'expresses': 'exprime',
        'initiates': 'initie',
        'believes_in': 'croit en',
        'doubts': 'doute de',
        'created': 'a créé',
        'is_defined_by': 'est défini par',

        # Narrative verbs
        'radically_contradicts': 'contredit radicalement',
        'is_in_tension_with': 'est en tension avec',
        'is_mechanism_of': 'est le mécanisme de',
        'contextualizes': 'contextualise',

        # Pre-modifiers
        'intensely': 'intensément',
        'barely': 'à peine',
        'suddenly': 'soudain',
        'inevitably': 'inévitablement',
        'definitely': 'définitivement',
        'perhaps': 'peut-être',
        'probably': 'probablement',
        'clearly': 'clairement',
        'actively': 'activement',
        'weakly': 'faiblement',
        'unexpectedly': 'de manière inattendue',
        'as_expected': 'comme prévu',

        # Post-modifiers
        'with_rage': 'avec rage',
        'with_terror': 'avec terreur',
        'with_hostility': 'avec hostilité',
        'with_apprehension': 'avec appréhension',
        'with_disgust': 'avec dégoût',
        'with_admiration': 'avec admiration',
        'with_distrust': 'avec méfiance',
        'with_confidence': 'avec confiance',
        'with_despair': 'avec désespoir',
        'with_euphoria': 'avec euphorie',
        'with_sadness': 'avec tristesse',
        'with_satisfaction': 'avec satisfaction',

        # Weight annotations
        'fundamental': '(fondamental)',
        'important': '(important)',
        'minor': '(mineur)',

        # Narrative context
        'as_belief': 'en tant que croyance',
        'as_pattern': 'comme schéma',
        'secretly': 'secrètement',
        'mechanically': 'mécaniquement',
        'in_memory': 'en souvenir',
        'prophetically': 'prophétiquement',

        # Node synthesis
        'intensely_present': 'intensément présent',
        'very_active': 'très actif',
        'withdrawn': 'en retrait',
        'central': '(central)',
        'charged': 'charged',
        'calm': 'calme',
        'burning': 'brûlant(e)',
        'dormant': 'dormant(e)',
        'incandescent': 'incandescent(e)',
        'active': 'actif/ve',
        'latent': 'latent(e)',
        'in_progress': '(en cours)',
        'completed': '(accompli)',
        'possible': '(possible)',

        # Connectors
        'and': 'et',
        'with': 'avec',

        # Temporal modifiers
        'just_now': "à l'instant",
        'recently': 'récemment',
        'today': "aujourd'hui",
        'this_week': 'cette semaine',
        'long_ago': 'depuis longtemps',
        'newly': 'nouvellement',
        'freshly': 'fraîchement',
        'anciently': 'anciennement',
        'timelessly': 'depuis toujours',
        'briefly': 'brièvement',
        'prolongedly': 'longuement',
        'extensively': 'extensivement',
        'ongoing': '(en cours)',
        'pending': '(en attente)',
        'stale': '(non visité depuis mise à jour)',
        'well_trodden': '(bien parcouru)',
    }
}

# Intensifier mappings
INTENSIFIERS = {
    'en': {
        'believes_in': ('tends to believe', 'firmly believes'),
        'doubts': ('hesitates about', 'rejects'),
        'contradicts': ('nuances', 'radically contradicts'),
        'confirms': ('supports', 'absolutely confirms'),
        'influences': ('touches', 'dominates'),
        'contains': ('borders', 'imprisons'),
        'shelters': ('welcomes', 'protects'),
        'belongs_to': ('is associated with', 'is inseparable from'),
        'owns': ('has access to', 'holds'),
        'proves': ('suggests', 'demonstrates'),
        'illustrates': ('evokes', 'embodies'),
        'expresses': ('sketches', 'proclaims'),
    },
    'fr': {
        'believes_in': ('tend à croire', 'croit fermement'),
        'doubts': ('hésite sur', 'rejette'),
        'contradicts': ('nuance', 'contredit radicalement'),
        'confirms': ('soutient', 'confirme absolument'),
        'influences': ('effleure', 'domine'),
        'contains': ('touche', 'emprisonne'),
        'shelters': ('welcomes', 'protège'),
        'belongs_to': ('est associé à', 'est indissociable de'),
        'owns': ('dispose de', 'détient'),
        'proves': ('suggère', 'démontre'),
        'illustrates': ('évoque', 'incarne'),
        'expresses': ('esquisse', 'proclame'),
    }
}

# Mutual verb forms for bidirectional links
MUTUAL_FORMS = {
    'en': {
        'influences': 'mutually influence each other',
        'acts_on': 'interact',
        'contradicts': 'contradict each other',
        'supports': 'reinforce each other',
        'linked_to': 'are linked',
        'believes_in': 'mutually validate each other',
    },
    'fr': {
        'influences': "mutually influence each other",
        'acts_on': 'interagissent',
        'contradicts': 'se contredisent',
        'supports': 'se renforcent',
        'linked_to': 'sont liés',
        'believes_in': 'se valident mutuellement',
    }
}


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def generate_synthesis(link, node_a, node_b, lang='en'):
    """Generate link synthesis with all v2.0 features."""
    v = VOCAB[lang]
    pre = []
    post = []

    # === NARRATIVE CONTEXT (if applicable) ===
    ctx = get_narrative_context_modifier(node_b, 'target', lang)
    if ctx:
        pre.append(ctx)

    # === PRE-MODIFIERS ===

    # Energy
    if link.energy > 8.0:
        pre.append(v['intensely'])
    elif link.energy < 0.5:
        pre.append(v['barely'])

    # Surprise-anticipation
    if link.surprise_anticipation > 0.7:
        pre.append(v['suddenly'])
    elif link.surprise_anticipation < -0.7:
        pre.append(v['inevitably'])
    elif link.surprise_anticipation > 0.4:
        pre.append(v['unexpectedly'])
    elif link.surprise_anticipation < -0.4:
        pre.append(v['as_expected'])

    # Permanence
    if link.permanence > 0.8:
        pre.append(v['definitely'])
    elif link.permanence < 0.2:
        pre.append(v['perhaps'])
    elif link.permanence < 0.4:
        pre.append(v['probably'])
    elif link.permanence > 0.6:
        pre.append(v['clearly'])

    # === BASE VERB ===
    verb_key = get_base_verb_key(link.hierarchy, link.polarity)
    verb_key = apply_semantic_override(verb_key, node_a.node_type, node_b.node_type, link)

    # === APPLY INTENSIFIER ===
    intensity = compute_intensity(link)
    verb = apply_intensifier(verb_key, intensity, lang)

    # === POST-MODIFIERS ===

    # Fear-anger
    if link.fear_anger < -0.7:
        post.append(v['with_rage'])
    elif link.fear_anger > 0.7:
        post.append(v['with_terror'])
    elif link.fear_anger < -0.4:
        post.append(v['with_hostility'])
    elif link.fear_anger > 0.4:
        post.append(v['with_apprehension'])

    # Trust-disgust
    if link.trust_disgust < -0.7:
        post.append(v['with_disgust'])
    elif link.trust_disgust > 0.7:
        post.append(v['with_admiration'])
    elif link.trust_disgust < -0.4:
        post.append(v['with_distrust'])
    elif link.trust_disgust > 0.4:
        post.append(v['with_confidence'])

    # Joy-sadness
    if link.joy_sadness < -0.7:
        post.append(v['with_despair'])
    elif link.joy_sadness > 0.7:
        post.append(v['with_euphoria'])
    elif link.joy_sadness < -0.4:
        post.append(v['with_sadness'])
    elif link.joy_sadness > 0.4:
        post.append(v['with_satisfaction'])

    # === ASSEMBLE ===
    pre = pre[:2]
    post = post[:2]

    parts = []
    if pre:
        parts.append(" ".join(pre))
    parts.append(verb)
    if post:
        parts.append(f" {v['and']} ".join(post))

    # Weight annotation
    if link.weight > 5.0:
        parts.append(v['fundamental'])
    elif link.weight < 1.0:
        parts.append(v['minor'])

    return " ".join(parts)


def get_base_verb_key(hierarchy, polarity):
    """Return verb key (language-agnostic)."""
    p0, p1 = polarity

    # Hierarchy-dominant
    if abs(hierarchy) > 0.5:
        if hierarchy < -0.7:
            return 'encompasses'
        elif hierarchy < -0.5:
            return 'contains'
        elif hierarchy > 0.7:
            return 'exemplifies'
        else:
            return 'elaborates'

    # Polarity-dominant
    if p0 > 0.7 and p1 < 0.3:
        return 'acts_on'
    elif p0 > 0.7 and p1 > 0.7:
        return 'interacts_with'
    elif p0 > 0.7:
        return 'influences'
    elif p1 > 0.7 and p0 < 0.3:
        return 'undergoes'
    elif p1 > 0.7:
        return 'receives_from'
    elif p0 < 0.3 and p1 < 0.3:
        return 'coexists_with'
    else:
        return 'linked_to'


def apply_semantic_override(verb_key, type_a, type_b, link):
    """Override generic verb with context-specific verb."""

    # === ACTOR OVERRIDES ===
    if type_a == 'actor':
        if type_b == 'moment':
            if verb_key == 'acts_on':
                return 'expresses'
            if verb_key == 'influences':
                return 'initiates'

        if type_b == 'narrative':
            if link.polarity[0] > 0.7 and link.trust_disgust > 0.5:
                return 'believes_in'
            if link.polarity[0] > 0.7 and link.trust_disgust < -0.5:
                return 'doubts'
            if link.hierarchy > 0.5:
                return 'created'
            if link.hierarchy < -0.5:
                return 'is_defined_by'

        if type_b == 'thing':
            if link.hierarchy < -0.3:
                if link.permanence > 0.8:
                    return 'holds'
                return 'owns'
            if link.polarity[0] > 0.7 and link.polarity[1] < 0.3:
                return 'uses'
            if link.polarity[0] < 0.3 and link.polarity[1] > 0.7:
                return 'depends_on'

        if type_b == 'space':
            if link.polarity[0] > 0.7:
                if link.permanence > 0.8:
                    return 'inhabits'
                return 'occupies'
            if link.polarity[0] < 0.3:
                if link.fear_anger > 0.4:
                    return 'fears'
                return 'flees'
            if link.hierarchy > 0.5:
                return 'dominates'
            if link.hierarchy < -0.5:
                return 'belongs_to'

    # === THING OVERRIDES ===
    if type_a == 'thing':
        if type_b == 'actor':
            if link.hierarchy > 0.3:
                if link.permanence > 0.8:
                    return 'belongs_to'  # "is the property of"
                return 'belongs_to'
            if link.polarity[0] > 0.7:
                return 'serves'

        if type_b == 'narrative':
            if link.permanence > 0.8:
                if link.trust_disgust > 0.5:
                    return 'proves'
                if link.trust_disgust < -0.5:
                    return 'refutes'
            if 0.5 <= link.permanence <= 0.8:
                if link.trust_disgust > 0.3:
                    return 'suggests'
                if link.trust_disgust < -0.3:
                    return 'questions'
            if link.permanence < 0.5:
                return 'evokes'
            if link.hierarchy > 0.5:
                return 'symbolizes'

        if type_b == 'thing':
            if link.hierarchy < -0.5:
                return 'contains'
            if link.hierarchy > 0.5:
                return 'composes'
            if abs(link.polarity[0] - 0.5) < 0.2 and abs(link.polarity[1] - 0.5) < 0.2:
                return 'accompanies'

    # === MOMENT OVERRIDES ===
    if type_a == 'moment':
        if type_b == 'narrative':
            if link.hierarchy > 0.5:
                return 'illustrates'
            if link.permanence > 0.8:
                if link.trust_disgust > 0.5:
                    return 'confirms'
                if link.trust_disgust < -0.5:
                    return 'contradicts'
            if 0.5 <= link.permanence <= 0.8:
                if link.trust_disgust > 0.3:
                    return 'supports'
                if link.trust_disgust < -0.3:
                    return 'questions'
            if link.permanence < 0.5:
                return 'evokes'

        if type_b == 'thing':
            if verb_key == 'acts_on':
                return 'concerns'
            if verb_key == 'influences':
                return 'affects'
            if link.hierarchy > 0.5:
                return 'reveals'
            if link.hierarchy < -0.5:
                return 'implicates'

    # === SPACE OVERRIDES ===
    if type_a == 'space':
        if type_b == 'actor':
            if link.hierarchy < -0.5:
                if link.energy > 6.0:
                    return 'welcomes'
                if link.fear_anger > 0.4:
                    return 'imprisons'
                if link.joy_sadness > 0.4:
                    return 'protects'
                if link.joy_sadness < -0.4:
                    return 'isolates'
                if link.hierarchy < -0.7:
                    return 'shelters'
                return 'contains'

        if type_b == 'thing':
            if link.hierarchy < -0.5:
                if link.permanence > 0.8:
                    return 'encloses'
                if link.permanence < 0.5:
                    return 'exposes'
                if link.hierarchy < -0.7:
                    return 'shelters'
                return 'contains'

    # === NARRATIVE OVERRIDES ===
    if type_a == 'narrative' and type_b == 'narrative':
        if link.trust_disgust < -0.7 and link.permanence > 0.8:
            return 'radically_contradicts'
        if link.trust_disgust < -0.5 and link.permanence > 0.8:
            return 'contradicts'
        if link.trust_disgust < -0.5 and link.permanence < 0.5:
            return 'is_in_tension_with'
        if link.trust_disgust > 0.5 and link.hierarchy > 0.5:
            return 'elaborates'
        if link.trust_disgust > 0.5 and link.hierarchy < -0.5:
            return 'contextualizes'
        if link.hierarchy > 0.7:
            return 'is_mechanism_of'
        if link.hierarchy < -0.7:
            return 'encompasses'

    return verb_key


def compute_intensity(link):
    """Compute intensity for verb intensification."""
    polarity_strength = abs(link.polarity[0] - link.polarity[1])
    return (link.permanence + polarity_strength) / 2


def apply_intensifier(verb_key, intensity, lang='en'):
    """Apply attenuated or intensified verb form."""
    v = VOCAB[lang]
    intensifiers = INTENSIFIERS.get(lang, {})

    if verb_key in intensifiers:
        attenuated, intensified = intensifiers[verb_key]
        if intensity < 0.4:
            return attenuated
        elif intensity > 0.8:
            return intensified

    return v.get(verb_key, verb_key)


def is_bidirectional(link):
    """Check if link has mutual polarity."""
    return abs(link.polarity[0] - link.polarity[1]) < 0.2


def generate_bidirectional_synthesis(link, node_a, node_b, lang='en'):
    """Generate synthesis for bidirectional links."""
    if not is_bidirectional(link):
        return {
            'forward': generate_synthesis(link, node_a, node_b, lang),
            'reverse': None,
            'combined': None
        }

    forward = generate_synthesis(link, node_a, node_b, lang)
    reverse = generate_synthesis(link, node_b, node_a, lang)

    # Get mutual form
    verb_key = get_base_verb_key(link.hierarchy, link.polarity)
    verb_key = apply_semantic_override(verb_key, node_a.node_type, node_b.node_type, link)
    mutual_forms = MUTUAL_FORMS.get(lang, {})
    mutual = mutual_forms.get(verb_key, forward)

    return {
        'forward': forward,
        'reverse': reverse,
        'combined': mutual
    }


def get_narrative_context_modifier(node, position, lang='en'):
    """Get narrative type context modifier."""
    if getattr(node, 'node_type', None) != 'narrative':
        return None

    narrative_type = getattr(node, 'type', None)
    if not narrative_type:
        return None

    v = VOCAB[lang]
    modifiers = {
        'belief': v.get('as_belief'),
        'pattern': v.get('as_pattern'),
        'secret': v.get('secretly'),
        'mechanism': v.get('mechanically'),
        'memory': v.get('in_memory'),
        'prophecy': v.get('prophetically'),
    }

    return modifiers.get(narrative_type)


# =============================================================================
# TEMPORAL MODIFIERS (v2.1)
# =============================================================================

import time

def get_recency_modifier(last_traversed_at_s, lang='en'):
    """Get recency modifier based on last traversal time."""
    if last_traversed_at_s is None:
        return None

    v = VOCAB[lang]
    now = int(time.time())
    elapsed = now - last_traversed_at_s

    if elapsed < 60:
        return v['just_now']
    elif elapsed < 3600:
        return v['recently']
    elif elapsed < 86400:
        return v['today']
    elif elapsed < 604800:
        return v['this_week']
    elif elapsed > 604800:
        return v['long_ago']

    return None


def get_age_modifier(created_at_s, lang='en'):
    """Get age modifier based on creation time."""
    if created_at_s is None:
        return None

    v = VOCAB[lang]
    now = int(time.time())
    age = now - created_at_s

    if age < 3600:
        return v['newly']
    elif age < 86400:
        return v['freshly']
    elif age > 31536000:  # Over a year
        return v['timelessly']
    elif age > 2592000:   # Over a month
        return v['anciently']

    return None


def get_duration_modifier(node, lang='en'):
    """Get duration modifier for Moment nodes."""
    if getattr(node, 'node_type', None) != 'moment':
        return None

    v = VOCAB[lang]

    started_at_s = getattr(node, 'started_at_s', None)
    completed_at_s = getattr(node, 'completed_at_s', None)
    duration_s = getattr(node, 'duration_s', None)

    # Check ongoing/pending status
    if started_at_s is not None and completed_at_s is None:
        return v['ongoing']
    if started_at_s is None:
        return v['pending']

    # Check duration
    if duration_s is not None:
        if duration_s < 60:
            return v['briefly']
        elif duration_s > 86400:
            return v['extensively']
        elif duration_s > 3600:
            return v['prolongedly']

    return None


def get_staleness_modifier(link, lang='en'):
    """Get staleness modifier comparing updated vs traversed times."""
    v = VOCAB[lang]

    updated_at_s = getattr(link, 'updated_at_s', None)
    last_traversed_at_s = getattr(link, 'last_traversed_at_s', None)

    if updated_at_s is None or last_traversed_at_s is None:
        return None

    if last_traversed_at_s < updated_at_s:
        return v['stale']
    elif last_traversed_at_s > updated_at_s + 86400:
        return v['well_trodden']

    return None


def get_temporal_modifier(link_or_node, lang='en'):
    """
    Get the most relevant temporal modifier for a link or node.
    Returns at most one modifier to avoid verbosity.
    Priority: recency > staleness > age > duration
    """
    # Try recency first
    last_traversed = getattr(link_or_node, 'last_traversed_at_s', None)
    recency = get_recency_modifier(last_traversed, lang)
    if recency and last_traversed:
        now = int(time.time())
        if now - last_traversed < 3600:  # Only show if within last hour
            return recency

    # Try staleness for links
    staleness = get_staleness_modifier(link_or_node, lang)
    if staleness:
        return staleness

    # Try age for notably old/new
    created_at = getattr(link_or_node, 'created_at_s', None)
    age = get_age_modifier(created_at, lang)
    if age:
        return age

    # Try duration for moments
    duration = get_duration_modifier(link_or_node, lang)
    if duration:
        return duration

    return None


# =============================================================================
# NODE SYNTHESIS
# =============================================================================

def synthesize_node(node, lang='en'):
    """Generate node synthesis based on type."""
    synthesizers = {
        'actor': synthesize_actor,
        'space': synthesize_space,
        'thing': synthesize_thing,
        'narrative': synthesize_narrative,
        'moment': synthesize_moment,
    }
    synthesizer = synthesizers.get(node.node_type, lambda n, l: n.name)
    return synthesizer(node, lang)


def synthesize_actor(node, lang='en'):
    v = VOCAB[lang]
    parts = [node.name]

    if node.energy > 8.0:
        parts.append(v['intensely_present'])
    elif node.energy > 6.0:
        parts.append(v['very_active'])
    elif node.energy < 1.0:
        parts.append(v['withdrawn'])

    if node.weight > 5.0:
        parts.append(v['central'])
    elif node.weight > 3.0:
        parts.append(v['important'])

    return ", ".join(parts)


def synthesize_space(node, lang='en'):
    v = VOCAB[lang]
    parts = [node.name]

    if node.energy > 6.0:
        parts.append(v['charged'])
    elif node.energy < 2.0:
        parts.append(v['calm'])

    if node.weight > 5.0:
        parts.append(v['central'])
    elif node.weight > 3.0:
        parts.append(v['important'])

    return ", ".join(parts)


def synthesize_thing(node, lang='en'):
    v = VOCAB[lang]
    parts = [node.name]

    if node.energy > 6.0:
        parts.append(v['burning'])
    elif node.energy < 2.0:
        parts.append(v['dormant'])

    if node.weight > 5.0:
        parts.append(v['fundamental'])
    elif node.weight > 3.0:
        parts.append(v['important'])
    elif node.weight < 1.0:
        parts.append(v['minor'])

    return ", ".join(parts)


def synthesize_narrative(node, lang='en'):
    v = VOCAB[lang]
    parts = [node.name]

    if node.energy > 8.0:
        parts.append(v['incandescent'])
    elif node.energy > 6.0:
        parts.append(v['burning'])
    elif node.energy > 4.0:
        parts.append(v['active'])
    elif node.energy < 2.0:
        parts.append(v['latent'])

    if node.weight > 5.0:
        parts.append(v['central'])
    elif node.weight > 3.0:
        parts.append(v['important'])

    return ", ".join(parts)


def synthesize_moment(node, lang='en'):
    v = VOCAB[lang]
    parts = [node.name]

    # Energy state
    if node.energy > 8.0:
        parts.append(v['incandescent'])
    elif node.energy > 6.0:
        parts.append(v['burning'])

    # Duration modifier (for temporal context)
    duration_mod = get_duration_modifier(node, lang)
    if duration_mod:
        parts.append(duration_mod)
    else:
        # Fall back to status if no duration info
        status = getattr(node, 'status', None)
        if status == 'active':
            parts.append(v['in_progress'])
        elif status == 'completed':
            parts.append(v['completed'])
        elif status == 'possible':
            parts.append(v['possible'])

    return ", ".join(parts)


# =============================================================================
# FULL EXPRESSION
# =============================================================================

def generate_full_expression(link, node_a, node_b, lang='en', include_temporal=True):
    """Generate complete: NodeA synthesis → Link synthesis → NodeB synthesis."""
    node_a_syn = synthesize_node(node_a, lang)
    link_syn = generate_synthesis(link, node_a, node_b, lang)
    node_b_syn = synthesize_node(node_b, lang)

    # Optionally add temporal context to link
    if include_temporal:
        temporal = get_temporal_modifier(link, lang)
        if temporal:
            link_syn = f"{link_syn}, {temporal}"

    return {
        'node_a': node_a_syn,
        'link': link_syn,
        'node_b': node_b_syn,
        'full': f"{node_a_syn} → {link_syn} → {node_b_syn}",
        'temporal': get_temporal_modifier(link, lang)
    }


def generate_synthesis_with_temporal(link, node_a, node_b, lang='en'):
    """Generate link synthesis with temporal modifier included."""
    base = generate_synthesis(link, node_a, node_b, lang)
    temporal = get_temporal_modifier(link, lang)

    if temporal:
        return f"{base}, {temporal}"
    return base
```

---

## INVARIANTS

1. Every link has exactly one base verb
2. Pre-modifiers come before verb
3. Post-modifiers come after verb, joined by "and" / "et"
4. Neutral values (-0.4 to +0.4) produce no modifier
5. Max 2 pre-modifiers, max 2 post-modifiers
6. Weight annotation is optional, in parentheses
7. Node type overrides take precedence over generic verbs
8. Intensity modifiers (attenuated/intensified) replace base verb
9. Bidirectional links (|polarity[0] - polarity[1]| < 0.2) use mutual forms
10. Max 1 temporal modifier per synthesis
11. Temporal fields are nullable — absence produces no temporal modifier
12. Duration modifiers apply only to Moment nodes
13. Staleness detection requires both updated_at_s and last_traversed_at_s
