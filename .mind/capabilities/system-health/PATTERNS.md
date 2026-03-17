# System Health — Patterns

```
STATUS: CANONICAL
CAPABILITY: system-health
```

---

## CHAIN

```
VOCABULARY:      ./VOCABULARY.md
THIS:            PATTERNS.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION.md
HEALTH:          ./HEALTH.md
```

---

## THE PROBLEM

The capability runtime is itself a distributed system — agents claim tasks, run health checks, and process queues. Without self-monitoring:

- Agents silently die (no heartbeat for 10+ minutes) and nobody notices
- Tasks claimed by dead agents stay locked forever — work stops
- Health checks crash and the system loses its ability to detect problems in other modules
- Queues fill up with no workers draining them — backpressure builds invisibly

The capability system monitors everything else, but nothing monitors the capability system. System-health closes that loop.

---

## THE PATTERN

**Self-monitoring meta-capability.**

System-health is a capability that monitors the capability runtime itself. It uses the same check/signal/task mechanism as every other capability, but its targets are the runtime's own components:

1. Cron triggers fire checks every 60s (agents, orphans) or 5m (queue)
2. Stream trigger catches health check crashes reactively
3. Checks query the AgentRegistry and Throttler — the runtime's own internal state
4. Signals escalate through the standard DEGRADED/CRITICAL path
5. Auto-healing fires inline for recoverable problems (orphan task release)
6. Investigation tasks are created for problems requiring agent judgment

```
capability runtime
    │
    ├── AgentRegistry ← H1 monitors (stuck/dead agents)
    ├── Throttler     ← H2 monitors (orphan tasks), H4 monitors (queue health)
    └── health.log    ← H3 monitors (check crashes)
         │
         └── system-health checks (H1-H4) — same mechanism, watching itself
```

---

## PRINCIPLES

### Principle 1: Self-Healing Where Possible

Recoverable problems should fix themselves without creating tasks. Orphan task release (H2) calls `throttler.on_abandon()` inline — the fix happens inside the check, not via a dispatched agent. Only create investigation tasks when the problem requires judgment.

### Principle 2: Escalation by Duration

The same underlying problem (agent not responding) has two severity levels based on time:
- 5 minutes → DEGRADED (stuck — might be on a slow operation)
- 10 minutes → CRITICAL (dead — mark it, release its tasks)

This avoids false positives from slow-but-healthy agents while still catching genuine failures.

### Principle 3: One Check Per Failure Mode

Each health check detects exactly one category of failure. Stuck agents, orphan tasks, check crashes, and queue health are separate checks with separate triggers, separate thresholds, and separate tasks. No god-check that tries to detect everything.

### Principle 4: Runtime Internals as Data Source

System-health checks don't scrape logs or parse files. They query the runtime's own in-memory state — `AgentRegistry.agents`, `Throttler.active`, `Throttler.get_stats()`. This is faster, more reliable, and structurally coupled to the thing being monitored.

### Principle 5: Fail-Open on Self-Failure

If system-health's own checks crash, H3 (health_check_failure) catches it via the error stream. But if H3 itself fails, the system degrades gracefully — other capabilities continue running, they just lose self-monitoring. The meta-check doesn't create infinite recursion.

---

## DESIGN DECISIONS

### Why 60-second check interval for agents?

- Fast enough to detect stuck agents within one heartbeat window
- Cheap — queries in-memory registry, no disk/graph I/O
- Aligns with the expected 60s heartbeat interval

### Why 5 minutes for STUCK, 10 minutes for DEAD?

- 5 minutes catches genuinely stuck agents early enough to help
- 10 minutes avoids killing agents on slow but legitimate operations (large graph queries, long LLM calls)
- The 5-minute window creates an investigation opportunity before auto-marking dead

### Why auto-release orphan tasks instead of creating a task for it?

- Orphan release is mechanical — no judgment needed
- Waiting for an agent to claim a release task adds latency to an already-broken situation
- The `auto_fixed=True` flag in the signal provides audit trail without blocking recovery

### Why a separate queue health check (H4) instead of folding it into H1?

- Different failure mode: queue fullness is about capacity, not individual agent health
- Different trigger interval: 5 minutes (queue trends are slower than heartbeats)
- Different response: may need to spawn agents, not investigate existing ones

### Why stream trigger for H3 instead of cron?

- Check crashes are urgent and unpredictable — polling on a cron would miss the window
- Stream trigger fires reactively when the error actually happens
- Cron would waste cycles checking an error log that's usually empty

---

## SCOPE

### In Scope

- Detecting stuck and dead agents via heartbeat monitoring
- Releasing tasks orphaned by dead agents (auto-healing)
- Detecting health check crashes across all capabilities
- Monitoring task queue capacity and worker availability
- Creating investigation tasks for non-recoverable problems

### Out of Scope

- **Monitoring application logic** — other capabilities handle their own domain health
- **Restarting dead agents** — that's the orchestrator's job; system-health only detects and flags
- **Agent performance** — slow-but-alive agents are not system-health's concern
- **Network/infra health** — FalkorDB connectivity, Render status, etc. are outside this capability
- **Log analysis** — the swarm-driver capability handles log-driven detection
