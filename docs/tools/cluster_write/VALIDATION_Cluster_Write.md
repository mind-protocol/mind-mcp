# Cluster Write — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Cluster_Write.md
PATTERNS:        ./PATTERNS_Cluster_Write.md
BEHAVIORS:       ./BEHAVIORS_Cluster_Write.md
THIS:            VALIDATION_Cluster_Write.md (you are here)
ALGORITHM:       ./ALGORITHM_Cluster_Write.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cluster_Write.md
HEALTH:          ./HEALTH_Cluster_Write.md
SYNC:            ./SYNC_Cluster_Write.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose?

These are the value-producing invariants — the things that make cluster_write worth building over sequential graph_write calls.

---

## INVARIANTS

### V1: Every Cluster Has a Moment

**Why we care:** The Moment is the anchor of the cluster. Without it, actors and things float unconnected — the "what happened" is missing. A cluster without a Moment is structurally meaningless.

```
MUST:   Every successful cluster_write produces exactly one Moment node with content, embedding, and timestamp
NEVER:  A cluster_write returns success without a Moment node existing in the graph
```

### V2: No Orphaned Nodes from Partial Writes

**Why we care:** If the Moment is created but the actor links fail, the graph has a dangling Moment that pollutes search and confuses the physics. If actors are created but the Moment fails, the graph has phantom actors. Partial writes are worse than no writes.

```
MUST:   If any node or link creation fails during Phase 4, all nodes and links created in this cluster are removed
NEVER:  A failed cluster_write leaves nodes or links in the graph
```

### V3: Platform-Verified Entities Never Create Duplicates

**Why we care:** If telegram_user_id=12345 creates a new actor every time they send a message, the graph fills with duplicate identities. The citizen's social graph becomes incoherent — "who is this person?" has multiple conflicting answers. Platform verification is ground truth; dedup on it must be absolute.

```
MUST:   An actor with a matching platform_id (same platform + same ID) is always reused, never duplicated
NEVER:  Two actor nodes exist with the same {platform}_id value
```

### V4: Confidence Is Reflected in Link Weight

**Why we care:** If a confirmed entity (platform-verified) and an unconfirmed entity (text mention) have the same link weight, the physics cannot distinguish them. Co-activation (L5) would reinforce both equally, even though one is ground truth and the other is a guess. The initial weight must encode the confidence so the physics starts from the right place.

```
MUST:   Links from confirmed entities have weight >= 1.0
MUST:   Links from unconfirmed entities have weight <= 0.5
NEVER:  An unconfirmed entity link has higher weight than a confirmed entity link
```

### V5: The Caller Is Always Linked as Creator

**Why we care:** Every Moment must have provenance — who created it. Without a CREATED link from the calling citizen to the Moment, the Moment has no author. This breaks trust computation (who said this?), narrative tracking (what did this citizen do?), and the L5/L6 co-activation that builds the citizen's relationship with their own memories.

```
MUST:   Every cluster_write produces a CREATED link from the calling citizen to the Moment
NEVER:  A Moment exists without a CREATED link to its author
```

### V6: URLs Produce Thing Nodes Deterministically

**Why we care:** A URL is an unambiguous identifier. "https://cesai.org/paper.pdf" refers to exactly one resource. If the same URL appears twice, it must resolve to the same Thing node. If different URLs create the same Thing node, the graph confuses distinct resources.

```
MUST:   The same URL always produces the same Thing node ID (deterministic: thing:url:{domain}:{path_hash})
MUST:   Different URLs always produce different Thing node IDs
NEVER:  Two Thing nodes exist for the same URL
```

### V7: Content Analysis Runs Before Any Write

**Why we care:** If writes happen before analysis completes, entities extracted late cannot be linked to the already-written Moment. The pipeline order (pre-compute → analyze → suggest → write) is not just procedural — it is a correctness requirement. Moving writes before analysis produces incomplete clusters.

```
MUST:   Phase 4 (Write) only executes after Phase 2 (Analyze) has completed
MUST:   All EntityCandidates are resolved before the first graph write
NEVER:  A node is written to the graph before entity analysis is complete
```

### V8: Suggestions Contain Enough Context for Fast Decisions

**Why we care:** If the suggestion says "Florent — match found" without showing which Florent, the citizen must re-search to decide. The suggestion must contain the match's SID, handle, and last activity so the citizen can decide in under 5 seconds.

```
MUST:   Each suggestion with a match includes: node_id, name, handle, SID, last_active, match_method, match_score
NEVER:  A suggestion presents a match without enough context for the citizen to confirm or reject it
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Every cluster has its anchor — the Moment | CRITICAL |
| V2 | Graph integrity — no pollution from failed writes | CRITICAL |
| V3 | Identity coherence — platform-verified actors are unique | CRITICAL |
| V4 | Physics gets accurate initial conditions from confidence | HIGH |
| V5 | Moment provenance — every Moment has an author | HIGH |
| V6 | URL determinism — same URL = same Thing, always | HIGH |
| V7 | Pipeline order — analysis before writes | HIGH |
| V8 | Suggestion quality — citizen can decide fast | MEDIUM |

---

## MARKERS

<!-- @mind:todo V2 rollback mechanism needs design — FalkorDB transaction support vs manual cleanup -->
<!-- @mind:todo V4 exact weight values (1.0 vs 0.5) need validation against physics behavior -->
<!-- @mind:escalation V3 uniqueness: should we enforce this at the FalkorDB index level (UNIQUE constraint on platform_id) or at the application level? -->
