# axis3/compiler/loader.py
"""
Legacy entry point — delegates to canonical Axis2 integration loader.

Do not use Axis3CardBuilder or axis3/rules/builder for new code.
"""

from __future__ import annotations
from typing import Iterable

from axis1.schema import Axis1Card
from axis3.state.game_state import GameState
from axis3.integration.runtime_loader import build_game_state_from_axis1_decks


def build_game_state_from_decks(
    player1_deck_axis1: Iterable[Axis1Card],
    player2_deck_axis1: Iterable[Axis1Card],
) -> GameState:
    return build_game_state_from_axis1_decks(player1_deck_axis1, player2_deck_axis1)
