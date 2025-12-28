# axis3/rules/costs/alternative.py

class AlternativeCost:
    """
    Represents an alternative cost for a spell or ability.
    Examples:
    - Pay 2 life instead of mana
    - Discard a card
    """
    def __init__(self, description: str, pay_func):
        """
        pay_func(game_state, player_id) -> None
        """
        self.description = description
        self.pay_func = pay_func

    def can_pay(self, game_state, player_id) -> bool:
        """
        Check if alternative cost can be paid.
        """
        try:
            return self.pay_func(game_state, player_id, check_only=True)
        except:
            return False

    def pay(self, game_state, player_id):
        """
        Execute the alternative cost.
        """
        self.pay_func(game_state, player_id, check_only=False)

# Example: discard a card
def discard_card_cost(game_state, player_id, check_only=False):
    ps = game_state.players[player_id]
    if not ps.hand:
        return False if check_only else None

    if not check_only:
        discarded = ps.hand.pop()
        obj = game_state.objects[discarded]
        obj.zone = "GRAVEYARD"
        ps.graveyard.append(discarded)
    return True

# You can instantiate an AlternativeCost for a spell
discard_cost = AlternativeCost(
    description="Discard a card instead of paying mana",
    pay_func=discard_card_cost
)