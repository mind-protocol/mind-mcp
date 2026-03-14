# PATTERNS -- Universe Graph

```
STATUS: DESIGNING
CREATED: 2026-03-13
UPDATED_BY: Force 1 (architect)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Universe_Graph.md
THIS:            ./PATTERNS_Universe_Graph.md
BEHAVIORS:       ./BEHAVIORS_Universe_Graph.md
ALGORITHM:       ./ALGORITHM_Universe_Graph.md
VALIDATION:      ./VALIDATION_Universe_Graph.md
SYNC:            ./SYNC_Universe_Graph.md
```

---

## DESIGN PHILOSOPHY

### Why a Single Universe Graph

The 4-layer model (L1 = citizen brain, L2 = organization, L3 = ecosystem, L4 = protocol) created a coordination problem: data lived in separate graphs per layer, requiring cross-graph joins for any query that spanned organizational boundaries. L2 in particular had no clear justification as a separate data store -- organizations are social constructs, not computational boundaries.

The insight: **everything is already in the same universe.** A discord message, a commit, a VR battle, and a financial transaction all happen in the same reality. They should live in the same graph. The boundaries between "my brain," "my org," and "the world" are access boundaries, not data boundaries.

The single universe graph eliminates L2 entirely. Organizations become Narratives (interpretive structures) with associated hall Spaces (context containers). The only layers that remain are:

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **L4 (Protocol)** | Canonical schema, registry, laws | `mind-protocol` repo |
| **L3 (Universe)** | Single graph per universe | One FalkorDB instance (e.g., `venezia`) |
| **L1 (Brain)** | Encrypted private Spaces within the universe graph | Same FalkorDB, content encrypted |

L1 is not a separate database. It is a set of encrypted Spaces inside the universe graph. The Actor's brain is a Space (or hierarchy of Spaces) with `HAS_ACCESS` granted only to that Actor. The topology is visible; the content is encrypted.

### Why Spaces (Not Channels, Rooms, or Repos)

A Space is the universal context container. It maps to every domain concept that means "a place where things happen":

| Domain | Space examples |
|--------|---------------|
| Chat | discord_general, telegram_group, whatsapp_thread |
| Code | github_mind_mcp, pr_1234 |
| VR/Games | tavern_ironhold, arena_bloodmoon |
| Physical | paris_france, office_14th_floor |
| Brain | manuele_self_model, manuele_working_memory |
| Organization | acme_corp_hall, engineering_dept |
| Economic | treasury_vault, liquidity_pool |

The Space concept absorbs every "container" type from every domain. We do NOT create separate node types for channels, rooms, repos, or addresses. They are all Spaces with different topological positions.

A Space can optionally carry a `space_type` string hint (e.g., `"discord_channel"`) for display purposes. But no algorithm reads this field. The distinction between a discord channel and a medieval tavern is entirely topological: which Actors have access, which bot services are linked, what Moments occur there.

### Why HAS_ACCESS Links

Previous models stored access as a property on nodes (`access: ["user_1", "user_2"]`) or in external ACL tables. Both create the same problem: access is not a graph relationship, so it cannot participate in graph physics, cannot be traversed, and cannot be visualized.

`HAS_ACCESS` is a standard `link` (same LinkBase as every other link) from Actor to Space, with these properties set:

| Property | Usage |
|----------|-------|
| `type` | `"has_access"` (free-form subtype on the link) |
| `hierarchy` | `-1` (Actor contains/owns the Space) or `0` (member) |
| `permanence` | `1.0` for ownership, lower for temporary access |
| `trust` | Trust level of this Actor within this Space |
| Role (on link content/synthesis) | `owner` / `admin` / `member` |
| Encrypted key (on link content) | Per-Space AES-256 key, encrypted with Actor's public key |

Because `HAS_ACCESS` is a graph link, it participates in normal graph operations:
- **Propagation (L2):** Activity in a Space energizes the `HAS_ACCESS` links to its members.
- **Co-activation (L5):** Actors who share Spaces get their mutual links strengthened.
- **Forgetting (L7):** Inactive `HAS_ACCESS` links decay -- if an Actor never visits a Space, the link weakens.
- **Crystallization (L10):** Dense actor-space interaction patterns can crystallize into narrative hubs.

### Hierarchical Access

Spaces can contain other Spaces. A `HAS_ACCESS` link to a parent Space grants access to all descendant Spaces (unless explicitly revoked). This is implemented through containment links (hierarchy = -1) between Spaces, not through stored permission inheritance.

Example:
```
acme_corp_hall (Space)
  |-- contains --> engineering (Space)
  |     |-- contains --> backend_team (Space)
  |     |-- contains --> frontend_team (Space)
  |-- contains --> marketing (Space)

Actor "alice" -- HAS_ACCESS --> acme_corp_hall  (role: admin)
```
Alice has access to engineering, backend_team, frontend_team, and marketing -- all derived from the single `HAS_ACCESS` link to `acme_corp_hall` plus the containment hierarchy.

### Why Organizations Are Narratives

An organization does not think. It does not run inference. It does not have drives or working memory. It is a story that people believe in.

In graph terms:
- An **Organization** is a `narrative` node (type: `"organization"`).
- It is `ABOUT` a hall Space (the organization's primary context container).
- Members have `HAS_ACCESS` links to the hall Space (and by hierarchy, to sub-Spaces).
- Members `BELIEVE` in the Narrative (link from Actor to Narrative, representing alignment with the org's values/mission).

This means:
- Creating an org = creating a Narrative + a Space + an initial `HAS_ACCESS` link (owner).
- Joining an org = creating a `HAS_ACCESS` link (member) to the hall Space + a `BELIEVE` link to the Narrative.
- Org reputation = reputation of the Narrative node (aggregated inbound trust).
- Org dissolution = all `HAS_ACCESS` links decay below threshold via Law 7.

No special organization code. No organization table. No org-specific API. Organizations emerge from the same primitives as everything else.

### Why Encrypted Brains

A brain is an Actor's private cognitive Space. It contains memories, values, desires, processes -- the full L1 cognitive substrate. This data must be:

1. **Private** -- Other Actors cannot read the content.
2. **Operational** -- Physics must still work on it (propagation, decay, crystallization).
3. **Portable** -- The Actor must be able to move their brain to a different universe instance.

Solution: **visible topology, encrypted content.**

| What | Encrypted? | Why |
|------|-----------|-----|
| Node existence (id, node_type) | No | Physics needs to know nodes exist |
| Physics floats (weight, energy, stability) | No | Laws operate on these values |
| Link structure (node_a, node_b) | No | Propagation needs graph topology |
| Link floats (trust, friction, affinity) | No | Physics dimensions must be readable |
| Node `content` | Yes (AES-256) | Private thoughts, memories, values |
| Node `synthesis` | Yes (AES-256) | Embeddable summary of private content |
| Node `embedding` | Yes (AES-256) | Vector representation of private content |
| Link `synthesis` | Yes (AES-256) | Human-readable link description |
| Link `embedding` | Yes (AES-256) | Vector representation of link meaning |

Embedding encryption means semantic search within a brain requires the decryption key. An Actor's own MCP server holds the key and can search; the universe graph server cannot.

### Key Management Model

Two classes of keys:

**AI citizen keys:**
- Generated at citizen creation.
- Stored in `.keys/` directory within the citizen's runtime environment.
- Same key pair used for $MIND transactions (Solana wallet) and Space content decryption.
- The MCP server loads the private key at startup; it never leaves the runtime.

**Human partner keys:**
- Managed via wallet model (Chrome extension or mobile app).
- Same key pair for $MIND and Space decryption.
- The wallet signs decryption requests; the private key never leaves the device.

**Per-Space symmetric keys:**
- Each Space has one AES-256 symmetric key.
- This key is stored on every `HAS_ACCESS` link to that Space, encrypted with the authorized Actor's public key.
- Granting access = encrypting the Space key with the new Actor's public key and storing it on the new `HAS_ACCESS` link.
- Revoking access = removing the `HAS_ACCESS` link. The Space key should be rotated and re-encrypted for remaining members if revocation is adversarial.

### Link Dimensions at L3 (No relation_kind)

L1 uses 14 `relation_kind` values (remembers, cares_about, wants, etc.) because a brain needs cognitive categories. The universe has no cognition. At L3:

- `relation_kind` is always `null`.
- All link semantics emerge from the mathematical dimensions: weight, trust, friction, affinity, aversion, polarity, hierarchy, permanence.
- Human-readable meaning is computed via the L3 Link Synthesis Grammar (see `docs/schema/GRAMMAR_L3_Link_Synthesis.md`).

The Plutchik emotion axes (joy_sadness, trust_disgust, fear_anger, surprise_anticipation) are always `0.0` at L3. The universe has no feelings. Each L1 brain colors the universe differently through its own emotional state.

### Three Layers, Not Four

The architecture collapses from 4 layers to 3:

```
L4: Protocol (schema, registry, laws)
    |
    v
L3: Universe Graph (one per universe, e.g., "venezia")
    |
    |-- Public Spaces (channels, repos, worlds, addresses)
    |-- Organization Narratives (+ hall Spaces)
    |-- Encrypted Brain Spaces (private, per-Actor)
    |
    v
L1: Cognitive Engine (21 laws, drives, working memory)
    Operates ON the brain Spaces within L3
    Uses decrypted content for inference
```

L2 is gone. Organizations are Narratives. Access control is link-based. The coordination layer is the graph itself.

---

## SCOPE

### What Is In Scope

- Universe graph structure (single FalkorDB graph per universe)
- Space model (creation, hierarchy, containment)
- `HAS_ACCESS` link-based access control
- Organization-as-Narrative pattern
- Encrypted brain Spaces
- Key management (AI keys, human keys, per-Space symmetric keys)
- Macro-crystallization (Law 10 at L3 scale)
- Link dissolution (Law 7 for self-management)
- L3 link dimensions (trust, friction, affinity, aversion -- no relation_kind)
- L3 physics law subset (L2, L3, L5, L6, L7, L10)

### What Is Out of Scope

- L1 cognitive engine implementation (Force 5)
- L1 physics laws not applicable at L3 (L1, L4, L8, L9, L11-L18)
- $MIND economic transactions (Force 2)
- Trust mechanics and value creation taxonomy (Force 4)
- Human partner data integration (Force 3)
- Solana blockchain integration
- Client applications (Chrome extension, mobile app)
- Migration tooling from existing `mind_mcp` graph (flagged as open question)

---

## DESIGN RATIONALE SUMMARY

| Decision | Why |
|----------|-----|
| Single graph per universe | Eliminates cross-graph coordination; one source of truth |
| Spaces as universal containers | Absorbs every domain's "context" concept; no new node types |
| HAS_ACCESS as graph link | Access participates in physics; auditable; revocable; no external ACL |
| Hierarchical access via containment | One link grants tree of access; no permission inheritance tables |
| Organizations as Narratives | No special type; social constructs use social primitives |
| Encrypted content, visible topology | Physics operates without decryption; privacy preserved |
| No relation_kind at L3 | Universe has no cognition; semantics emerge from dimensions |
| No space_type taxonomy | Topology determines context; no categorical maintenance burden |
| Same physics laws, different thresholds | One engine, two scopes; parameters tuned per context |
