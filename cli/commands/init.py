"""mind init - Initialize .mind/ in a project directory."""

from datetime import datetime
from pathlib import Path

from ..helpers.copy_ecosystem_templates_to_target import copy_ecosystem_templates
from ..helpers.copy_runtime_package_to_target import copy_runtime_package
from ..helpers.create_ai_config_files_for_claude_agents_gemini import create_ai_config_files
from ..helpers.sync_skills_to_ai_tool_directories import sync_skills_to_ai_tools
from ..helpers.create_database_config_yaml import create_database_config
from ..helpers.setup_database_and_apply_schema import setup_database
from ..helpers.create_env_example_file import create_env_example
from ..helpers.create_mcp_config_json import create_mcp_config
from ..helpers.update_gitignore_with_runtime_entry import update_gitignore
from ..helpers.ingest_repo_files_to_graph import ingest_repo_files
from ..helpers.get_mcp_version_from_config import get_mcp_version


def run(target_dir: Path, database: str = "falkordb") -> bool:
    """Initialize .mind/ in target directory."""
    graph_name = target_dir.name.lower().replace("-", "_").replace(" ", "_")
    version = get_mcp_version()
    steps = []

    print(f"\n# mind init v{version}")
    print(f"Target: {target_dir}")
    print(f"Database: {database} (graph: {graph_name})")
    print()

    # 1. Ecosystem templates
    print("## Ecosystem")
    copy_ecosystem_templates(target_dir)
    steps.append("ecosystem")

    # 2. Runtime package
    print("\n## Runtime")
    copy_runtime_package(target_dir)
    steps.append("runtime")

    # 3. AI config files
    print("\n## AI Configs")
    create_ai_config_files(target_dir)
    steps.append("ai_configs")

    # 4. Skills sync
    print("\n## Skills")
    sync_skills_to_ai_tools(target_dir)
    steps.append("skills")

    # 5. Database config
    print("\n## Database Config")
    create_database_config(target_dir, database, graph_name)
    steps.append("database_config")

    # 6. Database setup
    print("\n## Database Setup")
    setup_database(target_dir, database, graph_name)
    steps.append("database_setup")

    # 7. File ingestion
    print("\n## File Ingestion")
    ingest_repo_files(target_dir, graph_name)
    steps.append("file_ingest")

    # 8. Env example
    print("\n## Environment")
    create_env_example(target_dir, database)
    steps.append("env_example")

    # 9. MCP config
    print("\n## MCP Server")
    create_mcp_config(target_dir)
    steps.append("mcp_config")

    # 10. Gitignore
    print("\n## Gitignore")
    update_gitignore(target_dir)
    steps.append("gitignore")

    # Write to SYNC file
    _update_sync_file(target_dir, version, database, graph_name, steps)

    print(f"\n---")
    print(f"✓ mind initialized (v{version}, {database}, graph: {graph_name})")
    print(f"✓ SYNC updated: .mind/state/SYNC_Project_State.md")
    return True


def _update_sync_file(target_dir: Path, version: str, database: str, graph_name: str, steps: list) -> None:
    """Append init record to SYNC file."""
    sync_file = target_dir / ".mind" / "state" / "SYNC_Project_State.md"

    if not sync_file.exists():
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"""
## Init: {timestamp}

| Setting | Value |
|---------|-------|
| Version | v{version} |
| Database | {database} |
| Graph | {graph_name} |

**Steps completed:** {", ".join(steps)}

---
"""

    # Append to SYNC file
    with open(sync_file, "a") as f:
        f.write(entry)
