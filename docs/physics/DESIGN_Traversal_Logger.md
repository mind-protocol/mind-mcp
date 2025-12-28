# TraversalLogger Design — SubEntity Exploration Logging

```
STATUS: DESIGN
CREATED: 2025-12-26
```

---

## PURPOSE

Log every SubEntity traversal step with full context for:
1. **Debugging** — understand why a SubEntity took a specific path
2. **Analysis** — identify patterns in exploration behavior
3. **Replay** — reconstruct exploration for visualization
4. **Tuning** — adjust formulas based on observed behavior

---

## LOG LEVELS

| Level | What | When |
|-------|------|------|
| `TRACE` | Every micro-decision (embedding comparisons, score components) | Deep debugging |
| `STEP` | Each traversal step with decision summary | Normal debugging |
| `EVENT` | State changes, branches, crystallizations | Production monitoring |
| `SUMMARY` | Exploration start/end with aggregate stats | Always |

Default: `STEP` for dev, `EVENT` for prod.

---

## LOG STRUCTURE

Each log entry is a structured record with these sections:

### 1. HEADER (all levels)

```yaml
header:
  timestamp: "2025-12-26T14:32:01.234Z"
  exploration_id: "exp_abc123"      # Groups all SubEntities in one exploration
  subentity_id: "se_def456"
  actor_id: "actor_edmund"
  tick: 42                          # Game tick when this occurred
  step_number: 7                    # Steps since this SubEntity spawned
  level: "STEP"
```

### 2. STATE (STEP+)

```yaml
state:
  before: "SEEKING"
  after: "SEEKING"                  # Same if no transition
  transition_reason: null           # Or "arrived_at_narrative", "no_aligned_links", etc.

  position:
    node_id: "moment_confrontation"
    node_type: "moment"
    node_name: "The Confrontation"

  depth: 3
  satisfaction: 0.35
  criticality: 0.42                 # (1 - 0.35) × (3/4)
```

### 3. DECISION (STEP+)

```yaml
decision:
  type: "traverse"                  # traverse | branch | resonate | reflect | crystallize | merge

  # For traverse decisions:
  candidates:
    - link_id: "link_001"
      target_id: "narrative_betrayal"
      target_type: "narrative"
      score: 0.72
      components:
        semantic: 0.85
        polarity: 0.90
        permanence_factor: 0.80     # 1 - permanence
        self_novelty: 0.95
        sibling_divergence: 1.00
    - link_id: "link_002"
      target_id: "space_garden"
      target_type: "space"
      score: 0.31
      components:
        semantic: 0.40
        polarity: 0.85
        permanence_factor: 0.90
        self_novelty: 0.98
        sibling_divergence: 0.95

  selected:
    link_id: "link_001"
    reason: "highest_score"         # Or "random_tiebreak", "forced_backtrack", etc.

  # For branch decisions:
  branch_info:
    outgoing_count: 3
    threshold_met: true
    children_spawned: ["se_child1", "se_child2", "se_child3"]
```

### 4. MOVEMENT (STEP+)

```yaml
movement:
  from:
    node_id: "moment_confrontation"
    node_type: "moment"
  to:
    node_id: "narrative_betrayal"
    node_type: "narrative"
  via:
    link_id: "link_001"
    polarity_used: 0.90             # Polarity in traversal direction
    permanence: 0.20
    energy_before: 0.5
    energy_after: 0.65              # After forward coloring
```

### 5. EMBEDDINGS (TRACE only)

```yaml
embeddings:
  intention:
    hash: "a1b2c3d4"                # Short hash for comparison
    norm: 1.0
    dim: 768
  crystallization:
    hash: "e5f6g7h8"
    norm: 1.0
    delta_from_last: 0.12           # Cosine distance from previous step
  position:
    hash: "i9j0k1l2"
```

### 6. FINDINGS (STEP+)

```yaml
findings:
  found_narratives:
    narrative_betrayal: 0.85
    narrative_trust: 0.62
  found_count: 2
  new_this_step: "narrative_betrayal"  # null if no new narrative
  alignment_this_step: 0.85
```

### 7. TREE (EVENT+)

```yaml
tree:
  parent_id: "se_parent123"
  sibling_ids: ["se_sib1", "se_sib2"]
  children_ids: []
  active_siblings: 2                 # How many siblings still exploring
```

### 8. EMOTIONS (STEP+)

```yaml
emotions:
  joy_sadness: 0.2
  trust_disgust: -0.3
  fear_anger: 0.1
  surprise_anticipation: 0.0
  blend_this_step:
    from_link: true
    weight: 0.15
```

### 9. FORWARD COLORING (TRACE only)

```yaml
forward_coloring:
  link_id: "link_001"
  embedding_blend_weight: 0.80      # 1 - permanence
  energy_added: 0.15
  polarity_reinforced: true
```

---

## EVENT TYPES

Special events get dedicated formats:

### EXPLORATION_START

```yaml
event: EXPLORATION_START
exploration_id: "exp_abc123"
actor_id: "actor_edmund"
origin_moment: "moment_question"
intention: "find truth about the betrayal"
intention_embedding_hash: "a1b2c3d4"
root_subentity_id: "se_root001"
timestamp: "2025-12-26T14:30:00.000Z"
```

### EXPLORATION_END

```yaml
event: EXPLORATION_END
exploration_id: "exp_abc123"
duration_ms: 1234
total_subentities: 5
total_steps: 47
found_narratives:
  narrative_betrayal: 0.92
  narrative_trust: 0.71
crystallized: null                   # Or narrative_id if created
satisfaction: 0.78
```

### BRANCH

```yaml
event: BRANCH
exploration_id: "exp_abc123"
parent_id: "se_parent123"
position: "moment_crossroads"
children:
  - id: "se_child1"
    target: "narrative_path1"
    initial_score: 0.82
  - id: "se_child2"
    target: "space_garden"
    initial_score: 0.71
```

### CRYSTALLIZE

```yaml
event: CRYSTALLIZE
exploration_id: "exp_abc123"
subentity_id: "se_def456"
new_narrative_id: "narrative_new_001"
embedding_hash: "x1y2z3w4"
novelty_score: 0.23                  # 1 - max_similarity to existing
path_length: 12
path_permanence_avg: 0.72
```

### MERGE

```yaml
event: MERGE
exploration_id: "exp_abc123"
subentity_id: "se_child1"
parent_id: "se_parent123"
contributed_narratives:
  narrative_betrayal: 0.85
satisfaction_contributed: 0.4
crystallized: null
```

---

## FILE FORMAT

### Primary Log: JSONL

One JSON object per line for easy parsing:

```
{"header":{"timestamp":"2025-12-26T14:32:01.234Z",...},"state":{...},"decision":{...}}
{"header":{"timestamp":"2025-12-26T14:32:01.456Z",...},"state":{...},"decision":{...}}
```

File: `mind/data/logs/traversal_{exploration_id}.jsonl`

### Human-Readable Summary

Separate file with formatted output:

```
═══ EXPLORATION exp_abc123 ═══
Actor: actor_edmund
Intention: "find truth about the betrayal"
Started: 2025-12-26T14:30:00Z

[se_root001] SEEKING @ moment_question
  → candidates: 3 links
  → selected: link_001 (score=0.72) → narrative_betrayal

[se_root001] RESONATING @ narrative_betrayal
  → alignment: 0.85
  → satisfaction: 0.35 → 0.52

[se_root001] BRANCHING @ moment_crossroads
  → spawned: se_child1, se_child2

  [se_child1] SEEKING @ space_garden
    → candidates: 2 links
    → selected: link_003 (score=0.61) → narrative_trust

  [se_child2] SEEKING @ thing_letter
    → no aligned links (best=0.12 < threshold)
    → REFLECTING

[se_root001] MERGING
  → found: {narrative_betrayal: 0.85, narrative_trust: 0.71}
  → satisfaction: 0.78

═══ END exp_abc123 (1.2s, 47 steps, 5 subentities) ═══
```

File: `mind/data/logs/traversal_{exploration_id}.txt`

---

## LOG ROTATION

| Log Type | Max Size | Retention |
|----------|----------|-----------|
| JSONL | 50MB | Last 100 explorations |
| Human | 10MB | Last 50 explorations |
| Summary index | 1MB | Last 1000 explorations |

Index file tracks all explorations for quick lookup:
```
mind/data/logs/traversal_index.jsonl
```

---

## API

```python
class TraversalLogger:
    """Log SubEntity exploration steps."""

    def __init__(
        self,
        log_dir: Path = Path("mind/data/logs"),
        level: LogLevel = LogLevel.STEP,
        enable_human_readable: bool = True,
    ):
        ...

    # Exploration lifecycle
    def exploration_start(
        self,
        exploration_id: str,
        actor_id: str,
        origin_moment: str,
        intention: str,
        intention_embedding: List[float],
        root_subentity_id: str,
    ) -> None: ...

    def exploration_end(
        self,
        exploration_id: str,
        found_narratives: Dict[str, float],
        crystallized: Optional[str],
        satisfaction: float,
    ) -> None: ...

    # Step logging
    def log_step(
        self,
        exploration_id: str,
        subentity: SubEntity,
        decision: TraversalDecision,
        movement: Optional[MovementInfo] = None,
    ) -> None: ...

    # Events
    def log_branch(
        self,
        exploration_id: str,
        parent: SubEntity,
        children: List[SubEntity],
    ) -> None: ...

    def log_crystallize(
        self,
        exploration_id: str,
        subentity: SubEntity,
        new_narrative_id: str,
        novelty_score: float,
    ) -> None: ...

    def log_merge(
        self,
        exploration_id: str,
        child: SubEntity,
        parent: SubEntity,
    ) -> None: ...

    # Query (for analysis)
    def get_exploration(self, exploration_id: str) -> List[Dict]: ...
    def get_recent_explorations(self, limit: int = 10) -> List[str]: ...
```

---

## DATA CLASSES

```python
@dataclass
class LinkCandidate:
    """A candidate link for traversal."""
    link_id: str
    target_id: str
    target_type: str
    score: float
    semantic: float
    polarity: float
    permanence_factor: float
    self_novelty: float
    sibling_divergence: float

@dataclass
class TraversalDecision:
    """Decision made at a step."""
    decision_type: str  # traverse, branch, resonate, reflect, crystallize, merge
    candidates: List[LinkCandidate]
    selected_link_id: Optional[str]
    selection_reason: str
    branch_info: Optional[Dict] = None

@dataclass
class MovementInfo:
    """Movement from one node to another."""
    from_node_id: str
    from_node_type: str
    to_node_id: str
    to_node_type: str
    via_link_id: str
    polarity_used: float
    permanence: float
    energy_before: float
    energy_after: float
```

---

## INTEGRATION POINTS

### In SubEntity.transition_to()

```python
def transition_to(self, new_state: SubEntityState, logger: TraversalLogger = None) -> None:
    if logger:
        logger.log_state_transition(self, self.state, new_state)
    # ... existing code
```

### In exploration runner

```python
async def run_exploration(actor_id: str, intention: str, ...):
    logger = get_traversal_logger()
    exp_id = f"exp_{uuid.uuid4().hex[:8]}"

    logger.exploration_start(exp_id, actor_id, ...)

    try:
        result = await explore(exp_id, logger, ...)
    finally:
        logger.exploration_end(exp_id, ...)
```

---

## CONFIGURATION

```yaml
# .mind-mcp/config.yaml
traversal_logging:
  enabled: true
  level: STEP              # TRACE, STEP, EVENT, SUMMARY
  log_dir: mind/data/logs
  human_readable: true
  max_jsonl_size_mb: 50
  max_human_size_mb: 10
  retention_explorations: 100

  # What to include at each level
  include:
    embeddings: false      # Only at TRACE
    full_candidates: true  # All candidates or just selected
    emotions: true
    forward_coloring: false
```

---

## EXAMPLE OUTPUT

### JSONL (one step)

```json
{
  "header": {
    "timestamp": "2025-12-26T14:32:01.234Z",
    "exploration_id": "exp_abc123",
    "subentity_id": "se_def456",
    "actor_id": "actor_edmund",
    "tick": 42,
    "step_number": 7,
    "level": "STEP"
  },
  "state": {
    "before": "SEEKING",
    "after": "SEEKING",
    "position": {"node_id": "moment_confrontation", "node_type": "moment"},
    "depth": 3,
    "satisfaction": 0.35,
    "criticality": 0.42
  },
  "decision": {
    "type": "traverse",
    "candidates": [
      {"link_id": "link_001", "target_id": "narrative_betrayal", "score": 0.72},
      {"link_id": "link_002", "target_id": "space_garden", "score": 0.31}
    ],
    "selected": {"link_id": "link_001", "reason": "highest_score"}
  },
  "movement": {
    "from": {"node_id": "moment_confrontation", "node_type": "moment"},
    "to": {"node_id": "narrative_betrayal", "node_type": "narrative"},
    "via": {"link_id": "link_001", "polarity": 0.90, "permanence": 0.20}
  },
  "findings": {
    "found_narratives": {"narrative_betrayal": 0.85},
    "new_this_step": "narrative_betrayal"
  },
  "emotions": {
    "joy_sadness": 0.2,
    "trust_disgust": -0.3
  }
}
```

---

## NEXT STEPS

1. Implement `TraversalLogger` class in `mind/physics/traversal_logger.py`
2. Add data classes for decisions and movements
3. Integrate with SubEntity and exploration runner
4. Add log rotation and index management
5. Create analysis tools for pattern detection
