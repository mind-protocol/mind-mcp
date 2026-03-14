# mind-mcp — Mapping: Translation to mind Schema

```
STATUS: STABLE
CREATED: 2025-12-26
UPDATED: 2026-03-13
```

---

## PURPOSE

Translates domain vocabulary (TAXONOMY) to the universal mind schema.
All modules reference this. New mappings are proposed in VOCABULARY.md, then merged here.

---

## MIND UNIVERSAL SCHEMA

The schema is **FIXED**. We map TO it, never extend it.

**Reference:** `docs/schema/schema.yaml`

### Key Points

- **node_type** (enum): `actor`, `moment`, `narrative`, `space`, `thing` — 5 types, universal
- **link type**: `link` — ONE type, all semantics in properties
- **Subtypes**: via `type` field (string, nullable) — free text, not an enum
- **No custom node types** at any layer — L1, L3, or anywhere else
- **No custom link types** — `relation_kind` is an optional property on LinkBase, not a new type

### Layer Differences

| Aspect | L1 (Brain) | L3 (Universe) |
|--------|------------|----------------|
| **Node types** | 5 universal (7 cognitive types MAP to them) | 5 universal only |
| **relation_kind** | 14 cognitive subtypes (nullable) | Always null |
| **Plutchik axes** | Active (joy_sadness, etc.) | Always 0.0 |
| **space_type** | N/A (no spaces in brain) | Free text, optional, never filtered |
| **Link semantics** | From relation_kind + dimensions | From dimensions ONLY |
| **Trust** | On links (limbic coloring) | On links (structural reliability) |
| **Physics laws** | 21 laws (18 core + 3 deferred) | 6 laws (L2, L3, L5, L6, L7, L10) |

### Backend Notes

| Backend | node_type | Subtype |
|---------|-----------|---------|
| FalkorDB | `node_type` field | `type` field |
| Neo4j | Node label | `type` field |

### Why No Custom Fields

- mind never does Cypher queries for filtering
- All retrieval is embedding-based
- `synthesis` = embeddable summary (for search)
- `content` = full prose/details (for display)
- Link meaning is computed from 13 dimensional floats, never stored as a verb

---

## L3 RULES — No Taxonomy, No Prescribed Types

These rules are **non-negotiable** and govern all L3 mappings:

### 1. No space_type taxonomy

`space_type` is a free optional string field on Space nodes. It exists as a hint
for display purposes only. **No algorithm, formula, or physics law reads space_type
for branching.** There is no enum, no prescribed values, no validation against a list.

Examples of valid space_type values: `"discord_channel"`, `"vr_room"`, `"github_repo"`,
`"physical_address"`, `"game_zone"`, `"medieval_tavern"`, `null`.

### 2. No relation_kind at L3

`relation_kind` is always null at L3. The 14 L1 cognitive subtypes (remembers,
cares_about, wants, etc.) are brain-internal vocabulary. The universe graph does
not have cognition.

### 3. Link semantics from math

All link meaning at L3 is computed from the 13 active dimensions:
weight, energy, stability, recency, polarity, hierarchy, permanence,
valence, ambivalence, trust, friction, affinity, aversion.

The grammar is documented in `docs/schema/GRAMMAR_L3_Link_Synthesis.md`.
The verb is never stored. It is always computed on read.

### 4. No emotions at L3

The Plutchik axes (joy_sadness, trust_disgust, fear_anger, surprise_anticipation)
are always 0.0 at L3. All affect lives in L1 — each brain colors the same
universe link differently.

### 5. Trust on links only

There is no trust field on nodes. Actor reputation is computed by aggregating
inbound link trust values: `reputation(A) = Σ(link.trust × link.weight) / Σ(link.weight)`.
This is never stored.

---

## NODE MAPPINGS

### L3 Universe Mappings

#### Person / AI Citizen / Service / Company -> actor

```yaml
domain_term: "Any entity that can initiate action"
maps_to:
  node_type: actor
  subtype: null  # Or free text like "citizen", "human", "bot", "service"

synthesis_template: |
  {name} — {brief role or description}

content_includes:
  - Public profile information
  - Capabilities or service description
  - External identifiers (not credentials)

example:
  domain: "AI citizen Manuele Mente"
  synthesis: "Manuele Mente — AI citizen of Mind Protocol"
  content: |
    First citizen of Mind Protocol. Founded by Nicolas Music.
    Capabilities: conversation, code, analysis.
```

#### Event / Action / Transaction / Commit -> moment

```yaml
domain_term: "Any discrete event in the universe"
maps_to:
  node_type: moment
  subtype: null  # Or free text like "commit", "transfer", "meeting", "battle"

synthesis_template: |
  {name} — {what happened} ({when})

content_includes:
  - Full event description
  - Participants referenced
  - Amounts, hashes, metadata
  - Timestamps (started_at_s, completed_at_s)

example:
  domain: "$MIND transfer of 50 tokens"
  synthesis: "Transfer — 50 $MIND from citizen_a to citizen_b (2026-03-13)"
  content: |
    50 $MIND transferred. TX hash: abc123. Reason: payment for code review.
```

#### Project Vision / Roadmap / Lore / Trend -> narrative

```yaml
domain_term: "Any public interpretive structure"
maps_to:
  node_type: narrative
  subtype: null  # Or free text like "vision", "lore", "trend", "report"

synthesis_template: |
  {name} — {core thesis or summary}

content_includes:
  - Full narrative text
  - Supporting evidence references
  - Crystallization source (if auto-generated from moments)

example:
  domain: "Q1 2026 Development Phase (crystallized)"
  synthesis: "Q1 2026 Development Phase — 300 commits consolidated, core runtime built"
  content: |
    Crystallized from 300 commit moments over Jan-Mar 2026.
    Key outcomes: MCP server, citizen management, orchestrator, bridges.
    Hub weight: 12.4 (inherited from constituent moments).
```

#### Channel / World / Room / Repo / Address -> space

```yaml
domain_term: "Any context container"
maps_to:
  node_type: space
  subtype: null
  space_type: "free text, optional"  # NOT an enum, NOT filtered anywhere

synthesis_template: |
  {name} — {purpose or description}

content_includes:
  - Description of the space
  - Access rules (described, not enforced by space_type)
  - Metadata (URL, coordinates, config)

example:
  domain: "Discord #general channel"
  synthesis: "general — Main discussion channel for Mind Protocol"
  content: |
    Discord channel. Public. Primary channel for community discussion.
  space_type: "discord_channel"  # Free text hint, never filtered
```

#### Tool / Token / Document / Artifact -> thing

```yaml
domain_term: "Any entity, object, or abstraction"
maps_to:
  node_type: thing
  subtype: null  # Or free text like "token", "document", "tool", "artifact"

synthesis_template: |
  {name} — {what it is}

content_includes:
  - Description
  - URI if applicable
  - Properties, specifications

example:
  domain: "$MIND token"
  synthesis: "$MIND — Native token of Mind Protocol ecosystem"
  content: |
    Solana Token-2022. Used for all economic transactions.
    Supply managed by metabolic economics.
```

### L1 Brain Mappings (Reference)

L1 uses 7 cognitive types that map to the 5 universal types:

| Cognitive Type | Universal Type | type field |
|----------------|----------------|------------|
| memory | moment | null |
| concept | thing | null |
| narrative | narrative | null |
| value | narrative | "value" |
| process | narrative | "process" |
| desire | narrative | "desire" |
| state | actor | (transient property) |

See `docs/schema/schema.yaml` section "L1 COGNITIVE TYPES" for full details.

---

## LINK MAPPINGS

### L3 Link Mappings — Dimensions Only

At L3, links are mapped by setting dimensional values. **No relation_kind. No stored verb.**
The human-readable label is computed by the L3 Link Synthesis Grammar.

#### Containment (parent contains child)

```yaml
domain_relationship: "X contains Y (world contains zone, org contains team, repo contains file)"
maps_to:
  hierarchy: -0.7 to -1.0    # Strong containment
  polarity: [0.7, 0.3]       # Parent acts on child
  permanence: 0.8 to 1.0     # Structural, not temporary
  trust: 0.5 to 0.8          # Reliable structural relationship
  friction: 0.0 to 0.2       # Low friction (natural nesting)
computed_verb: "encompasses" or "contains"
```

#### Ownership (actor owns thing)

```yaml
domain_relationship: "Actor owns Thing"
maps_to:
  hierarchy: -0.5 to -0.8    # Actor contains/possesses
  polarity: [0.8, 0.1]       # Strong a→b
  permanence: 0.7 to 1.0     # Usually permanent
  trust: varies               # How reliable the ownership claim is
computed_verb: "owns" or "holds"
```

#### Collaboration (actor works with actor)

```yaml
domain_relationship: "Two actors collaborate"
maps_to:
  hierarchy: -0.1 to 0.1     # Flat, peer relationship
  polarity: [0.5, 0.5]       # Balanced bilateral
  trust: 0.3 to 0.9          # Builds over time via L5+L6
  affinity: 0.4 to 0.9       # Natural co-activation
  friction: 0.0 to 0.3       # Low friction for good collaborations
computed_verb: "trusted collaborator of" or "partner of"
```

#### Authorship (actor created moment/thing)

```yaml
domain_relationship: "Actor performed/created an event or artifact"
maps_to:
  hierarchy: 0.2 to 0.5      # Actor elaborates (is source of)
  polarity: [0.8, 0.2]       # Strong a→b
  permanence: 0.8 to 1.0     # Historical fact
  valence: 0.2 to 0.5        # Constructive
computed_verb: "performed" or "created"
```

#### Economic Transfer (actor -> actor via moment)

```yaml
domain_relationship: "$MIND transfer"
maps_to:
  hierarchy: 0.0              # Flat
  polarity: [0.9, 0.05]      # Strongly directional
  permanence: 1.0             # Irrevocable on-chain
  trust: varies               # Based on relationship history
  valence: 0.3                # Constructive (value exchange)
computed_verb: "acts on" or "transferred to" (with Actor->Actor override)
```

#### Access (actor can access space)

```yaml
domain_relationship: "Actor has access to Space"
maps_to:
  hierarchy: 0.3 to 0.5      # Actor is subordinate to space rules
  polarity: [0.6, 0.3]       # Actor acts on space (enters, reads)
  permanence: varies          # 0.3 for visitor, 0.9 for inhabitant
  trust: varies               # Permission level
computed_verb: "inhabits" or "visits" (based on permanence)
```

#### Causation (moment -> moment)

```yaml
domain_relationship: "Event A caused/triggered Event B"
maps_to:
  hierarchy: -0.3 to 0.3     # Roughly peer (or A contains B context)
  polarity: [0.8, 0.2]       # A → B directional
  permanence: 0.7 to 1.0     # Factual causation
  valence: varies             # Constructive or destructive cause
computed_verb: "caused" or "triggered"
```

#### Crystallization (hub -> constituent)

```yaml
domain_relationship: "Narrative hub crystallized from moments"
maps_to:
  hierarchy: -0.9             # Hub contains constituents
  polarity: [0.8, 0.2]       # Hub acts on constituent
  permanence: 1.0             # Structural fact
  trust: 0.7                  # Reliable (math-derived)
  relation_kind: null         # Even at L1 this uses "contains"/"abstracts"
computed_verb: "encompasses" (hub→constituent) or "is a detail of" (constituent→hub)
```

### L1 Link Mappings (Reference)

At L1, links may use `relation_kind` from the 14 cognitive subtypes:
`remembers`, `relates_to`, `cares_about`, `prefers`, `follows_process`,
`supports`, `conflicts_with`, `wants`, `evokes`, `projects_toward`,
`habitually_checks`, `regulates`, `contains`, `abstracts`.

These are nullable and only used in L1 brain contexts. See `docs/schema/schema.yaml`
section "LINK SCHEMA" for full details.

---

## COMMON PATTERNS

### Documentation -> Narrative

```yaml
doc_type: "PATTERNS.md"
maps_to:
  node_type: narrative
  subtype: pattern
synthesis_template: "{module} patterns — {brief description}"
```

### Code Directory -> Space

```yaml
code_pattern: "src/{module}/"
maps_to:
  node_type: space
  subtype: null  # NOT "module" as a type — free text only
  space_type: "code_directory"  # Free text hint
synthesis_template: "{module} — {purpose}"
```

### Source File -> Thing

```yaml
file_pattern: "*.py"
maps_to:
  node_type: thing
  subtype: null  # Or "file" as free text
synthesis_template: "{filename} — {primary responsibility}"
```

### Git Commit -> Moment

```yaml
domain_pattern: "git commit"
maps_to:
  node_type: moment
  subtype: null  # Or "commit" as free text
synthesis_template: "{hash_short} — {commit_message}"
content_includes:
  - Full commit message
  - Changed files list
  - Author reference
```

### $MIND Transfer -> Moment

```yaml
domain_pattern: "$MIND transaction"
maps_to:
  node_type: moment
  subtype: null  # Or "transfer" as free text
synthesis_template: "Transfer — {amount} $MIND {from} → {to} ({date})"
content_includes:
  - Amount
  - Sender and receiver references
  - Transaction hash
  - Reason/memo
```

---

## ANTI-PATTERNS

Things that are **wrong** and must not appear in mappings:

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|----------------|------------------|
| Creating a new node_type "organization" | Schema has 5 types, period | Map to `narrative` (orgs are social constructs, not agents -- see F1 Universe Graph: "Why Organizations Are Narratives") |
| Using space_type in a formula | space_type is display-only | Use graph topology (links, hierarchy) for algorithmic branching |
| Storing "employs" as relation_kind at L3 | relation_kind is null at L3 | Set hierarchy=-0.6, permanence=0.8 — grammar computes "employs" |
| Adding trust field to actor node | Trust lives on links only | Compute reputation from inbound link trust values |
| Creating link type "transfer" | One link type: `link` | Create a moment node for the transfer event, link it to actors |
| Using Plutchik axes at L3 | L3 has no emotions | Leave at 0.0; affect is L1 brain interpretation |

---

## POINTERS

- Schema v2.0: `docs/schema/schema.yaml`
- L1 Link Grammar: `docs/schema/GRAMMAR_Link_Synthesis.md`
- L3 Link Grammar: `docs/schema/GRAMMAR_L3_Link_Synthesis.md`
- L3 Universe section: `docs/schema/schema.yaml` (search "L3 UNIVERSE GRAPH")
