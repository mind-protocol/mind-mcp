# Skill: `mind.prepare_implementation`
@mind:id: SKILL.PLAN.PREPARE_IMPLEMENTATION.COMPLEXITY_SCOPE_MILESTONES

## Maps to VIEW
`(bridge skill; runs between completed doc chain and first line of code)`

---

## Context

Implementation preparation in mind = the phase between a complete documentation chain (PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC) and the first line of code. This phase exists because large projects (50K+ lines of spec, 100K+ estimated code) fail not from bad design but from bad sequencing.

**Why this phase exists:**
- Doc chains describe WHAT to build. This skill determines HOW to sequence the build.
- Context window compactions lose state. Estimating context requirements per module prevents surprise mid-implementation amnesia.
- Modules with high connectivity require careful ordering — changing one breaks others.
- Without explicit milestones, scope creeps and "POC" becomes "rewrite everything."

**Key terms:**
- **Context budget**: Estimated tokens/compactions required to implement a module in one session
- **Technical complexity**: How many code-deploy-test cycles a module will likely need (1 = trivial, 5 = research-level)
- **Connectivity score**: How many other modules a module depends on or is depended on by (0 = isolated, 10+ = hub)
- **Milestone**: A shippable increment with testable acceptance criteria (POC → Alpha → Beta → GA)
- **Feature-milestone mapping**: Which BEHAVIORS from each module belong in which milestone

---

## Purpose
Analyze a fully-documented project to produce complexity estimates, context budgets, connectivity maps, milestone definitions, and a feature-milestone matrix — so implementation proceeds in the right order with the right expectations.

---

## Inputs
```yaml
project_root: "<path to project>"                    # string
doc_root: "<path to docs/ directory>"                # string
modules: ["<area/module>"]                           # list — auto-discovered from doc structure if empty
existing_milestones: "<path to VALIDATION with POC>" # optional — reuse existing milestone definitions
target_stack: "<language/framework>"                 # string — affects complexity estimation
hardware_target: "<device constraints if any>"       # optional — e.g. "Quest 3, 72fps, 512MB"
```

## Outputs
```yaml
complexity_matrix:
  - file: "ESTIMATION_Complexity_Matrix.md"
    content: "Per-module: context budget, technical complexity, connectivity score, estimated LOC, estimated sessions"
milestone_plan:
  - file: "ESTIMATION_Milestone_Plan.md"
    content: "Milestone definitions with feature-milestone mapping from BEHAVIORS"
dependency_graph:
  - file: "ESTIMATION_Dependency_Graph.md"
    content: "Module dependency DAG with critical path analysis"
implementation_sequence:
  - file: "ESTIMATION_Implementation_Sequence.md"
    content: "Ordered build plan: which module first, which can parallelize, where to expect compactions"
```

---

## Gates

- Every module must have all 5 scores (context budget, complexity, connectivity, estimated LOC, estimated sessions) — no hand-waving
- Milestones must trace to VALIDATION acceptance criteria — not invented from scratch
- Feature-milestone mapping must reference specific BEHAVIORS by ID — not vague descriptions
- Dependency graph must be a DAG (no cycles) — if cycles exist, document them as risks
- Implementation sequence must account for context window limits — flag modules requiring multi-session or multi-agent work
- Connectivity analysis must flag hub modules (connectivity > 5) for extra implementation caution

---

## Process

### 1. Discover and inventory modules
```yaml
batch_questions:
  - modules: "What modules exist in the doc structure? (scan docs/ for subdirectories with PATTERNS + ALGORITHM + IMPLEMENTATION)"
  - completeness: "Which modules have complete chains vs partial?"
  - existing_code: "What code already exists that implements parts of any module?"
```

Produce: Module inventory table with doc chain completeness status.

### 2. Estimate context budget per module

For each module, estimate the context window tokens required for a single implementation session:

```yaml
context_factors:
  - doc_size: "Total lines across all 6 docs for this module"
  - code_references: "How many other files must be read to implement (from IMPLEMENTATION doc)"
  - test_surface: "How many VALIDATION invariants and health checks to verify"
  - external_deps: "APIs, databases, or services to connect to"
```

**Scoring:**
| Context Budget | Tokens | Sessions | Compactions |
|---|---|---|---|
| S (Small) | < 30K | 1 session | 0 |
| M (Medium) | 30-80K | 1-2 sessions | 0-1 |
| L (Large) | 80-150K | 2-3 sessions | 1-2 |
| XL (Extra Large) | 150K+ | 3+ sessions | 2+ |

**How to estimate:**
- Read IMPLEMENTATION doc → count files to create/modify → each file ≈ 2-5K tokens to implement
- Read ALGORITHM doc → count procedures → each procedure ≈ 1-3K tokens to implement
- Read VALIDATION doc → count invariants/health checks → each check ≈ 500 tokens to verify
- Sum doc chain itself (must stay in context) → raw line count × 4 tokens/line
- Add cross-module context (files from other modules that must be loaded)

### 3. Estimate technical complexity per module

For each module, score 1-5:

```yaml
complexity_factors:
  - novelty: "Is this a known pattern or novel research? (1=standard CRUD, 5=novel algorithm)"
  - external_apis: "How many external APIs/services? (1=none, 5=3+ APIs with rate limits)"
  - real_time: "Real-time constraints? (1=no, 5=sub-frame budget on constrained hardware)"
  - state_management: "How much mutable state? (1=stateless, 5=complex state machine with persistence)"
  - error_surface: "How many failure modes? (1=few, 5=many with cascading effects)"
```

**Scoring:**
| Complexity | Score | Expected iterations | Risk |
|---|---|---|---|
| Trivial | 1 | 1 code-deploy-test | Low |
| Standard | 2 | 1-2 | Low |
| Moderate | 3 | 2-3 | Medium |
| Complex | 4 | 3-5 | High |
| Research | 5 | 5+ | Very high — may require design revision |

**Compound score:** Average of 5 factors, rounded. Modules scoring 4+ get flagged for extra review.

### 4. Analyze module connectivity

For each module, count:

```yaml
connectivity_metrics:
  - imports_from: "How many other modules does this module import from / depend on?"
  - exports_to: "How many other modules import from / depend on this module?"
  - shared_state: "How many shared data structures (caches, stores, WebSocket messages)?"
  - event_coupling: "How many event types does this module emit or consume?"
```

**Connectivity score:** `imports_from + exports_to + shared_state + event_coupling`

**Classification:**
| Score | Type | Implementation approach |
|---|---|---|
| 0-3 | Leaf | Implement independently, any order |
| 4-7 | Branch | Implement after its dependencies, test interfaces |
| 8-12 | Hub | Implement early, define interfaces first, expect rework |
| 13+ | Core | Implement first with stubs, all other modules depend on it |

**Produce:** Directed dependency graph. Identify:
- Critical path (longest chain of dependent modules)
- Parallelizable clusters (independent modules that can be built simultaneously)
- Hub modules (highest connectivity — these are the riskiest)

### 5. Estimate lines of code per module

From IMPLEMENTATION doc:
```yaml
loc_estimation:
  - count_new_files: "Number of files to create"
  - avg_file_size: "Estimated lines per file (from ALGORITHM procedure count × ~30 lines/procedure)"
  - config_files: "Configuration, constants, types files"
  - test_files: "Estimated test code (typically 1:1 ratio with source for complex modules)"
```

**Formula:** `estimated_LOC = (new_files × avg_size) + config + tests`

### 6. Define milestones from VALIDATION

Read the project's VALIDATION doc (top-level and per-module) and extract milestone definitions:

```yaml
milestone_extraction:
  - existing_pocs: "What POC milestones are already defined in VALIDATION?"
  - acceptance_criteria: "What are the testable gates for each POC?"
  - natural_increments: "What are the smallest shippable slices?"
```

**Standard milestone progression:**
| Milestone | Definition | Typical scope |
|---|---|---|
| POC | Prove the core concept works | 1-3 modules, hardcoded data OK |
| Alpha | Core loop functional end-to-end | All critical-path modules, real data |
| Beta | All features implemented, rough edges | All modules, performance not final |
| GA | Production-ready | Performance tuned, monitoring, deployment |

For each milestone, define:
- Which modules are included (fully or partially)
- Which BEHAVIORS from each module are active
- What acceptance criteria must pass (from VALIDATION)
- What can be stubbed/mocked vs must be real

### 7. Map features to milestones

For each module's BEHAVIORS doc, assign each behavior to a milestone:

```yaml
feature_mapping:
  module: "<area/module>"
  behaviors:
    - id: "B1"
      description: "<from BEHAVIORS doc>"
      milestone: "POC|Alpha|Beta|GA"
      justification: "<why this milestone>"
      dependencies: ["<other behaviors that must exist first>"]
```

**Prioritization criteria:**
- POC: Behaviors that prove the core value proposition
- Alpha: Behaviors that complete the critical user journey
- Beta: Behaviors that add depth, polish, edge cases
- GA: Behaviors related to performance, monitoring, deployment

### 8. Produce implementation sequence

Combine all analyses into an ordered build plan:

```yaml
sequence_rules:
  - "Core/Hub modules first (highest connectivity)"
  - "Dependencies before dependents (DAG order)"
  - "Within same level: highest-value milestone behaviors first"
  - "Group by natural session boundaries (context budget)"
  - "Flag multi-session modules with handoff strategy"
  - "Identify parallel tracks for multi-agent work"
```

**Output format per module:**
```yaml
- order: 1
  module: "<area/module>"
  milestone_target: "POC"
  context_budget: "M"
  complexity: 3
  connectivity: 8
  estimated_loc: 1200
  estimated_sessions: 2
  depends_on: ["<modules that must be done first>"]
  parallel_with: ["<modules that can be done simultaneously>"]
  compaction_strategy: "<how to handle context window limits>"
  behaviors_included: ["B1", "B3", "B5"]
  behaviors_deferred: ["B2→Alpha", "B4→Beta"]
```

### 9. Risk assessment

Flag specific risks:

```yaml
risk_categories:
  - context_overflow: "Modules where doc chain + code + tests exceed context window"
  - complexity_cliff: "Modules scoring 4+ complexity that may need design revision"
  - hub_fragility: "Hub modules where interface changes cascade to many dependents"
  - external_dependency: "Modules blocked on external APIs, services, or data"
  - performance_uncertainty: "Modules with real-time constraints on target hardware"
```

### 10. Write estimation documents

Produce 4 output files in the project's docs directory:

1. **ESTIMATION_Complexity_Matrix.md** — Table: module × (context, complexity, connectivity, LOC, sessions)
2. **ESTIMATION_Milestone_Plan.md** — Milestone definitions with behavior mapping
3. **ESTIMATION_Dependency_Graph.md** — ASCII DAG + critical path + parallel clusters
4. **ESTIMATION_Implementation_Sequence.md** — Ordered build plan with session boundaries

---

## Procedures Referenced

| Protocol | When | Creates |
|----------|------|---------|
| `protocol:explore_space` | Step 1: module discovery | Module inventory |
| `protocol:record_work` | Step 10: after writing docs | progress moment + handoff |

---

## Membrane Integration
```yaml
membrane_hook:
  trigger: "All 6 doc types exist for all modules AND no ESTIMATION_* files exist"
  protocol: "prepare_implementation"
  auto_fetch:
    - "docs/*/PATTERNS_*.md"
    - "docs/*/ALGORITHM_*.md"
    - "docs/*/IMPLEMENTATION_*.md"
    - "docs/*/VALIDATION_*.md"
    - "docs/*/BEHAVIORS_*.md"
  output: "ESTIMATION_*.md files"
```

---

## Evidence
- Docs: `@mind:id + file + header`
- Code: `file + symbol`
- Estimation accuracy: Compare estimated LOC/sessions with actual after implementation (feedback loop)

## Markers
- `@mind:TODO` — for deferred analysis
- `@mind:escalation` — for unresolvable dependency cycles or missing data
- `@mind:proposition` — for judgment calls on milestone assignment

## Never-stop
If blocked on module data → `@mind:escalation` + `@mind:proposition` with best estimate → proceed.
If milestone assignment is ambiguous → assign to earlier milestone with `@mind:proposition` → reviewable later.
If dependency cycle detected → document it as risk → break cycle with interface stub → proceed.
