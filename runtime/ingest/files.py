"""
File ingestion for the mind graph.

Scans repository files and creates Thing nodes in the graph.

DOCS: docs/ingest/PATTERNS_File_Ingestion.md
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

# Skip directories that should never be scanned
SKIP_DIRS = {
    '.git', '.mind', '__pycache__', '.venv', 'venv',
    'node_modules', '.next', 'dist', 'build', '.cache',
    '.pytest_cache', '.mypy_cache', 'coverage', '.tox',
    '.idea', '.vscode', 'egg-info',
}

# File extensions to include
INCLUDE_EXTENSIONS = {
    # Code
    '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.kt', '.rb',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.swift', '.scala', '.clj',
    # Config
    '.yaml', '.yml', '.json', '.toml', '.ini', '.cfg',
    # Docs
    '.md', '.rst', '.txt',
    # Web
    '.html', '.css', '.scss', '.less',
    # Data
    '.sql', '.graphql',
}


def scan_and_ingest_files(
    target_dir: Path,
    graph_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scan repository and ingest files as Thing nodes.

    Creates:
    - Space nodes for directories (AREA, MODULE)
    - Thing nodes for files
    - LINK edges: Space --contains--> Thing
    - Embeddings for all nodes with synthesis

    Args:
        target_dir: Repository root
        graph_name: Graph to ingest into (default: from config)

    Returns:
        Stats dict: {files_scanned, things_created, spaces_created, ...}
    """
    from ..infrastructure.database import get_database_adapter
    from ..doctor_files import should_ignore_path, is_binary_file, load_doctor_config

    # Load config for ignore patterns
    config = load_doctor_config(target_dir)
    ignore_patterns = config.ignore if hasattr(config, 'ignore') else []

    # Get database adapter
    adapter = get_database_adapter(graph_name=graph_name)

    stats = {
        "files_scanned": 0,
        "things_created": 0,
        "things_updated": 0,
        "spaces_created": 0,
        "links_created": 0,
        "areas": set(),
        "modules": set(),
        "errors": [],
    }

    # Track created spaces to avoid duplicates
    created_spaces: Set[str] = set()

    def _ensure_space(space_id: str, name: str, space_type: str) -> None:
        """Create Space node if not exists."""
        if space_id in created_spaces:
            return

        # Check if exists in DB
        result = adapter.query(
            "MATCH (s:Space {id: $id}) RETURN s.id",
            {"id": space_id}
        )
        if result:
            created_spaces.add(space_id)
            return

        # Create Space node
        adapter.execute(
            """
            CREATE (s:Space {
                id: $id,
                name: $name,
                type: $type,
                synthesis: $synthesis
            })
            """,
            {
                "id": space_id,
                "name": name,
                "type": space_type,
                "synthesis": f"{space_type}: {name}",
            }
        )
        created_spaces.add(space_id)
        stats["spaces_created"] += 1
        if space_type == "area":
            stats["areas"].add(name)
        else:
            stats["modules"].add(name)

    def _create_thing(rel_path: str, parent_space_id: str) -> None:
        """Create Thing node and link to parent Space."""
        thing_id = f"thing:{rel_path}"
        filename = Path(rel_path).name
        file_ext = Path(rel_path).suffix.lower()

        # Determine file type
        if file_ext in {'.py', '.js', '.ts', '.go', '.rs', '.java'}:
            file_type = "code"
        elif file_ext in {'.md', '.rst', '.txt'}:
            file_type = "doc"
        elif file_ext in {'.yaml', '.yml', '.json', '.toml'}:
            file_type = "config"
        else:
            file_type = "file"

        # Generate synthesis from file content
        synthesis = _generate_synthesis(target_dir / rel_path, filename)

        # Upsert Thing node
        result = adapter.query(
            "MATCH (t:Thing {id: $id}) RETURN t.id",
            {"id": thing_id}
        )

        if result:
            # Update existing
            adapter.execute(
                """
                MATCH (t:Thing {id: $id})
                SET t.synthesis = $synthesis, t.file_type = $file_type
                """,
                {"id": thing_id, "synthesis": synthesis, "file_type": file_type}
            )
            stats["things_updated"] += 1
        else:
            # Create new
            adapter.execute(
                """
                CREATE (t:Thing {
                    id: $id,
                    name: $name,
                    path: $path,
                    file_type: $file_type,
                    synthesis: $synthesis
                })
                """,
                {
                    "id": thing_id,
                    "name": filename,
                    "path": rel_path,
                    "file_type": file_type,
                    "synthesis": synthesis,
                }
            )
            stats["things_created"] += 1

        # Create contains link
        adapter.execute(
            """
            MATCH (s:Space {id: $space_id})
            MATCH (t:Thing {id: $thing_id})
            MERGE (s)-[r:LINK {type: 'contains'}]->(t)
            ON CREATE SET r.hierarchy = -0.7, r.synthesis = 'contains'
            """,
            {"space_id": parent_space_id, "thing_id": thing_id}
        )
        stats["links_created"] += 1

    def _generate_synthesis(file_path: Path, filename: str) -> str:
        """Generate synthesis text from file content."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:2000]

            # Extract docstring/first comment
            if file_path.suffix == '.py':
                # Python docstring
                if content.startswith('"""') or content.startswith("'''"):
                    end_quote = '"""' if content.startswith('"""') else "'''"
                    end_idx = content.find(end_quote, 3)
                    if end_idx > 0:
                        return content[3:end_idx].strip()[:200]
                # Python comment
                lines = content.split('\n')
                for line in lines[:10]:
                    if line.strip().startswith('#') and not line.strip().startswith('#!'):
                        return line.strip()[1:].strip()[:200]

            elif file_path.suffix == '.md':
                # Markdown: first heading or first paragraph
                lines = content.split('\n')
                for line in lines[:5]:
                    if line.strip() and not line.startswith('#'):
                        return line.strip()[:200]
                    if line.startswith('# '):
                        return line[2:].strip()[:200]

            # Fallback: filename
            return filename

        except Exception:
            return filename

    def _scan_dir(directory: Path, depth: int = 0) -> None:
        """Recursively scan directory."""
        if depth > 10:
            return

        try:
            items = sorted(directory.iterdir())
        except PermissionError:
            return

        for item in items:
            # Skip hidden
            if item.name.startswith('.'):
                continue

            # Skip known dirs
            if item.is_dir() and item.name in SKIP_DIRS:
                continue

            # Check ignore patterns
            if should_ignore_path(item, ignore_patterns, target_dir):
                continue

            if item.is_dir():
                _scan_dir(item, depth + 1)

            elif item.is_file():
                # Skip binary
                if is_binary_file(item):
                    continue

                # Check extension
                if item.suffix.lower() not in INCLUDE_EXTENSIONS:
                    continue

                stats["files_scanned"] += 1

                try:
                    rel_path = item.relative_to(target_dir)
                    rel_path_str = str(rel_path)

                    # Determine space hierarchy
                    parts = rel_path.parts[:-1]

                    if not parts:
                        # Root level file
                        parent_id = "space:root"
                        _ensure_space(parent_id, "root", "module")
                    elif len(parts) == 1:
                        # Area level (e.g., engine/file.py)
                        area_id = f"space:area:{parts[0]}"
                        _ensure_space(area_id, parts[0], "area")
                        parent_id = area_id
                    else:
                        # Module level (e.g., engine/physics/file.py)
                        area_id = f"space:area:{parts[0]}"
                        module_name = f"{parts[0]}/{parts[1]}"
                        module_id = f"space:module:{module_name}"

                        _ensure_space(area_id, parts[0], "area")
                        _ensure_space(module_id, module_name, "module")

                        # Link area -> module
                        adapter.execute(
                            """
                            MATCH (a:Space {id: $area_id})
                            MATCH (m:Space {id: $module_id})
                            MERGE (a)-[r:LINK {type: 'contains'}]->(m)
                            ON CREATE SET r.hierarchy = -0.7
                            """,
                            {"area_id": area_id, "module_id": module_id}
                        )

                        parent_id = module_id

                    _create_thing(rel_path_str, parent_id)

                except Exception as e:
                    stats["errors"].append(f"{item}: {e}")
                    logger.warning(f"Error ingesting {item}: {e}")

    # Run scan
    _scan_dir(target_dir)

    # Convert sets to counts
    stats["areas_count"] = len(stats["areas"])
    stats["modules_count"] = len(stats["modules"])
    del stats["areas"]
    del stats["modules"]

    return stats


def _embed_all_nodes(adapter) -> int:
    """Embed all nodes that have synthesis but no embedding."""
    try:
        from ..infrastructure.embeddings.service import EmbeddingService

        embed_service = EmbeddingService()

        # Find all nodes without embeddings (Things, Spaces, Actors, etc.)
        result = adapter.query(
            """
            MATCH (n)
            WHERE n.embedding IS NULL AND (n.synthesis IS NOT NULL OR n.description IS NOT NULL)
            RETURN n.id, COALESCE(n.synthesis, n.description) as text
            """
        )

        if not result:
            return 0

        count = 0
        for row in result:
            node_id = row[0]
            text = row[1]

            if not text:
                continue

            embedding = embed_service.embed(text)
            if embedding:
                adapter.execute(
                    "MATCH (n {id: $id}) SET n.embedding = $embedding",
                    {"id": node_id, "embedding": embedding}
                )
                count += 1

        return count

    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return 0
