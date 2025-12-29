# axis3/engine/loop.py

from axis3.engine.turn.turn_manager import TurnManager
from axis3.rules.sba.checker import run_sbas
from axis3.engine.actions.pass_action import PassAction


def game_loop(game_state, ui):
    """
    Main engine loop.
    - UI-agnostic (Textual, CLI, React, etc.)
    - Stack-driven
    - Priority-driven
    - TurnManager-driven
    """

    tm = game_state.turn_manager
    tm.begin_game()

    while True:
        # inside game_loop, after ui.render(game_state, tm)
        for line in game_state.debug_log:
            print("[DEBUG]", line)
        game_state.debug_log.clear()

        player_id = tm.priority.current
        
        # --- 1. Render current state ---
        ui.render(game_state, tm)
        # --- 2. Run SBAs before priority decisions ---
        run_sbas(game_state)

        # --- 3. If stack has items, priority is about resolving or adding more ---
        if not game_state.stack.is_empty():
            action = ui.get_player_action(player_id)

            if action is None or action.kind == "pass":
                tm.handle_player_pass(player_id)
            else:
                action.execute(game_state)
                tm.after_player_action(player_id)

            continue

        # --- 4. Stack is empty → normal priority actions (cast, activate, etc.) ---
        action = ui.get_player_action(player_id)

        if action is None:
            continue

        if isinstance(action, PassAction):
            tm.handle_player_pass(player_id)
            continue

        action.execute(game_state)

        if action.uses_priority:
            tm.after_player_action(player_id)
