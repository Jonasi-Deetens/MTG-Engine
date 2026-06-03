# axis3/rules/atomic/zone_change.py

from axis3.state.zones import ZoneType as Zone
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements


def apply_zone_change(game_state, event: Event):
    """
    Apply a ZONE_CHANGE event to the game state.
    Handles replacement effects, actual movement, and derived events.
    """

    # 1️⃣ Apply replacement effects FIRST
    event = apply_replacements(game_state, event)
    if event is None:
        return

    obj_id = event.payload["obj_id"]
    from_zone = event.payload["from_zone"]
    to_zone = event.payload["to_zone"]
    controller = event.payload["controller"]
    cause = event.payload.get("cause")

    rt_obj = game_state.objects.get(obj_id)
    if not rt_obj:
        return

    # 2️⃣ Move object between zones
    if from_zone is not None:
        zone_list = game_state.zone_list(controller, from_zone)
        if obj_id in zone_list:
            zone_list.remove(obj_id)

    if to_zone is not None:
        game_state.zone_list(controller, to_zone).append(obj_id)
        rt_obj.zone = to_zone
        rt_obj.controller = controller
    else:
        # Token ceases to exist
        del game_state.objects[obj_id]
        return

    # 3️⃣ Reset damage if leaving battlefield
    if from_zone == Zone.BATTLEFIELD:
        rt_obj.damage = 0

    # 4️⃣ Derived events
    if from_zone == Zone.BATTLEFIELD:
        game_state.event_bus.publish(Event(
            type=EventType.LEAVES_BATTLEFIELD,
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))

    if to_zone == Zone.BATTLEFIELD:
        game_state.event_bus.publish(Event(
            type=EventType.ENTERS_BATTLEFIELD,
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))

    # Creature dies
    ec = game_state.layers.evaluate(obj_id)
    if from_zone == Zone.BATTLEFIELD and to_zone == Zone.GRAVEYARD and "Creature" in ec.types:
        game_state.event_bus.publish(Event(
            type=EventType.CREATURE_DIES,
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))
