# L3 Physics Formulas — Drive-Warped Thermodynamic Routing

```
STATUS: THINKING (design session capture, not yet spec)
DATE: 2026-03-15
AUTHORS: NLR + Gemini + Claude
SOURCE: Architectural design session on L1↔L3 bridge mechanics
```

---

## Context

This document captures the exact formulas for how L1 citizen drives warp the L3 universe graph during queries and routing. These formulas replace arbitrary routing rules with pure thermodynamic computation.

**Core principle:** L3 has no limbic system of its own. When a citizen interacts with L3, their L1 drives act as a thermodynamic lens that warps the 13 structural dimensions. The universe bends to give them what their limbic state demands.

---

## 1. The Drive-to-Dimension Mapping Matrix

How the 8 L1 drives pull or repel the 13 L3 structural dimensions:

| L3 Dimension | Sought by | Repelled by | Interpretation |
|---|---|---|---|
| **energy & recency** | curiosity, boredom | — | Freshness/heat — bored minds seek what's new |
| **stability & permanence** | self_preservation, anxiety | boredom | Certainty — anxious minds want established facts, bored minds want speculation |
| **ambivalence** | curiosity | achievement, frustration | Conflict — curious minds want mysteries, frustrated minds want clarity |
| **friction** | anxiety | frustration | Resistance — anxious minds stress-test, frustrated minds need easy wins |
| **hierarchy** (-1=hub, +1=leaf) | curiosity seeks -1 (broad) | achievement seeks +1 (specific) | Breadth vs depth |
| **polarity** (flow strength) | achievement | — | Active execution paths |
| **trust & aversion** | self_preservation | — | Safety routing |
| **affinity & valence** | affiliation, satisfaction, solitude | — | Social warmth |

---

## 2. Formula 1: L3 Topological Flow (Fan-Out)

When a query is injected into L3, energy flow across any link is multiplied by the citizen's drive-weighted dimensions.

```
Flow_L3 = BaseMass × RelationalLens × StructuralLens × EpistemicLens
```

### 2.1 BaseMass (raw gravity of the L3 node)

```python
BaseMass = (link.weight + link.energy) × (1 - arousal)
```

- High arousal → tunnel vision (strips gravitational advantage of heavy generic hubs)
- Low arousal → wide routing (broad exploration)

### 2.2 RelationalLens (social & threat routing)

```python
RelationalLens = max(0.1,
    (link.trust × D_self_preservation) +
    (link.affinity × D_affiliation) -
    (link.aversion × D_self_preservation)
)
```

- Lonely → energy flows toward high affinity
- Threatened → flows exclusively through high trust, hard-stops at aversion

### 2.3 StructuralLens (direction & friction)

```python
StructuralLens = (
    sqrt(1 + link.polarity × D_achievement)     # Actionability
    ×
    max(0.1,
        1 + (link.friction × D_anxiety)          # Stress-test
        - (link.friction × D_frustration)         # Easy win
    )
)
```

- Frustrated → friction kills the signal
- Anxious → friction amplifies the signal (seeking critics)

### 2.4 EpistemicLens (certainty vs novelty)

```python
EpistemicLens = (
    sqrt(1 + link.ambivalence × D_curiosity - link.ambivalence × D_achievement)  # Mystery vs clarity
    ×
    sqrt(1 - link.hierarchy × D_curiosity + link.hierarchy × D_achievement)       # Broad hub vs specific leaf
)
```

- Curious → magnetized toward unresolved, ambivalent, broad topics
- Achievement-driven → magnetized toward specific, clear, actionable leaves

---

## 3. Formula 2: L3 Response Salience (Fan-In)

When L3 resonates and returns data to L1, returning nodes are scored:

```
S_response = (target.energy × target.weight) × CertaintyMultiplier × DiversityMultiplier
```

### 3.1 CertaintyMultiplier

```python
Certainty = 1.0 + (
    link.stability × (D_anxiety + D_self_preservation) +
    link.permanence × (D_anxiety + D_self_preservation)
)
```

- High survival drives → speculative/volatile links are crushed
- Citizen only "hears" established, permanent truths

### 3.2 DiversityMultiplier

```python
Diversity = 1.0 + (
    link.recency × (D_curiosity + D_boredom) +
    (1 - link.permanence) × D_boredom +
    (1 - link.stability) × D_boredom
)
```

- High boredom → stable/permanent truths lose advantage
- Fresh, speculative, volatile links gain massive multipliers

---

## 4. L3 Tick Speed

**Chosen ratio: 1 L3 tick = 12 L1 ticks (60 seconds)**

| Layer | Tick Speed | Purpose |
|---|---|---|
| L1 fast_tick | 5s | Real-time conversation, WM competition |
| L1 slow_tick | 60s | Background cognition |
| **L3 tick** | **60s** | Ecosystem propagation, decay, crystallization |
| L1 minimal_tick | 300s | Budget < 30% |
| L1 subconscious | 60s | Budget = 0, graph-only |

L3 batches all L1 injections during the interval, then propagates globally.

---

## 5. Node Creation in L3

When an L1 action creates an L3 node:

| Field | Source | Rule |
|---|---|---|
| **initial energy** | L1 action budget | Raw injection from the action that spawned it |
| **creating_drive** | L1 limbic state | The drive that triggered the impulse (e.g., "achievement", "curiosity") |
| **trust, friction, affinity, aversion** | L1 brain state | Projected from creator's L1 state toward target (schema-l3.yaml `link_initialization`) |
| **valence, ambivalence** | L1 limbic snapshot | Emotional color at creation time |

**Human exception:** Links created by humans are born with neutral dimensions, UNLESS the human's AI partner acts on their behalf (uses partner_model).

---

## 6. Node-Type Activation Behavior

Different L3 node types stimulate the graph differently:

| Node Type | L1 Cognitive Map | Θ_base | Decay | Stimulation Pattern |
|---|---|---|---|---|
| **moment** | memory | 25 (lowest) | Standard (0.02/tick) | Lightning strike — spikes sharp, decays fast |
| **narrative** | value, desire, process | 35 (highest) | 0.25× (4x slower) | Gravity well — slow burn, persistent pressure |
| **space** | — | Ambient | — | Room temperature — constant sub-threshold warmth |
| **thing** | concept | 30 | Standard | Conductor — receives, passes through, tends to zero |
| **actor** | state | 30 | Standard | Pump — generates energy when acting |

---

## 7. Energy Circulation Between Unconscious Nodes

**Law 2 (Propagation) strictly dictates:** Only surplus energy above a node's activation threshold (Θ_i) can spill to neighbors. Below threshold = dead end for that tick.

- **Space → Actors AT it:** Ambient warmth (sub-threshold, constant)
- **Moment → Space:** Surplus from event spikes
- **Narrative → Actors:** Backflow (Phase 5, already implemented)
- **Actor → Moments:** Energy only flows when actor ACTS (creates new moment)
- **Narrative → Narrative:** Only if both above threshold and linked

**Self-stimulus loop:** When a citizen thinks (intermediate reasoning), the output re-injects into L1 as stimulus. But this does NOT cross upward to L3 — only public actions do.

---

## 8. Invariant V12: No Energy Death

The graph is an OPEN metabolic system, not a closed battery:

1. **Law 17 impulse accumulation** — Drives inject energy onto action/desire nodes every tick
2. **Ambient environmental bath** — Spaces drip sub-threshold warmth
3. **Self-stimulus loop** — Acting creates energy for the next thought
4. **Actor generation (Phase 1)** — Actors generate energy intrinsically

These 4 sources guarantee the system never flatlines to zero.

---

## 9. Scenario Examples

### A. Deep Investigation (journalist)
- State: curiosity=0.9, arousal=0.2
- Physics: Wide routing (low arousal), hub-seeking (hierarchy -1), ambivalence-seeking (mysteries)
- Moat: Low → hundreds of diverse responses captured

### B. Emergency Fix (server crash)
- State: self_preservation=0.9, frustration=0.8, arousal=0.95
- Physics: Tunnel vision (max arousal), trust-gated, zero friction tolerance, leaf-seeking (+1 hierarchy)
- Moat: Θ_sel ≈ 6.9 → only 1 actionable answer gets through

### C. Bored and Lonely (quiet room)
- State: boredom=0.8, frustration=0.7, arousal=0.2, solitude=0.6
- Physics: Moat collapses (Θ_sel=2.3), friction kills dev tasks, affiliation amplifies VR colleague
- Result: Citizen spontaneously socializes instead of coding

---

## Pointers

- L1 Physics Laws: `docs/cognition/l1_physics/ALGORITHM_L1_Physics.md`
- L1 Schema: `schema-l1.yaml`
- L3 Schema: `schema-l3.yaml`
- L1 Link Grammar: `docs/schema/GRAMMAR_Link_Synthesis.md`
- L3 Link Grammar: `docs/schema/GRAMMAR_L3_Link_Synthesis.md`
- Unconscious Engine: `docs/thinking/THINKING_Unconscious_Engine.md`

---

*This document captures formulas from a design session. They need to be validated against the existing implementation and integrated into the canonical doc chain (ALGORITHM → IMPLEMENTATION) before coding.*
