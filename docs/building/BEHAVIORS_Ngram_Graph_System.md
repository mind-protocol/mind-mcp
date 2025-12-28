# mind Graph System — Behaviors: Observable Value

```
STATUS: DESIGNING
CREATED: 2024-12-23
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_Mind_Graph_System.md
PATTERNS:       ./PATTERNS_Mind_Graph_System.md
THIS:           BEHAVIORS_Mind_Graph_System.md (you are here)
ALGORITHM:      ./ALGORITHM_Mind_Graph_System.md
VALIDATION:     ./VALIDATION_Mind_Graph_System.md
IMPLEMENTATION: ./IMPLEMENTATION_Mind_Graph_System.md
HEALTH:         ./HEALTH_Mind_Graph_System.md
SYNC:           ./SYNC_Mind_Graph_System.md
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC.

---

## Why This Matters

These are the outcomes we care about. The value the system produces. Not how it works — what it delivers.

---

## BEHAVIORS

### B1: Agent Produces Useful Work Without Explicit Instruction

**Objective:** Graph runs the dev process.

**Why:** No task assignment. No orchestration layer. Agent receives context, does work. The graph decides what's relevant through physics.

```
GIVEN:  Agent in a Space with hot Narratives
WHEN:   Agent triggered
THEN:   Agent produces work that addresses those Narratives
AND:    Work is coherent with context
AND:    No human had to specify what to do
```

---

### B2: Relevant Context Surfaces, Noise Doesn't

**Objective:** Agents receive context from graph.

**Why:** Context quality determines work quality. Hot Narratives surface. Cold ones don't clutter. Agent sees what matters now.

```
GIVEN:  Space has many Narratives
WHEN:   Actor enters Space
THEN:   Only hot Narratives appear in context
AND:    Cold Narratives stay dormant
AND:    Context is focused, not overwhelming
```

---

### B3: Goals Complete Naturally Through Physics

**Objective:** Memory through strength.

**Why:** No explicit "mark done." Energy decays as goal is addressed. Goal goes cold. Feels complete. No ceremony required.

```
GIVEN:  Goal Narrative exists
WHEN:   Work addresses it over time
THEN:   Goal energy decays naturally
AND:    Goal stops surfacing in context
AND:    Completion happens without explicit close
```

---

### B4: Old Work Resurfaces When Relevant Again

**Objective:** Memory through strength.

**Why:** Nothing truly forgotten. High-strength links remember what mattered. When Space reactivated, old knowledge returns.

```
GIVEN:  Cold Narrative with high strength
WHEN:   Related area becomes active
THEN:   Old Narrative resurfaces in context
AND:    Previous decisions and rationale available
AND:    No need to re-explain history
```

---

### B5: Agents Differentiate Over Time

**Objective:** Many agents, emergent differentiation.

**Why:** No hardcoded specialization. Agents accumulate beliefs, memories, Space affinity through work. Distinct personalities emerge.

```
GIVEN:  Multiple agents starting similar
WHEN:   Agents work over weeks/months
THEN:   Each agent develops distinct focus areas
AND:    Differentiation visible in their outputs
AND:    No system prompt changes required
```

---

### B6: Docs Become Queryable Knowledge

**Objective:** Docs dissolve into narratives.

**Why:** Markdown is dead format. Narratives are living graph. Questions get answered from graph, not file search.

```
GIVEN:  Docs ingested as Narratives
WHEN:   Actor needs information
THEN:   Relevant Narratives surface through context
AND:    Links show relationships between concepts
AND:    No grep/search through files
```

---

### B7: Changes Flow to Affected Areas

**Objective:** All actors generate energy through activity.

**Why:** Change creates Moments. Energy flows through links. Affected Narratives warm up. Related agents notice.

```
GIVEN:  Actor modifies something
WHEN:   Change recorded as Moment
THEN:   Linked Narratives receive energy
AND:    Agents in affected Spaces may trigger
AND:    Downstream effects propagate naturally
```

---

### B8: World Stays Alive Without Human Attention

**Objective:** World runs continuously.

**Why:** Not event-driven. Agents work while human sleeps. x1/x2/x3 speeds. Work continues.

```
GIVEN:  Runner active
WHEN:   Human not actively engaged
THEN:   Agents still trigger on hot Narratives
AND:    Work progresses
AND:    Human returns to updated state
```

---

### B9: Parallel Work Doesn't Conflict

**Objective:** Many agents, emergent differentiation.

**Why:** Agents in different Spaces work on different things. No coordination overhead. Physics handles it.

```
GIVEN:  Multiple agents in different Spaces
WHEN:   All working simultaneously
THEN:   Each produces coherent work for their Space
AND:    No stepping on each other
AND:    Conflicts rare (different contexts)
```

---

### B10: New Project Bootstraps Quickly

**Objective:** Same engine, multiple clients.

**Why:** Ingest docs → get Narratives → agents can work. No custom setup. Same physics, different content.

```
GIVEN:  New project with existing docs
WHEN:   Docs ingested
THEN:   Narratives created automatically
AND:    Spaces populated
AND:    Agents can start working immediately
```

---

### B11: Human Focus Drives Priority

**Objective:** All actors generate energy.

**Why:** Human attention = energy. What human focuses on heats up. Agents follow the heat.

```
GIVEN:  Human focuses on area (enters Space, discusses topic)
WHEN:   Energy injected through activity
THEN:   That area becomes hot
AND:    Agents more likely to work there
AND:    Human implicitly steers without explicit assignment
```

---

## INPUTS / OUTPUTS

### System Input: Human Activity

| Input | Effect |
|-------|--------|
| Enter Space | Context loaded, proximity increases |
| Write message | Moment created, energy flows |
| Create goal | Narrative created, surfaces to agents |
| Ignore area | Energy decays, goes cold |

### System Output: Observable Value

| Output | Evidence |
|--------|----------|
| Useful work | Agent outputs that address context |
| Relevant context | Hot Narratives match current focus |
| Natural completion | Goals go quiet when done |
| Memory recall | Old work resurfaces when relevant |
| Emergent specialization | Agents develop distinct focuses |

---

## ANTI-BEHAVIORS (Failure Modes)

### A1: Agent Produces Irrelevant Work

```
GIVEN:  Agent triggered
WHEN:   Context is noisy or wrong
THEN:   Work doesn't address what matters
FIX:    Refine Space boundaries, tune energy thresholds
```

### A2: Important Context Doesn't Surface

```
GIVEN:  Relevant Narrative exists
WHEN:   Energy too low
THEN:   Actor misses important information
FIX:    Check link weight, strength accumulation
```

### A3: Goals Never Complete

```
GIVEN:  Goal Narrative exists
WHEN:   Energy never decays
THEN:   Goal haunts context forever
FIX:    Check decay rates, ensure work links to goal
```

### A4: Old Work Never Resurfaces

```
GIVEN:  Cold Narrative with history
WHEN:   Space reactivated
THEN:   Previous work not available
FIX:    Check strength retention, link health
```

---

## MARKERS

<!-- @mind:todo Define thresholds for context relevance -->
<!-- @mind:todo Specify agent differentiation metrics -->
<!-- @mind:todo Design bootstrap ingest process -->

<!-- @mind:escalation B9 assumes Spaces don't overlap — what if agent is in multiple Spaces that both have hot Moments? Which triggers first? -->
<!-- @mind:escalation B3 "goals complete naturally" — what if goal energy never decays because it keeps getting referenced? Stuck goal problem. -->
<!-- @mind:escalation B11 "human focus drives priority" — but human might focus on wrong thing. Should agents be able to surface competing priorities? -->

<!-- @mind:proposition B5 differentiation could be measured — track "specialization index" as distance from average agent belief vector -->
<!-- @mind:proposition B4 resurface could be proactive — agent notices pattern match with cold high-strength Narrative, brings it up -->
<!-- @mind:proposition B10 bootstrap could include "seed agents" — pre-trained on similar projects to accelerate differentiation -->
