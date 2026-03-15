# THE BLOOD LEDGER — Validation Specification
# Version: 1.0

---

# =============================================================================
# PURPOSE
# =============================================================================

purpose: |
  This document defines what the game should FEEL like,
  maps those feelings to mechanisms, and provides tests
  to validate the mechanisms produce the feelings.
  
  The energy system is invisible. Players never see "energy" or "pressure."
  They feel companions, urgency, memory, weight.
  
  If the mechanisms are correct but the feelings are wrong, we failed.
  If the feelings are right, the mechanisms worked.

# =============================================================================
# CHAIN
# =============================================================================

## CHAIN

```
PATTERNS:   ./PATTERNS_Graph.md
BEHAVIORS:  ./BEHAVIORS_Graph.md
ALGORITHM:  ../ALGORITHM_Physics.md
THIS:       VALIDATION_Living_Graph.md
SYNC:       ./SYNC_Graph.md
```

# =============================================================================
# INVARIANTS
# =============================================================================

## INVARIANTS

The living graph must never create orphaned nodes, disconnected clusters, or
links that reference missing targets. Mutations must be partially persisted:
valid items remain, invalid items are rejected with actionable feedback, and
the graph continues operating with intact integrity guarantees.

# =============================================================================
# PROPERTIES
# =============================================================================

## PROPERTIES

Graph behavior should remain legible and deterministic for the same inputs:
energy flow, pressure buildup, and propagation must produce repeatable
surfaces for Voices and narrative pressure. Properties here are observed in
gameplay, not only in low-level graph queries.

# =============================================================================
# ERROR CONDITIONS
# =============================================================================

## ERROR CONDITIONS

Validation must surface orphaned nodes, disconnected clusters, missing
targets, invalid types, or missing required fields immediately. Database
connection failures are fatal for validation runs and should halt further
mutation application until the database is available again.

# =============================================================================
# TEST COVERAGE
# =============================================================================

## TEST COVERAGE

Coverage draws from the behavior tests in this validation document plus the
physics engine tests in `runtime/tests/` that exercise graph integrity,
propagation, and flip mechanics. Any manual validation runs should be noted
in `docs/physics/graph/SYNC_Graph.md` to avoid drift.

# =============================================================================
# VERIFICATION PROCEDURE
# =============================================================================

## VERIFICATION PROCEDURE

1. Run the automated physics and graph-related tests in `runtime/tests/`.
2. Apply representative mutation batches and confirm partial persistence
   behavior matches the examples and error handling described above.
3. Simulate a short travel sequence and confirm world-runner narratives
   surface according to the behaviors and tests in this doc.
4. Record any deviations or missing coverage in `docs/physics/graph/SYNC_Graph.md`.

# =============================================================================
# SYNC STATUS
# =============================================================================

## SYNC STATUS

This validation spec is aligned with `docs/physics/graph/SYNC_Graph.md`. If
the SYNC file is missing updates about validation changes, treat the results
as provisional and document the gap before closing a repair.

# =============================================================================
# GRAPH INTEGRITY RULES
# =============================================================================

graph_integrity:
  rules:
    - "New clusters must connect to the existing graph."
    - "No orphaned nodes: every node must have at least one link."
    - "Partial persistence: valid items persist, invalid items are rejected with feedback."

  valid_mutation_example: |
    nodes:
      - type: character
        id: char_wulfric
        name: Wulfric

    links:
      - type: belief
        character: char_wulfric    # NEW node
        narrative: narr_oath       # EXISTING node
        heard: 1.0

  invalid_mutation_example: |
    nodes:
      - type: character
        id: char_wulfric
        name: Wulfric
      # No links — char_wulfric would be orphaned

  error_handling_example: |
    result = write.apply(path="mutations/scene_001.yaml")

    if result.errors:
        for error in result.errors:
            print(f"{error.item}: {error.message}")
            print(f"  Fix: {error.fix}")

    print(f"Persisted: {result.persisted}")
    print(f"Rejected: {result.rejected}")

  error_types:
    - error: orphaned_node
      message: "char_wulfric has no links"
      fix: "Add at least one link connecting this node"
    - error: disconnected_cluster
      message: "New nodes [char_a, char_b] not connected to graph"
      fix: "Add link from cluster to existing node"
    - error: missing_target
      message: "Link references non-existent node: narr_unknown"
      fix: "Create the target node first, or fix the ID"
    - error: invalid_type
      message: "Invalid character type: warrior"
      fix: "Check SCHEMA.md for allowed values"
    - error: invalid_field
      message: "Unknown field: foo on character"
      fix: "Check SCHEMA.md for valid fields"
    - error: missing_required
      message: "narrative.content is required"
      fix: "Add the required field"
    - error: db_connection
      message: "Cannot connect to FalkorDB"
      fix: "docker run -p 6379:6379 falkordb/falkordb"

  partial_persistence_example: |
    result = write.apply(path="mutations/batch.yaml")

    # result.persisted = ["char_aldric", "narr_oath", "link_belief_1"]
    # result.rejected = [
    #   {"item": "char_wulfric", "error": "orphaned_node", "fix": "Add link..."}
    # ]

    The engine persists everything it can, then reports what failed and why.


# =============================================================================
# VISION MAPPING
# =============================================================================

vision_moments:
  
  # --- COVERED BY ENERGY SYSTEM ---
  
  "My past speaks":
    description: "In a tense moment, your oaths and debts pull in different directions."
    mechanism: High-energy narratives surface as Voices
    status: covered
  
  "The world moved":
    description: "You arrive somewhere and hear about events that happened without you."
    mechanism: World Runner processes distant pressure → news propagates
    status: covered
  
  "Everything led here":
    description: "In a climactic moment, you see how all choices wove together."
    mechanism: Narrative clusters converge → cascade → confrontation
    status: covered
  
  # --- REQUIRES NARRATOR/CONTENT ---
  
  "I know what I need to do":
    description: "Early clarity. You can articulate your goal."
    mechanism: Opening establishes purpose (content design)
    status: narrator_job
  
  "I see where I'm going":
    description: "You know the next step, not just the goal."
    mechanism: Goal narratives surface with path (Narrator)
    status: narrator_job
  
  "I know this place":
    description: "Certain locations become familiar, grounding, home."
    mechanism: Place-player narratives accumulate (visits create beliefs)
    status: partial
  
  "They remembered":
    description: "An character references something you did sessions ago."
    mechanism: Player actions create narratives → characters believe → resurface later
    status: covered
  
  "I was wrong":
    description: "Discover foundational belief was mistaken. Reality shifts."
    mechanism: Supersession + revelation drains old belief, surfaces new
    status: covered
  
  "This is my band":
    description: "You look at companions and feel ownership, belonging."
    mechanism: Companion presence + shared narratives + time
    status: partial
  
  "They became real":
    description: "A character becomes complex — a person, not a type."
    mechanism: Pre-generation creates depth → revealed through conversation
    status: covered
  
  "I know them":
    description: "You can predict what they'd do. You know this person."
    mechanism: Consistent beliefs/traits → player learns → predictions match
    status: covered
  
  "I can rely on them":
    description: "You send a companion confidently. They succeed for predicted reasons."
    mechanism: Skills + traits inform outcomes → player's model validated
    status: covered


# =============================================================================
# EXPECTED BEHAVIORS
# =============================================================================

behaviors:

  # ---------------------------------------------------------------------------
  # PRESENCE & PROXIMITY
  # ---------------------------------------------------------------------------
  
  companion_presence:
    id: B01
    category: presence
    
    gameplay: |
      Aldric's concerns, memories, and oaths keep surfacing in your mind.
      He feels like he's THERE, not just following silently.
    
    mechanism: |
      High proximity (1.0) × high relationship = high character energy
      → pumps strongly into his narratives
      → those narratives stay energized
      → surface frequently as Voices
    
    failure_looks_like: |
      Companions feel like silent followers.
      Their concerns never surface unless you ask.
  
  approach_escalation:
    id: B02
    category: presence
    
    gameplay: |
      The closer you get to York, the more Edmund weighs on you.
      Three days away feels distant. One day away is a knot in your stomach.
    
    mechanism: |
      Proximity increases (0.2 → 0.7 → 1.0)
      → Edmund's energy rises (relationship × proximity)
      → his narratives heat up
      → Voices intensify
      → pressure builds automatically
    
    failure_looks_like: |
      Edmund feels equally present whether near or far.
      Arrival feels no different from a week away.
  
  distant_dormant:
    id: B03
    category: presence
    
    gameplay: |
      There's politics in Wessex. Lords scheming. You've heard whispers.
      But you don't care — it's far away, you have no stake.
      It doesn't keep you up at night.
    
    mechanism: |
      Low relationship × low proximity = low character energy
      → barely pumps into narratives
      → decay > inflow
      → narratives dormant
      → never surface as Voices
    
    failure_looks_like: |
      Random distant events intrude on your attention.
      Everything feels equally important.

  # ---------------------------------------------------------------------------
  # LIVING WORLD
  # ---------------------------------------------------------------------------
  
  world_moved:
    id: B04
    category: living_world
    
    gameplay: |
      You arrive in York and hear about the feud that broke out while you traveled.
      Edmund made a move. The sheriff issued a decree.
      You weren't there — but it happened. The world didn't wait.
    
    mechanism: |
      World Runner processes distant pressure during travel
      → creates narratives of events
      → news propagates via character beliefs
      → on arrival, Narrator surfaces "what you missed"
      → new narratives with recent timestamps
    
    failure_looks_like: |
      Nothing happens while you're away.
      The world freezes until you arrive.
  
  antagonist_acts:
    id: B05
    category: living_world
    
    gameplay: |
      Edmund isn't waiting for you. He's scheming, building alliances, preparing.
      You hear about his moves. He feels like a PERSON pursuing goals,
      not a boss waiting in a room.
    
    mechanism: |
      Antagonists have beliefs → beliefs create pressure
      → pressure breaks on its own timeline
      → World Runner creates narratives of their actions
      → propagates as news you eventually hear
    
    failure_looks_like: |
      Edmund only does things when you're present.
      He's static until the confrontation.
  
  news_travels:
    id: B06
    category: living_world
    
    gameplay: |
      You did something notable in Thornwick.
      A week later, in York, someone's heard about it.
      Your reputation precedes you. Word spreads — good or bad.
    
    mechanism: |
      Significant player actions create narratives
      → propagate through character belief network over time
      → distant characters eventually believe versions
      → affects their disposition when you meet
    
    failure_looks_like: |
      Your actions have no reputation effects.
      characters only know what they witnessed.

  # ---------------------------------------------------------------------------
  # NARRATIVE TENSION
  # ---------------------------------------------------------------------------
  
  contradiction_unresolved:
    id: B07
    category: narrative_pressure
    
    gameplay: |
      You heard Edmund saved the family. But you KNOW he betrayed you.
      Both versions keep surfacing. You can't settle it. It gnaws.
    
    mechanism: |
      Player believes both A and B
      → contradiction link heats both sides (bidirectional, factor 0.3)
      → neither fades
      → both surface as Voices
      → pressure persists until player acts or chooses
    
    failure_looks_like: |
      One version dominates immediately.
      The contradiction doesn't feel unresolved.
  
  loyalty_cluster:
    id: B08
    category: narrative_pressure
    
    gameplay: |
      When you doubt Aldric's oath, you start doubting everything about him —
      his stories, his past, why he's really here.
      Trust is a fabric, not a fact.
    
    mechanism: |
      Support links cluster narratives (bidirectional, factor 0.2)
      → doubt one, energy drops
      → propagates to cluster
      → all related Voices weaken together
    
    failure_looks_like: |
      Doubting one thing doesn't affect related beliefs.
      Trust is atomic, not interconnected.
  
  old_news_fades:
    id: B09
    category: narrative_pressure
    
    gameplay: |
      You used to obsess about where Edmund was. Now you know he fled York.
      The old question stops haunting you.
    
    mechanism: |
      Supersedes link drains old narrative (factor 0.25)
      → old narrative loses energy
      → new narrative gains energy + drain
      → old stops surfacing as Voice
    
    failure_looks_like: |
      Outdated information keeps surfacing.
      You can't "update" your mental state.
  
  belief_shattered:
    id: B10
    category: narrative_pressure
    
    gameplay: |
      You believed Edmund betrayed you. Everything pointed to it.
      Then you learn the truth — Father changed the will.
      The foundation shifts. You have to reconsider everything.
    
    mechanism: |
      Player believes narrative A (truth: 0.3)
      → contradicting narrative B exists (truth: 0.9)
      → revelation event: player learns B
      → B supersedes A
      → A's energy drains
      → belief structure reorganizes
      → Voices change character
    
    failure_looks_like: |
      Revelations feel like new information, not paradigm shifts.
      Old beliefs persist alongside new ones without pressure.

  # ---------------------------------------------------------------------------
  # COMPANION DEPTH
  # ---------------------------------------------------------------------------
  
  they_remembered:
    id: B11
    category: companion_depth
    
    gameplay: |
      The innkeeper mentions the coin you left last time.
      Aldric references the choice you made at Thornwick.
      Someone you helped sends word. The world has memory.
    
    mechanism: |
      Player actions create narratives
      → characters gain beliefs about those narratives
      → later interactions, Narrator surfaces character beliefs about player's past
    
    failure_looks_like: |
      characters never reference your history.
      Each encounter feels fresh, without continuity.
  
  they_became_real:
    id: B12
    category: companion_depth
    
    gameplay: |
      You started with "Aldric the loyal sword."
      Now you know he lost his brother, hates the cold, prays alone.
      He's not a type — he's a person.
    
    mechanism: |
      Pre-generation creates character depth
      → even unanswered questions have answers (in graph)
      → consistent personality from backstory + beliefs
      → Narrator reveals through conversation over time
    
    failure_looks_like: |
      Characters stay archetypes.
      Learning more doesn't make them more specific.
  
  i_know_them:
    id: B13
    category: companion_depth
    
    gameplay: |
      You can predict what Aldric would do.
      "He'd never abandon a wounded man."
      "He'll want to pray before we move."
      You KNOW this person.
    
    mechanism: |
      Character beliefs + traits + backstory are consistent
      → player learns them through play
      → predictions match behavior
      → trust builds from accurate mental model
    
    failure_looks_like: |
      Characters surprise randomly.
      You can't form a reliable mental model of them.
  
  i_can_rely:
    id: B14
    category: companion_depth
    
    gameplay: |
      You send Aldric to scout. He succeeds — and you're not surprised,
      because you knew his skills, knew the situation played to his strengths.
      Trust is validated.
    
    mechanism: |
      Character skills + traits inform outcomes
      → player who understands character makes good choices
      → outcomes match expectations
      → competence trust established
    
    failure_looks_like: |
      Outcomes feel random.
      Your understanding of characters doesn't help you use them.

  # ---------------------------------------------------------------------------
  # SYSTEM HEALTH
  # ---------------------------------------------------------------------------
  
  equilibrium:
    id: B15
    category: system_health
    
    gameplay: |
      After a few days of travel, your mind settles.
      The same concerns surface. The same weights press.
      It's not chaos — it's YOUR situation, crystallized.
    
    mechanism: |
      Energy equilibrium: inflow = outflow
      → narratives stabilize
      → consistent Voices
      → coherent internal state
    
    failure_looks_like: |
      Voices are erratic, random.
      Your mental state doesn't feel stable or coherent.
  
  something_simmers:
    id: B16
    category: system_health
    
    gameplay: |
      There's always SOMETHING about to break.
      Not everything at once, but one or two threads pulled tight.
      The story has momentum.
    
    mechanism: |
      Criticality feedback keeps some pressure points hot
      → decay_rate adjusts to maintain pressure distribution
      → at least one narrative cluster near breaking
      → player feels impending drama
    
    failure_looks_like: |
      Everything feels equally calm.
      No sense of building pressure or imminent change.
  
  no_explosion_freeze:
    id: B17
    category: system_health
    
    gameplay: |
      Things happen at a human pace.
      Not constant crisis. Not dead quiet.
      Room to breathe, but never for long.
    
    mechanism: |
      Conservation + criticality bound total energy
      → breaks happen but don't cascade endlessly
      → quiet moments exist but system heats back up
      → 2-5 breaks per game-hour is the target
    
    failure_looks_like: |
      Everything breaks at once (chaos).
      Or nothing ever breaks (stagnation).
  
  breaks_ripple:
    id: B18
    category: system_health
    
    gameplay: |
      Edmund loses the sheriff's favor. Suddenly other things shift —
      your opportunity, Osric's scheming, the balance of power.
      One break reshapes the web.
    
    mechanism: |
      Break creates narratives
      → new believers pump energy
      → propagates to related narratives
      → other pressure points affected
      → possible cascade (max depth 5)
    
    failure_looks_like: |
      Events are isolated.
      What happens to Edmund doesn't affect anything else.

  # ---------------------------------------------------------------------------
  # TIME & PRESSURE
  # ---------------------------------------------------------------------------
  
  deadline_feels_real:
    id: B19
    category: time_pressure
    
    gameplay: |
      "Three days to the feast" feels like planning.
      "Tomorrow" feels like pressure.
      "Tonight" feels like now-or-never.
      Time creates urgency.
    
    mechanism: |
      Scheduled progression jumps pressure at checkpoints
      → Day 12: 0.2, Day 13: 0.5, Day 14: 0.8
      → psychological cliff mirrors mechanical cliff
    
    failure_looks_like: |
      Time passes uniformly.
      "One day away" feels same as "three days away."
  
  deadline_severity_varies:
    id: B20
    category: time_pressure
    
    gameplay: |
      The knight arrives on Day 14 no matter what.
      But if you stirred up trouble, arrival is DISASTER.
      If you prepared, it's merely tense.
    
    mechanism: |
      Hybrid pressure has floor (scheduled) + variable (event-driven)
      → deadline guaranteed
      → severity depends on accumulated pressure from actions
    
    failure_looks_like: |
      Deadlines have fixed outcomes regardless of preparation.

  # ---------------------------------------------------------------------------
  # ENGAGEMENT
  # ---------------------------------------------------------------------------
  
  attention_grows:
    id: B21
    category: engagement
    
    gameplay: |
      You asked about Thornwick. Now it's on your mind.
      Aldric's past, the Harrying, what happened to his family —
      it all starts surfacing more.
    
    mechanism: |
      Engagement increases belief strength
      → more energy pumped into that narrative
      → propagates to related narratives via support links
      → cluster heats up
      → more Voices from that cluster
    
    failure_looks_like: |
      Asking about something doesn't make it more present.
      Your attention has no effect on what surfaces.
  
  revelation_sinks_in:
    id: B22
    category: engagement
    
    gameplay: |
      Aldric just told you about his grandmother.
      It's there, you heard it, but it hasn't fully landed yet.
      In a day, it might haunt you.
    
    mechanism: |
      New narrative starts with energy = 0
      → believers pump over ticks
      → gradually rises toward equilibrium
      → eventually surfaces as Voice
    
    failure_looks_like: |
      New information immediately dominates.
      No sense of things "sinking in" over time.
  
  narrator_shapes:
    id: B23
    category: engagement
    
    gameplay: |
      The church conspiracy keeps surfacing even though you haven't engaged.
      The narrator wants you to notice.
      Or: you ignored it twice, and it fades — the narrator lets it go.
    
    mechanism: |
      Focus multiplies belief_flow_rate for specific narratives
      → high focus = faster energy accumulation = persistent surfacing
      → low focus = slower accumulation = natural fade
    
    failure_looks_like: |
      Narrator has no ability to emphasize or de-emphasize.
      Everything is purely reactive to player.


# =============================================================================
# ANTI-PATTERNS
# =============================================================================

anti_patterns:

  quest_log:
    id: AP01
    phrase: "Let me check my quest log."
    
    failure: |
      Player treats the Ledger as a checklist of objectives.
      "Go to York. Talk to Wulfric. Find the sword."
    
    success: |
      Ledger shows debts, oaths, blood ties — weight, not tasks.
      Player opens it to feel the pressure, not to find instructions.
    
    mechanism_check: |
      Ledger displays narratives of type [debt, oath, blood, enmity]
      → emotional framing, not objective framing
      → no "complete X" language
    
    test: |
      Review Ledger UI. Count task-like entries vs weight-like entries.
      Task-like entries should be zero.
  
  optimal_choice:
    id: AP02
    phrase: "What's the optimal choice?"
    
    failure: |
      Player min-maxes relationship points.
      Choices feel like optimization problems with correct answers.
    
    success: |
      Choices feel like CHOICES — trade-offs between values.
      Helping A means neglecting B. There's no optimal solution.
    
    mechanism_check: |
      Choices affect multiple relationships in different directions
      → no single choice benefits everything
      → outcomes depend on context, not universal value
    
    test: |
      Review 10 significant choices. Each should have at least one
      positive and one negative relational consequence.
  
  who_is_this:
    id: AP03
    phrase: "Who is this again?"
    
    failure: |
      Player can't remember characters.
      "Wulfric? Was he the innkeeper or the blacksmith?"
    
    success: |
      Characters are memorable through relationship to player.
      "The one who lied about Edmund." "The one I owe silver."
    
    mechanism_check: |
      Characters are introduced through relationship context
      → referenced by relationship, not just name
      → appear in Ledger/Faces connected to player's story
    
    test: |
      Introduce character in scene 2, return in scene 10.
      Ask playtesters to identify. They should describe relationship, not name.
  
  skip_skip_skip:
    id: AP04
    phrase: "Skip skip skip."
    
    failure: |
      Player skips text to get to choices.
      Text is obstacle, not engagement.
    
    success: |
      Player reads Voices, engages with clickable words.
      Text IS the interaction, not preamble to it.
    
    mechanism_check: |
      Clickable words in narration and Voices
      → engagement happens IN the text
      → no "skip to choices" affordance
    
    test: |
      Track click patterns. Players should click within text,
      not skip to bottom. Voices should receive clicks.


# =============================================================================
# TEST SUITE
# =============================================================================

tests:

  # ---------------------------------------------------------------------------
  # PRESENCE & PROXIMITY
  # ---------------------------------------------------------------------------
  
  - id: T01
    behavior: B01 (companion_presence)
    scenario: "Aldric travels with player. Edmund is in York (distant)."
    setup:
      - char_aldric at player location
      - char_edmund at place_york (2 days travel)
      - Both have equal relationship intensity to player
    steps:
      - Run 10 ticks
      - Compare energy of Aldric's narratives vs Edmund's narratives
    expected: "Aldric's narratives have 3-5x more energy than Edmund's."
    assertion: avg(aldric_narrative.energy) > 3 * avg(edmund_narrative.energy)
  
  - id: T02
    behavior: B02 (approach_escalation)
    scenario: "Player travels from North to York over 3 days."
    setup:
      - Player in North (2 days from York)
      - Edmund in York
      - Edmund relationship intensity: 4.0
    steps:
      - Record Edmund's energy at Day 12
      - Simulate 1 day travel (proximity: 0.2 → 0.4)
      - Record Edmund's energy at Day 13
      - Simulate 1 day travel (proximity: 0.4 → 0.7)
      - Record Edmund's energy at Day 14
    expected: "Edmund's energy increases ~3.5x from Day 12 to Day 14."
    assertion: edmund.energy[day14] > 3 * edmund.energy[day12]
  
  - id: T03
    behavior: B03 (distant_dormant)
    scenario: "Wessex lord exists but player has no connection."
    setup:
      - char_wessex_lord in distant Wessex
      - Player has no narratives about Wessex lord
      - Wessex lord believes some narratives
    steps:
      - Run 20 ticks
      - Check energy of narratives believed only by Wessex lord
    expected: "Wessex narratives decay below 0.1."
    assertion: max(wessex_narrative.energy) < 0.1

  # ---------------------------------------------------------------------------
  # LIVING WORLD
  # ---------------------------------------------------------------------------
  
  - id: T04
    behavior: B04 (world_moved)
    scenario: "Player travels 3 days. Distant pressure breaks during travel."
    setup:
      - pressure_feud level at 0.88
      - Player traveling (not near feud location)
    steps:
      - Simulate 3 days travel
      - Check for new narratives created by World Runner
      - Check if player can discover these on arrival
    expected: "New narratives exist from feud break. Discoverable at destination."
    assertion: new_narratives_from_break.count > 0
  
  - id: T05
    behavior: B05 (antagonist_acts)
    scenario: "Edmund has active pressure points. Player is elsewhere."
    setup:
      - Edmund in York
      - pressure_edmund_position level at 0.85
      - Player in North (not traveling to York)
    steps:
      - Simulate 5 days
      - Check for breaks involving Edmund
      - Check for new narratives about Edmund's actions
    expected: "Edmund's pressure breaks. New narratives show his actions."
    assertion: narratives_about_edmund_actions.count > 0
  
  - id: T06
    behavior: B06 (news_travels)
    scenario: "Player does notable action. Check if distant characters learn."
    setup:
      - Player does significant action creating narrative N
      - characters at various distances
    steps:
      - Mark which characters believe N at time 0
      - Simulate 7 days with news propagation
      - Check which characters believe N or version of N
    expected: "Nearby characters learn quickly. Distant characters learn slowly or partially."
    assertion: nearby_npc.believes(N) > distant_npc.believes(N)

  # ---------------------------------------------------------------------------
  # NARRATIVE TENSION
  # ---------------------------------------------------------------------------
  
  - id: T07
    behavior: B07 (contradiction_unresolved)
    scenario: "Player believes two contradicting narratives."
    setup:
      - narr_betrayal (player believes 1.0)
      - narr_salvation (player believes 0.3)
      - narr_betrayal contradicts narr_salvation (strength 0.8)
    steps:
      - Run 10 ticks
      - Check energy of both narratives
    expected: "Both narratives gain energy. Neither dominates."
    assertion: narr_betrayal.energy > 0.5 AND narr_salvation.energy > 0.2
  
  - id: T08
    behavior: B08 (loyalty_cluster)
    scenario: "Player weakens belief in Aldric's oath."
    setup:
      - narr_oath (player believes 1.0)
      - narr_aldric_loyal supports narr_oath (strength 0.8)
      - narr_aldric_saved_me supports narr_aldric_loyal (strength 0.6)
    steps:
      - Record energy of all three
      - Reduce player.believes(narr_oath) to 0.3
      - Run 10 ticks
      - Record energy of all three
    expected: "All three narratives lose energy together."
    assertion: all narratives.energy[after] < narratives.energy[before] * 0.7
  
  - id: T09
    behavior: B09 (old_news_fades)
    scenario: "New narrative supersedes old."
    setup:
      - narr_edmund_in_york (player believes 0.8, energy 1.0)
      - Create narr_edmund_fled (player believes 0.9)
      - narr_edmund_fled supersedes narr_edmund_in_york (strength 1.0)
    steps:
      - Run 10 ticks
    expected: "Old narrative loses energy. New narrative gains."
    assertion: >
      narr_edmund_in_york.energy < 0.3 AND
      narr_edmund_fled.energy > 0.8
  
  - id: T10
    behavior: B10 (belief_shattered)
    scenario: "Player discovers foundational belief was false."
    setup:
      - narr_betrayal (player believes 1.0, truth 0.3)
      - narr_father_willing (player believes 0.0, truth 0.9)
      - narr_father_willing supersedes narr_betrayal
    steps:
      - Player learns narr_father_willing (believes → 0.9)
      - Run 15 ticks
    expected: "Old belief drains. New understanding dominates. Voice character changes."
    assertion: >
      narr_betrayal.energy < 0.3 AND
      narr_father_willing.energy > 0.7

  # ---------------------------------------------------------------------------
  # COMPANION DEPTH
  # ---------------------------------------------------------------------------
  
  - id: T11
    behavior: B11 (they_remembered)
    scenario: "character references player's past action."
    setup:
      - Player previously created narr_player_helped_innkeeper
      - Innkeeper believes this narrative (strength 0.9)
      - Time passes
    steps:
      - Player returns to innkeeper
      - Query innkeeper's beliefs about player
    expected: "Innkeeper has belief about player's past action available for Narrator."
    assertion: innkeeper.believes(narr_player_helped_innkeeper) > 0.5
  
  - id: T12
    behavior: B12 (they_became_real)
    scenario: "Character depth exists even if not yet revealed."
    setup:
      - char_aldric with full backstory
      - Player has not asked about grandmother
    steps:
      - Query: Does Aldric have narrative about grandmother?
      - Query: Is it consistent with his other narratives?
    expected: "Backstory exists. Pre-generation made it real."
    assertion: narr_aldric_grandmother exists AND is_consistent(aldric.backstory)
  
  - id: T13
    behavior: B13 (i_know_them)
    scenario: "Character behavior matches established traits."
    setup:
      - char_aldric with traits: loyalty 0.95, piety 0.7, courage 0.8
      - Present scenario: wounded ally needs help, but mission is urgent
    steps:
      - Query: What would Aldric do?
      - Compare to trait-based prediction
    expected: "Aldric's response consistent with high loyalty (help wounded ally)."
    assertion: aldric_decision matches trait_prediction
  
  - id: T14
    behavior: B14 (i_can_rely)
    scenario: "Companion success correlates with skill match."
    setup:
      - char_aldric with tracking: skilled, sneaking: untrained
      - Task A: tracking mission
      - Task B: stealth mission
    steps:
      - Send Aldric on Task A, record outcome
      - Send Aldric on Task B, record outcome
    expected: "Task A succeeds. Task B fails or struggles."
    assertion: task_a.success == true AND task_b.success == false

  # ---------------------------------------------------------------------------
  # SYSTEM HEALTH
  # ---------------------------------------------------------------------------
  
  - id: T15
    behavior: B15 (equilibrium)
    scenario: "System stabilizes without input."
    setup:
      - Normal graph state with various energies
    steps:
      - Run 50 ticks with no changes
      - Record energy delta between tick 49 and 50
    expected: "Energy values stabilized (delta < 0.01)."
    assertion: max(energy_delta) < 0.01
  
  - id: T16
    behavior: B16 (something_simmers)
    scenario: "At least one pressure point near breaking."
    setup:
      - Normal graph state
    steps:
      - Run 20 ticks
      - Count pressure points with level > 0.7
    expected: "At least one pressure point is 'hot'."
    assertion: count(pressure_point.level > 0.7) >= 1
  
  - id: T17
    behavior: B17 (no_explosion_freeze)
    scenario: "Reasonable break frequency over time."
    setup:
      - Normal graph state
    steps:
      - Simulate 1 game-hour
      - Count total breaks
    expected: "2-5 breaks occurred. Not constant crisis, not dead."
    assertion: break_count >= 2 AND break_count <= 5
  
  - id: T18
    behavior: B18 (breaks_ripple)
    scenario: "Break affects other pressure points."
    setup:
      - pressure_A at 0.88, pressure_B at 0.85
      - Breaking A creates narrative that supports B's narratives
    steps:
      - Force pressure_A to break
      - Run 3 ticks
      - Check pressure_B level
    expected: "Pressure_B level increased. May have flipped."
    assertion: pressure_B.level[after] > pressure_B.level[before]

  # ---------------------------------------------------------------------------
  # TIME & PRESSURE
  # ---------------------------------------------------------------------------
  
  - id: T19
    behavior: B19 (deadline_feels_real)
    scenario: "Scheduled pressure jumps at checkpoints."
    setup:
      - pressure_scheduled with progression:
        - Day 12: 0.2
        - Day 13: 0.5
        - Day 14: 0.8
    steps:
      - Set time to Day 12, record pressure
      - Advance to Day 13, record pressure
      - Advance to Day 14, record pressure
    expected: "Pressure jumps match progression, not gradual tick."
    assertion: >
      pressure[day12] == 0.2 AND
      pressure[day13] == 0.5 AND
      pressure[day14] == 0.8
  
  - id: T20
    behavior: B20 (deadline_severity_varies)
    scenario: "Hybrid pressure exceeds floor via events."
    setup:
      - pressure_hybrid with floor 0.5 at Day 12
      - Current pressure 0.5
    steps:
      - Inject events that add 0.25 pressure
      - Advance to Day 13 (new floor 0.6)
      - Check pressure
    expected: "Pressure is max(ticked, floor) — at least 0.6."
    assertion: pressure >= 0.6

  # ---------------------------------------------------------------------------
  # ENGAGEMENT
  # ---------------------------------------------------------------------------
  
  - id: T21
    behavior: B21 (attention_grows)
    scenario: "Player engagement increases narrative energy."
    setup:
      - narr_thornwick (player believes 0.3, energy X)
    steps:
      - Simulate player clicking "Thornwick" (increases belief to 0.6)
      - Run 5 ticks
      - Check energy of narr_thornwick and related narratives
    expected: "Thornwick narrative and cluster gain energy."
    assertion: narr_thornwick.energy > X * 1.5
  
  - id: T22
    behavior: B22 (revelation_sinks_in)
    scenario: "New narrative starts cold, warms over time."
    setup:
      - Create new narr_grandmother_death
      - char_aldric.believes = 1.0
    steps:
      - Check energy at tick 0
      - Run 5 ticks
      - Check energy at tick 5
    expected: "Energy starts 0, rises toward equilibrium."
    assertion: >
      energy[tick0] == 0 AND
      energy[tick5] > 0.3
  
  - id: T23
    behavior: B23 (narrator_shapes)
    scenario: "Focus multiplier affects energy accumulation."
    setup:
      - narr_A and narr_B identical (same believers, same strengths)
      - narr_A.focus = 2.0
      - narr_B.focus = 0.5
    steps:
      - Run 15 ticks
      - Compare energies
    expected: "High focus has ~4x energy of low focus."
    assertion: narr_A.energy / narr_B.energy > 3.5

  # ---------------------------------------------------------------------------
  # CRITICALITY
  # ---------------------------------------------------------------------------
  
  - id: T24
    behavior: B16 (criticality_cold_recovery)
    scenario: "System recovers from cold state."
    setup:
      - Force low energy state (all narratives energy < 0.1)
      - All pressure points level < 0.2
    steps:
      - Run 20 ticks
      - Check decay_rate changes
      - Check pressure distribution
    expected: "Decay_rate decreased. Pressures rose."
    assertion: >
      decay_rate < initial_decay_rate AND
      avg(pressure.level) > 0.3
  
  - id: T25
    behavior: B17 (criticality_hot_dampening)
    scenario: "System cools from hot state."
    setup:
      - Force high energy state (many narratives energy > 2.0)
      - Multiple pressure points level > 0.8
    steps:
      - Run 20 ticks
      - Check decay_rate changes
      - Check break frequency
    expected: "Decay_rate increased. System cooled."
    assertion: >
      decay_rate > initial_decay_rate AND
      break_count_in_20_ticks < 10

  # ---------------------------------------------------------------------------
  # CASCADE
  # ---------------------------------------------------------------------------
  
  - id: T26
    behavior: B18 (cascade_depth_limit)
    scenario: "Cascades stop at max depth."
    setup:
      - Chain of 10 pressure points that could cascade
      - Each break creates narrative that pushes next over threshold
    steps:
      - Trigger first pressure point
      - Count total breaks
    expected: "Cascade stops at max_depth (5)."
    assertion: break_count <= 5

  # ---------------------------------------------------------------------------
  # ANTI-PATTERNS
  # ---------------------------------------------------------------------------
  
  - id: T27
    anti_pattern: AP01 (quest_log)
    scenario: "Audit Ledger content."
    steps:
      - Export all Ledger entries
      - Classify each as "task-like" or "weight-like"
    expected: "Zero task-like entries."
    assertion: task_like_entries == 0
  
  - id: T28
    anti_pattern: AP02 (optimal_choice)
    scenario: "Audit choice consequences."
    steps:
      - Review 10 significant choices
      - For each, list positive and negative relationship consequences
    expected: "Each choice has mixed consequences."
    assertion: all choices have >= 1 positive AND >= 1 negative consequence
  
  - id: T29
    anti_pattern: AP03 (who_is_this)
    scenario: "Character recall test."
    steps:
      - Introduce character in early scene
      - Return character in later scene
      - Ask playtesters to identify
    expected: "Playtesters describe relationship, not name."
    assertion: identification_by_relationship > identification_by_name
  
  - id: T30
    anti_pattern: AP04 (skip_skip_skip)
    scenario: "Track engagement patterns."
    steps:
      - Log all clicks during play session
      - Calculate ratio: clicks_in_text vs clicks_at_bottom
    expected: "Most clicks are within text (Voices, clickable words)."
    assertion: clicks_in_text > clicks_at_bottom * 2


# =============================================================================
# SUMMARY
# =============================================================================

summary:
  
  total_behaviors: 23
  total_anti_patterns: 4
  total_tests: 30
  
  categories:
    presence_proximity: 3 behaviors, 3 tests
    living_world: 3 behaviors, 3 tests
    narrative_pressure: 4 behaviors, 4 tests
    companion_depth: 4 behaviors, 4 tests
    system_health: 4 behaviors, 6 tests
    time_pressure: 2 behaviors, 2 tests
    engagement: 3 behaviors, 3 tests
    anti_patterns: 4 patterns, 4 tests
  
  vision_coverage:
    fully_covered: 10
    partial: 2
    narrator_job: 2
  
  validation_approach: |
    1. Implement graph engine with energy mechanics
    2. Run automated tests T01-T26 against simulation
    3. Run content audits T27-T28 against game data
    4. Run playtests for T29-T30 behavioral observation
    5. Iterate on parameters until tests pass
    6. Playtest for FEELINGS, not just mechanics

---

## MARKERS

- Which invariants should be enforced at mutation time versus during scheduled
  health checks, and how should partial persistence report the difference?
- Are the current behavior tests sufficient to validate narrative attention,
  or do we need targeted probes for low-energy suppression edge cases?
- Should graph integrity validation include explicit cycle checks for certain
  link types (e.g., supersedes) to prevent contradictory feedback loops?

---

*"If the mechanisms are correct but the feelings are wrong, we failed.*
*If the feelings are right, the mechanisms worked."*
