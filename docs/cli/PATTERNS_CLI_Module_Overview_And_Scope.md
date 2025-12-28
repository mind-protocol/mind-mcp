# mind Framework CLI — Patterns: Command Surface Overview and Scope

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_CLI_Module_Overview_And_Scope.md
BEHAVIORS:       ./BEHAVIORS_CLI_Module_Command_Surface_Effects.md
ALGORITHM:       ./ALGORITHM_CLI_Command_Execution_Logic.md
VALIDATION:      ./VALIDATION_CLI_Module_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_CLI_Code_Architecture.md
HEALTH:          ./HEALTH_CLI_Module_Verification.md
SYNC:            ./SYNC_CLI_Module_Current_State.md
```

---

## PURPOSE

The CLI is the operational entrypoint for the protocol. It owns argument parsing,
command routing, and consistent output for health and repair workflows.

## SCOPE

In scope:
- Argument parsing and command routing for `mind` commands.
- Coordination of protocol health, repair, and prompt generation flows.
- Dispatch to command modules with traceable exits.

Out of scope:
- Deep health logic (owned by doctor checks).
- Refactor mechanics (owned by `mind refactor` internals).
