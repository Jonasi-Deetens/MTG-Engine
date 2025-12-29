# src/axis3/state/objects.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from .zones import ZoneType
from axis2.schema import Axis2Characteristics
# ---------------------------------------------------------
# Runtime Object ID
# ---------------------------------------------------------

RuntimeObjectId = str


# ---------------------------------------------------------
# Base Runtime Object
# ---------------------------------------------------------

@dataclass
class RuntimeObject:
    """
    Base class for all objects that can exist in the Axis3 game state.
    This includes permanents, spells on the stack, tokens, and ability objects.
    """
    id: RuntimeObjectId
    owner: int
    controller: int
    zone: ZoneType

    # NEW FIELD — required by Axis3 tests
    name: str = ""  

    # Axis1 + Axis2 references
    axis1_card: Any = None
    axis2_card: Any = None

    # Dynamic state
    tapped: bool = False
    damage: int = 0
    counters: Dict[str, int] = field(default_factory=dict)

    # Characteristics (P/T, colors, types, etc.)
    characteristics: Axis2Characteristics = None

    # Token flag (used by SBA rules)
    is_token: bool = False

    def has_type(self, t: str) -> bool: 
        """Check if the object has a given type (Creature, Land, etc.).""" 
        print(f"Checking if {self.name} has type {t}")
        print(f"Characteristics: {self.characteristics}")
        print(f"Types: {self.characteristics.types}")
        if self.characteristics and t in self.characteristics.types: 
            return True 
        return False


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
