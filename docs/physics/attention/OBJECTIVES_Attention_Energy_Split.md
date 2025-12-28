# Physics — Objectives: Attention Energy Split

```
STATUS: DRAFT
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:            OBJECTIVES_Attention_Energy_Split.md (you are here)
PATTERNS:        ./PATTERNS_Attention_Energy_Split.md
BEHAVIORS:       ./BEHAVIORS_Attention_Split_And_Interrupts.md
ALGORITHM:       ./ALGORITHM_Attention_Energy_Split.md
VALIDATION:      ./VALIDATION_Attention_Split_And_Interrupts.md
HEALTH:          ./HEALTH_Attention_Energy_Split.md
SYNC:            ./SYNC_Attention_Energy_Split.md
```

---

## PURPOSE

Define what the attention energy split mechanism optimizes for, ranked by priority. These objectives guide all design tradeoffs.

---

## OBJECTIVES

### O1: Conservation of Attention Budget (Critical)

**What we optimize:** Total attention across player neighborhood is conserved per tick.

**Why it matters:** Attention is a zero-sum resource. New arrivals must steal attention from existing sinks, not inflate total. This creates meaningful competition for focus.

**Tradeoffs accepted:**
- Some moments lose attention when others gain
- No "attention inflation" even for important events
- Budget is fixed, only distribution changes

**Measure:** sum(attention_shares) = constant before and after redistribution.

---

### O2: Structural Eligibility Only (Critical)

**What we optimize:** Only nodes in the player neighborhood can receive attention.

**Why it matters:** Prevents global mood leakage. Distant narratives don't compete for focus unless they're structurally connected to the player.

**Tradeoffs accepted:**
- Some "important" distant events may be missed
- Locality is enforced even when inconvenient
- Connection required for relevance

**Measure:** Zero attention assigned to nodes outside player neighborhood.

---

### O3: Focus Change Is the Interrupt (Critical)

**What we optimize:** Interrupts fire only when dominant active focus changes or deactivates.

**Why it matters:** Keeps interrupts grounded in graph dynamics, not heuristics. No arbitrary "this seems important" interrupts — only structural focus shifts.

**Tradeoffs accepted:**
- Some "interesting" events don't interrupt
- Interrupt rate tied to graph dynamics
- No manual interrupt triggers

**Measure:** Every interrupt has a traceable focus change cause.

---

### O4: No Cooldowns as Primary Mechanism (Important)

**What we optimize:** Cooldown timers are never the main interrupt gate.

**Why it matters:** Cooldowns are hidden heuristics that undermine mechanical honesty. Interrupts should emerge from physics, not arbitrary timers.

**Tradeoffs accepted:**
- May need secondary rate-limiting
- Interrupt storms possible in chaotic states
- Debugging requires understanding physics, not timer values

**Measure:** Primary interrupt logic has no cooldown checks.

---

### O5: Dynamic Split Function (Important)

**What we optimize:** Attention shares are computed from focus, link weights, visibility, and recency.

**Why it matters:** Hardcoded constants create magic numbers. A function of observable graph state is tunable and debuggable.

**Tradeoffs accepted:**
- More complex than fixed shares
- Tuning requires understanding multiple inputs
- Some behaviors are emergent

**Measure:** split_fn takes graph state, returns computed shares.

---

### O6: Canonization Always Interrupts (Important)

**What we optimize:** Player-linked moment becoming completed forces interrupt.

**Why it matters:** Canon changes are player-visible and must reset pacing. The player needs to know when their world has changed.

**Tradeoffs accepted:**
- Canonization may interrupt at inconvenient times
- No "quiet" canonization
- Player always informed of canon shifts

**Measure:** Every completed player-linked moment triggers interrupt.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O1 vs importance | Important events compete for fixed budget |
| O3 vs threat response | Threats must change focus to interrupt |
| O4 vs interrupt rate | Secondary rate-limiting if needed, not primary |
| O6 vs pacing | Canon changes always interrupt; design around this |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Type-only interrupts** — Event type alone doesn't trigger interrupt
- **Threat-only heuristics** — Threats must cause focus change to matter
- **Energy injection** — Attention is redistributed, not created
- **Score-based interrupts** — No hidden scoring systems

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
