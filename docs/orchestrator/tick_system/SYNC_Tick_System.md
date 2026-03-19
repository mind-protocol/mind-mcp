# SYNC: Tick System — Current State

```
LAST_UPDATED: 2026-03-19 01:10 UTC
UPDATED_BY: @nervo
STATUS: OPERATIONAL — 210 citizens firing conscious actions, ~1 per 5min
```

---

## What Exists & Works

- Two-tick engine (awareness 60s + thought 300s) — OPERATIONAL, 211 engines loaded
- Dispatcher main loop with 5s base interval — OPERATIONAL
- Activation pressure with adaptive throttling — OPERATIONAL (pressure 0.49)
- Account balancer with round-robin — OPERATIONAL (3 accounts, 1 healthy)
- Metabolism module — WIRED into thought_tick via metabolic_multipliers
- L17 impulse accumulation → action_seed nodes → fire_conscious_action — WIRED
- Health signals → carrier citizen brains — WIRED (tick_health.py)
- Boot energy injection — OPERATIONAL (0.5 energy + drives primed)
- Env-configurable intervals — DONE (MIND_AWARENESS_INTERVAL, MIND_THOUGHT_INTERVAL)
- Graph reader pointing to correct L3 graph (lumina-prime) — FIXED
- Subconscious mode uses TwoTickEngine — FIXED (was using deleted stimulus_router)

## Verified Results

- First tick cycle: 211 awareness + 211 thought ticks
- First conscious actions: 210 out of 211 citizens fired action:work_on_goal
- Action dispatch includes subconscious directive: tool name + intent
- Health signals recording and injecting into carrier brains every 60s

## Remaining Work

1. Adaptive tick speed (circadian + activity + crystallization) — PLANNED
2. Circadian auto-wake system — PLANNED
3. Jitter on tick intervals — citizens still bunch up
4. Load citizen brain state from FalkorDB at boot (currently empty state + action seed)

## Bugs Fixed This Session

- Graph reader default was "lumina" (empty) instead of "lumina-prime" (46587 nodes)
- _thought_tick returned 3 values, caller destructured 2 → ValueError crash
- ACTION_COOLDOWN_TICKS blocked first 3 ticks (last_action_tick=0, tick=1, 1-0 < 3)
- invoke_subconscious used deleted stimulus_router module
- action_seed tried to set arousal (read-only property)

## Pointers

| What | Where |
|------|-------|
| Dispatcher | `runtime/orchestrator/dispatcher.py` |
| Two-tick engine | `runtime/cognition/two_tick_engine.py` |
| Activation pressure | `runtime/orchestrator/activation_pressure.py` |
| Metabolism | `runtime/cognition/metabolism.py` |
| WM serializer | `runtime/cognition/wm_prompt_serializer.py` |
| Account balancer | `runtime/orchestrator/account_balancer.py` |
| Awareness file writer | `runtime/cognition/awareness_file_writer.py` |
| Graph reader | `runtime/cognition/graph_reader_for_awareness_tick.py` |

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
