# Graph — Objectives

```
STATUS: Canonical
VERSION: v1.0
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:       OBJECTIVES_Graph.md (you are here)
PATTERNS:   ./PATTERNS_Graph.md
BEHAVIORS:  ./BEHAVIORS_Graph.md
ALGORITHM:  ../ALGORITHM_Physics.md
VALIDATION: ./VALIDATION_Living_Graph.md
SYNC:       ./SYNC_Graph.md
```

---

## PURPOSE

Define what the living graph physics optimizes for, ranked by priority. These objectives guide all design tradeoffs.

---

## OBJECTIVES

### O1: Computed Energy, Not Declared (Critical)

**What we optimize:** Energy emerges from structure, never from direct assignment.

**Why it matters:** If energy can be set directly, the system becomes arbitrary. Narratives must earn their importance through connections, beliefs, and pressure — not authorial fiat.

**Tradeoffs accepted:**
- Some desired energy states are hard to achieve
- Authors must work through structure, not shortcuts
- Debugging requires understanding propagation

**Measure:** No code path sets energy directly; all energy changes flow from link/structure updates.

---

### O2: Pressure Must Resolve (Critical)

**What we optimize:** Accumulated pressure eventually breaks, creating drama.

**Why it matters:** Stories need rhythm: slow build → sudden break → cascade. A system where pressure leaks gradually or never breaks has no dramatic shape.

**Tradeoffs accepted:**
- Some pressure buildups may feel slow
- Breaks can cascade unexpectedly
- Timing is emergent, not controlled

**Measure:** Pressure above threshold always triggers break within bounded ticks.

---

### O3: Attention Is Scarce (Critical)

**What we optimize:** Only high-energy nodes surface in context windows.

**Why it matters:** The graph is larger than any context window can hold. Energy determines what matters now vs what exists but sleeps. Without scarcity, agents drown in irrelevant data.

**Tradeoffs accepted:**
- Low-energy content may be missed
- Surfacing algorithm is critical path
- Some narrative threads go dormant

**Measure:** Context window population is bounded; priority determined by energy.

---

### O4: Graph Is Canon (Important)

**What we optimize:** Graph state is the single source of narrative truth.

**Why it matters:** If state lives elsewhere (session cache, agent memory, UI state), truth diverges. The graph must be authoritative for what happened and what can happen.

**Tradeoffs accepted:**
- Graph queries may be slower than local cache
- All mutations must go through graph operations
- External state must reconcile with graph

**Measure:** Any narrative query returns same result from any caller.

---

### O5: Deterministic Propagation (Important)

**What we optimize:** Same graph state + same tick = same output state.

**Why it matters:** Non-determinism makes debugging impossible and narrative feel arbitrary. Energy flow must be reproducible for testing and trust.

**Tradeoffs accepted:**
- No randomness in core propagation
- Explicit ordering where needed
- Some "organic" feel sacrificed for predictability

**Measure:** Replay any tick sequence → identical final state.

---

### O6: Near-Critical Operation (Nice to have)

**What we optimize:** The system operates near the edge of stability.

**Why it matters:** Too stable = boring (nothing happens). Too chaotic = meaningless (everything breaks constantly). The sweet spot: enough pressure that breaks feel earned, enough stability that builds feel meaningful.

**Tradeoffs accepted:**
- Tuning requires observation
- Some playthroughs may feel slow or chaotic
- Narrator adjusts to maintain criticality

**Measure:** Break frequency within target range; player-reported drama satisfaction.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O1 vs author control | Authors work through structure; energy follows |
| O2 vs pacing control | Accept emergent timing; tune thresholds |
| O3 vs narrative completeness | Dormant threads can resurface; not lost |
| O5 vs organic feel | Determinism in mechanics; variety in content |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Direct energy manipulation** — Energy is derived, not set
- **Narrator prompt engineering** — That belongs to narrator module
- **UI presentation of energy** — That belongs to frontend
- **Data ingestion pipelines** — That belongs to world-scraping

---

## THE CORE INSIGHT

**Characters are batteries. Narratives are circuits. Energy flows through links.**

No one injects energy. The story emerges from structure.

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
