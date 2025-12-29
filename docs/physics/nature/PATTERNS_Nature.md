# Nature — Patterns

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Nature.md
THIS:            PATTERNS_Nature.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Nature.md
```

---

## DESIGN PHILOSOPHY

### Universal Vocabulary

**One vocabulary for everything.** Same nature string produces same physics floats whether applied to a node or a link.

```
Format: [pre_modifier] verb [, post_modifier]

Examples:
  "proves"                          # Just verb
  "suddenly proves"                 # Pre-modifier + verb
  "proves, with admiration"         # Verb + post-modifier
  "suddenly proves, with admiration" # Full form
```

Applied to:
- **Link:** "Edmund `suddenly proves` his loyalty" → link gets high permanence + surprise
- **Node:** Task with nature `"urgent, with confidence"` → node gets high energy + trust

### Controlled Vocabulary over Free Text

Why structured, not free text?
- Deterministic physics derivation
- No LLM required for parsing
- Consistent behavior across agents
- Same semantics for nodes and links

### Layered Composition

Physics floats accumulate through layers:

```
1. DEFAULTS     → base values (permanence: 0.5, etc.)
2. VERB         → override from verb definition
3. PRE-MODIFIER → override certainty/surprise/energy
4. POST-MODIFIER → override emotion axes
```

Later layers override earlier ones. Conflicts are tracked.

### YAML as Source of Truth

All definitions live in `nature.yaml`:

```yaml
base_verbs:
  proves:
    permanence: 0.9
    trust_disgust: 0.6
    type_a: thing
    type_b: narrative

pre_modifiers:
  suddenly:
    surprise_anticipation: 0.8
```

Python code (`nature.py`) is pure loader/parser. No hardcoded values.

---

## SCOPE

### In Scope

- Verb definitions with physics floats
- Pre-modifiers (before verb)
- Post-modifiers (after comma)
- Type hints (type_a, type_b)
- Intensifiers (attenuated/intensified forms)
- Translations (EN↔FR)
- Weight annotations

### Out of Scope

- Physics simulation (see tick_v1_2.py)
- Synthesis generation (see synthesis.py)
- Link creation (see graph operations)
- Validation enforcement (advisory only)

---

## KEY PATTERNS

### P1: Longest Match First

When parsing, find verbs by longest match to avoid ambiguity:

```python
# "acts on" should match "acts on", not "acts"
for verb in sorted(all_verbs.keys(), key=len, reverse=True):
    if verb in nature_string:
        return verb
```

### P2: Conflict Detection

Track when modifiers override each other:

```python
floats, conflicts = parse_with_conflicts("definitely perhaps believes in")
# conflicts = [{'key': 'permanence', 'previous': 0.9, 'new': 0.1, 'from': 'perhaps'}]
```

### P3: Category Organization

Verbs grouped by semantic domain:

| Category | Domain | Example |
|----------|--------|---------|
| base_verbs | Generic relations | encompasses, contains |
| ownership_verbs | Thing↔Actor | belongs to, owns |
| evidential_verbs | Evidence→Narrative | proves, refutes |
| spatial_verbs | Space↔Actor/Thing | shelters, occupies |
| actor_verbs | Actor→Moment/Narrative | believes in, expresses |
| narrative_verbs | Narrative→Narrative | contradicts, contextualizes |
| temporal_verbs | Moment→Moment | precedes, triggers |
| workflow_verbs | Task/Actor relations | claims, resolves |

### P4: Physics Axes

Eight physics dimensions:

| Axis | Range | Meaning |
|------|-------|---------|
| hierarchy | -1 to +1 | Parent↔child relationship |
| polarity | [0-1, 0-1] | [source_agency, target_agency] |
| permanence | 0 to 1 | How lasting is this relationship |
| joy_sadness | -1 to +1 | Emotional valence |
| trust_disgust | -1 to +1 | Trust dimension |
| fear_anger | -1 to +1 | Fear/anger dimension |
| surprise_anticipation | -1 to +1 | Expectedness |
| energy | 0 to 10 | Activation level |

---

## ANTI-PATTERNS

| Don't | Why | Do Instead |
|-------|-----|------------|
| Hardcode verbs in Python | Violates YAML-as-truth | Add to nature.yaml |
| Parse natural language | Non-deterministic | Use structured format |
| Enforce type constraints | Limits agent flexibility | Advisory hints only |
| Skip conflict detection | Silent overwrites confuse | Always track conflicts |
