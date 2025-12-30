#!/usr/bin/env python3
"""
mind CLI

Usage:
    mind init [--database falkordb|neo4j]
    mind status
    mind upgrade
    mind fix-embeddings [--dry-run]
    mind swarm --agents N
"""

import argparse
import sys
from pathlib import Path

from .commands import init, status, upgrade, fix_embeddings, swarm
from .helpers.show_upgrade_notice_if_available import show_upgrade_notice


def main():
    parser = argparse.ArgumentParser(prog="mind", description="Mind Protocol CLI")
    subs = parser.add_subparsers(dest="command")

    p = subs.add_parser("init", help="Initialize .mind/")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())
    p.add_argument("--database", "-db", choices=["falkordb", "neo4j"], default="falkordb")

    p = subs.add_parser("status", help="Show status")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    p = subs.add_parser("upgrade", help="Check for updates")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    p = subs.add_parser("fix-embeddings", help="Fix missing/mismatched embeddings")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())
    p.add_argument("--dry-run", action="store_true", help="Show what would be fixed")

    p = subs.add_parser("swarm", help="Run multiple agents in parallel")
    p.add_argument("--agents", "-n", type=int, default=0, help="Number of agents to spawn")
    p.add_argument("--status", action="store_true", help="Show swarm status")
    p.add_argument("--stop", action="store_true", help="Stop all agents")
    p.add_argument("--stream", action="store_true", help="Stream moments live")
    p.add_argument("--logs", action="store_true", help="Tail log files")
    p.add_argument("--log-file", type=str, default=None, help="Custom log file path")

    args = parser.parse_args()

    if args.command == "init":
        ok = init.run(args.dir, database=args.database)
        show_upgrade_notice()
        sys.exit(0 if ok else 1)

    elif args.command == "status":
        code = status.run(args.dir)
        show_upgrade_notice()
        sys.exit(code)

    elif args.command == "upgrade":
        ok = upgrade.run(args.dir)
        sys.exit(0 if ok else 1)

    elif args.command == "fix-embeddings":
        ok = fix_embeddings.run(args.dir, dry_run=args.dry_run)
        sys.exit(0 if ok else 1)

    elif args.command == "swarm":
        swarm.run(
            agents=args.agents,
            status=args.status,
            stop=args.stop,
            stream=args.stream,
            logs=args.logs,
            log_file=args.log_file,
        )
        sys.exit(0)

    else:
        parser.print_help()
        show_upgrade_notice()
        sys.exit(1)


if __name__ == "__main__":
    main()
