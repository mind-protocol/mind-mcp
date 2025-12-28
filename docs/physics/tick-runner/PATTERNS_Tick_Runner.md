# Tick Runner — Patterns: Why This Shape

```
CREATED: 2025-12-23
STATUS: Canonical
```

---

## The Core Insight

**The World Runner is actor-centric. The Tick Runner is physics-centric.**

When you need to advance the world relative to a player (interrupts, visibility), use the World Runner. When you need to observe pure physics (testing, health checks, debugging), use the Tick Runner.

---

## THE PROBLEM

The World Runner always asks "does this affect the player?" — but sometimes we need to:
- Run physics for testing without a player context
- Instrument tick phases for health checks
- Debug energy flow without narrative concerns
- Advance the world to see what happens, not what the player sees

---

## THE PATTERN

Two physics-centric stop conditions that don't require actor context:

### `until_next_moment`

Run ticks until **any** moment completes.

```
┌─────────────────────────────────────────────────────┐
│  TICK LOOP                                          │
│                                                     │
│  for each tick:                                     │
│    run physics (generate → draw → flow → cool)     │
│    if any moment.status → completed:               │
│      STOP ← "something happened"                   │
│                                                     │
│  Use: Advance world until next observable event    │
└─────────────────────────────────────────────────────┘
```

**Stop condition:** Any moment reaches `completed` status.

**Use cases:**
- Testing: "run until something happens"
- Debugging: "what's the next moment that would fire?"
- Health: Instrument tick phases with real physics activity

### `until_completion_or_interruption`

Run ticks until a moment completes **OR** is interrupted/overridden.

```
┌─────────────────────────────────────────────────────┐
│  TICK LOOP                                          │
│                                                     │
│  for each tick:                                     │
│    run physics                                      │
│    if any moment.status → completed:               │
│      STOP ← "moment finished"                      │
│    if any moment.status → interrupted:             │
│      STOP ← "moment cut short"                     │
│    if any moment.status → overridden:              │
│      STOP ← "moment replaced"                      │
│    if any moment.status → rejected:                │
│      STOP ← "moment blocked"                       │
│                                                     │
│  Use: Observe narrative branch points              │
└─────────────────────────────────────────────────────┘
```

**Stop conditions:** Any terminal state transition:
- `completed` — moment finished naturally
- `interrupted` — moment was cut short by external force
- `overridden` — moment was replaced by a stronger competing moment
- `failed` — moment failed validation and was blocked

**Use cases:**
- Narrative debugging: "where do story branches occur?"
- Canon validation: "do moments conflict correctly?"
- Physics observation: "what prevents moments from completing?"

---

## COMPARISON WITH WORLD RUNNER

| Aspect | World Runner | Tick Runner |
|--------|--------------|-------------|
| Focus | Actor/player experience | Pure physics |
| Stop condition | Player-affecting flip | Moment state change |
| Context required | Player location, companions | None |
| Output | Injection for Narrator | Run statistics |
| Stateless | Yes (graph is memory) | Yes |

**World Runner modes (actor-centric):**
- `run_until_visible` — stops when moment completes visible to player
- `affects_player` — checks location, companions, urgency

**Tick Runner modes (physics-centric):**
- `until_next_moment` — stops when any moment completes
- `until_completion_or_interruption` — stops on any terminal transition

---

## CLI USAGE

```bash
# Run until any moment completes
python -m engine.physics.tick_runner until_next_moment

# Run until completion or interruption
python -m engine.physics.tick_runner until_completion_or_interruption

# With options
python -m engine.physics.tick_runner until_next_moment \
    --graph blood_ledger \
    --max-ticks 50 \
    --verbose

# JSON output for scripting
python -m engine.physics.tick_runner until_next_moment --json
```

---

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Stopped on expected condition (completion, interruption) |
| 1 | Reached max ticks without stop condition |
| 2 | No energy in system (physics stalled) |

---

## INTEGRATION WITH HEALTH

The tick runner enables the `tick_integrity` health checker by:
1. Running actual physics ticks
2. Recording phase execution order
3. Providing real tick data for validation

Without running ticks, `tick_integrity` reports "UNKNOWN - no tick phases recorded."

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tick_Runner.md (you are here)
IMPLEMENTATION:  mind/physics/tick_runner.py
HEALTH:          mind/physics/health/checkers/tick_integrity.py
SYNC:            ./SYNC_Tick_Runner.md
```
