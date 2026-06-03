# axis3/engine/stack_processor.py

from axis3.state.game_state import GameState
from axis3.rules.orchestrator import resolve_top_of_stack

def resolve_stack(game_state: GameState):
    """
    Resolve stack items until empty or until a player gains priority.
    """
    while not game_state.stack.is_empty():
        resolve_top_of_stack(game_state)
