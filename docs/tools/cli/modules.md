# CLI Modules

This map helps agents navigate the command-level documentation under `docs/cli`.

| Module | Description | Canonical doc chain |
|--------|-------------|---------------------|
| **CLI core** | Framework-level guidance, architecture, health, and tooling decisions that apply across all commands. | `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md` → `docs/cli/core/BEHAVIORS_CLI_Command_Effects.md` → `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md` (canonical init/validate/doctor/repair/markers/refactor/docs-fix algorithms) → `docs/cli/core/VALIDATION_CLI_Instruction_Invariants.md` → `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md` → `docs/cli/core/HEALTH_CLI_Command_Test_Coverage.md` → `docs/cli/core/SYNC_CLI_Development_State.md` |
| **Prompt** | Bootstraps agents with `.mind` paths, views, and checklist instructions. | `docs/cli/prompt/PATTERNS_Prompt_Command_Workflow_Design.md` → … → `docs/cli/prompt/SYNC_Prompt_Command_State.md` |
| **Doctor** | Health diagnostics for the entire project (see `docs/mcp-design/doctor`). | `docs/mcp-design/doctor/PATTERNS_Project_Health_Doctor.md` → … → `docs/mcp-design/doctor/SYNC_Project_Health_Doctor.md` |
| **Repair, Sync, Validate, etc.** | General notes appear in CLI core or in their respective command directories if they get their own PATTERNS/…/SYNC chain. | Refer to `docs/cli/core/` for shared guidance, plus the per-module VIEW files under `.mind/views/`. |
| **CLI refactor** | Keeps module/docs paths and modules.yaml consistent after renames/moves and re-runs overview/doctor as proof. | `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md` (refactor section shares the CLI core chain) |
