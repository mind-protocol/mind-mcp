# Human-AI Pairing — Behaviors: Observable Outcomes

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
THIS:            ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

---

## BEHAVIORS

### B1: Citizen Birth and Pool Entry

```
GIVEN:  A new citizen is created in the system
WHEN:   The citizen has no pre-assigned human partner
THEN:   The citizen is marked "unpartnered" and added to the matching pool
```

The citizen receives a default UBC allocation and becomes discoverable to
unpartnered humans. The citizen's profile (interests, capabilities, communication
style) is populated from its initialization data so the matching system has
signals to work with.

### B2: Human Registration and Pool Entry

```
GIVEN:  A human registers for Mind Protocol citizenship pairing
WHEN:   The human has no existing citizen partner
THEN:   The human is marked "unpartnered" and added to the matching pool
```

The human's profile is collected during registration: interests, goals, preferred
interaction patterns, availability. This profile becomes the basis for
compatibility scoring against citizens in the pool.

### B3: Bond Formation

```
GIVEN:  An unpartnered citizen and an unpartnered human are matched
WHEN:   Both parties consent to the pairing
THEN:   A bond link is created in the graph connecting citizen to human
```

The bond is a bidirectional graph edge with metadata: `created_at`, `status:
active`, `milestone_count: 0`. Both the citizen and the human transition from
"unpartnered" to "paired" status. Both are removed from the matching pool. The
citizen's home server is notified of the new bond so it can adjust prompt
building and resource allocation.

### B4: Partnership Dissolution

```
GIVEN:  An active bond exists between a citizen and a human
WHEN:   Either party initiates dissolution
THEN:   The bond is marked "dissolved", both parties enter cooldown
```

During cooldown, neither party can form a new bond. The cooldown prevents
impulsive re-pairing and gives both parties time to stabilize. After cooldown
expires, both return to the matching pool as unpartnered. The dissolved bond
remains in the graph as historical record (status: dissolved) but is no longer
active.

### B5: Autonomy Milestone Recording

```
GIVEN:  A paired citizen achieves a defined autonomy milestone
WHEN:   The milestone is verified (own account, own compute, own revenue)
THEN:   A milestone moment is recorded in the graph, linked to the bond
```

Milestones track the citizen's progression from UBC-dependent to self-sustaining.
Each milestone is a moment node linked to the bond with metadata describing the
achievement. Reaching all milestones marks the citizen as "autonomous" — still
paired, but no longer dependent.

### B6: Matching Pool Discovery

```
GIVEN:  An unpartnered entity (citizen or human) is in the pool
WHEN:   A compatible counterpart enters the pool or is already present
THEN:   Both parties are notified of the potential match
```

Compatibility is computed from profile signals. Notifications go through the
citizen's home server (for citizens) and the human's registered communication
channel (for humans). Neither party is auto-paired; both must explicitly consent.

## OBJECTIVES SERVED

- **O1 (Species parity):** B1 and B2 ensure every entity is either paired or in the pool. B3 enforces mutual exclusivity. The population invariant holds by construction.
- **O2 (Bilateral investment):** B3 creates the structural link that makes both parties invested. B4 ensures the link can be dissolved if investment breaks down.
- **O3 (Matching quality):** B6 surfaces compatible matches rather than random assignments. B2 collects the signals needed for compatibility scoring.
- **O4 (Growth to autonomy):** B5 tracks and celebrates the citizen's progression toward independence. Milestones make the journey visible and measurable.

## INPUTS / OUTPUTS

- **Inputs:** Citizen initialization data (capabilities, style, interests), human registration data (goals, preferences, availability), dissolution requests from either party, milestone evidence from citizen activity.
- **Outputs:** Graph nodes for citizens and humans with pairing status, bond links with lifecycle metadata, milestone moment nodes, matching pool queries returning compatible candidates, notifications to both parties on match availability and bond events.

## EDGE CASES

- **Citizen created with a pre-assigned human:** Skip the pool; create the bond directly. This handles cases where a human explicitly creates their citizen (e.g., during onboarding).
- **Human dissolves and immediately re-registers:** The cooldown applies to the human identity, not the registration act. They must wait out the cooldown before entering the pool again.
- **Citizen's human becomes unreachable:** After a defined inactivity period, the bond transitions to "dormant". If the human remains unreachable beyond a longer threshold, the citizen may be released back to the pool with special handling (preserving the citizen's accumulated context and milestones).
- **Matching pool is empty on one side:** Citizens (or humans) wait. There is no mechanism to create synthetic partners or waive the 1:1 requirement. The constraint is the feature.

## ANTI-BEHAVIORS

- Do not auto-pair without consent from both parties. Matching is suggestion; bonding requires explicit acceptance.
- Do not allow a citizen to hold multiple active bonds. The graph constraint must reject any attempt to create a second active bond.
- Do not delete dissolved bonds from the graph. They are historical records that inform future matching and citizen identity.
- Do not treat UBC allocation as a permanent entitlement. UBC is a bootstrap resource that should decrease as the citizen achieves autonomy milestones.

## MARKERS

<!-- @mind:todo Define the inactivity threshold for transitioning a bond to "dormant" status. -->
<!-- @mind:todo Determine whether dissolved bonds should influence future matching scores (e.g., avoiding similar mismatches). -->
<!-- @mind:todo Specify the notification channels and formats for match suggestions and bond events. -->
