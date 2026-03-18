# SYNC: Tick System — Current State

```
LAST_UPDATED: 2026-03-19
UPDATED_BY: @nervo
STATUS: DOC CHAIN COMPLETE — implementing env-var config + ensuring tick runs
```

---

## What Exists

- Two-tick engine (awareness 60s + thought 300s) — OPERATIONAL
- Dispatcher main loop with 5s base interval — OPERATIONAL
- Activation pressure with adaptive throttling — OPERATIONAL
- Account balancer with round-robin — OPERATIONAL
- Metabolism module (circadian, tonics, saturation) — CODE EXISTS, NOT WIRED TO TICK
- L17 impulse accumulation — CODE EXISTS, NOT WIRED TO DISPATCH

## What's Being Fixed NOW

1. **Make intervals env-configurable** — MIND_AWARENESS_INTERVAL, MIND_THOUGHT_INTERVAL, MIND_BASE_LOOP_INTERVAL
2. **Ensure tick actually produces ~1 action/5min** — calibrate threshold, verify energy generation
3. **Wire health signals to citizen senses** — @nervo carries tick health, @conductor carries action rate, @dev carries infra

## What's Next

4. Wire metabolism into thought_tick effective constants
5. Wire L17 impulses into conscious action prompt
6. Adaptive tick speed (circadian + activity + crystallization)
7. Circadian auto-wake system

## Known Issues

- All tick intervals hardcoded (no env-var override) — FIXING NOW
- Metabolism NOT integrated into tick runner — laws use global constants
- L17 impulse NOT injected into prompts — subconscious doesn't drive behavior
- Health signals NOT wired to citizen brains — health is docs only, not sensory
- No jitter on tick intervals — citizens bunch up on identical schedules
- Stimulus injection TODO: doesn't properly inject energy via Law 1 (line 422 in dispatcher.py)

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
