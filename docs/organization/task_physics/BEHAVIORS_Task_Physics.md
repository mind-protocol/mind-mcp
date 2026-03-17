# Task Physics — Behaviors: Observable Effects of Thermodynamic Tasks

```
STATUS: CANONICAL
CREATED: 2026-03-15
LAYER: L2 (Organization)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Physics.md
PATTERNS:        ./PATTERNS_Task_Physics.md
THIS:            BEHAVIORS_Task_Physics.md (you are here)
ALGORITHM:       ./ALGORITHM_Task_Physics.md
VALIDATION:      ./VALIDATION_Task_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
SYNC:            ./SYNC_Task_Physics.md

IMPL:            runtime/organization/task_physics.py
```

---

## BEHAVIORS

### B1: Urgency Accumulation on Task Creation

**Why:** A task is not a static record. It is a gravity well that concentrates organizational attention. The more critical the objectives it serves and the more work it blocks, the more energy it accumulates.

```
GIVEN:  A new Task node is created in the graph
WHEN:   The task has CONTRIBUTES_TO links to objectives with high energy
THEN:   The task's energy increases proportionally to the connected objective pressure
AND:    The task's energy increases for each downstream task it BLOCKS

GIVEN:  A new Task node is created with no dependencies
WHEN:   It exists in isolation
THEN:   Its energy equals the intrinsic urgency (base_energy from creation params)
AND:    It still participates in normal physics (decay, propagation)
```

### B2: Cascade Unblocking on Completion

**Why:** The most powerful effect in the system. Completing a blocker releases dammed energy into all downstream tasks, which can trigger chain reactions across the dependency graph.

```
GIVEN:  Task X has BLOCKS links to Tasks Y and Z
AND:    Tasks Y and Z have low energy (dammed behind X)
WHEN:   Task X is marked completed
THEN:   All BLOCKS links from X are severed
AND:    Tasks Y and Z receive an energy surge: surge = X.energy_at_completion × cascade_factor
AND:    If Y or Z's new energy exceeds the activation threshold (Θ) of their assigned citizen,
        those citizens wake up and begin working

GIVEN:  Task Y (just unblocked) itself BLOCKS Tasks W and V
WHEN:   Citizen Y completes Task Y (triggered by cascade from X)
THEN:   Another cascade fires: W and V receive energy surge from Y
AND:    Cascade depth is bounded by MAX_CASCADE_DEPTH (default: 5)
```

### B3: Crystallization of Artifacts

**Why:** Completed work must leave permanent traces. The organization's knowledge graph grows through crystallized artifacts, not through task nodes that decay away.

```
GIVEN:  Task X is marked completed with a TRACE evaluation
WHEN:   The TRACE contains output artifacts (code, documents, decisions)
THEN:   For each artifact:
          - A new node is created (type: Code, Document, or Decision)
          - An IMPLEMENTS or RESOLVES link connects artifact → Task X
          - The artifact node has weight = 0.5 (stable, no rapid decay)
AND:    The artifact's synthesis field contains a description of what was produced

GIVEN:  Task X is completed but TRACE contains no artifacts
WHEN:   Crystallization phase runs
THEN:   No artifact nodes are created (empty completion is valid)
AND:    The task still undergoes energy collapse and cascade
```

### B4: Structural Learning from Outcomes

**Why:** The network must learn who is good at what. Every task completion is a training signal that adjusts the weights on collaboration and expertise links.

```
GIVEN:  Citizen C completed Task X successfully (TRACE evaluation positive)
WHEN:   The learning phase runs
THEN:   The MEMBER_OF link (C → X) weight increases by learning_rate × trace_score
AND:    If C has expertise links related to X's category, those links strengthen
AND:    If C collaborated with Citizen D on Task X, the trust link (C ↔ D) strengthens

GIVEN:  Citizen C failed Task X (TRACE evaluation negative or timeout)
WHEN:   The learning phase runs
THEN:   The MEMBER_OF link weight is NOT decreased (failure doesn't punish)
AND:    Task X's energy increases by 0.3 (becomes louder for reassignment)
AND:    C's load_penalty increases (fewer new tasks routed to C temporarily)
```

### B5: Rapid Decay of Completed Tasks

**Why:** Consciousness should focus on active work. Completed tasks must fade from working memory while their artifacts persist.

```
GIVEN:  Task X is marked completed
WHEN:   Physics tick runs
THEN:   Task X's energy decays with half-life = TASK_COMPLETED_HALF_LIFE (default: 2 hours)
AND:    After ~6 hours (3 half-lives), energy < 0.125 × original
AND:    After ~12 hours, energy approaches zero (pruning candidate)

GIVEN:  Task X is active (not completed)
WHEN:   Physics tick runs
THEN:   Task X's energy decays at the standard rate (DECAY_RATE = 0.02/tick)
BUT:    Dependency pressure from CONTRIBUTES_TO and BLOCKS links continuously replenishes energy
AND:    Net energy change can be positive if pressure exceeds decay
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Why It Matters |
|----------|-----------|----------------|
| B1 | O1 (energy manipulators) | Tasks concentrate organizational attention |
| B2 | O2 (dependency cascades) | Completions trigger chain reactions |
| B3 | O3 (crystallization) | Work produces permanent knowledge |
| B4 | O4 (weight learning) | Network develops accurate expertise model |
| B5 | O5 (rapid decay) | Consciousness focuses on the active, not the done |

---

## INPUTS / OUTPUTS

### Primary Event: Task Creation

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | str | Unique task node ID |
| synthesis | str | Task description (embeddable) |
| contributes_to | list[str] | Objective node IDs this task feeds |
| blocks | list[str] | Task node IDs this task blocks |
| requires | list[str] | Task node IDs this task depends on |
| base_energy | float | Initial urgency (default: 0.5) |

**Outputs:**

| Effect | Type | Description |
|--------|------|-------------|
| Task node | Node | Created in graph with energy = base_energy + dependency_pressure |
| CONTRIBUTES_TO links | Links | Task → Objective (pressure channel) |
| BLOCKS links | Links | Task → downstream Tasks (energy dam) |
| Citizen awakening | Side effect | If task energy exceeds citizen Θ |

### Primary Event: Task Completion

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | str | Completed task node ID |
| trace | dict | TRACE evaluation (score, artifacts, collaborators) |
| completed_by | str | Citizen handle who completed |

**Outputs:**

| Effect | Type | Description |
|--------|------|-------------|
| Energy collapse | Mutation | Task energy enters rapid decay (half-life 2h) |
| BLOCKS severed | Mutation | All outgoing BLOCKS links removed |
| Energy surge | Mutation | Downstream tasks receive energy burst |
| Artifact nodes | Nodes | Code/Document/Decision nodes created |
| Weight updates | Mutations | MEMBER_OF, expertise, trust link weights adjusted |
| `mission.completed` | Event | Broadcast via `graph.delta.node.upsert` |

---

## EDGE CASES

### E1: Circular Dependencies

```
GIVEN:  Task A BLOCKS Task B, Task B BLOCKS Task A
THEN:   Cycle is detected at link creation time
AND:    The second BLOCKS link is rejected with error
```

### E2: Cascade Exceeds MAX_CASCADE_DEPTH

```
GIVEN:  A chain of 10+ tasks, each blocking the next
WHEN:   The first task completes
THEN:   Cascade propagates up to MAX_CASCADE_DEPTH (default: 5)
AND:    Remaining tasks receive no cascade energy (they'll get it on the next tick via normal propagation)
```

### E3: Completed Task Still Has BLOCKS Links After Crash

```
GIVEN:  Server crashes between marking task complete and severing BLOCKS
WHEN:   System restarts
THEN:   Health checker detects completed tasks with outgoing BLOCKS
AND:    Severing + cascade is replayed
```

### E4: Task With No Assigned Citizen

```
GIVEN:  Task has high energy from dependency pressure
BUT:    No citizen is assigned via MEMBER_OF
WHEN:   Energy exceeds orphan_threshold
THEN:   Task routing (L1) is triggered to assign a citizen
```

---

## ANTI-BEHAVIORS

### A1: Flat Priority

```
GIVEN:   Task has dependency links
MUST NOT: Use a static priority field to determine urgency
INSTEAD:  Compute urgency from energy (which reflects topology)
```

### A2: Silent Completion

```
GIVEN:   Task is marked completed
MUST NOT: Simply flip a status bit and move on
INSTEAD:  Execute the full cascade: collapse + unblock + crystallize + learn
```

### A3: Knowledge Loss

```
GIVEN:   Task is completed and decayed
MUST NOT: Delete the task node and lose the connection to artifacts
INSTEAD:  Task node stays (low energy, prunable) but artifacts persist with stable weight
```
