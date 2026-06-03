# axis3/engine/utils.py

from axis3.state.game_state import GameState

def get_permanents_controlled_by(game_state: GameState, player_id: int):
    """
    Return all permanents on battlefield controlled by a player.
    """
    return [
        obj for obj in game_state.objects.values()
        if obj.zone.name == "BATTLEFIELD" and obj.controller == player_id
    ]
