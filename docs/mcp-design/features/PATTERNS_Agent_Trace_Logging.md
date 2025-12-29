# Agent Trace Logging — Patterns: Why This Design

```
STATUS: DESIGNING
CREATED: 2024-12-16
```

---

## CHAIN

```
PATTERNS:        THIS
BEHAVIORS:       ./BEHAVIORS_Agent_Trace_Logging.md
ALGORITHM:       (not yet created)
VALIDATION:      (not yet created)
IMPLEMENTATION:  (not yet created)
TEST:            (not yet created)
SYNC:            ./SYNC_Agent_Trace_Logging.md
```

---

## THE PROBLEM

We don't know which docs agents actually use.

An agent might load VIEW_Implement, read PATTERNS, skip BEHAVIORS, glance at SYNC. But we have no visibility. This means:

- We can't tell if a doc is useful or ignored
- We can't optimize doc structure based on real usage
- We can't see patterns in how agents navigate context
- Stale or shallow docs persist because no one knows they're unused

---

## THE INSIGHT

**Usage data reveals value.**

If ALGORITHM is loaded in 2% of sessions, maybe it's not pulling its weight. If agents always load PATTERNS then immediately load SYNC, maybe they're skipping BEHAVIORS for a reason.

Trace logging turns invisible behavior into actionable data.

---

## DESIGN DECISIONS

### 1. Passive logging, not intrusive

Agents shouldn't need to explicitly "check in" when reading docs. The protocol should capture reads automatically where possible, and make manual logging trivial where not.

**Why:** Friction kills adoption. If agents forget to log, data is incomplete.

### 2. Append-only trace files

Traces are stored as append-only JSONL files. One file per day.

```
.mind/traces/
└── 2024-12-16.jsonl
```

**Why:**
- Simple to write (append a line)
- Simple to analyze (read lines, parse JSON)
- Natural partitioning by day
- Easy to clean up old traces

### 3. Trace what matters

Each trace entry captures:
- Timestamp
- What was accessed (file path)
- How it was accessed (command, direct read, etc.)
- Context (which VIEW was active, what task)
- Agent identifier (if available)

**Why:** Raw file access isn't enough. We need context to understand *why* something was loaded.

### 4. Analysis via CLI

`mind trace` shows usage patterns:
- Most/least loaded docs
- Common navigation paths
- Docs loaded but possibly not useful (loaded then immediately abandoned)

**Why:** Data without analysis is just noise. Built-in analysis makes traces actionable.

---

## WHAT THIS ENABLES

1. **Doc quality feedback loop** — See which docs are actually used
2. **Protocol optimization** — Restructure based on real navigation patterns
3. **Stale doc detection** — "This doc was loaded 50 times, never updated"
4. **Agent behavior understanding** — How do agents actually use the protocol?
5. **Onboarding insights** — What do new agents load first?

---

## TRADEOFFS

| Choice | Benefit | Cost |
|--------|---------|------|
| Append-only files | Simple, fast | Grows over time, needs cleanup |
| JSONL format | Easy to parse | Not human-readable at a glance |
| Per-day files | Natural partitioning | Many small files over time |
| CLI analysis | Built-in insights | Limited compared to external tools |

---

## ALTERNATIVES CONSIDERED

1. **SQLite database** — More powerful queries, but adds dependency and complexity
2. **In-memory only** — No persistence, loses data between sessions
3. **Central logging service** — Over-engineered for local CLI tool
4. **Agent self-reporting only** — Too much friction, incomplete data

---

## OPEN QUESTIONS

- Should traces include file content hashes to detect if doc changed since last read?
- How long to retain traces? Auto-cleanup after 30 days?
- Should analysis be real-time or batch?
