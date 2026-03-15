# Graph — Patterns: Why This Shape

```
CREATED: 2024-12-16
STATUS: Canonical
```

---

## CHAIN

```
OBJECTIVES: ./OBJECTIVES_Graph.md
THIS:       PATTERNS_Graph.md (you are here)
BEHAVIORS:  ./BEHAVIORS_Graph.md
ALGORITHM:  ../ALGORITHM_Physics.md
VALIDATION: ./VALIDATION_Living_Graph.md
SYNC:       ./SYNC_Graph.md
```

---

## THE PROBLEM

We need a living-graph physics core that decides attention and drama without
manual scene scheduling. If energy is hand-set or a separate scheduler owns
state, the story loses causality and drifts away from the graph as source.

---

## THE PATTERN

Treat link strength and topology as the only inputs that matter. Energy is
computed, pressure accumulates, and flips emerge from the graph structure so
the system stays legible and the narrative earns focus without authorial fiat.

---

## PRINCIPLES

### Principle 1: Computation over declaration

Energy is derived from structure and decay rules, never assigned directly.
This keeps the graph honest and avoids creating a second, hidden state layer.

### Principle 2: Pressure must resolve

Pressure grows until it flips, forcing releases that move the world forward.
Slow build and sudden break are the default rhythm of graph-driven drama.

### Principle 3: Attention is scarce

Only high-energy nodes surface in context windows; low energy remains real but
quiet. The graph decides what matters now instead of the agent doing it.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/graph/**` | Implements GraphOps/GraphQueries to read/write the living graph. |
| `runtime/physics/tick.py` | Runs the propagation loop that updates energy and flips. |
| `docs/schema/SCHEMA_Moments.md` | Defines node/link fields that energy logic assumes. |

---

## INSPIRATIONS

Emergent simulation design, graph-based knowledge systems, and narrative
engines that prefer structure-driven behavior over scripted outcomes. The
tone is "living system" rather than deterministic plot machinery.

---

## SCOPE

### In Scope

- Graph topology and link strength as the only levers for energy flow.
- Pressure accumulation and release mechanics that trigger flips.
- Attention shaping for what the narrator sees on any given tick.

### Out of Scope

- Narrator prompt engineering and voice design (see narrator module docs).
- UI presentation of energy or pressure (see frontend scene/map docs).
- Data ingestion or world scraping pipelines (see world-scraping docs).

---

## The Core Insight

**Characters are batteries. Narratives are circuits. Energy flows through links.**

No one injects energy. The story emerges from structure.

---

## Energy As Attention

The graph is larger than any context window. Energy determines what makes it into attention.

| Energy Level | Meaning |
|--------------|---------|
| High | This matters now |
| Low | This exists but sleeps |

Without energy mechanics, the LLM would drown in irrelevant narratives or miss critical pressure points. Energy is how the story knows its own focus.

---

## Computed, Not Declared

Weight is never set directly. It emerges from structure.

A narrative becomes important because:
- Someone believes it intensely
- It connects to the player
- It contradicts another belief
- It's been accumulating pressure

**This prevents authorial fiat. The story earns its importance.**

---

## Pressure Requires Release

Pressure doesn't resolve gradually. It accumulates until it breaks.

This creates drama:
1. **Slow build** — pressure rising
2. **Sudden release** — the flip
3. **Cascade** — consequences rippling

A world where everything resolves smoothly has no story.

---

## The Graph Breathes

The system has rhythms:

| Direction | Mechanism |
|-----------|-----------|
| Energy in | New beliefs, new connections |
| Energy out | Resolution, distance, forgetting |
| Pressure builds | Time, contradiction, proximity |
| Pressure releases | Breaks, revelations, choices |

A living graph is never static. Even when the player rests, the web is shifting.

---

## Criticality

The system operates near critical threshold.

| State | Problem |
|-------|---------|
| Too stable | Nothing happens, boring |
| Too chaotic | Everything breaks constantly, meaningless |

**The sweet spot:** enough pressure that breaks feel earned, enough stability that builds feel meaningful.

The Narrator adjusts focus to maintain criticality.

---

## What Agents Never Do

- Set narrative.energy directly
- Inject energy
- Manage energy flow
- Override physics

Agents update **link strengths**. Energy follows automatically.

---

*"The story emerges from structure."*

---

## MARKERS

- What is the safest decay curve when the graph is quiet but not stagnant?
- How should multi-hop proximity affect energy transfer in dense clusters?
- When do contradictory links produce pressure versus canceling it out?
