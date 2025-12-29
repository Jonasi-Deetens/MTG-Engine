from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

class AddManaEffect:
    def __init__(self, color):
        self.color = color

    def apply(self, game_state: "GameState", obj: "RuntimeObject"):
        player = game_state.players[obj.controller]
        player.mana_pool[self.color] += 1

        game_state.event_bus.publish(Event(
            type=EventType.MANA_ABILITY_RESOLVED,
            payload={
                "obj_id": obj.id,
                "controller": obj.controller,
                "color": self.color
            }
        ))
