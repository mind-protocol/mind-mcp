# Example Traversal Log Output

This shows what a complete SubEntity exploration looks like in both formats.

---

## Scenario

**Actor:** Edmund (actor_edmund)
**Intention:** "find truth about the betrayal"
**Origin:** moment_question (Edmund asks "Who betrayed me?")

The exploration:
1. Starts at moment_question
2. Finds narrative_betrayal (high alignment)
3. Branches at moment_crossroads into 2 children
4. Child 1 finds narrative_trust
5. Child 2 dead-ends, reflects
6. Merges back, returns findings

---

## Human-Readable Format

File: `mind/data/logs/traversal_exp_7f3a2b.txt`

```
═══════════════════════════════════════════════════════════════════════════════
 EXPLORATION exp_7f3a2b
═══════════════════════════════════════════════════════════════════════════════
 Actor:     actor_edmund
 Intention: "find truth about the betrayal"
 Origin:    moment_question
 Started:   2025-12-26T14:30:00.000Z
───────────────────────────────────────────────────────────────────────────────

[se_root001] SPAWN @ moment_question (depth=0)
    intention: "find truth about the betrayal"
    satisfaction: 0.00 | criticality: 0.00

[se_root001] SEEKING @ moment_question
    ├─ candidates:
    │   ├─ link_001 → narrative_betrayal (narrative)  score=0.82
    │   │      semantic=0.91  polarity=0.95  perm=0.90  novelty=1.00  diverge=1.00
    │   ├─ link_002 → space_courtyard (space)         score=0.34
    │   │      semantic=0.45  polarity=0.80  perm=0.85  novelty=1.00  diverge=1.00
    │   └─ link_003 → thing_letter (thing)            score=0.28
    │          semantic=0.35  polarity=0.90  perm=0.80  novelty=1.00  diverge=1.00
    └─ selected: link_001 → narrative_betrayal (highest_score)

[se_root001] TRAVERSE moment_question → narrative_betrayal
    via link_001 | polarity=0.95 | permanence=0.10
    energy: 0.00 → 0.29 (+0.29)
    embedding blend: weight=0.90 (1-perm)

[se_root001] RESONATING @ narrative_betrayal
    ├─ alignment: 0.87 (high)
    ├─ found_narratives: {narrative_betrayal: 0.87}
    ├─ satisfaction: 0.00 → 0.43
    └─ continue exploring (satisfaction < 0.8)

[se_root001] SEEKING @ narrative_betrayal
    ├─ candidates:
    │   ├─ link_004 → moment_crossroads (moment)      score=0.71
    │   │      semantic=0.78  polarity=0.92  perm=0.85  novelty=0.95  diverge=1.00
    │   └─ link_005 → actor_margaret (actor)          score=0.52
    │          semantic=0.65  polarity=0.85  perm=0.80  novelty=0.98  diverge=1.00
    └─ selected: link_004 → moment_crossroads (highest_score)

[se_root001] TRAVERSE narrative_betrayal → moment_crossroads
    via link_004 | polarity=0.92 | permanence=0.15
    energy: 0.50 → 0.72 (+0.22)

[se_root001] BRANCHING @ moment_crossroads
    ├─ outgoing links: 3 (threshold=2 met)
    ├─ spawning children:
    │   ├─ se_child01 → link_006 → narrative_trust    (score=0.68)
    │   └─ se_child02 → link_007 → space_garden       (score=0.61)
    └─ waiting for children...

    ┌───────────────────────────────────────────────────────────────────────
    │ CHILD se_child01 (sibling: se_child02)
    │
    │ [se_child01] SPAWN @ moment_crossroads (depth=1)
    │     intention: "find truth about the betrayal"
    │     satisfaction: 0.43 | criticality: 0.29
    │
    │ [se_child01] TRAVERSE moment_crossroads → narrative_trust
    │     via link_006 | polarity=0.88 | permanence=0.20
    │
    │ [se_child01] RESONATING @ narrative_trust
    │     ├─ alignment: 0.72
    │     ├─ found_narratives: {narrative_betrayal: 0.87, narrative_trust: 0.72}
    │     ├─ satisfaction: 0.43 → 0.61
    │     └─ continue exploring
    │
    │ [se_child01] SEEKING @ narrative_trust
    │     ├─ candidates:
    │     │   └─ link_008 → actor_john (actor)           score=0.31
    │     │          semantic=0.42  polarity=0.80  perm=0.75  novelty=0.88  diverge=0.95
    │     └─ selected: link_008 (only option)
    │
    │ [se_child01] TRAVERSE narrative_trust → actor_john
    │     via link_008 | polarity=0.80 | permanence=0.25
    │
    │ [se_child01] SEEKING @ actor_john
    │     ├─ candidates: none with score > 0.2
    │     └─ no viable options → REFLECTING
    │
    │ [se_child01] REFLECTING @ actor_john
    │     ├─ path: [link_006, link_008]
    │     ├─ backward coloring: permanence +0.05 per link (alignment=0.72)
    │     └─ satisfaction=0.61 → MERGING
    │
    │ [se_child01] MERGE → parent se_root001
    │     contributed: {narrative_trust: 0.72}
    │     satisfaction: 0.61
    │     crystallized: null
    └───────────────────────────────────────────────────────────────────────

    ┌───────────────────────────────────────────────────────────────────────
    │ CHILD se_child02 (sibling: se_child01)
    │
    │ [se_child02] SPAWN @ moment_crossroads (depth=1)
    │     intention: "find truth about the betrayal"
    │     satisfaction: 0.43 | criticality: 0.29
    │
    │ [se_child02] TRAVERSE moment_crossroads → space_garden
    │     via link_007 | polarity=0.85 | permanence=0.30
    │
    │ [se_child02] SEEKING @ space_garden
    │     ├─ candidates:
    │     │   ├─ link_009 → thing_bench (thing)          score=0.18
    │     │   │      semantic=0.25  polarity=0.75  perm=0.70  novelty=0.92  diverge=0.85
    │     │   └─ link_010 → thing_fountain (thing)       score=0.15
    │     │          semantic=0.20  polarity=0.80  perm=0.65  novelty=0.90  diverge=0.82
    │     └─ all scores < 0.2 threshold → REFLECTING
    │
    │ [se_child02] REFLECTING @ space_garden
    │     ├─ path: [link_007]
    │     ├─ backward coloring: skipped (alignment too low)
    │     └─ satisfaction=0.43, criticality=0.29 < 0.8 → MERGING (not crystallizing)
    │
    │ [se_child02] MERGE → parent se_root001
    │     contributed: {} (nothing new)
    │     satisfaction: 0.43
    │     crystallized: null
    └───────────────────────────────────────────────────────────────────────

[se_root001] CHILDREN COMPLETE
    ├─ merged from se_child01: {narrative_trust: 0.72}
    ├─ merged from se_child02: {}
    └─ combined: {narrative_betrayal: 0.87, narrative_trust: 0.72}

[se_root001] REFLECTING @ moment_crossroads
    ├─ path: [link_001, link_004]
    ├─ backward coloring: permanence +0.08 per link
    └─ satisfaction=0.71 → MERGING (satisfied enough)

[se_root001] MERGE → (root, exploration complete)
    final_findings: {narrative_betrayal: 0.87, narrative_trust: 0.72}
    satisfaction: 0.71
    crystallized: null

═══════════════════════════════════════════════════════════════════════════════
 END exp_7f3a2b
═══════════════════════════════════════════════════════════════════════════════
 Duration:     847ms
 SubEntities:  3 (1 root + 2 children)
 Total Steps:  12
 Nodes Visited: 6 unique
 Links Traversed: 5
 Narratives Found: 2
 Crystallized: 0
 Final Satisfaction: 0.71
═══════════════════════════════════════════════════════════════════════════════
```

---

## JSONL Format (Machine-Readable)

File: `mind/data/logs/traversal_exp_7f3a2b.jsonl`

Each line is one JSON object. Here are key entries:

### Line 1: EXPLORATION_START

```json
{"event":"EXPLORATION_START","exploration_id":"exp_7f3a2b","actor_id":"actor_edmund","origin_moment":"moment_question","intention":"find truth about the betrayal","intention_embedding_hash":"a1b2c3d4","root_subentity_id":"se_root001","timestamp":"2025-12-26T14:30:00.000Z"}
```

### Line 2: First STEP (seeking at origin)

```json
{
  "header": {
    "timestamp": "2025-12-26T14:30:00.012Z",
    "exploration_id": "exp_7f3a2b",
    "subentity_id": "se_root001",
    "actor_id": "actor_edmund",
    "tick": 42,
    "step_number": 1,
    "level": "STEP"
  },
  "state": {
    "before": "SEEKING",
    "after": "SEEKING",
    "transition_reason": null,
    "position": {
      "node_id": "moment_question",
      "node_type": "moment",
      "node_name": "Edmund asks about betrayal"
    },
    "depth": 0,
    "satisfaction": 0.00,
    "criticality": 0.00
  },
  "decision": {
    "type": "traverse",
    "candidates": [
      {
        "link_id": "link_001",
        "target_id": "narrative_betrayal",
        "target_type": "narrative",
        "score": 0.82,
        "components": {
          "semantic": 0.91,
          "polarity": 0.95,
          "permanence_factor": 0.90,
          "self_novelty": 1.00,
          "sibling_divergence": 1.00
        }
      },
      {
        "link_id": "link_002",
        "target_id": "space_courtyard",
        "target_type": "space",
        "score": 0.34,
        "components": {
          "semantic": 0.45,
          "polarity": 0.80,
          "permanence_factor": 0.85,
          "self_novelty": 1.00,
          "sibling_divergence": 1.00
        }
      },
      {
        "link_id": "link_003",
        "target_id": "thing_letter",
        "target_type": "thing",
        "score": 0.28,
        "components": {
          "semantic": 0.35,
          "polarity": 0.90,
          "permanence_factor": 0.80,
          "self_novelty": 1.00,
          "sibling_divergence": 1.00
        }
      }
    ],
    "selected": {
      "link_id": "link_001",
      "reason": "highest_score"
    }
  },
  "movement": {
    "from": {"node_id": "moment_question", "node_type": "moment"},
    "to": {"node_id": "narrative_betrayal", "node_type": "narrative"},
    "via": {
      "link_id": "link_001",
      "polarity_used": 0.95,
      "permanence": 0.10,
      "energy_before": 0.00,
      "energy_after": 0.29
    }
  },
  "findings": {
    "found_narratives": {},
    "found_count": 0,
    "new_this_step": null
  },
  "tree": {
    "parent_id": null,
    "sibling_ids": [],
    "children_ids": [],
    "active_siblings": 0
  },
  "emotions": {
    "joy_sadness": 0.0,
    "trust_disgust": 0.0,
    "fear_anger": 0.0,
    "surprise_anticipation": 0.0
  }
}
```

### Line 3: RESONATING (found narrative_betrayal)

```json
{
  "header": {
    "timestamp": "2025-12-26T14:30:00.024Z",
    "exploration_id": "exp_7f3a2b",
    "subentity_id": "se_root001",
    "step_number": 2
  },
  "state": {
    "before": "SEEKING",
    "after": "RESONATING",
    "transition_reason": "arrived_at_narrative",
    "position": {"node_id": "narrative_betrayal", "node_type": "narrative"},
    "depth": 0,
    "satisfaction": 0.43,
    "criticality": 0.00
  },
  "decision": {
    "type": "resonate",
    "alignment": 0.87,
    "narrative_id": "narrative_betrayal",
    "action": "continue_exploring"
  },
  "findings": {
    "found_narratives": {"narrative_betrayal": 0.87},
    "found_count": 1,
    "new_this_step": "narrative_betrayal",
    "alignment_this_step": 0.87
  }
}
```

### Line 5: BRANCH event

```json
{
  "event": "BRANCH",
  "exploration_id": "exp_7f3a2b",
  "parent_id": "se_root001",
  "position": "moment_crossroads",
  "timestamp": "2025-12-26T14:30:00.048Z",
  "children": [
    {
      "id": "se_child01",
      "target_link": "link_006",
      "target_node": "narrative_trust",
      "initial_score": 0.68
    },
    {
      "id": "se_child02",
      "target_link": "link_007",
      "target_node": "space_garden",
      "initial_score": 0.61
    }
  ]
}
```

### Line 8: Child with sibling divergence

```json
{
  "header": {
    "timestamp": "2025-12-26T14:30:00.072Z",
    "exploration_id": "exp_7f3a2b",
    "subentity_id": "se_child01",
    "step_number": 2
  },
  "state": {
    "before": "SEEKING",
    "after": "SEEKING",
    "position": {"node_id": "narrative_trust", "node_type": "narrative"},
    "depth": 1,
    "satisfaction": 0.43,
    "criticality": 0.29
  },
  "decision": {
    "type": "traverse",
    "candidates": [
      {
        "link_id": "link_008",
        "target_id": "actor_john",
        "score": 0.31,
        "components": {
          "semantic": 0.42,
          "polarity": 0.80,
          "permanence_factor": 0.75,
          "self_novelty": 0.88,
          "sibling_divergence": 0.95
        }
      }
    ],
    "selected": {"link_id": "link_008", "reason": "only_option"}
  },
  "tree": {
    "parent_id": "se_root001",
    "sibling_ids": ["se_child02"],
    "children_ids": [],
    "active_siblings": 1
  }
}
```

### Line 12: MERGE event

```json
{
  "event": "MERGE",
  "exploration_id": "exp_7f3a2b",
  "subentity_id": "se_child01",
  "parent_id": "se_root001",
  "timestamp": "2025-12-26T14:30:00.156Z",
  "contributed_narratives": {"narrative_trust": 0.72},
  "satisfaction_contributed": 0.61,
  "crystallized": null,
  "path_length": 2
}
```

### Final Line: EXPLORATION_END

```json
{
  "event": "EXPLORATION_END",
  "exploration_id": "exp_7f3a2b",
  "timestamp": "2025-12-26T14:30:00.847Z",
  "duration_ms": 847,
  "total_subentities": 3,
  "total_steps": 12,
  "nodes_visited": ["moment_question", "narrative_betrayal", "moment_crossroads", "narrative_trust", "actor_john", "space_garden"],
  "links_traversed": 5,
  "found_narratives": {
    "narrative_betrayal": 0.87,
    "narrative_trust": 0.72
  },
  "crystallized": null,
  "satisfaction": 0.71
}
```

---

## Index Entry

File: `mind/data/logs/traversal_index.jsonl`

```json
{"exploration_id":"exp_7f3a2b","actor_id":"actor_edmund","intention":"find truth about the betrayal","started":"2025-12-26T14:30:00.000Z","duration_ms":847,"subentities":3,"steps":12,"narratives_found":2,"crystallized":false,"satisfaction":0.71,"log_file":"traversal_exp_7f3a2b.jsonl"}
```

---

## Query Examples

With JSONL format, easy to analyze with `jq`:

```bash
# All decisions where sibling_divergence < 0.5
cat traversal_exp_7f3a2b.jsonl | jq 'select(.decision.candidates[]?.components.sibling_divergence < 0.5)'

# All BRANCH events
cat traversal_exp_7f3a2b.jsonl | jq 'select(.event == "BRANCH")'

# Steps where satisfaction increased
cat traversal_exp_7f3a2b.jsonl | jq 'select(.findings.new_this_step != null)'

# Average link score per exploration
cat traversal_exp_7f3a2b.jsonl | jq '[.decision.candidates[]?.score] | add / length'
```
