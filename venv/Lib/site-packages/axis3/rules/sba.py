# src/axis3/rules/sba.py

from __future__ import annotations

from typing import List

from axis3.state.game_state import GameState
from axis3.state.objects import RuntimeObject, RuntimeObjectId, RuntimeToken
from axis3.state.zones import ZoneType as Zone
from axis3.rules.events import Event
from axis3.rules.replacement import apply_replacement_effects
from axis3.rules.zone_change import _perform_zone_change
from axis3.rules.layers import evaluate_characteristics


def run_sbas(game_state: GameState) -> None:
    """
    Run state-based actions until no more apply.
    This is the core SBA loop.
    """

    while True:
        changes_made = False

        # 1. Player loses the game at life <= 0
        for player in game_state.players:
            if player.life <= 0:
                # For now, just mark them as dead.
                # Later: eliminate them from game.
                player.life = 0
                # You can add a flag like player.dead = True
                # but for now we just stop the game.
                # No further SBAs needed.
                return

        # 2. Creatures with lethal damage die
        for obj_id, rt_obj in list(game_state.objects.items()):
            if rt_obj.zone == Zone.BATTLEFIELD and "Creature" in rt_obj.characteristics.types:
                ec = evaluate_characteristics(game_state, rt_obj.id)
                toughness = ec.toughness
                if rt_obj.damage >= toughness:
                    _move_to_graveyard(game_state, rt_obj)
                    changes_made = True
                    continue

        # 3. Creatures with 0 or less toughness die
        for obj_id, rt_obj in list(game_state.objects.items()):
            if rt_obj.zone == Zone.BATTLEFIELD and "Creature" in rt_obj.characteristics.types:
                ec = evaluate_characteristics(game_state, rt_obj.id)
                toughness = ec.toughness
                if toughness <= 0:
                    _move_to_graveyard(game_state, rt_obj)
                    changes_made = True
                    continue

        # 4. Tokens cease to exist when not on battlefield
        for obj_id, rt_obj in list(game_state.objects.items()):
            if isinstance(rt_obj, RuntimeToken) and rt_obj.zone != Zone.BATTLEFIELD:
                _move_to_graveyard(game_state, rt_obj)
                changes_made = True
                continue

        # 5. Legendary rule (simple version)
        # If a player controls 2+ legendary permanents with same name → keep one, others die
        for player in game_state.players:
            name_groups = {}
            for obj_id in player.battlefield:
                rt_obj = game_state.objects[obj_id]
                if "Legendary" in rt_obj.characteristics.supertypes:
                    name_groups.setdefault(rt_obj.characteristics.name, []).append(rt_obj)

            for name, objs in name_groups.items():
                if len(objs) > 1:
                    # Keep the first, kill the rest
                    for rt_obj in objs[1:]:
                        _move_to_graveyard(game_state, rt_obj)
                        changes_made = True

        # If no SBAs applied, we’re done
        if not changes_made:
            return


def _move_to_graveyard(game_state: GameState, rt_obj: RuntimeObject):
    """
    Move a permanent to its owner's graveyard.
    """
    owner = game_state.players[rt_obj.owner]

    event = {
        "type": "zone_change",
        "obj_id": rt_obj.id,
        "from_zone": rt_obj.zone,
        "to_zone": Zone.GRAVEYARD,
        "controller": rt_obj.controller,
    }

    event = apply_replacement_effects(game_state, event)
    _perform_zone_change(game_state, event)

    # Reset damage
    rt_obj.damage = 0

    if "Creature" in rt_obj.characteristics.types: 
        game_state.event_bus.publish(Event( 
            type="dies", 
            payload={"obj_id": rt_obj.id} 
        ))