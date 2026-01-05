# axis3/state/player_data.py

from dataclasses import dataclass, field

@dataclass
class PlayerTurnState:
    mana_pool: Dict[str, int] = field(default_factory=lambda: {"W":0,"U":0,"B":0,"R":0,"G":0})
    priority: bool = False
    has_played_land: bool = False

def reset_for_new_turn(self):
    self.priority = False
    self.has_played_land = False
    self.mana_pool = {"W":0,"U":0,"B":0,"R":0,"G":0}
