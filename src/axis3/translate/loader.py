# src/axis3/translate/loader.py

from __future__ import annotations
import itertools
import random
from typing import Iterable, List

from axis1.schema import Axis1Card
from axis2.builder import Axis2Builder
from axis2.schema import Axis2Card

from axis3.state.objects import RuntimeObject, RuntimeObjectId
from axis3.state.characteristics import RuntimeCharacteristics
from axis3.state.game_state import GameState, PlayerState
from axis3.state.zones import ZoneType as Zone
from axis3.rules.stack import Stack
from axis3.rules.events import EventBus

from axis3.translate.ability_builder import register_runtime_triggers_for_object
from axis3.translate.continuous_builder import build_continuous_effects_for_object
from axis3.translate.replacement_builder import build_replacement_effects_for_object


_uid_counter = itertools.count(1)

def _next_id() -> RuntimeObjectId:
    return str(next(_uid_counter))


def derive_base_characteristics(axis1_card: Axis1Card) -> RuntimeCharacteristics:
    face = axis1_card.faces[0]
    return RuntimeCharacteristics(
        name=getattr(face, "name", axis1_card.names[0] if axis1_card.names else "Unknown"),
        mana_cost=getattr(face, "mana_cost", None),
        types=list(getattr(face, "types", []) or []),
        supertypes=list(getattr(face, "supertypes", []) or []),
        subtypes=list(getattr(face, "subtypes", []) or []),
        colors=list(getattr(face, "colors", []) or []),
        power=int(getattr(face, "power", 0)) if getattr(face, "power", None) not in (None, "") else None,
        toughness=int(getattr(face, "toughness", 0)) if getattr(face, "toughness", None) not in (None, "") else None,
    )


def create_runtime_object(
    axis1_card: Axis1Card,
    axis2_card: Axis2Card,
    owner_id: str,
    zone: Zone,
    game_state: GameState,
) -> RuntimeObject:
    obj_id = _next_id()
    characteristics = derive_base_characteristics(axis1_card)

    rt_obj = RuntimeObject(
        id=obj_id,
        owner=str(owner_id),
        controller=str(owner_id),
        zone=zone,
        name=axis1_card.names[0] if hasattr(axis1_card, "names") else "",
        axis1=axis1_card,
        axis2=axis2_card,
        characteristics=characteristics,
    )

    # --- FULL INTEGRATION ---
    register_runtime_triggers_for_object(game_state, rt_obj)
    build_continuous_effects_for_object(game_state, rt_obj)
    build_replacement_effects_for_object(game_state, rt_obj)

    return rt_obj


def build_game_state_from_decks(
    player1_deck_axis1: Iterable[Axis1Card],
    player2_deck_axis1: Iterable[Axis1Card],
    axis2_builder: Axis2Builder,
) -> GameState:
    objects: dict = {}
    players: List[PlayerState] = [
        PlayerState(id=0, life=20),
        PlayerState(id=1, life=20),
    ]

    dummy_game_state = GameState(
        players=players,
        objects={},
        stack=Stack(),
        event_bus=EventBus(),
        replacement_effects=[],
        continuous_effects=[],
    )

    # --- Player 0 library ---
    for axis1_card in player1_deck_axis1:
        axis2 = axis2_builder.build(axis1_card, game_state=dummy_game_state)
        rt_obj = create_runtime_object(axis1_card, axis2, owner_id=0, zone=Zone.LIBRARY, game_state=dummy_game_state)
        objects[rt_obj.id] = rt_obj
        players[0].library.append(rt_obj.id)

    # --- Player 1 library ---
    for axis1_card in player2_deck_axis1:
        axis2 = axis2_builder.build(axis1_card, game_state=dummy_game_state)
        rt_obj = create_runtime_object(axis1_card, axis2, owner_id=1, zone=Zone.LIBRARY, game_state=dummy_game_state)
        objects[rt_obj.id] = rt_obj
        players[1].library.append(rt_obj.id)

    # Shuffle libraries
    random.shuffle(players[0].library)
    random.shuffle(players[1].library)

    game_state = GameState(
        players=players,
        objects=objects,
    )

    return game_state
