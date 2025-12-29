# axis3/rules/layers/types.py

from dataclasses import dataclass
from typing import Set

@dataclass
class EvaluatedCharacteristics:
    """
    Holds the final characteristics of a permanent after applying layers.
    """
    power: int
    toughness: int

    types: Set[str]
    subtypes: Set[str]
    supertypes: Set[str]
    colors: Set[str]
    abilities: Set[str]

