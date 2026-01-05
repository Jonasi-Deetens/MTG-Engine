# src/axis3/engine/engine.py

from __future__ import annotations

from typing import Dict

from axis3.state.game_state import GameState
from axis3.engine.turn import advance_step
from axis3.engine.controller import PlayerController, PlayerActionType
from axis3.rules.actions import cast_spell_from_hand, resolve_top_of_stack


def run_single_step_with_priority(
    game_state: GameState,
    controllers: Dict[int, PlayerController],
) -> None:
    """
    Run a single step:
    - give priority to players in turn (for now, only active player acts)
    - if all pass and stack non-empty: resolve top
    - if all pass and stack empty: move to next step
    """

    ts = game_state.turn
    active = ts.active_player

    # For now, only the active player gets to act.
    controller = controllers[active]

    while True:
        action = controller.choose_action(game_state, active)

        if action.type == PlayerActionType.CAST_SPELL_FROM_HAND:
            cast_spell_from_hand(game_state, active, action.obj_id)
            ts.stack_empty_since_last_priority = False
            # After casting, priority returns to active player in this simplified model.
            continue

        elif action.type == PlayerActionType.PASS_PRIORITY:
            # If stack is not empty, resolve top and give priority back.
            if not game_state.stack.is_empty():
                resolve_top_of_stack(game_state)
                ts.stack_empty_since_last_priority = False
                # Give priority back to active
                continue

            # Stack empty and player passed: step ends, advance.
            ts.stack_empty_since_last_priority = True
            advance_step(game_state)
            return

        else:
            raise ValueError(f"Unknown action type: {action.type}")


def run_full_turn(
    game_state: GameState,
    controllers: Dict[int, PlayerController],
) -> None:
    """
    Run an entire turn for the current active player.
    For now:
      - we don't automate untap/draw, you can do it via tests or later hooks
      - we just iterate steps, giving priority each time
    """
    starting_turn_number = game_state.turn.turn_number

    while game_state.turn.turn_number == starting_turn_number:
        run_single_step_with_priority(game_state, controllers)
