# src/axis3/rules/actions.py

from __future__ import annotations

from typing import Optional

from axis3.state.game_state import GameState
from axis3.state.zones import ZoneType as Zone
from axis3.state.objects import RuntimeObject
from axis3.rules.sba import run_sbas
from axis3.rules.events import Event
from axis3.abilities.triggered import RuntimeTriggeredAbility
from axis3.rules.replacement import apply_replacement_effects
from axis3.rules.zone_change import _perform_zone_change


def _get_zone_list_for_player(game_state: GameState, player_id: int, zone: Zone):
    ps = game_state.players[player_id]
    if zone == Zone.LIBRARY:
        return ps.library
    if zone == Zone.HAND:
        return ps.hand
    if zone == Zone.BATTLEFIELD:
        return ps.battlefield
    if zone == Zone.GRAVEYARD:
        return ps.graveyard
    if zone == Zone.EXILE:
        return ps.exile
    if zone == Zone.COMMAND:
        return ps.command
    raise ValueError(f"Zone {zone} is not a per-player zone")


def draw_card(game_state: GameState, player_id: int, n: int = 1) -> None:
    """
    Draw n cards from the player's library into their hand.
    No loss-on-empty-library handling yet; just a foundation.
    """
    ps = game_state.players[player_id]

    for _ in range(n):
        if not ps.library:
            # Mill / loss will be handled later; for now, just stop drawing.
            break

        obj_id = ps.library.pop()  # top of library = end of list
        ps.hand.append(obj_id)

        rt_obj = game_state.objects[obj_id]
        rt_obj.zone = Zone.HAND


def move_object_between_players_zone(
    game_state: GameState,
    obj_id,
    from_player_id: int,
    from_zone: Zone,
    to_player_id: int,
    to_zone: Zone,
    to_index: Optional[int] = None,
) -> None:
    """
    Move an object from one player's zone to another's.

    This is mostly for completeness; most moves will be same-player.
    """
    from_list = _get_zone_list_for_player(game_state, from_player_id, from_zone)
    to_list = _get_zone_list_for_player(game_state, to_player_id, to_zone)

    if obj_id not in from_list:
        raise ValueError(f"Object {obj_id} not found in {from_zone} of player {from_player_id}")

    from_list.remove(obj_id)

    if to_index is None or to_index >= len(to_list):
        to_list.append(obj_id)
    else:
        to_list.insert(to_index, obj_id)

    rt_obj = game_state.objects[obj_id]
    rt_obj.zone = to_zone
    rt_obj.controller = to_player_id  # may or may not be desired; adjust later

from axis3.engine.stack.item import StackItem
from axis3.state.zones import ZoneType as Zone


def cast_spell_from_hand(
    game_state: GameState,
    player_id: int,
    obj_id,
    x_value: int = None,
):
    """
    Cast a spell from hand. For Phase 2, we skip:
    - mana payment
    - stack
    - timing restrictions
    - targeting
    - triggers

    We simply:
    1. Verify the card is in hand
    2. Move it to a temporary 'resolving' state
    3. Resolve immediately
    
    """
    rt_obj = game_state.objects[obj_id]
    # ⭐ Lands are played, not cast 
    if "Land" in rt_obj.characteristics.types:
        return play_land_from_hand(game_state, player_id, obj_id)

    ps = game_state.players[player_id]

    if obj_id not in ps.hand:
        raise ValueError(f"Player {player_id} cannot cast {obj_id}: not in hand")

    # Remove from hand
    ps.hand.remove(obj_id)
    rt_obj.zone = Zone.STACK

    # Push onto stack
    game_state.stack.push(StackItem(
        obj_id=obj_id,
        controller=player_id,
        x_value=x_value,
    ))

    game_state.event_bus.publish(Event(
        type="cast_this_spell",
        payload={"obj_id": obj_id}
    ))

def play_land_from_hand(game_state, player_id, obj_id):
    rt_obj = game_state.objects[obj_id]
    ps = game_state.players[player_id]

    # Remove from hand
    ps.hand.remove(obj_id)

    # ⭐ Apply ETB replacement effects BEFORE entering battlefield
    for eff in rt_obj.axis2.replacement_effects:
        # Axis2 ReplacementEffect object
        event = getattr(eff, "event", None)
        replacement = getattr(eff, "replacement", None)

        if event in ("enter_battlefield", "enters_battlefield"):
            if replacement == "enters_tapped":
                rt_obj.tapped = True

    # Now enter battlefield
    rt_obj.zone = Zone.BATTLEFIELD
    ps.battlefield.append(obj_id)

    # Fire ETB triggers
    game_state.event_bus.publish(Event(
        type="enter_battlefield",
        payload={"obj_id": obj_id}
    ))


def resolve_spell_immediately(
    game_state: GameState,
    player_id: int,
    rt_obj: RuntimeObject,
    x_value: int = None,
):
    """
    Resolve a spell immediately (Phase 2).
    Permanent spells → battlefield
    Non-permanent spells → graveyard
    """

    # Determine if this is a permanent spell
    types = rt_obj.characteristics.types

    is_permanent = any(t in ("Creature", "Artifact", "Enchantment", "Planeswalker", "Battle", "Land")
                       for t in types)

    if is_permanent:
        _resolve_permanent_spell(game_state, player_id, rt_obj)
    else:
        _resolve_nonpermanent_spell(game_state, player_id, rt_obj)

def _resolve_permanent_spell(game_state: GameState, player_id: int, rt_obj: RuntimeObject):
    """
    Put a permanent onto the battlefield.
    """

    ps = game_state.players[player_id]
    
    event = {
        "type": "zone_change",
        "obj_id": rt_obj.id,
        "from_zone": rt_obj.zone,
        "to_zone": Zone.BATTLEFIELD,
        "controller": player_id,
    }

    event = apply_replacement_effects(game_state, event)
    _perform_zone_change(game_state, event)

    # Move to battlefieldµ
    rt_obj.controller = player_id

    # Summoning sickness for creatures
    if "Creature" in rt_obj.characteristics.types:
        rt_obj.summoning_sick = True

    run_sbas(game_state)

    game_state.event_bus.publish(Event(
        type="enters_battlefield",
        payload={"obj_id": rt_obj.id}
    ))
    print("DEBUG axis1 oracle_text:", rt_obj.axis1.faces[0].oracle_text)
    print("DEBUG axis1:", rt_obj.axis1.faces)
    print("DEBUG axis2 triggers:", rt_obj.axis2.triggers)
    print("DEBUG _resolve_permanent_spell axis2:", rt_obj.axis2)
    print("DEBUG _resolve_permanent_spell axis2.triggers:", getattr(rt_obj.axis2, "triggers", None))
    # ⭐ NEW: turn Axis2 ETB triggers into RuntimeTriggeredAbility on the stack 
    for trig in rt_obj.axis2.triggers: 
        if trig.event == "enters_battlefield": 
            rta = RuntimeTriggeredAbility( 
                source_id=rt_obj.id, 
                controller=rt_obj.controller, 
                axis2_trigger=trig, 
            ) 
            game_state.stack.push(StackItem(triggered_ability=rta))


def _resolve_nonpermanent_spell(game_state: GameState, player_id: int, rt_obj: RuntimeObject):
    """
    Sorceries/instants go to graveyard after resolving.
    """

    ps = game_state.players[player_id]

    # For Phase 2, we skip the actual effect.
    # Later we will execute Axis2 effect_text here.

    event = {
        "type": "zone_change",
        "obj_id": rt_obj.id,
        "from_zone": rt_obj.zone,
        "to_zone": Zone.GRAVEYARD,
        "controller": player_id,
    }

    event = apply_replacement_effects(game_state, event)
    _perform_zone_change(game_state, event)


    run_sbas(game_state)

def resolve_top_of_stack(game_state: GameState):
    """
    Pop the top stack item and resolve it.
    """
    if game_state.stack.is_empty():
        return

    item = game_state.stack.pop()

    # Triggered ability? 
    if item.triggered_ability is not None: 
        rta = item.triggered_ability 
        _resolve_triggered_ability(game_state, rta) 
        return

    rt_obj = game_state.objects[item.obj_id]

    # Determine if permanent
    types = rt_obj.characteristics.types
    is_permanent = any(t in ("Creature", "Artifact", "Enchantment", "Planeswalker", "Battle", "Land")
                       for t in types)

    if is_permanent:
        _resolve_permanent_spell(game_state, item.controller, rt_obj)
    else:
        _resolve_nonpermanent_spell(game_state, item.controller, rt_obj)


def _resolve_triggered_ability(game_state: GameState, rta: RuntimeTriggeredAbility):
    """
    Execute the effect_text of the Axis2 trigger.
    For now, we stub this out.
    """

    effect = rta.axis2_trigger.effect_text.lower()

    # Minimal examples:
    if "draw a card" in effect:
        from axis3.rules.actions import draw_card
        draw_card(game_state, rta.controller, 1)

    if "lose 1 life" in effect:
        game_state.players[rta.controller].life -= 1

    # Later: full effect parser + executor
