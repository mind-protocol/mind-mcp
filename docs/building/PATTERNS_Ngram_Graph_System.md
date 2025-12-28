# mind Graph System — Design Patterns

## Core Philosophy

**The graph runs the dev process.**

Docs dissolve into Narratives. Tasks emerge from energy. Agents differentiate through accumulated state. The world ticks continuously. Physics decides what's relevant.

## Key Decisions

### 1. Same Rules for All Actors

```
actor: human | agent
```

No special pump. Every actor:
- Exists in a Space
- Generates energy based on proximity
- Creates Moments
- Creates Narratives
- Accumulates beliefs/memories through links

Differentiation emerges from graph state, not hardcoded roles.

### 2. Docs Are Views, Graph Is Truth

```
markdown file → rendered from Narratives
change → creates Moment + updates Narrative
```

The doc chain (OBJECTIVES → PATTERNS → VALIDATION → etc.) becomes Narrative nodes linked by `relates`. Markdown files are regenerated views, not source of truth.

Ingest existing docs → atomic sections become Narratives → graph is canonical.

### 3. Space = Context Loader

```yaml
space:
  type: module | feature | focus
  contains: [narratives, moments, things, actors]
```

Actor enters Space → loads hot Narratives as context. Space determines what's relevant, not explicit instructions.

Actors can be in multiple Spaces. Energy flows through Space containment.

### 4. Narratives Mirror Doc Chain

```yaml
narrative:
  type: objectif | pattern | behavior | algorithm | validation | implementation | health | sync | goal | rationale | memory
```

**Doc chain types** (from ingested docs):

| Type | What It Captures |
|------|------------------|
| `objectif` | Primary objectives, non-objectives, tradeoffs |
| `pattern` | Design decisions, key patterns |
| `behavior` | Observable effects, what it should do |
| `algorithm` | Procedures, how it works |
| `validation` | Invariants, what must be true |
| `implementation` | Code architecture, docking points |
| `health` | Verification mechanics |
| `sync` | Current state, handoffs |

**Emergent types** (from work):

| Type | Created When | Example |
|------|--------------|---------|
| `goal` | Work needed | "Ship health checkers" |
| `rationale` | Work completed | "Simplified 14 link types to 9" |
| `memory` | Past event worth retaining | "We tried X, it failed" |

Narratives link via `relates` with direction: `supports | contradicts | elaborates | supersedes`.

### 5. Moments Are Ephemeral, Strength Is Memory

```
Moment: what happened (high energy, decays)
Link strength: what mattered (accumulates, persists)
```

Moments flow through, heat up links, then cool. Strength remains. Old work resurfaces when Space reactivated — not through Moment recall, but through high-strength links.

### 6. World Runs Continuously

```
tick_speed: x1 | x2 | x3
```

Not event-driven. World runner ticks at chosen speed. All actors generate energy each tick. Hot areas surface. Agents get triggered.

Human is an actor in the world, not the controller of it.

### 7. Many Agents, No Specialization

```
agent_count: 6+  # minimum
specialization: emergent from graph state
```

Agents start similar. Beliefs, memories, Space affinity accumulate through work. One agent gravitates toward physics, another toward docs. Not designed — discovered.

### 8. Energy Determines Activation

```python
if narrative.energy > ACTIVATION_THRESHOLD:
    trigger_linked_agents(narrative)
```

No task queues. No explicit assignment. Hot Narratives in an agent's Space = work surfaces. Agent works → creates Moments → energy flows → next hot thing emerges.

## What's NOT in This System

- **Explicit task lists** — Narratives with energy are implicit tasks
- **Agent instructions** — Context is the instruction
- **Doc versioning** — Moments track changes, not file versions
- **Coordination layer** — Physics handles it
- **External triggers** — GitHub/Slack etc. come later

## Invariants

- All actors generate energy (no passive observers)
- All Narratives can become goals (type is semantic, not behavioral)
- Spaces contain, not own (actors can be in multiple)
- Moments decay, strength accumulates
- World ticks whether or not human is active

## Open Patterns (Unresolved)

- **Space granularity** — per module? per objective? per feature? TBD through use.
- **Agent spawn** — fixed 6? dynamic based on load? Start fixed, evolve.
- **Narrative lifecycle** — when does goal become "done"? Physics (energy → 0) or explicit?

---

## MARKERS

<!-- @mind:escalation Multiple agents triggered by same Moment — who goes first? Energy split? Sequential? Race condition risk? -->
<!-- @mind:escalation Narrative in multiple Spaces via multiple contains links — does it appear in both contexts? Energy split between Spaces? -->
<!-- @mind:escalation Bootstrap problem — first Moment creation before agents exist. Human seeds initial state, but how does first agent trigger happen? -->
<!-- @mind:escalation Agent "leaving" a Space — explicit move action? Or just add to new Space? Can agent be in 0 Spaces? -->
<!-- @mind:escalation Strength accumulation without bound — over years, does everything become max strength? Need soft cap or decay? -->

<!-- @mind:proposition Use embeddings to auto-create relates links between semantically similar Narratives -->
<!-- @mind:proposition Track agent "personality vector" derived from their accumulated beliefs/memories for observability -->
<!-- @mind:proposition Explicit "focus" command where human enters Space (like cd) to concentrate energy injection -->
<!-- @mind:proposition "Narrative merge" when two Narratives become redundant — physics-driven consolidation? -->
<!-- @mind:proposition Agent can "flag" a Narrative for human attention by boosting its energy artificially -->

<!-- @mind:escalation [D2] Speed modes x1/x2/x3 — how to handle in multiplayer?
  Options:
    A) Global speed — all actors share same tick rate
    B) Per-actor speed — each actor has own tempo
    C) Hybrid — global base with actor modifiers
  Opinion: (A) Global speed. Per-actor breaks physics causality — if agent A runs 3x and agent B runs 1x, their Moments interleave unpredictably. Energy flow assumes synchronized ticks. Start simple.
  Phase: 6 -->

<!-- @mind:escalation [D4] Agent Space Assignment — initial assignment to which Space(s)?
  Options:
    A) All agents start in root Space
    B) Each agent assigned to different module Space
    C) Dynamic — first interaction determines affinity
    D) Configured in agents.yaml per agent
  Opinion: (D) Config in agents.yaml. Explicit is better than emergent for bootstrap. Let agents drift later through physics. Default unassigned agents to root. Avoids cold-start problem where agents have no context.
  Phase: 3 -->

<!-- @mind:escalation [D7] Human Query Mechanism — how does human query graph directly?
  Options:
    A) CLI commands (mind query "...")
    B) API endpoints (REST/GraphQL)
    C) Physics-aware queries (respects energy thresholds)
    D) Raw graph queries (bypasses physics)
  Opinion: Start (A) CLI with (D) raw queries. Human needs to see full graph for debugging, not just hot items. Physics-aware queries are for agents. Add API later for tooling integration.
  Phase: 2 -->

<!-- @mind:escalation [Q8] Agent Count Strategy — fixed 6 agents or dynamic spawn?
  Options:
    A) Fixed 6 forever
    B) Dynamic spawn based on hot Space count
    C) Dynamic spawn based on total energy
    D) Manual scaling by human
  Opinion: (A) Fixed 6 initially. Dynamic spawn adds complexity — when to spawn? when to kill? Memory of dead agents? Start with 6, observe differentiation patterns. Revisit in Phase 6 when we understand agent behavior better. Premature optimization otherwise.
  Phase: 6 -->
