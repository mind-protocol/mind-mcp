# TraversalLogger Implementation

```
STATUS: CANONICAL
CREATED: 2025-12-26
MODULE: physics/traversal_logger
```

---

## PURPOSE

Agent-comprehensible logging for SubEntity exploration. Every traversal step is recorded with full context, explanations, and analysis to make exploration behavior understandable to AI agents.

---

## CODE LOCATIONS

| Component | File | Description |
|-----------|------|-------------|
| TraversalLogger | `runtime/physics/traversal_logger.py:692` | Main logger class |
| Data Classes | `runtime/physics/traversal_logger.py:66-354` | LinkCandidate, DecisionInfo, StepRecord, etc. |
| ExplanationGenerator | `runtime/physics/traversal_logger.py:399-527` | Natural language explanations |
| AnomalyDetector | `runtime/physics/traversal_logger.py:529-591` | Detects exploration anomalies |
| CausalChainBuilder | `runtime/physics/traversal_logger.py:594-641` | Builds cause-effect chains |
| LearningSignalExtractor | `runtime/physics/traversal_logger.py:644-685` | Extracts learning signals |
| State Diagram | `runtime/physics/traversal_logger.py:360-392` | ASCII state machine diagram |
| generate_exploration_id | `runtime/physics/traversal_logger.py:1186` | Descriptive ID generator |
| Tests | `runtime/tests/test_traversal_logger.py` | 48 tests |

---

## DATA CLASSES

### LinkCandidate

```python
@dataclass
class LinkCandidate:
    link_id: str
    target_id: str
    target_type: str
    target_name: str = ""
    score: float = 0.0

    # Score components
    semantic: float = 0.0
    polarity: float = 0.0
    permanence_factor: float = 0.0  # 1 - permanence
    self_novelty: float = 0.0
    sibling_divergence: float = 0.0

    # Agent-comprehensible additions
    verdict: str = ""  # SELECTED, REJECTED, TIED
    why_not: Optional[str] = None  # Explanation if rejected
    semantic_interpretation: str = ""
```

### DecisionInfo

```python
@dataclass
class DecisionInfo:
    decision_type: str  # traverse, branch, resonate, reflect, crystallize, merge, dead_end
    candidates: List[LinkCandidate] = field(default_factory=list)
    selected_link_id: Optional[str] = None
    selection_reason: str = ""

    # Agent-comprehensible additions
    explanation: str = ""
    confidence: float = 0.0
    confidence_factors: Dict[str, float] = field(default_factory=dict)
    confidence_interpretation: str = ""
    branch_info: Optional[Dict[str, Any]] = None
    counterfactual: Optional[Dict[str, Any]] = None
```

### StepRecord

Complete record of a single exploration step with:
- Header: timestamp, exploration_id, subentity_id, tick, step_number
- State: before/after, position, depth, satisfaction, criticality
- Decision: type, candidates, selection
- Movement: from/to nodes, via link
- Findings: narratives found, new this step
- Tree: parent_id, sibling_ids, children_ids
- Emotions: joy_sadness, trust_disgust, fear_anger, surprise_anticipation
- Agent additions: progress_narrative, anomalies, causal_chain, learning_signals, exploration_context, state_diagram

---

## HELPER CLASSES

### ExplanationGenerator

Generates natural language explanations:

| Method | Purpose |
|--------|---------|
| `explain_link_selection()` | Why a link was selected over others |
| `explain_branch()` | Why branching occurred |
| `explain_dead_end()` | Why exploration hit a dead end |
| `explain_resonance()` | How narrative resonance affected satisfaction |
| `generate_why_not()` | Why a candidate was rejected |

### AnomalyDetector

Detects anomalies in exploration:

| Anomaly Type | Severity | Trigger |
|--------------|----------|---------|
| `LOW_SIBLING_DIVERGENCE` | WARN | Selected link divergence < 0.5 |
| `BACKTRACK` | INFO | Revisiting previously visited node |
| `SATISFACTION_PLATEAU` | WARN | No satisfaction change for 5 steps |
| `DEEP_EXPLORATION` | INFO | Depth > 8 |
| `HIGH_CRITICALITY_NO_FINDINGS` | WARN | Criticality > 0.8 with no narratives |

### CausalChainBuilder

Builds cause-effect chains:
- State transition causes (arrived at narrative → RESONATING)
- Satisfaction change causes (alignment → satisfaction increase)
- Decision causes (high semantic → selected as best)

### LearningSignalExtractor

Extracts learning signals:
- `semantic_alignment_predictive`: High semantic correctly predicted valuable narrative
- `container_nodes_indirect`: Space/thing nodes led to dead end
- `branching_initiated`: Parallel exploration started

---

## LOGGER API

### Exploration ID Generation

```python
from mind.physics.traversal_logger import generate_exploration_id

# Generate descriptive exploration ID
exp_id = generate_exploration_id("actor_edmund", "find truth about betrayal")
# Result: exp_edmund_find_truth_about_betrayal_20251226_143052

# Format: exp_{actor}_{query_slug}_{YYYYMMDD}_{HHMMSS}
```

Features:
- Removes `actor_` prefix from actor_id
- Slugifies intention (lowercase, underscores, no special chars)
- Limits query to 40 characters
- Appends UTC timestamp

### Initialization

```python
logger = TraversalLogger(
    log_dir=Path("mind/data/logs/traversal"),
    level=LogLevel.STEP,
    enable_human_readable=True,
    enable_jsonl=True,
)

# Or use factory
logger = create_traversal_logger(log_dir=custom_path)

# Or use singleton
logger = get_traversal_logger()
```

### Exploration Lifecycle

```python
# Start exploration
logger.exploration_start(
    exploration_id="exp_abc123",
    actor_id="actor_edmund",
    origin_moment="moment_question",
    intention="find truth about betrayal",
    root_subentity_id="se_root",
)

# Log each step
step = logger.log_step(
    exploration_id="exp_abc123",
    subentity_id="se_001",
    actor_id="actor_edmund",
    tick=42,
    step_number=1,
    state_before="SEEKING",
    state_after="RESONATING",
    # ... all other fields
)

# End exploration
logger.exploration_end(
    exploration_id="exp_abc123",
    found_narratives={"narrative_betrayal": 0.85},
    satisfaction=0.78,
)
```

### Event Logging

```python
# Log branch
logger.log_branch(
    exploration_id="exp_abc123",
    parent_id="se_parent",
    position="moment_crossroads",
    children=[
        {"id": "se_child_1", "target": "narrative_1"},
        {"id": "se_child_2", "target": "space_1"},
    ],
)

# Log merge
logger.log_merge(
    exploration_id="exp_abc123",
    child_id="se_child_1",
    parent_id="se_parent",
    contributed_narratives={"narrative_betrayal": 0.85},
    satisfaction=0.6,
    crystallized=None,
)

# Log crystallize
logger.log_crystallize(
    exploration_id="exp_abc123",
    subentity_id="se_001",
    new_narrative_id="narrative_new_001",
    novelty_score=0.23,
    path_length=12,
)
```

---

## OUTPUT FILES

### JSONL (Machine-Readable)

Location: `runtime/data/logs/traversal/traversal_{exploration_id}.jsonl`

One JSON object per line:
```json
{"event":"EXPLORATION_START","exploration_id":"exp_abc123","actor_id":"actor_edmund",...}
{"header":{"timestamp":"...","step_number":1},"state":{...},"decision":{...},"progress_narrative":"..."}
{"event":"EXPLORATION_END","total_steps":47,"satisfaction":0.78,...}
```

### Human-Readable

Location: `runtime/data/logs/traversal/traversal_{exploration_id}.txt`

Formatted output:
```
════════════════════════════════════════════════════════════════════════════════
 EXPLORATION exp_abc123
════════════════════════════════════════════════════════════════════════════════
 Actor:     actor_edmund
 Intention: "find truth about betrayal"
 Origin:    moment_question
────────────────────────────────────────────────────────────────────────────────

[se_001] RESONATING @ narrative_betrayal
    Step 1: Transitioned from SEEKING to RESONATING. Found narrative_betrayal (alignment=0.85).
    ├─ candidates:
    │   ├─ link_001 → narrative_betrayal (narrative) score=0.72 ✓
    │   │      sem=0.85 pol=0.90 perm=0.80 nov=0.95 div=1.00
    │   └─ link_002 → space_garden (space) score=0.31 ✗
    │          sem=0.40 pol=0.85 perm=0.90 nov=0.98 div=0.95
    │          Rejected: weak semantic match (0.40)
    └─ Selected narrative_betrayal because of strong semantic alignment (0.85)
    ★ Found: narrative_betrayal (alignment=0.85)
    satisfaction=0.50 criticality=0.25 depth=1
```

---

## LOG LEVELS

| Level | What | When |
|-------|------|------|
| `TRACE` | Everything including embeddings | Deep debugging |
| `STEP` | Each step with decision details | Normal debugging |
| `EVENT` | State changes, branches, crystallizations | Production monitoring |
| `SUMMARY` | Start/end only | Always |

Default: `STEP` for dev, `EVENT` for prod.

---

## INTEGRATION

### With SubEntity

```python
# In SubEntity exploration runner
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

## AGENT-COMPREHENSIBLE FEATURES

1. **Natural Language Explanations** — "Selected X because of strong semantic alignment (0.85)"
2. **Why Not** — "Rejected: weak semantic match (0.40)"
3. **Counterfactuals** — What would have happened if another choice was made
4. **Progress Narratives** — "Step 5: Making progress. Found narrative_betrayal."
5. **Anomaly Flags** — Detects and explains unusual behavior
6. **Causal Chains** — "High semantic alignment → Selected as best candidate"
7. **Decision Confidence** — Score + interpretation
8. **Exploration Context** — Steps taken, nodes visited, estimated remaining
9. **State Diagrams** — ASCII visualization of current state
10. **Learning Signals** — What can be learned from this step

---

## LINKS

- DESIGN: `docs/physics/DESIGN_Traversal_Logger.md`
- EXAMPLE: `docs/physics/EXAMPLE_Traversal_Log.md`
- IMPL: `runtime/physics/traversal_logger.py`
- TESTS: `runtime/tests/test_traversal_logger.py`
- SUBENTITY: `runtime/physics/subentity.py`
