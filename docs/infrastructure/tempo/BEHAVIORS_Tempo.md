# Tempo Controller — Behaviors: Observable Pacing Effects

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tempo.md
THIS:            BEHAVIORS_Tempo.md (you are here)
ALGORITHM:       ./ALGORITHM_Tempo_Controller.md
VALIDATION:      ./VALIDATION_Tempo.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tempo.md
HEALTH:          ./HEALTH_Tempo.md
SYNC:            ./SYNC_Tempo.md

IMPL:            runtime/infrastructure/tempo/tempo_controller.py (planned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Speed Mode Defines Stop Conditions

```
GIVEN:  speed is set to pause, 1x, 2x, or 3x
WHEN:   the tempo loop runs
THEN:   the stop conditions for ticks follow the mode rules
AND:    cadence does not depend on narrator latency
```

### B2: Pause Runs Exactly One Tick

```
GIVEN:  speed = pause
WHEN:   the tempo loop is triggered
THEN:   exactly one tick is executed
AND:    no moment node is returned to the player
```

### B3: 1x Stops on Player-Linked Moment

```
GIVEN:  speed = 1x
WHEN:   ticks run
THEN:   ticking stops after a moment linked to the player flips
```

### B4: 2x Runs Past Player-Linked Moment, Stops on Interrupt

```
GIVEN:  speed = 2x
WHEN:   ticks run
THEN:   ticking continues after a player-linked moment flips
AND:    stops only when an interrupting player-linked moment flips
```

### B5: 3x Runs Until Interrupt, Then Drops to 1x

```
GIVEN:  speed = 3x
WHEN:   ticks run
THEN:   ticking continues until an interrupting player-linked moment flips
AND:    speed resets to 1x on interrupt
```

---

## INPUTS / OUTPUTS

### Primary Function: `TempoController.run()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| speed | enum | pause/1x/2x/3x pacing mode |
| running | bool | loop control flag |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| tick_result | dict | physics + canon stats per tick |

**Side Effects:**

- Invokes physics tick
- Triggers canon scan and broadcast

---

## EDGE CASES

### E1: Pause Mode

```
GIVEN:  speed = pause
THEN:   no ticks are emitted until resumed
```

### E2: Backpressure

```
GIVEN:  pending outputs exceed a safe limit
THEN:   tempo slows or skips ticks to avoid overload
```

---

## ANTI-BEHAVIORS

### A1: Blocking on Narrator

```
GIVEN:   narrator is slow or stalled
WHEN:    tempo tick is due
MUST NOT: block the loop waiting on narrator
INSTEAD: continue with physics and canon cadence
```

### A2: Unbounded Surfacing

```
GIVEN:   many possible moments are present
WHEN:    a tick occurs
MUST NOT: surface unbounded moments in one tick
INSTEAD: enforce per-tick limits
```

---

## MARKERS

<!-- @mind:todo Decide per-tick cap for canon surfacing. -->
<!-- @mind:todo Determine how tempo reports backlog to operators. -->
<!-- @mind:proposition expose cadence metrics for health checks. -->
