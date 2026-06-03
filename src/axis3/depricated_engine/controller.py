# src/axis3/engine/controller.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from axis3.state.objects import RuntimeObjectId
from axis3.state.game_state import GameState


class PlayerActionType(Enum):
    CAST_SPELL_FROM_HAND = auto()
    PASS_PRIORITY = auto()


@dataclass
class PlayerAction:
    type: PlayerActionType
    obj_id: Optional[RuntimeObjectId] = None
    # Later: targets, modes, X, etc.


class PlayerController:
    """
    Abstract decision interface for a player.
    Implementations can be AI, scripted, or interactive.
    """

    def choose_action(self, game_state: GameState, player_id: int) -> PlayerAction:
        raise NotImplementedError

@dataclass
class NoOpController(PlayerController):
    def choose_action(self, game_state: GameState, player_id: int) -> PlayerAction:
        return PlayerAction(type=PlayerActionType.PASS_PRIORITY)
