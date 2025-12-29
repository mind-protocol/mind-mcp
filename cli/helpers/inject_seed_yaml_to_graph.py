"""Inject seed-injection.yaml files into the graph during init."""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def inject_seed_yaml(target_dir: Path, graph_name: str) -> None:
    """
    Find and inject seed-injection.yaml files into the graph.

    Seed files provide the semantic structure:
    - Spaces (areas, modules)
    - Actors (human, system, agents)
    - Narratives (objectives, patterns)
    - Moments (bootstrap events)

    This should run BEFORE file ingestion so Things can link
    to existing Spaces.
    """
    try:
        from runtime.infrastructure.database import get_database_adapter
    except ImportError as e:
        print(f"⚠ Seed injection skipped: {e}")
        return

    # Find seed files
    docs_dir = target_dir / "docs"
    seed_files = _find_seed_files(docs_dir)

    if not seed_files:
        print("○ No seed-injection.yaml found")
        return

    # Get database adapter
    try:
        adapter = get_database_adapter(graph_name=graph_name)
    except Exception as e:
        print(f"⚠ Seed injection skipped: {e}")
        return

    total_nodes = 0
    total_links = 0

    for seed_file in seed_files:
        rel_path = seed_file.relative_to(target_dir)
        nodes, links = _inject_seed_file(adapter, seed_file)
        total_nodes += nodes
        total_links += links
        print(f"✓ {rel_path}: {nodes} nodes, {links} links")

    if total_nodes > 0 or total_links > 0:
        print(f"✓ Total: {total_nodes} nodes, {total_links} links")

    # Inject git info if .git exists (user, repo)
    git_nodes, git_links = _inject_git_info(target_dir, adapter)
    if git_nodes > 0:
        print(f"✓ Git info: {git_nodes} nodes, {git_links} links")


def _inject_git_info(target_dir: Path, adapter) -> Tuple[int, int]:
    """
    Create nodes from git config if .git exists.

    Creates:
    - Human actor from user.name/user.email
    - Repo Thing with remote URL and name
    """
    git_dir = target_dir / ".git"
    if not git_dir.exists():
        return 0, 0

    nodes_created = 0
    links_created = 0

    # Get git info
    user_name = _git_config("user.name", target_dir)
    user_email = _git_config("user.email", target_dir)
    remote_url = _git_config("remote.origin.url", target_dir)
    repo_name = target_dir.name

    # Create human actor if user.name exists
    if user_name:
        actor_id = f"actor_human_{user_name.lower().replace(' ', '_').replace('-', '_')}"

        node = {
            "id": actor_id,
            "node_type": "actor",
            "type": "human",
            "name": user_name,
            "email": user_email,
            "description": f"Human developer: {user_name}" + (f" <{user_email}>" if user_email else ""),
            "weight": 10.0,
            "energy": 0.0,
        }
        if _upsert_node(adapter, node):
            nodes_created += 1

        # Link human to root
        link = {
            "id": f"inhabits_{actor_id}_root",
            "node_a": actor_id,
            "node_b": "space:root",
            "nature": "inhabits",
            "weight": 1.0,
            "name": "present",
            "description": f"{user_name} present in codebase",
        }
        if _upsert_link(adapter, link):
            links_created += 1

    # Create repo Thing with git info
    repo_node = {
        "id": "thing_repo",
        "node_type": "thing",
        "type": "repository",
        "name": repo_name,
        "url": remote_url,
        "weight": 5.0,
        "energy": 0.0,
    }

    # Try to get more info from GitHub/GitLab API if public
    if remote_url:
        api_info = _fetch_repo_api_info(remote_url)
        if api_info:
            repo_node.update(api_info)

    # Set description if not from API
    if "description" not in repo_node or not repo_node["description"]:
        repo_node["description"] = f"Repository: {repo_name}" + (f" ({remote_url})" if remote_url else "")

    if _upsert_node(adapter, repo_node):
        nodes_created += 1

    # Link repo to root space
    repo_link = {
        "id": "belongs_repo_root",
        "node_a": "thing_repo",
        "node_b": "space:root",
        "nature": "belongs to",
        "weight": 1.0,
        "name": "repository",
        "description": f"{repo_name} repository metadata",
    }
    if _upsert_link(adapter, repo_link):
        links_created += 1

    return nodes_created, links_created


def _git_config(key: str, cwd: Path) -> Optional[str]:
    """Read a value from git config."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _parse_github_url(url: str) -> Optional[Tuple[str, str]]:
    """Parse GitHub URL to extract owner and repo name."""
    import re

    # Handle various GitHub URL formats
    patterns = [
        r"github\.com[:/]([^/]+)/([^/\.]+?)(?:\.git)?$",  # git@ or https://
        r"github\.com/([^/]+)/([^/]+?)/?$",  # web URL
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)

    return None


def _fetch_repo_api_info(remote_url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch repository info from GitHub API if public.

    Returns dict with: description, topics, license, stars, forks,
    language, created_at, updated_at, default_branch
    """
    import urllib.request
    import json

    parsed = _parse_github_url(remote_url)
    if not parsed:
        return None

    owner, repo = parsed
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        req = urllib.request.Request(
            api_url,
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "mind-mcp"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        info = {}

        # Basic info
        if data.get("description"):
            info["description"] = data["description"]
        if data.get("homepage"):
            info["homepage"] = data["homepage"]
        if data.get("language"):
            info["language"] = data["language"]
        if data.get("default_branch"):
            info["default_branch"] = data["default_branch"]

        # Metrics
        if data.get("stargazers_count") is not None:
            info["stars"] = data["stargazers_count"]
        if data.get("forks_count") is not None:
            info["forks"] = data["forks_count"]
        if data.get("open_issues_count") is not None:
            info["open_issues"] = data["open_issues_count"]

        # License
        if data.get("license") and data["license"].get("spdx_id"):
            info["license"] = data["license"]["spdx_id"]

        # Topics
        if data.get("topics"):
            info["topics"] = ", ".join(data["topics"])

        # Dates
        if data.get("created_at"):
            info["created_at"] = data["created_at"]
        if data.get("pushed_at"):
            info["last_push"] = data["pushed_at"]

        # Visibility
        info["visibility"] = "public" if not data.get("private") else "private"

        return info if info else None

    except Exception:
        # API call failed (private repo, rate limited, network error)
        return None


def _find_seed_files(docs_dir: Path) -> List[Path]:
    """Find all seed-injection.yaml files in docs/."""
    if not docs_dir.exists():
        return []

    seed_files = []
    for pattern in ["seed-injection.yaml", "seed-injection.yml"]:
        seed_files.extend(docs_dir.rglob(pattern))

    return sorted(seed_files)


def _inject_seed_file(adapter, seed_file: Path) -> tuple:
    """Inject a single seed file, return (nodes_count, links_count)."""
    try:
        import yaml
    except ImportError:
        return 0, 0

    try:
        with open(seed_file) as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"  ⚠ Failed to parse: {e}")
        return 0, 0

    if not data:
        return 0, 0

    nodes = data.get("nodes", [])
    links = data.get("links", [])

    nodes_created = 0
    links_created = 0

    # Upsert nodes
    for node in nodes:
        if _upsert_node(adapter, node):
            nodes_created += 1

    # Upsert links
    for link in links:
        if _upsert_link(adapter, link):
            links_created += 1

    return nodes_created, links_created


def _upsert_node(adapter, node: Dict[str, Any]) -> bool:
    """Upsert a node into the graph."""
    node_id = node.get("id")
    node_type = node.get("node_type", "thing")

    if not node_id:
        return False

    # Map node_type to label
    label_map = {
        "actor": "Actor",
        "space": "Space",
        "thing": "Thing",
        "narrative": "Narrative",
        "moment": "Moment",
    }
    label = label_map.get(node_type, "Thing")

    # Build properties (exclude node_type from props)
    props = {k: v for k, v in node.items() if k != "node_type" and v is not None}

    # Handle multiline content
    if "content" in props and isinstance(props["content"], str):
        props["content"] = props["content"].replace("'", "\\'").replace("\n", "\\n")

    try:
        # Build MERGE query
        props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
        query = f"MERGE (n:{label} {{id: $id}}) SET n += {{{props_str}}} RETURN n.id"
        adapter.execute(query, props)
        return True
    except Exception:
        return False


def _upsert_link(adapter, link: Dict[str, Any]) -> bool:
    """Upsert a link into the graph."""
    node_a = link.get("node_a")
    node_b = link.get("node_b")

    if not node_a or not node_b:
        return False

    # Build properties (exclude structural fields)
    exclude = {"node_a", "node_b", "nature"}
    props = {k: v for k, v in link.items() if k not in exclude and v is not None}

    # Parse nature to floats if link_vocab available
    nature = link.get("nature")
    if nature:
        try:
            from runtime.physics.link_vocab import nature_to_floats
            floats = nature_to_floats(nature)
            for key, value in floats.items():
                if key not in props and value is not None:
                    if key == "polarity":
                        props["polarity_ab"] = value[0]
                        props["polarity_ba"] = value[1]
                    else:
                        props[key] = value
        except ImportError:
            # No link_vocab, just store nature as string
            props["nature"] = nature

    # Remove None values
    props = {k: v for k, v in props.items() if v is not None}

    try:
        if props:
            props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
            query = f"""
            MATCH (a {{id: $node_a}})
            MATCH (b {{id: $node_b}})
            MERGE (a)-[r:LINK]->(b)
            SET r += {{{props_str}}}
            RETURN type(r)
            """
        else:
            query = """
            MATCH (a {id: $node_a})
            MATCH (b {id: $node_b})
            MERGE (a)-[r:LINK]->(b)
            RETURN type(r)
            """

        params = {"node_a": node_a, "node_b": node_b, **props}
        adapter.execute(query, params)
        return True
    except Exception:
        return False
