# axis3/engine/ui/interface.py

class UIInterface:
    """
    Abstract UI interface for Axis3.
    Any UI (CLI, Textual, React, WebSocket) must implement:
      - render(game_state, turn_manager)
      - get_player_action(player_id)
    """

    def render(self, game_state, turn_manager):
        raise NotImplementedError

    def get_player_action(self, player_id):
        """
        Must return a PlayerAction instance or None.
        """
        raise NotImplementedError
