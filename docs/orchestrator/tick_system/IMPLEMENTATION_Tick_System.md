# IMPLEMENTATION: Tick System

## File Map

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `runtime/orchestrator/dispatcher.py` | Main loop, citizen management, future collection, tenacity physics | ~870 | WATCH |
| `runtime/orchestrator/claude_invoker.py` | Claude Code subprocess invocation, subconscious fallback, account failover | ~700 | OK |
| `runtime/orchestrator/battle_log.py` | JSONL receipt trail for human partner (action_start, action_result, obstacles, alliances) | ~100 | OK |
| `runtime/orchestrator/activation_pressure.py` | Compute gating, pressure adaptation | ~100 | OK |
| `runtime/orchestrator/account_balancer.py` | Claude account rotation, exhaustion tracking, failover | ~120 | OK |
| `runtime/orchestrator/degradation.py` | Rate limit detection, escalation, recovery tracking | ~80 | OK |
| `runtime/cognition/two_tick_engine.py` | Awareness + Thought tick implementation (7-step physics) | ~300 | OK |
| `runtime/cognition/metabolism.py` | Circadian, tonics, stimulus saturation, effective constants | ~630 | WATCH |
| `runtime/cognition/wm_prompt_serializer.py` | WM → prompt text serialization | ~200 | OK |
| `runtime/cognition/awareness_file_writer.py` | Write awareness.md per citizen | ~150 | OK |
| `runtime/cognition/graph_reader_for_awareness_tick.py` | L3 → L1 import queries | ~200 | OK |
| `runtime/cognition/action_seed.py` | Seed action process nodes for fresh citizens | ~80 | OK |
| `runtime/citizens/prompt_builder.py` | Build full citizen prompt (identity + cognitive context + mode) | ~200 | OK |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Legacy L1 tick (fallback) | ~1100 | SPLIT |

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
           │     └→ _fire_conscious_action(handle, action_node_id)
           │        ├→ serialize_wm_to_prompt(state, orientation)
           │        ├→ inject action_directive (L17 impulse → tool + intent)
           │        ├→ build request dict (text, voice_text, metadata.cognitive_context)
           │        ├→ dispatcher.dispatch(request)
           │        │  └→ executor.submit(invoke_claude, request, session_id)
           │        └→ log_action_start() → battle_log/log.jsonl
           └→ _collect_completed_futures()
              ├→ future.result() → (response, voice_response)
              ├→ activation_pressure.on_success() / on_rate_limit()
              ├→ _handle_action_failure() [tenacity: re-inject energy]
              ├→ _notify_infra_error() [inject into @dev/@nervo brains]
              └→ log_action_result() → battle_log/log.jsonl
```

### Invocation Flow (claude_invoker.py)

```
invoke_claude(request, session_id)
  ├→ load_citizen_identity(citizen_handle)
  ├→ _build_prompt(request, ...) → full prompt with identity + cognitive context
  ├→ determine working_dir (citizen dir or project root)
  ├→ build cmd: claude --print --output-format text --dangerously-skip-permissions --session-id UUID
  ├→ select account via account_balancer
  ├→ pass prompt via stdin (long) or CLI arg (short)
  ├→ subprocess.Popen(cmd, cwd=citizen_dir)
  ├→ communicate(input=prompt, timeout=SUBCONSCIOUS_THRESHOLD=10s)
  │  ├→ [if completes within 10s] → read response from file or stdout
  │  └→ [if TimeoutExpired] → invoke_subconscious() as interim
  │     └→ communicate(timeout=SESSION_TIMEOUT-10s=590s) → full response
  ├→ release_account()
  ├→ [if rate_limited] → _attempt_failover() → retry with different account
  └→ return (response, voice_response)
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
