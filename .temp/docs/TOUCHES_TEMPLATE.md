# TOUCHES: {Concept_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- LAST VERIFIED: YYYY-MM-DD -->

## PURPOSE

Index of where the cross-cutting concept `{Concept_Name}` appears in the system.
This file lives alongside `CONCEPT_{Concept_Name}.md` and maps concept to code.

---

## MODULES THAT IMPLEMENT

| Module | What it does with this concept | Schema types used | Key files |
|--------|-------------------------------|-------------------|-----------|
| {module} | {how it uses the concept} | {node_type, link dimensions, physics laws} | {file paths} |

## INTERFACES

### {Module 1}

**Functions:**
- `{function_name}({params})` — {what it does with this concept}

**Schema operations:**
- Creates: {node_type with type="{value}"}
- Reads: {NodeBase/LinkBase fields}
- Modifies: {fields}

**Relevant docs:**
- `docs/{area}/{module}/PATTERNS_{module}.md`

### {Module 2}

{Same format.}

## DEPENDENCIES

How this concept flows between modules.

```
{module_A} ──[defines]──→ {concept} ──[consumed by]──→ {module_B}
                                    ──[transformed by]──→ {module_C}
```

## INVARIANTS ACROSS MODULES

Cross-module constraints on this concept.

### I1: {Invariant name}

**MUST:** {what must be true across all modules using this concept}
**Schema backing:** {invariant from schema.yaml}
**Modules affected:** {list}

### I2: {Invariant name}

{Same format.}

## CONFLICTS / TENSIONS

Any disagreements between modules on how this concept works.

| Module A | Module B | Tension | Resolution |
|----------|----------|---------|------------|
| {module} | {module} | {what they disagree about} | {how resolved, or `@mind:escalation`} |

## SYNC

- **LAST_VERIFIED:** {YYYY-MM-DD}
- **ALL_MODULES_ALIGNED:** YES / NO
- **CONFLICTS:** {list or "none"}

## WHEN TO UPDATE

- When a module starts using this concept
- When a module changes how it uses this concept
- When dependencies between modules change
- When new interfaces are added that touch this concept
- When schema.yaml changes affect this concept

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
