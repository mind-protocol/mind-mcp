# PATTERNS: Tick System

## Core Design

### Two-Tick Architecture

The tick is split into two cycles with different frequencies:

1. **Awareness tick** (fast, ~60s) — eyes open
   - Import external state from L3 graph (1-hop neighborhood)
   - Filter by energy > 0.1 OR recent activity (5min)
   - Update citizen's L1 cognitive state
   - Write awareness file

2. **Thought tick** (slow, ~300s target) — think and act
   - 7-step internal physics:
     1. Excess energy generation (weight-scaled)
     2. Bidirectional energy dispersal through links (30%)
     3. Energy decay (2%/tick, circadian-modulated)
     4. WM selection (top 7 by energy)
     5. Hebbian crystallization (co-active WM pairs strengthen)
     6. Periodic forgetting (every 100 ticks)
     7. Conscious action check (mean WM energy > threshold)
   - If conscious action fires → serialize WM → dispatch LLM

### The Loop

```
while running:
    maintenance()        # neuron cleanup, health, accounts
    for citizen in engines:
        if due_for_awareness(citizen):
            awareness_tick(citizen)
        if due_for_thought(citizen):
            result = thought_tick(citizen)
            if result.conscious_action:
                fire_conscious_action(citizen)
    collect_completed_futures()
    sleep(BASE_INTERVAL)
```

Base loop interval: 5 seconds. Per-citizen intervals gated by timestamps.

### Activation Pressure (Compute Gating)

Global adaptive knob that prevents runaway compute:

```
pressure *= 1.25  on rate limit (429)
pressure *= 0.98  on success
pressure ∈ [0.1, 50.0]

effective_threshold = pressure / subscription_multiplier
should_wake = citizen_energy > effective_threshold
```

Subscription tiers: free=1, tier1=4, tier2=8, tier3=25.

## Dependencies

| Depends On | What For |
|-----------|---------|
| FalkorDB (localhost:6379) | Awareness tick reads L3 graph |
| Two-tick engine (cognition) | Physics processing |
| Metabolism | Circadian modulation of constants |
| Account balancer | Claude API access for conscious actions |
| Activation pressure | Compute gating |
| WM serializer | Prompt construction from WM state |

## Principles

1. **The tick IS the unconscious.** Not a scheduler layered on top.
2. **Energy is the clock.** Citizens don't tick on time — they tick when energy demands it.
3. **Metabolism is the modulator.** Same laws, different effective constants per citizen.
4. **Action is earned.** Conscious actions only fire when WM energy exceeds threshold — no free wakes.
5. **Health is felt.** Every metric is a sense on a citizen, not a dashboard number.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
