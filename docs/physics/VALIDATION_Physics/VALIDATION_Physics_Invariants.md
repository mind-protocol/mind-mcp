# Physics — Validation: Invariants

```
STATUS: CANONICAL
UPDATED: 2025-12-21
```

---

## CHAIN

```
PATTERNS:       ../PATTERNS_Physics.md
BEHAVIORS:      ../BEHAVIORS_Physics.md
ALGORITHMS:     ../ALGORITHM_Physics.md
VALIDATION:     ./VALIDATION_Physics_Invariants.md
IMPLEMENTATION: ../IMPLEMENTATION_Physics.md
HEALTH:         ../HEALTH_Physics.md
SYNC:           ../SYNC_Physics.md
```

---

## INVARIANTS

The checks below define the non-negotiable physics rules. They are written
as validation anchors so any deviation is treated as a defect, not a
variance in interpretation or runtime configuration.
Review these invariants whenever physics constants or schema fields change.

## PROPERTIES

Physics behavior is deterministic for a fixed graph state, conserves energy
with explicit decay, and keeps canon ordering stable regardless of display
speed. These properties are validated by the invariants and benchmarks here.
We expect repeatable outputs for identical seeds and graph snapshots.

## ERROR CONDITIONS

Validation must flag missing ticks, invalid status enums, weight values
outside bounds, or illegal links (e.g., THEN to non-Moment nodes). Handler
scope violations and non-deterministic flips are critical errors.
These should fail validation immediately rather than log and continue.

## TEST COVERAGE

Physics validation relies on integration tests in `mind/tests/` plus schema
checks in the graph-health suite. See `docs/physics/TEST_Physics.md` for
specific cases, coverage notes, and known gaps.
Manual verification notes supplement tests when dependencies are missing.

## VERIFICATION PROCEDURE

1. Run automated physics and schema tests from `mind/tests/`.
2. Execute a short simulated scenario at 1x and 3x to compare canon chains.
3. Inspect graph queries for invariant violations (status, weights, links).
4. Review SYNC notes for open gaps before claiming completion.
5. Record deviations or skipped steps in `docs/physics/SYNC_Physics.md`.

## SYNC STATUS

Validation guidance is aligned with `docs/physics/SYNC_Physics.md`. Update the
SYNC file whenever invariants or verification steps change to avoid drift.
If SYNC is stale, treat the validation result as incomplete.

## Core Invariants

These must **always** hold. Violations indicate bugs.

### I1: Single Source of Truth

**The graph is the only truth.**

```python
def check_single_truth():
    # No state stored outside graph
    # (This is architectural, not queryable)
    # Verify: handlers don't cache state
    # Verify: no files store moment state
    # Verify: display queue reads from graph
    pass
```

### I2: Graph Is Always Running

**The graph never stops.**

```python
def check_graph_alive():
    # Physics tick runs continuously
    # (Verify via tick counter)
    assert physics.tick_count > 0
    assert physics.is_running == True
```

### I3: History Is Immutable

**THEN links never deleted or modified.**

```python
def check_then_immutable():
    # THEN links only from completed moments
    assert query("""
        MATCH (m:Moment)-[:THEN]->()
        WHERE m.status NOT IN ["completed", 'active']
        RETURN count(m)
    """) == 0

    # THEN links must have tick
    assert query("""
        MATCH ()-[t:THEN]->()
        WHERE t.tick IS NULL
        RETURN count(t)
    """) == 0

    # No THEN links deleted in test run
    # (Track count before/after)
```

### I4: Handler Isolation

**Handler only writes for its character.**

```python
def check_handler_isolation():
    # All moments created by handler X are ATTACHED_TO character X
    # (This requires tracking handler outputs)

    # Verify in handler code:
    # - No writes to other character's moments
    # - No direct graph modifications outside ATTACHED_TO scope
    pass
```

### I5: Canon Is Final

**Once recorded, it happened.**

```python
def check_canon_final():
    # Spoken moments cannot revert to possible
    assert query("""
        MATCH (m:Moment)
        WHERE m.status = 'completed' AND m.previous_status = 'possible'
        RETURN count(m)
    """) == 0  # This would require tracking previous_status

    # THEN links are permanent
    # (No DELETE on THEN links in codebase)
```

### I6: Speed Doesn't Change Content

**Same events at any speed.**

```python
def check_speed_invariance():
    # Run same scenario at 1x and 3x
    # Compare THEN link chains
    # Should be identical (display differs, canon same)

    graph_state_1x = run_scenario_at_speed('1x')
    graph_state_3x = run_scenario_at_speed('3x')

    assert get_then_chains(graph_state_1x) == get_then_chains(graph_state_3x)
```

### I7: Energy Conservation

**Energy in = energy out + decay losses.**

```python
def check_energy_conservation():
    # Sum of all weights before tick
    total_before = query("MATCH (m:Moment) RETURN sum(m.weight)")

    # Tick
    physics.tick()

    # Sum after = before - decay + injection
    total_after = query("MATCH (m:Moment) RETURN sum(m.weight)")
    expected_decay = total_before * DECAY_RATE
    expected_injection = calculate_expected_injection()

    assert abs(total_after - (total_before - expected_decay + expected_injection)) < 0.01
```

### I8: Physics Is The Scheduler

**No arbitrary triggers, cooldowns, or caps.**

```python
def check_physics_scheduling():
    # Handlers only triggered by flip
    # (Verify handler trigger conditions in code)

    # No cooldown logic in handler system
    # No artificial caps on handler runs per tick
    pass
```

---

## Graph State Invariants

### Moment Status Consistency

```python
def check_status_consistency():
    # Status must be valid enum
    assert query("""
        MATCH (m:Moment)
        WHERE NOT m.status IN ['possible', 'active', "completed", "possible", 'decayed']
        RETURN count(m)
    """) == 0

    # Spoken moments must have tick_resolved
    assert query("""
        MATCH (m:Moment)
        WHERE m.status = 'completed' AND m.tick_resolved IS NULL
        RETURN count(m)
    """) == 0

    # Decayed moments must have tick_resolved
    assert query("""
        MATCH (m:Moment)
        WHERE m.status = 'decayed' AND m.tick_resolved IS NULL
        RETURN count(m)
    """) == 0
```

### Weight Bounds

```python
def check_weight_bounds():
    # Weight must be 0-1
    assert query("""
        MATCH (m:Moment)
        WHERE m.weight < 0 OR m.weight > 1
        RETURN count(m)
    """) == 0

    # CAN_SPEAK weight must be 0-1
    assert query("""
        MATCH ()-[r:CAN_SPEAK]->()
        WHERE r.weight < 0 OR r.weight > 1
        RETURN count(r)
    """) == 0
```

### Link Validity

```python
def check_link_validity():
    # CAN_SPEAK must originate from Character
    assert query("""
        MATCH (n)-[:CAN_SPEAK]->(:Moment)
        WHERE NOT n:Character
        RETURN count(n)
    """) == 0

    # ATTACHED_TO targets must be valid types
    assert query("""
        MATCH (m:Moment)-[:ATTACHED_TO]->(target)
        WHERE NOT (target:Character OR target:Place OR target:Thing
                   OR target:Narrative)
        RETURN count(m)
    """) == 0

    # THEN links connect Moments only
    assert query("""
        MATCH (a)-[:THEN]->(b)
        WHERE NOT (a:Moment AND b:Moment)
        RETURN count(a)
    """) == 0
```

---

## Physics Invariants

### Decay Is Time-Based

```python
def check_time_based_decay():
    # At 3x speed, total decay over 10 seconds real-time
    # should equal decay at 1x over 10 seconds real-time

    initial_weight = 0.5
    real_time = 10.0  # seconds

    decay_1x = simulate_decay(initial_weight, real_time, speed='1x')
    decay_3x = simulate_decay(initial_weight, real_time, speed='3x')

    assert abs(decay_1x - decay_3x) < 0.01
```

### Flip Threshold Is Deterministic

```python
def check_deterministic_flip():
    # Same state → same flips
    save_state = snapshot_graph()

    flips_1 = physics.tick()
    restore_graph(save_state)
    flips_2 = physics.tick()

    assert flips_1 == flips_2
```

### Energy Must Land

```python
def check_energy_lands():
    # After player input, something responds (eventually)
    process_input("Hello everyone")

    # Run physics until stable or max ticks
    for _ in range(100):
        physics.tick()
        if any_moments_flipped():
            break

    # Either NPC responded or player character observed silence
    assert any_moments_flipped() or player_character_has_observation()
```

---

## Handler Invariants

### Handler Output Structure

```python
def check_handler_output():
    # Handler must produce valid moment drafts
    output = run_handler('char_aldric', mock_trigger())

    for moment in output.moments:
        assert moment.content is not None
        assert moment.type in ['dialogue', 'thought', 'action', 'narration']
        # Handler does NOT set weight
        assert not hasattr(moment, 'weight') or moment.weight is None
```

### Handler Scope

```python
def check_handler_scope():
    # Handler output only attaches to its character
    output = run_handler('char_aldric', mock_trigger())

    for moment in output.moments:
        # When injected, should only attach to Aldric
        links = get_links_for_moment(moment)
        character_attachments = [l for l in links if l.type == 'ATTACHED_TO'
                                  and l.target_type == 'Character']
        for att in character_attachments:
            assert att.target_id == 'char_aldric'
```

---

## Canon Invariants

### Simultaneous Actions Are Drama

```python
def check_drama_not_blocked():
    # Two characters grabbing same item should BOTH canonize
    moment_a = create_action_moment('char_aldric', 'take', 'thing_sword')
    moment_b = create_action_moment('char_mildred', 'take', 'thing_sword')

    # Both should flip (high weight)
    set_weight(moment_a, 0.9)
    set_weight(moment_b, 0.85)

    physics.tick()

    # Both should be canon
    assert get_moment(moment_a).status == 'completed'
    assert get_moment(moment_b).status == 'completed'

    # Action processing handles the conflict, not canon holder
```

### True Mutex Is Rare

```python
def check_true_mutex():
    # Same character, incompatible actions → mutex
    travel_east = create_action_moment('char_aldric', 'travel', 'place_east')
    travel_west = create_action_moment('char_aldric', 'travel', 'place_west')

    set_weight(travel_east, 0.9)
    set_weight(travel_west, 0.85)

    physics.tick()

    # Only one should canonize (higher weight)
    assert get_moment(travel_east).status == 'completed'
    assert get_moment(travel_west).status == 'possible'  # Returns to potential
```

---

## Speed Invariants

### Display Doesn't Affect Canon

```python
def check_display_independence():
    # At 3x, low-weight moments still create THEN links
    moment = create_moment("Minor observation", weight=0.3)

    set_speed('3x')
    physics.tick()

    # Not displayed (below threshold)
    assert not was_displayed(moment)

    # But is canon
    assert get_moment(moment).status == 'completed'
    assert has_then_links(moment)
```

### Interrupt Breaks Through

```python
def check_interrupt_display():
    # At 3x, interrupt moments always display
    combat_moment = create_action_moment('char_enemy', 'attack', 'char_player')

    set_speed('3x')
    physics.tick()

    # Must display (combat is interrupt)
    assert was_displayed(combat_moment)
    # Speed should drop to 1x
    assert get_speed() == '1x'
```

---

## Action Invariants

### Sequential Processing

```python
def check_action_sequence():
    # Actions process one at a time
    action_a = create_action_moment('char_aldric', 'take', 'thing_sword')
    action_b = create_action_moment('char_mildred', 'take', 'thing_sword')

    process_actions([action_a, action_b])

    # First succeeds
    assert get_thing('thing_sword').carried_by == 'char_aldric'

    # Second gets blocked consequence
    assert has_blocked_consequence('char_mildred')
```

### Validation Before Execution

```python
def check_action_validation():
    # Stale action fails validation
    action = create_action_moment('char_aldric', 'take', 'thing_sword')

    # Sword already taken by someone else
    execute_take('char_enemy', 'thing_sword')

    # Action should fail validation
    result = process_action(action)
    assert result.success == False
```

---

## Question Answering Invariants

### Non-Blocking

```python
def check_qa_non_blocking():
    # Handler doesn't wait for QA
    start = time.time()
    output = run_handler('char_aldric', mock_trigger_with_question())
    elapsed = time.time() - start

    # Should complete in LLM time, not LLM time × 2 (waiting for QA)
    assert elapsed < 5.0  # Single LLM call timing
```

### Consistency

```python
def check_qa_consistency():
    # QA cannot contradict existing facts
    # Aldric already has a father defined
    create_character('char_aldric_father', name="Wulfstan")
    create_link('FAMILY', 'char_aldric', 'char_aldric_father', {'relationship': 'father'})

    # QA for "who is my father" must return existing, not invent new
    answer = question_answerer.answer('char_aldric', "Who is my father?")

    # Should reference existing father, not create new one
    assert 'Wulfstan' in answer.text or answer.references_existing('char_aldric_father')
```

---

## Performance Benchmarks

### View Query Performance

```python
def benchmark_view_query():
    # Setup: 1000 moments, 50 characters, 20 places
    setup_large_graph()

    start = time.time()
    for _ in range(100):
        get_current_view("char_player")
    elapsed = time.time() - start

    assert elapsed / 100 < 0.05  # <50ms per query
```

### Physics Tick Performance

```python
def benchmark_physics_tick():
    # Setup: 10000 moments
    setup_many_moments(10000)

    start = time.time()
    for _ in range(100):
        physics.tick()
    elapsed = time.time() - start

    assert elapsed / 100 < 0.1  # <100ms per tick
```

### Handler Parallel Execution

```python
def benchmark_parallel_handlers():
    # 4 characters flip simultaneously
    flips = [create_flip('char_' + str(i)) for i in range(4)]

    start = time.time()
    asyncio.run(process_flips_parallel(flips))
    elapsed = time.time() - start

    # Should be ~1 LLM call time, not 4
    assert elapsed < 8.0  # Single LLM call (~3-5s) + overhead
```

---

## Verification Checklist

Before release:

**Core Invariants:**
<!-- @mind:todo I1: No state stored outside graph -->
<!-- @mind:todo I2: Physics tick runs continuously -->
<!-- @mind:todo I3: THEN links immutable -->
<!-- @mind:todo I4: Handlers write only for their character -->
<!-- @mind:todo I5: Canon cannot revert -->
<!-- @mind:todo I6: Same canon at any speed -->
<!-- @mind:todo I7: Energy conservation holds -->
<!-- @mind:todo I8: No arbitrary handler triggers -->

**Graph State:**
<!-- @mind:todo Status values valid -->
<!-- @mind:todo Weight bounds enforced -->
<!-- @mind:todo Link types valid -->

**Physics:**
<!-- @mind:todo Decay time-based not tick-based -->
<!-- @mind:todo Flip deterministic -->
<!-- @mind:todo Energy always lands -->

**Handlers:**
<!-- @mind:todo Output structure valid -->
<!-- @mind:todo Scope isolation enforced -->

**Canon:**
<!-- @mind:todo Drama not blocked -->
<!-- @mind:todo True mutex rare and handled -->

**Speed:**
<!-- @mind:todo Display doesn't affect canon -->
<!-- @mind:todo Interrupts break through -->

**Actions:**
<!-- @mind:todo Sequential processing -->
<!-- @mind:todo Validation before execution -->

**Question Answering:**
<!-- @mind:todo Non-blocking -->
<!-- @mind:todo Consistent with existing facts -->

**Performance:**
<!-- @mind:todo View query <50ms -->
<!-- @mind:todo Physics tick <100ms -->
<!-- @mind:todo Parallel handlers work -->

---

## PROPERTIES

These properties describe expected characteristics of a healthy physics run
that are observable without asserting exact event content. They complement
the invariants by describing measurable system traits, not strict rules.

- Energy propagation produces measurable decay per tick even when no new
  player input arrives, confirming the world does not idle.
- Canon ordering remains stable under replays with identical seeds and graph
  state snapshots, even if display speed differs.
- Handler output stays within the moment schema and never asserts weight or
  energy directly, keeping physics authoritative.
- Flip detection produces consistent counts across identical snapshots, with
  variance attributable only to randomized seed configuration.

## ERROR CONDITIONS

These are explicit failure states that must be surfaced by tests or runtime
checks, because silent degradation here would undermine physics authority and
simulation credibility.

- Missing or null tick metadata on THEN links or completed moments.
- Moment weights or energies outside allowed bounds after a physics tick.
- Handler output attaching to the wrong character or writing to non-moment
  nodes without an explicit graph operation.
- Speed changes producing different canon chains or missing interrupts.
- Tick loop halted while the simulation reports an active playthrough.

## TEST COVERAGE

Primary coverage lives in `docs/physics/TEST_Physics.md` and the engine test
suite under `mind/tests/`, especially tests that exercise moment graph
consistency and physics tick behavior. The validation checklist maps to those
tests, and any gaps are tracked in the physics TEST doc and SYNC file.

## VERIFICATION PROCEDURE

1. Review `docs/physics/ALGORITHM_Physics.md` and confirm invariants align with
   the documented tick, decay, flip, and canon mechanics.
2. Run the relevant physics tests from `mind/tests/` and confirm no skips
   obscure missing coverage for tick, graph, or handler logic.
3. Validate graph integrity checks against a representative playthrough
   dataset, confirming status, weight, link, and THEN-link requirements.
4. Compare canon chains across at least two speed settings to confirm
   display-only differences and identical actualization outcomes.
5. Record verification outcomes in `docs/physics/SYNC_Physics.md` with any
   deviations, failing checks, or follow-up items.

## SYNC STATUS

Physics validation drift is tracked in `docs/physics/SYNC_Physics.md`. Any
changes to invariants, properties, or procedures must be logged there to keep
the validation doc aligned with current engine behavior.
