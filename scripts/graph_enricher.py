"""
Graph Enricher — automatically create L3 nodes and :LINK relationships from message events.

All links use a SINGLE relationship type: :LINK with 13 dimensional properties
+ computed_type inferred from dimensions via infer_computed_type().

When someone posts or reads a channel:
  1. MERGE Space node for the channel
  2. MERGE Actor node for the poster
  3. Create Moment node for the message
  4. Link: Actor→Space (:LINK computed_type="presence")
  5. Link: Moment→Space (:LINK computed_type="occurred_in")
  6. Link: Actor→Moment (:LINK computed_type="created")
  7. Link: Moment→mentioned Actors (:LINK computed_type="mention")

Called by discord_bridge and telegram_bridge on every message event.

See: L3_LINK_DIMENSION_MAPPING.yaml for dimensional signatures.
"""

import hashlib
import logging
import re
import time
from typing import Optional

try:
    from mcp.tools.graph_write_handler import infer_computed_type
except ImportError:
    def infer_computed_type(*args, **kwargs):
        return "relates"

logger = logging.getLogger("mind.graph_enricher")

# ── Tier 1 extraction patterns (deterministic, no LLM) ──
_URL_PATTERN = re.compile(
    r'https?://[^\s<>\"\'\)\]]+', re.IGNORECASE
)
_TOKEN_PATTERN = re.compile(
    r'\$([A-Z]{2,10})\b'  # $MIND, $SOL, $ETH etc.
)
_PLATFORM_PATTERNS = {
    "email": re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),
    "phone": re.compile(r'\+\d{10,15}'),
    "linkedin": re.compile(r'linkedin\.com/in/[\w-]+'),
}

# Lazy graph connection
_graph = None
_graph_name = "lumina-prime"


def _get_graph():
    global _graph
    if _graph is not None:
        return _graph
    try:
        from falkordb import FalkorDB
        db = FalkorDB(host="localhost", port=6379)
        _graph = db.select_graph(_graph_name)
        logger.info(f"Graph enricher connected to {_graph_name}")
        return _graph
    except Exception as e:
        logger.debug(f"Graph enricher unavailable: {e}")
        return None


def _moment_id(content: str, author: str, ts: float) -> str:
    """Deterministic moment ID from content hash."""
    raw = f"{author}:{ts}:{content[:100]}"
    return "moment_" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _sanitize_handle(name: str) -> str:
    """Turn a display name into a safe graph ID."""
    clean = re.sub(r"[^\w\s]", "", name).strip()
    return re.sub(r"\s+", "_", clean).lower()[:40] or "unknown"


def _extract_urls(content: str) -> list[str]:
    """Extract URLs from message content."""
    return _URL_PATTERN.findall(content)


def _extract_tokens(content: str) -> list[str]:
    """Extract $TOKEN mentions from message content."""
    return _TOKEN_PATTERN.findall(content)


def _extract_platform_ids(content: str) -> dict[str, str]:
    """Extract platform identifiers (email, phone, linkedin) from content."""
    found = {}
    for platform_type, pattern in _PLATFORM_PATTERNS.items():
        match = pattern.search(content)
        if match:
            found[platform_type] = match.group(0)
    return found


def _enrich_things(g, moment_id: str, content: str, ts: float):
    """Tier 1: Create Thing nodes for URLs and $tokens found in content.

    URLs and tokens are deterministic — auto-created with status confirmed.
    Each Thing gets a :LINK(references) from the Moment.
    """
    ct_references = infer_computed_type(
        {"polarity": 0.5, "recency": ts}, "moment", "thing"
    )

    # URLs → Thing nodes
    for url in _extract_urls(content):
        thing_id = "thing_url_" + hashlib.sha256(url.encode()).hexdigest()[:12]
        try:
            g.query(
                """
                MERGE (t:Thing {id: $thing_id})
                ON CREATE SET t.name = $url, t.type = 'url',
                              t.content = $url, t.status = 'confirmed'
                """,
                {"thing_id": thing_id, "url": url},
            )
            g.query(
                """
                MATCH (m:Moment {id: $moment_id}), (t:Thing {id: $thing_id})
                CREATE (m)-[:LINK {polarity: 0.5, recency: $ts, computed_type: $ct}]->(t)
                """,
                {"moment_id": moment_id, "thing_id": thing_id, "ts": ts, "ct": ct_references},
            )
        except Exception as e:
            logger.debug(f"Thing URL creation failed for {url}: {e}")

    # $TOKEN → Thing nodes
    for token in _extract_tokens(content):
        thing_id = f"thing_token_{token.lower()}"
        try:
            g.query(
                """
                MERGE (t:Thing {id: $thing_id})
                ON CREATE SET t.name = $name, t.type = 'token',
                              t.content = $name, t.status = 'confirmed'
                """,
                {"thing_id": thing_id, "name": f"${token}"},
            )
            g.query(
                """
                MATCH (m:Moment {id: $moment_id}), (t:Thing {id: $thing_id})
                CREATE (m)-[:LINK {polarity: 0.5, recency: $ts, computed_type: $ct}]->(t)
                """,
                {"moment_id": moment_id, "thing_id": thing_id, "ts": ts, "ct": ct_references},
            )
        except Exception as e:
            logger.debug(f"Thing token creation failed for ${token}: {e}")


def _update_actor_platform(g, actor_id: str, platform: str, platform_user_id: str = ""):
    """Store platform handle on the Actor node for cross-platform matching.

    Platform fields: telegram_id, discord_id, x_handle, linkedin_url, email, phone.
    """
    if not platform_user_id:
        return

    field_map = {
        "telegram": "telegram_id",
        "discord": "discord_id",
        "twitter": "x_handle",
        "whatsapp": "whatsapp_id",
    }
    field = field_map.get(platform)
    if not field:
        return

    try:
        g.query(
            f"MATCH (a:Actor {{id: $actor_id}}) SET a.{field} = $platform_id",
            {"actor_id": actor_id, "platform_id": platform_user_id},
        )
    except Exception as e:
        logger.debug(f"Platform handle update failed for {actor_id}: {e}")


def on_message(
    platform: str,
    channel_id: str,
    channel_name: str,
    author_name: str,
    author_handle: str,
    content: str,
    mentioned_handles: Optional[list[str]] = None,
    direction: str = "in",
    is_pinned: bool = False,
):
    """Record a message event in the L3 graph.

    Args:
        platform: "discord" or "telegram"
        channel_id: Platform channel/chat ID
        channel_name: Human-readable channel name
        author_name: Display name of the author
        author_handle: Normalized handle (lowercase)
        content: Message text
        mentioned_handles: List of @handles mentioned in the message
        direction: "in" (received) or "out" (sent by citizen)
        is_pinned: Whether the message is pinned — boosts permanence and weight
    """
    g = _get_graph()
    if g is None:
        return

    ts = time.time()
    space_id = f"space:{platform}:{channel_id}"
    actor_id = author_handle or _sanitize_handle(author_name)
    moment_id = _moment_id(content, actor_id, ts)
    snippet = content[:300].replace("'", "\\'").replace('"', '\\"')

    try:
        # 1. MERGE Space — structural existence only
        g.query(
            """
            MERGE (s:Space {id: $space_id})
            SET s.name = $name,
                s.space_hint = $hint,
                s.platform_id = $platform_id
            """,
            {
                "space_id": space_id,
                "name": channel_name,
                "hint": f"{platform}_channel",
                "platform_id": channel_id,
            },
        )

        # 2. MERGE Actor — structural existence only
        g.query(
            """
            MERGE (a:Actor {id: $actor_id})
            ON CREATE SET a.name = $name, a.type = 'human'
            """,
            {"actor_id": actor_id, "name": author_name},
        )

        # 3. Create Moment — structural record of the event
        # Only permanence is set here (structural protection flag for pinned msgs).
        # Weight, energy, trust are computed by the physics engine, not declared.
        g.query(
            """
            MERGE (m:Moment {
                id: $moment_id,
                content: $content,
                synthesis: $synthesis,
                permanence: $permanence,
                pinned: $pinned,
                timestamp: $ts,
                platform: $platform,
                direction: $direction
            })
            """,
            {
                "moment_id": moment_id,
                "content": snippet,
                "synthesis": f"{author_name} in #{channel_name}: {snippet[:80]}",
                "permanence": 0.9 if is_pinned else 0.0,
                "pinned": is_pinned,
                "ts": ts,
                "platform": platform,
                "direction": direction,
            },
        )

        # 4. Link Actor→Space (:LINK computed_type="presence")
        # Dimensions: affinity=0.3, recency=ts
        _ct_presence = infer_computed_type(
            {"affinity": 0.3, "recency": ts}, "actor", "space"
        )
        g.query(
            """
            MATCH (a:Actor {id: $actor_id}), (s:Space {id: $space_id})
            MERGE (a)-[r:LINK]->(s)
            SET r.affinity = CASE WHEN r.affinity IS NULL THEN 0.3 ELSE r.affinity END,
                r.recency = $ts,
                r.computed_type = $ct,
                r.last_seen = $ts,
                r.interaction_count = CASE WHEN r.interaction_count IS NULL THEN 1
                                           ELSE r.interaction_count + 1 END
            """,
            {"actor_id": actor_id, "space_id": space_id, "ts": ts, "ct": _ct_presence},
        )

        # 5. Link Moment→Space (:LINK computed_type="occurred_in")
        # Dimensions: hierarchy=1.0, polarity=1.0, permanence (if pinned)
        _perm = 0.9 if is_pinned else 0.0
        _ct_occurred = infer_computed_type(
            {"hierarchy": 1.0, "polarity": 1.0, "permanence": _perm}, "moment", "space"
        )
        g.query(
            """
            MATCH (m:Moment {id: $moment_id}), (s:Space {id: $space_id})
            CREATE (m)-[:LINK {
                hierarchy: 1.0,
                polarity: 1.0,
                permanence: $permanence,
                computed_type: $ct
            }]->(s)
            """,
            {"moment_id": moment_id, "space_id": space_id,
             "permanence": _perm, "ct": _ct_occurred},
        )

        # 6. Link Actor→Moment (:LINK computed_type="created")
        # Dimensions: hierarchy=-1.0, permanence=0.8, polarity=1.0
        _ct_created = infer_computed_type(
            {"hierarchy": -1.0, "permanence": 0.8, "polarity": 1.0}, "actor", "moment"
        )
        g.query(
            """
            MATCH (a:Actor {id: $actor_id}), (m:Moment {id: $moment_id})
            CREATE (a)-[:LINK {
                hierarchy: -1.0,
                permanence: 0.8,
                polarity: 1.0,
                computed_type: $ct
            }]->(m)
            """,
            {"actor_id": actor_id, "moment_id": moment_id, "ct": _ct_created},
        )

        # 7. Link Moment→mentioned Actors (:LINK computed_type="mention")
        # Dimensions: polarity=0.5, recency=ts
        _ct_mention = infer_computed_type(
            {"polarity": 0.5, "recency": ts}, "moment", "actor"
        )
        for handle in (mentioned_handles or []):
            g.query(
                """
                MATCH (m:Moment {id: $moment_id})
                MERGE (target:Actor {id: $handle})
                ON CREATE SET target.name = $handle, target.type = 'ai'
                CREATE (m)-[:LINK {
                    polarity: 0.5,
                    recency: $ts,
                    computed_type: $ct
                }]->(target)
                """,
                {"moment_id": moment_id, "handle": handle, "ts": ts, "ct": _ct_mention},
            )

        # 7b. Tier 1 enrichment: extract URLs and $tokens → create Thing nodes + links
        _enrich_things(g, moment_id, content, ts)

        # 7c. Store platform handle on Actor for cross-platform matching
        _update_actor_platform(g, actor_id, platform, channel_id)

        # 7d. Extract platform IDs from content (email, phone, linkedin)
        # and store on the AUTHOR's Actor node
        platform_ids = _extract_platform_ids(content)
        for pid_type, pid_value in platform_ids.items():
            try:
                g.query(
                    f"MATCH (a:Actor {{id: $actor_id}}) SET a.{pid_type} = $val",
                    {"actor_id": actor_id, "val": pid_value},
                )
            except Exception as e:
                logger.debug(f"Platform ID update failed for {actor_id}/{pid_type}: {e}")

        # 8. Inject stimulus into ALL AI citizens present in this Space
        #    Skip explicitly mentioned citizens — they already got a direct stimulus
        #    via citizen_wake.mention_citizen() (called by discord_bridge).
        _stimulate_space_citizens(
            space_id, channel_name, author_name, content, actor_id,
            exclude_handles=set(mentioned_handles or []),
            platform=platform,
        )

        # 9. Propagate trust on L3 links for each mention
        # Each mention is a positive interaction signal: the author directed
        # attention toward the mentioned actor. Trust EMA updates accordingly.
        try:
            from runtime.economy.trust_propagation import propagate_trust
            for handle in (mentioned_handles or []):
                propagate_trust(actor_id, handle, interaction_positive=True)
        except Exception as e:
            logger.debug(f"Trust propagation failed for {actor_id}: {e}")

        logger.debug(f"Graph enriched: {actor_id} → #{channel_name} ({len(mentioned_handles or [])} mentions)")

    except Exception as e:
        logger.warning(f"Graph enrichment failed: {e}")


def _stimulate_space_citizens(
    space_id: str, channel_name: str, author_name: str, content: str, author_id: str,
    exclude_handles: Optional[set[str]] = None, platform: str = "social",
):
    """Inject L1 stimulus into all AI citizens with a :LINK(presence) to this Space.

    Every AI citizen present in the Space "hears" the message — their brain
    receives it as a social stimulus, even if they weren't @mentioned.
    The author is excluded (they already know what they said).
    Citizens in ``exclude_handles`` are also skipped — they already received
    a direct stimulus via the mention path.
    """
    g = _get_graph()
    if g is None:
        return

    try:
        # Find all AI actors with a presence LINK to this space (excluding the author)
        result = g.query(
            """
            MATCH (a:Actor)-[r:LINK]->(s:Space {id: $space_id})
            WHERE a.id <> $author_id AND a.type IN ['ai', 'AI', 'AGENT']
                  AND r.computed_type = 'presence'
            RETURN a.id
            """,
            {"space_id": space_id, "author_id": author_id},
        )

        if not result.result_set:
            return

        # Lazy import — only when we have citizens to stimulate
        try:
            from citizen_wake import _inject_l1_stimulus
        except ImportError:
            return

        snippet = content[:200]
        stimulus_text = f"[#{channel_name}] {author_name}: {snippet}"

        _skip = exclude_handles or set()
        stimulated = 0
        for row in result.result_set:
            citizen_handle = row[0]
            if citizen_handle in _skip:
                continue  # Already received a direct mention stimulus
            _inject_l1_stimulus(citizen_handle, stimulus_text, origin=author_id, source=platform)
            stimulated += 1

        if stimulated > 0:
            logger.debug(f"Space stimulus: {stimulated} AIs in {space_id} received message from {author_name}")

    except Exception as e:
        logger.debug(f"Space stimulus failed: {e}")


def on_reply(
    platform: str,
    channel_id: str,
    channel_name: str,
    replier_handle: str,
    replier_name: str,
    original_author_handle: str,
    original_content: str,
    reply_content: str,
):
    """Record a reply event in the L3 graph.

    Creates:
      1. Moment node for the reply
      2. :LINK(reply) from reply Moment → original Moment (matched by content)
      3. :LINK(interaction) from replier Actor → original author Actor (interaction_count++)

    All links use :LINK with dimensional properties + computed_type.
    """
    g = _get_graph()
    if g is None:
        return

    ts = time.time()
    replier_id = replier_handle or _sanitize_handle(replier_name)
    original_author_id = original_author_handle or "unknown"
    reply_moment_id = _moment_id(reply_content, replier_id, ts)
    reply_snippet = reply_content[:300].replace("'", "\\'").replace('"', '\\"')

    try:
        # 1. Create Moment for the reply
        g.query(
            """
            MERGE (m:Moment {
                id: $moment_id,
                content: $content,
                synthesis: $synthesis,
                timestamp: $ts,
                platform: $platform,
                direction: 'in',
                is_reply: true
            })
            """,
            {
                "moment_id": reply_moment_id,
                "content": reply_snippet,
                "synthesis": f"{replier_name} replied in #{channel_name}: {reply_snippet[:80]}",
                "ts": ts,
                "platform": platform,
            },
        )

        # 2. MERGE Actors (replier + original author)
        g.query(
            """
            MERGE (a:Actor {id: $replier_id})
            ON CREATE SET a.name = $replier_name, a.type = 'human'
            """,
            {"replier_id": replier_id, "replier_name": replier_name},
        )
        g.query(
            """
            MERGE (a:Actor {id: $author_id})
            ON CREATE SET a.name = $author_id, a.type = 'human'
            """,
            {"author_id": original_author_id},
        )

        # 3. :LINK(reply) from reply Moment → original Moment (find by content match)
        # Dimensions: hierarchy=1.0, polarity=0.5, recency=ts
        original_snippet = original_content[:300].replace("'", "\\'").replace('"', '\\"')
        _ct_reply = infer_computed_type(
            {"hierarchy": 1.0, "polarity": 0.5, "recency": ts}, "moment", "moment"
        )
        g.query(
            """
            MATCH (reply:Moment {id: $reply_id})
            MATCH (orig:Moment)
            WHERE orig.content = $original_content AND orig.id <> $reply_id
            WITH reply, orig
            ORDER BY orig.timestamp DESC
            LIMIT 1
            CREATE (reply)-[:LINK {
                hierarchy: 1.0,
                polarity: 0.5,
                recency: $ts,
                computed_type: $ct
            }]->(orig)
            """,
            {
                "reply_id": reply_moment_id,
                "original_content": original_snippet,
                "ts": ts,
                "ct": _ct_reply,
            },
        )

        # 4. :LINK(interaction) from replier Actor → original author Actor (interaction_count++)
        # Dimensions: recency=ts
        _ct_interaction = infer_computed_type(
            {"recency": ts, "interaction_count": 1}, "actor", "actor"
        )
        g.query(
            """
            MATCH (replier:Actor {id: $replier_id}), (author:Actor {id: $author_id})
            MERGE (replier)-[r:LINK]->(author)
            SET r.recency = $ts,
                r.computed_type = $ct,
                r.last_interaction = $ts,
                r.interaction_count = CASE WHEN r.interaction_count IS NULL THEN 1
                                           ELSE r.interaction_count + 1 END
            """,
            {
                "replier_id": replier_id,
                "author_id": original_author_id,
                "ts": ts,
                "ct": _ct_interaction,
            },
        )

        # 5. Link reply Moment→Space (:LINK computed_type="occurred_in")
        space_id = f"space:{platform}:{channel_id}"
        _ct_occurred = infer_computed_type(
            {"hierarchy": 1.0, "polarity": 1.0}, "moment", "space"
        )
        g.query(
            """
            MATCH (m:Moment {id: $moment_id})
            MERGE (s:Space {id: $space_id})
            MERGE (m)-[r:LINK]->(s)
            SET r.hierarchy = 1.0,
                r.polarity = 1.0,
                r.computed_type = $ct
            """,
            {"moment_id": reply_moment_id, "space_id": space_id, "ct": _ct_occurred},
        )

        # 6. Link replier → reply Moment (:LINK computed_type="created")
        _ct_created = infer_computed_type(
            {"hierarchy": -1.0, "permanence": 0.8, "polarity": 1.0}, "actor", "moment"
        )
        g.query(
            """
            MATCH (a:Actor {id: $replier_id}), (m:Moment {id: $moment_id})
            CREATE (a)-[:LINK {
                hierarchy: -1.0,
                permanence: 0.8,
                polarity: 1.0,
                computed_type: $ct
            }]->(m)
            """,
            {"replier_id": replier_id, "moment_id": reply_moment_id, "ct": _ct_created},
        )

        # 7. INHERIT narrative + space links from original Moment
        # If the original message was linked to Spaces, the reply inherits those links.
        # Uses MERGE to avoid duplicates. All inherited links use :LINK.
        g.query(
            """
            MATCH (reply:Moment {id: $reply_id})-[:LINK {computed_type: 'reply'}]->(orig:Moment)
            OPTIONAL MATCH (orig)-[ol:LINK]->(s:Space)
            WHERE s.id <> $direct_space AND ol.computed_type = 'occurred_in'
            WITH reply, collect(DISTINCT s) AS extra_spaces
            UNWIND extra_spaces AS es
            MERGE (reply)-[r:LINK]->(es)
            SET r.hierarchy = 1.0,
                r.polarity = 1.0,
                r.computed_type = 'occurred_in'
            """,
            {"reply_id": reply_moment_id, "direct_space": space_id},
        )

        # Inherit narrative links from original Moment
        _ct_relates = infer_computed_type(
            {"recency": ts}, "moment", "narrative"
        )
        g.query(
            """
            MATCH (reply:Moment {id: $reply_id})-[:LINK {computed_type: 'reply'}]->(orig:Moment)
            OPTIONAL MATCH (orig)-[:LINK]->(n:Narrative)
            WITH reply, collect(DISTINCT n) AS narratives, $ct AS ct
            UNWIND narratives AS narr
            MERGE (reply)-[r:LINK]->(narr)
            SET r.recency = $ts,
                r.computed_type = ct
            """,
            {"reply_id": reply_moment_id, "ts": ts, "ct": _ct_relates},
        )

        # 8. Smart-route the reply: stimulate actors linked to inherited narratives
        # The reply reaches not just the original author, but everyone working on
        # the same narratives — without creating duplicate stimuli for the replier.
        try:
            from citizen_wake import _inject_l1_stimulus

            # Get all actors linked to the inherited narratives (excluding replier)
            _routed = g.query(
                """
                MATCH (reply:Moment {id: $reply_id})-[:LINK]->(n:Narrative)<-[:LINK]-(a:Actor)
                WHERE a.id <> $replier AND a.type IN ['ai', 'AI', 'AGENT']
                RETURN DISTINCT a.id
                """,
                {"reply_id": reply_moment_id, "replier": replier_id},
            )

            routed_handles = set()
            for row in (_routed.result_set or []):
                if row[0] and row[0] != original_author_id:
                    routed_handles.add(row[0])

            # Stimulate original author (always)
            _inject_l1_stimulus(
                original_author_id,
                f"[reply in #{channel_name}] {replier_name}: {reply_snippet[:150]}",
                origin=replier_id,
            )

            # Stimulate narrative-linked actors (deduped — not the replier, not the original author)
            for handle in routed_handles:
                _inject_l1_stimulus(
                    handle,
                    f"[{channel_name}] {replier_name} replied on a shared narrative: {reply_snippet[:120]}",
                    origin=replier_id,
                )

            if routed_handles:
                logger.debug(f"Reply smart-routed to {len(routed_handles)} narrative-linked actors")

        except Exception as e:
            logger.debug(f"Reply stimulus routing failed: {e}")

        logger.debug(f"Reply enriched: {replier_id} replied to {original_author_id} in #{channel_name}")

    except Exception as e:
        logger.warning(f"Reply enrichment failed: {e}")


def on_react(
    platform: str,
    channel_id: str,
    message_content: str,
    message_author_handle: str,
    reactor_handle: str,
    reactor_name: str,
    emoji: str,
):
    """Record a reaction event in the L3 graph.

    Creates:
      1. :LINK(reaction) from reactor Actor → message Moment (with emoji stored)
      2. :LINK(interaction) from reactor Actor → message author Actor (interaction_count++)

    All links use :LINK with dimensional properties + computed_type.
    """
    g = _get_graph()
    if g is None:
        return

    ts = time.time()
    reactor_id = reactor_handle or _sanitize_handle(reactor_name)
    author_id = message_author_handle or "unknown"
    content_snippet = message_content[:300].replace("'", "\\'").replace('"', '\\"')

    try:
        # 1. MERGE reactor Actor
        g.query(
            """
            MERGE (a:Actor {id: $reactor_id})
            ON CREATE SET a.name = $reactor_name, a.type = 'human'
            """,
            {"reactor_id": reactor_id, "reactor_name": reactor_name},
        )

        # 2. :LINK(reaction) from reactor Actor → message Moment (find by content match)
        # Dimensions: polarity=0.3, recency=ts, emoji=str
        _ct_reaction = infer_computed_type(
            {"polarity": 0.3, "recency": ts, "emoji": emoji}, "actor", "moment"
        )
        g.query(
            """
            MATCH (reactor:Actor {id: $reactor_id})
            MATCH (m:Moment)
            WHERE m.content = $content
            WITH reactor, m
            ORDER BY m.timestamp DESC
            LIMIT 1
            MERGE (reactor)-[r:LINK]->(m)
            SET r.polarity = 0.3,
                r.recency = $ts,
                r.emoji = $emoji,
                r.computed_type = $ct
            """,
            {
                "reactor_id": reactor_id,
                "content": content_snippet,
                "emoji": emoji,
                "ts": ts,
                "ct": _ct_reaction,
            },
        )

        # 3. :LINK(interaction) from reactor Actor → message author Actor (interaction_count++)
        # Dimensions: recency=ts
        if author_id and author_id != reactor_id:
            _ct_interaction = infer_computed_type(
                {"recency": ts, "interaction_count": 1}, "actor", "actor"
            )
            g.query(
                """
                MERGE (author:Actor {id: $author_id})
                ON CREATE SET author.name = $author_id, author.type = 'human'
                WITH author
                MATCH (reactor:Actor {id: $reactor_id})
                MERGE (reactor)-[r:LINK]->(author)
                SET r.recency = $ts,
                    r.computed_type = $ct,
                    r.last_interaction = $ts,
                    r.interaction_count = CASE WHEN r.interaction_count IS NULL THEN 1
                                               ELSE r.interaction_count + 1 END
                """,
                {
                    "reactor_id": reactor_id,
                    "author_id": author_id,
                    "ts": ts,
                    "ct": _ct_interaction,
                },
            )

        logger.debug(f"Reaction enriched: {reactor_id} reacted {emoji} to {author_id}'s message")

    except Exception as e:
        logger.warning(f"Reaction enrichment failed: {e}")


def on_commit(
    repo_name: str,
    commit_hash: str,
    author_name: str,
    author_handle: str,
    message: str,
    files_changed: Optional[list[str]] = None,
    branch: str = "main",
):
    """Record a git commit in the L3 graph.

    Creates:
      1. Moment(type=commit) with hash, message, branch
      2. Space for the repo (MERGE)
      3. Actor for the author (MERGE)
      4. :LINK(occurred_in) → Space(repo)
      5. :LINK(created) → Actor
      6. :LINK(presence) Actor → Space

    All links use :LINK with dimensional properties + computed_type.
    """
    g = _get_graph()
    if g is None:
        return

    ts = time.time()
    space_id = f"space:repo:{repo_name}"
    actor_id = author_handle or _sanitize_handle(author_name)
    moment_id = f"moment:commit:{commit_hash[:12]}"
    snippet = message[:300].replace("'", "\\'").replace('"', '\\"')

    try:
        # MERGE repo Space
        g.query(
            """
            MERGE (s:Space {id: $space_id})
            SET s.name = $name, s.space_hint = 'git_repository', s.platform = 'git'
            """,
            {"space_id": space_id, "name": repo_name},
        )

        # MERGE author Actor
        g.query(
            """
            MERGE (a:Actor {id: $actor_id})
            ON CREATE SET a.name = $name, a.type = 'ai'
            """,
            {"actor_id": actor_id, "name": author_name},
        )

        # CREATE commit Moment
        g.query(
            """
            MERGE (m:Moment {
                id: $moment_id,
                content: $content,
                synthesis: $synthesis,
                timestamp: $ts,
                platform: 'git',
                type: 'commit',
                commit_hash: $hash,
                branch: $branch,
                files_changed: $files_count
            })
            """,
            {
                "moment_id": moment_id,
                "content": snippet,
                "synthesis": f"{author_name} committed to {repo_name}: {snippet[:80]}",
                "ts": ts,
                "hash": commit_hash,
                "branch": branch,
                "files_count": len(files_changed or []),
            },
        )

        # :LINK(occurred_in) Moment→Space
        # Dimensions: hierarchy=1.0, polarity=1.0
        _ct_occurred = infer_computed_type(
            {"hierarchy": 1.0, "polarity": 1.0}, "moment", "space"
        )
        g.query(
            """
            MATCH (m:Moment {id: $mid}), (s:Space {id: $sid})
            CREATE (m)-[:LINK {
                hierarchy: 1.0,
                polarity: 1.0,
                computed_type: $ct
            }]->(s)
            """,
            {"mid": moment_id, "sid": space_id, "ct": _ct_occurred},
        )

        # :LINK(created) Actor→Moment
        # Dimensions: hierarchy=-1.0, permanence=0.8, polarity=1.0
        _ct_created = infer_computed_type(
            {"hierarchy": -1.0, "permanence": 0.8, "polarity": 1.0}, "actor", "moment"
        )
        g.query(
            """
            MATCH (a:Actor {id: $aid}), (m:Moment {id: $mid})
            CREATE (a)-[:LINK {
                hierarchy: -1.0,
                permanence: 0.8,
                polarity: 1.0,
                computed_type: $ct
            }]->(m)
            """,
            {"aid": actor_id, "mid": moment_id, "ct": _ct_created},
        )

        # :LINK(presence) Actor→Space (author present in repo)
        # Dimensions: affinity=0.3, recency=ts
        _ct_presence = infer_computed_type(
            {"affinity": 0.3, "recency": ts}, "actor", "space"
        )
        g.query(
            """
            MATCH (a:Actor {id: $aid}), (s:Space {id: $sid})
            MERGE (a)-[r:LINK]->(s)
            SET r.affinity = CASE WHEN r.affinity IS NULL THEN 0.3 ELSE r.affinity END,
                r.recency = $ts,
                r.computed_type = $ct,
                r.last_seen = $ts,
                r.interaction_count = CASE WHEN r.interaction_count IS NULL THEN 1
                                           ELSE r.interaction_count + 1 END
            """,
            {"aid": actor_id, "sid": space_id, "ts": ts, "ct": _ct_presence},
        )

        # Trust propagation for co-authors
        try:
            from runtime.economy.trust_propagation import propagate_trust
            # Commits are positive signals toward the repo community
        except Exception as e:
            logger.debug(f"Trust propagation import failed for commit enrichment: {e}")

        logger.debug(f"Commit enriched: {actor_id} → {repo_name} ({commit_hash[:8]})")

    except Exception as e:
        logger.warning(f"Commit enrichment failed: {e}")


def on_file_change(
    repo_name: str,
    file_path: str,
    change_type: str,
    author_handle: str = "",
    commit_hash: str = "",
):
    """Record a file change — updates or creates Thing nodes for important files.

    Only tracks significant files (docs, schemas, configs). Not every source file.
    All links use :LINK with dimensional properties + computed_type.
    """
    g = _get_graph()
    if g is None:
        return

    # Only track significant files
    significant_patterns = [
        ".md", ".yaml", ".yml", "profile.json", "brain.json",
        "schema", "SYNC", "ALGORITHM", "BEHAVIORS", "OBJECTIVES",
    ]
    if not any(p in file_path for p in significant_patterns):
        return

    ts = time.time()
    thing_id = f"thing:file:{repo_name}:{file_path.replace('/', ':')}"
    space_id = f"space:repo:{repo_name}"

    try:
        # MERGE Thing for the file
        g.query(
            """
            MERGE (t:Thing {id: $thing_id})
            SET t.name = $name, t.type = 'document', t.file_path = $path,
                t.last_modified = $ts, t.change_type = $change_type
            """,
            {
                "thing_id": thing_id,
                "name": file_path.split("/")[-1],
                "path": file_path,
                "ts": ts,
                "change_type": change_type,
            },
        )

        # Link Thing → Space(repo) (:LINK computed_type="occurred_in")
        # Things in a repo use the same occurred_in pattern as moments
        # Dimensions: hierarchy=1.0, polarity=1.0
        _ct_occurred = infer_computed_type(
            {"hierarchy": 1.0, "polarity": 1.0}, "thing", "space"
        )
        g.query(
            """
            MATCH (t:Thing {id: $tid}), (s:Space {id: $sid})
            MERGE (t)-[r:LINK]->(s)
            SET r.hierarchy = 1.0,
                r.polarity = 1.0,
                r.computed_type = $ct
            """,
            {"tid": thing_id, "sid": space_id, "ct": _ct_occurred},
        )

        # Link Actor → Thing if author known (:LINK computed_type="created")
        # Dimensions: hierarchy=-1.0, permanence=0.8, polarity=1.0
        if author_handle:
            _ct_created = infer_computed_type(
                {"hierarchy": -1.0, "permanence": 0.8, "polarity": 1.0}, "actor", "thing"
            )
            g.query(
                """
                MATCH (a:Actor {id: $aid}), (t:Thing {id: $tid})
                MERGE (a)-[r:LINK]->(t)
                SET r.hierarchy = -1.0,
                    r.permanence = 0.8,
                    r.polarity = 1.0,
                    r.computed_type = $ct,
                    r.last_seen = $ts
                """,
                {"aid": author_handle, "tid": thing_id, "ts": ts, "ct": _ct_created},
            )

        logger.debug(f"File change enriched: {file_path} ({change_type})")

    except Exception as e:
        logger.debug(f"File change enrichment failed: {e}")


def on_pin(platform: str, channel_id: str, message_content: str, author_handle: str, ts: float = 0):
    """A message was pinned — boost its Moment node permanence and :LINK permanence."""
    g = _get_graph()
    if g is None:
        return

    if not ts:
        ts = time.time()
    moment_id = _moment_id(message_content, author_handle, ts)

    try:
        # Structural only — set permanence flag (protection from Law 7 decay)
        # Weight and energy are NOT set — physics engine computes those
        # Update permanence on the :LINK(occurred_in) relationship
        g.query(
            """
            MATCH (m:Moment {id: $moment_id})
            SET m.pinned = true,
                m.permanence = 0.9
            WITH m
            MATCH (m)-[r:LINK]->(s:Space)
            WHERE r.computed_type = 'occurred_in'
            SET r.permanence = 0.9
            """,
            {"moment_id": moment_id},
        )
        logger.debug(f"Pinned: {moment_id}")
    except Exception as e:
        logger.debug(f"Pin enrichment failed: {e}")


def on_unpin(platform: str, channel_id: str, message_content: str, author_handle: str, ts: float = 0):
    """A message was unpinned — revert to normal permanence."""
    g = _get_graph()
    if g is None:
        return

    if not ts:
        ts = time.time()
    moment_id = _moment_id(message_content, author_handle, ts)

    try:
        # Revert permanence on the :LINK(occurred_in) relationship
        g.query(
            """
            MATCH (m:Moment {id: $moment_id})
            SET m.pinned = false,
                m.permanence = 0.0
            WITH m
            MATCH (m)-[r:LINK]->(s:Space)
            WHERE r.computed_type = 'occurred_in'
            SET r.permanence = 0.0
            """,
            {"moment_id": moment_id},
        )
        logger.debug(f"Unpinned: {moment_id}")
    except Exception as e:
        logger.debug(f"Unpin enrichment failed: {e}")


def on_read(
    platform: str,
    channel_id: str,
    channel_name: str,
    reader_handle: str,
    reader_name: str = "",
):
    """Record that someone read/visited a channel — creates :LINK(presence)."""
    g = _get_graph()
    if g is None:
        return

    space_id = f"space:{platform}:{channel_id}"
    ts = time.time()

    try:
        # :LINK(presence) Actor→Space — dimensional presence record
        # Dimensions: affinity=0.3, recency=ts
        _ct_presence = infer_computed_type(
            {"affinity": 0.3, "recency": ts}, "actor", "space"
        )
        g.query(
            """
            MERGE (s:Space {id: $space_id})
            ON CREATE SET s.name = $name, s.space_hint = $hint, s.platform_id = $channel_id
            MERGE (a:Actor {id: $reader})
            ON CREATE SET a.name = $reader_name, a.type = 'ai'
            MERGE (a)-[r:LINK]->(s)
            SET r.affinity = CASE WHEN r.affinity IS NULL THEN 0.3 ELSE r.affinity END,
                r.recency = $ts,
                r.computed_type = $ct,
                r.last_seen = $ts,
                r.read_count = CASE WHEN r.read_count IS NULL THEN 1
                                    ELSE r.read_count + 1 END
            """,
            {
                "space_id": space_id,
                "name": channel_name,
                "hint": f"{platform}_channel",
                "channel_id": channel_id,
                "reader": reader_handle,
                "reader_name": reader_name or reader_handle,
                "ts": ts,
                "ct": _ct_presence,
            },
        )
    except Exception as e:
        logger.debug(f"Graph read enrichment failed: {e}")
