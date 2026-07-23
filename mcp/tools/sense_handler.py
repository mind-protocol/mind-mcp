"""
[THINK] Sense — Return the citizen's current awareness: what they see, feel, and sense.

Four perceptual layers:
  1. Exteroception — what I see in the world (spaces, actors, moments, things)
  2. Interoception — what I feel inside (energy, drives, emotions, WM load)
  3. Senses — custom sense readings (rolling scores, correlations, insights)
  4. Vision — what I see in the 3D world (camera, visible citizens)

Usage via MCP:
    sense()                         → full awareness (all 4 layers)
    sense(layer="exteroception")    → just what I see
    sense(layer="interoception")    → just what I feel
    sense(layer="senses")           → just custom sense readings
    sense(layer="vision")           → just 3D world vision

This is NOT a dashboard. It's the citizen reading their own perceptual state.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import logging
from pathlib import Path
from typing import Any, Dict

from runtime.permissions.access_check import check_access, detect_citizen_handle

logger = logging.getLogger("mind.sense")

# ── Path anchors ─────────────────────────────────────────────────────────────
_MIND_MCP_ROOT = Path(__file__).resolve().parent.parent.parent
_WORLD_ROOT = _MIND_MCP_ROOT.parent.parent


TOOL_SCHEMA = {
    "name": "sense",
    "description": (
        "Read your current awareness — what you see (exteroception), "
        "what you feel (interoception), and what your custom senses measure. "
        "This is NOT a dashboard — it's you reading your own perceptual state."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "layer": {
                "type": "string",
                "enum": ["all", "exteroception", "interoception", "senses", "vision"],
                "description": "Which awareness layer to read. Default: all.",
            },
            "handle": {
                "type": "string",
                "description": "Citizen handle. Auto-detected if omitted.",
            },
        },
    },
}


def handle_sense(args: dict, ctx) -> Dict[str, Any]:
    """Return the citizen's current awareness state."""

    layer = args.get("layer", "all")
    citizen_handle = args.get("handle") or _detect_handle()

    sections = []

    # Une couche muette n'est pas une couche vide. Auparavant, une couche sans
    # donnée renvoyait "" et disparaissait du rapport : seule la Vision (un
    # placeholder 3D optionnel) parlait encore, y compris pour dire son échec.
    # sense(layer="all") ressemblait donc à « tout le moteur est mort » alors que
    # rien n'était cassé, et les réveils s'interrompaient pour rien. L'absence
    # doit être énoncée, jamais devinée.
    who = citizen_handle or "handle non détecté"

    def _add(text: str, title: str, why: str) -> None:
        sections.append(text if text else f"## {title}\nIndisponible — {why} (citoyen : {who}).")

    # ── Exteroception: what I see ──
    if layer in ("all", "exteroception"):
        _add(_get_exteroception(citizen_handle, ctx), "What I See",
             "aucun moteur vivant ni état L3 pour ce citoyen")

    # ── Interoception: what I feel ──
    if layer in ("all", "interoception"):
        _add(_get_interoception(citizen_handle, ctx), "What I Feel",
             "aucun état L1 vivant ni fichier awareness.md")

    # ── Custom senses: what I measure ──
    if layer in ("all", "senses"):
        _add(_get_senses(citizen_handle, ctx), "What I Measure",
             "aucun nœud de type 'sense' dans le graphe de ce citoyen")

    # ── Vision: what I see in the 3D world (optionnel) ──
    # Explicitement optionnelle : son indisponibilité ne dit rien de la santé du
    # reste du système, et ne doit pas être lue comme une panne générale.
    if layer in ("all", "vision"):
        sections.append(_get_vision() or "## What I See (3D World)\nIndisponible (couche optionnelle).")

    if not sections:
        return _ok("No awareness data available. Engine may not be loaded.")

    return _ok("\n\n---\n\n".join(sections))


# ── Exteroception ────────────────────────────────────────────────────────────

def _get_exteroception(citizen_handle: str, ctx) -> str:
    """Get exteroception awareness text — placeholder, wired to engine when available."""
    try:
        # Try dispatcher engines first (live state)
        dispatcher = _get_dispatcher(ctx)
        if dispatcher:
            engine = dispatcher._citizen_engines.get(citizen_handle)
            if engine:
                extero = getattr(engine, '_exteroception', None)
                if extero and extero is not False:
                    state = dispatcher._citizen_states.get(citizen_handle)
                    metabolism = state.metabolism if state else None
                    return extero.get_awareness_text(citizen_handle, metabolism)

        # Fallback: create a fresh exteroception scan from L3
        if ctx and ctx.graph_ops:
            from runtime.cognition.exteroception import ExteroceptionEngine
            extero = ExteroceptionEngine()

            def _query_fn(cypher, params):
                result = ctx.graph_ops._query(cypher, params)
                return result if result else []

            # Run one scan to populate environment
            extero._scan_environment(citizen_handle, _query_fn)
            return extero.get_awareness_text(citizen_handle)

    except Exception as e:
        logger.debug(f"Exteroception unavailable for {citizen_handle}: {e}")

    return ""


# ── Interoception ────────────────────────────────────────────────────────────

def _get_interoception(citizen_handle: str, ctx) -> str:
    """Get interoception text — what the citizen feels internally.

    Tries live L1 state from the dispatcher first. Falls back to reading
    the citizen's .mind/awareness.md from their directory in the world repo.
    """
    # ── Try live L1 state ──
    live_text = _get_interoception_live(citizen_handle, ctx)
    if live_text:
        return live_text

    # ── Fallback: read awareness.md from citizen dir in world repo ──
    return _get_interoception_from_awareness_file(citizen_handle)


def _get_interoception_live(citizen_handle: str, ctx) -> str:
    """Try to get interoception from live dispatcher state."""
    lines = ["## What I Feel Right Now"]

    try:
        dispatcher = _get_dispatcher(ctx)
        if not dispatcher:
            return ""

        state = dispatcher._citizen_states.get(citizen_handle)
        if not state:
            return ""

        # Drives
        active_drives = {
            name: drive.intensity
            for name, drive in state.limbic.drives.items()
            if drive.intensity > 0.05
        }
        if active_drives:
            top = sorted(active_drives.items(), key=lambda x: -x[1])
            drive_lines = [f"{name} ({intensity:.0%})" for name, intensity in top[:5]]
            lines.append(f"Drives: {', '.join(drive_lines)}.")

        # Emotions
        active_emotions = {
            name: val
            for name, val in state.limbic.emotions.items()
            if val > 0.05
        }
        if active_emotions:
            top = sorted(active_emotions.items(), key=lambda x: -x[1])
            emotion_lines = [f"{name} ({val:.0%})" for name, val in top[:5]]
            lines.append(f"Emotions: {', '.join(emotion_lines)}.")

        # WM state
        wm_count = len(state.wm.node_ids) if hasattr(state, 'wm') else 0
        wm_max = 7
        if wm_count >= wm_max:
            lines.append(f"Working memory: full ({wm_count}/{wm_max}).")
        elif wm_count > 0:
            lines.append(f"Working memory: {wm_count}/{wm_max} slots used.")
        else:
            lines.append("Working memory: empty.")

        # Energy
        total_energy = sum(n.energy for n in state.nodes.values())
        lines.append(f"Total brain energy: {total_energy:.1f}.")

        # Orientation
        engine = dispatcher._citizen_engines.get(citizen_handle)
        if engine:
            orientation = getattr(engine, '_current_orientation', None)
            if orientation:
                lines.append(f"Current orientation: {orientation}.")

        # Metabolism
        if state.metabolism:
            phase = state.metabolism.circadian_phase()
            if phase < 0.2:
                lines.append("Circadian: deep rest phase.")
            elif phase < 0.4:
                lines.append("Circadian: winding down.")
            elif phase > 0.8:
                lines.append("Circadian: peak alertness.")
            else:
                lines.append(f"Circadian phase: {phase:.0%}.")

        # Tick count
        lines.append(f"Ticks lived: {state.tick_count}.")

        return "\n".join(lines)

    except Exception as e:
        logger.debug(f"Live interoception unavailable for {citizen_handle}: {e}")
        return ""


def _get_interoception_from_awareness_file(citizen_handle: str) -> str:
    """Fallback: read .mind/awareness.md from the citizen's directory in the world repo."""
    if not citizen_handle:
        return ""

    # Look in the world repo citizens directory
    awareness_path = _WORLD_ROOT / "citizens" / citizen_handle / ".mind" / "awareness.md"

    if not awareness_path.is_file():
        # Also try without .mind subdirectory
        awareness_path = _WORLD_ROOT / "citizens" / citizen_handle / "awareness.md"

    if not awareness_path.is_file():
        return ""

    # ── Permission check: reading another citizen's awareness file ──
    requesting_handle = detect_citizen_handle()
    if requesting_handle and requesting_handle != citizen_handle:
        if not check_access(requesting_handle, str(awareness_path), "read"):
            logger.debug(
                f"Access denied: {requesting_handle} cannot read "
                f"awareness file of {citizen_handle}"
            )
            return ""

    try:
        content = awareness_path.read_text(encoding="utf-8").strip()
        if content:
            return f"## What I Feel Right Now\n\n{content}"
    except Exception as e:
        logger.debug(f"Could not read awareness file for {citizen_handle}: {e}")

    return ""


# ── Custom Senses ────────────────────────────────────────────────────────────

def _get_senses(citizen_handle: str, ctx) -> str:
    """Get custom sense readings from the brain graph.

    Queries sense nodes (type='sense') from the citizen's L1 brain graph
    and returns their current readings.
    """
    lines = ["## My Senses"]

    try:
        dispatcher = _get_dispatcher(ctx)
        if not dispatcher:
            # Fallback: try querying sense nodes directly from graph
            return _get_senses_from_graph(citizen_handle, ctx)

        engine = dispatcher._citizen_engines.get(citizen_handle)
        if not engine:
            return _get_senses_from_graph(citizen_handle, ctx)

        sense_eng = getattr(engine, '_sense_engine', None)
        if not sense_eng or sense_eng is False:
            lines.append("No custom senses loaded.")
            return "\n".join(lines)

        if not sense_eng._sense_definitions:
            lines.append("No custom senses defined.")
            return "\n".join(lines)

        for sense_id, definition in sense_eng._sense_definitions.items():
            name = definition.get("_name", sense_id)
            text = sense_eng.get_awareness_text(sense_id)
            if text:
                lines.append(f"### {name}")
                lines.append(text)
            else:
                lines.append(f"### {name}: no data yet.")

    except Exception as e:
        logger.debug(f"Senses unavailable for {citizen_handle}: {e}")
        lines.append("(senses unavailable)")

    return "\n".join(lines)


def _get_senses_from_graph(citizen_handle: str, ctx) -> str:
    """Query sense nodes directly from the citizen's brain graph in FalkorDB."""
    if not ctx or not ctx.graph_ops:
        return ""

    lines = ["## My Senses"]

    try:
        graph_name = f"brain_{citizen_handle}"
        result = ctx.graph_ops._query(
            "MATCH (n {type: 'sense'}) RETURN n.id, n.content, n.weight, n.energy",
            {},
            graph_name=graph_name,
        )
        if not result:
            return ""

        for row in result:
            if isinstance(row, (list, tuple)):
                sense_id = row[0] if len(row) > 0 else "unknown"
                content = row[1] if len(row) > 1 else ""
                weight = row[2] if len(row) > 2 else 0
                energy = row[3] if len(row) > 3 else 0
            else:
                sense_id = row.get("n.id", "unknown")
                content = row.get("n.content", "")
                weight = row.get("n.weight", 0)
                energy = row.get("n.energy", 0)

            lines.append(f"### {sense_id}")
            if content:
                lines.append(content)
            lines.append(f"weight={weight:.2f} energy={energy:.2f}")

    except Exception as e:
        logger.debug(f"Graph sense query failed for {citizen_handle}: {e}")
        return ""

    if len(lines) <= 1:
        return ""

    return "\n".join(lines)


# ── Vision ───────────────────────────────────────────────────────────────────

def _get_vision() -> str:
    """Get the latest 3D world frame — what the citizen sees through their camera.

    The engine captures frames at /perception/frame and stores latest at
    perception/latest.png + perception/latest.json (metadata: camera position,
    visible citizens, timestamp).

    Placeholder — connects to cities-of-light engine when available.
    """
    import json as json_mod
    import os

    lines = ["## What I See (3D World)"]

    engine_url = os.environ.get("ENGINE_URL", "http://localhost:8800")

    try:
        import requests
        resp = requests.get(f"{engine_url}/perception/latest", timeout=5)
        if resp.ok:
            data = resp.json()
            frame = data.get("frame")
            if frame:
                lines.append(f"Last frame: {frame.get('ts', 'unknown')}")
                pos = frame.get("camera_position")
                if pos:
                    lines.append(
                        f"Camera position: x={pos.get('x', 0):.1f}, "
                        f"y={pos.get('y', 0):.1f}, z={pos.get('z', 0):.1f}"
                    )
                visible = frame.get("visible_citizens", [])
                if visible:
                    lines.append(f"I can see: {', '.join(visible[:10])}.")
                else:
                    lines.append("No other citizens visible from here.")
                return "\n".join(lines)
            else:
                lines.append("No frame captured yet. The 3D viewer hasn't been opened.")
                return "\n".join(lines)
    except Exception:
        # Nommer ce qui est absent. "Engine not reachable" laissait croire que
        # tout Mind était tombé, alors que ce moteur 3D est optionnel et distinct
        # du home_server (:8765) : un réveil s'est arrêté sur ce seul message.
        lines.append(
            f"Moteur 3D optionnel (cities-of-light) injoignable sur {engine_url} — "
            "sans effet sur le reste de la perception ni sur le home_server."
        )
        return "\n".join(lines)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_dispatcher(ctx=None):
    """Get the dispatcher — from ctx first, then from home_server state."""
    # Prefer the dispatcher attached to the server context
    if ctx and getattr(ctx, 'dispatcher', None):
        return ctx.dispatcher

    try:
        import sys
        if "home_server" in sys.modules:
            return sys.modules["home_server"]._state.get("dispatcher")
    except Exception as e:
        logger.error(f"[Sense] Failed to resolve dispatcher from home_server: {e}")

    return None


def _detect_handle() -> str:
    """Auto-detect citizen handle from environment.

    Délègue au détecteur canonique déjà importé plus haut. Cette fonction en
    était une copie qui découpait sur "/citizens/" : sous Windows le cwd est en
    "\", donc le handle restait toujours vide et les trois couches de perception
    remontaient muettes. Une seule implémentation, corrigée à un seul endroit.
    """
    return detect_citizen_handle()


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}
