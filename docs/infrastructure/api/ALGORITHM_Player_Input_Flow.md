# Player Input → Moment Output Flow

```
STATUS: IMPLEMENTED
UPDATED: 2025-12-22
```

## Overview

Two paths exist for player input, optimized for different latency requirements:

| Path | Endpoint | Latency Target | LLM? | Use Case |
|------|----------|----------------|------|----------|
| Fast | `/api/moment/click` | <50ms | No | Word clicks, traversals |
| Full | `/api/action` | Seconds | Yes | Free-form actions |

---

## Fast Path: Word Click

```
Frontend                           Backend
────────                           ───────
User clicks word
      │
      ▼
POST /api/moment/click ─────────▶ app.py:364
{                                       │
  playthrough_id,                       ▼
  moment_id,                    graph_ops_moments.py:38
  word,                         handle_click()
  tick                                  │
}                          ┌────────────┼────────────┐
                           ▼            ▼            ▼
                        Query       Transfer      Check
                      CAN_LEAD_TO    weight      ≥0.8?
                      transitions      │            │
                           │           ▼            ▼
                           │     SET weight    SET status
                           │                   = 'active'
                           │           │            │
                           └───────────┴────────────┘
                                       │
                                       ▼
                              Return response
                                       │
◀──────────────────────────────────────┘
{
  flipped: true,
  flipped_moments: [{id, text, weight}],
  weight_updates: [{id, old, new}],
  queue_narrator: false
}
      │
      ▼
Update React state
Re-render moments
```

### Key Functions

| File | Line | Function |
|------|------|----------|
| `app.py` | 364 | `/api/moment/click` endpoint |
| `graph_ops_moments.py` | 38 | `handle_click()` |
| `graph_ops_moments.py` | 69 | Find CAN_LEAD_TO edges |
| `graph_ops_moments.py` | 118 | Apply weight transfer |
| `graph_ops_moments.py` | 142 | Check activation flip |

### Cypher Executed

```cypher
-- 1. Find transitions from clicked moment
MATCH (m:Moment {id: $moment_id})-[r:CAN_LEAD_TO]->(target:Moment)
WHERE r.require_words IS NOT NULL
RETURN target.id, r.require_words, r.weight_transfer, r.consumes_origin

-- 2. Update target weight
MATCH (m:Moment {id: $target_id})
SET m.weight = $new_weight
WHERE m.weight < $new_weight

-- 3. Flip to active if threshold met
MATCH (m:Moment {id: $target_id})
WHERE m.weight >= 0.8 AND m.status = 'possible'
SET m.status = 'active', m.tick_resolved = $tick
```

---

## Full Path: Action

```
POST /api/action ─────────────▶ app.py:314
{                                    │
  playthrough_id,                    ▼
  action: "I look around",    orchestrator.py:59
  player_id                   process_action()
}                                    │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              Build scene      Call Narrator     Run tick
              context          (LLM)             (if ≥5min)
                    │                │                │
                    │                ▼                │
                    │         narrator.py:45         │
                    │         generate()             │
                    │                │                │
                    │                ▼                │
                    │         Returns:               │
                    │         - dialogue             │
                    │         - mutations            │
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ▼
                             Apply mutations
                                     │
                                     ▼
                             Check for flips
                                     │
                              ┌──────┴──────┐
                              ▼             ▼
                          No flips      Flips found
                              │             │
                              │             ▼
                              │      WorldRunner
                              │      process_flips()
                              │             │
                              └──────┬──────┘
                                     │
                                     ▼
                             Return response
```

### Key Functions

| File | Line | Function |
|------|------|----------|
| `app.py` | 314 | `/api/action` endpoint |
| `orchestrator.py` | 59 | `process_action()` |
| `orchestrator.py` | 93 | `_build_scene_context()` |
| `narrator.py` | 45 | `generate()` |
| `orchestrator.py` | 112 | `_apply_mutations()` |
| `surface.py` | 42 | `check_for_flips()` |

---

## Thresholds

| Threshold | Value | Effect |
|-----------|-------|--------|
| Activation | weight ≥ 0.8 | `status` → `'active'` |
| Decay | weight < 0.1 | `status` → `'decayed'` |
| Tick trigger | elapsed ≥ 5 min | Run physics/decay |
| Decay rate | 0.99/tick | Multiplicative decay |

---

## Validation

### Fast Path Test

```bash
# 1. Create playthrough
PT=$(curl -s -X POST http://localhost:3000/api/playthroughs \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "thornwick_betrayed", "player_name": "Test"}' \
  | jq -r '.playthrough_id')

# 2. Get current moments
curl -s "http://localhost:8000/api/view/$PT" | jq '.moments[:2]'

# 3. Click a word (get moment_id from step 2)
curl -s -X POST http://localhost:8000/api/moment/click \
  -H "Content-Type: application/json" \
  -d "{\"playthrough_id\": \"$PT\", \"moment_id\": \"moment_xxx\", \"word\": \"test\"}"

# 4. Verify weight changed
curl -s -X POST "http://localhost:8000/api/graph/$PT/query" \
  -H "Content-Type: application/json" \
  -d '{"cypher": "MATCH (m:Moment) WHERE m.weight > 0 RETURN m.id, m.weight LIMIT 5"}'
```

### Full Path Test

```bash
# Action with narrator
curl -s -X POST http://localhost:8000/api/action \
  -H "Content-Type: application/json" \
  -d "{\"playthrough_id\": \"$PT\", \"action\": \"I look around the ruins\"}"
```

---

## Chain

```
PATTERNS:       ./PATTERNS_Api.md
ALGORITHM:      ./ALGORITHM_Player_Input_Flow.md (this file)
IMPLEMENTATION: ../../../runtime/infrastructure/api/app.py
                ../../../runtime/physics/graph/graph_ops_moments.py
                ../../../runtime/infrastructure/orchestration/orchestrator.py
```
