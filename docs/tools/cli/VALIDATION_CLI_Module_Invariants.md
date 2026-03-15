# mind Framework CLI — Validation: Command Invariants

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

## INVARIANTS

- Commands must fail loudly on invalid arguments.
- Health checks must never be skipped when explicitly requested.
- Doc chain references must remain valid for CLI-owned docs.
