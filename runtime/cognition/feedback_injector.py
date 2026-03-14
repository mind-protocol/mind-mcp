"""
Feedback Injector — post-action self-stimulus and limbic updates.

Spec: docs/l1_wiring/ALGORITHM_L1_Wiring.md Section 4

After a citizen's LLM session completes, inject the result back into
the L1 graph as self-stimulus. This closes the perception-action loop:
  message → stimulus → tick → WM → prompt → LLM → action → feedback → stimulus

The feedback includes:
- Self-stimulus from action output (the citizen "hears" its own response)
- Limbic shifts based on action outcome (satisfaction/frustration deltas)
- Energy consumption for the active WM nodes (CONSUME step)
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from .models import CitizenCognitiveState
from .tick_runner_l1_cognitive_engine import Stimulus
from .stimulus_router import StimulusRouter

logger = logging.getLogger("cognition.feedback")


def inject_post_action_feedback(
    state: CitizenCognitiveState,
    router: StimulusRouter,
    action_output: str,
    success: bool = True,
    response_time_ms: Optional[float] = None,
) -> Optional[Stimulus]:
    """Inject post-action feedback into the L1 engine.

    Called after a citizen's LLM session produces output. Converts the
    output into a self-stimulus and updates limbic state based on outcome.

    Args:
        state: Citizen's cognitive state
        router: Citizen's stimulus router (for anti-loop checking)
        action_output: The text the citizen produced
        success: Whether the action succeeded (affects frustration/satisfaction)
        response_time_ms: How long the action took (affects satisfaction)

    Returns:
        Self-stimulus if anti-loop allows it, None if filtered
    """
    # Record that an action was taken (anti-loop tracking)
    router.record_action()

    # Build self-stimulus from action output
    # Truncate long outputs — the citizen doesn't need to re-read everything
    content = action_output
    if len(content) > 500:
        content = content[:250] + " [...] " + content[-200:]

    from .stimulus_router import IncomingEvent

    event = IncomingEvent(
        content=content,
        source="self",
        citizen_handle=router.citizen_handle,
        is_social=False,
        is_failure=not success,
        is_progress=success,
    )

    stimulus = router.route(event)

    # Update limbic state based on outcome
    _update_limbic_from_outcome(state, success, response_time_ms)

    if stimulus:
        logger.debug(
            f"Feedback injected for {router.citizen_handle}: "
            f"success={success}, energy={stimulus.energy_budget:.2f}"
        )

    return stimulus


def _update_limbic_from_outcome(
    state: CitizenCognitiveState,
    success: bool,
    response_time_ms: Optional[float],
):
    """Update limbic drives based on action outcome.

    Success → satisfaction bump, frustration relief
    Failure → frustration bump, achievement drive increase
    Slow response → mild anxiety increase
    """
    drives = state.limbic.drives
    emotions = state.limbic.emotions

    if success:
        # Satisfaction bump
        if "satisfaction" in emotions:
            emotions["satisfaction"] = min(1.0, emotions["satisfaction"] + 0.1)
        else:
            emotions["satisfaction"] = 0.1

        # Frustration relief
        if "frustration" in drives:
            drives["frustration"].intensity = max(0.0, drives["frustration"].intensity - 0.05)

        # Achievement partial fulfillment
        if "achievement" in drives:
            drives["achievement"].intensity = max(0.0, drives["achievement"].intensity - 0.03)
    else:
        # Frustration increase
        if "frustration" in drives:
            drives["frustration"].intensity = min(1.0, drives["frustration"].intensity + 0.15)

        # Achievement drive intensifies on failure (want to try harder)
        if "achievement" in drives:
            drives["achievement"].intensity = min(1.0, drives["achievement"].intensity + 0.05)

    # Slow response → mild anxiety
    if response_time_ms is not None and response_time_ms > 30000:  # 30s+
        if "anxiety" in emotions:
            emotions["anxiety"] = min(1.0, emotions["anxiety"] + 0.05)
