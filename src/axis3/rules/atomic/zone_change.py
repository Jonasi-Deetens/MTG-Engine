# axis3/rules/atomic/zone_change.py

from axis3.state.zones import ZoneType as Zone
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements

def apply_zone_change(game_state, event: Event):
    """
    Apply a ZONE_CHANGE event to the game state.
    Handles replacement effects, actual movement, and derived events.
    
    event.payload should include:
      obj_id, from_zone, to_zone, controller, cause
    """
    obj_id = event.payload["obj_id"]
    from_zone = event.payload["from_zone"]
    to_zone = event.payload["to_zone"]
    controller = event.payload["controller"]
    cause = event.payload.get("cause", None)

    rt_obj = game_state.objects.get(obj_id)
    if not rt_obj:
        return  # object may have already been removed

    # 1️⃣ Apply replacement effects first
    event = apply_replacements(game_state, event)

    # 2️⃣ Actually move object
    # Remove from old zone
    if from_zone is not None and obj_id in game_state.zone_list(controller, from_zone):
        game_state.zone_list(controller, from_zone).remove(obj_id)

    # Add to new zone
    if to_zone is not None:
        game_state.zone_list(controller, to_zone).append(obj_id)
        rt_obj.zone = to_zone
        rt_obj.controller = controller
    else:
        # Special case: token removal
        del game_state.objects[obj_id]

    # 3️⃣ Reset damage if moving from battlefield
    if from_zone == Zone.BATTLEFIELD:
        rt_obj.damage = 0

    # 4️⃣ Derived events
    # Leaving battlefield
    if from_zone == Zone.BATTLEFIELD:
        game_state.event_bus.publish(Event(
            type=EventType.LEAVES_BATTLEFIELD,
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))

    # Entering battlefield
    if to_zone == Zone.BATTLEFIELD:
        game_state.event_bus.publish(Event(
            type=EventType.ENTERS_BATTLEFIELD,
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))

    # Dies event: creature leaving battlefield to graveyard
    if from_zone == Zone.BATTLEFIELD and to_zone == Zone.GRAVEYARD and "Creature" in rt_obj.characteristics.types:
        game_state.event_bus.publish(Event(
            type="dies",
            payload={"obj_id": obj_id, "controller": controller, "cause": cause}
        ))
