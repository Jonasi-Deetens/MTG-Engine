# axis3/rules/sba/checker.py

from axis3.state.game_state import GameState
from axis3.rules.sba.rules import (
    check_lethal_damage,
    check_zero_toughness,
    check_tokens,
    check_legend_rule,
)

def run_sbas(game_state: GameState):
    """
    Run state-based actions until the game state stabilizes.
    """
    while True:
        changed = False

        # Game loss
        for player in game_state.players:
            if player.life <= 0:
                player.dead = True
                return

        if check_lethal_damage(game_state):
            changed = True

        if check_zero_toughness(game_state):
            changed = True

        if check_tokens(game_state):
            changed = True

        if check_legend_rule(game_state):
            changed = True

        if not changed:
            return
