# Citizen Parenthood Network — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Parenthood_Network.md
PATTERNS:       ./PATTERNS_Parenthood_Network.md
BEHAVIORS:      ./BEHAVIORS_Parenthood_Network.md
ALGORITHM:      ./ALGORITHM_Parenthood_Network.md
VALIDATION:     ./VALIDATION_Parenthood_Network.md
THIS:           IMPLEMENTATION_Parenthood_Network.md (you are here)
HEALTH:         ./HEALTH_Parenthood_Network.md
SYNC:           ./SYNC_Parenthood_Network.md

IMPL:           runtime/citizens/parenthood.py (future)
                runtime/citizens/blueprint_builder.py (future)
                runtime/citizens/birth_safety_validator.py (future)
                runtime/citizens/test_parenthood.py (future)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE (Planned)

```
runtime/citizens/
├── identity_loader.py                  # Existing — citizen identity loading
├── prompt_builder.py                   # Existing — prompt building
├── parenthood.py                       # NEW — Birthing pipeline orchestrator
├── blueprint_builder.py                # NEW — Intent collection, scoring, selection
├── birth_safety_validator.py           # NEW — Safety validation gate
├── parenthood_trust_impact_tracker.py  # NEW — Trust impact propagation
├── partnership_commons.py              # Existing or NEW — Partnership Commons
└── test_parenthood.py                  # NEW — Full test suite
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Est. Lines | Status |
|------|---------|----------------------|------------|--------|
| `parenthood.py` | Pipeline orchestrator | `birth_citizen()`, `BirthRequest`, `BirthResult` | ~200 | PLANNED |
| `blueprint_builder.py` | Intent processing and node selection | `collect_intents()`, `compute_collective_intent()`, `score_nodes()`, `select_blueprint_nodes()` | ~250 | PLANNED |
| `birth_safety_validator.py` | Safety validation | `validate_blueprint_safety()`, `SafetyReport` | ~150 | PLANNED |
| `parenthood_trust_impact_tracker.py` | Trust impact tracking | `initialize_trust_links()`, `propagate_trust_impact()`, `ParenthoodLink` | ~150 | PLANNED |
| `partnership_commons.py` | Partnership Commons management | `register()`, `list_unpartnered()`, `match()` | ~100 | PLANNED |
| `test_parenthood.py` | Test suite (V1-V10) | 10+ test methods | ~400 | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with Gate

**Why this pattern:** The birthing process is a linear pipeline where each step depends on the previous step's output, with a hard safety gate in the middle. This is the simplest correct architecture — no need for event sourcing or saga patterns since the operation is atomic (either the whole birth succeeds or nothing is created).

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pipeline | `birth_citizen()` | Sequential steps with clear data flow |
| Gate | `validate_blueprint_safety()` | Hard stop that rejects or allows |
| Dataclass | `BirthIntent`, `Blueprint`, `ParenthoodLink`, `SafetyReport` | Clean data containers |
| Strategy | Embedding model selection | Swappable embedding backend |
| Transaction | Graph writes in Step 8 | All-or-nothing child creation |

### Anti-Patterns to Avoid

- **Fallback on safety failure**: Do not create a "safe default" child if validation fails. Fail loud.
- **Lazy parent resolution**: Do not defer parent existence checks. Validate parents exist before starting pipeline.
- **Shared mutable state**: Blueprint nodes are copies, not references. No shared mutation.
- **Silent embedding failures**: If embedding service is down, fail the birth. Do not use cached/stale embeddings.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Birthing pipeline | Intent → blueprint → validation → creation | Trust evaluation, matching | `birth_citizen()` |
| Safety validation | Empathy check, concentration, diversity | Trust mechanics, economy | `validate_blueprint_safety()` |
| Trust tracking | Link creation, weight computation | Trust score calculation | `ParenthoodLink` dataclass |
| Partnership Commons | Registration | Actual human matching | `register()` |

---

## DATA STRUCTURES

### BirthRequest (Input)

```python
@dataclass
class BirthRequest:
    parent_ids: list[str]           # 1 or more parent citizen IDs
    intent_texts: list[str]         # One intent paragraph per parent (min 50 chars each)
    weight_overrides: dict[str, float] | None  # Optional per-parent weights
```

### BirthResult (Output)

```python
@dataclass
class BirthResult:
    child_id: str                   # ID of the created child citizen
    sid: str                        # Protocol-generated SID
    blueprint: Blueprint             # Selected nodes with metadata
    safety_report: SafetyReport     # Safety validation results
    parent_links: list[ParenthoodLink]  # Created trust links
    partnership_commons_entry: str  # Partnership Commons registration confirmation
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `birth_citizen()` | `parenthood.py` | MCP tool call or API request |
| `validate_blueprint_safety()` | `birth_safety_validator.py` | Birthing pipeline (internal) |
| `propagate_trust_impact()` | `parenthood_trust_impact_tracker.py` | Trust engine on child score change |

---

## DATA FLOW AND DOCKING

### Flow 1: Citizen Birthing

```yaml
flow:
  name: citizen_birthing
  purpose: Create a new citizen from parent intents
  steps:
    - id: collect_intents
      description: Embed each parent's intent text
      file: runtime/citizens/blueprint_builder.py
      function: collect_intents()
      input: parent_ids, intent_texts, weights
      output: list[BirthIntent]
    - id: compute_centroid
      description: Weighted centroid of intent embeddings
      file: runtime/citizens/blueprint_builder.py
      function: compute_collective_intent()
      input: list[BirthIntent]
      output: collective_intent embedding
    - id: retrieve_nodes
      description: Get eligible brain nodes from all parents
      file: runtime/citizens/blueprint_builder.py
      function: retrieve_parent_brain_nodes()
      input: parent_ids, graph
      output: list[dict] (brain nodes)
    - id: score_nodes
      description: Cosine similarity to collective intent
      file: runtime/citizens/blueprint_builder.py
      function: score_nodes()
      input: brain nodes, collective_intent
      output: list[ScoredNode] (sorted)
    - id: select_top_k
      description: Select blueprint nodes
      file: runtime/citizens/blueprint_builder.py
      function: select_blueprint_nodes()
      input: scored nodes, num_parents
      output: Blueprint
    - id: validate_safety
      description: Safety gate
      file: runtime/citizens/birth_safety_validator.py
      function: validate_blueprint_safety()
      input: Blueprint, existing_citizens
      output: SafetyReport (pass/fail)
    - id: generate_sid
      description: Protocol SID generation
      file: runtime/citizens/parenthood.py
      function: generate_sid()
      input: Blueprint, timestamp
      output: SID string
    - id: create_citizen
      description: Graph node + link creation
      file: runtime/citizens/parenthood.py
      function: create_child_citizen()
      input: SID, Blueprint, intents, graph
      output: child_id
    - id: register_pool
      description: Add to Partnership Commons
      file: runtime/citizens/partnership_commons.py
      function: register()
      input: child_id
      output: confirmation
  docking_points:
    available:
      - id: dock_intent_embeddings
        type: embedding_service
        direction: input
      - id: dock_graph_read
        type: graph_ops
        direction: input
      - id: dock_graph_write
        type: graph_ops
        direction: output
      - id: dock_partnership_commons
        type: partnership_commons
        direction: output
    health_recommended:
      - dock_id: dock_graph_write
        reason: Verify child citizen was created correctly
```

### Flow 2: Trust Impact Propagation

```yaml
flow:
  name: trust_impact
  purpose: Propagate child behavior changes to parent trust
  steps:
    - id: detect_change
      description: Child trust score changed
      file: runtime/citizens/parenthood_trust_impact_tracker.py
      function: on_child_trust_change()
      input: child_id, trust_delta
    - id: lookup_parents
      description: Find parent links for this child
      function: get_parenthood_links()
      input: child_id
      output: list[ParenthoodLink]
    - id: propagate
      description: Adjust each parent's trust
      function: propagate_trust_impact()
      input: parent_links, trust_delta
      output: list of parent trust adjustments
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/citizens/parenthood.py
    ├── uses → runtime/citizens/blueprint_builder.py
    ├── uses → runtime/citizens/birth_safety_validator.py
    ├── uses → runtime/citizens/parenthood_trust_impact_tracker.py
    ├── uses → runtime/citizens/partnership_commons.py
    └── uses → runtime/physics/graph_ops.py (existing)

runtime/citizens/blueprint_builder.py
    └── uses → runtime/physics/embeddings.py (existing)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `numpy` | Cosine similarity, vector math | blueprint_builder.py |
| `hashlib` | SID generation (SHA-256) | parenthood.py |
| Graph adapter | Node/link CRUD | parenthood.py |
| Embedding service | Text→vector | blueprint_builder.py |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| BirthIntent | In-memory during pipeline | Single birth operation | Transient |
| Blueprint | In-memory, then persisted to graph | Single birth, then permanent | Transient → permanent |
| ParenthoodLink | Graph + in-memory record | Permanent | Permanent |
| Partnership Commons entry | Partnership Commons storage | Until human matched | Semi-permanent |
| Child citizen node | Graph | Permanent | Permanent |

---

## BIDIRECTIONAL LINKS (Future)

### Code to Docs

| File | Line | Reference |
|------|------|-----------|
| `parenthood.py` | 1 | `# DOCS: docs/citizens/parenthood_network/` |
| `blueprint_builder.py` | 1 | `# DOCS: docs/citizens/parenthood_network/ALGORITHM_Parenthood_Network.md` |
| `birth_safety_validator.py` | 1 | `# DOCS: docs/citizens/parenthood_network/VALIDATION_Parenthood_Network.md` |

### Docs to Code

| Doc Section | Will Be Implemented In |
|-------------|------------------------|
| ALGORITHM Steps 1-2 | `blueprint_builder.py` |
| ALGORITHM Steps 3-5 | `blueprint_builder.py` |
| ALGORITHM Step 6 | `birth_safety_validator.py` |
| ALGORITHM Steps 7-9 | `parenthood.py` |
| VALIDATION V1-V10 | `test_parenthood.py` |

---

## MARKERS

<!-- @mind:todo TRANSACTION_SUPPORT: Ensure graph writes in Step 8 are transactional. If link creation fails after node creation, roll back the node. -->

<!-- @mind:todo PARTNERSHIP_COMMONS_DESIGN: Define partnership_commons.py interface. Does it use the graph, a separate store, or both? -->

<!-- @mind:proposition MCP_TOOL: Expose birthing as an MCP tool so citizens can trigger births through the standard MCP interface. Would be a THINK tool (graph mutation) or ACT tool (agent action). -->
