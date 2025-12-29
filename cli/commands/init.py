"""mind init - Initialize .mind/ in a project directory."""

from datetime import datetime
from pathlib import Path

from ..helpers.copy_ecosystem_templates_to_target import copy_ecosystem_templates
from ..helpers.copy_capabilities_to_target import copy_capabilities
from ..helpers.copy_runtime_package_to_target import copy_runtime_package
from ..helpers.create_ai_config_files_for_claude_agents_gemini import create_ai_config_files
from ..helpers.sync_skills_to_ai_tool_directories import sync_skills_to_ai_tools
from ..helpers.create_database_config_yaml import create_database_config
from ..helpers.setup_database_and_apply_schema import setup_database
from ..helpers.create_env_example_file import create_env_example
from ..helpers.create_mcp_config_json import create_mcp_config
from ..helpers.update_gitignore_with_runtime_entry import update_gitignore
from ..helpers.ingest_repo_files_to_graph import ingest_repo_files
from ..helpers.ingest_capabilities_to_graph import ingest_capabilities
from ..helpers.inject_agents_to_graph import inject_agents
from ..helpers.generate_repo_overview_maps import generate_overview
from ..helpers.generate_embeddings_for_graph_nodes import generate_embeddings
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

    # 2. Capabilities
    print("\n## Capabilities")
    copy_capabilities(target_dir)
    steps.append("capabilities")

    # 3. Runtime package
    print("\n## Runtime")
    copy_runtime_package(target_dir)
    steps.append("runtime")

    # 4. AI config files
    print("\n## AI Configs")
    create_ai_config_files(target_dir)
    steps.append("ai_configs")

    # 5. Skills sync
    print("\n## Skills")
    sync_skills_to_ai_tools(target_dir)
    steps.append("skills")

    # 6. Database config
    print("\n## Database Config")
    create_database_config(target_dir, database, graph_name)
    steps.append("database_config")

    # 7. Database setup
    print("\n## Database Setup")
    setup_database(target_dir, database, graph_name)
    steps.append("database_setup")

    # 8. File ingestion (creates Spaces and Things from repo files)
    print("\n## File Ingestion")
    ingest_repo_files(target_dir, graph_name)
    steps.append("file_ingest")

    # 9. Capability graph injection (creates capability spaces, tasks, skills, procedures)
    print("\n## Capability Graph")
    ingest_capabilities(target_dir, graph_name)
    steps.append("capabilities_graph")

    # 11. Env example
    print("\n## Environment")
    create_env_example(target_dir, database)
    steps.append("env_example")

    # 12. MCP config
    print("\n## MCP Server")
    create_mcp_config(target_dir)
    steps.append("mcp_config")

    # 13. Gitignore
    print("\n## Gitignore")
    update_gitignore(target_dir)
    steps.append("gitignore")

    # 14. Overview (generates map.md files)
    print("\n## Overview")
    generate_overview(target_dir)
    steps.append("overview")

    # 15. Embeddings (with progress bar)
    print("\n## Embeddings")
    generate_embeddings(graph_name)
    steps.append("embeddings")

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
