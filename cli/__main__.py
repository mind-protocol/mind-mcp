#!/usr/bin/env python3
"""
mind CLI — The Cognitive Membrane command line.

Usage:
    mind init [--mode project-team|universe|roleplay]
    mind status
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="mind", description="Mind Protocol — The Cognitive Membrane")
    subs = parser.add_subparsers(dest="command")

    p = subs.add_parser("init", help="Initialize .mind/ in a project directory")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())
    p.add_argument("--database", "-db", choices=["falkordb", "neo4j"], default="falkordb")
    p.add_argument("--mode", choices=["project-team", "universe", "roleplay"], default=None,
                   help="System prompt mode for CLAUDE.md (default: project-team)")

    p = subs.add_parser("status", help="Show project status")
    p.add_argument("--dir", "-d", type=Path, default=Path.cwd())

    args = parser.parse_args()

    if args.command == "init":
        from .commands.init import run
        ok = run(args.dir, database=args.database, mode=args.mode)
        sys.exit(0 if ok else 1)

    elif args.command == "status":
        try:
            from .commands.status import run
            code = run(args.dir)
            sys.exit(code)
        except ImportError:
            print("Status command not available")
            sys.exit(1)

    else:
        # Fall through to runtime CLI which has more commands
        try:
            from runtime.cli import main as runtime_main
            runtime_main()
        except Exception:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
