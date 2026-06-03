# axis3/engine/turn/priority.py

from __future__ import annotations


class PriorityManager:
    """
    Handles which player has priority and the 'both passed in succession' logic.
    This is deliberately minimal and stateless enough to be UI-friendly.
    """

    def __init__(self, active_player: int):
        self.active_player = active_player
        self.priority_player = active_player
        self._last_passed_player: int | None = None

    @property
    def current(self) -> int:
        return self.priority_player

    def reset_for_new_step(self, active_player: int):
        self.active_player = active_player
        self.priority_player = active_player
        self._last_passed_player = None

    def give_to(self, player_id: int):
        self.priority_player = player_id
        self._last_passed_player = None

    def pass_priority(self) -> bool:
        """
        Called when the current priority player passes.
        Returns True if both players have passed in succession (and the
        caller should advance the step or resolve the stack), else False.
        """
        if self._last_passed_player is not None and self._last_passed_player != self.priority_player:
            # Both players have now passed in succession
            self._last_passed_player = None
            return True

        # Toggle priority to the other player
        self._last_passed_player = self.priority_player
        self.priority_player ^= 1
        return False
