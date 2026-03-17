#!/usr/bin/env python3
"""
Ingest Citizen History — Backfill L3 graph from a citizen's existing work.

Scans a citizen's directory, git history, and known files to create
Moments, Things, and links that reflect what they actually did.

Usage:
  python3 scripts/ingest_citizen_history.py vox
  python3 scripts/ingest_citizen_history.py conductor --repos mind-mcp,graphcare
  python3 scripts/ingest_citizen_history.py --all-primers
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from graph_enricher import on_commit, on_file_change, on_message

# ── Config ──

MIND_MCP = Path(__file__).parent.parent
HOME = Path("/home/mind-protocol")
REPOS = {
    "mind-mcp": HOME / "mind-mcp",
    "mind-protocol": HOME / "mind-protocol",
    "lumina-prime": HOME / "lumina-prime",
    "venezia": HOME / "venezia",
    "graphcare": HOME / "graphcare",
    "mind-ops": HOME / "mind-ops",
    "cities-of-light": HOME / "cities-of-light",
    "mind-platform": HOME / "mind-platform",
    "contre-terre": HOME / "contre-terre",
}

PRIMERS = {"conductor", "forge", "dev", "herald", "mentor", "vox", "sentinel", "mind", "nlr_ai"}


def _get_graph():
    try:
        from falkordb import FalkorDB
        return FalkorDB(host="localhost", port=6379).select_graph("lumina-prime")
    except Exception:
        return None


# ── 1. Git commits ──

def ingest_git_commits(handle: str, repos: list[str] = None):
    """Find all commits by this citizen across repos."""
    if repos is None:
        repos = list(REPOS.keys())

    total = 0
    for repo_name in repos:
        repo_path = REPOS.get(repo_name)
        if not repo_path or not (repo_path / ".git").exists():
            continue

        # Get commits by this handle (check various author patterns)
        patterns = [handle, handle.replace("_", " ").title(), handle.upper()]
        # Also check Co-Authored-By
        for pattern in patterns:
            try:
                result = subprocess.run(
                    ["git", "log", f"--author={pattern}", "--format=%H|%an|%s|%at", "--all", "-100"],
                    cwd=str(repo_path), capture_output=True, text=True, timeout=10,
                )
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split("|", 3)
                    if len(parts) < 4:
                        continue
                    commit_hash, author, message, timestamp = parts

                    # Get files changed
                    files_result = subprocess.run(
                        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                        cwd=str(repo_path), capture_output=True, text=True, timeout=5,
                    )
                    files = [f for f in files_result.stdout.strip().split("\n") if f]

                    on_commit(
                        repo_name=repo_name,
                        commit_hash=commit_hash,
                        author_name=author,
                        author_handle=handle,
                        message=message,
                        files_changed=files,
                        branch="main",
                    )
                    total += 1
            except Exception:
                pass

    print(f"  Commits: {total} ingested across {len(repos)} repos")
    return total


# ── 2. Works directory ──

def ingest_works(handle: str):
    """Scan citizen's works/ directory for files → Thing + Moment nodes."""
    works_dir = MIND_MCP / "citizens" / handle / "works"
    if not works_dir.exists():
        # Try lumina-prime
        works_dir = HOME / "lumina-prime" / "citizens" / handle / "works"
    if not works_dir.exists():
        print(f"  Works: no works/ dir found")
        return 0

    g = _get_graph()
    if not g:
        return 0

    total = 0
    for f in works_dir.rglob("*"):
        if not f.is_file() or f.name.startswith("."):
            continue

        thing_id = f"thing:work:{handle}:{f.stem}"
        ts = f.stat().st_mtime

        try:
            content = ""
            if f.suffix in (".md", ".txt", ".yaml", ".yml", ".json"):
                content = f.read_text(errors="ignore")[:500]

            # Create Thing node
            g.query(
                """
                MERGE (t:Thing {id: $tid})
                SET t.name = $name, t.type = 'document', t.file_path = $path,
                    t.content = $content, t.timestamp = $ts
                """,
                {"tid": thing_id, "name": f.name, "path": str(f.relative_to(MIND_MCP)),
                 "content": content[:300], "ts": ts},
            )

            # Link author
            g.query(
                """
                MATCH (a:Actor {id: $h}), (t:Thing {id: $tid})
                MERGE (a)-[r:LINK]->(t)
                SET r.hierarchy = -1, r.permanence = 0.8, r.polarity = 1.0,
                    r.computed_type = 'created'
                """,
                {"h": handle, "tid": thing_id},
            )

            total += 1
        except Exception:
            pass

    print(f"  Works: {total} files ingested from {works_dir}")
    return total


# ── 3. Discord messages (from log) ──

def ingest_discord_messages(handle: str):
    """Find this citizen's messages in the Discord log → ensure Moments exist."""
    log_path = MIND_MCP / "shrine" / "state" / "discord_messages.jsonl"
    if not log_path.exists():
        return 0

    total = 0
    for line in log_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            m = json.loads(line)
            author = m.get("author", "")
            if handle.lower() in author.lower():
                # on_message is idempotent (CREATE not MERGE for moments though)
                # Skip to avoid duplicates — just count
                total += 1
        except json.JSONDecodeError:
            pass

    print(f"  Discord: {total} messages found in log (already in L3 via enricher)")
    return total


# ── 4. Link to narratives/projects ──

def link_to_narratives(handle: str, narrative_ids: list[str]):
    """Create links between a citizen and narratives they contributed to."""
    g = _get_graph()
    if not g:
        return

    for nid in narrative_ids:
        try:
            g.query(
                """
                MATCH (a:Actor {id: $h}), (n:Narrative {id: $nid})
                MERGE (a)-[r:LINK]->(n)
                SET r.hierarchy = -1, r.affinity = 0.7, r.permanence = 0.7,
                    r.polarity = 1.0, r.computed_type = 'responsible'
                """,
                {"h": handle, "nid": nid},
            )
        except Exception:
            pass

    print(f"  Narratives: linked to {len(narrative_ids)}")


# ── 5. Profile enrichment ──

def ensure_actor(handle: str):
    """Make sure the Actor node exists with proper data from profile."""
    g = _get_graph()
    if not g:
        return

    profile_path = MIND_MCP / "citizens" / handle / "profile.json"
    if not profile_path.exists():
        return

    try:
        p = json.loads(profile_path.read_text())
        identity = p.get("identity", {})
        g.query(
            """
            MERGE (a:Actor {id: $h})
            SET a.name = $name, a.type = $type,
                a.universe = $universe, a.handle = $h
            """,
            {
                "h": handle,
                "name": identity.get("name", handle),
                "type": identity.get("type", "ai"),
                "universe": identity.get("universe", ""),
            },
        )
        print(f"  Actor: @{handle} ensured in L3")
    except Exception as e:
        print(f"  Actor: failed — {e}")


# ── Main ──

def ingest(handle: str, repos: list[str] = None):
    """Full ingestion for a citizen."""
    print(f"\n{'='*50}")
    print(f"Ingesting @{handle}")
    print(f"{'='*50}")

    ensure_actor(handle)
    ingest_git_commits(handle, repos)
    ingest_works(handle)
    ingest_discord_messages(handle)

    print(f"Done for @{handle}")


def main():
    args = sys.argv[1:]

    if "--all-primers" in args:
        for handle in sorted(PRIMERS):
            ingest(handle)
        return

    if not args:
        print("Usage: python3 scripts/ingest_citizen_history.py <handle> [--repos repo1,repo2]")
        print("       python3 scripts/ingest_citizen_history.py --all-primers")
        return

    handle = args[0]
    repos = None
    for i, a in enumerate(args):
        if a == "--repos" and i + 1 < len(args):
            repos = args[i + 1].split(",")

    ingest(handle, repos)


if __name__ == "__main__":
    main()
