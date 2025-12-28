# src/axis3/rules/replacement/apply.py

from axis3.rules.events.event import Event
from axis3.state.objects import RuntimeObject

def apply_replacements(game_state: "GameState", event: Event) -> Event:
    """
    Apply all replacement effects to a given event.
    Returns a new Event object (or the original if unchanged).
    """
    obj_id = event.payload.get("obj_id")
    new_event = event

    # 1️⃣ Object-specific replacement effects
    if obj_id is not None:
        rt_obj = game_state.objects.get(obj_id)
        if rt_obj:
            for eff in getattr(rt_obj, "replacement_effects", []):
                result = _check_and_apply(eff, new_event, game_state, rt_obj)
                if result is not None:
                    new_event = result

    # 2️⃣ Global replacement effects
    for eff in getattr(game_state, "replacement_effects", []):
        result = _check_and_apply(eff, new_event, game_state, None)
        if result is not None:
            new_event = result

    return new_event


def _check_and_apply(eff, event: Event, game_state: "GameState", rt_obj) -> Event | None:
    """
    Apply a single replacement effect if its condition passes.
    Returns a new Event or None if no change.
    """
    if not hasattr(eff, "condition") or not hasattr(eff, "apply"):
        return None

    if eff.condition(event):
        return eff.apply(event)

    return None
