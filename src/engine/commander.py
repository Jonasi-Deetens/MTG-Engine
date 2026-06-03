from __future__ import annotations

from typing import Optional

from .state import GameState
from .zones import ZONE_COMMAND


COMMANDER_TAX_INCREMENT = 2


def register_commander(game_state: GameState, player_id: int, commander_id: str) -> None:
    player = game_state.get_player(player_id)
    player.commander_id = commander_id
    if commander_id not in player.command:
        player.command.append(commander_id)
    obj = game_state.objects.get(commander_id)
    if obj:
        obj.zone = ZONE_COMMAND


def apply_commander_tax(game_state: GameState, player_id: int) -> int:
    player = game_state.get_player(player_id)
    tax = player.commander_tax
    player.commander_tax += COMMANDER_TAX_INCREMENT
    return tax


def record_commander_damage(game_state: GameState, source_id: str, target_player_id: int, amount: int) -> None:
    target = game_state.get_player(target_player_id)
    target.commander_damage_taken[source_id] = target.commander_damage_taken.get(source_id, 0) + amount
