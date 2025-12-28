# axis3/engine/trigger_processor.py

from axis3.state.game_state import GameState
from axis3.rules.triggers.runtime import process_runtime_triggers

def process_triggers(game_state: GameState):
    """
    Check EventBus and convert Axis2 triggers into RuntimeTriggeredAbility.
    """
    process_runtime_triggers(game_state)
