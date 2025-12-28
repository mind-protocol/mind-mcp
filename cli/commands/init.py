"""mind init - Initialize .mind/ in a project directory."""

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
from ..helpers.get_mcp_version_from_config import get_mcp_version


def run(target_dir: Path, database: str = "falkordb") -> bool:
    """Initialize .mind/ in target directory."""
    graph_name = target_dir.name.lower().replace("-", "_").replace(" ", "_")

    copy_ecosystem_templates(target_dir)
    copy_runtime_package(target_dir)
    create_ai_config_files(target_dir)
    sync_skills_to_ai_tools(target_dir)
    create_database_config(target_dir, database, graph_name)
    setup_database(target_dir, database, graph_name)
    create_env_example(target_dir, database)
    create_mcp_config(target_dir)
    update_gitignore(target_dir)

    print(f"\n✓ mind initialized (v{get_mcp_version()}, {database})")
    return True
