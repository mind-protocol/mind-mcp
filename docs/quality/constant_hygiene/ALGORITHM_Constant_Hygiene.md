# Constant Hygiene — Algorithm

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
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
THIS:            ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
IMPLEMENTATION:  ./IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md

IMPL:            runtime/orchestrator/constant_hygiene.py
```

---

## OVERVIEW

The algorithm has three phases: **discover** (find unscanned commits), **analyze** (read diff, detect constants), **inject** (create Concept node in citizen's neighborhood). All three run in a single `evaluate()` call from the dispatcher's maintenance loop.

---

## ALGORITHM: evaluate()

### Step 1: Discover Unscanned Commits

```
Query L3:
  MATCH (m:Moment)
  WHERE m.subtype = 'commit'
    AND m.created_at_s > now - 600
    AND m.constant_hygiene_scanned IS NULL
  RETURN m.id, m.name, m.origin_citizen, m.commit_hash
  LIMIT 10
```

Only looks at the last 10 minutes of commits. Marks each as scanned after processing (idempotent — won't re-process).

### Step 2: Analyze Each Commit's Diff

```
For each commit:
  diff = git diff {hash}~1 {hash} -- *.py *.js *.ts

  For each added line (starts with +):
    Skip if line matches safe patterns (HTTP codes, math, byte sizes, comments)
    Check against constant detection patterns:
      - ALL_CAPS = number
      - if/elif with numeric comparison
      - default = number
      - .get(key, "number")
      - timeout/interval/threshold = number
    If match → add to findings list
```

### Step 3: Inject Concept (if constants found)

```
If findings is not empty AND citizen is known:
  concept_id = "concept:constant_hygiene:{hash[:8]}"

  # Energy: proportional to count relative to citizen's own history
  history = citizen's last 20 constant counts
  if enough history:
    energy = min(0.7, count / (avg_history * 2))
  else:
    energy = min(0.5, count * 0.1)

  MERGE Concept node in L3:
    id, name, content (with skill reference + examples), energy

  MERGE OBSERVED_IN link from citizen Actor to Concept:
    weight=0.4, energy=derived
```

### Step 4: Mark Scanned

```
SET m.constant_hygiene_scanned = true
```

Prevents re-processing. If the mark fails, worst case is we re-scan the same commit next cycle — harmless.

---

## DATA FLOW

```
[L3 Moment(commit)] → query → [unscanned commits]
         ↓
[git diff {hash}] → subprocess → [diff text]
         ↓
[pattern matching] → [findings: file, line, pattern]
         ↓
[energy derivation from citizen history] → [energy value]
         ↓
[MERGE Concept in L3] + [MERGE OBSERVED_IN link to citizen]
         ↓
[citizen awareness tick] → imports Concept → [WM competition]
         ↓
[citizen FEELS the skill reference] → [acts or doesn't]
```

---

## KEY DECISIONS

### D1: Why git diff in subprocess, not graph content?

The commit Moment in L3 doesn't contain the full diff — it has metadata (hash, message, author). The actual code changes live in git. Subprocess is the only way to read them. Cost: ~10ms per diff. Acceptable for a maintenance-cycle task.

### D2: Why energy from history, not a fixed value?

A citizen who normally writes zero constants and suddenly writes 5 should get a bright concept (novel event). A citizen who always writes 3 per commit and writes 3 again gets a dimmer concept (expected behavior). The energy adapts to each citizen's own baseline — same principle as the silence sentinel.

### D3: Why limit to 10 commits per cycle?

Prevents the scan from blocking the maintenance loop on burst commit scenarios (e.g., batch of 50 commits from a merge). 10 per cycle × 15min cycles = 40 commits/hour capacity. If commits arrive faster, they queue and get scanned next cycle.

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
