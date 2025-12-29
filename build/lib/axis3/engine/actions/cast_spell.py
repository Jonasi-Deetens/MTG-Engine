# src/axis3/engine/actions/cast_spell.py

from .base import Action
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.state.zones import ZoneType

class CastSpellAction(Action):
    def __init__(self, player_id: int, card_id: str):
        super().__init__(player_id)
        self.card_id = card_id
        self.kind = "cast"
        self.uses_priority = True

    def execute(self, gs):
        # Fetch the runtime object
        obj = gs.get_object(self.card_id)
        if obj is None:
            print("Card not found.")
            return

        player = gs.players[self.player_id]

        # Must be in hand
        if obj.zone != ZoneType.HAND:
            print("You can only cast spells from your hand.")
            return

        # Must have priority
        if gs.turn_manager.priority.current != self.player_id:
            print("You don't have priority.")
            return


        # Sorcery-speed restriction for creatures
        if obj.is_creature():
            if not gs.turn.is_main_phase() or not gs.stack.is_empty():
                print("You can only cast creature spells at sorcery speed.")
                return

        # 1. Check mana cost
        if hasattr(obj, "mana_cost") and obj.mana_cost is not None:
            if not obj.mana_cost.can_pay(player):
                print(f"Not enough mana to cast {obj.name}.")
                return

            # 2. Pay mana cost
            obj.mana_cost.pay(gs, player)

        # 3. Publish CAST_SPELL event
        gs.event_bus.publish(Event(
            type=EventType.CAST_SPELL,
            payload={
                "card_id": self.card_id,
                "player_id": self.player_id,
                "cause": "cast_action"
            }
        ))
