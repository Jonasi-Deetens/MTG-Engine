# axis3/state/player_data.py

from dataclasses import dataclass, field

@dataclass
class PlayerData:
    mana_pool: dict = field(default_factory=lambda: {"W":0,"U":0,"B":0,"R":0,"G":0})
    priority: bool = False
    has_played_land: bool = False
