from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

class TapCost:
    def pay(self, game_state: "GameState", obj: "RuntimeObject"):
        if obj.tapped:
            raise Exception(f"{obj.id} is already tapped and cannot pay TapCost")

        obj.tapped = True

        # Fire tap events
        game_state.event_bus.publish(Event(
            type=EventType.TAP,
            payload={
                "obj_id": obj.id,
                "controller": obj.controller
            }
        ))

        game_state.event_bus.publish(Event(
            type=EventType.BECOMES_TAPPED,
            payload={
                "obj_id": obj.id,
                "controller": obj.controller
            }
        ))
