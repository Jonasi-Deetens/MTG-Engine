# axis3/engine/turn/steps.py

from __future__ import annotations
from enum import Enum, auto
from typing import List, Tuple

from .phases import Phase


class Step(Enum):
    # Beginning phase
    UNTAP = auto()
    UPKEEP = auto()
    DRAW = auto()

    # Combat phase
    BEGIN_COMBAT = auto()
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    COMBAT_DAMAGE = auto()
    END_COMBAT = auto()

    # Generic phase-level markers (for main/ending phases)
    MAIN = auto()
    END = auto()
    CLEANUP = auto()

    def __str__(self) -> str:
        return self.name


# Ordered turn structure as (Phase, Step) pairs
PHASE_STEP_ORDER: List[Tuple[Phase, Step]] = [
    # Beginning
    (Phase.BEGINNING, Step.UNTAP),
    (Phase.BEGINNING, Step.UPKEEP),
    (Phase.BEGINNING, Step.DRAW),

    # Precombat main
    (Phase.PRECOMBAT_MAIN, Step.MAIN),

    # Combat
    (Phase.COMBAT, Step.BEGIN_COMBAT),
    (Phase.COMBAT, Step.DECLARE_ATTACKERS),
    (Phase.COMBAT, Step.DECLARE_BLOCKERS),
    (Phase.COMBAT, Step.COMBAT_DAMAGE),
    (Phase.COMBAT, Step.END_COMBAT),

    # Postcombat main
    (Phase.POSTCOMBAT_MAIN, Step.MAIN),

    # Ending
    (Phase.ENDING, Step.END),
    (Phase.ENDING, Step.CLEANUP),
]
