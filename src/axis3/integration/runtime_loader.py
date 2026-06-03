"""
Load cards into GameState using Axis2 as the only effect builder.

Replaces:
  - axis3/compiler/loader.py (broken Axis3CardBuilder import)
  - axis3/rules/builder/* (duplicate regex)
"""

from __future__ import annotations

import random
from typing import Iterable, List

from axis1.schema import Axis1Card
from axis2.build_pipeline import Axis2BuildPipeline
from axis2.schema import Axis2Card

from axis3.state.game_state import GameState, PlayerState
from axis3.state.objects import RuntimeObject
from axis3.state.zones import ZoneType as Zone
from axis3.engine.stack.stack import Stack

from axis3.engine.translate.ability_builder import register_runtime_abilities_for_object
from axis3.engine.translate.continuous_builder import build_continuous_effects_for_object
from axis3.engine.translate.replacement_builder import build_replacement_effects_for_object
from axis3.engine.translate.activated_builder import register_runtime_activated_abilities


_pipeline = Axis2BuildPipeline()


def compile_axis2(axis1_card: Axis1Card) -> Axis2Card:
    """Run the Axis2 effect-builder wizard."""
    return _pipeline.build(axis1_card)


def create_runtime_object(
    axis1_card: Axis1Card,
    axis2_card: Axis2Card,
    owner_id: int,
    zone: Zone,
    game_state: GameState,
) -> RuntimeObject:
    """Attach Axis2 rules to a runtime object (canonical loader)."""
    obj_id = axis1_card.card_id
    rt_obj = RuntimeObject(
        id=obj_id,
        owner=int(owner_id),
        controller=int(owner_id),
        zone=zone,
        name=axis1_card.names[0] if axis1_card.names else "",
        axis1_card=axis1_card,
        axis2_card=axis2_card,
        characteristics=axis2_card.characteristics,
    )

    register_runtime_abilities_for_object(game_state, rt_obj)
    build_continuous_effects_for_object(game_state, rt_obj)
    build_replacement_effects_for_object(game_state, rt_obj)
    register_runtime_activated_abilities(game_state, rt_obj)

    return rt_obj


def build_game_state_from_axis1_decks(
    player1_deck: Iterable[Axis1Card],
    player2_deck: Iterable[Axis1Card],
) -> GameState:
    """Build a full game from two Axis1 decks using Axis2BuildPipeline."""
    players: List[PlayerState] = [
        PlayerState(id=0, life=20),
        PlayerState(id=1, life=20),
    ]
    objects = {}

    game_state = GameState(players=players, objects=objects, stack=Stack())

    def load_deck(cards: Iterable[Axis1Card], player_id: int) -> None:
        for axis1 in cards:
            axis2 = compile_axis2(axis1)
            rt = create_runtime_object(
                axis1, axis2, player_id, Zone.LIBRARY, game_state
            )
            objects[rt.id] = rt
            players[player_id].library.append(rt.id)

    load_deck(player1_deck, 0)
    load_deck(player2_deck, 1)

    game_state.objects = objects
    random.shuffle(players[0].library)
    random.shuffle(players[1].library)

    return game_state
