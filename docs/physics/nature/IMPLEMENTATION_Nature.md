# Nature — Implementation

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
VALIDATION:      ./VALIDATION_Nature.md
THIS:            IMPLEMENTATION_Nature.md (you are here)
HEALTH:          ./HEALTH_Nature.md
```

---

## FILE STRUCTURE

```
runtime/physics/
├── nature.py              # Parser and converter
├── nature_physics.yaml    # Physics definitions
└── __init__.py            # Exports nature functions
```

---

## CODE ARCHITECTURE

### nature_physics.yaml

Source of truth for all definitions:

```yaml
# Defaults
defaults:
  hierarchy: 0.0
  polarity: [0.5, 0.5]
  ...

# Verb categories
base_verbs: { ... }
ownership_verbs: { ... }
evidential_verbs: { ... }
spatial_verbs: { ... }
actor_verbs: { ... }
narrative_verbs: { ... }
temporal_verbs: { ... }
grammar_verbs: { ... }

# Modifiers
pre_modifiers: { ... }
post_modifiers: { ... }
weight_annotations: { ... }

# Variations
intensifiers: { ... }
translations: { ... }
```

### nature.py

Pure loader and parser:

| Function | Purpose |
|----------|---------|
| `_load_nature()` | Load YAML (cached) |
| `_get_all_verbs()` | Merge all verb categories |
| `get_defaults()` | Return default floats |
| `get_pre_modifiers()` | Return pre-modifiers |
| `get_post_modifiers()` | Return post-modifiers |
| `parse_nature(str)` | Parse to (pre, verb, post) |
| `nature_to_floats(str)` | Convert to physics dict |
| `parse_with_conflicts(str)` | Convert + track conflicts |
| `get_intensified_verb(verb, intensity)` | Get verb form |
| `translate(term, lang)` | Translate term |
| `get_nature_reference()` | Markdown reference |
| `get_nature_compact()` | Compact dict for tools |
| `reload_nature()` | Clear cache |

### __init__.py

Exports for `from runtime.physics import ...`:

```python
from .nature import (
    nature_to_floats,
    parse_nature,
    parse_with_conflicts,
    get_verb_for_nature,
    get_nature_reference,
    get_nature_compact,
    get_defaults,
    get_pre_modifiers,
    get_post_modifiers,
    get_intensifiers,
    get_intensified_verb,
    select_verb_form,
    translate,
    get_translations,
    reload_nature,
)
```

---

## DATA FLOW

```
                    ┌─────────────────┐
                    │ nature_physics  │
                    │     .yaml       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  _load_nature() │
                    │    (cached)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ get_verbs  │  │ get_mods   │  │ get_trans  │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           └───────┬───────┘               │
                   ▼                       │
          ┌────────────────┐               │
          │  parse_nature  │               │
          └───────┬────────┘               │
                  │                        │
                  ▼                        │
         ┌─────────────────┐               │
         │ nature_to_floats│               │
         └───────┬─────────┘               │
                 │                         │
                 ▼                         ▼
         ┌─────────────┐           ┌─────────────┐
         │ physics dict│           │  translate  │
         └─────────────┘           └─────────────┘
```

---

## DEPENDENCIES

| Dependency | Version | Purpose |
|------------|---------|---------|
| PyYAML | >=6.0 | YAML parsing |
| pathlib | stdlib | File paths |
| typing | stdlib | Type hints |

---

## USAGE EXAMPLES

### Basic Conversion

```python
from runtime.physics import nature_to_floats

floats = nature_to_floats("suddenly proves, with admiration")
print(floats['permanence'])  # 0.9
print(floats['trust_disgust'])  # 0.8
```

### With Conflict Detection

```python
from runtime.physics import parse_with_conflicts

floats, conflicts = parse_with_conflicts("definitely perhaps believes in")
if conflicts:
    print(f"Warning: {len(conflicts)} conflicts detected")
```

### Agent Reference

```python
from runtime.physics import get_nature_reference

# Include in agent prompt
reference = get_nature_reference()
```

### Hot Reload

```python
from runtime.physics import reload_nature

# After editing nature_physics.yaml
reload_nature()
```

---

## EXTENSION POINTS

### Adding a New Verb

1. Edit `nature_physics.yaml`
2. Add to appropriate category
3. Define physics floats and type hints
4. Optionally add intensifier forms
5. Optionally add translations

```yaml
# In grammar_verbs:
my_new_verb:
  permanence: 0.8
  trust_disgust: 0.5
  type_a: actor
  type_b: narrative
```

### Adding a New Modifier

```yaml
# In pre_modifiers:
urgently:
  energy: 8.0

# In post_modifiers:
with reluctance:
  trust_disgust: -0.3
```

No code changes required.
