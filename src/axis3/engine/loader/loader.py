# axis3/engine/loader/loader.py
"""
Legacy entry point — delegates to canonical Axis2 integration loader.

Prefer: axis3.integration.runtime_loader
"""

from __future__ import annotations

from typing import Iterable

from axis1.schema import Axis1Card
from axis2.schema import Axis2Card

from axis3.state.game_state import GameState
from axis3.state.zones import ZoneType as Zone
from axis3.state.objects import RuntimeObject

from axis3.integration.runtime_loader import (
    compile_axis2,
    create_runtime_object as _create_runtime_object,
    build_game_state_from_axis1_decks,
)


def create_runtime_object(
    axis1_card: Axis1Card,
    axis2_card: Axis2Card,
    owner_id: int,
    zone: Zone,
    game_state: GameState,
) -> RuntimeObject:
    return _create_runtime_object(axis1_card, axis2_card, owner_id, zone, game_state)


def build_game_state_from_decks(
    player1_deck_axis1: Iterable[Axis1Card],
    player2_deck_axis1: Iterable[Axis1Card],
    axis2_builder=None,
) -> GameState:
    """axis2_builder is ignored; Axis2BuildPipeline is always used."""
    return build_game_state_from_axis1_decks(player1_deck_axis1, player2_deck_axis1)
