# VALIDATION -- Universe Graph

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
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
THIS:            ./VALIDATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md
```

---

## STRUCTURAL INVARIANTS

### INV-1: No Orphan Spaces

**Statement:** Every Space in the universe graph must have at least one `HAS_ACCESS` link from an Actor with role `owner`.

**Why:** A Space with no owner is unmanageable -- no one can grant access, rotate keys, or delete content. Orphan Spaces would accumulate as dead weight.

**Verification:**
```
for space in all_spaces():
    owner_links = find_links(
        to=space.id,
        type="has_access"
    ).filter(lambda l: "owner" in l.content)
    assert len(owner_links) >= 1, f"Space {space.id} has no owner"
```

**Exception:** If all owners leave and the Space has been inactive long enough, Law 7 (forgetting) will eventually dissolve the Space node itself. This is acceptable -- the Space dies naturally.

**Recovery:** If an orphan Space is detected with active content but no owner, escalate to protocol admin. Do not auto-assign ownership.

---

### INV-2: All Access Via Links

**Statement:** No code path may determine access by reading a property on a node (e.g., `space.access_list`). All access checks must query `HAS_ACCESS` links.

**Why:** Property-based access doesn't participate in graph physics, can't be traversed, and creates a parallel permission system.

**Verification:**
```
# Static analysis: grep for property-based access patterns
assert no matches for:
    - "access_list"
    - "allowed_users"
    - "members" as a property on Space nodes
    - Any dict/list field on nodes used for permission checking
```

**How to test:** Integration test where access is granted via `HAS_ACCESS` link, then verify that removing the link (not a property) revokes access.

---

### INV-3: Encryption Coverage

**Statement:** For every Space marked as encrypted (brain Spaces and any explicitly encrypted Space), every node within that Space must have its `content`, `synthesis`, and `embedding` fields encrypted.

**Why:** Partial encryption is worse than no encryption -- it creates a false sense of security while leaking data.

**Verification:**
```
for space in encrypted_spaces():
    space_key = get_space_key_for_validation(space.id)  # admin/test key
    for node in nodes_in_space(space.id):
        # Content must not be plaintext
        assert not is_plaintext(node.content), f"Node {node.id} content unencrypted"
        assert not is_plaintext(node.synthesis), f"Node {node.id} synthesis unencrypted"
        if node.embedding:
            assert not is_plaintext_vector(node.embedding), f"Node {node.id} embedding unencrypted"

        # Content must be decryptable with the space key
        assert can_decrypt(node.content, space_key), f"Node {node.id} content not decryptable"
```

**Edge case:** Newly created nodes in an encrypted Space must be encrypted before being committed to the graph. No "encrypt later" pattern.

---

### INV-4: Single Universe Per Graph

**Statement:** Each FalkorDB graph (or namespace) contains exactly one universe. Cross-universe queries are not supported.

**Why:** Universe isolation prevents data leakage between universes and simplifies the operational model.

**Verification:**
```
# At graph creation, a universe_id metadata node is created
universe_nodes = find_nodes(node_type="thing", type="universe_metadata")
assert len(universe_nodes) == 1, "Graph must contain exactly one universe identifier"
```

---

### INV-5: relation_kind Always Null at L3

**Statement:** Every link in the universe graph (L3 scope) must have `relation_kind = null`. Non-null `relation_kind` values are L1-only.

**Why:** The universe has no cognition. Cognitive categories (remembers, cares_about, wants) are brain-internal constructs that do not apply at universe scale.

**Verification:**
```
for link in all_l3_links():
    assert link.relation_kind is null, f"Link {link.id} has relation_kind={link.relation_kind}"
```

**Note:** Brain Spaces are within the universe graph but their content is encrypted. When an L1 engine decrypts and operates on brain content, it may use `relation_kind` internally. The invariant applies to unencrypted L3-scope links only.

---

### INV-6: Plutchik Axes Frozen at L3

**Statement:** All Plutchik emotion axes (`joy_sadness`, `trust_disgust`, `fear_anger`, `surprise_anticipation`) must be `0.0` on L3-scope links.

**Why:** The universe has no feelings. Emotional coloring happens in L1 brains.

**Verification:**
```
for link in all_l3_links():
    assert link.joy_sadness == 0.0
    assert link.trust_disgust == 0.0
    assert link.fear_anger == 0.0
    assert link.surprise_anticipation == 0.0
```

---

### INV-7: Trust Lives on Links Only

**Statement:** No node in the universe graph may have a `trust` or `trust_score` or `reputation` field. Trust is exclusively a link property. Reputation is computed on demand.

**Why:** Storing trust on nodes creates a single "reputation score" that flattens the multi-dimensional reality of trust relationships. An Actor may be highly trusted by collaborators and distrusted by competitors -- this is two different link trust values, not one node score.

**Verification:**
```
for node in all_nodes():
    assert "trust" not in node.fields  # (beyond what NodeBase defines)
    assert "trust_score" not in node.fields
    assert "reputation" not in node.fields
```

---

### INV-8: HAS_ACCESS Link Structure

**Statement:** Every `HAS_ACCESS` link must have:
- `type` field = `"has_access"`
- `node_a` = Actor (node_type: actor)
- `node_b` = Space (node_type: space)
- `content` containing `role` (one of: owner, admin, member)
- For encrypted Spaces: `content` containing `encrypted_key` (base64 AES-256 key encrypted with Actor's public key)

**Why:** Malformed `HAS_ACCESS` links break the access resolution algorithm and can lead to access grants without encryption keys (data visible but undecryptable) or keys without proper role assignment.

**Verification:**
```
for link in find_links(type="has_access"):
    source = get_node(link.node_a)
    target = get_node(link.node_b)
    assert source.node_type == "actor", f"HAS_ACCESS source must be actor, got {source.node_type}"
    assert target.node_type == "space", f"HAS_ACCESS target must be space, got {target.node_type}"
    content = parse_json(link.content)
    assert content.role in ["owner", "admin", "member"]
    if is_encrypted_space(target.id):
        assert "encrypted_key" in content, f"Encrypted space {target.id} missing key on HAS_ACCESS link"
```

---

### INV-9: Space Hierarchy Acyclicity

**Statement:** The containment hierarchy (links with hierarchy = -1 between Spaces) must be a DAG (directed acyclic graph). No Space may be an ancestor of itself.

**Why:** Cycles in containment would cause infinite loops in access resolution (ALG-1) and key chain resolution.

**Verification:**
```
function check_acyclicity():
    for space in all_spaces():
        visited = set()
        current = space.id
        while current:
            assert current not in visited, f"Cycle detected at {current}"
            visited.add(current)
            current = parent_space(current)
```

---

### INV-10: Energy Conservation at L3

**Statement:** During L3 propagation (Law 2 at universe scale), the total energy in the system must be conserved. A node depletes exactly its surplus when propagating to neighbors.

**Why:** Energy creation from nothing would cause runaway activation. Energy destruction would cause the graph to go dark.

**Verification:**
```
function verify_propagation_conservation(node, pre_state, post_state):
    surplus = pre_state.node_energy - PROPAGATION_THRESHOLD
    energy_distributed = sum(
        post_state.neighbor_energy[n] - pre_state.neighbor_energy[n]
        for n in node.neighbors
    )
    energy_retained = post_state.node_energy - pre_state.node_energy + surplus

    # Conservation: what left = what arrived (within float tolerance)
    assert abs(surplus - energy_distributed) < 1e-6
    assert abs(post_state.node_energy - PROPAGATION_THRESHOLD) < 1e-6
```

**Exception:** Energy decay (Law 3) deliberately destroys energy. Conservation applies only within a single propagation step, not across ticks.

---

### INV-11: No Algorithm Branches on space_type

**Statement:** No physics law, formula, access check, or crystallization rule may read the `space_type` field for conditional logic.

**Why:** Taxonomy-based branching creates a maintenance burden and prevents the graph from handling novel Space types without code changes.

**Verification:**
```
# Static analysis across all physics, access, and crystallization code
assert no matches for:
    - "space_type ==" or "space_type !="
    - "if.*space_type"
    - "match.*space_type"
    - "filter.*space_type"
in files: runtime/physics/**, runtime/access/**, runtime/crystallization/**
```

---

### INV-12: Macro-Crystallization Hub Integrity

**Statement:** Every hub node created by macro-crystallization must have:
- At least one `contains` link (hierarchy = -1) to a constituent
- At least one `abstracts` link (hierarchy = +1) from a constituent
- Weight = sum of constituent weights * DAMPING_FACTOR (within tolerance)
- Type derived from majority rule among constituents

**Why:** Hubs without proper links don't actually organize the graph. Hubs with incorrect weight distort the physics.

**Verification:**
```
for hub in find_nodes(created_by="crystallization"):
    contains_links = find_links(from=hub.id, hierarchy=-1)
    abstracts_links = find_links(to=hub.id, hierarchy=+1)
    assert len(contains_links) >= 1
    assert len(abstracts_links) >= 1

    constituent_weight_sum = sum(
        get_node(l.node_b).weight for l in contains_links
    )
    expected_weight = constituent_weight_sum * DAMPING_FACTOR
    assert abs(hub.weight - expected_weight) < 0.1
```

---

## TEST STRATEGY

### Unit Tests

| Test | Validates |
|------|-----------|
| `test_has_access_direct` | ALG-1: Direct link grants access |
| `test_has_access_inherited` | ALG-1: Ancestor link grants access to sub-Space |
| `test_has_access_revoked` | ALG-1: Removed link denies access |
| `test_key_encryption_roundtrip` | ALG-2: Key encrypt/decrypt cycle |
| `test_key_rotation` | ALG-2: After rotation, old key fails, new key works |
| `test_crystallization_trigger` | ALG-3: Cluster above threshold triggers crystallization |
| `test_crystallization_below_threshold` | ALG-3: Cluster below threshold does not trigger |
| `test_hierarchy_acyclicity` | INV-9: Cycle detection rejects cyclic containment |
| `test_energy_conservation` | INV-10: Propagation conserves energy |
| `test_encrypted_content_unreadable` | INV-3: Encrypted content without key is gibberish |

### Integration Tests

| Test | Validates |
|------|-----------|
| `test_space_creation_to_moment_recording` | B1 + B4: Create Space, record Moment, verify actor perceives it |
| `test_org_creation_membership_access` | B5 + B6: Create org, join, verify hall Space access |
| `test_crystallization_lifecycle` | B7 + B8: Create many moments, trigger crystallization, verify hub, verify cleanup |
| `test_brain_encryption_isolation` | B9: Create brain Space, verify content encrypted, verify other actors cannot read |
| `test_access_decay_via_law7` | B8: Verify unused HAS_ACCESS link eventually dissolves |

### Load Tests

| Test | Validates |
|------|-----------|
| `test_graph_with_1m_nodes` | O5: Scalability without taxonomy |
| `test_propagation_performance` | ALG-6: L3 propagation at scale |
| `test_crystallization_at_scale` | ALG-3: Macro-crystallization with 10k+ node clusters |
