# TAXONOMY: {Project_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- CREATED: YYYY-MM-DD -->
<!-- UPDATED: YYYY-MM-DD -->

## PURPOSE

Central vocabulary for the entire project. All modules reference this.
New terms are proposed in module `VOCABULARY.md` files, then merged here after validation.

Every term must be traceable to the schema (schema.yaml v2.2).

---

## TERMS

### {term_id}

- **Definition:** {clear, precise definition}
- **Properties:** {key characteristics}
- **_meta:**
  - abstraction_level: {1=substrate, 2=structural, 3=dynamic, 4=phenomenal, 5=relational}
  - literature_status: {L1_established, L2_fuzzy, L3_popular, L4_novel}
  - importance: {1-5}
  - confidence: {0-100%}
  - precision: {0-100%}
- **Related terms:** {links to other terms in this taxonomy}
- **Schema anchor:** {node_type / cognitive_type / link dimension / physics law — what this term maps to in schema.yaml}
- **_comments:** {gaps, uncertainties, open questions}

### {term_id_2}

{Same format.}

## TERMINOLOGY DECISIONS

| We use | Not | Reason |
|--------|-----|--------|
| {preferred term} | {rejected alternative} | {why — precision, schema alignment, existing usage} |

## META-ATTRIBUTE DEFINITIONS

### Abstraction levels

| Level | Name | Description | Schema layer |
|-------|------|-------------|-------------|
| 1 | Substrate | Physical implementation | NodeBase/LinkBase fields |
| 2 | Structural | Architectural patterns | Node types, link dimensions |
| 3 | Dynamic | Runtime processes | Physics laws L1–L21 |
| 4 | Phenomenal | Emergent properties | Drive system, working memory |
| 5 | Relational | Inter-entity meaning | Trust, affinity, L3 universe |

### Literature status

| Status | Meaning |
|--------|---------|
| L1_established | Well-defined in literature, consensus exists |
| L2_fuzzy | Known concept, definitions vary |
| L3_popular | Widely used, often misused |
| L4_novel | New to this project, no prior literature |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
