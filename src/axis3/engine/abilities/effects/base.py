class Axis3Effect:
    layering: str = "resolution"
    def apply(self, game_state, source, controller):
        raise NotImplementedError
