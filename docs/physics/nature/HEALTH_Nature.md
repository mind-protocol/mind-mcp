# Nature — Health

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
IMPLEMENTATION:  ./IMPLEMENTATION_Nature.md
THIS:            HEALTH_Nature.md (you are here)
SYNC:            ./SYNC_Nature.md
```

---

## PURPOSE

Health indicators for the nature system. Monitors YAML validity, parsing correctness, and cache behavior.

---

## INDICATORS

### H1: YAML Load Health

```yaml
name: YAML Load Health
priority: critical
rationale: System cannot function without valid definitions

mechanism: |
  Try to load nature_physics.yaml
  If parse error: critical
  If file missing: critical
  If loaded successfully: healthy

signals:
  healthy: YAML loads without error
  critical: YAML parse error or file missing

detection: on_startup, on_reload
```

### H2: Verb Coverage

```yaml
name: Verb Coverage
priority: high
rationale: All node type pairs should have relationship verbs

mechanism: |
  Check verb definitions cover:
  - actor → narrative
  - actor → moment
  - thing → narrative
  - space → actor
  - moment → moment
  - narrative → narrative

  Missing combinations = degraded

signals:
  healthy: All major type pairs covered
  degraded: Some type pairs missing verbs
  critical: (Not applicable)

detection: on_startup
```

### H3: Translation Completeness

```yaml
name: Translation Completeness
priority: medium
rationale: Multilingual support requires complete translations

mechanism: |
  For each verb in all_verbs:
    Check if translation exists for each language

  Missing translations = degraded

signals:
  healthy: All verbs have translations
  degraded: Some verbs missing translations
  critical: (Not applicable)

detection: on_startup
```

### H4: Cache Validity

```yaml
name: Cache Validity
priority: medium
rationale: Stale cache causes unexpected behavior

mechanism: |
  Compare cache timestamp to file modification time
  If file newer than cache: degraded
  (User should call reload_nature())

signals:
  healthy: Cache matches file or no cache
  degraded: File modified since cache load
  critical: (Not applicable)

detection: on_access (lazy check)
```

### H5: Parse Success Rate

```yaml
name: Parse Success Rate
priority: high
rationale: Nature strings should parse to valid physics

mechanism: |
  Track parse_nature() calls
  Count: total, found_verb, unknown_verb

  unknown_verb / total > 10% = degraded

signals:
  healthy: >90% strings have recognized verbs
  degraded: 70-90% recognition rate
  critical: <70% recognition rate

detection: runtime_sampling
```

---

## HEALTH CHECK IMPLEMENTATION

```python
def check_nature_health() -> dict:
    """Run all health checks for nature system."""
    results = {
        'status': 'healthy',
        'checks': {}
    }

    # H1: YAML Load
    try:
        _load_nature()
        results['checks']['yaml_load'] = 'healthy'
    except Exception as e:
        results['checks']['yaml_load'] = f'critical: {e}'
        results['status'] = 'critical'
        return results

    # H2: Verb Coverage
    all_verbs = _get_all_verbs()
    required_pairs = [
        ('actor', 'narrative'),
        ('thing', 'narrative'),
        ('moment', 'moment'),
    ]
    missing = []
    for type_a, type_b in required_pairs:
        found = any(
            v.get('type_a') == type_a and v.get('type_b') == type_b
            for v in all_verbs.values()
        )
        if not found:
            missing.append(f"{type_a}→{type_b}")

    if missing:
        results['checks']['verb_coverage'] = f'degraded: missing {missing}'
        if results['status'] == 'healthy':
            results['status'] = 'degraded'
    else:
        results['checks']['verb_coverage'] = 'healthy'

    # H3: Translation Completeness
    translations = _load_nature().get('translations', {})
    all_terms = list(all_verbs.keys())
    for lang in ['en', 'fr']:
        lang_trans = translations.get(lang, {})
        missing_trans = [t for t in all_terms if t not in lang_trans]
        if missing_trans:
            results['checks'][f'translations_{lang}'] = f'degraded: {len(missing_trans)} missing'
        else:
            results['checks'][f'translations_{lang}'] = 'healthy'

    return results
```

---

## GAPS

| Gap | Risk | Mitigation |
|-----|------|------------|
| No runtime parse tracking | Can't detect low recognition rates | Sample logging |
| No cache timestamp check | Stale cache undetected | Document reload_nature() |
| No YAML schema validation | Invalid structure undetected | Startup checks |
