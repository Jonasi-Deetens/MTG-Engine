# axis3/engine/game_loop.py

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
        # Dump debug log
        for line in game_state.debug_log:
            print("[DEBUG]", line)
        game_state.debug_log.clear()

        player_id = tm.priority.current

        # --- 1. Render current state ---
        ui.render(game_state, tm)

        # --- 2. Run SBAs before priority decisions ---
        run_sbas(game_state)

        # --- 3. Player chooses an action with priority ---
        # Note: we no longer treat "stack non-empty" as a special mode
        action = ui.get_player_action(player_id)

        if action is None:
            continue

        if isinstance(action, PassAction) or action.kind == "pass":
            tm.handle_player_pass(player_id)
            continue

        # Non-pass action (cast spell, activate ability, etc.)
        action.execute(game_state)

        if getattr(action, "uses_priority", True):
            tm.after_player_action(player_id)
