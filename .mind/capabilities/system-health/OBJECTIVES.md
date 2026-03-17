# OBJECTIVES — System Health

```
STATUS: CANONICAL
CAPABILITY: system-health
CREATED: 2026-03-15
```

---

## CHAIN

```
THIS:            OBJECTIVES.md (you are here - START HERE)
VOCABULARY:      ./VOCABULARY.md
VALIDATION:      ./VALIDATION.md
HEALTH:          ./HEALTH.md
IMPLEMENTATION:  ./IMPLEMENTATION.md
SYNC:            ./SYNC.md

RUNTIME:         ./runtime/checks.py
TASKS:           ./tasks/
```

---

## PRIMARY OBJECTIVES (ranked)

1. **Detect stuck and dead agents before tasks rot** — Agents that stop heartbeating hold claimed tasks hostage. Without detection, the work queue silently drains as tasks sit in limbo. The 5-minute STUCK threshold gives agents time to recover from slow operations; the 10-minute DEAD threshold triggers auto-release of their tasks. This is the #1 objective because a single dead agent can block the entire swarm's throughput.

2. **Auto-heal what can be auto-healed** — Orphan tasks (claimed by dead agents) can be released back to pending without human intervention. This is the highest-value self-repair in the system: it turns a queue-blocking failure into a recoverable event. Auto-release runs every 60 seconds, meaning a dead agent's tasks are available again within 2 minutes at worst.

3. **Accurate severity classification** — DEGRADED (stuck agent, full queue) and CRITICAL (dead agent, stuck + full queue) must map precisely to conditions. Over-escalation wastes human attention. Under-escalation lets critical failures fester. The severity contract is simple: CRITICAL means "tasks are being lost right now." DEGRADED means "tasks may be lost soon."

4. **Self-monitoring — detect own failures** — A health check that crashes silently is the worst outcome: the system reports healthy because no alarm fired. H3 (health_check_failure) uses stream-based triggers on `.mind/logs/health.log` to catch check.py crashes immediately, not on the next cron cycle.

5. **Queue visibility** — When the task queue is full (>80%) with no active workers or stuck workers, the system is about to stall. Queue health (H4) provides the early warning that prevents the stall from becoming a full stop.

## NON-OBJECTIVES

- **Agent lifecycle management** — System-health detects stuck/dead agents. It does NOT restart them, spawn replacements, or manage their lifecycle. That's the orchestrator's job. System-health fires the signal; the orchestrator acts on it.
- **Task scheduling or priority** — System-health monitors queue fullness, not which tasks should run next. Task dispatch, priority ordering, and agent-task matching belong to the swarm-driver.
- **Application-level correctness** — System-health verifies that the capability runtime itself works (agents heartbeat, tasks flow, checks run). It does NOT verify that the agents' work output is correct. That's each capability's own HEALTH checks.
- **Performance optimization** — Thresholds (5min/10min/80%) are conservative and fixed. System-health is not trying to optimize throughput. It's trying to prevent total failure. Tuning belongs to the orchestrator.

## TRADEOFFS (canonical decisions)

- When **detection speed** conflicts with **false positive rate**, choose **fewer false positives**. A 5-minute STUCK threshold means genuinely slow operations aren't falsely flagged. The cost is that a truly stuck agent sits for 5 minutes before detection. This is acceptable because the alternative (false positives) destroys trust in the monitoring system (V6).
- When **auto-heal coverage** conflicts with **safety**, choose **safety**. Only TASK_ORPHAN is auto-fixed. AGENT_STUCK, HEALTH_CHECK_FAILED, and QUEUE_UNHEALTHY all require investigation. Auto-fixing a stuck agent (e.g., by killing it) risks data loss. We accept slower recovery to prevent unsafe auto-actions (V3).
- When **signal completeness** conflicts with **check performance**, choose **completeness**. Each signal must carry the full context its task handler needs (agent IDs, task lists, counts). The alternative — returning a boolean and making the handler re-query — doubles the work and introduces race conditions (V7).
- We accept **lazy imports inside check functions** to preserve **check isolation**. Module-level imports create circular dependency risk and mean one broken import kills all checks. The per-call import cost is negligible at 60s+ intervals (V8).

## SUCCESS SIGNALS (observable)

- Zero orphan tasks persist for more than 2 minutes (auto-release within 2 cron cycles)
- No agent sits STUCK for more than 5 minutes without a signal firing
- No agent sits DEAD for more than 10 minutes without its tasks being released
- Zero false positives on a healthy system (all checks return Signal.healthy())
- A crashed check.py triggers H3 within seconds (stream-based, not cron-based)
- Queue > 80% with no workers triggers DEGRADED signal within 5 minutes
- Each health signal contains enough context for its task handler to act without re-querying
- Runtime thresholds in checks.py match VOCABULARY.md exactly (no drift)
