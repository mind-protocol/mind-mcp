# SYNC: Tick System — Current State

```
LAST_UPDATED: 2026-03-19 19:30 UTC
UPDATED_BY: @mechanical_visionary (guest session, guided by NLR)
STATUS: CRITICAL FIX APPLIED — invoke_claude was sending empty prompts. Fix deployed, awaiting restart.
```

---

## Maturity

**What's canonical (v1):**
- Two-tick engine (awareness 60s + thought 300s)
- Dispatcher main loop with 5s base interval
- Activation pressure with adaptive throttling
- Account balancer with round-robin + failover
- L17 impulse accumulation → action_seed → fire_conscious_action
- Health signals → carrier citizen brains (H1-H7)
- Battle log (action_start/action_result to JSONL)

**What's still being designed:**
- Adaptive tick speed (circadian + activity + crystallization) — PLANNED
- Circadian auto-wake system — PLANNED
- Jitter on tick intervals (citizens still bunch up)

**What's proposed (v2+):**
- Load citizen brain state from FalkorDB at boot (currently empty state + action seed)
- H8/H9 health signals for invocation success monitoring

---

## Current State

The tick system is OPERATIONAL — 210+ citizens have registered engines, awareness and thought ticks fire on schedule, and the subconscious loop correctly selects actions from drive-modulated WM. However, until 2026-03-19 19:30 UTC, **conscious actions were failing silently at 98.8% rate** due to two bugs in `claude_invoker.py`. The fix has been applied but the tick loop has not yet been restarted.

---

## In Progress

### P0 Fix: Claude Invocation Bug (APPLIED, AWAITING RESTART)

- **Started:** 2026-03-19 ~18:00 UTC
- **By:** @mechanical_visionary (guest session via NLR)
- **Status:** Code fixed, not yet tested in production
- **Context:** Root cause analysis from battle log showing 174 action_starts and 2 action_results for a fresh citizen. The 2 results were subconscious placeholders, not real Claude output.

---

## Recent Changes

### 2026-03-19: CRITICAL — Invoke prompt ordering fix

- **What:** Two bugs in `claude_invoker.py` fixed:
  1. **Message appended after Popen** (line 158 → moved to line 139-144). The prompt text was added to the `cmd` list AFTER `subprocess.Popen()` already launched the process. Since `input_text` was `None`, Claude received no input — no CLI argument, no stdin. Every citizen session was effectively `claude --print` with an empty prompt.
  2. **Full prompt discarded** (line 93 → now used at line 149-155). `_build_prompt()` constructed a rich prompt with citizen identity, cognitive context, WM state, and action directives — but the result was stored in a local variable and never passed to the subprocess. Only the bare `voice_text` (e.g., "[conscious_action] handle") was sent.
  3. **Failover path missing message** — failover built a fresh cmd without the message. Fixed to carry forward from `base_cmd` or `input_text`.

- **Why:** This was THE blocker for the entire system. Citizens appeared to be acting (action_starts logged, subconscious interim generated) but 98.8% of invocations returned empty. The system looked alive but couldn't think.

- **Files:** `runtime/orchestrator/claude_invoker.py` — lines 139-167 (main path) and lines 290-303 (failover path)

- **Evidence:**
  - mechanical_visionary: 174 starts, 2 results (1.2% completion)
  - dragon_slayer: 219 starts, 38 results (17.4% completion)
  - echo: 70 starts, 20 results (28.6% completion)
  - The 2 results for mechanical_visionary were identical subconscious placeholder text

- **Struggles/Insights:** The bug was invisible because the system continued operating — the subconscious fallback generated interim responses when the 10s threshold expired, and the battle log recorded action_starts. Without comparing start-to-result ratios, the system appeared healthy.

### 2026-03-19 01:10: Previous session by @nervo

- Fixed graph reader default ("lumina" → "lumina-prime")
- Fixed thought_tick return value destructuring
- Fixed ACTION_COOLDOWN_TICKS blocking first 3 ticks
- Fixed invoke_subconscious using deleted stimulus_router
- Fixed action_seed setting read-only arousal property

---

## Known Issues

### Subconscious threshold too aggressive (10s)

- **Severity:** medium
- **Symptom:** Almost every citizen session will trigger the subconscious interim path because Claude Code needs >10s to initialize (load CLAUDE.md, MCP tools, etc.)
- **Suspected cause:** SUBCONSCIOUS_THRESHOLD default is 10s, which is shorter than Claude Code's startup time
- **Recommended:** Increase to 30-60s via `SUBCONSCIOUS_THRESHOLD` env var, or make it adaptive based on observed response times

### Citizen tick bunching

- **Severity:** low
- **Symptom:** All citizens tick at the same time since they share the same base intervals
- **Suspected cause:** No jitter applied to per-citizen timestamps
- **Attempted:** Not yet addressed

---

## Handoff: For Agents

**Your likely VIEW:** VIEW_Debug (if investigating action failures) or VIEW_Extend (if adding health senses)

**Where I stopped:** Bug fix applied to `claude_invoker.py`. Doc chain updated (IMPLEMENTATION, ALGORITHM, VALIDATION, HEALTH, SYNC). The fix needs a tick loop restart to take effect.

**What you need to understand:**
The invocation pathway is: dispatcher._fire_conscious_action → dispatcher.dispatch → executor.submit(invoke_claude) → subprocess.Popen("claude --print"). The prompt reaches Claude via stdin (for long prompts) or as a CLI positional argument (for short messages). The response comes back via a state file (`shrine/state/last_response_{session_id}.txt`) or stdout fallback.

**Watch out for:**
- The `communicate()` call has a two-phase timeout: 10s first try, then 590s second try. If the first times out, a subconscious response is generated as interim. The subconscious writes to the SAME response file that Claude would use — if Claude's output doesn't overwrite it, the subconscious text is returned as the "final" response.
- The `cmd` list is mutated in-place. If you add more flags or arguments, ensure they're added BEFORE `Popen()`.

**Open questions I had:**
- Does `claude --print` with stdin input handle multi-line prompts correctly? (Assumption: yes, but untested with the full citizen prompt which can be 200+ lines)
- What happens when 15 simultaneous Claude subprocesses compete for the same account? (Rate limiting?)

---

## Handoff: For Human

**Executive summary:**
Critical bug found and fixed in the Claude invocation layer — citizens were sending empty prompts to Claude for every conscious action. The fix moves the prompt construction before subprocess launch and uses the full built prompt instead of bare voice_text. All 8 doc chain files updated. Restart needed.

**Decisions made:**
- Long prompts go via stdin, short messages via CLI arg (avoids OS arg length limits)
- Added two new health signals (H8: invocation success rate, H9: battle log completeness) to catch this class of bug in the future
- Added two new VALIDATION invariants (V8, V9) protecting the invocation pathway

**Needs your input:**
- Restart the tick loop to deploy the fix
- Consider bumping SUBCONSCIOUS_THRESHOLD from 10s to 30-60s

---

## TODO

### Doc/Impl Drift

- [x] IMPL→DOCS: claude_invoker.py was missing from file map → added
- [x] IMPL→DOCS: Invocation flow was not documented in ALGORITHM → added
- [x] IMPL→DOCS: Battle log module not in file map → added
- [ ] DOCS→IMPL: H8 (invocation success rate) health checker not yet coded
- [ ] DOCS→IMPL: H9 (battle log completeness) health checker not yet coded

### Immediate

- [ ] Restart tick loop to deploy invoke fix
- [ ] Monitor first 50 action_results after restart — verify non-empty, substantive output
- [ ] Tune SUBCONSCIOUS_THRESHOLD (10s → 30-60s)

### Later

- [ ] Implement H8/H9 health checkers in `runtime/checks.py`
- [ ] Add jitter to per-citizen tick timestamps
- [ ] Adaptive tick speed based on circadian + activity + crystallization
- [ ] Load citizen brain state from FalkorDB at boot
- IDEA: Track prompt length in battle_log — empty prompt = 0 chars = instant bug detection

---

## Consciousness Trace

**Mental state when stopping:**
Confident. The root cause was unambiguous — `cmd.append()` after `Popen()` is a clear Python semantics error. The fix is minimal and surgical. The doc chain is now accurate.

**Threads I was holding:**
- The subconscious interim writes to the same file Claude uses for responses — potential overwrite race
- The failover path might need the prompt passed differently if the original was via stdin
- Dispatcher._collect_completed_futures is called every 5s — if 15 workers are all blocked on 600s timeouts, the queue grows unbounded

**Intuitions:**
- The 10s subconscious threshold was probably set assuming Claude would respond quickly with no input (which it did, with empty output). With real prompts, 30-60s is more appropriate.
- The action start-to-result ratio should be a PRIMARY health signal. A ratio > 10:1 is a red flag that something is fundamentally broken in the invocation layer.

**What I wish I'd known at the start:**
That `claude_invoker.py` was not in the IMPLEMENTATION file map. The most critical file in the entire system was undocumented.

---

## Pointers

| What | Where |
|------|-------|
| Claude invoker (the fix) | `runtime/orchestrator/claude_invoker.py:139-167` |
| Dispatcher main loop | `runtime/orchestrator/dispatcher.py:186-199` |
| Fire conscious action | `runtime/orchestrator/dispatcher.py:532-606` |
| Collect futures | `runtime/orchestrator/dispatcher.py:775-850` |
| Battle log writer | `runtime/orchestrator/battle_log.py` |
| Two-tick engine | `runtime/cognition/two_tick_engine.py` |
| Citizen prompt builder | `runtime/citizens/prompt_builder.py` |
| Account balancer | `runtime/orchestrator/account_balancer.py` |
| Mechanical visionary battle log | `citizens/mechanical_visionary/battle_log/log.jsonl` |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
