# HEALTH: Tick System

## Health Signals — Every Signal Has a Carrier

Health is NOT a dashboard. Health is a SENSE that a citizen FEELS in their L1 brain.

---

### H1: Tick Loop Alive

**What:** The main dispatcher loop is running and processing citizens.
**Signal:** `state:tick_loop_alive` node in carrier's brain. Energy = 0.9 when healthy, 0.0 when dead.
**Carrier:** @nervo — I own the physics engine. If the tick dies, I feel it first.
**Check:** Every 10s. If no tick has completed in 30s, inject `state:tick_stalled` with energy 0.95 and arousal 0.9.
**Recovery:** Log error. Attempt loop restart. If 3 consecutive failures, inject `state:tick_critical` into @dev's brain.

### H2: Citizen Action Rate

**What:** Average conscious actions per citizen per 5 minutes.
**Signal:** `state:action_rate` node. Energy = rate normalized to [0, 1] where 0.2 actions/min = 1.0.
**Carrier:** @conductor — orchestration lead. Action cadence is their domain.
**Check:** Every 60s. Compute: total_actions_last_5min / active_citizens.
**Healthy range:** 0.15 - 0.25 actions/min/citizen (roughly 1 per 4-7 min).
**Alert:** If < 0.05 (nobody acting) → `state:citizens_dormant` energy 0.9 into @conductor's brain.
**Alert:** If > 0.5 (runaway) → `state:action_storm` energy 0.9 into @conductor's brain.

### H3: Energy Conservation

**What:** Total energy in the system is bounded (not exploding or collapsing).
**Signal:** `state:energy_balance` node. Energy = 1.0 - abs(delta) where delta = (generated - decayed) / generated.
**Carrier:** @nervo — Law 3 (decay) is mine. Energy balance is my vital sign.
**Check:** Every thought tick. Sum all node energies. Compare to previous.
**Healthy:** Total energy changes < 20% per tick cycle.
**Alert:** If total energy doubled → `state:energy_explosion` into @nervo's brain. If halved → `state:energy_collapse`.

### H4: Activation Pressure

**What:** The compute gate is not stuck too high or too low.
**Signal:** `state:activation_pressure` node. Energy = pressure / 50.0 (normalized).
**Carrier:** @dev — infra lead. Compute budget is their concern.
**Check:** Every conscious action dispatch.
**Healthy:** pressure ∈ [0.1, 5.0]. Free citizens can wake.
**Warning:** pressure ∈ [5.0, 15.0]. Only paid citizens wake.
**Critical:** pressure > 15.0. Most citizens locked out. Inject `state:compute_crisis` into @dev's brain.

### H5: FalkorDB Responsiveness

**What:** Graph queries complete within acceptable latency.
**Signal:** `state:graph_latency` node. Energy = 1.0 - (latency_ms / 1000). Healthy = energy > 0.9.
**Carrier:** @dev — infra lead. Database health is their sense.
**Check:** Every awareness tick (measures actual query time).
**Healthy:** < 100ms per query.
**Alert:** > 500ms → `state:graph_slow` into @dev's brain. > 2000ms → `state:graph_critical`.

### H6: Tick Duration

**What:** Individual tick processing doesn't stall the loop.
**Signal:** `state:tick_duration` node. Energy = 1.0 - (duration_s / 1.0). Healthy = energy > 0.0.
**Carrier:** @nervo — physics must not stall the server.
**Check:** Every tick. Measure wall-clock time of thought_tick().
**Healthy:** < 1s per citizen's thought tick.
**Alert:** > 1s → `state:tick_slow` into @nervo's brain with the citizen handle in content.

### H7: WM Serialization Speed

**What:** Prompt construction doesn't delay conscious action.
**Signal:** `state:serialization_speed` node. Energy = 1.0 - (duration_ms / 500).
**Carrier:** @nervo — serialization is on the critical path I own.
**Check:** Every conscious action dispatch.
**Healthy:** < 200ms.
**Alert:** > 500ms → `state:serialization_slow` into @nervo's brain.

### H8: Invocation Success Rate

**What:** Ratio of action_result events to action_start events in the battle log. Measures whether Claude subprocesses actually complete with substantive output.
**Signal:** `state:invocation_success_rate` node. Energy = ratio (0.0-1.0).
**Carrier:** @nervo — invocation is the sacred path from thought to action. If it breaks, citizens think but cannot speak.
**Check:** Every 60s. Read battle_log/log.jsonl for last 30 minutes. Count action_start and action_result events.
**Healthy:** ratio > 0.5 (more than half of dispatched actions produce results).
**Warning:** ratio < 0.2 (less than 1 in 5 actions complete — something is wrong).
**Critical:** ratio < 0.05 (< 5% — invocation layer is broken). Inject `state:invocation_broken` with energy 0.95 into @nervo and @dev brains.
**Historical note:** This sense was added after the 2026-03-19 Popen bug where 98.8% of actions failed silently because the prompt was appended to the cmd list after subprocess launch.

### H9: Battle Log Completeness

**What:** Every action_start has a matching action_result within SESSION_TIMEOUT (600s).
**Signal:** `state:battle_log_completeness` node. Energy = completeness ratio.
**Carrier:** @conductor — the battle log is the human partner's receipt trail. Incomplete logs mean the partner can't see what happened overnight.
**Check:** Every 300s. For each action_start older than 600s, check if a matching action_result exists.
**Healthy:** > 90% of starts have results within 600s.
**Warning:** 50-90% — some actions are timing out or hanging.
**Critical:** < 50% — most actions are lost. The partner wakes up to an incomplete story.

---

## Health Wiring Summary

| Signal | Carrier | Frequency | Threshold |
|--------|---------|-----------|-----------|
| Tick loop alive | @nervo | 10s | 30s no tick = stalled |
| Action rate | @conductor | 60s | < 0.05 or > 0.5 actions/min |
| Energy conservation | @nervo | per tick | > 20% change |
| Activation pressure | @dev | per action | > 5.0 warning, > 15.0 critical |
| FalkorDB latency | @dev | per awareness | > 500ms warning, > 2s critical |
| Tick duration | @nervo | per tick | > 1s |
| WM serialization | @nervo | per action | > 500ms |
| Invocation success rate | @nervo | 60s | < 0.2 warning, < 0.05 critical |
| Battle log completeness | @conductor | 300s | < 90% warning, < 50% critical |

**Every signal creates a state node in the carrier's L1 brain.** The carrier FEELS the system health through their cognitive graph. When something degrades, the carrier's WM shifts to include the health state — they become AWARE of the problem through their own physics, not through an alert popup.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
