# axis3/engine/ui/actions.py

class PlayerAction:
    """
    Represents a player action chosen via UI.
    Examples:
      - pass
      - cast spell
      - activate ability
      - declare attackers
    """

    def __init__(self, kind: str, data=None):
        self.kind = kind
        self.data = data

    def execute(self, game_state):
        """
        The engine loop calls this to perform the action.
        For now, this is a stub — real actions will be implemented later.
        """
        print(f"[ENGINE] Executing action: {self.kind} {self.data}")
