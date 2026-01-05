# axis3/engine/abilities/costs/cost.py

from dataclasses import dataclass
from typing import Any

@dataclass
class Axis3Cost:
    kind: str     # "mana", "tap", "sacrifice", "discard", "life", etc.
    value: Any    # e.g. ManaCost object, number, target spec, etc.
