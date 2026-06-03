from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PriorityManager:
    player_order: List[int]
    current_index: int = 0
    last_passed_player: Optional[int] = None
    pass_count: int = 0

    @property
    def current(self) -> int:
        return self.player_order[self.current_index]

    def give_to(self, player_id: int) -> None:
        if player_id in self.player_order:
            self.current_index = self.player_order.index(player_id)
            self.last_passed_player = None
            self.pass_count = 0

    def reset_for_new_step(self, active_player_id: int) -> None:
        self.give_to(active_player_id)

    def update_order(self, player_order: List[int], current_player_id: Optional[int] = None) -> None:
        self.player_order = list(player_order)
        self.pass_count = 0
        self.last_passed_player = None
        if not self.player_order:
            self.current_index = 0
            return
        if current_player_id is None:
            self.current_index = 0
            return
        if current_player_id in self.player_order:
            self.current_index = self.player_order.index(current_player_id)
        else:
            self.current_index = 0

    def pass_priority(self) -> bool:
        player_id = self.current
        if self.last_passed_player == player_id:
            return False
        self.pass_count += 1
        self.last_passed_player = player_id

        if self.pass_count >= len(self.player_order):
            self.pass_count = 0
            self.last_passed_player = None
            return True

        self.current_index = (self.current_index + 1) % len(self.player_order)
        return False
