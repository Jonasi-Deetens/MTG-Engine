# axis3/engine/stack/resolver.py

from axis3.engine.stack.item import StackItem
from axis3.engine.abilities.triggered import RuntimeTriggeredAbility
from axis3.rules.events.event import Event
from axis3.rules.replacement.apply import apply_replacements
from axis3.rules.atomic import zone_change
from axis3.rules.sba.checker import run_sbas


def resolve_runtime_triggered_ability(game_state, rta: RuntimeTriggeredAbility):
    rta.resolve(game_state)


def _get_types(rt_obj) -> list:
    if getattr(rt_obj, "characteristics", None):
        return getattr(rt_obj.characteristics, "types", []) or []
    if getattr(rt_obj, "axis2_card", None) and rt_obj.axis2_card:
        return rt_obj.axis2_card.characteristics.types or []
    if getattr(rt_obj, "axis3_card", None) and rt_obj.axis3_card:
        return rt_obj.axis3_card.types or []
    return []


def _resolve_spell_effects(game_state, rt_obj, controller: int):
    axis2 = getattr(rt_obj, "axis2_card", None)
    if not axis2:
        return
    effects = []
    for face in getattr(axis2, "faces", []) or []:
        effects.extend(getattr(face, "spell_effects", []) or [])
    if effects:
        game_state.effect_executor.execute_all(effects, rt_obj.id, controller)


def resolve_top_of_stack(game_state):
    """
    Resolve the top item on the stack (LIFO).
  """
    if not game_state.stack or game_state.stack.is_empty():
        return

    item: StackItem = game_state.stack.pop()

    if item.is_triggered_ability():
        resolve_runtime_triggered_ability(game_state, item.triggered_ability)
        run_sbas(game_state)
        return

    if item.is_activated_ability():
        raa = item.activated_ability
        if hasattr(raa, "pay_costs") and not raa.pay_costs(game_state):
            return
        raa.effect(game_state)
        run_sbas(game_state)
        return

    obj_id = item.obj_id
    if obj_id is None or obj_id not in game_state.objects:
        return

    rt_obj = game_state.objects[obj_id]
    types = _get_types(rt_obj)

    is_permanent = any(
        t in ("Creature", "Artifact", "Enchantment", "Planeswalker", "Land", "Battle")
        for t in types
    )

    if not is_permanent:
        _resolve_spell_effects(game_state, rt_obj, item.controller)

    if is_permanent:
        to_zone = "BATTLEFIELD"
    else:
        to_zone = "GRAVEYARD"

    if rt_obj.is_token and not is_permanent:
        del game_state.objects[rt_obj.id]
        run_sbas(game_state)
        return

    event = Event(
        type="zone_change",
        payload={
            "obj_id": rt_obj.id,
            "from_zone": rt_obj.zone,
            "to_zone": to_zone,
            "controller": item.controller,
            "cause": "resolution",
        },
    )

    event = apply_replacements(game_state, event)
    zone_change.apply_zone_change(game_state, event)
    run_sbas(game_state)


def resolve_stack(game_state):
    while game_state.stack and not game_state.stack.is_empty():
        resolve_top_of_stack(game_state)
