#!/usr/bin/env python3
"""
mind CLI

Usage:
    mind init [--database falkordb|neo4j]
    mind status
    mind upgrade
    mind fix-embeddings [--dry-run]
"""

import argparse
import sys
from pathlib import Path

from .commands import init, status, upgrade, fix_embeddings
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

    else:
        parser.print_help()
        show_upgrade_notice()
        sys.exit(1)


if __name__ == "__main__":
    main()
