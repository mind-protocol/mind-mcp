# Constant Hygiene — Behaviors

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
OBJECTIVES:      ./OBJECTIVES_Constant_Hygiene.md
PATTERNS:        ./PATTERNS_Constant_Hygiene.md
THIS:            BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md

IMPL:            runtime/orchestrator/constant_hygiene.py
```

---

## BEHAVIORS

### B1: Commit With Constants Creates Concept in Citizen's Neighborhood

**Why:** The citizen needs to feel the finding while context is hot.

```
GIVEN:  A citizen commits code and a Moment(subtype='commit') is created in L3
WHEN:   The maintenance cycle runs and the sense reads the unscanned commit
AND:    The git diff contains lines matching constant patterns (ALL_CAPS = number, etc.)
AND:    The matched lines are not safe exclusions (HTTP codes, math constants)
THEN:   A Concept node is created in L3 with the skill reference and constant examples
AND:    The Concept is linked to the committing citizen via OBSERVED_IN
AND:    The Concept energy is proportional to constants found relative to citizen's history
AND:    The commit Moment is marked as scanned (won't re-process)
```

### B2: Citizen Feels the Concept Through Normal Physics

**Why:** No hooks, no notifications. The graph routes the finding through the same physics as everything else.

```
GIVEN:  A Concept node exists in the citizen's 1-hop neighborhood with energy > import threshold
WHEN:   The citizen's next awareness tick runs
THEN:   The Concept is imported into the citizen's L1 cognitive state
AND:    WM competition determines if it enters consciousness
AND:    If curiosity drive is high, the concept wins attention more easily
AND:    The citizen sees: "mind.eliminate_constants — can these derive from system state?"
```

### B3: Clean Commits Strengthen the Objective

**Why:** Positive reinforcement. Citizens who derive values instead of hardcoding feel the objective brightening.

```
GIVEN:  A citizen commits code
WHEN:   The diff contains zero detected constants
THEN:   The sense fires healthy
AND:    Objective weight grows (+0.02)
AND:    The citizen's awareness of "constant-free code" concept strengthens over time
```

### B4: Repeated Constants Consolidate Into Conscious Action

**Why:** If a citizen doesn't act on the concept, it shouldn't just decay — it should accumulate until the physics compels action.

```
GIVEN:  A citizen has committed constants in 3+ consecutive commits
WHEN:   The Concept nodes accumulate energy (each new commit reinforces)
THEN:   The energy crosses the conscious action threshold
AND:    The citizen's impulse system fires: "Run mind.eliminate_constants on recent commits"
AND:    This is not a scheduled task — it's a natural consequence of energy accumulation
```

### B5: Safe Constants Are Not Flagged

**Why:** HTTP 200 is not a frozen assumption. It's a protocol specification.

```
GIVEN:  A commit diff contains a line like `if resp.status_code == 200:`
WHEN:   The sense scans the diff
THEN:   The line is excluded by safe pattern matching
AND:    No Concept node is created for this line
AND:    The commit still counts as "clean" if no other constants are found
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Result |
|----------|-----------|--------|
| B1 | O1: Detected at commit time | R1: Caught at creation |
| B2 | O2: Felt, not reported | R2: Felt in awareness |
| B3 | O3: Behavior improves | R3: Trend downward |
| B4 | O3: Behavior improves | R3: Trend downward |
| B5 | (quality) | (precision — no false alarms on safe constants) |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
