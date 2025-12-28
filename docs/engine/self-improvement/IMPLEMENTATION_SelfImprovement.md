# Self-Improvement — Implementation

```
STATUS: DESIGNING
VERSION: v0.1
UPDATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_SelfImprovement.md
PATTERNS:       ./PATTERNS_SelfImprovement.md
BEHAVIORS:      ./BEHAVIORS_SelfImprovement.md
ALGORITHM:      ./ALGORITHM_SelfImprovement.md
VALIDATION:     ./VALIDATION_SelfImprovement.md
THIS:           ./IMPLEMENTATION_SelfImprovement.md
HEALTH:         ./HEALTH_SelfImprovement.md
SYNC:           ./SYNC_SelfImprovement.md
```

---

## CODE STRUCTURE

```
mind/improvement/
├── __init__.py
├── loop.py                    # Main improvement loop runner
├── triggers.py                # Trigger handlers and queue
├── signals/
│   ├── __init__.py
│   ├── collector.py           # Signal collection orchestrator
│   ├── sources/
│   │   ├── exploration.py     # Exploration log signals
│   │   ├── agent.py           # Agent trace signals
│   │   ├── health.py          # Doctor health signals
│   │   └── graph.py           # Graph event signals
│   └── aggregator.py          # Signal aggregation
├── diagnosis/
│   ├── __init__.py
│   ├── pattern_detector.py    # Pattern detection algorithms
│   ├── layer_attribution.py   # Root cause layer attribution
│   └── evidence.py            # Evidence gathering per layer
├── proposals/
│   ├── __init__.py
│   ├── generator.py           # Proposal generation
│   ├── types.py               # Proposal type definitions
│   ├── scorer.py              # Proposal scoring
│   └── templates/
│       ├── constant_tune.py
│       ├── formula_change.py
│       ├── behavior_fix.py
│       ├── protocol_update.py
│       └── skill_improve.py
├── validation/
│   ├── __init__.py
│   ├── validator.py           # Validation orchestrator
│   ├── modes/
│   │   ├── unit_test.py
│   │   ├── shadow.py
│   │   ├── canary.py
│   │   └── ab_test.py
│   └── metrics.py             # Metrics collection for validation
├── approval/
│   ├── __init__.py
│   ├── tiers.py               # Approval tier logic
│   ├── queue.py               # Human approval queue
│   └── notifications.py       # Approval notifications
├── deployment/
│   ├── __init__.py
│   ├── deployer.py            # Deployment execution
│   ├── backup.py              # Backup creation and restoration
│   ├── monitor.py             # Post-deploy monitoring
│   └── rollback.py            # Rollback execution
├── learning/
│   ├── __init__.py
│   ├── extractor.py           # Learning extraction from cycles
│   ├── pattern_library.py     # Known patterns and fixes
│   └── embeddings.py          # Pattern embeddings for similarity
├── audit/
│   ├── __init__.py
│   ├── logger.py              # Audit log writer
│   └── store.py               # Audit record storage
├── config.py                  # Configuration and thresholds
└── models.py                  # Data models (Proposal, Diagnosis, etc.)

mind/tests/
├── test_improvement_loop.py
├── test_pattern_detection.py
├── test_layer_attribution.py
├── test_proposals.py
├── test_validation.py
├── test_deployment.py
└── test_learning.py

mind/data/
├── improvement/
│   ├── patterns/              # Pattern library storage
│   ├── proposals/             # Proposal history
│   ├── deployments/           # Deployment records
│   └── audit/                 # Audit logs
└── config/
    └── improvement_config.yaml
```

---

## FILE RESPONSIBILITIES

### mind/improvement/loop.py

**Purpose:** Main improvement loop runner and cycle orchestration.

**Key exports:**
- `ImprovementLoop` — Main loop class
- `ImprovementCycle` — Single cycle dataclass
- `run_improvement_loop()` — Entry point
- `stop_improvement_loop()` — Graceful shutdown

**Key methods:**
- `start()` — Start loop, begin listening for triggers
- `handle_trigger()` — Process incoming trigger
- `run_cycle()` — Execute full improvement cycle
- `shutdown()` — Clean shutdown with state preservation

**Lines:** ~400 (estimated)

---

### mind/improvement/signals/collector.py

**Purpose:** Orchestrate signal collection from all sources.

**Key exports:**
- `SignalCollector` — Main collector class
- `SignalSet` — Collected signal container
- `collect_signals()` — Collection entry point

**Key methods:**
- `collect()` — Collect from all sources for time window
- `filter()` — Apply relevance filters
- `aggregate()` — Compute aggregates from signals

**Lines:** ~250 (estimated)

---

### mind/improvement/diagnosis/pattern_detector.py

**Purpose:** Detect patterns from aggregated signals.

**Key exports:**
- `PatternDetector` — Main detector class
- `Pattern` — Pattern dataclass
- `detect_patterns()` — Detection entry point

**Key methods:**
- `detect_recurring()` — Find recurring anomalies
- `detect_drift()` — Find metric trends
- `detect_correlation()` — Find correlated metrics
- `score_pattern()` — Compute pattern significance

**Lines:** ~350 (estimated)

---

### mind/improvement/diagnosis/layer_attribution.py

**Purpose:** Attribute root cause to specific layer.

**Key exports:**
- `LayerAttributor` — Main attribution class
- `Diagnosis` — Diagnosis dataclass
- `Layer` — Layer enum
- `diagnose()` — Attribution entry point

**Key methods:**
- `gather_evidence()` — Collect evidence per layer
- `attribute_layer()` — Find root cause layer
- `compute_confidence()` — Diagnosis confidence score

**Lines:** ~400 (estimated)

---

### mind/improvement/proposals/generator.py

**Purpose:** Generate improvement proposals from diagnosis.

**Key exports:**
- `ProposalGenerator` — Main generator class
- `Proposal` — Proposal dataclass
- `generate_proposals()` — Generation entry point

**Key methods:**
- `generate()` — Create proposals for diagnosis
- `from_known_pattern()` — Adapt known fix
- `score_proposals()` — Rank proposals
- `add_validation_plans()` — Attach validation plans

**Lines:** ~300 (estimated)

---

### mind/improvement/validation/validator.py

**Purpose:** Orchestrate proposal validation.

**Key exports:**
- `Validator` — Main validation class
- `ValidationResult` — Result dataclass
- `validate()` — Validation entry point

**Key methods:**
- `select_mode()` — Choose validation mode
- `run_validation()` — Execute selected mode
- `collect_metrics()` — Gather comparison metrics
- `compute_result()` — Determine pass/fail

**Lines:** ~300 (estimated)

---

### mind/improvement/deployment/deployer.py

**Purpose:** Execute deployments with safety measures.

**Key exports:**
- `Deployer` — Main deployer class
- `DeploymentResult` — Result dataclass
- `deploy()` — Deployment entry point

**Key methods:**
- `create_backup()` — Backup before change
- `apply_change()` — Apply proposal changes
- `verify()` — Run verification tests
- `start_monitoring()` — Begin post-deploy watch

**Lines:** ~350 (estimated)

---

### mind/improvement/learning/pattern_library.py

**Purpose:** Store and query known patterns and fixes.

**Key exports:**
- `PatternLibrary` — Main library class
- `KnownPattern` — Known pattern dataclass
- `ProvenFix` — Proven fix dataclass

**Key methods:**
- `find_similar()` — Find matching known patterns
- `get_fix()` — Get proven fix for pattern
- `record_diagnosis()` — Store pattern → diagnosis
- `record_fix()` — Store fix outcome

**Lines:** ~400 (estimated)

---

## DESIGN PATTERNS

### Architecture Pattern: Event-Driven Loop

The improvement loop is event-driven, not scheduled:

```python
class ImprovementLoop:
    def __init__(self):
        self.trigger_queue = asyncio.Queue()
        self.running = False

    async def start(self):
        self.running = True
        asyncio.create_task(self._listen_health_events())
        asyncio.create_task(self._listen_pattern_events())
        asyncio.create_task(self._periodic_check())

        while self.running:
            trigger = await self.trigger_queue.get()
            await self.handle_trigger(trigger)

    async def handle_trigger(self, trigger: Trigger):
        cycle = ImprovementCycle(trigger=trigger)
        await self.run_cycle(cycle)
```

### Code Patterns

**Phased Execution:**
```python
async def run_cycle(self, cycle: ImprovementCycle):
    try:
        cycle.signals = await self.observe(cycle)
        cycle.patterns = await self.diagnose(cycle)
        cycle.proposals = await self.propose(cycle)
        cycle.validation = await self.validate(cycle)
        cycle.approval = await self.approve(cycle)
        cycle.deployment = await self.deploy(cycle)
        cycle.learning = await self.learn(cycle)
    except CycleError as e:
        await self.handle_cycle_error(cycle, e)
```

**Type-Specific Dispatch:**
```python
def generate_proposals(self, diagnosis: Diagnosis) -> List[Proposal]:
    generators = {
        Layer.PHYSICS: self._generate_physics_proposals,
        Layer.BEHAVIOR: self._generate_behavior_proposals,
        Layer.PROTOCOL: self._generate_protocol_proposals,
        Layer.SKILL: self._generate_skill_proposals,
    }

    generator = generators.get(diagnosis.root_layer)
    if generator:
        return generator(diagnosis)
    return []
```

**Validation Mode Strategy:**
```python
class Validator:
    def __init__(self):
        self.modes = {
            ValidationMode.UNIT_TEST: UnitTestValidator(),
            ValidationMode.SHADOW_MODE: ShadowValidator(),
            ValidationMode.CANARY: CanaryValidator(),
            ValidationMode.AB_TEST: ABTestValidator(),
        }

    async def validate(self, proposal: Proposal) -> ValidationResult:
        mode = self.select_mode(proposal)
        validator = self.modes[mode]
        return await validator.run(proposal)
```

---

## ENTRY POINTS

| Entry Point | Location | Trigger |
|-------------|----------|---------|
| `start_improvement_loop()` | loop.py | System startup |
| `trigger_improvement()` | triggers.py | External trigger |
| `check_patterns()` | pattern_detector.py | Periodic check |
| `human_approve()` | queue.py | Human approval action |
| `force_rollback()` | rollback.py | Manual rollback |

---

## DATA FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                      │
└─────────────────────────────────────────────────────────────────────────┘

External Events (health breach, pattern, periodic, human)
    │
    ▼
┌─────────────┐
│   TRIGGER   │ ──────────────────────────────────────────────────────┐
└─────────────┘                                                        │
    │                                                                  │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│   OBSERVE   │ ◀── │ Signal Sources                               │   │
└─────────────┘     │  • exploration_logs/*.jsonl                  │   │
    │               │  • agent_traces/*.jsonl                      │   │
    │               │  • health_metrics (doctor)                   │   │
    │               │  • graph_events (graph_ops)                  │   │
    │               └─────────────────────────────────────────────┘   │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│  DIAGNOSE   │ ◀── │ Pattern Library                             │   │
└─────────────┘     │  • known patterns                           │   │
    │               │  • prior diagnoses                          │   │
    │               │  • fix history                              │   │
    │               └─────────────────────────────────────────────┘   │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│   PROPOSE   │ ──▶ │ Proposal Types                              │   │
└─────────────┘     │  • constant_tune                            │   │
    │               │  • formula_change                           │   │
    │               │  • behavior_fix                             │   │
    │               │  • protocol_update                          │   │
    │               │  • skill_improve                            │   │
    │               └─────────────────────────────────────────────┘   │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│  VALIDATE   │ ──▶ │ Validation Modes                            │   │
└─────────────┘     │  • unit_test                                │   │
    │               │  • shadow_mode                              │   │
    │               │  • canary                                   │   │
    │               │  • ab_test                                  │   │
    │               └─────────────────────────────────────────────┘   │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│   APPROVE   │ ◀── │ Approval Queue (human)                      │   │
└─────────────┘     └─────────────────────────────────────────────┘   │
    │                                                                  │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│   DEPLOY    │ ──▶ │ Affected Files                              │   │
└─────────────┘     │  • mind/physics/constants.py              │   │
    │               │  • mind/physics/*.py                      │   │
    │               │  • protocols/*.yaml                         │   │
    │               │  • skills/*.md                              │   │
    │               └─────────────────────────────────────────────┘   │
    ▼                                                                  │
┌─────────────┐     ┌─────────────────────────────────────────────┐   │
│   LEARN     │ ──▶ │ Pattern Library (update)                    │   │
└─────────────┘     │  • new patterns                             │   │
    │               │  • diagnosis records                        │   │
    │               │  • fix outcomes                             │   │
    │               └─────────────────────────────────────────────┘   │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
                              (next cycle)
```

---

## STATE MANAGEMENT

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Active cycles | Memory (loop.py) | Per loop | Loop lifetime |
| Trigger queue | Memory (triggers.py) | Per loop | Loop lifetime |
| Pattern library | Disk (patterns/) | Global | Persistent |
| Proposal history | Disk (proposals/) | Global | Persistent |
| Audit log | Disk (audit/) | Global | Persistent, immutable |
| Deployment backups | Disk (backups/) | Per deployment | Until cleanup |
| Validation state | Memory (validator.py) | Per validation | Validation lifetime |

---

## CONFIGURATION

```yaml
# mind/data/config/improvement_config.yaml

# Trigger thresholds
triggers:
  pattern_threshold: 3          # Min occurrences for pattern
  drift_threshold: 0.05         # Min trend for drift
  correlation_threshold: 0.7    # Min for correlation

# Observation
observation:
  window_default: 24h
  window_max: 7d
  overhead_limit: 0.05          # 5% max overhead

# Validation
validation:
  shadow_duration: 1h
  canary_duration: 4h
  canary_percentage: 10
  ab_duration: 24h
  significance_threshold: 0.95

# Deployment
deployment:
  monitor_duration: 24h
  degradation_threshold: 0.1    # 10% triggers rollback
  rollback_timeout: 5m

# Approval
approval:
  auto_tier_max_risk: low
  auto_tier_types: [constant_tune]
  require_tier_types: [formula_change, behavior_fix]
  approval_timeout: 7d

# Learning
learning:
  similarity_threshold: 0.8
  min_fixes_for_confidence: 3

# Meta
meta:
  max_cycles_per_day: 1
  require_tier: true
```

---

## DEPENDENCIES

### Internal

| Module | Depends On | For |
|--------|------------|-----|
| loop | triggers, signals, diagnosis, proposals, validation, deployment, learning | Full cycle |
| signals | traversal_logger, agent_tracer, doctor, graph_ops | Signal sources |
| diagnosis | pattern_library | Known patterns |
| proposals | diagnosis, pattern_library | Proposal templates |
| validation | metrics, deployer | Test execution |
| deployment | backup, monitor, rollback | Safe deployment |
| learning | pattern_library, embeddings | Knowledge storage |

### External

| Package | Version | For |
|---------|---------|-----|
| asyncio | stdlib | Async loop |
| dataclasses | stdlib | Data models |
| numpy | >=1.20 | Statistics |
| scipy | >=1.7 | Statistical tests |
| pyyaml | >=6.0 | Config loading |

---

## BIDIRECTIONAL LINKS

### Code → Docs

```python
# mind/improvement/loop.py:1
"""
Self-Improvement Loop — Continuous System Improvement

Schema: docs/mind/self-improvement/ALGORITHM_SelfImprovement.md
Patterns: docs/mind/self-improvement/PATTERNS_SelfImprovement.md
Validation: docs/mind/self-improvement/VALIDATION_SelfImprovement.md
"""
```

### Docs → Code

| Doc Section | Code Location |
|-------------|---------------|
| Trigger handling | loop.py:handle_trigger |
| Signal collection | signals/collector.py:collect |
| Pattern detection | diagnosis/pattern_detector.py:detect_patterns |
| Layer attribution | diagnosis/layer_attribution.py:diagnose |
| Proposal generation | proposals/generator.py:generate |
| Validation modes | validation/modes/*.py |
| Deployment execution | deployment/deployer.py:deploy |
| Learning extraction | learning/extractor.py:extract |

---

## TESTS

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| test_improvement_loop.py | Loop lifecycle, cycle execution | V1, V2 |
| test_pattern_detection.py | Pattern detection algorithms | V5 |
| test_layer_attribution.py | Layer attribution logic | V5 |
| test_proposals.py | Proposal generation, typing | V6 |
| test_validation.py | Validation modes | V1 |
| test_deployment.py | Deployment, rollback | V3, V4, V9 |
| test_learning.py | Learning extraction, library | V8 |
| test_invariants.py | All invariant checks | V1-V10 |

---

## IMPLEMENTATION ORDER

### Phase 1: Foundation
1. `models.py` — Core data structures
2. `config.py` — Configuration loading
3. `audit/` — Audit logging (V2)
4. `loop.py` — Basic loop structure

### Phase 2: Observation
5. `signals/sources/` — Signal source adapters
6. `signals/collector.py` — Signal collection
7. `signals/aggregator.py` — Aggregation

### Phase 3: Diagnosis
8. `diagnosis/pattern_detector.py` — Pattern detection
9. `diagnosis/evidence.py` — Evidence gathering
10. `diagnosis/layer_attribution.py` — Layer attribution

### Phase 4: Proposals
11. `proposals/types.py` — Proposal types
12. `proposals/templates/` — Per-type generators
13. `proposals/generator.py` — Orchestration
14. `proposals/scorer.py` — Scoring

### Phase 5: Validation
15. `validation/modes/unit_test.py` — Unit test mode
16. `validation/modes/shadow.py` — Shadow mode
17. `validation/validator.py` — Orchestration

### Phase 6: Deployment
18. `deployment/backup.py` — Backup/restore (V3)
19. `deployment/deployer.py` — Deployment execution
20. `deployment/monitor.py` — Post-deploy monitoring
21. `deployment/rollback.py` — Rollback (V9)

### Phase 7: Approval
22. `approval/tiers.py` — Tier logic (V4)
23. `approval/queue.py` — Human approval queue
24. `approval/notifications.py` — Notifications

### Phase 8: Learning
25. `learning/pattern_library.py` — Pattern storage
26. `learning/extractor.py` — Learning extraction (V8)
27. `learning/embeddings.py` — Pattern similarity

### Phase 9: Integration
28. Integration tests
29. End-to-end tests
30. Documentation updates
