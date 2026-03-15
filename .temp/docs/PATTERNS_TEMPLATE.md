# PATTERNS: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
→ PATTERNS (you are here)
  → BEHAVIORS_{Module_Name}.md
    → ALGORITHM_{Module_Name}.md
      → VALIDATION_{Module_Name}.md
        → IMPLEMENTATION_{Module_Name}.md
          → HEALTH_{Module_Name}.md
            → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

### Bidirectional Contract

- **Before modifying this doc:** read OBJECTIVES (upstream) AND ALGORITHM (downstream).
- **Before modifying code:** read this doc AND IMPLEMENTATION.
- **After modifying this doc:** update IMPLEMENTATION or add `@mind:TODO` to SYNC.
- **After modifying code:** update this doc or add `@mind:TODO` to SYNC.

---

## THE PROBLEM

{What does this module solve? What goes wrong without it? What pain does it address?}

## THE PATTERN

{Core design approach. The key insight that makes it work.}

### Key insight

{One paragraph. The single idea that, if you understand it, everything else follows.}

## SCHEMA ALIGNMENT

How this module maps to the canonical schema (schema.yaml v2.2).

### Node types used

| Schema type | Cognitive type (if L1) | Role in this module | Example |
|-------------|----------------------|---------------------|---------|
| {actor/moment/narrative/space/thing} | {memory/concept/narrative/value/process/desire/state or N/A} | {what this node represents here} | {concrete example} |

### Link dimensions relied on

| Dimension | Range | How this module uses it | Physics law |
|-----------|-------|-------------------------|-------------|
| {weight/energy/trust/friction/affinity/...} | {[0,∞] / [0,1] / [-1,+1]} | {specific usage} | {L1-L21} |

### Layer separation

- **L1 (Brain):** {what this module does in the citizen's private graph, if anything}
- **L3 (Universe):** {what this module does in the shared universe graph, if anything}
- **Cross-layer:** {any L1↔L3 interactions via Law 21 or membrane}

## BEHAVIORS SUPPORTED

Which behaviors from BEHAVIORS doc this pattern enables.

| Behavior | How this pattern enables it |
|----------|---------------------------|
| B{N}: {name} | {mechanism} |

## BEHAVIORS PREVENTED

Anti-behaviors this pattern structurally blocks.

| Anti-behavior | How this pattern prevents it |
|---------------|----------------------------|
| A{N}: {name} | {mechanism} |

## PRINCIPLES

Design rules this module follows. Each must have a WHY.

### P1: {Principle name}

{Description.}

**Why:** {Consequence if violated.}

### P2: {Principle name}

{Description.}

**Why:** {Consequence if violated.}

### P3: {Principle name}

{Description.}

**Why:** {Consequence if violated.}

## PHYSICS LAWS USED

Which of the 21 laws this module depends on.

| Law | Name | Role in this module | Essential vs enrichment |
|-----|------|---------------------|------------------------|
| L{N} | {name} | {how this module uses it} | {essential / enrichment / deferred} |

## DATA

Sources of truth.

| Source | Location | What it provides |
|--------|----------|-----------------|
| {name} | {file path or URL} | {what data} |

## DEPENDENCIES

| Module | Why we depend on it |
|--------|---------------------|
| {module} | {what it provides to us} |

## INSPIRATIONS

| Source | What we took from it |
|--------|---------------------|
| {paper, pattern, system} | {specific insight} |

## SCOPE

### In scope

- {Responsibility 1}
- {Responsibility 2}

### Out of scope

- {Exclusion 1} — {why, and what handles it}
- {Exclusion 2}

### Limitations

- {Known limitation 1}
- {Known limitation 2}

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
