from .base import Action

class PassAction(Action):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        # Metadata the game loop expects
        self.kind = "pass"
        # Passing consumes priority in your loop logic
        self.uses_priority = True

    def execute(self, gs):
        # No engine-side work; TurnManager handles pass logic
        return
