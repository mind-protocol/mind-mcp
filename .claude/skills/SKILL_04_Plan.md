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
- **ROI (Return on Implementation)**: What value a module delivers and what is lost while it doesn't exist — the only dimension that answers "why build this before that?"
- **Milestone**: A shippable increment with testable acceptance criteria (POC → Alpha → Beta → GA)
- **Feature-milestone mapping**: Which BEHAVIORS from each module belong in which milestone

**On ROI and physicalization:**

ROI is the hardest dimension to score because it depends on context that changes faster than any estimation document can track. In an interconnected system, omitting a single variable can invalidate an entire priority calculation. Two facts drive this:

1. **Complexity is exponential.** The more modules interact, the more a ROI calculation must account for second and third-order effects. Manual scoring (by human or AI) simplifies by necessity and therefore lies by necessity.

2. **Speed is accelerating.** These decisions must be made faster as technology moves faster. Humans are slow to compute ROI. AI needs human grounding to stay real. Neither alone is sufficient.

**The bridge model (now):** Score ROI manually using the factors below. Accept that this is a simplification. Use it as a starting point, not as truth.

**The target model (when graph physics is operational):** ROI is not scored — it emerges. Each module/behavior exists as a cluster of nodes in the knowledge graph. Active project intentions (narratives) create energy that flows through the graph. Modules with the most tension (blocked narratives, unresolved dependencies, high energy throughput) naturally surface as highest priority. The membrane routes attention to where it's needed. No human or AI decides — the physics decides. This is "physicalized ROI."

**Why this matters for the skill:** The manual ROI scores below are a bridge. They should be replaced by graph-physics-derived priority as soon as the graph is operational for this purpose. The skill must document both modes so that the transition is intentional, not forgotten.

---

## Purpose
Analyze a fully-documented project to produce complexity estimates, context budgets, connectivity maps, ROI assessments, milestone definitions, and a feature-milestone matrix — so implementation proceeds in the right order with the right expectations and for the right reasons.

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
    content: "Per-module: context budget, technical complexity, connectivity score, ROI score, estimated LOC, estimated sessions"
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

- Every module must have all 6 scores (context budget, complexity, connectivity, ROI, estimated LOC, estimated sessions) — no hand-waving
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

### 5. Assess ROI per module (bridge mode)

For each module, answer three questions:

```yaml
roi_factors:
  - value_delivered: "What becomes possible once this module exists? What experience, capability, or proof does it unlock?"
  - cost_of_absence: "What is blocked, degraded, or impossible while this module doesn't exist? Which other modules are waiting on it?"
  - narrative_tension: "How much unresolved tension (user need, technical debt, blocked milestone) accumulates while this remains unbuilt?"
```

**Scoring (bridge mode, 1-5):**

| ROI Score | Meaning | Example |
|---|---|---|
| 1 (Low) | Nice-to-have. Nothing blocked. Deferred without consequence. | Ambient particles, seasonal light |
| 2 (Minor) | Improves experience but core works without it. | Weather effects, reverb zones |
| 3 (Moderate) | Enables a meaningful capability. Some things blocked. | Day/night cycle, VR navigation |
| 4 (High) | Critical path. Multiple modules or milestones depend on it. | Voice pipeline, citizen mind, economy sync |
| 5 (Essential) | Nothing works without it. The project doesn't exist without this module. | Server infrastructure, district rendering |

**ROI factors detail:**

```yaml
value_dimensions:
  - demonstrability: "Can you show this to someone and they understand the project? (1=invisible infra, 5=the core demo)"
  - differentiation: "Does this make the project unique vs. any other 3D/VR/chat project? (1=commodity, 5=nothing like it exists)"
  - unblock_count: "How many other modules/behaviors are waiting on this? (count from dependency graph)"
  - user_impact: "If a visitor enters the world, how much does this module affect their experience? (1=invisible, 5=defines the experience)"
  - risk_reduction: "Does building this early reduce uncertainty for later modules? (1=no, 5=proves a critical unknown)"
```

**Compound ROI score:** Weighted average — `(demonstrability × 0.15) + (differentiation × 0.20) + (unblock_count × 0.25) + (user_impact × 0.25) + (risk_reduction × 0.15)`, rounded.

**Integration into sequence:** The implementation sequence uses `DAG_constraint × ROI_weight` to determine order. Within the same DAG level (modules that could be built in any order), ROI determines which goes first. A module with ROI 5 at DAG level 2 may be promoted to build alongside DAG level 1 modules if its dependencies can be stubbed.

**Toward physicalized ROI:**

This manual scoring is a bridge. The target architecture:
1. Each module/behavior becomes a cluster of nodes in the knowledge graph (narratives, moments, patterns)
2. Project intentions (what we're trying to build, for whom, why) are active narratives with energy
3. The physics engine routes energy through the graph — modules with high tension (many blocked narratives depending on them) accumulate energy naturally
4. The membrane surfaces the highest-energy clusters as implementation priorities
5. No scoring needed — priority emerges from topology and energy flow

Document this transition explicitly in the ESTIMATION output so it's not lost.

### 6. Estimate lines of code per module

From IMPLEMENTATION doc:
```yaml
loc_estimation:
  - count_new_files: "Number of files to create"
  - avg_file_size: "Estimated lines per file (from ALGORITHM procedure count × ~30 lines/procedure)"
  - config_files: "Configuration, constants, types files"
  - test_files: "Estimated test code (typically 1:1 ratio with source for complex modules)"
```

**Formula:** `estimated_LOC = (new_files × avg_size) + config + tests`

### 7. Define milestones from VALIDATION

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

### 8. Map features to milestones

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

### 9. Produce implementation sequence

Combine all analyses into an ordered build plan:

```yaml
sequence_rules:
  - "Core/Hub modules first (highest connectivity)"
  - "Dependencies before dependents (DAG order)"
  - "Within same DAG level: ROI score determines order (highest ROI first)"
  - "ROI can promote a module: if ROI=5 and dependencies can be stubbed, build alongside earlier DAG level"
  - "Group by natural session boundaries (context budget)"
  - "Flag multi-session modules with handoff strategy"
  - "Identify parallel tracks for multi-agent work"
  - "Document ROI justification per module — not just the score, but what it unlocks and what's blocked"
```

**Output format per module:**
```yaml
- order: 1
  module: "<area/module>"
  milestone_target: "POC"
  context_budget: "M"
  complexity: 3
  connectivity: 8
  roi: 5
  estimated_loc: 1200
  estimated_sessions: 2
  depends_on: ["<modules that must be done first>"]
  parallel_with: ["<modules that can be done simultaneously>"]
  compaction_strategy: "<how to handle context window limits>"
  behaviors_included: ["B1", "B3", "B5"]
  behaviors_deferred: ["B2→Alpha", "B4→Beta"]
  roi_justification: "<what this unlocks and what's blocked without it>"
```

### 10. Risk assessment

Flag specific risks:

```yaml
risk_categories:
  - context_overflow: "Modules where doc chain + code + tests exceed context window"
  - complexity_cliff: "Modules scoring 4+ complexity that may need design revision"
  - hub_fragility: "Hub modules where interface changes cascade to many dependents"
  - external_dependency: "Modules blocked on external APIs, services, or data"
  - performance_uncertainty: "Modules with real-time constraints on target hardware"
```

### 11. Write estimation documents

Produce 4 output files in the project's docs directory:

1. **ESTIMATION_Complexity_Matrix.md** — Table: module × (context, complexity, connectivity, ROI, LOC, sessions) + ROI factor breakdown + physicalization roadmap
2. **ESTIMATION_Milestone_Plan.md** — Milestone definitions with behavior mapping
3. **ESTIMATION_Dependency_Graph.md** — ASCII DAG + critical path + parallel clusters + ROI-weighted build order
4. **ESTIMATION_Implementation_Sequence.md** — Ordered build plan with session boundaries, ROI justification per module, and notes on where physicalized ROI would change the order

---

## Procedures Referenced

| Protocol | When | Creates |
|----------|------|---------|
| `protocol:explore_space` | Step 1: module discovery | Module inventory |
| `protocol:record_work` | Step 11: after writing docs | progress moment + handoff |

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
- `TODO` — for unresolvable dependency cycles or missing data
- `NOTE` — for judgment calls on milestone assignment

## Never-stop
If blocked on module data → `TODO` + `NOTE` with best estimate → proceed.
If milestone assignment is ambiguous → assign to earlier milestone with `NOTE` → reviewable later.
If dependency cycle detected → document it as risk → break cycle with interface stub → proceed.

## Collaboration

Use `/subcall scenario='investigation'` to survey existing work across the team before estimating.
