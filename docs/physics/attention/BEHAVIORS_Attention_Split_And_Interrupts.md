# Physics — Behaviors: Attention Split and Interrupts

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Attention_Energy_Split.md
THIS:            BEHAVIORS_Attention_Split_And_Interrupts.md (you are here)
ALGORITHM:       ./ALGORITHM_Attention_Energy_Split.md
VALIDATION:      ./VALIDATION_Attention_Split_And_Interrupts.md
IMPLEMENTATION:  ./IMPLEMENTATION_Attention_Energy_Split.md
HEALTH:          ./HEALTH_Attention_Energy_Split.md
SYNC:            ./SYNC_Attention_Energy_Split.md

IMPL:            runtime/physics/attention_split_sink_mass_distribution_mechanism.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Attention Redistribution Happens Each Tick

```
GIVEN:  player neighborhood is defined for a runner position
WHEN:   physics tick runs
THEN:   eligible attention sinks are enumerated (narratives + moments)
AND:    split_fn computes shares using dynamic functions
AND:    energies are updated deterministically
```

### B2: Arrival or Witness Adds a Sink

```
GIVEN:  a character becomes present and is visible to the player neighborhood
WHEN:   the system records the arrival
THEN:   a witnessed narrative (or equivalent node) enters the sink set
AND:    attention redistribution may reconfigure focus
```

### B3: Interrupt Fires on Focus Reconfiguration

```
GIVEN:  a tick completes energy propagation and redistribution
WHEN:   primary active moment changes OR active moment deactivates OR a moment becomes completed
THEN:   interrupt = YES for that runner position
```

### B4: Non-Interrupt Flips Do Not Stop Acceleration

```
GIVEN:  flips occur in the neighborhood
WHEN:   focus state does not change and no spoken occurs
THEN:   interrupt = NO
AND:    acceleration may continue
```

### B5: CONTRADICTS Visibility Interrupts

```
GIVEN:  canonization links alternates via CONTRADICTS in the player neighborhood
WHEN:   CONTRADICTS becomes visible
THEN:   interrupt = YES
```

### B6: Void Pressure Can Create a Sink

```
GIVEN:  time_since_last_spoken exceeds threshold
WHEN:   a void narrative is created and linked to the player neighborhood
THEN:   it participates in attention redistribution next tick
AND:    may cause focus reconfiguration
```

---

## INPUTS / OUTPUTS

### Primary Function: `apply_attention_split()` (implemented)

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| neighborhood | set | player-linked narratives + moments |
| focus_map | dict | node_id → focus scalar |
| context | dict | visibility/recency/links |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| redistribution | dict | node_id → energy share |
| interrupt | bool | focus reconfiguration flag |

**Side Effects:**

- Updates energy for eligible sinks
- May demote active moment below threshold

---

## EDGE CASES

### E1: Empty Neighborhood

```
GIVEN:  neighborhood has no eligible sinks
THEN:   attention split is skipped and interrupt = NO
```

### E2: Large Sink Set

```
GIVEN:  neighborhood has many eligible sinks
THEN:   split_fn still returns bounded shares without zeroing all energy
```

---

## ANTI-BEHAVIORS

### A1: Queries Cause Energy Changes

```
GIVEN:   read-only queries
WHEN:    queries execute
MUST NOT: mutate energy/weight/status
INSTEAD: only explicit physics writes may change state
```

### A2: Interrupt via Cooldown or Scores

```
GIVEN:   focus state unchanged
WHEN:    flips occur
MUST NOT: declare interrupt via cooldown timers or hidden scores
INSTEAD: interrupt only on focus reconfiguration or spoken
```

---

## MARKERS

<!-- @mind:todo Define player_neighborhood() scope (links + depth). -->
<!-- @mind:todo Define split_fn inputs and bounds. -->
<!-- @mind:proposition add debug-only logging for sink shares and interrupt reason. -->
