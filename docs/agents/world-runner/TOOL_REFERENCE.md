# World Runner Tool Reference

Definitive schema summary for World Runner output. Use in prompts via `@docs/agents/world-runner/TOOL_REFERENCE.md`.

---

## WorldRunnerOutput

```typescript
interface WorldRunnerOutput {
  thinking: string;
  graph_mutations: GraphMutations;
  world_injection: WorldInjection;
}
```

---

## Graph Mutations

```typescript
interface GraphMutations {
  new_narratives?: NewNarrative[];
  new_beliefs?: NewBelief[];
  character_movements?: CharacterMovement[];
  modifier_changes?: ModifierChange[];
}
```

### New Narrative

```typescript
interface NewNarrative {
  id: string;
  name: string;
  content: string;
  interpretation?: string;
  type: NarrativeType;
  about: {
    characters?: string[];
    relationship?: string[];
    places?: string[];
    things?: string[];
  };
  tone?: NarrativeTone;
  truth?: number;
  focus?: number;
}
```

**NarrativeType:** `memory`, `account`, `rumor`, `reputation`, `identity`, `bond`, `oath`, `debt`, `blood`, `enmity`, `love`, `service`, `ownership`, `claim`, `control`, `origin`, `belief`, `prophecy`, `lie`, `secret`

**NarrativeTone:** `bitter`, `proud`, `shameful`, `defiant`, `mournful`, `cold`, `righteous`, `hopeful`, `fearful`, `warm`, `dark`, `sacred`

### New Belief

```typescript
interface NewBelief {
  character: string;
  narrative: string;
  heard: number;
  believes?: number;
  doubts?: number;
  denies?: number;
  source: BeliefSource;
  from_whom?: string;
}
```

**BeliefSource:** `witnessed`, `told`, `inferred`, `assumed`, `taught`

### Character Movement

```typescript
interface CharacterMovement {
  character: string;
  from?: string;
  to: string;
  visible?: boolean;
}
```

### Modifier Change

```typescript
interface ModifierChange {
  node: string;
  add?: Modifier;
  remove?: string;
}
```

---

## World Injection

```typescript
interface WorldInjection {
  time_since_last: string;
  breaks: Break[];
  news_arrived?: NewsItem[];
  energy_shifts?: Record<string, string>;
  interruption?: Interruption | null;
  atmosphere_shift?: string;
  narrator_notes?: string;
}
```

### Break

```typescript
interface Break {
  narrative_id: string;
  narrative: string;
  event: string;
  location: string;
  player_awareness: PlayerAwareness;
  witnesses?: string[];
}
```

**PlayerAwareness:** `witnessed`, `encountered`, `heard`, `will_hear`, `unknown`

### News Item

```typescript
interface NewsItem {
  narrative: string;
  summary: string;
  source: string;
  reliability: number;
}
```

### Interruption

```typescript
interface Interruption {
  type: 'arrival' | 'message' | 'event';
  character?: string;
  event?: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}
```

---

## Validation Rules (Summary)

1. `thinking` is required.
2. All IDs must exist or be created in the same mutation.
3. `about` references must resolve to existing or newly created nodes.
4. `truth` is director-only.
5. `heard` must be > 0 for belief confidence fields to matter.
6. `player_awareness` must match player location and time.

---

## Processing Order

1. New narratives
2. New beliefs
3. Character movements
4. Modifier changes

---

## Archive Note

Verbose examples and the full JSON schema were archived to keep this module under size limits.

---

## CHAIN

PATTERNS:        ./PATTERNS_World_Runner.md
BEHAVIORS:       ./BEHAVIORS_World_Runner.md
ALGORITHM:       ./ALGORITHM_World_Runner.md
VALIDATION:      ./VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_World_Runner_Service_Architecture.md
TEST:            ./TEST_World_Runner_Coverage.md
INPUTS:          ./INPUT_REFERENCE.md
TOOLS:           ./TOOL_REFERENCE.md
SYNC:            ./SYNC_World_Runner.md
