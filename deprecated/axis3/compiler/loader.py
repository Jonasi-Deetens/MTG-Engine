# src/axis3/compiler/loader.py

from __future__ import annotations
import itertools
import random
from typing import Iterable, List

from axis1.schema import Axis1Card

from axis3.cards.card_builder import Axis3CardBuilder
from axis3.state.game_state import GameState, PlayerState
from axis3.state.zones import ZoneType as Zone


_uid_counter = itertools.count(1)

def _next_id() -> str:
    return f"obj_{next(_uid_counter)}"


def build_game_state_from_decks(
    player1_deck_axis1: Iterable[Axis1Card],
    player2_deck_axis1: Iterable[Axis1Card],
) -> GameState:

    # Create empty object map and players
    objects = {}
    players: List[PlayerState] = [
        PlayerState(id=0, life=20),
        PlayerState(id=1, life=20),
    ]

    # Create an empty GameState (systems initialize in __post_init__)
    game_state = GameState(players=players, objects=objects)

    # Helper to load a deck into a player's library
    def load_deck(axis1_cards: Iterable[Axis1Card], player_id: int):
        for axis1_card in axis1_cards:
            axis3_card = Axis3CardBuilder.build(axis1_card)

            # Create a RuntimeObject using the GameState factory
            rt_obj = game_state.create_object(
                axis3_card=axis3_card,
                owner=player_id,
                controller=player_id,
                zone=Zone.LIBRARY,
            )

            # Store in global object map
            objects[rt_obj.id] = rt_obj

            # Add to player's library
            players[player_id].library.append(rt_obj.id)

    # Load both decks
    load_deck(player1_deck_axis1, 0)
    load_deck(player2_deck_axis1, 1)

    # Shuffle libraries
    random.shuffle(players[0].library)
    random.shuffle(players[1].library)

    return game_state
