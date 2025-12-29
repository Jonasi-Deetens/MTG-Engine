# axis3/rules/atomic/damage.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements


def apply_damage(game_state, event: Event):
    """
    Apply a damage event to a target object or player.
    Replacement effects are applied first.
    """

    # 1️⃣ Apply replacement effects
    event = apply_replacements(game_state, event)
    if event is None:
        return

    target_id = event.payload["target_id"]
    amount = event.payload["amount"]
    damage_type = event.payload.get("damage_type", "default")

    # 2️⃣ Player damage
    if target_id in game_state.players_by_id:
        # Do NOT modify life directly — publish a life change event
        game_state.event_bus.publish(Event(
            type=EventType.LIFE_CHANGE,
            payload={
                "player_id": target_id,
                "amount": -amount,
                "cause": damage_type
            }
        ))

        # Derived event: damage was dealt
        game_state.event_bus.publish(Event(
            type=EventType.DAMAGE_DEALT,
            payload={
                "target_id": target_id,
                "amount": amount,
                "cause": damage_type
            }
        ))
        return

    # 3️⃣ Permanent damage
    rt_obj = game_state.objects.get(target_id)
    if rt_obj is None or rt_obj.zone != "BATTLEFIELD":
        return

    rt_obj.damage += amount

    # Derived event: damage was dealt
    game_state.event_bus.publish(Event(
        type=EventType.DAMAGE_DEALT,
        payload={
            "obj_id": target_id,
            "amount": amount,
            "cause": damage_type
        }
    ))
