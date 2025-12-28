# axis3/rules/replacement/apply.py

from axis3.rules.events.event import Event

def apply_replacements(game_state, event: Event) -> Event:
    """
    Apply all replacement effects to a given event.
    Replacement effects can come from:
      1️⃣ Object-specific replacement effects (Axis2)
      2️⃣ Global/continuous replacement effects (battlefield, static abilities)
    Returns a potentially modified Event.
    """
    obj_id = event.payload.get("obj_id")

    # -------------------------
    # 1️⃣ Object-specific effects
    # -------------------------
    if obj_id is not None:
        rt_obj = game_state.objects.get(obj_id)
        if rt_obj:
            for eff in getattr(rt_obj.axis2, "replacement_effects", []):
                event = _apply_single_replacement(game_state, event, rt_obj, eff)

    # -------------------------
    # 2️⃣ Global / continuous effects
    # -------------------------
    for eff in getattr(game_state, "global_replacement_effects", []):
        event = _apply_single_replacement(game_state, event, None, eff)

    return event


def _apply_single_replacement(game_state, event: Event, rt_obj, eff) -> Event:
    """
    Apply a single replacement effect to an event.
    """
    eff_event = getattr(eff, "event", None)
    replacement = getattr(eff, "replacement", None)

    if eff_event is None or replacement is None:
        return event

    # -------- Object dies → exile instead
    if eff_event in ("die", "dies") and event.payload.get("to_zone") == "GRAVEYARD":
        if replacement == "exile":
            event.payload["to_zone"] = "EXILE"

    # -------- Enters battlefield tapped
    if eff_event in ("enter_battlefield", "enters_battlefield"):
        if replacement == "enters_tapped" and rt_obj:
            rt_obj.tapped = True

    # -------- Draw replacement
    if eff_event == "draw" and event.type == "draw":
        if replacement == "gain_life_instead":
            player_id = event.payload.get("player_id")
            if player_id is not None:
                game_state.players[player_id].life += 1
            event.payload["skip"] = True  # prevent actual draw

    # -------- Life loss replacement
    if eff_event == "lose_life" and event.type == "life_change":
        if replacement == "prevent":
            event.payload["skip"] = True

    # -------- Example: reduce spell cost (future integration)
    if eff_event == "spell_cast" and event.type == "cast_spell":
        if replacement.startswith("reduce_cost_"):
            amount = int(replacement.split("_")[-1])
            if "mana_cost" in event.payload:
                event.payload["mana_cost"].colorless = max(
                    0, event.payload["mana_cost"].colorless - amount
                )

    return event
