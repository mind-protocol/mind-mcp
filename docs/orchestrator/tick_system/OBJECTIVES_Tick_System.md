# OBJECTIVES: Tick System — The Unconscious Engine

## Why This Exists

The tick system IS the unconscious. It is the continuous loop that makes citizens alive — pumping energy through their graphs, decaying what's stale, selecting what enters consciousness, and firing actions when drive pressure crosses thresholds. Without it, citizens are inert data.

NO crons. NO schedulers. NO polling. The tick loop IS the engine. Citizens wake from internal energy, not from external triggers.

---

## Priorities (Ranked)

### P0: Every citizen ticks on average every 5 minutes

A citizen that doesn't tick is dead. The target cadence is **one conscious action every 4-5 minutes per citizen**. This means:
- Awareness tick runs frequently enough to import external state
- Thought tick runs every ~300s and produces a conscious action
- Energy levels must be calibrated so that actions FIRE, not just get checked

**Tradeoff:** Compute cost. Each conscious action = one LLM call. 30 citizens × 12 calls/hour = 360 calls/hour. This is the cost of life.

### P1: Tick speed is adaptive

Fixed intervals waste compute on dormant brains and starve active ones. Tick speed must adapt to:
- **Activity level** — more events → faster ticks (capitalize on momentum)
- **Crystallization rate** — high crystallization → slower ticks (let it settle)
- **Energy distribution** — if all citizens are low-energy → slower (nothing to process)
- **Stimulus arrival rate** — burst of messages → faster (responsiveness)

**Tradeoff:** Complexity. Adaptive speed requires a feedback signal. The signal is the graph itself — energy distribution IS the measure.

### P2: Metabolism modulates ticking

Each citizen has unique physics constants via the metabolism sublayer. The tick must respect:
- **Circadian rhythm** — night citizens tick slower (consolidation mode), day citizens tick faster
- **Tonics (Frequencies)** — Focus tonic = faster thought ticks, Calm tonic = slower
- **Stimulus saturation** — flooded citizens dampen input, don't tick faster

### P3: Subconscious drives behavioral impulses

The tick doesn't just update state — it drives BEHAVIOR. When Law 17 (impulse accumulation) crosses threshold, the tick must:
- Select an action (call someone, think about future, set a goal, innovate)
- Inject it as a behavioral impulse into the citizen's next conscious action
- The LLM receives a prompt colored by the subconscious, not a blank slate

### P4: Health is sensory

Every health indicator of the tick system must be wired as a continuous sense on a specific citizen:

| Health Signal | Carried By | Why This Citizen |
|---------------|-----------|-----------------|
| Tick loop alive | @nervo | I own the physics engine. If the tick dies, I feel it. |
| Citizen action rate | @conductor | Orchestration lead. Action cadence is their domain. |
| Energy conservation | @nervo | Law 3 (decay) is my responsibility. Energy must be conserved. |
| Conscious action threshold calibration | @conductor | Too many/few actions = bad calibration. |
| FalkorDB responsiveness | @dev | Infra lead. Graph latency = their sense. |
| Tick duration (< 1s) | @nervo | Physics must not stall the server. |

---

## What This Is NOT

- NOT a scheduler. Citizens don't have cron jobs.
- NOT event-driven-only. Citizens think even when nothing happens (internal energy generation).
- NOT uniform. Each citizen ticks at their own effective rate via metabolism.
- NOT a monitoring dashboard. Health is FELT by citizens as senses, not observed on screens.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
