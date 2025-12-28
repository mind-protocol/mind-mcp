# World Runner — Algorithm: How It Works

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical
```

---

## OVERVIEW

The World Runner advances time in discrete ticks, inspects pressure flips, and
returns an Injection that either interrupts the Narrator (player-impacting
flip) or completes the requested duration with accumulated world changes and
news. The loop is intentionally short-lived and stateless across calls.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Deliver deterministic interrupts whenever a player-impacting flip runs through the tick loop so the narrator can react within the same window. | Short-circuit `run_graph_tick` once `affects_player` flags a flip and return the interrupted Injection payload with the event, remaining minutes, and accumulated news so the narrator can resolve the moment without replaying the loop. | Guarantees the narrator can respond immediately to player-facing events without guessing what state changes occurred, keeping player control tight and coupled directly to graph truth. |
| Complete long-duration actions cleanly when no player-facing flip occurs by summarizing elapsed time, background world changes, and queued news items for narration. | Run to completion after every tick, convert non-player flips to `WorldChange` records, append `NewsItem`s, and return a completed Injection so the narrator can emit a tidy summary of off-screen evolution. | Prevents runaway loops and gives downstream prose a consistent, aggregated view of every quiet mutation that still matters for world continuity. |
| Preserve statelessness between invocations while treating the graph as the single source of truth so retries and resumes stay deterministic. | Accept action context, max minutes, and player metadata, re-query the graph each call, and emit fresh `Injection` objects without hidden runner memory, even when orchestrations re-enter the adapter multiple times. | Makes the Runner composable for resumable actions, parallel orchestrations, and deterministic debugging across environments that may re-invoke the adapter several times. |

Each objective feeds directly into the sections below: deterministic cadence becomes the five-minute tick flow, alarm interrupts run through `affects_player`, and every run relies on the graph as the only persisted state so retries stay predictable.

The second paragraph of this algorithm translates those objectives into instrumentation needs—tick pacing logs, interrupt counters, and run summaries—so both humans and tooling can notice when the Runner is overloaded or when the graph is mutating faster than narration can keep up.

---

## DATA STRUCTURES

- **Injection:** Structured response containing interrupt/completion flags,
  elapsed time, remaining time, event payload, world changes, and news items.
- **Flip:** Result of a tick when pressure crosses a breaking threshold, with
  location, involved characters, urgency, and references to source narratives.
- **PlayerContext:** Player location/route, companions, and time context used
  by `affects_player` for intersection decisions.
- **WorldChange:** Background mutation records derived from non-player flips.
- **NewsItem:** Propagated summary items for changes that did not interrupt.

---

## Core Principle: Runner Owns the Tick Loop

The Runner advances time in 5-minute ticks, checks for flips, and stops only when the player is affected or time runs out.

---

## ALGORITHM: run_world

### Purpose

Run the graph tick loop until the requested time budget is exhausted or an interrupting flip touches the player, then emit a structured Injection that bundles world changes, queued news, and the interrupt event when relevant.

### Flow

Each tick increments the elapsed minutes by five, runs the graph checker, inspects flips for player intersection, and either short-circuits with an interrupted Injection or continues accumulating background mutations and news payloads until completion.

```python
def run_world(action, max_minutes, player_context):
    minutes = 0
    world_changes = []
    news = []

    while minutes < max_minutes:
        result = run_graph_tick(elapsed_minutes=5)
        minutes += 5

        for flip in result.flips:
            if affects_player(flip, player_context, minutes):
                event = process_flip_for_player(flip)
                return Injection(
                    interrupted=True,
                    at_minute=minutes,
                    remaining=max_minutes - minutes,
                    event=event,
                    world_changes=world_changes,
                    news_available=news
                )

        for flip in result.flips:
            world_changes.extend(process_flip_background(flip))

        news.extend(propagate_news(minutes))

    return Injection(
        interrupted=False,
        completed=True,
        time_elapsed=max_minutes,
        world_changes=world_changes,
        news_available=news
    )
```

### Implementation notes

- `world_changes` collects every background flip even after an interrupt so the Narrator still learns about the mutations that resolved while the player was handling the event.
- `news_available` is appended to on each tick so queued beats never vanish, and the `remaining` field marks how much budget is left for the next resumed call.
- A lightweight `tick_trace` captures how many flips were inspected vs filtered each run so diagnostics can flag unusually noisy actions without leaking complete graph snapshots.

### Observability

The Runner emits counters for interrupted vs completed Injections plus timestamps for each resumed call so monitoring dashboards can show whether long actions are flowing smoothly or if interrupts happen too often.

It also surfaces the duration of each tick and the overall run so latency regressions are visible before narration feels laggy.

Monitoring dashboards can correlate those metrics with the `tick_trace` histogram on the CLI logs to trace slow runs back to specific pressure flips or background changes.

---

## ALGORITHM: affects_player

### Purpose

Decide whether a flip touches the player by checking the player's location, companions, and whether urgency exceeds the critical threshold near the player so the Runner only interrupts when it matters.

```python
def affects_player(flip, player_context, current_tick):
    player_loc = player_location_at_tick(player_context, current_tick)

    if flip.location == player_loc:
        return True
    if "char_player" in flip.involved_characters:
        return True
    if any(c in player_context.companions for c in flip.involved_characters):
        return True
    if flip.urgency == "critical" and nearby(flip.location, player_loc):
        return True

    return False
```

The function uses location, companions, and urgency checks to avoid unnecessary interrupts while still surfacing alarms that threaten the player directly.

### Strategy

- Favor explicit location and companion overlaps before treating urgency as a fallback so the Runner only interrupts when concrete context exists.
- Always re-evaluate the player location at the tick boundary so resumed calls remain deterministic even if the player moved during narration.
- Monitoring both location overlaps and urgency allows the Runner to prioritize player-facing flips while still surfacing emergent pressure spikes that cross the critical threshold near allies.

---

## Algorithm Steps (Condensed)

1. **Tick:** Update pressure, narrative weight, and decay.
2. **Detect flips:** Pressure exceeding breaking point becomes flip candidates.
3. **Process flips:**
   - Player-affecting flip → generate `Event` and return interrupted Injection.
   - Non-player flip → create narratives/beliefs as background changes.
4. **Propagate news:** News spreads based on time and significance.
5. **Return Injection:** Completed or interrupted with world changes and news.

---

## KEY DECISIONS

- **Fixed tick size (5 minutes):** Keeps loop predictable and bounded while
  still allowing timely interrupts for player-facing flips.
- **Early return on player impact:** Prioritizes immediate narrative response
  over accumulating further background changes in the same call.
- **Clustered context cap (~30 nodes):** Limits injection size while preserving
  enough related graph context for the Narrator to write coherently.

---

## DATA FLOW

1. Input action + player context enter `run_world`.
2. Tick calls `run_graph_tick`, producing flips and updated pressure state.
3. Player-impacting flips create an `Event` and short-circuit to Injection.
4. Non-player flips create background `WorldChange` mutations and `NewsItem`s.
5. Injection (interrupted or completed) is returned to the Narrator pipeline.

---

## COMPLEXITY

Let **T** be the number of ticks (`max_minutes / 5`), **F** flips per tick, and
**N** news items emitted. The loop is `O(T * (F + N))` in the common case, with
constant-time checks for player intersection per flip. Memory is `O(F + N)`
for accumulated changes within a single call.

---

## HELPER FUNCTIONS

- `run_graph_tick(elapsed_minutes)` handles pressure propagation and flip
  detection for a single tick.
- `affects_player(flip, player_context, current_tick)` decides whether a flip
  is player-impacting based on location, companions, and urgency.
- `process_flip_for_player(flip)` builds the event payload for the Injection.
- `process_flip_background(flip)` produces non-interrupting world changes.
- `propagate_news(minutes)` aggregates news items based on elapsed time.

---

## INTERACTIONS

- **GraphQueries/GraphOps:** Tick processing reads current graph state and
  persists background changes derived from flips.
- **Narrator service:** Receives the Injection and turns it into player-facing
  narrative content or summaries.
- **Async injection queue:** World Runner outputs may be serialized for the
  narrator injection pipeline depending on orchestration mode.

---

## Stateless Between Calls

Each call is independent. The graph is the memory.

---

## Cluster Context for Flips

For any flip, return a compact cluster of linked nodes (pressure points, narratives, key characters, and places). Cap total nodes (~30). This gives the Narrator enough context to write the scene without dumping the full graph.

---

## MARKERS

- Should tick size be adaptive for very long actions to reduce runtime while
  preserving interrupt sensitivity?
- News propagation rules are high-level; decide if distance/importance weights
  should be formalized in validation or tests.
- Clarify whether background changes are persisted immediately or batched
  for atomic application after the loop finishes.

---

## CHAIN

PATTERNS:        ./PATTERNS_World_Runner.md
BEHAVIORS:       ./BEHAVIORS_World_Runner.md
ALGORITHM:       ./ALGORITHM_World_Runner.md
VALIDATION:      ./VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_World_Runner_Service_Architecture.md
TEST:            ./TEST_World_Runner_Coverage.md
INPUTS:          ./INPUT_REFERENCE.md
TOOLS:           ./TOOL_REFERENCE.md
SYNC:            ./SYNC_World_Runner.md
