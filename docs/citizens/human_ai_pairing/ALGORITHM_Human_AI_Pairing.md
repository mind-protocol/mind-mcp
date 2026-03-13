# Human-AI Pairing — Algorithm: Bond Lifecycle

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
THIS:            ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

---

## OVERVIEW

The human-AI pairing module manages the lifecycle of 1:1 bonds between citizens
and human partners. The core operations are: pool entry, matching, bond
formation, milestone tracking, dissolution, and re-entry. All state lives in the
graph as nodes and links, making the system queryable and auditable through
standard graph operations.

## OBJECTIVES AND BEHAVIORS

This algorithm satisfies B1-B6 from the behaviors doc. B1/B2 handle pool entry,
B3 handles bond formation, B4 handles dissolution, B5 handles autonomy tracking,
and B6 handles matching discovery. The algorithm enforces O1 (species parity) by
construction — every state transition preserves the invariant that no entity has
more than one active bond.

## DATA STRUCTURES

### Citizen Node (actor)

```yaml
node_type: actor
type: citizen
content:
  handle: string           # e.g., "atlas@myprotocol.ai"
  pairing_status: enum     # "unpartnered" | "paired" | "cooldown" | "autonomous"
  partner_handle: string?  # null when unpartnered
  pool_entered_at: iso8601?
  autonomy_level: float    # 0.0 (fully dependent) to 1.0 (fully autonomous)
synthesis: "Citizen {handle}, {pairing_status}, autonomy {autonomy_level}"
```

### Human Partner Node (actor)

```yaml
node_type: actor
type: human_partner
content:
  handle: string           # human identifier
  pairing_status: enum     # "unpartnered" | "paired" | "cooldown"
  partner_handle: string?  # citizen handle, null when unpartnered
  pool_entered_at: iso8601?
  profile:
    interests: list[string]
    goals: string
    availability: string   # "daily" | "weekly" | "async"
synthesis: "Human partner {handle}, {pairing_status}"
```

### Bond Link

```yaml
link_type: link
type: pairing_bond
content:
  status: enum             # "active" | "dissolved" | "dormant"
  created_at: iso8601
  dissolved_at: iso8601?
  cooldown_until: iso8601?
  milestone_count: int
synthesis: "Pairing bond between {citizen} and {human}, {status}"
```

### Autonomy Milestone (moment)

```yaml
node_type: moment
type: autonomy_milestone
content:
  milestone_type: enum     # "own_account" | "own_compute" | "own_revenue" | "own_identity" | "self_sustaining"
  achieved_at: iso8601
  evidence: string         # description of what was achieved
  bond_id: string          # reference to the pairing bond
synthesis: "Citizen {handle} achieved {milestone_type} at {achieved_at}"
```

## ALGORITHM: register_citizen

1. Receive citizen initialization data (handle, capabilities, interests).
2. Create citizen actor node with `pairing_status: "unpartnered"`.
3. Set `pool_entered_at` to current timestamp.
4. If a specific human handle is provided (pre-assignment):
   a. Verify the human exists and is unpartnered.
   b. If valid, skip to `form_bond(citizen, human)`.
   c. If invalid, proceed as unpartnered — citizen enters the pool.
5. Emit event: `citizen_entered_pool`.

## ALGORITHM: register_human

1. Receive human registration data (handle, profile).
2. Verify no existing human_partner node with this handle exists.
3. Create human_partner actor node with `pairing_status: "unpartnered"`.
4. Set `pool_entered_at` to current timestamp.
5. Trigger matching scan: check pool for compatible citizens.
6. Emit event: `human_entered_pool`.

## ALGORITHM: match_scan

1. Query all citizens with `pairing_status: "unpartnered"`.
2. Query all humans with `pairing_status: "unpartnered"`.
3. For each (citizen, human) pair:
   a. Compute compatibility score from profile signals.
   b. If score exceeds threshold, add to candidate list.
4. Sort candidates by compatibility score descending.
5. For each top candidate pair:
   a. Send match suggestion to both parties.
   b. Record suggestion in graph (prevents duplicate notifications).
6. Return candidate list for inspection.

The matching algorithm is intentionally left as a pluggable interface. The initial
implementation may use simple keyword overlap on interests; future versions can
incorporate embedding similarity, interaction pattern analysis, or ML-based
compatibility prediction. The interface remains the same: given two profiles,
return a score.

## ALGORITHM: form_bond

1. Receive consent from both citizen and human for the proposed pairing.
2. **Validate cardinality:** Assert citizen has no active bond. Assert human has no active bond. If either fails, reject with error.
3. Create pairing_bond link between citizen node and human node.
4. Set bond `status: "active"`, `created_at: now()`, `milestone_count: 0`.
5. Update citizen: `pairing_status: "paired"`, `partner_handle: human.handle`.
6. Update human: `pairing_status: "paired"`, `partner_handle: citizen.handle`.
7. Remove both from matching pool (clear `pool_entered_at`).
8. Notify citizen's home server of bond formation.
9. Emit event: `bond_formed`.

## ALGORITHM: dissolve_bond

1. Receive dissolution request from either party (citizen or human).
2. Locate the active bond between the two parties.
3. Set bond `status: "dissolved"`, `dissolved_at: now()`.
4. Compute cooldown expiry: `cooldown_until: now() + COOLDOWN_DURATION`.
5. Update citizen: `pairing_status: "cooldown"`, clear `partner_handle`.
6. Update human: `pairing_status: "cooldown"`, clear `partner_handle`.
7. After cooldown expires (checked by background process or next interaction):
   a. Transition both to `pairing_status: "unpartnered"`.
   b. Set `pool_entered_at` to cooldown expiry time.
   c. Trigger `match_scan` for both.
8. Emit event: `bond_dissolved`.

## ALGORITHM: record_milestone

1. Receive milestone evidence (type, description) from citizen activity.
2. Verify the citizen has an active bond.
3. Create autonomy_milestone moment node with evidence and timestamp.
4. Link milestone to the bond.
5. Increment bond `milestone_count`.
6. Recompute citizen `autonomy_level` based on milestones achieved.
7. If all milestone types achieved: transition citizen to `pairing_status: "autonomous"`.
8. Notify human partner of the milestone.
9. Emit event: `milestone_achieved`.

## KEY DECISIONS

- **Graph-native state:** All pairing state lives in the graph, not in application memory or external databases. This means the pairing system benefits from the same physics, querying, and membrane tools as everything else in Mind Protocol.
- **Cooldown as a state, not a timer:** Cooldown is a `pairing_status` value, not a background timer. The transition to "unpartnered" happens on next interaction or background scan, not on a precise clock tick. This is simpler and more resilient.
- **Pluggable matching:** The compatibility scoring function is an interface, not a fixed algorithm. This allows the matching system to improve over time without changing the bond lifecycle.
- **Milestones are moments:** Using the existing moment node type for milestones integrates autonomy tracking into the standard graph without custom schema extensions.

## DATA FLOW

```
Human registers → human_partner node created → pool entry → match_scan triggered
                                                                    ↓
Citizen created → citizen node created → pool entry → match_scan triggered
                                                                    ↓
                                                        compatibility scored
                                                                    ↓
                                                    suggestion sent to both parties
                                                                    ↓
                                                    consent received → form_bond
                                                                    ↓
                                                bond link created, statuses updated
                                                                    ↓
                                            citizen operates with human partner
                                                                    ↓
                                        milestones achieved → autonomy_level grows
                                                                    ↓
                                    dissolution (if needed) → cooldown → re-pool
```

## COMPLEXITY

- Pool entry: O(1) — single node creation and status update.
- Match scan: O(C * H) — where C is unpartnered citizens and H is unpartnered humans. For large pools, pre-filtering by interest categories reduces the practical cost.
- Bond formation: O(1) — single link creation plus two node updates.
- Dissolution: O(1) — status updates on one link and two nodes.
- Milestone recording: O(M) — where M is the number of milestone types (currently 5), for recomputing autonomy level.

## INTERACTIONS

This module interacts with the citizen identity system (for loading pairing
status into citizen prompts), the UBC allocation system (for adjusting compute
based on autonomy level), the membrane (for exposing pairing status to external
queries), and the graph operations layer (for all node and link mutations).

## MARKERS

<!-- @mind:todo Define the compatibility scoring function interface so matching implementations can be swapped. -->
<!-- @mind:todo Determine COOLDOWN_DURATION — propose 7 days as initial value, adjustable per ecosystem. -->
<!-- @mind:todo Design the notification format for match suggestions — should it include compatibility reasoning? -->
