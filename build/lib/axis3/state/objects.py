# src/axis3/state/objects.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from .zones import ZoneType
from axis3.model.characteristics import PrintedCharacteristics
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
    owner: str
    controller: str
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
    characteristics: PrintedCharacteristics = None

    # Token flag (used by SBA rules)
    is_token: bool = False

    def has_type(self, t: str) -> bool:
        """Check if the object has a given type (Creature, Instant, etc.)."""
        return t in self.characteristics.types if self.characteristics else False

    def is_creature(self) -> bool:
        return self.has_type("Creature")

    def is_spell(self) -> bool:
        return self.zone == ZoneType.STACK


# ---------------------------------------------------------
# Runtime Permanent
# ---------------------------------------------------------

@dataclass
class RuntimePermanent(RuntimeObject):
    """
    A permanent on the battlefield.
    """
    summoning_sick: bool = True

    def can_attack(self) -> bool:
        return (
            self.is_creature()
            and not self.tapped
            and not self.summoning_sick
        )


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

    def is_spell(self) -> bool:
        return True


# ---------------------------------------------------------
# Runtime Token (optional)
# ---------------------------------------------------------

@dataclass
class RuntimeToken(RuntimePermanent):
    """
    A token permanent created by effects.
    """
    token_name: str = ""
