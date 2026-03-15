# Graph — Behaviors: What Should Happen

```
CREATED: 2024-12-16
STATUS: Canonical
```

---

## CHAIN

```
PATTERNS:   ./PATTERNS_Graph.md
THIS:       BEHAVIORS_Graph.md
ALGORITHM:  ../ALGORITHM_Physics.md
VALIDATION: ./VALIDATION_Living_Graph.md
SYNC:       ./SYNC_Graph.md
```

---

## Overview

The graph exhibits five observable behaviors:

| Behavior | What You See |
|----------|--------------|
| Energy Flow | Companions' narratives stay hot; distant lords' narratives go cold |
| Propagation | Related narratives heat up together; contradictions both intensify |
| Decay | Unattended narratives fade; core oaths persist |
| Pressure | Pressure builds toward breaking; some scheduled, some gradual |
| Flips | Things break; consequences cascade |

---

## BEHAVIORS

These behaviors describe what the graph physics layer makes observable to
players and agents, independent of UI framing, across ticks and flips.

---

## Behavior: Companions Matter More

**Expected:** Narratives about nearby characters stay energized. Distant characters fade.

| Situation | Expected Behavior |
|-----------|-------------------|
| Aldric travels with you | His narratives are always hot |
| Edmund is in York (one day away) | His narratives simmer, don't dominate |
| Edmund approaches | His narratives heat up automatically |
| You arrive in York | Edmund's narratives spike — confrontation imminent |

**Why:** Character energy = relationship × proximity. Approach changes proximity. Energy follows.

**Emergent:** Travel toward an enemy creates pressure automatically. No one decided this.

---

## Behavior: Contradictions Intensify Together

**Expected:** When two narratives contradict, both heat up. Arguments need two hot takes.

| Example | Expected Behavior |
|---------|-------------------|
| "Edmund betrayed me" vs "Edmund was forced" | Both gain energy together |
| Player attends to one side | Other side also rises |
| Resolution | One supersedes the other; loser fades |

**Why:** Contradiction links are bidirectional. Energy flows both ways.

**Emergent:** You can't think about a debate without both sides coming alive.

---

## Behavior: Support Clusters Rise and Fall Together

**Expected:** Allied narratives share fate. Doubt one, doubt them all.

| Example | Expected Behavior |
|---------|-------------------|
| "Aldric is loyal" + "The Oath" + "Aldric saved my life" | All rise together |
| One is weakened | Whole cluster cools |
| One is strengthened | Whole cluster heats |

**Why:** Support links transfer energy bidirectionally.

**Emergent:** Loyalty is a web. Betrayal poisons the whole structure.

---

## Behavior: Old Truths Fade When Replaced

**Expected:** When new information supersedes old, the old narrative loses energy.

| Example | Expected Behavior |
|---------|-------------------|
| "Edmund is in York" → "Edmund fled York" | Old narrative fades |
| "Edmund is my enemy" → "Edmund is dead" | Old narrative loses relevance |

**Why:** Supersession links drain energy from source to target.

**Emergent:** The world updates naturally. Outdated beliefs don't linger.

---

## Behavior: Core Oaths Persist

**Expected:** Oaths, blood debts, and fundamental bonds resist decay.

| Narrative Type | Expected Decay |
|----------------|----------------|
| Casual rumor | Fades quickly if not reinforced |
| Witnessed event | Moderate persistence |
| Oath, blood, debt | Very slow decay |

**Why:** Core narrative types have 0.25x decay rate.

**Emergent:** Some things are never forgotten. The ledger persists.

---

## Behavior: Pressure Builds Toward Breaking

**Expected:** Pressure accumulates until something breaks.

### Gradual Pressure

| Situation | Expected Behavior |
|-----------|-------------------|
| Aldric's loyalty questioned | Pressure rises slowly each tick |
| Time passes without resolution | Pressure continues building |
| Reaches threshold | Flip — something happens |

### Scheduled Pressure

| Situation | Expected Behavior |
|-----------|-------------------|
| Knight arriving on Day 14 | Pressure follows timeline |
| Day 12 | Low pressure — "days away" |
| Day 13 | Moderate — "tomorrow" |
| Day 14 dawn | High — "today" |
| Day 14 noon | Maximum — breaks if not resolved |

**Why:** Scheduled pressure creates deadlines you can feel.

**Emergent:** "Three days away" feels distant. "Tomorrow" feels immediate.

---

## Behavior: Cascades Ripple Through

**Expected:** One break can trigger others. Consequences compound.

| Example | Expected Cascade |
|---------|------------------|
| Edmund loses Malet's favor | Creates "Edmund is vulnerable" |
| Rolf sees opportunity | Pushes Rolf's vengeance pressure over threshold |
| Rolf acts | Second break — confrontation |

**Why:** New narratives from breaks inject energy. Energy propagates. Thresholds crossed.

**Limit:** Maximum 5 cascades before pause. Let Narrator present what happened.

---

## Behavior: System Stays Near Criticality

**Expected:** Always some pressure hot. Always some breaks possible. Not boring. Not chaotic.

| Measure | Healthy Range |
|---------|---------------|
| Average pressure | 0.4 - 0.6 |
| Hot pressure points (>0.7) | At least one |
| Breaks per game-hour | 0.5 - 2.0 |

**If too cold:** Decay slows. System heats up.
**If too hot:** Decay speeds up. System cools down.

**Emergent:** The story maintains pressure without intervention.

---

## Behavior: Agents Update Links, Not Energy

**Expected:** Narrator and World Runner change the structure. Energy follows automatically.

### Narrator Updates Links When:

| Trigger | What Changes |
|---------|--------------|
| Player clicks word | Player's belief in that narrative strengthens |
| Discovery in generation | New narrative created; believers established |

### World Runner Updates Links When:

| Trigger | What Changes |
|---------|--------------|
| Pressure breaks | New narrative created; witnesses believe it |
| News travels | Character gains belief link |
| Character moves | Proximity changes; energy follows next tick |

**Never:** Agents set energy directly. Energy is computed, not declared.

---

## Summary: What To Expect

1. **Nearby companions dominate** — their narratives stay hot
2. **Approach creates pressure** — proximity change = energy change
3. **Contradictions heat together** — debates are bidirectional
4. **Clusters share fate** — doubt one, doubt all
5. **Old truths fade** — supersession drains the original
6. **Core bonds persist** — oaths resist decay
7. **Pressure builds to breaking** — gradual or scheduled
8. **Breaks cascade** — consequences compound
9. **System self-regulates** — stays near criticality
10. **Structure creates energy** — no injection, just physics

---

## INPUTS / OUTPUTS

**Inputs:** graph topology, link strengths, proximity updates, pressure
schedules, tick cadence, and newly created narratives from handlers.

**Outputs:** updated energy/pressure levels, flip events, cascade-triggered
narratives, and graph state changes that surface as new moments.

**Note:** The query helpers briefly bump the retrieved node’s stored `energy`
by a small increment (≈0.05) so the field always reflects the most recent
views without making agents responsible for writing in new values.

---

## EDGE CASES

- **Isolated nodes:** lone narratives with no links should decay gracefully
  rather than oscillating or receiving phantom energy.
- **Dense cycles:** highly connected clusters must avoid runaway energy loops;
  decay and normalization prevent infinite amplification.
- **Simultaneous flips:** when multiple tensions cross threshold in one tick,
  order cascades deterministically to avoid inconsistent narrative forks.

---

## ANTI-BEHAVIORS

- **No manual energy injection:** agents must never set energy directly;
  energy is computed from structure and decay rules.
- **No infinite cascades:** a hard cap prevents an endless flip storm from
  starving the narrator of a stable presentation window.
- **No orphaned pressure:** pressure cannot build without a possible release;
  unresolved tensions must either flip or decay.

---

## MARKERS

<!-- @mind:escalation
title: "How should energy routing behave when a nearby character is incapacitated but still linked by proximity?"
priority: 5
response:
  status: resolved
  choice: "Contradicts links block actions, energy still routes"
  behavior: "Incapacitated character gets contradicts links to action potentials. Energy still flows through them (they're present, witnessed). They cannot respond but absorb focus. See also: BEHAVIORS_Physics_Behaviors_Advanced.md for sleep/unconscious."
  notes: "2025-12-23: Resolved by Nicolas."
-->
<!-- @mind:escalation
title: "What normalization strategy best prevents dense clusters from drowning out sparse but high-stakes narratives?"
priority: 5
response:
  status: resolved
  choice: "Handled by existing weight/decay mechanics"
  behavior: |
    No special normalization needed. Existing mechanisms solve this:
    - Node weight (unbounded): high-stakes nodes get high weight → high inertia → retain energy
    - Link weight: oath links 0.9, gossip links 0.3 → energy flows where it matters
    - Decay: dense clusters have more surface area → dissipate faster
    - Sparse high-stakes: few links + high weight = energy stays concentrated
  notes: "2025-12-23: Resolved by Nicolas. Weight already handles this."
-->
<!-- @mind:proposition Add a diagnostic view that highlights the top three pressure drivers -->
  during each tick for debugging and balancing.

---

*"The story emerges from structure."*
