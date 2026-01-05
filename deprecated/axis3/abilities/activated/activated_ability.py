# axis3/abilities/activated/activated_ability.py

from dataclasses import dataclass, field
from typing import List, Any, Optional

from axis3.engine.abilities.effects.base import Axis3Effect
from axis3.engine.abilities.costs.cost import Axis3Cost


@dataclass
class ActivatedAbility:
    """
    Axis3-native activated ability.

    - costs: fully parsed Axis3Cost objects
    - effects: fully parsed Axis3Effect objects
    - restrictions: structural restrictions (e.g., "sorcery_speed")
    - timing: "instant" or "sorcery"
    - is_mana_ability: special-case for priority rules
    """

    costs: List[Axis3Cost]
    effects: List[Axis3Effect]

    restrictions: List[str] = field(default_factory=list)
    timing: str = "instant"            # "instant" or "sorcery"
    is_mana_ability: bool = False

    # Optional metadata for advanced mechanics
    metadata: dict = field(default_factory=dict)
