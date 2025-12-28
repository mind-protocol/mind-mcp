# SubEntity — Implementation

```
STATUS: CANONICAL
VERSION: v1.9
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SubEntity.md
PATTERNS:       ./PATTERNS_SubEntity.md
BEHAVIORS:      ./BEHAVIORS_SubEntity.md
ALGORITHM:      ./ALGORITHM_SubEntity.md
VALIDATION:     ./VALIDATION_SubEntity.md
THIS:           ./IMPLEMENTATION_SubEntity.md
HEALTH:         ./HEALTH_SubEntity.md
SYNC:           ./SYNC_SubEntity.md
```

---

## CODE STRUCTURE

```
mind/physics/
├── subentity.py              # Core SubEntity dataclass + helpers (984 lines)
├── exploration.py            # ExplorationRunner async state machine (1033 lines)
├── traversal_logger.py       # Agent-comprehensible logging (1247 lines)
├── link_scoring.py           # Link score computation
├── crystallization.py        # Embedding computation for crystallization
├── cluster_presentation.py   # Rendering crystallized content
└── flow.py                   # Forward/backward coloring, energy injection

mind/tests/
├── test_subentity.py         # SubEntity unit tests
├── test_traversal_logger.py  # Logging tests
└── test_subentity_health.py  # Health validation tests

mind/data/logs/traversal/   # Log output directory
├── traversal_{id}.jsonl      # Machine-readable logs
└── traversal_{id}.txt        # Human-readable logs
```

---

## FILE RESPONSIBILITIES

### mind/physics/subentity.py

**Purpose:** Core SubEntity dataclass and supporting utilities.

**Key exports:**
- `SubEntity` — Main dataclass with state machine, tree structure, emotions
- `SubEntityState` — Enum of states (SEEKING, BRANCHING, etc.)
- `ExplorationContext` — Registry for lazy sibling/parent resolution
- `IntentionType` — Enum of intention types (SUMMARIZE, VERIFY, etc.)
- `create_subentity()` — Factory function
- `cosine_similarity()` — Vector similarity
- `compute_self_novelty()` — Avoid backtracking
- `compute_sibling_divergence()` — Spread exploration
- `compute_link_score()` — Full link scoring

**Lines:** ~984

**Status:** OK

---

### mind/physics/exploration.py

**Purpose:** Async ExplorationRunner that executes state machine.

**Key exports:**
- `ExplorationRunner` — Main class with explore() entry point
- `ExplorationResult` — Result dataclass
- `ExplorationConfig` — Configuration (max_depth, timeout, etc.)
- `ExplorationTimeoutError` — Exception for timeouts
- `run_exploration()` — Async convenience function
- `run_exploration_sync()` — Sync wrapper

**Key methods:**
- `explore()` — Start exploration from actor
- `_run_subentity()` — State machine loop
- `_step_seeking()` — SEEKING logic
- `_step_branching()` — BRANCHING logic
- `_step_absorbing()` — ABSORBING logic (v1.9)
- `_step_resonating()` — RESONATING logic
- `_step_reflecting()` — REFLECTING logic
- `_step_crystallizing()` — CRYSTALLIZING logic
- `_step_merging()` — MERGING logic

**Lines:** ~1033

**Status:** OK

---

### mind/physics/traversal_logger.py

**Purpose:** Agent-comprehensible logging for exploration.

**Key exports:**
- `TraversalLogger` — Main logger class
- `StepRecord` — Complete step record
- `DecisionInfo` — Decision details with candidates
- `LinkCandidate` — Candidate link with score breakdown
- `MovementInfo` — From/to movement details
- `Anomaly` — Detected anomaly
- `ExplanationGenerator` — Natural language explanations
- `AnomalyDetector` — Detects exploration issues
- `CausalChainBuilder` — Builds cause-effect chains
- `LearningSignalExtractor` — Extracts learnable patterns

**Output formats:**
- JSONL: Machine-readable, one JSON per line
- TXT: Human/agent-readable formatted output

**Lines:** ~1247

**Status:** OK

---

### mind/physics/link_scoring.py

**Purpose:** Link score computation for SEEKING decisions.

**Key exports:**
- `score_outgoing_links()` — Score all links from a node
- `select_branch_candidates()` — Pick top N for branching
- `should_branch()` — Check if branching appropriate
- `get_target_node_id()` — Get link target
- `cosine_similarity()` — Vector similarity
- `max_cosine_against_set()` — Max similarity to set

**Lines:** ~200

**Status:** OK

---

### mind/physics/crystallization.py

**Purpose:** Crystallization embedding computation.

**Key exports:**
- `compute_crystallization_embedding()` — Weighted blend formula
- `check_novelty()` — Check against existing narratives

**Lines:** ~100

**Status:** OK

---

### mind/physics/flow.py

**Purpose:** Graph coloring and energy operations.

**Key exports:**
- `forward_color_link()` — Color link during traversal
- `backward_color_path()` — Reinforce path during reflecting
- `inject_node_energy()` — v1.9 energy injection
- `add_node_weight_on_resonating()` — Weight boost on finding
- `blend_embeddings()` — Weighted embedding blend
- `regenerate_link_synthesis_if_drifted()` — Update synthesis text
- `regenerate_node_synthesis_if_drifted()` — Update node synthesis

**Lines:** ~300

**Status:** OK

---

## DESIGN PATTERNS

### Architecture Pattern: Async State Machine

ExplorationRunner uses async/await with explicit state transitions.
Each state has its own step function. Branching uses asyncio.gather
for parallel child execution.

### Code Patterns

**Lazy References (v1.7.2):**
```python
sibling_ids: List[str]  # Not List[SubEntity]

@property
def siblings(self) -> List[SubEntity]:
    return [self._context.get(sid) for sid in self.sibling_ids
            if self._context.exists(sid)]
```

**Factory Function:**
```python
def create_subentity(...) -> SubEntity:
    # Normalize inputs, register with context, return
```

**Result Dataclass:**
```python
@dataclass
class ExplorationResult:
    found_narratives: Dict[str, float]
    crystallized: Optional[str]
    ...
```

---

## ENTRY POINTS

| Entry Point | Location | Trigger |
|-------------|----------|---------|
| `explore()` | exploration.py:252 | Actor spawns exploration |
| `create_subentity()` | subentity.py:933 | Factory for new SubEntity |
| `log_step()` | traversal_logger.py:879 | Each traversal step |

---

## DATA FLOW

```
Actor Request
    │
    ▼
┌─────────────────────────────────────────────────┐
│ ExplorationRunner.explore()                      │
│   │                                              │
│   ▼                                              │
│ create_subentity() ─────────────────────────────▶ SubEntity registered
│   │                                              │   in ExplorationContext
│   ▼                                              │
│ _run_subentity() ◀──────────────────────────────┐│
│   │                                              ││
│   ├─▶ _step_seeking()                            ││
│   │     ├─ score_outgoing_links()                ││
│   │     ├─ forward_color_link()                  ││
│   │     ├─ inject_node_energy()                  ││
│   │     └─ update_crystallization_embedding()    ││
│   │                                              ││
│   ├─▶ _step_branching()                          ││
│   │     ├─ spawn_child() × N                     ││
│   │     ├─ asyncio.gather() ─────────────────────┘│
│   │     └─ merge_child_results()                  │
│   │                                               │
│   ├─▶ _step_resonating()                          │
│   │     ├─ compute alignment                      │
│   │     └─ update satisfaction                    │
│   │                                               │
│   ├─▶ _step_crystallizing()                       │
│   │     ├─ create_narrative()                     │
│   │     └─ create_link() × 2                      │
│   │                                               │
│   └─▶ _step_merging() ──────────────────────────▶ ExplorationResult
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## STATE MANAGEMENT

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| SubEntity fields | SubEntity dataclass | Per exploration | Created → Merged |
| ExplorationContext._registry | ExplorationContext | Per exploration | Start → End |
| TraversalLogger._history | TraversalLogger | Per exploration | Start → End |
| Graph nodes/links | Graph database | Global | Persistent |

---

## RUNTIME BEHAVIOR

### Initialization

```python
runner = ExplorationRunner(graph, config, logger)
result = await runner.explore(
    actor_id="actor_edmund",
    query="What happened at the crossing?",
    query_embedding=[...],
    intention="find truth about betrayal",
    intention_embedding=[...],
    intention_type="summarize",
)
```

### Main Loop

State machine loop in `_run_subentity()` continues until:
1. SubEntity reaches MERGING state
2. Step count exceeds MAX_STEPS (1000)
3. Timeout (ExplorationTimeoutError raised)

### Shutdown

- MERGING state is terminal
- completed_at timestamp set
- Results collected via `collect_result()`
- Logger writes final summary

---

## CONFIGURATION

| Config | Default | Purpose |
|--------|---------|---------|
| max_depth | 10 | Maximum traversal depth |
| max_children | 3 | Maximum children per branch |
| timeout_s | 30.0 | Exploration timeout |
| min_branch_links | 2 | Minimum links to trigger branching |
| satisfaction_threshold | 0.8 | Stop when satisfied |
| novelty_threshold | 0.85 | Crystallization gate |
| min_link_score | 0.1 | Below this is dead end |

---

## BIDIRECTIONAL LINKS

### Code → Docs

```python
# mind/physics/subentity.py:1
"""
SubEntity — Temporary Consciousness Traversal (v1.9)

Schema: docs/schema/schema.yaml v1.9
Patterns: docs/physics/subentity/PATTERNS_SubEntity.md
Algorithm: docs/physics/subentity/ALGORITHM_SubEntity.md
"""
```

### Docs → Code

| Doc Section | Code Location |
|-------------|---------------|
| State machine | subentity.py:125 (SubEntityState) |
| STATE_MULTIPLIER | subentity.py:181 |
| Link scoring | subentity.py:879 (compute_link_score) |
| Crystallization embedding | subentity.py:504 |
| ExplorationRunner | exploration.py:133 |
| Logging | traversal_logger.py:692 |

---

## TESTS

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| test_subentity.py | SubEntity structure, state machine | V1, V2, V3 |
| test_traversal_logger.py | Logging functionality | Logging |
| test_subentity_health.py | Health validation | V4, V5, V7 |

---

## DEPENDENCIES

### Internal

| Module | Purpose |
|--------|---------|
| engine.physics.flow | Coloring, energy injection |
| engine.physics.link_scoring | Score computation |
| engine.physics.crystallization | Embedding computation |
| engine.physics.cluster_presentation | Content rendering |

### External

| Package | Purpose |
|---------|---------|
| asyncio | Parallel exploration |
| dataclasses | Data structures |
| typing | Type hints |
| json | Log serialization |
