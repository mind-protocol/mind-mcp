#!/bin/bash
# Install this as .git/hooks/post-commit in any Mind Protocol repo.
# It calls graph_enricher to create L3 nodes for every commit.

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
COMMIT_HASH="$(git rev-parse HEAD)"
AUTHOR_NAME="$(git log -1 --format='%an')"
COMMIT_MSG="$(git log -1 --format='%s')"
BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
FILES_CHANGED="$(git diff-tree --no-commit-id --name-only -r HEAD | head -50)"

MIND_MCP="${MIND_MCP_ROOT:-/home/mind-protocol/mind-mcp}"

python3 - <<PYEOF
import sys
sys.path.insert(0, "${MIND_MCP}/scripts")
sys.path.insert(0, "${MIND_MCP}")
try:
    from graph_enricher import on_commit, on_file_change
    files = [f for f in """${FILES_CHANGED}""".strip().split("\n") if f]
    author_handle = """${AUTHOR_NAME}""".lower().replace(" ", "_")
    on_commit(
        repo_name="${REPO_NAME}",
        commit_hash="${COMMIT_HASH}",
        author_name="${AUTHOR_NAME}",
        author_handle=author_handle,
        message="""${COMMIT_MSG}""",
        files_changed=files,
        branch="${BRANCH}",
    )
    for f in files:
        on_file_change("${REPO_NAME}", f, "modified", author_handle, "${COMMIT_HASH}")
    # Refresh repo stats on every commit (event-driven, no cron)
    from pathlib import Path
    stats_script = Path("/home/mind-protocol/mind-platform/scripts/generate_repo_stats.py")
    if stats_script.exists():
        import subprocess
        subprocess.Popen([sys.executable, str(stats_script)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass
PYEOF
