from .base import Action
from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

class PlayLandAction(Action):
    def __init__(self, player_id: int, card_id: str):
        super().__init__(player_id)
        self.card_id = card_id

    def execute(self, gs):
        player = gs.players[self.player_id]

        max_lands = gs.max_lands_per_turn(self.player_id)
        lands_played = gs.turn.lands_played_this_turn[self.player_id]

        if self.card_id not in player.hand:
            print("You don't have that card in hand.")
            return

        obj = gs.objects[self.card_id]
        # Check the card is actually a land 
        if not obj.is_land(): 
            print("You can only play lands using 'playland'.") 
            return

        if lands_played >= max_lands:
            print(f"You have already played {lands_played} land(s) this turn.")
            return
            
        # ✅ let move_card handle all zone changes
        gs.move_card(self.card_id, "BATTLEFIELD", self.player_id)

        gs.event_bus.publish(Event(
            type=EventType.ENTERS_BATTLEFIELD,
            payload={"card_id": self.card_id, "player_id": self.player_id}
        ))
