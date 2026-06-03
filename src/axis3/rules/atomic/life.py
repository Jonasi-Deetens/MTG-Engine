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

    # 1️⃣ Apply replacement effects
    event = apply_replacements(game_state, event)
    if event is None:
        return

    player_id = event.payload["player_id"]
    amount = event.payload["amount"]

    # 2️⃣ Apply the life change
    player = game_state.players[player_id]
    player.life += amount

    # 3️⃣ Publish a derived event (NOT another LIFE_CHANGE)
    game_state.event_bus.publish(Event(
        type=EventType.LIFE_CHANGED,
        payload={
            "player_id": player_id,
            "amount": amount,
            "cause": event.payload.get("cause")
        }
    ))
