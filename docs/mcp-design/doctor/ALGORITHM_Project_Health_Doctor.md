# ALGORITHM: Project Health Doctor

**Step-by-step procedures for graph-based health checks.**

---

## OVERVIEW

Doctor is a graph-native issue detection and task creation system:

1. **Surface Issues** — Static analysis, tests, health checks create Narrative nodes (type: issue)
2. **Traverse Up** — From issues to objectives via graph links
3. **Create Tasks** — Group issues into Narrative nodes (type: task) based on outcome

All entities follow schema v1.2:
- Issues, Objectives, Tasks are **Narrative** nodes with different `type` attributes
- Modules are **Space** nodes
- Files are **Thing** nodes
- Links use **relates** with `direction` property for semantic meaning

---

## ID CONVENTION

All node and link IDs follow a consistent naming pattern optimized for agent scanning:

```
{node-type}_{SUBTYPE}_{instance-context}_{disambiguator}
```

| Component | Case | Purpose | Example |
|-----------|------|---------|---------|
| `node-type` | lowercase | Schema type (low info, already known) | `narrative`, `space`, `thing` |
| `SUBTYPE` | ALLCAPS | What you scan for (high info) | `ISSUE`, `OBJECTIVE`, `TASK`, `MODULE`, `FILE` |
| `instance-context` | lowercase, `-` between words | Which one (descriptive context) | `monolith-engine-physics-graph-ops` |
| `disambiguator` | lowercase | Collision safety (2-char hash or index) | `a7`, `01` |

### Node ID Examples

```yaml
# Issues
narrative_ISSUE_monolith-engine-physics-graph-ops_a7
narrative_ISSUE_stale-sync-mind-cli-doctor_f2

# Objectives
narrative_OBJECTIVE_engine-physics-documented
narrative_OBJECTIVE_mind-cli-tested

# Tasks
narrative_TASK_serve-engine-physics-documented_01
narrative_TASK_reconstruct-orphan-utils_01
narrative_TASK_triage-legacy-code_01

# Spaces (modules)
space_MODULE_engine-physics
space_MODULE_mind-cli

# Things (files)
thing_FILE_engine-physics-graph-ops_a7
thing_FILE_doctor-checks_f2
```

### Link ID Examples

```yaml
# Semantic links (with role name)
relates_BLOCKS_narrative-issue-a7_TO_narrative-objective-b3
relates_SERVES_narrative-task-01_TO_narrative-objective-b3
relates_INCLUDES_narrative-task-01_TO_narrative-issue-a7
relates_ABOUT_narrative-issue-a7_TO_thing-file-b3

# Structural links
contains_space-module-engine-physics_TO_narrative-issue-a7
```

### Rationale

- **SUBTYPE in ALLCAPS**: When scanning a list of IDs, the subtype is what differentiates entries. ALLCAPS makes it jump out.
- **Lowercase node-type**: You already know you're looking at a node. Low information value.
- **Dashes within sections**: Words like `engine-physics` stay together visually.
- **Underscores between sections**: `_` clearly separates the structural parts.
- **Short hash**: 2 characters provide 256 collision buckets — sufficient for most modules.

---

## MAIN FLOW

```
┌────────────────────────────────────────────────────────────────┐
│ 1. FETCH OBJECTIVES                                            │
│    Query graph for existing Narrative nodes (type: objective)  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ 2. SURFACE ISSUES                                              │
│    Static analysis + Tests + Health checks                     │
│    Create Narrative nodes (type: issue) with links             │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ 3. TRAVERSE UP                                                 │
│    From each issue → Space → Objective                         │
│    Determine outcome: SERVE | RECONSTRUCT | TRIAGE             │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ 4. CREATE TASKS                                                │
│    Group issues by outcome and objective                       │
│    Create Narrative nodes (type: task)                         │
│    Link tasks to issues and objectives                         │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│ 5. OUTPUT                                                      │
│    Return tasks with linked issues, objectives, skills         │
└────────────────────────────────────────────────────────────────┘
```

---

## 1. FETCH OBJECTIVES

Objectives are Narrative nodes (type: objective) that already exist in the graph.
Doctor reads them, doesn't create them.

```python
def fetch_objectives(store: DoctorGraphStore) -> List[ObjectiveNarrative]:
    """Query existing objectives from graph."""
    return store.query_nodes(
        node_type="narrative",
        subtype="objective"
    )
```

### Objective Schema

```yaml
node:
  id: "narrative_OBJECTIVE_{module}-{type}"
  # Example: narrative_OBJECTIVE_engine-physics-documented
  node_type: narrative
  type: objective
  name: "Module {module} is {type}"
  content: "All {type}-related issues resolved"
  weight: 1.0
  energy: 0.0

  # Objective-specific fields
  objective_type: documented | synced | maintainable | tested | healthy | secure | resolved
  module: "{module_id}"
  status: open | achieved | deferred | deprecated
```

### Standard Objective Types

| Type | Meaning | Blocking Issues |
|------|---------|-----------------|
| `documented` | Complete doc chain | UNDOCUMENTED, INCOMPLETE_CHAIN, PLACEHOLDER, NO_DOCS_REF |
| `synced` | Docs reflect current state | STALE_SYNC, STALE_IMPL, CODE_DOC_DELTA_COUPLING |
| `maintainable` | Code is clean | MONOLITH, NAMING_CONVENTION, MAGIC_VALUES, STUB_IMPL |
| `tested` | Has test coverage | MISSING_TESTS, TEST_FAILED, INVARIANT_UNTESTED |
| `healthy` | Health signals pass | HEALTH_FAILED, INVARIANT_VIOLATED, LOG_ERROR |
| `secure` | No vulnerabilities | HARDCODED_SECRET |
| `resolved` | No open conflicts | ESCALATION, SUGGESTION, UNRESOLVED_QUESTION |

---

## 2. SURFACE ISSUES

Issues come from three sources:

### 2.1 Static Analysis

Scan codebase for structural problems:

```python
def run_static_checks(target_dir: Path, config: DoctorConfig) -> List[DoctorIssue]:
    issues = []
    issues.extend(check_monolith(target_dir, config))
    issues.extend(check_undocumented(target_dir, config))
    issues.extend(check_stale_sync(target_dir, config))
    issues.extend(check_naming_convention(target_dir, config))
    # ... etc
    return issues
```

### 2.2 Test Runner

Execute tests and surface failures:

```python
def run_tests(target_dir: Path) -> List[TestResult]:
    """Run pytest/jest and parse results."""
    # Each failure becomes an issue
    # TEST_FAILED, TEST_ERROR, TEST_TIMEOUT
```

### 2.3 Health Checks

Execute health signals from HEALTH_*.md:

```python
def run_health_checks(target_dir: Path, modules: Dict) -> List[HealthResult]:
    """Run health checks defined in HEALTH docs."""
    # Each failure becomes an issue
    # HEALTH_FAILED, INVARIANT_VIOLATED
```

### Issue Schema

```yaml
node:
  id: "narrative_ISSUE_{issue-type}-{module}-{file}_{hash}"
  # Example: narrative_ISSUE_monolith-engine-physics-graph-ops_a7
  node_type: narrative
  type: issue
  name: "{ISSUE_TYPE} in {module}/{file}"
  content: |
    ## {ISSUE_TYPE}

    **Module:** {module}
    **File:** {path}
    **Severity:** {severity}

    ### Description
    {message}
  weight: 1.0
  energy: 1.0 | 0.5 | 0.2  # critical | warning | info

  # Issue-specific fields
  issue_type: "MONOLITH"
  severity: critical | warning | info
  status: open | resolved | in_progress
  module: "{module_id}"
  path: "{file_path}"
  message: "{human description}"
  detected_at: "{ISO timestamp}"
```

### Issue Creation with Links

When an issue is created, these links are also created:

```yaml
links:
  # Space contains Issue
  - id: "contains_space-module-engine-physics_TO_narrative-issue-a7"
    node_a: "space_MODULE_engine-physics"
    node_b: "narrative_ISSUE_monolith-engine-physics-graph-ops_a7"
    nature: "contains"

  # Issue relates to Thing (file)
  - id: "relates_ABOUT_narrative-issue-a7_TO_thing-file-b3"
    node_a: "narrative_ISSUE_monolith-engine-physics-graph-ops_a7"
    node_b: "thing_FILE_engine-physics-graph-ops_a7"
    nature: "relates to"
    name: "about"
```

### Upsert Logic

```python
def upsert_issue(issue_type, severity, path, message, module, store):
    """Create or update issue node."""
    issue_id = generate_issue_id(issue_type, module, path)
    existing = store.get_node(issue_id)

    if existing:
        # Update: severity, message, detected_at, status=open
        existing.severity = severity
        existing.message = message
        existing.detected_at = now()
        existing.status = "open"
        store.upsert_node(existing)
    else:
        # Create new with links
        issue = create_issue_node(...)
        store.upsert_node(issue)
        store.create_link(space_contains_issue)
        store.create_link(issue_about_thing)

    return issue
```

---

## 3. TRAVERSE UP

For each issue, traverse up to find which objective it blocks.

### Traversal Logic

```python
def traverse_to_objective(issue: IssueNarrative, store, modules) -> TraversalResult:
    """
    Traverse: Issue → Space → Objective

    Returns:
        - SERVE: Found objective
        - RECONSTRUCT: Missing nodes in chain
        - TRIAGE: No objective defined
    """
    missing_nodes = []

    # Step 1: Find Space
    # ID: space_MODULE_{module}
    space_id = generate_space_id(issue.module)  # → space_MODULE_engine-physics
    space = store.get_node(space_id)
    if not space:
        missing_nodes.append(f"Space:{issue.module}")

    # Step 2: Check doc chain exists
    module_info = modules.get(issue.module, {})
    if module_info.get("docs"):
        for doc_type in ["patterns", "sync"]:
            doc_id = f"narrative_{doc_type}_{issue.module}"
            if not store.get_node(doc_id):
                missing_nodes.append(f"{doc_type.upper()}:{issue.module}")

    # Step 3: Find objective
    # ID: narrative_OBJECTIVE_{module}-{type}
    objective_types = ISSUE_BLOCKS_OBJECTIVE[issue.issue_type]
    objective = None
    for obj_type in objective_types:
        obj_id = generate_objective_id(obj_type, issue.module)
        # → narrative_OBJECTIVE_engine-physics-documented
        obj_node = store.get_node(obj_id)
        if obj_node:
            objective = obj_node
            break

    # Determine outcome
    if missing_nodes:
        return TraversalResult(outcome=RECONSTRUCT, missing_nodes=missing_nodes)
    elif objective:
        return TraversalResult(outcome=SERVE, objective=objective)
    else:
        return TraversalResult(outcome=TRIAGE)
```

### Traversal Outcomes

| Outcome | Condition | Task Type | Skill |
|---------|-----------|-----------|-------|
| `SERVE` | Objective found | Normal task | (by objective type) |
| `RECONSTRUCT` | Missing nodes in chain | Rebuild chain | `create_module_documentation` |
| `TRIAGE` | No objective exists | Evaluate usefulness | `triage_unmapped_code` |

---

## 4. CREATE TASKS

Group issues by outcome and create Task narrative nodes.

### Task Schema

```yaml
node:
  id: "narrative_TASK_{task-type}-{module}-{objective}_{index}"
  # Example: narrative_TASK_serve-engine-physics-documented_01
  node_type: narrative
  type: task
  name: "Serve {objective} for {module}" | "Reconstruct chain for {module}" | "Triage: {module}"
  content: |
    ## Task: Serve documented for engine-physics

    **Type:** serve
    **Module:** engine-physics
    **Objective:** narrative_OBJECTIVE_engine-physics-documented
    **Skill:** create_module_documentation

    ### Issues (3)
    - [ ] `narrative_ISSUE_undocumented-engine-physics-root_a7`
    - [ ] `narrative_ISSUE_incomplete-chain-engine-physics-patterns_b2`
    - [ ] `narrative_ISSUE_no-docs-ref-engine-physics-runner_c3`
  weight: 1.0
  energy: 0.0

  # Task-specific fields
  task_type: serve | reconstruct | triage
  objective_id: "narrative_OBJECTIVE_{...}" | null
  module: "{module_id}"
  skill: "{skill_name}"
  status: open | in_progress | completed
  issue_ids: ["narrative_ISSUE_{...}", ...]
  missing_nodes: ["Space:...", "PATTERNS:..."]  # for reconstruct
```

### Task Links

```yaml
links:
  # Task serves Objective (direction: support)
  - id: "relates_SERVES_narrative-task-01_TO_narrative-objective-b3"
    node_a: "narrative_TASK_serve-engine-physics-documented_01"
    node_b: "narrative_OBJECTIVE_engine-physics-documented"
    nature: "relates to"
    name: "serves"
    direction: support

  # Task includes Issue (direction: subsume)
  - id: "relates_INCLUDES_narrative-task-01_TO_narrative-issue-a7"
    node_a: "narrative_TASK_serve-engine-physics-documented_01"
    node_b: "narrative_ISSUE_monolith-engine-physics-graph-ops_a7"
    nature: "relates to"
    name: "includes"
    direction: subsume

  # Issue blocks Objective (direction: oppose)
  - id: "relates_BLOCKS_narrative-issue-a7_TO_narrative-objective-b3"
    node_a: "narrative_ISSUE_monolith-engine-physics-graph-ops_a7"
    node_b: "narrative_OBJECTIVE_engine-physics-documented"
    nature: "relates to"
    name: "blocks"
    direction: oppose
```

### Task Creation Logic

```python
MAX_ISSUES_PER_TASK = 5

def create_tasks_from_issues(issues, store, modules):
    tasks = []

    # Group by outcome
    grouped = group_issues_by_outcome(issues, store, modules)

    # SERVE tasks: group by objective, split if > MAX
    for module, issue_results in grouped[SERVE].items():
        by_objective = group_by_objective(issue_results)
        for obj_id, obj_issues in by_objective.items():
            chunks = split_chunks(obj_issues, MAX_ISSUES_PER_TASK)
            for idx, chunk in enumerate(chunks, 1):
                task = create_task_node(
                    task_type="serve",
                    module=module,
                    skill=OBJECTIVE_TO_SKILL[objective.objective_type],
                    issue_ids=[i.id for i in chunk],
                    objective_id=obj_id,
                    index=idx
                )
                store.upsert_node(task)
                # Create links
                store.create_link(task_serves_objective(task.id, obj_id))
                for issue in chunk:
                    store.create_link(task_includes_issue(task.id, issue.id))
                    store.create_link(issue_blocks_objective(issue.id, obj_id))
                tasks.append(task)

    # RECONSTRUCT tasks: one per module with gaps
    for module, issue_results in grouped[RECONSTRUCT].items():
        missing = collect_missing_nodes(issue_results)
        task = create_task_node(
            task_type="reconstruct",
            module=module,
            skill="create_module_documentation",
            issue_ids=[i.id for i, _ in issue_results],
            missing_nodes=list(missing)
        )
        store.upsert_node(task)
        tasks.append(task)

    # TRIAGE tasks: one per orphan module
    for module, issue_results in grouped[TRIAGE].items():
        task = create_task_node(
            task_type="triage",
            module=module,
            skill="triage_unmapped_code",
            issue_ids=[i.id for i, _ in issue_results]
        )
        store.upsert_node(task)
        tasks.append(task)

    return tasks
```

---

## 5. OUTPUT

### Task Surface Result

```yaml
summary:
  issues_surfaced: 45
  issues_from_checks: 40
  issues_from_tests: 3
  issues_from_health: 2
  tasks_created: 12
  tasks_serve: 8
  tasks_reconstruct: 2
  tasks_triage: 2

tasks:
  - id: "narrative_TASK_serve-engine-physics-documented_01"
    type: serve
    module: engine-physics
    skill: create_module_documentation
    objective: "narrative_OBJECTIVE_engine-physics-documented"
    issues:
      - "narrative_ISSUE_undocumented-engine-physics-root_a7"
      - "narrative_ISSUE_incomplete-chain-engine-physics-patterns_b2"

  - id: "narrative_TASK_reconstruct-orphan-utils_01"
    type: reconstruct
    module: orphan-utils
    skill: create_module_documentation
    missing:
      - "Space:orphan-utils"
      - "PATTERNS:orphan-utils"
    issues:
      - "narrative_ISSUE_no-docs-ref-orphan-utils-helpers_c3"
```

---

## OBJECTIVE → SKILL MAPPING

| Objective Type | Skill |
|----------------|-------|
| `documented` | `create_module_documentation` |
| `synced` | `update_module_sync_state` |
| `maintainable` | `implement_write_or_modify_code` |
| `tested` | `test_integrate_and_gate` |
| `healthy` | `health_define_and_verify` |
| `resolved` | `review_evaluate_changes` |
| `secure` | `implement_write_or_modify_code` |

---

## ISSUE TYPE → OBJECTIVE MAPPING

### Documentation Issues → `documented`
UNDOCUMENTED, INCOMPLETE_CHAIN, PLACEHOLDER, DOC_TEMPLATE_DRIFT, NO_DOCS_REF, BROKEN_IMPL_LINK, ORPHAN_DOCS, NON_STANDARD_DOC_TYPE, DOC_DUPLICATION, DOC_LINK_INTEGRITY

### Sync Issues → `synced`
STALE_SYNC, STALE_IMPL, CODE_DOC_DELTA_COUPLING, DOC_GAPS

### Code Quality Issues → `maintainable`
MONOLITH, STUB_IMPL, INCOMPLETE_IMPL, NAMING_CONVENTION, MAGIC_VALUES, HARDCODED_CONFIG, LONG_PROMPT, LONG_SQL, LEGACY_MARKER

### Test Issues → `tested`
MISSING_TESTS, TEST_FAILED, TEST_ERROR, TEST_TIMEOUT, INVARIANT_UNTESTED, TEST_NO_VALIDATES

### Health Issues → `healthy`
HEALTH_FAILED, INVARIANT_VIOLATED, INVARIANT_NO_TEST, VALIDATION_BEHAVIORS_MISSING, CONFIG_MISSING, LOG_ERROR, MEMBRANE_*

### Review Issues → `resolved`
ESCALATION, SUGGESTION, UNRESOLVED_QUESTION

### Security Issues → `secure`
HARDCODED_SECRET

---

## CLI INTEGRATION

```bash
# Basic doctor (static only)
mind doctor

# With tests
mind doctor --tests

# With health checks
mind doctor --health

# Full (static + tests + health)
mind doctor --full

# Output formats
mind doctor --format yaml
mind doctor --format json

# Show tasks only
mind doctor --tasks
```

---

## AUTO-RESOLVE

When a previously failing test/health check passes, the issue is resolved:

```python
def auto_resolve(issue_id: str, store: DoctorGraphStore):
    """Mark issue as resolved when underlying problem is fixed."""
    issue = store.get_node(issue_id)
    if issue and issue.status == "open":
        issue.status = "resolved"
        issue.resolved_at = now()
        issue.energy = 0.0  # No longer active
        store.upsert_node(issue)
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Project_Health_Doctor.md
BEHAVIORS:       ./BEHAVIORS_Project_Health_Doctor.md
ALGORITHM:       THIS
VALIDATION:      ./VALIDATION_Project_Health_Doctor.md
HEALTH:          ./HEALTH_Project_Health_Doctor.md
SYNC:            ./SYNC_Project_Health_Doctor.md
```
