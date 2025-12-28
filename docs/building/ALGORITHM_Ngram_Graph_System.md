# mind Graph System — Algorithm: Client Procedures

```
STATUS: DESIGNING
CREATED: 2024-12-23
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Mind_Graph_System.md
PATTERNS:        ./PATTERNS_Mind_Graph_System.md
BEHAVIORS:       ./BEHAVIORS_Mind_Graph_System.md
THIS:            ALGORITHM_Mind_Graph_System.md (you are here)
VALIDATION:      ./VALIDATION_Mind_Graph_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Mind_Graph_System.md
HEALTH:          ./HEALTH_Mind_Graph_System.md
SYNC:            ./SYNC_Mind_Graph_System.md

IMPL:            building/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC.

---

## BOUNDARY

**We are a client of the mind engine.**

| We Own | Engine Owns |
|--------|-------------|
| Ingest (docs → nodes) | Physics (tick, energy, decay) |
| Agent response handling | Activation thresholds |
| Narrative/Moment content | Graph structure |
| Trigger reaction | Trigger detection |
| Query patterns | Query execution |

We call engine APIs. We don't modify physics.

---

## OVERVIEW

Four client-side algorithms:

1. **Ingest** — Transform our docs into graph nodes
2. **Context Query** — Ask engine for actor's relevant view
3. **Agent Handler** — React when engine triggers our agents
4. **Content Creation** — Ask engine to create our Moments/Narratives

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | What We Do |
|-----------|---------------------|------------|
| Docs dissolve into narratives | B6, B10 | Ingest transforms files to nodes |
| Agents receive context from graph | B1, B2 | Query engine for hot narratives |
| All actors generate energy | B7, B11 | Create moments when actors think |

---

## ALGORITHM 1: INGEST

### Purpose

Transform repository docs into graph nodes. Run once at bootstrap, incrementally on changes. Calls engine APIs to create nodes/links.

### Step 1: Discover Files

```
FOR each file in repo:
  IF matches pattern in repo_to_graph_mapping.yaml:
    queue for processing
```

### Step 2: Create Spaces

```
FOR each directory pattern match:
  # ID follows convention: {node-type}_{SUBTYPE}_{instance}
  # Example: space_MODULE_engine-physics
  space_id = generate_space_id(directory_name, "MODULE")

  engine.create_space(
    id: space_id,
    name: directory name,
    type: module | code_area | meta,
    weight: from mapping.physics.spaces,
    energy: 0.0
  )
```

> **ID Convention:** See `docs/schema/PATTERNS_Schema.md` section 3 for format.

### Step 3: Create Narratives from Docs

```
FOR each doc file:
  PARSE content

  # ID follows convention: narrative_{SUBTYPE}_{module}-{doc-type}
  # Example: narrative_PATTERN_engine-physics-patterns
  narrative_id = generate_narrative_id(doc_pattern, module_name)

  engine.create_narrative(
    id: narrative_id,
    type: from doc pattern (OBJECTIVES_ → objectives, etc.),
    content: file content or summary,
    weight: from mapping.physics.narratives,
    energy: from mapping.physics.narratives
  )

  engine.create_link(
    from: space_id,
    to: narrative_id,
    nature: "contains"
  )

  # Extract sections if configured
  FOR each section matching extract pattern:
    child_id = engine.create_narrative(...)
    engine.create_link(
      from: narrative_id,
      to: child_id,
      nature: "relates to",
      direction: contains
    )
```

### Step 4: Extract Markers

```
FOR each @mind:todo marker:
  goal_id = engine.create_narrative(
    type: goal,
    status: pending,
    content: marker text,
    energy: 0.3  # goals start warm
  )
  engine.create_link(
    from: goal_id,
    to: containing_doc_id,
    nature: "is about"
  )

FOR each @mind:escalation marker:
  engine.create_narrative(
    type: escalation,
    status: pending,
    energy: 0.5  # escalations start hot
  )
```

### Step 5: Create Things

```
FOR each code file:
  # ID follows convention: thing_{SUBTYPE}_{path-context}_{hash}
  # Example: thing_FILE_engine-physics-graph-ops_a7
  thing_id = generate_thing_id(file_path, "FILE")

  engine.create_thing(
    id: thing_id,
    type: file,
    path: full path
  )
  engine.create_link(from: space_id, to: thing_id, nature: "contains")

FOR each external URL in docs:
  thing_id = generate_thing_id(url, "EXTERNAL")
  engine.create_thing(id: thing_id, type: external, uri: URL)
```

### Step 6: Create Actors

```
# Human — ID: actor_HUMAN_nicolas
human_id = generate_actor_id("nicolas", "HUMAN")
engine.create_actor(
  id: human_id,
  type: human,
  weight: 1.0,
  energy: 1.0
)

# Agents from config
FOR each agent in agents.yaml:
  # ID: actor_AGENT_narrator, actor_AGENT_world-runner
  actor_id = generate_actor_id(agent.name, "AGENT")
  engine.create_actor(
    id: actor_id,
    type: agent,
    name: agent.name,
    weight: 0.8,
    energy: 0.0
  )
  engine.create_link(from: agent.space, to: actor_id, nature: "contains")
```

### Step 7: Create Doc Chain Links

```
FOR each doc with CHAIN section:
  FOR each referenced doc:
    engine.create_link(
      from: this_narrative_id,
      to: referenced_narrative_id,
      nature: "relates to",
      direction: chain
    )
```

### Data Flow

```
repo files
    ↓
pattern matching (our mapping.yaml)
    ↓
engine.create_space() calls
    ↓
engine.create_narrative() calls
    ↓
engine.create_thing() calls
    ↓
engine.create_actor() calls
    ↓
engine.create_link() calls
    ↓
GRAPH READY (engine owns it now)
```

---

## ALGORITHM 2: CONTEXT QUERY

### Purpose

Ask engine for actor's relevant view. Called before agent work.

### Step 1: Request Context

```
context = engine.get_context(
  actor_id: actor_id,
  max_narratives: 20,
  max_moments: 10,
  include_things: True
)
```

### What Engine Returns

```
Context:
  narratives: List[Narrative]  # hot ones, sorted by energy
  moments: List[Moment]        # recent ones in actor's spaces
  things: List[Thing]          # linked to hot narratives
  spaces: List[Space]          # actor's current spaces
```

### What We Do With It

```
# Format for agent consumption
system_context = format_for_agent(context)
```

Engine handles:
- HOT_THRESHOLD filtering
- Energy sorting
- Space scoping
- Moment windowing

We just ask and format.

---

## ALGORITHM 3: AGENT HANDLER

### Purpose

React when engine triggers one of our agents. Engine calls us.

### Trigger Signature

```
# Engine calls this when agent should activate
def on_agent_trigger(agent_id: str, moment: Moment, context: Context):
```

### Step 1: Build System Prompt

```
system = load_base_prompt(agent_id)
system += "\n\n## CURRENT CONTEXT\n"
system += format_narratives(context.narratives)
system += "\n\n## RECENT ACTIVITY\n"
system += format_moments(context.moments)
system += "\n\n## AVAILABLE RESOURCES\n"
system += format_things(context.things)
```

### Step 2: Build Opening

```
opening = f"Active moment: {moment.content}"
opening += f"\nIn space: {context.spaces[0].name}"
```

### Step 3: Call LLM

```
response = llm.complete(
  system=system,
  messages=[{"role": "user", "content": opening}]
)
```

### Step 4: Parse Response

```
# Extract what agent created
moments_to_create = parse_moments(response)
narratives_to_create = parse_narratives(response)
```

### Step 5: Create Content via Engine

```
FOR each m in moments_to_create:
  engine.create_moment(
    actor_id: agent_id,
    prose: m.prose,
    type: m.type,
    about: m.touched_ids
  )

FOR each n in narratives_to_create:
  engine.create_narrative(
    actor_id: agent_id,
    type: n.type,
    content: n.content,
    relates_to: n.related_ids
  )
```

### Step 6: Signal Completion

```
engine.complete_moment(moment.id)
# Engine handles energy flow from completion
```

---

## ALGORITHM 4: CONTENT CREATION

### Purpose

Create Moments and Narratives when actors think. Wrapper around engine calls.

### Moment Creation

```
def create_moment(actor_id: str, prose: str, touched_ids: List[str]):

  # Determine type from content
  type = infer_moment_type(prose)  # thought | message | decision | query

  # Call engine
  moment_id = engine.create_moment(
    actor_id: actor_id,
    prose: prose,
    type: type,
    about: touched_ids,
    space_id: get_actor_space(actor_id)
  )

  return moment_id
```

### Narrative Creation

```
def create_narrative(actor_id: str, content: str, related_ids: List[str]):

  # Determine type from content
  type = infer_narrative_type(content)  # goal | pattern | rationale | memory

  # Call engine
  narrative_id = engine.create_narrative(
    actor_id: actor_id,
    content: content,
    type: type,
    relates_to: related_ids,
    space_id: get_actor_space(actor_id),
    weight: NARRATIVE_WEIGHTS[type],
    energy: NARRATIVE_ENERGIES[type]
  )

  return narrative_id
```

### Type Inference (Our Logic)

```
def infer_moment_type(prose: str) -> str:
  IF contains question mark:
    return "query"
  ELIF contains decision language ("decided", "choosing", "will"):
    return "decision"
  ELIF starts with addressing someone:
    return "message"
  ELSE:
    return "thought"

def infer_narrative_type(content: str) -> str:
  IF contains goal language ("need to", "should", "must"):
    return "goal"
  ELIF contains pattern language ("always", "never", "when X then Y"):
    return "pattern"
  ELIF contains rationale language ("because", "since", "reason"):
    return "rationale"
  ELSE:
    return "memory"
```

---

## HELPER FUNCTIONS

### `format_narratives(narratives: List[Narrative]) -> str`

**Purpose:** Format narratives for agent system prompt.

**Logic:**
```
lines = []
for n in narratives:
  lines.append(f"- [{n.type}] {n.content[:200]}")
return "\n".join(lines)
```

### `format_moments(moments: List[Moment]) -> str`

**Purpose:** Format recent moments for agent context.

**Logic:**
```
lines = []
for m in moments:
  actor = get_actor_name(m.actor_id)
  lines.append(f"- {actor}: {m.prose[:150]}")
return "\n".join(lines)
```

### `format_things(things: List[Thing]) -> str`

**Purpose:** Format available resources for agent.

**Logic:**
```
lines = []
for t in things:
  lines.append(f"- {t.type}: {t.path or t.uri}")
return "\n".join(lines)
```

---

## INTERACTIONS

| We Call | Engine Provides |
|---------|-----------------|
| engine.create_space() | Space node in graph |
| engine.create_narrative() | Narrative node with physics fields |
| engine.create_moment() | Moment node + links |
| engine.create_thing() | Thing node |
| engine.create_actor() | Actor node |
| engine.create_link() | Link with weight |
| engine.get_context() | Filtered, sorted context |
| engine.complete_moment() | Energy flow from completion |

| Engine Calls | We Provide |
|--------------|------------|
| on_agent_trigger() | Agent response handling |

---

## WHAT WE DON'T DO

- Set energy thresholds (engine config)
- Run tick (engine runner)
- Flow energy (engine physics)
- Decay energy (engine physics)
- Grow strength (engine physics)
- Detect activations (engine physics)

We create content. Engine runs the world.

---

## MARKERS

<!-- @mind:todo Define NARRATIVE_WEIGHTS, NARRATIVE_ENERGIES constants -->
<!-- @mind:todo Implement incremental ingest for file changes -->
<!-- @mind:todo Design agent base prompt loading -->
<!-- @mind:todo Implement response parsing for moments/narratives -->

<!-- @mind:escalation Type inference is heuristic-based — will misclassify. Should agents be able to correct/reclassify? -->
<!-- @mind:escalation Ingest runs once at bootstrap — what about docs created after? File watcher? Git hook? Manual re-ingest? -->
<!-- @mind:escalation Agent handler calls LLM synchronously — what about timeout? Retry? Partial response? -->

<!-- @mind:proposition Ingest could create "draft" narratives that agent reviews before they go live -->
<!-- @mind:proposition Type inference could use LLM classification instead of heuristics -->
<!-- @mind:proposition Agent response could include structured JSON alongside prose for reliable parsing -->

<!-- @mind:escalation [D1] Agent Query Mechanism — how do agents query context?
  Options:
    A) engine.get_context() — physics-aware, respects thresholds
    B) Direct graph queries — raw Cypher, agent sees everything
    C) Hybrid — get_context() for hot items, direct for specific lookups
  Opinion: (A) engine.get_context(). Agents should see what physics surfaces, not everything. This is the core design — energy determines relevance. Direct queries would bypass the whole point. If agent needs specific lookup, that's a different API (get_narrative_by_id).
  Phase: 2 -->

<!-- @mind:escalation [D3] Already Running Agent Injection — if agent is mid-LLM-call and new Moment arrives?
  Options:
    A) Inject into current context (modify prompt mid-stream)
    B) Queue for next activation
    C) Interrupt current call, restart with new context
    D) Ignore until current work completes
  Opinion: (B) Queue. LLM calls are atomic — can't inject mid-stream. Interrupting wastes tokens and creates confusion. Queue maintains causality. Agent finishes current thought, then sees new Moment. Simple, predictable.
  Phase: 3 -->

<!-- @mind:escalation [D5] Opening Message Contents — what goes in the opening to agent?
  Options:
    A) Just the triggering Moment prose
    B) Moment + list of hot Narrative titles
    C) Moment + condensed summary of context
    D) Full context dump (everything from get_context)
  Opinion: (C) Moment + condensed summary. (A) is too sparse — agent has no grounding. (D) is too verbose — wastes tokens on stuff in system prompt. Summary gives agent situational awareness without duplication. Format: "You're working on: {moment}. Context: {3-5 key narratives}."
  Phase: 3 -->

<!-- @mind:escalation [Q1] Agent Response Format — how to reliably extract Moments/Narratives from response?
  Options:
    A) Freeform text, parse with regex/heuristics
    B) Structured JSON with schema
    C) XML-like markers in prose
    D) Separate structured + prose sections
  Opinion: (B) Structured JSON. LLMs are good at JSON now. Regex parsing is fragile. Markers are ugly. Define schema: {moments: [...], narratives: [...], prose: "..."}. Prose field preserves natural language for logging/display. Use Claude's JSON mode.
  Phase: 3 -->

<!-- @mind:escalation [Q2] Multi-Agent Same Moment — if multiple agents triggered by same hot Narrative?
  Options:
    A) All respond, energy splits proportionally
    B) First responder wins, others skip
    C) Highest-affinity agent only
    D) Random selection of one
  Opinion: (A) All respond, energy splits. This is how differentiation emerges — agents develop different responses to same stimulus. First-wins creates race conditions. Random is arbitrary. Energy split means popular topics get distributed attention. Natural load balancing.
  Phase: 5 -->

<!-- @mind:escalation [Q5] Agent Failure Handling — what happens if LLM call fails?
  Options:
    A) Silent fail, log error
    B) Retry once with same prompt
    C) Retry with simplified prompt
    D) Mark moment as failed, surface to human
    E) Fallback to different model
  Opinion: (B) then (D). Retry once — transient errors are common. If still fails, mark failed with reason. Don't retry infinitely (cost). Don't fail silently (loses visibility). Failed moments should surface in health checks. Human can investigate pattern of failures.
  Phase: 3 -->

<!-- @mind:escalation [Q6] Type Inference Strategy — how to classify Moment/Narrative types?
  Options:
    A) Heuristics only (keyword matching)
    B) LLM classification for all
    C) Heuristics first, LLM fallback for low-confidence
    D) Let agent self-classify in response
  Opinion: (C) Heuristics + LLM fallback. Pure heuristics misclassify subtle cases. Pure LLM is slow/expensive for every item. Heuristics handle obvious cases (80%+), LLM handles ambiguous. Confidence threshold: 0.7. Below that, ask LLM. (D) is interesting but adds prompt complexity.
  Phase: 3 -->

<!-- @mind:escalation [Q9] Bootstrap Sequence — how does the world start?
  Options:
    A) Human creates first Moment manually
    B) Ingest creates warm Narratives, physics triggers agents
    C) Special "bootstrap agent" seeds initial state
    D) Empty start, human interaction creates first energy
  Opinion: (B) Ingest creates warm Narratives. Bootstrap should be automatic after ingest. Set initial energy on ingested Narratives (e.g., 0.3 for docs, 0.5 for goals). First tick, hot Narratives surface, agents trigger. No special bootstrap agent — same physics from start. Human can then interact normally.
  Phase: 3 -->
