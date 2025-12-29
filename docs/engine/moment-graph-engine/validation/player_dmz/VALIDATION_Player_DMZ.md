# Moment Graph Engine — Validation: Player DMZ Invariants (Stub)

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
THIS:            VALIDATION_Player_DMZ.md
IMPL:            ../../../../../mind/world_builder/*
                 ../../../../../runtime/moment_graph/queries.py

# Note: PATTERNS and BEHAVIORS files planned but not yet created
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | WorldBuilder respects player DMZ | Prevents world mutation under player view |
| B2 | DMZ computed from view neighborhood | Ensures stable locality boundary |

---

## INVARIANTS

### VDMZ1: WorldBuilder Never Writes Inside DMZ

```
WorldBuilder MUST NOT mutate nodes/links within DMZ = N_k(current_view(player)).
```

### VDMZ2: DMZ Computed From Whitelisted Links

```
DMZ neighborhood is derived from current_view(player) with a fixed link whitelist.
```

### VDMZ3: Same-Place Writes Allowed Only Outside DMZ

```
Mutations in the player's place are allowed only if target nodes are outside DMZ.
```

---

## PROPERTIES

### PDMZ1: DMZ Invariance Under Non-Local Changes

```
Far-away graph changes MUST NOT expand DMZ membership for player view.
```

---

## ERROR CONDITIONS

### EDMZ1: DMZ Violation

```
WHEN:    WorldBuilder attempts a write inside DMZ
THEN:    reject or quarantine mutation
SYMPTOM: scene contradictions
```

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| VDMZ1 | dmz_write_rejections | ⚠ NOT YET VERIFIED |
| VDMZ2 | dmz_neighborhood_size | ⚠ NOT YET VERIFIED |
| VDMZ3 | dmz_same_place_write_rate | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] DMZ is computed from current_view(player)
[ ] WorldBuilder writes are blocked inside DMZ
```

### Automated

```bash
pytest tests/runtime/test_dmz_worldbuilder.py
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-20
VERIFIED_AGAINST:
  impl: mind/world_builder/* @ UNKNOWN
  test: tests/runtime/test_dmz_worldbuilder.py @ UNKNOWN
VERIFIED_BY: NOT RUN
RESULT:
  VDMZ1: NOT RUN
  VDMZ2: NOT RUN
  VDMZ3: NOT RUN
```

---

## MARKERS

<!-- @mind:todo Define exact DMZ link whitelist and hop depth. -->
<!-- @mind:todo Decide whether DMZ is view-based or player-node based. -->
