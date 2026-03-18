# Custom Senses — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Custom_Senses.md
PATTERNS:        ./PATTERNS_Custom_Senses.md
BEHAVIORS:       ./BEHAVIORS_Custom_Senses.md
THIS:            VALIDATION_Custom_Senses.md (you are here)
ALGORITHM:       ./ALGORITHM_Custom_Senses.md
IMPLEMENTATION:  ./IMPLEMENTATION_Custom_Senses.md
HEALTH:          ./HEALTH_Custom_Senses.md
SYNC:            ./SYNC_Custom_Senses.md
```

---

## PURPOSE

These invariants define what properties, if violated, would mean custom senses have failed their purpose as citizen-defined perception extensions. They protect the defining constraints: custom senses flow through the same gating as built-in channels, YAML parsing is safe, malformed definitions cannot crash the tick, and the system has zero overhead for citizens who do not use custom senses.

---

## INVARIANTS

### V1: Custom Stimuli Enter Standard Gating

**Why we care:** If custom senses inject stimuli directly into the output list (bypassing priority sort and channel gating), they could flood a citizen's attention and overwhelm the MAX_STIMULI_PER_TICK budget. The exteroception pipeline's attention management would be broken for any citizen using custom senses.

```
MUST:   Custom sense candidates are appended to the shared candidates list in tick()
MUST:   Candidates are sorted by priority together with built-in channel candidates
MUST:   The MAX_STIMULI_PER_TICK cap (3) applies to the combined set
NEVER:  Inject custom stimuli directly into the returned stimuli list
NEVER:  Create a separate output path for custom sense stimuli
```

### V2: Malformed Senses Cannot Crash the Tick

**Why we care:** One citizen creating a broken sense definition must not crash the exteroception tick for that citizen or any other. The tick is part of the physics loop, which must never stall (stated in OBJECTIVES as a success signal and as a guardrail in the citizen contract).

```
MUST:   YAML parsing errors are caught per-sense and logged at debug level
MUST:   Non-dict YAML results are silently skipped (isinstance check)
MUST:   Empty or null content fields are skipped before YAML parsing
MUST:   Filter evaluation errors (ValueError, TypeError) return False, not raise
NEVER:  Allow a single malformed sense to prevent other senses from loading
NEVER:  Allow a filter evaluation error to propagate to the tick() caller
```

### V3: Zero Overhead Without Custom Senses

**Why we care:** The vast majority of citizens will not have custom senses. If the custom sense system adds measurable latency to their tick, it degrades the entire system for a feature they do not use. The OBJECTIVES file states this explicitly as a success signal.

```
MUST:   _load_custom_senses executes one graph query that returns empty when no links exist
MUST:   _evaluate_custom_senses returns immediately when _custom_senses list is empty
MUST:   No additional processing (no YAML parsing, no Cypher building, no filter evaluation) for zero-sense citizens
NEVER:  Add per-tick overhead (beyond the empty-list check) for citizens without ->perceives_with-> links
```

### V4: Sense Count Is Bounded

**Why we care:** A citizen could theoretically create hundreds of `->perceives_with->` links. Without a cap, each tick would execute hundreds of graph queries (one per sense), causing the tick to exceed the 1-second physics budget. The LIMIT 10 in the loading query is the structural cap.

```
MUST:   The loading query uses LIMIT 10 to cap loaded senses
MUST:   At most 10 SensoryChannel instances are registered per citizen for custom senses
NEVER:  Remove the LIMIT from the loading query
NEVER:  Allow unbounded iteration in _evaluate_custom_senses
```

### V5: One Match Per Sense Per Tick

**Why we care:** Without the break-after-first-match constraint, a single sense scanning 20 nodes could produce up to 20 candidate tuples. With 10 senses, that is 200 candidates — dominating the priority sort and drowning out built-in channels. The one-match limit ensures fair competition.

```
MUST:   _evaluate_custom_senses breaks after the first matching node per sense
MUST:   A sense that matches produces exactly one candidate tuple
NEVER:  Allow a sense to produce multiple candidates from a single evaluation cycle
```

### V6: YAML Senses Do Not Execute Code

**Why we care:** Thing content fields contain user-defined YAML. If the system ever evaluates Python expressions from these fields (eval, exec, or function construction), it becomes a remote code execution vector. Custom senses are data, not programs.

```
MUST:   YAML content is parsed via yaml.safe_load() (not yaml.load())
MUST:   Filter evaluation uses only comparison operators and string containment
MUST:   Template substitution uses only str.replace() with {node.name} and {node.synthesis}
NEVER:  Call eval(), exec(), compile(), or __import__ on any data from Thing content fields
NEVER:  Use yaml.load() (unsafe) — always yaml.safe_load()
```

### V7: Channel Names Are Unique Per Sense

**Why we care:** If two senses share a channel name, their refractory periods would interfere — firing one sense would block the other. Channel names must be derived from the unique sense ID to guarantee isolation.

```
MUST:   Channel name format is "custom_{sense_id}" where sense_id is the Thing node ID
MUST:   Thing node IDs are unique in FalkorDB (guaranteed by the database)
MUST:   Channel registration checks for existence before creating (no duplicates)
NEVER:  Use the sense's human-readable name as the channel key
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
| V1 | Attention budget integrity (gating not bypassed) | CRITICAL |
| V2 | Tick stability (malformed senses cannot crash physics) | CRITICAL |
| V3 | Baseline performance (zero overhead without senses) | HIGH |
| V4 | Tick budget (bounded sense count) | HIGH |
| V5 | Fair competition (one match per sense per tick) | MEDIUM |
| V6 | Security (no code execution from YAML) | CRITICAL |
| V7 | Channel isolation (unique names per sense) | MEDIUM |

---

## MARKERS

<!-- @mind:todo Add invariant for Python sense sandboxing when v2 tier is designed — query_fn only, no imports, no filesystem -->
<!-- @mind:todo Consider whether the LIMIT 10 cap should be configurable or remain hardcoded -->
<!-- @mind:proposition V3 could be strengthened to require _load_custom_senses to be a no-op (not even a graph query) for citizens known to have no custom senses — but this would require pre-knowledge of the citizen's link topology -->
