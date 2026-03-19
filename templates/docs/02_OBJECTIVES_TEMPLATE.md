# OBJECTIVES — {Module}

```
STATUS: DRAFT | REVIEW | STABLE
CREATED: {DATE}
VERIFIED: {DATE} against {COMMIT}
```

---

## CHAIN

```
THIS:            OBJECTIVES_*.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_*.md
BEHAVIORS:      ./BEHAVIORS_*.md
ALGORITHM:      ./ALGORITHM_*.md
VALIDATION:     ./VALIDATION_*.md
IMPLEMENTATION: ./IMPLEMENTATION_*.md
SYNC:           ./SYNC_*.md

IMPL:           {path/to/main/source/file.py}
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)
1. {Objective} — {why it matters}
2. {Objective} — {why it matters}
3. {Objective} — {why it matters}

## NON-OBJECTIVES
- {What we explicitly do NOT optimize}
- {What this module will not attempt}

## TRADEOFFS (canonical decisions)
- When {X} conflicts with {Y}, choose {X}.
- We accept {cost} to preserve {value}.

## SUCCESS SIGNALS (observable)
- {metric/behavior}
- {metric/behavior}

## RESULTS REQUIRED

**Every objective MUST be provable by at least one RESULT in RESULTS_{name}.md.**
**Every result MUST be measured by a SENSE and verified by a HEALTH signal.**

This is non-negotiable. An objective without a result is a wish. A result without a sense is a promise. A sense without health verification is a lie. See RESULTS_{name}.md for the full guarantee loop.
