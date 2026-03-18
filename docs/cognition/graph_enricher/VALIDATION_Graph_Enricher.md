# Graph Enricher — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Graph_Enricher.md
PATTERNS:        ./PATTERNS_Graph_Enricher.md
BEHAVIORS:       ./BEHAVIORS_Graph_Enricher.md
THIS:            VALIDATION_Graph_Enricher.md (you are here)
ALGORITHM:       ./ALGORITHM_Graph_Enricher.md
IMPLEMENTATION:  ./IMPLEMENTATION_Graph_Enricher.md
HEALTH:          ./HEALTH_Graph_Enricher.md
SYNC:            ./SYNC_Graph_Enricher.md
```

---

## PURPOSE

**Validation = what we care about being true.**

The graph enricher populates the L3 universe with entities extracted from text. If it fails, the graph is either blind (missing entities), polluted (ghost duplicates), or lying (wrong entity types, false merges). Each invariant below protects a property that, if violated, corrupts the citizen's understanding of the world.

---

## INVARIANTS

### V1: Every Message Produces a Structural Record

**Why we care:** The structural record (Moment + Actor + Space + links) is the foundation for all enrichment. If the base record is missing, no entity extraction can happen. The citizen has no memory of the event.

```
MUST:   Every call to on_message() with valid parameters creates at minimum:
        1 Moment node, 1 Actor node (MERGE), 1 Space node (MERGE),
        and the 3 structural links (presence, occurred_in, created).
NEVER:  A message event passes through the enricher without creating any graph state.
```

### V2: Pattern-Matched Entities Are Always Confirmed

**Why we care:** URLs, $tokens, and explicitly @mentioned handles are deterministic extractions. There is no uncertainty. Marking them as anything other than "confirmed" would incorrectly suggest they need review, wasting human attention and delaying their integration into context assembly.

```
MUST:   Every URL produces a Thing(status="confirmed").
        Every $TOKEN produces a Thing(status="confirmed").
        Every @handle match links to an existing or newly MERGED Actor.
NEVER:  A regex-matched entity is created with status="unconfirmed".
```

### V3: LLM-Extracted Entities Start as Unconfirmed

**Why we care:** LLM extraction is inherently uncertain. Even at high confidence, the model might hallucinate a name or misidentify an entity type. Creating confirmed nodes from LLM output would inject unverified facts into the graph that downstream systems treat as ground truth.

```
MUST:   Every entity created from Gemini extraction has status="unconfirmed"
        (unless it matches an existing confirmed node with similarity > 0.95).
NEVER:  An LLM-extracted entity is created with status="confirmed" without
        deterministic verification (platform_id match, email match, etc.).
```

### V4: Platform Handle Uniqueness Enforced

**Why we care:** A platform_id (telegram_id, discord_id, etc.) uniquely identifies a person on that platform. If two Actor nodes have the same telegram_id, they are the same person. Allowing duplicates means the graph has two representations of one person, each accumulating separate weight and trust — fragmenting identity.

```
MUST:   At most one Actor node has any given (platform, platform_id) pair.
        If a second Actor is found with the same platform_id, auto-merge fires.
NEVER:  Two Actor nodes coexist with the same telegram_id, discord_id,
        or other platform-specific identifier.
```

### V5: Auto-Merge Preserves All Links

**Why we care:** When two Actor nodes are merged, every relationship (LINK edge) from the discarded node must be transferred to the surviving node. Losing links during merge means losing relationship history — trust scores, interaction counts, narrative connections all disappear.

```
MUST:   After auto-merge, every LINK that pointed to/from the discarded node
        now points to/from the surviving node. No links are deleted by merge
        (only the duplicate node itself is deleted).
NEVER:  A merge operation deletes LINK edges without transferring them.
```

### V6: Enrichment Never Blocks the Structural Write Path

**Why we care:** The structural enrichment (Step 1 — creating Moment/Actor/Space) is on the critical path for every message. If the enricher stalls here, bridges back up, messages are delayed, and the system becomes unresponsive. LLM extraction (tier 2) is the expensive step and must not block structural writes.

```
MUST:   on_message() completes the structural enrichment (Step 1) and tier 1
        pattern extraction (Step 3) before any tier 2 LLM call begins.
NEVER:  A Gemini API timeout or error prevents the Moment/Actor/Space
        nodes from being created.
```

### V7: No Entity Created Below Confidence Threshold

**Why we care:** Low-confidence extractions are noise. Creating nodes for uncertain entities pollutes the graph with garbage that must later be cleaned up. The confidence threshold (0.6) filters out the LLM's uncertain guesses.

```
MUST:   Only LLM extractions with confidence >= 0.6 proceed to entity resolution.
NEVER:  An entity with confidence < 0.6 creates a graph node.
```

### V8: Embedding Match Does Not Create False Merges

**Why we care:** A false merge collapses two distinct real-world entities into one node. This is worse than a duplicate because it conflates identities — trust, relationships, and context from person A contaminate person B. Auto-matching requires very high similarity (>0.95). Moderate similarity (0.85-0.95) creates a merge proposal but never auto-merges.

```
MUST:   Auto-match (linking to existing node without creating new) requires
        embedding similarity > 0.95.
MUST:   Similarity between 0.85 and 0.95 creates a merge proposal task
        without merging.
NEVER:  Two entities are auto-merged based on embedding similarity alone
        (deterministic signals required for auto-merge: platform_id, email, phone).
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Graph blind or corrupted |
| **HIGH** | Major value lost | Identity fragmented or data lost |
| **MEDIUM** | Partial value lost | Noise or latency degradation |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Every message produces a structural record | CRITICAL |
| V2 | Pattern-matched entities are always confirmed | HIGH |
| V3 | LLM-extracted entities start as unconfirmed | HIGH |
| V4 | Platform handle uniqueness enforced | HIGH |
| V5 | Auto-merge preserves all links | HIGH |
| V6 | Enrichment never blocks the structural write path | CRITICAL |
| V7 | No entity created below confidence threshold | MEDIUM |
| V8 | Embedding match does not create false merges | HIGH |

---

## MARKERS

<!-- @mind:todo Add tests for V4 (platform handle uniqueness + auto-merge trigger) -->
<!-- @mind:todo Add tests for V5 (link preservation during merge) -->
<!-- @mind:todo Add tests for V8 (threshold enforcement on embedding match) -->
<!-- @mind:escalation V6 enforcement: should tier 2 extraction be fully async (background task) or inline with timeout? -->
