class Action:
    """
    Base class for all player actions.
    """
    def __init__(self, player_id: int):
        self.player_id = player_id
        # Default metadata; subclasses can override in their __init__
        self.kind: str | None = None
        self.uses_priority: bool = True

    def execute(self, gs):
        raise NotImplementedError
