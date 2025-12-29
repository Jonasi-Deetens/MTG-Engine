# axis3/model/characteristics.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass(frozen=True)
class PrintedCharacteristics:
    """
    Immutable printed characteristics of a card.
    These are the base values before continuous effects and layers.
    """

    name: str
    mana_cost: Optional[str]

    # Types
    types: List[str]
    supertypes: List[str]
    subtypes: List[str]

    # Colors (e.g. ["W", "U"])
    colors: List[str]

    # P/T (None for non-creatures)
    power: Optional[int]
    toughness: Optional[int]

    # Loyalty, counters, keywords, abilities
    loyalty: Optional[int] = None
    counters: Optional[Dict[str, int]] = None
    keywords: Optional[List[str]] = None
    abilities: Optional[List[str]] = None
