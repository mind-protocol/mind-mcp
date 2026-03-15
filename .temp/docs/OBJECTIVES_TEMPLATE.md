# OBJECTIVES: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
→ OBJECTIVES (you are here)
  → PATTERNS_{Module_Name}.md
    → BEHAVIORS_{Module_Name}.md
      → ALGORITHM_{Module_Name}.md
        → VALIDATION_{Module_Name}.md
          → IMPLEMENTATION_{Module_Name}.md
            → HEALTH_{Module_Name}.md
              → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

## PRIMARY OBJECTIVES

Ranked by priority. Each objective states WHAT we optimize and WHY it matters.

### O1: {Objective name}

{What this optimizes. Why it matters. What degrades without it.}

### O2: {Objective name}

{What this optimizes. Why it matters. What degrades without it.}

### O3: {Objective name}

{What this optimizes. Why it matters. What degrades without it.}

## NON-OBJECTIVES

What this module explicitly does NOT optimize. Including these prevents scope creep.

- **{Non-objective}** — {Why we exclude it. What handles it instead, if anything.}
- **{Non-objective}** — {Why we exclude it.}

## TRADEOFFS

Canonical decisions for when objectives conflict. These are binding — downstream docs reference them.

| When | Conflicts with | We choose | We accept | Why |
|------|----------------|-----------|-----------|-----|
| {situation} | O1 vs O2 | O1 | {cost of choosing O1} | {reasoning} |
| {situation} | {X} vs {Y} | {X} | {cost} | {reasoning} |

## SUCCESS SIGNALS

Observable indicators that this module is working. Not tests — real-world signals.

After {N} ticks / {N} days / {condition}:

- [ ] {Signal 1: observable behavior or metric}
- [ ] {Signal 2}
- [ ] {Signal 3}

## GRAPH MAPPING

How this module's objectives relate to the schema (schema.yaml v2.2).

| Objective | Node types involved | Link dimensions used | Physics laws depended on |
|-----------|--------------------|-----------------------|--------------------------|
| O1 | {actor, narrative, ...} | {weight, energy, trust, ...} | {L1, L4, L6, ...} |
| O2 | {...} | {...} | {...} |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
