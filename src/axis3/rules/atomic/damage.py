# axis3/rules/atomic/damage.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements

def apply_damage(game_state, event: Event):
    """
    Apply a damage event to a target object or player.
    Replacement effects are applied first.
    event.payload must include: target_id, amount, damage_type
    """
    # 1️⃣ Apply replacements
    event = apply_replacements(game_state, event)

    target_id = event.payload["target_id"]
    amount = event.payload["amount"]
    damage_type = event.payload.get("damage_type", "default")

    # Player damage
    if target_id in game_state.players_by_id:
        player = game_state.players_by_id[target_id]
        player.life -= amount

        game_state.event_bus.publish(Event(
            type=EventType.LIFE_CHANGE,
            payload={"player_id": target_id, "amount": -amount, "cause": damage_type}
        ))
        return

    # Permanent damage
    rt_obj = game_state.objects.get(target_id)
    if rt_obj is None or rt_obj.zone != "BATTLEFIELD":
        return

    rt_obj.damage += amount
    game_state.event_bus.publish(Event(
        type=EventType.DAMAGE,
        payload={"obj_id": target_id, "amount": amount, "cause": damage_type}
    ))
