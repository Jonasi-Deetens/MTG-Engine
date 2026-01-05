# axis3/engine/turn/phases.py

from __future__ import annotations
from enum import Enum, auto


class Phase(Enum):
    BEGINNING = auto()
    PRECOMBAT_MAIN = auto()
    COMBAT = auto()
    POSTCOMBAT_MAIN = auto()
    ENDING = auto()

    def __str__(self) -> str:
        return self.name
