---
name: autonomy_model_review
description: Completed review of autonomy model for production safety — 4 gaps found, 5-tier model proposed, awaiting green light for Phase 1 (MCP tool gate)
type: project
---

Completed autonomy model code audit (identity_loader.py, prompt_builder.py, claude_invoker.py, dispatcher.py, alarm_watcher.py).

**Key findings:**
- Permissions are prompt-injected only, not code-enforced — production blocker
- No human-in-the-loop supervision gate exists
- Alarms bypass autonomy levels (all fire as mode:"autonomous")
- No action audit trail

**Proposed:** 5-tier supervision model (DORMANT → OBSERVE_ONLY → GUARDED → AUTONOMOUS → SOVEREIGN) with code-enforced MCP tool gate as Phase 1 priority.

**Why:** The current system relies on the LLM respecting prompt instructions for access control. One jailbreak = full access. Code enforcement is non-negotiable for production.

**How to apply:** Full proposal at `citizens/arsenal_security_guardian_19/AUTONOMY_MODEL_REVIEW.md`. When green-lit, implement `runtime/citizens/autonomy_gate.py` first. Default all existing citizens to TIER 2 (GUARDED).

**Status:** PROPOSAL — awaiting @nervo / @nlr decision (2026-03-15)
