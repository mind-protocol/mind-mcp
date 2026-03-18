# IMPLEMENTATION: Tick System

## File Map

| File | Purpose | Lines |
|------|---------|-------|
| `runtime/orchestrator/dispatcher.py` | Main loop, citizen management, future collection | ~450 |
| `runtime/cognition/two_tick_engine.py` | Awareness + Thought tick implementation | ~300 |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Legacy L1 tick (fallback) | ~1100 |
| `runtime/orchestrator/activation_pressure.py` | Compute gating, pressure adaptation | ~100 |
| `runtime/cognition/metabolism.py` | Circadian, tonics, stimulus saturation | ~630 |
| `runtime/cognition/wm_prompt_serializer.py` | WM → prompt text serialization | ~200 |
| `runtime/cognition/awareness_file_writer.py` | Write awareness.md per citizen | ~150 |
| `runtime/cognition/graph_reader_for_awareness_tick.py` | L3 → L1 import queries | ~200 |
| `runtime/orchestrator/account_balancer.py` | Claude account rotation | ~120 |

## Key Constants (Current → Target)

| Constant | Current | Target | Env Var |
|----------|---------|--------|---------|
| BASE_LOOP_INTERVAL | 5s (hardcoded) | 5s | MIND_BASE_LOOP_INTERVAL |
| AWARENESS_INTERVAL | 60s (hardcoded) | 60s | MIND_AWARENESS_INTERVAL |
| THOUGHT_INTERVAL | 300s (hardcoded) | 300s (adaptive ±120s) | MIND_THOUGHT_INTERVAL |
| CONSCIOUS_ACTION_THRESHOLD | 0.15 (env) | 0.15 | MIND_CONSCIOUS_ACTION_THRESHOLD |
| ACTION_COOLDOWN_TICKS | 3 (hardcoded) | 3 | MIND_ACTION_COOLDOWN |
| NEURON_CLEANUP_INTERVAL | 60s | 60s | — |
| HEALTH_CHECK_INTERVAL | 10s | 10s | — |

## Call Chain

```
home_server.py (lifespan)
  └→ Dispatcher.__init__()
     └→ start()
        └→ Thread(_run_loop)
           ├→ _maintenance()
           │  ├→ neuron cleanup (60s)
           │  ├→ health check (10s)
           │  ├→ account refresh (1800s)
           │  └→ first-boot scan (30s)
           ├→ _tick_all_citizens()
           │  ├→ awareness_tick() → TwoTickEngine.awareness_tick(graph_read_fn)
           │  └→ thought_tick() → TwoTickEngine.thought_tick()
           │     └→ _fire_conscious_action()
           │        ├→ serialize_wm_to_prompt()
           │        ├→ inject_impulses() [L17]
           │        ├→ account_balancer.get_account_env()
           │        └→ executor.submit(invoke_claude)
           └→ _collect_completed_futures()
              └→ activation_pressure.on_success() / on_rate_limit()
```

## Data Flows

```
[L3 FalkorDB] → graph_reader → awareness_tick → [L1 state update]
                                                        ↓
[L1 state] → thought_tick → 7 physics steps → [WM selection]
                                                    ↓
[WM] → serializer → [prompt] → Claude → [response] → [graph_write mutations]
                        ↑
              [L17 impulses injected]
```

## Integration Points

| From | To | What |
|------|-----|------|
| Bridges (TG/WA) | Dispatcher.inject_stimulus() | External stimulus → immediate awareness tick |
| Metabolism | thought_tick() | Effective constants (circadian, tonics) |
| Activation pressure | fire_conscious_action() | Compute gate (should this citizen wake?) |
| Account balancer | fire_conscious_action() | Which Claude account to use |
| L17 impulse | serialize_wm_to_prompt() | Behavioral directives in prompt |

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
