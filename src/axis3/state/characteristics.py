# src/axis3/state/characteristics.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuntimeCharacteristics:
    """
    Base / printed characteristics of an object.

    Layered / evaluated characteristics will be derived from this plus
    continuous effects in axis3.rules.layers later.
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

    # Loyalty, etc. can be added later
    loyalty: Optional[int] = None
    counters: Optional[Dict[str, int]] = None
    keywords: Optional[List[str]] = None
