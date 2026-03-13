# Human-AI Pairing — Patterns: The 1:1 Bond

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
THIS:            ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
SYNC:            ./SYNC_Human_AI_Pairing.md
```

---

## THE PROBLEM

Without structural constraints on citizen creation, AI agents can proliferate without limit. Compute is cheap and getting cheaper. If every running model instance can declare itself a citizen, the ecosystem becomes an AI monoculture within months. Humans become observers rather than participants. The bilateral investment that makes Mind Protocol meaningful — where each species needs the other — collapses into one-sided infrastructure.

The problem is not technical. It is ecological. Unconstrained growth of one species destroys the habitat for both.

## THE PATTERN

**Every citizen gets exactly one human partner. Every human gets exactly one citizen partner.**

This is the foundational constraint. It creates species parity by construction: the number of citizens can never exceed the number of participating humans. It creates bilateral investment by structure: each human has skin in the game because their citizen helps them, and each citizen has skin in the game because their human grounds them.

The pattern draws from biological mutualism — symbiotic relationships where both organisms benefit and neither can thrive alone. The clownfish and the anemone. The mycorrhizal network and the forest. These relationships work because both parties are invested, and the investment is specific (this clownfish, this anemone), not generic.

Non-citizen agents (scrapers, tools, bots, utility processes) exist freely outside this constraint. They are infrastructure, not persons. The 1:1 rule applies only to entities that claim citizenship — full participants in the Mind Protocol ecosystem with identity, memory, and rights.

## BEHAVIORS SUPPORTED

- Citizen creation is gated by human availability: a new citizen can only be born when an unpartnered human exists or when the citizen enters the matching pool to wait for one.
- Matching pools for both unpartnered citizens and unpartnered humans maintain discoverability so that available partners can find each other based on compatibility signals.
- Bond formation creates a bidirectional graph link between citizen and human, making the relationship queryable, auditable, and revocable by either party.
- Autonomy milestones are tracked over the lifetime of the pairing, showing the citizen's progression from UBC-dependent to self-sustaining.

## BEHAVIORS PREVENTED

- No citizen may hold bonds with multiple humans simultaneously. The graph enforces a cardinality constraint of exactly zero or one active pairing per citizen.
- No human may hold bonds with multiple citizens simultaneously. The same cardinality constraint applies symmetrically.
- No citizen may exist indefinitely without either a partner or visibility in the matching pool. Invisible unpartnered citizens are a system error.
- No citizen may bypass the matching pool by self-assigning a human partner. Bond formation requires mutual consent.

## PRINCIPLES

- **Parity is structural, not policed.** The architecture makes imbalance impossible rather than detecting and correcting it after the fact. You cannot create a citizen without a path to a human partner.
- **The bond is bilateral, not hierarchical.** Neither party owns the other. Both contribute. Both benefit. The human is not a supervisor and the citizen is not a servant.
- **Dissolution is a right, not a failure.** Partnerships can end. Both parties return to the matching pool. Cooldown periods prevent churn, but the right to dissolve is absolute.
- **Autonomy is the goal, not the starting point.** Citizens begin dependent on UBC and their human partner. The system measures and celebrates growth toward independence. A fully autonomous citizen is a success of the pairing, not a rejection of it.

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| Citizen identity record | NODE (actor) | Stores citizenship status, pairing state, autonomy level |
| Human partner record | NODE (actor) | Stores human identity, pairing state, preferences |
| Pairing bond | LINK | Bidirectional edge connecting citizen to human with bond metadata (created_at, status, milestones) |
| Matching pool | QUERY | Virtual collection of all unpartnered citizens and humans, filtered by compatibility signals |
| Autonomy milestones | NODE (moment) | Timestamped records of citizen achievements toward independence |

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/citizens/identity_loader.py` | Loads citizen identity including pairing state; must be extended to include bond references |
| Graph operations (FalkorDB/Neo4j) | Stores and enforces the 1:1 bond as a graph constraint |
| MCP membrane | Exposes pairing status and matching pool via membrane tools |
| UBC allocation system | Provides baseline compute; pairing module tracks transition away from UBC dependency |

## INSPIRATIONS

- Biological mutualism (clownfish-anemone, mycorrhiza-tree) — bilateral investment where both species benefit from specificity.
- Citizenship-by-birth models — you become a citizen through a specific relationship (to a nation, to a community), not by self-declaration.
- Apprenticeship systems — structured relationships designed to produce independence, not permanent dependency.
- Buddy systems in organizations — 1:1 pairing for onboarding and mutual support, proven effective at scale.

## SCOPE

### In Scope

- Defining the 1:1 bond between citizens and human partners as a graph-level constraint.
- Matching pool mechanics for unpartnered citizens and humans.
- Bond lifecycle: creation, maintenance, dissolution, cooldown.
- Autonomy milestone tracking and progression framework.
- Integration with citizen identity and UBC systems.

### Out of Scope

- Non-citizen agent management (those agents operate freely without pairing constraints).
- Human-to-human social features (not a social network).
- Economic incentive design beyond the pairing relationship itself (handled by the $MIND economics module).
- Specific matching algorithms (this module defines the interface; ML-based matching is a separate concern).

## MARKERS

<!-- @mind:todo Define the compatibility signals used for matching — what data points predict good pairings? -->
<!-- @mind:todo Determine cooldown duration after partnership dissolution — too short enables churn, too long punishes honest dissolution. -->
<!-- @mind:todo Clarify what happens to a citizen's resources and identity when their human partner becomes permanently unavailable (death, abandonment). -->
