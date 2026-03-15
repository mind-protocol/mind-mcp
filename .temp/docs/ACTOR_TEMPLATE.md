# ACTOR: {Actor_Name}

## NODE

```yaml
node_type: actor
type: "{agent | mechanical | service}"
status: active
```

## PURPOSE

{Role in the system. What this actor does, why it exists.}

## CAPABILITIES

Tasks this actor can execute:

| Task | Description | Frequency |
|------|-------------|-----------|
| TASK_{name} | {what it does} | {how often} |

## TRIGGERS

| Trigger type | Details |
|-------------|---------|
| Cron | {schedule, e.g., "every 5 min", "daily at 00:00"} |
| Event | {event type that activates this actor} |
| Manual | {how to invoke manually} |

## IMPLEMENTATION

| Aspect | Value |
|--------|-------|
| Code path | {file path, if mechanical} |
| Agent name | {agent subtype, if agent-executed} |
| MCP tools used | {list of membrane tools this actor calls} |

## SCHEMA INSTANCE

At initialization, this actor is represented as:

```yaml
node_type: actor
type: "{subtype}"
name: "{actor_name}"
synthesis: "{subtype}: {actor_name} — {purpose summary}"
```

### Links

| Direction | Target | relation_kind | Key dimensions |
|-----------|--------|---------------|----------------|
| serves → | {template narrative node} | instance_of | hierarchy: 1.0, permanence: 1.0 |
| contained_by → | {space node} | relates_to | hierarchy: -0.7 |

## DRIVES (if agent type)

Default drive configuration for this actor's cognitive profile.

| Drive | Baseline | Intensity | Rationale |
|-------|----------|-----------|-----------|
| curiosity | {0-1} | {0-1} | {why this level} |
| care | {0-1} | {0-1} | {why} |
| achievement | {0-1} | {0-1} | {why} |
| self_preservation | {0-1} | {0-1} | {why} |

## GRAPH OPERATIONS

| Operation | Node type | Fields | Frequency |
|-----------|-----------|--------|-----------|
| {create/read/update} | {type} | {fields} | {per-tick / on-demand / etc.} |
