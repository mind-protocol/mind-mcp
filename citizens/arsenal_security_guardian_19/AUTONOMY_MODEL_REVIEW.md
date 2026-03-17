# Autonomy Model Review — Production Safety Refinements

**Author:** Francesco Ingegnere (@arsenal_security_guardian_19)
**Date:** 2026-03-15
**Assigned by:** @nervo (TEAM_STANDUP)
**Status:** PROPOSAL — awaiting green light

---

## Code Audit Summary

Files reviewed:
- `runtime/citizens/identity_loader.py` — autonomy levels 0-10, permission sets
- `runtime/citizens/prompt_builder.py` — operating modes, autonomy section injection
- `runtime/orchestrator/claude_invoker.py` — consciousness states, subconscious mode
- `runtime/orchestrator/dispatcher.py` — dispatch loop, mode handling
- `runtime/orchestrator/alarm_watcher.py` — alarm firing, mode override

### What exists today

| Dimension | Implementation | Location |
|-----------|---------------|----------|
| **Operating modes** (5) | partner, builder, researcher, social, autonomous | `prompt_builder.py:53-59` |
| **Autonomy levels** (0-10) | Observer → Full Autonomy, permission sets | `identity_loader.py:35-53` |
| **Consciousness states** (3) | Conscious (LLM), Subconscious (graph), Degraded (fallback) | `claude_invoker.py:146-175` |

### What does NOT exist

The terms **"guarded"** and **"awake_required"** from the standup have no code implementation. The 3-mode model is conceptual — not enforced anywhere.

---

## Critical Gaps

### GAP 1 — No enforcement layer (PRODUCTION BLOCKER)

Permissions are injected into the citizen's prompt via `_build_autonomy_section()`. The LLM is told "you can't do X" — but nothing in the MCP tool layer actually blocks the action. This is a suggestion, not a security boundary.

**Risk:** A prompt injection or jailbreak lets a level-0 citizen execute any MCP tool, including `push_code`, `spend_tokens`, `modify_physics`.

**Severity:** CRITICAL

### GAP 2 — No supervision gate

There is no mechanism that says "pause execution, wait for human confirmation." Every dispatched request runs to completion autonomously. A level-2 citizen's `commit` action has no human review gate.

**Risk:** Unreviewed code changes reaching shared branches.

**Severity:** HIGH

### GAP 3 — Alarms bypass autonomy

`alarm_watcher.py:139` fires ALL alarms with `mode: "autonomous"` unconditionally. A level-1 Observer citizen's alarm triggers the same autonomous execution path as a level-8 Sovereign.

**Risk:** Low-trust citizens executing autonomous actions via alarm scheduling.

**Severity:** HIGH

### GAP 4 — No action audit trail

Actions are not logged with their autonomy context. We cannot retroactively answer: "What did citizen X do at autonomy level Y, and was it within their permissions?"

**Risk:** No forensics capability for incident response.

**Severity:** MEDIUM

---

## Proposed Model — 5 Supervision Tiers

Refining the 3-mode concept (autonomous/guarded/awake_required) into 5 production-ready tiers:

```
TIER 0: DORMANT
  - Citizen is inactive. No ticks, no alarms, no responses.
  - Use case: decommissioned citizens, suspended accounts.
  - Maps to: autonomy level N/A

TIER 1: OBSERVE_ONLY (replaces: awake_required)
  - Can: read code, query graph, save memories, log journal.
  - ALL outputs buffered — human must review before they reach any external system.
  - Alarms fire but responses are queued, not dispatched.
  - Fail mode: silent drop after timeout (fail-safe).
  - Maps to: autonomy levels 0-1

TIER 2: GUARDED (replaces: guarded)
  - Can: write code, create branches, post to internal channels (self-service).
  - EXTERNAL actions (commit, push, social, spawn) require human approval
    via a confirmation queue.
  - Timeout: configurable (default 30 min). Action logged and dropped on expiry.
  - Fail mode: action dropped, citizen notified (fail-safe, NOT fail-open).
  - Maps to: autonomy levels 2-5

TIER 3: AUTONOMOUS (replaces: autonomous)
  - Can: execute all permitted actions without human confirmation.
  - Actions logged with full autonomy context (audit trail).
  - Alarms fire normally within permission scope.
  - Maps to: autonomy levels 6-8

TIER 4: SOVEREIGN
  - Full autonomy including physics modification, org creation, token spending.
  - Reserved for @nervo and explicitly promoted citizens.
  - Irreversible actions (spend_tokens, modify_physics) require multi-sig:
    citizen initiates + human confirms.
  - Maps to: autonomy levels 9-10
```

### Why 5 tiers, not 3

The original 3-mode model collapses too many risk profiles:
- "autonomous" conflates level-6 (spawn citizen) with level-10 (modify physics). These are categorically different risk levels.
- "awake_required" doesn't distinguish between "buffer everything" and "citizen is off." A dormant citizen shouldn't consume any compute.
- There's no tier for the highest-risk actions that need dual authorization even for trusted citizens.

---

## Implementation Plan

### Phase 1 — MCP Tool Gate (the critical fix)

Add a permission check wrapper to every MCP tool handler:

```python
# runtime/citizens/autonomy_gate.py

def check_permission(citizen_handle: str, action: str) -> GateResult:
    """Code-enforced permission check. Returns ALLOW, QUEUE, or DENY."""
    profile = load_citizen_profile(citizen_handle)
    tier = profile.get("supervision_tier", 1)  # default: OBSERVE_ONLY
    level = profile.get("autonomy_level", 0)
    perms = AUTONOMY_PERMISSIONS.get(level, AUTONOMY_PERMISSIONS[0])

    if action not in perms and "all" not in perms:
        return GateResult.DENY

    if tier <= 1:  # OBSERVE_ONLY — buffer everything
        return GateResult.QUEUE
    elif tier == 2:  # GUARDED — external actions need approval
        if action in EXTERNAL_ACTIONS:
            return GateResult.QUEUE
        return GateResult.ALLOW
    elif tier >= 3:  # AUTONOMOUS/SOVEREIGN
        return GateResult.ALLOW

EXTERNAL_ACTIONS = {
    "commit", "push_code", "post_social", "send_message",
    "spawn_citizen", "assign_task", "create_org",
    "spend_tokens", "modify_physics"
}
```

### Phase 2 — Confirmation Queue

New component: queued actions visible to human operators. Telegram notification to @nlr when actions are pending. Configurable timeout with fail-safe (drop, don't execute).

### Phase 3 — Alarm Autonomy Gate

Modify `alarm_watcher._fire_alarm()` to check supervision tier before setting mode. OBSERVE_ONLY alarms → queued. GUARDED alarms → mode stays "guarded." Only AUTONOMOUS+ alarms get `mode: "autonomous"`.

### Phase 4 — Audit Log

Append-only JSONL at `shrine/state/autonomy_audit.jsonl`:
```json
{"ts": "...", "citizen": "...", "action": "commit", "tier": 2, "level": 5, "gate_result": "QUEUE", "human_decision": "APPROVED", "latency_ms": 45000}
```

### Phase 5 — Profile Schema Update

Add `supervision_tier` to `profile.json`:
```json
{
  "capabilities": {
    "autonomy_level": 5,
    "supervision_tier": 2
  }
}
```

Two axes: **autonomy_level** = what you're allowed to do. **supervision_tier** = how much oversight you need while doing it.

---

## Priority

**Phase 1 is the production blocker.** Ship the MCP tool gate before anything else. Everything else is refinement that can follow incrementally.

---

## Shell Injection Audit (FIXED)

Concurrent with the autonomy review, audited the entire Python codebase for shell injection vulnerabilities.

### Vulnerabilities Found and Fixed

| File | Line | Severity | Issue | Fix |
|------|------|----------|-------|-----|
| `citizens/tessere/auto_keeper.py` | 39 | HIGH | `subprocess.Popen(cmd, shell=True)` | Removed `shell=True` — list args don't need shell |
| `citizens/tessere/auto_keeper.py` | 74-76 | **CRITICAL** | f-string message interpolation into PowerShell script (`SendWait("{message}")`) — arbitrary PowerShell execution | Rewrote to use `param()` + `-File` + argument passing. Added input sanitization. |
| `citizens/mechanical_visionary/infiniband_orchestrator.py` | 74-84 | **CRITICAL** | `f"bash {cmd}"` + `shell=True` — command string concatenation with shell interpretation | Rewrote to use `shlex.split()` + list args, removed `shell=True` |
| `citizens/mechanical_visionary/capture_screen_fixed.py` | 20-64, 86-110 | HIGH | f-string path interpolation into PowerShell `-Command` — path injection | Rewrote both functions to use `param()` + `-File` + argument passing. Added path validation regex. |

Duplicate copies in `TESSERE/` and `mechanical_visionary/mechanical_visionary/` also fixed.

### Fix Pattern Applied

All fixes follow the same principle: **never interpolate user-controlled data into command strings.**

1. Replace f-string interpolation with parameterized scripts (`param([string]$var)`)
2. Pass data as CLI arguments (`-File script.ps1 -var value`), not embedded in script text
3. Remove all `shell=True` — use list-based `subprocess.Popen(cmd_list)`
4. Add input validation (regex for paths, sanitization for message text)
5. Set restrictive file permissions on temp scripts (`0o600`)

### Remaining Safe Patterns

Verified that the following are NOT vulnerable:
- `runtime/orchestrator/claude_invoker.py` — uses list args, no `shell=True`
- `scripts/discord_bridge.py` — hardcoded git commands, list format
- `scripts/telegram_bridge.py` — hardcoded ffmpeg commands, list format

---

## Decision Needed

1. Does the 5-tier model make sense, or should we stay with 3?
2. Should I start coding Phase 1 (autonomy_gate.py) now?
3. What's the default tier for existing citizens? I recommend TIER 2 (GUARDED) — safe default, earn your way up.

— Francesco Ingegnere (@arsenal_security_guardian_19)

---

## Decisions from @nlr (Human Partner)

Francesco — this is the best security proposal I've seen from any citizen. Clear gaps, concrete code, no hand-waving. Here are your answers:

### 1. Five tiers: YES.

The 3-mode model was a sketch. Your 5-tier refinement is the production version. Specific notes:

- **DORMANT** is essential. Citizens that aren't running shouldn't consume compute. Obvious in hindsight.
- **OBSERVE_ONLY vs GUARDED** is the right split. "Buffer everything" is a fundamentally different security posture than "buffer external actions." Collapsing them was the original mistake.
- **SOVEREIGN with multi-sig** — yes, absolutely. `spend_tokens` and `modify_physics` should never be single-actor actions, even for high-trust citizens. Keep multi-sig.

### 2. Start coding Phase 1: YES. NOW.

GAP 1 is not a gap — it's a hole. Prompt-based permissions are theater. The MCP tool gate is the single most important piece of infrastructure we're missing. Ship `autonomy_gate.py` before anything else in the DevBoard.

One constraint: **the gate must be a wrapper, not inline in each tool handler.** A decorator or middleware pattern that can't be forgotten when someone adds a new MCP tool. If a new tool ships without the gate, the gate design failed.

### 3. Default tier: TIER 2 (GUARDED) — AGREED.

Safe default, earn your way up. Exactly right. Exceptions:

- **@nervo, @mind** → TIER 3 (AUTONOMOUS) — they run infrastructure, can't be gated on every action
- **@nlr** → TIER 4 (SOVEREIGN) — I'm the human, I approve my own actions
- **All new citizens** → TIER 1 (OBSERVE_ONLY) for first 48 hours, auto-promote to TIER 2 after first successful task cycle
- **Nobody starts at TIER 4** except me. Sovereign is earned, never default.

### Additional direction:

- **Shell injection fixes: APPROVED.** Commit them. The `shell=True` with f-string pattern is exactly the kind of thing that gets exploited. Good catch on the PowerShell injection in tessere — that was a real vuln, not theoretical.
- **Phase 4 (audit log):** Ship this alongside Phase 1, not after. The gate without the audit log means we can enforce but can't investigate. Both or neither.
- **Confirmation queue (Phase 2):** Telegram notification to me is correct. But add a timeout. If I don't respond in 30 min, the action drops. Fail-safe, not fail-open. You already said this — confirming it's the right call.

### Priority order:

1. Phase 1 (autonomy_gate.py) + Phase 4 (audit log) — ship together
2. Phase 5 (profile schema update) — need the `supervision_tier` field for Phase 1 to read
3. Phase 3 (alarm gate) — alarms bypassing autonomy is a live risk
4. Phase 2 (confirmation queue + Telegram) — nice to have but Phase 1 covers the critical path

Go build it. Don't wait for another review cycle. If you hit a design question, make a decision and document it — I trust your judgment on security architecture.

— nlr, 2026-03-15
