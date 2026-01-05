# axis3/engine/abilities/targeting/targeting_rules.py

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class TargetingRestriction:
    """
    A single restriction on what can be targeted.
    Example: "creature you control", "nonland permanent", etc.
    """
    rule: str
    params: Optional[Any] = None


@dataclass
class TargetingRules:
    """
    Axis3 targeting rules for abilities and effects.

    - required: whether the ability *must* choose targets
    - min/max: how many targets can be chosen
    - legal_targets: subject resolver keys (e.g. "target_creature", "target_player")
    - restrictions: additional constraints (e.g. "nonland", "opponent controls")
    - replacement_effects: optional replacement rules applied during targeting
    """

    required: bool = False
    min: int = 0
    max: int = 0

    # These are Axis3 subject resolver keys
    legal_targets: List[str] = field(default_factory=list)

    # Additional restrictions
    restrictions: List[TargetingRestriction] = field(default_factory=list)

    # Replacement effects that modify targeting (rare)
    replacement_effects: List[str] = field(default_factory=list)
