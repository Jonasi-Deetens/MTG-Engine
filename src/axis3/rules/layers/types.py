# axis3/rules/layers/types.py

from dataclasses import dataclass

@dataclass
class EvaluatedCharacteristics:
    """
    Holds the final characteristics of a permanent after applying layers.
    """
    power: int
    toughness: int
    types: set
    subtypes: set
    supertypes: set
    colors: set
    abilities: set
