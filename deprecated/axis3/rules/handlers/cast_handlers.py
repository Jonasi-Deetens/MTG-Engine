# src/axis3/rules/handlers/cast_handlers.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.state.objects import RuntimeSpell
from axis3.state.zones import ZoneType

def handle_cast_spell(gs, event: Event):
    card_id = event.payload["card_id"]
    player = event.payload["player_id"]

    # 1. Lookup the existing runtime object (currently in HAND)
    old_obj = gs.objects[card_id]

    # 2. Lookup card definition
    old_obj = gs.objects[card_id]
    card_def = old_obj.axis2_card

    # 3. Move the existing object from HAND → STACK
    gs.move_card(card_id, ZoneType.STACK, controller=player)

    # 4. Convert the existing object into a RuntimeSpell
    spell = RuntimeSpell(
        id=old_obj.id,
        owner=old_obj.owner,
        controller=player,
        zone=ZoneType.STACK,
        name=getattr(card_def, "name", old_obj.name),
        axis1_card=card_def,
        characteristics=getattr(card_def, "characteristics", None),
    )

    # Preserve any dynamic state if needed (rare for spells)
    # e.g., counters, chosen modes, etc.

    # 5. Replace the object in the game state
    gs.objects[card_id] = spell

    # 6. Push onto the stack list
    gs.stack.push(card_id)

    # 7. Publish SPELL_CAST for triggers
    gs.event_bus.publish(Event(
        type=EventType.SPELL_CAST,
        payload={"obj_id": card_id, "player_id": player}
    ))
