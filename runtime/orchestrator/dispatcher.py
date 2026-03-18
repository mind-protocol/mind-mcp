"""Two-tick engine dispatcher — no queue, no budget, no response routing.

Background loop runs maintenance (neuron cleanup, health check) and
tick_all_citizens(). Each citizen has two independent tick intervals:

  awareness_tick  — L1 physics: decay, drives, WM selection, orientation
  thought_tick    — conscious action: serialize WM, dispatch Claude session

When a tick changes WM → write_awareness.
When a tick fires a conscious action → dispatch Claude session.

Direct dispatch: incoming requests go straight to ThreadPoolExecutor.
No message queue. No ComputeBudget. No response callback routing.
"""

import os
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import Optional

from runtime.orchestrator.account_balancer import (
    init as init_accounts,
    status_line as accounts_status,
    proactive_refresh as refresh_accounts,
)
from runtime.orchestrator.claude_invoker import invoke_claude, invoke_degraded
from runtime.orchestrator import activation_pressure
from runtime.orchestrator.session_tracker import (
    write_neuron_profile,
    update_neuron_status,
    cleanup_old_neurons,
    enforce_neuron_cap,
)
from runtime.orchestrator import degradation

# L1 Cognitive Engine integration
try:
    from runtime.cognition.two_tick_engine import TwoTickEngine
    from runtime.cognition.awareness_file_writer import write_awareness_file
    from runtime.cognition.wm_prompt_serializer import serialize_wm_to_prompt
    from runtime.cognition.models import CitizenCognitiveState
    from runtime.cognition.graph_reader_for_awareness_tick import create_graph_read_fn
    TWO_TICK_AVAILABLE = True
except ImportError:
    TWO_TICK_AVAILABLE = False

# Fallback: try legacy L1 if two-tick not yet deployed
try:
    from runtime.cognition.models import CitizenCognitiveState as _LegacyState
    from runtime.cognition.tick_runner_l1_cognitive_engine import L1CognitiveTickRunner
    from runtime.cognition.stimulus_router import StimulusRouter, IncomingEvent
    from runtime.cognition.wm_prompt_serializer import serialize_wm_to_prompt as _legacy_serialize
    LEGACY_L1_AVAILABLE = True
except ImportError:
    LEGACY_L1_AVAILABLE = False

logger = logging.getLogger("orchestrator.dispatcher")

# ── Constants ───────────────────────────────────────────────────────────────

NEURON_CLEANUP_INTERVAL = 60     # seconds between neuron cleanups
HEALTH_CHECK_INTERVAL = 10       # seconds between degradation checks
ACCOUNT_REFRESH_INTERVAL = 1800  # seconds — proactive token refresh (30 min)
AWARENESS_INTERVAL = 60          # seconds — L1 physics tick per citizen
THOUGHT_INTERVAL = 300           # seconds — conscious action check per citizen

# Suppress infrastructure errors from reaching users
SUPPRESS_PATTERNS = [
    "credits balance is too low",
    "rate limit",
    "overloaded_error",
    "529 overloaded",
    "could not connect to the api",
]


class Dispatcher:
    """Two-tick engine dispatcher. No queue, no budget, no response routing."""

    def __init__(self):
        max_parallel = int(os.environ.get("MAX_PARALLEL", "15"))
        self.executor = ThreadPoolExecutor(max_workers=max_parallel)
        self.active_futures: dict[Future, tuple[str, dict]] = {}

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_cleanup = 0.0
        self._last_health_check = 0.0
        self._last_account_refresh = 0.0

        # Per-citizen tick timestamps
        self._last_awareness_tick: dict[str, float] = {}
        self._last_thought_tick: dict[str, float] = {}

        # Shared graph reader (one connection for all citizens)
        self._graph_read_fn = None
        if TWO_TICK_AVAILABLE:
            try:
                self._graph_read_fn = create_graph_read_fn()
                logger.info("Graph reader created for two-tick engine")
            except Exception as e:
                logger.warning(f"Graph reader creation failed: {e}")

        # Citizen engine instances (two-tick or legacy)
        self._citizen_engines: dict = {}
        self._citizen_states: dict = {}
        self._citizen_routers: dict = {}

    def start(self):
        """Start the dispatch loop in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="orchestrator")
        self._thread.start()
        logger.info("Dispatcher started (two-tick engine)")

    def stop(self):
        """Stop the dispatch loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        self.executor.shutdown(wait=False)
        logger.info("Dispatcher stopped")

    # ── Background Loop ────────────────────────────────────────────────────

    def _run_loop(self):
        """Main loop — runs in background thread."""
        accounts = init_accounts()
        logger.info(f"Accounts: {len(accounts)} ({accounts_status()})")

        while self._running:
            try:
                self._maintenance()
                self._tick_all_citizens()
                self._collect_completed_futures()
            except Exception as e:
                logger.exception(f"Tick error: {e}")

            time.sleep(5)  # base loop interval

    def _maintenance(self):
        """Periodic housekeeping: neuron cleanup, health check, account refresh."""
        now = time.time()

        if now - self._last_cleanup > NEURON_CLEANUP_INTERVAL:
            cleanup_old_neurons()
            enforce_neuron_cap()
            self._last_cleanup = now

        if now - self._last_health_check > HEALTH_CHECK_INTERVAL:
            degradation.check_deadlock(notify_fn=None)
            self._last_health_check = now

        if now - self._last_account_refresh > ACCOUNT_REFRESH_INTERVAL:
            try:
                refresh_accounts(notify_fn=None)
            except Exception as e:
                logger.debug(f"Account refresh check: {e}")
            self._last_account_refresh = now

    def _tick_all_citizens(self):
        """For each citizen, check tick intervals and run appropriate ticks."""
        now = time.time()

        for handle in list(self._citizen_engines.keys()):
            try:
                wm_changed = False

                # Awareness tick (L1 physics)
                last_awareness = self._last_awareness_tick.get(handle, 0.0)
                if now - last_awareness > AWARENESS_INTERVAL:
                    wm_changed = self._awareness_tick(handle)
                    self._last_awareness_tick[handle] = now

                # Thought tick (conscious action check)
                last_thought = self._last_thought_tick.get(handle, 0.0)
                if now - last_thought > THOUGHT_INTERVAL:
                    conscious_action = self._thought_tick(handle)
                    self._last_thought_tick[handle] = now

                    if conscious_action:
                        self._fire_conscious_action(handle)

                # Write awareness file if WM changed
                if wm_changed and TWO_TICK_AVAILABLE:
                    try:
                        state = self._citizen_states.get(handle)
                        if state:
                            engine = self._citizen_engines.get(handle)
                            orientation = None
                            tick_num = 0
                            if isinstance(engine, TwoTickEngine):
                                orientation = engine._current_orientation
                                tick_num = engine._thought_tick_counter
                            write_awareness_file(state, tick_num, orientation)
                    except Exception as e:
                        logger.debug(f"Awareness write failed for {handle}: {e}")

            except Exception as e:
                logger.exception(f"Tick error for {handle}: {e}")

    def _awareness_tick(self, handle: str) -> bool:
        """Run L1 physics tick for a citizen. Returns True if WM changed."""
        engine = self._citizen_engines.get(handle)
        if not engine:
            return False

        try:
            if TWO_TICK_AVAILABLE and isinstance(engine, TwoTickEngine):
                result = engine.awareness_tick()
                return getattr(result, 'wm_changed', False)
            elif LEGACY_L1_AVAILABLE and isinstance(engine, L1CognitiveTickRunner):
                result = engine.run_tick()  # No stimulus — background tick
                return True  # Legacy doesn't track wm_changed
            return False
        except Exception as e:
            logger.debug(f"Awareness tick failed for {handle}: {e}")
            return False

    def _thought_tick(self, handle: str) -> bool:
        """Check if citizen should fire a conscious action. Returns True if action needed."""
        engine = self._citizen_engines.get(handle)
        if not engine:
            return False

        try:
            if TWO_TICK_AVAILABLE and isinstance(engine, TwoTickEngine):
                result = engine.thought_tick()
                return getattr(result, 'action_emitted', False)
            elif LEGACY_L1_AVAILABLE and isinstance(engine, L1CognitiveTickRunner):
                # Legacy: check last tick result for action_emitted
                result = engine.run_tick()
                return getattr(result, 'action_emitted', False)
            return False
        except Exception as e:
            logger.debug(f"Thought tick failed for {handle}: {e}")
            return False

    def _fire_conscious_action(self, handle: str):
        """Serialize WM to prompt and dispatch a Claude session."""
        state = self._citizen_states.get(handle)
        if not state:
            return

        # Build cognitive context
        orientation = None
        engine = self._citizen_engines.get(handle)
        if hasattr(engine, '_current_orientation'):
            orientation = engine._current_orientation

        serialize_fn = serialize_wm_to_prompt if TWO_TICK_AVAILABLE else (
            _legacy_serialize if LEGACY_L1_AVAILABLE else None
        )
        if not serialize_fn:
            return

        wm_prompt = serialize_fn(state, orientation)

        request = {
            "text": wm_prompt,
            "voice_text": f"[conscious_action] {handle}",
            "mode": "autonomous",
            "source": "conscious_action",
            "sender_id": handle,
            "metadata": {
                "citizen_handle": handle,
                "autonomous": True,
                "orientation": orientation,
                "cognitive_context": wm_prompt,
            },
        }

        self.dispatch(request)
        logger.info(f"Conscious action fired for {handle} (orientation={orientation})")

    # ── Direct Dispatch ────────────────────────────────────────────────────

    def dispatch(self, request: dict):
        """Direct submit to ThreadPoolExecutor. No queue. Inject cognitive context."""
        citizen_handle = (request.get("metadata") or {}).get("citizen_handle", "_system")
        session_id = _generate_session_id()
        mode = request.get("mode", "partner")
        source = request.get("source", "unknown")
        voice_text = request.get("voice_text", "")[:80]

        # Inject cognitive context if not already present
        if citizen_handle != "_system" and (TWO_TICK_AVAILABLE or LEGACY_L1_AVAILABLE):
            metadata = request.get("metadata") or {}
            if "cognitive_context" not in metadata:
                wm_context = self._get_citizen_wm_context(citizen_handle)
                if wm_context:
                    metadata["cognitive_context"] = wm_context
                    request["metadata"] = metadata

        # Write neuron profile
        write_neuron_profile(
            session_id=session_id,
            name=f"{mode}_{source}",
            purpose=voice_text or f"{mode} request from {source}",
            status="spawning",
            metadata={
                "source": source,
                "citizen_handle": citizen_handle,
                "sender_id": request.get("sender_id", ""),
            },
        )

        # Choose invocation path
        if degradation.is_degraded():
            invoke_fn = invoke_degraded
        else:
            invoke_fn = invoke_claude

        future = self.executor.submit(invoke_fn, request, session_id)
        self.active_futures[future] = (session_id, request)
        update_neuron_status(session_id, "busy")

        logger.debug(f"Dispatched {session_id} ({mode}/{source}): {voice_text}")

    def _get_citizen_wm_context(self, citizen_handle: str) -> str:
        """Get WM prompt context for a citizen's next LLM session."""
        self._ensure_citizen_engine(citizen_handle)
        state = self._citizen_states.get(citizen_handle)
        if not state:
            return ""

        orientation = None
        engine = self._citizen_engines.get(citizen_handle)
        if hasattr(engine, '_current_orientation'):
            orientation = engine._current_orientation

        serialize_fn = serialize_wm_to_prompt if TWO_TICK_AVAILABLE else (
            _legacy_serialize if LEGACY_L1_AVAILABLE else None
        )
        if not serialize_fn:
            return ""

        return serialize_fn(state, orientation)

    # ── Collect Completed Futures ──────────────────────────────────────────

    def _collect_completed_futures(self):
        """Process results, update neuron status. No response_callback."""
        done_futures = [f for f in self.active_futures if f.done()]
        for future in done_futures:
            session_id, request = self.active_futures.pop(future)
            try:
                result = future.result()
                if isinstance(result, tuple):
                    response, voice_response = result
                else:
                    response, voice_response = result, None

                # Suppress infrastructure errors + feed activation pressure
                if response and any(p.lower() in response.lower() for p in SUPPRESS_PATTERNS):
                    logger.warning(f"Suppressed infra error in {session_id}: {response[:80]}")
                    if any(p in response.lower() for p in ["rate limit", "429", "quota", "credit balance", "out of"]):
                        activation_pressure.on_rate_limit()
                else:
                    activation_pressure.on_success()

                update_neuron_status(session_id, "idle",
                                     sender_id=str(request.get("sender_id", "")))

            except Exception as e:
                logger.exception(f"Future {session_id} raised: {e}")
                update_neuron_status(session_id, "error")

    # ── Citizen Engine Management ──────────────────────────────────────────

    def _ensure_citizen_engine(self, citizen_handle: str):
        """Get or create an engine instance for a citizen."""
        if citizen_handle in self._citizen_engines:
            return

        if TWO_TICK_AVAILABLE:
            state = CitizenCognitiveState(citizen_id=citizen_handle)
            self._attach_l3(state)
            engine = TwoTickEngine(state, graph_read_fn=self._graph_read_fn)
            self._citizen_states[citizen_handle] = state
            self._citizen_engines[citizen_handle] = engine
            logger.info(f"Two-tick engine initialized for {citizen_handle}")

        elif LEGACY_L1_AVAILABLE:
            state = _LegacyState(citizen_id=citizen_handle)

            # Attach metabolism
            try:
                from runtime.cognition.metabolism import CitizenMetabolism
                state.metabolism = CitizenMetabolism()
            except ImportError:
                pass

            self._attach_l3(state)
            runner = L1CognitiveTickRunner(state)
            router = StimulusRouter(citizen_handle)

            self._citizen_states[citizen_handle] = state
            self._citizen_engines[citizen_handle] = runner
            self._citizen_routers[citizen_handle] = router
            logger.info(f"Legacy L1 engine initialized for {citizen_handle}")

    def _attach_l3(self, state):
        """Attach L3 graph query/write functions to a cognitive state."""
        try:
            from falkordb import FalkorDB
            _db = FalkorDB(host="localhost", port=6379)
            _graph_name = os.environ.get("L3_GRAPH", os.environ.get("FALKORDB_GRAPH", "lumina-prime"))
            _l3 = _db.select_graph(_graph_name)

            def _query_l3(cypher, params):
                r = _l3.query(cypher, params)
                return r.result_set if r.result_set else []

            def _write_l3(cypher, params):
                _l3.query(cypher, params)

            state._l3_query_fn = _query_l3
            state._l3_write_fn = _write_l3
        except Exception as e:
            logger.debug(f"L3 graph not available: {e}")

    def inject_stimulus(self, citizen_handle: str, content: str,
                        source: str = "external", is_social: bool = False,
                        is_failure: bool = False, is_progress: bool = False):
        """Inject a stimulus into a citizen's engine. Called by bridges."""
        self._ensure_citizen_engine(citizen_handle)

        if LEGACY_L1_AVAILABLE:
            router = self._citizen_routers.get(citizen_handle)
            if router:
                event = IncomingEvent(
                    content=content,
                    source=source,
                    citizen_handle=citizen_handle,
                    is_social=is_social,
                    is_failure=is_failure,
                    is_progress=is_progress,
                )
                stimulus = router.route(event)
                if stimulus:
                    runner = self._citizen_engines.get(citizen_handle)
                    if runner and isinstance(runner, L1CognitiveTickRunner):
                        runner.run_tick(stimulus=stimulus)

    def bulk_load_citizen_engines(self, citizen_handles: list[str]):
        """Pre-load engines at boot for all citizens."""
        loaded = 0
        for handle in citizen_handles:
            try:
                self._ensure_citizen_engine(handle)
                loaded += 1
            except Exception as e:
                logger.warning(f"Failed to load engine for {handle}: {e}")

        engine_type = "two-tick" if TWO_TICK_AVAILABLE else "legacy-L1"
        logger.info(f"Engines: {loaded}/{len(citizen_handles)} loaded ({engine_type})")

    # ── Public API ─────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Running, active_sessions, citizen_engines count, degradation, accounts."""
        active_count = sum(1 for f in self.active_futures if not f.done())
        return {
            "running": self._running,
            "active_sessions": active_count,
            "citizen_engines": len(self._citizen_engines),
            "degradation": degradation.get_status(),
            "accounts": accounts_status(),
        }


# ── Helpers ────────────────────────────────────────────────────────────────

def _generate_session_id() -> str:
    """Generate a short, human-readable session ID."""
    import uuid
    return uuid.uuid4().hex[:12]
