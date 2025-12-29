# axis3/rules/replacement/apply.py

from __future__ import annotations
from axis3.rules.events.event import Event
from axis3.state.objects import RuntimeObject

# For type hints only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from axis3.state.game_state import GameState


def apply_replacements(game_state: GameState, event: Event) -> Event:
    """
    Apply all replacement effects to an event, returning the modified event.
    Replacement effects may chain, so we loop until stable.
    """
    current_event = event

    while True:
        changed = False

        # 1️⃣ Object-specific replacement effects
        obj_id = current_event.payload.get("obj_id")
        if obj_id is not None:
            rt_obj: RuntimeObject | None = game_state.objects.get(obj_id)
            if rt_obj:
                for eff in getattr(rt_obj, "replacement_effects", []):
                    new_event = _check_and_apply(eff, current_event, game_state, rt_obj)
                    if new_event is not None and new_event is not current_event:
                        current_event = new_event
                        changed = True

        # 2️⃣ Global replacement effects
        for eff in getattr(game_state, "replacement_effects", []):
            new_event = _check_and_apply(eff, current_event, game_state, None)
            if new_event is not None and new_event is not current_event:
                current_event = new_event
                changed = True

        # No more changes → event is stable
        if not changed:
            return current_event


def _check_and_apply(eff, event: Event, game_state: GameState, rt_obj: RuntimeObject | None) -> Event | None:
    """
    Apply a single replacement effect if its condition passes.
    Returns a new Event or None if unchanged.
    """
    # Must have both condition and apply
    if not hasattr(eff, "condition") or not hasattr(eff, "apply"):
        return None

    try:
        if eff.condition(game_state, event, rt_obj):
            return eff.apply(game_state, event, rt_obj)
    except TypeError:
        # Backwards compatibility for older effects using condition(event)
        if eff.condition(event):
            return eff.apply(event)

    return None
