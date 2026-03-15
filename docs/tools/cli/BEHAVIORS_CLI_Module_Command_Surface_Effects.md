# mind Framework CLI — Behaviors: Command Surface Effects

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

## BEHAVIORS

- Each command returns a deterministic exit code (0 success, 1 failure).
- Output is structured to be readable by humans and parsable by agents.
- Health-related commands surface issues without hiding failures.
