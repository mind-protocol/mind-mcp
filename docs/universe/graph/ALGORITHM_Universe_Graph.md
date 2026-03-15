# ALGORITHM -- Universe Graph

```
STATUS: DESIGNING
CREATED: 2026-03-13
UPDATED_BY: Force 1 (architect)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Graph.md
PATTERNS:        ./PATTERNS_Universe_Graph.md
BEHAVIORS:       ./BEHAVIORS_Universe_Graph.md
THIS:            ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md
```

---

## ALG-1: HAS_ACCESS Resolution

Determines whether Actor A can access Space S.

### Input
- `actor_id`: the Actor to check
- `space_id`: the Space to check access for

### Algorithm

```
function has_access(actor_id, space_id):
    # Step 1: Direct link check
    direct_link = find_link(
        from=actor_id,
        to=space_id,
        type="has_access"
    )
    if direct_link exists:
        return AccessResult(
            granted=true,
            role=direct_link.role,
            key=decrypt_space_key(direct_link.encrypted_key, actor_private_key)
        )

    # Step 2: Hierarchical traversal (walk UP from space to ancestors)
    ancestor = parent_space(space_id)  # follow containment links where hierarchy=-1
    while ancestor is not null:
        ancestor_link = find_link(
            from=actor_id,
            to=ancestor,
            type="has_access"
        )
        if ancestor_link exists:
            # Inherited access -- role may be downgraded
            inherited_role = min_role(ancestor_link.role, "member")
            # Key: the sub-space key is encrypted inside the ancestor space
            # Must resolve key chain: ancestor_key -> sub_space_key
            space_key = resolve_key_chain(actor_id, space_id, ancestor)
            return AccessResult(
                granted=true,
                role=inherited_role,
                key=space_key
            )
        ancestor = parent_space(ancestor)

    # Step 3: No access found
    return AccessResult(granted=false)
```

### Key Resolution Chain

When access is inherited (Actor has access to ancestor but not directly to the Space), the symmetric key for the target Space must be resolvable:

```
function resolve_key_chain(actor_id, target_space_id, ancestor_space_id):
    # Get the ancestor's key (Actor can decrypt it)
    ancestor_link = find_link(from=actor_id, to=ancestor_space_id, type="has_access")
    ancestor_key = decrypt(ancestor_link.encrypted_key, actor_private_key)

    # Walk DOWN from ancestor to target, decrypting at each level
    path = find_path(from=ancestor_space_id, to=target_space_id, via="containment")
    current_key = ancestor_key
    for step in path:
        # Each child space stores its key encrypted with parent space's key
        child_key_encrypted = step.child_space.parent_encrypted_key
        current_key = aes_decrypt(child_key_encrypted, current_key)

    return current_key
```

### Complexity
- Direct access: O(1) -- single link lookup
- Hierarchical: O(d) where d = depth of Space hierarchy (typically 3-5 levels)
- Key chain resolution: O(d) -- one decryption per hierarchy level

### Edge Cases
- Actor with `HAS_ACCESS` to a Space that has been deleted: link exists but Space node is gone. Treat as no access.
- Space with no parent (root Space): hierarchy traversal terminates immediately.
- Multiple paths to same Space: first valid path wins. Role = best role among all valid paths.

---

## ALG-2: Encryption Key Distribution

How keys are created, distributed, and rotated.

### Space Key Creation

```
function create_space(actor_id, space_name, parent_space_id=null):
    # Generate AES-256 symmetric key for this space
    space_key = generate_aes256_key()

    # Create the Space node
    space = create_node(
        node_type="space",
        name=space_name,
        type=null  # free-form, set later if desired
    )

    # Create HAS_ACCESS link (owner)
    actor_public_key = get_public_key(actor_id)
    encrypted_space_key = rsa_encrypt(space_key, actor_public_key)

    create_link(
        node_a=actor_id,
        node_b=space.id,
        type="has_access",
        hierarchy=-1,       # Actor owns the Space
        permanence=1.0,     # Ownership is permanent
        trust=1.0,          # Full trust (owner)
        content=json({
            "role": "owner",
            "encrypted_key": base64(encrypted_space_key)
        })
    )

    # If sub-space, store space_key encrypted with parent's key
    if parent_space_id:
        parent_key = get_space_key(actor_id, parent_space_id)
        parent_encrypted_child_key = aes_encrypt(space_key, parent_key)
        create_link(
            node_a=parent_space_id,
            node_b=space.id,
            hierarchy=-1,       # Parent contains child
            permanence=0.9,
            content=json({
                "parent_encrypted_key": base64(parent_encrypted_child_key)
            })
        )

    return space
```

### Granting Access

```
function grant_access(grantor_id, target_actor_id, space_id, role="member"):
    # Verify grantor has admin/owner access
    grantor_access = has_access(grantor_id, space_id)
    assert grantor_access.granted
    assert grantor_access.role in ["owner", "admin"]

    # Get the space key (grantor can decrypt it)
    space_key = grantor_access.key

    # Encrypt space key with target actor's public key
    target_public_key = get_public_key(target_actor_id)
    encrypted_space_key = rsa_encrypt(space_key, target_public_key)

    # Create HAS_ACCESS link
    create_link(
        node_a=target_actor_id,
        node_b=space_id,
        type="has_access",
        hierarchy=0,            # Member, not owner
        permanence=0.7,         # Can decay if unused
        trust=0.3,              # Initial trust, grows via L5/L6
        content=json({
            "role": role,
            "encrypted_key": base64(encrypted_space_key)
        })
    )
```

### Key Rotation (After Adversarial Revocation)

```
function rotate_space_key(admin_id, space_id):
    # Generate new key
    new_key = generate_aes256_key()

    # Re-encrypt all content in the Space with new key
    for node in nodes_in_space(space_id):
        if node.content is encrypted:
            old_content = decrypt(node.content, old_key)
            node.content = encrypt(old_content, new_key)
            # Same for synthesis and embedding

    # Re-encrypt for all remaining HAS_ACCESS links
    for link in find_links(to=space_id, type="has_access"):
        actor_public_key = get_public_key(link.node_a)
        link.content.encrypted_key = rsa_encrypt(new_key, actor_public_key)

    # Update parent containment link if sub-space
    parent = parent_space(space_id)
    if parent:
        parent_key = get_space_key(admin_id, parent)
        update_parent_encrypted_key(parent, space_id, new_key, parent_key)
```

---

## ALG-3: Macro-Crystallization (Law 10 at L3)

Identifies dense clusters in the universe graph and collapses them into hub Narratives.

### Trigger Detection

```
function detect_crystallization_candidates(universe_graph):
    candidates = []

    # Run every N ticks (crystallization_check_interval)
    # At L3: every 500 ticks (slower than L1's 50 ticks)
    for cluster in find_dense_clusters(universe_graph):
        density = cluster.internal_link_count / max_possible_links(cluster.size)
        avg_co_activation = mean(link.weight for link in cluster.internal_links)

        if cluster.size >= L3_CRYSTALLIZATION_MIN_SIZE      # 50 nodes
           and density >= L3_CRYSTALLIZATION_DENSITY         # 0.15
           and avg_co_activation >= L3_CRYSTALLIZATION_WEIGHT:  # 3.0
            candidates.append(cluster)

    return candidates
```

### Crystallization Execution

```
function crystallize(cluster):
    # Step 1: Determine hub type (majority rule)
    type_counts = count_by(cluster.nodes, key=lambda n: n.node_type)
    hub_type = most_common(type_counts)
    # At L3, most crystallizations produce narratives (from moment clusters)
    # Force narrative type if majority is moment (events crystallize into stories)
    if hub_type == "moment":
        hub_type = "narrative"

    # Step 2: Compute centroid embedding
    embeddings = [n.embedding for n in cluster.nodes if n.embedding is not null]
    centroid = mean(embeddings)

    # Step 3: Find medoid (closest node to centroid)
    medoid = argmin(cluster.nodes, key=lambda n: cosine_distance(n.embedding, centroid))

    # Step 4: Create hub node
    hub = create_node(
        node_type=hub_type,
        name=medoid.name,  # Name from most central node
        synthesis=medoid.synthesis,  # Will be regenerated
        embedding=centroid,
        weight=sum(n.weight for n in cluster.nodes) * DAMPING_FACTOR,  # 0.7
        energy=mean(n.energy for n in cluster.nodes),
        stability=0.8  # Hub starts stable
    )

    # Step 5: Create bidirectional links
    for node in cluster.nodes:
        # Hub contains constituent
        create_link(
            node_a=hub.id,
            node_b=node.id,
            hierarchy=-1,
            permanence=0.9,
            weight=node.weight * 0.5
        )
        # Constituent abstracts to hub
        create_link(
            node_a=node.id,
            node_b=hub.id,
            hierarchy=+1,
            permanence=0.9,
            weight=node.weight * 0.3  # Weaker upward link
        )

    # Step 6: Connect hub to cluster's external connections
    for ext_link in cluster.external_links:
        create_link(
            node_a=hub.id,
            node_b=ext_link.external_node,
            weight=ext_link.weight * 0.5,
            # Inherit other dimensions from the external link
            trust=ext_link.trust,
            affinity=ext_link.affinity
        )

    return hub
```

### Post-Crystallization Cleanup

After crystallization, Law 7 (forgetting) handles cleanup:
- Internal links between constituent nodes that are now mediated by the hub lose their utility.
- They decay via normal L7 forgetting (no special cleanup step).
- High-weight constituent-to-constituent links survive (important relationships persist alongside the hub).
- Low-weight constituents themselves may eventually dissolve if they have no other connections.

### L3 Crystallization Parameters

| Parameter | L3 Value | L1 Value | Rationale |
|-----------|----------|----------|-----------|
| `MIN_SIZE` | 50 | 5 | Universe clusters are much larger |
| `DENSITY` | 0.15 | 0.3 | Sparser clusters are still meaningful at scale |
| `WEIGHT_THRESHOLD` | 3.0 | 2.0 | Higher bar for universe-level structure |
| `CHECK_INTERVAL` | 500 ticks | 50 ticks | Less frequent checks at universe scale |
| `DAMPING_FACTOR` | 0.7 | 0.7 | Same damping (hub doesn't get full sum) |
| `HUB_HIERARCHY` | enabled | enabled | Hubs can crystallize into meta-hubs |

---

## ALG-4: Space Hierarchy Traversal

Resolves the full tree of sub-Spaces under a given Space.

### Downward Traversal (Children)

```
function get_sub_spaces(space_id, max_depth=10):
    result = []
    queue = [(space_id, 0)]

    while queue:
        current, depth = queue.pop(0)
        if depth > max_depth:
            continue

        children = find_links(
            from=current,
            type=null,  # containment links don't have type="has_access"
            hierarchy=-1  # parent contains child
        ).filter(lambda link: get_node(link.node_b).node_type == "space")

        for link in children:
            child_space = get_node(link.node_b)
            result.append(SpaceChild(
                space=child_space,
                depth=depth + 1,
                containment_weight=link.weight
            ))
            queue.append((child_space.id, depth + 1))

    return result
```

### Upward Traversal (Ancestors)

```
function parent_space(space_id):
    # Find containment link pointing TO this space with hierarchy=-1
    parent_links = find_links(
        to=space_id,
        hierarchy=-1
    ).filter(lambda link: get_node(link.node_a).node_type == "space")

    if not parent_links:
        return null

    # A Space should have at most one parent
    # If multiple exist, take the highest-weight one
    return max(parent_links, key=lambda l: l.weight).node_a
```

---

## ALG-5: Moment Perception Routing

When a Moment is created in a Space, determines which Actors should perceive it.

```
function route_moment_perception(moment_id, space_id):
    # Find all actors with access to this Space
    accessing_actors = []

    # Direct HAS_ACCESS to this Space
    direct_links = find_links(to=space_id, type="has_access")
    for link in direct_links:
        accessing_actors.append(link.node_a)

    # Actors with HAS_ACCESS to ancestor Spaces (inherited access)
    ancestor = parent_space(space_id)
    while ancestor:
        ancestor_links = find_links(to=ancestor, type="has_access")
        for link in ancestor_links:
            if link.node_a not in accessing_actors:
                accessing_actors.append(link.node_a)
        ancestor = parent_space(ancestor)

    # For each accessing actor, inject the moment as an L1 stimulus
    for actor_id in accessing_actors:
        inject_stimulus(
            actor_id=actor_id,
            stimulus_type="moment_perception",
            moment_id=moment_id,
            space_id=space_id,
            # If encrypted space, the actor's MCP decrypts using its key
            encrypted=is_encrypted_space(space_id)
        )
```

---

## ALG-6: L3 Energy Model

Energy enters the universe graph from L1 actions and propagates structurally.

### Energy Injection (from L1)

Unlike L1 (which has Law 1 for external stimulus), L3 receives energy only from citizen actions:

```
function inject_l3_energy(actor_id, action_type, space_id, energy_amount):
    # Create or update moment
    moment = create_moment(actor_id, action_type, space_id)

    # Energy injection into the moment
    moment.energy += energy_amount

    # Energy splits:
    # - 60% to the Space (activity in context)
    # - 30% to the Actor (actor was active)
    # - 10% to linked Things/Narratives (contextual activation)
    space_link = find_link(moment.id, space_id)
    space_link.energy += energy_amount * 0.6

    actor_link = find_link(moment.id, actor_id)
    actor_link.energy += energy_amount * 0.3

    for related in find_related_nodes(moment):
        related_link = find_link(moment.id, related.id)
        related_link.energy += energy_amount * 0.1 / count(related)
```

### L3 Propagation (Law 2)

Same surplus spill-over as L1, but without compatibility filtering (Law 8 does not apply at L3):

```
function l3_propagate(node):
    threshold = L3_PROPAGATION_THRESHOLD  # 1.0
    if node.energy <= threshold:
        return

    surplus = node.energy - threshold
    outbound_links = find_links(from=node.id)
    total_weight = sum(link.weight for link in outbound_links)

    for link in outbound_links:
        share = surplus * (link.weight / total_weight) * link.polarity[0]
        # No compatibility filter (Law 8 off at L3)
        # No activation_gain modulation (frozen at L3)
        neighbor = get_node(link.node_b)
        neighbor.energy += share
        link.energy += share * 0.1  # Link remembers flow

    node.energy = threshold  # Depletes exactly its surplus
```

### L3 Decay (Law 3)

```
function l3_decay(node):
    node.energy *= (1 - L3_DECAY_RATE)  # L3_DECAY_RATE = 0.01 (slower than L1's 0.02)
    node.recency *= (1 - L3_RECENCY_DECAY)  # 0.005
```

### L3 Weight Consolidation (Law 6)

Law 6 (Weighted Consolidation) applies at L3 with a modified utility gate. At L1, utility is gated by limbic significance (satisfaction, achievement). At L3, the universe has no limbic system, so utility is determined by structural significance:

```
function l3_consolidate(link):
    # At L1: U = limbic_significance (subjective value)
    # At L3: U = structural_utility (objective usage)
    #   For service/thing nodes: U = normalized_usage_count (how often the service is invoked)
    #   For actor-actor links: U = co_activation_frequency (how often both are active together)
    #   For space links: U = presence_intensity (aggregate actor hours)

    U = compute_structural_utility(link)
    dW = CONSOLIDATION_ALPHA * link.avg_energy * U * (1 - link.weight)
    link.weight += dW
```

This is critical for the Metabolic Economy (Force 2): Formula 1 (Progressive Pricing) uses `U_S` (service utility weight) and Formula 4 (Batch Settlement) uses `weight(thing_used)`, both of which depend on L6 consolidation at L3. The `structural_utility` function determines how service nodes accumulate weight without limbic input.

---

## ALG-7: Organization Lifecycle

### Creation

```
function create_organization(founder_id, org_name, mission_statement):
    # Create hall Space
    hall = create_space(founder_id, org_name + "_hall")

    # Create Narrative
    org_narrative = create_node(
        node_type="narrative",
        type="organization",
        name=org_name,
        synthesis=mission_statement,
        weight=1.0
    )

    # Narrative is ABOUT the hall Space
    create_link(
        node_a=org_narrative.id,
        node_b=hall.id,
        hierarchy=-1,  # Narrative defines the Space
        permanence=0.9,
        valence=0.5
    )

    # Founder BELIEVES in the org
    create_link(
        node_a=founder_id,
        node_b=org_narrative.id,
        hierarchy=0,
        trust=0.8,
        affinity=0.7,
        valence=0.5
    )

    return org_narrative, hall
```

### Dissolution

No explicit dissolution action. An organization dissolves when:
1. All `HAS_ACCESS` links to its hall Space decay below threshold (Law 7).
2. All `BELIEVES` links to its Narrative decay below threshold (Law 7).
3. The Narrative node itself decays below weight threshold and is pruned.

This is organic: an abandoned org dies naturally. An active org lives.

---

## ALG-8: Actor Reputation Computation

```
function compute_reputation(actor_id):
    inbound_links = find_links(to=actor_id)

    if not inbound_links:
        return 0.0

    weighted_trust_sum = sum(
        link.trust * link.weight
        for link in inbound_links
        if link.trust > 0
    )
    weight_sum = sum(
        link.weight
        for link in inbound_links
        if link.trust > 0
    )

    if weight_sum == 0:
        return 0.0

    return weighted_trust_sum / weight_sum
```

Always computed on demand. Never stored. Different queries may apply different filters (e.g., "reputation within Space X" = only consider links from Actors in Space X).
