# axis3/rules/handlers/untap_handler.py

from axis3.rules.events.types import EventType
from axis3.rules.events.event import Event

def handle_untap_event(gs: "GameState", event: Event):
    active = event.payload["active_player"]

    print(f"Untapping player {active}")

    # 1. Untap permanents
    for obj in gs.objects.values():
        if obj.zone.name == "BATTLEFIELD" and obj.controller == active:
            obj.tapped = False

    # 2. Clear mana pool
    player = gs.players[active]
    for color in player.mana_pool:
        player.mana_pool[color] = 0
