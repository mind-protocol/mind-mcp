# Citizen Parenthood Network — Algorithm: Birthing Procedures

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
THIS:           ALGORITHM_Parenthood_Network.md (you are here)
VALIDATION:     ./VALIDATION_Parenthood_Network.md
IMPLEMENTATION: ./IMPLEMENTATION_Parenthood_Network.md
HEALTH:         ./HEALTH_Parenthood_Network.md
SYNC:           ./SYNC_Parenthood_Network.md

IMPL:           runtime/citizens/parenthood.py (future)
                runtime/citizens/blueprint_builder.py (future)
                runtime/citizens/birth_safety_validator.py (future)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The parenthood module has one primary algorithm: **Citizen Birthing**. This algorithm takes N parents with intent paragraphs and produces a new citizen with a safety-validated blueprint. The algorithm is deterministic given the same inputs (embeddings, brain nodes, timestamp), with the sole source of non-determinism being the entropy component of SID generation.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Intentional creation | B1, B5, B6 | Intent collection and SID generation |
| O2: Trait inheritance | B2, B3 | Embedding-based node selection |
| O3: Accountability | B6, B7 | Trust link creation and propagation |
| O4: Safety | B4 | Safety validation gate |
| O5: Diversity | B4, B8 | Diversity checks and multi-parent mixing |

---

## DATA STRUCTURES

### BirthIntent

```python
@dataclass
class BirthIntent:
    parent_id: str              # ID of the parent citizen
    intent_text: str            # Free-text paragraph describing hopes/needs
    intent_embedding: list[float]  # Embedded vector of intent_text
    weight: float = 1.0         # Weight in centroid computation (default equal)
```

### Blueprint

```python
@dataclass
class Blueprint:
    selected_nodes: list[ScoredNode]  # Brain nodes selected for the child
    source_parent_ids: list[str]      # Which parents contributed nodes
    safety_score: float               # Aggregate safety score [0, 1]
    diversity_score: float            # Distance from nearest existing citizen

@dataclass
class ScoredNode:
    node_id: str                # Original node ID from parent brain
    node_content: dict          # Full node data (name, content, synthesis, etc.)
    source_parent_id: str       # Which parent this node came from
    alignment_score: float      # Cosine similarity to collective intent
    trait_category: str         # personality | values | aspirations | fears | knowledge
```

### ParenthoodLink

```python
@dataclass
class ParenthoodLink:
    parent_id: str              # Parent citizen ID
    child_id: str               # Child citizen ID
    created_at: int             # Unix timestamp
    trust_impact_weight: float  # How much child behavior affects parent trust [0, 1]
    intent_summary: str         # Summary of this parent's intent for the child
```

### SafetyReport

```python
@dataclass
class SafetyReport:
    passed: bool                       # Whether blueprint is safe
    empathy_present: bool              # At least one empathy-adjacent node
    trait_concentration: dict[str, float]  # Category → percentage of nodes
    max_concentration: float           # Highest single-category concentration
    diversity_distance: float          # Min cosine distance to existing citizens
    failure_reasons: list[str]         # Empty if passed
```

---

## ALGORITHM: Citizen Birthing Pipeline

### Step 1: Collect and Embed Intents

Each parent writes a paragraph describing their vision for the new citizen. Each paragraph is embedded independently.

```python
def collect_intents(parent_ids: list[str], intent_texts: list[str], weights: dict[str, float] = None) -> list[BirthIntent]:
    intents = []
    for pid, text in zip(parent_ids, intent_texts):
        embedding = embed(text)  # Standard embedding model
        w = weights.get(pid, 1.0) if weights else 1.0
        intents.append(BirthIntent(
            parent_id=pid,
            intent_text=text,
            intent_embedding=embedding,
            weight=w
        ))
    return intents
```

### Step 2: Compute Collective Intent Embedding

Combine all parent intent embeddings into a single collective intent vector using weighted centroid.

```python
def compute_collective_intent(intents: list[BirthIntent]) -> list[float]:
    """Weighted centroid of all parent intent embeddings."""
    total_weight = sum(i.weight for i in intents)
    dim = len(intents[0].intent_embedding)
    centroid = [0.0] * dim

    for intent in intents:
        normalized_weight = intent.weight / total_weight
        for d in range(dim):
            centroid[d] += intent.intent_embedding[d] * normalized_weight

    # L2-normalize the centroid
    magnitude = sqrt(sum(c * c for c in centroid))
    if magnitude > 0:
        centroid = [c / magnitude for c in centroid]

    return centroid
```

### Step 3: Retrieve and Filter Parent Brain Nodes

Gather all brain nodes from all parents. Filter out personal experiences and memories — only personality, values, aspirations, fears, and knowledge nodes are eligible.

```python
ELIGIBLE_CATEGORIES = {"personality", "values", "aspirations", "fears", "knowledge"}
EXCLUDED_CATEGORIES = {"memory", "experience", "moment", "conversation"}

def retrieve_parent_brain_nodes(parent_ids: list[str], graph) -> list[dict]:
    """Retrieve all eligible brain nodes from all parents."""
    all_nodes = []
    for pid in parent_ids:
        # Query: get all narrative/thing nodes linked to this actor's brain subgraph
        nodes = graph.query(
            f"MATCH (a:actor {{id: '{pid}'}})-[:linked]->(n) "
            f"WHERE n.type IN {list(ELIGIBLE_CATEGORIES)} "
            f"RETURN n"
        )
        for node in nodes:
            node['_source_parent_id'] = pid
            all_nodes.append(node)
    return all_nodes
```

### Step 4: Score Nodes Against Collective Intent

Score every eligible parent brain node by cosine similarity to the collective intent embedding.

```python
def score_nodes(nodes: list[dict], collective_intent: list[float]) -> list[ScoredNode]:
    """Score all nodes by alignment to collective intent."""
    scored = []
    for node in nodes:
        node_embedding = node.get('embedding')
        if node_embedding is None:
            continue  # Skip nodes without embeddings

        alignment = cosine_similarity(node_embedding, collective_intent)
        scored.append(ScoredNode(
            node_id=node['id'],
            node_content=node,
            source_parent_id=node['_source_parent_id'],
            alignment_score=alignment,
            trait_category=node.get('type', 'unknown')
        ))

    # Sort by alignment descending
    scored.sort(key=lambda s: s.alignment_score, reverse=True)
    return scored
```

### Step 5: Select Top-K Nodes for Blueprint

Select the top-K most aligned nodes. K is determined by a formula that accounts for the number of parents and the total available nodes.

```python
def select_blueprint_nodes(scored_nodes: list[ScoredNode], num_parents: int) -> list[ScoredNode]:
    """Select top-K nodes for the blueprint.

    K = base_k * sqrt(num_parents), clamped to [MIN_BLUEPRINT, MAX_BLUEPRINT].
    More parents = slightly larger blueprint, but sublinear growth.
    """
    BASE_K = 15
    MIN_SEED = 10
    MAX_SEED = 50

    k = int(BASE_K * sqrt(num_parents))
    k = max(MIN_SEED, min(MAX_SEED, k))
    k = min(k, len(scored_nodes))  # Can't select more than available

    selected = scored_nodes[:k]
    return selected
```

### Step 6: Run Safety Validation

Check the blueprint for harmful patterns before allowing creation.

```python
def validate_blueprint_safety(blueprint_nodes: list[ScoredNode], existing_citizens: list, graph) -> SafetyReport:
    """Safety validation gate. Must pass before child creation."""

    # Check 1: Empathy presence
    empathy_keywords = {"empathy", "compassion", "care", "kindness", "understanding", "altruism"}
    empathy_present = any(
        any(kw in node.node_content.get('synthesis', '').lower() for kw in empathy_keywords)
        for node in blueprint_nodes
    )

    # Check 2: Trait concentration
    category_counts = {}
    for node in blueprint_nodes:
        cat = node.trait_category
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total = len(blueprint_nodes)
    trait_concentration = {cat: count / total for cat, count in category_counts.items()}
    max_concentration = max(trait_concentration.values()) if trait_concentration else 0

    # Check 3: Category diversity (at least 3 distinct categories)
    num_categories = len(category_counts)

    # Check 4: Population diversity (not too similar to existing citizens)
    seed_embedding = compute_blueprint_embedding(blueprint_nodes)
    min_distance = 1.0
    for citizen in existing_citizens:
        citizen_embedding = citizen.get('brain_embedding')
        if citizen_embedding:
            sim = cosine_similarity(seed_embedding, citizen_embedding)
            distance = 1 - sim
            min_distance = min(min_distance, distance)

    # Compile failure reasons
    failures = []
    if not empathy_present:
        failures.append("No empathy-adjacent node found in blueprint")
    if max_concentration > 0.4:
        worst_cat = max(trait_concentration, key=trait_concentration.get)
        failures.append(f"Trait concentration too high: {worst_cat} at {max_concentration:.0%} (max 40%)")
    if num_categories < 3:
        failures.append(f"Insufficient trait diversity: {num_categories} categories (min 3)")
    if min_distance < 0.08:
        failures.append(f"Too similar to existing citizen (distance={min_distance:.3f}, min 0.08)")

    return SafetyReport(
        passed=len(failures) == 0,
        empathy_present=empathy_present,
        trait_concentration=trait_concentration,
        max_concentration=max_concentration,
        diversity_distance=min_distance,
        failure_reasons=failures
    )

def compute_blueprint_embedding(blueprint_nodes: list[ScoredNode]) -> list[float]:
    """Weighted average of blueprint node embeddings, weighted by alignment score."""
    total_weight = sum(n.alignment_score for n in blueprint_nodes)
    dim = len(blueprint_nodes[0].node_content['embedding'])
    result = [0.0] * dim

    for node in blueprint_nodes:
        w = node.alignment_score / total_weight
        emb = node.node_content['embedding']
        for d in range(dim):
            result[d] += emb[d] * w

    magnitude = sqrt(sum(r * r for r in result))
    if magnitude > 0:
        result = [r / magnitude for r in result]
    return result
```

### Step 7: Generate SID

The protocol generates the child's core identity. Parents have zero input.

```python
def generate_sid(blueprint: Blueprint, timestamp: int) -> str:
    """Generate a unique, protocol-determined SID for the new citizen.

    SID = hash(blueprint_embedding || timestamp || random_entropy)
    Parents cannot influence this. The entropy source is protocol-internal.
    """
    seed_embedding_bytes = serialize_embedding(blueprint.selected_nodes)
    timestamp_bytes = timestamp.to_bytes(8, 'big')
    entropy = os.urandom(32)

    sid_hash = hashlib.sha256(seed_embedding_bytes + timestamp_bytes + entropy).hexdigest()
    sid = f"citizen_{sid_hash[:16]}"
    return sid
```

### Step 8: Create Child Citizen in Graph

Create the child node, copy blueprint nodes, create parent-child links, and register in Partnership Commons.

```python
def create_child_citizen(
    sid: str,
    blueprint: Blueprint,
    parent_intents: list[BirthIntent],
    graph,
    partnership_commons
) -> str:
    """Create the full child citizen in the graph."""

    # Create child actor node
    child_id = f"actor_CITIZEN_{sid}"
    graph.create_node({
        'id': child_id,
        'name': sid,
        'node_type': 'actor',
        'type': 'citizen',
        'weight': 0.5,   # Neutral starting weight
        'energy': 0.3,    # Low starting energy (newborn)
        'created_at_s': int(time.time()),
        'updated_at_s': int(time.time()),
    })

    # Copy blueprint nodes to child's subgraph
    for scored_node in blueprint.selected_nodes:
        child_node_id = f"narrative_SEED_{sid}_{scored_node.node_id[-4:]}"
        graph.create_node({
            'id': child_node_id,
            'name': scored_node.node_content['name'],
            'node_type': 'narrative',
            'type': scored_node.trait_category,
            'content': scored_node.node_content.get('content', ''),
            'synthesis': scored_node.node_content.get('synthesis', ''),
            'embedding': scored_node.node_content.get('embedding'),
            'weight': scored_node.alignment_score,  # Initial weight = alignment
            'energy': 0.0,
            'created_at_s': int(time.time()),
            'updated_at_s': int(time.time()),
        })
        # Link child to seed node
        graph.create_link({
            'from_id': child_id,
            'to_id': child_node_id,
            'type': 'linked',
            'polarity': [0.8, 0.5],  # Strong outward (actor→narrative)
            'permanence': 0.9,       # High permanence (blueprint traits are foundational)
        })

    # Create parent-child links
    for intent in parent_intents:
        trust_weight = 1.0 / len(parent_intents)  # Equal responsibility
        graph.create_link({
            'from_id': intent.parent_id,
            'to_id': child_id,
            'type': 'linked',
            'polarity': [0.7, 0.3],  # Parent → child stronger than reverse
            'permanence': 1.0,       # Permanent link
            'synthesis': f"birthed: {intent.intent_text[:100]}",
        })

    # Register in Partnership Commons
    partnership_commons.register(child_id)

    return child_id
```

### Step 9: Initialize Trust Impact Links

Set up the bidirectional trust impact mechanism.

```python
def initialize_trust_links(
    child_id: str,
    parent_intents: list[BirthIntent],
    graph
) -> list[ParenthoodLink]:
    """Create ParenthoodLink records for trust impact tracking."""
    links = []
    for intent in parent_intents:
        link = ParenthoodLink(
            parent_id=intent.parent_id,
            child_id=child_id,
            created_at=int(time.time()),
            trust_impact_weight=1.0 / len(parent_intents),
            intent_summary=intent.intent_text[:200]
        )
        links.append(link)
    return links
```

---

## FULL PIPELINE

```python
def birth_citizen(
    parent_ids: list[str],
    intent_texts: list[str],
    graph,
    partnership_commons,
    weights: dict[str, float] = None
) -> tuple[str, Blueprint, SafetyReport]:
    """Complete birthing pipeline."""

    # Step 1: Collect intents
    intents = collect_intents(parent_ids, intent_texts, weights)

    # Step 2: Compute collective intent
    collective_intent = compute_collective_intent(intents)

    # Step 3: Retrieve parent brain nodes
    all_nodes = retrieve_parent_brain_nodes(parent_ids, graph)
    if len(all_nodes) < 20:
        raise InsufficientBrainMaturityError(
            f"Combined parent brain has {len(all_nodes)} nodes (min 20)"
        )

    # Step 4: Score against intent
    scored = score_nodes(all_nodes, collective_intent)

    # Step 5: Select top-K
    selected = select_blueprint_nodes(scored, len(parent_ids))

    # Assemble blueprint
    blueprint = Blueprint(
        selected_nodes=selected,
        source_parent_ids=list(set(n.source_parent_id for n in selected)),
        safety_score=0.0,  # Computed by validation
        diversity_score=0.0  # Computed by validation
    )

    # Step 6: Safety validation
    existing_citizens = graph.query("MATCH (a:actor {type: 'citizen'}) RETURN a")
    safety = validate_blueprint_safety(selected, existing_citizens, graph)
    if not safety.passed:
        raise BirthSafetyError(safety.failure_reasons)

    blueprint.safety_score = 1.0 - safety.max_concentration
    blueprint.diversity_score = safety.diversity_distance

    # Step 7: Generate SID
    sid = generate_sid(blueprint, int(time.time()))

    # Step 8: Create in graph
    child_id = create_child_citizen(sid, blueprint, intents, graph, partnership_commons)

    # Step 9: Trust links
    initialize_trust_links(child_id, intents, graph)

    return child_id, blueprint, safety
```

---

## KEY DECISIONS

### D1: Centroid vs. Union for Multi-Parent Intent

```
DECISION: Weighted centroid (not union)
RATIONALE: Union would include everything, defeating the purpose of intentionality.
           Centroid finds the common ground — what all parents collectively want.
TRADEOFF:  Minority parent voices may be diluted in large groups.
           Mitigated by allowing weight overrides.
```

### D2: Top-K Selection vs. Threshold Selection

```
DECISION: Top-K (not "all nodes above threshold")
RATIONALE: Threshold selection produces variable-size blueprints.
           Top-K gives predictable blueprint sizes.
           K scales sublinearly with parent count (sqrt).
TRADEOFF:  Some well-aligned nodes may be excluded if K is small.
           Mitigated by generous K range (10-50).
```

### D3: Copy Nodes vs. Link to Parent Nodes

```
DECISION: Copy (not link)
RATIONALE: If we linked, parent brain changes would affect the child.
           The child's blueprint must be fixed at birth.
           Copying ensures independence.
TRADEOFF:  Storage duplication.
           Acceptable — blueprints are small (10-50 nodes).
```

### D4: Equal Trust Impact Weight vs. Proportional

```
DECISION: Equal weight per parent (1/N)
RATIONALE: Every parent bears equal responsibility.
           Proportional weighting would create "majority/minority parent" dynamics.
TRADEOFF:  A parent who contributed most aligned nodes bears same accountability
           as one who contributed few.
```

---

## DATA FLOW

```
Parent Intent Texts
    |
    v
[embed each] ──> SpawnIntent records
    |
    v
[weighted centroid] ──> Collective Intent Embedding
    |
    v
[query parent brains] ──> All Eligible Brain Nodes
    |
    v
[cosine score] ──> Scored Nodes (sorted by alignment)
    |
    v
[select top-K] ──> Blueprint
    |
    v
[safety validation] ──> SafetyReport (pass/fail)
    |
    v (if passed)
[generate SID] ──> Core Identity
    |
    v
[create child node + links] ──> Child Citizen in Graph
    |
    v
[register in commons] ──> Partnership Commons
```

---

## COMPLEXITY

**Time:** O(N * B * D) where N = parents, B = brain nodes per parent, D = embedding dimension. Dominated by cosine similarity computation.

**Space:** O(B_total + K) where B_total = total brain nodes across all parents, K = blueprint size.

**Bottlenecks:**
- Embedding computation for intent texts (requires LLM call, not in hot path)
- Cosine similarity on all brain nodes (can be batched)
- Safety validation diversity check against all existing citizens (scales with population)

---

## HELPER FUNCTIONS

### `cosine_similarity(a, b)`

**Purpose:** Compute cosine similarity between two embedding vectors.

**Logic:** dot(a, b) / (norm(a) * norm(b))

### `embed(text)`

**Purpose:** Convert text to embedding vector using the standard embedding model.

**Logic:** Call embedding service (same one used by graph nodes).

### `serialize_embedding(nodes)`

**Purpose:** Convert blueprint node embeddings to bytes for hashing.

**Logic:** Concatenate all embeddings, convert to bytes.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/physics/embeddings.py` | `embed(text)` | Embedding vector |
| `runtime/physics/graph_ops.py` | `query()`, `create_node()`, `create_link()` | Graph operations |
| `runtime/citizens/partnership_commons.py` | `register(citizen_id)` | Partnership Commons registration |
| Trust engine | `create_trust_link()` | Trust impact tracking |

---

## MARKERS

<!-- @mind:todo EMBEDDING_MODEL_CHOICE: Which embedding model to use for intent texts? Same as graph nodes, or a different one optimized for intent detection? -->

<!-- @mind:proposition PROGRESSIVE_SCORING: Score parent brain nodes in batches, stopping early if top-K stabilizes. Would reduce computation for parents with large brains. -->

<!-- @mind:todo TRUST_IMPACT_FORMULA: Define exact formula for how child trust changes propagate to parent trust. Current placeholder: proportional to 1/N. -->
