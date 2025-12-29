# Nature — Validation

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
ALGORITHM:       ./ALGORITHM_Nature.md
THIS:            VALIDATION_Nature.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Nature.md
```

---

## INVARIANTS

### I1: Deterministic Output

**Statement:** Same nature string always produces same physics floats.

```python
def test_deterministic():
    for _ in range(100):
        floats1 = nature_to_floats("suddenly proves, with admiration")
        floats2 = nature_to_floats("suddenly proves, with admiration")
        assert floats1 == floats2
```

**Severity:** CRITICAL

### I2: Default Completeness

**Statement:** Output always contains all physics keys.

```python
def test_default_completeness():
    REQUIRED_KEYS = {
        'hierarchy', 'polarity', 'permanence',
        'joy_sadness', 'trust_disgust', 'fear_anger',
        'surprise_anticipation', 'energy', 'weight'
    }

    floats = nature_to_floats("any string")
    assert set(floats.keys()) == REQUIRED_KEYS
```

**Severity:** CRITICAL

### I3: Range Constraints

**Statement:** Physics values stay within valid ranges.

```python
def test_range_constraints():
    for nature in all_possible_natures():
        floats = nature_to_floats(nature)

        assert -1 <= floats['hierarchy'] <= 1
        assert 0 <= floats['polarity'][0] <= 1
        assert 0 <= floats['polarity'][1] <= 1
        assert 0 <= floats['permanence'] <= 1
        assert -1 <= floats['joy_sadness'] <= 1
        assert -1 <= floats['trust_disgust'] <= 1
        assert -1 <= floats['fear_anger'] <= 1
        assert -1 <= floats['surprise_anticipation'] <= 1
        assert floats['energy'] is None or 0 <= floats['energy'] <= 10
```

**Severity:** CRITICAL

### I4: Conflict Tracking

**Statement:** When modifiers override values, conflicts are recorded.

```python
def test_conflict_tracking():
    floats, conflicts = parse_with_conflicts("definitely perhaps proves")

    # 'definitely' sets permanence=0.9, 'perhaps' overrides to 0.1
    assert len(conflicts) >= 1
    assert any(c['key'] == 'permanence' for c in conflicts)
```

**Severity:** HIGH

### I5: Longest Match

**Statement:** Multi-word verbs match before single-word substrings.

```python
def test_longest_match():
    # "acts on" should not match just "acts"
    pre, verb, post = parse_nature("acts on something")
    assert verb == "acts on"

    # "is linked to" should not match just "is"
    pre, verb, post = parse_nature("is linked to")
    assert verb == "is linked to"
```

**Severity:** HIGH

### I6: Case Insensitivity

**Statement:** Nature parsing is case-insensitive.

```python
def test_case_insensitive():
    assert nature_to_floats("PROVES") == nature_to_floats("proves")
    assert nature_to_floats("Suddenly Proves") == nature_to_floats("suddenly proves")
```

**Severity:** MEDIUM

### I7: YAML Consistency

**Statement:** All verbs in YAML have valid physics keys.

```python
def test_yaml_consistency():
    VALID_KEYS = {
        'hierarchy', 'polarity', 'permanence',
        'joy_sadness', 'trust_disgust', 'fear_anger',
        'surprise_anticipation', 'energy', 'weight',
        'type_a', 'type_b'
    }

    for category in ['base_verbs', 'ownership_verbs', ...]:
        for verb, props in yaml[category].items():
            for key in props.keys():
                assert key in VALID_KEYS, f"{verb} has invalid key {key}"
```

**Severity:** HIGH

---

## TEST COVERAGE

| Invariant | Unit Test | Integration Test |
|-----------|-----------|------------------|
| I1: Determinism | ✓ | ✓ |
| I2: Completeness | ✓ | — |
| I3: Ranges | ✓ | — |
| I4: Conflicts | ✓ | — |
| I5: Longest Match | ✓ | — |
| I6: Case Insensitive | ✓ | — |
| I7: YAML Valid | ✓ | — |

---

## EDGE CASE TESTS

```python
def test_empty_string():
    floats = nature_to_floats("")
    assert floats == get_defaults()

def test_unknown_verb():
    pre, verb, post = parse_nature("xyzzy")
    assert verb == "xyzzy"
    assert pre == []
    assert post == []

def test_only_modifiers():
    # No valid verb, modifiers ignored
    floats = nature_to_floats("suddenly")
    assert floats['surprise_anticipation'] == 0.0  # Modifier not applied without verb

def test_multiple_commas():
    pre, verb, post = parse_nature("proves, with admiration, extra")
    assert post == ["with admiration, extra"]  # Only first comma splits
```
