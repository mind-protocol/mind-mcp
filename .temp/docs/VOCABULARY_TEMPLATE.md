# VOCABULARY: {Module_Name}

<!-- STATUS: PROPOSED (not yet merged to TAXONOMY/MAPPING) -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
→     VOCABULARY (you are here — between PATTERNS and BEHAVIORS)
        → BEHAVIORS_{Module_Name}.md

Merge targets:
  docs/TAXONOMY.md — term definitions
  docs/MAPPING.md — schema translations
```

---

## PURPOSE

New terms introduced by this module. Each term must eventually be:
1. Validated against schema.yaml v2.2
2. Merged to `docs/TAXONOMY.md` (definition)
3. Merged to `docs/MAPPING.md` (schema translation)

## NEW TERMS

### {term_id}

- **Definition:** {clear, precise definition}
- **Properties:** {key characteristics}
- **_meta:**
  - abstraction_level: {1=substrate, 2=structural, 3=dynamic, 4=phenomenal, 5=relational}
  - literature_status: {L1_established, L2_fuzzy, L3_popular, L4_novel}
  - importance: {1-5}
  - confidence: {0-100%}
  - precision: {0-100%}
- **Related terms:** {links to other terms}
- **Schema mapping:**
  - node_type: {actor / moment / narrative / space / thing}
  - cognitive_type: {memory / concept / narrative / value / process / desire / state — or N/A if not L1}
  - type_field: {string value for the `type` field, or null}
  - synthesis_template: "{how to generate synthesis from this term's content}"
  - content_includes: {what goes in the `content` field}
  - relevant_link_dimensions: {which LinkBase dimensions this term typically uses}

### {term_id_2}

{Same format.}

## NEW RELATIONSHIPS

### {relationship_name}

- **Definition:** {what this relationship means}
- **Between:** {source_term} → {target_term}
- **Schema mapping:**
  - relation_kind: {one of 14 L1 kinds, or null for L3}
  - polarity: [{a→b}, {b→a}]
  - hierarchy: {-1 to +1}
  - permanence: {0 to 1}
  - key_dimensions: {which of trust/friction/affinity/aversion are primary}

## TASKS

### TASK_{task_name}

- **Definition:** {outcome, not process}
- **Executor:** {agent / automated / mechanical}
- **SKILL:** {SKILL_name if agent-executed}
- **Schema:** narrative node with type: "task"

## ACTORS

### ACTOR_{actor_name}

- **Subtype:** {mechanical / agent}
- **Purpose:** {role in system}
- **Capabilities:** [{TASK_1}, {TASK_2}]
- **Triggers:** {cron / event / manual}
- **Schema:** actor node with type: "{subtype}"

## PROBLEMS

Abnormal situations detected by HEALTH and resolved by tasks.

### PROBLEM_{problem_name}

- **Definition:** {abnormal situation — what's wrong}
- **Severity:** {critical / warning / info}
- **Resolves with:** TASK_{name}
- **Detection hint:** {which HEALTH indicator or graph query catches this}
- **Schema signal:** {which NodeBase/LinkBase/drive fields indicate this problem}

## TERMINOLOGY PROPOSALS

Changes to existing terms in TAXONOMY.

| Propose | Instead of | Reason |
|---------|-----------|--------|
| {new term} | {old term} | {why the change — precision, alignment with schema, etc.} |

## MERGE STATUS

- [ ] Terms reviewed against schema.yaml v2.2
- [ ] Schema mappings validated (node_type, cognitive_type, type_field)
- [ ] Link dimension mappings validated
- [ ] Merged to TAXONOMY.md
- [ ] Merged to MAPPING.md

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
