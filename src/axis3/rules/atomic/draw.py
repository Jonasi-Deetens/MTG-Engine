# axis3/rules/atomic/draw.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements
from axis3.state.zones import ZoneType as Zone

def apply_draw(game_state, event: Event):
    """
    Draw one or more cards from a player's library into their hand.
    Replacement effects are applied first.
    event.payload must include: player_id, amount
    """
    # 1️⃣ Apply replacements
    event = apply_replacements(game_state, event)

    player_id = event.payload["player_id"]
    amount = event.payload.get("amount", 1)
    ps = game_state.players[player_id]

    for _ in range(amount):
        if not ps.library:
            break
        card_id = ps.library.pop()
        ps.hand.append(card_id)

        rt_obj = game_state.objects[card_id]
        rt_obj.zone = Zone.HAND

        game_state.event_bus.publish(Event(
            type=EventType.DRAW,
            payload={"player_id": player_id, "obj_id": card_id}
        ))
