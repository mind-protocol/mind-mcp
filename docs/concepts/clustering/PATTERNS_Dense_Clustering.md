# PATTERNS: Dense Clustering

## Core Insight

**Documents describe graph. Extract the graph.**

A doc isn't just a file. It contains:
- Definitions (health indicators, validations, checkers)
- References (to code, to other docs, to concepts)
- Relationships (verifies, implements, blocks)
- Work items (TODOs, escalations, propositions)
- Metadata (priority, status, ownership)

All of this is structure. Dense clustering extracts it.

## Design Philosophy

### Everything Is a Node

If it's mentioned, it's a node.

| Mentioned | Node Type |
|-----------|-----------|
| "schema_compliance indicator" | narrative_HEALTH |
| "verifies V1" | narrative_VALIDATION (find or create) |
| "dock at check_health.py:272" | thing_DOCK |
| "@mind:todo Add physics checks" | narrative_TODO |
| "triggers: mind doctor" | narrative_CHECKER |

### Relationships Are Explicit

If there's a relationship, it's a link.

```
"schema_compliance verifies V1 and V6"
         │              │
         │              └── creates 2 links: verifies → V1, verifies → V6
         └── creates node: narrative_HEALTH_schema-compliance
```

### Dense Over Sparse

| Sparse | Dense |
|--------|-------|
| 1 node per doc | ~20-50 nodes per doc |
| Grep to find relationships | Query to find relationships |
| Structure in prose | Structure in graph |

We choose dense because **queryability >> storage cost**.

## Node Type Patterns

### From HEALTH Docs

| Content | Node Type | ID Pattern |
|---------|-----------|------------|
| Health indicator | narrative | `narrative_HEALTH_{name}` |
| Validation reference | narrative | `narrative_VALIDATION_{name}` |
| Dock (observation point) | thing | `thing_DOCK_{health}-{direction}` |
| Checker | narrative | `narrative_CHECKER_{name}` |
| Flow | narrative | `narrative_FLOW_{name}` |

### From Any Doc

| Content | Node Type | ID Pattern |
|---------|-----------|------------|
| The doc file | thing | `thing_FILE_{path-slug}` |
| TODO marker | narrative | `narrative_TODO_{slug}` |
| Escalation marker | narrative | `narrative_ESCALATION_{slug}` |
| Proposition marker | narrative | `narrative_PROPOSITION_{slug}` |
| Code reference | thing | `thing_FILE_{path}` or `thing_FUNC_{path}_{name}` |

## Link Type Patterns

| Relationship | Link Type | Direction Property |
|--------------|-----------|-------------------|
| Space contains node | contains | — |
| Health verifies validation | relates | verifies |
| Dock observes symbol | relates | observes |
| Checker implemented by file | relates | implemented_by |
| Health part of flow | relates | part_of |
| Doc references doc | relates | references |
| TODO about target | relates | about |
| Moment about created nodes | about | — |
| Actor expresses moment | expresses | — |

## Extraction Principles

### 1. Parse, Don't Guess

Use explicit structure:
- YAML blocks for definitions
- Markers for work items (`@mind:todo`, `@mind:escalation`)
- Headers for sections
- Links for references

### 2. Resolve References

When doc says "verifies V1":
1. Check if `narrative_VALIDATION_V1` exists
2. If yes, link to it
3. If no, create it (minimal node)
4. Create link: `health -[verifies]-> validation`

### 3. Upsert, Not Duplicate

Same doc ingested twice:
- Updates existing nodes (if changed)
- Creates new nodes (if new content)
- Never duplicates (MERGE by ID)

### 4. Record Provenance

Every extraction creates a moment:
```yaml
moment_INGEST_{doc}-{timestamp}:
  expresses ← actor_SYSTEM_doctor
  about → [all created/updated nodes]
```

## Scope

### In Scope

- HEALTH docs → health indicators, docks, checkers, flows
- VALIDATION docs → validation rules
- IMPLEMENTATION docs → code references
- Any doc → TODOs, escalations, propositions
- Any doc → doc chain links

### Out of Scope

- Prose summarization (we extract structure, not meaning)
- NLP-based relationship detection (we use explicit markers)
- Cross-repo linking (future)

## Related

- OBJECTIVES_Dense_Clustering.md — Goals and priorities
- ALGORITHM_Dense_Clustering.md — Extraction procedures
- IMPLEMENTATION_Dense_Clustering.md — Code architecture
