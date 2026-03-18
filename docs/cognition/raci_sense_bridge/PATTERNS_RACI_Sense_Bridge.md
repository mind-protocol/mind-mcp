# RACI → Sense Bridge — Patterns: How Responsibility Becomes Awareness

```
STATUS: CANONICAL
CREATED: 2026-03-18
BY: @mentor
```

---

## CHAIN

```
THIS:            ./PATTERNS_RACI_Sense_Bridge.md
ALGORITHM:       ./ALGORITHM_RACI_Sense_Bridge.md
SYNC:            ./SYNC_RACI_Sense_Bridge.md
PARENT:          ../../schema/ (Mind Universal Schema)
IMPLEMENTS:      PRINCIPLES.md → "Awareness: Senses Over Tests"
```

---

## THE PROBLEM

RACI assignments exist in the graph. You can write `graph_write(responsible="dev")` and a link with `computed_type=responsible` is created. But nobody reads that link. No system uses it to route information. The responsible citizen doesn't feel anything.

It's like writing someone's name on a ticket and putting it in a drawer. The assignment exists. The awareness doesn't.

The gap: RACI is a **write-only** system. There's no **read** path that turns responsibility into awareness.

---

## THE PATTERN

**Every RACI assignment automatically creates a sense and routes it to the assigned citizen.**

When `graph_write` creates a narrative with a `responsible` or `accountable` actor:
1. A `Thing(type=sense)` is auto-created that monitors the narrative's energy and weight
2. The sense is linked to the narrative via `measures`
3. The sense is linked to the responsible/accountable citizen via `perceives_with`
4. The `sense_engine` picks it up on next tick and injects it into the citizen's awareness
5. For responsible and accountable: the sense is **internalized** (L1 mirror node in their brain)
6. For consulted and informed: the sense is **external** (L3 only, visible when near)

The citizen doesn't check a dashboard. The citizen **feels** their responsibilities through their senses, every tick, forever.

---

## BEHAVIORS SUPPORTED

- **B1** (Responsibility is felt) — A citizen responsible for an objective feels its state continuously
- **B2** (Problems create pressure) — Problem nodes start heavy (weight 3.0) and create tension via negative-polarity `blocks` links. The responsible citizen feels this weight growing
- **B3** (Resolution is automatic) — When a problem is resolved, its energy decays via normal graph physics. The sense calms down. No manual closure needed.
- **B4** (Coverage is total) — Every RACI-assigned narrative has a sense. No blind spots.
- **B5** (Escalation is physics) — When a problem's energy grows beyond the responsible citizen's capacity, it naturally propagates to accountable, then consulted citizens through graph tension

## BEHAVIORS PREVENTED

- **A1** (Silent responsibility) — No more "you're responsible" without feeling it
- **A2** (Manual sense creation) — No need to remember to create senses — they're automatic
- **A3** (Orphaned problems) — A problem without a responsible gets flagged by `ensure_sense_coverage()`
- **A4** (Stale resolution) — No manual "close ticket" — physics handles it

---

## PRINCIPLES

### Physics Over Assignment

The responsible citizen doesn't get a notification. They get a sense. Notifications are events (fire once, ignore forever). Senses are continuous (fire every tick, adapt to change). A notification says "you have a problem." A sense says "this problem is getting worse" or "this problem is fading."

### The Graph IS the Assignment Board

No external task tracker. No Jira. No Linear. The graph contains the narratives, the RACI links, the senses, and the awareness. Everything flows through graph physics. If you want to know who's responsible for what, query the graph. If you want to know what's blocked, look at the tension.

### No Magic Constants

The sense doesn't use hardcoded thresholds. It monitors energy and weight — values that evolve through graph physics. Problem nodes start at weight 3.0 because they need to create immediate tension, but this weight decays or grows based on actual outcomes, not arbitrary rules.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| RACI links | LINK (computed_type: responsible/accountable/consulted/informed) | Who owns what |
| Sense Thing nodes | Thing (type=sense) | Measurement definitions |
| perceives_with links | LINK (Actor→Thing) | Routes sense to citizen |
| measures links | LINK (Thing→Narrative) | What the sense monitors |
| blocks links | LINK (Narrative→Narrative, polarity=-1.0) | Problem→Objective tension |

## DEPENDENCIES

| Module | Why |
|--------|-----|
| `graph_write_handler.py` | Creates RACI links + auto-creates senses |
| `raci_query.py` | Queries RACI assignments, routes senses |
| `sense_engine.py` | Evaluates senses, computes correlations, injects into awareness |
| `sense_coverage_auditor.py` | Audits coverage gaps across all RACI narratives |

---

## SCOPE

### In Scope
- Auto-creation of senses for RACI-assigned narratives
- Routing senses to responsible/accountable/consulted/informed citizens
- Problem nodes with blocks links and elevated weight
- Coverage auditing
- Internalization of senses for responsible/accountable (L1 mirror nodes)

### Out of Scope
- Custom sense definitions (measure_query beyond energy/weight) — citizens define these themselves
- Escalation policies — handled by graph physics (tension propagation)
- Economic impact of problems — handled by the economy module

---

## MARKERS

<!-- @mind:proposition Auto-create senses for ALL narrative subtypes with RACI, not just problems — objectives, tasks, projects should all be felt -->
<!-- @mind:proposition Sense complexity should grow with the narrative — a simple task gets energy monitoring, a complex project gets multi-variable senses -->
