# src/axis3/state/objects.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

from .zones import ZoneType
from axis3.model.axis3_card import Axis3Card


RuntimeObjectId = str


@dataclass
class RuntimeObject:
    """
    Base class for all objects in Axis3.
    Permanents, spells, tokens, abilities.
    """
    id: RuntimeObjectId
    owner: int
    controller: int
    zone: ZoneType

    # Card reference (Axis3 only)
    axis3_card: Optional[Axis3Card] = None

    # Optional Axis1 reference (debugging)
    axis1_card: Any = None

    # Dynamic state
    name: str = ""
    tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=dict)

    # Token flag
    is_token: bool = False

    # ---------------------------------------------------------
    # Type helpers (use Axis3Card characteristics)
    # ---------------------------------------------------------
    def has_type(self, t: str) -> bool:
        if not self.axis3_card:
            return False
        return t in self.axis3_card.types

    def is_creature(self) -> bool:
        return self.has_type("Creature")

    def is_spell(self) -> bool:
        return self.zone == ZoneType.STACK

    def is_land(self) -> bool:
        return self.has_type("Land")

    def can_tap(self):
        return not self.tapped

    def tap(self):
        self.tapped = True


# ---------------------------------------------------------
# Runtime Permanent
# ---------------------------------------------------------

@dataclass
class RuntimePermanent(RuntimeObject):
    """
    A permanent on the battlefield.
    """
    summoning_sick: bool = True


# ---------------------------------------------------------
# Runtime Spell (on the stack)
# ---------------------------------------------------------

@dataclass
class RuntimeSpell(RuntimeObject):
    """
    A spell object on the stack.
    Holds chosen modes, targets, and costs paid.
    """
    chosen_targets: List[List[RuntimeObjectId]] = field(default_factory=list)
    chosen_modes: Optional[List[int]] = None
    mana_paid: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------
# Runtime Token (optional)
# ---------------------------------------------------------

@dataclass
class RuntimeToken(RuntimePermanent):
    """
    A token permanent created by effects.
    """
    token_name: str = ""
