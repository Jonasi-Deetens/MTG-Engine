# axis3/engine/priority.py

from axis3.state.game_state import GameState

def pass_priority(game_state: GameState):
    """
    Cycle priority between players.
    """
    num_players = len(game_state.players)
    game_state.turn.priority_player = (game_state.turn.priority_player + 1) % num_players
    game_state.turn.stack_empty_since_last_priority = game_state.stack.is_empty()
