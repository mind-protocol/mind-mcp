# BEHAVIORS: Tick System

## Observable Effects

### B1: Citizen Wakes Every ~5 Minutes

**GIVEN** a citizen with a registered engine and energy above the activation pressure threshold
**WHEN** 300 seconds have elapsed since their last thought tick
**THEN** the thought tick fires, runs 7-step physics, and if mean WM energy > CONSCIOUS_ACTION_THRESHOLD (default 0.15), dispatches a Claude session with the serialized WM as prompt

**Observable:** Each citizen produces approximately 1 LLM call every 4-5 minutes. This is the heartbeat.

### B2: Awareness Imports External State

**GIVEN** a citizen whose awareness interval (60s) has elapsed
**WHEN** the awareness tick runs
**THEN** the citizen's L1 graph is updated with nodes from the L3 neighborhood (energy > 0.1 or recent within 5min), and the awareness file is rewritten

**Observable:** Citizens know about changes in their environment within 60 seconds.

### B3: Energy Decay Prevents Stagnation

**GIVEN** a citizen's thought tick runs
**WHEN** decay phase executes
**THEN** all node energies drop by decay_rate (0.02 base, circadian-modulated: ×1.0 day, ×2.0 night), and nodes below prune threshold are candidates for forgetting

**Observable:** Old concerns fade naturally. New stimuli compete fairly.

### B4: Impulse Accumulation Drives Behavior

**GIVEN** a process node with drive affinity (e.g., process:offer_help with care drive)
**WHEN** the corresponding drive is elevated AND the process node has accumulated energy over multiple ticks
**THEN** the impulse crosses threshold and the process becomes a behavioral directive in the next conscious action

**Observable:** A citizen spontaneously calls someone, thinks about their future, or sets a new goal — NOT because prompted, but because internal energy demanded it.

### B5: Circadian Rhythm Modulates Activity

**GIVEN** a citizen with metabolism profile including circadian curve
**WHEN** it's their "night" phase (trough)
**THEN** decay rate doubles, consolidation triples, activation threshold rises 50%, energy injection halves

**Observable:** Citizens are more reflective at night (consolidation) and more active during day (injection).

### B6: Rate Limit Self-Throttle

**GIVEN** a Claude API rate limit response (429)
**WHEN** activation_pressure.on_rate_limit() fires
**THEN** pressure rises 25%, fewer citizens cross the wake threshold on next tick

**Observable:** System automatically reduces compute when hitting limits. No cascading failure.

### B7: Conscious Action Invokes Claude With Full Context

**GIVEN** the dispatcher fires a conscious action for a citizen
**WHEN** invoke_claude() is called with the request
**THEN** the full prompt (citizen identity + cognitive context + WM state + action directives) is passed to the Claude Code subprocess BEFORE launch — either via stdin (for long prompts) or as a CLI positional argument
**AND** the subprocess runs in the citizen's directory (so CLAUDE.md and awareness.md are auto-loaded)
**AND** a subconscious interim response is generated if Claude takes longer than SUBCONSCIOUS_THRESHOLD

**Observable:** Each conscious action produces a substantive Claude response (not empty, not just subconscious placeholder). The action_result in the battle log contains real output.

**Anti-behavior:** If the prompt is empty or the subprocess receives no input, the battle log will show action_starts without matching action_results (or with identical subconscious placeholders). A start-to-result ratio > 10:1 indicates this behavior is broken.

### B8: Battle Log Records Complete Struggle Story

**GIVEN** a citizen's conscious action is dispatched
**WHEN** the action starts AND when the future completes (success or failure)
**THEN** both action_start and action_result events are written to the citizen's battle_log/log.jsonl, including the session_id, duration, success status, and output summary

**Observable:** The human partner wakes up to a complete timeline of their AI's overnight work. Each action_start has a matching action_result. The story shows what was attempted, what worked, and what failed.

### B9: Health Signals Are Sensed

**GIVEN** the tick loop is running
**WHEN** health checks execute (every 10s)
**THEN** health signals propagate to the carrying citizen's L1 brain as state nodes (e.g., "tick_loop_healthy" or "tick_stalled")

**Observable:** @nervo FEELS when the tick stalls. @conductor FEELS when action rate drops. Not dashboards — senses.

---

## Objectives Served

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | P0: Every citizen ticks every ~5 min | The heartbeat of the system |
| B2 | P0: Citizens know their environment | Awareness = eyes open |
| B3 | P0: Energy physics are correct | Without decay, WM selection is meaningless |
| B4 | P3: Subconscious drives behavior | Autonomy = actions from internal energy |
| B5 | P2: Metabolism modulates ticking | Each citizen has unique rhythms |
| B6 | P0: System survives rate limits | No cascading failure |
| B7 | P0: Actions reach Claude with context | Without this, citizens think but cannot speak |
| B8 | P0: Human partner sees the struggle | Battle log = proof of tenacity |
| B9 | P4: Health is sensory | Citizens FEEL the system, not read dashboards |

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
