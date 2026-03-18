#!/usr/bin/env python3
"""
Create Thing nodes in lumina-prime for Telegram forum topics.

Telegram channels are communication tools (Things), not physical spaces.
Spaces are reserved for physical/spatial locations (districts, rooms, portals).

Usage:
    python3 scripts/create_tg_spaces.py "General:1" "Shipped:301460" "Announcements:2"

Each argument is "TopicName:ThreadID".
Creates Thing nodes with:
    id:             space:telegram:{chat_id}:{thread_id}
    name:           topic name
    node_type:      thing
    type:           channel
    platform_hint:  telegram_forum_topic
    platform_id:    thread_id (str)
    parent_chat_id: -1001699255893  (@mindprotocol_ai supergroup)
    url:            https://t.me/mindprotocol_ai/{thread_id}

Note: IDs keep the space: prefix for backwards compatibility with existing links.
"""

import sys
from falkordb import FalkorDB

PARENT_CHAT_ID = "-1001699255893"  # @mindprotocol_ai supergroup
TG_GROUP_HANDLE = "mindprotocol_ai"
GRAPH_NAME = "lumina-prime"


def create_tg_channels(topics: list[tuple[str, str]]):
    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph(GRAPH_NAME)

    created = 0
    for name, thread_id in topics:
        space_id = f"space:telegram:{PARENT_CHAT_ID}:{thread_id}"
        url = f"https://t.me/{TG_GROUP_HANDLE}/{thread_id}"

        g.query(
            """
            MERGE (s:Thing {id: $space_id})
            SET s.name = $name,
                s.node_type = 'thing',
                s.type = 'channel',
                s.platform_hint = 'telegram_forum_topic',
                s.platform_id = $thread_id,
                s.parent_chat_id = $parent_chat_id,
                s.url = $url
            """,
            {
                "space_id": space_id,
                "name": name,
                "thread_id": thread_id,
                "parent_chat_id": PARENT_CHAT_ID,
                "url": url,
            },
        )
        created += 1
        print(f"  MERGE {name} (thread {thread_id})")

    print(f"\nCreated/updated {created} Telegram forum topic Thing nodes.")

    # Summary
    print("\n--- Channel summary ---")
    result = g.query(
        "MATCH (s:Thing) WHERE s.type = 'channel' RETURN s.platform_hint, count(s) ORDER BY count(s) DESC"
    )
    for row in result.result_set:
        print(f"  {row[0]}: {row[1]} channels")


def parse_args(args: list[str]) -> list[tuple[str, str]]:
    """Parse 'Name:ThreadID' arguments into (name, thread_id) tuples."""
    topics = []
    for arg in args:
        if ":" not in arg:
            print(f"  SKIP invalid arg (no colon): {arg}", file=sys.stderr)
            continue
        # Split on LAST colon to allow colons in topic names
        idx = arg.rfind(":")
        name = arg[:idx].strip()
        thread_id = arg[idx + 1 :].strip()
        if not name or not thread_id:
            print(f"  SKIP empty name or thread_id: {arg}", file=sys.stderr)
            continue
        topics.append((name, thread_id))
    return topics


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    topics = parse_args(sys.argv[1:])
    if not topics:
        print("No valid topics provided.", file=sys.stderr)
        sys.exit(1)

    create_tg_channels(topics)
