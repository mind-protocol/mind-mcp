# Nature — Algorithm

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
BEHAVIORS:       ./BEHAVIORS_Nature.md
THIS:            ALGORITHM_Nature.md (you are here)
VALIDATION:      ./VALIDATION_Nature.md
```

---

## CORE ALGORITHM

### 1. Load Definitions

```
ON first_access():
    IF cache IS NULL:
        yaml = READ("nature_physics.yaml")
        cache = PARSE(yaml)
    RETURN cache
```

### 2. Parse Nature String

```
FUNCTION parse_nature(nature_string):
    INPUT: "suddenly proves, with admiration"

    # Step 1: Normalize
    nature = LOWERCASE(TRIM(nature_string))

    # Step 2: Split on comma for post-modifiers
    IF "," IN nature:
        main_part, post_part = SPLIT(nature, ",", limit=1)
        post_modifiers = [TRIM(post_part)]
    ELSE:
        main_part = nature
        post_modifiers = []

    # Step 3: Find verb (longest match first)
    all_verbs = MERGE(base_verbs, ownership_verbs, ..., grammar_verbs)
    SORT(all_verbs, BY=length, ORDER=descending)

    FOR verb IN all_verbs:
        IF verb IN main_part:
            found_verb = verb
            found_pos = POSITION(verb, main_part)
            BREAK

    IF NOT found_verb:
        RETURN ([], main_part, post_modifiers)

    # Step 4: Extract pre-modifiers
    pre_part = main_part[0:found_pos]
    pre_modifiers = []

    FOR mod IN SORTED(pre_modifiers_vocab, BY=length, DESC):
        IF mod IN pre_part:
            APPEND(pre_modifiers, mod)
            pre_part = REMOVE(pre_part, mod)

    RETURN (pre_modifiers, found_verb, post_modifiers)
```

### 3. Convert to Physics

```
FUNCTION nature_to_floats(nature_string):
    (pre_mods, verb, post_mods) = parse_nature(nature_string)

    # Start with defaults
    floats = COPY(defaults)
    conflicts = []

    # Layer 1: Apply verb
    IF verb IN all_verbs:
        FOR key, value IN all_verbs[verb]:
            IF key NOT IN ['type_a', 'type_b']:
                IF floats[key] != defaults[key]:
                    RECORD_CONFLICT(conflicts, key, floats[key], value, verb)
                floats[key] = value

    # Layer 2: Apply pre-modifiers
    FOR mod IN pre_mods:
        IF mod IN pre_modifiers:
            FOR key, value IN pre_modifiers[mod]:
                IF floats[key] != defaults[key]:
                    RECORD_CONFLICT(conflicts, key, floats[key], value, mod)
                floats[key] = value

    # Layer 3: Apply post-modifiers
    FOR mod IN post_mods:
        IF mod IN post_modifiers:
            FOR key, value IN post_modifiers[mod]:
                IF floats[key] != defaults[key]:
                    RECORD_CONFLICT(conflicts, key, floats[key], value, mod)
                floats[key] = value

    # Layer 4: Check weight annotations
    FOR annotation IN weight_annotations:
        IF annotation IN LOWERCASE(nature_string):
            floats['weight'] = weight_annotations[annotation]['weight']

    RETURN (floats, conflicts)
```

### 4. Intensify Verb

```
FUNCTION get_intensified_verb(base_verb, intensity):
    # intensity: -1 (attenuated) to +1 (intensified)

    IF base_verb NOT IN intensifiers:
        RETURN base_verb

    [attenuated, intensified] = intensifiers[base_verb]

    IF intensity < -0.3:
        RETURN attenuated
    ELIF intensity > 0.3:
        RETURN intensified
    ELSE:
        RETURN base_verb
```

### 5. Select Verb Form

```
FUNCTION select_verb_form(base_verb, permanence, energy):
    # Combine permanence and energy into intensity
    energy_norm = MIN(energy, 10) / 10
    intensity = (permanence - 0.5) + (energy_norm - 0.5)

    RETURN get_intensified_verb(base_verb, intensity)
```

---

## DATA STRUCTURES

### Physics Floats

```yaml
defaults:
  hierarchy: 0.0          # -1 (parent) to +1 (child)
  polarity: [0.5, 0.5]    # [source_agency, target_agency]
  permanence: 0.5         # 0 (ephemeral) to 1 (permanent)
  joy_sadness: 0.0        # -1 (sad) to +1 (joy)
  trust_disgust: 0.0      # -1 (disgust) to +1 (trust)
  fear_anger: 0.0         # -1 (anger) to +1 (fear)
  surprise_anticipation: 0.0  # -1 (anticipated) to +1 (surprising)
  energy: null            # 0-10, null = don't override
  weight: null            # Link weight, null = default
```

### Verb Definition

```yaml
proves:
  permanence: 0.9
  trust_disgust: 0.6
  type_a: thing           # Source node type hint
  type_b: narrative       # Target node type hint
```

### Modifier Definition

```yaml
suddenly:
  surprise_anticipation: 0.8

with admiration:
  trust_disgust: 0.8
```

### Intensifier Definition

```yaml
proves: [suggests, demonstrates beyond doubt]
#        ↑ attenuated  ↑ intensified
```

---

## COMPLEXITY

| Operation | Time | Space |
|-----------|------|-------|
| Load YAML | O(n) | O(n) |
| Parse nature | O(v × m) | O(1) |
| Convert to floats | O(m) | O(1) |

Where n = YAML size, v = verb count, m = modifier count
