# BEHAVIORS -- Universe Graph

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
THIS:            ./BEHAVIORS_Universe_Graph.md
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md
```

---

## OBSERVABLE BEHAVIORS

### B1: Space Creation

**When** an Actor creates a new context (channel, repo, world, brain Space), **then** a Space node is created in the universe graph, and a `HAS_ACCESS` link (role: owner, hierarchy: -1, permanence: 1.0) is created from the Actor to the Space.

**Economic implications:** Space creation may carry a $MIND cost or deposit requirement. The economic rules governing Space creation costs are defined by the Metabolic Economy (Force 2). See `docs/economy/metabolic/` for pricing and anti-gaming mechanisms. F1 defines the structural operations; F2 defines the economic constraints.

**Observable effects:**
- New Space node appears with `node_type: space`.
- Free-form `type` field may carry a hint (e.g., `"discord_channel"`, `"brain_self_model"`).
- `space_type` field may carry a descriptive string. No algorithm reads this.
- A `HAS_ACCESS` link exists from the creating Actor to the Space.
- The link carries the per-Space AES-256 symmetric key, encrypted with the Actor's public key.
- If the Space is a sub-Space, a containment link (hierarchy: -1) is created from the parent Space to this Space.
- The parent Space's existing `HAS_ACCESS` members inherit access to the new sub-Space (no new links created -- access resolution traverses the hierarchy).

### B2: Access Granting

**When** an Actor with admin/owner role on a Space grants access to another Actor, **then** a new `HAS_ACCESS` link is created from the target Actor to the Space.

**Observable effects:**
- New link appears with `type: "has_access"` and the granted role.
- The per-Space symmetric key is encrypted with the target Actor's public key and stored on the link.
- The target Actor can now read unencrypted content in the Space (if it has the key) and create Moments within it.
- Co-activation (Law 5) between the granting Actor and the target Actor is triggered by the shared Space activity.

### B3: Access Revocation

**When** an Actor's `HAS_ACCESS` link to a Space is removed (or decays below threshold via Law 7), **then** the Actor loses the ability to read or write within that Space.

**Observable effects:**
- The `HAS_ACCESS` link no longer exists.
- The encrypted symmetric key on the removed link is lost.
- If revocation is adversarial (Actor was removed for cause, not natural decay), the Space key should be rotated and re-encrypted for all remaining `HAS_ACCESS` links.
- Downstream sub-Space access derived from this link is also lost (hierarchy traversal no longer reaches the Actor).

### B4: Moment Recording

**When** something happens in a Space (a message is sent, a commit is pushed, a battle occurs, a transaction settles), **then** a Moment node is created and linked to the Space.

**Observable effects:**
- New Moment node with `node_type: moment`, `status: active` (or `completed` for atomic events).
- Link from Moment to Space (hierarchy: +1, meaning the Moment elaborates the Space).
- Link from Moment to the Actor who created it (hierarchy: +1, meaning the Moment elaborates the Actor's history).
- Energy is injected into the Moment -- this energy propagates (Law 2) to the Space, to the Actor, and through connected links.
- All Actors with `HAS_ACCESS` to the Space can perceive this Moment (their L1 brains receive it as a stimulus via Law 21 / L3->L1 membrane).
- If the Space is encrypted (brain Space), the Moment's content and synthesis are encrypted with the Space's symmetric key.

### B5: Organization Creation

**When** an Actor creates an organization, **then** a Narrative node (type: `"organization"`) and a hall Space are created.

**Observable effects:**
- New Narrative node: `node_type: narrative`, `type: "organization"`, name = org name, synthesis = org mission statement.
- New Space node: the "hall" Space, the org's primary container.
- Link from Narrative to Space: the org is `ABOUT` its hall. (hierarchy: -1, the narrative contains/defines the space).
- `HAS_ACCESS` link from the creating Actor to the hall Space (role: owner).
- Link from Actor to Narrative: the Actor `BELIEVES` in the org. (polarity biased toward the narrative, positive valence).

### B6: Organization Membership

**When** an Actor joins an organization, **then** they receive `HAS_ACCESS` to the org's hall Space and create a `BELIEVES` link to the org Narrative.

**Observable effects:**
- New `HAS_ACCESS` link: Actor to hall Space (role: member).
- New link: Actor to Narrative (representing belief/alignment).
- The Actor can now perceive all Moments in the hall Space and its sub-Spaces.
- The Actor's trust toward the Narrative node contributes to the org's reputation.

### B7: Macro-Crystallization

**When** a dense cluster of co-activated nodes exceeds the crystallization threshold within a region of the universe graph, **then** Law 10 fires and creates a new hub Narrative.

**Observable effects:**
- New Narrative node created with weight inherited from constituent nodes.
- `contains` links (hierarchy: -1) from hub to each constituent.
- `abstracts` links (hierarchy: +1) from each constituent to hub.
- Name derived from medoid node (the constituent most central to the cluster).
- Type derived from majority rule among constituent types.
- Content/synthesis derived from centroid embedding.
- Over subsequent ticks, Law 7 (forgetting) dissolves low-weight links between individual constituents that are now represented by the hub.
- Net effect: node/link count in that region decreases as the hub absorbs the cluster.

Example thresholds at L3 scale:
- Commit cluster: ~300 commits -> 1 project-phase narrative
- Transaction cluster: ~500 transfers -> 1 economic partnership narrative
- Battle cluster: ~200 events -> 1 campaign narrative

### B8: Link Dissolution (Self-Management)

**When** a link has not been traversed or activated for a sustained period, **then** Law 7 (forgetting) reduces its weight. Below a threshold, the link dissolves entirely.

**Observable effects:**
- Link weight decreases tick by tick.
- Once weight falls below dissolution threshold, the link is removed from the graph.
- For `HAS_ACCESS` links: this means access naturally decays if the Actor never visits the Space. An Actor who joined a channel 2 years ago and never returned will eventually lose their `HAS_ACCESS` link.
- Structural links (contains, abstracts from crystallization) decay at a slower rate (4x slower, matching L1 behavior for identity-critical links).

### B9: Encrypted Brain Operations

**When** an Actor's L1 cognitive engine runs (tick cycle), **then** it operates on the Actor's brain Spaces within the universe graph, decrypting content as needed.

**Observable effects:**
- The MCP server holds the Actor's private key.
- On tick, it reads brain Space topology directly from the universe graph (no decryption needed for structure).
- It retrieves encrypted content/synthesis/embedding fields for nodes in the brain Space.
- It decrypts them using the per-Space symmetric key (retrieved from its own `HAS_ACCESS` link, decrypted with its private key).
- Physics laws execute on the decrypted data.
- Any new nodes or updated content are re-encrypted before being written back.
- An external observer querying the universe graph can see the brain's topology but cannot read any content.

### B10: Cross-Space Energy Propagation

**When** a Moment in one Space is linked to an Actor who is also in other Spaces, **then** energy propagates through the Actor node into other connected contexts.

**Observable effects:**
- Moment in Space A energizes Space A (via link) and Actor X (via link).
- Actor X has `HAS_ACCESS` links to Spaces B and C.
- Energy from Actor X spills over (Law 2) into the `HAS_ACCESS` links.
- Spaces B and C receive propagated energy.
- This models cross-context awareness: a commit in a repo can energize the developer's presence in a chat channel.
- Propagation is governed by link properties -- high-weight `HAS_ACCESS` links propagate more energy than low-weight ones.

### B11: Trust Accumulation on Links

**When** two Actors repeatedly interact successfully within shared Spaces, **then** the trust dimension on their mutual link increases.

**Observable effects:**
- Co-activation reinforcement (Law 5) fires on their mutual link each time both are active in the same Space.
- Consolidation (Law 6) increases the link's weight (and trust grows with weight for positive interactions).
- The trust value on the link is in [0, 1].
- Actor reputation is computed on demand: `reputation(A) = sum(link.trust * link.weight) / sum(link.weight)` across all inbound links.
- No transitive trust at L3. A trusting B and B trusting C does not create A-trusting-C. That inference happens only in L1 brains.

### B12: Space Discovery

**When** an Actor queries for available Spaces (e.g., "what channels can I join?"), **then** the universe graph returns Spaces the Actor could potentially access.

**Observable effects:**
- Public Spaces (those without encryption, or with open `HAS_ACCESS` policies) are discoverable by all.
- Private Spaces are invisible unless the Actor has a path to them (e.g., invited via another member).
- Brain Spaces are never discoverable by other Actors -- they exist only in the Actor's own access tree.
- Discovery does NOT reveal encrypted content. Only Space name, type hint, and topology (number of members, activity level) are visible.

---

## ANTI-BEHAVIORS

### A1: Property-Based Access

Access MUST NOT be determined by checking a property on the Space node (e.g., `access: ["user_1", "user_2"]`). If you find code that reads a list of authorized users from a node property instead of querying `HAS_ACCESS` links, it is wrong.

### A2: Type-Based Routing

No algorithm or code path MUST branch on `space_type` value. If you find `if space.space_type == "discord_channel"` anywhere, it is wrong. Topological signals (which Actors, which bots, what link patterns) determine context.

### A3: Separate Organization Graphs

Organizations MUST NOT get their own graph, database, or namespace. An organization is a Narrative node + a hall Space + `HAS_ACCESS` links, all within the single universe graph.

### A4: Unencrypted Brain Content

Brain Space content MUST NOT be stored in plaintext in the universe graph. If brain node `content`, `synthesis`, or `embedding` fields are readable without decryption, the encryption invariant is violated.

### A5: Stored Verb Labels on Links

At L3, link meaning MUST NOT be stored as a verb string (e.g., `relation: "collaborates_with"`). All semantics are computed from dimensions via the L3 Link Synthesis Grammar. If you find stored verb labels on L3 links, they must be removed.

### A6: Node-Level Trust

Trust MUST NOT be stored as a field on Actor nodes. If you find `actor.trust_score = 0.85`, it is wrong. Trust lives on links. Reputation is always computed from inbound link trust values.
