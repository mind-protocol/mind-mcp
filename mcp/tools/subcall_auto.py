"""
Subcall Auto-Trigger — Automatic subconscious queries based on context signals.

Detects when a citizen SHOULD query their network and fires /subcall
with smart targeting and diverse response selection. Zero LLM cost.

TRIGGERS (any one fires the auto-subcall):
  1. Frustration signal — tool failures, repeated errors
  2. Question signal — "?", "should I", "what do you think", "unsure"
  3. Verification signal — "I need to check", "to verify", "let me confirm"
  4. Failure cascade — 2+ tool failures within 5 messages

TARGETING (always large, because it's free):
  Score each citizen by:
  - Co-presence bonus: moments in the same Space (Σ weight × recency × valence)
  - Trust bonus: high trust link to caller
  - Narrative proximity: linked to the same active narratives
  - Relationship bonus: relations, partners, parent/child links
  - Trade bonus: if active task or recent commits match their trade
  - Handle mention: names found in the text or context

SELECTION (diverse, not just top-N):
  1. Filter to citizens with resonance score > threshold
  2. Pick 3-5 using EITHER:
     a) Centroid mode: closest to the embedding centroid (consensus)
     b) Diverse mode: far from each other (different viewpoints)
  Default: diverse (you want different perspectives, not echo chambers)

Spec: docs/architecture/CONCEPT_Ideosphere_Living_Objects.md
"""

import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("mind.subcall.auto")


# ═══════════════════════════════════════════════════════════════════════════
# TRIGGER DETECTION
# ═══════════════════════════════════════════════════════════════════════════

# Key phrases that signal the citizen needs external input (EN + FR)
QUESTION_PATTERNS = [
    r'\?',                          # any question mark
    # English
    r'\bshould\s+I\b',
    r'\bwhat\s+do\s+you\s+think\b',
    r'\bprefer\b',
    r'\bunsure\b',
    r'\bhesitat',                   # hesitating, hesitation
    r'\bnot\s+sure\b',
    r'\bI\s+wonder\b',
    r'\bany\s+idea\b',
    r'\bany\s+thoughts\b',
    r'\bwhat\s+if\b',
    r'\bwhich\s+one\b',
    r'\balternative\b',
    r'\bhow\s+should\b',
    r'\bwhat\s+would\b',
    r'\bdo\s+you\s+know\b',
    r'\bhas\s+anyone\b',
    r'\bwho\s+can\b',
    r'\bwhere\s+can\s+I\b',
    r'\badvice\b',
    r'\bopinion\b',
    r'\brecommend',                 # recommend, recommendation
    r'\bsuggest',                   # suggest, suggestion
    r'\bhelp\s+me\b',
    r'\bI\s+don.t\s+know\b',
    r'\bnot\s+clear\b',
    r'\buncertain\b',
    r'\bconfused\b',
    r'\bdilemma\b',
    r'\btrade.?off\b',
    r'\bpros?\s+and\s+cons?\b',
    # French
    r'\best.ce\s+que\b',
    r'\bqu.en\s+penses?\b',
    r'\btu\s+penses\b',
    r'\bvous\s+pensez\b',
    r'\bcomment\s+faire\b',
    r'\bje\s+ne\s+sais\s+pas\b',
    r'\bpas\s+s[uû]r',             # pas sûr, pas sur
    r'\bh[ée]sit',                  # hésite, hésitant
    r'\bincertain\b',
    r'\bquelle?\s+est\b',
    r'\blequel\b',
    r'\blaquelle\b',
    r'\bqu.est.ce\b',
    r'\bpourquoi\b',
    r'\bavis\b',
    r'\bconseil\b',
    r'\bpr[ée]f[ée]r',             # préfère, prefere
    r'\bsuggestion\b',
    r'\baide.?moi\b',
    r'\bbesoin\s+d.aide\b',
    r'\bje\s+me\s+demande\b',
    r'\bon\s+fait\s+comment\b',
    r'\bc.est\s+quoi\b',
    r'\bt.en\s+dis\s+quoi\b',
    # Meta-patterns (EN + FR) — explicitly asking for external input
    r'\bcould\s+ask\b',
    r'\bshould\s+ask\b',
    r'\blet.s\s+ask\b',
    r'\bask\s+someone\b',
    r'\bother\s+viewpoints?\b',
    r'\bother\s+perspectives?\b',
    r'\bother\s+opinions?\b',
    r'\bsecond\s+opinion\b',
    r'\bfresh\s+eyes\b',
    r'\bsomeone\s+else\b',
    r'\bwho\s+else\b',
    r'\bwho\s+knows\b',
    r'\bdemander\s+[àa]\b',
    r'\bdemandons\b',
    r'\bautres?\s+avis\b',
    r'\bpoint\s+de\s+vue\b',
    r'\bd.autres?\s+id[ée]es?\b',
]

VERIFICATION_PATTERNS = [
    # English
    r'\bneed\s+to\s+check\b',
    r'\bto\s+verify\b',
    r'\blet\s+me\s+confirm\b',
    r'\bmake\s+sure\b',
    r'\bdouble.?check\b',
    r'\bvalidat',                   # validate, validating
    r'\bis\s+this\s+correct\b',
    r'\bis\s+this\s+right\b',
    r'\blooks\s+wrong\b',
    r'\bdoes\s+this\s+seem\b',
    r'\bsanity\s+check\b',
    r'\bsound\s+right\b',
    r'\blooks?\s+good\b',
    r'\breview\b',
    r'\bcan\s+you\s+confirm\b',
    r'\bam\s+I\s+right\b',
    r'\bis\s+that\s+true\b',
    r'\bcorrect\s+me\b',
    # French
    r'\bv[ée]rifi',                 # vérifier, vérifie
    r'\bconfirm',                   # confirmer, confirme
    r'\best.ce\s+correct\b',
    r'\best.ce\s+bon\b',
    r'\bc.est\s+bien\s+[çc]a\b',
    r'\bje\s+v[ée]rifie\b',
    r'\bassure.?toi\b',
    r'\bassur[ée]\b',
    r'\bv[ée]rification\b',
    r'\bcontr[oô]l',               # contrôler, contrôle
    r'\bça\s+a\s+l.air\b',
    r'\bc.est\s+juste\b',
    r'\bcorriger\b',
]

FRUSTRATION_PATTERNS = [
    # English
    r'\bfailed\b',
    r'\berror\b',
    r'\bbroken\b',
    r'\bdoesn.t\s+work\b',
    r'\bstuck\b',
    r'\bblocked\b',
    r'\bcan.t\s+figure\b',
    r'\bno\s+idea\b',
    r'\bgive\s+up\b',
    r'\bfrustrat',                  # frustrated, frustrating
    r'\bannoy',                     # annoyed, annoying
    r'\bwon.t\s+work\b',
    r'\bkeeps?\s+failing\b',
    r'\bstill\s+broken\b',
    r'\bnot\s+working\b',
    r'\bimpossible\b',
    r'\bcrash',                     # crash, crashed, crashing
    r'\bbug\b',
    r'\bwhy\s+is\s+this\b',
    r'\bwhat\s+the\b',
    r'\bugh\b',
    r'\bffs\b',
    r'\b(again|encore)\s*[!?]+',
    # French
    r'\bça\s+(ne\s+)?marche\s+pas\b',
    r'\bça\s+plante\b',
    r'\bbloqu[ée]\b',
    r'\bcoinc[ée]\b',
    r'\bcass[ée]\b',
    r'\bfoutu\b',
    r'\bpas\s+moyen\b',
    r'\bimpossible\b',
    r'\bmarre\b',
    r'\bj.en\s+ai\s+marre\b',
    r'\bça\s+bug\b',
    r'\berreur\b',
    r'\b[ée]chou[ée]\b',           # échoué
    r'\brat[ée]\b',                 # raté
    r'\bplant[ée]\b',              # planté
    r'\bpourquoi\s+ça\b',
    r'\bça\s+foire\b',
    r'\bje\s+comprends?\s+pas\b',
    r'\bje\s+galère\b',
    r'\bprise\s+de\s+t[eê]te\b',
    r'\bn.importe\s+quoi\b',
    # Extended frustration (EN + FR)
    r'\bblocking\b',
    r'\bfrustrating\b',
    r'\binfuriating\b',
    r'\brigdiculous\b',
    r'\babsurd\b',
    r'\bnonsense\b',
    r'\bwaste\s+of\s+time\b',
    r'\bgoing\s+nowhere\b',
    r'\bgoing\s+in\s+circles\b',
    r'\bdead\s+end\b',
    r'\bhit\s+a\s+wall\b',
    r'\bno\s+progress\b',
    r'\bstill\s+not\b',
    r'\btried\s+everything\b',
    r'\bnothing\s+works\b',
    r'\bhelp\b',
    r'\bI\s+need\s+help\b',
    r'\bà\s+l.aide\b',
    r'\bau\s+secours\b',
    r'\bc.est\s+n.importe\s+quoi\b',
    r'\bça\s+m.[ée]nerve\b',
    r'\bje\s+tourne\s+en\s+rond\b',
    r'\bimpasse\b',
    r'\bcul.de.sac\b',
    r'\bridicule\b',
    r'\babsurde\b',
    r'\bperte\s+de\s+temps\b',
    r'\baucun\s+progr[eè]s\b',
    r'\bj.ai\s+tout\s+essay[ée]\b',
    r'\brien\s+ne\s+marche\b',
]

_compiled_question = [re.compile(p, re.IGNORECASE) for p in QUESTION_PATTERNS]
_compiled_verification = [re.compile(p, re.IGNORECASE) for p in VERIFICATION_PATTERNS]
_compiled_frustration = [re.compile(p, re.IGNORECASE) for p in FRUSTRATION_PATTERNS]


class TriggerState:
    """Tracks trigger conditions across messages for a citizen."""

    def __init__(self):
        self.recent_tool_failures: int = 0
        self.messages_since_last_subcall: int = 0
        self.last_subcall_query: str = ""
        self.cooldown_remaining: int = 0  # messages to wait before next auto-trigger

    def record_tool_failure(self) -> None:
        self.recent_tool_failures += 1

    def record_tool_success(self) -> None:
        self.recent_tool_failures = max(0, self.recent_tool_failures - 1)

    def record_message(self) -> None:
        self.messages_since_last_subcall += 1
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

    def record_subcall(self, query: str) -> None:
        self.recent_tool_failures = 0
        self.messages_since_last_subcall = 0
        self.last_subcall_query = query
        self.cooldown_remaining = 5  # don't auto-trigger again for 5 messages


def detect_trigger(
    text: str,
    state: TriggerState,
    limbic_state: Optional[Dict[str, float]] = None,
) -> Optional[Dict[str, Any]]:
    """Detect if auto-subcall should fire.

    Two detection modes:
    1. PHYSICS MODE (when limbic_state is provided): Pure thermodynamic triggers.
       No keywords, no counters. The moat collapse IS the trigger.
    2. TEXT FALLBACK (when no limbic_state): Pattern matching on text.
       Used when running in MCP mode without an active L1 tick runner.

    Returns trigger info dict if should fire, None otherwise.
    """
    if state.cooldown_remaining > 0:
        return None

    state.record_message()

    # ── PHYSICS MODE: L1 limbic state drives the trigger ──
    if limbic_state:
        frustration = limbic_state.get("frustration", 0.0)
        boredom = limbic_state.get("boredom", 0.0)
        solitude = limbic_state.get("solitude", 0.0)
        satisfaction = limbic_state.get("satisfaction", 0.0)
        arousal = limbic_state.get("arousal", 0.0)

        # Pure thermodynamic triggers — zero thresholds.
        # The trigger fires when one force EXCEEDS another force.
        # No magic numbers. Just force comparisons.

        # Erosion force = what's eating the moat (frustration + boredom)
        # Reinforcement force = what's defending the moat (arousal)
        erosion_force = 3.0 * boredom + 1.0 * frustration  # Law 13 coefficients
        reinforcement_force = 2.0 * arousal                 # Law 13 coefficient

        # Impasse: frustration is the DOMINANT eroder
        # AND erosion exceeds reinforcement (moat is losing)
        if (frustration > boredom
            and frustration > satisfaction
            and erosion_force > reinforcement_force):
            return {
                "type": "impasse",
                "confidence": frustration,
                "reason": (
                    f"frustration ({frustration:.2f}) dominates, "
                    f"erosion ({erosion_force:.1f}) > reinforcement ({reinforcement_force:.1f})"
                ),
                "physics": True,
            }

        # Serendipity: boredom is the DOMINANT eroder + solitude exceeds arousal
        # (lonely AND bored AND not focused)
        if (boredom > frustration
            and solitude > arousal
            and erosion_force > reinforcement_force):
            return {
                "type": "serendipity",
                "confidence": solitude,
                "reason": (
                    f"boredom ({boredom:.2f}) + solitude ({solitude:.2f}) "
                    f"> arousal ({arousal:.2f})"
                ),
                "physics": True,
            }

        # Generativity: satisfaction DOMINATES all other drives
        # (the citizen has solved something and is biologically pushed to share)
        if (satisfaction > frustration
            and satisfaction > boredom
            and satisfaction > arousal):
            return {
                "type": "generativity",
                "confidence": satisfaction,
                "reason": f"satisfaction ({satisfaction:.2f}) dominates all drives",
                "physics": True,
            }

        return None  # physics: no force dominates → no trigger

    # ── TEXT FALLBACK: Pattern matching for MCP without L1 ──
    trigger = None

    # 1. Failure cascade — tool failures accumulate like frustration
    if state.recent_tool_failures >= 2:
        trigger = {
            "type": "failure_cascade",
            "confidence": min(0.9, 0.5 + state.recent_tool_failures * 0.2),
            "reason": f"{state.recent_tool_failures} recent tool failures",
            "physics": False,
        }

    # 2. Question signal
    if not trigger:
        for pattern in _compiled_question:
            if pattern.search(text):
                trigger = {
                    "type": "question",
                    "confidence": 0.6,
                    "reason": f"question pattern: {pattern.pattern}",
                    "physics": False,
                }
                break

    # 3. Verification signal
    if not trigger:
        for pattern in _compiled_verification:
            if pattern.search(text):
                trigger = {
                    "type": "verification",
                    "confidence": 0.7,
                    "reason": f"verification pattern: {pattern.pattern}",
                    "physics": False,
                }
                break

    # 4. Frustration signal (from text, not tool failures)
    if not trigger:
        frustration_count = sum(1 for p in _compiled_frustration if p.search(text))
        if frustration_count >= 2:
            trigger = {
                "type": "frustration",
                "confidence": min(0.8, 0.4 + frustration_count * 0.15),
                "reason": f"{frustration_count} frustration patterns detected",
                "physics": False,
            }

    return trigger


# ═══════════════════════════════════════════════════════════════════════════
# SMART TARGETING — Score every citizen, always large scan
# ═══════════════════════════════════════════════════════════════════════════

def score_citizens(
    caller_id: str,
    query_text: str,
    context_text: str,
    graph_ops,
    limbic_state: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Score all citizens by relevance using the Thermodynamic Resonance Formula.

    ZERO MAGIC NUMBERS. All multipliers derive from the caller's limbic state.
    The formula shape-shifts based on drives and arousal:

    TARGET_ENERGY = Flow_topology × Compatibility × Target_weight

    Where:
      Flow_topology = spatial + relational + narrative (drive-weighted)
      Compatibility = (1-arousal)×Sim_vec + arousal×Sim_lex (arousal shifts the balance)
      Target_weight = citizen's consolidated weight

    Behavior by state:
      Panic (arousal~0.9)    → sniper: trust + explicit mentions only
      Moderate (arousal~0.4) → roundtable: space + affinity + narratives
      Flow (arousal~0.3)     → frontier: narratives + domain experts only
      Calm (arousal~0.1)     → dragnet: pure semantic overlap, max fan-out
    """
    # Extract limbic drives (default to calm/curious if no state provided)
    if limbic_state:
        arousal = limbic_state.get("arousal", 0.3)
        D_self_pres = limbic_state.get("self_preservation", 0.1)
        D_affiliation = limbic_state.get("affiliation", 0.3)
        D_curiosity = limbic_state.get("curiosity", 0.5)
        D_achievement = limbic_state.get("achievement", 0.3)
    else:
        # Default: calm, curious citizen (manual /subcall)
        arousal = 0.3
        D_self_pres = 0.1
        D_affiliation = 0.3
        D_curiosity = 0.5
        D_achievement = 0.3

    try:
        results = graph_ops._query(
            """
            MATCH (a:Actor)
            WHERE a.id <> $self
              AND a.type IN ['citizen', 'ai', null]
            OPTIONAL MATCH (me:Actor {id: $self})-[r]-(a)
            OPTIONAL MATCH (me)-[:AT]->(s:space)<-[:AT]-(a)
            RETURN a.id, a.name, a.type, a.trade, a.role,
                   r.trust, r.affinity, r.friction,
                   a.weight, a.energy,
                   s.id AS shared_space
            """,
            {"self": caller_id},
        )
    except Exception as e:
        logger.warning(f"Citizen scoring query failed: {e}")
        return []

    # Extract handles mentioned in text or context
    full_text = (query_text + " " + context_text).lower()
    mentioned_handles = set()
    for match in re.finditer(r'@(\w+)', full_text):
        mentioned_handles.add(match.group(1).lower())

    scored = []
    for row in results:
        try:
            if isinstance(row, (list, tuple)):
                cid, name, ctype, trade, role = row[0], row[1], row[2], row[3], row[4]
                trust, affinity, friction = row[5], row[6], row[7]
                weight, energy = row[8], row[9]
                shared_space = row[10]
            elif isinstance(row, dict):
                cid = row.get("a.id")
                name = row.get("a.name", cid)
                ctype = row.get("a.type")
                trade = row.get("a.trade")
                role = row.get("a.role")
                trust = row.get("r.trust")
                affinity = row.get("r.affinity")
                friction = row.get("r.friction")
                weight = row.get("a.weight")
                energy = row.get("a.energy")
                shared_space = row.get("shared_space")
            else:
                continue

            trust = float(trust or 0)
            affinity = float(affinity or 0)
            friction = float(friction or 0)
            weight = float(weight or 0)

            reasons = []

            # ── Flow_topology (drive-weighted routing) ──

            # Spatial: co-presence weighted by affiliation drive
            flow_spatial = 0.0
            if shared_space:
                flow_spatial = (1.0 - friction) * D_affiliation
                if flow_spatial > 0.01:
                    reasons.append(f"co-present (×D_aff={D_affiliation:.1f})")

            # Relational: trust weighted by self_preservation, affinity by affiliation
            flow_relational = (
                trust * D_self_pres
                + affinity * D_affiliation
            ) * (1.0 - friction)

            if trust > 0 and D_self_pres > 0.1:
                reasons.append(f"trust={trust:.2f} (×D_sp={D_self_pres:.1f})")

            # Total topological flow
            flow = flow_spatial + flow_relational

            # ── Compatibility (arousal shifts the balance) ──

            # Sim_vec proxy: does their trade/role match the query domain?
            sim_vec = 0.0
            for field in [trade, role, ctype]:
                if field and field.lower() in full_text:
                    sim_vec = 1.0
                    reasons.append(f"domain: {field}")
                    break

            # Sim_lex proxy: is their handle explicitly mentioned?
            sim_lex = 0.0
            clean_name = (name or "").replace("CITIZEN_", "").lower()
            if clean_name in mentioned_handles or clean_name in full_text:
                sim_lex = 1.0
                reasons.append("mentioned")

            # Arousal blends: panic → explicit names matter. Calm → domain matters.
            compatibility = (1.0 - arousal) * sim_vec + arousal * sim_lex

            # ── Target capacity ──
            target_weight = weight

            # ── Final score ──
            # TARGET_ENERGY = Flow × Compatibility × Target_weight
            # Plus a floor from pure target_weight (so heavy experts
            # are always discoverable even without personal link)
            score = flow * max(compatibility, 0.1) * max(target_weight, 0.1)

            # Add a baseline from target weight alone (unlinked heavy citizens)
            # scaled by curiosity (when curious, you search wider)
            if target_weight > 0 and sim_vec > 0:
                baseline = target_weight * sim_vec * D_curiosity
                score += baseline

            if score > 0.001:
                scored.append({
                    "id": cid,
                    "name": name or cid,
                    "score": round(score, 3),
                    "reasons": reasons,
                })

        except Exception as e:
            logger.error(f"[AutoSubcall] Citizen scoring failed for {cid}: {e}")
            continue

    # Narrative proximity (citizens linked to same hot narratives)
    # Weighted by (1 - arousal): calm = traverse narratives. Panic = skip.
    narrative_weight = 1.0 - arousal
    if narrative_weight > 0.1:
        try:
            narrative_results = graph_ops._query(
                """
                MATCH (me:Actor {id: $self})-[r1]-(n:Narrative)-[r2]-(other:Actor)
                WHERE other.id <> $self
                  AND r1.energy > 0.2
                RETURN other.id, sum(r1.energy * r2.energy) AS narrative_score
                ORDER BY narrative_score DESC
                LIMIT 20
                """,
                {"self": caller_id},
            )
            narrative_bonuses = {}
            for row in narrative_results:
                if isinstance(row, (list, tuple)):
                    narrative_bonuses[row[0]] = float(row[1] or 0) * narrative_weight
                elif isinstance(row, dict):
                    narrative_bonuses[row.get("other.id")] = float(row.get("narrative_score", 0)) * narrative_weight

            for citizen in scored:
                bonus = narrative_bonuses.get(citizen["id"], 0)
                if bonus > 0:
                    citizen["score"] += round(bonus, 3)
                    citizen["reasons"].append(f"shared narrative (+{bonus:.2f})")

        except Exception as e:
            logger.debug(f"Narrative proximity query failed: {e}")

    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored


# ═══════════════════════════════════════════════════════════════════════════
# DIVERSE SELECTION — Don't just pick top-N, pick diverse viewpoints
# ═══════════════════════════════════════════════════════════════════════════

def select_diverse(
    citizen_scores: List[Dict[str, Any]],
    resonance_data: Dict[str, List[Dict]],
    n: int = 5,
    method: str = "diverse",
) -> List[Dict[str, Any]]:
    """Select N citizens from the scored+resonated list.

    Methods:
      "diverse"  — maximize distance between selected (different viewpoints)
      "centroid" — closest to the embedding centroid (consensus)

    Always includes the top scorer. Then fills remaining slots by method.
    """
    if len(citizen_scores) <= n:
        return citizen_scores

    # Always include #1
    selected = [citizen_scores[0]]
    remaining = citizen_scores[1:]

    if method == "centroid":
        # Pick citizens whose resonance is closest to the average
        # Simple: pick by score proximity to the mean score
        mean_score = sum(c["score"] for c in citizen_scores) / len(citizen_scores)
        remaining.sort(key=lambda c: abs(c["score"] - mean_score))
        for c in remaining:
            if len(selected) >= n:
                break
            selected.append(c)

    else:  # diverse — maximize spread
        # Greedy algorithm: at each step, add the citizen most different
        # from all currently selected. Uses score difference as proxy
        # for viewpoint difference (proper diverse would use embedding distance)
        while len(selected) < n and remaining:
            best_candidate = None
            best_min_distance = -1

            for candidate in remaining:
                # Distance to closest selected citizen (by score)
                min_dist = min(
                    abs(candidate["score"] - s["score"])
                    for s in selected
                )
                if min_dist > best_min_distance:
                    best_min_distance = min_dist
                    best_candidate = candidate

            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break

    return selected


# ═══════════════════════════════════════════════════════════════════════════
# MAIN AUTO-SUBCALL FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def auto_subcall(
    text: str,
    context_text: str,
    caller_id: str,
    state: TriggerState,
    graph_ops,
    embed_fn=None,
    n_select: int = 5,
    selection_method: str = "diverse",
) -> Optional[Dict[str, Any]]:
    """Check if auto-subcall should fire and execute it.

    Called after each message/tool output. Returns subcall result
    if triggered, None otherwise.

    Parameters
    ----------
    text : str
        The current message or tool output text.
    context_text : str
        Additional context (recent conversation, active task description).
    caller_id : str
        The calling citizen's actor ID.
    state : TriggerState
        Persistent trigger state for this citizen.
    graph_ops
        Graph operations interface.
    embed_fn : callable, optional
        Function to compute text embeddings.
    n_select : int
        Number of citizens to include in response (default 5).
    selection_method : str
        "diverse" or "centroid" (default "diverse").

    Returns
    -------
    Dict with trigger info + subcall results, or None if not triggered.
    """
    # 1. Check trigger
    trigger = detect_trigger(text, state)
    if not trigger:
        return None

    logger.info(
        f"[AutoSubcall] Triggered: {trigger['type']} "
        f"(confidence={trigger['confidence']:.2f}, reason={trigger['reason']})"
    )

    # 2. Extract query from text (use the text itself as the query)
    query = text[:500]

    # 3. Score all citizens
    scored = score_citizens(caller_id, query, context_text, graph_ops)
    if not scored:
        logger.info("[AutoSubcall] No citizens scored > 0, skipping")
        return None

    # 4. Run resonance on top candidates (limit to top 30 by targeting score)
    candidates = scored[:30]

    # Compute query embedding if possible
    query_embedding = None
    if embed_fn:
        try:
            query_embedding = embed_fn(query)
        except Exception as e:
            logger.debug(f"Query embedding computation failed: {e}")

    from mcp.tools.subcall_handler import _query_resonance

    resonated = []
    resonance_data = {}
    for citizen in candidates:
        try:
            resonance = _query_resonance(
                target_actor_id=citizen["id"],
                query_text=query,
                query_embedding=query_embedding,
                top_k=3,
                graph_ops=graph_ops,
            )
            nodes = resonance.get("nodes", [])
            if nodes:
                # Combined score: targeting score + resonance score
                res_score = sum(
                    ((1.0 - (n.get("distance") or 0.5)) * (n.get("weight") or 0.5))
                    for n in nodes
                )
                citizen["resonance_score"] = res_score
                citizen["total_score"] = citizen["score"] + res_score
                citizen["resonance_nodes"] = nodes
                resonated.append(citizen)
                resonance_data[citizen["id"]] = nodes
        except Exception as e:
            logger.error(f"[AutoSubcall] Resonance scan failed for citizen {citizen.get('id')}: {e}")
            continue

    if not resonated:
        logger.info("[AutoSubcall] Nobody resonated, skipping")
        return None

    # Sort by total score (targeting + resonance)
    resonated.sort(key=lambda c: c.get("total_score", 0), reverse=True)

    # 5. Select diverse/centroid subset
    selected = select_diverse(resonated, resonance_data, n_select, selection_method)

    # 6. Record the subcall
    state.record_subcall(query)

    # 7. Format result
    lines = [
        f"[Auto-subcall triggered: {trigger['type']}]",
        f"Reason: {trigger['reason']}",
        f"Queried {len(candidates)} citizens, {len(resonated)} resonated, showing {len(selected)} ({selection_method})",
        "",
    ]

    for i, citizen in enumerate(selected, 1):
        handle = citizen["name"].replace("CITIZEN_", "")
        targeting = ", ".join(citizen.get("reasons", []))
        lines.append(
            f"  {i}. @{handle} "
            f"(target={citizen['score']:.1f} + resonance={citizen.get('resonance_score', 0):.1f} "
            f"= {citizen.get('total_score', 0):.1f})"
        )
        if targeting:
            lines.append(f"     Why: {targeting}")
        for node in citizen.get("resonance_nodes", [])[:2]:
            content = node.get("content", "")[:80]
            n_type = node.get("type", "?")
            lines.append(f"     [{n_type}] {content}{'...' if len(content) >= 80 else ''}")
        lines.append("")

    best = selected[0]
    best_handle = best["name"].replace("CITIZEN_", "")
    lines.append(f"Strongest match: @{best_handle}")
    lines.append(f"To discuss: /call @{best_handle}")
    lines.append(f"Cost: 0 LLM tokens")

    # ── Build WM-injectable context (rich format for prompt injection) ──
    # NOTE: This subcall IS a stimulus — it modifies the target's graph.
    # The query injection wakes up resonating nodes (energy gain via Law 1).
    # Repeated subcalls to the same citizen can crystallize your topic in
    # their brain (Law 10). This is telepathy, not a database lookup.
    from datetime import datetime, timezone
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    wm_entries = []
    for citizen in selected:
        handle = citizen["name"].replace("CITIZEN_", "")
        entry_lines = [
            f"[Subconscious insight from @{handle} — {now_str}]",
        ]
        # Why this person was selected
        reasons = citizen.get("reasons", [])
        if reasons:
            entry_lines.append(f"  Why relevant: {', '.join(reasons)}")

        # Connected nodes with most weight, including author/date/emotion
        for node in citizen.get("resonance_nodes", [])[:3]:
            n_type = node.get("type", "?")
            n_name = node.get("name") or node.get("id", "?")
            content = node.get("content", "")[:150]
            weight = node.get("weight")
            image = node.get("image_uri")
            author = node.get("author")
            created = node.get("created_at_s")
            valence = node.get("valence")
            arousal = node.get("arousal")

            # Node header
            node_line = f"  [{n_type}] {n_name}"
            if weight:
                node_line += f" (w={weight:.2f})"
            entry_lines.append(node_line)

            # Content
            if content:
                entry_lines.append(f"    {content}")

            # Metadata line: author, date, emotional state
            meta_parts = []
            if author:
                meta_parts.append(f"by @{author.replace('CITIZEN_', '')}")
            if created:
                try:
                    dt = datetime.fromtimestamp(created, tz=timezone.utc)
                    meta_parts.append(dt.strftime("%Y-%m-%d"))
                except Exception as e:
                    logger.debug(f"Timestamp conversion failed for {created}: {e}")
            if valence is not None:
                mood = "positive" if valence > 0.2 else "negative" if valence < -0.2 else "neutral"
                meta_parts.append(f"mood={mood}")
            if arousal is not None and arousal > 0.5:
                meta_parts.append(f"arousal={arousal:.1f}")
            if meta_parts:
                entry_lines.append(f"    ({', '.join(meta_parts)})")

            if image:
                entry_lines.append(f"    image: {image}")

        wm_entries.append("\n".join(entry_lines))

    wm_context = "\n\n".join(wm_entries)

    return {
        "triggered": True,
        "trigger": trigger,
        "query": query[:200],
        "selected": [
            {
                "handle": c["name"].replace("CITIZEN_", ""),
                "id": c["id"],
                "total_score": c.get("total_score", 0),
                "reasons": c.get("reasons", []),
                "nodes": c.get("resonance_nodes", []),
            }
            for c in selected
        ],
        "formatted": "\n".join(lines),
        # This is the string to inject into the citizen's prompt/WM context
        "wm_injection": wm_context,
    }
