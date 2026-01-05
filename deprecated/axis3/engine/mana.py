# axis3/engine/mana.py

from axis3.state.game_state import GameState

def pay_mana_cost(game_state: GameState, player_id: int, cost: dict) -> bool:
    """
    Attempt to pay a mana cost from the player's pool.
    Returns True if paid, False otherwise.
    """
    player = game_state.players[player_id]

    for color, amount in cost.items():
        if player.mana_pool.get(color, 0) < amount:
            return False  # cannot pay

    # Deduct
    for color, amount in cost.items():
        player.mana_pool[color] -= amount

    return True
