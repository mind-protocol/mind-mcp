# Nature — Behaviors

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Nature.md
THIS:            BEHAVIORS_Nature.md (you are here)
ALGORITHM:       ./ALGORITHM_Nature.md
```

---

## OBSERVABLE BEHAVIORS

### B1: Parse Nature String

**Input:** Nature string like `"suddenly proves, with admiration"`

**Output:** Tuple of (pre_modifiers, verb, post_modifiers)

```python
>>> parse_nature("suddenly proves, with admiration")
(['suddenly'], 'proves', ['with admiration'])

>>> parse_nature("proves")
([], 'proves', [])

>>> parse_nature("unknown verb")
([], 'unknown verb', [])  # Falls through with unknown as "verb"
```

### B2: Convert to Physics Floats

**Input:** Nature string

**Output:** Dict of physics floats

```python
>>> nature_to_floats("proves")
{
    'hierarchy': 0.0,
    'polarity': [0.5, 0.5],
    'permanence': 0.9,      # From 'proves'
    'trust_disgust': 0.6,   # From 'proves'
    'joy_sadness': 0.0,
    'fear_anger': 0.0,
    'surprise_anticipation': 0.0,
    'energy': None,
    'weight': None
}

>>> nature_to_floats("suddenly proves, with admiration")
{
    'permanence': 0.9,
    'trust_disgust': 0.8,           # 0.6 + 'with admiration' override
    'surprise_anticipation': 0.8,   # From 'suddenly'
    ...
}
```

### B3: Detect Conflicts

**Input:** Nature string with contradictory modifiers

**Output:** Floats plus conflict list

```python
>>> floats, conflicts = parse_with_conflicts("definitely perhaps believes in")
>>> conflicts
[{
    'key': 'permanence',
    'previous': 0.9,    # From 'definitely'
    'new': 0.1,         # From 'perhaps'
    'from': 'perhaps'
}]
```

### B4: Extract Verb

**Input:** Nature string

**Output:** Base verb or None

```python
>>> get_verb_for_nature("suddenly proves, with admiration")
'proves'

>>> get_verb_for_nature("random words")
None
```

### B5: Intensify Verb

**Input:** Base verb + intensity (-1 to +1)

**Output:** Attenuated/base/intensified form

```python
>>> get_intensified_verb("proves", -0.5)
'suggests'  # Attenuated

>>> get_intensified_verb("proves", 0.0)
'proves'    # Base

>>> get_intensified_verb("proves", 0.5)
'demonstrates beyond doubt'  # Intensified
```

### B6: Translate

**Input:** Term + language code

**Output:** Translated term

```python
>>> translate("proves", "fr")
'prouve'

>>> translate("suddenly", "fr")
'soudain'
```

### B7: Get Reference

**Input:** None

**Output:** Formatted markdown reference for agents

```python
>>> print(get_nature_reference())
# Nature Reference

Format: `[pre_modifier] verb [, post_modifier]`
...
```

### B8: Hot Reload

**Input:** None (reads from disk)

**Output:** Cache cleared, next call loads fresh

```python
>>> reload_nature()
# nature.yaml re-read on next access
```

---

## EDGE CASES

| Case | Behavior |
|------|----------|
| Empty string | Returns defaults |
| Unknown verb | Returns string as-is in verb position |
| Multiple commas | Only first comma splits post-modifier |
| Verb substring match | Longest match prevents "acts" matching "acts on" |
| Modifier not in vocab | Ignored, no error |
| YAML syntax error | Raises on load |
