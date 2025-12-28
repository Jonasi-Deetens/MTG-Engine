# axis3/rules/atomic/life.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.rules.replacement.apply import apply_replacements

def apply_life_change(game_state, event: Event):
    """
    Adjust a player's life total.
    Positive = gain, negative = lose.
    Replacement effects are applied first.
    """
    # 1️⃣ Apply replacements
    event = apply_replacements(game_state, event)

    player_id = event.payload["player_id"]
    amount = event.payload["amount"]

    player = game_state.players[player_id]
    player.life += amount

    game_state.event_bus.publish(Event(
        type=EventType.LIFE_CHANGE,
        payload={"player_id": player_id, "amount": amount}
    ))
