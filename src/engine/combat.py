from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CombatState:
    attacking_player_id: Optional[int] = None
    defending_player_id: Optional[int] = None
    defending_object_id: Optional[str] = None
    attackers: List[str] = field(default_factory=list)
    blockers: Dict[str, List[str]] = field(default_factory=dict)
    attackers_declared: bool = False
    blockers_declared: bool = False
    first_strike_resolved: bool = False
    combat_damage_resolved: bool = False


